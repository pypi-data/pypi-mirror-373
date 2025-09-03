# -*- coding: utf-8 -*- ----------------------------------------------------===#
#
#  Copyright 2016-2025 Trovares Inc. dba Rocketgraph.  All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#===------------------------------------------------------------------------===#

from __future__ import annotations

import ipaddress
import logging
import operator
import os.path
import pyarrow
import sys
import warnings

from collections.abc import Iterable, Mapping, Sequence
from typing import Optional, Union

from . import DataService_pb2 as data_proto
from . import ErrorMessages_pb2 as err_proto
from . import SchemaMessages_pb2 as sch_proto

log = logging.getLogger(__name__)

BOOLEAN = 'boolean'
INT = 'int'
UINT = 'uint'
FLOAT = 'float'
DATE = 'date'
TIME = 'time'
DATETIME = 'datetime'
IPADDRESS = 'ipaddress'
TEXT = 'text'
DURATION = 'duration'
ROWID = 'row_id'
LIST = 'list'
WGSPOINT = 'wgspoint'
CARTESIANPOINT = 'cartesianpoint'

# Send in 2MB chunks (grpc recommends 16-64 KB, but this got the best
# performance locally).  By default grpc only supports up to 4MB.
MAX_PACKET_SIZE = 2097152

# Default number of rows to use for Arrow data transfers between the client and
# the server.
DEFAULT_CHUNK_SIZE = 10000

# Server capabilities as indicated by the protocol version.

# TrustedProxyAuth supported by the server.
TRUSTED_PROXY = 0x1

# String used to separate namespaces from frame names.
FRAME_SEPARATOR = '__'

class HeaderMode:
  NONE = 'none'
  IGNORE = 'ignore'
  NORMAL = 'normal'
  STRICT = 'strict'

  _all = [NONE,IGNORE,NORMAL,STRICT]

class XgtError(Exception):
  """
  Base exception class from which all other xgt exceptions inherit. It is
  raised in error cases that don't have a specific xgt exception type.
  """
  def __init__(self, msg : str, trace : str = ''):
    self.msg = msg
    self.trace = trace

    if log.getEffectiveLevel() >= logging.DEBUG:
      if self.trace != '':
        log.debug(self.trace)
      else:
        log.debug(self.msg)
    Exception.__init__(self, self.msg)

class XgtNotImplemented(XgtError):
  """Raised for functionality with pending implementation."""

class XgtInternalError(XgtError):
  """
  Intended for internal server purposes only. This exception should not become
  visible to the user.
  """

class XgtIOError(XgtError):
  """An I/O problem occurred either on the client or server side."""
  def __init__(self, msg, trace : str = '', job : Optional[Job] = None):
    self._job = job
    XgtError.__init__(self, msg, trace)

  @property
  def job(self):
    """
    Job: Job associated with the load/insert operation if available. May be
    None.
    """
    return self._job

class XgtServerMemoryError(XgtError):
  """
  The server memory usage is close to or at capacity and work could be lost.
  """

class XgtConnectionError(XgtError):
  """
  The client cannot properly connect to the server. This can include a failure
  to connect due to an xgt module version error.
  """

class XgtSyntaxError(XgtError):
  """A query was provided with incorrect syntax."""

class XgtTypeError(XgtError):
  """
  An unexpected type was supplied.

  For queries, an invalid data type was used either as an entity or as a
  property. For frames, either an edge, vertex or table frames was expected
  but the wrong frame type or some other data type was provided. For
  properties, the property declaration establishes the expected data type. A
  type error is raise if the data type used is not appropriate.
  """

class XgtValueError(XgtError):
  """An invalid or unexpected value was provided."""

class XgtNameError(XgtError):
  """
  An unexpected name was provided. Typically can occur during object retrieval
  where the object name was not found.
  """

class XgtArithmeticError(XgtError):
  """An invalid arithmetic calculation was detected and cannot be handled."""

class XgtFrameDependencyError(XgtError):
  """
  The requested action will produce an invalid graph or break a valid graph.
  """

class XgtTransactionError(XgtError):
  """A Transaction was attempted but didn't complete."""

class XgtSecurityError(XgtError):
  """A security violation occurred."""

XgtErrorTypes = Union[XgtNotImplemented, XgtInternalError, XgtIOError,
                      XgtServerMemoryError, XgtConnectionError, XgtSyntaxError,
                      XgtTypeError, XgtValueError, XgtNameError,
                      XgtArithmeticError, XgtTransactionError, XgtSecurityError]

class _ContainerMap:
  """
  Maps container ids to frames.
  The user shouldn't manually construct this.

  Parameters
  ----------
  conn : Connection
    xgt Connection.
  container_dict : dictionary
    Dictionary containing keys of container ids to map.
    If empty is given, will map all frames.
  """
  def __init__(self, conn, container_dict = {}):
    self.frames = { }
    frames = conn.get_frames()

    for frame in frames:
      if not container_dict or frame._container_id in container_dict:
        self.frames[frame._container_id] = frame

  def get_frame(self, id, is_container_id = False):
    # The row_id is a 64 bit unsigned int where the 42 low bits are the
    # row position and the next higher 15 bits are the container ID.  The 7
    # high bits will never be set.
    container_id = id if is_container_id else id >> 42

    return self.frames[container_id] if container_id in self.frames else None

  def get_data(self, row_id, validation_id, include_row_labels = False):
    # The row_id is a 64 bit unsigned int where the 42 low bits are the
    # row position and the next higher 15 bits are the container ID.  The 7
    # high bits will never be set.
    container_id = row_id >> 42
    if container_id in self.frames:
      row_pos = row_id & 0x3FFFFFFFFFF
      frame = self.frames[container_id]

      return frame._get_data_python(frame.schema, offset = row_pos, length = 1,
                                    include_row_labels = include_row_labels,
                                    validation_id = validation_id,
                                    absolute_indexing = True)[0]

    return None

