import os
import math
import yaml
import shutil
from django.http import Http404
from django.conf import settings
from django.core import management
from django.shortcuts import render
from table_stacker import views, api
from table_stacker.models import Table
from table_stacker.feeds import LatestTables
from toolbox.FileIterator import FileIterator
from django.test.client import RequestFactory
from django.contrib.syndication.views import feed
from django.core.management.base import BaseCommand


class YAMLDoesNotExistError(Exception):
    """
    Called when you try to open a YAML that doesn't exist.
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


class Command(BaseCommand):
    help = 'Bake out the entire site as static files in the build directory'
    
    def get_yaml(self, yaml_name):
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
    
    def get_all_yaml(self):
        """
        Returns a list of all the tables configured in the YAML_DIR
        in dictionary form.
        """
        file_list = FileIterator(settings.YAML_DIR)
        yaml_list = [i for i in file_list if i.endswith('.yaml')]
        return [self.get_yaml(i) for i in yaml_list]
    
    def write(self, path, data):
        outfile = open(os.path.join(settings.BUILD_DIR, path), 'w')
        outfile.write(data)
        outfile.close()
    
    def handle(self, *args, **options):
        
        self.stdout.write("Creating build directory\n")
        
        # Destroy the build directory, if it exists
        if os.path.exists(settings.BUILD_DIR):
            shutil.rmtree( settings.BUILD_DIR )
        
        # Then recreate it from scratch
        os.makedirs(settings.BUILD_DIR)
        
        # Copy the static files
        self.stdout.write("Building static files\n")
        management.call_command("collectstatic", interactive=False, verbosity=0)
        shutil.copytree(settings.STATIC_ROOT, os.path.join(settings.BUILD_DIR, 'static'))
        shutil.copytree(settings.MEDIA_ROOT, os.path.join(settings.BUILD_DIR, 'media'))
        
        # Load all YAML files into the local database
        self.stdout.write("Building database\n")
        [Table.objects.update_or_create(i) for i in self.get_all_yaml()]
        
        # Create a fake request we can use to fire up the pages
        rf = RequestFactory()
        
        # Build index page
        self.stdout.write("Building table lists\n")
        response = views.table_index(rf.get("/"))
        self.write('index.html', response.content)
        
        # Build table list pagination
        os.makedirs(os.path.join(settings.BUILD_DIR, 'page'))
        pages = int(math.ceil(Table.objects.all().count() / 10.0))
        for page in range(1, pages+1):
            response = views.table_page(rf.get("/pages/%s/" % page), page)
            path = os.path.join(settings.BUILD_DIR, 'page', str(page))
            os.makedirs(path)
            self.write(os.path.join(path, 'index.html'), response.content)
        
        # Build table detail pages
        self.stdout.write("Building table detail pages\n")
        for table in Table.objects.all():
            try:
                response = views.table_detail(rf.get("/%s/" % table.slug), table.slug)
            except Http404:
                continue
            path = os.path.join(settings.BUILD_DIR, table.slug)
            os.makedirs(path)
            self.write(os.path.join(path, 'index.html'), response.content)
        
        # JSON dumps of tables
        self.stdout.write("Building API dumps\n")
        path = os.path.join(settings.BUILD_DIR, "api")
        os.makedirs(path)
        for table in Table.objects.all():
            # JSON
            try:
                response = api.table_json(rf.get("/api/%s.json" % table.slug), table.slug)
            except Http404:
                continue
            self.write(os.path.join(path, '%s.json' % table.slug), response.content)
            # XLS
            try:
                response = api.table_xls(rf.get("/api/%s.xls" % table.slug), table.slug)
            except Http404:
                continue
            self.write(os.path.join(path, '%s.xls' % table.slug), response.content)
            # CSV
            try:
                response = api.table_csv(rf.get("/api/%s.csv" % table.slug), table.slug)
            except Http404:
                continue
            self.write(os.path.join(path, '%s.csv' % table.slug), response.content)
        
        # Sitemap
        self.stdout.write("Building sitemap\n")
        response = views.sitemap(rf.get("/sitemap.xml"))
        self.write('sitemap.xml', response.content)
        
        # Build 404 page
        self.stdout.write("Building 404 page\n")
        response = render(rf.get("/404.html"), '404.html', {})
        self.write('404.html', response.content)
        
        # RSS feeds
        self.stdout.write("Building RSS feeds\n")
        os.makedirs(os.path.join(settings.BUILD_DIR, 'feeds'))
        response = feed(rf.get("/feeds/latest.xml"), url='latest',
            feed_dict=dict(latest=LatestTables))
        self.write(os.path.join(settings.BUILD_DIR, 'feeds', 'latest.xml'),
            response.content)

