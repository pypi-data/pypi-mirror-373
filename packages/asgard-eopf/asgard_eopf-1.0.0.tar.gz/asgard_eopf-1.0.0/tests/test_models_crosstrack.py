#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
"""
Unit tests for CrossTrackPointingModel
"""

import numpy as np
import pytest

from asgard.models.crosstrack import CrossTrackPointingModel


@pytest.fixture(name="pointing", scope="module")
def given_crosstrack_pointing_model():
    """
    Fixture to generate a CrossTrackPointingModel
    """

    return CrossTrackPointingModel(resolution=16000.0, center_position=64)


@pytest.fixture(name="coords", scope="module")
def given_image_coordinates():
    """
    Fixture to generate a image coordinate
    """
    return np.array(
        [
            [0, 1],
            [35, 2],
            [64, 3],
            [100, 4],
        ],
        dtype="int64",
    )


def test_crosstrack_pointing(pointing, coords):
    """
    Test for CrossTrackPointingModel.compute_los
    """

    assert isinstance(pointing, CrossTrackPointingModel)

    dataset = {"coords": coords}
    pointing.compute_los(dataset)

    assert np.all(dataset["los_vec"] == [0, 0, 1])
    assert np.all(dataset["los_pos"] == [0, 0, 0])

    ref_ac_dist = np.array([64 * 16000, 29 * 16000, 0, -36 * 16000])
    assert np.allclose(dataset["ac_dist"], ref_ac_dist)
