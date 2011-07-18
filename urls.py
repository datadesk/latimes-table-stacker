# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *
from table_stacker.feeds import LatestTables
from django.contrib.syndication.views import feed
from django.views.generic.simple import redirect_to

urlpatterns = patterns('table_stacker.views',
    # Homepage
    url(r'^$', 'table_index', name='table-index'),
    
    # Pagination
    url(r'^page/(?P<page>[0-9]+)/$', 'table_page', name='table-page'),
    url(r'^tag/(?P<tag>.*)/page/(?P<page>[0-9]+)/$', 'tag_page', name='tag-page'),
    
    # Serialization
    url(r'^xls/(?P<slug>[-\w]+)/$', 'table_xls', name='table-xls'),
    url(r'^json/(?P<slug>[-\w]+)/$', 'table_json', name='table-json'),
    
    # Table detail
    url(r'^(?P<slug>[-\w]+)/$', 'table_detail', name='table-detail'),
    
    # Extras
    url(r'^feeds/(?P<url>.*)/$', feed,
        {'feed_dict': dict(latest=LatestTables,)}, name='feeds'),
    url(r'^sitemap.xml$', 'sitemap', name='sitemap')
)

