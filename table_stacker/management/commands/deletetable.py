import os
import yaml
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
    help = 'Deletes the specified table from the datastore'
    args = '<table_file_name>'
    option_list = BaseCommand.option_list + custom_options
    
    def handle(self, *args, **options):
        # Make sure they provided a table name
        try:
            yaml_name = args[0]
        except:
            raise CommandError("You must provide the name of a table config file as the first argument.")
        
        # Set the host
        app_id = get_app_id()
        if options.get('host'):
            host = options.get('host')
        else:
            host = '%s.appspot.com' % app_id
        print host
        
        # Configure the remote connection
        remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)
        
        # Check if the table already exists in the datastore
        obj = Table.get_by_key_name(yaml_name)
        if obj:
            # If it does, delete it.
            print "Deleted %s" % obj
            obj.delete()
        else:
            raise CommandError("Table does not exist")