class RowID:
  """
  RowID represents a row ID returned from a server.
  The user shouldn't manually construct these.

  Parameters
  ----------
  container_map : _ContainerMap
    Map of container ids to frames.
  row_id_list : list
    List in the form: [X, Y] where X is the row id and Y is the commit
    id when this value was valid.
  """
  def __init__(self, container_map : _ContainerMap, row_id_list: list[int]):
    """
    Constructor for RowID. Should never be called directly by a user.
    """
    self._container_map = container_map
    self._row_id = row_id_list[0]
    self._validationid = row_id_list[1]

  def get_data(self, include_row_labels : bool = False) -> list:
    """
    Returns row data. If the frame this row points to has had deletions since
    the RowID was created, this row is considered invalid and will raise an
    exception.

    Parameters
    ----------
    include_row_labels : bool
      Indicates whether the security labels for each row should be egested
      along with the row.

    Returns
    -------
    list

    Raises
    ------
    XgtNameError
      If the frame does not exist on the server.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    ValueError
      If parameter is out of bounds or the row is no longer valid due to a
      transactional update.
    """
    return self._container_map.get_data(self._row_id, self._validationid,
                                        include_row_labels)

  @property
  def frame(self) -> Union[TableFrame, VertexFrame, EdgeFrame]:
    """
    TableFrame, VertexFrame, or EdgeFrame: The frame the RowID points into.
    """
    return self._container_map.get_frame(self._row_id)

  @property
  def position(self) -> int:
    """
    int: The row position the RowID points to.
    """
    # The row_id is a 64 bit unsigned int where the 42 low bits are the
    # row position and the next higher 15 bits are the container ID.  The 7
    # high bits will never be set.
    return self._row_id & 0x3FFFFFFFFFF

  @property
  def _validation_id(self):
    """
    int: The validation ID of the row id.
    """
    return self._validationid

  def __str__(self):
    return f"{{ ROW: {self.get_data()} }}"

  def __repr__(self):
    return str(self)

  def __eq__(self, obj):
    return self._row_id == obj._row_id and \
           self._validationid == obj._validationid

  def __lt__(self, obj):
    return self._row_id < obj._row_id

  def __hash__(self):
    return hash((self._row_id, self._validationid))

class TableRow(dict):
  """
  Represents a row from a table frame providing access to the row properties and
  the frame the row belongs to.

  The user shouldn't manually construct these.  They will be constructed by
  calls to get_data().

  The class is implemented as a dictionary with the following keys:

  - 'id': Row ID
  - 'metadata': dict containing frame metadata:
   - 'name': Table frame name
  - 'properties': dict mapping column names to values

  .. experimental:: The API of this class may change in future releases.

  """
  def __init__(self, *args, container_map : Optional[_ContainerMap] = None,
               validation_id : int, **kwargs):
    super().__init__(*args, **kwargs)
    self._container_map = container_map
    self._validation_id = validation_id

  @property
  def position(self) -> int:
    """
    int: The position of the element's row in its frame.
    """
    return self.get('id') & 0x3FFFFFFFFFF

  @property
  def properties(self) -> dict:
    """
    dict: A dictionary of the properties of the element.  The keys are the
    property names.
    """
    return self.get('properties', {})

  @property
  def frame(self) -> Union[TableFrame, VertexFrame, EdgeFrame]:
    """
    TableFrame, VertexFrame, or EdgeFrame: The frame the element belongs to.
    """
    return self._container_map.get_frame(self.get('id'))

class Edge(TableRow):
  """
  Represents an edge from an edge frame providing access to the properties and
  the frame the edge belongs to.

  The user shouldn't manually construct these.  They will be constructed by
  calls to get_data().

  The class is implemented as a dictionary with the following keys:

  - 'id': Row ID
  - 'metadata': dict containing frame metadata:
   - 'name': Edge frame name
   - 'source_name': Source vertex frame name
   - 'target_name': Target vertex frame name
   - 'source_key': Source vertex key column name
   - 'target_key': Target vertex key column name
  - 'properties': dict mapping property names to values

  .. experimental:: The API of this class may change in future releases.

  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

class Vertex(TableRow):
  """
  Represents a vertex from a vertex frame providing access to the properties and
  the frame the vertex belongs to.

  The user shouldn't manually construct these.  They will be constructed by
  calls to get_data().

  The class is implemented as a dictionary with the following keys:

  - 'id': Row ID
  - 'metadata': dict containing frame metadata:
   - 'name': Vertex frame name
   - 'key': Vertex key column name
  - 'properties': dict mapping property names to values

  .. experimental:: The API of this class may change in future releases.

  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

