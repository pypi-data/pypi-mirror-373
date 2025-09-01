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
"""
Unit tests for the propagation model
"""
import os
import os.path as osp
from collections import namedtuple

import numpy as np
import pytest
from numpy.random import RandomState

# isort: off
# pylint: disable=unused-import
import asgard.wrappers.orekit  # JCC initVM() # noqa: F401

# isort: on

# pylint: disable=ungrouped-imports, no-name-in-module
from asgard.models.body import EarthBody
from asgard.models.dem import MINUS_90, MINUS_180
from asgard.models.propagation import PropagationModel
from asgard.models.time import TimeReference

# Resources directory
TEST_DIR = osp.dirname(__file__)
RESOURCES = osp.join(TEST_DIR, "resources/propagation")

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path (older version)
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20230428T185052.zarr")

"""
Test data from /pyrugged/location/optical.py::direct_location_inert_vec

# The numpy arrays are exported using:
# (use a breakpoint at the beginning of the method)
for list_vector3d, filename in (
    (pos_inert, "los_pos"), (los_inert, "los_vec"), (spacecraft_velocity, "spacecraft_velocities")
):
    np.save (f"/path/to/resources/{filename}.npy", np.array ([to_array_v (v3d.toArray()) for v3d in list_vector3d]))

# For itrf_positions and itrf_rotations:
# (use a breakpoint at the beginning of the method)
p,v,a,r,rr,ra = [],[],[],[],[],[]
for transform in inert_to_body:
    for list_, value_ in (
        (p, transform.getTranslation()),
        (v, transform.getVelocity()),
        (a, transform.getAcceleration()),
        (rr, transform.getRotationRate()),
        (ra, transform.getRotationAcceleration())
    ):
        list_.append ([value_.getX(), value_.getY(), value_.getZ()])
    value_ = transform.getRotation()
    r.append ([value_.getQ0(), value_.getQ1(), value_.getQ2(), value_.getQ3()])
np.save ("/path/to/resources/itrf_positions.npy", np.array(p))
np.save ("/path/to/resources/itrf_velocities.npy", np.array(v))
np.save ("/path/to/resources/itrf_accelerations.npy", np.array(a))
np.save ("/path/to/resources/itrf_rotations.npy", np.array(r))
np.save ("/path/to/resources/itrf_rotation_rates.npy", np.array(rr))
np.save ("/path/to/resources/itrf_rotation_accelerations.npy", np.array(ra))

# For grounds:
# (use a breakpoint at the end of the method)
np.save ("/path/to/resources/gnd_coords.npy", np.array([
    [ground.longitude, ground.latitude, ground.altitude]
    if ground is not None
    else [None, None, None]
    for ground in result
]))
"""

# Test data.
# Pass the directory names from /tests/resources/propagation, the correction parameters
# and the TileUpdater from the corresponding pyrugged test.
Data = namedtuple(
    "Data",
    [
        "dirname",
        "light_time_correction",
        "aberration_of_light_correction",
        "atmospheric_refraction",
        "deg_threshold",
        "meter_threshold",
        "average_elevation",
    ],
)

#
# The reference .npy numpy arrays are taken from the pyrugged pytests:

# test_location_multiple_points
WITH_NO_CORRECTION = Data(
    "with_no_correction",
    False,
    False,
    False,
    8e-9,
    1e-3,
    269.0,
)

# test_location_timing with CorrectionsParams(True, True, None) and first sensor
WITH_LIGHT_TIME_AND_ABERRATION = Data(
    "with_light_time_and_aberration",
    True,
    True,
    False,
    8e-9,
    1e-3,
    261.0,
)

# test_atmospheric_refraction_correction but add before the 2nd direct_location_of_sensor_line (with the
# atmospheric refraction):
# nb_samples = 11
# lines_linspace = np.linspace(0, dimension, nb_samples)
# pixels_linspace = np.linspace(0, dimension, nb_samples)
# lines, pixels = np.meshgrid(lines_linspace, pixels_linspace)
# lines = lines.flatten()
# pixels = pixels.flatten()
# longitudes, latitudes, altitudes = location.direct_location(lines, pixels)
WITH_ATMOSPHERIC_REFRACTION = Data(
    "with_atmospheric_refraction",
    False,
    False,
    True,
    8e-9,
    1e-3,
    57.0,
)


