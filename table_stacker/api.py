import os
import csv
from models import Table
from django.conf import settings
from django.utils import simplejson
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render


def table_csv(request, slug):
    """
    A table, in CSV format.
    """
    # Get the csv data
    obj = get_object_or_404(Table, slug=slug)
    if not obj.is_published:
        raise Http404
    csv_path = os.path.join(settings.CSV_DIR, obj.csv_name)
    csv_data = open(csv_path, 'r').read()
    # Prep response
    response = HttpResponse(unicode(csv_data), mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slug
    return response


def table_xls(request, slug):
    """
    A table, in Excel format.
    
    Lifted from http://www.djangosnippets.org/snippets/911/
    """
    # Get the csv data
    obj = get_object_or_404(Table, slug=slug)
    if not obj.is_published:
        raise Http404
    csv_path = os.path.join(settings.CSV_DIR, obj.csv_name)
    context = {'csv': csv.reader(open(csv_path, 'r'))}
    # Prep an XLS response
    response = render(request, "table.xls.txt", context)
    response['Content-Disposition'] = 'attachment; filename=%s.xls' % slug
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    return response


def table_json(request, slug):
    """
    A table, in json format.
    """
    # Get the csv data
    obj = get_object_or_404(Table, slug=slug)
    if not obj.is_published:
        raise Http404
    csv_path = os.path.join(settings.CSV_DIR, obj.csv_name)
    csv_data = list(csv.reader(open(csv_path, 'r')))
    # Convert it to JSON key/value formatting
    headers = csv_data.pop(0)
    dict_list = []
    for row in csv_data:
        col_dict = {}
        for i, h in enumerate(headers):
            col_dict[h] = row[i]
        dict_list.append(col_dict)
    # Pass it out
    return HttpResponse(simplejson.dumps(dict_list), mimetype="text/javascript")