class _RowIDCache:
  """
  RowIDCache efficiently batches and caches row data retrieval for a set of
  RowIDs.

  - Collects RowIDs to be fetched from the server.
  - Groups RowIDs by their frame/container for efficient batch retrieval.
  - After calling build_cache(), provides fast lookup of row data by RowID.
  - Optionally converts row data into Edge, Vertex, or Table objects for
    serialization.
  - Stores frame-level metadata once per cache for later use
    (e.g., serialization).

  Usage:
    1. Append RowIDs using append().
    2. Call build_cache() to fetch and cache all row data.
    3. Retrieve row data with get().
    4. Use clear() to reset the cache.

  .. experimental:: The API of this class may change in future releases.

  """
  def __init__(self, conn : Connection):
    self._data_map = {}
    self._container_id_map = { }
    self._container_map = _ContainerMap(conn)
    self._cache_built = False
    self._conn = conn

  def append(self, row_id : RowID):
    """
    Add a RowID object to the cache for later batch retrieval.

    Parameters
    ----------
    row_id : RowID
      RowID object to be cached.
    """
    container_id = row_id._row_id >> 42
    if container_id not in self._container_id_map:
      self._container_id_map[container_id] = (row_id.frame,
                                              row_id.validation_id,
                                              [row_id._row_id])
    else:
      self._container_id_map[container_id][2].append(row_id._row_id)

  def build_cache(self, expand : str = 'none'):
    """
    Fetch and cache all row data for the appended RowIDs.

    Parameters
    ----------
    expand : str
      If not 'none', expand frame data into Edge, Vertex, or Table objects.
    """
    # Return if there are no rows.
    if self._cache_built or len(self._container_id_map) == 0:
      return

    metadata = {}
    for frame, validation_id, row_ids in self._container_id_map.values():
      # Get the data for the row IDs for this frame.
      row_positions = [x & 0x3FFFFFFFFFF for x in row_ids]
      row_data = frame._get_data(rows = row_positions,
                                 validation_id = validation_id)
      frame_name = frame.name
      # Add an entry from the row_id to its data.
      if expand != 'none':
        from .graph import (TableFrame, VertexFrame, EdgeFrame)
        if frame_name not in metadata:
          if isinstance(frame, EdgeFrame):
            metadata[frame_name] = {
              "name": frame.name,
              "source_name": frame.source_name,
              "target_name": frame.target_name,
              "source_key": frame.source_key,
              "target_key": frame.target_key,
              "schema": frame.schema
            }
          elif isinstance(frame, VertexFrame):
            metadata[frame_name] = {
              "name": frame.name,
              "key": frame.key,
              "schema": frame.schema
            }
          elif isinstance(frame, TableFrame):
            metadata[frame_name] = {
              "name": frame.name,
              "schema": frame.schema
            }
        field_names = [field[0] for field in frame.schema]
        use_metadata = expand == 'full'
        frame_type = type(frame)
        meta = metadata[frame.name] if use_metadata else None

        if frame_type is EdgeFrame:
            def make_object(row_id, row):
                args = {
                    "id": row_id,
                    "properties": dict(zip(field_names, row))
                }
                if use_metadata:
                    args["metadata"] = meta
                return Edge(
                    **args,
                    container_map=self._container_map,
                    validation_id=validation_id
                )
        elif frame_type is VertexFrame:
            def make_object(row_id, row):
                args = {
                    "id": row_id,
                    "properties": dict(zip(field_names, row))
                }
                if use_metadata:
                    args["metadata"] = meta
                return Vertex(
                    **args,
                    container_map=self._container_map,
                    validation_id=validation_id
                )
        elif frame_type is TableFrame:
            def make_object(row_id, row):
                args = {
                    "id": row_id,
                    "properties": dict(zip(field_names, row))
                }
                if use_metadata:
                    args["metadata"] = meta
                return TableRow(
                    **args,
                    container_map=self._container_map,
                    validation_id=validation_id
                )
        else:
            raise TypeError(f"Unexpected frame type: {frame_type}")

        for row_id, row in zip(row_ids, row_data):
            self._data_map[row_id] = make_object(row_id, row)
      else:
        for row_id, row in zip(row_ids, row_data):
          self._data_map[row_id] = row

    # Clear the container_id_map after building the cache to free up space.
    self._container_id_map.clear()
    # Mark the cache as built.
    self._cache_built = True

  def get(self, row_id : 'RowID'):
    """
    Retrieve cached data for a given RowID.

    Parameters
    ----------
    row_id : RowID
      The RowID to look up.

    Returns
    -------
    Data or None
      The cached data for the given RowID, or None if not found.
    """
    return self._data_map.get(row_id._row_id)

  def clear(self):
    """
    Clear all cached data and reset the cache state.
    """
    self._data_map.clear()
    self._container_id_map.clear()
    self._container_map = _ContainerMap(self._conn)
    self._cache_built = False

  def _append_by_id_tuple(self, row_id : tuple[int, int]):
    """
    Add a row_id tuple to the cache for batch retrieval.

    Parameters
    ----------
    row_id : tuple[int, int]
      Tuple of (row_id, validation_id).
    """
    container_id = row_id[0] >> 42
    if container_id not in self._container_id_map:
      self._container_id_map[container_id] = (
        self._container_map.get_frame(container_id, True),
        row_id[1],
        [row_id[0]]
      )
    else:
      self._container_id_map[container_id][2].append(row_id[0])

  def _get_by_id_tuple(self, row_id : tuple[int, int]):
    """
    Retrieve cached data for a given row_id tuple.

    Parameters
    ----------
    row_id : tuple[int, int]
      Tuple of (row_id, validation_id).

    Returns
    -------
    Data or None
      The cached data for the given row_id, or None if not found.
    """
    return None if row_id is None else self._data_map.get(row_id[0])

  def _resolve_nested_ids(self, value, depth: int = 0):
    """
    Recursively traverse a nested list structure and replace integer IDs
    with their corresponding Edge, Vertex, or Table objects.

    Parameters
    ----------
    value : list
      The nested list or value to process.
    depth : int
      The current depth of nesting. If greater than 1, the function recurses
      into sublists.

    Returns
    -------
    list
      A nested list structure with integer IDs replaced by their corresponding
      objects, or None if the input is None.
    """
    if value is None:
      return None
    elif depth > 1:
      return [self._resolve_nested_ids(list_val, depth - 1)
              if list_val != None else None for list_val in value]
    else:
      return [self._get_by_id_tuple(id_val) if id_val != None else None
              for id_val in value]

# Deprecation functions

def _deprecated(name, replacement, stacklevel = 0):
  # Display the caller of the function that calls _deprecated by default
  warnings.warn(f'{name} is deprecated and will be removed in future versions. '
                f'Use {replacement} instead.',
                DeprecationWarning, stacklevel = stacklevel + 3)

# Validation support functions

def _validated_schema_column(col):
  """
  Takes a user-supplied object representing a schema column and returns a
  valid schema column.

  Users can supply a variety of objects as valid schema columns. To simplify
  internal processing, we canonicalize these into a tuple containing name and
  type information, performing validation along the way.
  """
  if not isinstance(col, (list, tuple)):
    raise XgtTypeError('An input schema column must be of type tuple or list.')

  num_cols = len(col)
  if num_cols < 2 or num_cols > 4:
    raise XgtTypeError('An input schema column must contain between 2 and 4 '
                       'entries.')

  val_name = _validated_property_name(col[0])
  val_type = _validated_property_type(col[1])

  if val_type != "LIST":
    if num_cols > 2:
      raise XgtTypeError('A non-list input schema column must contain 2 '
                         'entries.')

    return (val_name, val_type)
  else:
    if num_cols < 3:
      raise XgtTypeError('A list input schema column must contain 3 or 4 '
                         'entries.')

    leaf_type = _validated_property_type(col[2])

    if num_cols == 3:
      return (val_name, val_type, leaf_type)
    else:
      if not isinstance(col[3], int):
        raise XgtTypeError('A list depth must be of integer type.')

      return (val_name, val_type, leaf_type, col[3])

