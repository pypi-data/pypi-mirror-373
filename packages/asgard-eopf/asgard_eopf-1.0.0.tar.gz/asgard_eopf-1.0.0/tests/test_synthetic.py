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
Unit tests for synthetic products
"""
import os.path as osp

import numpy as np
import pytest
from drivers.explorer_legacy import ExplorerDriver
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import GeodeticComparator

from asgard.sensors.synthetic import GroundTrackGrid

TEST_DIR = osp.dirname(__file__)

SLSTR_DT_THEOR = 0.2999858


@pytest.fixture(name="gtg", scope="module")
def ground_track():
    """
    Fixture to generate a GroundTrackGrid
    """

    orbit_file = osp.join(
        TEST_DIR,
        "resources/S3/FRO/orbit_fro_20221030_eme2000.EOF",
    )
    orbit_data = ExplorerDriver.read_orbit_file(orbit_file)

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources/207_BULLETIN_B207.txt"))

    time_origin = 8338.060745251598
    delta_tp = 8.0 * SLSTR_DT_THEOR / 86400.0
    times = np.array([time_origin + k * delta_tp for k in range(5, 10)], dtype="float64")
    config = {
        "sat": "SENTINEL_3",
        "orbits": [orbit_data],
        "ac_samples": 11,
        "ac_center_position": 5,
        "ac_resolution": 16000.0,
        "times": {"offsets": times},
        "time_origin": time_origin,
        "qc_first_scan": 0,
        "qc_last_scan": 5,
        "eop": {
            "iers_bulletin_b": iers_data,
        },
    }
    product = GroundTrackGrid(**config)
    product.compute_along_track_coordinates()

    return product


def test_ground_track_grid_direct_loc(gtg):
    """
    Unit test for GroundTrackGrid
    """

    assert gtg is not None

    coordinates = np.zeros((5, 11, 2), dtype="int64")
    for row in range(5):
        for col in range(11):
            coordinates[row, col, 0] = col
            coordinates[row, col, 1] = row

    grid, grid_times = gtg.direct_loc(coordinates)

    np.save(osp.join(TEST_DIR, "outputs/small_ground_track_grid.npy"), grid)

    assert np.allclose(grid_times[:, 4], gtg.config["times"]["offsets"])

    geo_comp = GeodeticComparator(gtg.body_model)

    ref_out = np.array(
        [
            [-5.12206929e01, 1.00821393e00, 2.41957605e-06],
            [-5.13610134e01, 9.76787273e-01, 2.42237002e-06],
            [-5.15013313e01, 9.45354719e-01, 2.42609531e-06],
            [-5.16416467e01, 9.13916457e-01, 2.42516398e-06],
            [-5.17819596e01, 8.82472674e-01, 2.42982060e-06],
            [-5.19222702e01, 8.51023560e-01, 2.43168324e-06],
            [-5.20625785e01, 8.19569304e-01, 2.43540853e-06],
            [-5.22028847e01, 7.88110095e-01, 2.43913382e-06],
            [-5.23431887e01, 7.56646121e-01, 2.43913382e-06],
            [-5.24834907e01, 7.25177571e-01, 2.44099647e-06],
            [-5.26237908e01, 6.93704635e-01, 2.44379044e-06],
        ]
    )
    plani_error = geo_comp.planar_error(grid[1], ref_out)
    height_error = np.abs(geo_comp.height_error(grid[1], ref_out))

    assert np.all(plani_error < 0.1)  # 0.1m for 2D error
    assert np.all(height_error < 0.01)  # 0.01m for alti error

    pointing = gtg.across_track_pointing(grid, coordinates, grid_times)

    ref_row_psi = [
        5.667,
        4.54,
        3.409,
        2.274,
        1.138,
        0.0,
        -1.138,
        -2.274,
        -3.409,
        -4.54,
        -5.667,
    ]
    for row in pointing:
        assert np.allclose(row, ref_row_psi, atol=1e-3)


def test_ground_track_grid_sun_angles(gtg):
    """
    Unit test for GroundTrackGrid.sun_angles
    """
    ground = np.array([-5.17819596e01, 8.82472674e-01, 0.0])
    time = np.array([gtg.config["times"]["offsets"][1]])

    angles = gtg.sun_angles(ground, time)

    assert np.allclose(angles, [242.16365374, 151.37504108])


def test_ground_track_grid_incidence_angles(gtg):
    """
    Unit test for GroundTrackGrid.incidence_angles
    """
    ground = np.array([-5.17819596e01, 8.82472674e-01, 0.0])
    time = np.array([gtg.config["times"]["offsets"][1]])

    angles = gtg.incidence_angles(ground, time)

    assert np.allclose(angles, [257.43892549, 1.2814262])


def test_ground_track_grid_along_track(gtg):
    """
    Unit test for GroundTrackGrid.compute_along_track_coordinates
    """

    # We expect to start around 5*16km => 80km since times started after 5 TP
    ref_track_y = [
        80342.45578432,
        96410.94694118,
        112479.53157556,
        128548.1919366,
        144616.94288551,
    ]
    assert np.allclose(gtg.track_y, ref_track_y)

    ref_track_az = [
        347.43707712,
        347.43696537,
        347.43682771,
        347.43666106,
        347.43666106,
    ]

    assert np.allclose(gtg.track_az, ref_track_az)


def test_ground_track_grid_ground_to_xy(gtg):
    """
    Unit test for GroundTrackGrid.ground_to_xy
    """

    coordinates = np.array(
        [
            [-51.89086994, 0.70918467],
            [-52.92, 0.9],
            [-53.0, 0.7],
            [-52.0, 0.9],
            [-51.0, 1.1],
            [-50.0, 1.3],
            [-49.0, 1.5],
            [-52.0, 1.1],
            [-52.0008, 1.20562333],
        ]
    )

    xy_position = gtg.ground_to_xy(coordinates)

    ref_position = np.array(
        [
            [0.0, 8.03424558e04],
            [-1.07213000e05, 1.25868788e05],
            [-1.20720000e05, 1.06221691e05],
            [-7.26700000e03, 1.03578800e05],
            [1.06182000e05, 1.00968466e05],
            [2.19624000e05, 9.83962587e04],
            [3.33058000e05, 9.58658615e04],
            [-2.45600000e03, 1.25164114e05],
            [-2.0, 1.36583075e05],
        ]
    )
    assert np.allclose(xy_position, ref_position)
