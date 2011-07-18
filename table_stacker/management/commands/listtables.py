from toolbox import ptable
from django.conf import settings
from google.appengine.ext import db
from table_stacker.management.commands import *
from toolbox.FileIterator import FileIterator
from django.core.management.base import BaseCommand, CommandError


class Command(GAECommand):
    help = 'Report on all the tables configured in the YAML repository'
    
    def handle(self, *args, **options):
        
        # Login
        self.authorize(options)
        
        results = []
        for i in get_all_yaml():
            obj = Table.get_by_key_name(i.get("slug"))
            if obj:
                exists = 'Y'
            else:
                exists = 'N'
            results.append([i.get("yaml_name"), exists])
        results.sort(key=lambda x: x[0])
        print ptable.indent(
            [['yaml', 'exists']] + results, 
            hasHeader=True, 
            separateRows=False,
            prefix='| ', postfix=' |',
        )
