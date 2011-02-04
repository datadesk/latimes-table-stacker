===============
Getting started
===============

This tutorial will walk you through the process of installing Table Stacker and publishing an example.

Requirements
------------

* `git <http://git-scm.com/>`_
* `python2.5 <http://www.python.org/download/releases/2.5.5/>`_
* `virtualenv <http://pypi.python.org/pypi/virtualenv>`_

01. Register a new application with Google App Engine
------------------------------------------------------

Go to `https://appengine.google.com/ <https://appengine.google.com/>`_. Don't download the SDK. Don't read the docs. Just create an account and mint a new application with a name like ``my-table-stacker``. It serves as the unique identifer for your app inside the Google system, and the namespace where it will first appear online (i.e. `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_).

02. Install the code on your computer
-------------------------------------

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

03. Set your application id
---------------------------

In the ``project`` folder you will find a file called ``app.yaml``. It contains the basic configuration for your Google App Engine site. You only need to make one little change: Replace ``my-table-stacker`` with the application id you registered in step one. ::

    application: my-table-stacker

04. Launch a test version of the site
-------------------------------------

You'll want to run this step in a new terminal shell. So open up a new window or tab, navigate to the ``project`` directory and fire off the following. It is a `Django management command <http://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-address-port>`_ that will start a test version of the site on your machine.

Note that you'll see me using ``python2.5`` throughout, instead of the usual ``python`` command. This is because I work in Ubuntu and I've found that Google App Engine `is not compatible with newer versions of Python <http://www.codigomanso.com/en/2010/05/google-app-engine-en-ubuntu-10-4-lucid-lynx/>`_. I suspect is is the case with other operating systems, but I'm not sure. So, I'd recommend using ``python2.5`` but, as always, your mileage may vary. ::

    $ python2.5 manage.py runserver

05. Load the example table
--------------------------

You'll learn how to layout your own data later, but for now we'll work with an example file: a list of the largest coal mines active in the United States. Jump back to your first terminal shell and drop the following line, which instructs our ``loadtable`` management command to follow instructions in the ``major-us-coal-mines-2009`` configuration file and create a new table in the test site we just launched at `http://localhost:8000 <http://localhost:8000>`_. ::

    $ python2.5 manage.py loadtable major-us-coal-mines-2009 --host=localhost:8000

06. Check it out
----------------

If everything clicked, you should see your demo site up and running with the coal mines table at `http://localhost:8000 <http://localhost:8000>`_.

07. Deploy your app
-------------------

Once everything's set, deploying your application to Google App Engine only takes a single command. Here it is. ::

    $ python2.5 manage.py update

08. Load the demo table on your live site
-----------------------------------------

You'll run the same ``loadtable`` command from step five, but drop the host option. It will post to your live site by default, so it's unnecessary this time around. ::

    $ python2.5 manage.py loadtable major-us-coal-mines-2009

09. Check it out
----------------

You should now see your starter site up and running at `http://my-table-stacker.appspot.com <http://my-table-stacker.appspot.com/>`_. You might draw errors for a few minutes as the app builds its indexes, but don't worry. It'll be ready after you have a cup of coffee.

10. Publish you own data table
------------------------------

Before you can publish your own data table, you'll need to learn about our YAML-based configuration system. But don't worry, it's not that hard. You can read about it in the :doc:`configuration <configuration>` section or school yourself by mimicking the examples files in the project's ``yaml`` subdirectory folder.



