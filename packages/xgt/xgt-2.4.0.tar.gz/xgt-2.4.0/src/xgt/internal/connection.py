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
The module represents features intended for use by internal Rocketgraph
staff only.  Note that we use "monkey patching" to add methods to the
standard xgt.Connection class.

To use the augmented internal functionality, simply import:

>>> import xgt.internal

rather than:

>>> import xgt

As an example, to use the internal version of Connection, the following code
can be used in the main driving script:

>>> c = xgt.Connection()
>>> c.shutdown_server()
"""

from datetime import datetime, timedelta
import time

# Importing functionality from the main feature level.
from ..connection import Connection
from .. import AdminService_pb2 as admin_proto
from .. import MetricsService_pb2 as metrics_proto

def shutdown_server(self, force = False):
  """
  Initiates an orderly server shutdown.
  """
  request = admin_proto.ShutdownRequest()
  request.force = force
  self._call(request, self._admin_svc.Shutdown)

def clear_metrics(self):
  """
  Clear the metrics cache. If metrics collection is turned on, metrics will be
  recomputed.

  Examples
  --------
  >>> conn = xgt.Connection()
  >>> conn.clear_metrics()
  """

  request = metrics_proto.ClearMetricsRequest()
  response = self._call(request, self._metrics_svc.ClearMetrics)

def run_job(self, query, **kwargs):
  job_obj = self._launch_job(query, wait = True, **kwargs)
  if job_obj.status == 'failed' or job_obj.status == 'rollback':
    msg = (u'Failed job. id={0} msg="{1}"').format(job_obj.id, job_obj.error)
    raise job_obj.error_type(msg, job_obj.trace)

  return job_obj

def schedule_job(self, query, **kwargs):
  return self._launch_job(query, wait = False, **kwargs)

# "Monkey patching" the feature classes with new functionality.
Connection.shutdown_server = shutdown_server
Connection.clear_metrics = clear_metrics
Connection.run_job = run_job
Connection.schedule_job = schedule_job
