import atexit
import sys
import traceback
import time

from whatap.conf.configure import Configure as conf
from whatap.util.date_util import DateUtil
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
import whatap.net.async_sender as async_sender
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap import logging


ctx = None


def global_exception_handler(exc_type, exc_value, exc_traceback):

    global ctx
    traceback.print_exception(exc_type, exc_value, exc_traceback)

    standalone_error(exc_value, ctx)

sys.excepthook = global_exception_handler


def standalone_error(e, ctx=None):
    
    if not ctx:
        ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return

    ctx.error_step = e
    if not ctx.error:
        ctx.error = 1

    errors = []
    errors.append(e.__class__.__name__)

    error_message = str(e)
    errors.append(error_message)

    error_stack = ''
    frame = sys._current_frames().get(ctx.thread.ident)
    if not frame:
        return

    for stack in traceback.extract_stack(frame):
        if '/whatap/trace' in stack.filename or '/threading.py' in stack.filename:
            continue
        error_stack += f'{stack.name} ({stack.filename}:{stack.lineno})\n'

    errors.append(error_stack)
    async_sender.send_packet(PacketTypeEnum.TX_ERROR, ctx, errors)
    if conf.profile_exception_stack:
        desc = '\n'.join(errors)
        datas = [' ', ' ', desc]
        ctx.start_time = DateUtil.nowSystem()
        async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)
        
    


@atexit.register
def standalone_end():
    global ctx
    ctx = ctx

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

    shutdown_start_time = time.time()
    while not async_sender.q.empty():
        if time.time() - shutdown_start_time > 3.0:
            break
        time.sleep(0.1)



def instrument_standalone_single():
    global ctx

    ctx = TraceContext()
    ctx = ctx
    if conf.dev:
        logging.debug('start transaction id(seq): {}'.format(ctx.id),
                      extra={'id': 'WA111'})
        print('start transaction id(seq): {}'.format(ctx.id), dict(extra={'id': 'WA111'}))

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    ctx.service_name = sys.argv[0]

    datas = [ctx.host,
             ctx.service_name,
             ctx.remoteIp,
             ctx.userAgentString,
             ctx.referer,
             ctx.userid,
             ctx.isStaticContents,
             ctx.http_method
             ]

    
    async_sender.send_packet(PacketTypeEnum.TX_START, ctx, datas)