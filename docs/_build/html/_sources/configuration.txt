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

.. attribute:: kicker

    A brief string to run above the headline in all capital letters. "SPREADSHEET" by default. Optional.

    .. code-block:: yaml

        kicker: data table

.. attribute:: legend

    A slot above the table where you can stick an HTML block containing a legend. Empty be default. Optional.
    
    .. code-block:: yaml
    
        legend: "<img src='http://example.com/legend.png'>"

.. attribute:: footer

    A slot below the table where you can stick and HTML block containing footnotes, corrections or other extra information. Optional.
    
    .. code-block:: yaml
    
        footer: "<p>We regret the error.</p>"

.. attribute:: is_published

    A boolean ``true`` or ``false`` that indicates whether the table should be published. If set to ``false``, the table will be loaded in the database but will not appear on the site. Required.

    .. code-block:: yaml

        is_published: true

.. attribute:: publication_date

    The date that will appear alongside with the byline. Should be provided in ``YYYY-MM-DD`` format. Required.

    .. code-block:: yaml

        publication_date: 2011-01-12

.. attribute:: publication_time

    The time that will appear alongside the date with the byline. Should be provided in ``HH:MM:SS`` format. Optional.

    .. code-block:: yaml

        publication_time: "11:58:00"

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

.. attribute:: per_page

    How many records should appear in each page of the data table. 50 by default. Optional.

    .. code-block:: yaml

        per_page: 50

.. attribute:: show_download_links

    Whether download links for CSV, XLS and JSON data should be made available on the table detail page. The default is true, so you only need to include it when you want to turn downloads off.

    .. code-block:: yaml

        show_download_links: false

.. attribute:: show_search_field

   Whether or not to show a search box on the table detail page that filters the table. The default is true, so you only need to include it when you want to turn the search off.

    .. code-block:: yaml

        show_search_field: false

.. attribute:: show_in_feeds

    Whether the table will show in the sitemap, RSS feeds and public-facing list pages. The default is true, so you only need to include it when you want to set it to false.
    
    .. code-block:: yaml
    
        show_in_feeds: false


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

.. attribute:: sorters

    A dictionary that specifies how to properly sort columns in the interactive table. The JavaScript library that crafts the table attempts to guess the proper sorting method for each column, but sometimes it is wrong. Other times you might not want to sort a column at all, which can be done by setting the value to ``false``. You can use these options to declare what you'd like it do. A full list of the available sorters can be found `here <https://github.com/datadesk/latimes-table-stacker/blob/master/table_stacker/static/js/jquery.tablesorter.js#L696>`_. Optional. 

    .. code-block:: yaml

        sorters:
          Production (Short tons): fancyNumber
          Name: false

