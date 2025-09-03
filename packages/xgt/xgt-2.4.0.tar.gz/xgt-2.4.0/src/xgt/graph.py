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

import decimal
import isodate
import glob
import math
import operator
import os.path
import struct
import sys
import traceback
import pyarrow
import pyarrow.flight

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, date, time, timedelta
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Optional, Union, TYPE_CHECKING

from . import DataService_pb2 as data_proto
from . import DataService_pb2_grpc as data_grpc
from . import GraphTypesService_pb2 as graph_proto
from . import SchemaMessages_pb2 as sch_proto
from .common import (_assert_isstring, _assert_noerrors,
                     _get_valid_property_types_for_return_only,
                     _get_valid_property_types_to_create,
                     _validated_property_name,
                     _validated_schema, _validated_schema_column,
                     _validated_schema_columns, _validated_columns,
                     _convert_flight_server_error_into_xgt,
                     _create_flight_ticket, _get_data_python, _get_data_pandas,
                     _get_data_arrow, _infer_xgt_schema_from_pyarrow_schema,
                     _generate_proto_schema_from_xgt_schema,
                     XgtNotImplemented, XgtConnectionError,
                     XgtIOError, XgtValueError, XgtInternalError, XgtTypeError,
                     MAX_PACKET_SIZE, DEFAULT_CHUNK_SIZE, BOOLEAN, INT, UINT,
                     FLOAT, DATE, TIME, DATETIME, IPADDRESS, TEXT, DURATION,
                     ROWID, LIST, WGSPOINT, CARTESIANPOINT, FRAME_SEPARATOR,
                     _deprecated, _compare_versions,
                     _validate_column_mapping_in_ingest,
                     _set_column_mapping_in_ingest_request, _group_paths,
                     _split_local_paths, _convert_header_mode, HeaderMode,
                     _process_graph_members, _is_qualified_name,
                     _parse_qualified_name)
from .job import Job

if TYPE_CHECKING:
  try:
    import pandas
  except ImportError:
    pass

# Cached values for stuff that changed in version pandas 2.1.0
# that gives warnings.
_cached_pandas_using_less_than_2_1_0 = None
_cached_pandas_map_function = None
_cached_pandas_array_type = None

def _validate_row_level_labels_for_ingest(row_labels,
                                          row_label_columns = None):
  if row_labels is not None and row_label_columns is not None:
    raise ValueError('Only one of row_labels and row_label_columns must ' +
                     'be passed.')
  if ((row_labels is not None and not isinstance(row_labels, Iterable)) or
      isinstance(row_labels, str)):
    raise TypeError('row_labels must be an Iterable of string labels.')
  if ((row_label_columns is not None and
       not isinstance(row_label_columns, Iterable)) or
      isinstance(row_label_columns, str)):
    raise TypeError('row_label_columns must be an Iterable of string labels ' +
                    'or column indices.')

def _get_processed_row_level_label_columns(row_label_columns,
                                           header_mode = HeaderMode.NONE):
  if row_label_columns is None:
    return None
  elif header_mode == HeaderMode.NONE or header_mode == HeaderMode.IGNORE:
    return [int(col) for col in row_label_columns]
  elif header_mode == HeaderMode.NORMAL or header_mode == HeaderMode.STRICT:
    for col in row_label_columns:
      _assert_isstring(col)
    return row_label_columns

def _row_level_labels_helper(request, row_labels, row_label_columns,
                             source_vertex_row_labels, target_vertex_row_labels,
                             header_mode):
  if row_labels is not None:
    if len(row_labels) == 0:
      row_labels.append("")
    for label in row_labels:
      request.row_labels.labels.extend([label])
  if source_vertex_row_labels is not None:
    for label in source_vertex_row_labels:
      request.row_labels.implicit_source_vertex_labels.extend([label])
  if target_vertex_row_labels is not None:
    for label in target_vertex_row_labels:
      request.row_labels.implicit_target_vertex_labels.extend([label])
  if row_label_columns is not None:
    if header_mode == HeaderMode.NONE or header_mode == HeaderMode.IGNORE:
      for col in row_label_columns:
        request.row_labels.label_column_indices.extend([col])
    elif header_mode == HeaderMode.NORMAL or header_mode == HeaderMode.STRICT:
      for col in row_label_columns:
        request.row_labels.label_column_names.extend([col])
  return request

def _get_pandas_array_types():
  import pandas as pd

  # Pull in cached stuff.
  global _cached_pandas_using_less_than_2_1_0
  global _cached_pandas_array_type
  global _cached_pandas_map_function

  # Check if we cached the type and map function that differs for pandas'
  # versions only if we haven't cached.
  if _cached_pandas_using_less_than_2_1_0 is None:
    result = _compare_versions(pd.__version__, "2.1.0", operator.lt)
    # On failure just assume we are < 2.1.0. This might be able to happen
    # if people are using a beta or alpha pandas?, but for now
    # the old function is still in pandas and will just give a warning.
    _cached_pandas_using_less_than_2_1_0 = result is None or result is True
    # Cache the version specific function and types that throw warnings.
    if _cached_pandas_using_less_than_2_1_0:
      _cached_pandas_array_type = pd.arrays.PandasArray
      _cached_pandas_map_function = pd.DataFrame.applymap
    else:
      _cached_pandas_array_type = pd.arrays.NumpyExtensionArray
      _cached_pandas_map_function = pd.DataFrame.map

  # These are the different types of arrays created with pandas.array().
  return (_cached_pandas_array_type, pd.arrays.BooleanArray,
          pd.arrays.IntegerArray,
          pd.arrays.FloatingArray, pd.arrays.StringArray,
          pd.arrays.DatetimeArray, pd.arrays.TimedeltaArray)

def _get_xgt_infer_type(column, infer_type):
  import numpy as np

  pandas_array_types = _get_pandas_array_types()

  if infer_type == "mixed":
    # Check if first non-null value is a numpy or pandas array.
    # Just assume everything is a list in this case.
    for _, val in column.items():
      if isinstance(val, type(None)):
        continue

      if isinstance(val, np.ndarray):
        return "ndarray", val.dtype.name
      elif isinstance(val, pandas_array_types):
        return "pandasarray", val.dtype
      else:
        return "mixed", None
  elif infer_type == "mixed-integer":
    return "mixed", None

  return "single", None

def _infer_xgt_type_from_pandas_column(table, col):
  import pandas as pd
  import numpy as np

  def convert_scalar_type(pandas_type):
    if pandas_type == 'string':
      return TEXT
    if pandas_type == 'floating':
      return FLOAT
    if pandas_type == 'integer':
      return INT
    if pandas_type == 'boolean':
      return BOOLEAN
    if pandas_type == 'datetime64' or pandas_type == 'datetime':
      return DATETIME
    if pandas_type == 'date':
      return DATE
    if pandas_type == 'timedelta64' or pandas_type == 'timedelta':
      return DURATION
    if pandas_type == 'time':
      return TIME

    return None

  def find_array_element_type(array, depth):
    for i in range(array.size):
      elem = array.item(i)
      if elem is not None:
        if isinstance(elem, (IPv4Address, IPv6Address)):
          return (IPADDRESS, depth)

      if isinstance(elem, np.ndarray):
        return find_array_element_type(elem, depth + 1)

      elem_type = convert_scalar_type(pd.api.types.infer_dtype(pd.Series(elem)))
      if elem_type is not None:
        return (elem_type, depth)

    raise XgtTypeError(f'Type not found for array element: {type(elem)}')

  infer_type = pd.api.types.infer_dtype(table[col])
  xgt_infer_type, xgt_infer_subtype = _get_xgt_infer_type(table[col],
                                                          infer_type)

  # For columns where datetimes and dates are mixed, the inferred dtype
  # will be date.  So we do additional checks.
  has_mixed_dates = False
  if infer_type == "date":
    check_mixed_dates = (_cached_pandas_map_function(table[[col]], type) !=
                         table[[col]].iloc[0].apply(type)).any(axis = 1)
    has_mixed_dates = len(table[check_mixed_dates]) > 0

  if has_mixed_dates or xgt_infer_type == 'mixed':
    has_ips = _cached_pandas_map_function(
      table[[col]],
      lambda x : isinstance(x, (IPv4Address, IPv6Address))).all(axis = 1)
    if has_ips.all():
      return (IPADDRESS, 0)
    raise XgtTypeError('Mixed type columns not supported for xGT '
                       'schema inference')

  scalar_type = convert_scalar_type(infer_type)
  if scalar_type is not None:
    return (scalar_type, 0)
  if xgt_infer_type == 'ndarray':
    scalar_type, depth = find_array_element_type(table[col].to_numpy(), 0)
    if scalar_type is not None:
      return (LIST, scalar_type, depth)
  if xgt_infer_type == 'pandasarray' and xgt_infer_subtype != 'object':
    return (LIST, convert_scalar_type(xgt_infer_subtype), 1)
  if xgt_infer_type == 'pandasarray' and xgt_infer_subtype == 'object':
    for i, entry in enumerate(table[col]):
      if (entry is not None and isinstance(entry, (IPv4Address, IPv6Address))):
        return (LIST, IPADDRESS, 1)
      elif (entry is not None):
        return (LIST, WGSPOINT, 1)

  raise XgtTypeError('Pandas type not supported')

def _infer_xgt_schema_from_pandas_data(data):
  columns = data.columns
  xgt_schema = [
    (col,) + _infer_xgt_type_from_pandas_column(data, col) for col in columns
  ]
  return xgt_schema

def _infer_xgt_schema_from_pyarrow_table(table):
  return _infer_xgt_schema_from_pyarrow_schema(table.schema)

def _infer_xgt_schema_from_python_data(data):
  if len(data) <= 0:
    return [ ]

  def get_scalar_type(elem):
    if isinstance(elem, bool):
      return (BOOLEAN, 0)
    if isinstance(elem, int):
      return (INT, 0)
    if isinstance(elem, float):
      return (FLOAT, 0)
    if isinstance(elem, decimal.Decimal):
      return (FLOAT, 0)
    if isinstance(elem, str):
      return (TEXT, 0)
    if isinstance(elem, date):
      return (DATE, 0)
    if isinstance(elem, time):
      return (TIME, 0)
    if isinstance(elem, datetime):
      return (DATETIME, 0)
    if isinstance(elem, timedelta):
      return (DURATION, 0)
    if isinstance(elem, (IPv4Address, IPv6Address)):
      return (IPADDRESS, 0)

    raise XgtTypeError(f'Unsupported Python type for xGT data: {type(elem)}')

  def get_list_type(elem, depth):
    if isinstance(elem, list):
      if len(elem) > 0:
        return get_list_type(elem[0], depth + 1)
      else:
        raise XgtValueError('Cannot find the base type of an empty list')
    else:
      elem_type = get_scalar_type(elem)
      return (LIST, elem_type[0], depth)

  def get_schema_for_row(row):
    schema = [ ]
    for i, col in enumerate(row):
      if isinstance(col, list):
        schema.append((f'f{i}',) + get_list_type(col, 0))
      else:
        schema.append((f'f{i}',) + get_scalar_type(col))

    return schema

  base_schema = get_schema_for_row(data[0])

  for i in range(1, len(data)):
    schema = get_schema_for_row(data[i])
    if schema != base_schema:
      raise XgtTypeError('Mixed type columns not supported for xGT schema '
                         f'inference, expected schema {base_schema} , row {i}'
                         f' schema {schema}')

  return base_schema

# -----------------------------------------------------------------------------

