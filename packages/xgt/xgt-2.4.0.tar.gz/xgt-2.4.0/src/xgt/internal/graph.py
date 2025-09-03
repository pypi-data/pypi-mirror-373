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

>>> v = xgt.Connection().get_frame('netflow__ip')
>>> v.load(["/path/to/file.csv"], record_history = False, print_timing = True)
"""

# Importing functionality from the main feature level.
from ..graph import (TableFrame, EdgeFrame, VertexFrame, HeaderMode)

def load(self, paths, **kwargs):
  """
  Override the load method to support internal-use-only parameters as well.

  Examples
  --------
  >>> result = my_frame.load(["/path/to/file.csv"], detailed_timing = True,
  >>>                        hide_tiny_times = True, print_timing = True)
  """
  return self._load(paths, **kwargs)

def save(self, path, **kwargs):
  """
  Override the load method to support internal-use-only parameters as well.

  Examples
  --------
  >>> result = my_frame.save("/path/to/file.csv", detailed_timing = True,
  >>>                        hide_tiny_times = True, print_timing = True)
  """
  return self._save(path, **kwargs)

# "Monkey patching" the feature classes with new functionality.
TableFrame.load = load
TableFrame.save = save
EdgeFrame.load = load
EdgeFrame.save = save
VertexFrame.load = load
VertexFrame.save = save
