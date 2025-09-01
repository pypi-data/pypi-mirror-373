import sys
import atexit
import time
import traceback

import whatap.net.async_sender as async_sender

from functools import wraps

from whatap.conf.configure import Configure as conf
from whatap.util.date_util import DateUtil
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.trace.mod.application.wsgi import trace_handler
from whatap import logging

def trace_handler(fn, start=False, preload=None):
    def handler(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if preload:
                preload(*args, **kwargs)

            ctx = TraceContextManager.getLocalContext()
            if not start and not ctx:
                return fn(*args, **kwargs)
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

def load_transaction_patterns():
    raw = conf.standalone_transaction_patterns
    patterns = set(entry.strip() for entry in raw.split(",") if entry.strip())

    return patterns


def shutdown_agent():

    start_time = time.time()

    while not async_sender.q.empty():
        if time.time() - start_time > 3.0:
            break
        time.sleep(0.1)

    if async_sender.q.empty():
        return
    else:
        remaining_items = async_sender.q.qsize()

def end_interceptor(ctx):
    if not ctx:
        return

    if conf.dev:
        logging.debug(f'end   transaction id(seq): {ctx.id}', extra={'id': 'WA112'})
        print(f'end   transaction id(seq): {ctx.id}', dict(extra={'id': 'WA112'}))

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    datas = [ctx.host, ctx.service_name, ctx.mtid, ctx.mdepth, ctx.mcaller_txid,
             ctx.mcaller_pcode, ctx.mcaller_spec, str(ctx.mcaller_url_hash), ctx.mcaller_poid, ctx.status]

    ctx.elapsed = DateUtil.nowSystem() - start_time

    async_sender.send_packet(PacketTypeEnum.TX_END, ctx, datas)


def start_interceptor(ctx):
    if conf.dev:
        logging.debug(f'start transaction id(seq): {ctx.id}', extra={'id': 'WA111'})
        print(f'start transaction id(seq): {ctx.id}', dict(extra={'id': 'WA111'}))

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    datas = [ctx.host, ctx.service_name, ctx.remoteIp, ctx.userAgentString,
             ctx.referer, ctx.userid, ctx.isStaticContents, ctx.http_method]

    async_sender.send_packet(PacketTypeEnum.TX_START, ctx, datas)

def error_interceptor(error_msg,error_type,ctx):
    if not ctx:
        ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return
    if not ctx.error:
        ctx.error = 1

    error = ''
    errors = []
    errors.append(error_type)
    errors.append(error_msg)

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

    async_sender.send_packet(PacketTypeEnum.TX_ERROR, ctx, errors)

    if conf.profile_exception_stack:
        desc = '\n'.join(errors)
        datas = [' ', ' ', desc]
        ctx.start_time = DateUtil.nowSystem()
        async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)

def instrument_standalone_multiple():
    atexit.register(shutdown_agent)

    patterns = load_transaction_patterns()
    targets_to_patch = {tuple(entry.split(":", 1)) for entry in patterns}

    tracked_methods = set()
    tracked_funcs = set()
    modules = set()


    for entry in patterns:
        mod, target = entry.split(":", 1)
        if "." in target:
            cls, mtd = target.split(".", 1)
            tracked_methods.add((mod, cls, mtd))
        else:
            func = target
            tracked_funcs.add((mod, func))

        modules.add(mod)

    def wrapper(fn, module_name, target_name):
        @trace_handler(fn, start=True)
        def trace(*args, **kwargs):
            prev_ctx = TraceContextManager.getLocalContext()
            ctx = TraceContext()
            ctx.service_name = f"{module_name}:{target_name}"
            start_interceptor(ctx)
            try:
                callback = fn(*args, **kwargs)
                return callback
            except Exception as e:
                error_msg = str(e)
                error_type = e.__class__.__name__
                error_interceptor(error_msg,error_type,ctx)
                raise e
            finally:
                end_interceptor(ctx)
                TraceContextManager.setLocalContext(prev_ctx)

        return trace



    patching_queue = []
    sys_trace_current_service_name = None

    def trace_and_patch_profiler(frame, event, arg):
        global sys_trace_current_service_name

        if not targets_to_patch and not patching_queue:
            pass

        module_name = frame.f_globals.get("__name__")
        if module_name not in (modules) or event not in ("call", "return","exception"):
            return trace_and_patch_profiler

        fn_name = frame.f_code.co_name
        is_method = "self" in frame.f_locals

        is_target = False
        full_target_name = fn_name
        target_tuple = None

        if is_method:
            cls_name = type(frame.f_locals["self"]).__name__
            full_target_name = f"{cls_name}.{fn_name}"
            if (module_name, cls_name, fn_name) in tracked_methods:
                is_target = True
                target_tuple = (module_name, full_target_name)
        else:
            if (module_name, fn_name) in tracked_funcs:
                is_target = True
                target_tuple = (module_name, full_target_name)

        if target_tuple in targets_to_patch:
            if event == "call":
                if not is_target:
                    return trace_and_patch_profiler

                prev_ctx = TraceContextManager.getLocalContext()
                if prev_ctx:
                    patching_queue.append(prev_ctx)

                ctx = TraceContext()
                ctx.service_name = f"{module_name}:{full_target_name}"
                sys_trace_current_service_name = ctx.service_name

                TraceContextManager.setLocalContext(ctx)
                start_interceptor(ctx)

                try:
                    module_obj = sys.modules[module_name]
                    if is_method:
                        cls_name, mtd_name = target_tuple[1].split('.', 1)
                        cls_obj = getattr(module_obj, cls_name)
                        fn = getattr(cls_obj, mtd_name)
                        wrapped_fn = wrapper(fn, module_name, target_tuple[1])
                        setattr(cls_obj, mtd_name, wrapped_fn)
                    else:
                        func_name = target_tuple[1]
                        fn = getattr(module_obj, func_name)
                        wrapped_fn = wrapper(fn, module_name, func_name)
                        setattr(module_obj, func_name, wrapped_fn)

                    targets_to_patch.remove(target_tuple)



                except (AttributeError, KeyError) as e:
                    if target_tuple in targets_to_patch:
                        targets_to_patch.remove(target_tuple)

        if event == "return":
            ctx = TraceContextManager.getLocalContext()
            if ctx and sys_trace_current_service_name == f"{module_name}:{full_target_name}":
                end_interceptor(ctx)
                if patching_queue:
                    prev_ctx = patching_queue.pop()
                    TraceContextManager.setLocalContext(prev_ctx)
                    sys_trace_current_service_name = prev_ctx.service_name
                else:
                    if not(targets_to_patch):
                        sys.settrace(None)

        if event == "exception":
            ctx = TraceContextManager.getLocalContext()
            if ctx and sys_trace_current_service_name == f"{module_name}:{full_target_name}":
                exc_type, exc_value , tb = arg
                error_interceptor(exc_value,exc_type,ctx)
                end_interceptor(ctx)
                if patching_queue:
                    prev_ctx = patching_queue.pop()
                    TraceContextManager.setLocalContext(prev_ctx)
                    sys_trace_current_service_name = prev_ctx.service_name
                else:
                    if not (targets_to_patch):
                        sys.settrace(None)

        return trace_and_patch_profiler

    sys.settrace(trace_and_patch_profiler)