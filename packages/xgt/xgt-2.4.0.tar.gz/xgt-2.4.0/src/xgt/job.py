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

import logging
import pyarrow

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Optional, Union, TYPE_CHECKING

from . import ErrorMessages_pb2 as err_proto
from . import JobService_pb2 as job_proto
from . import SchemaMessages_pb2 as sch_proto
from .common import (XgtError, XgtInternalError, XgtNotImplemented,
                     XgtTypeError, XgtValueError, XgtErrorTypes,
                     _create_flight_ticket, _verify_offset_length,
                     _validated_columns, _get_data_python_from_table,
                     _get_data_pandas_from_table,
                     _get_data_arrow, _code_error_map, _deprecated)

if TYPE_CHECKING:
  try:
    import pandas
  except ImportError:
    pass

log = logging.getLogger(__name__)

class _QueryPlan(object):
  class _QueryPlanSingleFrame(object):
    def __init__(self, query_element_message):
      self._label = query_element_message.source_label
      self._frame = query_element_message.source_frame

    @property
    def name(self):
      return f"{self._label}:{self._frame}"

    def __str__(self):
      return f"({self._label}:{self._frame})"

  class _QueryPlanEdge(object):
    def __init__(self, query_edge_message):
      if (query_edge_message.edge_direction ==
            sch_proto.QueryEdgeDirection.Value('FORWARD')):
        self.forward_edge = True
      else:
        self.forward_edge = False
      self._source_label = query_edge_message.source_label
      self._source_frame = query_edge_message.source_frame
      self._edge_label = query_edge_message.edge_label
      self._edge_frame = query_edge_message.edge_frame
      self._target_label = query_edge_message.target_label
      self._target_frame = query_edge_message.target_frame

    @property
    def name(self):
      return f"{self._edge_label}:{self._edge_frame}"

    @property
    def edge_name(self):
      return f"{self._edge_label}:{self._edge_frame}"

    @property
    def source_name(self):
      return f"{self._source_label}:{self._source_frame}"

    @property
    def target_name(self):
      return f"{self._target_label}:{self._target_frame}"

    # The string representation of a _QueryPlanEdge object is a tuple
    # of the source vertex, edge, and target vertex. The direction
    # of the edge is always forward.
    def __str__(self):
      if self.forward_edge:
        vertex1 = self.source_name
        vertex2 = self.target_name
      else:
        vertex2 = self.source_name
        vertex1 = self.target_name
      return f"({vertex1}, {self.edge_name}, {vertex2})"

  def __init__(self, query_plan_response):
    # The _plan member is a list of lists. Each list represents a query
    # that starts with MATCH in cypher and contains elements representing
    # edges or (if only a single frame was matched), a vertex or table.
    self._plan = []
    for query in query_plan_response.plan_as_edge_list:
      query_representation = []
      plan_score = None
      for element in query.edges:
        if (element.edge_direction ==
              sch_proto.QueryEdgeDirection.Value('NOT_EDGE')):
          query_representation.append(self._QueryPlanSingleFrame(element))
        else:
          query_representation.append(self._QueryPlanEdge(element))
      if query.HasField("plan_score"):
        plan_score = query.plan_score
      self._plan.append((query_representation, plan_score))

  def __str__(self):
    as_string = ""
    for (idx, query) in enumerate(self._plan):
      if idx > 0:
        as_string += "\n"
      if len(query[0]) > 0:
        as_string += "QUERY:"
        for element in query[0]:
          as_string += f"\n{element}"
    return as_string

  def to_cypher(self):
    cypher = ""
    for query, score in self._plan:
      # The corresponding query section had no MATCH portion. It won't be
      # included in the cypher representation currently used as only
      # the structure of the MATCH portions is shown.
      if len(query) == 0:
        continue
      if len(cypher) > 0:
        cypher += "\n"
      cypher += "MATCH\n"
      last_target_name = ""

      # Write the first element of the query. This must be a vertex or table
      # frame.
      if isinstance(query[0], self._QueryPlanEdge):
        cypher += f"({query[0].source_name})"
      else:
        cypher += f"({query[0].name})"

      for (element_idx, element) in enumerate(query):
        if isinstance(element, self._QueryPlanEdge):
          if last_target_name != element.source_name and element_idx > 0:
            # This edge starts a new path in the query. We must write the
            # source.
            cypher += f",\n({element.source_name})"
          if not element.forward_edge:
            cypher += "<"
          cypher += f"-[{element.edge_name}]-"
          if element.forward_edge:
            cypher += ">"
          cypher += f"({element.target_name})"
          last_target_name = element.target_name
        elif element_idx > 0:
          # This is not an edge element. It is a vertex or table frame.
          # If it was the first in this query, then it has already been
          # written. Otherwise, it starts a new path in the query and
          # must be written.
          cypher += f",\n({element.name})"
    return cypher

  def get_scores(self):
    return [score for query, score in self._plan]

