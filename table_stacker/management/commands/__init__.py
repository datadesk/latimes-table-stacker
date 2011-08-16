"""
Utilities shared by multiple custom management commands.
"""
import os
import csv
import yaml
import getpass
from django.conf import settings
from optparse import make_option
from django.utils import simplejson
from google.appengine.ext import db
from toolbox.slugify import slugify
from toolbox.FileIterator import FileIterator
from table_stacker.models import Table, Tag
from google.appengine.api.labs import taskqueue
from google.appengine.ext.remote_api import remote_api_stub
from django.core.management.base import BaseCommand, CommandError

#
# Errors
#

class YAMLDoesNotExistError(Exception):
    """
    Called when you try to open a YAML that doesn't exist.
    """
    def __init__(self, value):
        self.parameter = value
    
    def __str__(self):
        return repr(self.parameter)


class CSVDoesNotExistError(Exception):
    """
    Called when you try to open a CSV that doesn't exist.
    """
    def __init__(self, value):
        self.parameter = value
    
    def __str__(self):
        return repr(self.parameter)


class InvalidYAMLError(Exception):
    """
    Called when your YAML doesn't get with the program.
    """
    def __init__(self, value):
        self.parameter = value
    
    def __str__(self):
        return repr(self.parameter)

#
# Custom management command
#

class GAECommand(BaseCommand):
    """
    A Django custom management command tailored for our way of using Google
    App engine.
    """
    custom_options = (
        make_option(
            "--host",
            action="store",
            dest="host",
            default=None,
            help="specify the host to update, defaults to <app_id>.appspot.com"
        ),
    )
    option_list = BaseCommand.option_list + custom_options
    
    def authorize(self, options):
        """
        Setup all the GAE remote API bizness.
        """
        # Pull the app id
        app_id = self.get_app_id()
        # Figure out the URL to hit
        if options.get('host'):
            host = options.get('host')
        else:
            host = '%s.appspot.com' % app_id
        # Connect
        remote_api_stub.ConfigureRemoteDatastore(None, '/remote_api', self.login, host)
    
    def get_app_id(self):
        """
        Retrieves the id of the current app.
        """
        path = os.path.join(settings.ROOT_PATH, 'app.yaml')
        yaml_data = yaml.load(open(path))
        return yaml_data['application']
    
    def login(self):
        """
        Quickie method for logging in to the remote api. From GAE docs.
        """
        return raw_input('Email:'), getpass.getpass('Password:')

#
# YAML
#

def get_yaml(yaml_name):
    """
    Retrieves the yaml file with the provided name as a Python object.
    """
    yaml_path = os.path.join(settings.YAML_DIR, yaml_name)
    try:
        yaml_data = open(yaml_path)
    except:
        raise YAMLDoesNotExistError("YAML file could not be opened: %s" % yaml_name)
    try:
        yaml_obj = yaml.load(yaml_data)['table']
        yaml_obj['yaml_name'] = yaml_name
    except:
        raise InvalidYAMLError("YAML file is improperly formatted.")
    yaml_data.close()
    return yaml_obj


def get_all_yaml():
    """
    Returns a list of all the tables configured in the YAML_DIR
    in dictionary form.
    """
    file_list = FileIterator(settings.YAML_DIR)
    yaml_list = [i for i in file_list if i.endswith('.yaml')]
    return [get_yaml(i) for i in yaml_list]


def update_or_create_table(yaml_data):
    """
    If the Table outlined by the provided YAML file exists, it's updated.
    
    If it doesn't, it's created.

    Returns a tuple with the object first, and then a boolean that is True
    when the object was created.
    """
    obj = Table.get_by_key_name(yaml_data.get("slug", yaml_data['yaml_name']))
    
    if obj:
        obj.csv_name=yaml_data['file']
        obj.csv_data=prep_csv_for_db(yaml_data['file'])
        obj.yaml_name=yaml_data['yaml_name']
        obj.yaml_data=str(yaml_data)
        obj.title=yaml_data['title']
        obj.slug=yaml_data.get("slug", yaml_data['yaml_name'])
        obj.kicker=yaml_data.get('kicker', '')
        obj.byline=yaml_data.get("byline", '')
        obj.publication_date=yaml_data['publication_date']
        obj.legend=yaml_data.get('legend', '')
        obj.description=yaml_data.get('description', '')
        obj.footer=yaml_data.get('footer', '')
        obj.sources=yaml_data.get('sources', '')
        obj.credits=yaml_data.get('credits', '')
        obj.tags=get_tag_keys(yaml_data.get('tags', []))
        obj.is_published=yaml_data.get('is_published', False)
        obj.show_download_links=yaml_data.get("show_download_links", True)
        obj.show_in_feeds=yaml_data.get("show_in_feeds", True)
        obj.put()
        created = False
    else:
        obj = Table(
            key_name=yaml_data.get("slug", yaml_data['yaml_name']),
            csv_name=yaml_data['file'],
            csv_data=prep_csv_for_db(yaml_data['file']),
            yaml_name=yaml_data['yaml_name'],
            yaml_data=str(yaml_data),
            title=yaml_data['title'],
            slug=yaml_data.get("slug", yaml_data['yaml_name']),
            kicker=yaml_data.get("kicker", ""),
            byline=yaml_data.get("byline", ""),
            publication_date=yaml_data['publication_date'],
            legend=yaml_data.get('legend', ''),
            description=yaml_data.get('description', ''),
            footer=yaml_data.get('footer', ''),
            sources=yaml_data.get('sources', ''),
            credits=yaml_data.get('credits', ''),
            tags=get_tag_keys(yaml_data.get('tags', [])),
            is_published=yaml_data.get('is_published', False),
            show_download_links=yaml_data.get("show_download_links", True),
            show_in_feeds=yaml_data.get("show_in_feeds", True),
        )
        obj.put()
        created = True
    # Update the similarity lists of tables with the same tags
    taskqueue.add(
        url='/_/table/update-similar/',
        params=dict(key=obj.key()),
        method='GET'
    )
    return obj, created

#
# CSV
#

def get_csv(csv_name):
    """
    Return the csv file with the provided name as a Python file object.
    """
    try:
        csv_path = os.path.join(settings.CSV_DIR, csv_name)
        csv_data = open(csv_path, 'r')
    except:
        raise CSVDoesNotExistError("CSV file could not be opened: %s" % csv_name)
    return csv_data


def prep_csv_for_db(csv_name):
    """
    Retrieves the csv file with the provided name and returns a db.Text object
    that is ready to be inserted into the database.
    """
    # Open up the CSV file
    csv_data = get_csv(csv_name)
    # Load it into the CSV module
    csv_data = csv.reader(csv_data)
    # Convert that to a list
    csv_data = list(csv_data)
    # Convert that to JSON
    csv_data = simplejson.dumps(csv_data)
    # Finish db preparation by loading it into GAE thingie
    return db.Text(csv_data, encoding="utf-8")

#
# Tags
#

def get_tag_keys(tag_list):
    """
    Accepts a list of humanized tag names and returns a list of the db.Key's
    for the corresponding Tag model entries.
    """
    if not tag_list:
        return []
    key_list = []
    for tag_name in tag_list:
        obj = Tag.get_by_key_name(slugify(tag_name))
        if obj:
            key_list.append(obj.key())
        else:
            slug = slugify(tag_name)
            obj = Tag(title=tag_name, slug=slug, key_name=slug)
            obj.put()
            key_list.append(obj.key())
    return key_list


