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



