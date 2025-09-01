#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2025 CS GROUP
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
"""
Unit tests for orbit propagation
"""

import os
import os.path as osp
import xml.etree.ElementTree as ET

import numpy as np
import pytest
from drivers.explorer_legacy import ExplorerDriver
from org.orekit.time import AbsoluteDate, TimeScalesFactory

from asgard.models.body import EarthBody
from asgard.models.orbit import OrbitScenarioModel
from asgard.models.time import DEFAULT_EPOCH, DEFAULT_UNIT, TimeRef, TimeReference

TEST_DIR = osp.dirname(__file__)
SLSTR_DIR = osp.join(TEST_DIR, "resources/S3/SLSTR")
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data")
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")
S3L0Geometry_DIR = osp.join(TEST_DIR, "resources/S3/S3L0Geometry/")


def get_orbit_info_l0(path: str) -> tuple:
    """
    Return orbit infos from lo xfdumanifest.xml file

    :param: path: path to xfdumanifest.xml file
    :return: start_time
    """
    tree = ET.parse(path)
    root = tree.getroot()
    namespace = {"sentinel-safe": "http://www.esa.int/safe/sentinel/1.1"}

    # Time Ref = UTC
    start_time = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/sentinel-safe:acquisitionPeriod/sentinel-safe:startTime",
        namespace,
    ).text
    orbit_number = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/sentinel-safe:orbitReference/sentinel-safe:orbitNumber",
        namespace,
    ).text
    rel_orbit_number = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/"
        "sentinel-safe:orbitReference/sentinel-safe:relativeOrbitNumber",
        namespace,
    ).text
    cycle_number = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/sentinel-safe:orbitReference/sentinel-safe:cycleNumber",
        namespace,
    ).text
    phase_id = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/"
        "sentinel-safe:orbitReference/sentinel-safe:phaseIdentifier",
        namespace,
    ).text

    return start_time, int(orbit_number), int(rel_orbit_number), int(cycle_number), int(phase_id)


@pytest.fixture(name="manifest", scope="module")
def given_manifest():
    return osp.join(S3L0Geometry_DIR, "xfdumanifest.xml")


@pytest.fixture(name="orbit_scenario", scope="module")
def orbit_scenario():
    """
    orbit_scenario from OSF
    """
    return ExplorerDriver.read_orbit_scenario_file(
        osp.join(
            TEST_DIR,
            "resources",
            "S3",
            "OSF",
            "S3A_OPER_MPL_ORBSCT_20160216T192404_99999999T999999_0006.EOF",  # up to 2021
            # "S3A_OPER_MPL_ORBSCT_20160216T192404_99999999T999999_0007.EOF", # up to 2023
        )
    )


@pytest.fixture(name="orbit_scenario_2020", scope="module")
def orbit_scenario_2020():
    """
    orbit_scenario from OSF
    """
    return ExplorerDriver.read_orbit_scenario_file(
        osp.join(
            TEST_DIR,
            "resources",
            "S3",
            "OSF",
            "osf_2020.xml",  # up to 2020
        )
    )


@pytest.fixture(name="orbit_model_osf", scope="module")
def orbit_model_osf(orbit_scenario):
    """
    Fixture create a OrbitScenarioModel instance
    """

    body_model = EarthBody(ellipsoid="WGS84")
    orbit_config = {
        "orbit_scenario": orbit_scenario,
        "orbit_frame": "EF",
        "attitude": {"aocs_mode": "YSM"},
        "earth_body": body_model,
    }

    return OrbitScenarioModel(**orbit_config)


@pytest.fixture(name="orbit_model_osf_2020", scope="module")
def orbit_model_osf_2020(orbit_scenario_2020):
    """
    Fixture create a OrbitScenarioModel instance
    """

    body_model = EarthBody(ellipsoid="WGS84")
    orbit_config = {
        "orbit_scenario": orbit_scenario_2020,
        "orbit_frame": "EME2000",
        "attitude": {"aocs_mode": "YSM"},
        "earth_body": body_model,
    }

    return OrbitScenarioModel(**orbit_config)


