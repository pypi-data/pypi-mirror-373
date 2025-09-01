
from whatap.conf.configure import Configure as conf
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.trace.trace_context import TraceContext
from whatap.trace.mod.application.wsgi import \
    interceptor_error,isIgnore, start_interceptor, end_interceptor
from whatap.util.hash_util import HashUtil as hash_util
from whatap.util.userid_util import UseridUtil
from whatap.util.date_util import DateUtil
from whatap.util.hexa32 import Hexa32 as hexa32 
from whatap.util.keygen import KeyGen
import whatap.util.throttle_util as throttle_util
import whatap.net.async_sender as async_sender
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap import logging


from functools import wraps
import logging as logging_module
import datetime, sys

SCOPE_ARGS_LENGTH = 2
HEADER = 'headers'
PATH = 'path'
USER_AGENT = 'user-agent'
REFERER = 'referer'
CLIENT = 'client'
COOKIE = 'cookie'
HOST = 'host'
QUERY_STRING = 'query_string'
WHATAP_CTX = '__whatap__ctx'

logger = logging_module.getLogger(__name__)

def blocking_handler_async():
    def handler(func):
        from django.http import HttpResponse
        async def wrapper(*args, **kwargs):
            scope, headers = parseHeaders(args)
    
            if conf.throttle_enabled and scope and headers:
                remote_ip = parseRemoteAddr(scope, headers)
                path = scope.get(PATH)
                if throttle_util.isblocking(remote_ip, path):
                    if conf.reject_event_enabled:
                        ctx = TraceContextManager.getLocalContext()
                        if not ctx:
                            ctx = TraceContext()

                        throttle_util.sendrejectevent(ctx, path, remote_ip)
                    if conf.throttle_blocked_forward:
                        response = HttpResponse(status=302)
                        response['Location'] = conf.throttle_blocked_forward
                        return response
                    status = '403 Forbidden'
                    start_response= args[2]
                    start_response(status, [])
                    response = HttpResponse(content=conf.throttle_blocked_message, status=403)
                    return response
            return await func(*args, **kwargs)

        return wrapper

    return handler

def trace_handler_async(fn, start=False):
    def handler(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = TraceContextManager.getLocalContext()
            if not start and not ctx:
                return fn(*args, **kwargs)
            
            try:
                callback = await func(*args, **kwargs)
            except Exception as e:
                ctx = TraceContextManager.getLocalContext()
                if ctx and ctx.error_step ==e:
                    ctx.error_step= None
                    raise e
                logging.debug(e, extra={'id': 'WA917'}, exc_info=True)
                print(e, dict(extra={'id': 'WA917'}, exc_info=True))
                import traceback
                traceback.print_exc()
                
                return await fn(*args, **kwargs)
            else:
                if ctx and ctx.error_step:
                    e = ctx.error_step
                    ctx.error_step = None
                    raise e
                return callback
        
        return wrapper
    
    return handler

def instrument_handlers_async(module):
    def get_response_wrapper(fn):
        @trace_handler_async(fn, start=True)
        async def trace(*args, **kwargs):
            
            print('starting wrapped:', args, kwargs)
            # request = get_request_fromargs(args)
            startedAt = datetime.datetime.Now()
            callback = await fn(*args, **kwargs)

            print('elapsed:', datetime.datetime.now() - startedAt )
            return callback
        print('wrapper called')
        return trace

    if hasattr(module, 'BaseHandler') and hasattr(module.BaseHandler, 'get_response_async'):
        module.BaseHandler.get_response_async = get_response_wrapper(module.BaseHandler.get_response_async)
    
def parseHeaders(args):
    headers = {}
    if len(args) > SCOPE_ARGS_LENGTH:
        scope = args[1]
        if HEADER in scope:
            for arg in scope[HEADER]:
                if arg and len(arg) == 2 and arg[0] and arg[1]:
                    headers[arg[0].decode('utf8').lower()] = arg[1].decode('utf8')

        return scope, headers
    return None, None

def parseRemoteAddr(scope, headers):
    remoteIp = ''
    if CLIENT in scope:
        remoteIp = scope.get(CLIENT)[0]
        if conf.trace_http_client_ip_header_key:
            header_val = headers.get(conf.trace_http_client_ip_header_key, '')
            remoteIp = header_val.split(',')[0].strip()

    return remoteIp

def getUserId(scope, headers,  defValue):
    try:
        if conf.user_header_ticket:
            ticket = headers.get(conf.user_header_ticket, "")
            if  ticket:
                return hash_util.hashFromString(ticket), ticket
            return 0,""
        cookie = headers.get(COOKIE, "")
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

async def interceptor_async(fn, *args, **kwargs):
    
    scope, headers = parseHeaders(args)
    if scope == None and headers == None:
        return await fn(*args, **kwargs)
    
    ctx = TraceContext()
    ctx.host = headers.get(HOST, '').split(':')[0]
    ctx.service_name = scope.get(PATH)
    
    ctx.remoteIp = parseRemoteAddr(scope, headers)

    ctx.userAgentString = headers.get(USER_AGENT, '')
    ctx.referer = headers.get(REFERER, '')

    if conf.trace_user_enabled:
        if conf.trace_user_using_ip:
            ctx.userid = parseRemoteAddr(scope, headers)
        else:
            ctx.userid, ctx._rawuserid = getUserId(scope, headers, ctx.remoteIp)

    mstt = headers.get(
        conf._trace_mtrace_caller_key.lower().replace('-', '_'), '')
    
    if mstt:
        ctx.setTransfer(mstt)
        if conf.stat_mtrace_enabled:
            val = headers.get(
                conf._trace_mtrace_info_key.lower().replace('-', '_'), '')
            if val and len(val):
                ctx.setTransferInfo(val)
            pass

        myid = headers.get(
            conf._trace_mtrace_callee_key.lower().replace('-', '_'), '')
        if myid:
            ctx.setTxid(myid)
    caller_poid = headers.get(
        conf._trace_mtrace_caller_poid_key.upper().replace('-', '_'), '')
    
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
        scope[WHATAP_CTX]= ctx
        callback = await fn(*args, **kwargs)
        query_string = str(scope.get(QUERY_STRING, ''))
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
            for key, value in headers.items():
                keys.append(key)
            keys.sort()
            
            text = ''
            for key in keys:
                text += '{}={}\n'.format(key.lower(),
                                        headers[key])
            
            datas = ['HTTP-HEADERS', 'HTTP-HEADERS', text]
            ctx.start_time = DateUtil.nowSystem()
            async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)
    finally:
        if ctx:
            end_interceptor(ctx=ctx)
    
