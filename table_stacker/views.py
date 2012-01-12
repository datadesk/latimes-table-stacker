from django.conf import settings
from table_stacker.models import Table
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.core.paginator import  InvalidPage, EmptyPage
from django.http import Http404, HttpResponse, HttpResponseRedirect


def get_table_page(request, page):
    """
    Creates a page of tables for our index and pagination system.
    """
    # Pull the data
    qs = Table.live.all()
    paginator = Paginator(qs, 10)
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
    return render(request, 'table_list.html', context)


def table_index(request):
    """
    A list of all the public tables
    """
    return get_table_page(request, 1)


def table_page(request, page):
    """
    A page of documents as we leaf back through everything in reverse chron.
    """
    # Send /page/1/ back to the index url
    if page == '1':
        return HttpResponseRedirect('/')
    return get_table_page(request, page)


def table_detail(request, slug):
    """
    A detail page all about one of the tables.
    """
    obj = get_object_or_404(Table, slug=slug)
    if not obj.is_published:
        raise Http404
    context = {
        'object': obj,
        'table': obj.get_tablefu(),
        'size_choices': [1,2,3,4],
    }
    return render(request, 'table_detail.html', context)


def sitemap(request):
    """
    Create a sitemap.xml file for Google and other search engines.
    """
    table_list = Table.live.all()
    context = {
        'table_list': table_list,
    }
    response = render(request, 'sitemap.xml', context)
    response.mimetype='text/xml'
    return response


