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
Unit tests for core.math
"""

import math

import numpy as np

from asgard.core.math import (
    extend_circular_lut,
    flatten_array,
    quat_to_matrix,
    restore_array,
    rotation_matrix,
    slerp,
    slerp_n,
)


def test_slerp():
    """
    Test for slerp function
    """
    quat1 = np.array([7.165851e-05, -9.052763e-05, 4.2369284e-06, 1.0])
    quat2 = np.array([7.365285e-05, -8.847247e-05, -2.0181976e-06, 1.0])

    assert np.allclose(slerp(0.0, quat1, quat2), quat1)
    assert np.allclose(slerp(1.0, quat1, quat2), quat2)

    assert np.allclose(
        slerp(0.5, quat1, quat2),
        [7.26556795e-05, -8.95000494e-05, 1.10936539e-06, 9.99999993e-01],
    )


def test_slerp_n():
    """
    Test for slerp_n function
    """
    quat_lut = np.array(
        [
            [7.165851e-05, -9.052763e-05, 4.2369284e-06, 1.0],
            [1.5267406e-06, -9.0639405e-05, 0.00019370459, 1.0],
            [7.365285e-05, -8.847247e-05, -2.0181976e-06, 1.0],
        ],
        dtype=np.double,
    )
    pos = np.array([0, 1, 2], dtype=np.double)
    assert np.allclose(slerp_n(pos, quat_lut), quat_lut)

    pos2 = np.array([0.5, -0.2, 1.7, 3.4])
    ref_quat = np.array(
        [
            [3.65926249e-05, -9.05835166e-05, 9.89707582e-05, 9.99999990e-01],
            [8.56848632e-05, -9.05052742e-05, -3.36566036e-05, 9.99999990e-01],
            [5.20150168e-05, -8.91225499e-05, 5.66986383e-05, 9.99999990e-01],
            [1.74629393e-04, -8.54387561e-05, -2.76030085e-04, 9.99999990e-01],
        ],
        dtype=np.double,
    )
    assert np.allclose(slerp_n(pos2, quat_lut), ref_quat)


def test_quat_to_matrix():
    """
    Test for quat_to_matrix
    """
    quat1 = [7.165851e-05, -9.052763e-05, 4.2369284e-06, 1.0]
    quat2 = [7.365285e-05, -8.847247e-05, -2.0181976e-06, 1.0]

    ref_mat_1 = [
        [9.99999997e-01, 8.46088265e-06, 1.81055867e-04],
        [-8.48683095e-06, 1.00000000e00, 1.43316253e-04],
        [-1.81054653e-04, -1.43317787e-04, 9.99999987e-01],
    ]

    ref_mat_2 = [
        [9.99999998e-01, -4.04942770e-06, 1.76944643e-04],
        [4.02336270e-06, 1.00000000e00, 1.47306057e-04],
        [-1.76945237e-04, -1.47305343e-04, 9.99999987e-01],
    ]

    assert np.allclose(quat_to_matrix(quat1), ref_mat_1)
    assert np.allclose(quat_to_matrix(quat2), ref_mat_2)


def test_flatten_restore():
    """
    Test for flatten_array and restore_array
    """
    arr1 = np.zeros((5, 4, 2))
    arr2 = np.ones((3))
    arr3 = np.zeros((8, 4, 6))

    farr1 = flatten_array(arr1, last_dim=2)
    farr2 = flatten_array(arr2, last_dim=3)
    farr3 = flatten_array(arr3)

    assert farr1.shape == (20, 2)
    assert farr2.shape == (1, 3)
    assert farr3.shape == (192,)

    rfarr1 = restore_array(farr1, arr1.shape[:-1], last_dim=2)
    rfarr2 = restore_array(farr2, arr2.shape[:-1], last_dim=3)
    rfarr3 = restore_array(farr3, arr3.shape)

    assert rfarr1.shape == arr1.shape
    assert rfarr2.shape == arr2.shape
    assert rfarr3.shape == arr3.shape

    # case where nothing happens
    assert np.allclose(restore_array(arr1, []), arr1)


def test_rotation_matrix():
    """
    Unit test for rotation_matrix
    """

    angle = np.deg2rad(60.0)

    cos_a = 0.5
    sin_a = math.sqrt(3) / 2.0

    ref_x = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, cos_a, -sin_a],
            [0.0, sin_a, cos_a],
        ]
    )

    ref_y = np.array(
        [
            [cos_a, 0.0, sin_a],
            [0.0, 1.0, 0.0],
            [-sin_a, 0.0, cos_a],
        ]
    )

    ref_z = np.array(
        [
            [cos_a, -sin_a, 0.0],
            [sin_a, cos_a, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )

    assert np.allclose(rotation_matrix(angle, "x"), ref_x)
    assert np.allclose(rotation_matrix(angle, "y"), ref_y)
    assert np.allclose(rotation_matrix(angle, "z"), ref_z)


def test_rotation_matrix_array():
    """
    Unit test for rotation_matrix with array input
    """

    angle = np.deg2rad([0.0, 30.0, 45.0, 60.0, 90.0])

    sq3_2 = math.sqrt(3) / 2.0
    sq2_2 = math.sqrt(2) / 2.0

    ref_out = np.array(
        [
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            [
                [1.0, 0.0, 0.0],
                [0.0, sq3_2, -0.5],
                [0.0, 0.5, sq3_2],
            ],
            [
                [1.0, 0.0, 0.0],
                [0.0, sq2_2, -sq2_2],
                [0.0, sq2_2, sq2_2],
            ],
            [
                [1.0, 0.0, 0.0],
                [0.0, 0.5, -sq3_2],
                [0.0, sq3_2, 0.5],
            ],
            [
                [1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0],
                [0.0, 1.0, 0.0],
            ],
        ]
    )

    assert np.allclose(rotation_matrix(angle, "x"), ref_out)


def test_extend_circular_lut():
    """
    Unit test for extend_circular_lut()
    """

    pos = [1, 2, 3, 4]
    val = [3.5, 2.3, -0.5, 1.5]

    ext_pos, ext_val = extend_circular_lut(pos, val, start=1, end=4)

    assert np.any(pos == ext_pos)
    assert np.any(val == ext_val)

    ext_pos, ext_val = extend_circular_lut(pos, val, start=0, end=4)
    assert np.any(ext_pos == [0, 1, 2, 3, 4])
    assert np.any(ext_val == ([4.7] + val))

    ext_pos, ext_val = extend_circular_lut(pos, val, start=0, end=5)
    assert np.any(ext_pos == [0, 1, 2, 3, 4, 5])
    assert np.any(ext_val == ([4.7] + val + [4.7]))

    pos = [-1, 2, 3, 4]
    val = [3.5, 2.3, -0.5, 1.5]

    ext_pos, ext_val = extend_circular_lut(pos, val, start=0, end=5)
    assert np.any(ext_pos == [-1, 2, 3, 4, 5])
    assert np.any(ext_val == (val + [3.1]))

    pos = [1, 2, 3, 4]
    val = np.array([[1, 5], [2, 6], [3, 7], [4, 8]])
    ext_pos, ext_val = extend_circular_lut(pos, val, start=0, end=5)
    assert np.any(ext_pos == [0, 1, 2, 3, 4, 5])
    assert np.any(ext_val == [[0, 4], [1, 5], [2, 6], [3, 7], [4, 8], [0, 4]])
