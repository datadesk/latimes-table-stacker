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




"""Utility functions shared between the file and sqlite datastore stubs."""





try:
  import hashlib
  _MD5_FUNC = hashlib.md5
except ImportError:
  import md5
  _MD5_FUNC = md5.new

import collections
import datetime
import itertools
import logging
import random
import struct
import threading

from google.appengine.api import api_base_pb
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_types
from google.appengine.api.taskqueue import taskqueue_service_pb
from google.appengine.datastore import datastore_index
from google.appengine.datastore import datastore_pb
from google.appengine.datastore import datastore_query
from google.appengine.runtime import apiproxy_errors
from google.appengine.datastore import entity_pb





_MAXIMUM_RESULTS = 1000





_MAX_QUERY_OFFSET = 1000



_PROPERTY_TYPE_NAMES = {
    0: 'NULL',
    entity_pb.PropertyValue.kint64Value: 'INT64',
    entity_pb.PropertyValue.kbooleanValue: 'BOOLEAN',
    entity_pb.PropertyValue.kstringValue: 'STRING',
    entity_pb.PropertyValue.kdoubleValue: 'DOUBLE',
    entity_pb.PropertyValue.kPointValueGroup: 'POINT',
    entity_pb.PropertyValue.kUserValueGroup: 'USER',
    entity_pb.PropertyValue.kReferenceValueGroup: 'REFERENCE'
    }


_SCATTER_PROPORTION = 32768

def _GetScatterProperty(entity_proto):
  """Gets the scatter property for an object.

  For ease of implementation, this is not synchronized with the actual
  value on the App Engine server, but should work equally well.

  Note: This property may change, either here or in production. No client
  other than the mapper framework should rely on it directly.

  Returns:
    The PropertyValue of the scatter property or None if this entity should not
    have a scatter property.
  """
  hash_obj = _MD5_FUNC()
  for element in entity_proto.key().path().element_list():
    if element.has_name():
      hash_obj.update(element.name())
    elif element.has_id():
      hash_obj.update(str(element.id()))
  hash_bytes = hash_obj.digest()[0:2]
  (hash_int,) = struct.unpack('H', hash_bytes)

  if hash_int >= _SCATTER_PROPORTION:
    return None

  scatter_property = entity_pb.Property()
  scatter_property.set_name('__scatter__')
  scatter_property.set_meaning(entity_pb.Property.BYTESTRING)
  scatter_property.set_multiple(False)
  property_value = scatter_property.mutable_value()
  property_value.set_stringvalue(hash_bytes)
  return scatter_property





_SPECIAL_PROPERTY_MAP = {
    '__scatter__' : (False, True, _GetScatterProperty)
    }

def GetInvisibleSpecialPropertyNames():
  """Gets the names of all non user-visible special properties."""
  invisible_names = []
  for name, value in _SPECIAL_PROPERTY_MAP.items():
    is_visible, _, _ = value
    if not is_visible:
      invisible_names.append(name)
  return invisible_names

def _PrepareSpecialProperties(entity_proto, is_load):
  """Computes special properties for loading or storing.
  Strips other special properties."""
  for i in xrange(entity_proto.property_size() - 1, -1, -1):
    if _SPECIAL_PROPERTY_MAP.has_key(entity_proto.property(i).name()):
      del entity_proto.property_list()[i]

  for is_visible, is_stored, property_func in _SPECIAL_PROPERTY_MAP.values():
    if is_load:
      should_process = is_visible
    else:
      should_process = is_stored

    if should_process:
      special_property = property_func(entity_proto)
      if special_property:
        entity_proto.property_list().append(special_property)


def PrepareSpecialPropertiesForStore(entity_proto):
  """Computes special properties for storing.
  Strips other special properties."""
  _PrepareSpecialProperties(entity_proto, False)


def LoadEntity(entity):
  """Prepares an entity to be returned to the user.

  Args:
    entity: a entity_pb.EntityProto or None

  Returns:
    A user friendly copy of entity or None.
  """
  if entity:
    clone = entity_pb.EntityProto()
    clone.CopyFrom(entity)
    PrepareSpecialPropertiesForLoad(clone)
    return clone


def StoreEntity(entity):
  """Prepares an entity for storing.

  Args:
    entity: a entity_pb.EntityProto to prepare

  Returns:
    A copy of entity that should be stored in its place.
  """
  clone = entity_pb.EntityProto()
  clone.CopyFrom(entity)



  PrepareSpecialPropertiesForStore(clone)
  return clone


def PrepareSpecialPropertiesForLoad(entity_proto):
  """Computes special properties that are user-visible.
  Strips other special properties."""
  _PrepareSpecialProperties(entity_proto, True)


def Check(test, msg='', error_code=datastore_pb.Error.BAD_REQUEST):
  """Raises an apiproxy_errors.ApplicationError if the condition is false.

  Args:
    test: A condition to test.
    msg: A string to return with the error.
    error_code: One of datastore_pb.Error to use as an error code.

  Raises:
    apiproxy_errors.ApplicationError: If test is false.
  """
  if not test:
    raise apiproxy_errors.ApplicationError(error_code, msg)


def CheckAppId(request_trusted, request_app_id, app_id):
  """Check that this is the stub for app_id.

  Args:
    request_trusted: If the request is trusted.
    request_app_id: The application ID of the app making the request.
    app_id: An application ID.

  Raises:
    apiproxy_errors.ApplicationError: if this is not the stub for app_id.
  """

  assert app_id
  Check(request_trusted or app_id == request_app_id,
        'app "%s" cannot access app "%s"\'s data' % (request_app_id, app_id))


def CheckReference(request_trusted, request_app_id, key):
  """Check this key.

  Args:
    request_trusted: If the request is trusted.
    request_app_id: The application ID of the app making the request.
    key: entity_pb.Reference

  Raises:
    apiproxy_errors.ApplicationError: if the key is invalid
  """

  assert isinstance(key, entity_pb.Reference)

  CheckAppId(request_trusted, request_app_id, key.app())

  for elem in key.path().element_list():
    Check(elem.has_id() != elem.has_name(),
          'each key path element should have id or name but not both: %r' % key)


def CheckTransaction(request_trusted, request_app_id, transaction):
  """Check that this transaction is valid.

  Args:
    request_trusted: If the request is trusted.
    request_app_id: The application ID of the app making the request.
    transaction: datastore_pb.Transaction

  Raises:
    apiproxy_errors.ApplicationError: if the transaction is not valid.
  """
  assert isinstance(transaction, datastore_pb.Transaction)
  CheckAppId(request_trusted, request_app_id, transaction.app())


