#!/usr/bin/env python
# coding: utf8
#
# Copyright 2023 CS GROUP
# Licensed to CS GROUP (CS) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# CS licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# pylint: disable=too-many-locals,import-error,too-many-branches
"""
Tests configuration
"""

pytest_plugins = "helpers.compare"  # pylint: disable=invalid-name

# Note: this should not be useful anymore
'''
def pytest_collection_modifyitems(items):
    """Modify the order in which the unit tests are run"""

    sorted_items = []

    front_index = 0
    for item in items:
        # Run the Sentinel-2 tests first because they must set the Orekit IERS directory
        # before the other tests use Orekit.
        if item.module.__name__ == "test_sentinel2_msi":
            sorted_items.insert(front_index, item)
            front_index += 1
        else:
            sorted_items.append(item)

    # In-place modification of the input item list
    items[:] = sorted_items
'''
