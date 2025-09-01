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
Validation for OLCI Sentinel 3 products in RAC mode respect to legacy processor
"""


import logging
import os
import os.path as osp

import netCDF4
import numpy as np
import pytest
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import pointing_error_azi_zen  # pylint: disable=import-error

from asgard.core.frame import FrameId
from asgard.core.logger import initialize
from asgard.models.body import EarthBody
from asgard.sensors.sentinel3 import S3OLCIGeometry

logging.getLogger().setLevel(logging.INFO)

TEST_DIR = osp.dirname(__file__)

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")

CALIBRATION_FILE = osp.join(
    ASGARD_DATA,
    "S3AOLCIdataset",
    "S3A_OL_1_CAL_AX_20230620T000000_20991231T235959_20230616T120000___________________MPC_O_AL_028.SEN3",
    "OL_1_CAL_AX.nc",
)

initialize("eocfi")


@pytest.fixture(name="pointing_vectors", scope="module")
def read_pointing_vectors_legacy():
    """
    Fixture to extract pointing vectors
    """
    return S3LegacyDriver.olci_pointing_angles(CALIBRATION_FILE)


@pytest.fixture(name="thermoelastic", scope="module")
def read_thermoelastic_legacy():
    """
    Fixture to extract thermoelastic grids
    """
    return S3LegacyDriver.s3_thermoelastic_tables(CALIBRATION_FILE, group="thermoelastic_model_RC")


@pytest.fixture(name="fro_20220510", scope="module")
def read_fro_20220510_legacy():
    """
    Fixture to extract FRO orbit from 2022-05-10
    """
    legacy_orbit = [
        osp.join(
            ASGARD_DATA,
            "S3AOLCIdataset",
            "OLCI_TDS1",
            "S3A_AX___FRO_AX_20220510T000000_20220520T000000_20220513T065145___________________EUM_O_AL_001.SEN3",
            "S3A_OPER_MPL_ORBRES_20220510T000000_20220520T000000_0001.EOF",
        )
    ]

    return S3LegacyDriver.read_orbit_file(legacy_orbit[0])


@pytest.fixture(name="img_coord", scope="module")
def img_coord_product():
    """
    Image coordinates for OLCI RAC
    """
    img_coord = np.zeros((2731, 740, 2), dtype="int32")
    for row in range(2731):
        for col in range(740):
            img_coord[row, col, 0] = col
            img_coord[row, col, 1] = row
    return img_coord


@pytest.fixture(name="olci")  # , scope="module")
def olci_product(fro_20220510, pointing_vectors, thermoelastic):
    """
    Fixture to initialize a S3OLCIGeometry with navatt
    """

    # Info retrieval from BP_O1-DE_3-1 : "block_0_jd_gps" --> Table of acquisition time for each frame (MJD GPS)
    output_bp_de_3_1 = osp.join(ASGARD_DATA, "OLCI_RAC_validation", "BP_OC-DE_3-1.nc")
    tmp_frames = {}
    with netCDF4.Dataset(output_bp_de_3_1, "r", encoding="utf8") as de3_1_dataset:
        S3LegacyDriver.read_netcdf_array_fields(
            de3_1_dataset,
            tmp_frames,
            ["jd"],
        )

    frames = tmp_frames["jd"]

    output_bp_de_4_1 = osp.join(ASGARD_DATA, "OLCI_RAC_validation", "BP_OC-DE_4-1.nc")
    tmp_nav = {}
    with netCDF4.Dataset(output_bp_de_4_1, "r", encoding="utf8") as de4_1_dataset:
        S3LegacyDriver.read_netcdf_array_fields(
            de4_1_dataset,
            tmp_nav,
            ["jd_nav", "poo_nav"],
        )

    orbit_path = osp.join(ASGARD_DATA, "OLCI_RAC_validation", "orbit")
    att_path = osp.join(ASGARD_DATA, "OLCI_RAC_validation", "attitude")

    orbit_scratch = S3LegacyDriver.read_orbit_file(orbit_path)
    attitude_scratch = S3LegacyDriver.read_attitude_file(att_path)

    driver = S3LegacyDriver(EarthBody())
    fro_20220510_eme = driver.change_orbit_frame(fro_20220510, FrameId.EME2000)

    attitude_scratch["times"]["GPS"] = orbit_scratch["times"]["GPS"]
    attitude_scratch["time_ref"] = "GPS"

    config = {
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20220510_eme],
        },
        "resources": {"dem_path": GETAS_PATH, "dem_type": "ZARR"},
        "pointing_vectors": pointing_vectors,
        "thermoelastic": thermoelastic,
        "frame": {"times": {"offsets": frames}},
        "navatt": {
            "orbit": orbit_scratch,
            "attitude": attitude_scratch,
            "times": {
                "offsets": tmp_nav["jd_nav"],
            },
            "oop": tmp_nav["poo_nav"],
        },
    }

    return S3OLCIGeometry(**config)


@pytest.fixture(name="range_idx", scope="module")
def get_range_index():
    """
    Fixture to define the range of times taken from legacy data, outside this range results of
    geo-referencing are set to 0 by EOCFI processor
    """
    return [1036, 1572]


@pytest.fixture(name="breakpoint_sun_pos", scope="module")
def read_bp_ge_4_1():
    """
    Fixture to read breakpont geo-referencing file
    """
    breakpoint_file = osp.join(ASGARD_DATA, "OLCI_RAC_validation", "BP_OC-GE_4-1.nc")
    tmp_bp_ge = {}
    with netCDF4.Dataset(breakpoint_file, "r", encoding="utf8") as bp_dataset:
        S3LegacyDriver.read_netcdf_array_fields(
            bp_dataset,
            tmp_bp_ge,
            ["d_sun"],
        )
    return tmp_bp_ge["d_sun"]


@pytest.fixture(name="breakpoint_angles", scope="module")
def read_bp_ge_5_1():
    """
    Fixture to read breakpont geo-referencing file
    """
    breakpoint_file = osp.join(ASGARD_DATA, "OLCI_RAC_validation", "BP_OC-GE_5-1.nc")
    tmp_bp_ge = {}
    with netCDF4.Dataset(breakpoint_file, "r", encoding="utf8") as bp_dataset:
        S3LegacyDriver.read_netcdf_array_fields(bp_dataset, tmp_bp_ge, ["phi_s", "theta_s"])
    return tmp_bp_ge


@pytest.fixture(name="norm_diffuser", scope="module")
def read_ins():
    """
    Fixture to read Instrument ADF file
    """
    instrument = osp.join(
        ASGARD_DATA,
        "S3AOLCIdataset",
        "S3A_OL_1_INS_AX_20201030T120000_20991231T235959_20220505T120000___________________MPC_O_AL_009.SEN3",
        "OL_1_INS_AX.nc",
    )
    tmp_norm_vec = {}
    with netCDF4.Dataset(instrument, "r", encoding="utf8") as ins_dataset:
        S3LegacyDriver.read_netcdf_array_fields(
            ins_dataset["white_diffuser_geometry"],
            tmp_norm_vec,
            ["wdiff1_normal_vector"],
        )

    return tmp_norm_vec["wdiff1_normal_vector"]


@pytest.mark.slow
@pytest.mark.dem
def test_val_instrument_to_sun(olci, norm_diffuser, range_idx, breakpoint_angles):  # pylint: disable=too-many-locals
    """
    Validation test for S3OLCIGeometry.instrument_to_sun in RAC mode
    with navatt data and for all cameras
    """

    times = olci.config["frame"]["times"]["offsets"][range_idx[0] : range_idx[1]]
    theta_sf_legacy = breakpoint_angles["theta_s"][range_idx[0] : range_idx[1]]
    phi_sf_legacy = breakpoint_angles["phi_s"][range_idx[0] : range_idx[1]]

    # Compute Sf vector
    sun_pos = olci.instrument_to_sun(times)
    sun_pos_eocfi = np.load(osp.join(TEST_DIR, "../resources/S3/OLCI/sun_pos_eocfi_rac.npy"))
    sun_norm = np.linalg.norm(sun_pos, axis=1)

    # Compute theta_sf
    sun_pos_x, sun_pos_y, sun_pos_z = sun_pos[:, 1], sun_pos[:, 0], -sun_pos[:, 2]
    sun_pos_eocfi_x, sun_pos_eocfi_y, sun_pos_eocfi_z = sun_pos_eocfi[:, 0], sun_pos_eocfi[:, 1], sun_pos_eocfi[:, 2]

    logging.warning(
        "The gap between sun position computed with Orekit vs EOCFI is %s",
        np.array([sun_pos_x - sun_pos_eocfi_x, sun_pos_y - sun_pos_eocfi_y, sun_pos_z - sun_pos_eocfi_z]),
    )

    unit_sun = 1.0 / sun_norm[:, None] * np.column_stack((sun_pos_y, sun_pos_x, -sun_pos_z))

    # Compute theta_sf in degrees
    theta_sf = np.degrees(np.arccos(np.dot(norm_diffuser, unit_sun.T)))

    # Compute phi_sf, see Angles Computations (OC-GE_5) in DPM
    u_instr = np.array([1, 0, 0])
    u_diff_num = u_instr - np.dot(norm_diffuser.dot(u_instr), norm_diffuser)
    u_diff = u_diff_num / np.linalg.norm(u_diff_num)
    v_diff = np.cross(norm_diffuser, u_diff)

    # Compute phi_sf in degrees
    phi_sf = np.degrees(np.arctan2(unit_sun.dot(v_diff), unit_sun.dot(u_diff)))

    direction_sf_legacy = np.stack((phi_sf_legacy, theta_sf_legacy), axis=1)
    direction_sf = np.stack((phi_sf, theta_sf), axis=1)

    pointing_error_deg = pointing_error_azi_zen(direction_sf_legacy, direction_sf)

    tolerance_angles = 1.0e-4
    counter = 0
    for pointing_err in range(pointing_error_deg.size):
        if np.fabs(pointing_error_deg[pointing_err]) > tolerance_angles:
            counter += 1

    logging.info(
        "Number of sun angles (pointing direction) above tolerance (%s deg) = %s upon %s angles",
        tolerance_angles,
        counter,
        pointing_error_deg.size,
    )
    logging.info("max error = %s", np.max(pointing_error_deg[:]))

    # Check that 99.73% (3 sigma) of the error on sun angles pointing direction is smaller than tolerance
    # Define tolerance for angles direction
    tol_angles = np.full(shape=pointing_error_deg.shape, fill_value=tolerance_angles)

    # Check if error on angle directions < tolerance
    bool_angles = np.less(np.absolute(pointing_error_deg), tol_angles)

    if np.sum(bool_angles) / bool_angles.size <= 0.9973:
        warn_msg = (
            "As the sun position is computed with Orekit (which is more precise than EOCFI) "
            "the error is in average equals to %s"
        )
        logging.warning(warn_msg, np.mean(pointing_error_deg))
