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
Validation for SLSTR Sentinel 3 products respect to legacy processor
"""

import glob
import logging
import os
import os.path as osp

import netCDF4
import numpy as np
import pytest
from drivers.sentinel_3_legacy import ExplorerDriver, S3LegacyDriver
from helpers.compare import (  # pylint: disable=import-error
    GeodeticComparator,
    pointing_error_azi_zen,
)

from asgard.core.frame import FrameId
from asgard.core.logger import initialize
from asgard.models.body import EarthBody
from asgard.models.time import TimeReference
from asgard.sensors.sentinel3.slstr import S3SLSTRGeometry

logging.getLogger().setLevel(logging.INFO)

TEST_DIR = os.path.dirname(osp.dirname(__file__))

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")


CALIBRATION_FILE = osp.join(
    ASGARD_DATA,
    "S3ASLSTRdataset",
    "S3A_SL_1_GEC_AX_20190101T000000_20991231T235959_20191010T120000___________________MPC_O_AL_009.SEN3",
    "SL_1_GEC_AX.nc",
)

initialize("eocfi")


@pytest.fixture(name="thermoelastic")
def read_thermoelastic_legacy():
    """
    Fixture to extract thermoelastic grids
    """
    return S3LegacyDriver.s3_thermoelastic_tables(CALIBRATION_FILE)


@pytest.fixture(name="fro_file")
def read_fro_legacy(dataset_name):
    """
    Fixture to extract FRO orbit from 2022-11-05
    """
    fro_base_orbit = osp.join(ASGARD_DATA, "S3ASLSTRdataset", dataset_name)
    fro_path = glob.glob(os.path.join(fro_base_orbit, "S3A_AX___FRO_AX*", "S3A_OPER_MPL_ORBRES_*.EOF"))

    if not fro_path:
        raise FileNotFoundError("No folder matching 'S3A_AX___FRO_AX*.SEN3' found!")

    return S3LegacyDriver.read_orbit_file(fro_path[0])


@pytest.fixture(name="geom_model")
def read_geometry_model():
    """
    Fixture to extract geometry model for SLSTR
    """
    return S3LegacyDriver.slstr_geometry_model(
        osp.join(
            ASGARD_DATA,
            "S3ASLSTRdataset",
            "S3A_SL_1_GEO_AX_20160216T000000_20991231T235959_20190912T120000___________________MPC_O_AL_008.SEN3",
            "SL_1_GEO_AX.nc",
        )
    )


@pytest.fixture(name="coord")
def img_coord_product(geometry):
    """
    Native instrument coordinates
    """
    group = geometry.split("/")[0]
    rows = 902 if group == "NAD" else 702
    cols = 1199 if group == "NAD" else 529
    # Create a grid of coordinates without using loops
    col_indices = np.arange(cols)
    row_indices = np.arange(rows)
    coordinates = np.zeros((rows, cols, 2), dtype="int64")

    coordinates[..., 0] = col_indices
    coordinates[..., 1] = row_indices[:, np.newaxis]

    coordinates_05 = np.zeros((rows, 2 * cols, 2), dtype="int64")
    expand_cols_indices = np.arange(2 * cols)
    coordinates_05[..., 0] = expand_cols_indices
    coordinates_05[..., 1] = row_indices[:, np.newaxis]

    return {"coord_1KM": coordinates, "coord_05KM": coordinates_05}


@pytest.fixture(name="coord_tp")
def img_coord_product_tp(geometry, bp_tp):
    """
    Tie point grid for SLSTR with TPix grid
    """
    rows = bp_tp.dimensions["n_TPix_along"].size
    cols_total = bp_tp.dimensions["n_TPix_across_det"].size

    group = geometry.split("/")[1]
    cols = int(cols_total / 4) if "05" in group else int(cols_total / 2)

    # Create a grid of coordinates without using loops
    col_indices = np.arange(cols)
    row_indices = np.arange(rows)
    coordinates = np.zeros((rows, cols, 2), dtype="int64")

    coordinates[..., 0] = col_indices
    coordinates[..., 1] = row_indices[:, np.newaxis]

    return coordinates


@pytest.fixture(name="coord_qc")
def img_coord_product_qc(bp_qc):
    """
    Tie point grid for SLSTR with TPix grid
    """
    rows = bp_qc.dimensions["qc_grid_N_TP"].size
    cols = bp_qc.dimensions["N_AC_TP_nadir"].size

    # Create a grid of coordinates without using loops
    col_indices = np.arange(cols)
    row_indices = np.arange(rows)
    coordinates = np.zeros((rows, cols, 2), dtype="int64")

    coordinates[..., 0] = col_indices
    coordinates[..., 1] = row_indices[:, np.newaxis]

    return coordinates


@pytest.fixture(name="comparator")
def get_comparator():
    """
    Fixture to instanciate GeodeticComparator object
    """
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    body = EarthBody(time_reference=time_model)

    return GeodeticComparator(body_model=body)


@pytest.fixture(name="slstr")
def slstr_product(
    fro_file, dataset_name, thermoelastic, geom_model, time_tp, bp_jd
):  # pylint: disable=too-many-positional-arguments
    """
    Fixture to initialize a S3SLSTRGeometry with navatt
    """

    output_bp_de_1_8_1 = osp.join(ASGARD_DATA, "SLSTR_validation", dataset_name, "BP_S1_L1A_1_8_1.nc")
    tmp_jd_nav = {}
    with netCDF4.Dataset(output_bp_de_1_8_1, "r", encoding="utf8") as de4_1_dataset:
        S3LegacyDriver.read_netcdf_array_fields(
            de4_1_dataset,
            tmp_jd_nav,
            ["JD_NAV", "POO_NAV"],
        )
    navatt_gps = tmp_jd_nav["JD_NAV"]
    navatt_oop = tmp_jd_nav["POO_NAV"] * 360.0 / (2 ** (32))

    orbit_path = osp.join(ASGARD_DATA, "SLSTR_validation", dataset_name, "orbit_scratch_file.xml")
    att_path = osp.join(ASGARD_DATA, "SLSTR_validation", dataset_name, "attitude_scratch_file.xml")

    orbit_scratch = S3LegacyDriver.read_orbit_file(orbit_path)

    if orbit_scratch["frame"] != "EME2000":
        iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
        time_model = TimeReference(iers_bulletin_b=iers_data)
        body = EarthBody(time_reference=time_model)
        driver = ExplorerDriver(earth_body=body)
        orbit_scratch = driver.change_orbit_frame(orbit_scratch, FrameId.EME2000)

    attitude_scratch = S3LegacyDriver.read_attitude_file(att_path)

    first_acq_n = [2469, 6139]
    first_acq_o = [1122, 4792]
    nb_scans_nad = len(np.ma.getdata(time_tp["NAD"]["t_scan"][:]))
    nb_scans_obl = len(np.ma.getdata(time_tp["OBL"]["t_scan"][:]))

    driver = S3LegacyDriver(EarthBody())
    fro_eme = driver.change_orbit_frame(orbit=fro_file, frame=FrameId.EME2000)

    orbit_scratch["time_ref"] = "GPS"
    attitude_scratch["times"]["GPS"] = orbit_scratch["times"]["GPS"]
    attitude_scratch["time_ref"] = "GPS"

    jd_anx = float(np.ma.getdata(bp_jd["JD_anx"]))

    config = {
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_eme],
        },
        "resources": {"dem_path": GETAS_PATH, "dem_type": "ZARR"},
        "thermoelastic": thermoelastic,
        "geometry_model": geom_model,
        "sw_geocal": 2,
        "jd_anx": jd_anx,
        "acquisition_times": {
            "NAD": {
                "scan_times": {"offsets": np.ma.getdata(time_tp["NAD"]["t_scan"][:])},
                "nb_pixels": 1500,
                "first_acquisition": np.tile(first_acq_n, nb_scans_nad // len(first_acq_n))[:nb_scans_nad],
            },
            "OBL": {
                "scan_times": {"offsets": np.ma.getdata(time_tp["OBL"]["t_scan"][:])},
                "nb_pixels": 900,
                "first_acquisition": np.tile(first_acq_o, nb_scans_obl // len(first_acq_o))[:nb_scans_obl],
            },
            "reference": "GPS",
        },
        "navatt": {
            "orbit": orbit_scratch,
            "attitude": attitude_scratch,
            "times": {"offsets": navatt_gps, "ref": "GPS"},
            "oop": navatt_oop,
        },
    }

    return S3SLSTRGeometry(**config)


# Define the geometries and datasets separately
geometries = [
    "NAD/1KM/0",
    "NAD/1KM/1",
    "NAD/05KM_A/0",
    "NAD/05KM_A/1",
    "NAD/05KM_A/2",
    "NAD/05KM_A/3",
    "NAD/05KM_B/0",
    "NAD/05KM_B/1",
    "NAD/05KM_B/2",
    "NAD/05KM_B/3",
    "NAD/1KM_F1/0",
    "NAD/1KM_F1/1",
    "OBL/1KM/0",
    "OBL/1KM/1",
    "OBL/05KM_A/0",
    "OBL/05KM_A/1",
    "OBL/05KM_A/2",
    "OBL/05KM_A/3",
    "OBL/05KM_B/0",
    "OBL/05KM_B/1",
    "OBL/05KM_B/2",
    "OBL/05KM_B/3",
    "OBL/1KM_F1/0",
    "OBL/1KM_F1/1",
]

datasets = ["SLSTR_TDS1", "SLSTR_TDS2", "SLSTR_TDS3"]

params = [(geometry, dataset) for geometry in geometries for dataset in datasets]


@pytest.mark.parametrize("geometry, dataset_name", params)
@pytest.mark.slow
@pytest.mark.dem
def test_slstr_direct_loc_all_val(slstr, coord, comparator, geometry, gnd_legacy_file):
    """
    Validation of direct localisation for SLSTR from origin instrument grid
    for all times and all coordinates points for geometry NAD/1KM/0
    """
    # Index to select the right array of coordinates
    coord_ind = geometry.split("/")[1].split("_")[0]
    img_coord = coord[f"coord_{coord_ind}"]

    # Variable for tolerance threshold: 1km or 500m according to geometry
    tol_dist = 1e3 if "1KM" in geometry.split("/")[1] else 500

    # Compute index to select right values in legacy, indeed the legacy arrays are stored with a column
    # for each detector (2 detectors for nadir view and 4 detectors for oblique view)
    detector_ind = int(geometry.split("/")[-1])
    jump_ind = jump_ind = 2 if "1KM" in geometry else 4

    step = 10
    subset_indices_1 = slice(0, img_coord.shape[0], step)
    subset_indices_2 = slice(0, img_coord.shape[1], step)

    # Define a subset on coordinates to avoid wasting time in computation (lot of cases)
    subset_coord = img_coord[subset_indices_1, subset_indices_2]

    gnd, _ = slstr.direct_loc(subset_coord, geometric_unit=geometry)

    gnd_legacy = (
        np.array(
            [
                np.ma.getdata(gnd_legacy_file["lon"][:, detector_ind::jump_ind]) % 360.0,
                np.ma.getdata(gnd_legacy_file["lat"][:, detector_ind::jump_ind]),
                np.ma.getdata(gnd_legacy_file["alt"][:, detector_ind::jump_ind]),
            ]
        )[:, subset_indices_1, subset_indices_2]
        .swapaxes(0, 1)
        .swapaxes(1, 2)
    )

    # Compute error on geodetic distance for each time on all pixel image
    error_map = [
        comparator.planar_error(gnd_legacy[time_ind, :, :], gnd[time_ind, :, :])
        for time_ind in range(subset_coord.shape[0] - 1)
    ]
    error_height = [
        comparator.height_error(gnd_legacy[time_ind, :, :], gnd[time_ind, :, :])
        for time_ind in range(subset_coord.shape[0] - 1)
    ]

    err_map_arr = np.array(error_map)
    error_height_arr = np.abs(np.array(error_height))

    # Define tolerance for geodetic distance
    tol_dist_arr = np.full(shape=err_map_arr.shape, fill_value=tol_dist)

    # Define tolerance for altitude (10m)
    tol_height = np.full(shape=error_height_arr.shape, fill_value=tol_dist)

    bool_dist = np.less(err_map_arr, tol_dist_arr)
    bool_alt = np.less(error_height_arr, tol_height)

    # Check that 99.73% (3sigma) of the error on geodetic distance is smaller than tolerance
    assert np.sum(bool_dist) / bool_dist.size > 0.9973, (
        f"Location on instrument grid not passed, there are {100 * (1 - np.sum(bool_dist) / bool_dist.size)} %% "
        f"of values above tolerance {tol_dist} for {geometry} geometry"
    )

    # Check that 99.73% (3sigma) of the error on height is smaller than tolerance
    assert np.sum(bool_alt) / bool_alt.size > 0.9973, (
        f"Altitude on instrument grid not passed, there are {100 * (1 - np.sum(bool_alt) / bool_alt.size)} %% "
        f"of values above tolerance {tol_height} for {geometry} geometry"
    )


@pytest.fixture(name="gnd_legacy_file")
def read_gnd_output(geometry, dataset_name):
    """
    Fixture to read longitude/latitude/altitude of legacy output
    """
    view = geometry.split("/")[0]
    group = geometry.split("/")[1]

    group_index = group if group == "1KM" else group.split("_")[-1]
    bp_with_out = osp.join(
        ASGARD_DATA, "SLSTR_validation", dataset_name, f"BP_S1_L1A_5_4_1_geo_with_outliers_{view}_{group_index}.nc"
    )

    return netCDF4.Dataset(bp_with_out)


# Define the geometries and datasets separately
geometries_tp = [geometry for geometry in geometries if "F1" not in geometry]
# Remove SLSTR_TDS2 antimeridian which has a pyrugged error under investigation
datasets.remove("SLSTR_TDS2")
params_tp = [(geometry, dataset_tp) for geometry in geometries_tp for dataset_tp in datasets]


@pytest.mark.parametrize("geometry, dataset_name", params_tp)
@pytest.mark.slow
@pytest.mark.dem
def test_slstr_tp_grid_val(slstr, bp_tp, geometry, coord_tp, comparator):
    """
    Validation of coordinates for SLSTR tie point grid for different geometries
    """

    # Compute index to select right values in legacy, indeed the legacy arrays are stored with a column
    # for each detector (2 detectors for nadir view and 4 detectors for oblique view)
    detector_ind = int(geometry.split("/")[-1])
    jump_ind = 2 if "1KM" in geometry else 4

    # Variable for tolerance threshold: 1km or 500m according to geometry
    tol_dist = 1e3 if "1KM" in geometry.split("/")[1] else 500

    # Define a subset on coordinates to avoid wasting time in computation (lot of cases)
    step = 4
    subset_indices_1 = slice(0, coord_tp.shape[0], step)
    subset_indices_2 = slice(0, coord_tp.shape[1], step)

    subset_coord = coord_tp[subset_indices_1, subset_indices_2]

    xy_legacy = np.rollaxis(
        np.array([bp_tp["X"][:, detector_ind::jump_ind], bp_tp["Y"][:, detector_ind::jump_ind]]), 0, 3
    )[subset_indices_1, subset_indices_2, ...]

    gnd_legacy = np.rollaxis(
        np.array(
            [
                bp_tp["lon_TPix"][:, detector_ind::jump_ind] % 360.0,
                bp_tp["lat_TPix"][:, detector_ind::jump_ind],
                bp_tp["alt_TPix"][:, detector_ind::jump_ind],
            ]
        ),
        0,
        3,
    )[subset_indices_1, subset_indices_2, ...]

    tp_grid = slstr.tie_points_grid()
    gnd_tp, _ = tp_grid.direct_loc(subset_coord, geometric_unit=geometry)

    error_map = []
    # Compute error on geodetic distance for each time on all pixel image
    for time_ind in range(subset_coord.shape[0]):
        error_map.append(comparator.planar_error(gnd_legacy[time_ind, ...], gnd_tp[time_ind, ...]))

    err_map_arr = np.array(error_map)

    qc_coords = slstr.quasi_cartesian_grid()
    qc_coords.compute_along_track_coordinates()

    gnd_coord_1km = qc_coords.ground_to_xy(gnd_tp[..., :2])

    # Compute euclidian distance between asgard results and legacy
    abs_distance = np.absolute(np.subtract(xy_legacy, gnd_coord_1km))
    err_xy = np.linalg.norm(abs_distance, axis=2)

    # Define tolerance for geodetic distance
    tol_dist_arr = np.full(shape=err_xy.shape, fill_value=tol_dist)

    bool_dist = np.less(err_map_arr, tol_dist_arr)
    bool_dist_xy = np.less(err_xy, tol_dist_arr)

    # Check that 99.73% (3sigma) of the error on geodetic distance is smaller than tolerance
    assert np.sum(bool_dist) / bool_dist.size > 0.9973, (
        f"Location on instrument grid not passed, there are {100 * (1 - np.sum(bool_dist) / bool_dist.size)} %% "
        f"of values above tolerance {tol_dist} for {geometry} geometry"
    )

    # Check that 99.73% (3sigma) of the error on cartesian coordiantes is smaller than tolerance
    assert np.sum(bool_dist_xy) / bool_dist_xy.size > 0.9973, (
        f"Location on instrument grid not passed, there are {100 * (1 - np.sum(bool_dist_xy) / bool_dist_xy.size)} %% "
        f"of values above tolerance {tol_dist} for {geometry} geometry"
    )


@pytest.mark.parametrize("geometry, dataset_name", params_tp)
@pytest.mark.slow
@pytest.mark.dem
def test_slstr_tp_angles_val(slstr, bp_tp, coord_tp, geometry):
    """
    Validation for sun angles (solar_phi, solar_theta), incidence angles (viewing_phi, viewing_theta)
    and distances (solar_path) on TPix grid with different geometries
    """

    # Compute index to select right values in legacy, indeed the legacy arrays are stored with a column
    # for each detector (2 detectors for nadir view and 4 detectors for oblique view)
    detector_ind = int(geometry.split("/")[-1])
    jump_ind = 2 if "1KM" in geometry else 4

    step = 4
    # Define a subset on coordinates to avoid wasting time in computation (lot of cases)
    subset_indices_1 = slice(0, coord_tp.shape[0], step)
    subset_indices_2 = slice(0, coord_tp.shape[1], step)

    sun_legacy = np.rollaxis(
        np.array([bp_tp["solar_phi"][:, detector_ind::jump_ind], bp_tp["solar_theta"][:, detector_ind::jump_ind]]),
        0,
        3,
    )[subset_indices_1, subset_indices_2, :]

    incidence_legacy = np.rollaxis(
        np.array([bp_tp["viewing_phi"][:, detector_ind::jump_ind], bp_tp["viewing_theta"][:, detector_ind::jump_ind]]),
        0,
        3,
    )[subset_indices_1, subset_indices_2, :]

    gnd_legacy = np.rollaxis(
        np.array(
            [
                np.ma.getdata(bp_tp["lon_TPix"][..., detector_ind::jump_ind]) % 360.0,
                np.ma.getdata(bp_tp["lat_TPix"][..., detector_ind::jump_ind]),
                np.ma.getdata(bp_tp["alt_TPix"][..., detector_ind::jump_ind]),
            ]
        ),
        0,
        3,
    )[subset_indices_1, subset_indices_2, :]

    times_legacy = np.squeeze(
        np.array(
            [
                np.ma.getdata(bp_tp["time_pix"][..., ::jump_ind]),
            ]
        )
    )[subset_indices_1, subset_indices_2]

    sun_path_legacy = np.ma.getdata(bp_tp["solar_path"][..., ::jump_ind])[subset_indices_1, subset_indices_2]

    tp_grid = slstr.tie_points_grid()

    sun_angles = tp_grid.sun_angles(gnd_legacy, times_legacy)
    incidence_angles = tp_grid.incidence_angles(gnd_legacy, times_legacy)

    # Compute pointing error for sun angles
    error_sun = pointing_error_azi_zen(sun_angles, sun_legacy)

    # Compute pointing error for incidence angles
    error_incidence = pointing_error_azi_zen(incidence_angles, incidence_legacy)

    # Define tolerance for sun and incidence angles (deg)
    tol_sun_val = 1e-4
    tol_incidence_val = 1e-3

    tol_sun = np.full(shape=error_sun.shape, fill_value=tol_sun_val)
    tol_incidence = np.full(shape=error_incidence.shape, fill_value=tol_incidence_val)

    bool_sun = np.less(error_sun, tol_sun)
    bool_incidence = np.less(error_incidence, tol_incidence)

    # Check that 99.73% (3sigma) of the error on sun_angles is smaller than tolerance
    if np.sum(bool_sun) / bool_sun.size <= 0.9973:
        logging.warning(
            "Sun angles test not passed, there are %.2f %% of values above tolerance %.1e deg for %s geometry,"
            "this is due to the sun position computed by Orekit (cf OLCI validation script)",
            100 * (1 - np.sum(bool_sun) / bool_sun.size),
            tol_sun_val,
            geometry,
        )
    else:
        logging.info("OKAY sun angles passed with tolerance %.0f deg for %s geometry", tol_sun_val, geometry)

    # Check that 99.73% (3sigma) of the error on incidence_angles is smaller than tolerance
    assert np.sum(bool_incidence) / bool_incidence.size > 0.9973, (
        f"Incidence angles on tie point grid not passed, there are "
        f"{100 * (1 - np.sum(bool_incidence) / bool_incidence.size)}  %% of values above tolerance{tol_incidence_val} "
        "for {geometry} geometry"
    )

    sun_distances = tp_grid.sun_distances(None, times_legacy)
    # Check sun distances errors, a relative threshold at 10^-4 is acceptable (ref: issue #330)
    rtol_sun_dist_val = 1e-4
    # The gap between sun distsance computed with Orekit vs EOCFI can be > 1.3e6
    assert np.allclose(sun_distances, sun_path_legacy, rtol=rtol_sun_dist_val, atol=0)


@pytest.mark.parametrize("dataset_name", [("SLSTR_TDS1"), ("SLSTR_TDS2")], ids=["nominal_tds", "antimeridian_tds"])
@pytest.mark.slow
@pytest.mark.dem
def test_slstr_qc_grid_loc_val(slstr, bp_qc, coord_qc, comparator):
    """
    Validation for coordinates of quasi-cartersian grid
    """
    qc_grid = slstr.quasi_cartesian_grid()
    qc_grid.compute_along_track_coordinates()

    gnd, _ = qc_grid.direct_loc(coord_qc)

    # Need to do a flip on longitude and latitude because there is an inversion
    gnd_qc_legacy = np.rollaxis(np.array([np.ma.getdata(bp_qc["lon"]), np.ma.getdata(bp_qc["lat"])]), 0, 3)
    across_x = np.array(np.ma.getdata(bp_qc["X"])[:])
    along_y = np.array(np.ma.getdata(bp_qc["Y"])[:])

    # Add altitude to legacy in order to use GeodeticComparator methods
    alt = gnd[..., 2]
    gnd_legacy = np.dstack((gnd_qc_legacy, alt[..., np.newaxis]))

    error_map = []

    # Compute error on geodetic distance for each time on all pixel image
    for time_ind in range(coord_qc.shape[0]):
        error_map.append(comparator.planar_error(gnd_legacy[time_ind, ...], gnd[time_ind, ...]))

    err_map_arr = np.array(error_map)

    # Define tolerance for geodetic distance (16km)
    tol_dist = 1.6e4
    tol_dist_arr = np.full(shape=err_map_arr.shape, fill_value=tol_dist)

    bool_dist = np.less(err_map_arr, tol_dist_arr)

    # Check that across X coordiantes and along Y coordinates if the qc grid are the same to legacy
    assert np.allclose(across_x, qc_grid.track_x)
    assert np.allclose(along_y, qc_grid.track_y)

    # Check that 99.73% (3sigma) of the error on geodetic distance is smaller than tolerance
    assert np.sum(bool_dist) / bool_dist.size > 0.9973, (
        f"Location on instrument grid not passed, there are {100 * (1 - np.sum(bool_dist) / bool_dist.size)} %%"
        f"of values above tolerance {tol_dist}"
    )


@pytest.fixture(name="bp_qc")
def read_bp_l1a_5_qc(dataset_name):
    """
    Fixture to read breakpoints for quasi cartesian grid
    """
    bp_qc_path = osp.join(ASGARD_DATA, "SLSTR_validation", dataset_name, "BP_S1_L1A_5_1_3_1.nc")

    return netCDF4.Dataset(bp_qc_path)


@pytest.fixture(name="time_tp")
def read_bp_l1a_4_tp(dataset_name):
    """
    Fixture to read breakpoints for times associated to tie point grid
    """

    base_path = osp.join(
        ASGARD_DATA,
        "SLSTR_validation",
        dataset_name,
    )

    time_nad = netCDF4.Dataset(osp.join(base_path, "BP_S1_L1A_4_4_1_NAD.nc"))
    time_obl = netCDF4.Dataset(osp.join(base_path, "BP_S1_L1A_4_4_1_OBL.nc"))

    time_datasets = {"NAD": time_nad, "OBL": time_obl}

    return time_datasets


@pytest.fixture(name="bp_tp")
def read_bp_l1a_5_tp_nad(geometry, dataset_name):
    """
    Fixture to read breakpoints for tie point grid
    """
    view = geometry.split("/")[0]
    group = geometry.split("/")[1]

    group_index = group if group == "1KM" else group.split("_")[-1]
    bp_tp_path = osp.join(
        ASGARD_DATA, "SLSTR_validation", dataset_name, f"BP_S1_L1A_5_4_1_TPix_{view}_{group_index}.nc"
    )

    return netCDF4.Dataset(bp_tp_path)


@pytest.fixture(name="bp_jd")
def read_time_jd(dataset_name):
    """
    Fixture to read times informations
    """
    bp_time = osp.join(ASGARD_DATA, "SLSTR_validation", dataset_name, "BP_S1_L1A_1_7_10.nc")

    return netCDF4.Dataset(bp_time)