class TableFrame(object):
  """
  A TableFrame represent a table held on the xGT server.  It can be used to
  retrieve information about the frame and the row properties.  A TableFrame
  should not be instantiated directly by the user.  Instead it is created by the
  method `Connection.create_table_frame()` or a MATCH query.

  Methods that return this object: `Connection.get_frame()`,
  `Connection.get_frames()` and `Connection.create_table_frame()`.

  Each row in a TableFrame shares the same properties, described in the frame's
  schema.

  Parameters
  ----------
  conn : Connection
    An open connection to an xGT server.
  name : str
    Fully qualified name of the frame, including the namespace.
  schema : Iterable[list[Any] | tuple[Any]]
    The schema defining the property names and types.  Each row in the frame
    will have these properties.  Given as a list of lists associating property
    names with xGT data types.
  container_id : int
    The ID of the frame's container on the server.
  commit_id : int
    The ID of the last commit to the frame.

  Examples
  --------
  >>> import xgt
  >>> conn = xgt.Connection()
  >>> ... run query and store results in Results
  >>> t = conn.get_frame('Results')
  >>> print(t.name)
  """
  def __init__(self, conn : Connection, name : str,
               schema : Iterable[Union[list[Any], tuple[Any]]],
               container_id : int, commit_id : int) -> None:
    """Constructor for TableFrame. Called when TableFrame is created."""
    self._conn = conn
    if _is_qualified_name(name):
      self._namespace, self._frame = _parse_qualified_name(name)
    else:
      self._namespace, self._frame = self._conn.get_default_namespace(), name
    self._name = self._namespace + FRAME_SEPARATOR + self._frame

    # Check the schema against the valid property types.
    valid_prop_types = _get_valid_property_types_to_create() + \
                       _get_valid_property_types_for_return_only()

    for col in schema:
      if col[1] not in valid_prop_types:
        raise XgtTypeError(f'Invalid property type "{col[1]}"')

    self._container_id = container_id
    self._commit_id = commit_id

  def __str__(self):
    return f"{{ 'name': '{self.name}', 'schema': {str(self.schema)} }}"

  @property
  def name(self) -> str:
    """Name of the frame."""
    if self._conn.get_default_namespace() != self._namespace:
      return self._name
    return self._frame

  @property
  def connection(self) -> Connection :
    """The connection used when constructing the frame."""
    return self._conn

  @property
  def schema(self) -> list[list[Any]] :
    """The frame's property names and types."""
    request = graph_proto.GetFrameSchemaRequest()
    request.name = self._name
    response = self._conn._call(request, self._conn._graph_svc.GetFrameSchema)
    return self._conn._translate_schema_from_server(response.schema)

  @property
  def num_rows(self) -> int:
    """The number of rows in the frame."""
    request = graph_proto.GetFrameSizeRequest()
    request.name = self._name
    response = self._conn._call(request, self._conn._graph_svc.GetFrameSize)
    return response.size

  @property
  def row_label_universe(self) -> list[str]:
    """
    The universe of row security labels that can be attached to rows of this
    frame. Only labels that are also in the authenticated user's label set
    are returned.
    """
    request = graph_proto.GetRowLabelUniverseRequest()
    request.name = self.name
    response = self._conn._call(request,
                                self._conn._graph_svc.GetRowLabelUniverse)
    return list(response.row_labels.label)

  @property
  def user_permissions(self) -> dict[str, bool]:
    """
    The actions a user is allowed to take on this frame.

    The actions are:

    ============ =======================================================
    Key          Description
    ============ =======================================================
    create_rows  True if the user can add rows to the frame.
    update_rows  True if the user can update columns/properties of rows.
    delete_rows  True if the user can delete rows of the frame.
    delete_frame True if the user can delete the frame.
    ============ =======================================================

    .. versionadded:: 2.0.1
    """
    request = graph_proto.GetUserPermissionsRequest()
    request.name = self.name
    response = self._conn._call(request,
                                self._conn._graph_svc.GetUserPermissions)
    return dict(response.user_permissions)

  def append_columns(
      self, new_columns : Iterable[Union[list[Any], tuple[Any]]]) -> None:
    """
    Appends columns to the frame's schema.  The new columns are given as schema
    entries and must have names unique from the existing column names.  Entries
    in new columns are initialized to null values.  If new_columns is None or
    has no entries, the function just returns.

    .. versionadded:: 1.15.0

    Parameters
    ----------
    new_columns : Iterable[list[Any] | tuple[Any]]
      The columns to append to the frame.  Given as an iterable over list or
      tuple representing valid column entries.

    Raises
    ------
    XgtTypeError
      If new_columns is not an Iterable or None or an entry is not a tuple or
      list giving a valid schema entry.
    XgtValueError
      If a new column has a duplicate name.
    """
    if new_columns is None:
      return

    new_cols_schema = _validated_schema(new_columns, False)
    if len(new_cols_schema) == 0:
      return

    new_schema = _validated_schema(self.schema) + new_cols_schema
    self._generate_modify_columns_call(new_schema)

  def delete_columns(self, columns : Iterable[Union[int, str]]) -> None:
    """
    Deletes columns from the frame's schema.  The columns are given as a mixed
    list of column positions and schema column names.  Duplicates of the same
    column are accepted and behave as if the column were given once.  If
    columns is None or has no entries, the function just returns.

    .. versionadded:: 1.15.0

    Parameters
    ----------
    columns : Iterable[int | str]
      The columns to delete.  Given as an iterable over mixed column positions
      and schema column names.

    Raises
    ------
    XgtTypeError
      If columns is not an Iterable or an entry is not an int or str.
    XgtValueError
      If a position is out-of-bounds, a name is not in the schema, or a key
      column is deleted.
    """
    schema = self.schema
    columns = _validated_columns(columns, schema)
    if columns is None or len(columns) == 0:
      return

    # Get schema entries for the columns not requested to be deleted.
    new_schema = []
    for i, entry in enumerate(schema):
      if i not in columns:
        new_schema.append(_validated_schema_column(entry))

    self._generate_modify_columns_call(new_schema)

  def modify_columns(
      self,
      new_columns : Iterable[Union[int, str, list[Any], tuple[Any]]]) -> None:
    """
    Modifies the frame's columns.  Can be used to add, delete, or reorder
    columns.  The new columns are given as a list or tuple of mixed column
    positions, schema column names, or schema entries.  Added columns must be
    given as schema entries.  Column positions or names must be valid in the
    current schema.

    Any columns in the current schema that are not in the new columns are
    deleted.  Schema entries in the new columns with names not in the current
    schema are added.  The columns are reordered to the order given in the new
    columns.  Entries in added columns are initialized to null values.

    The types of columns in the current schema cannot be changed.  Key columns
    must be in the new columns.

    .. versionadded:: 1.15.0

    Parameters
    ----------
    new_columns : Iterable[int | str | list[Any] | tuple[Any]]
      The new schema to apply to the frame.  Given as an iterable over mixed
      column positions, schema column names, or sequences representing valid
      column entries.

    Raises
    ------
    XgtTypeError
      If new_columns is not an Iterable, is empty, or an entry is not an int,
      str, or list or tuple giving a valid schema entry.  If the type of an
      existing column is changed.
    XgtValueError
      If a position is out-of-bounds, a name is not in the schema, a key column
      is not included in the new schema, or a column name is duplicated.
    """
    schema = _validated_schema_columns(new_columns, self.schema)
    self._generate_modify_columns_call(schema)

  def _generate_modify_columns_call(self, schema):
    request = graph_proto.ModifyColumnsRequest()
    request.name = self._name

    _generate_proto_schema_from_xgt_schema(request, schema)

    self._conn._call(request, self._conn._graph_svc.ModifyColumns)

  def update_columns(
      self, columns : Iterable[Union[int, str]],
      data : Union[Iterable[Iterable[Any]], pandas.DataFrame, pyarrow.Table],
      offset : int = 0,
      chunk_size : int = DEFAULT_CHUNK_SIZE) -> None :
    """
    Updates the entries for columns in a frame.  The columns are specified by
    position or name.  The data used for the update can be python data, a pandas
    dataframe or a pyarrow table (Beta).

    .. versionadded:: 1.16.0

    Parameters
    ----------
    columns : Iterable[int | str]
      The columns to update.  Given as a column's name or position.
    data : Iterable[Iterable[Any]] | pandas.DataFrame | pyarrow.Table
      Data represented by a list of lists of data items, by a pandas
      DataFrame or by a pyarrow Table.
    offset : int
      Position (index) of the first row to update.
    chunk_size : int
      Number of rows to transfer in a single Arrow chunk between the client and
      the server.

    Raises
    ------
    XgtTypeError
      If column is not a str or int.
    XgtValueError
      If the column's name or position is not in the schema or if the offset is
      invalid.
    """
    schema = self.schema
    columns = _validated_columns(columns, schema)
    if columns is None or len(columns) == 0:
      return

    if offset < 0:
      raise XgtValueError('Offset cannot be negative for updating columms')

    table, invalid_rows = self._build_arrow_table(
      data, None, None, False, None, False, update_columns = columns)
    path = self._build_flight_path(
      row_labels = None, row_label_columns = None, suppress_errors = False,
      column_mapping = None, on_duplicate_keys = 'error', row_filter = None,
      update_columns = columns, offset = offset)
    return self._write_table_to_flight(table, path, invalid_rows, chunk_size)

  def load(self, paths : Union[Iterable[str], str],
           header_mode : str = HeaderMode.NONE,
           record_history : bool = True,
           row_labels : Optional[Iterable[str]] = None,
           row_label_columns : Optional[Iterable[Union[str, int]]] = None,
           delimiter : str = ',',
           column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
           suppress_errors : bool = False, row_filter : Optional[str] = None,
           chunk_size : int = DEFAULT_CHUNK_SIZE) -> Job:
    """
    Loads data from one or more files specified in the list of paths.  These
    files may be CSV, Parquet, or compressed CSV.  Some limitations exist for
    compressed CSV.  See docs.rocketgraph.com for more details.  Each
    path may have its own protocol as described below.

    Parameters
    ----------
    paths : Iterable[str] | str
      A single path or a list of paths to files.  Local or server paths may
      contain wildcards.  Wildcard expressions can contain *, ?, range sets,
      and negation.  See docs.rocketgraph.com for more details.

      ==================== =====================================
                      Syntax for one file path
      ----------------------------------------------------------
          Resource type                 Path syntax
      ==================== =====================================
          local to Python: '<path to file>'
                           'xgt://<path to file>'
          xGT server:      'xgtd://<path to file>'
          AWS S3:          's3://<path to file>'
          https site:      'https://<path to file>'
          http site:       'http://<path to file>'
          ftps server:     'ftps://<path to file>'
          ftp server:      'ftp://<path to file>'
      ==================== =====================================
    header_mode : str
      Indicates how the file header should be processed:
        - HeaderMode.NONE:
          No header exists.
        - HeaderMode.IGNORE:
          Ignore the first line containing the header.
        - HeaderMode.NORMAL:
          Process the header in non-strict mode. If a schema column is missing,
          a null value is ingested for that schema column. Any file column
          whose name does not correspond to a schema column or a security label
          column is ignored.
        - HeaderMode.STRICT:
          Process the header in strict mode. The name of each header column
          should correspond to a schema column, a security label column, or be
          named IGNORE. Each schema column must appear in the file.

      Only applies to CSV files.

      .. versionadded:: 1.11.0
    record_history : bool
      If true, records the history of the job.
    row_labels : Iterable[str] | None
      A list of security labels to attach to each row inserted with the load.
      Each label must have been passed in to the row_label_universe parameter
      when creating the frame. Note: Only one of row_labels and
      row_label_columns must be passed.
    row_label_columns: Iterable[str | int] | None
      A list of columns indicating which columns in the CSV file contain
      security labels to attach to the inserted row. If the header mode is NONE
      or IGNORE, this must be a list of integer column indices. If the header
      mode is NORMAL or STRICT, this must be a list of string column names.
      Note: Only one of row_labels and row_label_columns must be passed.
    delimiter : str
      Single character delimiter for CSV data. Only applies to CSV files.
    column_mapping : Mapping[str, str | int] | None
      Maps the frame column names to file columns for the ingest. The key of
      each element is a frame column name. The value is either the name of the
      file column (from the file header) or the file column index. If file
      column names are used, the header_mode must be NORMAL. If only file column
      indices are used, the header_mode can be NORMAL, NONE, or
      IGNORE.

      .. versionadded:: 1.15.0
    suppress_errors : bool
      If true, continues to load data if an ingest error is encountered,
      placing the first 1000 errors into the job history.  If false, stops on
      first error and raises. Defaults to False.

      .. versionadded:: 1.11.0
    row_filter : str | None
      OpenCypher fragment used to filter, modify and parameterize the raw data
      from the input to produce the row data fed to the frame.

      .. versionadded:: 1.15.0
    chunk_size : int
      Number of rows to transfer in a single Arrow chunk between the client and
      the server.

      .. versionadded:: 1.16.0

    Returns
    -------
    Job
      A Job object representing the job that has executed the load.

    Raises
    ------
    XgtIOError
      If a file specified cannot be opened or if there are errors inserting any
      lines in the file into the frame.
    XgtNameError
      If the frame does not exist on the server.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    return self._load(
               paths, header_mode, record_history, row_labels,
               row_label_columns, delimiter = delimiter,
               column_mapping = column_mapping,
               suppress_errors = suppress_errors, row_filter = row_filter,
               chunk_size = chunk_size)

  def _load(self, paths, header_mode = HeaderMode.NONE, record_history = True,
            row_labels = None, row_label_columns = None,
            source_vertex_row_labels = None, target_vertex_row_labels = None,
            delimiter = ',', column_mapping = None, suppress_errors = False,
            row_filter = None, on_duplicate_keys = 'error',
            chunk_size = DEFAULT_CHUNK_SIZE, **kwargs):
    for entry in self.schema:
      if (entry[1] == ROWID or
          (entry[1] == LIST and entry[2] == ROWID)):
        raise TypeError('Loading into a frame that has a ROWID column is not '
                        'supported.')

    if not isinstance(record_history, bool):
      error = ("record_history must be a bool.")
      raise TypeError(error)

    if not isinstance(delimiter, str) or len(delimiter) != 1:
      error = ("delimiter must be a single character string.")
      raise TypeError(error)

    if header_mode is None or header_mode not in HeaderMode._all:
      raise TypeError(f'header_mode invalid: "{header_mode}. Use a value from HeaderMode."')

    if header_mode == HeaderMode.STRICT and column_mapping is not None:
      error = "Passing column_mapping with HeaderMode.STRICT is not supported."
      raise XgtValueError(error)

    column_mapping, row_filter = self._validate_common_load_params(
      row_labels, row_label_columns, column_mapping,
      suppress_errors, row_filter)

    _validate_row_level_labels_for_ingest(source_vertex_row_labels)
    _validate_row_level_labels_for_ingest(target_vertex_row_labels)

    if on_duplicate_keys not in ['error', 'skip', 'skip_same']:
      raise TypeError('on_duplicate_keys must be error, skip, or skip_same.')

    row_label_columns = _get_processed_row_level_label_columns(
        row_label_columns, header_mode)

    if paths is None:
      raise TypeError('the "paths" parameter is None')
    if not isinstance(paths, Iterable):  # Covers str case, too.
      raise TypeError(f'one or more file paths are expected; the data type of '
                      f'the "paths" parameter is "{type(paths)}"')
    client_paths, server_paths, url_paths = _group_paths(paths, True)
    if (len(client_paths) == 0 and len(server_paths) == 0 and
        len(url_paths) == 0):
      raise XgtIOError(f'no valid paths found: {str(paths)}')

    if 'record_history' not in kwargs:
      kwargs['record_history'] = record_history
    # TODO (josh) : Somehow make this a single transaction for multiple paths
    #               between grpc end point and arrow flight?
    if len(client_paths) > 0:
      job = self._local_ingest(client_paths, header_mode, row_labels,
                               row_label_columns, source_vertex_row_labels,
                               target_vertex_row_labels,
                               delimiter, column_mapping,
                               suppress_errors = suppress_errors,
                               on_duplicate_keys = on_duplicate_keys,
                               row_filter = row_filter, chunk_size = chunk_size,
                               **kwargs)
    if len(server_paths) > 0:
      job = self._ingest(server_paths, header_mode, row_labels,
                         row_label_columns, source_vertex_row_labels,
                         target_vertex_row_labels,
                         delimiter, column_mapping,
                         suppress_errors = suppress_errors,
                         on_duplicate_keys = on_duplicate_keys,
                         row_filter = row_filter, **kwargs)
    if len(url_paths) > 0:
      job = self._ingest(url_paths, header_mode, row_labels, row_label_columns,
                         source_vertex_row_labels, target_vertex_row_labels,
                         delimiter, column_mapping,
                         suppress_errors = suppress_errors,
                         on_duplicate_keys = on_duplicate_keys,
                         row_filter = row_filter, **kwargs)

    return job

  def save(self, path : str , offset : int = 0, length : Optional[int] = None,
           headers : bool = False, record_history : bool = True,
           include_row_labels : bool = False,
           row_label_column_header : Optional[str] = None,
           preserve_order : bool = False, number_of_files : int = 1,
           duration_as_interval : bool = False, delimiter : str = ',',
           row_filter : Optional[str] = None,
           windows_newline : bool = False) -> Job:
    """
    Writes the rows from the frame to a file in the location indicated by the
    path parameter. Will save as a Parquet file if the extension is .parquet,
    otherwise saves as a CSV.

    Parameters
    ----------
    path : str
      Path to a file.

      ==================== =====================================
                      Syntax for one file path
      ----------------------------------------------------------
          Resource type                 Path syntax
      ==================== =====================================
          local to Python: '<path to file>'
                           'xgt://<path to file>'
          xGT server:      'xgtd://<path to file>'
          AWS S3 (Beta):   's3://<path to file>'
      ==================== =====================================
    offset : int
      Position (index) of the first row to be retrieved.
    length : int | None
      Maximum number of rows to be retrieved.
    headers : bool
      Indicates if headers should be added.
    record_history : bool
      If true, records the history of the job.
    include_row_labels : bool
      Indicates whether the security labels for each row should be egested
      along with the row.
    row_label_column_header : str | None
      The header column name to use for all row labels if include_row_labels is
      true and headers is true.
    preserve_order : bool
      Indicates if the output should keep the order the frame is stored in.
    number_of_files : int
      Number of files to save. Only works with the xgtd:// protocol.
    duration_as_interval : bool
      For Parquet files duration will be saved as the logical Interval type
      instead of the default 64 bit unsigned integer type.
      Only works with the xgtd:// protocol.

      .. versionadded:: 1.13.0
    delimiter : str
      Single character delimiter for CSV data. Only applies to CSV files.

      .. versionadded:: 1.13.1
    row_filter : str | None
      OpenCypher fragment used to filter, modify and parameterize the frame's
      data to produce the row data saved in the file.

      .. versionadded:: 1.15.0
    windows_newline : bool
      False indicates CSV files should use a Unix newline of line feed (LF).
      True indicates a Windows newline of carriage return (CR), line feed (LF).
      Only applies to CSV files.

      .. versionadded:: 2.0.4

    Returns
    -------
    Job
      A Job object representing the job that has executed the save.

    Raises
    ------
    XgtIOError
      If a file specified cannot be opened.
    XgtNameError
      If the frame does not exist on the server.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    return self._save(path, offset, length, headers, record_history,
                      include_row_labels,
                      row_label_column_header, preserve_order, number_of_files,
                      duration_as_interval, delimiter, row_filter,
                      windows_newline)

  def _save(self, path, offset = 0, length = None, headers = False,
            record_history = True, include_row_labels = False,
            row_label_column_header = None, preserve_order = False,
            number_of_files = 1, duration_as_interval = False,
            delimiter = ',', row_filter = None, windows_newline = False,
            **kwargs):
    for entry in self.schema:
      if (entry[1] == ROWID or
          (entry[1] == LIST and entry[2] == ROWID)):
        raise TypeError('Saving from a frame that has a ROWID column is not '
                        'supported.')

    if path is None:
      raise TypeError('the "path" parameter is None')
    if not isinstance(path, str):
      raise TypeError(f'a file path is expected; the data type of the "path" '
                      f'parameter is "{type(path)}"')

    client_paths, server_paths, url_paths = _group_paths(path, False)
    if (len(client_paths) == 0 and len(server_paths) == 0 and
        len(url_paths) == 0):
      raise XgtIOError(f'no valid paths found: {str(path)}')

    if not isinstance(delimiter, str) or len(delimiter) != 1:
      error = ("Delimiter must be a single character string.")
      raise ValueError(error)

    if row_filter is not None and not isinstance(row_filter, str):
      raise TypeError("Output filter must be a string representing an OpenCypher "
                      "fragment.")

    if len(client_paths) > 0:
      return self._local_egest(
                 client_paths[0], offset, length, headers,
                 record_history = record_history,
                 include_row_labels = include_row_labels,
                 row_label_column_header = row_label_column_header,
                 preserve_order = preserve_order,
                 duration_as_interval = duration_as_interval,
                 delimiter = delimiter, row_filter = row_filter,
                 windows_newline = windows_newline, **kwargs)
    if len(server_paths) > 0:
      return self._egest(server_paths[0], offset, length, headers,
                         record_history = record_history,
                         include_row_labels = include_row_labels,
                         row_label_column_header = row_label_column_header,
                         preserve_order = preserve_order,
                         number_of_files = number_of_files,
                         duration_as_interval = duration_as_interval,
                         delimiter = delimiter, row_filter = row_filter,
                         windows_newline = windows_newline, **kwargs)
    if len(url_paths) > 0:
      return self._egest(url_paths[0], offset, length, headers,
                         record_history = record_history,
                         include_row_labels = include_row_labels,
                         row_label_column_header = row_label_column_header,
                         preserve_order = preserve_order,
                         number_of_files = number_of_files,
                         duration_as_interval = duration_as_interval,
                         delimiter = delimiter, row_filter = row_filter,
                         windows_newline = windows_newline, **kwargs)

  def insert(self, data : Union[Iterable[Iterable[Any]],
                                pandas.DataFrame, pyarrow.Table],
             row_labels : Optional[Iterable[str]] = None,
             row_label_columns : Optional[Iterable[int]] = None,
             column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
             suppress_errors : bool = False, row_filter : Optional[str] = None,
             chunk_size : int = DEFAULT_CHUNK_SIZE) -> Job:
    """
    Inserts data rows. The properties of the new data must match the schema in
    both order and type.

    Parameters
    ----------
    data : Iterable[Iterable[Any]] | pandas.DataFrame | pyarrow.Table
      Data represented by a list of lists of data items, by a pandas
      DataFrame or by a pyarrow Table.
    row_labels : Iterable[str] | None
      A list of security labels to attach to each row inserted.  Each label
      must have been passed in to the row_label_universe parameter when
      creating the frame. Note: Only one of row_labels and row_label_columns
      must be passed.
    row_label_columns : Iterable[int] | None
      A list of integer column indices indicating which columns in the input
      data contain security labels to attach to the inserted row. Note: Only
      one of row_labels and row_label_columns must be passed.
    column_mapping : Mapping[str, str | int] | None
      Maps the frame column names to input columns for the ingest. The key of
      each element is a frame column name. The value is either the name of the
      column (from the Pandas frame or xGT schema column name for lists) or the
      file column index.

      .. versionadded:: 1.15.0
    suppress_errors : bool
      If true, will continue to insert data if an ingest error is encountered,
      placing the first 1000 errors in the job history. If false, stops on
      first error and raises.  Defaults to False.

      .. versionadded:: 1.11.0
    row_filter : str | None
      OpenCypher fragment used to filter, modify and parameterize the raw data
      from the input to produce the row data fed to the frame.

      .. versionadded:: 1.15.0
    chunk_size : int
      Number of rows to transfer in a single Arrow chunk between the client and
      the server.

      .. versionadded:: 1.16.0

    Returns
    -------
    Job
      A Job object representing the job that has executed the insert.

    Raises
    ------
    XgtIOError
      If there are errors in the data being inserted or some data could
      not be inserted into the frame.
    XgtNameError
      If the frame does not exist on the server.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    if data is None:
      return
    if len(data) == 0:
      return

    column_mapping, row_filter = self._validate_common_load_params(
      row_labels, row_label_columns, column_mapping,
      suppress_errors, row_filter)

    table, invalid_rows = self._build_arrow_table(
      data, row_labels, row_label_columns, suppress_errors,
      column_mapping, row_filter is not None)
    path = self._build_flight_path(
      row_labels, row_label_columns, suppress_errors,
      column_mapping = column_mapping, row_filter = row_filter)
    return self._write_table_to_flight(table, path, invalid_rows, chunk_size)

  def _build_arrow_table(self, data, row_labels, row_label_columns,
                         suppress_errors, column_mapping, has_row_filter,
                         update_columns = None):
    def handle_error(row, invalid_rows):
      if suppress_errors:
        invalid_rows.append(row)
      else:
        raise XgtIOError(row[0])

    def convert_pandas_column(i, col, schema_col, table, out_dict):
      import numpy as np

      # These are the different types of arrays created with pandas.array().
      pandas_array_types = _get_pandas_array_types()

      # Change the name of arrow columns to the pandas names for the arrow
      # table.  This allows name mapping for pandas frames.  Only do this if
      # the pandas frame has column names.
      infer_type = pd.api.types.infer_dtype(table[col])
      xgt_infer_type, xgt_infer_subtype = _get_xgt_infer_type(table[col],
                                                              infer_type)

      # For columns where datetimes and dates are mixed, the inferred dtype
      # will be date.  So we do additional checks.
      has_mixed_dates = False
      if infer_type == "date":
        check_mixed_dates = (_cached_pandas_map_function(table[[col]], type) !=
                             table[[col]].iloc[0].apply(type)).any(axis = 1)
        has_mixed_dates = len(table[check_mixed_dates]) > 0

      # If the column is detected to be mixed type, convert the column to
      # strings.
      if has_mixed_dates or xgt_infer_type == "mixed":
        if schema_col[1] == INT or schema_col[1] == UINT:
          def fixcol(x) -> str:
            if pd.isnull(x):
              return None
            # Floats, bools, and decimals must first be converted to an int to
            # have consistent behavior with when no mixed types.
            elif isinstance(x, (float, bool, decimal.Decimal)):
              return str(int(x))
            # Datetime must be converted to microseconds since epoch to have
            # consistent behavior with when no mixed types.
            elif isinstance(x, datetime):
              seconds_since_epoch = x - datetime(1970, 1, 1)
              microseconds_since_epoch = \
                  seconds_since_epoch / timedelta(seconds = 1) * 1_000_000
              return str(int(microseconds_since_epoch))
            # Date must be converted to days since epoch to have consistent
            # behavior with when no mixed types.
            elif isinstance(x, date):
              days_between_ordinal_and_epoch = 719163
              return str(x.toordinal() - days_between_ordinal_and_epoch)
            # Time must be converted to microseconds since 00:00:00.000000 to
            # have consistent behavior with when no mixed types.
            elif isinstance(x, time):
              seconds_since_zero = \
                  datetime.combine(date.min, x) - datetime.min
              microseconds_since_zero = \
                  seconds_since_zero / timedelta(seconds = 1) * 1_000_000
              return str(int(microseconds_since_zero))
            elif isinstance(x, timedelta):
              return str(int(x / timedelta(microseconds = 1)))
            else:
              return str(x)

          fixed_col = table[col].apply(fixcol)
        elif schema_col[1] == FLOAT:
          def fixcol(x) -> str:
            if pd.isnull(x):
              return None
            else:
              return str(x)

          fixed_col = table[col].apply(fixcol)
        elif schema_col[1] == TEXT:
          def fixcol(x) -> str:
            if pd.isnull(x):
              return None
            # Whole numbers should be converted to have no fractional part.
            elif isinstance(x, float) and x != float('inf') and int(x) == x:
              if x != 0:
                return str(int(x))
              # Negative zero needs the sign.
              elif math.copysign(1.0, x) == -1.0:
                return '-0'
              else:
                return '0'
            # Arrow decimal types always convert -0 to +0.  Do that for mixed
            # types to be consistent.
            elif isinstance(x, decimal.Decimal) and x == 0.0:
              return '0.0'
            elif isinstance(x, timedelta):
              return isodate.duration_isoformat(x)
            else:
              return str(x)

          fixed_col = table[col].apply(fixcol)
        elif schema_col[1] == BOOLEAN:
          # Ints must first be converted to a bool to have consistent
          # behavior with when no mixed types.
          def fixcol(x) -> str:
            if pd.isnull(x):
              return None
            elif isinstance(x, int):
              return 'True' if x != 0 else 'False'
            else:
              return str(x)

          fixed_col = table[col].apply(fixcol)
        elif schema_col[1] == DURATION:
          def fixcol(x) -> str:
            if pd.isnull(x):
              return None
            elif (isinstance(x, time)):
              # Turn a time into a mangled string as it's normal string x is
              # insertable into a duration.  It should fail on insert.
              return f'time({x})'
            else:
              return str(x)

          fixed_col = table[col].apply(fixcol)
        else:
          fixed_col = table[col].astype('string')

        out_dict[i] = pyarrow.Array.from_pandas(fixed_col)
      else:
        # float('nan') values can't be converted by default to some of the
        # xgt column types.  Explicitly do that.
        if ((infer_type == "floating" and
             schema_col[1] not in [FLOAT, INT, TEXT]) or
            (xgt_infer_type == "ndarray" and
             xgt_infer_subtype in ['float32', 'float64'] and
             (schema_col[1] not in [WGSPOINT, CARTESIANPOINT] and
              schema_col[2] not in [FLOAT, INT, TEXT]))):
          def fix_floats(x):
            # It's enough for an ndarray to convert the type to object.
            if isinstance(x, np.ndarray):
              return x.astype('object')

            return None if pd.isnull(x) else x
          fixed_col = table[col].apply(fix_floats)
        else:
          fixed_col = table[col]

        # IP addresses need to be converted to strings.  For scalar columns,
        # the mixed type code does the conversion.  Do the conversion for
        # numpy.ndarrays.  This handles all depths.
        if (xgt_infer_type == "ndarray" and xgt_infer_subtype == "object" and
            schema_col[1] in [LIST, WGSPOINT, CARTESIANPOINT]):
          # TODO(Greg): Should this use recurive calls to np.vectorize()?
          #             Needs to handle all list depths.
          def recursive_convert(x):
            if isinstance(x, (IPv4Address, IPv6Address)):
              return str(x)
            elif isinstance(x, np.ndarray):
              if x.ndim > 1:
                raise XgtValueError('Multi-dimensional numpy arrays not '
                                    'supported')
              new_array = np.ndarray(shape = x.shape, dtype = x.dtype)
              for i in range(x.size):
                new_array[i] = recursive_convert(x[i])
              return new_array
            else:
              return x

          fix_ip_helper = np.vectorize(recursive_convert, otypes = [object])

          def fix_ip_addresses(x):
            return fix_ip_helper(x) if isinstance(x, np.ndarray) else x

          fixed_col = fixed_col.apply(fix_ip_addresses)

        # pyarrow.Array.from_pandas() can't convert ndarrays of depth 2 or
        # greater.  Do this manually.
        if (xgt_infer_type == "ndarray" and ((schema_col[1] == LIST and
            len(schema_col) > 3 and schema_col[3] > 1) or (
            len(schema_col) > 2 and
            schema_col[2] in [WGSPOINT, CARTESIANPOINT]))):
          if (schema_col[2] == TEXT and
              xgt_infer_subtype in ['float32', 'float64']):
            # When converting floats to text, just calling tolist() on a
            # numpy.ndarray loses the exact precision of the input floats.  For
            # instance, 4.2 might be modified to 4.199999809265137.  Convert to
            # Python lists of string manually.
            def fix_floats(x):
              if isinstance(x, np.ndarray):
                return [fix_floats(_) for _ in x]
              elif pd.isnull(x):
                return None
              # Whole numbers should be converted to have no fractional part.
              elif x != float('inf') and int(x) == x:
                if x != 0:
                  return str(int(x))
                # Negative zero needs the sign.
                elif math.copysign(1.0, x) == -1.0:
                  return '-0'
                else:
                  return '0'
              elif xgt_infer_subtype == 'float32':
                # The server decodes floats to a max of 7 digits when inserting
                # floats to a text column.  Need to limit to 7 digits here,
                # too.
                return f"{x:.7g}"
              else:
                # The server decodes doubles to a max of 15 digits when
                # inserting floats to a text column.  Need to limit to 15
                # digits here, too.
                return f"{x:.15g}"

            fixed_col = fixed_col.apply(fix_floats)
          else:
            fixed_col = fixed_col.apply(
                lambda x: x.tolist() if isinstance(x, np.ndarray) else x)

        # pyarrow.Array.from_pandas() can't convert pandas.arrays.  Do this
        # manually.
        if (xgt_infer_type == "pandasarray" and schema_col[1] == LIST):
          def fix_pandas_array(x):
            if isinstance(x, pandas_array_types):
              return [fix_pandas_array(_) for _ in x]
            elif pd.isnull(x):
              return None
            elif isinstance(x, pd.Timedelta):
              # In almost all cases, timedeltas (pandas or numpy) are stored
              # with nanosecond resolution.  For some reason when stored in
              # pandas arrays, the resolution is microseconds instead.  This
              # function returns a numpy.timedelta with forced nanosecond
              # resolution.
              return x.to_timedelta64()
            elif isinstance(x, pd.Timestamp):
              # In almost all cases, timestamps (pandas or numpy) are stored
              # with nanosecond resolution.  For some reason when stored in
              # pandas arrays, the resolution is microseconds instead.  This
              # function returns a numpy.timestamp with forced nanosecond
              # resolution.
              return x.to_datetime64()
            elif isinstance(x, (IPv4Address, IPv6Address)):
              # IP addresses need to be converted to strings.
              return str(x)
            else:
              return x

          fixed_col = fixed_col.apply(fix_pandas_array)

        out_dict[i] = pyarrow.Array.from_pandas(fixed_col)

    def convert_python_column(i, col, schema_col):
      if schema_col[1] == INT or schema_col[1] == UINT:
        for j, val in enumerate(col):
          # Floats, bools, and decimals must first be converted to an int to
          # have consistent behavior with when no mixed types.
          if isinstance(val, (float, bool, decimal.Decimal)):
            col[j] = str(int(val))
          # Datetime must be converted to microseconds since epoch to have
          # consistent behavior with when no mixed types.
          elif isinstance(val, datetime):
            seconds_since_epoch = val - datetime(1970, 1, 1)
            microseconds_since_epoch = \
                seconds_since_epoch / timedelta(seconds = 1) * 1_000_000
            col[j] = str(int(microseconds_since_epoch))
          # Date must be converted to days since epoch to have consistent
          # behavior with when no mixed types.
          elif isinstance(val, date):
            days_between_ordinal_and_epoch = 719163
            col[j] = str(val.toordinal() -
                                 days_between_ordinal_and_epoch)
          # Time must be converted to microseconds since 00:00:00.000000 to
          # have consistent behavior with when no mixed types.
          elif isinstance(val, time):
            seconds_since_zero = datetime.combine(date.min, val) - datetime.min
            microseconds_since_zero = \
                seconds_since_zero / timedelta(seconds = 1) * 1_000_000
            col[j] = str(int(microseconds_since_zero))
          elif isinstance(val, timedelta):
            col[j] = str(int(val / timedelta(microseconds = 1)))
          elif val != None:
            col[j] = str(val)
      elif schema_col[1] == FLOAT:
        for j, val in enumerate(col):
          # Convert nan to string 'nan' for mixed types.  Detect nan because
          # it's the only value not equal to itself.
          if val != val:
            col[j] = 'nan'
          elif val != None:
            col[j] = str(val)
      elif schema_col[1] == TEXT:
        for j, val in enumerate(col):
          # Whole numbers should be converted to have no fractional part.
          if (isinstance(val, float) and val == val and
              val != float('inf') and int(val) == val):
            if val != 0:
              col[j] = str(int(val))
            # Negative zero needs the sign.
            elif math.copysign(1.0, val) == -1.0:
              col[j] = '-0'
            else:
              col[j] = '0'
          # Arrow decimal types always convert -0 to +0.  Do that for mixed
          # types to be consistent.
          elif isinstance(val, decimal.Decimal) and val == 0.0:
            col[j] = '0.0'
          elif isinstance(val, timedelta):
            col[j] = isodate.duration_isoformat(val)
          elif val != None:
            col[j] = str(val)
      elif schema_col[1] == BOOLEAN:
        for j, val in enumerate(col):
          # Ints must first be converted to a bool to have consistent behavior
          # with when no mixed types.
          if isinstance(val, int):
            col[j] = str(bool(val))
          elif val != None:
            col[j] = str(val)
      elif schema_col[1] == DURATION:
        for j, val in enumerate(col):
          if (isinstance(val, time)):
            # Turn a time into a mangled string as it's normal string value is
            # insertable into a duration.  It should fail on insert.
            col[j] = f'time({val})'
          elif val != None:
            col[j] = str(val)
      else:
        for j, val in enumerate(col):
          if val != None:
            col[j] = str(val)

    # Detect if user passed in a pandas frame.
    is_pandas = False
    try:
      import pandas as pd
      is_pandas = isinstance(data, pd.DataFrame)
    except:
      pass
    is_iterable = isinstance(data, Iterable)
    is_pyarrow_table = isinstance(data, pyarrow.Table)

    if not (is_pandas or is_iterable or is_pyarrow_table):
      raise TypeError('a list of lists, a pandas DataFrame, or a pyarrow '
                      'Table is expected')

    # Exceptions for iterators get eaten by grpc so we check outside
    # the generator function:
    if is_iterable and not (is_pandas or is_pyarrow_table):
      for i, entry in enumerate(data):
          if not isinstance(entry, Iterable):
              raise TypeError(f'Row #{i} is not a list. A list of lists '
                              f'or a pandas DataFrame is expected')

    schema = self.schema
    for entry in schema:
      if (entry[1] == ROWID or
          (entry[1] == LIST and entry[2] == ROWID)):
        raise TypeError('Inserting into a frame that has a ROWID column is not '
                        'supported.')

    row_label_columns = _get_processed_row_level_label_columns(
        row_label_columns, HeaderMode.NONE)

    final_schema = []

    # Locations to insert row label columns into the schema.
    if row_label_columns is not None:
      schema_mods = set(row_label_columns)
    else:
      schema_mods = { }
    correction = 0


    if update_columns is not None:
      final_schema = [schema[i] for i in update_columns]
    elif not has_row_filter:
      for i, xgt_type in enumerate(schema):
        # We need to insert the row label columns into the schema.
        while i + correction in schema_mods:
          correction += 1
          final_schema.append([f"row_labels{i + correction}", TEXT] )
        final_schema.append(xgt_type)
      final_length = len(final_schema)

      # End row label columns to the end.
      for i in range(len(schema) + len(schema_mods) - final_length):
        final_schema.append([f"row_labels{i + final_length}", TEXT] )
    else:
      # We have an input filter so the data is not necessarily correlated to the
      # frame's schema.  Let's try inferring a schema from the raw data.

      # Disable column mapping with an input filter
      column_mapping = None
      if is_pandas:
        final_schema = _infer_xgt_schema_from_pandas_data(data)
      elif is_pyarrow_table:
        final_schema = _infer_xgt_schema_from_pyarrow_table(data)
      else:
        final_schema = _infer_xgt_schema_from_python_data(data)

    # List of invalid rows.
    invalid_rows = []
    table = data

    # The variable out_dict will be the input to build a PyArrow.Table which is
    # column major.  Regardless of if table is a pandas DataFrame or Python
    # list of lists, out_dict is a column major table.

    # For mapping we need to make sure we are handling conversions on the
    # column the data is being mapped to.
    def set_type_for_mapping():
      data_col_name_to_type = { elem[0] : elem[1] for elem in final_schema }
      data_col_name_to_pos = { elem[0] : i
                               for i, elem in enumerate(final_schema) }
      mapped_type = { }
      for frame_col, data_col in column_mapping.items():
        col_type = data_col_name_to_type[frame_col]
        if isinstance(data_col, str):
          pos = data_col_name_to_pos[frame_col]
        elif isinstance(data_col, int):
          pos = data_col
          if data_col >= len(final_schema) or data_col < 0:
            err = ("Error creating the schema. The column mapping refers to "
                   f"data column position {data_col}, but only "
                   f"{len(final_schema)} columns were found in the data.")
            raise XgtValueError(err)

        # If the column is mapped to multiple frame column types, just
        # represent it as a string on transfer.
        if pos in mapped_type and mapped_type[pos] != col_type:
          mapped_type[pos] = TEXT
        else:
          mapped_type[pos] = col_type

      for pos, col_type in mapped_type.items():
        final_schema[pos][1] = col_type

      for i, col in enumerate(table):
        if isinstance(col, str):
          final_schema[i][0] = col

    if column_mapping is not None:
      set_type_for_mapping()
      for i, col in enumerate(table):
        if isinstance(col, str):
          final_schema[i][0] = col

    if is_pandas:
      # The input table is a pandas DataFrame which is column major.
      out_dict = [[] for i in range(len(table.columns))]

      for i, col in enumerate(table):
        # Stop filling columns if there are more columns in the input DataFrame
        # than the schema.
        if i >= len(final_schema):
          break

        convert_pandas_column(i, col, final_schema[i], table, out_dict)
    elif is_pyarrow_table:
      return (data, invalid_rows)
    else:
      # The input table is a Python list of lists which is row major.
      out_dict = [[None for i in range(len(table))]
                  for j in range(len(final_schema))]
      multiple_detected = [False for j in range(len(final_schema))]
      types_detected = [None for j in range(len(final_schema))]
      correction = 0

      # Copy the input data to out_dict, converting to column major.
      for i, row in enumerate(table):
        if len(row) != len(out_dict):
          correction += 1
          handle_error([f"Expected {len(out_dict)} columns but found "
                        f"{len(row)}.", "", i] + list(row), invalid_rows)
          continue

        for j, val in enumerate(row):
          if val != None:
            if types_detected[j] == None:
              types_detected[j] = type(val)
            elif type(val) != types_detected[j]:
              multiple_detected[j] = True

          def fix_values(val):
            if isinstance(val, list):
              # This applies the fixes recursively and ensure lists are deep
              # copied from the input.
              return [fix_values(x) for x in val]
            elif isinstance(val, (IPv4Address, IPv6Address)):
              # Convert all ipaddresses to strings.
              return str(val)
            elif (val != val and
                  (final_schema[j][1] not in [FLOAT, TEXT, LIST] or
                   (final_schema[j][1] == LIST and
                    final_schema[j][2] not in [FLOAT, TEXT]))):
              # Convert nan to None for all column types that aren't float or
              # text.  Detect nan because it's the only value not equal to
              # itself.
              return None
            else:
              return val

          out_dict[j][i - correction] = fix_values(val)

      if correction > 0:
        for i, col in enumerate(out_dict):
          out_dict[i] = col[:-correction]

      # Try to get mixed column types into a common str type.
      for i, col in enumerate(out_dict):
        if multiple_detected[i]:
          convert_python_column(i, col, final_schema[i])

    # If all the rows are garbage, raise.
    if len(out_dict[0]) == 0:
      job = Job(self._conn, python_errors = invalid_rows)
      raise XgtIOError(self._create_ingest_error_message(job), job = job)

    # Create dictionary from the columns.
    arrow_dict = { entry[0] : out_dict[i] for i, entry in
                   enumerate(final_schema) if i < len(out_dict) }

    try:
      pyarrow_table = pyarrow.Table.from_pydict(arrow_dict)
    except pyarrow.lib.ArrowTypeError as err:
      raise XgtIOError(str(err), str(err))
    except pyarrow.lib.ArrowInvalid as err:
      raise XgtIOError(str(err), str(err))

    return (pyarrow_table, invalid_rows)

  def _build_flight_path(self, row_labels, row_label_columns, suppress_errors,
                         source_vertex_row_labels = None,
                         target_vertex_row_labels = None,
                         column_mapping = None, on_duplicate_keys = 'error',
                         row_filter = None, update_columns = None, **kwargs):
    path = tuple(self.name.split("__"))
    for x in path:
      x = f'`{x}`'

    if row_labels is not None:
      # Convert to list to check if there's at least one element.
      row_labels_list = list(row_labels)
      if len(row_labels_list) > 0:
        labels = ".labels=" + ",".join(f"'{w}'" for w in row_labels_list)
        path += (labels,)

    if row_label_columns is not None:
      # Convert to list to check if there's at least one element.
      row_label_columns_list = list(row_label_columns)
      if len(row_label_columns_list) > 0:
        if isinstance(row_label_columns_list[0], int):
          label_indices = ".label_column_indices=" + \
                           ",".join(str(x) for x in row_label_columns_list)
          path += (label_indices,)
        elif isinstance(row_label_columns_list[0], str):
          label_names = ".label_column_names=" + \
                        ",".join(x for x in row_label_columns_list)
          path += (label_names,)

    suppress_errors_option = ".suppress_errors=" + str(suppress_errors).lower()
    on_duplicate_keys_option = ".on_duplicate_keys=" + \
                               str(on_duplicate_keys).lower()
    path += (suppress_errors_option,)
    path += (on_duplicate_keys_option,)

    if row_filter is not None:
      row_filter_value = f'.row_filter="{row_filter}"'
      path += (row_filter_value,)

    if source_vertex_row_labels is not None:
      # Convert to list to check if there's at least one element.
      source_vertex_row_labels_list = list(source_vertex_row_labels)
      if len(source_vertex_row_labels_list) > 0:
        src_labels = ".implicit_source_vertex_labels=" + \
                     ",".join(f"'{w}'" for w in source_vertex_row_labels_list)
        path += (src_labels,)

    if target_vertex_row_labels is not None:
      # Convert to list to check if there's at least one element.
      target_vertex_row_labels_list = list(target_vertex_row_labels)
      if len(target_vertex_row_labels_list) > 0:
        trg_labels = ".implicit_target_vertex_labels=" + \
                     ",".join(f"'{w}'" for w in target_vertex_row_labels_list)
        path += (trg_labels,)

    if column_mapping is not None:
      map_values = ".map_column_names=[" + \
          ','.join(f"{key}:{value}" for key, value in column_mapping.items()
                   if isinstance(value, str)) + "]"
      path += (map_values,)
      map_values = ".map_column_ids=[" + \
          ','.join(f"{key}:{value}" for key, value in column_mapping.items()
                   if isinstance(value, int)) + "]"
      path += (map_values,)

    if update_columns is not None:
      columns = '.update_columns=' + \
        ','.join(f"{str(column)}" for column in update_columns)
      path += (columns,)

    has_record_history = False
    for k,v in kwargs.items():
      if k in ("headerMode", "print_timing", "detailed_timing"):
        #TODO(josh): Support print timing on local parquet load.
        pass
      elif k == "record_history":
        has_record_history = True
        path += (f".record_history={str(v)}",)
      elif k == "offset":
        path += (f".offset={str(v)}",)
      else:
        raise ValueError(f"kwarg {k} not supported.")
    # Don't record history for inserts
    if not has_record_history:
      path += (".record_history=false",)

    return path

  def _write_table_to_flight(self, table, path, invalid_rows, chunk_size):
    try:
      writer, metadata = self._conn.arrow_conn.do_put(
          pyarrow.flight.FlightDescriptor.for_path(*path), table.schema)

      batches = table.to_batches(max_chunksize = chunk_size)
      for batch in batches:
        writer.write_batch(batch)

      # Write an empty batch with metadata to indicate we are done.
      empty = [[]] * len(table.schema)
      empty_batch = pyarrow.RecordBatch.from_arrays(empty,
                                                    schema = table.schema)
      metadata_end = struct.pack('<i', 0)
      writer.write_with_metadata(empty_batch, metadata_end)
      buf = metadata.read()
      job_proto = sch_proto.JobStatus()
      if buf is not None:
        job_proto.ParseFromString(buf.to_pybytes())

      writer.close()
    except pyarrow._flight.FlightServerError as err:
      raise _convert_flight_server_error_into_xgt(err) from err
    except pyarrow._flight.FlightCancelledError as err:
      raise XgtConnectionError(str(err)) from err
    except pyarrow._flight.FlightUnavailableError as err:
      raise XgtConnectionError(str(err)) from err

    job = Job(self._conn, job_proto, python_errors = invalid_rows)
    job_data = job.get_ingest_errors()

    if job_data is not None and len(job_data) > 0:
      raise XgtIOError(self._create_ingest_error_message(job), job = job)
    return job

  def get_data(
      self, offset : int = 0, length : Optional[int] = None,
      rows : Optional[Iterable[int]] = None,
      columns : Optional[Iterable[Union[int, str]]] = None,
      format : str = 'python', include_row_labels : bool = False,
      row_label_column_header : Optional[str] = None,
      row_filter : Optional[str] = None, expand : str = 'none'
  ) -> Union[list[list[Any]], pandas.DataFrame, pyarrow.Table]:
    """
    Returns frame data starting at a given offset and spanning a given length.

    Parameters
    ----------
    offset : int
      Position (index) of the first row to be retrieved. Cannot be given with
      rows.
    length : int | None
      Maximum number of rows to be retrieved starting from the row
      indicated by offset. A value of 'None' means 'all rows' on and
      after the offset. Cannot be given with rows.
    rows : Iterable[int] | None
      The rows to retrieve.  A value of 'None' means all rows.  Cannot be given
      with either offset or length.

      .. versionadded:: 1.16.0
    columns : Iterable[int | str] | None
      The columns to retrieve.  Given as an iterable over mixed column
      positions and schema column names.  A value of 'None' means all columns.

      .. versionadded:: 1.14.0
    format : str
      Selects the data format returned: a Python list of list, a pandas
      Dataframe, or an Apache Arrow Table.  Must be one of 'python', 'pandas',
      or 'arrow'.

      .. versionadded:: 1.14.0
    include_row_labels : bool
      Indicates whether the security labels for each row should be egested
      along with the row. Default=False.
    row_label_column_header : str | None
      The header column name to use for all row labels if include_row_labels is
      true and headers is true.
      Ignored for python format. Default=None.
    row_filter : str | None
      OpenCypher fragment used to filter, modify and parameterize the frame's
      data to produce the row data returned to the client. Default=None.

      .. versionadded:: 1.15.0
    expand : str
      Controls what is returned for a RowID column type.  Allowed values are:
        - 'none': Only RowID.  Original behavior.
        - 'light': Expands RowIDs to Vertex, Edge, and TableRow types that
          include properties.
        - 'full': Expands RowIDs to Vertex, Edge, and TableRow types that
          include properties.  Also includes frame data.

      Works only for python and pandas format.

      .. experimental:: The API of this parameter may change in future releases.

    Returns
    -------
    list[list[Any]] | pandas.DataFrame | pyarrow.Table

    Raises
    ------
    XgtNameError
      If the frame does not exist on the server.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    ValueError
      If parameter is out of bounds or invalid format given.
    OverflowError
      If data is out of bounds when converting.
    """
    return self._get_data(
        offset=offset,
        length=length,
        rows=rows,
        columns=columns,
        format=format,
        include_row_labels=include_row_labels,
        row_label_column_header=row_label_column_header,
        row_filter=row_filter,
        expand=expand,
        validation_id=None
    )

  def _get_data(
      self, offset : int = 0, length : Optional[int] = None,
      rows : Optional[Iterable[int]] = None,
      columns : Optional[Iterable[Union[int, str]]] = None,
      format : str = 'python', include_row_labels : bool = False,
      row_label_column_header : Optional[str] = None,
      row_filter : Optional[str] = None,
      expand : str = 'none', validation_id = None
  ) -> Union[list[list[Any]], pandas.DataFrame, pyarrow.Table]:
    """
    Internal version of get_data that supports validation_id.
    """
    # Get the requested columns as a list of integers.
    schema = self.schema
    columns = _validated_columns(columns, schema)

    # If specific columns are requested, the schema used to convert the pyarrow
    # table to pandas or pandas format should only include those columns.
    if columns is not None:
      schema = []
      for i in columns:
        schema.append(self.schema[i])

    if not isinstance(format, str):
      raise XgtTypeError('format must be of type string')

    # Ignore format case.
    lc_format = format.lower()

    if lc_format == 'python':
      return self._get_data_python(schema, offset, length, rows, columns,
                                   include_row_labels, validation_id,
                                   row_filter = row_filter, expand = expand)
    elif lc_format == 'pandas':
      ticket = _create_flight_ticket(
                 self, self._name, offset, length, rows = rows,
                 columns = columns, include_row_labels = include_row_labels,
                 validation_id = validation_id,
                 row_label_column_header = row_label_column_header,
                 row_filter = row_filter)

      return _get_data_pandas(self._conn, ticket, schema, expand)
    elif lc_format == 'arrow':
      ticket = _create_flight_ticket(
                   self, self._name, offset, length, rows = rows,
                   columns = columns, include_row_labels = include_row_labels,
                   validation_id = validation_id,
                   row_label_column_header = row_label_column_header,
                   row_filter = row_filter)

      return _get_data_arrow(self._conn, ticket)
    else:
      raise XgtValueError('format must be one of python, pandas, or arrow, '
                          f'given: {format}')

  # Internal function that contains validation_id that allows validating that
  # no deletes have occurred to this frame since the validation_id was created.
  def _get_data_python(self, schema, offset = 0, length = None, rows = None,
                       columns = None, include_row_labels = False,
                       validation_id = None, row_filter = None,
                       absolute_indexing = False, expand = 'none'):
    ticket = _create_flight_ticket(
               self, self._name, offset, length, rows = rows, columns = columns,
               include_row_labels = include_row_labels,
               validation_id = validation_id, row_filter = row_filter,
               absolute_indexing = absolute_indexing)
    return _get_data_python(self._conn, ticket, schema, expand)

  def _get_data_csv(self, offset = 0, length = None, headers = True,
                    content_type = data_proto.CSV, include_row_labels = False,
                    row_label_column_header = None, preserve_order = False,
                    delimiter: str = ',', row_filter = None,
                    windows_newline = False, **kwargs):
    if isinstance(offset, str):
      offset = int(offset)
    if isinstance(length, str):
      length = int(length)
    if isinstance(offset, int):
      if offset < 0:
        raise ValueError('offset is negative')
    if isinstance(length, int):
      if length < 0:
        raise ValueError('length is negative')

    request = data_proto.DownloadDataRequest()
    request.repository_name = self._name
    if offset is not None:
      request.offset.value = offset
    if length is not None:
      request.length.value = length
    request.with_headers = headers
    request.content_type = content_type
    request.preserve_order = preserve_order
    request.delimiter = delimiter

    for k,v in kwargs.items():
      if isinstance(v, bool):
        request.kwargs[k].bool_value = v
      elif isinstance(v, int):
        request.kwargs[k].int_value = v
      elif isinstance(v, float):
        request.kwargs[k].float_value = v
      elif isinstance(v, str):
        request.kwargs[k].string_value = v

    request.row_labels.egest_labels = include_row_labels
    if row_label_column_header is not None:
      request.row_labels.label_header_name = row_label_column_header
    else:
      request.row_labels.label_header_name = "ROWLABEL"

    if row_filter is not None:
      request.row_filter = row_filter

    request.windows_newline = windows_newline

    responses = self._conn._call(request, self._conn._data_svc.DownloadData)
    return responses

  def _create_csv_packet (self, frame_name, header_mode, row_labels,
                          row_label_columns, source_vertex_row_labels,
                          target_vertex_row_labels, delimiter,
                          column_mapping, suppress_errors,
                          on_duplicate_keys, row_filter, **kwargs):
    request = data_proto.UploadDataRequest()
    request.frame_name = frame_name.encode('utf-8')
    request.content_type = data_proto.CSV
    request.is_python_insert = False
    request.suppress_errors = suppress_errors
    request.on_duplicate_keys = on_duplicate_keys

    request = _row_level_labels_helper(request, row_labels,
                                       row_label_columns,
                                       source_vertex_row_labels,
                                       target_vertex_row_labels,
                                       header_mode)

    request.delimiter = delimiter

    _convert_header_mode(header_mode, request)
    request.implicit_vertices = True

    if row_filter is not None:
      request.row_filter = row_filter
    # Set the mapping of frame column to file source.
    if column_mapping is not None:
      request.column_mapping.CopyFrom(
        _set_column_mapping_in_ingest_request(column_mapping))
    for k,v in kwargs.items():
      if isinstance(v, bool):
        request.kwargs[k].bool_value = v
      elif isinstance(v, int):
        request.kwargs[k].int_value = v
      elif isinstance(v, float):
        request.kwargs[k].float_value = v
      elif isinstance(v, str):
        request.kwargs[k].string_value = v

    return request

  def _insert_csv_packet_generator(self, paths, header_mode, row_labels,
                                   row_label_columns, source_vertex_row_labels,
                                   target_vertex_row_labels, delimiter,
                                   column_mapping, suppress_errors,
                                   on_duplicate_keys, row_filter, **kwargs):
    request = self._create_csv_packet(self._name, header_mode,
                                      row_labels, row_label_columns,
                                      source_vertex_row_labels,
                                      target_vertex_row_labels,
                                      delimiter, column_mapping,
                                      suppress_errors, on_duplicate_keys,
                                      row_filter, **kwargs)
    for fpath in paths:
        try:
          data = ''
          dsize = 0
          with open(fpath, 'rb') as f:
            line = f.readline()
            while line:
              line = line.decode('utf-8')
              lsize = len(line)
              if (dsize + lsize) < MAX_PACKET_SIZE:
                data += line
                dsize += lsize
              else:
                request.file_path = fpath
                request.content = data.encode('utf-8')
                yield request
                data = line
                dsize = len(data)
              line = f.readline()
            request.file_path = fpath
            request.content = data.encode('utf-8')
            yield request
        except:
          # Print the error and don't throw since grpc will give an unknown
          # error.
          sys.stderr.write(f"Error in {fpath}: ")
          traceback.print_exc(file = sys.stderr)
          sys.stderr.write("\n")
          pass

  # Returns last job run.
  def _local_ingest(self, paths, header_mode = HeaderMode.NONE,
                    row_labels = None, row_label_columns = None,
                    source_vertex_row_labels = None,
                    target_vertex_row_labels = None, delimiter = ',',
                    column_mapping = None, suppress_errors = None,
                    on_duplicate_keys = None, row_filter = None,
                    chunk_size = DEFAULT_CHUNK_SIZE, **kwargs):
      # If any paths have * or ? etc, try to expand those cases to real files.
      final_paths = []
      for path in paths:
        glob_paths = glob.glob(path)
        final_paths += glob_paths if glob_paths != [] else [path]

      parquet_paths, other_paths = _split_local_paths(final_paths)

      # TODO (josh) : Somehow make this a single transaction for multiple paths
      #               between grpc end point and arrow flight?
      job = None
      if len(parquet_paths) > 0:
        job = self._insert_from_parquet(parquet_paths, header_mode, row_labels,
                                        row_label_columns,
                                        source_vertex_row_labels,
                                        target_vertex_row_labels,
                                        column_mapping, suppress_errors,
                                        on_duplicate_keys, row_filter,
                                        chunk_size, **kwargs)
      if len(other_paths) > 0:
        job = self._insert_from_csv(other_paths, header_mode, row_labels,
                                    row_label_columns, source_vertex_row_labels,
                                    target_vertex_row_labels, delimiter,
                                    column_mapping, suppress_errors,
                                    on_duplicate_keys, row_filter, **kwargs)
      return job

  # Returns last job run.
  def _insert_from_parquet(self, paths, header_mode = HeaderMode.NONE,
                           row_labels = None, row_label_columns = None,
                           source_vertex_row_labels = None,
                           target_vertex_row_labels = None,
                           column_mapping = None, suppress_errors = None,
                           on_duplicate_keys = None, row_filter = None,
                           chunk_size = DEFAULT_CHUNK_SIZE, **kwargs):
    flight_path = self._build_flight_path(row_labels, row_label_columns,
                                          suppress_errors,
                                          source_vertex_row_labels,
                                          target_vertex_row_labels,
                                          column_mapping, on_duplicate_keys,
                                          row_filter, **kwargs)
    job = None
    # TODO (josh) : Somehow make this a single transaction for
    #               multiple paths and different schemas?
    try:
      for path in paths:
        file = pyarrow.parquet.ParquetFile(path)
        writer, metadata = self._conn.arrow_conn.do_put(
          pyarrow.flight.FlightDescriptor.for_path(*flight_path),
                                                   file.schema_arrow)
        batches = file.iter_batches(batch_size = chunk_size)
        for batch in batches:
          writer.write_batch(batch)

        # Write an empty batch with metadata to indicate we are done.
        empty = [[]] * len(file.schema_arrow)
        empty_batch = pyarrow.RecordBatch.from_arrays(
            empty, schema = file.schema_arrow)
        metadata_end = struct.pack('<i', 0)
        writer.write_with_metadata(empty_batch, metadata_end)
        buf = metadata.read()
        job_proto = sch_proto.JobStatus()
        if buf is not None:
          job_proto.ParseFromString(buf.to_pybytes())

        writer.close()
        job = Job(self._conn, job_proto)
        job_data = job.get_ingest_errors()

        if job_data is not None and len(job_data) > 0:
          raise XgtIOError(self._create_ingest_error_message(job), job = job)

    except pyarrow._flight.FlightServerError as err:
      raise _convert_flight_server_error_into_xgt(err) from err
    except pyarrow._flight.FlightUnavailableError as err:
      raise XgtConnectionError(str(err)) from err
    except FileNotFoundError as err:
      raise XgtIOError(str(err)) from err

    return job

  def _insert_from_csv(self, paths, header_mode = HeaderMode.NONE,
                       row_labels = None, row_label_columns = None,
                       source_vertex_row_labels = None,
                       target_vertex_row_labels = None, delimiter = ',',
                       column_mapping = None, suppress_errors = None,
                       on_duplicate_keys = None, row_filter = None, **kwargs):
    data_iter = self._insert_csv_packet_generator(paths, header_mode,
                                                  row_labels, row_label_columns,
                                                  source_vertex_row_labels,
                                                  target_vertex_row_labels,
                                                  delimiter,
                                                  column_mapping,
                                                  suppress_errors,
                                                  on_duplicate_keys,
                                                  row_filter, **kwargs)
    response = self._conn._call(data_iter, self._conn._data_svc.UploadData)
    job = Job(self._conn, response.job_status)
    job_data = job.get_ingest_errors()

    if job_data is not None and len(job_data) > 0:
      raise XgtIOError(self._create_ingest_error_message(job), job = job)

    return job

  def _ingest(self, paths, header_mode = HeaderMode.NONE,
              row_labels = None, row_label_columns = None,
              source_vertex_row_labels = None,
              target_vertex_row_labels = None, delimiter = ',',
              column_mapping = None, suppress_errors = None,
              on_duplicate_keys = None, row_filter = None, **kwargs):
    request = data_proto.IngestUriRequest()
    request.frame_name = self._name
    request = _row_level_labels_helper(request, row_labels, row_label_columns,
                                       source_vertex_row_labels,
                                       target_vertex_row_labels, header_mode)

    if isinstance(paths, (list, tuple)):
      request.content_uri.extend(paths)
    else:
      request.content_uri.extend([paths])

    _convert_header_mode(header_mode, request)

    # Set the mapping of frame column to file source.
    if column_mapping is not None:
      request.column_mapping.CopyFrom(
        _set_column_mapping_in_ingest_request(column_mapping))

    request.suppress_errors = suppress_errors
    request.on_duplicate_keys = on_duplicate_keys

    if (len(self._conn.aws_access_key_id) > 0 and
        len(self._conn.aws_secret_access_key) > 0):
      request.authorization = self._conn.aws_access_key_id + ':' + \
                              self._conn.aws_secret_access_key + ':' + \
                              self._conn.aws_session_token

    request.implicit_vertices = True
    request.delimiter = delimiter
    if row_filter is not None:
      request.row_filter = row_filter

    for k,v in kwargs.items():
      if isinstance(v, bool):
        request.kwargs[k].bool_value = v
      elif isinstance(v, int):
        request.kwargs[k].int_value = v
      elif isinstance(v, float):
        request.kwargs[k].float_value = v
      elif isinstance(v, str):
        request.kwargs[k].string_value = v

    response = self._conn._call(iter([ request ]), self._conn._data_svc.IngestUri)
    job = Job(self._conn, response.job_status)
    job_data = job.get_ingest_errors()

    if job_data is not None and len(job_data) > 0:
      raise XgtIOError(self._create_ingest_error_message(job), job = job)

    return job

  def _local_egest(self, path, offset = 0, length = None, headers = False,
                   include_row_labels = False, row_label_column_header = None,
                   preserve_order = False, duration_as_interval = False,
                   delimiter: str = ',', row_filter = None,
                   windows_newline = False, **kwargs):
    extension = os.path.splitext(path)[-1]
    if extension == ".parquet":
      return self._save_to_parquet(path, offset, length, include_row_labels,
                                   row_label_column_header, preserve_order,
                                   duration_as_interval, row_filter, **kwargs)
    else:
      return self._save_to_csv(path, offset, length, headers,
                               include_row_labels, row_label_column_header,
                               preserve_order, delimiter,
                               row_filter, windows_newline, **kwargs)

  def _save_to_parquet(self, path, offset = 0, length = None,
                       include_row_labels = False,
                       row_label_column_header = None, preserve_order = False,
                       duration_as_interval = False, row_filter = None,
                       **kwargs):
    ticket = _create_flight_ticket(
               self, self._name, offset, length,
               include_row_labels = include_row_labels,
               row_label_column_header = row_label_column_header,
               order = preserve_order,
               duration_as_interval = duration_as_interval,
               row_filter = row_filter, **kwargs)

    try:
      reader = self._conn.arrow_conn.do_get(pyarrow.flight.Ticket(ticket))
      first_batch = reader.read_chunk()
      with pyarrow.parquet.ParquetWriter(path, first_batch.data.schema,
                                         version = '2.6') as writer:
        writer.write_batch(first_batch.data)
        for batch in reader:
          writer.write_batch(batch.data)
    except pyarrow._flight.FlightServerError as err:
      raise _convert_flight_server_error_into_xgt(err) from err
    except pyarrow._flight.FlightUnavailableError as err:
      raise XgtConnectionError(str(err)) from err

    return Job(self._conn)

  def _save_to_csv(self, path, offset = 0, length = None, headers = False,
                   include_row_labels = False, row_label_column_header = None,
                   preserve_order = False, delimiter: str = ',',
                   row_filter = None, windows_newline = False, **kwargs):
    # This will stream the bytes directly which is > 10X faster than using
    # JSON.
    responses = self._get_data_csv(
        offset = offset, length = length, headers = headers,
        include_row_labels = include_row_labels,
        row_label_column_header = row_label_column_header,
        preserve_order = preserve_order, delimiter = delimiter,
        row_filter = row_filter, windows_newline = windows_newline, **kwargs)

    job_status = None

    with open(path, 'wb') as fobject:
      # Each packet can be directly written to the file since we have the raw
      # data. This avoids extra conversion issues and extra memory from JSON.
      for response in responses:
          _assert_noerrors(response)
          fobject.write(response.content)
          if response.HasField("job_status"):
            if job_status is None:
              job_status = response.job_status
            else:
              raise XgtInternalError('Job status already set in packet stream')

    fobject.close()
    return job_status

  def _egest(self, path, offset = 0, length = None, headers = False,
             include_row_labels = False, row_label_column_header = None,
             preserve_order = False, number_of_files = 1,
             duration_as_interval = False, delimiter: str = ',',
             row_filter = None, windows_newline = False, **kwargs):
    if isinstance(offset, str):
      offset = int(offset)
    if isinstance(length, str):
      length = int(length)
    if isinstance(offset, int):
      if offset < 0:
        raise ValueError('offset is negative')
    if isinstance(length, int):
      if length < 0:
        raise ValueError('length is negative')

    request = data_proto.EgestUriRequest()
    request.frame_name = self._name
    request.file_name = path
    request.with_headers = headers
    request.preserve_order = preserve_order
    request.number_of_files = number_of_files
    request.duration_as_interval = duration_as_interval
    request.offset.value = offset
    request.delimiter = delimiter
    if length is not None:
      request.length.value = length

    if (len(self._conn.aws_access_key_id) > 0 and
        len(self._conn.aws_secret_access_key) > 0):
      request.authorization = self._conn.aws_access_key_id + ':' + \
                              self._conn.aws_secret_access_key + ':' + \
                              self._conn.aws_session_token

    request.row_labels.egest_labels = include_row_labels
    if row_label_column_header is not None:
      request.row_labels.label_header_name = row_label_column_header
    else:
      request.row_labels.label_header_name = "ROWLABEL"

    if row_filter is not None:
      request.row_filter = row_filter

    if windows_newline:
      request.windows_newline.value = True

    for k,v in kwargs.items():
      if isinstance(v, bool):
        request.kwargs[k].bool_value = v
      elif isinstance(v, int):
        request.kwargs[k].int_value = v
      elif isinstance(v, float):
        request.kwargs[k].float_value = v
      elif isinstance(v, str):
        request.kwargs[k].string_value = v

    response = self._conn._call(request, self._conn._data_svc.EgestUri)
    return Job(self._conn, response.job_status)

  def _create_ingest_error_message(self, job):
    num_errors = job.total_ingest_errors

    error_string = ('Errors occurred when inserting data into frame '
                    f'{self._name}.\n')

    error_string += f'  {num_errors} line'
    if num_errors > 1:
      error_string += 's'

    error_string += (' had insertion errors.\n'
                     '  Lines without errors were inserted into the frame.\n'
                     '  To see the number of rows in the frame, run "'
                     f'{self._name}.num_rows".\n'
                     '  To see the data in the frame, run "'
                     f'{self._name}.get_data()".\n')

    extra_text = ''
    if num_errors > 10:
      extra_text = ' first 10'

    error_string += (f'Errors associated with the{extra_text} lines '
                     'that could not be inserted are shown below:')

    # Only print the first 10 messages.
    for error in job.get_ingest_errors(0, 10):
      delim = ','

      # Will process a list of strings. Convert to this format.
      if isinstance(error, str):
        error_cols = error.split(delim)
      elif isinstance(error, list):
        error_cols = [str(elem) for elem in error]
      else:
        raise XgtIOError("Error processing ingest error message.")

      # The first comma separated fields of the error string are the error
      # description, file name, and line number.
      error_explanation = "" if len(error_cols) < 1 else error_cols[0]
      error_file_name = \
          "" if len(error_cols) < 2 else os.path.basename(error_cols[1])
      error_line_number = "" if len(error_cols) < 3 else error_cols[2]

      # The second part of the error string contains the line that caused the
      # error. The line contains comma separated fields so we need to re-join
      # these comma separated portions to get back the line.
      line_with_error = \
          "" if len(error_cols) < 4 else delim.join(error_cols[3:])

      if error_line_number == -1:
        error_string += f"\n {error_explanation}"
      else:
        error_string += (f"\n  File: {error_file_name}: Line: "
                         f"{error_line_number}: {error_explanation}")

    return error_string

  def _validate_common_load_params(self, row_labels, row_label_columns,
                                   column_mapping, suppress_errors,
                                   row_filter):
    _validate_row_level_labels_for_ingest(row_labels, row_label_columns)
    _validate_column_mapping_in_ingest(column_mapping)

    if not isinstance(suppress_errors, bool):
      raise TypeError("suppress_errors expected to be bool.")

    if row_filter is not None and not isinstance(row_filter, str):
      raise TypeError("row_filter expected to be a string.")

    return (column_mapping, row_filter)

  def _graphs(self):
    request = graph_proto.GetGraphsForFrameRequest()
    request.name = self.name
    response = self._conn._call(request,
                                self._conn._graph_svc.GetGraphsForFrame)
    return set(response.graphs)

# -----------------------------------------------------------------------------

class VertexFrame(TableFrame):
  """
  A VertexFrame represents a collection of vertices held on the xGT server.  It
  can be used to retrieve information about the frame and the vertex properties.
  A VertexFrame should not be instantiated directly by the user.  Instead it is
  created by the method `Connection.create_vertex_frame()`.

  Methods that return this object: :py:meth:`Connection.get_frame`,
  `Connection.get_frames()` and `Connection.create_vertex_frame()`.

  Each vertex in a VertexFrame shares the same properties, described in the
  frame's schema. Each vertex in the frame is uniquely identified by the
  schema property listed in `VertexFrame.key`.

  Parameters
  ----------
  conn : Connection
    An open connection to an xGT server.
  name : str
    Fully qualified name of the vertex frame, including the namespace.
  schema : Iterable[list[Any] | tuple[Any]]
    The schema defining the property names and types.  Each vertex in the frame
    will have these properties.  Given as a list of lists associating property
    names with xGT data types.
  key : str
    The schema property name used to uniquely identify vertices in the graph.
    The property's value must be unique for each vertex in the frame.
  container_id : int
    The ID of the frame's container on the server.
  commit_id : int
    The ID of the last commit to the frame.

  Examples
  --------
  >>> import xgt
  >>> conn = xgt.Connection()
  >>> v1 = conn.create_vertex_frame(
  ...        name = 'People',
  ...        schema = [['id', xgt.INT],
  ...                  ['name', xgt.TEXT]],
  ...        key = 'id')
  >>> v2 = conn.get_frame('Companies') # An existing vertex frame
  >>> print(v1.name, v2.name)
  """
  def __init__(self, conn : Connection, name : str,
               schema : Iterable[Union[list[Any], tuple[Any]]],
               key : str, container_id : int, commit_id : int):
    """Constructor for VertexFrame. Called when VertexFrame is created."""
    super(VertexFrame, self).__init__(conn, name, schema,
                                      container_id, commit_id)
    self._key = key

  def __str__(self):
    return (f"{{'name': '{self.name}'"
            f", 'schema': {str(self.schema)}"
            f", 'key': '{self.key}'}}")

  @property
  def num_vertices(self) -> int:
    """The number of vertices in the VertexFrame."""
    return self.num_rows

  @property
  def key(self) -> str:
    """The property name that uniquely identifies vertices of this type."""
    return self._key

  @property
  def key_column(self) -> int:
    """The column position of the frame's key."""
    request = graph_proto.GetFrameSchemaRequest()
    request.name = self._name
    response = self._conn._call(request, self._conn._graph_svc.GetFrameSchema)
    return self._conn._server_schema_col_name_to_position(response.schema,
                                                          self._key)

  @property
  def graphs(self) -> set[str]:
    """
    The names of the graphs that the frame belongs to.
    Only includes graphs the user has permissions to see.

    .. experimental:: The API of this property may change in future releases.
    """
    return self._graphs()

  def load(self, paths : Union[Iterable[str], str],
           header_mode : str = HeaderMode.NONE,
           record_history : bool = True,
           row_labels : Optional[Iterable[str]] = None,
           row_label_columns : Optional[Iterable[Union[str, int]]] = None,
           delimiter : str = ',',
           column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
           suppress_errors : bool = False, row_filter : Optional[str] = None,
           chunk_size : int = DEFAULT_CHUNK_SIZE,
           on_duplicate_keys : str = 'error') -> Job:
    """
    Loads data from one or more files specified in the list of paths.  These
    files may be CSV, Parquet, or compressed CSV.  Some limitations exist for
    compressed CSV.  See docs.rocketgraph.com for more details.  Each
    path may have its own protocol as described below.

    Parameters
    ----------
    paths : list or str
      A single path or a list of paths to files.  Local or server paths may
      contain wildcards.  Wildcard expressions can contain *, ?, range sets,
      and negation.  See docs.rocketgraph.com for more details.

      ==================== =====================================
                      Syntax for one file path
      ----------------------------------------------------------
          Resource type                 Path syntax
      ==================== =====================================
          local to Python: '<path to file>'
                           'xgt://<path to file>'
          xGT server:      'xgtd://<path to file>'
          AWS S3:          's3://<path to file>'
          https site:      'https://<path to file>'
          http site:       'http://<path to file>'
          ftps server:     'ftps://<path to file>'
          ftp server:      'ftp://<path to file>'
      ==================== =====================================
    header_mode : str
      Indicates how the file header should be processed:
        - HeaderMode.NONE:
          No header exists.
        - HeaderMode.IGNORE:
          Ignore the first line containing the header.
        - HeaderMode.NORMAL:
          Process the header in non-strict mode. If a schema column is missing,
          a null value is ingested for that schema column. Any file column
          whose name does not correspond to a schema column or a security label
          column is ignored.
        - HeaderMode.STRICT:
          Process the header in strict mode. The name of each header column
          should correspond to a schema column, a security label column, or be
          named IGNORE. Each schema column must appear in the file.

      Only applies to CSV files.

      .. versionadded:: 1.11.0
    record_history : bool
      If true, records the history of the job.
    row_labels : list
      A list of security labels to attach to each row inserted with the load.
      Each label must have been passed in to the row_label_universe parameter
      when creating the frame. Note: Only one of row_labels and
      row_label_columns must be passed.
    row_label_columns: list
      A list of columns indicating which columns in the CSV file contain
      security labels to attach to the inserted row. If the header mode is NONE
      or IGNORE, this must be a list of integer column indices. If the header
      mode is NORMAL or STRICT, this must be a list of string column names.
      Note: Only one of row_labels and row_label_columns must be passed.
    delimiter : str
      Single character delimiter for CSV data. Only applies to CSV files.
    column_mapping : dictionary
      Maps the frame column names to file columns for the ingest. The key of
      each element is a frame column name. The value is either the name of the
      file column (from the file header) or the file column index. If file
      column names are used, the header_mode must be NORMAL. If only file column
      indices are used, the header_mode can be NORMAL, NONE, or
      IGNORE.

      .. versionadded:: 1.15.0
    suppress_errors : bool
      If true, continues to load data if an ingest error is encountered,
      placing the first 1000 errors into the job history.  If false, stops on
      first error and raises. Defaults to False.

      .. versionadded:: 1.11.0
    row_filter : str
      OpenCypher fragment used to filter, modify and parameterize the raw data
      from the input to produce the row data fed to the frame.

      .. versionadded:: 1.15.0
    chunk_size : int
      Number of rows to transfer in a single Arrow chunk between the client and
      the server.

      .. versionadded:: 1.16.0
    on_duplicate_keys : str
      Specifies what to do upon encountering a duplicate key.  Allowed values
      are:
        - 'error': Raise an Exception when a duplicate key is found.
        - 'skip': Skip duplicate keys without raising.
        - 'skip_same': Skip duplicate keys if the row is exactly the same
          without raising.

      .. versionadded:: 1.12.0

    Returns
    -------
    Job
      A Job object representing the job that has executed the load.

    Raises
    ------
    XgtIOError
      If a file specified cannot be opened or if there are errors inserting any
      lines in the file into the frame.
    XgtNameError
      If the frame does not exist on the server.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    return self._load(
               paths, header_mode, record_history, row_labels,
               row_label_columns, delimiter = delimiter,
               column_mapping = column_mapping,
               suppress_errors = suppress_errors, row_filter = row_filter,
               chunk_size = chunk_size, on_duplicate_keys = on_duplicate_keys)

  def insert(self, data : Union[Iterable[Iterable[Any]],
                                pandas.DataFrame, pyarrow.Table],
             row_labels : Optional[Iterable[str]] = None,
             row_label_columns : Optional[Iterable[int]] = None,
             column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
             suppress_errors : bool = False, on_duplicate_keys : str = 'error',
             row_filter : Optional[str] = None,
             chunk_size : int = DEFAULT_CHUNK_SIZE) -> Job:
    """
    Inserts data rows. The properties of the new data must match the schema in
    both order and type.

    Parameters
    ----------
    data : Iterable[Iterable[Any]] | pandas.DataFrame | pyarrow.Table
      Data represented by a list of lists of data items, by a pandas
      DataFrame or by a pyarrow Table.
    row_labels : Iterable[str] | None
      A list of security labels to attach to each row inserted.  Each label
      must have been passed in to the row_label_universe parameter when
      creating the frame. Note: Only one of row_labels and row_label_columns
      must be passed.
    row_label_columns : Iterable[int] | None
      A list of integer column indices indicating which columns in the input
      data contain security labels to attach to the inserted row. Note: Only
      one of row_labels and row_label_columns must be passed.
    column_mapping : Mapping[str, str | int] | None
      Maps the frame column names to input columns for the ingest. The key of
      each element is a frame column name. The value is either the name of the
      column (from the Pandas frame or xGT schema column name for lists) or the
      file column index.

      .. versionadded:: 1.15.0
    suppress_errors : bool
      If true, will continue to insert data if an ingest error is encountered,
      placing the first 1000 errors in the job history. If false, stops on
      first error and raises.  Defaults to False.

      .. versionadded:: 1.11.0
    row_filter : str | None
      OpenCypher fragment used to filter, modify and parameterize the raw data
      from the input to produce the row data fed to the frame.

      .. versionadded:: 1.15.0
    on_duplicate_keys : str
      Specifies what to do upon encountering a duplicate key.  Allowed values
      are:
        - 'error': raise an Exception when a duplicate key is found.
        - 'skip': skip duplicate keys without raising.
        - 'skip_same': skip duplicate keys if the row is exactly the same
          without raising.

      .. versionadded:: 1.12.0
    chunk_size : int
      Number of rows to transfer in a single Arrow chunk between the client and
      the server.

      .. versionadded:: 1.16.0

    Returns
    -------
    Job
      A Job object representing the job that has executed the insert.

    Raises
    ------
    XgtIOError
      If there are errors in the data being inserted or some data could
      not be inserted into the frame.
    XgtNameError
      If the frame does not exist on the server.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    if data is None:
      return
    if len(data) == 0:
      return

    column_mapping, row_filter = self._validate_common_load_params(
      row_labels, row_label_columns, column_mapping,
      suppress_errors, row_filter)

    if on_duplicate_keys not in ['error', 'skip', 'skip_same']:
      raise TypeError('on_duplicate_keys must be error, skip, or skip_same.')

    table, invalid_rows = self._build_arrow_table(
      data, row_labels, row_label_columns, suppress_errors,
      column_mapping, row_filter is not None)
    path = self._build_flight_path(
      row_labels, row_label_columns, suppress_errors,
      column_mapping = column_mapping,
      on_duplicate_keys = on_duplicate_keys, row_filter = row_filter)
    return self._write_table_to_flight(table, path, invalid_rows, chunk_size)

