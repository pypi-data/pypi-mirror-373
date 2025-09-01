from whatap.trace.mod.application.wsgi import trace_handler, \
    interceptor_error, start_interceptor, end_interceptor, \
    isIgnore, interceptor_step_error
from copy import copy
from whatap.trace.trace_context import TraceContext, TraceContextManager
from whatap.util.userid_util import UseridUtil as userid_util
import whatap.util.bit_util as bit_util
from whatap.conf.configure import Configure as conf
from whatap.util.date_util import DateUtil
import whatap.net.async_sender as async_sender
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.hash_util import HashUtil as hash_util
from whatap.util.hexa32 import Hexa32 as hexa32
from whatap.util.keygen import KeyGen
import whatap.pack.logSinkPack as logSinkPack
import whatap.io as whatapio
import logging as logging_module
import sys
import traceback
import linecache
import inspect

logger = logging_module.getLogger(__name__)
_WHATAP_DICT="__whatap__"
_DEPENDANT='dependant'
_REQUEST='request'
_RESPONSE='response'
_REMOTE_ADDR='remoteAddr'
_COOKIE='cookie'

async def sse_body_wrapper(original_iterator, ctx,environ, response):
    try:
        async for chunk in original_iterator:
            yield chunk
    except Exception as e:
        interceptor_step_error(e)
        raise
    finally:
        if ctx:
            if conf.profile_http_header_enabled:
                sendHeaders(ctx, environ)
            if response and conf.trace_user_enabled:
                if not conf.trace_user_using_ip:
                    setUserId(environ, response, ctx._rawuserid)
            end_interceptor(ctx=ctx)


def getUserId(headers,  defValue):
    try:
        if conf.user_header_ticket:
            ticket = headers.get(conf.user_header_ticket)
            if  ticket:
                return hash_util.hashFromString(ticket), ticket
            return 0,""
        cookie = headers.get("cookie")

        if cookie:
            if len(cookie) >= conf.trace_user_cookie_limit :
                return defValue

            x1 = cookie.find(userid_util.WHATAP_R)
            if x1 >= 0:
                x2 = cookie.find(';', x1)
                if x2 > 0:
                    value = cookie[x1 + len(userid_util.WHATAP_R) + 1: x2]
                else:
                    value = cookie[x1 + len(userid_util.WHATAP_R) + 1:]
                return hexa32.toLong32(value), value
        userid=KeyGen.next()
        return userid, hexa32.toString32(userid)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.debug("A057",10, str(exc_value))

def getRemoteAddr(headers, whatap_dict):
    if conf.trace_http_client_ip_header_key:
        header_val = headers.get(conf.trace_http_client_ip_header_key)
        if header_val:
            return header_val.split(',')[0].strip()
    x_forwarded_for = headers.get("x-forwarded-for")
    if x_forwarded_for:
        x_forwarded_for = x_forwarded_for.split(',')[0].strip() if ',' in x_forwarded_for else None
        return x_forwarded_for
    if whatap_dict:
        return whatap_dict.get(_REMOTE_ADDR)

    return None

def sendHeaders(ctx, environ):
    keys = []
    for key, value in environ.items():
        keys.append(key)
    keys.sort()

    text = ''
    for key in keys:
        text += '{}={}\n'.format(key,
                                environ[key])

    datas = ['HTTP-HEADERS', 'HTTP-HEADERS', text]
    ctx.start_time = DateUtil.nowSystem()
    async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)

def setUserId(environ, res, cookieValue):
    try:
        if not conf.user_header_ticket:
            cookie = environ.get(_COOKIE)

            if not cookie or cookie.find(userid_util.WHATAP_R) < 0 or cookie.find(cookieValue) < 0:
                res.set_cookie(key=userid_util.WHATAP_R, value=cookieValue, \
                    max_age=bit_util.INT_MAX_VALUE, path="/", \
                        domain=conf.trace_user_cookie_domain)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.debug("A503", 10, str(exc_value))

def interceptor_error_log(trxid, e, fn, args, kwargs):
    if conf.log_unhandled_exception == 'false':
        return
    errorClass = ''
    if e.args:
        errorClass = str(e.args[0])
    elif hasattr(e, "detail"):
        errorClass = getattr(e, "detail")

    error = ''
    _, _, tb = sys.exc_info()
    lastfilename = None
    lastlineno = None
    lastf_globals = None
    for (fr, lineno) in traceback.walk_tb(tb):
        co = fr.f_code
        filename = co.co_filename
        lastfilename = filename
        lastlineno = lineno
        lastf_globals = fr.f_globals

    fields = {'errorClass': errorClass,
                  'args': str(inspect.getcallargs(fn, *args, **kwargs))}
    if lastfilename and lastlineno:
        fields['filename'] = lastfilename
        fields['lineno'] = lastlineno
        linecache.checkcache(lastfilename)

        for i, l in enumerate(linecache.getlines(lastfilename, lastf_globals)):
            if i == lastlineno -1 and len(l.lstrip()) > 2:

                indent = len(l) - len(l.lstrip())
                indicator = '-'*(indent-1) + '>'
                error += ''.join([indicator, l.lstrip()])
            else:
                error += l

    p = logSinkPack.getLogSinkPack(
        t = DateUtil.now(),
        category = "UnhandledException",
        tags = {'@txid': trxid},
        fields = fields,
        line=DateUtil.now(),
        content = error
    )
    p.pcode = conf.PCODE
    bout = whatapio.DataOutputX()
    bout.writePack(p, None)
    packbytes = bout.toByteArray()

    async_sender.send_relaypack(packbytes)

