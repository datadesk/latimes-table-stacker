from django.conf.urls.defaults import patterns, include, url
from table_stacker.feeds import LatestTables
from django.conf import settings
from django.contrib.syndication.views import feed
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Admin
    (r'^admin/', include(admin.site.urls)),
    # Dev static files, like admin media
    url(r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve'),
    # Prod static files, like css and js that power the public-facing pages
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
)

urlpatterns += patterns("table_stacker",
    # Homepage
    url(r'^$', 'views.table_index', name='table-index'),
    
    # Pagination
    url(r'^page/(?P<page>[0-9]+)/$', 'views.table_page', name='table-page'),
    
    # Serialization
    url(r'^api/(?P<slug>[-\w]+).xls$', 'api.table_xls', name='table-xls'),
    url(r'^api/(?P<slug>[-\w]+).json$', 'api.table_json', name='table-json'),
    url(r'^api/(?P<slug>[-\w]+).csv$', 'api.table_csv', name='table-csv'),
    
    # Extras
    url(r'^feeds/(?P<url>.*).xml$', feed,
        {'feed_dict': dict(latest=LatestTables)}, name='feeds'),
    url(r'^sitemap.xml$', 'views.sitemap', name='sitemap'),
    
    # Table detail
    url(r'^(?P<slug>[-\w]+)/$', 'views.table_detail', name='table-detail'),
)

