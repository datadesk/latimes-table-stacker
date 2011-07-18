from table_stacker.models import Table
from table_stacker.management.commands import *
from google.appengine.api.labs import taskqueue
from django.core.management.base import BaseCommand, CommandError


class Command(GAECommand):
    help = 'Deletes the specified table from the datastore'
    args = '<table_key_name>'
    
    def handle(self, *args, **options):
        # Make sure they provided a table name
        try:
            table_name = args[0]
        except:
            raise CommandError("You must provide the name of a table config file as the first argument.")
        
        # Login
        self.authorize(options)
        
        # Check if the table already exists in the datastore
        obj = Table.get_by_key_name(table_name)
        if obj:
            # If it does, delete it.
            print "Deleted %s" % obj
            obj.delete()
        else:
            raise CommandError("Table does not exist")
        # Update the related list of all the related documents
        taskqueue.add(
            url='/_/table/update-similar/',
            params=dict(key=obj.key()),
            method='GET'
        )
