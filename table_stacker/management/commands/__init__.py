"""
Utilities shared by multiple custom management commands.
"""
import os
import csv
import yaml
from django.conf import settings
from django.utils import simplejson
from toolbox.slugify import slugify
from toolbox.FileIterator import FileIterator
from table_stacker.models import Table, Tag
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.core.handlers.wsgi import WSGIRequest
from django.core.management.base import BaseCommand, CommandError


class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.
    
    Usage:
    
    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})
    
    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client
    
    Once you have a request object you can pass it to any view function, 
    just as if that view had been hooked up using a URLconf.
    
    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)


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
    try:
        obj = Table.objects.get(slug=yaml_data.get("slug", yaml_data['yaml_name']))
    except Table.DoesNotExist:
        obj = None

    if obj:
        obj.csv_name=yaml_data['file']
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
        obj.is_published=yaml_data.get('is_published', False)
        obj.show_download_links=yaml_data.get("show_download_links", True)
        obj.show_in_feeds=yaml_data.get("show_in_feeds", True)
        obj.tags.clear()
        [obj.tags.add(i) for i in get_tag_list(yaml_data.get('tags', []))]
        obj.save()
        obj.save()
        created = False
    else:
        obj = Table(
            csv_name=yaml_data['file'],
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
            is_published=yaml_data.get('is_published', False),
            show_download_links=yaml_data.get("show_download_links", True),
            show_in_feeds=yaml_data.get("show_in_feeds", True),
        )
        obj.save()
        [obj.tags.add(i) for i in get_tag_list(yaml_data.get('tags', []))]
        obj.save()
        created = True
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

#
# Tags
#

def get_tag_list(tag_list):
    """
    Accepts a list of humanized tag names and returns a list of the db.Key's
    for the corresponding Tag model entries.
    """
    if not tag_list:
        return []
    obj_list = []
    for tag_name in tag_list:
        try:
            obj = Tag.objects.get(slug=slugify(tag_name))
        except Tag.DoesNotExist:
            obj = None
        if obj:
            obj_list.append(obj)
        else:
            slug = slugify(tag_name)
            obj = Tag(title=tag_name, slug=slug)
            obj.save()
            obj_list.append(obj)
    return obj_list


