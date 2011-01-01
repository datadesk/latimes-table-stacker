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

"""Google3 version of apphosting/ext/mapreduce/testutil.py."""


from google.appengine.tools import os_compat

import os
import sys

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import queueinfo
from google.appengine.api import user_service_stub
from google.appengine.api.memcache import memcache_stub
from google.appengine.api.taskqueue import taskqueue_stub
from google.testing.pybase import googletest


class HandlerTestBase(googletest.TestCase):
  """Base class for all webapp.RequestHandler tests."""

  MAPREDUCE_KICKOFF_URL = "/_ah/mapreduce/kickoffjob_callback"

  def setUp(self):
    googletest.TestCase.setUp(self)

    self.appid = "testapp"
    os.environ["APPLICATION_ID"] = self.appid

    self.memcache = memcache_stub.MemcacheServiceStub()
    self.taskqueue = taskqueue_stub.TaskQueueServiceStub()
    self.taskqueue.queue_yaml_parser = (
        lambda x: queueinfo.LoadSingleQueue(
            "queue:\n"
            "- name: default\n"
            "  rate: 10/s\n"
            "- name: crazy-queue\n"
            "  rate: 2000/d\n"
            "  bucket_size: 10\n"))
    self.datastore = datastore_file_stub.DatastoreFileStub(
        self.appid, "/dev/null", "/dev/null")
    self.user = user_service_stub.UserServiceStub()

    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    apiproxy_stub_map.apiproxy.RegisterStub("taskqueue", self.taskqueue)
    apiproxy_stub_map.apiproxy.RegisterStub("memcache", self.memcache)
    apiproxy_stub_map.apiproxy.RegisterStub("datastore_v3", self.datastore)
    apiproxy_stub_map.apiproxy.RegisterStub("user", self.user)

  def assertTaskStarted(self, queue="default"):
    tasks = self.taskqueue.GetTasks(queue)
    self.assertEquals(1, len(tasks))
    self.assertEquals(tasks[0]["url"], self.MAPREDUCE_KICKOFF_URL)

  def assertTaskNotStarted(self, queue="default"):
    tasks = self.taskqueue.GetTasks(queue)
    self.assertEquals(0, len(tasks))
