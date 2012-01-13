import os
from django.conf import settings
from table_stacker.models import Table
from django.test.client import RequestFactory
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.core.paginator import  InvalidPage, EmptyPage


class TableListView(ListView):
    """
    A list of all tables.
    """
    template_name = 'table_list.html'
    queryset = Table.live.all()
    
    def build(self):
        """
        Build the view as a flat HTML file.
        """
        # Make a fake request
        self.request = RequestFactory().get("/")
        # Render the list page as HTML
        html = self.get(self.request).render().content
        # Write it out to the appointed flat file
        path = os.path.join(settings.BUILD_DIR, 'index.html')
        outfile = open(path, 'w')
        outfile.write(html)
        outfile.close()


class TableDetailView(DetailView):
    """
    All about one table.
    """
    template_name = 'table_detail.html'
    queryset = Table.live.all()
    
    def get_context_data(self, **kwargs):
        context = super(TableDetailView, self).get_context_data(**kwargs)
        context.update({
            'size_choices': [1,2,3,4],
            'table': context['object'].get_tablefu(),
        })
        return context
    
    def build_object(self, obj):
        """
        Build a detail page as a flat HTML file.
        """
        # Make a fake request
        self.request = RequestFactory().get("/%s/" % obj.slug)
        # Set the kwargs to fetch this particular object
        self.kwargs = dict(slug=obj.slug)
        # Render the detail page HTML
        html = self.get(self.request).render().content
        # Create the path to save the flat file
        path = os.path.join(settings.BUILD_DIR, obj.slug)
        os.path.exists(path) or os.makedirs(path)
        path = os.path.join(path, 'index.html')
        # Write out the data
        outfile = open(path, 'w')
        outfile.write(html)
        outfile.close()
    
    def build_queryset(self):
        """
        Build flat HTML files for all of the objects in the queryset.
        """
        [self.build_object(obj) for obj in self.queryset]


def sitemap(request):
    """
    A sitemap.xml file for Google and other search engines.
    """
    table_list = Table.live.all()
    context = {
        'table_list': table_list,
    }
    response = render(request, 'sitemap.xml', context)
    response.mimetype='text/xml'
    return response


