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




"""Stubs for Log Service service."""




from google.appengine.api import apiproxy_stub


class LogServiceStub(apiproxy_stub.APIProxyStub):
  """Python stub for Log Service service."""

  def __init__(self):
    """Constructor."""
    super(LogServiceStub, self).__init__('logservice')
    self.status = None

  def _Dynamic_Flush(self, unused_request, unused_response):
    """NoOp, as Dev appserver logs are continuously flushed."""
    return

  def _Dynamic_SetStatus(self, request, unused_response):
    """Record the recently seen status."""
    self.status = request.status()

  def get_status(self):
    """Internal method for dev_appserver to read the status."""
    return self.status
