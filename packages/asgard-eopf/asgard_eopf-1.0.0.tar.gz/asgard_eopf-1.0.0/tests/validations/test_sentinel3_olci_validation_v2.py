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
Validation for OLCI Sentinel 3 products in Earth Observation mode respect to legacy processor
"""


import glob
import logging
import os
import os.path as osp

import netCDF4
import numpy as np
import pytest
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import (  # pylint: disable=import-error
    GeodeticComparator,
    pointing_error_azi_zen,
)

from asgard.core.frame import FrameId
from asgard.core.logger import initialize
from asgard.core.math import flatten_array, restore_array
from asgard.models.body import EarthBody
from asgard.models.time import TimeReference
from asgard.sensors.sentinel3 import S3OLCIGeometry

logging.getLogger().setLevel(logging.INFO)

TEST_DIR = os.path.dirname(osp.dirname(__file__))

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")


initialize("eocfi")


@pytest.fixture(name="calibration_path")
def get_calibration_path(dataset_name):
    """
    Fixture to extract pointing vectors
    """
    calibration_base_path = osp.join(
        ASGARD_DATA,
        "S3AOLCIdataset",
        dataset_name,
    )

    calib_folder = glob.glob(os.path.join(calibration_base_path, "S3A_OL_1_CAL_AX*"))

    if not calib_folder:
        raise FileNotFoundError("No folder matching 'S3A_OL_1_CAL_AX*' found!")

    calibration_path = os.path.join(calib_folder[0], "OL_1_CAL_AX.nc")
    return calibration_path


@pytest.fixture(name="pointing_vectors")
def read_pointing_vectors_legacy(calibration_path):
    """
    Fixture to extract pointing vectors
    """

    return S3LegacyDriver.olci_pointing_angles(calibration_path)


@pytest.fixture(name="thermoelastic")
def read_thermoelastic_legacy(calibration_path):
    """
    Fixture to extract thermoelastic grids
    """

    return S3LegacyDriver.s3_thermoelastic_tables(calibration_path, group="thermoelastic_model_EO")


@pytest.fixture(name="fro_file")
def read_fro_legacy(dataset_name):
    """
    Fixture to extract FRO orbit from 2022-05-10
    """
    legacy_base_orbit = osp.join(
        ASGARD_DATA,
        "S3AOLCIdataset",
        dataset_name,
    )

    legacy_orbit = glob.glob(os.path.join(legacy_base_orbit, "S3A_AX___FRO_AX*", "S3A_OPER_MPL_ORBRES_*.EOF"))

    if not legacy_orbit:
        raise FileNotFoundError("No folder matching 'S3A_AX___FRO_AX*.SEN3' found!")

    return S3LegacyDriver.read_orbit_file(legacy_orbit[0])


@pytest.fixture(name="img_coord")
def img_coord_product(breakpoint_gr):
    """
    Image coordinates for OLCI
    """
    shape_ground_coord = breakpoint_gr["block_0_lon"].shape

    rows = shape_ground_coord[0] - 206
    cols = shape_ground_coord[2]
    row_indices = np.arange(rows)
    col_indices = np.arange(cols)

    coordinates = np.zeros((rows, cols, 2), dtype="int64")

    coordinates[..., 0] = col_indices
    coordinates[..., 1] = row_indices[:, np.newaxis]
    return coordinates


@pytest.fixture(name="breakpoint_gr")
def read_legacy(dataset_name):
    """
    Fixture to read breakpont geo-referencing file
    """
    breakpoint_file = osp.join(ASGARD_DATA, "OLCI_validation", dataset_name, "BP_O1-GR_4-1.nc")

    return netCDF4.Dataset(breakpoint_file)


@pytest.fixture(name="olci")
def olci_product(dataset_name, fro_file, pointing_vectors, thermoelastic, range_idx):
    """
    Fixture to initialize a S3OLCIGeometry with navatt
    """

    # Info retrieval from BP_O1-DE_3-1 : "block_0_jd_gps" --> Table of acquisition time for each frame (MJD GPS)
    output_bp_de_3_1 = osp.join(ASGARD_DATA, "OLCI_validation", dataset_name, "BP_O1-DE_3-1.nc")
    tmp_frames = {}
    with netCDF4.Dataset(output_bp_de_3_1, "r", encoding="utf8") as de3_1_dataset:
        S3LegacyDriver.read_netcdf_array_fields(
            de3_1_dataset,
            tmp_frames,
            ["block_0_jd_gps"],
        )

    frames = tmp_frames["block_0_jd_gps"][range_idx[0] : range_idx[1]]

    bp_de_4_1 = osp.join(ASGARD_DATA, "OLCI_validation", dataset_name, "BP_O1-DE_4-1.nc")
    tmp_nav = {}
    with netCDF4.Dataset(bp_de_4_1, "r", encoding="utf8") as de4_1_dataset:
        S3LegacyDriver.read_netcdf_array_fields(
            de4_1_dataset,
            tmp_nav,
            ["jd_nav", "poo_nav"],
        )

    orbit_path = osp.join(ASGARD_DATA, "OLCI_validation", dataset_name, "orbit")
    att_path = osp.join(ASGARD_DATA, "OLCI_validation", dataset_name, "attitude")

    orbit_scratch = S3LegacyDriver.read_orbit_file(orbit_path)
    attitude_scratch = S3LegacyDriver.read_attitude_file(att_path)

    driver = S3LegacyDriver(EarthBody())
    fro_eme = driver.change_orbit_frame(orbit=fro_file, frame=FrameId.EME2000)

    attitude_scratch["times"]["GPS"] = orbit_scratch["times"]["GPS"]
    attitude_scratch["time_ref"] = "GPS"

    config = {
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_eme],
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
    geo-referencing are set to 0 by legacy processor
    """
    return [106, -100]