def CheckQuery(query, filters, orders, max_query_components):
  """Check a datastore query with normalized filters, orders.

  Raises an ApplicationError when any of the following conditions are violated:
  - transactional queries have an ancestor
  - queries that are not too large
    (sum of filters, orders, ancestor <= max_query_components)
  - ancestor (if any) app and namespace match query app and namespace
  - kindless queries only filter on __key__ and only sort on __key__ ascending
  - multiple inequality (<, <=, >, >=) filters all applied to the same property
  - filters on __key__ compare to a reference in the same app and namespace as
    the query
  - if an inequality filter on prop X is used, the first order (if any) must
    be on X

  Args:
    query: query to validate
    filters: normalized (by datastore_index.Normalize) filters from query
    orders: normalized (by datastore_index.Normalize) orders from query
    max_query_components: limit on query complexity
  """

  key_prop_name = datastore_types._KEY_SPECIAL_PROPERTY
  unapplied_log_timestamp_us_name = (
      datastore_types._UNAPPLIED_LOG_TIMESTAMP_SPECIAL_PROPERTY)

  if query.has_transaction():

    Check(query.has_ancestor(),
          'Only ancestor queries are allowed inside transactions.')


  num_components = len(filters) + len(orders)
  if query.has_ancestor():
    num_components += 1
  Check(num_components <= max_query_components,
        'query is too large. may not have more than %s filters'
        ' + sort orders ancestor total' % max_query_components)


  if query.has_ancestor():
    ancestor = query.ancestor()
    Check(query.app() == ancestor.app(),
          'query app is %s but ancestor app is %s' %
              (query.app(), ancestor.app()))
    Check(query.name_space() == ancestor.name_space(),
          'query namespace is %s but ancestor namespace is %s' %
              (query.name_space(), ancestor.name_space()))



  ineq_prop_name = None
  for filter in filters:
    Check(filter.property_size() == 1,
          'Filter has %d properties, expected 1' % filter.property_size())

    prop = filter.property(0)
    prop_name = prop.name().decode('utf-8')

    if prop_name == key_prop_name:



      Check(prop.value().has_referencevalue(),
            '%s filter value must be a Key' % key_prop_name)
      ref_val = prop.value().referencevalue()
      Check(ref_val.app() == query.app(),
            '%s filter app is %s but query app is %s' %
                (key_prop_name, ref_val.app(), query.app()))
      Check(ref_val.name_space() == query.name_space(),
            '%s filter namespace is %s but query namespace is %s' %
                (key_prop_name, ref_val.name_space(), query.name_space()))

    if (filter.op() in datastore_index.INEQUALITY_OPERATORS and
        prop_name != unapplied_log_timestamp_us_name):
      if ineq_prop_name is None:
        ineq_prop_name = prop_name
      else:
        Check(ineq_prop_name == prop_name,
              'Only one inequality filter per query is supported. '
              'Encountered both %s and %s' % (ineq_prop_name, prop_name))

  if ineq_prop_name is not None and orders:

    first_order_prop = orders[0].property().decode('utf-8')
    Check(first_order_prop == ineq_prop_name,
          'The first sort property must be the same as the property '
          'to which the inequality filter is applied.  In your query '
          'the first sort property is %s but the inequality filter '
          'is on %s' % (first_order_prop, ineq_prop_name))

  if not query.has_kind():

    for filter in filters:
      prop_name = filter.property(0).name().decode('utf-8')
      Check(prop_name == key_prop_name or
                prop_name == unapplied_log_timestamp_us_name,
            'kind is required for non-__key__ filters')
    for order in orders:
      prop_name = order.property().decode('utf-8')
      Check(prop_name == key_prop_name and
                order.direction() is datastore_pb.Query_Order.ASCENDING,
            'kind is required for all orders except __key__ ascending')


class ValueRange(object):
  """A range of values defined by its two extremes (inclusive or exclusive)."""

  def __init__(self):
    """Constructor.

    Creates an unlimited range.
    """
    self.__start = self.__end = None
    self.__start_inclusive = self.__end_inclusive = False

  def Update(self, rel_op, limit):
    """Filter the range by 'rel_op limit'.

    Args:
      rel_op: relational operator from datastore_pb.Query_Filter.
      limit: the value to limit the range by.
    """

    if rel_op == datastore_pb.Query_Filter.LESS_THAN:
      if self.__end is None or limit <= self.__end:
        self.__end = limit
        self.__end_inclusive = False
    elif (rel_op == datastore_pb.Query_Filter.LESS_THAN_OR_EQUAL or
          rel_op == datastore_pb.Query_Filter.EQUAL):
      if self.__end is None or limit < self.__end:
        self.__end = limit
        self.__end_inclusive = True

    if rel_op == datastore_pb.Query_Filter.GREATER_THAN:
      if self.__start is None or limit >= self.__start:
        self.__start = limit
        self.__start_inclusive = False
    elif (rel_op == datastore_pb.Query_Filter.GREATER_THAN_OR_EQUAL or
          rel_op == datastore_pb.Query_Filter.EQUAL):
      if self.__start is None or limit > self.__start:
        self.__start = limit
        self.__start_inclusive = True

  def Contains(self, value):
    """Check if the range contains a specific value.

    Args:
      value: the value to check.
    Returns:
      True iff value is contained in this range.
    """
    if self.__start is not None:
      if self.__start_inclusive and value < self.__start: return False
      if not self.__start_inclusive and value <= self.__start: return False
    if self.__end is not None:
      if self.__end_inclusive and value > self.__end: return False
      if not self.__end_inclusive and value >= self.__end: return False
    return True

  def Remap(self, mapper):
    """Transforms the range extremes with a function.

    The function mapper must preserve order, i.e.
      x rel_op y iff mapper(x) rel_op y

    Args:
      mapper: function to apply to the range extremes.
    """
    self.__start = self.__start and mapper(self.__start)
    self.__end = self.__end and mapper(self.__end)

  def MapExtremes(self, mapper):
    """Evaluate a function on the range extremes.

    Args:
      mapper: function to apply to the range extremes.
    Returns:
      (x, y) where x = None if the range has no start,
                       mapper(start, start_inclusive, False) otherwise
                   y = None if the range has no end,
                       mapper(end, end_inclusive, True) otherwise
    """
    return (
        self.__start and mapper(self.__start, self.__start_inclusive, False),
        self.__end and mapper(self.__end, self.__end_inclusive, True))


def ParseKeyFilteredQuery(filters, orders):
  """Parse queries which only allow filters and ascending-orders on __key__.

  Raises exceptions for illegal queries.
  Args:
    filters: the normalized filters of a query.
    orders: the normalized orders of a query.
  Returns:
     The key range (a ValueRange over datastore_types.Key) requested in the
     query.
  """

  remaining_filters = []
  key_range = ValueRange()
  key_prop = datastore_types._KEY_SPECIAL_PROPERTY
  for f in filters:
    op = f.op()
    if not (f.property_size() == 1 and
            f.property(0).name() == key_prop and
            not (op == datastore_pb.Query_Filter.IN or
                 op == datastore_pb.Query_Filter.EXISTS)):
      remaining_filters.append(f)
      continue

    val = f.property(0).value()
    Check(val.has_referencevalue(), '__key__ kind must be compared to a key')
    limit = datastore_types.FromReferenceProperty(val)
    key_range.Update(op, limit)


  remaining_orders = []
  for o in orders:
    if not (o.direction() == datastore_pb.Query_Order.ASCENDING and
            o.property() == datastore_types._KEY_SPECIAL_PROPERTY):
      remaining_orders.append(o)
    else:
      break



  Check(not remaining_filters,
        'Only comparison filters on ' + key_prop + ' supported')
  Check(not remaining_orders,
        'Only ascending order on ' + key_prop + ' supported')

  return key_range


def ParseKindQuery(query, filters, orders):
  """Parse __kind__ (schema) queries.

  Raises exceptions for illegal queries.
  Args:
    query: A Query PB.
    filters: the normalized filters from query.
    orders: the normalized orders from query.
  Returns:
     The kind range (a ValueRange over string) requested in the query.
  """

  Check(not query.has_ancestor(), 'ancestor queries on __kind__ not allowed')

  key_range = ParseKeyFilteredQuery(filters, orders)
  key_range.Remap(_KindKeyToString)

  return key_range


def _KindKeyToString(key):
  """Extract kind name from __kind__ key.

  Raises an ApplicationError if the key is not of the form '__kind__'/name.

  Args:
    key: a key for a __kind__ instance.
  Returns:
    kind specified by key.
  """
  key_path = key.to_path()
  if (len(key_path) == 2 and key_path[0] == '__kind__' and
      isinstance(key_path[1], basestring)):
    return key_path[1]
  Check(False, 'invalid Key for __kind__ table')


def ParseNamespaceQuery(query, filters, orders):
  """Parse __namespace__  queries.

  Raises exceptions for illegal queries.
  Args:
    query: A Query PB.
    filters: the normalized filters from query.
    orders: the normalized orders from query.
  Returns:
     The kind range (a ValueRange over string) requested in the query.
  """

  Check(not query.has_ancestor(),
        'ancestor queries on __namespace__ not allowed')

  key_range = ParseKeyFilteredQuery(filters, orders)
  key_range.Remap(_NamespaceKeyToString)

  return key_range


def _NamespaceKeyToString(key):
  """Extract namespace name from __namespace__ key.

  Raises an ApplicationError if the key is not of the form '__namespace__'/name
  or '__namespace__'/_EMPTY_NAMESPACE_ID.

  Args:
    key: a key for a __namespace__ instance.
  Returns:
    namespace specified by key.
  """
  key_path = key.to_path()
  if len(key_path) == 2 and key_path[0] == '__namespace__':
    if key_path[1] == datastore_types._EMPTY_NAMESPACE_ID:
      return ''
    if isinstance(key_path[1], basestring):
      return key_path[1]
  Check(False, 'invalid Key for __namespace__ table')


