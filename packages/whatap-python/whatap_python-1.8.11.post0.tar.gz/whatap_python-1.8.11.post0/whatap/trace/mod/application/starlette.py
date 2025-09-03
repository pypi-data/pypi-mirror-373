import whatap.net.async_sender as async_sender
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil
from whatap.util.userid_util import UseridUtil as userid_util
from whatap.trace.mod.application.wsgi import interceptor_step_error, \
start_interceptor,end_interceptor
from whatap.conf.configure import Configure as conf
from typing import Any



def intercept_websocket(web_socket, data: str):
    try:
        ctx = TraceContext()

        scope = web_socket.scope
        headers = dict(scope.get("headers", []))  # headers는 리스트(tuple) 형태
        query_string = scope.get("query_string", b'').decode()
        client = scope.get("client", ("0.0.0.0", 0))

        # 기본 ctx 설정
        ctx.service_name = scope.get("path", "WebSocket")
        if query_string:
            ctx.service_name += f"?{query_string}"
        ctx.http_method = "WEBSOCKET"
        ctx.remoteIp = client[0]
        ctx.port = client[1]

        # User-Agent, Referer 추출 (바이트를 디코딩)
        ctx.userAgentString = headers.get(b'user-agent', b'').decode()
        ctx.referer = headers.get(b'referer', b'').decode()

        # userid 관련
        if conf.trace_user_enabled:
            if conf.trace_user_using_ip:
                ctx.userid = ctx.remoteIp
            else:
                ctx.userid, ctx._rawuserid = userid_util.getUserId([scope], ctx.remoteIp)

        # 트랜잭션 전파 관련
        mstt = headers.get(f"HTTP_{conf._trace_mtrace_caller_key}".encode(), b'').decode()
        if mstt:
            ctx.setTransfer(mstt)
            if conf.stat_mtrace_enabled:
                val = headers.get(f"HTTP_{conf._trace_mtrace_info_key}".encode(), b'').decode()
                if val:
                    ctx.setTransferInfo(val)
            txid = headers.get(f"HTTP_{conf._trace_mtrace_callee_key}".encode(), b'').decode()
            if txid:
                ctx.setTxid(txid)

        poid = headers.get(f"HTTP_{conf._trace_mtrace_caller_poid_key}".encode(), b'').decode()
        if poid:
            ctx.mcaller_poid = poid

        start_interceptor(ctx)

        start_time = DateUtil.nowSystem()
        ctx.start_time = start_time
        ctx.error = 0
        ctx.elapsed = 0

        datas = [ctx.remoteIp, ctx.port, ctx.elapsed, ctx.error]
        async_sender.send_packet(PacketTypeEnum.TX_WEB_SOCKET, ctx, datas)

    except Exception as e:
        interceptor_step_error(e)
    finally:
        end_interceptor(ctx=ctx)


def instrument_starlette_websocket(module):

    if not conf.trace_websocket_enabled:
        return

    OriginalWebSocket = module.WebSocket
    if getattr(OriginalWebSocket, "_whatap_patched", False):
        return

    #original_accept = OriginalWebSocket.accept
    original_send_text = OriginalWebSocket.send_text
    original_send_bytes = OriginalWebSocket.send_bytes
    original_send_json = OriginalWebSocket.send_json


    # # 연결 시점도 래핑은 하지만, APM 인터셉트는 하지 않음
    # async def wrapped_accept(self, *args, **kwargs):
    #     try:
    #         pass
    #     except Exception as e:
    #         interceptor_step_error(e)
    #     return await original_accept(self, *args, **kwargs)

    async def wrapped_send_text(self, data: str):
        try:
            intercept_websocket(self, data)
        except Exception as e:
            interceptor_step_error(e)
        return await original_send_text(self, data)

    async def wrapped_send_bytes(self, data: bytes):
        try:
            intercept_websocket(self, None)
        except Exception as e:
            interceptor_step_error(e)
        return await original_send_bytes(self, data)

    async def wrapped_send_json(self, data: Any):
        try:
            intercept_websocket(self, None)
        except Exception as e:
            interceptor_step_error(e)
        return await original_send_json(self, data)

    #OriginalWebSocket.accept = wrapped_accept
    OriginalWebSocket.send_text = wrapped_send_text
    OriginalWebSocket.send_bytes = wrapped_send_bytes
    OriginalWebSocket.send_json = wrapped_send_json
    OriginalWebSocket._whatap_patched = True