def generate_time_array(scenario: str) -> dict:
    """
    Build the time array for the different test scenario
    """
    time_array = None
    if scenario == "with_no_correction":
        lines, _ = np.meshgrid(
            np.linspace(0, 200, 11),
            np.linspace(0, 200, 11),
        )
        flat_lines = lines.flatten()
        time_array = {
            "offsets": (flat_lines - 100) * 1.5e-3,
            "epoch": "2012-01-01T12:30:00",
            "unit": "s",
            "ref": "UTC",
        }
    elif scenario == "with_light_time_and_aberration":
        lines = RandomState(10).rand(500) * 2000.0
        rate = 1.0 / 1.5e-3
        time_array = {
            "offsets": (lines - 1000.0) / rate,
            "epoch": "2012-01-01T12:30:00",
            "unit": "s",
            "ref": "UTC",
        }
    elif scenario == "with_atmospheric_refraction":
        lines, _ = np.meshgrid(
            np.linspace(0, 4000, 11),
            np.linspace(0, 4000, 11),
        )
        flat_lines = lines.flatten()
        time_array = {
            "offsets": (flat_lines - 2000) * 1.5e-3,
            "epoch": "2012-01-01T12:30:00",
            "unit": "s",
            "ref": "UTC",
        }
    return time_array


@pytest.fixture(name="earth_body", scope="module")
def given_earth_body():
    """
    Fixture to initialize an EarthBody with WGS84 ellipsoid and a TimeReference based on pyrugged data
    """
    time_model = TimeReference(orekit_data="pyrugged:data/orekit-data-master")
    return EarthBody(ellipsoid="WGS84", time_reference=time_model)


@pytest.mark.parametrize(
    "data",
    [WITH_NO_CORRECTION, WITH_LIGHT_TIME_AND_ABERRATION, WITH_ATMOSPHERIC_REFRACTION],
    ids=[
        "with_no_correction",
        "with_light_time_and_aberration",
        "with_atmospheric_refraction",
    ],
)
def test_models_propagation_dem_zarr(data, earth_body):
    """
    Test the ASGARD propagation model with zarr DEM.
    """

    # Build the PropagationModel
    config = {
        "earth_body": earth_body,
        "zarr_dem": {
            "path": GETAS_PATH,
            "flip_lat": True,
            "shift_lon": MINUS_180,
            "shift_lat": MINUS_90,
        },
        "body_rotating_frame": "EF",  # implemented by ITRF
        "light_time_correction": data.light_time_correction,
        "aberration_of_light_correction": data.aberration_of_light_correction,
    }
    if data.atmospheric_refraction:
        config["atmospheric_refraction"] = {
            "MultiLayerModel": {
                "pixel_step": 100,
                "line_step": 100,
            },
        }
    model = PropagationModel(**config)

    # Data passed to the model
    dataset = {}

    # For each .npy file in the resource directory
    resources = os.path.join(RESOURCES, data.dirname)
    for filename in os.listdir(resources):
        if filename.endswith(".npy"):
            # Load the numpy array and add it to the dataset with key=filename
            dataset[filename[:-4]] = np.load(os.path.join(resources, filename))

    dataset["times"] = generate_time_array(data.dirname)

    # Save and remove the ground results reference
    grounds_reference = dataset.pop("gnd_coords")

    # Call the propagation model
    model.sensor_to_target(dataset)

    # Compare results to pyrugged (increase tolerance due to inconsistent elevation from ADF)
    abs_diff = np.absolute(dataset["gnd_coords"] - grounds_reference).T
    assert abs_diff[0].max() < data.deg_threshold  # longitude in degrees
    assert abs_diff[1].max() < data.deg_threshold  # latitude in degrees
    assert abs_diff[2].max() < data.meter_threshold  # altitude in meters