def ParsePropertyQuery(query, filters, orders):
  """Parse __property__  queries.

  Raises exceptions for illegal queries.
  Args:
    query: A Query PB.
    filters: the normalized filters from query.
    orders: the normalized orders from query.
  Returns:
     The kind range (a ValueRange over (kind, property) pairs) requested
     in the query.
  """

  Check(not query.has_transaction(),
        'transactional queries on __property__ not allowed')

  key_range = ParseKeyFilteredQuery(filters, orders)
  key_range.Remap(lambda x: _PropertyKeyToString(x, ''))

  if query.has_ancestor():
    ancestor = datastore_types.Key._FromPb(query.ancestor())
    ancestor_kind, ancestor_property = _PropertyKeyToString(ancestor, None)


    if ancestor_property is not None:
      key_range.Update(datastore_pb.Query_Filter.EQUAL,
                       (ancestor_kind, ancestor_property))
    else:

      key_range.Update(datastore_pb.Query_Filter.GREATER_THAN_OR_EQUAL,
                       (ancestor_kind, ''))
      key_range.Update(datastore_pb.Query_Filter.LESS_THAN_OR_EQUAL,
                       (ancestor_kind + '\0', ''))
    query.clear_ancestor()

  return key_range

def _PropertyKeyToString(key, default_property):
  """Extract property name from __property__ key.

  Raises an ApplicationError if the key is not of the form
  '__kind__'/kind, '__property__'/property or '__kind__'/kind

  Args:
    key: a key for a __property__ instance.
    default_property: property value to return when key only has a kind.
  Returns:
    kind, property if key = '__kind__'/kind, '__property__'/property
    kind, default_property if key = '__kind__'/kind
  """
  key_path = key.to_path()
  if (len(key_path) == 2 and
      key_path[0] == '__kind__' and isinstance(key_path[1], basestring)):
    return (key_path[1], default_property)
  if (len(key_path) == 4 and
      key_path[0] == '__kind__' and isinstance(key_path[1], basestring) and
      key_path[2] == '__property__' and isinstance(key_path[3], basestring)):
    return (key_path[1], key_path[3])

  Check(False, 'invalid Key for __property__ table')


def SynthesizeUserId(email):
  """Return a synthetic user ID from an email address.

  Note that this is not the same user ID found in the production system.

  Args:
    email: An email address.

  Returns:
    A string userid derived from the email address.
  """

  user_id_digest = _MD5_FUNC(email.lower()).digest()
  user_id = '1' + ''.join(['%02d' % ord(x) for x in user_id_digest])[:20]
  return user_id


def FillUsersInQuery(filters):
  """Fill in a synthetic user ID for all user properties in a set of filters.

  Args:
    filters: The normalized filters from query.
  """
  for filter in filters:
    for property in filter.property_list():
      FillUser(property)


def FillUser(property):
  """Fill in a synthetic user ID for a user properties.

  Args:
    property: A Property which may have a user value.
  """
  if property.value().has_uservalue():
    uid = SynthesizeUserId(property.value().uservalue().email())
    if uid:
      property.mutable_value().mutable_uservalue().set_obfuscated_gaiaid(uid)


class BaseCursor(object):
  """A base query cursor over a list of entities.

  Public properties:
    cursor: the integer cursor
    app: the app for which this cursor was created

  Class attributes:
    _next_cursor: the next cursor to allocate
    _next_cursor_lock: protects _next_cursor
  """
  _next_cursor = 1
  _next_cursor_lock = threading.Lock()

  def __init__(self, app):
    """Constructor.

    Args:
      app: The app this cursor is being created for.
    """
    self.app = app
    self.cursor = self._AcquireCursorID()

  def PopulateCursor(self, query_result):
    if query_result.more_results():
      cursor = query_result.mutable_cursor()
      cursor.set_app(self.app)
      cursor.set_cursor(self.cursor)

  @classmethod
  def _AcquireCursorID(cls):
    """Acquires the next cursor id in a thread safe manner."""
    cls._next_cursor_lock.acquire()
    try:
      cursor_id = cls._next_cursor
      cls._next_cursor += 1
    finally:
      cls._next_cursor_lock.release()
    return cursor_id


class ListCursor(BaseCursor):
  """A query cursor over a list of entities.

  Public properties:
    keys_only: whether the query is keys_only
  """

  def __init__(self, query, results, order_compare_entities,
               order_property_names):
    """Constructor.

    Args:
      query: the query request proto
      results: list of datastore_pb.EntityProto
      order_compare_entities: a __cmp__ function for datastore_pb.EntityProto
        that follows sort order as specified by the query
      order_property_names: a set of the names of properties used in
        order_compare_entities.
    """
    super(ListCursor, self).__init__(query.app())

    self.__order_property_names = order_property_names
    if query.has_compiled_cursor() and query.compiled_cursor().position_list():
      self.__last_result, inclusive = (self._DecodeCompiledCursor(
          query.compiled_cursor()))
      start_cursor_position = ListCursor._GetCursorOffset(
          results, self.__last_result, inclusive, order_compare_entities)
    else:
      self.__last_result = None
      start_cursor_position = 0

    if query.has_end_compiled_cursor():
      if query.end_compiled_cursor().position_list():
        end_cursor_entity, inclusive = self._DecodeCompiledCursor(
            query.end_compiled_cursor())
        end_cursor_position = ListCursor._GetCursorOffset(
            results, end_cursor_entity, inclusive, order_compare_entities)
      else:
        end_cursor_position = 0
    else:
      end_cursor_position = len(results)


    results = results[start_cursor_position:end_cursor_position]


    if query.has_limit():
      limit = query.limit()
      if query.offset():
        limit += query.offset()
      if limit >= 0 and limit < len(results):
        results = results[:limit]

    self.__results = results
    self.__offset = 0
    self.__count = len(self.__results)


    self.keys_only = query.keys_only()

  @staticmethod
  def _GetCursorOffset(results, cursor_entity, inclusive, compare):
    """Converts a cursor entity into a offset into the result set even if the
    cursor_entity no longer exists.

    Args:
      results: the query's results (sequence of datastore_pb.EntityProto)
      cursor_entity: the datastore_pb.EntityProto from the compiled query
      inclusive: boolean that specifies if to offset past the cursor_entity
      compare: a function that takes two datastore_pb.EntityProto and compares
        them.
    Returns:
      the integer offset
    """
    lo = 0
    hi = len(results)
    if inclusive:

      while lo < hi:
        mid = (lo + hi) // 2
        if compare(results[mid], cursor_entity) < 0:
          lo = mid + 1
        else:
          hi = mid
    else:

      while lo < hi:
        mid = (lo + hi) // 2
        if compare(cursor_entity, results[mid]) < 0:
          hi = mid
        else:
          lo = mid + 1
    return lo

  def _DecodeCompiledCursor(self, compiled_cursor):
    """Converts a compiled_cursor into a cursor_entity.

    Args:
      compiled_cursor: The datastore_pb.CompiledCursor to decode.

    Returns:
      (cursor_entity, inclusive): a datastore_pb.EntityProto and if it should
      be included in the result set.
    """
    assert len(compiled_cursor.position_list()) == 1

    position = compiled_cursor.position(0)




    remaining_properties = self.__order_property_names.copy()
    cursor_entity = datastore_pb.EntityProto()
    cursor_entity.mutable_key().CopyFrom(position.key())
    for indexvalue in position.indexvalue_list():
      property = cursor_entity.add_property()
      property.set_name(indexvalue.property())
      property.mutable_value().CopyFrom(indexvalue.value())
      remaining_properties.remove(indexvalue.property())

    Check(not remaining_properties,
          'Cursor does not match query: missing values for %r' %
          remaining_properties)

    return (cursor_entity, position.start_inclusive())

  def _EncodeCompiledCursor(self, compiled_cursor):
    """Converts the current state of the cursor into a compiled_cursor.

    Args:
      query: the datastore_pb.Query this cursor is related to
      compiled_cursor: an empty datstore_pb.CompiledCursor
    """
    if self.__last_result is not None:


      position = compiled_cursor.add_position()
      position.mutable_key().MergeFrom(self.__last_result.key())
      for prop in self.__last_result.property_list():
        if prop.name() in self.__order_property_names:
          indexvalue = position.add_indexvalue()
          indexvalue.set_property(prop.name())
          indexvalue.mutable_value().CopyFrom(prop.value())
      position.set_start_inclusive(False)

  def Count(self):
    """Counts results, up to the query's limit.

    Note this method does not deduplicate results, so the query it was generated
    from should have the 'distinct' clause applied.

    Returns:
      int: Result count.
    """
    return self.__count

  def PopulateQueryResult(self, result, count, offset, compile=False):
    """Populates a QueryResult with this cursor and the given number of results.

    Args:
      result: datastore_pb.QueryResult
      count: integer of how many results to return
      offset: integer of how many results to skip
      compile: boolean, whether we are compiling this query
    """

    offset = min(offset, self.__count - self.__offset)
    limited_offset = min(offset, _MAX_QUERY_OFFSET)
    if limited_offset:
      self.__offset += limited_offset
      result.set_skipped_results(limited_offset)

    if offset == limited_offset and count:

      if count > _MAXIMUM_RESULTS:
        count = _MAXIMUM_RESULTS
      results = self.__results[self.__offset:self.__offset + count]
      count = len(results)
      self.__offset += count





      result.result_list().extend(LoadEntity(entity) for entity in results)

    if self.__offset:

      self.__last_result = self.__results[self.__offset - 1]

    result.set_keys_only(self.keys_only)
    result.set_more_results(self.__offset < self.__count)
    self.PopulateCursor(result)
    if compile:
      self._EncodeCompiledCursor(result.mutable_compiled_cursor())


