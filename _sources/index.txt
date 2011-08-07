.. epigraph::

    Publish spreadsheets as interactive tables. And do it on deadline.

Features
========

* Convert a CSV file into an interactive HTML table that sorts, filters and paginates.
* Quickly publish interactives tables to Google App Engine and serve them on the web for free.
* Instantly syndicate data as CSV, XLS and JSON.
* Post an RSS feed and sitemap that promote the latest data.
* Link similar datasets together with blog-style tagging.

.. raw:: html

   <hr>

Resources
=========

* `Source code <https://www.github.com/datadesk/latimes-table-stacker/>`_
* `Working demonstration <http://table-stacker.appspot.com>`_

.. raw:: html

   <hr>

Getting started
===============

This tutorial will walk you through the process of installing Table Stacker and publishing an example.

**Requirements**

* `git <http://git-scm.com/>`_
* `python2.5 <http://www.python.org/download/releases/2.5.5/>`_
* `virtualenv <http://pypi.python.org/pypi/virtualenv>`_

**01. Register a new application with Google App Engine**

Go to `https://appengine.google.com/ <https://appengine.google.com/>`_. Don't download the SDK. Don't read the docs. Just create an account and mint a new application with a name like ``my-table-stacker``. It serves as the unique identifer for your app inside the Google system, and the namespace where it will first appear online (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

**02. Install the code on your computer**

It's not required, but I recommend creating a virtual environment to store your application. I like to do this with the Python module `virtualenv <http://pypi.python.org/pypi/virtualenv>`_, which creates a walled-off garden for the Python code to work without distraction from the outside world. If you don't have it, you'll need to install it now, which just might be as easy as::

    $ pip install virtualenv
    # Or maybe ...
    $ sudo easy_install install virtualenv
    # Or, if you're in Ubuntu ...
    $ sudo apt-get install python-virtualenv

Once you have virtualenv installed, make it happen by navigating to wherever you keep your code and firing off the following. I'm going to call this project ``my-table-stacker``, but you should substitute whatever you're calling your version. ::

    $ virtualenv --no-site-packages my-table-stacker

Now jump into the directory it creates. ::

    $ cd table-stacker

Activate the private environment with virtualenv's custom command. ::

    $ . bin/activate

Download the latest version of the code repository into a directory called ``project``. ::

    $ git clone git://github.com/datadesk/latimes-table-stacker.git project

And jump in and get ready to work. ::

    $ cd project

**03. Set your application id**

In the ``project`` folder you will find a file called ``app.yaml``. It contains the basic configuration for your Google App Engine site. You only need to make one little change: Replace ``my-table-stacker`` with the application id you registered in step one. ::

    application: my-table-stacker

**04. Launch a test version of the site**

You'll want to run this step in a new terminal shell. So open up a new window or tab, navigate to the ``project`` directory and fire off the following. It is a `Django management command <http://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-address-port>`_ that will start a test version of the site on your machine.

Note that you'll see me using ``python2.5`` throughout, instead of the usual ``python`` command. This is because I work in Ubuntu and I've found that Google App Engine `is not compatible with newer versions of Python <http://www.codigomanso.com/en/2010/05/google-app-engine-en-ubuntu-10-4-lucid-lynx/>`_. I suspect is is the case with other operating systems, but I'm not sure. So, I'd recommend using ``python2.5`` but, as always, your mileage may vary. ::

    $ python2.5 manage.py runserver

**05. Load the example table**

You'll learn how to layout your own data later, but for now we'll work with an example file: a list of the largest coal mines active in the United States. Jump back to your first terminal shell and drop the following line, which instructs our ``loadtable`` management command to follow instructions in the ``major-us-coal-mines-2009`` configuration file and create a new table in the test site we just launched at `http://localhost:8000 <http://localhost:8000>`_. ::

    $ python2.5 manage.py loadtable major-us-coal-mines-2009 --host=localhost:8000

**06. Check it out**

If everything clicked, you should see your demo site up and running with the coal mines table at `http://localhost:8000 <http://localhost:8000>`_.

**07. Deploy your app**

Once everything's set, deploying your application to Google App Engine only takes a single command. Here it is. ::

    $ python2.5 manage.py update

**08. Load the demo table on your live site**

You'll run the same ``loadtable`` command from step five, but drop the host option. It will post to your live site by default, so it's unnecessary this time around. ::

    $ python2.5 manage.py loadtable major-us-coal-mines-2009

**09. Check it out**

You should now see your starter site up and running at `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_. You might draw errors for a few minutes as the app builds its indexes, but don't worry. It'll be ready after you have a cup of coffee.

**10. Publish you own data table**

Before you can publish your own data table, you'll need to learn about our YAML-based configuration system. But don't worry, it's not that hard. You can read about it in the :doc:`configuration <configuration>` section or school yourself by mimicking the examples files in the project's ``yaml`` subdirectory folder.

.. raw:: html

   <hr>

Configuration
=============

Each published table is drawn from a CSV file you provide and styled according to the rules outlined in a configuration file written in `YAML <http://en.wikipedia.org/wiki/YAML>`_ configuration file. CSV files are stored in the ``csv`` folder in the root directory. YAML configuration files are stored in the ``yaml`` folder, with one configuration per file.

Example
-------
Here is an example YAML configuration that specifies how to layout `this demonstration table <http://table-stacker.appspot.com/major-us-coal-mines-2009/>`_. ::

    table:
      title: Major U.S. coal mines, 2009
      file:  major-us-coal-mines-2009.csv
      slug: major-us-coal-mines-2009
      byline: Ben Welsh
      description: <p>A list of the largest coal-producing U.S. mines for the year 2009. The U.S. Energy Information Administration reports the production of all mines that produce more than 4 million short tons. In 2009, 47 mines qualified by the list. All together, major mines produced more than 650 million short tons of coal, a majority of the roughly 1 billion total short tons unearthed across the nation. Wyoming mines dominate the list, filling out the first nine positions.</p>
      column_options:
        columns:
          - Mine
          - Company
          - Type
          - State
          - Production (Short tons)
        style:
          Mine: 'text-align:left; width:250px;'
          Company: 'text-align:left; width:250px;'
          Type: "width:80px;"
          State: "width:100px;"
        sorted_by:
          - Production (Short tons): descending
        formatting:
          Production (Short tons):
            method: intcomma
      is_published: true
      publication_date: 2011-01-12
      sources: <a href="http://www.eia.doe.gov/cneaf/coal/page/acr/acr_sum.html">U.S. Energy Information Administration</a>
      credits: <a href="mailto:ben.welsh@latimes.com">Ben Welsh</a>
      tags:
        - Coal
        - Energy
        - Mines
        - Business

Metadata Options
-----------------

The following YAML configuration options detail how to present a number of attributes about the table. All entries should be placed inside a dictionary titled ``table``.

.. attribute:: title
    
    The headline that will appear in lists and at the top of the table's detail page. Required.
    
    .. code-block:: yaml
        
        title: Major U.S. coal mines, 2009

.. attribute:: file
    
    The name of the CSV file the table will be based on. It should be in the ``csv`` directory with a header row included. Required.
    
    .. code-block:: yaml
    
        file: major-us-coal-mines-2009.csv

.. attribute:: slug
    
    A string that serves as the unique identifier of the table in the database and doubles as the relative url of its web page. It cannot be used for more than one table in your database. It's recommended that you do not use spaces or strange characters. Required.
    
    .. code-block:: yaml
    
        file: major-us-coal-mines-2009

.. attribute:: byline

    The name or list of names that will appear as a byline in lists and on the table's detail page. Optional.

    .. code-block:: yaml
    
        byline: Bob Woodard and Carl Bernstein

.. attribute:: description

    A block of text describing the table that will appear above the table on its detail page. HTML can and should be included. Optional.

    .. code-block:: yaml

        description: <p>A list of the largest coal-producing U.S. mines for the year 2009.</p>

.. attribute:: is_published

    A boolean ``true`` or ``false`` that indicates whether the table should be published. If set to ``false``, the table will be loaded in the database but will not appear on the site. Required.

    .. code-block:: yaml

        is_published: true

.. attribute:: publication_date

    The date that will appear alongside with the byline. Should be provided in ``YYYY-MM-DD`` format. Required.

    .. code-block:: yaml

        publication_date: 2011-01-12

.. attribute:: sources

    A block of text describing where the data came from. Will appear at the bottom of the table detail page after the phrase ``Sources:``. HTML can and should be included. Optional.

    .. code-block:: yaml

        sources: <a href="http://www.eia.doe.gov/cneaf/coal/page/acr/acr_sum.html">U.S. Energy Information Administration</a>

.. attribute:: credits

    A block of text listing all the people who helped make the page. Will appear at the bottom of the table detail page after the phrase ``Credits:``. HTML can and should be included. Optional.

    .. code-block:: yaml

          credits: <a href="mailto:russ.stanton@latimes.com">Russ Stanton</a>
          # Or ...
          credits: Bob Woodward and Carl Bernstein

.. attribute:: tags

    A list of blog-style tags that apply to the table. Will appear in a list at the bottom of the table's detail page and be used to generate lists that connect this table to similar tables. Optional.

    .. code-block:: yaml

          tags:
            - Coal
            - Energy
            - Mines
            - Business

Column Options
--------------

The following YAML configuration options specify how to present the columns in the data table. They should appear as entries in a dictionary titled ``column_options``.

.. attribute:: columns

    A list of the columns from the CSV that should appear in the published table. They will appear in the order specified here. Key names should correspond to headers in the CSV file. Optional.

    .. code-block:: yaml

        columns:
          - Mine
          - Company
          - Type
          - State
          - Production (Short tons)

.. attribute:: style

    A dictionary that specifies custom CSS to be applied to columns in the data table. CSS declarations should be included just as they would in an HTML ``style`` attribute. Key names should correspond to headers in the CSV file. Optional.

    .. code-block:: yaml
    
        style:
          Mine: 'text-align:left; width:250px;'
          Company: 'text-align:left; width:250px;'
          Type: "width:80px;"
          State: "width:100px;"

.. attribute:: sorted_by

    A single item list that specifies which column that table should be sorted by default, and which directions. Key names should correspond to headers in the CSV file. The direction can be either ``ascending`` or ``descending``. Optional.

    .. code-block:: yaml

        sorted_by:
          - Production (Short tons): descending

.. attribute:: formatting

    A dictionary that specifies formatting methods to be applied to all rows in a particular column. Each entry should include the column's name, followed by a dictionary requesting a particular method and, if necessary, identifing other columns to be passed in arguments. Optional.

    Available methods:

    * ``dollars``: Converts an number to a string containing commas every three digits with a dollar sign at the front.
    * ``intcomma``: Converts an integer to a string containing commas every three digits.
    * ``link``: Wraps a string in an HTML hyperlink. The URL from another column passed as an argument.
    * ``percentage``: Multiplies a float by 100, converts it to a string and follows it with a percentage sign. Defaults to one decimal place.
    * ``percent_change``: Converts a float into a percentage value with a + or - on the front and a percentage sign on the back. Defauls to one decimal place. Zero division errors should print out as "N/A."
    * ``title``: Converts a string into titlecase.

    .. code-block:: yaml

        formatting:
          Employees Affected:
            method: intcomma
          Company Name:
            method: title
          Title:
            method: link
            argument: url

    If you'd like to add a new filter of your own, open the ``table_fu/formatting.py`` file and add it there. Formatting filters are simple functions that accept a value and return the transformed value we'd like to present.

    .. code-block:: python

        def title(value):
            """
            Converts a string into titlecase.
            
            Lifted from Django.
            """
            value = value.lower()
            t = re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), value.title())
            return re.sub("\d([A-Z])", lambda m: m.group(0).lower(), t)

    After you've written a new filter, add it to the DEFAULT_FORMATTERS dictionary in that same file and you should now be available for use in YAML configuration files.

    .. code-block:: python

        DEFAULT_FORMATTERS = {
            'link': link,
            'intcomma': intcomma,
            'dollars': dollars,
            'percentage': percentage,
            'title': title,
        }

