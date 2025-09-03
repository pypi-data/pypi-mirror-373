import inspect

from whatap.trace.mod.application.wsgi import trace_handler , async_trace_handler
from whatap.trace.mod.database.util import (
    interceptor_db_con, interceptor_db_execute, interceptor_db_close,
    async_interceptor_db_con, async_interceptor_db_execute, async_interceptor_db_close,
    interceptor_pool_get, interceptor_pool_release,
    async_interceptor_pool_get, async_interceptor_pool_release
)

db_info = {}


class BaseCursor:
    def __init__(self, cursor, db_info):
        self._cursor = cursor
        self._db_info = db_info
        self._is_wrapped = True

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            setattr(self._cursor, name, value)

    @property
    def connection(self):
        return self._cursor.connection

    def _execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        def safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return original_execute_method(*args, **kwargs)

        return safe_execute


class SyncCursor(BaseCursor):
    def __enter__(self):
        self._cursor.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._cursor.__exit__(exc_type, exc_val, exc_tb)

    def execute(self, *args, **kwargs):
        if hasattr(self._cursor, '_is_wrapped'):
            return self._cursor.execute(*args, **kwargs)
        real_execute = self._cursor.execute
        safe_fn = self._execute_wrapper(real_execute)
        return interceptor_db_execute(safe_fn, self._db_info, self._cursor, *args, **kwargs)

    def executemany(self, *args, **kwargs):
        if hasattr(self._cursor, '_is_wrapped'):
            return self._cursor.executemany(*args, **kwargs)
        real_executemany = getattr(self._cursor, "executemany", None)
        if real_executemany is None:
            return self._cursor.executemany(*args, **kwargs)
        safe_fn = self._execute_wrapper(real_executemany)
        return interceptor_db_execute(safe_fn, self._db_info, self._cursor, *args, **kwargs)


class AsyncCursor(BaseCursor):
    async def __aenter__(self):
        await self._cursor.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._cursor.__aexit__(exc_type, exc_val, exc_tb)

    def _async_execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        async def async_safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return await original_execute_method(*args, **kwargs)

        return async_safe_execute

    async def execute(self, *args, **kwargs):
        if hasattr(self._cursor, '_is_wrapped'):
            return await self._cursor.execute(*args, **kwargs)
        real_execute = self._cursor.execute
        safe_fn = self._async_execute_wrapper(real_execute)
        return await async_interceptor_db_execute(safe_fn, self._db_info, self._cursor, *args, **kwargs)

    async def executemany(self, *args, **kwargs):
        if hasattr(self._cursor, '_is_wrapped'):
            return await self._cursor.executemany(*args, **kwargs)
        real_executemany = getattr(self._cursor, "executemany", None)
        if real_executemany is None:
            return await self._cursor.executemany(*args, **kwargs)
        safe_fn = self._async_execute_wrapper(real_executemany)
        return await async_interceptor_db_execute(safe_fn, self._db_info, self._cursor, *args, **kwargs)