def _validated_schema(obj, raise_on_empty_schema = True):
  """
  Takes a user-supplied object and returns a valid schema.

  Users can supply a variety of objects as valid schemas. To simplify internal
  processing, we canonicalize these into a list of tuples performing validation
  along the way. The inner tuples contain name and type information.
  """
  if not isinstance(obj, Iterable):
    raise XgtTypeError('The schema must be an Iterable with elements of '
                       'schema entries.')

  schema_returned = []
  for col in obj:
    schema_returned.append(_validated_schema_column(col))

  if raise_on_empty_schema and len(schema_returned) < 1:
    raise XgtTypeError('A schema cannot be empty.')

  return schema_returned

def _validated_columns(columns, schema):
  """
  Takes a user-supplied iterable of column indicators and returns a list of
  column positions sorted in the original schema order.

  The column indicators can be either column names from the schema or column
  positions.  Mixing is okay.
  """
  if columns is None:
    return None

  if not isinstance(columns, Iterable):
    raise XgtTypeError('columns must be an Iterable with elements of column '
                       'positions or column names.')

  fixed_columns = []
  schema_len = len(schema)
  for column in columns:
    if isinstance(column, int):
      if column < 0 or column >= schema_len:
        raise XgtValueError(f'Column position ({column}) out of bounds. '
                            f'Schema has {schema_len} columns.')

      if column not in fixed_columns:
        fixed_columns.append(column)
    elif isinstance(column, str):
      pos = -1
      for i, entry in enumerate(schema):
        if entry[0] == column:
          pos = i
          break

      if pos == -1:
        raise XgtValueError(f'Invalid column name: {column}.')

      if pos not in fixed_columns:
        fixed_columns.append(pos)
    else:
      raise XgtTypeError('Invalid column indicator. Must be column '
                         'positions or column names.')

  if isinstance(columns, set):
    fixed_columns = sorted(fixed_columns)

  return fixed_columns

def _validated_schema_columns(columns, schema):
  """
  Takes a user-supplied iterable of mixed column positions, column names, or
  schema entries and returns a valid schema.  Column positions and names must
  refer to valid columns in the schema.  Schema entries can refer to existing
  columns in the schema or new columns.
  """
  if columns is None:
    raise XgtTypeError('columns cannot be None.')

  if not isinstance(columns, Iterable):
    raise XgtTypeError('columns must be an Iterable with elements of column '
                       'positions, column names, or schema entries.')

  fixed_columns = []
  schema_len = len(schema)
  for column in columns:
    if isinstance(column, int):
      if column < 0 or column >= schema_len:
        raise XgtValueError(f'Column position ({column}) out of bounds. '
                            f'Schema has {schema_len} columns.')

      schema_col = schema[column]
    elif isinstance(column, str):
      schema_col = None
      for entry in schema:
        if entry[0] == column:
          schema_col = entry
          break

      if schema_col is None:
        raise XgtValueError(f'Invalid column name: {column}.')
    else:
      schema_col = column

    fixed_columns.append(_validated_schema_column(schema_col))

  if len(fixed_columns) < 1:
    raise XgtTypeError('A schema cannot be empty.')

  return fixed_columns

def _validated_frame_name(obj):
  """Takes a user-supplied object and returns a Unicode frame name string."""
  _assert_isstring(obj)
  name = str(obj)
  if len(name) < 1:
    raise XgtNameError('Frame names cannot be empty.')
  return name

def _validated_namespace_name(obj):
  """Takes a user-supplied object and returns a Unicode frame name string."""
  _assert_isstring(obj)
  name = str(obj)
  if len(name) < 1:
    raise XgtNameError('Namespace names cannot be empty.')
  return name

def _validated_property_name(obj):
  """Takes a user-supplied object and returns a Unicode property name string."""
  _assert_isstring(obj)
  return str(obj)

def _get_valid_property_types_to_create():
  return [BOOLEAN, INT, UINT, FLOAT, DATE, TIME, DATETIME, IPADDRESS, TEXT,
          LIST, ROWID, DURATION, WGSPOINT, CARTESIANPOINT]

def _get_valid_property_types_for_return_only():
  return ['container_id', 'job_id']

def _validated_property_type(obj):
  """Takes a user-supplied object and returns an xGT schema type."""
  _assert_isstring(obj)
  prop_type = str(obj)
  valid_prop_types = _get_valid_property_types_to_create()
  if prop_type.lower() not in valid_prop_types:
    if prop_type.lower in _get_valid_property_types_for_return_only():
      raise XgtTypeError(f'Invalid schema property type "{prop_type}". This '
                         'type cannot be used when creating a frame.')
    else:
      raise XgtTypeError(f'Invalid schema property type "{prop_type}"')
  return prop_type.upper()

def _validate_opt_level(optlevel):
  """
  Valid optimization level values are:
    - 0: No optimization.
    - 1: General optimization.
    - 2: WHERE-clause optimization.
    - 3: Degree-cycle optimization.
    - 4: Query order optimization.
  """
  if isinstance(optlevel, int):
    if optlevel not in [0, 1, 2, 3, 4]:
      raise XgtValueError(f"Invalid optlevel '{optlevel}'")
  else:
    raise XgtTypeError("optlevel must be an integer")
  return True

def _assert_noerrors(response):
  if len(response.error) > 0:
    error = response.error[0]
    try:
      error_code_name = err_proto.ErrorCodeEnum.Name(error.code)
      error_class = _code_error_map[error_code_name]
      raise error_class(error.message, error.detail)
    except XgtError:
      raise
    except Exception as ex:
      raise XgtError(f"Error detected while raising exception{str(ex)}",
                     str(ex))

def _convert_flight_server_error_into_xgt(error):
  if len(error.extra_info) >= 8 and error.extra_info[0:6] == b"ERROR:":
    try:
      error_class = _code_error_map[
          err_proto.ErrorCodeEnum.Name(int(error.extra_info[6:8]))]
      return error_class(str(error), error.extra_info)
    except:
      pass
  return XgtError(str(error))

def _assert_isstring(value):
  if not isinstance(value, str):
    raise TypeError(f"{str(value)} is not a string")

_code_error_map = {
  'GENERIC_ERROR': XgtError,
  'NOT_IMPLEMENTED': XgtNotImplemented,
  'INTERNAL_ERROR': XgtInternalError,
  'IO_ERROR': XgtIOError,
  'SERVER_MEMORY_ERROR': XgtServerMemoryError,
  'CONNECTION_ERROR': XgtConnectionError,
  'SYNTAX_ERROR': XgtSyntaxError,
  'TYPE_ERROR': XgtTypeError,
  'VALUE_ERROR': XgtValueError,
  'NAME_ERROR': XgtNameError,
  'ARITHMETIC_ERROR': XgtArithmeticError,
  'FRAME_DEPENDENCY_ERROR': XgtFrameDependencyError,
  'TRANSACTION_ERROR': XgtTransactionError,
  'SECURITY_ERROR': XgtSecurityError,
}

