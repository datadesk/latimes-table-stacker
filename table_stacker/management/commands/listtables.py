from django.conf import settings
from google.appengine.ext import db
from toolbox.FileIterator import FileIterator
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Print the names of all tables configured in the YAML repository'
    
    def handle(self, *args, **options):
        file_list = FileIterator(settings.YAML_DIR)
        yaml_list = [i for i in file_list if i.endswith('.yaml')]
        yaml_list.sort()
        for i in yaml_list:
            print i.replace(".yaml", "")