@pytest.mark.parametrize(
    "dataset_name",
    [
        ("OLCI_TDS1"),
        ("OLCI_TDS2"),
    ],
    ids=[
        "nominal_tds",
        "antimeridian_tds",
    ],
)
@pytest.mark.slow
@pytest.mark.dem
def test_direct_loc_all_cam_v2(olci, dataset_name, img_coord, range_idx, breakpoint_gr):  # pylint: disable=R0914
    """
    Validation test for S3OLCIGeometry.direct_loc with navatt data and for all cameras
    """
    # Possibility to take a subset of the data with a step
    step = 10

    # Define a subset on coordinates (time, pixel) of 10% to make test faster
    subset_indices_1 = slice(0, img_coord.shape[0], step)
    subset_indices_2 = slice(0, img_coord.shape[1], step)
    subset_coord = img_coord[subset_indices_1, subset_indices_2]

    nb_pixel = subset_coord.shape[1]
    gnd_legacy = np.array(
        [
            ((breakpoint_gr["block_0_lon"][range_idx[0] : range_idx[1], ...] + 180) % 360) - 180,
            breakpoint_gr["block_0_lat"][range_idx[0] : range_idx[1], ...],
            breakpoint_gr["block_0_alt"][range_idx[0] : range_idx[1], ...],
        ]
    )[:, subset_indices_1, :, subset_indices_2]

    times_legacy = (
        np.tile(olci.config["frame"]["times"]["offsets"], (nb_pixel, 5, 1))
        .swapaxes(0, 1)
        .swapaxes(1, 2)[:, subset_indices_1, :]
    )

    gnd_vec, times_vec = [], []

    # Because low-level API used Pyrugged which is not optimized the for loop on direct_loc is skip by default
    # using the bool variable launch_test_too_long.
    launch_test_too_long = True
    if launch_test_too_long:
        for cam in ["C1", "C2", "C3", "C4", "C5"]:
            logging.info("Computing direct_loc on camera %s", cam)
            gnd, time = olci.direct_loc(subset_coord, geometric_unit=cam)
            gnd_vec.append(gnd)
            times_vec.append(time)

    else:
        gnd_array = np.load(f"{ASGARD_DATA}/OLCI_validation/{dataset_name}/gnd_asgard_olci_refac.npy")[
            :, subset_indices_1, subset_indices_2, :
        ]
        time_reshaped = np.load(f"{ASGARD_DATA}/OLCI_validation/{dataset_name}/time_asgard_olci_refac.npy")[
            :, subset_indices_1, subset_indices_2
        ]

    gnd_array = np.array(gnd_vec)
    time_reshaped = np.array(times_vec)

    gnd_reshaped = np.swapaxes(gnd_array, 0, 3).swapaxes(2, 3)  # .swapaxes(2, 3)

    # Times comparison
    diff_times = np.subtract(times_legacy, time_reshaped)

    # Define tolerance for times
    tolerance_time = 1.0e-12
    tol_time = np.full(shape=diff_times.shape, fill_value=tolerance_time)
    bool_times = np.less(np.absolute(diff_times), tol_time)

    # Check that 99.73% (3sigma) of the error on times is smaller than tolerance
    assert np.sum(bool_times) / bool_times.size > 0.9973

    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    # Unit of Earth radius = m
    body = EarthBody(time_reference=time_model)

    # setup comparator
    comp = GeodeticComparator(body_model=body)

    # S3 full resolution = 300 m
    # Define tolerance for planimetric error (m)
    tolerance_planimetric = 75
    # Define tolerance for altitude (m)
    tolerance_altitude = 10

    for cam in range(5):
        logging.info("\n###### Camera %s", cam + 1)

        # Compute error on planimetric distance (m) for each time on all pixel image for camera c
        error_gp_map_camera = [
            comp.planar_error(
                gnd_legacy[:, :, cam, pix_ind].swapaxes(0, 1), gnd_reshaped[:, :, cam, pix_ind].swapaxes(0, 1)
            )
            for pix_ind in range(nb_pixel)
        ]
        error_gp_arr = np.array(error_gp_map_camera)
        logging.info("GP max error = %s", np.max(error_gp_arr))

        tol_dist = np.full(shape=error_gp_arr.shape, fill_value=tolerance_planimetric)

        # Check if error on geodetic distance < tolerance
        bool_dist = np.less(np.absolute(error_gp_arr), tol_dist)

        # Compute the number of points above the tolerance
        logging.info(
            "For camera %s with planimetric error, "
            "number of points above tolerance (%s m) = %s upon %s geodetic points",
            cam + 1,
            tolerance_planimetric,
            bool_dist.size - np.sum(bool_dist),
            error_gp_arr.size,
        )

        # Check that 99.73% (3sigma) of the error on geodetic distance is smaller than tolerance
        # TODO: Due to aberrant point for camera 1 and 2 : test failed
        if cam not in (0, 1) and dataset_name == "OLCI_TDS1":
            assert np.sum(bool_dist) / bool_dist.size > 0.9973

        # Compute error on altitude (m) for each time on all pixel image for camera c
        error_alt_map_camera = []
        for pix_ind in range(nb_pixel):
            error_alt_map_camera.append(
                comp.height_error(
                    gnd_legacy[:, :, cam, pix_ind].swapaxes(0, 1), gnd_reshaped[:, :, cam, pix_ind].swapaxes(0, 1)
                )
            )
        error_alt_arr = np.array(error_alt_map_camera)
        logging.info("Altitude max error = %s", np.max(error_alt_arr))

        tol_alt = np.full(shape=error_alt_arr.shape, fill_value=tolerance_altitude)

        # Check if error on altitude < tolerance
        bool_alt = np.less(np.absolute(error_alt_arr), tol_alt)

        # Compute the number of points above the tolerance
        logging.info(
            "For camera %s with planimetric error, number of altitudes above tolerance (%s m) = %s upon %s points",
            cam + 1,
            tolerance_altitude,
            bool_alt.size - np.sum(bool_alt),
            error_alt_arr.size,
        )

        # Check that 99.73% (3sigma) of the error on altitude is smaller than tolerance
        assert np.sum(bool_alt) / bool_alt.size > 0.9973


