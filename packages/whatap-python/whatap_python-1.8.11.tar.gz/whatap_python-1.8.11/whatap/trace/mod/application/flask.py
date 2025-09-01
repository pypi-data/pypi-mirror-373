from whatap.trace.mod.application.wsgi import interceptor, trace_handler, \
    interceptor_error
from whatap.trace.trace_context_manager import TraceContextManager

def instrument(module):
    def wrapper(fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            flask_instance = args[0]
            environ = args[1]
            original_start_response = args[2]

            def custom_start_response(status, response_headers, exc_info=None):
                ctx = TraceContextManager.getLocalContext()
                ctx.status = status[:3]
                return original_start_response(status, response_headers, exc_info)

            new_args = (flask_instance, environ, custom_start_response)
            callback = interceptor(fn, *new_args, **kwargs)
            return callback
        
        return trace
    
    module.Flask.wsgi_app = wrapper(module.Flask.wsgi_app)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            from werkzeug.exceptions import HTTPException
            callback = fn(*args, **kwargs)
            if callback is None:
                e = args[1]
                errors = [e.__class__.__name__]
                status_code = getattr(e, 'code', 500)
                #Flask 레이어의 예외 처리
                if isinstance(e, HTTPException):
                    errors.append(e.description)

                #Flask 예외 객체가 아닌 경우의 예외처리
                #에러 코드와 메세지가 함께 나타날 수 있음.
                else:
                    status_code = 500
                    errors.append(str(e))
                interceptor_error(status_code, errors)

            return callback

        return trace
    if hasattr(module.Flask, '_find_error_handler'):
        module.Flask._find_error_handler = wrapper(
            module.Flask._find_error_handler)
