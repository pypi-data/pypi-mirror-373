from whatap.trace.mod.application.wsgi import trace_handler
from whatap.trace.mod.database.util import interceptor_db_con, interceptor_db_execute, interceptor_db_close

class CursorProxy:
    def __init__(self, real_cursor, db_info):
        self._cur = real_cursor
        self._db_info = db_info

    def execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        def safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return original_execute_method(*args, **kwargs)

        return safe_execute

    def execute(self, *args, **kwargs):
        safe_fn = self.execute_wrapper(self._cur.execute)
        callback = interceptor_db_execute(safe_fn, self._db_info, self._cur, *args, **kwargs)
        return callback

    def executemany(self, *args, **kwargs):
        safe_fn = self.execute_wrapper(self._cur.executemany)
        callback = interceptor_db_execute(safe_fn, self._db_info, self._cur, *args, **kwargs)
        return callback

    def close(self, *args, **kwargs):
        callback = self._cur.close(*args, **kwargs)
        return callback

    def __enter__(self):
        self._cur.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._cur.__exit__(exc_type, exc_val, exc_tb)

    def __getattr__(self, name):
        return getattr(self._cur, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            setattr(self._cur, name, value)

class ConnectionProxy:
    def __init__(self, real_connection, db_info):
        self._real_connection = real_connection
        self._db_info = db_info

    def execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        def safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return original_execute_method(*args, **kwargs)

        return safe_execute

    def execute(self, *args, **kwargs):
        real_cursor = self._real_connection.cursor()
        safe_fn = self.execute_wrapper(real_cursor.execute)
        callback = interceptor_db_execute(safe_fn,self._db_info,real_cursor,*args,**kwargs)
        return callback

    def executemany(self, *args, **kwargs):
        real_cursor = self._real_connection.cursor()
        safe_fn = self.execute_wrapper(real_cursor.executemany)
        callback = interceptor_db_execute(safe_fn, self._db_info, real_cursor, *args, **kwargs)
        return callback

    def executescript(self, *args, **kwargs):
        real_cursor = self._real_connection.cursor()
        safe_fn = self.execute_wrapper(real_cursor.executescript)
        callback = interceptor_db_execute(safe_fn, self._db_info, real_cursor, *args, **kwargs)
        return callback

    def cursor(self, *args, **kwargs):
        real_cursor = self._real_connection.cursor(*args, **kwargs)
        return CursorProxy(real_cursor, self._db_info)

    def close(self, *args, **kwargs):
        callback = interceptor_db_close(self._real_connection.close, *args, **kwargs)
        return callback

    def __getattr__(self, name):
        return getattr(self._real_connection, name)

    def __enter__(self):
        self._real_connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._real_connection.__exit__(exc_type, exc_val, exc_tb)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            setattr(self._real_connection, name, value)


def instrument_sqlite3(module):

    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            if args:
                kwargs['database'] = args[0]
                args = args[1:]

            db_name = kwargs.get('database', 'unknown')
            db_info = {'type': 'sqlite', 'db': db_name}
            db_info.update(kwargs)

            real_connection = interceptor_db_con(fn, db_info, *args, **kwargs)

            if real_connection:
                return ConnectionProxy(real_connection, db_info)

            return real_connection

        return trace

    if hasattr(module, "connect"):
        module.connect = wrapper(module.connect)