def test_get_osv(orbit_model_osf):
    """
    test get_osv method
    """
    # reset propagator to avoid cached data and propagator from other tests
    orbit_model_osf.reset_propagator()

    # np.set_printoptions(precision=17, suppress=False)
    tr = TimeReference()

    targetDate = AbsoluteDate(
        "2021-04-22T21:58:29.000000", TimeScalesFactory.getTAI()
    )  # .shiftedBy(37.)#last OSF date 2021 TAI +8sec + 1month
    targetDate_offset = tr.from_str(targetDate.toString(), fmt="CCSDSA_MICROSEC")  # TAI,

    targetDate2 = AbsoluteDate(
        "2021-05-22T21:58:29.000000", TimeScalesFactory.getTAI()
    )  # .shiftedBy(37.)#last OSF date 2021 TAI +8sec  +  2 1month
    targetDate_offset2 = tr.from_str(targetDate2.toString(), fmt="CCSDSA_MICROSEC")  # TAI

    targetDate6 = AbsoluteDate(
        "2021-09-22T21:58:29.000000", TimeScalesFactory.getTAI()
    )  # .shiftedBy(37.)#last OSF date 2021 TAI +8sec  +  6month
    targetDate_offset6 = tr.from_str(targetDate6.toString(), fmt="CCSDSA_MICROSEC")

    dataset = {
        "times": {
            "offsets": np.array([targetDate_offset, targetDate_offset2, targetDate_offset6]),  # in days
            "ref": "TAI",
        },
    }

    _ = orbit_model_osf.get_osv(dataset=dataset, field_time="times", fields_out=("positions", "velocities"))

    pod_pos = np.array(
        [
            [6981915.052648, -180561.445951, 1671950.824808],
            [2870929.794331, 1019252.379631, -6511249.340461],
            [-2006751.119184, 1016443.442170, -6827587.113592],
        ]
    )

    pod_vel = np.array(
        [
            [-1766.022603, -1613.400592, 7158.564297],
            [6892.254858, -583.772775, 2948.510726],
            [7214.706235, 530.528863, -2042.454164],
        ]
    )

    # print("\n --- Abs Diff ASGARD vs POEORB_POD ---")
    # print("Position (m):", np.linalg.norm(np.abs(pod_pos - dataset["positions"]), axis=1))
    # print("Speed (m/s):", np.linalg.norm(np.abs(pod_vel - dataset["velocities"]), axis=1))

    np.testing.assert_allclose(dataset["positions"], pod_pos, atol=55000)
    np.testing.assert_allclose(dataset["velocities"], pod_vel, atol=100)

    # instant_in = 2021-04-22T21:58:21.2567999","2021-05-22T21:58:21.256799","2021-09-22T21:58:21.256799"
    # last OSF date 2021 TAI + 1month,2month, 6month
    eocfi_pos = np.array(
        [
            [6976573.810361229814589024, -184956.362181531847454607, 1693638.685423577437177300],
            [2898312.704885698389261961, 1016795.956950466148555279, -6499529.361153431236743927],
            [-1996485.102555722929537296, 1016452.434453541645780206, -6830853.392277104780077934],
        ]
    )
    eocfi_vel = np.array(
        [
            [-1789.237151851996259211, -1611.756575552776212135, 7153.085414909278370033],
            [6879.568928038185731566, -592.253094829814131117, 2976.405396761837891972],
            [7217.639567832839020411, 527.588243023414406707, -2031.771012452098830181],
        ]
    )

    # print("\n --- Abs Diff ASGARD vs EOCFI  ---")
    # print("Position (m):", np.linalg.norm(np.abs(eocfi_pos - dataset["positions"]), axis=1))
    # print("Speed (m/s):", np.linalg.norm(np.abs(eocfi_vel - dataset["velocities"]), axis=1))
    np.testing.assert_allclose(dataset["positions"], eocfi_pos, atol=55000)
    np.testing.assert_allclose(dataset["velocities"], eocfi_vel, atol=100)