def _SynchronizeTxn(function):
  """A decorator that locks a transaction during the function call."""

  def sync(txn, *args, **kwargs):

    assert txn._read_pos is None or txn._read_pos >= LiveTxn.FIRST_LOG_POS

    txn._lock.acquire()
    try:

      return function(txn, *args, **kwargs)
    finally:

      txn._lock.release()
  return sync


def _GetEntityGroup(ref):
  """Returns the entity group key for the given reference."""
  entity_group = entity_pb.Reference()
  entity_group.CopyFrom(ref)
  assert (entity_group.path().element_list()[0].has_id() or
          entity_group.path().element_list()[0].has_name())
  del entity_group.path().element_list()[1:]
  return entity_group


class LiveTxn(object):
  """An in flight transaction."""


  FIRST_LOG_POS = -1
  COMMITED = -2
  APPLIED = -3
  ROLLEDBACK = -4



  _read_pos = None
  _commit_time = None



  _snapshot = None



  _entity_group = None

  def __init__(self, txn_manager, app):
    assert isinstance(txn_manager, BaseTransactionManager)
    assert isinstance(app, basestring)

    self._txn_manager = txn_manager
    self._app = app



    self._lock = threading.RLock()


    self._put = {}
    self._delete = {}
    self._actions = []

  def _GetEntityGroup(self):
    """Get the current entity group.

    If no entity group has been discovered returns a 'global' entity group.
    This is possible if the txn only contains transactional tasks.

    Returns:
      The entity_pb.Reference for the entity group used in this txn.
    """
    return self._entity_group or datastore_types.Key.from_path(
        '__global__', 1, _app=self._app)._ToPb()

  def GetEntityGroup(self):
    """Get the current entity group.

    If no entity group has been discovered returns a 'global' entity group.
    This is possible if the txn only contains transactional tasks.

    This can only be called after the txn has been committed as the entity group
    can change as operations are performed.

    Returns:
      The entity_pb.Reference for the entity group used in this txn.
    """
    assert self._read_pos == self.COMMITED
    return self._GetEntityGroup()

  def _CheckOrSetEntityGroup(self, reference):
    """Checks or sets the entity group.

    If no entity group has been set, the entity group of the given
    entity_pb.Reference is set for the txn. Otherwise the entity group of the
    reference is asserted to be the set entity group.

    Args:
      reference: A entity_pb.Reference from which to extract the entity group.
    """
    entity_group = _GetEntityGroup(reference)
    if self._entity_group:
      Check(self._entity_group == entity_group,
            'Transactions cannot span entity groups')
    else:
      Check(self._app == reference.app())
      self._entity_group = entity_group

  def _CheckOrSetSnapshot(self, reference):
    """Checks or sets the snapshot for this txn.

    The entity group of reference is first checked or set on the current txn.
    Then, if no snapshot has been set, a snapshot is taken of the entity_group
    and stored for future reads (this also sets the read position)

    Args:
      reference: A entity_pb.Reference from which to extract the entity group.
    """
    self._CheckOrSetEntityGroup(reference)
    if self._snapshot is None:
      self._read_pos, self._snapshot = self._txn_manager._GrabSnapshot(
          self._entity_group)

  @_SynchronizeTxn
  def Get(self, reference):
    """Returns the entity associated with the given entity_pb.Reference or None.

    Does not see any modifications in the current txn.

    Args:
      reference: The entity_pb.Reference of the entity to look up.

    Returns:
      The associated entity_pb.EntityProto or None if no such entity exists.
    """
    self._CheckOrSetSnapshot(reference)
    entity = self._snapshot.get(datastore_types.ReferenceToKeyValue(reference))
    return LoadEntity(entity)

  @_SynchronizeTxn
  def GetQueryCursor(self, query, filters, orders):
    """Runs the given datastore_pb.Query and returns a QueryCursor for it.

    Does not see any modifications in the current txn.

    Args:
      query: The datastore_pb.Query to run.
      filters: A list of filters that override the ones found on query.
      orders: A list of orders that override the ones found on query.

    Returns:
      A BaseCursor that can be used to fetch query results.
    """
    Check(query.has_ancestor(),
          'Query must have an ancestor when performed in a transaction.')
    self._CheckOrSetSnapshot(query.ancestor())
    return _GetQueryCursor(self._snapshot.values(), query, filters, orders)

  @_SynchronizeTxn
  def Put(self, entity, insert):
    """Puts the given entity.

    Args:
      entity: The entity_pb.EntityProto to put.
      insert: A boolean that indicates if we should fail if the entity already
        exists.
    """
    self._CheckOrSetEntityGroup(entity.key())
    key = datastore_types.ReferenceToKeyValue(entity.key())
    self._delete.pop(key, None)
    self._put[key] = (entity, insert)

  @_SynchronizeTxn
  def Delete(self, reference):
    """Deletes the entity associated with the given reference.

    Args:
      reference: The entity_pb.Reference of the entity to delete.
    """
    self._CheckOrSetEntityGroup(reference)
    key = datastore_types.ReferenceToKeyValue(reference)
    self._put.pop(key, None)
    self._delete[key] = reference

  @_SynchronizeTxn
  def AddActions(self, actions, max_actions=None):
    """Adds the given actions to the current txn.

    Args:
      actions: A list of pbs to send to taskqueue.Add when the txn is applied.
      max_actions: A number that indicates the maximum number of actions to
        allow on this txn.
    """
    Check(not max_actions or len(self._actions) + len(actions) <= max_actions,
          'Too many messages, maximum allowed %s' % max_actions)
    self._actions.extend(actions)

  @_SynchronizeTxn
  def Rollback(self):
    """Rollback the current txn."""
    self._read_pos = self.ROLLEDBACK

  @_SynchronizeTxn
  def Commit(self):
    """Commits the current txn.

    This function hands off the responsibility of calling _Apply to the owning
    TransactionManager.
    """

    if not self._put and not self._delete and not self._actions:
      return self.Rollback()

    try:


      for entity, insert in self._put.itervalues():
        Check(not insert or self.Get(entity.key()) is None,
              'the id allocated for a new entity was already '
              'in use, please try again')


      entity_group = self._GetEntityGroup()
      self._commit_time = datetime.datetime.now()
      success = False
      self._read_pos = self._txn_manager._AcquireWriteLock(entity_group,
                                                           self._read_pos)
    except:

      self.Rollback()
      raise

    try:

      self._read_pos = self.COMMITED
      success = True
    finally:

      self._txn_manager._ReleaseWriteLock(entity_group, self, success)

  def _Apply(self):
    """Applies the current txn.

    This function blindly performs the operations contained in the current txn.
    The calling function must acquire the entity group write lock and insure
    transactions are applied in order.
    """

    self._lock.acquire()
    try:

      assert self._read_pos == self.COMMITED


      for entity, insert in self._put.itervalues():
        self._txn_manager._Put(entity, insert)


      for key in self._delete.itervalues():
        self._txn_manager._Delete(key)


      for action in self._actions:
        try:
          apiproxy_stub_map.MakeSyncCall(
              'taskqueue', 'Add', action, api_base_pb.VoidProto())
        except apiproxy_errors.ApplicationError, e:
          logging.warning('Transactional task %s has been dropped, %s',
                          action, e)

      self._read_pos = self.APPLIED
      self._txn_manager._OnApply()
    finally:
      self._lock.release()


