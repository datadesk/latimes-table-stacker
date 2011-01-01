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

"""Used to confirm and act on delete requests from the Admin Console."""



import logging
import re
import urllib

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.datastore_admin import utils
from google.appengine.ext.mapreduce import control
from google.appengine.ext.mapreduce import model
from google.appengine.ext.mapreduce import operation

MAPREDUCE_OBJECTS = ['MapreduceState', 'ShardState']
XSRF_ACTION = 'delete'
KIND_AND_SIZE_RE = re.compile('^(.*)\|(-?[0-9]+)$')


def DeleteEntity(entity):
  """Delete function which deletes all processed entities.

  Args:
    entity: entity to delete.

  Yields:
    a delete operation if the entity is not an active mapreduce object.
  """
  if not entity.kind() in MAPREDUCE_OBJECTS or not entity['active']:
    yield operation.db.Delete(entity)


def _GetPrintableStrs(namespace, kinds):
  """Returns tuples describing affected kinds and namespace.

  Args:
    namespace: namespace being targeted.
    kinds: list of kinds being targeted.

  Returns:
    (namespace_str, kind_str) tuple used for display to user.
  """
  namespace_str = ''
  if kinds:
    kind_str = 'all %s entities' % ', '.join(kinds)
  else:
    kind_str = ''
  return (namespace_str, kind_str)


class ConfirmDeleteHandler(webapp.RequestHandler):
  """Handler to deal with requests from the admin console to delete data."""

  SUFFIX = 'confirm_delete'

  @classmethod
  def Render(cls, handler):
    """Rendering method that can be called by main.py or get.

    This method executes no action, so the method by which it is accessed is
    immaterial.  Creating a form with get may be a desirable function.  That is,
    if this builtin is turned on, anyone can create a form to delete a kind by
    simply linking to the ConfirmDeleteHandler like so:
    <a href="/_ah/datastore_admin/confirm_delete?kind=trash">
        Delete all Trash Objects</a>

    Args:
      handler: the webapp.RequestHandler invoking the method
    """
    namespace = handler.request.get('namespace')
    kinds = handler.request.get('kind', allow_multiple=True)
    sizes_known, size_total, remainder = cls._ParseKindsAndSizes(kinds)

    (namespace_str, kind_str) = _GetPrintableStrs(namespace, kinds)
    template_params = {
        'form_target': DoDeleteHandler.SUFFIX,
        'kind_list': kinds,
        'remainder': remainder,
        'sizes_known': sizes_known,
        'size_total': size_total,
        'app_id': handler.request.get('app_id'),
        'cancel_url': handler.request.get('cancel_url'),
        'kind_str': kind_str,
        'namespace_str': namespace_str,
        'xsrf_token': utils.CreateXsrfToken(XSRF_ACTION),
    }
    utils.RenderToResponse(handler, 'confirm_delete.html', template_params)

  @classmethod
  def _ParseKindsAndSizes(cls, kinds):
    """Parses kind|size list and returns template parameters.

    Args:
      kinds: list of kinds to process.

    Returns:
      sizes_known: whether or not all kind objects have known sizes.
      size_total: total size of objects with known sizes.
      len(kinds) - 2: for template rendering of greater than 3 kinds.
    """
    sizes_known = True
    size_total = 0
    kinds_and_sizes = utils.RetrieveCachedStats()

    if kinds_and_sizes:
      for kind in kinds:
        if kind in kinds_and_sizes:
          size_total += kinds_and_sizes[kind]
        else:
          sizes_known = False
    else:
      sizes_known = False

    if size_total:
      size_total = utils.GetPrettyBytes(size_total)

    return sizes_known, size_total, len(kinds) - 2

  def get(self):
    """Handler for get requests to datastore_admin/confirm_delete."""
    ConfirmDeleteHandler.Render(self)


class DoDeleteHandler(webapp.RequestHandler):
  """Handler to deal with requests from the admin console to delete data."""

  SUFFIX = 'delete.do'
  DELETE_HANDLER = (
      'google.appengine.ext.datastore_admin.delete_handler.DeleteEntity')
  INPUT_READER = (
      'google.appengine.ext.mapreduce.input_readers.DatastoreKeyInputReader')
  MAPREDUCE_DETAIL = utils.config.MAPREDUCE_PATH + '/detail?mapreduce_id='

  def get(self):
    """Handler for get requests to datastore_admin/delete.do.

    Status of executed jobs is displayed.
    """
    jobs = self.request.get('job', allow_multiple=True)
    error = self.request.get('error', '')

    template_params = {
        'job_list': jobs,
        'mapreduce_detail': self.MAPREDUCE_DETAIL,
        'error': error,
    }
    utils.RenderToResponse(self, 'do_delete.html', template_params)

  def post(self):
    """Handler for post requests to datastore_admin/delete.do.

    Jobs are executed and user is redirected to the get handler.
    """
    namespace = self.request.get('namespace')
    kinds = self.request.get('kind', allow_multiple=True)
    (namespace_str, _) = _GetPrintableStrs(namespace, kinds)
    app_id = self.request.get('app_id')
    token = self.request.get('xsrf_token')

    jobs = []
    if utils.ValidateXsrfToken(token, XSRF_ACTION):
      try:
        for kind in kinds:
          name = 'Delete all %s objects%s' % (kind, namespace_str)
          mapreduce_params = {
              'entity_kind': kind,
          }

          if utils.config.CLEANUP_MAPREDUCE_STATE:
            mapreduce_params['done_callback'] = '%s/%s' % (
                utils.config.BASE_PATH, DeleteDoneHandler.SUFFIX)

          jobs.append(control.start_map(
              name, self.DELETE_HANDLER,
              self.INPUT_READER, mapreduce_params,
              mapreduce_parameters=mapreduce_params,
              base_path=utils.config.MAPREDUCE_PATH,
              _app=app_id))

        error = ''
      except Exception, e:
        error = self._HandleException(e)

      parameters = [('job', job) for job in jobs]
      if error:
        parameters.append(('error', error))
    else:
      parameters = [('xsrf_error', '1')]

    query = urllib.urlencode(parameters)

    self.redirect('%s/%s?%s' % (utils.config.BASE_PATH, self.SUFFIX, query))

  def _HandleException(self, e):
    """Make exception handling overrideable by tests.

    In normal cases, return only the error string; do not fail to render the
    page for user.
    """
    return str(e)


class DeleteDoneHandler(webapp.RequestHandler):
  """Handler to delete data associated with successful MapReduce jobs."""

  SUFFIX = 'delete_done'

  def post(self):
    """Uses mapreduce_id param to delete data associated with a successful job.
    """
    if 'Mapreduce-Id' in self.request.headers:
      mapreduce_id = self.request.headers['Mapreduce-Id']

      keys = []
      job_success = True
      for shard_state in model.ShardState.find_by_mapreduce_id(mapreduce_id):
        keys.append(shard_state.key())
        if not shard_state.result_status == 'success':
          job_success = False

      if job_success:
        keys.append(model.MapreduceState.get_key_by_job_id(mapreduce_id))
        keys.append(model.MapreduceControl.get_key_by_job_id(mapreduce_id))
        db.delete(keys)
        logging.info('State for successful job %s was deleted.', mapreduce_id)
      else:
        logging.info('Job %s was not successful so no state was deleted.', (
            mapreduce_id))
    else:
      logging.error('Done callback called without Mapreduce Id.')
