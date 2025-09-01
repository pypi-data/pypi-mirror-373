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
Unit test for SAR propagation model
"""

import os.path as osp

import numpy as np
import pytest
from drivers.sentinel_1_legacy import S1LegacyDriver
from helpers.compare import GeodeticComparator

from asgard.core.math import angular_distance
from asgard.core.transform import RigidTransform
from asgard.models.body import EarthBody
from asgard.models.orbit import GenericOrbitModel
from asgard.models.sar import SPEED_LIGHT, SarPropagationModel
from asgard.models.time import TimeReference

TEST_DIR = osp.dirname(__file__)

# ======================================[ Support classes ]=========================================


@pytest.fixture(name="time_ref", scope="module")
def given_time_reference():
    """
    Create a TimeReference with IERS bulletin
    """
    iers_data = S1LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    return TimeReference(iers_bulletin_b=iers_data)


@pytest.fixture(name="earth_body", scope="module")
def given_earth_body(time_ref):
    """
    Fixture to initialize an EarthBody with WGS84 ellipsoid and a TimeReference based on pyrugged data
    """
    return EarthBody(ellipsoid="WGS84", time_reference=time_ref)


@pytest.fixture(name="driver", scope="module")
def given_legacy_driver(earth_body):
    """
    Create a S1LegacyDriver with IERS bulletin for 2022-11-11
    """

    return S1LegacyDriver(earth_body)


@pytest.fixture(name="comparator", scope="module")
def given_geodesic_comparator(earth_body):
    """
    Fixture to get a comparator
    """
    return GeodeticComparator(earth_body)


# ======================[ Test case based on data generated from EOCFI ]============================


@pytest.fixture(name="context", scope="module")
def given_context_from_eocfi():
    """
    Fixture to generate a dataset context from EOCFI.

    Warning: in EOCFI, the range intersection plane is defined with an azimuth angle from the
    satellite front-looking direction (90° for right side looking, 270° for left side looking),
    whereas in pyRugged, the intersection plane is normal to the velocity (with zero-doppler). So,
    for this test case, we have computed with EOCFI the front-looking direction in EF coordinates,
    and use it instead of velocity.
    """

    dataset = {}

    dataset["ref_ground"] = np.array(
        [
            [287.2382024, 1.14461759, 240.42183921],
            [286.12407347, 6.23705345, 657.9598779],
            [285.03920717, 11.33291209, -10.99418142],
            [283.96199939, 16.42788791, -15.97993476],
            [282.88547574, 21.52118065, -16.22495678],
            [281.79781573, 26.61123378, -30.98815772],
            [280.68501557, 31.69655107, -35.98649494],
            [279.52335138, 36.77468095, 832.94790875],
            [278.30893154, 41.84725376, 137.00725246],
            [276.99104458, 46.90968738, 385.33368589],
        ],
        dtype="float64",
    )

    dataset["times"] = {
        "offsets": np.array(
            [
                8338.13090278,
                8338.13190278,
                8338.13290278,
                8338.13390278,
                8338.13490278,
                8338.13590278,
                8338.13690278,
                8338.13790278,
                8338.13890278,
                8338.13990278,
            ],
            dtype="float64",
        ),
        "ref": "GPS",
    }

    # orbital pos / satellite "front" direction in EF
    dataset["orb_pos"] = np.array(
        [
            [1614569.2867854312, -7000064.101786228, 17878.486784294175],
            [1469641.9397702797, -7000741.378940781, 653401.5764441283],
            [1313323.2396637893, -6943561.393878607, 1283661.8405110084],
            [1147587.7084904332, -6828840.289586152, 1903581.5488508595],
            [974479.3601041144, -6657384.159633201, 2508165.8307405394],
            [796088.9058863737, -6430482.97705677, 3092544.024272697],
            [614530.579275772, -6149900.037335066, 3652009.8192051426],
            [431919.0067088408, -5817857.178751689, 4182059.725347913],
            [250346.33630921924, -5437016.000135426, 4678429.728268347],
            [71859.84843984844, -5010455.132868715, 5137129.777307236],
        ],
        dtype="float64",
    )

    dataset["orb_vel"] = np.array(
        [
            [-0.21653763985898056, -0.050974842606028185, 0.9749425705884388],
            [-0.23564400102631963, 0.0381741972352337, 0.9710894065150507],
            [-0.25178573510382596, 0.1272351451520511, 0.9593826981118445],
            [-0.26483656042133424, 0.21544465488849301, 0.9399176543422169],
            [-0.2747051095382205, 0.30204603431629984, 0.9128555723373718],
            [-0.28133586965957535, 0.38629663378185025, 0.8784219027162868],
            [-0.284709456047492, 0.46747497810515776, 0.836903620784809],
            [-0.2848423608540202, 0.5448874752244898, 0.7886459717811213],
            [-0.2817862780754821, 0.6178746134595073, 0.7340486738157298],
            [-0.27562706988172647, 0.6858165799062055, 0.6735616802299318],
        ],
        dtype="float64",
    )

    dataset["slant_range"] = np.array(
        [
            956344.33484039,
            955129.18945612,
            955586.22272535,
            955572.46794766,
            955871.1011742,
            956475.51421445,
            957317.30093936,
            957297.06565811,
            959335.59279817,
            960319.33634603,
        ],
        dtype="float64",
    )

    dataset["range_times"] = dataset["slant_range"] * 2 / SPEED_LIGHT

    dataset["is_right"] = True

    dataset["los_pos"] = dataset["orb_pos"]
    dataset["los_vec"] = dataset["orb_vel"]

    return dataset


@pytest.fixture(name="propag", scope="module")
def given_sar_propagation_model(earth_body, context):
    """
    Fixture to instanciate a SarPropagationModel
    """

    config = {
        "earth_body": earth_body,
        "terrain_height_lut": {
            "azimuth": context["times"],  # same azimuth times
            "height": context["ref_ground"][:, 2],  # expected height
        },
        "frame": "EF",
    }

    return SarPropagationModel(**config)


def test_sar_propagation_model(propag, context, comparator):
    """
    Unit test for propagation model
    """

    dataset = context.copy()

    propag.sensor_to_target(dataset)

    assert "gnd_coords" in dataset

    plani_error = comparator.planar_error(dataset["gnd_coords"], dataset["ref_ground"])
    assert np.all(plani_error < 1e-2)  # 1cm


# ===================[ Test case with real SLC product ]============================================


@pytest.fixture(name="propag_ef", scope="module")
def given_sar_propagation_model_ef(earth_body, context):
    """
    Fixture to instanciate a SarPropagationModel
    """

    config = {
        "earth_body": earth_body,
        "terrain_height_lut": {
            "azimuth": context["times"],  # same azimuth times
            "height": context["ref_ground"][:, 2],  # expected height
        },
        "frame": "EF",
    }

    return SarPropagationModel(**config)


@pytest.fixture(name="pvt_20221111", scope="module")
def given_pvt_2022_11_11(driver):
    """
    Read PVT data extracted from sub-commutated data, in EF
    """

    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "PVT_ATT_20221111T114656",
        "s1_orbit.xml",
    )
    orbit = driver.read_orbit_file(orbit_file)

    return orbit


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


@pytest.fixture(name="context_ew1", scope="module")
def given_context_from_ew1_slc(time_ref, earth_body, pvt_20221111, preorb_20221111):
    """
    Context from S1A_EW_SLC__1SDH_20221111T114659_20221111T114758_045846_057C1E_CCDA.SAFE
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
        [time_ref.from_str(item, unit="s", epoch="2022-11-11T11:47:00") for item in first_line_utc],
        dtype="float64",
    )
    azimuth_tx_times = azimuth_zd_times - 0.5 * (ew3_slant_range_time + ew3_samples * 0.5 * range_sampling_time)

    dataset = {}

    dataset["range_times"] = np.array(
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

    # parse azimuth times from GCP
    utc_times_str = [
        "2022-11-11T11:47:01.512951",
        "2022-11-11T11:47:01.512959",
        "2022-11-11T11:47:01.512967",
        "2022-11-11T11:47:04.551833",
        "2022-11-11T11:47:04.551841",
        "2022-11-11T11:47:04.551849",
    ]
    azimuth_times = np.array(
        [time_ref.from_str(item, unit="s", epoch="2022-11-11T11:47:00") for item in utc_times_str],
        dtype="float64",
    )

    # build zd azimuth times from burst TX times
    azimuth_times_2 = np.array(
        [
            azimuth_tx_times[0] + 0.5 * dataset["range_times"][0],
            azimuth_tx_times[0] + 0.5 * dataset["range_times"][1],
            azimuth_tx_times[0] + 0.5 * dataset["range_times"][2],
            azimuth_tx_times[1] + 0.5 * dataset["range_times"][3],
            azimuth_tx_times[1] + 0.5 * dataset["range_times"][4],
            azimuth_tx_times[1] + 0.5 * dataset["range_times"][5],
        ],
        dtype="float64",
    )

    # Save azimuth times
    dataset["derived_azimuth_times"] = azimuth_times_2
    dataset["gcp_azimuth_times"] = azimuth_times

    dataset["times"] = {"offsets": azimuth_times_2, "ref": "UTC", "unit": "s", "epoch": "2022-11-11T11:47:00"}

    # EW1 first & second line GCPs
    dataset["ref_ground"] = np.array(
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

    fused_orbit = GenericOrbitModel.merge_orbits([preorb_20221111, pvt_20221111])

    config = {
        "orbit": fused_orbit,
        "attitude": {"aocs_mode": "ZD", "frame": "EF"},
        "earth_body": earth_body,
    }
    orb_model = GenericOrbitModel(**config)
    orb_model.get_osv(dataset)
    orb_model.compute_quaternions(dataset)

    zd_vel = np.array([0.0, -1.0, 0.0], dtype="float64")
    sat_to_earth = RigidTransform(
        rotation=dataset["attitudes"],
    )

    original_zd_vel = sat_to_earth.transform_direction(zd_vel)

    dataset["los_vec"] = original_zd_vel

    dataset["is_right"] = True

    dataset["los_pos"] = dataset["orb_pos"]

    return dataset


def test_check_ew1_context(context_ew1):
    """
    Test case to check numerical values from EW1 context with baselines coming from EOCFI
    """

    azimuth_delta = context_ew1["gcp_azimuth_times"] - context_ew1["times"]["offsets"]
    assert np.all(np.abs(azimuth_delta) < 1e-6)

    eocfi_orb_pos = np.array(
        [
            [1090580.647796136, -2047724.0810932398, 6674565.624384388],
            [1090580.6476525697, -2047724.1392270925, 6674565.606610014],
            [1090580.6475090045, -2047724.1973609463, 6674565.588835642],
            [1090515.7290002243, -2069753.565276403, 6667792.138290744],
            [1090515.7288017643, -2069753.6233402325, 6667792.120337515],
            [1090515.7286033037, -2069753.6814040616, 6667792.102384285],
        ],
        dtype="float64",
    )

    eocfi_front_dir = np.array(
        [
            [-0.0023596984502844975, -0.9562968594709167, -0.2923880099957683],
            [-0.002359700858175995, -0.9562968570340964, -0.2923880179463055],
            [-0.0023597032660674366, -0.9562968545972759, -0.29238802589684265],
            [-0.003272361317022243, -0.9553678277331191, -0.29540075386483394],
            [-0.003272363722927496, -0.9553678252696062, -0.2954007618055312],
            [-0.00327236612883286, -0.9553678228060931, -0.2954007697462285],
        ],
        dtype="float64",
    )

    pos_delta = context_ew1["los_pos"] - eocfi_orb_pos
    assert np.all(np.linalg.norm(pos_delta, axis=1) < 1.0)  # 1m

    direction_delta = angular_distance(context_ew1["los_vec"], eocfi_front_dir)
    assert np.all(direction_delta < 1e-3)  # 1e-3 degrees, to be improved...


def test_sar_propagation_model_ew1(propag_ef, context_ew1, comparator):
    """
    Test case with data from EW1 GCPs
    """

    dataset = context_ew1.copy()

    propag_ef.sensor_to_target(dataset, altitude=7.0e-4)

    plani_error = comparator.planar_error(dataset["gnd_coords"], dataset["ref_ground"])
    # ~ print("plani error:")
    # ~ print(plani_error)
    assert np.all(plani_error < 8.0)  # 8m is a bit large, but due to errors on front_direction

    # use position and front_direction from EOCFI
    dataset["los_pos"] = np.array(
        [
            [1090580.647796136, -2047724.0810932398, 6674565.624384388],
            [1090580.6476525697, -2047724.1392270925, 6674565.606610014],
            [1090580.6475090045, -2047724.1973609463, 6674565.588835642],
            [1090515.7290002243, -2069753.565276403, 6667792.138290744],
            [1090515.7288017643, -2069753.6233402325, 6667792.120337515],
            [1090515.7286033037, -2069753.6814040616, 6667792.102384285],
        ],
        dtype="float64",
    )
    dataset["los_vec"] = np.array(
        [
            [-0.0023596984502844975, -0.9562968594709167, -0.2923880099957683],
            [-0.002359700858175995, -0.9562968570340964, -0.2923880179463055],
            [-0.0023597032660674366, -0.9562968545972759, -0.29238802589684265],
            [-0.003272361317022243, -0.9553678277331191, -0.29540075386483394],
            [-0.003272363722927496, -0.9553678252696062, -0.2954007618055312],
            [-0.00327236612883286, -0.9553678228060931, -0.2954007697462285],
        ],
        dtype="float64",
    )
    propag_ef.sensor_to_target(dataset, altitude=7.0e-4)
    plani_error = comparator.planar_error(dataset["gnd_coords"], dataset["ref_ground"])
    assert np.all(plani_error < 1.5)  # error should be much smaller with EOCFI position and "front_direction"