def interceptor(fn, dependant, *args, **kwargs):
    if not hasattr(dependant, _WHATAP_DICT):
        return fn(*args, **kwargs)
    whatap_dict = getattr(dependant, _WHATAP_DICT)

    ctx = TraceContextManager.getLocalContext()
    environ = whatap_dict.get('headers')
    ctx.host = environ.get('host')
    ctx.service_name = dependant.path

    ctx.remoteIp = getRemoteAddr(environ, whatap_dict)

    ctx.userAgentString = environ.get('user_agent')
    ctx.referer = environ.get('referer')

    if conf.trace_user_enabled:
        if conf.trace_user_using_ip:
            ctx.userid = ctx.remoteIp
        else:
            ctx.userid, ctx._rawuserid = getUserId(environ, ctx.remoteIp)

    mstt = environ.get('{}'.format(
        conf._trace_mtrace_caller_key), '')

    if mstt:
        ctx.setTransfer(mstt)
        if conf.stat_mtrace_enabled:
            val = environ.get('{}'.format(
                conf._trace_mtrace_info_key), '')
            if val and len(val):
                ctx.setTransferInfo(val)
            pass

        myid = environ.get('{}'.format(
            conf._trace_mtrace_callee_key), '')
        if myid:
            ctx.setTxid(myid)
    caller_poid = environ.get('{}'.format(
        conf._trace_mtrace_caller_poid_key), '')

    if caller_poid:
        ctx.mcaller_poid = caller_poid

    try:
        if isIgnore(ctx.service_name):
            ctx.is_ignored = True
            return  fn(*args, **kwargs)
    except Exception as e:
        pass

    start_interceptor(ctx)

    try:
        callback = fn(*args, **kwargs)
        ctx = TraceContextManager.getLocalContext()
        if ctx:
            query_string = "&".join([str(query) for query in dependant.query_params])
            if query_string:
                ctx.service_name += '?{}'.format(query_string)

            if ctx.service_name.find('.') > -1 and ctx.service_name.split('.')[
                1] in conf.web_static_content_extensions:
                ctx.isStaticContents = 'true'

            if hasattr(callback, 'status_code'):
                status_code = callback.status_code
                errors = [ callback.__class__.__name__]
                if hasattr(callback, 'reason_phrase'):
                    errors.insert(0, callback.reason_phrase)
                interceptor_error(status_code, errors)

            return callback
    except Exception as e:
        interceptor_step_error(e)
        raise e
    finally:
        ctx = TraceContextManager.getLocalContext()
        if ctx:
            if conf.profile_http_header_enabled:
                sendHeaders(ctx, environ)
            response = whatap_dict.get(_RESPONSE)

            if response and conf.trace_user_enabled:
                if not conf.trace_user_using_ip:
                    setUserId(environ, response, ctx._rawuserid )
            end_interceptor(ctx=ctx)
        if hasattr(dependant, _WHATAP_DICT):
            delattr(dependant, _WHATAP_DICT)

