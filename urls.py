from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from table_stacker.models import Table
from table_stacker import views, api, feeds, sitemaps


urlpatterns = patterns('',
    # Dev static files, like admin media
    url(r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve'),
    # Prod static files, like css and js that power the public-facing pages
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
)

urlpatterns += patterns("",
    # Homepage
    url(r'^$', views.TableListView.as_view(), name='table-list'),
    
    # Serialization
    url(r'^api/(?P<slug>[-\w]+).xls$', api.TableDetailXLSView.as_view(),
        name='table-xls'),
    url(r'^api/(?P<slug>[-\w]+).json$', api.TableDetailJSONView.as_view(),
        name='table-json'),
    url(r'^api/(?P<slug>[-\w]+).csv$', api.TableDetailCSVView.as_view(),
        name='table-csv'),
    
    # Extras
    url(r'^feeds/latest/$', feeds.LatestTables(), name="table-feed"),
    
    url(r'^sitemap.xml$', sitemaps.SitemapView.as_view(), name='sitemap'),
    
    # Table detail
    url(r'^(?P<slug>[-\w]+)/$', views.TableDetailView.as_view(), name='table-detail'),
)

