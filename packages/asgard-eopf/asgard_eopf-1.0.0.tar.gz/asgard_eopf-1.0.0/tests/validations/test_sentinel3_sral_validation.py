#!/usr/bin/env python
# coding: utf8
#
# Copyright 2024 CS GROUP
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
Validation for SRAL Sentinel 3 products respect to legacy data
"""


import logging
import os
import os.path as osp

import netCDF4
import numpy as np
import pytest
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import GeodeticComparator  # pylint: disable=import-error

from asgard.models.body import EarthBody
from asgard.models.time import JD_TO_SECONDS, TimeRef, TimeReference
from asgard.sensors.sentinel3.sral import S3SRALGeometry

TEST_DIR = osp.dirname(__file__)

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")


@pytest.fixture(name="fro_20200708", scope="module")
def read_fro_20200708_legacy():
    """
    Fixture to extract FRO orbit from 2020-07-08
    """
    legacy_orbit = [
        osp.join(
            ASGARD_DATA,
            "S3BSRALdataset",
            "S3B_AX___FRO_AX_20200708T000000_20200718T000000_20200711T065100___________________EUM_O_AL_001.SEN3",
            "S3B_OPER_MPL_ORBRES_20200708T000000_20200718T000000_0001.EOF",
        )
    ]

    return S3LegacyDriver.read_orbit_file(legacy_orbit[0])


@pytest.fixture(name="comparator", scope="module")
def get_comparator():
    """
    Fixture to instanciate GeodeticComparator object
    """
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "../resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    body = EarthBody(time_reference=time_model)

    return GeodeticComparator(body_model=body)


@pytest.fixture(name="sral", scope="module")
def sral_product(fro_20200708, cal_l1b):
    """
    Fixture to initialize a S3SRALGeometry with navatt
    """

    time_cal2_sar = np.ma.getdata(cal_l1b["time_l0_cal2_sar"][:]) / JD_TO_SECONDS

    orbit_path = osp.join(ASGARD_DATA, "SRAL_validation", "Orbit_Scratch.EEF")
    att_path = osp.join(ASGARD_DATA, "SRAL_validation", "Altitude_Scratch.EEF")

    orbit_scratch = S3LegacyDriver.read_orbit_file(orbit_path)
    attitude_scratch = S3LegacyDriver.read_attitude_file(att_path)

    # We set a common time scale for orbit and attitude -> GPS
    attitude_scratch["time_ref"] = "GPS"
    attitude_scratch["times"]["GPS"] = orbit_scratch["times"]["GPS"]
    orbit_scratch["time_ref"] = "GPS"

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "../resources/bulletinb-413.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    frames = time_model.convert(time_cal2_sar, ref_in=TimeRef.UTC, ref_out=TimeRef.GPS)

    config = {
        "eop": {
            "iers_bulletin_b": iers_data,
        },
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20200708],
        },
        "frame": {"times": {"offsets": frames}},
        "navatt": {
            "orbit": orbit_scratch,
            "attitude": attitude_scratch,
            "times": {
                "offsets": orbit_scratch["times"]["GPS"]["offsets"],
                "ref": "GPS",
            },
            "oop": np.zeros(attitude_scratch["quaternions"].shape[0]),
        },
    }

    return S3SRALGeometry(**config)


@pytest.fixture(name="cal_l1b", scope="module")
def get_preprocessing():
    """
    Parse preprocessing results of SRAL legacy processor
    """
    legacy_pre = osp.join(ASGARD_DATA, "SRAL_validation", "calibration_l1bi.nc")

    return netCDF4.Dataset(legacy_pre)


@pytest.fixture(name="img_coord", scope="module")
def img_coord_product():
    """
    Image coordinates for SRAL
    """
    return np.column_stack((np.arange(120), np.arange(120)))


@pytest.mark.slow
@pytest.mark.dem
def test_direct_loc_sral_val(sral, img_coord, cal_l1b, comparator):
    """
    Validation test for S3SRALGeometry.direct_loc with navatt data
    """

    # Truncate 0 values at the beginning and at the end of the ground legacy vectors lon/lat/alt
    gnd_legacy = np.array(
        [
            np.ma.getdata(cal_l1b["lon_l0_cal2_sar"][:]),
            np.ma.getdata(cal_l1b["lat_l0_cal2_sar"][:]),
            np.ma.getdata(cal_l1b["alt_l0_cal2_sar"][:]),
            np.ma.getdata(cal_l1b["orb_alt_rate_l0_cal2_sar"]),
        ]
    ).swapaxes(0, 1)

    gnd = sral.direct_loc(img_coord)
    alt_rate = sral.compute_altitude_rate(img_coord, eps_value=1e-5)
    ground = np.c_[gnd, alt_rate]

    # S3 SRAL resolution = 300 m
    # Define tolerance for planimetric error (m)
    tolerance_planimetric = 10
    # Define tolerance for altitude (m)
    tolerance_altitude = 1

    # Compute error on geodetic distance for each times
    error_map = comparator.planar_error(gnd_legacy[:, :3], ground[:, :3])

    error_height = comparator.height_error(gnd_legacy[:, :3], ground[:, :3])

    # diff_times = np.absolute(np.subtract(times_legacy, time))

    err_map_arr = np.array(error_map)
    error_height_arr = np.abs(np.array(error_height))

    # Define tolerance for geodetic distance (10m)
    tol_dist = np.full(shape=err_map_arr.shape, fill_value=tolerance_planimetric)

    # Define tolerance for altitude (1m)
    tol_height = np.full(shape=error_height_arr.shape, fill_value=tolerance_altitude)

    # Define tolerance for times
    # tol_time = np.full(shape=diff_times.shape, fill_value=1e-12)

    bool_dist = np.less(err_map_arr, tol_dist)
    bool_alt = np.less(error_height_arr, tol_height)
    # bool_times = np.less(diff_times, tol_time)

    # Check that 99.73% (3sigma) of the error on longitude and latitude is smaller than tolerance
    assert np.sum(bool_dist) / bool_dist.size > 0.9973

    # Check that 99.73% (3sigma) of the error on altitude is smaller than tolerance
    assert np.sum(bool_alt) / bool_alt.size > 0.9973

    # Check that 99.73% (3sigma) of the error on times is smaller than tolerance
    # assert np.sum(bool_times) / bool_times.size > 0.9973


@pytest.mark.slow
@pytest.mark.dem
def test_compute_altitude_rate_sral_val(sral, img_coord, cal_l1b):
    """
    Validation test for S3SRALGeometry.compute_altitude_rate with navatt data
    """

    # Truncate 0 values at the beginning and at the end of the ground legacy vectors lon/lat/alt
    alt_rate_legacy = np.array(np.ma.getdata(cal_l1b["orb_alt_rate_l0_cal2_sar"]))

    alt_rate = sral.compute_altitude_rate(img_coord, eps_value=1e-5)

    diff_alt_rate = np.absolute(np.subtract(alt_rate_legacy, alt_rate))

    # Define tolerance for altitude rate
    # NOTICE : that in legacy processor output the precision of double is 10^(-2)
    tol_alt_rate = np.full(shape=diff_alt_rate.shape, fill_value=1e-2)

    logging.warning("The double precision of altitude rate output is 10^(-2)")

    bool_alt_rate = np.less(diff_alt_rate, tol_alt_rate)

    # Check that 99.73% (3sigma) of the error on altitude rate is smaller than tolerance
    assert np.sum(bool_alt_rate) / bool_alt_rate.size > 0.9973


@pytest.mark.slow
@pytest.mark.dem
def test_compute_incidence_angles_val(sral, cal_l1b):
    """
    Validation test for S3SRALGeometry.incidence_angles with navatt data
    """
    # Truncate 0 values at the beginning and at the end of the ground legacy vectors lon/lat/alt
    gnd_legacy = np.array(
        [
            np.ma.getdata(cal_l1b["lon_l0_cal2_sar"][:]),
            np.ma.getdata(cal_l1b["lat_l0_cal2_sar"][:]),
            np.ma.getdata(cal_l1b["alt_l0_cal2_sar"][:]),
            np.ma.getdata(cal_l1b["orb_alt_rate_l0_cal2_sar"]),
        ]
    ).swapaxes(0, 1)

    times_legacy = sral.config["frame"]["times"]["offsets"]

    incidence_angles = sral.incidence_angles(gnd_legacy[:, :3], times_legacy)

    assert np.allclose(incidence_angles, np.zeros(gnd_legacy[:, :2].shape))
