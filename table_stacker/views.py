# Response helpers
import csv
from django.utils import simplejson
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template

# Models
from google.appengine.ext import db
from table_stacker.models import Table, Tag

# Pagination
from django.core.paginator import Paginator
from django.core.paginator import  InvalidPage, EmptyPage

# Cache
from django.conf import settings
from google.appengine.api import memcache
from toolbox.cache import get_cache_key, get_cached_response


#
# The biz
#

def get_table_page(request, page):
    """
    Creates a page of tables for our index and pagination system.
    """
    # Pull the data
    qs = Table.all()
    object_list = qs.filter("is_published =", True).filter("show_in_feeds =", True).order("-publication_date")
    paginator = Paginator(object_list, 10)
    # Limit it to thise page
    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        raise Http404
    # Create a response and pass it back
    context = {
        'headline': 'Latest spreadsheets',
        'object_list': page.object_list,
        'page_number': page.number,
        'has_next': page.has_next(),
        'next_page_number': page.next_page_number(),
    }
    return direct_to_template(request, 'table_list.html', context)


def table_index(request):
    """
    A list of all the public tables
    """
    # Check if the page is cached
    cache_key = 'table_index'
    cached_response = get_cached_response(request, cache_key)
    if cached_response:
        return cached_response
    # If not, get the data
    response = get_table_page(request, 1)
    # Add it to the cache
    memcache.add(cache_key, response, 60)
    # Pass it back
    return response


def table_page(request, page):
    """
    A page of documents as we leaf back through everything in reverse chron.
    """
    # Send /page/1/ back to the index url
    if page == '1':
        return HttpResponseRedirect('/')
    # Check if it's cached
    cache_key = 'table_page:%s' % page
    cached_response = get_cached_response(request, cache_key)
    if cached_response:
        return cached_response
    # If not, get the data
    response = get_table_page(request, page)
    # Add it to the cache
    memcache.add(cache_key, response, 60)
    # Pass it back
    return response


def tag_page(request, tag, page):
    """
    Lists tables with a certain tag.
    """
    # Check if the page is cached
    cache_key = 'tag_page:%s-%s' % (tag, page)
    cached_response = get_cached_response(request, cache_key)
    if cached_response:
        return cached_response
    # Get the data
    tag = Tag.get_by_key_name(tag)
    if not tag:
        raise Http404
    object_list = Table.all().filter("is_published =", True).filter("show_in_feeds =", True).filter('tags =', tag.key())
    paginator = Paginator(object_list, 10)
    # Limit it to thise page
    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        raise Http404
    # Create a response and pass it back
    context = {
        'headline': 'Spreadsheets tagged &lsquo;%s&rsquo;' % tag.title,
        'object_list': page.object_list,
        'page_number': page.number,
        'has_next': page.has_next(),
        'next_page_number': page.next_page_number(),
    }
    return direct_to_template(request, 'table_list.html', context)


def table_detail(request, slug):
    """
    A detail page all about one of the tables.
    """
    # Check if it's cached
    cache_key = 'table_detail:%s' % slug
    cached_response = get_cached_response(request, cache_key)
    if cached_response:
        return cached_response
    # If not, get the data
    obj = Table.get_by_key_name(slug)
    if not obj or not obj.is_published:
        raise Http404
    context = {
        'object': obj,
        'force': request.GET.get('force', None),
    }
    response = direct_to_template(request, 'table_detail.html', context)
    memcache.add(cache_key, response, 60)
    return response


def table_xls(request, slug):
    """
    A table, in Excel format.
    
    Lifted from http://www.djangosnippets.org/snippets/911/
    """
    # Get the data
    obj = Table.get_by_key_name(slug)
    if not obj or not obj.is_published:
        raise Http404
    csv_data = simplejson.loads(unicode(obj.csv_data))
    context = {'csv': csv_data}
    # Prep an XLS response
    response = direct_to_template(request, "table.xls.txt", context)
    response['Content-Disposition'] = 'attachment; filename=%s.xls' % slug
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    return response


def table_json(request, slug):
    """
    A table, in json format.
    """
    # Get the csv data
    obj = Table.get_by_key_name(slug)
    if not obj or not obj.is_published:
        raise Http404
    csv_data = simplejson.loads(unicode(obj.csv_data))
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


def sitemap(request):
    """
    Create a sitemap.xml file for Google and other search engines.
    """
    table_list = Table.all().filter("is_published =", True).filter("show_in_feeds =", True).order("-publication_date")
    tag_list = Tag.all()
    context = {
        'tag_list': tag_list,
        'table_list': table_list,
    }
    return direct_to_template(request, 'sitemap.xml', context, mimetype='text/xml')




