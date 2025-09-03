import copy
import queue, time, threading
from . import udp_session
from whatap.conf.configure import Configure as conf
from whatap.trace.simple_trace_context import SimpleTraceContext

q = queue.Queue(conf.max_send_queue_size)

from enum import Enum
class SendType(Enum):
    DATAS = 1
    RELAY = 2

def send_packet( packet_type, ctx, datas=[]):
    ctx = SimpleTraceContext(ctx)

    # deep coopy TraceContext object before adding it to the queue, preventing potential data overwriting issues caused by concurrent modifications
    copied_ctx = ctx.getDeepCopiedContext()
    _initThread()
    global q
    if q.full():
        return
    q.put((SendType.DATAS, (packet_type, copied_ctx, datas)))

def send_relaypack( packbytes):
    _initThread()
    global q
    if q.full():
        return
    q.put((SendType.RELAY, packbytes))

def startWhatapThread():
    def __sendPackets():
        global q
        while True:
            packet_env = q.get()
            if not packet_env:
                time.sleep(0.1)
                continue
            sendType,params = packet_env
            if sendType == SendType.DATAS:
                packet_type, ctx, datas = params
                udp_session.UdpSession.send_packet(packet_type, ctx, datas)
            elif sendType == SendType.RELAY:
                packbytes = params
                udp_session.UdpSession.send_relaypack(packbytes)    
    t = threading.Thread(target=__sendPackets)
    t.setDaemon(True)
    t.start()

_lock = threading.Lock()
_initialized = False

def _initThread():
    global _lock, _initialized
    if _initialized:
        return
    try:
        if _initialized:
            return
        _lock.acquire()
        if _initialized:
            return
        _initialized=True
        startWhatapThread()
    finally:
        _lock.release()

