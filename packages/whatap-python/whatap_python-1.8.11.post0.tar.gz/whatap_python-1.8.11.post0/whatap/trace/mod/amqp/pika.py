from whatap.trace import get_dict
from whatap.trace.mod.application.wsgi import trace_handler, \
    interceptor_step_error, start_interceptor, end_interceptor
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
import whatap.net.async_sender as async_sender
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil


def parseConnection(conn):
    connstr = ''
    if conn.host:
        connstr += conn.host
    if conn.virtual_host:
        connstr += "/" + conn.virtual_host
    return connstr


def intercept_publish(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    text = 'rabbitmq://'
    text += parseConnection(args[0].connection.params)
    text += '?exchage='
    text += kwargs['exchange']
    text += '&routing='
    text += kwargs['routing_key']
    ctx.active_dbc = text
    ctx.lctx['dbc'] = text

    try:
        result = fn(*args, **kwargs)

        ctx.active_dbc = 0
        ctx.db_opening = True
        ctx.elapsed = DateUtil.nowSystem() - start_time
        datas = [' ', ' ', 'MQ SESSION INFO: ' + text]
        async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)

        return result
    except Exception as e:
        ctx.active_dbc = 0
        ctx.db_opening = False
        ctx.elapsed = DateUtil.nowSystem() - start_time
        raise e


def instrument_pika(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            return intercept_publish(fn, *args, **kwargs)

        return trace

    if hasattr(module, 'Channel') and hasattr(module.Channel, 'basic_publish'):
        module.Channel.basic_publish = wrapper(module.Channel.basic_publish)