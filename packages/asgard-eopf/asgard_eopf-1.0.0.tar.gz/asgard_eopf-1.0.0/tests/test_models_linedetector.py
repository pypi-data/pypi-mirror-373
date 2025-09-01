#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022 CS GROUP
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
Unit tests for line detetector timestamp model
"""

import os.path as osp

import numpy as np
import pytest
from drivers.sentinel_3_legacy import S3LegacyDriver

from asgard.models.linedetector import (
    LineDetectorPointingModel,
    LineDetectorTimestampModel,
)

TEST_DIR = osp.dirname(__file__)


@pytest.fixture(name="atm", scope="module")
def models_linedetector():
    """
    Fixture to instanciate an LineDetectorTimestampModel
    """
    frames = {
        "offsets": np.array(
            [
                8168.02456,
                8168.02466,
                8168.02476,
                8168.02486,
                8168.02496,
            ],
            dtype="float64",
        ),
    }
    conf = {"times": frames}

    return LineDetectorTimestampModel(**conf)


def test_acquisition_times(atm):
    """
    Unit test for AbstractTimestampModel with acquisition_times function
    """

    # Test with int coordinates
    img_coords = np.zeros((30, 2), dtype="int32")
    for row in range(5):
        img_coords[row, 0] = row * 2
        img_coords[row, 1] = row

    dataset = {"coords": img_coords, "geom": "C2"}

    atm.acquisition_times(dataset)

    assert np.allclose(dataset["times"]["offsets"][:5], atm.config["times"]["offsets"])

    # Test with float coordinates
    img_coords_float = np.zeros((30, 2), dtype="float64")
    for row in range(5):
        img_coords[row, 0] = row * 2
        img_coords[row, 1] = row + 0.5

    dataset_float = {"coords": img_coords_float, "geom": "C2"}
    atm.acquisition_times(dataset_float)

    assert np.allclose(dataset_float["times"]["offsets"][:5], atm.config["times"]["offsets"])


@pytest.fixture(name="pointing_vectors", scope="module")
def read_pointing_vectors():
    """
    Fixture to extract pointing vectors
    """
    calibration_file = osp.join(TEST_DIR, "resources/S3/OLCI/CAL", "OL_1_CAL_AX.nc")
    return S3LegacyDriver.olci_pointing_angles(calibration_file)


def test_pointing_olci_product(pointing_vectors):
    """
    Unit test for pointing on S3OLCIProduct
    """

    conf = {"unit_vectors": {}}

    # Warning: the computation of azimuth in legacy OLCI processor
    # indicates that X/Y pointing components are switched compared to
    # a default instrument reference frame (where 'x' is cross-track,
    # and 'y' is along-track). Also in this default instrument reference
    # frame, Z axis is pointing toward space (not Earth), so the Z
    # component of the line of sight should be negative.

    for idx, instr in enumerate(["C1", "C2", "C3", "C4", "C5"]):
        # Need to switch X and Y coordinates to match Instrument Frame convention
        vec_x = pointing_vectors["Y"][idx, :]
        vec_y = pointing_vectors["X"][idx, :]
        assert vec_x.shape == vec_y.shape
        # reconstruct Z component with negative sign
        vec_z = -np.sqrt(1 - (vec_x**2) - (vec_y**2))
        vec_pnt = np.stack([vec_x, vec_y, vec_z], axis=-1)
        conf["unit_vectors"][instr] = vec_pnt

    mdl = LineDetectorPointingModel(**conf)
    assert mdl is not None

    # Select coordinates
    coords = np.array([[0, 0], [0, 10], [20, 0], [738, 0], [739, 0]])
    dataset = {"coords": coords, "geom": "C4"}

    mdl.compute_los(dataset)

    assert "los_vec" in dataset
    assert "los_pos" in dataset
    assert np.allclose(dataset["los_vec"][0], [-0.1056327, 5.154276e-04, -0.9944051], rtol=0, atol=1e-6)
    assert np.all(dataset["los_vec"][1] == dataset["los_vec"][0])
    assert np.allclose(dataset["los_vec"][2], [-9.9053882e-02, 5.1669800e-04, -0.99508196], rtol=0, atol=1e-6)
    extrapolation_value = -0.5 * dataset["los_vec"][3] + 1.5 * dataset["los_vec"][4]
    assert np.allclose(dataset["los_vec"][4], [0.14034821, 5.7055976e-04, -0.99010205], rtol=0, atol=1e-6)

    # Select floating coordinates
    coords = np.array([[0.0, 0.0], [0.0, 10.0], [20.0, 0.0], [21.0, 0.0], [20.5, 0.0], [739.5, 0.0]])
    dataset = {"coords": coords, "geom": "C4"}

    mdl.compute_los(dataset)

    assert "los_vec" in dataset
    assert "los_pos" in dataset
    assert np.allclose(dataset["los_vec"][0], [-0.1056327, 5.154276e-04, -0.9944051], rtol=0, atol=1e-6)
    assert np.all(dataset["los_vec"][1] == dataset["los_vec"][0])
    assert np.allclose(dataset["los_vec"][4], (dataset["los_vec"][2] + dataset["los_vec"][3]) / 2, rtol=0, atol=1e-6)
    assert np.allclose(dataset["los_vec"][5], extrapolation_value, rtol=0, atol=1e-6)
