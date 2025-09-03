import traceback

import sys

from whatap.conf.configure import Configure as conf
from whatap.net.packet_type_enum import PacketTypeEnum
import whatap.net.async_sender as async_sender
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.util.date_util import DateUtil
from whatap.util.hash_util import HashUtil
from whatap.util.userid_util import UseridUtil as userid_util
from functools import wraps
from whatap import logging
import re

from whatap.util.hexa32 import Hexa32

import traceback, threading


def isEventlet():
    greenlet = sys.modules.get('greenlet')

    if greenlet:
        current = greenlet.getcurrent()
        if current is not None and current.parent:
            print('thread:', threading.get_ident(), 'greenlet:', id(current.parent))
            traceback.print_stack()
            return True
    else:
        return False


def sendDebugProfile(ctx, msg):
    if ctx:
        ctx.elapsed = 0
        datas = [' ', ' ', 'DEBUG: ' + msg]
        async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)


def trace_handler(fn, start=False, preload=None):
    def handler(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if preload:
                preload(*args, **kwargs)
            # if isEventlet():
            #     print("trace_handler: greenlet found")
            # else:
            #     print("trace_handler: greenlet not found")
            ctx = TraceContextManager.getLocalContext()
            # print("trace_handler ctx:", ctx)
            if not start and not ctx:
                return fn(*args, **kwargs)

            # check raise step error
            # if ctx and ctx.error_step:
            #     end_interceptor(ctx=ctx)
            #     raise Exception(ctx.error_step)

            try:
                callback = func(*args, **kwargs)
            except Exception as e:
                if ctx and ctx.error_step == e:
                    ctx.error_step = None
                    raise e
                raise
            else:
                if ctx and ctx.error_step:
                    e = ctx.error_step
                    ctx.error_step = None
                    raise e
                return callback

        return wrapper

    return handler

def async_trace_handler(fn, start=False, preload=None):
    def handler(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if preload:
                preload(*args, **kwargs)

            ctx = TraceContextManager.getLocalContext()

            if not start and not ctx:
                return await fn(*args, **kwargs)

            try:
                callback = await func(*args, **kwargs)
            except Exception as e:
                if ctx and ctx.error_step == e:
                    ctx.error_step = None
                    raise e
                raise
            else:
                if ctx and ctx.error_step:
                    e = ctx.error_step
                    ctx.error_step = None
                    raise e
                return callback

        return wrapper

    return handler


def start_interceptor(ctx):
    if conf.dev:
        logging.debug('start transaction id(seq): {}'.format(ctx.id),
                      extra={'id': 'WA111'})
        print('start transaction id(seq): {}'.format(ctx.id), dict(extra={'id': 'WA111'}))

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    if ctx.service_name and not ctx.service_hash:
        ctx.service_hash = HashUtil.hashFromString(ctx.service_name)

    datas = [ctx.host,
             ctx.service_name,
             ctx.remoteIp,
             ctx.userAgentString,
             ctx.referer,
             ctx.userid,
             ctx.isStaticContents,
             ctx.http_method
             ]
    # print("start_interceptor txid:", ctx.id)
    async_sender.send_packet(PacketTypeEnum.TX_START, ctx, datas)

    return ctx


def end_interceptor(thread_id=None, ctx=None):
    if not ctx:
        ctx = TraceContextManager.getContext(
            thread_id) if thread_id else TraceContextManager.getLocalContext()
    if not ctx:
        return

    if conf.dev:
        logging.debug('end   transaction id(seq): {}'.format(ctx.id),
                      extra={'id': 'WA112'})
        print('end   transaction id(seq): {}'.format(ctx.id),
              dict(extra={'id': 'WA112'}))

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    datas = [ctx.host, ctx.service_name, ctx.mtid, ctx.mdepth, ctx.mcaller_txid,
             ctx.mcaller_pcode, ctx.mcaller_spec, str(ctx.mcaller_url_hash), ctx.mcaller_poid,ctx.status]
    ctx.elapsed = DateUtil.nowSystem() - start_time

    async_sender.send_packet(PacketTypeEnum.TX_END, ctx, datas)


def parseServiceName(environ):
    return environ.get('PATH_INFO', '')


def isIgnore(service_name):
    if conf.trace_ignore_url_prefix and service_name.startswith(conf.trace_ignore_url_prefix):
        return True

    if conf.trace_ignore_url_set and service_name in conf.trace_ignore_url_set:
        return True

    return False


def interceptor(rn_environ, *args, **kwargs):
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
            return fn(*args, **kwargs)
    except Exception as e:
        pass

    start_interceptor(ctx)

    try:

        callback = fn(*args, **kwargs)
        query_string = environ.get('QUERY_STRING', '')
        if query_string:
            ctx.service_name += '?{}'.format(query_string)

        if ctx.service_name.find('.') > -1 and ctx.service_name.split('.')[
            1] in conf.web_static_content_extensions:
            ctx.isStaticContents = 'true'

        if getattr(callback, 'status_code', None):
            status_code = callback.status_code

            if (status_code >= 400):
                errors = [callback.__class__.__name__, callback.reason_phrase]
                interceptor_error(status_code, errors, ctx=ctx)

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


def interceptor_error(status_code, errors, ctx=None):
    if not ctx:
        ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return
    ctx.status = status_code
    if status_code >= 400 and not ctx.error:
        ctx.error = 1

        error = ''
        frame = sys._current_frames().get(ctx.thread.ident)
        if not frame:
            return

        for stack in traceback.extract_stack(frame):
            line = stack[0]
            line_num = stack[1]
            method_name = stack[2]

            if line.find('/whatap/trace') > -1 or line.find(
                    '/threading.py') > -1:
                continue
            error += '{} ({}:{})\n'.format(method_name, line, line_num)

        errors.append(error)

        # errors.append(''.join(traceback.format_list(traceback.extract_stack(sys._current_frames()[ctx.thread.ident]))))
        async_sender.send_packet(PacketTypeEnum.TX_ERROR, ctx, errors)


def interceptor_step_error(e, ctx=None):
    from whatap.trace.mod.database.util import extract_db_error_message
    if not ctx:
        ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return
    ctx.error_step = e
    if not ctx.error:
        ctx.error = 1

    errors = []
    errors.append(e.__class__.__name__)

    error_message = extract_db_error_message(e)
    errors.append(error_message)

    error = ''
    frame = sys._current_frames().get(ctx.thread.ident)
    if not frame:
        return

    for stack in traceback.extract_stack(frame):
        line = stack[0]
        line_num = stack[1]
        method_name = stack[2]

        if line.find('/whatap/trace') > -1 or line.find('/threading.py') > -1:
            continue
        error += '{} ({}:{})\n'.format(method_name, line, line_num)

    errors.append(error)
    async_sender.send_packet(PacketTypeEnum.TX_ERROR, ctx, errors)

    if conf.profile_exception_stack:
        desc = '\n'.join(errors)
        datas = [' ', ' ', desc]
        ctx.start_time = DateUtil.nowSystem()
        async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)




def interceptor_httpc_request(fn, httpc_url, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    if not ctx or ctx.active_httpc_hash:
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            interceptor_step_error(e, ctx=ctx)
        finally:
            return
    param = None
    method = None
    if httpc_url.find('?') > -1:
        httpc_url, param = httpc_url.split('?')

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    ctx.httpc_url = httpc_url
    ctx.active_httpc_hash = ctx.httpc_url

    try:
        try:
            callback = fn(*args, **kwargs)
            return callback
        except TypeError as e:
            callback = fn(*args)
            return callback
    except Exception as e:
        interceptor_step_error(e, ctx=ctx)
    finally:
        # ctx = TraceContextManager.getLocalContext()
        datas = [ctx.httpc_url, ctx.mcallee]
        ctx.elapsed = DateUtil.nowSystem() - start_time
        async_sender.send_packet(PacketTypeEnum.TX_HTTPC, ctx, datas)

        if conf.profile_http_parameter_enabled:
            if type(args[1]) == dict:
                param = (args[1].body if 'body' in args[1] else args[1]) or param
                method = args[1].method if 'method' in args[1] else args[1]

            if param:
                datas = ['HTTP-PARAMETERS', method, param]
                ctx.start_time = DateUtil.nowSystem()
                async_sender.send_packet(PacketTypeEnum.TX_SECURE_MSG, ctx, datas)

        ctx.active_httpc_hash = 0
        ctx.httpc_url = None


def interceptor_sock_connect(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return fn(*args, **kwargs)

    try:
        ctx.socket_connecting = True
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        ctx.socket_connecting = False


check_seq = 1


def inter_tx_trace_auto_on(ctx):
    try:
        if isinstance(conf.mtrace_rate, str):
            conf.mtrace_rate = int(conf.mtrace_rate)
    except ValueError:
        conf.mtrace_rate = 0
    finally:
        if conf.mtrace_rate <= 0 or ctx.httpc_checked or ctx.mtid != 0:
            return

        ctx.httpc_checked = True

        try:
            inter_tx_trace_auto_on.check_seq += 1
        except AttributeError:
            inter_tx_trace_auto_on.check_seq = 1
        finally:
            check_seq = inter_tx_trace_auto_on.check_seq

            rate = int(conf.mtrace_rate / 10)
            if rate == 10:
                ctx.mtid = TraceContextManager.getId()
            elif rate == 9:
                if check_seq % 10 != 0:
                    ctx.mtid = TraceContextManager.getId()
            elif rate == 8:
                if check_seq % 5 != 0:
                    ctx.mtid = TraceContextManager.getId()
            elif rate == 7:
                if check_seq % 4 != 0:
                    ctx.mtid = TraceContextManager.getId()
            elif rate == 6:
                if check_seq % 3 != 0:
                    ctx.mtid = TraceContextManager.getId()
            elif rate == 5:
                if check_seq % 2 == 0:
                    ctx.mtid = TraceContextManager.getId()
            elif rate == 4:
                if check_seq % 3 == 0 or check_seq % 5 == 0:
                    ctx.mtid = TraceContextManager.getId()
            elif rate == 3:
                if check_seq % 4 == 0 or check_seq % 5 == 0:
                    ctx.mtid = TraceContextManager.getId()
            elif rate == 2:
                if check_seq % 5 == 0:
                    ctx.mtid = TraceContextManager.getId()
            elif rate == 1:
                if check_seq % 10 == 0:
                    ctx.mtid = TraceContextManager.getId()


def transfer(headers):
    ctx = TraceContextManager.getLocalContext()

    if not ctx.mtid:
        inter_tx_trace_auto_on(ctx)

    if ctx.mtid:
        headers[conf._trace_mtrace_caller_key] = ctx.transfer()
        if conf.stat_mtrace_enabled:
            headers[conf._trace_mtrace_info_key] = ctx.transferInfo()

        ctx.mcallee = TraceContextManager.getId()
        headers[conf._trace_mtrace_callee_key] = Hexa32.toString32(ctx.mcallee)
        headers[conf._trace_mtrace_caller_poid_key] = ctx.transferPOID()
    return headers