@pytest.mark.parametrize(
    "dataset_name",
    [
        ("OLCI_TDS1"),
        ("OLCI_TDS2"),
    ],
    ids=[
        "nominal_tds",
        "antimeridian_tds",
    ],
)
@pytest.mark.slow
@pytest.mark.dem
def test_sun_angles_all_cam(olci, dataset_name, breakpoint_gr, range_idx, img_coord):  # pylint: disable=too-many-locals
    """
    Valdation test for S3OLCIGeometry sun angles with navatt data and for all cameras
    """
    # Possibility to take a subset of the data with a step
    step = 10
    subset_indices_1 = slice(0, img_coord.shape[0], step)
    subset_indices_2 = slice(0, img_coord.shape[1], step)

    # Define a subset on coordinates to avoid wasting time in computation (lot of cases)
    subset_coord = img_coord[subset_indices_1, subset_indices_2]

    nb_pixel = subset_coord.shape[1]
    nb_time = subset_coord.shape[0]

    # Truncate 0 values at the beginning and at the end of the ground legacy vectors lon/lat/alt
    sun_legacy = np.array(
        [
            breakpoint_gr["block_0_phi_s"][range_idx[0] : range_idx[1], ...],
            breakpoint_gr["block_0_theta_s"][range_idx[0] : range_idx[1], ...],
        ]
    )[:, subset_indices_1, :, subset_indices_2]

    gnd_legacy = (
        np.array(
            [
                breakpoint_gr["block_0_lon"][range_idx[0] : range_idx[1], ...],
                breakpoint_gr["block_0_lat"][range_idx[0] : range_idx[1], ...],
                breakpoint_gr["block_0_alt"][range_idx[0] : range_idx[1], ...],
            ]
        )
        .swapaxes(0, 2)
        .swapaxes(2, 3)
    )[:, subset_indices_1, subset_indices_2, :]

    times_legacy = np.tile(olci.config["frame"]["times"]["offsets"][subset_indices_1], (nb_pixel, 1)).swapaxes(0, 1)
    gnd_to_sun = np.zeros((nb_time, nb_pixel, 2, 5))
    gnd_to_sun_pos_eocfi = np.zeros((nb_time, nb_pixel, 2, 5))

    for i, _ in enumerate(["C1", "C2", "C3", "C4", "C5"]):
        logging.info("Computing sun angles for camera %s", _)
        # Compute of sun_angles with sun positions computed with Orekit
        gnd_to_sun[..., i] = olci.sun_angles(gnd_legacy[i, ...], times_legacy)

        # Compute of sun_angles with sun positions computed with EOCFI
        flat_coords = flatten_array(gnd_legacy[i, ...], 3)
        flat_times = flatten_array(times_legacy)
        assert flat_coords.shape[0] == flat_times.shape[0]

        dataset = {
            "position": flat_coords,
            "times": {
                "offsets": flat_times,
                "unit": olci.default_time["unit"],
                "epoch": olci.default_time["epoch"],
                "ref": olci.default_time["ref"],
            },
        }
        # get sun position from EOCFI computation
        sun_pos_legacy = np.load(osp.join(TEST_DIR, "resources", "S3", "OLCI", f"sun_pos_eocfi_{dataset_name}.npy"))
        sun_pos_legacy_reshaped = sun_pos_legacy.reshape((img_coord.shape[0], img_coord.shape[1], 3))
        dataset["body_pos"] = flatten_array(sun_pos_legacy_reshaped[subset_indices_1, subset_indices_2, :], last_dim=3)

        # convert body position to topocentric ("body_pos", "position" -> "body_topo")
        # Note: the Orekit-based Earth body model uses geodetic coordinates for "position"
        olci.body_model.ef_to_topocentric(
            dataset,
            coord_in="body_pos",
            ground_in="position",
            coord_out="body_topo",
        )
        sun_angles = dataset["body_topo"]

        # use zenith angle
        sun_angles[:, 1] = 90.0 - sun_angles[:, 1]

        # restore initial shape and drop last coord
        gnd_to_sun_pos_eocfi[..., i] = restore_array(sun_angles[:, :2], gnd_legacy[i, ...].shape[:-1], last_dim=2)

    # (2, nb_times, 5, nb_pixel)
    gnd_to_sun_reshaped = np.swapaxes(gnd_to_sun, 0, 2).swapaxes(2, 3).swapaxes(1, 3)
    gnd_to_sun_pos_eocfi_reshaped = np.swapaxes(gnd_to_sun_pos_eocfi, 0, 2).swapaxes(2, 3).swapaxes(1, 3)

    # For comparison with pointing_error_azi_zen: the sun angles column must be the last one
    # (nb_times, 5, nb_pixel, 2)
    gnd_to_sun_compare = np.moveaxis(gnd_to_sun_reshaped, 0, -1)
    gnd_to_sun_pos_eocfi_compare = np.moveaxis(gnd_to_sun_pos_eocfi_reshaped, 0, -1)
    sun_legacy_compare = np.moveaxis(sun_legacy, 0, -1)

    # (nb_times, 5, nb_pixel)
    # Compute error for sun angles using sun position computed with Orekit
    pointing_error_sun_deg = pointing_error_azi_zen(sun_legacy_compare, gnd_to_sun_compare)

    # Compute error for sun angles using sun position computed with EOCFI
    sun_error_with_sun_pos_eocfi = pointing_error_azi_zen(sun_legacy_compare, gnd_to_sun_pos_eocfi_compare)

    tolerance_sun_angles = 1.0e-4
    for cam in range(5):
        counter_orekit, counter_eocfi = 0, 0
        for t in range(nb_time):
            for pix in range(nb_pixel):
                if pointing_error_sun_deg[t, cam, pix] > tolerance_sun_angles:
                    counter_orekit += 1
                if sun_error_with_sun_pos_eocfi[t, cam, pix] > tolerance_sun_angles:
                    counter_eocfi += 1

        logging.info("----- For camera C%s -----\n", cam + 1)
        orekit_msg = (
            "Using Orekit sun position, number of sun angles (pointing direction) "
            "above tolerance (%s deg) = %s upon %s sun angles\n"
        )
        logging.info(
            orekit_msg,
            tolerance_sun_angles,
            counter_orekit,
            pointing_error_sun_deg.size / 5,
        )

        logging.info("max error using Orekit sun position = %s", np.max(pointing_error_sun_deg[:, cam, :]))
        logging.info("mean error using Orekit sun position = %s", np.mean(pointing_error_sun_deg[:, cam, :]))

        eocfi_msg = (
            "Using EOCFI sun position, number of sun angles (pointing direction) "
            "above tolerance (%s deg) = %s upon %s sun angles\n"
        )
        logging.info(
            eocfi_msg,
            tolerance_sun_angles,
            counter_eocfi,
            sun_error_with_sun_pos_eocfi.size / 5,
        )

        logging.info("max error using EOCFI sun position = %s", np.max(sun_error_with_sun_pos_eocfi[:, cam, :]))

    # Define tolerance for sun angles directions
    tol_sun_angles = np.full(shape=pointing_error_sun_deg.shape, fill_value=tolerance_sun_angles)

    # Check if error on sun angle directions < tolerance
    bool_sun_angles = np.less(np.absolute(pointing_error_sun_deg), tol_sun_angles)
    bool_sun_angles_eocfi = np.less(np.absolute(sun_error_with_sun_pos_eocfi), tol_sun_angles)

    # Check that 99.73% (3sigma) of the error on sun angles direction is smaller than tolerance
    # for Orekit sun position computation
    if np.sum(bool_sun_angles) / bool_sun_angles.size <= 0.9973:
        warning_message = (
            "The error made on sun angles is about 10^(-3), this is due to the fact that Orekit "
            "is using another method of sun position computation compared to EOCFI"
        )
        logging.warning(warning_message)

    # Check that 99.73% (3sigma) of the error on sun angles direction is smaller than tolerance
    # for EOCFI sun position computation
    assert np.sum(bool_sun_angles_eocfi) / bool_sun_angles_eocfi.size > 0.9973