# -----------------------------------------------------------------------------

class EdgeFrame(TableFrame):
  """
  An EdgeFrame represents a collection of edges held on the xGT server.  It can
  be used to retrieve information about the frame and the edge properties.  An
  EdgeFrame should not be instantiated directly by the user.  Instead it is
  created by the method `Connection.create_edge_frame()`.

  Methods that return this object: `Connection.get_frame()`,
  `Connection.get_frames()` and `Connection.create_edge_frame()`.

  Each edge in an EdgeFrame shares the same properties, described by the frame's
  schema.  An edge connects a source vertex to a target vertex.
  `EdgeFrame.source_key` gives the schema property that identifies the source
  vertex of each edge.  `EdgeFrame.target_key` gives the schema property that
  identifies the target vertex of each edge.

  The source vertex of each edge in an EdgeFrame must belong to the same
  VertexFrame. The name of the source VertexFrame is given by
  `EdgeFrame.source_name`.  The targe vertex of each edge in an EdgeFrame must
  belong to the same VertexFrame. The name of the target VertexFrame is given by
  `EdgeFrame.target_name`.

  Parameters
  ----------
  conn : Connection
    An open connection to an xGT server.
  name : str
    Fully qualified name of the edge frame, including the namespace.
  schema : Iterable[list[Any] | tuple[Any]]
    The schema defining the property names and types.  Each edge in the frame
    will have these properties.  Given as a list of lists associating property
    names with xGT data types.
  source : str | VertexFrame
    The VertexFrame to which the source of each edge in this EdgeFrame belongs.
    Given as the name of a VertexFrame or a VertexFrame object.
  target : str | VertexFrame
    The VertexFrame to which the target of each edge in this EdgeFrame belongs.
    Given as the name of a VertexFrame or a VertexFrame object.
  source_key : str
    The schema property name that identifies the source vertex of an edge.
  target_key : str
    The schema property name that identifies the target vertex of an edge.
  container_id : int
    The ID of the frame's container on the server.
  commit_id : int
    The ID of the last commit to the frame.

  Examples
  --------
  >>> import xgt
  >>> conn = xgt.Connection()
  >>> e1 = conn.create_edge_frame(
  ...        name = 'WorksFor',
  ...        schema = [['srcid', xgt.INT],
  ...                  ['role', xgt.TEXT],
  ...                  ['trgid', xgt.INT]],
  ...        source = 'People',
  ...        target = 'Companies',
  ...        source_key = 'srcid',
  ...        target_key = 'trgid')
  >>> e2 = conn.get_frame('RelatedTo') # An existing edge frame
  >>> print(e1.name, e2.name)
  """
  def __init__(self, conn : Connection, name : str,
               schema : Iterable[Union[list[Any], tuple[Any]]],
               source : Union[str, VertexFrame],
               target : Union[str, VertexFrame],
               source_key : str, target_key : str,
               container_id : int, commit_id : int):
    """Constructor for EdgeFrame. Called when EdgeFrame is created."""
    super(EdgeFrame, self).__init__(conn, name, schema, container_id, commit_id)
    self._source_name = source
    self._target_name = target
    self._source_key = source_key
    self._target_key = target_key

  def __str__(self):
    return (f"{{'name': '{self.name}'"
            f", 'source': '{self.source_name}'"
            f", 'target': '{self.target_name}'"
            f", 'schema': {str(self.schema)}"
            f", 'source_key': '{self.source_key}'"
            f", 'target_key': '{self.target_key}'}}")

  @property
  def num_edges(self) -> int:
    """The number of edges in the EdgeFrame."""
    return self.num_rows

  @property
  def source_name(self) -> str:
    """The name of the source vertex frame."""
    return self._source_name

  @property
  def target_name(self) -> str:
    """The name of the target vertex frame."""
    return self._target_name

  @property
  def source_key(self) -> str:
    """The edge property name that identifies the source vertex of an edge."""
    return self._source_key

  @property
  def target_key(self) -> str:
    """The edge property name that identifies the target vertex of an edge."""
    return self._target_key

  @property
  def source_key_column(self) -> int:
    """The column position of the frame's source key."""
    request = graph_proto.GetFrameSchemaRequest()
    request.name = self._name
    response = self._conn._call(request, self._conn._graph_svc.GetFrameSchema)
    return self._conn._server_schema_col_name_to_position(response.schema,
                                                          self._source_key)

  @property
  def target_key_column(self) -> int:
    """The column position of the frame's target key."""
    request = graph_proto.GetFrameSchemaRequest()
    request.name = self._name
    response = self._conn._call(request, self._conn._graph_svc.GetFrameSchema)
    return self._conn._server_schema_col_name_to_position(response.schema,
                                                          self._target_key)

  @property
  def graphs(self) -> set[str]:
    """
    The names of the graphs that the frame belongs to.
    Only includes graphs the user has permissions to see.

    .. experimental:: The API of this property may change in future releases.
    """
    return self._graphs()

  def load(self, paths : Union[Iterable[str], str],
           header_mode : str = HeaderMode.NONE,
           record_history : bool = True,
           row_labels : Optional[Iterable[str]] = None,
           row_label_columns : Optional[Iterable[Union[str, int]]] = None,
           source_vertex_row_labels : Optional[Iterable[str]] = None,
           target_vertex_row_labels : Optional[Iterable[str]] = None,
           delimiter : str = ',',
           column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
           suppress_errors : bool = False, row_filter : Optional[str] = None,
           chunk_size : int = DEFAULT_CHUNK_SIZE) -> Job:
    """
    Loads data from one or more files specified in the list of paths.  These
    files may be CSV, Parquet, or compressed CSV.  Some limitations exist for
    compressed CSV.  See docs.rocketgraph.com for more details.  Each
    path may have its own protocol as described below.

    Parameters
    ----------
    paths : Iterable[str] | str
      A single path or a list of paths to files.  Local or server paths may
      contain wildcards.  Wildcard expressions can contain *, ?, range sets,
      and negation.  See docs.rocketgraph.com for more details.

      ==================== =====================================
                      Syntax for one file path
      ----------------------------------------------------------
          Resource type                 Path syntax
      ==================== =====================================
          local to Python: '<path to file>'
                           'xgt://<path to file>'
          xGT server:      'xgtd://<path to file>'
          AWS S3:          's3://<path to file>'
          https site:      'https://<path to file>'
          http site:       'http://<path to file>'
          ftps server:     'ftps://<path to file>'
          ftp server:      'ftp://<path to file>'
      ==================== =====================================
    header_mode : str
      Indicates how the file header should be processed:
        - HeaderMode.NONE:
          No header exists.
        - HeaderMode.IGNORE:
          Ignore the first line containing the header.
        - HeaderMode.NORMAL:
          Process the header in non-strict mode. If a schema column is missing,
          a null value is ingested for that schema column. Any file column
          whose name does not correspond to a schema column or a security label
          column is ignored.
        - HeaderMode.STRICT:
          Process the header in strict mode. The name of each header column
          should correspond to a schema column, a security label column, or be
          named IGNORE. Each schema column must appear in the file.

      Only applies to CSV files.

      .. versionadded:: 1.11.0
    record_history : bool
      If true, records the history of the job.
    row_labels : Iterable[str] | None
      A list of security labels to attach to each row inserted with the load.
      Each label must have been passed in to the row_label_universe parameter
      when creating the frame. Note: Only one of row_labels and
      row_label_columns must be passed.
    row_label_columns: Iterable[str | int] | None
      A list of columns indicating which columns in the CSV file contain
      security labels to attach to the inserted row. If the header mode is NONE
      or IGNORE, this must be a list of integer column indices. If the header
      mode is NORMAL or STRICT, this must be a list of string column names.
      Note: Only one of row_labels and row_label_columns must be passed.
    source_vertex_row_labels : Iterable[str] | None
      A list of security labels to attach to each source vertex that is
      implicitly inserted. Each label must have been passed in to the
      row_label_universe parameter when creating the frame.
    target_vertex_row_labels : Iterable[str] | None
      A list of security labels to attach to each target vertex that is
      implicitly inserted. Each label must have been passed in to the
      row_label_universe parameter when creating the frame.
    delimiter : str
      Single character delimiter for CSV data. Only applies to CSV files.
    column_mapping : Mapping[str, str | int] | None
      Maps the frame column names to file columns for the ingest. The key of
      each element is a frame column name. The value is either the name of the
      file column (from the file header) or the file column index. If file
      column names are used, the header_mode must be NORMAL. If only file column
      indices are used, the header_mode can be NORMAL, NONE, or
      IGNORE.

      .. versionadded:: 1.15.0
    suppress_errors : bool
      If true, continues to load data if an ingest error is encountered,
      placing the first 1000 errors into the job history.  If false, stops on
      first error and raises. Defaults to False.

      .. versionadded:: 1.11.0
    row_filter : str | None
      OpenCypher fragment used to filter, modify and parameterize the raw data
      from the input to produce the row data fed to the frame.

      .. versionadded:: 1.15.0
    chunk_size : int
      Number of rows to transfer in a single Arrow chunk between the client and
      the server.

      .. versionadded:: 1.16.0

    Returns
    -------
    Job
      A Job object representing the job that has executed the load.

    Raises
    ------
    XgtIOError
      If a file specified cannot be opened or if there are errors inserting any
      lines in the file into the frame.
    XgtNameError
      If the frame does not exist on the server.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    return self._load(
               paths, header_mode, record_history,
               row_labels, row_label_columns, source_vertex_row_labels,
               target_vertex_row_labels, delimiter,
               column_mapping = column_mapping,
               suppress_errors = suppress_errors, row_filter = row_filter,
               chunk_size = chunk_size)

  def insert(self, data : Union[Iterable[Iterable[Any]],
                                pandas.DataFrame, pyarrow.Table],
             row_labels : Optional[Iterable[str]] = None,
             row_label_columns : Optional[Iterable[int]] = None,
             source_vertex_row_labels : Optional[Iterable[str]] = None,
             target_vertex_row_labels : Optional[Iterable[str]] = None,
             column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
             suppress_errors : bool = False, row_filter : Optional[str] = None,
             chunk_size : int = DEFAULT_CHUNK_SIZE) -> Job:
    """
    Inserts data rows. The properties of the new data must match the schema in
    both order and type.

    Parameters
    ----------
    data : Iterable[Iterable[Any]] | pandas.DataFrame | pyarrow.Table
      Data represented by a list of lists of data items, by a pandas
      DataFrame or by a pyarrow Table.
    row_labels : Iterable[str] | None
      A list of security labels to attach to each row inserted.  Each label
      must have been passed in to the row_label_universe parameter when
      creating the frame. Note: Only one of row_labels and row_label_columns
      must be passed.
    row_label_columns : Iterable[int] | None
      A list of integer column indices indicating which columns in the input
      data contain security labels to attach to the inserted row. Note: Only
      one of row_labels and row_label_columns must be passed.
    source_vertex_row_labels : Iterable[str] | None
      A list of security labels to attach to each source vertex that is
      implicitly inserted. Each label must have been passed in to the
      row_label_universe parameter when creating the frame.
    target_vertex_row_labels : Iterable[str] | None
      A list of security labels to attach to each target vertex that is
      implicitly inserted. Each label must have been passed in to the
      row_label_universe parameter when creating the frame.
    column_mapping : Mapping[str, str | int] | None
      Maps the frame column names to input columns for the ingest. The key of
      each element is a frame column name. The value is either the name of the
      column (from the Pandas frame or xGT schema column name for lists) or the
      file column index.

      .. versionadded:: 1.15.0
    suppress_errors : bool
      If true, will continue to insert data if an ingest error is encountered,
      placing the first 1000 errors in the job history. If false, stops on
      first error and raises.  Defaults to False.

      .. versionadded:: 1.11.0
    row_filter : str | None
      OpenCypher fragment used to filter, modify and parameterize the raw data
      from the input to produce the row data fed to the frame.

      .. versionadded:: 1.15.0
    chunk_size : int
      Number of rows to transfer in a single Arrow chunk between the client and
      the server.

      .. versionadded:: 1.16.0

    Returns
    -------
    Job
      A Job object representing the job that has executed the insert.

    Raises
    ------
    XgtIOError
      If there are errors in the data being inserted or some data could
      not be inserted into the frame.
    XgtNameError
      If the frame does not exist on the server.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    if data is None:
      return
    if len(data) == 0:
      return

    column_mapping, row_filter = self._validate_common_load_params(
      row_labels, row_label_columns, column_mapping,
      suppress_errors, row_filter)

    _validate_row_level_labels_for_ingest(source_vertex_row_labels)
    _validate_row_level_labels_for_ingest(target_vertex_row_labels)

    table, invalid_rows = self._build_arrow_table(
      data, row_labels, row_label_columns, suppress_errors,
      column_mapping, row_filter is not None)
    path = self._build_flight_path(
      row_labels, row_label_columns, suppress_errors,
      source_vertex_row_labels, target_vertex_row_labels,
      column_mapping = column_mapping, row_filter = row_filter)
    return self._write_table_to_flight(table, path, invalid_rows, chunk_size)

