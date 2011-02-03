from table_stacker.models import Table
from table_stacker.management.commands import *


class Command(GAECommand):
    help = 'Delete all tables in the datastore'
    
    def handle(self, *args, **options):
        
        # Login
        self.authorize(options)
        
        # Loop through them...
        for obj in Table.all():
            # ... and do the deed.
            print "Deleted %s" % obj
            obj.delete()

