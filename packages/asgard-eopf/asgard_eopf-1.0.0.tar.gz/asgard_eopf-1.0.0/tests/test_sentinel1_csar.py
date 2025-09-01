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
Unit tests for Sentinel 1 Product
"""

import os
import os.path as osp
import time

import numpy as np
import pytest
from drivers.sentinel_1_legacy import S1LegacyDriver
from helpers.compare import GeodeticComparator

from asgard.core.time import JD_TO_SECONDS
from asgard.models.body import EarthBody
from asgard.models.sar import SPEED_LIGHT
from asgard.models.time import TimeReference
from asgard.sensors.sentinel1.csar import S1SARGeometry

TEST_DIR = osp.dirname(__file__)
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")


@pytest.fixture(name="driver", scope="module")
def given_legacy_driver():
    """
    Create a S1LegacyDriver with IERS bulletin for 2022-11-11
    """
    iers_data = S1LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    return S1LegacyDriver(EarthBody(time_reference=time_model))


@pytest.fixture(name="tref", scope="module")
def given_time_correlation_model(driver):
    """
    Create a TimeReference with IERS bulletin for 2022-11-11
    """

    return driver.time_reference


@pytest.fixture(name="ew1_azimuth", scope="module")
def given_ew1_azimuth_times(tref):
    """
    Generate input azimuth times for product S1A_EW_RAW__0SDH_20221111T114657_20221111T114758
    """

    # from annotations, this is the azimuth time at mid slant range (of EW3) for each burst
    first_line_utc = [
        "2022-11-11T11:47:01.513329",
        "2022-11-11T11:47:04.552211",
        "2022-11-11T11:47:07.591093",
        "2022-11-11T11:47:10.629975",
        "2022-11-11T11:47:13.665937",
        "2022-11-11T11:47:16.704819",
        "2022-11-11T11:47:19.746620",
        "2022-11-11T11:47:22.779664",
        "2022-11-11T11:47:25.815627",
        "2022-11-11T11:47:28.857428",
        "2022-11-11T11:47:31.893391",
        "2022-11-11T11:47:34.935192",
        "2022-11-11T11:47:37.974074",
        "2022-11-11T11:47:41.010037",
        "2022-11-11T11:47:44.051838",
        "2022-11-11T11:47:47.087800",
        "2022-11-11T11:47:50.123763",
        "2022-11-11T11:47:53.162645",
    ]

    range_sampling_rate = 2.502314816000000e07
    range_sampling_time = 1 / range_sampling_rate
    ew3_slant_range_time = 5.556849666167215e-03
    ew3_samples = 8457

    azimuth_zd_times = np.array(
        [tref.from_str(item, unit="s", epoch="2022-11-11T11:47:00") for item in first_line_utc],
        dtype="float64",
    )
    azimuth_tx_times = azimuth_zd_times - 0.5 * (ew3_slant_range_time + ew3_samples * 0.5 * range_sampling_time)

    return {"offsets": azimuth_tx_times, "ref": "UTC", "unit": "s", "epoch": "2022-11-11T11:47:00"}


@pytest.fixture(name="ew2_azimuth", scope="module")
def given_ew2_azimuth_times(tref):
    """
    Generate input azimuth times for product S1A_EW_RAW__0SDH_20221111T114657_20221111T114758
    """

    # from annotations, this is the azimuth time at mid slant range (of EW3) for each burst
    first_line_utc = [
        "2022-11-11T11:47:02.140955",
        "2022-11-11T11:47:05.176918",
        "2022-11-11T11:47:08.215800",
        "2022-11-11T11:47:11.254682",
        "2022-11-11T11:47:14.290644",
        "2022-11-11T11:47:17.332446",
        "2022-11-11T11:47:20.368408",
        "2022-11-11T11:47:23.407290",
        "2022-11-11T11:47:26.443253",
        "2022-11-11T11:47:29.482135",
        "2022-11-11T11:47:32.521017",
        "2022-11-11T11:47:35.559899",
        "2022-11-11T11:47:38.598781",
        "2022-11-11T11:47:41.637663",
        "2022-11-11T11:47:44.673625",
        "2022-11-11T11:47:47.712507",
        "2022-11-11T11:47:50.751389",
        "2022-11-11T11:47:53.790271",
    ]

    range_sampling_rate = 2.502314816000000e07
    range_sampling_time = 1 / range_sampling_rate
    ew3_slant_range_time = 5.556849666167215e-03
    ew3_samples = 8457

    azimuth_zd_times = np.array(
        [tref.from_str(item, unit="s", epoch="2022-11-11T11:47:00") for item in first_line_utc],
        dtype="float64",
    )
    azimuth_tx_times = azimuth_zd_times - 0.5 * (ew3_slant_range_time + ew3_samples * 0.5 * range_sampling_time)

    # use days unit for EW2
    azimuth_tx_times *= 1 / JD_TO_SECONDS

    return {"offsets": azimuth_tx_times, "ref": "UTC", "unit": "d", "epoch": "2022-11-11T11:47:00"}


@pytest.fixture(name="preorb_20221111", scope="module")
def given_preorb_2022_11_11(driver):
    """
    Read orbit file PREORB from 2022-11-11
    """
    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "PREORB",
        "S1A_OPER_AUX_PREORB_OPOD_20221111T102740_V20221111T093852_20221111T161352.EOF",
    )
    return driver.read_orbit_file(orbit_file)


@pytest.fixture(name="resorb_20221111", scope="module")
def given_resorb_2022_11_11(driver):
    """
    Read orbit file RESORB from 2022-11-11
    """
    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "RESORB",
        "S1A_OPER_AUX_RESORB_OPOD_20221111T145817_V20221111T111732_20221111T143502.EOF",
    )
    return driver.read_orbit_file(orbit_file)


@pytest.fixture(name="pvt_20221111", scope="module")
def given_pvt_2022_11_11(driver):
    """
    Read PVT data extracted from sub-commutated data
    """

    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "PVT_ATT_20221111T114656",
        "s1_orbit.xml",
    )
    return driver.read_orbit_file(orbit_file)


@pytest.fixture(name="att_20221111", scope="module")
def given_att_2022_11_11(driver):
    """
    Read attitude data extracted from sub-commutated data
    """

    attitude_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "PVT_ATT_20221111T114656",
        "s1_attitude_eocfi.xml",
    )
    return driver.read_attitude_file(attitude_file)


@pytest.fixture(name="comparator", scope="module")
def given_geodetic_comparator(driver):
    """
    Instanciate a GeodeticComparator
    """

    return GeodeticComparator(driver.earth_body)


@pytest.fixture(name="sar_product", scope="module")
def given_a_sar_product(ew1_azimuth, ew2_azimuth, att_20221111, resorb_20221111):
    """
    Fixture to initialize a S1SARGeometry
    """
    iers_data = S1LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))

    config = {
        "sat": "SENTINEL_1A",
        "look_side": "RIGHT",
        "swaths": {
            "EW1": {
                "azimuth_times": ew1_azimuth,
                "azimuth_convention": "TX",
                "azimuth_time_interval": 2.919194958309765e-03,
                "burst_lines": 1168,
                "slant_range_time": 4.969473533235427e-03,
                "range_sampling_rate": 2.502314816000000e07,
                "burst_samples": 8337,
            },
            "EW2": {
                "azimuth_times": ew2_azimuth,
                "azimuth_convention": "TX",
                "azimuth_time_interval": 2.919194958309765e-03,
                "burst_lines": 1163,
                "slant_range_time": 5.293253736597336e-03,
                "range_sampling_rate": 2.502314816000000e07,
                "burst_samples": 6824,
            },
        },
        "oper_mode": "EW",
        # Using RESORB instead of PREORB+PVT as they give a poor accuracy
        # ~ "orbits": [preorb_20221111, pvt_20221111],
        "orbits": [resorb_20221111],
        "attitude": att_20221111,
        "resources": {
            "dem_path": GETAS_PATH,
            "dem_type": "ZARR",
        },
        "eop": {"iers_bulletin_b": iers_data},
    }

    return S1SARGeometry(**config)


@pytest.fixture(name="ew1_ref_gnd", scope="module")
def given_ew1_ref_points():
    """
    EW1 ground points
    """
    return np.array(
        [
            [-6.762578195754736e01, 7.176164392050084e01, 8.109956979751587e-04],
            [-6.782411568924066e01, 7.178595395115323e01, 7.661003619432449e-04],
            [-6.801734076501413e01, 7.180938212297656e01, 7.254164665937424e-04],
            [-6.784216246590383e01, 7.158965518166175e01, 8.110590279102325e-04],
            [-6.803887692841759e01, 7.161376929430187e01, 7.662279531359673e-04],
            [-6.823051944476376e01, 7.163700916532649e01, 7.255943492054939e-04],
        ],
        dtype="float64",
    )


@pytest.fixture(name="ew1_ref_azi", scope="module")
def given_ew1_ref_azimuth(tref):
    """
    EW1 azimuth times for a few GCP
    """
    ref_azimuth_times_str = [
        "2022-11-11T11:47:01.512951",
        "2022-11-11T11:47:01.512959",
        "2022-11-11T11:47:01.512967",
        "2022-11-11T11:47:04.551833",
        "2022-11-11T11:47:04.551841",
        "2022-11-11T11:47:04.551849",
    ]

    # use the same unit/epoch as EW1 azimuth times in S1SARGeometry
    ref_azimuth_times = np.array(
        [tref.from_str(item, unit="s", epoch="2022-11-11T11:47:00") for item in ref_azimuth_times_str],
        dtype="float64",
    )
    return ref_azimuth_times


@pytest.mark.dem
def test_sar_product_init(sar_product):
    """
    Unit test to initialize a S1SARGeometry
    """

    assert isinstance(sar_product, S1SARGeometry)


@pytest.mark.dem
def test_sar_product_direct_loc_ew1(comparator, sar_product, ew1_ref_gnd, ew1_ref_azi):
    """
    Unit test to compute "slant range" direct location on S1SARGeometry
    """

    # Test on EW1
    img_coords = np.array(
        [
            [0, 0],
            [417, 0],
            [834, 0],
            [0, 1168],
            [417, 1168],
            [834, 1168],
        ],
        dtype="int64",
    )
    gnd, times = sar_product.direct_loc(img_coords, geometric_unit="EW1", altitude=0.0)

    assert gnd.shape == (6, 3)

    plani_delta = comparator.planar_error(gnd, ew1_ref_gnd)
    assert np.all(plani_delta < 1.0)
    alti_delta = np.abs(comparator.height_error(gnd, ew1_ref_gnd))
    assert np.all(alti_delta < 0.001)

    # Compare with zero-doppler azimuth times (in seconds) from geolocation grid
    assert np.allclose(times, ew1_ref_azi, rtol=0, atol=1e-6)  # threshold : 1e-6 second


@pytest.fixture(name="img_coord", scope="module")
def img_coord_product():
    """
    Image coordinates for OLCI
    """
    img_coords = np.zeros((100, 740, 2), dtype="int32")
    for row in range(100):
        for col in range(740):
            img_coords[row, col, 0] = col
            img_coords[row, col, 1] = row

    return img_coords


@pytest.mark.slow
@pytest.mark.dem
@pytest.mark.perfo
def test_sar_product_perf(sar_product, img_coord):
    """
    Unit test for S1SARGeometry.direct_loc, with 740000 points
    """

    # ~ from cProfile import Profile
    # ~ from pyprof2calltree import convert, visualize
    # ~ profiler = Profile()
    # ~ profiler.runctx('sar_product.direct_loc(img_coord, geometric_unit="EW1", altitude=0.0)', locals(), globals())
    # ~ visualize(profiler.getstats())
    # ~ convert(profiler.getstats(), osp.join(TEST_DIR, "outputs", "test_sar_product_perf.kgrind"))

    # call direct_loc
    tic = time.perf_counter()
    sar_product.direct_loc(img_coord, geometric_unit="EW1", altitude=0.0)
    tac = time.perf_counter()
    print(f"SAR direct_loc at constant height speed: {img_coord.size * 0.5 / (tac-tic):.1f}")


@pytest.mark.dem
def test_sar_product_direct_loc_ew2(comparator, sar_product):
    """
    Unit test to compute "slant range" direct location on S1SARGeometry with EW2 swath
    """

    # Test on EW2
    img_coords = np.array(
        [
            [0, 0],
            [342, 0],
            [684, 0],
            [0, 1163],
            [342, 1163],
            [684, 1163],
        ],
        dtype="int64",
    )
    gnd, _ = sar_product.direct_loc(img_coords, geometric_unit="EW2", altitude=0.0)

    # From EW2 SLC geolocation grids
    ref_gnd = np.array(
        [
            [-7.090851413345283e01, 7.209056486571241e01, 3.478694707155228e-04],
            [-7.102658085831695e01, 7.210258442505206e01, 3.380356356501579e-04],
            [-7.114365807497863e01, 7.211441759111342e01, 3.285873681306839e-04],
            [-7.109681888640921e01, 7.191581992766110e01, 3.483509644865990e-04],
            [-7.121386407388923e01, 7.192774625498713e01, 3.385227173566818e-04],
            [-7.132992592757041e01, 7.193948782856501e01, 3.290809690952301e-04],
        ],
        dtype="float64",
    )

    plani_delta = comparator.planar_error(gnd, ref_gnd)
    assert np.all(plani_delta < 1.0)
    alti_delta = np.abs(comparator.height_error(gnd, ref_gnd))
    assert np.all(alti_delta < 0.001)


@pytest.mark.dem
def test_sar_slant_range_localisation(tref, driver, comparator, sar_product, ew1_ref_gnd):
    """
    Unit test to compute "slant range" intersection on S1SARLegacyGeometry
    """
    azimuth_times_str = [
        "2022-11-11T11:47:01.512951",
        "2022-11-11T11:47:01.512959",
        "2022-11-11T11:47:01.512967",
        "2022-11-11T11:47:04.551833",
        "2022-11-11T11:47:04.551841",
        "2022-11-11T11:47:04.551849",
    ]

    azimuth_times = {
        "offsets": np.array(
            [tref.from_str(item, unit="s", epoch="2022-11-11T11:47:00") for item in azimuth_times_str], dtype="float64"
        ),
        "ref": "UTC",
        "unit": "s",
        "epoch": "2022-11-11T11:47:00",
    }

    range_times = np.array(
        [
            4.969473533235427e-03,
            4.986138103070272e-03,
            5.002802672905118e-03,
            4.969473533235427e-03,
            4.986138103070272e-03,
            5.002802672905118e-03,
        ],
        dtype="float64",
    )
    range_distance = range_times * (SPEED_LIGHT * 0.5)

    altitudes = np.array(
        [
            8.109956979751587e-04,
            7.661003619432449e-04,
            7.254164665937424e-04,
            8.110590279102325e-04,
            7.662279531359673e-04,
            7.255943492054939e-04,
        ],
        dtype="float64",
    )

    gnd, gnd_velocity = sar_product.slant_range_localisation(
        azimuth_times,
        range_distance,
        altitudes,
        compute_velocity=True,
    )

    dataset = {"position": gnd}
    driver.earth_body.cartesian_to_geodetic(dataset)

    # Reference points from SLC geolocation grid
    plani_delta = comparator.planar_error(dataset["position"], ew1_ref_gnd)
    assert np.all(plani_delta < 1.0)
    alti_delta = np.abs(comparator.height_error(dataset["position"], ew1_ref_gnd))
    assert np.all(alti_delta < 0.001)

    # reference data is just an output of current implementation
    ref_velocity = np.array(
        [
            [-42.96412715, -7256.09199423, -2205.67614958],
            [-42.12477175, -7256.05627173, -2205.7997603],
            [-41.3599686, -7256.02374738, -2205.91231063],
            [-50.10033294, -7249.12650534, -2228.43525652],
            [-49.25434408, -7249.09085012, -2228.55994571],
            [-48.48338861, -7249.05838422, -2228.67348976],
        ],
        dtype="float64",
    )

    assert np.allclose(gnd_velocity, ref_velocity, rtol=0, atol=1e-3)


def test_sar_sun_angles(sar_product, ew1_ref_gnd, ew1_ref_azi):
    """
    Unit test for S1SARLegacyGeometry.sun_angles(), not actually used...
    """

    sun_angles = sar_product.sun_angles(ew1_ref_gnd, ew1_ref_azi)

    assert sun_angles.shape == (6, 2)


def test_sar_incidence_angles(sar_product, ew1_ref_gnd, ew1_ref_azi):
    """
    Unit test for S1SARLegacyGeometry.incidence_angles(), not actually used...
    """

    incidence_angles = sar_product.incidence_angles(ew1_ref_gnd, ew1_ref_azi)

    assert incidence_angles.shape == (6, 2)

    ref_incidence_angles = np.array(
        [
            1.927721414695747e01,
            1.988226897720746e01,
            2.046655029413662e01,
            1.928371860708993e01,
            1.988856176818265e01,
            2.047265009930931e01,
        ]
    )

    assert np.allclose(incidence_angles[:, 1], ref_incidence_angles, rtol=0, atol=1e-4)


def test_sar_viewing_angles(sar_product, ew1_ref_gnd, ew1_ref_azi):
    """
    Unit test for S1SARLegacyGeometry.viewing_angles(), not actually used...
    """

    viewing_angles = sar_product.viewing_angles(ew1_ref_gnd, ew1_ref_azi)

    assert viewing_angles.shape == (6, 2)

    ref_viewing_angles = np.array(
        [
            1.728279136234930e01,
            1.782082146278001e01,
            1.833996936304380e01,
            1.728865199947117e01,
            1.782649186285195e01,
            1.834546633250886e01,
        ]
    )

    assert np.allclose(viewing_angles[:, 1], ref_viewing_angles, rtol=0, atol=1e-4)


def test_sar_terrain_height(tref, sar_product):
    """
    Unit test for S1SARLegacyGeometry.terrain_height()
    """

    terrain_azimuth_str = [
        "2022-11-11T11:47:11.513329",
        "2022-11-11T11:47:21.513329",
        "2022-11-11T11:47:31.513329",
        "2022-11-11T11:47:41.513329",
    ]

    terrain_azimuth = [tref.from_str(item, unit="s", epoch="2022-11-11T11:47:00") for item in terrain_azimuth_str]

    terrain_ref_height = np.array(
        [
            0.0,
            2.069604196638655e02,
            5.904932870588235e02,
            7.984219369696970e02,
        ],
        dtype="float64",
    )

    elevations = sar_product.terrain_height(
        terrain_azimuth,
        azimuth_block_size=1,
        azimuth_subsampling=1,
        range_subsampling=100,
        geometric_unit="EW1",
    )

    assert elevations.shape == (4,)

    assert np.allclose(elevations, terrain_ref_height, rtol=0, atol=160)


def test_sar_zero_doppler_to_attitude(sar_product):
    """
    Unit test for S1SARLegacyGeometry.zero_doppler_to_attitude()
    """

    times = sar_product.config["attitude"]["times"]["UTC"]["offsets"][6:16]
    time_array = {"offsets": times, "unit": "d", "ref": "UTC"}

    angles = sar_product.zero_doppler_to_attitude(time_array)

    ref_angles = np.array(
        [
            [-2.97109726e01, -4.00665116e-04, -2.99725584e-04],
            [-2.97111063e01, -4.37516793e-04, -3.36377560e-04],
            [-2.97114187e01, -4.78702840e-04, -3.40137378e-04],
            [-2.97115973e01, -3.68933345e-04, -3.62570927e-04],
            [-2.97118569e01, -3.27343898e-04, -4.38950860e-04],
            [-2.97122094e01, -3.75853261e-04, -4.05073101e-04],
            [-2.97125616e01, -3.07389798e-04, -3.58872510e-04],
            [-2.97129829e01, -2.81198519e-04, -3.66853376e-04],
            [-2.97135699e01, -2.71666264e-04, -3.40642850e-04],
            [-2.97140620e01, -2.61258061e-04, -3.43953827e-04],
        ],
    )

    assert np.allclose(angles, ref_angles, rtol=0, atol=0.001)
