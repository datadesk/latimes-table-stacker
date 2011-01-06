import os
import csv
import yaml
from django.utils import simplejson
from django.conf import settings

# Models
from google.appengine.ext import db
from table_stacker.models import Table

# Auth
from google.appengine.ext.remote_api import remote_api_stub

# Command toys
from django.core.management.base import BaseCommand, CommandError
from table_stacker.management.commands import auth_func, get_app_id, custom_options


class Command(BaseCommand):
    help = 'Loads the specified table into the datastore'
    args = '<table_file_name>'
    option_list = BaseCommand.option_list + custom_options
    
    def handle(self, *args, **options):
        # Make sure they provided a table name
        try:
            yaml_name = args[0]
        except:
            raise CommandError("You must provide the name of a table config file as the first argument.")
        
        # Try to open the YAML file
        try:
            yaml_path = os.path.join(settings.YAML_DIR, '%s.yaml' % yaml_name)
            yaml_data = yaml.load(open(yaml_path))['table']
            yaml_raw = str(yaml_data)
        except IOError:
            raise
            raise CommandError("YAML file %s.yaml could not be opened" % yaml_name)
        
        # Set the host
        app_id = get_app_id()
        if options.get('host'):
            host = options.get('host')
        else:
            host = '%s.appspot.com' % app_id
        print host
        
        # Configure remote connection
        remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)
        
        # Check if the table already exists in the datastore
        obj = Table.get_by_key_name(yaml_name)
        if obj:
            print "Table already exists"
        else:
            print "Table does not yet exist."
        
        # Open up the CSV file
        try:
            csv_name = yaml_data['file']
            csv_path = os.path.join(settings.CSV_DIR, csv_name)
            print "Retrieving CSV data from %s" % csv_path
            csv_data = open(csv_path)
        except:
            raise CommandError("CSV file %s could not be opened" % csv_name)
        csv_data = db.Text(simplejson.dumps(list(csv.reader(csv_data))), encoding="utf-8")

        # Update the obj if it exists
        if obj:
            obj.csv_name=csv_name
            obj.csv_data=csv_data
            obj.yaml_name=yaml_name
            obj.yaml_data=yaml_raw
            obj.title=yaml_data['title']
            obj.slug=yaml_name
            obj.byline=yaml_data.get("byline", '')
            obj.publication_date=yaml_data['publication_date']
            obj.description=yaml_data.get('description', '')
            obj.footer=yaml_data.get('footer', '')
            obj.sources=yaml_data.get('source', '')
            obj.credits=yaml_data.get('credits', '')
            obj.tags=yaml_data.get('tags', [])
            obj.is_published=yaml_data.get('is_published', False)
            obj.put()
            print "Updated %s" % obj
        # Create it if it doesn't
        else:
            obj = Table(
                key_name=yaml_name,
                csv_name=csv_name,
                csv_data=csv_data,
                yaml_name=yaml_name,
                yaml_data=yaml_raw,
                title=yaml_data['title'],
                slug=yaml_name,
                byline=yaml_data.get("byline", ""),
                publication_date=yaml_data['publication_date'],
                description=yaml_data.get('description', ''),
                footer=yaml_data.get('footer', ''),
                sources=yaml_data.get('source', ''),
                credits=yaml_data.get('credits', ''),
                tags=yaml_data.get('tags', []),
                is_published=yaml_data.get('is_published', False),
            )
            obj.put()
            print "Created %s" % obj
        
