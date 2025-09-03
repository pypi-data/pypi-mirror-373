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
The Python interface to the Rocketgraph xGT graph analytics engine for internal
use only.

The module represents features intended for use by internal Rocketgraph
staff only.  Note that we use "monkey patching" to add methods to the
standard object classes in the xgt module.
"""

__all__ = [
  'Connection',
  'Graph',
  ]

from . import connection
from . import graph
