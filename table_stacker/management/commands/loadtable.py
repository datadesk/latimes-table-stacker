from table_stacker.management.commands import *
from django.core.management.base import CommandError


class Command(GAECommand):
    help = 'Loads the specified table into the datastore'
    args = '<table_file_name>'
    
    def handle(self, *args, **options):
        # Make sure they provided a table name
        try:
            yaml_name = args[0]
        except:
            raise CommandError("You must provide the name of a table config file as the first argument.")
        
        # Login
        self.authorize(options)
        
        # Make it happen
        yaml_obj = get_yaml("%s.yaml" % yaml_name)
        obj, created = update_or_create_table(yaml_obj)
        if created:
            print "Created %s" % obj
        else:
            print "Updated %s" % obj
        
