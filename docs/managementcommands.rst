Management commands
===================

Interactions with the Table Stacker database are handled using custom `Django management commands <http://docs.djangoproject.com/en/dev/ref/django-admin/>`_ that allow you to create, update and delete tables.

Like other Django commands, they are run by interacting with the ``manage.py`` file in your project's root directory.

.. attribute:: build [options]
    
    Builds a static site with all the tables okayed for publication
    
    .. code-block:: bash
        
        $ python manage.py build

.. attribute:: buildserver [options]
    
    Delete the table outlined in the configuration file provided by the first argument.
    
    .. code-block:: bash
        
        $ python manage.py buildserver
        # Optionally, set the port for the server.
        $ python manage.py buildserver 8080

.. attribute:: publish [options]
    
    Sync the build directory with the Amazon S3 bucket specified in settings.py
    
    .. code-block:: bash
    
        $ python manage.py publish

.. attribute:: unbuild [options]
    
    Empties the build directory
    
    .. code-block:: bash
    
        $ python manage.py unbuild

.. attribute:: unpublish [options]
    
   Empties the Amazon S3 bucket defined in settings.py
    
    .. code-block:: bash
    
        $ python manage.py unpublish
