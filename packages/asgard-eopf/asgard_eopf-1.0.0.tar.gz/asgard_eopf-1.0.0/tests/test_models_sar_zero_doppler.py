#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
Unit tests for orbit model ZeroDoppler mode
"""

import os.path as osp

import numpy as np
import pytest
from drivers.sentinel_1_legacy import S1LegacyDriver
from scipy.spatial.transform import Rotation as R

from asgard.core.frame import FrameId
from asgard.models.body import EarthBody
from asgard.models.orbit import GenericOrbitModel
from asgard.models.time import TimeReference

TEST_DIR = osp.dirname(__file__)

ZD_DIR = osp.join(TEST_DIR, "resources", "S1", "zero_doppler")


@pytest.fixture(name="driver", scope="module")
def given_legacy_driver():
    """
    Create a S1LegacyDriver with IERS bulletin for 2022-11-11
    """
    iers_data = S1LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    return S1LegacyDriver(EarthBody(time_reference=time_model))


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
    orbit = driver.read_orbit_file(orbit_file)

    return orbit


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


@pytest.fixture(name="pos_tod", scope="module")
def given_tod_reference_pos():
    """
    Orbit state vector in TOD frame computed by EOCFI
    """

    return np.load(osp.join(ZD_DIR, "s1_orb_pos_tod.npy"))


@pytest.fixture(name="vel_tod", scope="module")
def given_tod_reference_vel():
    """
    Orbit state vector in TOD frame computed by EOCFI
    """

    return np.load(osp.join(ZD_DIR, "s1_orb_vel_tod.npy"))


@pytest.fixture(name="fused_orbit", scope="module")
def given_fused_orbit(preorb_20221111, pvt_20221111):
    """
    Fuse PRE and navatt orbits, in EF
    """

    fused_orbit = GenericOrbitModel.merge_orbits([preorb_20221111, pvt_20221111])
    fused_orbit["frame"] = "EF_EQUINOX"

    return fused_orbit


@pytest.fixture(name="model", scope="module")
def given_orbit_model(fused_orbit, driver):
    """
    Build a GenericOrbitModel
    """

    # reproj orbit to GCRF
    reproj_orbit = driver.change_orbit_frame(fused_orbit, FrameId.GCRF)

    config = {"orbit": reproj_orbit, "attitude": {"aocs_mode": "ZD", "frame": "GCRF"}}

    return GenericOrbitModel(**config, earth_body=driver.earth_body)


@pytest.fixture(name="acq_times", scope="module")
def given_input_times():
    """
    Load sample acquisition times
    """
    time_array = np.load(osp.join(ZD_DIR, "s1_times.npy"))
    acq_times = {
        "offsets": time_array,
        "unit": "d",
        "ref": "UTC",
    }
    return acq_times


@pytest.fixture(name="zd_ref", scope="module")
def given_reference_zd_quaternions():
    """
    Load reference quaternion for Zero-Doppler frame (from EOCFI)
    """

    return np.load(osp.join(ZD_DIR, "s1_zd_quaternions.npy"))


def test_orbit_zero_doppler_mode(model, acq_times, zd_ref):
    """
    Test computation of zero-doppler attitude from GenericOrbitModel
    """

    assert model is not None

    dataset = {"times": acq_times}
    model.compute_quaternions(dataset)

    assert "attitudes" in dataset

    rot_test = R.from_quat(dataset["attitudes"])
    rot_ref = R.from_quat(zd_ref)
    full_mag = (rot_test * rot_ref.inv()).magnitude()
    # ~ print("First implementation error magnitude:")
    # ~ print(full_mag)
    assert np.all(full_mag < 7e-6)


def test_orbit_zero_doppler_from_reference_osv(pos_tod, vel_tod, acq_times, zd_ref, model):
    """
    Test computation of zero-doppler attitude from EOCFI OSV data in TOD frame
    """

    # try computation from reference TOD osv
    # pylint: disable=protected-access
    rot_zd_to_tod = model._cached["attitude_provider"].compute_frame_tod(pos_tod, vel_tod)

    # compute TOD to EME2000 with Orekit
    dataset = {"times": acq_times}
    model.earth_body_model.frame_transform(
        dataset,
        frame_in=FrameId.TOD,
        frame_out=FrameId.GCRF,
        fields_out=("tod_eme2000_T", "tod_eme2000_R"),
    )
    tod_to_target = R.from_quat(dataset["tod_eme2000_R"])

    # TOD to EME2000 from EOCFI
    eocfi_tod_to_eme2000 = R.from_quat(np.load(osp.join(ZD_DIR, "s1_tod_eme2000_quaternions.npy")))

    rot_zd_to_target = tod_to_target * rot_zd_to_tod

    rot_ref = R.from_quat(zd_ref)
    full_mag = (rot_zd_to_target * rot_ref.inv()).magnitude()
    # ~ print("Using EOCFI TOD error magnitude")
    # ~ print(full_mag)
    assert np.all(full_mag < 4e-7)  # Observed: 3.37e-7 rad

    # using also TOD to EME2000 from EOCFI
    rot_zd_to_target = eocfi_tod_to_eme2000 * rot_zd_to_tod

    full_mag = (rot_zd_to_target * rot_ref.inv()).magnitude()
    # ~ print("Using EOCFI TOD + EME2000 error magnitude")
    # ~ print(full_mag)
    assert np.all(full_mag < 1e-15)  # Observed: between 1e-16 and 1e-15 rad
