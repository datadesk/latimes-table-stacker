=============
Configuration
=============

Each published table is drawn from a CSV file you provide and styled according to the rules outlined in a configuration file written in `YAML <http://en.wikipedia.org/wiki/YAML>`_. 

CSV files are stored in the ``csv`` folder in the root directory.

YAML configuration files are stored in the ``yaml`` folder, with one configuration per file.

Example
------------
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

title
^^^^^

The headline that will appear in lists and at the top of the table's detail page. Required.

Example::
    
    title: Major U.S. coal mines, 2009

file
^^^^

The name of the CSV file the table will be based on. It should be in the ``csv`` directory with a header row included. Required.

Example::
    
    file: major-us-coal-mines-2009.csv

slug
^^^^

A string that serves as the unique identifier of the table in the database and doubles as the relative url of its web page. It cannot be used for more than one table in your database. It's recommended that you do not use spaces or strange characters. Required.

Example::
    
    file: major-us-coal-mines-2009

byline
^^^^^^

The name or list of names that will appear as a byline in lists and on the table's detail page. Optional.

Example::
    
    byline: Russ Stanton
    # Or ...
    byline: Bob Woodard and Carl Bernstein

description
^^^^^^^^^^^

A block of text describing the table that will appear above the table on its detail page. HTML can and should be included. Optional.

Example::

    description: <p>A list of the largest coal-producing U.S. mines for the year 2009.</p>

is_published
^^^^^^^^^^^^

A boolean ``true`` or ``false`` that indicates whether the table should be published. If set to ``false``, the table will be loaded in the database but will not appear on the site. Required.

Example::

    is_published: true

publication_date
^^^^^^^^^^^^^^^^

The date that will appear alongside with the byline. Should be provided in ``YYYY-MM-DD`` format. Required.

Example::

      publication_date: 2011-01-12

sources
^^^^^^^

A block of text describing where the data came from. Will appear at the bottom of the table detail page after the phrase ``Sources:``. HTML can and should be included. Optional.

Example::

    sources: <a href="http://www.eia.doe.gov/cneaf/coal/page/acr/acr_sum.html">U.S. Energy Information Administration</a>

credits
^^^^^^^

A block of text listing all the people who helped make the page. Will appear at the bottom of the table detail page after the phrase ``Credits:``. HTML can and should be included. Optional.

Example::

      credits: <a href="mailto:russ.stanton@latimes.com">Russ Stanton</a>
      # Or ...
      credits: Bob Woodward and Carl Bernstein

tags
^^^^

A list of blog-style tags that apply to the table. Will appear in a list at the bottom of the table's detail page and be used to generate lists that connect this table to similar tables. Optional.

Example::

      tags:
        - Coal
        - Energy
        - Mines
        - Business

Column Options
--------------

The following YAML configuration options specify how to present the columns in the data table. They should appear as entries in a dictionary titled ``column_options``.

columns
^^^^^^^

A list of the columns from the CSV that should appear in the published table. They will appear in the order specified here. Key names should correspond to headers in the CSV file. Optional.

Example::

    columns:
      - Mine
      - Company
      - Type
      - State
      - Production (Short tons)

style
^^^^^

A dictionary that specifies custom CSS to be applied to columns in the data table. CSS declarations should be included just as they would in an HTML ``style`` attribute. Key names should correspond to headers in the CSV file. Optional.

Example::
    
    style:
      Mine: 'text-align:left; width:250px;'
      Company: 'text-align:left; width:250px;'
      Type: "width:80px;"
      State: "width:100px;"


sorted_by
^^^^^^^^^

A single item list that specifies which column that table should be sorted by default, and which directions. Key names should correspond to headers in the CSV file. The direction can be either ``ascending`` or ``descending``. Optional.

Example::

    sorted_by:
      - Production (Short tons): descending


.. _formatting-option:

formatting
^^^^^^^^^^

A dictionary that specifies formatting methods to be applied to all rows in a particular column. Each entry should include the column's name, followed by a dictionary requesting a particular method and, if necessary, identifing other columns to be passed in arguments. Optional.

Available methods:

* ``dollars``: Converts an number to a string containing commas every three digits with a dollar sign at the front.
* ``intcomma``: Converts an integer to a string containing commas every three digits.
* ``link``: Wraps a string in an HTML hyperlink. The URL from another column passed as an argument.
* ``percentage``: Multiplies a float by 100, converts it to a string and follows it with a percentage sign. Defaults to one decimal place.
* ``percent_change``: Converts a float into a percentage value with a + or - on the front and a percentage sign on the back. Defauls to one decimal place. Zero division errors should print out as "N/A."
* ``title``: Converts a string into titlecase.

Custom methods can be added by following the instructions in the :ref:`customization <data-formatting>` section.


Example::

    formatting:
      Employees Affected:
        method: intcomma
      Company Name:
        method: title
      Title:
        method: link
        argument: url

per_page
^^^^^^^^

How many records should appear in each page of the data table. 20 by default. Optional.

Example::

    per_page: 50

show_download_links
^^^^^^^^^^^^^^^^^^^

Whether download links for CSV, XLS and JSON data should be made available on the table detail page. The default is true, so you only need to include it when you want to turn downloads off.

Example::

    show_download_links: false