.. attribute:: per_page

    How many records should appear in each page of the data table. 20 by default. Optional.

    .. code-block:: yaml

        per_page: 50

.. attribute:: show_download_links

    Whether download links for CSV, XLS and JSON data should be made available on the table detail page. The default is true, so you only need to include it when you want to turn downloads off.

    .. code-block:: yaml

        show_download_links: false

.. raw:: html

   <hr>

Management commands
===================

Interactions with the Table Stacker database are handled using custom `Django management commands <http://docs.djangoproject.com/en/dev/ref/django-admin/>`_ that allow you to create, update and delete tables.

Like other Django commands, they are run by interacting with the ``manage.py`` file in your project's root directory.

.. attribute:: deletealltables <config_file_name> [options]

    Deletes all tables in the database

    .. cmdoption:: --host=<host_address>

        An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

        .. code-block:: bash

            # Clear the database in your live site
            $ python2.5 manage.py deletealltables 
            # Or for a test site running on your local machine
            $ python2.5 manage.py deletealltables --host=localhost:8000

.. attribute:: deletetable <config_file_name> [options]

    Delete the table outlined in the configuration file provided by the first argument.

    .. cmdoption:: --host=<host_address>

        An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

        .. code-block:: bash

            $ python2.5 manage.py deletetable config-file-name --host=localhost:8000

