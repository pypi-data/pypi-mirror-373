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
The Python interface to the Rocketgraph xGT graph analytics engine for system
administration functions.

The module represents features intended for use by xGT system admins only.

To use this admin functionality, simply import:

>>> import xgt.admin as xa

Examples
--------

>>> import xgt
>>> import xgt.admin as xa
>>> server = xgt.Connection(auth = xgt.UserCredentialsAuth(userid="user01"))
>>> labelset = xa.compute_label_set(server, ['group1', 'group14'])
>>> print("Labelset: {}".format(labelset))
"""

__all__ = [
  'compute_label_set',
  ]

def compute_label_set(server, groupset):
  """
  Compute the set of labels reachable from at least one group in the groupset.
  """
  groups = list(dict.fromkeys(groupset))
  data = server.get_frame('xgt__Group_Label').get_data()
  result = dict()
  for row in data:
    if row[0] in groups:
      result[row[1]] = None
  return list(result.keys())
