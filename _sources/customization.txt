=============
Customization
=============

Table Stacker is published with `minimal styling <http://table-stacker.appspot.com/>`_. If you want to adapt it for your site, you'll probably want to change the appearance and layout. 

CSS Styles
----------

The CSS styles that regulate the appearance of Table Stacker are stored in the ``/media/css`` directory. Change them and you'll change the appearance of the site.

Template Layout
---------------

Table Stacker's layout is managed using `Django's templating system <http://docs.djangoproject.com/en/dev/ref/templates/>`_ and configured through a series of files in the ``templates`` directory. Change them and you'll change the layout of the site.

.. _data-formatting:

Data formatting
---------------

The appearance of a column can be customized by applying a formatting filter to each row. This is done by selecting one of the available filters and listing it in the :ref:`configuration file <formatting-option>`. If you'd like to add a new filter of your own, open the ``table_fu/formatting.py`` file and add it there. 

Formatting filters are simple functions that accept a value and return the transformed value we'd like to present.

Example::

    def title(value):
        """
        Converts a string into titlecase.
        
        Lifted from Django.
        """
        value = value.lower()
        t = re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), value.title())
        return re.sub("\d([A-Z])", lambda m: m.group(0).lower(), t)

After you've written a new filter, add it to the DEFAULT_FORMATTERS dictionary in that same file and you should now be available for use in :doc:`YAML configuration files <configuration>`.

::

    DEFAULT_FORMATTERS = {
        'link': link,
        'intcomma': intcomma,
        'dollars': dollars,
        'percentage': percentage,
        'title': title,
    }
