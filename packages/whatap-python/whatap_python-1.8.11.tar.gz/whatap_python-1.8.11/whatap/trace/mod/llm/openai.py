import socket
import logging

from openai import OpenAIError

from whatap import DateUtil, conf
from whatap.pack import logSinkPack
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.trace.mod.application.wsgi import trace_handler

import whatap.io as whatapio
import whatap.net.async_sender as async_sender


def __send_llm_pack(metadata):
    try:
        ctx = TraceContextManager.getLocalContext()

        input_text = metadata.get("input_text", "")
        output_text = metadata.get("output_text", "")
        content = f"[REQUEST]{input_text}\n[RESPONSE]{output_text}"

        tags = {'@txid': str(ctx.id)} if ctx else {}
        fields = {}

        # 1. 기본 LLM 팩 데이터 구성
        llm_tags = {
            'ip': metadata.get('ip'),
            'host_name': metadata.get('host_name'),
            'model': metadata.get('model'),
            'stream': str(metadata.get('stream', False)),
            'success': str(metadata.get('success', False))
        }
        tags.update(llm_tags)

        llm_fields = {
            'prompt_tokens': metadata.get('prompt_tokens'),
            'completion_tokens': metadata.get('completion_tokens'),
            'total_tokens': metadata.get('total_tokens'),
        }

        fields.update(llm_fields)

        # 2. 에러 데이터 팩인지 확인
        if (metadata.get('error_type') == 'api_error'):
            error_fields = {
                "error": metadata.get('error'),
                "error_type": "api_error",
            }
            fields.update(error_fields)

        elif (metadata.get('error_type') == 'program_error'):
            error_fields = {
                "error": metadata.get('error'),
                "error_type": "program_error",
            }
            fields.update(error_fields)

        # 3. value 가 None 이 아닌 것들로 tags,fields 재구성
        tags = {k: v for k, v in tags.items() if v is not None}
        fields = {k: v for k, v in fields.items() if v is not None}

        p = logSinkPack.getLogSinkPack(
            t=DateUtil.now(),
            category="LLMResponse",
            tags=tags,
            fields=fields,
            line=DateUtil.now(),
            content=content
        )

        p.pcode = conf.PCODE
        bout = whatapio.DataOutputX()
        bout.writePack(p, None)
        packbytes = bout.toByteArray()
        try:
            async_sender.send_relaypack(packbytes)
        except Exception as e:
            logging.debug(str(e))
            pass

    except Exception as e:
        logging.debug(str(e))
        pass


def __streaming_response_wrapper(response_stream, metadata, prompt_tokens):
    collected_text = ""
    is_first_chunk = True
    #TODO
    """ 
    스트리밍 경우인 경우, completion_tokens 의 개수를 가져올 수 없기 때문에 토큰 계산 모듈을 통해, 추출하는 방법밖에 없음.
    현재 관련 로직에 대해서 개발된 바가 없기에 0으로 제공중임.
    """
    completion_tokens = 0
    try:
        for chunk in response_stream:
            if is_first_chunk:
                is_first_chunk = False

            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None) or ""
            collected_text += content
            yield chunk
    finally:
        metadata.update({
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "output_text": collected_text,
            "success": True,
        })
        __send_llm_pack(metadata)


def intercept_create(fn, *args, **kwargs):
    prompt_messages = kwargs.get("messages", [])
    model_name = kwargs.get("model")
    stream_flag = kwargs.get("stream", False)


    input_text = "".join([msg.get("content", "") or "" for msg in prompt_messages])


    metadata = {
        "ip": socket.gethostbyname(socket.gethostname()),
        "host_name": socket.gethostname(),
        "model": model_name,
        "input_text": input_text,
        "stream": stream_flag,
    }

    try:
        response = fn(*args, **kwargs)

        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", 0)
        completion_tokens = getattr(usage, "completion_tokens", 0)

    except OpenAIError as api_err:
        metadata.update({
            "success": False,
            "error": str(api_err),
            "error_type": "api_error"
        })
        __send_llm_pack(metadata)
        raise api_err

    except Exception as code_err:
        metadata.update({
            "success": False,
            "error": str(code_err),
            "error_type": "program_error"
        })
        __send_llm_pack(metadata)
        raise code_err

    if stream_flag:
        return __streaming_response_wrapper(response, metadata, prompt_tokens)

    try:
        response_text = "".join([choice.message.content or "" for choice in response.choices])
    except Exception as e:
        raise e

    metadata.update({
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "output_text": response_text,
        "success": True,
    })
    __send_llm_pack(metadata)

    if not hasattr(response, "choices"):
        logging.debug("The returned object doesn't have attribute which is 'choices'")

    return response


def instrument_openai(module):

    if not (conf.trace_llm_log_enabled):
        return

    def create_wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            return intercept_create(fn, *args, **kwargs)

        return trace


    if (hasattr(module, 'resources') and
            hasattr(module.resources, 'chat') and
            hasattr(module.resources.chat, 'completions') and
            hasattr(module.resources.chat.completions, 'Completions') and
            hasattr(module.resources.chat.completions.Completions, 'create')):
        original_create = module.resources.chat.completions.Completions.create
        module.resources.chat.completions.Completions.create = create_wrapper(original_create)