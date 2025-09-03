PLUGIN = {}
IMPORT_HOOKS = {}



DEFINITION = {
    'plugin': [
        ('', 'instrument_plugin'),
    ],
    'standalone': [
        ('', 'instrument_standalone_single'),
        ('', 'instrument_standalone_multiple')
    ],
    'email.smtp': [
        ('smtplib', 'instrument_smtp'),
    ],
    'amqp.pika': [
        ('pika.channel', 'instrument_pika'),
    ],
    'llm.openai': [
        ('openai', 'instrument_openai')
    ],
    'logging': [
        ('logging.handlers', 'instrument_logging'),
        ('loguru._handler', 'instrument_loguru'),
    ],


    'httpc.httplib': [
        ('httplib', 'instrument_httplib'),
        ('http.client', 'instrument_httplib'),
        ('httplib2', 'instrument_httplib2'),
    ],
    'httpc.requests': [
        ('requests.sessions', 'instrument_requests'),
    ],
    'httpc.urllib3': [
        ('urllib3.request', 'instrument_urllib3'),
    ],
    'httpc.django': [
        ('revproxy.views', 'instrument_revproxy_views'),
    ],
    'httpc.httpx' : [
        ('httpx', 'instrument_httpx')
    ],


    'database.mysql': [
        ('MySQLdb', 'instrument_MySQLdb'),
        ('MySQLdb.cursors', 'instrument_MySQLdb_cursors'),
        ('pymysql', 'instrument_pymysql'),
        ('pymysql.cursors', 'instrument_pymysql_cursors'),
    ],
    'database.psycopg2': [
        ('psycopg2', 'instrument_psycopg2'),
        ('psycopg2._psycopg', 'instrument_psycopg2_connection'),
        ('psycopg2.extensions', 'instrument_psycopg2_extensions'),
    ],
    'database.psycopg3': [
        ('psycopg', 'instrument_psycopg'),
        ('psycopg_pool', 'instrument_psycopg_pool'),
    ],

    'database.neo4j': [
        ('neo4j', 'instrument_neo4j')
    ],
    'database.sqlite3': [
        ('sqlite3', 'instrument_sqlite3')
    ],
    'database.cxoracle':[
        ('cx_Oracle', 'instrument_oracle_client'),
    ],
    'database.redis': [
        ('redis', 'instrument_redis_connection'),
    ],
    'database.mongo': [
        ('pymongo', 'instrument_mongo_client'),
    ],
    'database.sqlalchemy': [
        ('sqlalchemy.orm.session', 'instrument_sqlalchemy'),
        ('sqlalchemy.engine.default', 'instrument_sqlalchemy_engine'),
        ('sqlalchemy.engine.create', 'instrument_sqlalchemy_engine_basic'),
        ('sqlalchemy.engine', 'instrument_sqlalchemy_engine_basic'),
    ],
    'database.util': [
        ('', ''),
    ],


    'application.starlette' : [
        ('starlette.websockets' , 'instrument_starlette_websocket'),
    ],
    'application.wsgi': [
        ('', ''),
    ],
    'application.bottle': [
        ('bottle', 'instrument'),
    ],
    'application.cherrypy': [
        ('cherrypy', 'instrument'),
    ],
    'application.django': [
        ('django.core.handlers.wsgi', 'instrument'),
        ('django.core.handlers.base', 'instrument_handlers_base'),
        ('django.views.generic.base', 'instrument_generic_base'),
        ('django.contrib.staticfiles.handlers', 'instrument_handlers_static'),
        ('channels.http', 'instrument_handlers_channels'),

        # Django==1.10
        ('django.urls.resolvers', 'instrument_url_resolvers', False),
        ('django.urls.base', 'instrument_urls_base', False),
        ('django.core.handlers.exception', 'instrument_handlers_exception',
         False),

    ],
    'application.django_asgi': [
        ('django.core.handlers.asgi', 'instrument_asgi'),
    ],
    'application.flask': [
        ('flask', 'instrument'),
    ],
    'application.tornado': [
        ('tornado.web', 'instrument'),
    ],
    'application.celery': [
        ('celery.execute.trace', 'instrument_celery_execute_trace'),
        ('celery.task.trace', 'instrument_celery_execute_trace'),
        ('celery.app.trace', 'instrument_celery_execute_trace'),
    ],
    'application.nameko': [
        ('nameko.containers', 'instrument_nameko_spawn_worker'),
        ('spsengine.containers', 'instrument_nameko_spawn_worker'),
    ],
    'application.graphql':[
        #graphen-core 3.x~
        ('graphql.execution.execute','instrument_graphql'),

        #graphen-core 2.x
        ('graphql.execution.executor','instrument_graphql'),
    ],
    'application.fastapi': [
        ('fastapi.applications', 'instrument_applications'),
        ('fastapi.routing', 'instrument'),
        ('fastapi.dependencies.utils', 'instrument_util'),

    ],
    'application.frappe': [
        ('frappe.app', 'instrument'),
    ],
    'application.odoo': [
        ('odoo', 'instrument'),
    ],
}
