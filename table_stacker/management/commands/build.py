import os
import math
import shutil
from django.http import Http404
from django.conf import settings
from table_stacker import views
from table_stacker.models import Table, Tag
from table_stacker.management.commands import *
from django.contrib.syndication.views import feed
from django.views.generic.simple import direct_to_template
from table_stacker.feeds import LatestTables


class Command(GAECommand):
    help = 'Bake out the entire site as flat files in the build directory'
    
    def write(self, path, data):
        outfile = open(os.path.join(settings.BUILD_DIR, path), 'w')
        outfile.write(data)
        outfile.close()

    def handle(self, *args, **options):
        
        print "Creating build directory"
        
        # Destroy the build directory, if it exists
        if os.path.exists(settings.BUILD_DIR):
            shutil.rmtree( settings.BUILD_DIR )
        
        # Then recreate it from scratch
        os.makedirs(settings.BUILD_DIR)
        
        # Copy the media directory
        print "Building media directory"
        shutil.copytree(settings.MEDIA_ROOT, os.path.join( settings.BUILD_DIR, 'media'))
        
        # Load all YAML files into the local database
        print "Filling database"
        [update_or_create_table(i) for i in get_all_yaml()]

        # Create a fake request we can use to fire up the pages
        rf = RequestFactory()

        # Build index page
        print "Building table lists"
        response = views.table_index(rf.get("/"))
        self.write('index.html', response.content)
        
        # Build table list pagination
        os.makedirs(os.path.join(settings.BUILD_DIR, 'page'))
        pages = int(math.ceil(Table.all().count() / 10.0))
        for page in range(1, pages+1):
            response = views.table_page(rf.get("/pages/%s/" % page), page)
            path = os.path.join(settings.BUILD_DIR, 'page', str(page))
            os.makedirs(path)
            self.write(os.path.join(path, 'index.html'), response.content)

        # Build table detail pages
        print "Building table detail pages"
        for table in Table.all():
            try:
                response = views.table_detail(rf.get("/%s/" % table.slug), table.slug)
            except Http404:
                continue
            path = os.path.join(settings.BUILD_DIR, table.slug)
            os.makedirs(path)
            self.write(os.path.join(path, 'index.html'), response.content)
        
        # JSON dumps of tables
        print "Building API dumps"
        path = os.path.join(settings.BUILD_DIR, "api")
        os.makedirs(path)
        for table in Table.all():
            # JSON
            try:
                response = views.table_json(rf.get("/%s/" % table.slug), table.slug)
            except Http404:
                continue
            self.write(os.path.join(path, '%s.json' % table.slug), response.content)
            # XLS
            try:
                response = views.table_xls(rf.get("/%s/" % table.slug), table.slug)
            except Http404:
                continue
            self.write(os.path.join(path, '%s.xls' % table.slug), response.content)
            # CSV
            data = open(os.path.join(settings.CSV_DIR, table.csv_name), "r").read()
            self.write(os.path.join(path, '%s.csv' % table.slug), data)
        
        # Tag pages
        print "Building tag pages"
        os.makedirs(os.path.join(settings.BUILD_DIR, 'tag'))
        for tag in Tag.all():
            table_set = Table.all().filter('tags =', tag.key()).filter("show_in_feeds =", True).filter("is_published =", True)
            pages = int(math.ceil(table_set.count() / 10.0))
            for page in range(1, pages+1):
                response = views.tag_page(rf.get("/tag/%s/page/%s/" % (tag.slug, page)), tag.slug, page)
                path = os.path.join(settings.BUILD_DIR, 'tag', tag.slug, 'page', str(page))
                os.makedirs(path)
                self.write(os.path.join(path, 'index.html'), response.content)
        
        # Sitemap
        print "Building sitemap"
        response = views.sitemap(rf.get("/sitemap.xml"))
        self.write('sitemap.xml', response.content)
        
        # RSS feeds
        print "Building RSS feeds"
        os.makedirs(os.path.join(settings.BUILD_DIR, 'feeds'))
        response = feed(rf.get("/feeds/latest.xml"), url='latest',
            feed_dict=dict(latest=LatestTables))
        self.write(os.path.join(settings.BUILD_DIR, 'feeds', 'latest.xml'),
            response.content)

