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
Unit tests for GroundRangePropagationModel
"""

import os
import os.path as osp

import numpy as np
import pytest
from helpers.compare import GeodeticComparator
from numpy.random import RandomState

from asgard.models.body import EarthBody
from asgard.models.range import GroundRangePropagationModel
from asgard.models.time import TimeReference

# Resources directory
TEST_DIR = osp.dirname(__file__)
RESOURCES = osp.join(TEST_DIR, "resources/propagation")

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")


@pytest.fixture(name="propagation", scope="module")
def given_ground_range_propagation_model():
    """
    Fixture to generate a GroundRangePropagationModel
    """

    time_model = TimeReference(orekit_data="pyrugged:data/orekit-data-master")
    earth_body = EarthBody(ellipsoid="WGS84", time_reference=time_model)
    config = {
        "earth_body": earth_body,
        "geoid_path": osp.join(
            ASGARD_DATA,
            "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr",
        ),
        "zarr_dem": {
            "path": GETAS_PATH,  # from new format ADF
        },
        "body_rotating_frame": "EF",  # implemented by ITRF
        "light_time_correction": False,
        "aberration_of_light_correction": False,
    }
    return GroundRangePropagationModel(**config)


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


def generate_time_array() -> dict:
    """
    Build the time array for the different test scenario
    """

    # ~ lines, _ = np.meshgrid(
    # ~ np.linspace(0, 200, 11),
    # ~ np.linspace(0, 200, 11),
    # ~ )
    # ~ flat_lines = lines.flatten()
    # ~ return {
    # ~ "offsets": (flat_lines - 100) * 1.5e-3,
    # ~ "epoch": "2012-01-01T12:30:00",
    # ~ "unit": "s",
    # ~ "ref": "UTC",
    # ~ }
    lines = RandomState(10).rand(500) * 2000.0
    rate = 1.0 / 1.5e-3
    return {
        "offsets": (lines - 1000.0) / rate,
        "epoch": "2012-01-01T12:30:00",
        "unit": "s",
        "ref": "UTC",
    }


def given_los_dataset(ac_dist: float):
    """
    Supply the dataset with LOS direction and position, times, across track distance
    """

    # Data passed to the model
    dataset = {}

    # For each .npy file in the resource directory, need to have the "orb_vel" array
    resources = os.path.join(RESOURCES, "with_light_time_and_aberration")
    for filename in os.listdir(resources):
        if filename.endswith(".npy"):
            # Load the numpy array and add it to the dataset with key=filename
            dataset[filename[:-4]] = np.load(os.path.join(resources, filename))

    dataset["times"] = generate_time_array()

    dataset["ac_dist"] = ac_dist * np.ones((len(dataset["times"]["offsets"]),), dtype="float64")

    return dataset


def test_ground_range_propagation_model(propagation):
    """
    Unit test for GroundRangePropagationModel.sensor_to_target()
    """

    assert isinstance(propagation, GroundRangePropagationModel)

    dataset_center = given_los_dataset(0.0)

    # Save and remove the ground results reference
    grounds_reference = dataset_center.pop("gnd_coords")

    propagation.sensor_to_target(dataset_center)

    # Compare results to pyrugged (increase tolerance due to inconsistent elevation from ADF)
    abs_diff = np.absolute(dataset_center["gnd_coords"] - grounds_reference).T
    assert abs_diff[0].max() < 0.05  # longitude in degrees
    assert abs_diff[1].max() < 0.01  # latitude in degrees
    assert abs_diff[2].max() < 3050  # altitude in meters

    dataset_left = given_los_dataset(-48000.0)
    dataset_left.pop("gnd_coords")

    propagation.sensor_to_target(dataset_left)

    comp = GeodeticComparator(propagation.body)
    plani_dist = comp.planar_error(dataset_center["gnd_coords"], dataset_left["gnd_coords"])
    assert np.allclose(plani_dist, 48000.0)
