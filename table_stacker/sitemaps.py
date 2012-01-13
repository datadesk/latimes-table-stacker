import os
from models import Table
from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView
from django.test.client import RequestFactory


class SitemapView(ListView):
    """
    A list of all tables in a Sitemap ready for Google.
    """
    template_name = 'sitemap.xml'
    queryset = Table.objects.filter(is_published=True, show_in_feeds=True)
    
    def render_to_response(self, context):
        return render(self.request, 'sitemap.xml', context,
            content_type="text/xml")
    
    def build_queryset(self):
        """
        Build the view as a flat HTML file.
        
        Example usage:
            
            SitemapView().build_queryset()
        
        """
        # Make a fake request
        self.request = RequestFactory().get("/")
        # Render the list page as HTML
        html = self.get(self.request).content
        # Write it out to the appointed flat file
        path = os.path.join(settings.BUILD_DIR, 'sitemap.xml')
        outfile = open(path, 'w')
        outfile.write(html)
        outfile.close()