.. attribute:: listtables [options]

    List all of the configuration files.

    .. cmdoption:: --host=<host_address>

        An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

        .. code-block:: bash

            $ python2.5 manage.py listtables --host=localhost:8000

.. attribute:: loadalltables [options]

    Create or update all tables outlined in the directory of configuration file.

    .. cmdoption:: --host=<host_address>

        An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

        .. code-block:: bash

            $ python2.5 manage.py loadalltables --host=localhost:8000

.. attribute:: loadtable <config_file_name> [options]

    Create or update the table outlined in the configuration file provided by the first argument.

    .. cmdoption:: --host=<host_address>

        An optional argument that specifies the host of the Google App Engine database you want to interact with. By default, it accesses the live site at the default address (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

        .. code-block:: bash

            python2.5 manage.py loadtable config-file-name --host=localhost:8000

.. attribute:: runserver

    The built-in command for firing up the Django test server. You can read more about it in `the official Django docs <http://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-address-port>`_.

    .. code-block:: bash

        python2.5 manage.py runserver

.. attribute:: update

    A custom command design for Google App Engine that deploys the code base to the web. Read more about it in the `google-app-engine-helper <http://code.google.com/p/google-app-engine-django/source/browse/trunk/README>`_ documentation.

    .. code-block:: bash

        python2.5 manage.py update

.. raw:: html

   <hr>

Customization
=============

Table Stacker is published with `minimal styling <http://table-stacker.appspot.com/>`_. If you want to adapt it for your site, you'll probably want to change the appearance and layout. The CSS styles that regulate the appearance of Table Stacker are stored in the ``/media/css`` directory. Change them and you'll change the appearance of the site. Table Stacker's layout is managed using `Django's templating system <http://docs.djangoproject.com/en/dev/ref/templates/>`_ and configured through a series of files in the ``templates`` directory. Change them and you'll change the layout of the site.

.. raw:: html

   <hr>

Credits
=======

This project would not be possible without the generous work of people like:

* `ProPublica's News Application Desk <http://www.propublica.org/nerds>`_, and particularly `Jeff Larson <https://github.com/thejefflarson>`_, who developed the Ruby libraries `table-fu <https://github.com/propublica/table-fu>`_ and `table-setter <https://github.com/propublica/table-setter>`_.
* `Chris Amico <https://github.com/eyeseast>`_, who did the noble work of porting table-fu to `Python <https://github.com/eyeseast/python-tablefu>`_.
* Christian Bach, the man who gave us `tablesorter <http://tablesorter.com/docs/>`_.
* Thomas Suh Lauder, who has suggested many style improvements and formatting options.
* The army of people who make something like `google-app-engine-django <http://code.google.com/p/google-app-engine-django/>`_ possible.


