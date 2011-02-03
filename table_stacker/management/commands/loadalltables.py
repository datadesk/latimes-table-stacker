from table_stacker.management.commands import GAECommand, get_all_yaml, update_or_create_table


class Command(GAECommand):
    help = 'Loads all tables into the datastore'
    
    def handle(self, *args, **options):
        
        # Login
        self.authorize(options)
        
        # Loop through all the table configs
        for yaml_name in get_all_yaml():
            # ...and make it happen
            obj, created = update_or_create_table(yaml_name)
            if created:
                print "Created %s" % obj
            else:
                print "Updated %s" % obj
        