def _verify_offset_length(offset, length):
  max_uint64 = sys.maxsize * 2 + 1

  if not isinstance(offset, (int, str)):
    raise XgtTypeError("offset must be an integer.")

  if isinstance(offset, str):
    offset = int(offset)

  if offset < 0:
    raise XgtValueError("offset must be a non-negative integer.")
  if offset > max_uint64:
    raise XgtValueError(f"offset must be < {max_uint64}")

  if length is not None:
    if not isinstance(length, (int, str)):
      raise XgtTypeError("length must be an integer.")

    if isinstance(length, str):
      length = int(length)

    if length < 0:
      raise XgtValueError("length must be a non-negative integer.")
    if length > max_uint64:
      raise XgtValueError(f"length must be < {max_uint64}")

  return offset, length

def _verify_row_positions(rows, frame_or_job):
  if rows is None:
    return

  if not isinstance(rows, Iterable):
    raise XgtTypeError('rows must be an Iterable with elements of integer row '
                       'positions.')

  # Get the number of rows.  Handle that a job could return None.
  num_rows = frame_or_job.num_rows
  if num_rows is None:
    num_rows = 0

  if num_rows == 0:
    if rows:
      raise XgtValueError('Cannot specify rows for a frame with no rows.')
    return

  for row in rows:
    if not isinstance(row, int):
      raise XgtTypeError('Invalid row indicator. Must be integer row position.')

    if row < 0 or row >= num_rows:
      raise XgtValueError(f'Row position {row} out of bounds. Must be in '
                          f'range 0 to {num_rows - 1}.')

def _create_flight_ticket(frame_or_job, name, offset, length, rows = None,
                          columns = None, include_row_labels = False,
                          row_label_column_header = None,
                          order = True, date_as_string = False,
                          job_id = None, validation_id = None,
                          duration_as_interval = False,
                          row_filter = None, absolute_indexing = False,
                          **kwargs):
  if rows is not None and (offset != 0 or length is not None):
    raise XgtValueError('Cannot give rows when giving either offset or length.')

  offset, length = _verify_offset_length(offset, length)
  _verify_row_positions(rows, frame_or_job)

  ticket = f'`{name}`'

  if offset != 0:
    ticket += f".offset={offset}"
  if length is not None:
    ticket += f".length={length}"
  if rows is not None:
    ticket += ".rows=" + ','.join([str(x) for x in rows])
  if columns is not None:
    ticket += ".columns=" + ','.join([str(x) for x in columns])
  if order:
    ticket += ".order=True"
  if date_as_string:
    ticket += ".dates_as_strings=True"
  if include_row_labels:
    ticket += ".egest_row_labels=True"
  if row_label_column_header is not None:
    ticket += ".label_column_header=" + row_label_column_header
  if validation_id is not None:
    ticket += f".validation_id={str(validation_id)}"
  if duration_as_interval:
    ticket += ".duration_as_interval=True"
  if absolute_indexing:
    ticket += ".absolute_indexing=True"

  if row_filter is not None:
    row_filter_value = f'.row_filter="{row_filter}"'
    ticket += row_filter_value

  for k,v in kwargs.items():
    if k == "record_history":
      ticket += f".record_history={str(v)}"
    else:
      raise ValueError(f"kwarg {k} not supported.")
  if len(kwargs) == 0:
    # For get_data
    ticket += ".record_history=false"

  if job_id is not None:
    if isinstance(job_id, str):
      job_id = int(job_id)
    elif not isinstance(job_id, int):
      raise ValueError("job ID must be an int.")
    ticket += f".job_id={job_id}"

  return ticket

def _cache_row_id_list(cache, value, depth = 0):
  if value is None:
    return
  elif depth > 1:
    for list_val in value:
      _cache_row_id_list(cache, list_val, depth - 1)
  else:
    for id_val in value:
      if id_val is not None:
        cache._append_by_id_tuple(id_val)

def _convert_row_id_list(container_map, value, depth = 0):
  if value is None:
    return None
  elif depth > 1:
    return [_convert_row_id_list(container_map, list_val, depth - 1)
            if list_val != None else None for list_val in value]
  else:
    return [RowID(container_map, id_val) if id_val != None else None
            for id_val in value]

def _convert_row_id_list_pandas(container_map, value, depth = 0):
  import numpy as np

  if value is None:
    return None

  # Pyarrow's conversion function to_pandas() converts nested pyarrow lists to
  # nested 1D numpy arrays, not a single multi-dimensional numpy array. To get
  # a numpy array of separate numpy arrays, the array has to be created with
  # object type and the correct size first and other numpy arrays copied into
  # the positions.  Otherwise, a multidimensional numpy array will be created.
  v = np.ndarray(shape=(len(value),), dtype = 'object')

  if depth > 1:
    for i, entry in enumerate(value):
      v[i] = _convert_row_id_list_pandas(container_map, entry, depth - 1) \
             if entry is not None else None
  else:
    for i, entry in enumerate(value):
      v[i] = RowID(container_map, entry) if entry is not None else None

  return v

def _convert_ip_address_list(value, depth = 1):
  if value is None:
    return None
  elif depth > 1:
    return [_convert_ip_address_list(list_val, depth - 1)
            if list_val is not None else None for list_val in value]
  else:
    return [ipaddress.ip_address(id_val) if id_val is not None else None
            for id_val in value]

def _convert_ip_address_list_pandas(value, depth = 1):
  import numpy as np

  if value is None:
    return None

  # Pyarrow's conversion function to_pandas() converts nested pyarrow lists to
  # nested 1D numpy arrays, not a single multi-dimensional numpy array. To get
  # a numpy array of separate numpy arrays, the array has to be created with
  # object type and the correct size first and other numpy arrays copied into
  # the positions.  Otherwise, a multidimensional numpy array will be created.
  v = np.ndarray(shape=(len(value),), dtype = 'object')

  if depth > 1:
    for i, entry in enumerate(value):
      v[i] = _convert_ip_address_list_pandas(entry, depth - 1) \
             if entry is not None else None
  else:
    for i, entry in enumerate(value):
      v[i] = ipaddress.ip_address(entry) if entry is not None else None

  return v

