import inspect
import whatap.net.async_sender as async_sender
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.userid_util import UseridUtil as userid_util
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.util.date_util import DateUtil
from whatap.conf.configure import Configure as conf
from whatap.trace.mod.application.wsgi import trace_handler, \
    start_interceptor, end_interceptor, interceptor_error, isIgnore


def parseServiceName(environ):
    return environ.get('PATH_INFO', '')


def instrument(module):
    def wrapper(fn):
        async def trace(*args, **kwargs):
            request = args[0].request
            environ = {
                'HTTP_HOST': request.host,
                'PATH_INFO': request.path,
                'QUERY_STRING': request.query_arguments,
                'REMOTE_ADDR': request.remote_ip,
                'HTTP_USER_AGENT': request.headers.get('User-Agent', ''),
                'HTTP_REFERER': request.headers.get('Referer', ''),
                'REQUEST_METHOD': request.method
            }

            for header_name, value in request.headers.items():
                key = 'HTTP_' + header_name.upper().replace('-', '_')
                environ[key] = value

            async def run():
                await interceptor((fn, environ), *args, **kwargs)

            from tornado.ioloop import IOLoop
            IOLoop.current().add_callback(run)

            return None

        return trace

    module.RequestHandler._execute = wrapper(module.RequestHandler._execute)

    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)

            e = args[1]
            status_code = args[0]._status_code
            errors = [e.__class__.__name__, str(e)]
            interceptor_error(status_code, errors)
            return callback

        return trace

    module.RequestHandler._handle_request_exception = wrapper(
        module.RequestHandler._handle_request_exception)


async def interceptor(rn_environ, *args, **kwargs):
    if not isinstance(rn_environ, tuple):
        rn_environ = (rn_environ, args[1])
    fn, environ = rn_environ

    ctx = TraceContext()
    ctx.host = environ.get('HTTP_HOST', '').split(':')[0]
    ctx.service_name = parseServiceName(environ)
    ctx.http_method = environ.get('REQUEST_METHOD', '')
    ctx.remoteIp = userid_util.getRemoteAddr(args)
    ctx.userAgentString = environ.get('HTTP_USER_AGENT', '')
    ctx.referer = environ.get('HTTP_REFERER', '')

    if conf.trace_user_enabled:
        if conf.trace_user_using_ip:
            ctx.userid = userid_util.getRemoteAddr(args)
        else:
            ctx.userid, ctx._rawuserid = userid_util.getUserId(args, ctx.remoteIp)

    mstt = environ.get('HTTP_{}'.format(
        conf._trace_mtrace_caller_key.upper().replace('-', '_')), '')

    if mstt:
        ctx.setTransfer(mstt)
        if conf.stat_mtrace_enabled:
            val = environ.get('HTTP_{}'.format(
                conf._trace_mtrace_info_key.upper().replace('-', '_')), '')
            if val and len(val):
                ctx.setTransferInfo(val)
            pass

        myid = environ.get('HTTP_{}'.format(
            conf._trace_mtrace_callee_key.upper().replace('-', '_')), '')
        if myid:
            ctx.setTxid(myid)
    caller_poid = environ.get('HTTP_{}'.format(
        conf._trace_mtrace_caller_poid_key.upper().replace('-', '_')), '')

    if caller_poid:
        ctx.mcaller_poid = caller_poid

    try:
        if isIgnore(ctx.service_name):
            ctx.is_ignored = True
            TraceContextManager.end(ctx.id)
            callback = fn(*args, **kwargs)
            if inspect.isawaitable(callback):
                return await callback
            return callback
    except Exception:
        pass

    start_interceptor(ctx)

    try:
        callback = fn(*args, **kwargs)
        if inspect.isawaitable(callback):
            callback = await callback

        query_string = environ.get('QUERY_STRING', '')
        if query_string:
            ctx.service_name += '?{}'.format(query_string)

        if ctx.service_name.find('.') > -1 and ctx.service_name.split('.')[
            1] in conf.web_static_content_extensions:
            ctx.isStaticContents = 'true'

        handler = args[0]
        status_code = getattr(handler, '_status_code', 200)
        if status_code >= 400:
            errors = [
                callback.__class__.__name__ if callback else 'Unknown',
                getattr(callback, 'reason_phrase', '')
            ]
            interceptor_error(status_code, errors, ctx=ctx)

        else:
            ctx.status = status_code

        if conf.profile_http_header_enabled:
            keys = []
            for key, value in environ.items():
                if key.startswith('HTTP_'):
                    keys.append(key)
            keys.sort()

            text = ''
            for key in keys:
                text += '{}={}\n'.format(key.split('HTTP_')[1].lower(),
                                         environ[key])

            datas = ['HTTP-HEADERS', 'HTTP-HEADERS', text]
            ctx.start_time = DateUtil.nowSystem()
            async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)

        return callback
    finally:
        end_interceptor(ctx=ctx)