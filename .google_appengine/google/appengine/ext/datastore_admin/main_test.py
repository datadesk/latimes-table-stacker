#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#

"""Tests for google.appengine.ext.datastore_admin.main."""


import datetime
import os
import tempfile

from google.testing.pybase import googletest
from google.appengine.api import datastore
from google.appengine.api import datastore_errors
from google.appengine.ext.datastore_admin import delete_handler
from google.appengine.ext.datastore_admin import main
from google.appengine.ext.datastore_admin import testutil
from google.appengine.ext.datastore_admin import utils
from google.appengine.ext.db import stats
from google.appengine.ext.webapp import mock_webapp


class MainTest(googletest.TestCase):
  """Tests for main module."""

  def testCreateApplication(self):
    """Test CreateApplication function."""
    main.CreateApplication()


class RouteActionHandlerTest(testutil.HandlerTestBase):

  def CreateStatEntity(self,
                       kind,
                       kind_name=None,
                       property_type=None,
                       property_name=None):
    """Create a single Statistic datastore entity.

    Args:
      kind: The name of the kind to store.
      kind_name: The value of the 'kind_name' property to set on the entity.
      property_type: The value of the 'property_type' property to set on the
        entity.
      property_name: The value of the 'property_name' property to set on the
        entity.
    """
    stat = datastore.Entity(kind)
    stat['bytes'] = 4
    stat['count'] = 2
    stat['timestamp'] = self.timestamp
    if kind_name is not None:
      stat['kind_name'] = kind_name
    if property_type is not None:
      stat['property_type'] = property_type
    if property_name is not None:
      stat['property_name'] = property_name
    datastore.Put(stat)

  def GetStats(self,
               stored_kind,
               timestamp=None,
               limit=1000):
    """Fetch datastore stats entities from an application's datastore.

    Args:
      stored_kind: kind name of the statistic in the datastore.
      timestamp: datetime.datetime timestamp to look for on the stat.
      limit: the maximum number of kind stats to try and fetch.

    Returns:
      list of datastore.Entity instances or None on error.
    """
    query = datastore.Query(stored_kind)
    if timestamp:
      query.update({'timestamp =': timestamp})

    try:
      results = query.Get(limit)
    except datastore_errors.Error:
      logging.exception('%s get failed.', stored_kind)
      return None

    return results

  def WrapRenderToResponse(self, handler, template_file, template_params):
    self.params = template_params
    self.render(handler, template_file, template_params)

  def setUp(self):
    """Sets up the test harness."""
    testutil.HandlerTestBase.setUp(self)
    self.timestamp = datetime.datetime.utcfromtimestamp(40)
    self.params = {}
    self.render = utils.RenderToResponse
    utils.RenderToResponse = self.WrapRenderToResponse
    self.ACTION = 'Delete'
    self.handler = main.RouteByActionHandler()
    self.handler.initialize(mock_webapp.MockRequest(),
                            mock_webapp.MockResponse())

    self.handler.request.path = '/_ah/datastore_admin/'
    self.handler.request.query_string = 'not-checked'
    self.render_called = False

  def testRouteActionHandler(self):
    """Test action is routed to ConfirmDeleteHandler."""
    def MockRender(handler):
      self.render_called = True
    self.handler.request.set('action', self.ACTION)
    self.assertFalse(self.render_called)
    main.GET_ACTIONS[self.ACTION] = MockRender
    self.handler.get()
    self.assertTrue(self.render_called)

  def testListActionRenders(self):
    """Test list action page renders."""
    self.handler.get()

  def testKindsRendering(self):
    """Test list of kinds renders in list_actions with supplied list."""
    get_schema_test_kinds = ['test1', 'test2']
    self.handler.request.set('kind', get_schema_test_kinds)
    self.handler.get()
    response = self.handler.response.out.getvalue()
    kind_list = [stat['kind_name'] for stat in self.params['kind_stats']]
    self.assertListEqual(kind_list, get_schema_test_kinds)

  def testExcludeNotInList(self):
    """Test kinds in datastore stats that are not in get schema list excluded.
    """
    stat_test_kinds = ['test1', 'test2', 'test3']
    get_schema_test_kinds = ['test1', 'test2']
    self.CreateStatEntity(stats.GlobalStat.STORED_KIND_NAME)
    for kind in stat_test_kinds:
      self.CreateStatEntity(stats.KindStat.STORED_KIND_NAME, kind)
    self.handler.request.set('kind', get_schema_test_kinds)
    self.handler.get()
    kind_list = [stat['kind_name'] for stat in self.params['kind_stats']]
    self.assertListEqual(kind_list, get_schema_test_kinds)

  def testIncludeNotInStats(self):
    """Test kinds in datastore stats that are not in get schema list excluded.
    """
    stat_test_kinds = ['test1', 'test2']
    get_schema_test_kinds = ['test1', 'test2', 'test3']
    self.CreateStatEntity(stats.GlobalStat.STORED_KIND_NAME)
    for kind in stat_test_kinds:
      self.CreateStatEntity(stats.KindStat.STORED_KIND_NAME, kind)
    self.handler.request.set('kind', ['test1', 'test2', 'test3'])
    self.handler.get()
    kind_list = [stat['kind_name'] for stat in self.params['kind_stats']]
    self.assertListEqual(kind_list, get_schema_test_kinds)

  def testKindsRenderingFromStats(self):
    """Test list of kinds renders in list_actions with no supplied list."""
    stat_test_kinds = ['test1', 'test2', 'test3']
    self.CreateStatEntity(stats.GlobalStat.STORED_KIND_NAME)
    for kind in stat_test_kinds:
      self.CreateStatEntity(stats.KindStat.STORED_KIND_NAME, kind)
    self.handler.get()
    kind_list = [stat['kind_name'] for stat in self.params['kind_stats']]
    self.assertListEqual(kind_list, stat_test_kinds)

  def testInvalidActionRenders(self):
    """Test invalid action renders."""
    self.handler.request.set('action', 'not-an-action')
    self.handler.get()

  def testListActionCalled(self):
    """Test list action is called when no action is present."""
    def MockRender():
      self.render_called = True
    self.handler.ListActions = MockRender
    self.handler.get()
    self.assertTrue(self.render_called)