def _process_schema(conn, schema, arrow_table, expand):
  container_map = None
  row_cache = None
  column_row_id_map = {}

  for pos, entry in enumerate(schema):
    if entry[1] == ROWID or (entry[1] == LIST and entry[2] == ROWID):
      if expand != 'none':
        if row_cache is None:
          row_cache = _RowIDCache(conn)
        column_data = arrow_table.column(pos).to_pylist()
        column_row_id_map[pos] = column_data
        if entry[1] == ROWID:
          for row_id in column_data:
            if row_id is not None:
              row_cache._append_by_id_tuple(row_id)
        elif len(entry) == 3:
          for row_list in column_data:
            _cache_row_id_list(row_cache, row_list, 1)
        else:
          length = entry[3]
          for row_list in column_data:
            _cache_row_id_list(row_cache, row_list, length)
      else:
        container_map = _ContainerMap(conn)
        break

  if expand != 'none' and row_cache is not None:
    row_cache.build_cache(expand = expand)

  return container_map, row_cache, column_row_id_map

# Creates a list of conversion functions from the schema.
# Currently has conversions for row id and paths(row id lists).
def _schema_row_conversion(schema, conn, arrow_table, expand):
  container_map, row_cache, column_row_id_map = _process_schema(
    conn, schema, arrow_table, expand
  )

  conversion_funcs = []
  for entry in schema:
    if entry[1] == IPADDRESS:
      def closure(value):
        return ipaddress.ip_address(value) if value is not None else None
      conversion_funcs.append(closure)
    elif(entry[1] == LIST and entry[2] == IPADDRESS):
      if len(entry) == 3:
        def closure(value):
          return _convert_ip_address_list(value)
        conversion_funcs.append(closure)
      else:
        length = entry[3]
        def closure(value):
          return _convert_ip_address_list(value, length)
        conversion_funcs.append(closure)
    elif entry[1] == ROWID and expand != 'none':
      def closure(value):
        return row_cache._get_by_id_tuple(value)
      conversion_funcs.append(closure)
    elif(entry[1] == LIST and entry[2] == ROWID and expand != 'none'):
      if len(entry) == 3:
        def closure(value):
          return row_cache._resolve_nested_ids(value, 1)
        conversion_funcs.append(closure)
      else:
        length = entry[3]
        def closure(value):
          return row_cache._resolve_nested_ids(value, length)
        conversion_funcs.append(closure)
    elif entry[1] == ROWID:
      def closure(value):
        return RowID(container_map, value) if value != None else None
      conversion_funcs.append(closure)
    elif(entry[1] == LIST and entry[2] == ROWID):
      if len(entry) == 3:
        def closure(value):
          return _convert_row_id_list(container_map, value, 1)
        conversion_funcs.append(closure)
      else:
        length = entry[3]
        def closure(value):
          return _convert_row_id_list(container_map, value, length)
        conversion_funcs.append(closure)
    else:
      conversion_funcs.append(None)

  return conversion_funcs, column_row_id_map

def _get_data_python_from_table(arrow_table, schema, conn, expand = 'none'):
  if arrow_table is None:
    return None

  # Get functions used to convert columns coming from the server.
  # Currently, this provides functions for converting paths(lists of row ids)
  # and row ids into the RowID class.
  conversion_funcs, column_row_id_map = _schema_row_conversion(
    schema, conn, arrow_table, expand
  )

  # List comprehension here is simpler, but has slow performance due to the
  # access pattern being bad for the cache hits.
  return_list = [None] * arrow_table.num_rows
  if arrow_table.num_columns > len(conversion_funcs):
    conversion_funcs += [None] * (arrow_table.num_columns -
                                  len(conversion_funcs))
  for i in range(arrow_table.num_rows):
    return_list[i] = []
  for i, x in enumerate(arrow_table):
    if conversion_funcs[i] == None:
      for j, y in enumerate(x):
        return_list[j].append(y.as_py())
    elif i in column_row_id_map:
      column = column_row_id_map[i]
      for j in range(len(x)):
        return_list[j].append(conversion_funcs[i](column[j]))
    else:
      for j, y in enumerate(x):
        return_list[j].append(conversion_funcs[i](y.as_py()))

  return return_list

def _get_data_pandas_from_table(arrow_table, schema, conn, expand = 'none'):
  import pandas as pd

  if arrow_table is None:
    return None

  pandas_dict = {}
  container_map = None
  container_map, row_cache, column_row_id_map = _process_schema(conn,
      schema, arrow_table, expand)
  schema_len = len(schema)
  for i, (name, col) in enumerate(zip(arrow_table.column_names, arrow_table)):
    if i < schema_len and schema[i][1] == IPADDRESS:
      pandas_dict[name] = \
          pd.Series([None if x.as_py() is None else ipaddress.ip_address(x)
                     for x in col], dtype = 'object')
    elif i < schema_len and schema[i][1] == ROWID and expand != 'none':
      column = column_row_id_map[i]
      pandas_dict[name] = \
          pd.Series([row_cache._get_by_id_tuple(column[j])
                     for j in range(len(column))], dtype = 'object')
    elif i < schema_len and schema[i][1] == ROWID:
      pandas_dict[name] = \
          pd.Series([None if x.as_py() is None else RowID(container_map,
                                                          x.as_py())
                     for x in col], dtype = 'object')
    elif i < schema_len and schema[i][1] == LIST and schema[i][2] == IPADDRESS:
      depth = 1 if len(schema[i]) == 3 else schema[i][3]
      pandas_dict[name] = pd.Series([_convert_ip_address_list_pandas(x.as_py(),
                                                                     depth)
                                     for x in col])
    elif (i < schema_len and schema[i][1] == LIST and
          schema[i][2] == ROWID and expand != 'none'):
      depth = 1 if len(schema[i]) == 3 else schema[i][3]
      column = column_row_id_map[i]
      pandas_dict[name] = \
          pd.Series([row_cache._resolve_nested_ids(column[j], depth)
                     for j in range(len(column))], dtype = 'object')
    elif i < schema_len and schema[i][1] == LIST and schema[i][2] == ROWID:
      depth = 1 if len(schema[i]) == 3 else schema[i][3]
      pandas_dict[name] = \
          pd.Series([None if x.as_py() is None else
                     _convert_row_id_list_pandas(container_map, x.as_py(),
                                                 depth)
                     for x in col], dtype = 'object')
    else:
      pandas_dict[name] = col.to_pandas()

  return pd.DataFrame(pandas_dict)