def test_valid_range(orbit_model_osf):
    """
    Test osf valid range
    """
    start, end = orbit_model_osf.valid_range

    tr = TimeReference()
    start = tr.to_str(start, fmt="CCSDSA_MICROSEC", ref_in=TimeRef.UTC, ref_out=TimeRef.UTC)
    end = tr.to_str(end, fmt="CCSDSA_MICROSEC", ref_in=TimeRef.UTC, ref_out=TimeRef.UTC)

    start_ref = "2016-02-16T19:24:03.000000"
    end_ref = "9000-01-01T01:01:01.000030"
    assert start == start_ref
    assert end == end_ref


def test_orbit_info_osf(orbit_model_osf_2020):
    """
    Test get_info method
    """

    target_date = AbsoluteDate("2021-03-22T21:58:21.256799", TimeScalesFactory.getTAI())  # last OSF date
    info = orbit_model_osf_2020.get_info(target_date)
    # prev_abs_orbit_ref = 21534  # number from the previous ANX
    abs_orbit_ref = 26539
    anx_lon_ref = 0.625065
    assert info["abs_orbit"] == pytest.approx(abs_orbit_ref, abs=0)
    assert info["anx_long"] == pytest.approx(anx_lon_ref, abs=2)
    assert info["anx_long"] == pytest.approx(0.32187665033680557, abs=1e-4)


def test_orbit_info_osf_compare_eocfi(orbit_model_osf):
    """
    Test comparison wtith eocfi
    """
    time = 8338.064236111111
    # reset propagator to avoid cached data and propagator from other tests
    orbit_model_osf.reset_propagator()
    times = {"offsets": time, "unit": DEFAULT_UNIT, "epoch": DEFAULT_EPOCH}
    target_date = list(TimeReference().to_dates(times, TimeRef.GPS))[0]

    info = orbit_model_osf.get_info(target_date)
    ref_anx = {
        "abs_orbit": 34897,
        "track_direction": "ascending",
        "repeat_cycle": 27.0,
        "cycle_length": 385.0,
        "mlst_drift": 0.0,
        "mlst": 22.003611111111113,
        "anx_long": 308.2614286362928,
        "utc_anx": 8338.060550110255,
        "pos_anx": [4448522.281468641, -5640609.073372022, 0.0],
        "vel_anx": [-1293.612720358994, -1009.3475760481004, 7366.402739366811],
        "mean_kepl": {
            "a": 7177942.028368431,
            "e": 0.001146,
            "i": 98.62724339755852,
            "ra": 8.414173539399298,
            "w": 90.0,
            "m": 270.1311829188864,
        },
        "osc_kepl": {
            "a": 7186938.553345348,
            "e": 0.0012303058507958577,
            "i": 98.62179565904049,
            "ra": 8.414131469092519,
            "w": 68.71376570553555,
            "m": 291.4175548877906,
        },
        "nodal_period": 6059.220779220779,
        "period_jd": 0.07012987012987013,
        "utc_smx": 0.0,
        "gps_anx": 8338.06075844359,
    }

    # all keys are present
    assert info["abs_orbit"] == ref_anx["abs_orbit"]
    assert info["anx_long"] == pytest.approx(ref_anx["anx_long"], 1.5)
    assert info["utc_anx"] == pytest.approx(ref_anx["utc_anx"], 5e-4)
    assert info["track_direction"] == ref_anx["track_direction"]


def test_valid_l0_orbit_info(manifest, orbit_model_osf):
    """
    Test to validate orbit info from l0
    """

    # ref data from L0
    date_str, orbit_number, rel_orbit_number, cycle_number, phase_id = get_orbit_info_l0(manifest)
    target_date = AbsoluteDate(date_str, TimeScalesFactory.getUTC())
    # reset propagator
    orbit_model_osf.reset_propagator()
    l0_info = orbit_model_osf.get_info(target_date, light=True)
    assert l0_info["phase_id"] == phase_id
    assert l0_info["cycle_number"] == cycle_number
    assert l0_info["abs_orbit"] == orbit_number
    assert l0_info["rel_orbit"] == rel_orbit_number
