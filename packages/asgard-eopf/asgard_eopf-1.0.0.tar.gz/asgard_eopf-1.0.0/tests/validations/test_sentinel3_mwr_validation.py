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
Validation for MWR Sentinel-3 product respect to legacy data
"""
import logging
import os
import os.path as osp

import netCDF4
import numpy as np
import pytest
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import GeodeticComparator  # pylint: disable=import-error

from asgard.core.frame import FrameId
from asgard.core.time import JD_TO_SECONDS, TimeRef
from asgard.models.body import EarthBody
from asgard.models.time import TimeReference
from asgard.sensors.sentinel3 import S3MWRGeometry

TEST_DIR = osp.dirname(osp.dirname(__file__))
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")
NB_FRAMES = 39057


@pytest.fixture(name="fro_20221030", scope="module")
def read_fro_20221030_legacy():
    """
    Fixture to extract FRO orbit from 2017-01-01
    """
    legacy_orbit = [
        osp.join(
            ASGARD_DATA,
            "S3AMWRdataset",
            "S3A_AX___FRO_AX_20221030T000000_20221109T000000_20221102T065450___________________EUM_O_AL_001.SEN3",
            "S3A_OPER_MPL_ORBRES_20221030T000000_20221109T000000_0001.EOF",
        )
    ]
    return S3LegacyDriver.read_orbit_file(legacy_orbit[0])


@pytest.fixture(name="comparator", scope="module")
def get_comparator():
    """
    Fixture to instanciate GeodeticComparator object
    """
    # Build geodetic comparator
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    body = EarthBody(time_reference=time_model)

    return GeodeticComparator(body_model=body)


@pytest.fixture(name="pointing_angles", scope="module")
def read_pointing_angles():
    """
    Fixture to extract pointing angles
    """
    calibration_file = osp.join(
        ASGARD_DATA,
        "S3AMWRdataset",
        "S3A_MW___CHDNAX_20160216T000000_20991231T235959_20210929T120000___________________MPC_O_AL_005.SEN3",
        "S3A_MW_CCDB_CHAR_NOM.20210728000000.nc",
    )
    pointing_dataset = netCDF4.Dataset(calibration_file, "r")
    return {
        "along_angle": np.array(
            [
                pointing_dataset["antenna_pointing"].variables["theta_a"][:][0][1],
                pointing_dataset["antenna_pointing"].variables["theta_a"][:][1][1],
            ],
            dtype=np.double,
        ),
        "across_angle": np.array(
            [
                pointing_dataset["antenna_pointing"].variables["theta_x"][:][0][1],
                pointing_dataset["antenna_pointing"].variables["theta_x"][:][1][1],
            ],
            dtype=np.double,
        ),
    }


@pytest.fixture(name="img_coord", scope="module")
def img_coord_product():
    """
    Image coordinates for OLCI
    """
    img_coord = np.zeros((NB_FRAMES, 1, 2), dtype="int32")
    for row in range(NB_FRAMES):
        for col in range(1):
            img_coord[row, col, 0] = col
            img_coord[row, col, 1] = row
    return img_coord


@pytest.fixture(name="netcdf_l1", scope="module")
def get_preprocessing():
    """
    Parse preprocessing results of MWR legacy processor
    """
    legacy_pre = osp.join(ASGARD_DATA, "MWR_validation", "measurement.nc")
    return netCDF4.Dataset(legacy_pre)


@pytest.fixture(name="scratch_data", scope="module")
def get_scratch_files_from_navatt():
    """
    Get scratch attitude and orbit files
    """
    attitude_legacy_path = osp.join(ASGARD_DATA, "MWR_validation", "attitude_file_legacy.xml")
    orbit_legacy_path = osp.join(ASGARD_DATA, "MWR_validation", "orbit_file_legacy.xml")

    attitude_legacy_file = S3LegacyDriver.read_attitude_file(attitude_legacy_path)
    orbit_legacy_file = S3LegacyDriver.read_orbit_file(orbit_legacy_path)

    return attitude_legacy_file, orbit_legacy_file


@pytest.fixture(name="mwr", scope="module")
def mwr_product(fro_20221030, pointing_angles, netcdf_l1, scratch_data):
    """
    Test fixture to produce a S3MWRLegacyProduct
    """
    logging.info("Creating S3MWR product...")
    time_mwr = np.ma.getdata(netcdf_l1["time_mwr_l1b"]) / JD_TO_SECONDS
    frames = TimeReference().convert(time_mwr, ref_in=TimeRef.UTC, ref_out=TimeRef.GPS)

    attitude_scratch, orbit_scratch = scratch_data

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    body = EarthBody(time_reference=time_model)

    fro_20221030_eme = body.transform_orbit(fro_20221030.copy(), FrameId.EME2000)
    fro_20221030_eme["time_ref"] = "GPS"

    orbit_scratch["time_ref"] = "GPS"
    attitude_scratch["times"]["GPS"] = orbit_scratch["times"]["GPS"]
    attitude_scratch["time_ref"] = "GPS"

    config = {
        "eop": {
            "iers_bulletin_b": iers_data,
        },
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20221030_eme],
        },
        "pointing_angles": pointing_angles,
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
    return S3MWRGeometry(**config)


@pytest.mark.slow
@pytest.mark.dem
def test_direct_loc_mwr_val(mwr, img_coord, netcdf_l1, comparator):
    """
    Validation test for S3MWRGeometry.direct_loc with navatt data
    """
    logging.info("Launching MWR validation...")

    sensor_list = ["C1", "C2"]

    gnd_legacy = np.transpose(
        np.array(
            [
                np.ma.getdata(netcdf_l1["lon_mwr_l1b"]) % 360.0,
                np.ma.getdata(netcdf_l1["lat_mwr_l1b"]),
                np.ma.zeros((NB_FRAMES, 2)),
            ]
        ),
        axes=[2, 1, 0],
    )

    logging.info("Apply direct loc...")
    gnd_vec = np.zeros((2, NB_FRAMES, 3))  # dimensions ->(sensor, frame, coords)
    times_vec = np.zeros((2, NB_FRAMES))  # dimensions ->(sensor, frame)
    for i, cam in enumerate(["C1", "C2"]):
        gnd, time = mwr.direct_loc(
            img_coord, geometric_unit=cam, altitude=0.0
        )  # Use constant altitude over ellipsoid with altitude=0.0
        gnd_vec[i] = np.squeeze(gnd, axis=1)
        # Put longitude in range [0,360]
        times_vec[i, ...] = np.squeeze(time, axis=1)

    # Put direct_loc longitude output in range [0,360]
    gnd_vec[:, :, 0] %= 360.0

    # Compute error on geodetic distance for each time
    error_list = []
    for i in range(len(sensor_list)):
        error_list.append(comparator.planar_error(gnd_legacy[i], gnd_vec[i]))
    error_map = np.array(error_list)
    logging.info("Geodetic planar max error = %s", np.max(error_map))

    # Define tolerance for planimetric error (m)
    tolerance_planimetric = 15.5
    tol_dist = np.full(shape=error_map.shape, fill_value=tolerance_planimetric)

    # Check for each time and sensor if error on geodetic distance smaller than the tolerance
    bool_dist = np.less(np.absolute(error_map), tol_dist)

    # Compute the number of points above the tolerance
    for cam in sensor_list:
        logging.info(
            "Sensor %s -> number of points above tolerance (%sm): \
            %s upon %s geodetic points",
            cam,
            tolerance_planimetric,
            bool_dist.size - np.sum(bool_dist),
            error_map.size,
        )

    # Check that 99.73% (3sigma) of the error on times is smaller than tolerance
    assert np.sum(bool_dist) / bool_dist.size > 0.9973
