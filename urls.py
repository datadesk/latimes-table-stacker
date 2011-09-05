from django.conf.urls.defaults import patterns, include, url
from table_stacker.feeds import LatestTables
from django.contrib.syndication.views import feed
from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.views import serve

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('table_stacker.views',
    # Admin
    (r'^admin/', include(admin.site.urls)),
    url(r'^static/(?P<path>.*)$', serve),
    
    # Homepage
    url(r'^$', 'table_index', name='table-index'),
    
    # Pagination
    url(r'^page/(?P<page>[0-9]+)/$', 'table_page', name='table-page'),
    url(r'^tag/(?P<tag>.*)/page/(?P<page>[0-9]+)/$', 'tag_page', name='tag-page'),
    
    # Serialization
    url(r'^api/(?P<slug>[-\w]+).xls$', 'table_xls', name='table-xls'),
    url(r'^api/(?P<slug>[-\w]+).json$', 'table_json', name='table-json'),
    url(r'^api/(?P<slug>[-\w]+).csv$', 'table_csv', name='table-csv'),
    
    # Extras
    url(r'^feeds/(?P<url>.*).xml$', feed,
        {'feed_dict': dict(latest=LatestTables)}, name='feeds'),
    url(r'^sitemap.xml$', 'sitemap', name='sitemap'),
    
    # Table detail
    url(r'^(?P<slug>[-\w]+)/$', 'table_detail', name='table-detail'),
)