def _get_data_arrow(conn, ticket):
  try:
    res_table = conn.arrow_conn.do_get(pyarrow.flight.Ticket(ticket)).read_all()
    return res_table
  except pyarrow._flight.FlightServerError as err:
    raise _convert_flight_server_error_into_xgt(err) from err
  except pyarrow._flight.FlightUnavailableError as err:
    raise XgtConnectionError(str(err)) from err

def _get_data_python(conn, ticket, schema, expand = 'none'):
  res_table = _get_data_arrow(conn, ticket)
  return _get_data_python_from_table(res_table, schema, conn, expand)

def _get_data_pandas(conn, ticket, schema, expand = 'none'):
  res_table = _get_data_arrow(conn, ticket)
  return _get_data_pandas_from_table(res_table, schema, conn, expand)

# Helper functions for low code.

# Convert the pyarrow type to an xgt type.
def _pyarrow_type_to_xgt_type(pyarrow_type, depth = 0):
  if pyarrow.types.is_boolean(pyarrow_type):
    return (BOOLEAN, depth)
  elif (pyarrow.types.is_timestamp(pyarrow_type) or
        pyarrow.types.is_date64(pyarrow_type)):
    return (DATETIME, depth)
  elif pyarrow.types.is_date(pyarrow_type):
    return (DATE, depth)
  elif pyarrow.types.is_time(pyarrow_type):
    return (TIME, depth)
  elif pyarrow.types.is_temporal(pyarrow_type):
    return (DURATION, depth)
  elif pyarrow.types.is_signed_integer(pyarrow_type):
    return (INT, depth)
  elif pyarrow.types.is_unsigned_integer(pyarrow_type):
    return (UINT, depth)
  elif (pyarrow.types.is_float32(pyarrow_type) or
        pyarrow.types.is_float64(pyarrow_type) or
        pyarrow.types.is_decimal(pyarrow_type)):
    return (FLOAT, depth)
  elif (pyarrow.types.is_string(pyarrow_type) or
        pyarrow.types.is_large_string(pyarrow_type)):
    return (TEXT, depth)
  elif (pyarrow.types.is_list(pyarrow_type) or
        pyarrow.types.is_large_list(pyarrow_type)):
    return _pyarrow_type_to_xgt_type(pyarrow_type.value_type, depth + 1)
  else:
    raise XgtTypeError(
        f"Cannot convert pyarrow type {str(pyarrow_type)} to xGT type.")

def _infer_xgt_schema_from_pyarrow_schema(pyarrow_schema):
  xgt_schema = []
  for c in pyarrow_schema:
    xgt_type = _pyarrow_type_to_xgt_type(c.type)
    if xgt_type[1] == 0:
      xgt_schema.append([c.name, xgt_type[0]])
    else:
      xgt_schema.append([c.name, LIST, xgt_type[0], xgt_type[1]])
  return xgt_schema

# Get the column in the schema by name or position.
def _find_key_in_schema(key, schema):
  if isinstance(key, str):
    found_key = False
    for elem in schema:
      if elem[0] == key:
        found_key = True
        break
    if not found_key:
      raise XgtNameError(
          f"The key {str(key)} not found in schema: {str(schema)}")
    return key
  elif isinstance(key, int):
    if key >= len(schema) or key < 0:
      raise XgtError(f"Could not locate key {str(key)} in schema with "
                     f"{len(schema)} entries.")
    return schema[key][0]

# Modify an xgt schema based on a frame column name to data column name
# mapping. The key names of this map will become the column names of the
# new schema. The values of the map correspond to the columns of the
# initial schema.
def _apply_mapping_to_schema(initial_schema, frame_to_data_column_mapping):
  def find_data_col_name(data_col):
    if isinstance(data_col, str):
      return data_col
    elif isinstance(data_col, int):
      if data_col >= len(initial_schema) or data_col < 0:
        err = ("Error creating the schema. The column mapping refers to "
               f"data column position {data_col}, but only "
               f"{len(initial_schema)} columns were found in the data.")
        raise XgtValueError(err)

      return initial_schema[data_col][0]

  data_col_name_to_type = { elem[0] : elem[1] for elem in initial_schema }

  schema = []
  for frame_col, data_col in frame_to_data_column_mapping.items():
    data_type = data_col_name_to_type[find_data_col_name(data_col)]
    schema.append([frame_col, data_type])

  return schema

def _remove_label_columns_from_schema(initial_schema, row_label_columns):
  def find_data_col_name(data_col):
    if isinstance(data_col, str):
      return data_col
    elif isinstance(data_col, int):
      if data_col >= len(initial_schema) or data_col < 0:
        err = ("Error creating the schema. The row_label_columns parameter "
               f"refers to data column position {data_col}, but only "
               f"{len(initial_schema)} columns were found in the data.")
        raise XgtValueError(err)
      return initial_schema[data_col][0]

  data_col_name_to_type = { elem[0] : elem[1] for elem in initial_schema }

  label_columns = set([find_data_col_name(col) for col in row_label_columns])

  return [col for col in initial_schema if col[0] not in label_columns]

def _generate_proto_schema_from_xgt_schema(request, schema):
  for col in schema:
    prop = sch_proto.Property()
    prop.name = col[0]
    prop.data_type = sch_proto.UvalTypeEnum.Value(col[1])

    if (prop.data_type == sch_proto.UvalTypeEnum.Value('LIST')):
      prop.leaf_type = sch_proto.UvalTypeEnum.Value(col[2])

      if (len(col) > 3):
        if col[3] > 1:
          prop.list_depth = col[3] - 1
        elif col[3] == 1:
          prop.list_depth = 0
        else:
          raise XgtTypeError("A list cannot have a depth less than one.")
      else:
        prop.list_depth = 0

    request.schema.property.extend([prop])

