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

"""Matcher API.

A service that enables AppEngine apps to match queries to documents.

Functions defined in this module:
  subscribe: Add a query to set of matching queries.
  unsubscribe: Remove query from set of matching queries.
  get_subscription: Retrieves subscription with particular id.
  list_subscriptions: Lists subscriptions on a particular topic.
  match: Match all subscribed queries to document.
"""






import base64
import sys

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore
from google.appengine.api.matcher import error_pb
from google.appengine.api.matcher import matcher_pb
from google.appengine.api import datastore_types
from google.appengine.runtime import apiproxy_errors
from google.appengine.datastore import entity_pb

DEFAULT_RESULT_BATCH_SIZE = 100
DEFAULT_LEASE_DURATION_SEC = 24 * 3600
DEFAULT_LIST_SUBSCRIPTIONS_MAX_RESULTS = 1000

_doc_class = matcher_pb.MatchRequest
_schema_type = matcher_pb.SchemaEntry
_entity_meaning = entity_pb.Property

SubscriptionState = matcher_pb.SubscriptionRecord

def GetSchemaEntryForPropertyType(property_type):
  """Converts db.Model type to internal schema type."""
  from google.appengine.ext import db
  _MODEL_TYPE_TO_SCHEMA_ENTRY = {
      db.StringProperty: (_schema_type.STRING, None),
      db.IntegerProperty: (_schema_type.INT32, None),
      db.DateTimeProperty: (_schema_type.INT32, _entity_meaning.GD_WHEN),
      db.BooleanProperty: (_schema_type.BOOLEAN, None),
      db.FloatProperty: (_schema_type.DOUBLE, None)
  }
  return _MODEL_TYPE_TO_SCHEMA_ENTRY.get(property_type, (None, None))


def GetModelTypeForPythonType(python_type):
  """Converts python built in type to db.Model type."""
  from google.appengine.ext import db
  _PYTHON_TYPE_TO_MODEL_TYPE = {
      str: db.StringProperty,
      int: db.IntegerProperty,
      bool: db.BooleanProperty,
      float: db.FloatProperty,
  }
  return _PYTHON_TYPE_TO_MODEL_TYPE.get(python_type, None)


class TopicNotSpecified(Exception):
  def __str__(self):
    return 'Topic must be specified.'


class SubscriptionDoesNotExist(Exception):
  """Subscription does not exist."""
  def __init__(self, topic, sub_id):
    Exception.__init__(self)
    self.topic = topic
    self.sub_id = sub_id

  def __str__(self):
    return 'Subscription %s on topic %s does not exist.' % (self.sub_id,
                                                            self.topic)


class DocumentTypeError(Exception):
  """Document type is not supported."""

  def __str__(self):
    return 'Document type is not supported.'


class SchemaError(Exception):
  """Schema error."""

  def __init__(self, detail):
    Exception.__init__(self)
    self.detail = detail

  def __str__(self):
    return 'SchemaError: %s' % self.detail


class QuerySyntaxError(Exception):
  """Query syntax not valid error."""

  def __init__(self, topic, sub_id, query, detail):
    Exception.__init__(self)
    self.topic = topic
    self.sub_id = sub_id
    self.query = query
    self.detail = detail

  def __str__(self):
    return "QuerySyntaxError: topic:'%s' sub_id:'%s' query:'%s' detail:'%s'" % (
        self.topic, self.sub_id, self.query, self.detail)

def get_document_topic(document, topic):
  if topic:
    return topic
  return document.kind()


def make_sync_call(service, call, request, response):
  """The APIProxy entry point for a synchronous API call.

  Args:
    service: string representing which service to call
    call: string representing which function to call
    request: protocol buffer for the request
    response: protocol buffer for the response

  Returns:
    Response protocol buffer. Caller should always use returned value
    which may or may not be same as passed in 'response'.

  Raises:
    apiproxy_errors.Error:
  """

  resp = apiproxy_stub_map.MakeSyncCall(service, call, request, response)
  if resp is not None:
    return resp
  return response


def _add_schema_entry(model_type, name, add_entry):
  """Add single entry to SchemaEntries by invoking add_entry."""
  schema_type, entity_meaning = GetSchemaEntryForPropertyType(model_type)
  if not schema_type:
    return
  entry = add_entry()
  entry.set_name(name)
  entry.set_type(schema_type)
  if entity_meaning:
    entry.set_meaning(entity_meaning)


def _python_schema_to_matcher_schema(schema, add_entry):
  """Produce SchemaEntries from python schema.

  Args:
    schema: python dictionary, datastore.Entity or db.model class.
    add_entry: sink function for schema entries.

  Raises:
    SchemaError: schema is invalid.
  """
  all_names = []
  for python_type, names in schema.items():
    all_names.extend(names)
    for name in names:
      model_type = GetModelTypeForPythonType(python_type)
      if not model_type:
        continue
      _add_schema_entry(model_type, name, add_entry)
  if len(all_names) != len(set(all_names)):
    duplicate_names = all_names
    for name in set(all_names):
      duplicate_names.remove(name)
    raise SchemaError('Duplicate names in schema: %s' % duplicate_names)


