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
Unit tests for orbit model
"""


import logging
import os
import os.path as osp
import re
import warnings
from pprint import pformat

import numpy as np
import pytest
from drivers.s2geo_legacy.s2geo_interface import S2geoInterface
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import sub
from scipy.spatial.transform import Rotation as R

from asgard.core.frame import FrameId
from asgard.core.logger import format_as_tree
from asgard.core.time import TimeRef
from asgard.models.body import EarthBody
from asgard.models.orbit import GenericOrbitModel  # New ways
from asgard.models.time import TimeReference

# isort: off
# Orekit wrappers needs to be imported before any org.orekit module
import asgard.wrappers.orekit  # pylint: disable=unused-import  # noqa : F401;

from org.orekit.time import (  # pylint: disable=import-error, wrong-import-order
    AbsoluteDate,
)

# isort: on


# For testing purpose, inject operator- in AbsoluteDate
def _abs_date_sub(lhs: AbsoluteDate, rhs: AbsoluteDate) -> float:
    if isinstance(rhs, AbsoluteDate):
        return lhs.durationFrom(rhs)
    return lhs.shiftedBy(-float(rhs))


AbsoluteDate.__sub__ = _abs_date_sub


def expect_fail(exception, match):
    """
    Helper context manager factory for excpecting exceptions.
    Actually just a trick for having pylint ignore multiple instructions in ``pytest.raises``
    """
    # In order to trick pylint...
    return pytest.raises(exception, match=match)


# Resources directory
TEST_DIR = osp.dirname(__file__)

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

ZD_DIR = osp.join(TEST_DIR, "resources", "S1", "zero_doppler")

# =============================[ FIXTURES & GIVEN ]=================================================


@pytest.fixture(name="osv_dataset", scope="module")
def given_input_osv_dataset() -> dict:
    """
    BDD-like "GIVEN" fixture that generates input arrays for computeOSV
    """
    nb_elem = 1000000

    epoch = "2022-09-18T02:51:34.000"
    start_date = 37.0
    stop_date = 111.0

    rng = np.random.default_rng()
    input_array = rng.random(size=nb_elem) * (stop_date - start_date) + start_date

    return {
        "times": {
            "epoch": epoch,
            "ref": "GPS",
            "offsets": input_array,
            "unit": "s",
        },
    }


def given_input_dataset(time_array) -> dict:
    """
    BDD "GIVEN" function that defines an input time series for orbit OSV tests
    """

    return {"times": time_array.copy()}


def given_input_dataset_and_dates(time_array, tr: TimeReference):
    """
    BDD "GIVEN" function that returns a dataset (new organisation) and AbsoluteDate list

    :param time_array: Time array  (see TIME_ARRAY)
    :param TimeReference tr: :class:`asgard.models.TimeReference` object used for AbsoluteDate generation.
    """
    dataset = given_input_dataset(time_array)

    abs_dates = list(tr.to_dates(time_array))
    return dataset, abs_dates


@pytest.fixture(name="time_model", scope="module")
def given_time_model() -> TimeReference:
    """
    Fixture to instanciate a TimeReference
    """
    # Read orekit-compatible IERS bulletin
    iers_path = osp.join(
        TEST_DIR,
        "resources",
        "orekit",
        "IERS",
        "S2__OPER_AUX_UT1UTC_ADG__20220916T000000_V20220916T000000_20230915T000000.txt",
    )

    iers_data = S3LegacyDriver.read_iers_file(iers_path)

    config = {
        "iers_bulletin_a": iers_data,
    }
    return TimeReference(**config)


@pytest.fixture(name="earth_body", scope="module")
def given_earth_body(time_model: TimeReference) -> EarthBody:
    """
    Fixture to instanciate an EarthBody
    """
    config = {"time_reference": time_model}
    return EarthBody(**config)


@pytest.fixture(name="orbit_model_msi", scope="module")
def given_msi_orbit_model(earth_body: EarthBody) -> GenericOrbitModel:
    """
    BDD-like "WHEN" fixture that returns a global orbit model for all tests.
    """
    data_path = osp.join(ASGARD_DATA, "S2MSIdataset/no_refining/S2GEO_Input_interface.xml")

    # S2geo interface file -> Python dict
    config = S2geoInterface(data_path).read()

    # logging.debug("config S2geoInterface(%s): %s", data_path, format_as_tree(d_orbits))
    model = GenericOrbitModel(
        orbit=config["orbits"],
        attitude=config["attitudes"],
        earth_body=earth_body,
    )
    return model


@pytest.fixture(name="fro_20221030", scope="module")
def given_fro_20221030() -> dict:
    """
    Fixture to extract FRO orbit from 2022-10-30
    """
    orbit_file = osp.join(
        TEST_DIR,
        "resources/S3/FRO",
        "S3A_OPER_MPL_ORBRES_20221030T000000_20221109T000000_0001.EOF",
    )

    orbit_info = S3LegacyDriver.read_orbit_file(orbit_file)
    return orbit_info


@pytest.fixture(name="fpo_20221030", scope="module")
def given_fpo_20221030() -> dict:
    """
    Fixture to extract FPO orbit from 2022-10-30
    """
    orbit_file = osp.join(
        TEST_DIR,
        "resources/S3/FPO",
        "S3A_OPER_MPL_ORBPRE_20221030T000000_20221106T000000_0001.EOF",
    )

    orbit_info = S3LegacyDriver.read_orbit_file(orbit_file)
    return orbit_info


@pytest.fixture(name="navatt_context", scope="module")
def given_navatt_from_20221101():
    """
    Fixture to extract Navatt from 2022-11-01
    Extracts both orbit and navatt in EME2000
    """

    iers_bulletin = osp.join(f"{TEST_DIR}/resources/bulletinb-413.txt")
    iers_data = S3LegacyDriver.read_iers_file(iers_bulletin)
    time_model = TimeReference(iers_bulletin_b=iers_data)
    config = {"time_reference": time_model}
    driver = S3LegacyDriver(EarthBody(**config))

    orbit, attitude, _ = driver.read_navatt_file(
        [osp.join(TEST_DIR, "resources/S3/NAT/20221101/ISPData.dat")],
        abs_orbit=34934,
    )

    # set reference time scale to GPS for both orbit and attitude
    orbit["time_ref"] = "GPS"
    attitude["time_ref"] = "GPS"

    return {"orbit": orbit, "attitude": attitude}


@pytest.fixture(name="ysm_context", scope="module")
def given_ysm(navatt_context) -> dict:
    """
    Fixture to extract Navatt from 2022-11-01, and setup attitude with Yaw-Steering-Mode
    """

    attitude = {"aocs_mode": "YSM"}

    return {"orbit": navatt_context["orbit"], "attitude": attitude}


@pytest.fixture(name="orb_model_olci_fro", scope="module")
def given_olci_orbit_model_with_fro(fro_20221030, time_model, earth_body) -> GenericOrbitModel:
    """
    BDD "GIVEN" function that return OrbitModel with FRO configuration
    """
    fake_attitude = {
        "times": {
            "UTC": {
                "offsets": fro_20221030["times"]["UTC"]["offsets"][0:5],
            },
        },
        "quaternions": np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
            ]
        ),
        "frame": "EF",
        "time_ref": "UTC",
    }

    time_orb_gps = 8338.064236111111  # same offset as the one used with eocfi tests => after ANX
    # time_orb_gps = 8338.060745 # a bit before the ANX found by EOCFI => ANX transition
    time_orb_str = f"GPS={time_model.to_str(time_orb_gps, ref_in=TimeRef.GPS)}"
    logging.debug("time_orb => %s", time_orb_str)

    config = {
        "orbit": fro_20221030,
        "attitude": fake_attitude,
        "time_orb": time_orb_str,
        "earth_body": earth_body,
    }
    return GenericOrbitModel(**config)


@pytest.fixture(name="orb_model_olci_fpo", scope="module")
def given_olci_orbit_model_with_fpo(fpo_20221030, earth_body) -> GenericOrbitModel:
    """
    BDD "GIVEN" function that return OrbitModel with FRO configuration
    """
    fake_attitude = {
        "times": {
            "UTC": {
                "offsets": fpo_20221030["times"]["UTC"]["offsets"][0:5],
            },
        },
        "quaternions": np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
            ]
        ),
        "frame": "EF",
        "time_ref": "UTC",
    }

    time_orb_str = "GPS=2022-10-30T08:47:12.45608"
    logging.debug("time_orb => %s", time_orb_str)

    config = {
        "orbit": fpo_20221030,
        "attitude": fake_attitude,
        "time_orb": time_orb_str,
        "earth_body": earth_body,
    }

    return GenericOrbitModel(**config)


@pytest.fixture(name="orb_model_olci_navatt", scope="module")
def given_olci_orbit_model_with_navatt(navatt_context, earth_body):
    """
    BDD "GIVEN" function that return OrbitModel with Navatt configuration
    """
    return GenericOrbitModel(**navatt_context, earth_body=earth_body)


@pytest.fixture(name="orb_model_olci_ysm", scope="module")
def given_ocli_orbit_model_with_ysm(ysm_context, earth_body):
    """
    BDD "GIVEN" function that return OrbitModel with Navatt orbit and Yaw-Steering-Mode attitude
    """
    return GenericOrbitModel(**ysm_context, earth_body=earth_body)


@pytest.fixture(name="s1_ebm", scope="module")
def given_earth_body_at_20221111():
    """
    Generate an EarthBody at 2022-11-11
    """

    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    return EarthBody(time_reference=time_model)


@pytest.fixture(name="s1_orbit", scope="module")
def given_fused_orbit(s1_ebm):
    """
    Fuse PRE and navatt orbits, in EF
    """

    driver = S3LegacyDriver(s1_ebm)

    pvt_orbit = driver.read_orbit_file(
        osp.join(
            TEST_DIR,
            "resources",
            "S1",
            "PVT_ATT_20221111T114656",
            "s1_orbit.xml",
        )
    )

    pre_orbit = driver.read_orbit_file(
        osp.join(
            TEST_DIR,
            "resources",
            "S1",
            "PREORB",
            "S1A_OPER_AUX_PREORB_OPOD_20221111T102740_V20221111T093852_20221111T161352.EOF",
        )
    )

    fused_orbit = GenericOrbitModel.merge_orbits([pre_orbit, pvt_orbit])
    fused_orbit["frame"] = "EF_EQUINOX"
    return fused_orbit


# ================================[ WHEN ACTIONS ]======================================


def when_computing_osv_with_generic_orbit_model(orbit_model: GenericOrbitModel, dataset, **kwargs):
    """
    BDD "WHEN" function that compute OSV with *new* :method:`GenericOrbitModel.get_osv` method.
    """
    return orbit_model.get_osv(dataset, **kwargs)


def when_computing_quat_with_generic_orbit_model(orbit_model: GenericOrbitModel, dataset, **kwargs):
    """
    BDD "WHEN" function that compute quaternions with *new*
    :method:`GenericOrbitModel.compute_quaternion` method.
    """
    return orbit_model.compute_quaternions(dataset, **kwargs)


# ================================[ TIME TESTS ]======================================


def test_date_decoding_from_olci_orbit_with_orekit(fro_20221030, time_model: TimeReference):
    """
    Test that all time points in OLCI orbit file are the same.

    Without this, we can't expected the same outputs on orbit interpolations when woring in a different time scale.
    """
    # GIVEN dates from the orbits points, in different time scales.
    dates_according_to_utc = list(time_model.to_dates(fro_20221030["times"]["UTC"], TimeRef.UTC))
    dates_according_to_tai = list(time_model.to_dates(fro_20221030["times"]["TAI"], TimeRef.TAI))
    dates_according_to_ut1 = list(time_model.to_dates(fro_20221030["times"]["UT1"], TimeRef.UT1))

    ts_utc = time_model.timeref_to_timescale(TimeRef.UTC)
    ts_tai = time_model.timeref_to_timescale(TimeRef.TAI)
    # ts_ut1 = time_model.timeref_to_timescale(TimeRef.UT1)

    # Some control logs
    logging.debug("UTC offsets -> %s", format_as_tree(fro_20221030["times"]["UTC"]["offsets"]))
    logging.debug("UTC dates   -> %s", format_as_tree(dates_according_to_utc[:3]))
    logging.debug("TAI offsets -> %s", format_as_tree(fro_20221030["times"]["TAI"]["offsets"]))
    logging.debug("TAI dates as AbsoluteDate -> %s", format_as_tree(dates_according_to_tai[:3]))
    logging.debug(
        "TAI dates as UTC -> %s",
        format_as_tree([d.toString(ts_utc) for d in dates_according_to_tai[:3]]),
    )
    logging.debug(
        "TAI dates as TAI -> %s",
        format_as_tree([d.toString(ts_tai) for d in dates_according_to_tai[:3]]),
    )
    logging.debug("UT1 offsets -> %s", format_as_tree(fro_20221030["times"]["UT1"]["offsets"]))
    logging.debug("UT1 dates   -> %s", format_as_tree(dates_according_to_ut1[:3]))

    def are_close_enough(ads1, ads2, ref1, ref2, precision):
        are_close = [ad1.isCloseTo(ad2, precision) for ad1, ad2 in zip(ads1, ads2)]
        ts_factory = time_model.timeref_to_timescale(TimeRef.TAI)
        delta = [ad1.offsetFrom(ad2, ts_factory) for ad1, ad2 in zip(ads1, ads2)]
        assert all(are_close), f"{ref1} - {ref2} dates > {precision}sec: {delta[:3]}..."

    # THEN:
    # - TAI time points are close enough from the UTC time points
    are_close_enough(dates_according_to_utc, dates_according_to_tai, "UTC", "TAI", 0.000001)

    # - But UT1 times points aren't close enough from the UTC time points
    #   Indeed, the same tests cannot be done on UT1 dates as they depend on the exact same IERS bulletin as the one
    #   used to generate the original orbit file, and we don't have it.


# ================================[ OSV TESTS ]======================================


def test_merge_orbits(fro_20221030, navatt_context):
    """
    Unit test for the merge_orbits function
    """

    # from given_navatt_from_20221101
    iers_bulletin = osp.join(f"{TEST_DIR}/resources/bulletinb-413.txt")
    iers_data = S3LegacyDriver.read_iers_file(iers_bulletin)
    time_model = TimeReference(iers_bulletin_b=iers_data)
    body_model = EarthBody(time_reference=time_model)
    # Transform FRO orbit to match navatt orbit frame
    navatt_ef = body_model.transform_orbit(navatt_context["orbit"].copy(), FrameId.EF)

    orbit_list = [fro_20221030, navatt_ef]

    fused_orbit = GenericOrbitModel.merge_orbits(orbit_list)

    ref_length = 34589

    assert len(fused_orbit["positions"]) == ref_length
    assert len(fused_orbit["velocities"]) == ref_length
    assert len(fused_orbit["times"]["GPS"]["offsets"]) == ref_length
    assert np.all(np.diff(fused_orbit["times"]["GPS"]["offsets"]) > 0)
    assert fused_orbit["time_ref"] == "GPS"

    diff_gps_utc = 86400.0 * (fused_orbit["times"]["GPS"]["offsets"] - fused_orbit["times"]["UTC"]["offsets"])
    assert np.allclose(diff_gps_utc, 18.0)


@pytest.mark.slow
def test_orbit_model_compute_osv(orbit_model_msi: GenericOrbitModel, osv_dataset):
    # Then, it executes
    # logging.debug("get_osv orekit0: %s", format_as_tree(osv_dataset))
    orbit_model_msi.get_osv(osv_dataset)


def test_interpolation_of_sampled_orbit_points_between_time_scales(fro_20221030, allclose, orb_model_olci_fro):
    """
    Test that new OrbitModel can reinterpolate points from the orbit definition
    where they actually are.
    The test checks the quality of the interpolation in various time scales: UTC, TAI and GPS.

    Observations:

        - Orekit interpolation of sample points is good.
        - However we have observed some degrations when using JDK 8 JVM instead of GraalVM on the precision
          of velocity interpolation on TAI and GPS time scales: absolute precision falls to 1e-6
    """
    # GIVEN: input fixtures

    tr = orb_model_olci_fro.time_reference_model

    # - Test datasets
    time_ref = fro_20221030["time_ref"]
    assert time_ref == "UTC"  # The test is written with this expectation in mind

    #   ~ UTC dataset
    dataset_ref, abs_dates_from_ref = given_input_dataset_and_dates(fro_20221030["times"][time_ref], tr)

    #   ~ TAI dataset
    dataset_tai, abs_dates_from_tai = given_input_dataset_and_dates(fro_20221030["times"]["TAI"], tr)

    #   ~ GPS dataset
    # The orbit file from the baseline gives no GPS data. But we want GPS dates for compatison as this is what EOCFI
    # ExplorerOrbit wrapper expects as inputs.
    dataset_gps, abs_dates_from_gps = given_input_dataset_and_dates(fro_20221030["times"]["GPS"], tr)

    # ~ Checking the quality of the input datasets
    # The precision of the comparisons of the orbit interpolation depends on the quality of the input dates.
    # And we'll see that there is a small degradation.
    # Note: allclose can't be used directly on AbsoluteDate as we need to be able to compute the RSM of an
    # AbsoluteDate...  => convert into duration from the firt date...
    start_date = abs_dates_from_tai[0]
    offsets_in_ref = [d.durationFrom(start_date) for d in abs_dates_from_ref]
    offsets_in_tai = [d.durationFrom(start_date) for d in abs_dates_from_tai]
    offsets_in_gps = [d.durationFrom(start_date) for d in abs_dates_from_gps]

    assert allclose(offsets_in_ref, offsets_in_tai, rtol=1e-8)
    assert not np.allclose(offsets_in_ref, offsets_in_tai, rtol=1e-9)  # 1 failure
    assert not np.allclose(offsets_in_ref, offsets_in_tai, rtol=1e-12)  # 5+ failures

    assert allclose(offsets_in_ref, offsets_in_gps, rtol=1e-8)
    assert not np.allclose(offsets_in_ref, offsets_in_gps, rtol=1e-9)  # 1 failure as well
    assert not np.allclose(offsets_in_ref, offsets_in_gps, rtol=1e-12)  # 5+ failures as well

    # WHEN
    when_computing_osv_with_generic_orbit_model(orb_model_olci_fro, dataset_ref)
    when_computing_osv_with_generic_orbit_model(orb_model_olci_fro, dataset_tai)
    when_computing_osv_with_generic_orbit_model(orb_model_olci_fro, dataset_gps)

    # THEN
    ref_pos = fro_20221030["positions"]
    ref_vel = fro_20221030["velocities"]

    # test outputs...
    assert allclose(dataset_ref["orb_pos"], ref_pos)
    assert allclose(dataset_ref["orb_vel"], ref_vel)

    # note: with a JVM 8 instead of GraalVM, the two (TAI and GPS) velocity tests may fail at atol=1e-7
    assert allclose(dataset_tai["orb_pos"], ref_pos)
    assert allclose(dataset_tai["orb_vel"], ref_vel)

    assert allclose(dataset_gps["orb_pos"], ref_pos)
    assert allclose(dataset_gps["orb_vel"], ref_vel)


def test_osv_interpolation_against_eocfi(s1_orbit, s1_ebm):
    """
    Estimate the accuracy (with EOCFI) of orbit interpolation in a S1 test scenario
    """

    config_ef = {"orbit": s1_orbit, "attitude": {"aocs_mode": "ZD", "frame": "EF_EQUINOX"}}
    model_ef = GenericOrbitModel(**config_ef, earth_body=s1_ebm)

    s1_times = np.load(osp.join(ZD_DIR, "s1_times.npy"))
    dataset = {
        "times": {
            "offsets": s1_times,
            "unit": "d",
            "ref": "UTC",
        }
    }
    model_ef.get_osv(dataset)
    pos_ef = np.load(osp.join(ZD_DIR, "s1_orb_pos.npy"))
    vel_ef = np.load(osp.join(ZD_DIR, "s1_orb_vel.npy"))

    max_error_pos = np.max(np.linalg.norm(dataset["orb_pos"] - pos_ef, axis=-1))
    max_error_vel = np.max(np.linalg.norm(dataset["orb_vel"] - vel_ef), axis=-1)
    if np.max(np.abs(dataset["orb_pos"] - pos_ef)) > 1e-2:
        warnings.warn(f"Inaccurate orbit position interpolation: {max_error_pos} m (> 1cm)", stacklevel=2)
    if np.max(np.abs(dataset["orb_vel"] - pos_ef)) > 1e-4:
        warnings.warn(f"Inaccurate orbit position interpolation: {max_error_vel} m/s (> 1e-4 m/s)", stacklevel=2)


# ================================[ ATTITUDE TESTS ]======================================


def test_orbit_model_compute_quaternion_navatt(orb_model_olci_navatt):
    """
    Unit test for the function :meth:`GenericOrbitModel.compute_quaternion` when relying on attitude samples
    """

    # - Test dataset
    dataset_gps = given_input_dataset(orb_model_olci_navatt.config["attitude"]["times"]["GPS"])

    when_computing_quat_with_generic_orbit_model(orb_model_olci_navatt, dataset_gps)

    ref_quat = orb_model_olci_navatt.config["attitude"]["quaternions"]

    # compute the maximum magnitude of the composed rotation: quat_test * quat_ref^-1
    rot_test = R.from_quat(dataset_gps["attitudes"])
    rot_ref = R.from_quat(ref_quat)
    full_mag = (rot_test * rot_ref.inv()).magnitude()

    assert np.max(full_mag) < 1e-15  # threshold is in radians


def test_orbit_model_can_compute_quaternion_ysm(orb_model_olci_ysm):
    """
    Unit test for the function :meth:`GenericOrbitModel.compute_quaternion` when in Yaw Steering Mode
    """

    # - Test dataset
    dataset_gps = given_input_dataset(orb_model_olci_ysm.config["orbit"]["times"]["GPS"])

    when_computing_quat_with_generic_orbit_model(orb_model_olci_ysm, dataset_gps)

    logging.debug("YSM quaternions: %s", pformat(dataset_gps["attitudes"]))

    # TODO: compareangainst a baseline


# ==================================[ ORBIT INFO TESTS ]====================================


def test_relaxed_orbit_anx(
    orb_model_olci_fro,
    # ~ eocfi_model_olci_fro,
):
    """
    Test GenericOrbitModel.info
    """
    # logging.debug("orbit info: %s" , format_as_tree(fro_20221030))
    # GIVEN: input fixtures

    # === Relaxed tests on many points
    cache = orb_model_olci_fro._cached  # pylint: disable=protected-access
    time_model = orb_model_olci_fro.time_reference_model

    def check_orbit_at_date(osv_idx: int | None = None, date: AbsoluteDate | None = None) -> None:
        date = date or cache["times"][osv_idx]
        # logging.debug("Testing OSV @%s (#%s)", date, osv_idx)
        # ~ t = time_model.from_date(date, ref=TimeRef.GPS)
        info_orekit = orb_model_olci_fro.get_info(date)
        # ~ info_eocfi = eocfi_model_olci_fro._gpd.orbit_info(t)  # pylint: disable=protected-access
        # ~ keys = {".repeat_cycle", ".cycle_length", ".mlst_drift", ".mlst", ".utc_smx", ".mean_kepl"}
        # ~ assert allclose_dicts(
        # ~ info_eocfi,
        # ~ info_orekit,
        # ~ ignore={".anx_date"} | keys,
        # ~ a_name="EOCFI info",
        # ~ b_name="Orekit info",
        # ~ atol=1e-1,
        # ~ )
        assert "utc_anx" in info_orekit
        assert "track_direction" in info_orekit
        assert "pos_anx" in info_orekit
        assert "nodal_period" in info_orekit

    # - around ANX, on sampled points; shall always be ascending...
    ao_indices = cache["absolute_orbit_indices"][1:-2]
    for ao_idx in ao_indices:
        check_orbit_at_date(ao_idx)

    # - around ANX sampled points
    for ao_idx in ao_indices:
        date = cache["times"][ao_idx]
        check_orbit_at_date(ao_idx, date=date - 5.0)  # minus 5sec
        check_orbit_at_date(ao_idx, date=date + 5.0)  # plus +5

    _ = """
    # - Check everything... Uncomment to test
    for idx in range(ao_indices[0], ao_indices[-1]):
        check_orbit_at_date(idx)
    """

    # - VZ/EF is negative at UTC=2022-10-30T01:56:00.000000 -> descending
    date = time_model.str_to_absolute_date("UTC=2022-10-30T01:56:00.000000", None)
    check_orbit_at_date(date=date)


def test_orbit_anx_exception_cases(orb_model_olci_fro):
    """
    Test GenericOrbitModel.info
    """

    cache = orb_model_olci_fro._cached  # pylint: disable=protected-access
    ao_indices = cache["absolute_orbit_indices"][1:-2]

    # === Check exception at times when the ANX cannot be estimated.
    with expect_fail(NotImplementedError, match=r".*Cannot search orbit information outside the range of.*first.*"):
        date = cache["times"][0] - 65.0  # long before the first sample
        orb_model_olci_fro.get_info(date=date)

    with expect_fail(NotImplementedError, match=r".*Cannot search orbit information outside the range of.*last.*"):
        date = cache["times"][-1] + 65.0  # long after the last sample
        orb_model_olci_fro.get_info(date=date)

    with expect_fail(NotImplementedError, match=r".*Cannot search the ANX of the first absolute orbit.*"):
        idx = ao_indices[0] - 1  # last sample of the first orbit
        date = cache["times"][idx]
        orb_model_olci_fro.get_info(date=date)

    # Cannot evaluate (yet?) nodal_period on last orbit
    idx = cache["absolute_orbit_indices"][-2]  # first date of the last orbit
    # logging.debug("idx: %s/%s", idx, len(cache["times"]))
    date = cache["times"][idx]
    assert orb_model_olci_fro.get_info(date=date)["nodal_period"] == NotImplemented

    # === Check calls with various parameters combinations
    with expect_fail(
        AssertionError, re.escape("orbit.get_info() shall be called on an absolute_orbit number or a date!")
    ):
        orb_model_olci_fro.get_info(date=None, abs_orbit=None)

    idx = ao_indices[5]
    date = cache["times"][idx]
    abs_orbit = orb_model_olci_fro.config["orbit"]["absolute_orbit"][idx]
    info_date = orb_model_olci_fro.get_info(date=date)
    info_orbit = orb_model_olci_fro.get_info(abs_orbit=abs_orbit, date=None)
    info_both = orb_model_olci_fro.get_info(abs_orbit=abs_orbit, date=date)
    keys = info_date.keys() - {"anx_date"}
    assert sub(info_date, keys) == sub(info_orbit, keys)
    assert sub(info_both, keys) == sub(info_date, keys)


def test_orbit_anx_using_fpo(orb_model_olci_fpo, fpo_20221030):
    """
    Test GenericOrbitModel.info using FPO file which contains PV coordinates for each ANX time.
    """
    # Compute the orbit info from time orb used to instansiate GenericOrbitModel()
    date = orb_model_olci_fpo.config["time_orb"]
    info_anx = orb_model_olci_fpo.get_info(date=date, time_ref=TimeRef.GPS)

    pos_anx_4 = fpo_20221030["positions"][4]
    vel_anx_4 = fpo_20221030["velocities"][4]
    time_anx_4 = fpo_20221030["times"]["UTC"]["offsets"][4]

    assert info_anx["utc_anx"] == time_anx_4
    assert np.allclose(info_anx["pos_anx"], pos_anx_4)
    assert np.allclose(info_anx["vel_anx"], vel_anx_4)


# ~ def test_precise_orbit_anx(
# ~ allclose_dicts,
# ~ orb_model_olci_fro,
# ~ eocfi_model_olci_fro,
# ~ ):
# ~ """
# ~ Test GenericOrbitModel.info for precise matching with EOCFI
# ~ """