async def interceptor_async(fn, dependant, *args, **kwargs):
    sse_imported = False
    if not hasattr(dependant, _WHATAP_DICT):
        return await fn(*args, **kwargs)

    ctx = TraceContextManager.getLocalContext()

    ctx.service_name = dependant.path

    whatap_dict = getattr(dependant, _WHATAP_DICT)
    environ = whatap_dict.get('headers')
    ctx.host = environ.get('host')
    ctx.remoteIp = getRemoteAddr(environ, whatap_dict)

    ctx.userAgentString = environ.get('user_agent')
    ctx.referer = environ.get('referer')

    if conf.trace_user_enabled:
        if conf.trace_user_using_ip:
            ctx.userid = ctx.remoteIp
        else:
            ctx.userid, ctx._rawuserid = getUserId(environ, ctx.remoteIp)

    mstt = environ.get('{}'.format(
        conf._trace_mtrace_caller_key), '')

    if mstt:
        ctx.setTransfer(mstt)
        if conf.stat_mtrace_enabled:
            val = environ.get('{}'.format(
                conf._trace_mtrace_info_key), '')
            if val and len(val):
                ctx.setTransferInfo(val)
            pass

        myid = environ.get('{}'.format(
            conf._trace_mtrace_callee_key), '')
        if myid:
            ctx.setTxid(myid)
    caller_poid = environ.get('{}'.format(
        conf._trace_mtrace_caller_poid_key), '')

    if caller_poid:
        ctx.mcaller_poid = caller_poid

    try:
        if isIgnore(ctx.service_name):
            ctx.is_ignored = True
            return await fn(*args, **kwargs)
    except Exception as e:
        pass

    start_interceptor(ctx)
    callback = None

    try:
        from fastapi.responses import StreamingResponse
        sse_imported = True
        callback = await fn(*args, **kwargs)
        ctx = TraceContextManager.getLocalContext()

        if isinstance(callback, StreamingResponse) and hasattr(callback, "body_iterator"):
            original_iter = callback.body_iterator
            callback.body_iterator = sse_body_wrapper(original_iter, ctx, environ,whatap_dict.get(_RESPONSE))

        if ctx:
            query_string = "&".join([str(query) for query in dependant.query_params])
            if query_string:
                ctx.service_name += '?{}'.format(query_string)

            if ctx.service_name.find('.') > -1 and ctx.service_name.split('.')[
                1] in conf.web_static_content_extensions:
                ctx.isStaticContents = 'true'

            if hasattr(callback, 'status_code'):
                status_code = callback.status_code
                errors = [ callback.__class__.__name__]
                if hasattr(callback, 'reason_phrase'):
                    errors.insert(0, callback.reason_phrase)
                interceptor_error(status_code, errors)

            return callback
    except Exception as e:
        interceptor_step_error(e)
        interceptor_error_log(ctx.id, e, fn, args, kwargs)
        raise e
    finally:
        ctx = TraceContextManager.getLocalContext()
        if ctx and sse_imported:
            if not isinstance(callback, StreamingResponse):
                if conf.profile_http_header_enabled:
                    sendHeaders(ctx, environ)
                response = whatap_dict.get(_RESPONSE)
                if response and conf.trace_user_enabled:
                    if not conf.trace_user_using_ip:
                        setUserId(environ, response, ctx._rawuserid)
                end_interceptor(ctx=ctx)
        elif ctx:
            if conf.profile_http_header_enabled:
                sendHeaders(ctx, environ)
            response = whatap_dict.get(_RESPONSE)
            if response and conf.trace_user_enabled:
                if not conf.trace_user_using_ip:
                    setUserId(environ, response, ctx._rawuserid)
            end_interceptor(ctx=ctx)
        if hasattr(dependant, _WHATAP_DICT):
            delattr(dependant, _WHATAP_DICT)

def instrument(module):
    def isCoroutine(kwargs={}):
        is_coroutine = 'is_coroutine'
        if is_coroutine in kwargs:
            return kwargs[is_coroutine]
        return False

    def func_wrapper(dependant, fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            callback = interceptor(fn, dependant, *args, **kwargs)
            return callback
        
        return trace

    def func_wrapperasync(dependant, fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            callback = interceptor_async(fn, dependant, *args, **kwargs)
            return callback
        
        return trace

    def wrapper(fn):
        @trace_handler(fn, True)
        def trace( *args, **kwargs):
            dependant = kwargs[_DEPENDANT]
            dependant = kwargs[_DEPENDANT] = copy(dependant)

            if isCoroutine(kwargs):
                dependant.call = func_wrapperasync(dependant, dependant.call)
            else:    
                dependant.call = func_wrapper(dependant, dependant.call)
            
            return fn(*args, **kwargs)
        
        return trace    
        
    if hasattr(module, 'run_endpoint_function'):
        module.run_endpoint_function = wrapper(
            module.run_endpoint_function)
    
def instrument_util(module):
    def wrapper(fn):
        async def trace( *args, **kwargs):
            if _DEPENDANT in kwargs:
                dependant = kwargs[_DEPENDANT]
                whatap_dict = dict()
                setattr(dependant, _WHATAP_DICT, whatap_dict)
                if _REQUEST in kwargs:
                    request = kwargs[_REQUEST]
                    if request:
                        if request.client is not None:
                            remoteAddr = request.client.host
                        else:
                            remoteAddr = request.headers.get('x-forwarded-for')
                        whatap_dict.update({
                            'remoteAddr': remoteAddr,
                            'headers': copy(request.headers),
                            'cookies': copy(request.cookies),
                            'query_params': copy(request.query_params),
                        })
            ret = await fn(*args, **kwargs)            
            if hasattr(ret, '__len__') and len(ret) >= 4:
                response = ret[3]
                whatap_dict[_RESPONSE] = response
            
            return ret

        return trace

    if hasattr(module, 'solve_dependencies'):
        module.solve_dependencies = wrapper(
            module.solve_dependencies)

def instrument_applications(module):
    def wrapper(fn):
        async def trace(instance, scope, receive, send):
            if scope["type"] != "http":
                await fn(instance, scope, receive, send)
            TraceContext()
            try:
                await fn(instance, scope, receive, send)
            finally:
                ctx = TraceContextManager.getLocalContext()
                if ctx:
                    TraceContextManager.end(ctx.id)
        return trace

    module.FastAPI.__call__ = wrapper(module.FastAPI.__call__)