def _model_to_matcher_schema(model, add_entry):
  """Produce SchemaEntries from db.Model class."""
  for name, model_property in model.properties().iteritems():
    _add_schema_entry(model_property.__class__, name, add_entry)


def subscribe(document_class,
              vanilla_query,
              sub_id,
              schema=None,
              topic=None,
              lease_duration_sec=DEFAULT_LEASE_DURATION_SEC):
  """Subscribe a query.

  If the document_class is a python dictionary or datastore.Entity, a schema
  must be specified to define how document_class member names map to the
  matcher supported types: bool, float, int, str.

  For example, the python dictionary 'person' has the following schema:

  person = {}
  person['first_name'] = 'Andrew'
  person['surname'] = 'Smith'
  person['height'] = 150

  person_schema = {
    'str' : ['first_name', 'surname'],
    'int' : ['height'],
  }

  The example would be almost identical if person = datastore.Entity().

  Args:
    document_class: python dictionary, datastore.Entity or db.model class.
    vanilla_query: user query for documents of type document_class.
    sub_id: subscription id returned when this subscription is matched.
    schema: required for python dictionary and datastore.Entity document_class.
    topic: required for python dictionary and datastore.Entity document_class.
        Only documents of same topic will be matched against this subscription.
    lease_duration_sec: minimum number of seconds subscription should exist.

  Raises:
    DocumentTypeError: document type is unsupported.
    TopicNotSpecified: raised for python dictionary and datastore.Entity
        document type if topic is not specified.
    QuerySyntaxError: raised when query is invalid or does not match schema.
    SchemaError: schema is invalid.
    apiproxy_errors.Error: subscribe call failed.
  """
  from google.appengine.ext import db

  request = matcher_pb.SubscribeRequest()
  request.set_sub_id(sub_id)
  request.set_vanilla_query(vanilla_query)
  request.set_lease_duration_sec(lease_duration_sec)

  if issubclass(document_class, db.Model):
    topic = get_document_topic(document_class, topic)
    _model_to_matcher_schema(document_class, request.add_schema_entry)
  elif (issubclass(document_class, datastore.Entity) or
        issubclass(document_class, dict)):
    if not topic:
      raise TopicNotSpecified()
    _python_schema_to_matcher_schema(schema, request.add_schema_entry)
  else:
    raise DocumentTypeError()
  request.set_topic(topic)

  response = matcher_pb.SubscribeResponse()
  try:
    make_sync_call('matcher', 'Subscribe', request, response)
  except apiproxy_errors.ApplicationError, e:
    if e.application_error is error_pb.Error.BAD_REQUEST:
      raise QuerySyntaxError(sub_id, topic, vanilla_query, e.error_detail)
    raise e


def unsubscribe(document_class, sub_id, topic=None):
  """Unsubscribe a query.

  Args:
    document_class: python dictionary, datastore.Entity or db.model class.
    sub_id: subscription id to remove.
    topic: required for python dictionary and datastore.Entity document_class.
        Topic must match topic used in the subscribe call for this subscription.

  Raises:
    DocumentTypeError: document type is unsupported.
    TopicNotSpecified: raised for python dictionary and datastore.Entity
        document type if topic is not specified.
    apiproxy_errors.Error: unsubscribe call failed.
  """
  from google.appengine.ext import db

  request = matcher_pb.UnsubscribeRequest()
  if issubclass(document_class, db.Model):
    topic = get_document_topic(document_class, topic)
  elif (issubclass(document_class, datastore.Entity) or
        issubclass(document_class, dict)):
    if not topic:
      raise TopicNotSpecified()
  else:
    raise DocumentTypeError()
  request.set_topic(topic)
  request.set_sub_id(sub_id)
  response = matcher_pb.UnsubscribeResponse()
  make_sync_call('matcher', 'Unsubscribe', request, response)


def get_subscription(document_class, sub_id, topic=None):
  subscriptions = list_subscriptions(document_class, sub_id, topic=topic,
                                     max_results=1)
  if len(subscriptions) and subscriptions[0][0] == sub_id:
    return subscriptions[0]
  raise SubscriptionDoesNotExist(topic, sub_id)


