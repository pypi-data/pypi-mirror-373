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
Unit tests for transformations
"""

import os.path as osp

import numpy as np
import pytest
from drivers.sentinel_3_legacy import S3LegacyDriver
from scipy.spatial.transform import Rotation as R

from asgard.core.time import JD_TO_SECONDS
from asgard.core.transform import (
    DynamicRotation,
    HomothetyTransform,
    RigidTransform,
    StaticTransform,
    TimeBasedTransform,
)
from asgard.models.thermoelastic import ThermoelasticModel

SAMPLE_VECTOR = np.array([3.0, -2.0, 1.0])

TEST_DIR = osp.dirname(__file__)


def given_rigid_1tr():
    """
    Fixture to generate a single translation RigidTransform
    """
    return RigidTransform(translation=np.array([1.0, 2.0, -0.5]))


def given_rigid_1rot():
    """
    Fixture to generate a single rotation matrix RigidTransform
    """
    return RigidTransform(
        rotation=np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0],
                [0.0, 1.0, 0.0],
            ]
        )
    )


def given_rigid_1tr_rot():
    """
    Fixture to generate a single rotation matrix RigidTransform
    """
    return RigidTransform(
        translation=np.array([1.0, 2.0, -0.5]),
        rotation=np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0],
                [0.0, 1.0, 0.0],
            ]
        ),
    )


def given_rigid_1quat():
    """
    Fixture to generate a single quaternion RigidTransform
    """
    return RigidTransform(rotation=np.array([1.0, 0.0, 0.0, 1.0]))


def given_rigid_1euler():
    """
    Fixture to generate a single Euler RigidTransform
    """
    return RigidTransform(
        rotation=[1.57079633, 0.0, 0.0],
    )


def given_rigid_1euler_yxz():
    """
    Fixture to generate a single Euler RigidTransform
    """
    return RigidTransform(
        rotation=np.array([-0.1556, 0.7759, 0.3132]) / 1000.0,
        euler_order="YXZ",
    )


def given_1homothety():
    """
    Fixture to generate a single HomothetyTransform
    """
    return HomothetyTransform(
        homothety=[1.0, 2.0, -1.0],
    )


def given_static_mirror():
    """
    Fixture to generate a single StaticTransform with Z-mirror
    """
    return StaticTransform(
        matrix=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, -1.0],
        ],
    )


def given_static_random():
    """
    Fixture to generate a single StaticTransform with random translation and matrix
    """
    return StaticTransform(
        translation=[1.0, 2.0, 3.0],
        matrix=[
            [1.0, 0.2, -0.1],
            [0.1, 1.0, 0.0],
            [0.0, -0.2, -1.0],
        ],
    )


@pytest.mark.parametrize(
    "trans, pos_out, dir_out, len_out",
    [
        (given_rigid_1tr(), [4.0, 0.0, 0.5], SAMPLE_VECTOR, 1),
        (given_rigid_1rot(), [3.0, -1.0, -2.0], [3.0, -1.0, -2.0], 1),
        (given_rigid_1tr_rot(), [4.0, 1.0, -2.5], [3.0, -1.0, -2.0], 1),
        (given_rigid_1quat(), [3.0, -1.0, -2.0], [3.0, -1.0, -2.0], 1),
        (given_rigid_1euler(), [3.0, -1.0, -2.0], [3.0, -1.0, -2.0], 1),
        (given_rigid_1euler_yxz(), [3.00140149, -1.99890468, 0.99798255], [3.00140149, -1.99890468, 0.99798255], 1),
        (given_1homothety(), [3.0, -4.0, -1.0], [3.0, -4.0, -1.0], 1),
        (given_static_mirror(), [3.0, -2.0, -1.0], [3.0, -2.0, -1.0], 1),
        (given_static_random(), [3.5, 0.3, 2.4], [2.5, -1.7, -0.6], 1),
    ],
    ids=["1tr", "1rot", "1tr_rot", "1quat", "1euler", "1eulerYXZ", "1homothety", "1mirror", "1random"],
)
def test_static_transform_generic(trans, pos_out, dir_out, len_out):
    """
    Generic unit test for StaticTransform
    """

    # check transform_XXX calls
    assert np.allclose(trans.transform_position(SAMPLE_VECTOR), pos_out)
    assert np.allclose(trans.transform_direction(SAMPLE_VECTOR), dir_out)

    # check transform on plain lists
    sample_list = SAMPLE_VECTOR.tolist()
    assert np.allclose(trans.transform_position(sample_list), pos_out)
    assert np.allclose(trans.transform_direction(sample_list), dir_out)

    # check len() operator
    assert len(trans) == len_out

    # invert transform
    inv_trans = trans.inv()
    assert np.allclose(inv_trans.transform_position(np.array(pos_out)), SAMPLE_VECTOR)
    assert np.allclose(inv_trans.transform_direction(np.array(dir_out)), SAMPLE_VECTOR)

    # compose direct and inverse transforms
    identity_trans = inv_trans * trans
    assert np.allclose(identity_trans.transform_position(SAMPLE_VECTOR), SAMPLE_VECTOR)
    assert np.allclose(identity_trans.transform_direction(SAMPLE_VECTOR), SAMPLE_VECTOR)


def test_static_transform_on_vector_stack():
    """
    Test case for a single static transform applied on a vector stack
    """
    vector_stack = np.array([SAMPLE_VECTOR, SAMPLE_VECTOR + 1, SAMPLE_VECTOR + 2, SAMPLE_VECTOR + 3])
    transfo = given_static_mirror()

    result = transfo.transform_direction(vector_stack)
    reference = np.array(
        [
            [3.0, -2.0, -1.0],
            [4.0, -1.0, -2.0],
            [5.0, 0.0, -3.0],
            [6.0, 1.0, -4.0],
        ]
    )
    assert np.all(result == reference)


def test_static_transform_stack_on_vector_stack():
    """
    Test case for a stack of static transform applied on a vector stack
    """
    vector_stack = np.array([SAMPLE_VECTOR, SAMPLE_VECTOR + 1, SAMPLE_VECTOR + 2, SAMPLE_VECTOR + 3])
    mirror_x = np.eye(3)
    mirror_y = np.eye(3)
    mirror_z = np.eye(3)
    mirror_x[0, 0] = -1.0
    mirror_y[1, 1] = -1.0
    mirror_z[2, 2] = -1.0
    transfo = StaticTransform(matrix=[mirror_x, mirror_y, mirror_z, mirror_x])

    result = transfo.transform_direction(vector_stack)
    reference = np.array(
        [
            [-3.0, -2.0, 1.0],
            [4.0, 1.0, 2.0],
            [5.0, 0.0, -3.0],
            [-6.0, 1.0, 4.0],
        ]
    )
    assert np.all(result == reference)


def test_transform_matrix_representation():
    """
    Test the matrix representation for StaticTransform, RigidTransform and Homothety
    """

    transfo = given_static_mirror()
    mirror_z = np.eye(3)
    mirror_z[2, 2] = -1.0
    assert np.all(transfo.matrix == mirror_z)

    homothety = given_1homothety()
    assert np.all(homothety.matrix == [[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, -1.0]])

    rotation = given_rigid_1rot()
    ref_rot_matrix = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])
    assert np.allclose(rotation.matrix, ref_rot_matrix, rtol=0, atol=1e-11)


def test_rigid_and_homothety_composed():
    """
    Test composition of a RigidTransform and a Homothety
    """

    homothety = given_1homothety()
    rotation = given_rigid_1rot()
    transfo = homothety * rotation
    assert isinstance(transfo, StaticTransform)

    ref_matrix = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -2.0], [0.0, -1.0, 0.0]])

    assert np.allclose(transfo.matrix, ref_matrix, rtol=0, atol=1e-11)

    transfo = rotation * homothety
    assert isinstance(transfo, StaticTransform)

    ref_matrix = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 2.0, 0.0]])

    assert np.allclose(transfo.matrix, ref_matrix, rtol=0, atol=1e-11)


def test_rigid_transform_fail_with_translation_rotation_mismatch():
    """
    Test to check failure of instantiation for a RigidTransform with 2 rotations and 3 translations
    """
    with pytest.raises(RuntimeError):
        RigidTransform(
            translation=np.ones((3, 3)),
            rotation=[np.eye(3), np.eye(3)],
        )


def test_rigid_transform_fail_on_mirror():
    """
    Test to check failure of instantiation for a RigidTransform with a Z-mirror
    """
    with pytest.raises(RuntimeError):
        RigidTransform(rotation=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]])

    with pytest.raises(RuntimeError):
        RigidTransform(rotation=[np.eye(3), [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]]])


def test_static_transform_fail_on_singular_matrix():
    """
    Test to check failure of instantiation for a StaticTransform with a singular matrix
    """
    with pytest.raises(RuntimeError):
        StaticTransform(matrix=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])

    with pytest.raises(RuntimeError):
        StaticTransform(matrix=[np.eye(3), [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]])


@pytest.mark.parametrize(
    "transfo",
    [
        StaticTransform(matrix=[np.eye(3), np.eye(3)]),
        RigidTransform(rotation=[np.eye(3), np.eye(3)]),
        HomothetyTransform(homothety=np.ones((2, 3))),
    ],
    ids=["static", "rigid", "homothety"],
)
def test_transform_stack_fail_on_single_vector(transfo):
    """
    Test to check failure on transformation of single vector with a transform stack
    """

    sample_list = [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
    sample_vector = np.array(sample_list)
    with pytest.raises(ValueError):
        transfo.transform_position(sample_vector)
    with pytest.raises(ValueError):
        transfo.transform_position(sample_list)
    with pytest.raises(ValueError):
        transfo.transform_direction(sample_vector)
    with pytest.raises(ValueError):
        transfo.transform_direction(sample_list)


@pytest.mark.parametrize(
    "transfo, ref",
    [
        (StaticTransform(matrix=np.eye(3)), {"translation": np.zeros([3]), "matrix": np.eye(3)}),
        (
            RigidTransform(rotation=np.eye(3)),
            {"translation": np.zeros([3]), "rotation": np.array([0.0, 0.0, 0.0, 1.0])},
        ),
        (HomothetyTransform(homothety=np.ones((3,))), {"homothety": np.ones([3])}),
    ],
    ids=["static", "rigid", "homothety"],
)
def test_transform_dump(transfo, ref, allclose_dicts):
    """
    Test how a transform is dumped to dict
    """
    data = transfo.dump()

    assert allclose_dicts(ref, data)


@pytest.fixture(name="tbt", scope="module")
def given_time_based_thermoelastic():
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
    }

    return TimeBasedTransform.build(**config)


def test_time_based_thermoelastic_init(tbt):
    """
    Unit test to check initialization of a time based transform
    """

    assert tbt.pdoy == (132.75074690216616 - 74) / (147 - 74)


def test_time_based_thermoelastic_estimate(tbt):
    """
    Unit test to check generation of StaticTransform from a time array
    """

    frames = {
        "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(10)], dtype="float64"),
    }

    transfo = tbt.estimate(frames)

    assert len(transfo) == 10
    assert np.all(transfo.translation == 0.0)

    ref_quat = np.array(
        [
            [-3.78462929e-05, 1.12564023e-05, -1.96393965e-05, 9.99999999e-01],
            [-3.78431995e-05, 1.12563792e-05, -1.96417085e-05, 9.99999999e-01],
            [-3.78401051e-05, 1.12563524e-05, -1.96440222e-05, 9.99999999e-01],
            [-3.78370132e-05, 1.12563248e-05, -1.96463356e-05, 9.99999999e-01],
            [-3.78339172e-05, 1.12562980e-05, -1.96486487e-05, 9.99999999e-01],
            [-3.78308251e-05, 1.12562727e-05, -1.96509613e-05, 9.99999999e-01],
            [-3.78277319e-05, 1.12562482e-05, -1.96532714e-05, 9.99999999e-01],
            [-3.78246373e-05, 1.12562213e-05, -1.96555863e-05, 9.99999999e-01],
            [-3.78215448e-05, 1.12561982e-05, -1.96578978e-05, 9.99999999e-01],
            [-3.78184520e-05, 1.12561734e-05, -1.96602109e-05, 9.99999999e-01],
        ]
    )

    test_quat = transfo.rotation.as_quat()
    for quat_t, quat_r in zip(test_quat, ref_quat):
        quat_diff = R.from_quat(quat_r) * R.from_quat(quat_t).inv()
        assert quat_diff.magnitude() < 1e-9


def test_time_based_thermoelastic_inverse(tbt):
    """
    Unit test to check inversion of a TimeBasedTransform
    """

    frames = {
        "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(10)], dtype="float64"),
    }

    tbt_inv = tbt.inv()

    transfo = tbt.estimate(frames)
    inv_transfo = tbt_inv.estimate(frames)

    direct_quat = transfo.rotation.as_quat()
    inv_quat = inv_transfo.rotation.as_quat()
    for quat_t, quat_t_inv in zip(direct_quat, inv_quat):
        quat_diff = R.from_quat(quat_t_inv) * R.from_quat(quat_t)
        assert quat_diff.magnitude() < 1e-9


def test_thermoelastic_model_split(tbt):
    """
    Unit test for ThermoelasticModel.split()
    """

    assert isinstance(tbt, ThermoelasticModel)
    individual_models = tbt.split()

    for item in tbt.instruments:
        assert isinstance(individual_models[item], ThermoelasticModel)
        assert individual_models[item].instruments == [item]
        assert individual_models[item].pdoy == tbt.pdoy
        assert np.all(individual_models[item].lut_times == tbt.lut_times)
        assert np.all(individual_models[item].lut_oop == tbt.lut_oop)
        assert len(individual_models[item].quaternion_lut) == 1
        assert individual_models[item].quaternion_lut[item] == tbt.quaternion_lut[item]
        assert np.all(individual_models[item].oop_grid[item] == tbt.oop_grid[item])


@pytest.fixture(name="dyn", scope="module")
def given_dynamic_rotation():
    """
    Instanciate a DynamicRotation transform
    """
    config = {
        "rotation": np.radians(np.array([[90, 0, 0], [-9, 9, 0]], dtype="float64")),
        "epoch": "2024-03-20T11:34:00",
        "unit": "s",
        "central_time": 3.14,
    }
    return DynamicRotation(**config)


def test_dynamic_rotation(dyn):
    """
    Unit test for dynamic transform
    """

    assert dyn is not None

    times = {
        "offsets": 3.14 + np.array([0, 5, 10], dtype="float64"),
        "unit": "s",
        "epoch": "2024-03-20T11:34:00",
        "ref": "GPS",
    }

    static_rot = dyn.estimate(times)
    assert isinstance(static_rot, RigidTransform)

    # apply rotation on sample vector [3, -2, 1]
    rotated = static_rot.transform_direction(SAMPLE_VECTOR)

    ref_rotated = np.array(
        [
            [3.0, -1.0, -2.0],
            [2.82842712, -0.41421356, -2.41421356],
            [1.0, -2.0, -3.0],
        ]
    )
    assert np.allclose(rotated, ref_rotated, rtol=0, atol=1e-6)

    # test with a different input epoch and unit
    cur_date = 8845.481944444444  # 2024-03-20T11:34:00
    times = {
        "offsets": cur_date + (3.14 + np.array([0, 5, 10], dtype="float64")) / JD_TO_SECONDS,
        "ref": "GPS",
    }
    static_rot = dyn.estimate(times)
    rotated = static_rot.transform_direction(SAMPLE_VECTOR)
    assert np.allclose(rotated, ref_rotated, rtol=0, atol=1e-6)


def test_dynamic_rotation_wrong_time_scale(dyn):
    """
    Raise exception if the input time scale is different
    """
    times = {
        "offsets": 3.14 + np.array([0, 5, 10], dtype="float64"),
        "unit": "s",
        "epoch": "2024-03-20T11:34:00",
        "ref": "UTC",
    }

    with pytest.raises(RuntimeError):
        dyn.estimate(times)


def test_dynamic_rotation_inverse(dyn):
    """
    Unit test for dynamic transform inverse
    """

    assert dyn is not None

    times = {
        "offsets": 3.14 + np.array([0, 5, 10], dtype="float64"),
        "unit": "s",
        "epoch": "2024-03-20T11:34:00",
        "ref": "GPS",
    }

    # compute inverse transform
    inv_dyn = dyn.inv()
    inv_rot = inv_dyn.estimate(times)

    static_rot = dyn.estimate(times)
    assert isinstance(static_rot, RigidTransform)

    # apply rotation and inverse on sample vector [3, -2, 1]
    rotated = static_rot.transform_direction(SAMPLE_VECTOR)
    inv_rotated = inv_rot.transform_direction(rotated)

    assert np.allclose(inv_rotated, np.outer(np.ones((3,)), SAMPLE_VECTOR), rtol=0, atol=1e-6)
