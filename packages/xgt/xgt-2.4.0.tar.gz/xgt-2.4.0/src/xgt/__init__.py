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

"""
The Python interface to the Rocketgraph xGT graph analytics engine.

Data Loading
============

xGT is a strongly-typed graph system. Loading data is a three step process:

1. Create a namespace or use a pre-created namespace.

  Frame names are represented using a two-level naming scheme. The first part
  represents the namespace in which the frame is stored. Users can create a
  namespace, or, alternatively, system administrators may want to create
  namespaces ahead of time. Creating a namespace can be done with
  :py:meth:`Connection.create_namespace` and a list of existing
  namespaces can be obtained using :py:meth:`Connection.get_namespaces`.

2. Describe the structure and data types of your graph.

  Define the vertex and edge frame structure with
  :py:meth:`Connection.create_vertex_frame` and
  :py:meth:`Connection.create_edge_frame`. Once the type structure is set,
  :py:class:`VertexFrame` and :py:class:`EdgeFrame` objects provide access to
  the server-side structures.

3. Load your edge and vertex data.

  The :py:class:`VertexFrame` and :py:class:`EdgeFrame` objects provide the
  high-performance, parallel :py:meth:`~VertexFrame.load` method to ingest data
  as well as a direct :py:meth:`~VertexFrame.insert` method to add small
  amounts of data piecewise.

Query Processing
================

Queries are expressed as strings written in `OpenCypher <https://docs.rocketgraph.com/user_ref/graphanalytics/tql_for_cypher_users.html>`_.

>>> query ='''
      MATCH  (emp:Employee)-[edge1:ReportsTo]->(boss:Employee)
      RETURN emp.person_id AS employee_id,
             boss.person_id AS boss_id
      INTO   ResultTable
'''

A query runs in the context of a :py:class:`Job`, which can be run, scheduled
and canceled. The :py:meth:`Connection.run_job` method runs the query and
blocks until it finishes successfully, terminates by an error, or is canceled.

Example Script
==============

The following Python script shows some of the functions that can be used to
create a graph, load data into it, run a query and access the results, and
finally remove that graph from the system. ::

  import xgt

  # Connect to xgtd.
  conn = xgt.Connection()

  # Set a default namespace for this session.
  conn.set_default_namespace('career')

  # Define and create the graph in the default namespace.
  employees = conn.create_vertex_frame(
    name='Employees',
    schema=[['person_id', xgt.INT],
            ['name', xgt.TEXT],
            ['postal_code', xgt.INT]],
    key='person_id')

  reports_to = conn.create_edge_frame(
    name='ReportsTo',
    schema=[['employee_id', xgt.INT],
            ['boss_id', xgt.INT],
            ['start_date', xgt.DATE],
            ['end_date', xgt.DATE]],
    source=employees,
    target=employees,
    source_key='employee_id',
    target_key='boss_id')

  # Load data to the graph in xgtd.
  # Use the insert() method for data of a few hundred rows or less;
  # for bigger amounts of data, use the load() method with csv files.
  employees.insert(
    [[111111101, 'Manny', 98103],
     [111111102, 'Trish', 98108],
     [911111501, 'Frank', 98101],
     [911111502, 'Alice', 98102]
    ])
  reports_to.insert(
    [[111111101, 911111501, '2015-01-03', '2017-04-14'],
     [111111102, 911111501, '2016-04-02', '2017-04-14'],
     [911111502, 911111501, '2016-07-07', '2017-04-14'],
     [111111101, 911111502, '2017-04-15', '3000-12-31'],
     [111111102, 911111502, '2017-04-15', '3000-12-31'],
     [911111501, 911111502, '2017-04-15', '3000-12-31']
    ])

  # Query data
  cmd = '''
    MATCH
      (employee:Employees)-[edge1:ReportsTo]->
      (boss:Employees)-[edge2:ReportsTo]->
      (employee)
    WHERE
      edge1.end_date <= edge2.start_date
    RETURN
      employee.person_id AS employee1_id,
      boss.person_id AS employee2_id,
      edge1.start_date AS start1,
      edge1.end_date AS end1,
      edge2.start_date AS start2,
      edge2.end_date AS end2
    INTO
      Results
    '''

  conn.run_job(cmd)
  results = conn.get_frame('Results')

  # Extract the results.
  for frame in [employees, reports_to, results]:
    print('{name}: {n_cols} columns, {n_rows} rows'.format(
      name=frame.name,
      n_cols=len(frame.schema),
      n_rows=frame.num_rows))

  print('\\n--- Results ---')
  for row in results.get_data(0,100):
    print(', '.join([str(c) for c in row]))

  # Drop all objects.
  [conn.drop_frame(f) for f in [reports_to, employees, results]]
"""

__all__ = [
  'BOOLEAN', 'INT', 'UINT', 'FLOAT', 'DATE', 'TIME', 'DATETIME', 'IPADDRESS',
  'TEXT', 'WGSPOINT', 'CARTESIANPOINT',
  'XgtError', 'XgtNotImplemented', 'XgtInternalError',
  'XgtIOError', 'XgtServerMemoryError', 'XgtConnectionError',
  'XgtSyntaxError', 'XgtTypeError', 'XgtValueError', 'XgtNameError',
  'XgtArithmeticError', 'XgtFrameDependencyError', 'XgtTransactionError',
  'XgtSecurityError',
  'Job', 'Connection', 'RowID', 'Vertex', 'Edge', 'TableRow',
  'VertexFrame', 'EdgeFrame', 'TableFrame']

from .common import (
  BOOLEAN, INT, UINT, FLOAT, DATE, TIME, DATETIME, IPADDRESS, TEXT, LIST, ROWID,
  DURATION, WGSPOINT, CARTESIANPOINT, RowID, Vertex, Edge, TableRow,
  XgtError, XgtNotImplemented, XgtInternalError, XgtIOError,
  XgtServerMemoryError, XgtConnectionError, XgtSyntaxError, XgtTypeError,
  XgtValueError, XgtNameError, XgtArithmeticError, XgtFrameDependencyError,
  XgtTransactionError, XgtSecurityError
)
from .connection import Connection, BasicAuth, KerberosAuth, PKIAuth
from .connection import ProxyPKIAuth, TrustedProxyAuth
from .graph import HeaderMode, VertexFrame, EdgeFrame, TableFrame, GraphFrame
from .job import Job

from xgt.ErrorMessages_pb2 import ErrorCodeEnum
from xgt.MetricsService_pb2 import MetricsStatusEnum
from xgt.SchemaMessages_pb2 import JobStatusEnum

from .version import (
  __version__, __version_major__, __version_minor__, __version_patch__
)

import warnings
warnings.filterwarnings(action='ignore', message='numpy.dtype size changed')
warnings.filterwarnings(action='ignore', message='numpy.ufunc size changed')
