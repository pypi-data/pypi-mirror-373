import traceback
from whatap.trace.mod.application.wsgi import interceptor, trace_handler, interceptor_error
from whatap.trace.trace_context_manager import TraceContextManager


def instrument(module):
    root = module.http.root
    AppClass = root.__class__
    original_call = AppClass.__call__

    def wrapper(fn):
        @trace_handler(fn, True)
        def trace(self, environ, start_response):
            def custom_start_response(status, headers, exc_info=None):
                ctx = TraceContextManager.getLocalContext()
                try:
                    ctx.status = int(status.split()[0])
                except:
                    ctx.status = 0
                return start_response(status, headers, exc_info)
            try:
                callback = interceptor(fn, self, environ, custom_start_response)
            except Exception as e:
                interceptor_error(
                    500 , #해당 status 값은 에러 처리용으로만 사용됩니다.
                    [e.__class__.__name__, str(e)]
                )
                raise
            return callback

        return trace

    AppClass.__call__ = wrapper(original_call)


    """ 
    Odoo 16+ HttpDispatcher.handle_error 패치
    """
    Dispatcher = getattr(module.http, 'HttpDispatcher', None)

    if Dispatcher:
        original_handle_error = Dispatcher.handle_error

        def wrapper(fn):
            @trace_handler(fn)
            def trace(self,exception):
                ctx = TraceContextManager.getLocalContext()
                interceptor_error(
                    500,  # 해당 status 값은 에러 처리용으로만 사용됩니다.
                    [exception.__class__.__name__,
                     str(exception)],
                    ctx=ctx
                )

                callback = fn(self, exception)
                return callback

            return trace
        Dispatcher.handle_error = wrapper(Dispatcher.handle_error)