# -----------------------------------------------------------------------------

class GraphFrame(object):
  """
  A GraphFrame object represents a grouping of vertex and edge frames that make
  a logical graph.  A GraphFrame should not be instantiated directly by the
  user.  Instead it is created by the method `Connection.create_graph_frame()`.

  Methods that return this object: `Connection.get_frame()`,
  `Connection.get_frames()` and `Connection.create_graph_frame()`.

  Parameters
  ----------
  conn : Connection
    An open connection to an xGT server.
  name : str
    Fully qualified name of the graph, including the namespace.
  container_id : int
    The ID of the graph's container on the server.

  Examples
  --------
  >>> import xgt
  >>> conn = xgt.Connection()
  >>> g = conn.create_graph_frame('MyGraph', { 'v0' : 'Vertex0',
  >>>                                          'v1' : 'other__Vertex0',
  >>>                                          'e'  : 'Edge' })
  >>> print(g.name)

  .. experimental:: The API of this class may change in future releases.
  """
  def __init__(self, conn : Connection, name : str, container_id : int):
    """Constructor for GraphFrame. Called when GraphFrame is created."""
    self._conn = conn
    self._name = name
    self._container_id = container_id

  def __str__(self):
    return f"{{ 'name': '{self.name}', 'members': {str(self.graph_members)} }}"

  @property
  def name(self) -> str:
    """Name of the graph frame."""
    return self._name

  @property
  def connection(self) -> Connection :
    """The connection used when constructing the frame."""
    return self._conn

  @property
  def graph_members(self) -> dict[str, str]:
    """
    The frames belonging to this graph.  Given as a dictionary mapping aliases
    to frame names.
    """
    request = graph_proto.GetFramesInGraphRequest()
    request.name = self._name
    response = self._conn._call(request, self._conn._graph_svc.GetFramesInGraph)
    return dict(response.frames)

  def add_frames(
      self,
      graph_members : Union[dict[str, Union[str, VertexFrame, EdgeFrame]],
                            set[Union[str, VertexFrame, EdgeFrame]]]) -> None:
    """
    Add frames to the graph.  The new frames are given as either a dictionary
    mapping aliases to frames or a set of frames.  The frames can be any of
    names, aliases, VertexFrames, and EdgeFrames.  If a frame is given without
    an alias, it is given an alias of its fully qualified name.

    Parameters
    ----------
    graph_members: dictionary[str | VertexFrame | EdgeFrame] | set[str | VertexFrame | EdgeFrame]
      Dictionary mapping aliases to frames or a set of frames to add to the
      graph.

    Raises
    ------
    XgtNameError
      If a frame specified in the dictionary or set does not exist in the
      system.
    XgtTypeError
      If the graph members are not a dictionary mapping strings to strings,
      VertexFrames, or EdgeFrames or a set of strings, VertexFrames, or
      EdgeFrames or if the request specifies a frame which is not a vertex or
      edge frame.
    """

    request = graph_proto.AddFramesToGraphRequest()
    request.name = self._name
    for key, value in _process_graph_members(graph_members).items():
      request.frames[key] = value
    response = self._conn._call(request, self._conn._graph_svc.AddFramesToGraph)

  def remove_frames(self, graph_members : set[Union[str, VertexFrame,
                                                    EdgeFrame]]) -> None:
    """
    Remove frames from the graph.  The frames are given as a set containing any
    of names, aliases, VertexFrames, and EdgeFrames.

    Parameters
    ----------
    graph_members: set[str | VertexFrame | EdgeFrame]
      Set of frames to be removed from the graph.

    Raises
    ------
    XgtTypeError
      If the graph members are not a set of strings, VertexFrames, or
      EdgeFrames.
    """
    members_actual = set()

    if isinstance(graph_members, set):
      for member in graph_members:
        if isinstance(member, str):
          members_actual.add(member)
        elif isinstance(member, VertexFrame) or isinstance(member, EdgeFrame):
          members_actual.add(member.name)
        else:
          raise XgtTypeError('Graph frame to be removed must be a string or ' +
                             'vertex/edge frame instance: ' + str(member))
    else:
      raise XgtTypeError('Graph members to be removed must be a set of ' +
                         'strings or vertex/edge frame instances')

    request = graph_proto.RemoveFramesFromGraphRequest()
    request.name = self._name
    request.frames.extend([ member for member in members_actual ])
    response = self._conn._call(request,
                                self._conn._graph_svc.RemoveFramesFromGraph)
