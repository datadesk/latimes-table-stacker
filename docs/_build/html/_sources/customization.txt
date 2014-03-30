Customization
=============

Table Stacker is published with `minimal styling <http://table-stacker.appspot.com/>`_. If you want to adapt it for your site, you'll probably want to change the appearance and layout. The CSS styles that regulate the appearance of Table Stacker are stored in the ``/static/css`` directory. Change them and you'll change the appearance of the site. Table Stacker's layout is managed using `Django's templating system <http://docs.djangoproject.com/en/dev/ref/templates/>`_ and configured through a series of files in the ``templates`` directory. Change them and you'll change the layout of the site.

Global settings
---------------

.. attribute:: SITE_NAME

    A ``settings.py`` configuration that sets the site's name in meta data around the site, like the title tag and Facebook open graph tags.

.. attribute:: FACEBOOK_ADMINS

    A list of Facebook user ids included in the open graph tags in each page's head. Useful for configuring the site's footprint on Facebook. Set in ``settings.py``.