@pytest.mark.parametrize(
    "data",
    [WITH_NO_CORRECTION, WITH_LIGHT_TIME_AND_ABERRATION, WITH_ATMOSPHERIC_REFRACTION],
    ids=[
        "with_no_correction",
        "with_light_time_and_aberration",
        "with_atmospheric_refraction",
    ],
)
def test_models_propagation_constant_altitude(data, earth_body):
    """
    Test the ASGARD propagation model with a constant average elevation.
    """

    # Build the PropagationModel
    config = {
        "earth_body": earth_body,
        "body_rotating_frame": "EF",  # implemented by ITRF
        "light_time_correction": data.light_time_correction,
        "aberration_of_light_correction": data.aberration_of_light_correction,
    }
    if data.atmospheric_refraction:
        config["atmospheric_refraction"] = {
            "MultiLayerModel": {
                "pixel_step": 100,
                "line_step": 100,
            },
        }
    model = PropagationModel(**config)

    # Data passed to the model
    dataset = {}

    # For each .npy file in the resource directory
    resources = os.path.join(RESOURCES, data.dirname)
    for filename in os.listdir(resources):
        if filename.endswith(".npy"):
            # Load the numpy array and add it to the dataset with key=filename
            dataset[filename[:-4]] = np.load(os.path.join(resources, filename))

    dataset["times"] = generate_time_array(data.dirname)

    # Save and remove the ground results reference
    grounds_reference = dataset.pop("gnd_coords")
    grounds_reference[:, 2] = data.average_elevation

    # Call the propagation model
    model.sensor_to_target(dataset, altitude=data.average_elevation)

    # Compare results to pyrugged (increase tolerance due to inconsistent elevation from ADF)
    abs_diff = np.absolute(dataset["gnd_coords"] - grounds_reference).T
    assert abs_diff[0].max() < 2e-3  # longitude in degrees
    assert abs_diff[1].max() < 2e-3  # latitude in degrees
    assert abs_diff[2].max() < data.meter_threshold  # altitude in meters


def test_models_propagation_constant_altitude_over_geoid(earth_body):
    """
    Test the ASGARD propagation model with a constant altitude on a geoid using geoid and DEM in format zarr.
    """

    # Build the PropagationModel for constant altitude over geoid
    config_geoid = {
        "earth_body": earth_body,
        "geoid_path": osp.join(
            ASGARD_DATA,
            "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr",
        ),
        "body_rotating_frame": "EF",  # implemented by ITRF
        "light_time_correction": False,
        "aberration_of_light_correction": False,
    }
    model_geoid = PropagationModel(**config_geoid)

    dataset_geoid = {}

    # For each .npy file in the resource directory
    resources = os.path.join(RESOURCES, "with_no_correction")
    for filename in os.listdir(resources):
        if filename.endswith(".npy"):
            # Load the numpy array and add it to the dataset with key=filename
            dataset_geoid[filename[:-4]] = np.load(os.path.join(resources, filename))

    dataset_geoid["times"] = generate_time_array("with_no_correction")

    # Call the propagation model
    model_geoid.sensor_to_target(dataset_geoid, altitude=10.0, altitude_reference="geoid")

    # Build the PropagationModel for constant altitude over ellipsoid
    config_ellipsoid = {
        "earth_body": earth_body,
        "body_rotating_frame": "EF",  # implemented by ITRF
        "light_time_correction": False,
        "aberration_of_light_correction": False,
    }
    model_ellipsoid = PropagationModel(**config_ellipsoid)

    # Data passed to the model
    dataset_ellipsoid = {}

    # For each .npy file in the resource directory
    resources = os.path.join(RESOURCES, "with_no_correction")
    for filename in os.listdir(resources):
        if filename.endswith(".npy"):
            # Load the numpy array and add it to the dataset with key=filename
            dataset_ellipsoid[filename[:-4]] = np.load(os.path.join(resources, filename))

    dataset_ellipsoid["times"] = generate_time_array("with_no_correction")

    # Call the propagation model
    alt_mean_geoid = np.mean([dataset_geoid["gnd_coords"][i][2] for i in range(10)])

    model_ellipsoid.sensor_to_target(dataset_ellipsoid, altitude=alt_mean_geoid, altitude_reference="ellipsoid")

    # Compare results obtained with constant elevation over ellispoid
    # with results obtained with constant elevation over geoid with equivalent elevation
    abs_diff = np.absolute(dataset_ellipsoid["gnd_coords"][:11] - dataset_geoid["gnd_coords"][:11]).T
    assert abs_diff[0].max() < 1.0e-6  # longitude in degrees
    assert abs_diff[1].max() < 1.0e-6  # latitude in degrees
    assert abs_diff[2].max() < 0.1  # altitude in meters
