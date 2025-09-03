from whatap.trace.mod.application.wsgi import trace_handler, \
    interceptor_error, start_interceptor, isIgnore, \
    end_interceptor
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.conf.configure import Configure as conf
from whatap.util.keygen import KeyGen
import whatap.util.bit_util as bit_util
from whatap.util.hash_util import HashUtil as hash_util
from whatap.util.date_util import DateUtil
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.hexa32 import Hexa32 as hexa32
import whatap.net.async_sender as async_sender
import logging as logging_module
import sys
from whatap.trace.trace_context import TraceContext


logger = logging_module.getLogger(__name__)
def toDjangoHeaderName(src):

    return 'HTTP_' + src.upper().replace('-','_')
class UseridUtil(object):
    WHATAP_R = "WHATAP"

    @staticmethod
    def getUserId(args,  defValue):
        try:

            if conf.user_header_ticket:
                ticket = UseridUtil.getHeader(args, conf.user_header_ticket)
                if  ticket:
                    return hash_util.hashFromString(ticket), ticket
                return 0,""
            cookie = UseridUtil.getHeader(args, "HTTP_COOKIE")
            if cookie:
                if len(cookie) >= conf.trace_user_cookie_limit :
                    return defValue

                x1 = cookie.find(UseridUtil.WHATAP_R)
                if x1 >= 0:
                    x2 = cookie.find(';', x1)
                    if x2 > 0:
                        value = cookie[x1 + len(UseridUtil.WHATAP_R) + 1: x2]
                    else:
                        value = cookie[x1 + len(UseridUtil.WHATAP_R) + 1:]
                    return hexa32.toLong32(value), value
            userid=KeyGen.next()
            return userid, hexa32.toString32(userid)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.debug("A502",10, str(exc_value))

    @staticmethod
    def setUserId(request, response, cookieValue):
        try:
            if not conf.user_header_ticket:
                if request.cookies:
                    cookie = request.cookies.get(UseridUtil.WHATAP_R)
                else:
                    cookie = None
                if not cookie:
                    cookieDomain=conf.trace_user_cookie_domain if conf.trace_user_cookie_domain else None
                    UseridUtil.setCookie( response, UseridUtil.WHATAP_R, cookieValue, bit_util.INT_MAX_VALUE, "/", cookieDomain )
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.debug("A503", 10, str(exc_value))

    @staticmethod
    def setCookie(response, key, value, max_age, path, domain):
        response.set_cookie(key, value, max_age=max_age, path=path, domain=domain)
        
    @staticmethod
    def getRemoteAddr(args):
        if conf.trace_http_client_ip_header_key:
            header_val = UseridUtil.getHeader(args, conf.trace_http_client_ip_header_key)
            if header_val:
                return header_val.split(',')[0].strip()
        x_forwarded_for = UseridUtil.getHeader(args, "x-forwarded-for")
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return UseridUtil.getHeader(args, "REMOTE_ADDR")
        #return UseridUtil.getHeader(args, "REMOTE_ADDR")

    @staticmethod
    def getHeader(args, key):

        if args:
            environ = args[0]
            wsgiHeaderKey = 'HTTP_'+key.upper().replace('-','_')
            return environ.get(key, environ.get(wsgiHeaderKey))
        else:
            return None


def parseServiceName(environ):
    return environ.get('PATH_INFO', '')


def interceptor(rn_environ, *args, **kwargs):
    if not isinstance(rn_environ, tuple):
        rn_environ = (rn_environ, args[1])
    fn, environ = rn_environ

    ctx = TraceContext()
    ctx.host = environ.get('HTTP_HOST', '').split(':')[0]
    ctx.service_name = parseServiceName(environ)
    ctx.remoteIp = UseridUtil.getRemoteAddr(args)
    ctx.userAgentString = environ.get('HTTP_USER_AGENT', '')
    ctx.referer = environ.get('HTTP_REFERER', '')
    
    if conf.trace_user_enabled:
        if conf.trace_user_using_ip:
            ctx.userid = UseridUtil.getRemoteAddr(args)
        else:
            ctx.userid, ctx._rawuserid = UseridUtil.getUserId(args, ctx.remoteIp)

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
            return fn(*args, **kwargs)
    except Exception as e:
        pass

    start_interceptor(ctx)

    try:

        callback = fn(*args, **kwargs)
        ctx = TraceContextManager.getLocalContext()
        if ctx:
            query_string = environ.get('QUERY_STRING', '')
            if query_string:
                ctx.service_name += '?{}'.format(query_string)

            if ctx.service_name.find('.') > -1 and ctx.service_name.split('.')[
                1] in conf.web_static_content_extensions:
                ctx.isStaticContents = 'true'

            if getattr(callback, 'status_code', None):
                status_code = callback.status_code
                errors = [callback.reason_phrase, callback.__class__.__name__]
                interceptor_error(status_code, errors)

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
        ctx = TraceContextManager.getLocalContext()
        if ctx:
            end_interceptor(ctx=ctx)

def instrument(module):
    def wrapper(fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            environ = args[0]
            callback = interceptor((fn, environ), *args, **kwargs)
    
            return callback
        
        return trace
    if hasattr(module, "application"):
        
        module.application = wrapper(module.application)
    

    def run_after_request_hooks_wrapper(fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            request = args[0]
            response = args[1]
            ctx = TraceContextManager.getLocalContext()
            if ctx and conf.trace_user_enabled:
                if not conf.trace_user_using_ip:
                    UseridUtil.setUserId(request, response,  ctx._rawuserid )
            callback = fn(*args, **kwargs)
            
            return callback
        
        return trace


    if hasattr(module, "run_after_request_hooks"):
        
        module.run_after_request_hooks = run_after_request_hooks_wrapper(module.run_after_request_hooks)
    