class BaseConnection:
    def __init__(self, connection, db_info):
        self._connection = connection
        self._db_info = db_info
        self._is_wrapped = True

    def __getattr__(self, name):
        return getattr(self._connection, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            setattr(self._connection, name, value)

    def _execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        def safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return original_execute_method(*args, **kwargs)

        return safe_execute


class SyncConnection(BaseConnection):
    def __enter__(self):
        self._connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._connection.__exit__(exc_type, exc_val, exc_tb)

    def close(self, *args, **kwargs):
        if self._db_info.get("pool"):
            interceptor_pool_release()
            return self._connection.close(*args, **kwargs)

        real_close = self._connection.close
        return interceptor_db_close(real_close, *args, **kwargs)

    def cursor(self, *args, **kwargs):
        real_cursor = self._connection.cursor(*args, **kwargs)
        if hasattr(real_cursor, '_is_wrapped'):
            return real_cursor
        return SyncCursor(real_cursor, self._db_info)

    def execute(self, *args, **kwargs):
        if hasattr(self._connection, '_is_wrapped'):
            return self._connection.execute(*args, **kwargs)
        real_execute = getattr(self._connection, "execute", None)
        if real_execute is None:
            return self._connection.execute(*args, **kwargs)
        safe_fn = self._execute_wrapper(real_execute)
        return interceptor_db_execute(safe_fn, self._db_info, self._connection, *args, **kwargs)


class AsyncConnection(BaseConnection):
    async def __aenter__(self):
        await self._connection.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._connection.__aexit__(exc_type, exc_val, exc_tb)

    def cursor(self, *args, **kwargs):
        real_cursor = self._connection.cursor(*args, **kwargs)
        if hasattr(real_cursor, '_is_wrapped'):
            return real_cursor
        return AsyncCursor(real_cursor, self._db_info)

    def _async_execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        async def async_safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return await original_execute_method(*args, **kwargs)

        return async_safe_execute

    async def execute(self, *args, **kwargs):
        if hasattr(self._connection, '_is_wrapped'):
            return await self._connection.execute(*args, **kwargs)
        real_execute = getattr(self._connection, "execute", None)
        if real_execute is None:
            return await self._connection.execute(*args, **kwargs)
        safe_fn = self._async_execute_wrapper(real_execute)
        return await async_interceptor_db_execute(safe_fn, self._db_info, self._connection, *args, **kwargs)

    async def close(self, *args, **kwargs):
        if self._db_info.get("pool"):
            await async_interceptor_pool_release()
            return await self._connection.close(*args, **kwargs)

        real_close = self._connection.close
        return await async_interceptor_db_close(real_close, *args, **kwargs)


def _is_called_by_pool():
    try:
        # 실제로 psycopg_pool은 보통 3-4 레벨 내에서 호출되므로 깊이 5로 결정.
        filenames = [f.filename for f in inspect.stack(context=0)[2:7]]
        return any('psycopg_pool' in f for f in filenames if f)
    except Exception:
        return False


def _sync_wrapper(fn):
    @trace_handler(fn)
    def wrapper(*args, **kwargs):
        if _is_called_by_pool():
            return fn(*args, **kwargs)

        db_info = {"type": "postgresql"}

        if args and isinstance(args[0], str) and '=' in args[0]:
            conn_str = args[0]
            parsed_kwargs = dict(
                x.split('=') for x in conn_str.split()
            )
            kwargs.update(parsed_kwargs)

        db_info.update(kwargs)

        connection = interceptor_db_con(fn, db_info, *args, **kwargs)
        if hasattr(connection, '_is_wrapped'):
            return connection
        return SyncConnection(connection, dict(db_info))

    return wrapper


def _async_wrapper(fn):
    @async_trace_handler(fn)
    async def wrapper(*args, **kwargs):
        if _is_called_by_pool():
            return await fn(*args, **kwargs)

        db_info = {"type": "postgresql"}

        if args and isinstance(args[0], str) and '=' in args[0]:
            conn_str = args[0]
            parsed_kwargs = dict(
                x.split('=') for x in conn_str.split()
            )
            kwargs.update(parsed_kwargs)

        db_info.update(kwargs)

        connection = await async_interceptor_db_con(fn, db_info, *args, **kwargs)
        if hasattr(connection, '_is_wrapped'):
            return connection
        return AsyncConnection(connection, dict(db_info))

    return wrapper


def _get_conn_info(connection):
    conn_info = {}
    try:
        if hasattr(connection, 'info'):
            conn_info['host'] = connection.info.host
            conn_info['port'] = connection.info.port
            conn_info['dbname'] = connection.info.dbname
            conn_info['user'] = connection.info.user
        elif hasattr(connection, 'dsn'):
            import re
            dsn_params = dict(x.split('=') for x in re.sub(r'\s*=\s*', '=', connection.dsn).split())
            conn_info.update(dsn_params)
    except Exception as e:
        print(f"Failed to extract connection info: {e}")
    return conn_info


def _pool_getconn_wrapper(original_getconn):
    def wrapper(self, *args, **kwargs):
        connection = original_getconn(self, *args, **kwargs)
        conn_info = _get_conn_info(connection)
        db_info = {"type": "postgresql", "pool": True, **conn_info}

        interceptor_pool_get(db_info)

        return SyncConnection(connection, db_info)

    return wrapper


def _async_pool_getconn_wrapper(original_getconn):
    async def wrapper(self, *args, **kwargs):
        connection = await original_getconn(self, *args, **kwargs)
        conn_info = _get_conn_info(connection)
        db_info = {"type": "postgresql", "pool": True, **conn_info}

        await async_interceptor_pool_get(db_info)

        return AsyncConnection(connection, db_info)

    return wrapper


def instrument_psycopg(module):
    original_connect = module.connect
    module.connect = _sync_wrapper(original_connect)
    if hasattr(module, 'AsyncConnection') and hasattr(module.AsyncConnection, 'connect'):
        original_async_connect = module.AsyncConnection.connect
        module.AsyncConnection.connect = _async_wrapper(original_async_connect)


def instrument_psycopg_pool(pool_module):
    if hasattr(pool_module, 'ConnectionPool'):
        pool_module.ConnectionPool.getconn = _pool_getconn_wrapper(pool_module.ConnectionPool.getconn)
    if hasattr(pool_module, 'AsyncConnectionPool'):
        pool_module.AsyncConnectionPool.getconn = _async_pool_getconn_wrapper(pool_module.AsyncConnectionPool.getconn)