def list_subscriptions(document_class,
                       sub_id_start="",
                       topic=None,
                       max_results=DEFAULT_LIST_SUBSCRIPTIONS_MAX_RESULTS,
                       expires_before=None):
  """List subscriptions on a topic.

  Args:
    document_class: python dictionary, datastore.Entity or db.model class.
    sub_id_start: return only subscriptions that are lexicographically equal or
        greater than the specified value.
    topic: required for python dictionary and datastore.Entity document_class.
    max_results: maximum number of subscriptions to return.
    expires_before: when set, limits list to subscriptions which will
        expire no later than expires_before (epoch time).
  Returns:
    List of subscription tuples. The subscription tuple contains:
        subscription id
        query
        expiration time (sec)
        state (SubscriptionState = OK/PENDING/ERROR)
        error_message (if state is ERROR)

  Raises:
    DocumentTypeError: document type is unsupported.
    TopicNotSpecified: raised for python dictionary and datastore.Entity
        document type if topic is not specified.
    apiproxy_errors.Error: list call failed.
  """
  from google.appengine.ext import db

  request = matcher_pb.ListSubscriptionsRequest()
  if issubclass(document_class, db.Model):
    topic = get_document_topic(document_class, topic)
  elif (issubclass(document_class, datastore.Entity) or
        issubclass(document_class, dict)):
    if not topic:
      raise TopicNotSpecified()
  else:
    raise DocumentTypeError()
  request.set_topic(topic)
  request.set_subscription_id_start(sub_id_start)
  request.set_max_results(max_results)
  if expires_before:
    request.set_expires_before(expires_before)
  response = matcher_pb.ListSubscriptionsResponse()
  make_sync_call('matcher', 'ListSubscriptions', request, response)
  subscriptions = []
  for sub in response.subscription_list():
    subscriptions.append((sub.id(),
                          sub.vanilla_query(),
                          sub.expiration_time_sec(),
                          sub.state(),
                          sub.error_message()))
  return subscriptions


def match(document,
          topic=None,
          result_key=None,
          result_relative_url='/_ah/matcher',
          result_task_queue='default',
          result_batch_size=DEFAULT_RESULT_BATCH_SIZE,
          result_return_document=True):
  """Match document with all subscribed queries on specified topic.

  Args:
    document: instance of dictionary, datastore.Entity or db.Model document.
    topic: required for python dictionary. Only subscriptions of this topic
        will be matched against this document.
    result_key: key to return in result, potentially to identify document.
    result_relative_url: url of taskqueue event handler for results.
    result_task_queue: name of taskqueue queue to put batched results on.
    result_batch_size: number of subscriptions ids per taskqueue task batch.
    result_return_document: returns document with match results if true.

  Raises:
    DocumentTypeError: document type is unsupported.
    TopicNotSpecified: raised for python dictionary document type if topic is
        not specified.
    apiproxy_errors.Error: match call failed.
  """
  from google.appengine.ext import db

  request = matcher_pb.MatchRequest()
  if isinstance(document, db.Model):
    topic = get_document_topic(document, topic)
    doc_pb = db.model_to_protobuf(document)
    if result_return_document:
      request.set_result_python_document_class(_doc_class.MODEL)
  elif isinstance(document, datastore.Entity):
    topic = get_document_topic(document, topic)
    doc_pb = document.ToPb()
    if result_return_document:
      request.set_result_python_document_class(_doc_class.ENTITY)
  elif isinstance(document, dict):
    if not topic:
      raise TopicNotSpecified()
    doc_entity = datastore.Entity(topic)
    doc_entity.update(document)
    doc_pb = doc_entity.ToPb()
    if result_return_document:
      request.set_result_python_document_class(_doc_class.DICT)
  else:
    raise DocumentTypeError()
  request.set_topic(topic)
  request.mutable_document().CopyFrom(doc_pb)
  if result_key:
    request.set_result_key(result_key)
  request.set_result_relative_url(result_relative_url)
  request.set_result_task_queue(result_task_queue)
  request.set_result_batch_size(result_batch_size)
  response = matcher_pb.MatchResponse()
  make_sync_call('matcher', 'Match', request, response)


def get_document(request):
  """Decodes document from matcher result POST request.

  Args:
    request: received POST request

  Returns:
    document: document which was used to generate this match.

  Raises:
    ProtocolBufferDecodeError:
    DocumentTypeError:
  """
  from google.appengine.ext import db

  doc_class = request.get('python_document_class')
  if not doc_class:
    return None
  entity = entity_pb.EntityProto()
  entity.ParseFromString(base64.urlsafe_b64decode(
      request.get('document').encode('utf-8')))
  doc_class = int(doc_class)
  if doc_class is _doc_class.DICT:
    return dict(datastore.Entity('temp-kind').FromPb(entity))
  elif doc_class is _doc_class.ENTITY:
    return datastore.Entity('temp-kind').FromPb(entity)
  elif doc_class is _doc_class.MODEL:
    return db.model_from_protobuf(entity)
  else:
    raise DocumentTypeError()