.. attribute:: formatting

    A dictionary that specifies formatting methods to be applied to all rows in a particular column. Each entry should include the column's name, 
    followed by a dictionary requesting a particular method and, if necessary, customization options and other columns to be passed in as arguments. Optional.

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
        
    **Available formatting filters**
    
    .. method:: ap_state(value)
       
        Converts a state's name, FIPS code or postal abbreviation to A.P. style. Returns the submitted string if a conversion cannot be made.
        
        .. code-block:: yaml
            
            formatting:
              ColumnName:
                method: ap_state
    
    .. method:: bubble(value, yes_icon="/static/img/bubble_yes.png", no_icon="/static/img/bubble_no.png", empty="&mdash;")
    
        Returns one of two "Consumer Reports" style bubbles that indicate yes (a filled bubble) or no (an empty bubble). The first letter of each type is what should be provided (i.e. Y, N). If a match cannot be made the empty argument is returned.
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: bubble
                
        You can customize the output by overriding the defaults
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: bubble
                options:
                  yes_icon: "http://example.com/yes.png"
                  no_icon: "http://example.com/no.png"
    
    .. method:: capfirst(value)
        
        Changes a string so that only the first character is capitalized.
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: capfirst

    .. method:: checkbox(value, yes_icon='/static/img/checkbox_yes.png',  no_icon='/static/img/checkbox_no.png')
        
        Returns one of two checkbox images that indicate yes (a checked box) or no (an empty box). The first letter of each type is what should be provided (i.e. Y, N). If a match cannot be made an empty string is returned.
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: checkbox
                
        You can customize the output by overriding the defaults
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: checkbox
                options:
                  yes_icon: "<img src='http://example.com/yes.png'>"
                  no_icon: "<img src='http://example.com/no.png'>"
    
    .. method:: date_and_time(value, formatting="N j, Y, h:i a")
    
        Reformats a date string in a humanized format, AP style by default.
        
        .. code-block:: yaml
            
            formatting:
              ColumnName:
                method: date_and_time
                
        You can override the output format by specifying an alternative in the formatting in the options. You must use `Django's datetime formatting style <https://docs.djangoproject.com/en/dev/ref/templates/builtins/?from=olddocs#date>`_.
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: date_and_time
                options:
                  formatting: "Y-m-d P"
    
    .. method:: dollar_signs(value)
    
        Converts an integer into the corresponding number of dollar sign symbols (ie. 3 -> "$$$"). Meant to emulate the illustration of price range on Yelp. If something besides an integer is submitted, "N/A" is returned.
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: dollar_signs
    
    .. method:: dollars(value, decimal_places=2)
    
        Converts an number to a string containing commas every three digits with a dollar sign at the front. Returns "N/A" if the something besides a number if submitted.
    
        .. code-block:: yaml
            
            formatting:
              ColumnName:
                method: dollars
    
        The number of decimal places the number is rounded at can controlled with an option. The default is two decimal places.
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: dollars
                options:
                  decimal_places: 0
    
    .. method:: intcomma(value)
    
        Converts an integer to a string containing commas every three digits.
    
        .. code-block:: yaml
            
            formatting:
              ColumnName:
                method: intcomma
    
    .. method:: image(value, width='', height='')
    
        Accepts a URL and returns an HTML image tag ready to be displayed.
        
        .. code-block:: yaml
            
            formatting:
              ColumnName:
                method: image
    
        Optionally, you can set the height and width with keyword arguments.

        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: image
                options:
                  height: "30px"
                  width: "30px"
    
    .. method:: link(title, url)
    
        Wraps a string in an HTML hyperlink. The URL from another column passed as an argument.
        
        .. code-block:: yaml
        
            formatting:
              TextColumnName:
                method: link
                arguments:
                  - LinkColumnName
    
    .. method:: percentage(value, decimal_places=1, multiply=True)
    
        Converts a floating point value into a percentage value. An empty string is returned if the input triggers an exception.
        
        .. code-block:: yaml
            
            formatting:
              ColumnName:
                method: percentage
                
        The number of decimal places set by the ``decimal_places`` option. The default is one. Also by default the number is multiplied by 100. You can prevent it from doing that by setting the ``multiply`` option to False.
    
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: percentage
                options:
                  decimal_places: 0
                  multiply: false
    
    .. method:: percent_change(value, decimal_places=1, multiply=True)
        
        Converts a float into a percentage value with a + or - on the front and a percentage sign on the back. "N/A" is returned if the input cannot be converted to a float.
        
        .. code-block:: yaml
            
            formatting:
              ColumnName:
                method: percent_change
        
        The number of decimal places set by the ``decimal_places`` option. The default is one. Also by default the number is multiplied by 100. You can prevent it from doing that by setting the ``multiply`` option to False.
    
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: percent_change
                options:
                  decimal_places: 0
                  multiply: false
    
    .. method:: short_ap_date(value, date_format=None)
    
        Reformats a date string in an abbreviated AP format.
        
        .. code-block:: yaml
            
            formatting:
              ColumnName:
                method: short_ap_date
                
        The method tries to parse the datestring automatically, but in some cases (i.e. dates in the first century) or less common date formats
        you might need to specifiy the date format using `strptime standards <http://docs.python.org/library/datetime.html#strftime-strptime-behavior>`_.

        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: short_ap_date
                options:
                  date_format: "%Y-%m-%d"
    
    .. method:: simple_bullet_graph(actual, target, width='95%', max=None)
    
        Renders a simple `bullet graph <http://en.wikipedia.org/wiki/Bullet_graph>`_ that compares a target line against an actual value. Unlike a conventional bullet graph, it does not shade the background into groups. Instead, it's all one solid color.
        
        .. code-block:: yaml
        
            formatting:
              ActualValueColumn:
                method: simple_bullet_graph
                arguments:
                  - TargetValueColumn
                options:
                  max: 60
    
    .. method:: title(value)
    
        Converts a string into titlecase.
        
            .. code-block:: yaml
            
                formatting:
                  ColumnName:
                    method: title
    
    .. method:: tribubble(value, yes_icon='/static/img/tribubble_yes.png', partly_icon='/static/img/tribubble_partly.png', no_icon="/static/img/tribubble_no.png", empty="&mdash;")
    
        Returns one of three "Consumer Reports" style bubbles that indicate yes (filled bubble), partly (half-filled bubble), no (empty bubble). The first letter of each type is what should be provided (i.e. Y, N, P). If a match cannot be made the empty argument is returned.
    
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: tribubble
                
        You can customize the output by overriding the defaults
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: tribubble
                options:
                  yes_icon: "http://example.com/yes.png"
                  no_icon: "http://example.com/no.png"
                  partly_icon: "http://example.com/partly.png"
    
    .. method:: vote(value, yes_vote='/static/img/thumb_up.png', no_vote='/static/img/thumb_down.png', did_not_vote="<b style='font-size:130%;'>&mdash;</b>")
    
        Returns one of three icons representing the outcome a vote: Yes (thumbs up); No (thumbs down); Did not vote (Bolded emdash). The first letter of each type is what should be provided, i.e. Y, N, anything else.
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: vote
                
        You can customize the output by overriding the defaults
        
        .. code-block:: yaml
        
            formatting:
              ColumnName:
                method: vote
                options:
                  yes_vote: "<img src='http://example.com/yes.png'>"
                  no_vote: "<img src='http://example.com/no.png'>"
                  did_not_vote: "<img src='http://example.com/didnotvote.png'>"


Override sort with URL
----------------------

You can override the default sorting order of a table by appending a query string argument that provides an alternative. There are two required parameters. 

.. attribute:: sortColumn

    The index of the column that the table should sort by. Starts with zero from the left. So to sort by the first column, you would provide ``0``.

.. attribute:: sortOrder

    The direction the column should sort in. ``0`` will sort in the ascending. ``1`` will sort in the descending.

Here is an example of resorting a table by the first column in ascending order.

.. code-block:: text

    http://table-stacker.s3-website-us-west-1.amazonaws.com/california-layoffs-december-2010/?sortColumn=0&sortOrder=0
