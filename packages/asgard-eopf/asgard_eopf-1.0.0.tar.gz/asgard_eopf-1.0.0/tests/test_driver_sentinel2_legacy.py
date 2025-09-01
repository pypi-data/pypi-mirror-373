#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022-2024 CS GROUP
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
Unit tests for S2Geo legacy driver
"""

import json
import os
import os.path as osp

import numpy as np
import pytest
from drivers.s2geo_legacy.s2geo_interface import S2geoInterface

TEST_DIR = osp.dirname(__file__)
RESOURCES = osp.join(TEST_DIR, "resources/S2MSIdataset")

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")


@pytest.mark.parametrize(
    "name",
    ["with_refining", "no_refining"],
)
def test_read_s2geo_context(name):
    """
    Unit test for S2Geo context reading
    """

    interface_path = osp.join(ASGARD_DATA, f"S2MSIdataset/{name}/S2GEO_Input_interface.xml")

    config = S2geoInterface(interface_path).read()

    reference_path = osp.join(RESOURCES, name, "config.json")
    with open(reference_path, "r", encoding="utf-8") as file_ref:
        ref_config = json.load(file_ref)

    for item in ["piloting_to_msi", "msi_to_focalplane", "focalplane_to_sensor"]:
        transfo_test = config["spacecraft"][item]
        transfo_ref = ref_config["spacecraft"][item]

        assert np.all(transfo_test["rotations"]["axis"] == transfo_ref["rotations"]["axis"])
        assert np.all(transfo_test["rotations"]["units"] == transfo_ref["rotations"]["units"])
        assert np.allclose(transfo_test["rotations"]["values"], transfo_ref["rotations"]["values"], rtol=0, atol=1e-9)
        assert np.all(transfo_test["combination_orders"] == transfo_ref["combination_orders"])
        assert np.allclose(transfo_test["scale_factors"], transfo_ref["scale_factors"], rtol=0, atol=1e-9)

        if "col_names" in transfo_ref:
            assert np.all(transfo_test["col_names"] == transfo_ref["col_names"])
        if "row_names" in transfo_ref:
            assert np.all(transfo_test["row_names"] == transfo_ref["row_names"])
