from whatap.trace.mod.application.wsgi import transfer, trace_handler, \
    interceptor_httpc_request


def instrument_httpx(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            request = args[1]
            request.headers = transfer(request.headers)

            httpc_url = str(request.url)
            callback = interceptor_httpc_request(fn, httpc_url, *args, **kwargs)

            return callback

        return trace

    if hasattr(module, 'Client') and hasattr(module.Client, 'send'):
        module.Client.send = wrapper(module.Client.send)


    if hasattr(module, 'AsyncClient') and hasattr(module.AsyncClient, 'send'):
        module.AsyncClient.send = wrapper(module.AsyncClient.send)