# ~ # === Check precisely at reference time_orb point.
# ~ eocfi_info = eocfi_model_olci_fro.info
# ~ # logging.debug("EOCFI orbit info: %s", format_as_tree(eocfi_info))
# ~ # logging.debug(
# ~ #     "anx_utc -> %s",
# ~ #     time_model.to_str(eocfi_info["utc_anx"], ref_in=TimeRef.UTC, ref_out=TimeRef.UTC, fmt="STD_MICROSEC"),
# ~ # )
# ~ # logging.debug(
# ~ #     "anx_gps -> %s",
# ~ #     time_model.to_str(eocfi_info["gps_anx"], ref_in=TimeRef.GPS, ref_out=TimeRef.UTC, fmt="STD_MICROSEC"),
# ~ # )

# ~ keys = {".repeat_cycle", ".cycle_length", ".mlst_drift", ".mlst", ".utc_smx"}
# ~ logging.warning("The following orbit info aren't compared between Orekit and EOCFI: %s", keys)

# ~ # Previous tests have demonstrated that position interpolation is precide at atol=1e-3 (1mm)
# ~ assert np.allclose(eocfi_model_olci_fro.info["pos_anx"], orb_model_olci_fro.info["pos_anx"], atol=1e-3)
# ~ # The ω Osculating Keplerian element seems to be precise at 1e-3 as well. Is it enough?
# ~ assert np.allclose(eocfi_model_olci_fro.info["osc_kepl"]["w"], orb_model_olci_fro.info["osc_kepl"]["w"], atol=1e-3)
# ~ # The Mean Keplerian elements aren't that precise either. Are they correctly computed???
# ~ assert np.allclose(
# ~ eocfi_model_olci_fro.info["mean_kepl"]["m"], orb_model_olci_fro.info["mean_kepl"]["m"], atol=1e-1
# ~ )
# ~ assert np.allclose(
# ~ eocfi_model_olci_fro.info["mean_kepl"]["w"], orb_model_olci_fro.info["mean_kepl"]["w"], atol=1e-1
# ~ )
# ~ assert np.allclose(
# ~ eocfi_model_olci_fro.info["mean_kepl"]["e"], orb_model_olci_fro.info["mean_kepl"]["e"], atol=1e-6
# ~ )
# ~ assert allclose_dicts(
# ~ eocfi_info,
# ~ orb_model_olci_fro.info,
# ~ ignore={".anx_date", ".pos_anx", ".osc_kepl.w", ".mean_kepl.m", ".mean_kepl.w", ".mean_kepl.e"} | keys,
# ~ a_name="EOCFI info",
# ~ b_name="Orekit info",
# ~ )

# ~ assert abs(eocfi_info["gps_anx"] - orb_model_olci_fro.info["gps_anx"]) < 0.1 / 86400


# ==================================[ OOP TESTS ]====================================


def test_orbit_model_position_on_orbit(orb_model_olci_fro):
    """
    Unit test for OrbitModel.position_on_orbit()
    """

    gpx_anx = orb_model_olci_fro.info["gps_anx"]
    period = orb_model_olci_fro.info["period_jd"]

    times = {"offsets": np.arange(gpx_anx, gpx_anx + period, period / 12)}

    oop = orb_model_olci_fro.position_on_orbit(times)

    oop_ref = np.array([0.0, 30.40, 60.78, 91.07, 121.09, 150.12, 167.33, 215.29, 244.03, 272.91, 300.94, 325.68])
    assert np.allclose(oop, oop_ref, atol=0.01)
