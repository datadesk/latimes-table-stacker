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

"""Shim module so that the old labs import path still works."""



__all__ = [

    'BadTaskStateError', 'BadTransactionState', 'BadTransactionStateError',
    'DatastoreError', 'DuplicateTaskNameError', 'Error', 'InternalError',
    'InvalidQueueError', 'InvalidQueueNameError', 'InvalidTaskError',
    'InvalidTaskNameError', 'InvalidUrlError', 'PermissionDeniedError',
    'TaskAlreadyExistsError', 'TaskTooLargeError', 'TombstonedTaskError',
    'TooManyTasksError', 'TransientError', 'UnknownQueueError',

    'MAX_QUEUE_NAME_LENGTH', 'MAX_TASK_NAME_LENGTH', 'MAX_TASK_SIZE_BYTES',
    'MAX_URL_LENGTH',

    'Queue', 'Task', 'add']


import os
import sys
import warnings

from google.appengine.api.taskqueue import *


if os.environ.get('DATACENTER', None) is None:
  warnings.warn('google.appengine.api.labs.taskqueue is deprecated, please use '
                'google.appengine.api.taskqueue', DeprecationWarning,
                stacklevel=2)


def _map_module(module_name):
  """Map a module from the new path to the labs path.

  Args:
    module_name: Name of the module to be mapped.

  Raises:
    ImportError: If the specified module we are mapping from does not exist.

  Returns:
    The module object of the module that was mapped.
  """
  labs_module_name = '%s.%s' % (__name__, module_name)
  module_prefix = '.'.join(__name__.split('.')[:2])
  new_module_name = '%s.api.taskqueue.%s' % (module_prefix, module_name)

  __import__(new_module_name)
  sys.modules[labs_module_name] = sys.modules[new_module_name]
  return sys.modules[labs_module_name]

taskqueue = _map_module('taskqueue')
taskqueue_service_pb = _map_module('taskqueue_service_pb')
taskqueue_stub = _map_module('taskqueue_stub')
