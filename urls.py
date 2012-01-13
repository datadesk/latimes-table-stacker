from django.conf.urls.defaults import patterns, include, url
from table_stacker.feeds import LatestTables
from table_stacker.models import Table
from django.conf import settings
from django.contrib.syndication.views import feed
from table_stacker.views import TableListView, TableDetailView
from table_stacker import api


urlpatterns = patterns('',
    # Dev static files, like admin media
    url(r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve'),
    # Prod static files, like css and js that power the public-facing pages
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
)

urlpatterns += patterns("table_stacker",
    # Homepage
    url(r'^$', TableListView.as_view(), name='table-list'),
    
    # Serialization
    url(r'^api/(?P<slug>[-\w]+).xls$', api.TableDetailXLSView.as_view(),
        name='table-xls'),
    url(r'^api/(?P<slug>[-\w]+).json$', api.TableDetailJSONView.as_view(),
        name='table-json'),
    url(r'^api/(?P<slug>[-\w]+).csv$', api.TableDetailCSVView.as_view(),
        name='table-csv'),
    
    # Extras
    url(r'^feeds/(?P<url>.*).xml$', feed,
        {'feed_dict': dict(latest=LatestTables)}, name='feeds'),
    url(r'^sitemap.xml$', 'views.sitemap', name='sitemap'),
    
    # Table detail
    url(r'^(?P<slug>[-\w]+)/$', TableDetailView.as_view(), name='table-detail'),
)