class EntityGroupMetaData(object):
  """The metadata assoicated with an entity group."""


  _log_pos = -1

  _snapshot = None

  def __init__(self):
    self._write_lock = threading.Lock()
    self._apply_queue = []

  def CatchUp(self):
    """Applies all outstanding txns."""

    assert self._write_lock.acquire(False) is False

    for txn in self._apply_queue:
      txn._Apply()
    self._apply_queue = []

  def IncrementLogPos(self):
    """Increments the current log position and clears the snapshot cache.

    This should be called everytime a txn is commited.
    """

    assert self._write_lock.acquire(False) is False
    self._log_pos += 1
    self._snapshot = None

class BaseConsistencyPolicy(object):
  """A base class for a consistency policy to be used with a transaction manger.
  """



  def _OnCommit(self, txn, meta_data):
    """Called after a LiveTxn has been commited.

    This function can either apply the txn right away or enqueue it in the
    entity group metadata.

    This function should assume the write lock on the metadata object is already
    acquired.

    Args:
      txn: A LiveTxn that has been commited
      meta_data: The EntityGroupMetaData for thie given txn
    """
    raise NotImplementedError

  def _OnGroom(self, meta_data_list):
    """Called once for every global query.

    This function must aqcuire the write lock for any meta data before applying
    any outstanding txns.

    Args:
      meta_data_list: A list of EntityGroupMetaData objects.
    """
    raise NotImplementedError


class MasterSlaveConsistencyPolicy(BaseConsistencyPolicy):
  """Enforces the Master / Slave consistency policy.

  Applies all txn on commit.
  """

  def _OnCommit(self, txn, meta_data):
    assert not meta_data._apply_queue
    txn._Apply()

  def _OnGroom(self, meta_data_list):
    pass


class BaseHighReplicationConsistencyPolicy(BaseConsistencyPolicy):
  """A base class for High Replication Datastore consistency policies.

  All txn are applied asynchronously.
  """

  def _OnCommit(self, txn, meta_data):
    meta_data._apply_queue.append(txn)

  def _OnGroom(self, meta_data_list):


    for meta_data in meta_data_list:
      if not meta_data._apply_queue:
        continue


      meta_data._write_lock.acquire()
      try:
        for i, txn in enumerate(meta_data._apply_queue):
          if self._ShouldApply(txn):

            txn._Apply()
          else:

            meta_data._apply_queue = meta_data._apply_queue[i:]
            break
        else:

          meta_data._apply_queue = []
      finally:
        meta_data._write_lock.release()

  def _ShouldApply(self, txn):
    """Determins if the given transaction should be applied."""
    raise NotImplementedError


class TimeBasedHRConsistencyPolicy(BaseHighReplicationConsistencyPolicy):
  """A High Replication Datastore consiseny policy based on elapsed time.

  This class tries to simulate performance seen in the high replication
  datastore using estimated probabilities of a transaction commiting after a
  given amount of time.
  """

  _classification_map = [(.98, 100),
                         (.99, 300),
                         (.995, 2000),
                         (1, 240000)
                         ]

  def SetClassificationMap(self, classification_map):
    """Set the probability a txn will be applied after a given amount of time.

    Args:
      classification_map: A list of tuples containing (float between 0 and 1,
        number of miliseconds) that define the probability of a transaction
        applying after a given amount of time.
    """
    for prob, delay in classification_map:
      if prob < 0 or prob > 1 or delay <= 0:
        raise TypeError(
            'classification_map must be a list of (probability, delay) tuples, '
            'found %r' % (classification_map,))

    self._classification_map = sorted(classification_map)

  def _ShouldApplyImpl(self, elapsed_ms, classification):
    for rate, ms in self._classification_map:
      if classification <= rate:
        break
    return elapsed_ms >= ms

  def _Classify(self, txn):
    return random.Random(id(txn)).random()

  def _ShouldApply(self, txn):
    elapsed_ms = ((datetime.datetime.now() - txn._commit_time).microseconds //
                  1000)
    classification = self._Classify(txn)
    return self._ShouldApplyImpl(elapsed_ms, classification)


class PseudoRandomHRConsistencyPolicy(BaseHighReplicationConsistencyPolicy):
  """A policy that always gives the same sequence of consistency decisions."""

  def __init__(self, probability=.5, seed=0):
    """Constructor.

    Args:
      probability: A number between 0 and 1 that is the likelihood of a
        transaction applying before a global query is executed.
      seed: A hashable object to use as a seed. Use None to use the current
        timestamp.
    """
    self.SetProbability(probability)
    self.SetSeed(seed)

  def SetProbability(self, probability):
    """Change the probability of a transaction applying.

    Args:
      probability: A number between 0 and 1 that determins the probability of a
        transaction applying before a global query is run.
    """
    if probability < 0 or probability > 1:
      raise TypeError('probability must be a number between 0 and 1, found %r' %
                      probability)
    self._probability = probability

  def SetSeed(self, seed):
    """Reset the seed."""
    self._random = random.Random(seed)

  def _ShouldApply(self, txn):
    return self._random.random() < self._probability


