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
        self.request = RequestFactory().get("/")
        html = self.get(self.request).render().content
        self.write('index.html', html)
    
    def write(self, path, data):
        outfile = open(os.path.join(settings.BUILD_DIR, path), 'w')
        outfile.write(data)
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
        self.request = RequestFactory().get("/%s/" % obj.slug)
        self.kwargs = {'slug': obj.slug}
        html = self.get(self.request).render().content
        path = os.path.join(settings.BUILD_DIR, obj.slug)
        self.write(path, html)

    def build_queryset(self):
        [self.build_object(obj) for obj in self.queryset]
    
    def write(self, path, data):
        os.path.exists(path) or os.makedirs(path)
        path = os.path.join(path, 'index.html')
        outfile = open(os.path.join(settings.BUILD_DIR, path), 'w')
        outfile.write(data)
        outfile.close()


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


