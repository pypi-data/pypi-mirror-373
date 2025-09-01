#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2023 CS GROUP
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
"""
Generate JSON schema example implementations for the slow unit tests.
"""

import os
import os.path as osp
import sys

# Repo import /tests/
sys.path.insert(0,osp.abspath(osp.dirname(__file__) + "/../../.."))
sys.path.insert(0,osp.abspath(osp.dirname(__file__) + "/../../../tests"))
from tests.drivers.s2geo_legacy.s2geo_interface import S2geoInterface


# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# Local import
sys.path.append(osp.dirname(__file__))
import doc_init_schema  # pylint: disable=wrong-import-order,import-error,wrong-import-position # noqa: E402

if __name__ == "__main__":
    #
    # See test_sentinel2_msi.py
    interface_path = osp.join(ASGARD_DATA, "S2MSIdataset/no_refining/S2GEO_Input_interface.xml")
    config = S2geoInterface(interface_path).read()
    doc_init_schema.generate_example(config, "S2MSIProduct.v2_no_refining_dem", shorten=True, verbose=True)
