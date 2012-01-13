import os
from models import Table
from datetime import datetime
from django.conf import settings
from django.test.client import RequestFactory
from django.contrib.syndication.views import Feed


class LatestTables(Feed):
    title = "Latest spreadsheets"
    link = "/feeds/latest/"
    title_template = "feeds/table_title.html"
    description_template = "feeds/table_description.html"
    
    def items(self):
        qs = Table.objects.filter(is_published=True, show_in_feeds=True)
        return qs.order_by("-publication_date")[:10]
    
    def item_pubdate(self, item):
        return datetime(*(item.publication_date.timetuple()[:6]))
    
    def build(self):
        # Make a fake request
        request = RequestFactory().get(self.link)
        # Generate the page
        data = self(request).content
        # Write it out to the appointed flat file
        path = os.path.join(settings.BUILD_DIR, 'feeds')
        os.path.exists(path) or os.makedirs(path)
        path = os.path.join(path, 'latest.xml')
        outfile = open(path, 'w')
        outfile.write(data)
        outfile.close()
