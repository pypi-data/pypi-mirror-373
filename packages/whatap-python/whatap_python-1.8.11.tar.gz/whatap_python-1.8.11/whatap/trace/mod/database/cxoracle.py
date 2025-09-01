from whatap.trace import get_dict
from whatap.trace.mod.application.wsgi import trace_handler
from whatap.trace.mod.database.util import interceptor_db_con, interceptor_db_execute, interceptor_db_close

db_info = {}


def instrument_oracle_client(module):

    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            global db_info
            db_info = {'type': 'oracle'}
            db_info.update(kwargs)
            callback = interceptor_db_con(fn, db_info, *args, **kwargs)
            return callback

        return trace

    if hasattr(module, "connect"):
        module.connect = wrapper(module.connect)

    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_close(fn, *args, **kwargs)
            return callback

        return trace

    if hasattr(module, "Connection") and hasattr(module.Connection, "close"):
        get_dict(module.Connection)['close'] = wrapper(
            module.Connection.close)

    # def wrapper(fn):
    #     @trace_handler(fn)
    #     def trace(*args, **kwargs):
    #         callback = interceptor_db_execute(fn, db_info, *args, **kwargs)
    #         return callback
    #
    #     return trace
    #
    # if hasattr(module, 'Cursor') and hasattr(module.Cursor, "execute"):
    #     get_dict(module.Cursor)['execute'] = wrapper(module.Cursor.execute)



