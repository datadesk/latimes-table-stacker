import os
import csv
from models import Table
from django.conf import settings
from django.shortcuts import render
from django.utils import simplejson
from django.http import HttpResponse
from django.views.generic import DetailView
from django.test.client import RequestFactory


class TableBaseAPIView(DetailView):
    """
    The basics necessary to publish a table outside of HTML.
    """
    queryset = Table.live.all()
    
    def build_object(self, obj):
        """
        Build a detail page as a flat HTML file.
        """
        # Make a fake request
        self.request = RequestFactory().get("/api/%s.%s" % (obj.slug, self.response_type))
        # Set the kwargs to fetch this particular object
        self.kwargs = dict(slug=obj.slug)
        # Render the detail page HTML
        html = self.get(self.request).content
        # Create the path to save the flat file
        path = os.path.join(settings.BUILD_DIR, "api")
        os.path.exists(path) or os.makedirs(path)
        path = os.path.join(path, '%s.%s' % (obj.slug, self.response_type))
        # Write out the data
        outfile = open(path, 'w')
        outfile.write(html)
        outfile.close()
    
    def build_queryset(self):
        """
        Build flat HTML files for all of the objects in the queryset.
        """
        [self.build_object(obj) for obj in self.queryset]


class TableDetailCSVView(TableBaseAPIView):
    """
    Publish a table as CSV.
    """
    response_type = 'csv'
    
    def render_to_response(self, context):
        path = os.path.join(settings.CSV_DIR, context['object'].csv_name)
        data = open(path, 'r').read()
        response = HttpResponse(unicode(data), mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % context['object'].slug
        return response


class TableDetailXLSView(TableBaseAPIView):
    """
    Publish a table as XLS.
    """
    response_type = 'xls'
    
    def render_to_response(self, context):
        path = os.path.join(settings.CSV_DIR, context['object'].csv_name)
        context['csv'] = csv.reader(open(path, 'r'))
        response = render(self.request, "table.xls.txt", context)
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % context['object'].slug
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
        return response


class TableDetailJSONView(TableBaseAPIView):
    """
    Publish a table as JSON.
    """
    response_type = 'json'
    
    def render_to_response(self, context):
        path = os.path.join(settings.CSV_DIR, context['object'].csv_name)
        data = list(csv.reader(open(path, 'r')))
        headers = data.pop(0)
        dict_list = []
        for row in data:
            col_dict = {}
            for i, h in enumerate(headers):
                col_dict[h] = row[i]
            dict_list.append(col_dict)
        return HttpResponse(simplejson.dumps(dict_list),
            mimetype="text/javascript")

