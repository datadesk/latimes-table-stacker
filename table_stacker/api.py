import os
import csv
from models import Table
from django.conf import settings
from django.shortcuts import render
from django.utils import simplejson
from django.http import HttpResponse
from bakery.views import BuildableDetailView, BuildableListView


class TableBaseAPIView(BuildableDetailView):
    """
    The basics necessary to publish a table outside of HTML.
    """
    queryset = Table.live.all()
    
    def get_csv_data(self, obj):
        path = os.path.join(settings.CSV_DIR, obj.csv_name)
        return open(path, 'r')
    
    def get_html(self):
        return self.get(self.request).content
    
    def get_build_path(self, obj):
        api_dir = os.path.join(
            settings.BUILD_DIR,
            'api',
        )
        os.path.exists(api_dir) or os.mkdir(api_dir)
        return os.path.join(settings.BUILD_DIR, self.get_url(obj)[1:])


class TableDetailCSVView(TableBaseAPIView):
    """
    Publish a table as CSV.
    """
    def get_url(self, obj):
        return obj.get_csv_url()
    
    def render_to_response(self, context):
        data = self.get_csv_data(context['object']).read()
        response = HttpResponse(unicode(data), mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % context['object'].slug
        return response


class TableDetailXLSView(TableBaseAPIView):
    """
    Publish a table as XLS.
    """
    def get_url(self, obj):
        return obj.get_xls_url()
    
    def render_to_response(self, context):
        data = self.get_csv_data(context['object'])
        context['csv'] = csv.reader(data)
        response = render(self.request, "table.xls.txt", context)
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % context['object'].slug
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
        return response


class TableDetailJSONView(TableBaseAPIView):
    """
    Publish a table as JSON.
    """
    def get_url(self, obj):
        return obj.get_json_url()
    
    def render_to_response(self, context):
        data = self.get_csv_data(context['object'])
        data = list(csv.reader(data))
        headers = data.pop(0)
        dict_list = []
        for row in data:
            col_dict = {}
            for i, h in enumerate(headers):
                col_dict[h] = row[i]
            dict_list.append(col_dict)
        return HttpResponse(
            simplejson.dumps(dict_list),
            mimetype="text/javascript"
        )