class BaseTransactionManager(object):
  """A class that manages the state of transactions.

  This includes creating consistent snap shots for transactions.
  """

  def __init__(self, consistency_policy=None):
    super(BaseTransactionManager, self).__init__()

    self._consistency_policy = (consistency_policy or
                                MasterSlaveConsistencyPolicy())


    self._meta_data_lock = threading.Lock()
    BaseTransactionManager.Clear(self)

  def SetConsistencyPolicy(self, policy):
    """Set the consistency to use.

    Causes all data to be flushed.

    Args:
      policy: A obj inheriting from BaseConsistencyPolicy.
    """
    if not isinstance(policy, BaseConsistencyPolicy):
      raise TypeError('policy should be of type '
                      'datastore_stub_util.BaseConsistencyPolicy found %r.' %
                      (policy,))
    self._consistency_policy = policy
    self.Clear()

  def Clear(self):
    """Discards any pending transactions and resets the meta_data."""

    self._meta_data = collections.defaultdict(EntityGroupMetaData)

    self._txn_map = {}

  def BeginTransaction(self, app):
    """Start a transaction on the given app.

    Args:
      app: A string representing the app for which to start the transaction.

    Returns:
      A datastore_pb.Transaction for the created transaction
    """
    txn = self._BeginTransaction(app)
    self._txn_map[id(txn)] = txn
    transaction = datastore_pb.Transaction()
    transaction.set_app(app)
    transaction.set_handle(id(txn))
    return transaction

  def GetTxn(self, transaction, request_trusted=False, request_app=None):
    """Gets the LiveTxn object associated with the given transaction.

    Args:
      transaction: The datastore_pb.Transaction to look up.
      request_trusted: A boolean indicating If the requesting app is trusted.
      request_app: A string representing the app making the request.

    Returns:
      The associated LiveTxn object.
    """
    request_app = datastore_types.ResolveAppId(request_app)
    CheckTransaction(request_trusted, request_app, transaction)
    txn = self._txn_map.get(transaction.handle())
    Check(txn and txn._app == transaction.app(),
          'Transaction %s not found' % transaction)
    return txn

  def Groom(self):
    """Attempts to apply any outstanding transactions.

    The consistency policy determins if a transaction should be applied.
    """
    self._meta_data_lock.acquire()
    try:
      self._consistency_policy._OnGroom(self._meta_data.itervalues())
    finally:
      self._meta_data_lock.release()

  def _GetMetaData(self, entity_group):
    """Safely gets the EntityGroupMetaData object for the given entity_group.
    """
    self._meta_data_lock.acquire()
    try:
      return self._meta_data[datastore_types.ReferenceToKeyValue(entity_group)]
    finally:
      self._meta_data_lock.release()

  def _BeginTransaction(self, app):
    """Starts a transaction without storing it in the txn_map."""
    return LiveTxn(self, app)

  def _GrabSnapshot(self, entity_group):
    """Grabs a consistent snapshot of the given entity group.

    Args:
      entity_group: A entity_pb.Reference of the entity group of which the
        snapshot should be taken.

    Returns:
      A tuple of (log_pos, snapshot) where log_pos is the current log position
      and snapshot is a map of reference key value to entity_pb.EntityProto.
    """

    meta_data = self._GetMetaData(entity_group)
    meta_data._write_lock.acquire()
    try:
      if not meta_data._snapshot:

        meta_data.CatchUp()
        meta_data._snapshot = self._GetEntitiesInEntityGroup(entity_group)
      return meta_data._log_pos, meta_data._snapshot
    finally:

      meta_data._write_lock.release()

  def _AcquireWriteLock(self, entity_group, log_pos=None):
    """Acquire the write lock for the given entity_group.

    This lock must be released with _ReleaseWriteLock before returning to the
    user.

    Args:
      entity_group: A entity_pb.Reference of the entity group to lock.
      log_pos: The log position to lock or None.

    Returns:
      The log position locked.

    Raises:
      apiproxy_errors.ApplicatonError if the log position cannot be locked
    """
    meta_data = self._GetMetaData(_GetEntityGroup(entity_group))
    meta_data._write_lock.acquire()
    try:
      if log_pos is None:

        meta_data.CatchUp()
      else:
          Check(meta_data._log_pos == log_pos,
                'Concurrency exception.',
                datastore_pb.Error.CONCURRENT_TRANSACTION)
    except:
      meta_data._write_lock.release()
      raise
    return meta_data._log_pos

  def _ReleaseWriteLock(self, entity_group, txn=None, modified=True):
    """Release the write lock of the given entity group.

    Args:
      entity_group: A entity_pb.Reference of the entity group to release.
      txn: A LiveTxn that may need to be applied or None.
      modified: A boolean that indicates if the entity group has been changed.
    """
    meta_data = self._GetMetaData(entity_group)
    try:
      if modified:
        meta_data.IncrementLogPos()
        if txn:
          self._consistency_policy._OnCommit(txn, meta_data)
    finally:
      meta_data._write_lock.release()

  def _RemoveTxn(self, txn):
    """Removes a LiveTxn from the txn_map."""
    del self._txn_map[id(txn)]

  def _Put(self, entity, insert):
    """Put the given entity.

    This must be implemented by a sub-class. The sub-class can assume that any
    need consistency is enforced at a higher level (and can just put blindly).

    Args:
      entity: The entity_pb.EntityProto to put.
      insert: A boolean that indicates if we should fail if the entity already
        exists.
    """
    raise NotImplementedError

  def _Delete(self, reference):
    """Delete the entity associated with the specified reference.

    This must be implemented by a sub-class. The sub-class can assume that any
    need consistency is enforced at a higher level (and can just delete
    blindly).

    Args:
      reference: The entity_pb.Reference of the entity to delete.
    """
    raise NotImplementedError

  def _OnApply(self):
    """Hook to take action after a transaction is applied."""
    pass

  def _GetEntitiesInEntityGroup(self, entity_group):
    """Gets the contents of a specific entity group.

    This must be implemented by a sub-class. The sub-class can assume that any
    need consistency is enforced at a higher level (and can just blindly read).

    Other entity groups may be modified concurrently.

    Args:
      entity_group: A entity_pb.Reference of the entity group to get.

    Returns:
      A dict mapping datastore_types.ReferenceToKeyValue(key) to EntityProto
    """
    raise NotImplementedError


class BaseIndexManager(object):
  """A generic index manager that stores all data in memory."""








  WRITE_ONLY = entity_pb.CompositeIndex.WRITE_ONLY
  READ_WRITE = entity_pb.CompositeIndex.READ_WRITE
  DELETED = entity_pb.CompositeIndex.DELETED
  ERROR = entity_pb.CompositeIndex.ERROR

  _INDEX_STATE_TRANSITIONS = {
      WRITE_ONLY: frozenset((READ_WRITE, DELETED, ERROR)),
      READ_WRITE: frozenset((DELETED,)),
      ERROR: frozenset((DELETED,)),
      DELETED: frozenset((ERROR,)),
  }

  def __init__(self):



    self.__indexes = collections.defaultdict(list)
    self.__indexes_lock = threading.Lock()
    self.__next_index_id = 1
    self.__index_id_lock = threading.Lock()

  def __FindIndex(self, index):
    """Finds an existing index by definition.

    Args:
      index: entity_pb.CompositeIndex

    Returns:
      entity_pb.CompositeIndex, if it exists; otherwise None
    """
    app = index.app_id()
    if app in self.__indexes:
      for stored_index in self.__indexes[app]:
        if index.definition() == stored_index.definition():
          return stored_index

    return None

  def CreateIndex(self, index, trusted=False, calling_app=None):
    calling_app = datastore_types.ResolveAppId(calling_app)
    CheckAppId(trusted, calling_app, index.app_id())
    Check(index.id() == 0, 'New index id must be 0.')
    Check(not self.__FindIndex(index), 'Index already exists.')


    self.__index_id_lock.acquire()
    index.set_id(self.__next_index_id)
    self.__next_index_id += 1
    self.__index_id_lock.release()


    clone = entity_pb.CompositeIndex()
    clone.CopyFrom(index)
    app = index.app_id()
    clone.set_app_id(app)


    self.__indexes_lock.acquire()
    try:
      self.__indexes[app].append(clone)
    finally:
      self.__indexes_lock.release()

    self._OnIndexChange(index.app_id())

    return index.id()

  def GetIndexes(self, app, trusted=False, calling_app=None):
    calling_app = datastore_types.ResolveAppId(calling_app)
    CheckAppId(trusted, calling_app, app)

    return self.__indexes[app]

  def UpdateIndex(self, index, trusted=False, calling_app=None):
    CheckAppId(trusted, calling_app, index.app_id())

    stored_index = self.__FindIndex(index)
    Check(stored_index, 'Index does not exist.')
    Check(index.state() == stored_index.state() or
          index.state() in self._INDEX_STATE_TRANSITIONS[stored_index.state()],
          'cannot move index state from %s to %s' %
              (entity_pb.CompositeIndex.State_Name(stored_index.state()),
              (entity_pb.CompositeIndex.State_Name(index.state()))))


    self.__indexes_lock.acquire()
    try:
      stored_index.set_state(index.state())
    finally:
      self.__indexes_lock.release()

    self._OnIndexChange(index.app_id())

  def DeleteIndex(self, index, trusted=False, calling_app=None):
    CheckAppId(trusted, calling_app, index.app_id())

    stored_index = self.__FindIndex(index)
    Check(stored_index, 'Index does not exist.')


    app = index.app_id()
    self.__indexes_lock.acquire()
    try:
      self.__indexes[app].remove(stored_index)
    finally:
      self.__indexes_lock.release()

    self._OnIndexChange(index.app_id())

  def _SideLoadIndex(self, index):
    self.__indexes[index.app()].append(index)

  def _OnIndexChange(self, app_id):
    pass


