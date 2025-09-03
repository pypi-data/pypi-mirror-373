
.. image:: https://www.whatap.io/img/common/whatap_logo_re.svg

.. _WhaTap: https://www.whatap.io/

WhaTap_ for python
==================

- Whatap allows for application performance monitoring.
- Support: WSGI server application & Batch job & Specific method profiling.
- Python version : 3.7+

Installation
------------

  .. code:: bash

    $ pip install whatap-python

Application Monitoring
----------------------

Supported web frameworks such as Django, Flask, Bottle, Cherrypy, Tornado and WSGI Server Application.

Configuration
~~~~~~~~~~~~~

  .. code:: bash

    $ export WHATAP_HOME=[PATH]
    $ whatap-setting-config --host [HOST_ADDR]
                            --license [LICENSE_KEY]
                            --app_name [APPLICATION_NAME]
                            --app_process_name [APP_PROCESS_NAME]

Usage
~~~~~

  .. code:: bash

    $ whatap-start-agent [YOUR_APPLICATION_START_COMMAND]

    ...

Unsupported web frameworks WSGI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want WSGI Application monitoring, include the @register_app decorator.

  .. code:: python

    import whatap

    @whatap.register_app
    def simple_app(environ, start_response):
    """Simplest possible application object"""
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Hello world!\n']

Method Profiling
~~~~~~~~~~~~~~~~

If you want method profiling, include the @method_profiling decorator.

  .. code:: python

    from whatap import method_profiling

    @method_profiling
    def db_connection():
        db.connect('mysql:// ..')

    @method_profiling
    def query():
        db.select('select * from ..')

      ....

Batch Monitoring
----------------

for Batch job.

Configuration
~~~~~~~~~~~~~

Set Environment valiable configuration.

  .. code:: bash

    $ export WHATAP_BATCH_HOME=[PATH]
    $ cat >> $WHATAP_BATCH_HOME/whatap.conf << EOF
    license=[LICENSE_KEY]
    whatap.server.host=[HOST_ADDR]

    app_name=batch
    app_process_name=batch
    EOF


Usage
~~~~~

Start bach agent.

  .. code:: bash

    $ whatap-start-batch

Example code
~~~~~~~~~~~~

  .. code:: python

    from whatap import method_profiling

    class Command(BaseCommand):

        @batch_profiling
        def handle(self, *args, **options):
            // batch code..
            ....

Restart
-------

Your Application restart.

Copyright
---------

Copyright (c) 2017 Whatap, Inc. All rights reserved.
