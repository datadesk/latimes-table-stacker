Getting started
===============

This tutorial will walk you through the process of installing Table Stacker and publishing an example.

Requirements
------------

* `git <http://git-scm.com/>`_
* `python <http://www.python.org/>`_

01. Install the code on your computer
-------------------------------------

It's not required, but I recommend creating a virtual environment to store your application. I like to do this with the Python module `virtualenv <http://pypi.python.org/pypi/virtualenv>`_, which creates a walled-off garden for the Python code to work without distraction from the outside world. If you don't have it, you'll need to install it now, which just might be as easy as

.. code-block:: bash

    $ pip install virtualenv
    # Or maybe ...
    $ sudo easy_install install virtualenv
    # Or, if you're in Ubuntu ...
    $ sudo apt-get install python-virtualenv

Once you have virtualenv installed, make it happen by navigating to wherever you keep your code and firing off the following. I'm going to call this project ``my-table-stacker``, but you should substitute whatever you're calling your version.

.. code-block:: bash

    $ virtualenv --no-site-packages my-table-stacker

Now jump into the directory it creates.

.. code-block:: bash

    $ cd my-table-stacker

Activate the private environment with virtualenv's custom command.

.. code-block:: bash

    $ . bin/activate

Download the latest version of the code repository into a directory called ``project``. 

.. code-block:: bash

    $ git clone git://github.com/datadesk/latimes-table-stacker.git project

And jump in and get ready to work.

.. code-block:: bash

    $ cd project

Install our app's Python dependencies.

.. code-block:: bash

    $ pip install -r requirements.txt

Create the project's database

.. code-block:: bash

    $ python manage.py syncdb
    $ python manage.py migrate

02. Build the example tables
----------------------------

You'll learn how to layout your own data later, but for now we'll work with the example files. Jump back to your first terminal shell and drop the following line, which instructs our ``build`` management command to bake out a static site using the instructions in ``settings.py`` and the table recipes in the ``yaml`` directory.

.. code-block:: bash

    $ python manage.py build

03. Launch the static version of the site
-----------------------------------------

You'll want to run this step in a new terminal shell. So open up a new window or tab, navigate to the ``project`` directory and fire off the following. It is a Django management command that will start a test version of the site on your machine, tailored to serve the static files we used created.

.. code-block:: bash

    $ python manage.py buildserver

04. Check it out
----------------

If everything clicked, you should see your demo site up and running with all the example tables at `http://localhost:8000 <http://localhost:8000>`_.

05. Deploy your app
-------------------

The static files we've created in your ``build`` directory could probably be served from most common web servers. So, if you've already
got yours worked out, you can just stop here and deploy that folder where you like. 

However, the app is prepared to help you easily deploy to `Amazon S3 <http://en.wikipedia.org/wiki/Amazon_S3>`_. To make that happen, you'll need to do a little set up. First, go to `aws.amazon.com/s3 <http://aws.amazon.com/s3>`_ and set up an account. Then you'll need to create a bucket for storing our files. If you need help there are some basic instructions `here <http://docs.amazonwebservices.com/AmazonS3/latest/gsg/>`_.

Next configure the bucket to act as a website. Amazon's official instructions say to do the following::

    In the bucket Properties pane, click the Website configuration tab. 

    Select the Enabled check box.

    In the Index Document Suffix text box, add the required index document name (index.html).

Before you leave that pane, note the URL at the bottom. This is where your site will be published.

Now, set your bucket name in the `settings.py` file.::

    AWS_BUCKET_NAME = 'table-stacker'

Next, install `s3cmd <http://s3tools.org/s3cmd>`_, a utility we'll use to move files back and forth between your desktop and S3. In Ubuntu, that's as simple as:

.. code-block:: bash

    $ sudo apt-get install s3cmd

If you're Mac or Windows, you'll need to `download the file <http://s3tools.org/download>`_ and follow the installation instructions you find there.

Once it's installed, we need to configure s3cmd with your Amazon login credentials. Go to Amazon's `security credentials <http://aws-portal.amazon.com/gp/aws/developer/account/index.html?action=access-key>`_ page and get your access key and secret access key. Then, from your terminal, run

.. code-block:: bash

    $ s3cmd --configure

Finally, now that everything is set up, publishing your files to s3 is as simple as:

.. code-block:: bash

    $ python manage.py publish

Once you do that, your site should appear at the the link provided in your AWS console. If you want to bind that to a subdomain of your site, say, www.tablestacker.com, you need to create a new CNAME record in your domain's DNS registration. You also need the name of your bucket to line up with the subdomain. Don't take it from me. Read the detailed instructions provided by Amazon. 

.. code-block:: text

    For example, if you have registered domain, www.example-bucket.com, you 
    could create a bucket www.example-bucket.com, and add a DNS CNAME entry 
    pointing to www.example-bucket.com.s3-website-<region>.amazonaws.com. 
    All requests to http://www.example-bucket.com will be routed to 
    www.example-bucket.com.s3-website-<region>.amazonaws.com.

More documentation on that is available `here <http://docs.amazonwebservices.com/AmazonS3/latest/dev/index.html?WebsiteHosting.html>`_.

06. Publish you own data table
------------------------------

Before you can publish your own data table, you'll need to learn about our YAML-based configuration system. But don't worry, it's not that hard. You can read about it in the configuration section or school yourself by mimicking the examples files in the project's ``yaml`` subdirectory folder. Then, doing the following:

.. code-block:: bash

    $ python manage.py build
    $ python manage.py publish