class StaticResourceHandlerTest(testutil.HandlerTestBase):

  def setUp(self):
    """Sets up the test harness."""
    testutil.HandlerTestBase.setUp(self)
    self.ACTION = 'Delete'
    self.handler = main.StaticResourceHandler()
    self.handler.initialize(mock_webapp.MockRequest(),
                            mock_webapp.MockResponse())

    self.render_called = False

  def testStaticCssResourceHandler(self):
    """Test css file can be fetched and absolute paths are made relative."""
    data = 'url(/img/someimage.png)'
    modified_data = 'url(../img/someimage.png)'
    self.handler.request.path = '/_ah/datastore_admin/static/css/compiled.css'
    base_path = tempfile.mkdtemp()
    main.StaticResourceHandler._BASE_FILE_PATH = base_path
    css_path = os.path.join(base_path, 'static', 'css')
    os.makedirs(css_path)
    file_path = os.path.join(css_path, 'compiled.css')
    f = open(file_path, 'w')
    f.write(data)
    f.close()
    self.handler.get()
    self.assertEqual(self.handler.response.out.getvalue(), modified_data)

  def testStaticResourceHandler(self):
    """Test js file can be fetched."""
    data = 'Just a string.'
    self.handler.request.path = '/_ah/datastore_admin/static/js/compiled.js'
    base_path = tempfile.mkdtemp()
    main.StaticResourceHandler._BASE_FILE_PATH = base_path
    css_path = os.path.join(base_path, 'static', 'js')
    os.makedirs(css_path)
    file_path = os.path.join(css_path, 'compiled.js')
    f = open(file_path, 'w')
    f.write(data)
    f.close()
    self.handler.get()
    self.assertEqual(self.handler.response.out.getvalue(), data)

  def testBadResourcePath(self):
    """Test bad file path."""
    self.handler.request.path = '/_ah/datastore_admin/static/css/not-a-file.txt'
    self.handler.get()
    self.assertEquals(self.handler.response.status, 404)


if __name__ == '__main__':
  googletest.main()
