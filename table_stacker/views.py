# Response helpers
from django.http import Http404, HttpResponse
from django.views.generic.simple import direct_to_template

# Models
from google.appengine.ext import db
from table_stacker.models import Table

# Pagination
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# Cache
from google.appengine.api import memcache

#
# Caching, grouping and the like
#

def get_cached_response(request, cache_key):
    """
    Returns a cached response, if one exists. Returns None if it doesn't.
    
    Provide your request object and the cache_key.
    """
    # Hit the cache and see if it already has this key
    cached_data = memcache.get(cache_key)
    # If it does, return the cached data (unless we force a reload with the qs)
    if cached_data is not None and not request.GET.get('force', None):
        return cached_data


def table_index(request):
    """
    A list of all the public tables
    """
    cache_key = 'table_index'
    cached_response = get_cached_response(request, cache_key)
    if cached_response:
        return cached_response
    else:
        object_list = Table.all().filter(
                "is_published =", True
            ).order("-publication_date")
        # Cut it first 10
        paginator = Paginator(object_list, 10)
        try:
            page = paginator.page(1)
        except (EmptyPage, InvalidPage):
            raise Http404
        # Create the response
        context = {
            'index': True,
            'object_list': page.object_list,
            'page_number': page.number,
            'has_next': page.has_next(),
            'next_page_number': page.next_page_number(),
        }
        response = direct_to_template(request, 'index.html', context)
        # Add it to the cache
        memcache.add(cache_key, response, 60)
        # Pass it back
        return response


def table_detail(request, slug):
    """
    A detail page all about one of the tables.
    """
    cache_key = 'table_detail:%s' % slug
    cached_response = get_cached_response(request, cache_key)
    if cached_response:
        return cached_response
    else:
        # Pull the object
        obj = Table.all().filter("slug =", slug).get()
        if not obj:
            # Drop out if it doesn't
            raise Http404
        response = HttpResponse(obj.get_rendered_html())
        memcache.add(cache_key, response, 60)
        return response
