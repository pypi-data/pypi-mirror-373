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
Unit tests for drivers.sentinel_1_legacy
"""

import os
import os.path as osp

import numpy as np
import pytest
from drivers.sentinel_1_legacy import S1LegacyDriver
from lxml import etree
from scipy.spatial.transform import Rotation as R

from asgard.core.logger import initialize
from asgard.core.schema import (
    ATTITUDE_SCHEMA,
    ORBIT_STATE_VECTORS_SCHEMA,
    validate_or_throw,
)
from asgard.models.body import EarthBody
from asgard.models.time import TimeReference

TEST_DIR = osp.dirname(__file__)

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

initialize("dfdl")


@pytest.fixture(name="driver", scope="module")
def given_legacy_driver():
    """
    Provide a Sentinel 1 legacy driver with IERS bulletin B
    """
    iers_data = S1LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    return S1LegacyDriver(EarthBody(time_reference=time_model))


def test_read_subcommutated_s1_data(driver):
    """
    Unit test for extraction of S1 sub-commutated data
    """

    assert driver is not None

    isp_path = osp.join(
        ASGARD_DATA,
        "S1ASARdataset",
        "S1A_EW_RAW__0SDH_20221111T114657_20221111T114758_045846_057C1E_9592.SAFE",
        "s1a-ew-raw-s-hh-20221111t114657-20221111t114758-045846-057c1e.dat",
    )

    orbit, attitude = driver.read_sub_commutated_data(isp_path, abs_orbit=45846)

    assert orbit is not None
    assert attitude is not None

    validate_or_throw(orbit, ORBIT_STATE_VECTORS_SCHEMA)
    validate_or_throw(attitude, ATTITUDE_SCHEMA)

    assert np.allclose(orbit["times"]["GPS"]["offsets"][0], 8350.491134259259, rtol=0, atol=1e-9)
    assert np.allclose(
        orbit["positions"][0], [1090644.64085965, -2007707.59976609, 6686675.67740303], rtol=0, atol=1e-6
    )
    assert np.allclose(orbit["velocities"][0], [-5.33160877e00, -7.26506934e03, -2.17594287e03], rtol=0, atol=1e-4)

    assert np.allclose(attitude["times"]["GPS"]["offsets"][0], 8350.4911328125, rtol=0, atol=1e-9)
    assert np.allclose(attitude["quaternions"][0], [0.29801461, 0.88681412, 0.25343516, 0.24600542], rtol=0, atol=1e-7)
    assert np.allclose(
        attitude["angular_rates"][0], [-3.17540216e-05, -9.56881617e-04, -4.67963459e-04], rtol=0, atol=1e-9
    )

    # Write output orbit file and attitude file
    out_dir = osp.join(TEST_DIR, "outputs", "sar")
    os.makedirs(out_dir, exist_ok=True)
    orbit_scratch_path = osp.join(out_dir, "s1_orbit.xml")
    att_scratch_path = osp.join(out_dir, "s1_attitude.xml")

    driver.write_orbit_file(orbit, orbit_scratch_path, mission="SENTINEL-1")
    driver.write_attitude_file(attitude, att_scratch_path, mission="SENTINEL-1")


def test_propagate_orbit_number(driver):
    """
    Unit test for orbit number propagation
    """

    positions = np.array(
        [
            [-1351020.389002, 6946799.449605, 150.0],
            [-1351020.389002, 6946799.449605, 50.0],
            [-1351020.389002, 6946799.449605, -50.0],
            [-1351020.389002, 6946799.449605, -150.0],
            [-1351020.389002, 6946799.449605, -50.0],
            [-1351020.389002, 6946799.449605, 50.0],
            [-1351020.389002, 6946799.449605, 150.0],
            [-1351020.389002, 6946799.449605, 50.0],
            [-1351020.389002, 6946799.449605, -50.0],
            [-1351020.389002, 6946799.449605, -150.0],
            [-1351020.389002, 6946799.449605, -50.0],
            [-1351020.389002, 6946799.449605, 50.0],
        ]
    )

    orb_num = driver.propagate_orbit_number(positions, 42)

    ref_orb = [42, 42, 42, 42, 42, 43, 43, 43, 43, 43, 43, 44]

    assert np.all(orb_num == ref_orb)
    assert orb_num.dtype == np.int32


def test_propagate_orbit_number_dask(driver):
    """
    Unit test for orbit number propagation using dask
    """
    import dask.array as da

    positions = da.array(
        [
            [-1351020.389002, 6946799.449605, 150.0],
            [-1351020.389002, 6946799.449605, 50.0],
            [-1351020.389002, 6946799.449605, -50.0],
            [-1351020.389002, 6946799.449605, -150.0],
            [-1351020.389002, 6946799.449605, -50.0],
            [-1351020.389002, 6946799.449605, 50.0],
            [-1351020.389002, 6946799.449605, 150.0],
            [-1351020.389002, 6946799.449605, 50.0],
            [-1351020.389002, 6946799.449605, -50.0],
            [-1351020.389002, 6946799.449605, -150.0],
            [-1351020.389002, 6946799.449605, -50.0],
            [-1351020.389002, 6946799.449605, 50.0],
        ]
    )
    orb_num = driver.propagate_orbit_number_dask(positions, 42)
    ref_orb = [42, 42, 42, 42, 42, 43, 43, 43, 43, 43, 43, 44]

    assert da.all(orb_num == ref_orb)
    assert orb_num.dtype == np.int32


def test_convert_quaternion(driver):
    """
    Unit test for attitude composition
    """
    att_file = osp.join(TEST_DIR, "resources", "S1", "PVT_ATT_20221111T114656", "s1_attitude.xml")
    attitude = driver.read_attitude_file(att_file)
    s1_to_eocfi = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, -1]], dtype="float64")
    attitude_eocfi = driver.apply_attitude_rotation(attitude, s1_to_eocfi)

    assert attitude_eocfi is not None

    vec = np.random.rand(3)
    rot_s1 = R.from_quat(attitude["quaternions"][0])
    rot_eocfi = R.from_quat(attitude_eocfi["quaternions"][0])
    rot_s1_to_eocfi = R.from_matrix(s1_to_eocfi)

    vec_out = rot_s1.apply(vec)
    vec_out_bis = rot_eocfi.apply(rot_s1_to_eocfi.apply(vec))

    assert np.allclose(vec_out, vec_out_bis, rtol=0, atol=1e-9)

    assert attitude["times"] == attitude_eocfi["times"]

    # write ouput attitudes
    out_dir = osp.join(TEST_DIR, "outputs", "sar")
    os.makedirs(out_dir, exist_ok=True)
    att_scratch_path = osp.join(out_dir, "s1_attitude_eocfi.xml")
    driver.write_attitude_file(attitude_eocfi, att_scratch_path, mission="SENTINEL-1")


def test_convert_quaternion_eocfi_note(driver):
    """
    Unit test for attitude composition with data from EOCFI note 052
    """

    attitude = {
        "quaternions": np.array(
            [
                -0.9336623549461364746,
                0.02849436365067958832,
                -0.1522108763456344604,
                -0.3229468762874603272,
            ],
            dtype="float64",
        ),
    }

    s1_to_eocfi = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, -1]], dtype="float64")

    ref_output_quaternion = np.array(
        [
            -0.335987242547,
            0.120728573839,
            0.640050374327,
            0.680347486678,
        ],
        dtype="float64",
    )

    attitude_eocfi = driver.apply_attitude_rotation(attitude, s1_to_eocfi)

    assert np.allclose(attitude_eocfi["quaternions"], ref_output_quaternion, rtol=0, atol=1e-7)


@pytest.fixture(name="tree", scope="module")
def given_parsed_annotation():
    """
    Read the content of the annotation file
    """

    annotation_path = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS1",
        "s1a-ew1-slc-hh-20221112t122835-20221112t122939-045861-057ca5-001.xml",
    )
    return etree.parse(annotation_path)


def test_load_annotation_swath_name(driver, tree):
    """
    Unit test for S1LegacyDriver.get_swath_name()
    """

    name = driver.get_swath_name(tree)

    assert name == "EW1"


def test_load_annotation_swath(driver, tree):
    """
    Unit test for S1LegacyDriver.get_swath()
    """

    swath = driver.get_swath(tree)

    expected_keys = [
        "azimuth_times",
        "azimuth_convention",
        "azimuth_time_interval",
        "burst_lines",
        "slant_range_time",
        "range_sampling_rate",
        "burst_samples",
    ]
    for key in expected_keys:
        assert key in swath, f"Missing key {key!r}"

    ref_times = np.array(
        [
            35.385453,
            38.421416,
            41.463217,
            44.49626,
            47.538062,
            50.579863,
            53.615826,
            56.654707,
            59.69067,
            62.732471,
            65.771353,
            68.810235,
            71.849117,
            74.88508,
            77.923962,
            80.962844,
            84.001726,
            87.040608,
            90.07949,
            93.115452,
            96.157254,
        ],
        dtype="float64",
    )
    assert np.allclose(swath["azimuth_times"]["offsets"], ref_times, rtol=0, atol=1e-4)

    assert swath["burst_lines"] == 1168
    assert swath["burst_samples"] == 8590


def test_load_annotation_geolocation(driver, tree):
    """
    Unit test for S1LegacyDriver.get_geolocation()
    """

    geo_grid = driver.get_geolocation(tree)

    expected_keys = ["ground", "image", "azimuth_time", "range_time", "incidence_angle", "elevation_angle"]

    for key in expected_keys:
        assert key in geo_grid

    assert geo_grid["image"].shape == (462, 2)
    assert geo_grid["ground"].shape == (462, 3)
    assert geo_grid["azimuth_time"]["offsets"].shape == (462,)
    assert geo_grid["range_time"].shape == (462,)
    assert geo_grid["incidence_angle"].shape == (462,)
    assert geo_grid["elevation_angle"].shape == (462,)


def test_load_annotation_terrain_height(driver, tree):
    """
    Unit test for S1LegacyDriver.get_terrain_height()
    """

    terrain_height = driver.get_terrain_height(tree)

    assert "azimuth" in terrain_height
    assert "height" in terrain_height

    assert len(terrain_height["height"]) == 9
    assert len(terrain_height["azimuth"]["offsets"]) == 9

    assert np.allclose(terrain_height["height"][0], 138.44, rtol=0, atol=0.01)
    assert np.allclose(terrain_height["azimuth"]["offsets"][0], 25.385453, rtol=0, atol=1e-3)


def test_load_annotation_attitude(driver, tree):
    """
    Unit test for S1LegacyDriver.get_attitude()
    """

    attitude = driver.get_attitude(tree)

    expected_keys = ["times", "quaternions", "angular_rates", "platform_angles"]
    for key in expected_keys:
        assert key in attitude

    assert np.allclose(attitude["times"]["UTC"]["offsets"][0], 34.874996, rtol=0, atol=1e-3)

    first_att = R.from_quat(attitude["quaternions"][0])
    ref_att = R.from_quat([-3.596351e-01, 5.993724e-03, 8.309419e-01, -4.244553e-01])
    quat_error = (first_att * ref_att.inv()).magnitude()
    assert quat_error < 1e-6

    ref_rates = [-3.042613934667315e-05, -9.527563233859837e-04, -4.670456110034138e-04]
    rate_error = np.abs(attitude["angular_rates"][0] - ref_rates)
    assert np.all(rate_error < 1e-9)

    ref_roll_pitch_yaw = [-1.717775753155568e01, 3.911673070105371e01, -1.320258853083685e02]
    platform_error = np.abs(attitude["platform_angles"][0] - ref_roll_pitch_yaw)
    assert np.all(platform_error < 1e-9)


def test_load_annotation_antenna_pattern(driver, tree):
    """
    Unit test for S1LegacyDriver.get_antenna_pattern()
    """

    antenna_pattern = driver.get_antenna_pattern(tree)

    expected_keys = [
        "azimuth_time",
        "slant_range_time",
        "elevation_angle",
        "elevation_pattern",
        "incidence_angle",
        "terrain_height",
        "roll",
    ]
    for key in expected_keys:
        assert key in antenna_pattern

    assert antenna_pattern["azimuth_time"]["offsets"].shape == (22,)
    assert antenna_pattern["slant_range_time"].shape == (22, 270)
    assert antenna_pattern["elevation_angle"].shape == (22, 270)
    assert antenna_pattern["elevation_pattern"].shape == (22, 270)
    assert antenna_pattern["incidence_angle"].shape == (22, 270)
    assert antenna_pattern["terrain_height"].shape == (22,)
    assert antenna_pattern["roll"].shape == (22,)

    assert np.allclose(antenna_pattern["azimuth_time"]["offsets"][0], 35.385453, rtol=0, atol=1e-3)
    assert np.allclose(antenna_pattern["slant_range_time"][0, 0], 4.956219e-03, rtol=0, atol=1e-6)
    assert np.allclose(antenna_pattern["elevation_angle"][0, 0], 1.690991e01, rtol=0, atol=1e-4)
    assert np.allclose(antenna_pattern["elevation_pattern"][0, 0], -6.447772e12 - 2.299737e13j, rtol=0, atol=1e9)
    assert np.allclose(antenna_pattern["incidence_angle"][0, 0], 1.889963e01, rtol=0, atol=1e-4)
    assert np.allclose(antenna_pattern["terrain_height"][0], 8.609705882352941e01, rtol=0, atol=1e-3)
    assert np.allclose(antenna_pattern["roll"][0], 2.972352354956712e01, rtol=0, atol=1e-3)


@pytest.mark.skip(reason="needs dataset PDGSANOM-12037")
def test_read_subcommutated_tds1(driver):
    """
    Unit test for extraction of S1 sub-commutated data from TDS 1
    """

    assert driver is not None

    isp_path = osp.join(
        ASGARD_DATA,
        "S1_L12",
        "PDGSANOM-12037",
        "S1A_EW_RAW__0SDH_20221112T122835_20221112T122943_045861_057CA5_588C.SAFE",
        "s1a-ew-raw-s-hh-20221112t122835-20221112t122943-045861-057ca5.dat",
    )

    orbit, attitude = driver.read_sub_commutated_data(isp_path, abs_orbit=45861)

    s1_to_eocfi = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, -1]], dtype="float64")
    attitude_eocfi = driver.apply_attitude_rotation(attitude, s1_to_eocfi)

    # dump orbit and attitude
    out_dir = osp.join(TEST_DIR, "outputs", "sar", "tds1")
    os.makedirs(out_dir, exist_ok=True)
    orbit_scratch_path = osp.join(out_dir, "s1_orbit.xml")
    att_scratch_path = osp.join(out_dir, "s1_attitude_eocfi.xml")

    driver.write_orbit_file(orbit, orbit_scratch_path, mission="SENTINEL-1")
    driver.write_attitude_file(attitude_eocfi, att_scratch_path, mission="SENTINEL-1")


@pytest.mark.skip(reason="needs dataset PDGSANOM-12247")
def test_read_subcommutated_tds2():
    """
    Unit test for extraction of S1 sub-commutated data from TDS 2
    """

    iers_data = S1LegacyDriver.read_iers_file(
        osp.join(
            TEST_DIR,
            "resources",
            "orekit",
            "IERS",
            "S2__OPER_AUX_UT1UTC_ADG__20220916T000000_V20220916T000000_20230915T000000.txt",
        )
    )
    time_model = TimeReference(iers_bulletin_a=iers_data)
    driver = S1LegacyDriver(EarthBody(time_reference=time_model))

    isp_path = osp.join(
        ASGARD_DATA,
        "S1_L12",
        "PDGSANOM-12247",
        "S1A_IW_RAW__0SDV_20230131T155748_20230131T155820_047030_05A42A_1AA8.SAFE",
        "s1a-iw-raw-s-vh-20230131t155748-20230131t155820-047030-05a42a.dat",
    )

    orbit, attitude = driver.read_sub_commutated_data(isp_path, abs_orbit=45861)

    s1_to_eocfi = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, -1]], dtype="float64")
    attitude_eocfi = driver.apply_attitude_rotation(attitude, s1_to_eocfi)

    # dump orbit and attitude
    out_dir = osp.join(TEST_DIR, "outputs", "sar", "tds2")
    os.makedirs(out_dir, exist_ok=True)
    orbit_scratch_path = osp.join(out_dir, "s1_orbit.xml")
    att_scratch_path = osp.join(out_dir, "s1_attitude_eocfi.xml")

    driver.write_orbit_file(orbit, orbit_scratch_path, mission="SENTINEL-1")
    driver.write_attitude_file(attitude_eocfi, att_scratch_path, mission="SENTINEL-1")


@pytest.mark.skip(reason="needs dataset S1A_S4_RAW__0SDH_20220801T234915")
def test_read_subcommutated_tds3():
    """
    Unit test for extraction of S1 sub-commutated data from TDS 3
    """

    iers_data = S1LegacyDriver.read_iers_file(
        osp.join(
            TEST_DIR,
            "resources",
            "bulletinb-415.txt",
        )
    )
    time_model = TimeReference(iers_bulletin_b=iers_data)
    driver = S1LegacyDriver(EarthBody(time_reference=time_model))

    isp_path = osp.join(
        ASGARD_DATA,
        "S1ASARdataset",
        "S1A_S4_RAW__0SDH_20220801T234915_20220801T234941_044366_054B70_9349.SAFE",
        "s1a-s4-raw-s-hh-20220801t234915-20220801t234941-044366-054b70.dat",
    )

    orbit, attitude = driver.read_sub_commutated_data(isp_path, abs_orbit=44366)

    s1_to_eocfi = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, -1]], dtype="float64")
    attitude_eocfi = driver.apply_attitude_rotation(attitude, s1_to_eocfi)

    # dump orbit and attitude
    out_dir = osp.join(TEST_DIR, "outputs", "sar", "tds3")
    os.makedirs(out_dir, exist_ok=True)
    orbit_scratch_path = osp.join(out_dir, "s1_orbit.xml")
    att_scratch_path = osp.join(out_dir, "s1_attitude_eocfi.xml")

    driver.write_orbit_file(orbit, orbit_scratch_path, mission="SENTINEL-1")
    driver.write_attitude_file(attitude_eocfi, att_scratch_path, mission="SENTINEL-1")


@pytest.mark.skip(reason="needs dataset S1A_WV_RAW__0SSV_20220801T200456")
def test_read_subcommutated_tds4():
    """
    Unit test for extraction of S1 sub-commutated data from TDS 4
    """

    iers_data = S1LegacyDriver.read_iers_file(
        osp.join(
            TEST_DIR,
            "resources",
            "bulletinb-415.txt",
        )
    )
    time_model = TimeReference(iers_bulletin_b=iers_data)
    driver = S1LegacyDriver(EarthBody(time_reference=time_model))

    isp_path = osp.join(
        ASGARD_DATA,
        "S1ASARdataset",
        "S1A_WV_RAW__0SSV_20220801T200456_20220801T203542_044363_054B5E_12FF.SAFE",
        "s1a-wv-raw-s-vv-20220801t200456-20220801t203542-044363-054b5e.dat",
    )

    orbit, attitude = driver.read_sub_commutated_data(isp_path, abs_orbit=44363)

    s1_to_eocfi = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, -1]], dtype="float64")
    attitude_eocfi = driver.apply_attitude_rotation(attitude, s1_to_eocfi)

    # dump orbit and attitude
    out_dir = osp.join(TEST_DIR, "outputs", "sar", "tds4")
    os.makedirs(out_dir, exist_ok=True)
    orbit_scratch_path = osp.join(out_dir, "s1_orbit.xml")
    att_scratch_path = osp.join(out_dir, "s1_attitude_eocfi.xml")

    driver.write_orbit_file(orbit, orbit_scratch_path, mission="SENTINEL-1")
    driver.write_attitude_file(attitude_eocfi, att_scratch_path, mission="SENTINEL-1")
