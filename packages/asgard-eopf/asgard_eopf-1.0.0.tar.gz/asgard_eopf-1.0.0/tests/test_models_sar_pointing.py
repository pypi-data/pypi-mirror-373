#!/usr/bin/env python
# coding: utf8
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
Unit tests for SarPointingModel
"""

import numpy as np

from asgard.models.sar import SarPointingModel


def test_sar_pointing_model():
    """
    Unit test for SARPointingModel
    """
    config = {"look_side": "RIGHT", "front_direction": np.array([0.0, -1.0, 0.0])}

    model = SarPointingModel(**config)

    assert model.config["look_side"] == "RIGHT"

    dataset = {"geom": "EW1"}
    model.compute_los(dataset)

    assert "los_pos" in dataset
    assert "los_vec" in dataset

    assert np.all(dataset["los_pos"] == np.zeros((3,), dtype="float64"))
    assert np.all(dataset["los_vec"] == np.array([0.0, -1.0, 0.0], dtype="float64"))