# Compares two dot-separated number versions like "2.10.8".
# Note: This function does not support versions with alpha/beta characters
# or any non-integer segments and will return None for such inputs.
# An example failure case would be: "2.10.8a"
def _compare_versions(version1, version2, op=operator.eq):
  try:
    v1 = list(map(int, version1.split('.')))
    v2 = list(map(int, version2.split('.')))
    return op(v1, v2)
  except:
    return None

def _validate_column_mapping_in_ingest(column_mapping):
  error_msg = ('The data type of "column_mapping" is incorrect. '
               'Expects a dictionary with string keys and string '
               'or integer values.')
  if column_mapping is not None:
    if not isinstance(column_mapping, Mapping):
      raise TypeError(error_msg)
    for frame_col, file_col in column_mapping.items():
      if not isinstance(frame_col, str) or not isinstance(file_col, (str, int)):
        raise TypeError(error_msg)

def _set_column_mapping_in_ingest_request(column_mapping):
  if column_mapping is not None:
    return_value = data_proto.ColumnMapping()
    return_value.has_mapping = True
    for frame_col, file_col in column_mapping.items():
      if isinstance(file_col, str):
        name_mapping = data_proto.FrameColumnToSourceName()
        name_mapping.frame_column_name = _validated_property_name(frame_col)
        name_mapping.file_column_name = file_col
        return_value.frame_column_to_source_name.extend(
            [name_mapping])
      elif isinstance(file_col, int):
        idx_mapping = data_proto.FrameColumnToSourceIdx()
        idx_mapping.frame_column_name = _validated_property_name(frame_col)
        idx_mapping.file_column_idx = file_col
        return_value.frame_column_to_source_idx.extend([idx_mapping])
      else:
        raise TypeError('The data type of "column_mapping" is incorrect. '
                        'Expects a dictionary with string keys and string '
                        'or integer values.')
  return return_value

def _validate_client_path(one_path):
  if one_path.endswith('.gz') or one_path.endswith('.bz2'):
    raise XgtNotImplemented(f'Loading/Saving compressed files from a local '
                            f'filesystem is not supported: {one_path}')

def _group_paths(paths, for_ingest):
  client_prefix = 'xgt://'
  server_prefix = 'xgtd://'
  url_prefixes = ['s3://', 'https://', 'http://', 'ftps://', 'ftp://']
  client_paths = []
  server_paths = []
  url_paths = []
  if isinstance(paths, str):
    paths = [paths]
  elif not isinstance(paths, (list, tuple)):
    return client_paths, server_paths, url_paths
  for one_path in paths:
    one_path_normalized = one_path.lower()
    if one_path == "":
      raise ValueError('one or more "paths" are empty')
    if one_path_normalized.startswith(client_prefix):
      _validate_client_path(one_path)
      client_paths.append(one_path[len(client_prefix):])
    elif one_path_normalized.startswith(server_prefix):
      server_paths.append(one_path[len(server_prefix):])
    elif any(map(lambda p: one_path_normalized.startswith(p), url_prefixes)):
      for url_prefix in url_prefixes:
        if one_path_normalized.startswith(url_prefix):
          url_paths.append(one_path)
          break
    else:
      if '://' in one_path:
        msg = f'Unsupported URL protocol in path "{one_path}".'
        raise XgtNotImplemented(msg)
      _validate_client_path(one_path)
      client_paths.append(one_path)
  return client_paths, server_paths, url_paths

def _split_local_paths(paths):
  parquet_paths = []
  other_paths = []
  for path in paths:
    extension = os.path.splitext(path)[-1]
    if extension == ".parquet":
      parquet_paths.append(path)
    else:
      other_paths.append(path)

  return parquet_paths, other_paths

def _convert_header_mode(header_mode, request):
  if header_mode == HeaderMode.IGNORE:
    request.header_mode = data_proto.IGNORE_HEADERS
  elif header_mode == HeaderMode.NORMAL:
    request.header_mode = data_proto.NORMAL
  elif header_mode == HeaderMode.STRICT:
    request.header_mode = data_proto.STRICT
  else:
    request.header_mode = data_proto.NONE

def _process_protocol_version(server_protocol, client_protocol):
  capabilities = 0
  if server_protocol is not None:
    if server_protocol >= client_protocol:
      capabilities |= TRUSTED_PROXY

  return capabilities

def _process_graph_members(graph_members):
  from .graph import (VertexFrame, EdgeFrame)

  if isinstance(graph_members, dict):
    for alias, frame in graph_members.items():
      if not isinstance(alias, str):
        raise XgtTypeError('Alias of a graph member frame must be a string: ' +
                           str(alias))
      if isinstance(frame, str):
        graph_members[alias] = _validated_frame_name(frame)
      elif isinstance(frame, VertexFrame) or isinstance(frame, EdgeFrame):
        graph_members[alias] = frame.name
      else:
        raise XgtTypeError('Expected string or valid VertexFrame or EdgeFrame '+
                           ' instance: ' + str(frame))
  elif isinstance(graph_members, set):
    validated_members = []
    for frame in graph_members:
      if isinstance(frame, str):
        validated_members.append(_validated_frame_name(frame))
      elif isinstance(frame, VertexFrame) or isinstance(frame, EdgeFrame):
        validated_members.append(frame.name)
      else:
        raise XgtTypeError('Expected string or valid VertexFrame or EdgeFrame '+
                           ' instance: ' + str(frame))
    graph_members = { frame : frame for frame in validated_members }
  else:
    raise XgtTypeError('Members of a graph must be a dictionary or set')

  return graph_members

def _is_qualified_name(name):
  if not isinstance(name, str):
    return False

  pos = name.find(FRAME_SEPARATOR)

  if pos < 0:
    return False

  nspace = name[0:pos]
  frame = name[pos + len(FRAME_SEPARATOR):]

  if FRAME_SEPARATOR in frame:
    return False

  return True

def _parse_qualified_name(name):
  if not isinstance(name, str):
    raise XgtTypeError('Expected a string got: {name!r}')

  pos = name.find(FRAME_SEPARATOR)

  if pos < 0:
    raise XgtValueError('Could not find namespace separator')

  nspace = name[0:pos]
  frame = name[pos + len(FRAME_SEPARATOR):]

  if FRAME_SEPARATOR in frame:
    raise XgtValueError('Invalid frame name')

  return (nspace, frame)