class BaseDatastore(BaseTransactionManager, BaseIndexManager):
  """A base implemenation of a Datastore.

  This class implements common functions associated with a datastore and
  enforces security restrictions passed on by a stub or client. It is designed
  to be shared by any number of threads or clients serving any number of apps.

  If an app is not specified explicitly it is pulled from the env and assumed to
  be untrusted.
  """



  _MAX_QUERY_COMPONENTS = 100



  _BATCH_SIZE = 20



  _MAX_ACTIONS_PER_TXN = 5

  def __init__(self, require_indexes=False, consistency_policy=None):
    BaseTransactionManager.__init__(self, consistency_policy=consistency_policy)
    BaseIndexManager.__init__(self)

    self._require_indexes = require_indexes
    self._pseudo_kinds = {}

  def Clear(self):
    """Clears out all stored values."""

    BaseTransactionManager.Clear(self)


  def _RegisterPseudoKind(self, kind):
    """Registers a pseudo kind to be used to satisfy a meta data query."""
    self._pseudo_kinds[kind.name] = kind




  def GetQueryCursor(self, raw_query, trusted=False, calling_app=None):
    """Execute a query.

    Args:
      raw_query: The non-validated datastore_pb.Query to run.
      trusted: If the calling app is trusted.
      calling_app: The app requesting the results or None to pull the app from
        the environment.

    Returns:
      A BaseCursor that can be used to retrieve results.
    """

    calling_app = datastore_types.ResolveAppId(calling_app)
    CheckAppId(trusted, calling_app, raw_query.app())


    filters, orders = datastore_index.Normalize(raw_query.filter_list(),
                                                raw_query.order_list())


    CheckQuery(raw_query, filters, orders, self._MAX_QUERY_COMPONENTS)
    FillUsersInQuery(filters)


    self._CheckHasIndex(raw_query)


    if raw_query.has_transaction():

      Check(raw_query.kind() not in self._pseudo_kinds,
            'transactional queries on "%s" not allowed' % raw_query.kind())
      txn = self.GetTxn(raw_query.transaction())
      return txn.GetQueryCursor(raw_query, filters, orders)

    if raw_query.has_ancestor() and raw_query.kind() not in self._pseudo_kinds:

      txn = self._BeginTransaction(raw_query.app())
      return txn.GetQueryCursor(raw_query, filters, orders)


    self.Groom()
    return self._GetQueryCursor(raw_query, filters, orders)

  def Get(self, raw_keys, transaction=None, eventual_consistency=False,
          trusted=False, calling_app=None):
    """Get the entities for the given keys.

    Args:
      raw_keys: A list of unverified entity_pb.Reference objects.
      transaction: The datastore_pb.Transaction to use or None.
      eventual_consistency: If we should allow stale, potentially inconsistent
        results.
      trusted: If the calling app is trusted.
      calling_app: The app requesting the results or None to pull the app from
        the environment.

    Returns:
      A list containing the entity or None if no entity exists.
    """
    if not raw_keys:
      return []

    calling_app = datastore_types.ResolveAppId(calling_app)

    if not transaction and eventual_consistency:

      result = []
      for key in raw_keys:
        CheckReference(calling_app, trusted, key)
        result.append(self._Get(key))
      return result




    grouped_keys = collections.defaultdict(list)
    for i, key in enumerate(raw_keys):
      CheckReference(calling_app, trusted, key)
      entity_group = _GetEntityGroup(key)
      entity_group_key = datastore_types.ReferenceToKeyValue(entity_group)
      grouped_keys[entity_group_key].append((key, i))

    if transaction:

      Check(len(grouped_keys) == 1, 'Transactions cannot span entity groups')
      txn = self.GetTxn(transaction)

      return [txn.Get(key) for key, _ in grouped_keys.values()[0]]
    else:


      result = [None] * len(raw_keys)
      def op(txn, v):
        key, i = v
        result[i] = txn.Get(key)
      for keys in grouped_keys.itervalues():
        self._RunInTxn(keys, keys[0][0].app(), op)
      return result

  def Put(self, raw_entities, transaction=None,
          trusted=False, calling_app=None):
    """Writes the given given entities.

    Updates an entity's key and entity_group in place if needed

    Args:
      raw_entities: A list of unverified entity_pb.EntityProto objects.
      transaction: The datastore_pb.Transaction to use or None.
      trusted: If the calling app is trusted.
      calling_app: The app requesting the results or None to pull the app from
        the environment.
    Returns:
      A list of entity_pb.Reference objects that indicates where each entity
      was stored.
    """
    if not raw_entities:
      return []

    calling_app = datastore_types.ResolveAppId(calling_app)


    result = [None] * len(raw_entities)
    grouped_entities = collections.defaultdict(list)
    for i, raw_entity in enumerate(raw_entities):
      CheckReference(trusted, calling_app, raw_entity.key())



      entity = entity_pb.EntityProto()
      entity.CopyFrom(raw_entity)


      for prop in itertools.chain(entity.property_list(),
                                  entity.raw_property_list()):
        FillUser(prop)

      assert entity.has_key()
      assert entity.key().path().element_size() > 0

      last_element = entity.key().path().element_list()[-1]
      if not (last_element.id() or last_element.has_name()):
        insert = True


        last_element.set_id(self._AllocateIds(entity.key())[0])
      else:
        insert = False

      entity_group = _GetEntityGroup(entity.key())
      entity.mutable_entity_group().CopyFrom(entity_group.path())
      entity_group_key = datastore_types.ReferenceToKeyValue(entity_group)
      grouped_entities[entity_group_key].append((entity, insert))



      key = entity_pb.Reference()
      key.CopyFrom(entity.key())
      result[i] = key

    if transaction:

      Check(len(grouped_entities) == 1,
            'Transactions cannot span entity groups')
      txn = self.GetTxn(transaction, trusted, calling_app)
      for entity, insert in grouped_entities.values()[0]:
        txn.Put(entity, insert)
    else:

      for entities in grouped_entities.itervalues():
        self._RunInTxn(entities, entities[0][0].key().app(),
                       lambda txn, v: txn.Put(v[0], v[1]))
    return result

  def Delete(self, raw_keys, transaction=None,
             trusted=False, calling_app=None):
    """Deletes the entities associated with the given keys.

    Args:
      raw_keys: A list of unverified entity_pb.Reference objects.
      transaction: The datastore_pb.Transaction to use or None.
      trusted: If the calling app is trusted.
      calling_app: The app requesting the results or None to pull the app from
        the environment.
    """
    if not raw_keys:
      return

    calling_app = datastore_types.ResolveAppId(calling_app)


    grouped_keys = collections.defaultdict(list)
    for key in raw_keys:
      CheckReference(trusted, calling_app, key)
      entity_group = _GetEntityGroup(key)
      entity_group_key = datastore_types.ReferenceToKeyValue(entity_group)
      grouped_keys[entity_group_key].append(key)

    if transaction:

      Check(len(grouped_keys) == 1,
            'Transactions cannot span entity groups')
      txn = self.GetTxn(transaction, trusted, calling_app)
      for key in grouped_keys.values()[0]:
        txn.Delete(key)
    else:

      for keys in grouped_keys.itervalues():
        self._RunInTxn(keys, keys[0].app(), lambda txn, key: txn.Delete(key))

  def Touch(self, raw_keys, trusted=False, calling_app=None):
    """Applies all outstanding writes."""
    calling_app = datastore_types.ResolveAppId(calling_app)

    grouped_keys = collections.defaultdict(list)
    for key in raw_keys:
      CheckReference(trusted, calling_app, key)
      entity_group = _GetEntityGroup(key)
      entity_group_key = datastore_types.ReferenceToKeyValue(entity_group)
      grouped_keys[entity_group_key].append(key)

    for keys in grouped_keys.itervalues():
      self._RunInTxn(keys, keys[0].app(), lambda txn, key: None)

  def _RunInTxn(self, values, app, op):
    """Runs the given values in separate Txns.

    Args:
      values: A list of arguments to op.
      app: The app to create the Txns on.
      op: A function to run in each Txn.
    """
    txn = self._BeginTransaction(app)
    for value in values:
      op(txn, value)
    txn.Commit()

  def _CheckHasIndex(self, query):
    """Checks if the query can be satisfied given the existing indexes.

    Args:
      query: the datstore_pb.Query to check
    """


    if query.kind() in self._pseudo_kinds or not self._require_indexes:
      return


    required, kind, ancestor, props, num_eq_filters = datastore_index.CompositeIndexForQuery(query)

    if not required:
      return

    indexes = self.GetIndexes(query.app())
    eq_filters_set = set(props[:num_eq_filters])
    remaining_filters = props[num_eq_filters:]
    required_key = kind, ancestor, props
    for index in indexes:
      definition = datastore_index.ProtoToIndexDefinition(index)
      index_key = datastore_index.IndexToKey(definition)
      if required_key == index_key:
        break
      if num_eq_filters > 1 and (kind, ancestor) == index_key[:2]:

        this_props = index_key[2]
        this_eq_filters_set = set(this_props[:num_eq_filters])
        this_remaining_filters = this_props[num_eq_filters:]
        if (eq_filters_set == this_eq_filters_set and
            remaining_filters == this_remaining_filters):
          break
    else:

      raise apiproxy_errors.ApplicationError(
          datastore_pb.Error.NEED_INDEX,
          "This query requires a composite index that is not defined. "
          "You must update the index.yaml file in your application root.")



  def _GetQueryCursor(self, query, filters, orders):
    """Runs the given datastore_pb.Query and returns a QueryCursor for it.

    This must be implemented by a sub-class. The sub-class does not need to
    enforced any consistency guarantees (and can just blindly read).

    Args:
      query: The datastore_pb.Query to run.
      filters: A list of filters that override the ones found on query.
      orders: A list of orders that override the ones found on query.

    Returns:
      A BaseCursor that can be used to fetch query results.
    """
    raise NotImplementedError

  def _Get(self, reference):
    """Get the entity for the given reference or None.

    This must be implemented by a sub-class. The sub-class does not need to
    enforced any consistency guarantees (and can just blindly read).

    Args:
      reference: A entity_pb.Reference to loop up.

    Returns:
      The entity_pb.EntityProto associated with the given reference or None.
    """
    raise NotImplementedError

  def _AllocateIds(self, reference, size=1, max_id=None):
    """Allocate ids for given reference.

    Args:
      reference: A entity_pb.Reference to allocate an id for.
      size: The size of the range to allocate
      max_id: The upper bound of the range to allocate

    Returns:
      A tuple containing (min, max) of the allocated range.
    """
    raise NotImplementedError