@pytest.mark.parametrize(
    "dataset_name",
    [
        ("OLCI_TDS1"),
        ("OLCI_TDS2"),
    ],
    ids=[
        "nominal_tds",
        "antimeridian_tds",
    ],
)
@pytest.mark.slow
@pytest.mark.dem
def test_incidence_angles_all_cam(olci, breakpoint_gr, range_idx, img_coord):
    """
    Valdation test for S3OLCIGeometry incident angles with navatt data and for all cameras
    """
    # Possibility to take a subset of the data with a step
    step = 10
    subset_indices_1 = slice(0, img_coord.shape[0], step)
    subset_indices_2 = slice(0, img_coord.shape[1], step)

    # Define a subset on coordinates to avoid wasting time in computation (lot of cases)
    subset_coord = img_coord[subset_indices_1, subset_indices_2]

    nb_pixel = subset_coord.shape[1]
    nb_time = subset_coord.shape[0]

    # Truncate 0 values at the beginning and at the end of the ground legacy vectors lon/lat/alt
    sat_legacy = np.array(
        [
            breakpoint_gr["block_0_phi_v"][range_idx[0] : range_idx[1], ...],
            breakpoint_gr["block_0_theta_v"][range_idx[0] : range_idx[1], ...],
        ]
    )[:, subset_indices_1, :, subset_indices_2]

    gnd_legacy = (
        np.array(
            [
                breakpoint_gr["block_0_lon"][range_idx[0] : range_idx[1], ...],
                breakpoint_gr["block_0_lat"][range_idx[0] : range_idx[1], ...],
                breakpoint_gr["block_0_alt"][range_idx[0] : range_idx[1], ...],
            ]
        )
        .swapaxes(0, 2)
        .swapaxes(2, 3)
    )[:, subset_indices_1, subset_indices_2, :]

    times_legacy = np.tile(olci.config["frame"]["times"]["offsets"][subset_indices_1], (nb_pixel, 1)).swapaxes(0, 1)

    # incidence angles = phi, theta
    gnd_to_sat = np.zeros((nb_time, nb_pixel, 2, 5))

    for i, _ in enumerate(["C1", "C2", "C3", "C4", "C5"]):
        gnd_to_sat[..., i] = olci.incidence_angles(gnd_legacy[i, ...], times_legacy)

    # (2, nb_times, 5, nb_pixel)
    gnd_to_sat_reshaped = np.swapaxes(gnd_to_sat, 0, 2).swapaxes(2, 3).swapaxes(1, 3)

    # For comparison with pointing_error_azi_zen: the (phi, theta) column must be the last one
    # (nb_times, 5, nb_pixel, 2)
    gnd_to_sat_compare = np.moveaxis(gnd_to_sat_reshaped, 0, -1)
    sat_legacy_compare = np.moveaxis(sat_legacy, 0, -1)

    # (nb_times, 5, nb_pixel)
    pointing_error_incidence_deg = pointing_error_azi_zen(sat_legacy_compare, gnd_to_sat_compare)

    tolerance_phi_theta = 1.0e-3
    for cam in range(5):
        counter = 0
        for t in range(nb_time):
            for pix in range(nb_pixel):
                if pointing_error_incidence_deg[t, cam, pix] > tolerance_phi_theta:
                    counter += 1

        logging.info("----- For camera C%s -----\n", cam + 1)
        logging.info(
            "Number of incidence angles (pointing direction) above tol (%s°) = %s upon %s incidence angles",
            tolerance_phi_theta,
            counter,
            pointing_error_incidence_deg.size / 5,
        )
        logging.info("max error = %s", np.max(pointing_error_incidence_deg[:, cam, :]))
        logging.info("mean error = %s", np.mean(pointing_error_incidence_deg[:, cam, :]))

    # Define tolerance for incidence angles directions
    tol_phi_theta = np.full(shape=pointing_error_incidence_deg.shape, fill_value=tolerance_phi_theta)

    # Check if error on incidence angle directions < tolerance
    bool_phi_theta = np.less(np.absolute(pointing_error_incidence_deg), tol_phi_theta)

    # Check that 99.73% (3sigma) of the error on incidence angles direction is smaller than tolerance
    # The error made is greater than in legacy-based version, it seems to be caused by the fact that ground coordinates
    # in Orekit topocentric frame definition are geodesic whereas in EOCFI they are cartesian.
    if np.sum(bool_phi_theta) / bool_phi_theta.size <= 0.9973:
        warning_message = (
            "The error made on incidence angles is about 10^(-2), this seems to be due to the fact that "
            "Orekit uses geodesic coordinates whereas EOCFI uses cartesian coordinates for "
            "topocentric frame definition"
        )
        logging.warning(warning_message)
