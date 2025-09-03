from whatap.trace.mod.application.wsgi import trace_handler
from whatap.trace.mod.database.util import interceptor_db_con, interceptor_db_execute, interceptor_db_close

db_info = {}





def instrument_neo4j(module):

    if hasattr(module, 'GraphDatabase'):
        orig_driver = module.GraphDatabase.driver
        def wrapper(fn):
            @trace_handler(fn)
            def trace(*args, **kwargs):
                db_info = {'type': 'neo4j'}

                if args:
                    db_info['uri'] = args[0]

                auth = kwargs.get('auth') or (args[1] if len(args) > 1 else None)
                if auth:
                    user = getattr(auth, 'principal', None) or (auth[0] if isinstance(auth, tuple) else None)
                    if user:
                        db_info['user'] = user

                callback = interceptor_db_con(fn, db_info, *args, **kwargs)
                return callback

            return trace
        module.GraphDatabase.driver = wrapper(orig_driver)



    if hasattr(module, 'Driver'):
        orig_driver_close = module.Driver.close
        def wrapper(fn):
            @trace_handler(fn)
            def trace(driver, *args, **kwargs):
                callback = interceptor_db_close(fn, driver, *args, **kwargs)
                return callback

            return trace

        module.Driver.close = wrapper(orig_driver_close)

    orig = module.Session.run
    def wrapper(fn):
        @trace_handler(fn)
        def trace(session, *args, **kwargs):
            db_info = {'type': 'neo4j'}
            try:
                setattr(session, 'rowcount', -1)
            except Exception as e:
                raise e
            callback = interceptor_db_execute(fn, db_info, session, *args, **kwargs)

            return callback
        return trace
    module.Session.run = wrapper(orig)

    def wrapper(fn):
        @trace_handler(fn)
        def trace(tx, *args, **kwargs):
            session = None
            try:
                session = tx._on_closed.__self__
            except AttributeError:
                return fn(tx, *args, **kwargs)
            db_info = {'type': 'neo4j'}
            try:
                setattr(tx, 'rowcount', -1)
            except Exception:
                pass
            callback = interceptor_db_execute(fn, db_info, tx, *args, **kwargs)
            return callback

        return trace

    tx_classes_to_patch = ['Transaction', 'ManagedTransaction', 'BoltTransaction']
    for class_name in tx_classes_to_patch:
        if hasattr(module, class_name):
            TxClass = getattr(module, class_name)
            if hasattr(TxClass, 'run'):
                original_run = getattr(TxClass, 'run')
                setattr(TxClass, 'run', wrapper(original_run))



