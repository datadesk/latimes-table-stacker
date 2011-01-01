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

"""Used render templates for datastore admin."""



import base64
import datetime
import logging
import os
import random

from google.appengine.api import lib_config
from google.appengine.api import memcache
from google.appengine.api import users

MEMCACHE_NAMESPACE = '_ah-datastore_admin'
XSRF_VALIDITY_TIME = 600
KINDS_AND_SIZES_VAR = 'kinds_and_sizes'


class ConfigDefaults(object):
  """Configurable constants.

  To override datastore_admin configuration values, define values like this
  in your appengine_config.py file (in the root of your app):

    datastore_admin_MAPREDUCE_PATH = /_ah/mapreduce
  """

  BASE_PATH = '/_ah/datastore_admin'
  MAPREDUCE_PATH = '/_ah/mapreduce'
  CLEANUP_MAPREDUCE_STATE = True


config = lib_config.register('datastore_admin', ConfigDefaults.__dict__)
config.BASE_PATH
from google.appengine.ext.webapp import template


def RenderToResponse(handler, template_file, template_params):
  """Render the given template_file using template_vals and write to response.

  Args:
    handler: the handler whose response we should render to
    template_file: the file name only of the template file we are using
    template_params: the parameters used to render the given template
  """
  template_params = _GetDefaultParams(template_params)
  rendered = template.render(_GetTemplatePath(template_file), template_params)
  handler.response.out.write(rendered)


def _GetTemplatePath(template_file):
  """Return the expected path for the template to render.

  Args:
    template_file: simple file name of template to render.

  Returns:
    path of template to render.
  """
  return os.path.join(
      os.path.dirname(__file__), 'templates', template_file)


def _GetDefaultParams(template_params):
  """Update template_params to always contain necessary paths and never be None.
  """
  if not template_params:
    template_params = {}
  template_params.update({
      'base_path': config.BASE_PATH,
      'mapreduce_path': config.MAPREDUCE_PATH,
  })
  return template_params


def CreateXsrfToken(action):
  """Generate a token to be passed with a form for XSRF protection.

  Args:
    action: action to restrict token to

  Returns:
    suitably random token which is only valid for ten minutes and, if the user
    is authenticated, is only valid for the user that generated it.
  """
  user_str = _MakeUserStr()

  token = base64.b64encode(
      ''.join([chr(int(random.random()*255)) for _ in range(0, 64)]))

  memcache.set(token,
               (user_str, action),
               time=XSRF_VALIDITY_TIME,
               namespace=MEMCACHE_NAMESPACE)

  return token


def ValidateXsrfToken(token, action):
  """Validate a given XSRF token by retrieving it from memcache.

  If the token has not been evicted from memcache (past ten minutes) and the
  user strings are equal, then this is a valid token.

  Args:
    token: token to validate from memcache.
    action: action that token should correspond to

  Returns:
    True if the token exists in memcache and the user strings are equal,
    False otherwise.
  """
  user_str = _MakeUserStr()
  token_obj = memcache.get(token, namespace=MEMCACHE_NAMESPACE)

  if not token_obj:
    return False

  token_str = token_obj[0]
  token_action = token_obj[1]

  if user_str != token_str or action != token_action:
    return False

  return True


def CacheStats(formatted_results):
  """Cache last retrieved kind size values in memcache.

  Args:
    formatted_results: list of dictionaries of the form returnned by
      main._PresentableKindStats.
  """
  kinds_and_sizes = {}
  for kind_dict in formatted_results:
    kinds_and_sizes[kind_dict['kind_name']] = kind_dict['total_bytes']

  memcache.set(KINDS_AND_SIZES_VAR,
               kinds_and_sizes,
               namespace=MEMCACHE_NAMESPACE)


def RetrieveCachedStats():
  """Retrieve cached kind sizes from last datastore stats call.

  Returns:
    Dictionary mapping kind names to total bytes.
  """
  kinds_and_sizes = memcache.get(KINDS_AND_SIZES_VAR,
                                 namespace=MEMCACHE_NAMESPACE)

  return kinds_and_sizes


def _MakeUserStr():
  """Make a user string to use to represent the user.  'noauth' by default."""
  user = users.get_current_user()
  if not user:
    user_str = 'noauth'
  else:
    user_str = user.nickname()

  return user_str


def GetPrettyBytes(bytes, significant_digits=0):
  """Get a pretty print view of the given number of bytes.

  This will give a string like 'X MBytes'.

  Args:
    bytes: the original number of bytes to pretty print.
    significant_digits: number of digits to display after the decimal point.

  Returns:
    A string that has the pretty print version of the given bytes.
  """
  byte_prefixes = ['', 'K', 'M', 'G', 'T', 'P', 'E']
  for i in range(0, 7):
    exp = i * 10
    if bytes < 2**(exp + 10):
      if i == 0:
        formatted_bytes = str(bytes)
      else:
        formatted_bytes = '%.*f' % (significant_digits, (bytes * 1.0 / 2**exp))
      if formatted_bytes != '1':
        plural = 's'
      else:
        plural = ''
      return '%s %sByte%s' % (formatted_bytes, byte_prefixes[i], plural)

  logging.error('Number too high to convert: %d', bytes)
  return 'Alot'


def FormatThousands(value):
  """Format a numerical value, inserting commas as thousands separators.

  Args:
    value: An integer, float, or string representation thereof.
      If the argument is a float, it is converted to a string using '%.2f'.

  Returns:
    A string with groups of 3 digits before the decimal point (if any)
    separated by commas.

  NOTE: We don't deal with whitespace, and we don't insert
  commas into long strings of digits after the decimal point.
  """
  if isinstance(value, float):
    value = '%.2f' % value
  else:
    value = str(value)
  if '.' in value:
    head, tail = value.split('.', 1)
    tail = '.' + tail
  elif 'e' in value:
    head, tail = value.split('e', 1)
    tail = 'e' + tail
  else:
    head = value
    tail = ''
  sign = ''
  if head.startswith('-'):
    sign = '-'
    head = head[1:]
  while len(head) > 3:
    tail = ',' + head[-3:] + tail
    head = head[:-3]
  return sign + head + tail


def TruncDelta(delta):
  """Strips microseconds from a timedelta."""
  return datetime.timedelta(days=delta.days, seconds=delta.seconds)
