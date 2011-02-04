===================
Management commands
===================

Interactions with the Table Stacker database are handled using custom `Django management commands <http://docs.djangoproject.com/en/dev/ref/django-admin/>`_ that allow you to create, update and delete tables.

Like other Django commands, they are run by interacting with the ``manage.py`` file in your project's root directory.


deletealltables [options]
-------------------------

Deletes all tables in the database

``--host=<host_address>``

An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

Example usage::

    # Clear the database in your live site
    $ python2.5 manage.py deletealltables 
    # Or for a test site running on your local machine
    $ python2.5 manage.py deletealltables --host=localhost:8000


deletetable <config_file_name> [options]
----------------------------------------

Delete the table outlined in the configuration file provided by the first argument.

``--host=<host_address>``

An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

Example usage::

    python2.5 manage.py deletetable config-file-name --host=localhost:8000


listtables [options]
--------------------

List all of the configuration files.

``--host=<host_address>``

An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

Example usage::

    python2.5 manage.py listtables --host=localhost:8000


loadalltables [options]
-----------------------

Create or update all tables outlined in the directory of configuration file.

``--host=<host_address>``

An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

Example usage::

    python2.5 manage.py loadalltables --host=localhost:8000


loadtable <config_file_name> [options]
--------------------------------------

Create or update the table outlined in the configuration file provided by the first argument.

``--host=<host_address>``

An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

Example usage::

    python2.5 manage.py loadtable config-file-name --host=localhost:8000


runserver
---------

The built-in command for firing up the Django test server. You can read more about it in `the official Django docs <http://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-address-port>`_.

Example usage::

    python2.5 manage.py runserver


update
------

A custom command design for Google App Engine that deploys the code base to the web. Read more about it in the `google-app-engine-helper <http://code.google.com/p/google-app-engine-django/source/browse/trunk/README>`_ documentation.

Example usage::

    python2.5 manage.py update
