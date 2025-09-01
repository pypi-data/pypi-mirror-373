from whatap.trace import get_dict
from whatap.trace.mod.application.wsgi import trace_handler
from whatap.trace.mod.database.util import interceptor_db_con, interceptor_db_execute, interceptor_db_close

db_info = {}

def instrument_psycopg2(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            global db_info
            db_info = {'type': 'postgresql'}
            db_info.update(kwargs)
            callback = interceptor_db_con(fn, db_info, *args, **kwargs)
            return callback

        return trace

    module.connect = wrapper(module.connect)


def instrument_psycopg2_connection(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_close(fn, *args, **kwargs)
            return callback

        return trace

    get_dict(module.connection)['close'] = wrapper(module.connection.close)


def instrument_psycopg2_extensions(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_execute(fn, db_info, *args, **kwargs)
            return callback

        return trace

    get_dict(module.cursor)['execute'] = wrapper(module.cursor.execute)