class Job(object):
  """
  Represents a user-scheduled Job.

  An instance of this object is created by job-scheduling functions like
  `xgt.Connection.run_job` and `xgt.Connection.schedule_job`.

  A `Job` is used as a proxy for a job in the server and allows the user
  to monitor its execution, possibly cancel it, and learn about its status
  during and after execution.

  The conn parameter represents a previously established connection to the xGT
  server.

  The job_response parameter is a single element of the array returned by the
  output of a job creation gRPC call.  Each individual element in the array will
  be constructed as a separate `Job` object.
  """
  def __init__(self, conn : Connection,
               job_response : Optional[JobStatus] = None,
               python_errors : Optional[str] = None):
    """
    Constructor for Job. Called when Job is created.
    """
    self._conn = conn
    if job_response is not None:
      self._id = job_response.job_id
      self._user = job_response.user
      self._data = self._parse_job_data(job_response)
    else:
      self._id = 0
      self._user = ""
      self._data = { 'status' : 'completed', 'num_rows' : 0 }

    if python_errors is not None:
      if 'ingest_errors' in self._data.keys():
        self._data['ingest_errors'] += python_errors
        self._data['total_ingest_errors'] += len(python_errors)
      else:
        if len(python_errors) > 0:
          self._data['ingest_errors'] = python_errors
        self._data['total_ingest_errors'] = len(python_errors)

  def _parse_job_data(self, job_response):
    job_data = {
      'jobid': job_response.job_id,
      'user': job_response.user,
      'status': sch_proto.JobStatusEnum.Name(job_response.status).lower(),
      'start_time': job_response.start_time.ToDatetime().replace(tzinfo=timezone.utc).astimezone().isoformat(),
      'end_time': job_response.end_time.ToDatetime().replace(tzinfo=timezone.utc).astimezone().isoformat(),
      'error_type': None,
      'visited_edges': job_response.visited_edges,
      'timing': job_response.timing,
      'description': job_response.description,
      'num_rows' : job_response.num_rows,
      'total_ingest_errors' : job_response.total_ingest_errors,
      'default_namespace': job_response.default_namespace,
      'results_frame': job_response.results_frame,
    }
    # Optional fields.
    if job_response.HasField('schema'):
      schema = self._conn._translate_schema_from_server(job_response.schema)
      job_data['schema'] = schema
    if job_response.ingest_error and len(job_response.ingest_error):
      job_data['ingest_errors'] = [data for data in job_response.ingest_error]
    if job_response.error and len(job_response.error) > 0:
        error_code_name = err_proto.ErrorCodeEnum.Name(
            job_response.error[0].code)
        job_data['error_type'] = _code_error_map[error_code_name]
        job_data['error'] = ', '.join([e.message for e in job_response.error])
        job_data['trace'] = ', '.join([e.detail for e in job_response.error])
    if job_response.HasField('query_plan'):
      job_data['query_plan'] =  _QueryPlan(job_response.query_plan)

    if job_response.end_time.ToSeconds() == 0:
      job_data['end_time'] = ''

    return job_data

  def _get_job_data(self):
    request = job_proto.GetJobsRequest()
    request.job_id.extend([self._id])
    responses = self._conn._call(request, self._conn._job_svc.GetJobs)
    job_data = None
    resp_cnt = 0
    for response in responses: # Expect only one response.
      # Retrieve the job status.
      job_data = self._parse_job_data(response.job_status)
      resp_cnt += 1

    if resp_cnt > 1:
      raise XgtInternalError("Expected a single job in response")

    # If the status is unknown, only update the status, not other fields as
    # they will be invalid.
    returned_status = job_data['status']
    if returned_status == 'unknown_job_status':
      self._data['status'] = returned_status
      return job_data

    # Cache the response from the server.
    self._data = job_data

    if log.getEffectiveLevel() >= logging.DEBUG:
      job_id = job_data['jobid']
      job_status = job_data['status']
      user = job_data['user']
      if 'error' in job_data:
        error = job_data['error']
      else:
        error = ''
      if 'trace' in job_data:
        trace = job_data['trace']
      else:
        trace = ''
      msg = f'Job: {job_id} User: {user} Status: {job_status}'
      if error != '':
        msg += "\nError: \n" + error
      if trace != '':
        msg += "\nTrace: \n" + trace
      log.debug(msg)

    return job_data

  def _is_status_final(self):
    if 'status' in self._data:
      curr_status = self._data['status']

      if ((curr_status == 'completed') or (curr_status == 'canceled') or
          (curr_status == 'failed') or (curr_status == 'rollback') or
          (curr_status == 'unknown_job_status')):
        return True

    return False

  # Returns the job results in arrow table form taking into account the
  # requested offset and length.  If the results are not yet available, None is
  # returned.
  def _load_arrow_table(self, offset, length, rows=None, columns=None):
    if not self._is_status_final():
      self._get_job_data()

    if self._is_status_final():
      curr_status = self._data['status']
      if curr_status != 'completed':
        return None

      # Skip getting the Arrow table if there are no results.  The schema is
      # not set for jobs without immediate results.
      if 'schema' not in self._data:
        return None

      ticket = _create_flight_ticket(self, 'xgt__Job_History',
                                     offset, length,
                                     rows = rows, columns = columns,
                                     include_row_labels = False,
                                     job_id = self._id)

      return _get_data_arrow(self._conn, ticket)

    return None

  @property
  def id(self) -> int:
    """
    int: Identifier of the job.

    A 64-bit integer value that uniquely identifies a job. It is
    automatically incremented for each scheduled job over the lifetime of
    the xGT server process.
    """
    return self._id

  @property
  def user(self) -> str:
    """
    str: User who ran the job.
    """
    return self._user

  @property
  def status(self) -> str:
    """
    str: Status of the job.

    ==================  ===============================================
          Job status
    -------------------------------------------------------------------
             Status                       Description
    ==================  ===============================================
             scheduled  The state after the job has been created, but
                        before it has started running.
               running  The job is being executed.
             completed  The job finished successfully.
              canceled  The job was canceled.
                failed  The job failed. When the job fails the `error`
                        and `trace` properties are populated.
              rollback  The job had a transactional conflict with
                        another job and was rolled back.
    unknown_job_status  The job was not found in the job history.
    ==================  ===============================================
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'status' in self._data:
      return self._data['status']
    else:
      return ''

  @property
  def start_time(self) -> str:
    """
    str: Date and time when the job was scheduled.

    This is a formatted string that has a resolution of seconds.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'start_time' in self._data:
      return datetime.fromisoformat(self._data['start_time'])
    else:
      return ''

  @property
  def end_time(self) -> str:
    """
    str: Date and time when the job finished running.

    This is a formatted string that has a resolution of seconds.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'end_time' in self._data and self._data['end_time'] != '':
      return datetime.fromisoformat(self._data['end_time'])
    else:
      return ''

  @property
  def default_namespace(self) -> str:
    """
    str: Default namespace of the job.

    .. versionadded:: 2.0.0
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'default_namespace' in self._data:
      return self._data['default_namespace']
    else:
      return None

  @property
  def results_frame(self) -> str:
    """
    str: Name of the results frame for a query job with an INTO clause or None
    for all other job types.

    .. versionadded:: 2.0.1
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'results_frame' in self._data:
      return self._data['results_frame']
    else:
      return None

  @property
  def visited_edges(self) -> dict[str, int]:
    """
    dict: A dictionary mapping Cypher bound variable names to an integer giving
    the number of edges visited during the job for the Edge Frame referenced by
    the bound variable.

    An edge is "visited" when the query considers the edge as a match to one of
    the query path edges.  Multiple Cypher variables can refer to the same edge
    frame.

    Consider the query path
    ``()-[a:graph_edges1]->()-[b:graph_edges2]->()-[c:graph_edges1]->()`` with
    a visited_edges result of ``a -> 5, b -> 7, c -> 4``.  In performing the
    query 5 edges of type `a` were visited, and so on.  Notice that the total
    number of edges visited for the frame graph_edges1 is 9 while the number of
    edges visited for the frame graph_edges2 is 7.
    """
    if not self._is_status_final():
      self._get_job_data()

    return self._data['visited_edges']

  @property
  def total_visited_edges(self) -> int:
    """
    int: The total number of edges traversed during the job. This is the sum
    of the counts for all edge labels returned in visited_edges.

    For the example given in the visited_edges documentation, the value of
    total_visited_edges would be 16.
    """
    if not self._is_status_final():
      self._get_job_data()

    return sum(self._data['visited_edges'].values())

  @property
  def _timing(self):
    """
    For internal use.
    """
    if not self._is_status_final():
      self._get_job_data()

    return self._data['timing']

  @property
  def description(self) -> str:
    """
    str: A description supplied when the job was started.  Usually a query.
    """
    if not self._is_status_final():
      self._get_job_data()

    return self._data['description']

  @property
  def error_type(self) -> XgtErrorTypes:
    """
    object: Class that belongs to the XgtError hierarchy that corresponds to
    the original exception type thrown that caused the Job to fail.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'error_type' in self._data:
      return self._data['error_type']
    else:
      return XgtError

  @property
  def error(self) -> str:
    """
    str: User-friendly error message describing the reason a job failed.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'error' in self._data:
      return self._data['error']
    else:
      return ''

  @property
  def trace(self) -> str:
    """
    str: Very detailed error message for a failed job.

    This error message contains the friendly error message and a stack
    strace for the code that participated in the error.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'trace' in self._data:
      return self._data['trace']
    else:
      return ''

  @property
  def schema(self) -> list[list]:
    """
    list of lists: The property names and types of the stored results.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'schema' in self._data:
      return self._data['schema']
    else:
      return None

  @property
  def num_rows(self) -> int:
    """
    int: The number of rows in the query result or the number of correctly
         ingested/inserted rows for an input operation.

    .. versionadded:: 1.15.0
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'num_rows' in self._data:
      return self._data['num_rows']
    else:
      return None

  @property
  def total_ingest_errors(self) -> int:
    """
    int: The number of errors that were thrown during ingest.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'total_ingest_errors' in self._data:
      return self._data['total_ingest_errors']
    else:
      return None

  def get_data(
      self, offset : int = 0, length : Optional[int] = None,
      rows : Optional[Iterable[int]] = None,
      columns : Optional[Iterable[Union[int, str]]] = None,
      format : str = 'python', expand : str = 'none'
  ) -> Union[list[list], pandas.DataFrame, pyarrow.Table, None]:
    """
    Returns results data for query jobs with a RETURN but no INTO or None for
    all other job types.

    Parameters
    ----------
    offset : int
      Position (index) of the first row to be retrieved. Cannot be given with
      rows.
    length : int
      Maximum number of rows to be retrieved starting from the row
      indicated by offset. A value of 'None' means 'all rows' on and
      after the offset. Cannot be given with rows.
    rows : Iterable of int
      The rows to retrieve.  A value of 'None' means all rows.  Cannot be given
      with either offset or length.

      .. versionadded:: 1.16.0
    columns : Iterable of int or str
      The columns to retrieve.  Given as an iterable over mixed column
      positions and schema column names.  A value of 'None' means all columns.

      .. versionadded:: 1.14.0
    format : str
      Selects the data format returned: a Python list of list, a pandas
      Dataframe, or an Apache Arrow Table.  Must be one of 'python', 'pandas',
      or 'arrow'. Default='python'.

      .. versionadded:: 1.14.0
    expand : str, valid values: {'none', 'light', 'full'}, default: 'none'
      If light or full, expands id/path types in the result to
      Edge, Vertex, or TableRow types with properties. If full, will also
      include frame data with each expanded type.

      Works only for python and pandas format.

      .. experimental:: The API of this method may change in future releases.

    Returns
    -------
    list of lists, pandas DataFrame, Apache Arrow Table, or None
      Returns one of the following if the job object represents an OpenCypher
      query with no RETURN clause: list of lists, pandas DataFrame, or Apache
      Arrow Table.  Otherwise, returns None.

    Raises
    ------
    ValueError
      If parameter is out of bounds or invalid format given.
    OverflowError
      If data is out of bounds when converting.
    """
    if not 'schema' in self._data:
      return None

    # Get the requested columns as a list of integers.
    schema = self._data['schema']
    columns = _validated_columns(columns, schema)

    # If specific columns are requested, the schema used to convert the pyarrow
    # table to pandas or pandas format should only include those columns.
    if columns is not None:
      schema = []
      for i in columns:
        schema.append(self._data['schema'][i])

    if not isinstance(format, str):
      raise XgtTypeError('format must be of type string')

    # Ignore format case.
    lc_format = format.lower()

    if lc_format == 'python':
      return _get_data_python_from_table(
                 self._load_arrow_table(offset, length, rows, columns),
                 schema, self._conn, expand)
    elif lc_format == 'pandas':
      return _get_data_pandas_from_table(
                 self._load_arrow_table(offset, length, rows, columns),
                 schema, self._conn, expand)
    elif lc_format == 'arrow':
      return self._load_arrow_table(offset, length, rows, columns)
    else:
      raise XgtValueError('format must be one of python, pandas, or arrow, '
                          f'given: {format}')

  def __str__(self):
    txt = f'id:{self.id}, user:{self.user}, description:{self.description}, ' \
          f'start:{self.start_time}, stop:{self.end_time}, status:{self.status}'
    if len(self.error) > 0:
      txt = f'{txt}, nerror:{self.error}'
    return txt

  def get_ingest_errors(self, offset : int = 0,
                        length : Optional[int] = None) -> list[str]:
    """
    Returns a table of strings giving error information from ingest.  The first
    thousand errors raised are retrievable this way.

    Parameters
    ----------
    offset : int
      Position (index) of the first row to be retrieved.
    length : int
      Maximum number of rows of errors to be retrieved starting from the row
      indicated by offset.  A value of 'None' means 'all rows' on and after
      the offset.

    Returns
    -------
    list of str
    If this is not an ingest job or no errors were raised, this returns None.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'ingest_errors' in self._data:
      offset, length = _verify_offset_length(offset, length)

      total_length = len(self._data['ingest_errors'])
      if length is None:
        length = total_length

      errors = self._data['ingest_errors']
      startpos = min(offset, total_length)
      endpos = min(offset + length + 1, total_length)

      return errors[startpos:endpos]
    else:
      return None

  @property
  def _query_plan(self):
    """
    For internal use.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'query_plan' in self._data:
      return str(self._data['query_plan'])
    else:
      return ''

  @property
  def _query_plan_as_cypher(self):
    """
    For internal use.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'query_plan' in self._data:
      return self._data['query_plan'].to_cypher()
    else:
      return ''

  @property
  def _query_plan_scores(self):
    """
    For internal use.
    """
    if not self._is_status_final():
      self._get_job_data()

    if 'query_plan' in self._data:
      return self._data['query_plan'].get_scores()
    else:
      return None