class DatastoreStub(object):
  """A stub that maps datastore service calls on to a BaseDatastore.

  This class also keeps track of query cursors.
  """

  def __init__(self,
               datastore,
               app_id=None,
               trusted=None):
    super(DatastoreStub, self).__init__()
    self._datastore = datastore
    self._app_id = datastore_types.ResolveAppId(app_id)
    self._trusted = trusted
    DatastoreStub.Clear(self)

  def Clear(self):
    """Clears out all stored values."""
    self._query_cursors = {}

  def SetTrusted(self, trusted):
    """Set/clear the trusted bit in the stub.

    This bit indicates that the app calling the stub is trusted. A
    trusted app can write to datastores of other apps.

    Args:
      trusted: boolean.
    """
    self._trusted = trusted



  def _Dynamic_Get(self, req, res):


    transaction = req.has_transaction() and req.transaction() or None
    for entity in self._datastore.Get(req.key_list(), transaction,
                                      req.has_failover_ms(),
                                      self._trusted, self._app_id):
      result = res.add_entity()
      if entity:
        result.mutable_entity().CopyFrom(entity)

  def _Dynamic_Put(self, req, res):
    transaction = req.has_transaction() and req.transaction() or None
    res.key_list().extend(self._datastore.Put(req.entity_list(), transaction,
                                              self._trusted, self._app_id))

  def _Dynamic_Delete(self, req, _):
    transaction = req.has_transaction() and req.transaction() or None
    self._datastore.Delete(req.key_list(), transaction,
                           self._trusted, self._app_id)

  def _Dynamic_Touch(self, req, _):
    self._datastore.Touch(req.key_list(), self._trusted, self._app_id)

  def _Dynamic_RunQuery(self, query, query_result):
    cursor = self._datastore.GetQueryCursor(query, self._trusted, self._app_id)

    if query.has_count():
      count = query.count()
    elif query.has_limit():
      count = query.limit()
    else:
      count = self._BATCH_SIZE

    cursor.PopulateQueryResult(query_result, count, query.offset(),
                               query.compile())
    if query_result.has_cursor():
      self._query_cursors[query_result.cursor().cursor()] = cursor


    if query.compile():


      compiled_query = query_result.mutable_compiled_query()
      compiled_query.set_keys_only(query.keys_only())
      compiled_query.mutable_primaryscan().set_index_name(query.Encode())


  def _Dynamic_Next(self, next_request, query_result):
    app = next_request.cursor().app()
    CheckAppId(self._trusted, self._app_id, app)

    cursor = self._query_cursors.get(next_request.cursor().cursor())
    Check(cursor and cursor.app == app,
          'Cursor %d not found' % next_request.cursor().cursor())

    count = self._BATCH_SIZE
    if next_request.has_count():
      count = next_request.count()

    cursor.PopulateQueryResult(query_result, count, next_request.offset(),
                               next_request.compile())

    if not query_result.has_cursor():
      del self._query_cursors[next_request.cursor().cursor()]

  def _Dynamic_AddActions(self, request, _):
    """Associates the creation of one or more tasks with a transaction.

    Args:
      request: A taskqueue_service_pb.TaskQueueBulkAddRequest containing the
        tasks that should be created when the transaction is committed.
    """




    if not request.add_request_list():
      return

    transaction = request.add_request_list()[0].transaction()
    txn = self._datastore.GetTxn(transaction)
    new_actions = []
    for add_request in request.add_request_list():



      Check(add_request.transaction() == transaction,
            'Cannot add requests to different transactions')
      clone = taskqueue_service_pb.TaskQueueAddRequest()
      clone.CopyFrom(add_request)
      clone.clear_transaction()
      new_actions.append(clone)

    txn.AddActions(new_actions, self._MAX_ACTIONS_PER_TXN)

  def _Dynamic_BeginTransaction(self, req, transaction):
    CheckAppId(self._trusted, self._app_id, req.app())
    transaction.CopyFrom(self._datastore.BeginTransaction(req.app()))

  def _Dynamic_Commit(self, transaction, _):
    CheckAppId(self._trusted, self._app_id, transaction.app())
    txn = self._datastore.GetTxn(transaction, self._trusted, self._app_id)
    txn.Commit()

  def _Dynamic_Rollback(self, transaction, _):
    CheckAppId(self._trusted, self._app_id, transaction.app())
    txn = self._datastore.GetTxn(transaction, self._trusted, self._app_id)
    txn.Rollback()

  def _Dynamic_CreateIndex(self, index, id_response):
    id_response.set_value(self._datastore.CreateIndex(index,
                                                      self._trusted,
                                                      self._app_id))

  def _Dynamic_GetIndices(self, app_str, composite_indices):
    composite_indices.index_list().extend(self._datastore.GetIndexes(
        app_str.value(), self._trusted, self._app_id))

  def _Dynamic_UpdateIndex(self, index, _):
    self._datastore.UpdateIndex(index, self._trusted, self._app_id)

  def _Dynamic_DeleteIndex(self, index, _):
    self._datastore.DeleteIndex(index, self._trusted, self._app_id)

  def _Dynamic_AllocateIds(self, allocate_ids_request, allocate_ids_response):
    CheckAppId(allocate_ids_request.model_key().app(),
               self._trusted, self._app_id)

    reference = allocate_ids_request.model_key()

    (start, end) = self._datastore._AllocateIds(reference,
                                                allocate_ids_request.size(),
                                                allocate_ids_request.max())

    allocate_ids_response.set_start(start)
    allocate_ids_response.set_end(end)


def CompareEntityPbByKey(a, b):
  """Compare two entity protobuf's by key.

  Args:
    a: datastore_pb.EntityProto to compare
    b: datastore_pb.EntityProto to compare
  Returns:
     <0 if a's key is before b's, =0 if they are the same key, and >0 otherwise.
  """
  return cmp(datastore_types.Key._FromPb(a.key()),
             datastore_types.Key._FromPb(b.key()))


def _GuessOrders(filters, orders):
  """Guess any implicit ordering.

  The datastore gives a logical, but not necessarily predictable, ordering when
  orders are not completely explicit. This function guesses at that ordering
  (which is better then always ordering by __key__ for tests).

  Args:
    filters: The datastore_pb.Query_Filter that have already been normilized and
      checked.
    orders: The datastore_pb.Query_Order that have already been normilized and
      checked. Mutated in place.
  """
  orders = orders[:]

  if not orders:
    for filter_pb in filters:
      if filter_pb.op() != datastore_pb.Query_Filter.EQUAL:

        order = datastore_pb.Query_Order()
        order.set_property(filter_pb.property(0).name())
        orders.append(order)
        break


  if not orders or orders[-1].property() != '__key__':
    order = datastore_pb.Query_Order()
    order.set_property('__key__')
    orders.append(order)
  return orders


def _GetQueryCursor(results, query, filters, orders):
  """Get the generate a cursor for the given datastore_pb.Query."""
  orders = _GuessOrders(filters, orders)

  clone = datastore_pb.Query()
  clone.CopyFrom(query)
  clone.clear_filter()
  clone.clear_order()
  clone.filter_list().extend(filters)
  clone.order_list().extend(orders)

  dsquery = datastore_query.Query._from_pb(clone)
  cursor = ListCursor(query, datastore_query.apply_query(dsquery, results),
                      dsquery._order.cmp_for_filter(dsquery._filter_predicate),
                      set(order.property() for order in orders
                          if order.property() != '__key__'))
  return cursor
