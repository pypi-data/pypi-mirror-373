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
Unit tests for GenericPlatformModel
"""

import os
import os.path as osp

import numpy as np
import numpy.testing as npt
import pytest  # pylint: disable=import-error
from drivers.sentinel_3_legacy import (  # noqa: F401  # pylint: disable=import-error
    S3LegacyDriver,
)
from scipy.spatial.transform import Rotation as R

from asgard.models.platform import (  # noqa: F401  # pylint: disable=import-error
    GenericPlatformModel,
)
from asgard.models.thermoelastic import ThermoelasticModel

TEST_DIR = osp.dirname(__file__)

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")


@pytest.fixture(name="thermoelastic", scope="module")
def given_thermoelastic_model():
    """
    Instanciate a thermoelastic time-based transform
    """

    calibration_file = osp.join(TEST_DIR, "resources/S3/OLCI/CAL", "OL_1_CAL_AX.nc")
    thermoelastic_tables = S3LegacyDriver.s3_thermoelastic_tables(calibration_file, group="thermoelastic_model_EO")

    navatt_gps = np.load(osp.join(TEST_DIR, "resources/sample_timestamps_gps.npy"))
    navatt_oop = np.load(osp.join(TEST_DIR, "resources/sample_oop.npy"))

    config = {
        "thermoelastic": thermoelastic_tables,
        "doy": 132.75074690216616,
        "lut_times": navatt_gps,
        "lut_oop": navatt_oop,
        "instruments": ["C1", "C2", "C3", "C4", "C5"],
    }

    return ThermoelasticModel(**config)


@pytest.fixture(name="gpm", scope="module")
def generic_platform_model(thermoelastic):
    """
    Fixture to produce a GenericPlatformModel
    """

    per_cam_models = thermoelastic.split()

    config_example_2_json = {
        "states": [
            {
                "name": "com1",
                "origin": "platform",
                # counter-clockwise rotation of 90 degrees about the x-axis + translation
                "rotation": np.array([np.radians(90.0), 0.0, 0.0]),
                "translation": np.array([-0.5, 0.5, -0.5]),
            },
            {
                "name": "instr1",
                "origin": "com1",
                # clockwise rotation of 90 degrees about the y-axis
                "rotation": np.array([0.0, -np.radians(90.0), 0.0]),
            },
            {
                "name": "com2",
                "origin": "platform",
                # clockwise rotation of 90 degrees about the y-axis
                "rotation": np.array([0.0, -np.radians(90.0), 0.0]),
            },
            {
                "name": "refined_instr2",
                "origin": "instr2",
                # homothety x2 on Z axis
                "homothety": np.array([1.0, 1.0, 2.0]),
            },
            {
                "name": "instr2",
                "origin": "com2",
                # clockwise rotation of 90 degrees about the x-axis
                "rotation": np.array([-np.radians(90.0), 0.0, 0.0]),
                "translation": np.array([1.0, 1.0, 1.0]),
            },
            {
                "name": "com2",
                "origin": "com1",
                # clockwise rotation of 90 degrees about the x-axis
                "rotation": np.array([np.radians(90.0), 0.0, 0.0]),
                "translation": np.array([-1.0, 1.0, 0.0]),
            },
            {
                "name": "com3",
                "origin": "platform",
                # Thermoelastic model from config
                "time_based_transform": {
                    "thermoelastic": {
                        "julian_days": np.array([1, 74, 147, 220, 293, 366], dtype=np.int16),  # time
                        # We define a quaternion matrix by increasing the angle on the y axis by 10 degrees
                        "quaternions_1": np.zeros((5, 6, 36), dtype=np.float64),
                        "quaternions_2": np.repeat(
                            np.sin(np.tile(np.arange(0, 360, 10, dtype=np.float64), (6, 1)) / 2)[np.newaxis, :, :],
                            repeats=5,
                            axis=0,
                        ),
                        "quaternions_3": np.repeat(
                            np.sin(
                                np.repeat(
                                    np.arange(0, 360, 60, dtype=np.float64)[..., None],
                                    36,
                                    axis=-1,
                                )
                                / 2
                            )[np.newaxis, :, :],
                            repeats=5,
                            axis=0,
                        ),
                        "quaternions_4": np.zeros((5, 6, 36), dtype=np.float64),
                        "on_orbit_positions_angle": np.repeat(
                            np.tile(np.arange(0, 360, 10, dtype=np.float64), (36, 1))[np.newaxis, :, :],
                            repeats=5,
                            axis=0,
                        ),
                    },
                    "lut_times": thermoelastic.lut_times,
                    "lut_oop": thermoelastic.lut_oop,
                    "doy": 8000.0 % 365.24,
                    "instruments": ["C1", "C2", "C3", "C4", "C5"],
                },
            },
            {
                "name": "instr3",
                "origin": "com3",
                # clockwise rotation of 90 degrees about the x-axis
                "rotation": np.array([-np.radians(90.0), 0.0, 0.0]),
                "translation": np.array([1.0, 1.0, 1.0]),
            },
            {
                "name": "instr4",
                "origin": "platform",
                # Thermoelastic model from instance
                "time_based_transform": per_cam_models["C4"],
            },
        ],
        "aliases": {
            "C1": "instr1",
            "C2": "instr2",
            "C3": "instr3",
            "C4": "instr4",
        },
    }

    model = GenericPlatformModel(**config_example_2_json)

    return model


ref_instr3_to_C2 = np.array(
    [
        [1.0, 0.07941818, 2.07355909],
        [1.0, 0.07943831, 2.07357634],
        [1.0, 0.07945836, 2.07359354],
        [1.0, 0.07947835, 2.07361068],
        [1.0, 0.07949827, 2.07362776],
        [1.0, 0.07951812, 2.07364478],
        [1.0, 0.07953791, 2.07366174],
        [1.0, 0.07955762, 2.07367864],
        [1.0, 0.07957726, 2.07369548],
        [1.0, 0.07959684, 2.07371226],
    ]
)


@pytest.mark.parametrize(
    "frame_in, frame_out, pos, ref, atol",
    [
        ("platform", "com1", [1.0, 1.0, 1.0], [0.5, -0.5, 0.5], 1e-15),
        ("com1", "platform", [0.5, -0.5, 0.5], [1.0, 1.0, 1.0], 1e-15),
        ("platform", "instr1", [1.0, 1.0, 1.0], [-0.5, -0.5, 0.5], 1e-15),
        ("platform", "instr2", [1.0, 1.0, 1.0], [0.0, 2.0, 0.0], 1e-15),
        ("instr2", "platform", [0.0, 2.0, 0.0], [1.0, 1.0, 1.0], 1e-15),
        ("instr2", "instr1", [0.0, 2.0, 0.0], [0.0, 1.0, 0.0], 1e-15),
        ("instr1", "instr2", [0.0, 1.0, 0.0], [0.0, 2.0, 0.0], 1e-15),
        ("instr3", "C2", [0.0, 1.0, 0.0], ref_instr3_to_C2, 1e-8),
        ("instr3", "C3", [0.0, 1.0, 0.0], [0.0, 1.0, 0.0], 1e-15),
        ("refined_instr2", "instr2", [1.0, 2.0, 3.0], [1.0, 2.0, 1.5], 1e-15),
        ("platform", "refined_instr2", [1.0, 2.0, 3.0], [-2.0, 2.0, -2.0], 1e-15),
    ],
    ids=[
        "platform_to_com1",
        "com1_to_platform",
        "platform_to_instr1",
        "platform_to_instr2",
        "instr2_to_platform",
        "instr2_to_instr1",
        "instr1_to_instr2",
        "instr3_to_C2",
        "identity",
        "refined_to_instr2",
        "platform_to_refined",
    ],
)
def test_transform_position(gpm, frame_in, frame_out, pos, ref, atol):
    """
    Unit test for GenericPlatformModel.transform_position
    """

    dataset = {
        "los_pos": pos,
        "los_vec": np.array([1, 1, 1]),
        "times": {
            "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(10)], dtype="float64"),
        },
    }
    gpm.transform_position(dataset, frame_in, frame_out)
    npt.assert_allclose(
        ref,
        dataset["los_pos"],
        atol=atol,
    )


ref_instr2_to_instr3 = np.array(
    [
        [0.92058182, 1.0, -1.07355909],
        [0.92056169, 1.0, -1.07357634],
        [0.92054164, 1.0, -1.07359354],
        [0.92052165, 1.0, -1.07361068],
        [0.92050173, 1.0, -1.07362776],
        [0.92048188, 1.0, -1.07364478],
        [0.92046209, 1.0, -1.07366174],
        [0.92044238, 1.0, -1.07367864],
        [0.92042274, 1.0, -1.07369548],
        [0.92040316, 1.0, -1.07371226],
    ]
)


@pytest.mark.parametrize(
    "frame_in, frame_out, vec, ref, atol",
    [
        ("com1", "instr1", [1.0, 1.0, 1.0], [-1.0, 1.0, 1.0], 1e-15),
        ("instr1", "com1", [-1.0, 1.0, 1.0], [1.0, 1.0, 1.0], 1e-15),
        ("platform", "instr2", [1, 1, 1], [-1.0, 1.0, -1.0], 1e-15),
        ("instr2", "instr3", [1, 1, 1], ref_instr2_to_instr3, 1e-6),
    ],
    ids=[
        "com1_to_instr1",
        "instr1_to_com1",
        "platform_to_instr2",
        "instr2_to_instr3",
    ],
)
def test_transform_direction(gpm, frame_in, frame_out, vec, ref, atol):
    """
    Unit test for GenericPlatformModel.transform_direction
    """
    dataset = {
        "los_pos": np.array([0, 0, 0]),
        "los_vec": np.array(vec),
        "times": {
            "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(10)], dtype="float64"),
        },
    }
    gpm.transform_direction(dataset, frame_in, frame_out)
    npt.assert_allclose(
        ref,
        dataset["los_vec"],
        atol=atol,
    )


def test_generic_platform_model_get_transform(gpm):
    """
    Unit test for GenericPlatformModel.get_transform
    """

    dataset = {
        "times": {
            "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(10)], dtype="float64"),
        }
    }

    gpm.get_transforms(dataset, "com3", "platform")

    npt.assert_allclose([0.0, 0.0, 0.0], dataset["translations"], atol=1e-15)
    ref_rotations = np.array(
        [
            [-0.99926734, -0.03827236, -0.0, 0.0],
            [-0.99926699, -0.03828172, -0.0, 0.0],
            [-0.99926663, -0.03829106, -0.0, 0.0],
            [-0.99926627, -0.03830036, -0.0, 0.0],
            [-0.99926592, -0.03830963, -0.0, 0.0],
            [-0.99926556, -0.03831887, -0.0, 0.0],
            [-0.99926521, -0.03832807, -0.0, 0.0],
            [-0.99926486, -0.03833725, -0.0, 0.0],
            [-0.99926451, -0.03834639, -0.0, 0.0],
            [-0.99926416, -0.0383555, -0.0, 0.0],
        ]
    )
    npt.assert_allclose(ref_rotations, dataset["rotations"], atol=1e-8)


def test_generic_platform_model_get_transform_matrix(gpm):
    """
    Unit test for GenericPlatformModel.get_transform
    """

    dataset = {
        "times": {
            "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(10)], dtype="float64"),
        }
    }

    gpm.get_transforms(dataset, "refined_instr2", "platform")

    npt.assert_allclose([-1.0, 1.0, 1.0], dataset["translations"], atol=1e-15)
    ref_matrix = np.array(
        [
            [0.0, 1.0, 0.0],
            [0.0, 0.0, -0.5],
            [-1.0, 0.0, 0.0],
        ]
    )
    npt.assert_allclose(ref_matrix, dataset["matrix"], atol=1e-8)


def test_compare_asgard_sxgeo_platform():
    """
    Compare the transformations between ASGARD and SXGeo.
    """

    # Input data dumped from a S2 MSI context
    # np.set_printoptions(formatter={'float': lambda x: "{0:0.10f}".format(x)})
    input_los_vec = np.array([[-0.0233755550, 0.1818363989, 0.9830509181]])

    # Angles for the "piloting_to_msi" transform
    angles = np.array([-0.1556, 0.7759, 0.3132], np.float64) / 1000.0

    # There is a single non-zero rotation transformation
    states = {
        "states": [
            {
                "name": "msi",
                "origin": "piloting",
                "rotation": angles,
                "euler_order": "YXZ",
            },
        ]
    }

    # This is the intermediate output from SXGeo (see LOSBuilder.getLOS) that serves as a reference.
    # These correspond to the "msi_to_piloting" transform
    sxgeo = np.array([[-0.0240813927, 0.181690988, 0.9830607669]])

    # Idem with the ASGARD model
    dataset = {"los_vec": input_los_vec}
    asgard_model = GenericPlatformModel(**states)
    asgard_model.transform_direction(
        dataset,
        frame_in="msi",
        frame_out="piloting",
    )
    asgard = dataset["los_vec"]

    # Basically all that ASGARD will do in that case is:
    #  - create a scipy.spatial.transform.Rotation from Euler angles, note that the angles should be
    #    given in the same order as the Euler order "YXZ": angle_Y, angle_X, angle_Z
    #  - invert the rotation to obtain the msi_to_piloting transform
    asgard_simple = R.from_euler("YXZ", [angles[1], angles[0], angles[2]]).inv().apply(input_los_vec)
    assert (asgard == asgard_simple).all()

    # Compare sxgeo with the ASGARD implementation
    assert np.allclose(sxgeo, asgard, atol=1.0e-8, rtol=0)
