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
Unit tests for SLSTR Sentinel 3 products
"""
import os
import os.path as osp
import time

import numpy as np
import pytest
from drivers.explorer_legacy import ExplorerDriver
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import GeodeticComparator, pointing_error_azi_zen

from asgard.sensors.sentinel3 import S3SLSTRGeometry

TEST_DIR = osp.dirname(__file__)
SLSTR_DIR = osp.join(TEST_DIR, "resources/S3/SLSTR")

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")


@pytest.fixture(name="fro_20221030", scope="module")
def read_fro_20221030():
    """
    Fixture to extract FRO orbit from 2022-10-30
    """
    orbit_file = osp.join(
        TEST_DIR,
        "resources/S3/FRO",
        "orbit_fro_20221030_eme2000.EOF",
    )
    return S3LegacyDriver.read_orbit_file(orbit_file)


@pytest.fixture(name="thermoelastic", scope="module")
def read_thermoelastic():
    """
    Fixture to extract thermoelastic model for SLSTR
    """
    return S3LegacyDriver.s3_thermoelastic_tables(osp.join(SLSTR_DIR, "GEC/SL_1_GEC_AX.nc"))


@pytest.fixture(name="geom_model", scope="module")
def read_geometry_model():
    """
    Fixture to extract geometric model for SLSTR
    """
    return S3LegacyDriver.slstr_geometry_model(osp.join(SLSTR_DIR, "GEO/SL_1_GEO_AX.nc"))


@pytest.fixture(name="sample_time_array", scope="module")
def sample_time_array():
    """
    sample_time_array fixture
    """
    return np.array(
        [
            8340.86902955,
            8340.86903302,
            8340.86903649,
            8340.86903996,
            8340.86904344,
            8340.86904691,
            8340.86905038,
            8340.86905385,
            8340.86905732,
            8340.8690608,
            8340.86906427,
            8340.86906774,
            8340.86907121,
            8340.86907468,
            8340.86907816,
            8340.86908163,
            8340.8690851,
            8340.86908857,
            8340.86909204,
            8340.86909552,
            8340.86909899,
            8340.86910246,
            8340.86910593,
            8340.8691094,
            8340.86911288,
            8340.86911635,
            8340.86911982,
            8340.86912329,
            8340.86912676,
            8340.86913024,
            8340.86913371,
            8340.86913718,
            8340.86914065,
            8340.86914413,
            8340.8691476,
            8340.86915107,
            8340.86915454,
            8340.86915801,
            8340.86916149,
            8340.86916496,
            8340.86916843,
            8340.8691719,
            8340.86917537,
            8340.86917885,
            8340.86918232,
            8340.86918579,
            8340.86918926,
            8340.86919273,
            8340.86919621,
            8340.86919968,
        ],
        dtype="float64",
    )


@pytest.fixture(name="slstr", scope="module")
def slstr_product(fro_20221030, thermoelastic, geom_model, sample_time_array):
    """
    Test fixture to product a S3SLSTRGeometry with navatt
    """

    navatt_orbit = S3LegacyDriver.read_orbit_file(osp.join(SLSTR_DIR, "navatt/sample_orbit_eme2000.xml"))
    navatt_attitude = S3LegacyDriver.read_attitude_file(osp.join(SLSTR_DIR, "navatt/sample_attitude.xml"))
    navatt_times = np.load(osp.join(SLSTR_DIR, "navatt/sample_timestamps_gps.npy"))
    navatt_oop = np.load(osp.join(SLSTR_DIR, "navatt/sample_oop.npy"))

    nb_scan = len(sample_time_array)

    # We set a common time scale for orbit and attitude -> GPS
    navatt_orbit["time_ref"] = "GPS"
    navatt_attitude["times"]["GPS"] = navatt_orbit["times"]["GPS"]
    navatt_attitude["time_ref"] = "GPS"

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources/207_BULLETIN_B207.txt"))

    config = {
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20221030],
        },
        "resources": {"dem_path": GETAS_PATH, "dem_type": "ZARR"},
        "thermoelastic": thermoelastic,
        "geometry_model": geom_model,
        "sw_geocal": 3,
        "acquisition_times": {
            "NAD": {
                "scan_times": {"offsets": sample_time_array},
                "nb_pixels": 1500,
                "first_acquisition": [2200 for k in range(nb_scan)],
            },
            "OBL": {
                "scan_times": {"offsets": sample_time_array},
                "nb_pixels": 900,
                "first_acquisition": [1060 for k in range(nb_scan)],
            },
            "reference": "GPS",
        },
        "navatt": {
            "orbit": navatt_orbit,
            "attitude": navatt_attitude,
            "times": {"offsets": navatt_times, "ref": "GPS"},
            "oop": navatt_oop,
        },
        "eop": {
            "iers_bulletin_b": iers_data,
        },
    }

    return S3SLSTRGeometry(**config)


@pytest.mark.dem
def test_slstr_instruments(slstr):
    """
    Unit test to check instruments list
    """

    assert slstr is not None
    assert slstr.instruments == [
        "NAD/1KM/0",
        "NAD/1KM/1",
        "NAD/1KM_F1/0",
        "NAD/1KM_F1/1",
        "NAD/05KM_A/0",
        "NAD/05KM_A/1",
        "NAD/05KM_A/2",
        "NAD/05KM_A/3",
        "NAD/05KM_B/0",
        "NAD/05KM_B/1",
        "NAD/05KM_B/2",
        "NAD/05KM_B/3",
        "OBL/1KM/0",
        "OBL/1KM/1",
        "OBL/1KM_F1/0",
        "OBL/1KM_F1/1",
        "OBL/05KM_A/0",
        "OBL/05KM_A/1",
        "OBL/05KM_A/2",
        "OBL/05KM_A/3",
        "OBL/05KM_B/0",
        "OBL/05KM_B/1",
        "OBL/05KM_B/2",
        "OBL/05KM_B/3",
    ]

    assert slstr.coordinates["NAD/1KM/1"] == {"scan": 50, "pixel": 1500}
    assert slstr.coordinates["OBL/1KM/1"] == {"scan": 50, "pixel": 900}
    assert slstr.coordinates["NAD/05KM_A/1"] == {"scan": 50, "pixel": 3000}
    assert slstr.coordinates["OBL/05KM_A/1"] == {"scan": 50, "pixel": 1800}


@pytest.mark.dem
def test_slstr_subsample_scan_positions(slstr):
    """
    Unit test for S3SLSTRGeometry.subsample_scan_positions
    """

    # test for quasi_cartesian_grid
    scan_info = slstr.subsample_scan_positions()

    assert scan_info["start_pos"] == 0
    assert scan_info["track_n_tp"] == 120
    assert scan_info["NAD"]["tp_first_scan"] == 111
    assert np.allclose(scan_info["jd_anx"], 8340.86593)
    assert np.allclose(scan_info["delta_t_tp"], 2.7776e-05)

    assert scan_info["OBL"]["tp_first_scan"] == 61


@pytest.mark.dem
@pytest.mark.perfo
def test_slstr_quasi_cartesian_grid(slstr):
    """
    Unit test for S3SLSTRGeometry.quasi_cartesian_grid
    """

    qc_grid = slstr.quasi_cartesian_grid(
        ac_samples=130,
        ac_center_position=64,
        ac_resolution=16000.0,
        scan_per_tp=8,
        view="NAD",
    )

    # QC grid has 8 rows, but we simulate more by replication
    coordinates = np.zeros((100, 130, 2), dtype="int64")
    for row in range(100):
        for col in range(130):
            coordinates[row, col, 0] = col
            coordinates[row, col, 1] = row % 8

    tic = time.perf_counter()
    grid, _ = qc_grid.direct_loc(coordinates)
    tac = time.perf_counter()
    print(f"QC grid direct_loc speed: {coordinates.size * 0.5 / (tac-tic):.1f}")

    np.save(osp.join(TEST_DIR, "outputs/slstr/qc_grid.npy"), grid)

    # ~ from cProfile import Profile
    # ~ from pyprof2calltree import convert
    # ~ profiler = Profile()
    # ~ profiler.runctx('qc_grid.direct_loc(coordinates)', locals(), globals())
    # ~ convert(profiler.getstats(), osp.join(TEST_DIR, "outputs", "test_slstr_qc_grid_perf.kgrind"))


@pytest.mark.dem
def test_slstr_tie_point_grid(slstr):
    """
    Unit test for S3SLSTRGeometry.tie_points_grid
    """

    tp_grid = slstr.tie_points_grid()

    assert isinstance(tp_grid, S3SLSTRGeometry)


@pytest.mark.dem
def test_slstr_scan_angles(slstr):
    """
    Unit test for S3SLSTRGeometry.scan_angles
    """

    # Nadir view
    abs_pos = np.array([2200, 3699, 2700], dtype="int64")
    abs_pos_500m = np.array([4400, 7399, 5400], dtype="int64")

    angles_1km = slstr.pointing_model.scan_angles(abs_pos, view="NAD", group="1KM")
    angles_f1 = slstr.pointing_model.scan_angles(abs_pos, view="NAD", group="1KM_F1")
    angles_05km = slstr.pointing_model.scan_angles(abs_pos_500m, view="NAD", group="05KM_A")

    assert np.allclose(angles_1km, [169.85850108, 316.89937302, 218.90482261])
    assert np.allclose(angles_f1, [169.80945481, 316.85032674, 218.85577633])
    assert np.allclose(angles_05km, [169.83397792, 316.92389618, 218.88029945])

    # Oblique view
    abs_pos = np.array([1000, 1500, 2000], dtype="int64")
    abs_pos_500m = np.array([2000, 3000, 4000], dtype="int64")

    angles_1km = slstr.pointing_model.scan_angles(abs_pos, view="OBL", group="1KM")
    angles_f1 = slstr.pointing_model.scan_angles(abs_pos, view="OBL", group="1KM_F1")
    angles_05km = slstr.pointing_model.scan_angles(abs_pos_500m, view="OBL", group="05KM_A")

    assert np.allclose(angles_1km, [52.14745857, 101.19378009, 150.24010162])
    assert np.allclose(angles_f1, [52.09841229, 101.14473382, 150.19105534])
    assert np.allclose(angles_05km, [52.12293541, 101.16925693, 150.21557846])


@pytest.mark.dem
def test_slstr_acquisition_times(slstr):
    """
    Unit test for S3SLSTRGeometry.acquisition_times
    """

    scan_coordinate = np.array([0, 0, 40, 40, 49, 49], dtype="int64")
    abs_position_nad_1km = np.array([2200, 3699, 2700, 2701, 2700, 3699], dtype="int64")
    abs_position_obl_1km = np.array([1060, 1959, 1500, 1501, 1500, 1959], dtype="int64")
    abs_position_nad_05km = np.array([4400, 7399, 5400, 5401, 5400, 7399], dtype="int64")
    abs_position_obl_05km = np.array([2120, 3919, 3000, 3001, 3000, 3919], dtype="int64")

    coord_nad_1km = np.stack([abs_position_nad_1km - 2200, scan_coordinate], axis=1)
    coord_obl_1km = np.stack([abs_position_obl_1km - 1060, scan_coordinate], axis=1)
    coord_nad_05km = np.stack([abs_position_nad_05km - 4400, scan_coordinate], axis=1)
    coord_obl_05km = np.stack([abs_position_obl_05km - 2120, scan_coordinate], axis=1)

    dataset = {"coords": coord_nad_1km}
    slstr.timestamp_models["NAD/1KM/0"].acquisition_times(dataset)
    times_nad_1km = dataset["times"]["offsets"]
    assert np.allclose(abs_position_nad_1km, dataset["abs_pos"])

    dataset = {"coords": coord_obl_1km}
    slstr.timestamp_models["OBL/1KM/0"].acquisition_times(dataset)
    times_obl_1km = dataset["times"]["offsets"]
    assert np.allclose(abs_position_obl_1km, dataset["abs_pos"])

    dataset = {"coords": coord_nad_05km}
    slstr.timestamp_models["NAD/05KM_A/0"].acquisition_times(dataset)
    times_nad_05km = dataset["times"]["offsets"]
    assert np.allclose(abs_position_nad_05km, dataset["abs_pos"])

    dataset = {"coords": coord_obl_05km}
    slstr.timestamp_models["OBL/05KM_A/0"].acquisition_times(dataset)
    times_obl_05km = dataset["times"]["offsets"]
    assert np.allclose(abs_position_obl_05km, dataset["abs_pos"])

    assert np.allclose(
        times_nad_1km,
        [
            8340.86903163,
            8340.86903305,
            8340.86917098,
            8340.86917099,
            8340.86920223,
            8340.86920318,
        ],
    )
    assert np.allclose(
        times_obl_1km,
        [
            8340.86903055,
            8340.8690314,
            8340.86916985,
            8340.86916985,
            8340.8692011,
            8340.86920153,
        ],
    )
    assert np.allclose(
        times_nad_05km,
        [
            8340.86903163,
            8340.86903305,
            8340.86917098,
            8340.86917099,
            8340.86920223,
            8340.86920318,
        ],
    )
    assert np.allclose(
        times_obl_05km,
        [
            8340.86903055,
            8340.8690314,
            8340.86916985,
            8340.86916985,
            8340.8692011,
            8340.86920153,
        ],
    )


@pytest.mark.dem
def test_slstr_group_to_resolution(slstr):
    """
    Unit test for S3SLSTRGeometry.group_to_resolution
    """

    assert slstr.group_to_resolution("1KM") == 1000
    assert slstr.group_to_resolution("1KM_F1") == 1000
    assert slstr.group_to_resolution("05KM_A") == 500
    assert slstr.group_to_resolution("05KM_B") == 500


@pytest.fixture(name="img_coord_nad", scope="module")
def img_coord_product_nad():
    """
    Image coordinates for SLSTR
    """
    img_coords = np.zeros((2, 14, 2), dtype="int32")
    for row in range(2):
        for col in range(14):
            img_coords[row, col, 0] = 100 * col
            img_coords[row, col, 1] = 49 * row

    return img_coords


@pytest.fixture(name="img_coord_obl", scope="module")
def img_coord_product_obl():
    """
    Image coordinates for SLSTR
    """
    img_coords = np.zeros((2, 30, 2), dtype="int32")
    for row in range(2):
        for col in range(30):
            img_coords[row, col, 0] = 30 * col
            img_coords[row, col, 1] = 49 * row

    return img_coords


@pytest.mark.dem
def test_slstr_direct_loc(slstr, img_coord_nad, img_coord_obl):
    """
    Unit test for S3SLSTRGeometry.direct_loc
    """
    out_folder = osp.join(TEST_DIR, "outputs/slstr")
    os.makedirs(out_folder, exist_ok=True)

    gnd_nad, times_nad = slstr.direct_loc(img_coord_nad, geometric_unit="NAD/1KM/0")
    np.save(osp.join(out_folder, "sample_gnd_nad.npy"), gnd_nad)

    gnd_obl, _ = slstr.direct_loc(img_coord_obl, geometric_unit="OBL/1KM/0")
    np.save(osp.join(out_folder, "sample_gnd_obl.npy"), gnd_obl)

    img_05_nad = np.copy(img_coord_nad)
    img_05_obl = np.copy(img_coord_obl)

    img_05_nad[:, :, 0] *= 2
    img_05_obl[:, :, 0] *= 2

    gnd_05_nad, _ = slstr.direct_loc(img_05_nad, geometric_unit="NAD/05KM_A/0")
    np.save(osp.join(out_folder, "sample_gnd_05_nad.npy"), gnd_05_nad)

    gnd_05_obl, _ = slstr.direct_loc(img_05_obl, geometric_unit="OBL/05KM_A/0")
    np.save(osp.join(out_folder, "sample_gnd_05_obl.npy"), gnd_05_obl)

    # setup comparator
    comp = GeodeticComparator(slstr.propagation_model.body)

    # reference data for gnd_nad[0,1:,:2]
    ref_nad = np.array(
        [
            [30.16827808, 9.94869925],
            [26.12415475, 12.72098938],
            [23.66286566, 14.2591944],
            [21.82409983, 15.23621302],
            [20.32236552, 15.87749119],
            [19.0255004, 16.28933101],
            [17.86893841, 16.52951923],
            [16.81020845, 16.63173446],
            [15.82058954, 16.61528004],
            [14.87863972, 16.48968019],
            [13.96682647, 16.2567609],
            [13.06944512, 15.91097581],
            [12.17136667, 15.43881266],
        ]
    )
    assert np.all(np.isnan(gnd_nad[0, 0, :]))
    error_2d = comp.planar_error(gnd_nad[0, 1:, :], ref_nad)
    assert np.all(error_2d < 10000)  # threshold 10km for first two samples
    assert np.all(error_2d[2:] < 2500)  # threshold 2.5km for the other samples

    # reference data for gnd_obl[0,:10,:2]
    ref_obl = np.array(
        [
            [12.1042901, 7.83244711],
            [12.51514652, 7.70644964],
            [12.93246904, 7.60445713],
            [13.35376796, 7.52136087],
            [13.77833056, 7.45743392],
            [14.20551493, 7.41429711],
            [14.63430603, 7.39059952],
            [15.06384212, 7.39004763],
            [15.49292328, 7.41115933],
            [15.919988, 7.45761827],
        ]
    )
    error_2d = comp.planar_error(gnd_obl[0, :10, :], ref_obl)
    assert np.all(error_2d < 6000)  # threshold 6km for all samples

    # reference data for gnd_05_nad[1,1:,:2]
    ref_05_nad = np.array(
        [
            [30.06124573, 10.76587988],
            [25.98622345, 13.56547286],
            [23.51268206, 15.11314587],
            [21.66608399, 16.09511385],
            [20.15333774, 16.73959285],
            [18.84995211, 17.15323461],
            [17.68639764, 17.39432357],
            [16.62185203, 17.49693406],
            [15.62725661, 17.48059492],
            [14.68081544, 17.35485494],
            [13.76493579, 17.12158645],
            [12.86392832, 16.77525859],
            [11.96246558, 16.30235741],
        ]
    )
    assert np.all(np.isnan(gnd_05_nad[1, 0, :]))
    error_2d = comp.planar_error(gnd_05_nad[1, 1:, :], ref_05_nad)
    assert np.all(error_2d < 10000)  # threshold 10km for first two samples
    assert np.all(error_2d[2:] < 2500)  # threshold 2.5km for the other samples

    # reference data for gnd_05_obl[1,:10,:2]
    ref_05_obl = np.array(
        [
            [11.89864357, 8.69241323],
            [12.30994459, 8.56425043],
            [12.72711036, 8.45639425],
            [13.15151456, 8.38263811],
            [13.5759309, 8.30942361],
            [14.00454108, 8.26569137],
            [14.43488928, 8.24457588],
            [14.86573303, 8.24619803],
            [15.2959388, 8.26901616],
            [15.72484387, 8.31015574],
        ]
    )
    error_2d = comp.planar_error(gnd_05_obl[1, :10, :], ref_05_obl)
    assert np.all(error_2d < 6000)  # threshold 6km for all samples

    # check sun and incidence angles
    gnd_to_sun = slstr.sun_angles(gnd_nad[0, 1:, :], times_nad[0, 1:])
    assert np.all(pointing_error_azi_zen(gnd_to_sun[0, :], [248.40688744, 166.51005644]) < 0.1)

    # check sun distances
    gnd_to_sun_dist = slstr.sun_distances(gnd_nad[0, 1:, :], times_nad[0, 1:])
    assert np.allclose(
        [
            1.48477292e11,
            1.48477202e11,
            1.48477127e11,
            1.48477062e11,
            1.48477004e11,
            1.48476950e11,
            1.48476900e11,
            1.48476852e11,
            1.48476806e11,
            1.48476761e11,
            1.48476716e11,
            1.48476669e11,
            1.48476621e11,
        ],
        gnd_to_sun_dist,
        rtol=1e-4,
        atol=0,
    )

    gnd_to_sat = slstr.incidence_angles(gnd_nad[0, 1:, :], times_nad[0, 1:])
    assert np.all(pointing_error_azi_zen(gnd_to_sat[0, :], [292.80867007, 75.17075427]) < 0.2)


@pytest.fixture(scope="module")
def slstr_204936_config(fro_20221030, thermoelastic, geom_model):
    """
    Test fixture to produce a S3SLSTRGeometry configuration with navatt and encoder angles and frame times from
    S3A_SL_0_SLT____20221101T204936
    """

    navatt_orbit = S3LegacyDriver.read_orbit_file(osp.join(SLSTR_DIR, "navatt/sample_orbit_eme2000.xml"))
    navatt_attitude = S3LegacyDriver.read_attitude_file(osp.join(SLSTR_DIR, "navatt/sample_attitude.xml"))
    navatt_times = np.load(osp.join(SLSTR_DIR, "navatt/sample_timestamps_gps.npy"))
    navatt_oop = np.load(osp.join(SLSTR_DIR, "navatt/sample_oop.npy"))

    slt_dir = osp.join(SLSTR_DIR, "SLT_20221101T204936")
    first_scan = 300
    scan_timestamps = np.load(osp.join(slt_dir, "sample_frame_times.npy"))
    nad_first_acq = np.load(osp.join(slt_dir, "sample_nad_first_acq.npy"))
    nad_scan_angle_1km = np.load(osp.join(slt_dir, "sample_nad_scan_angle_1km.npy"))
    nad_scan_angle_05km = np.load(osp.join(slt_dir, "sample_nad_scan_angle_05km.npy"))
    obl_first_acq = np.load(osp.join(slt_dir, "sample_obl_first_acq.npy"))
    obl_scan_angle_1km = np.load(osp.join(slt_dir, "sample_obl_scan_angle_1km.npy"))
    obl_scan_angle_05km = np.load(osp.join(slt_dir, "sample_obl_scan_angle_05km.npy"))

    nb_pixels_nad = nad_scan_angle_1km.shape[1]
    nb_pixels_obl = obl_scan_angle_1km.shape[1]

    scan_time_array = scan_timestamps[first_scan:]

    # We set a common time scale for orbit and attitude -> GPS
    navatt_orbit["time_ref"] = "GPS"
    navatt_attitude["times"]["GPS"] = navatt_orbit["times"]["GPS"]
    navatt_attitude["time_ref"] = "GPS"

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources/207_BULLETIN_B207.txt"))

    config = {
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20221030],
        },
        "resources": {"dem_path": GETAS_PATH, "dem_type": "ZARR"},
        "thermoelastic": thermoelastic,
        "geometry_model": geom_model,
        "sw_geocal": 3,
        "acquisition_times": {
            "NAD": {
                "scan_times": {"offsets": scan_time_array},
                "nb_pixels": nb_pixels_nad,
                "first_acquisition": nad_first_acq[first_scan:],
            },
            "OBL": {
                "scan_times": {"offsets": scan_time_array},
                "nb_pixels": nb_pixels_obl,
                "first_acquisition": obl_first_acq[first_scan:],
            },
        },
        "navatt": {
            "orbit": navatt_orbit,
            "attitude": navatt_attitude,
            "times": {"offsets": navatt_times, "ref": "GPS"},
            "oop": navatt_oop,
        },
        "scan_encoder": {
            "NAD": {
                "1KM": nad_scan_angle_1km[first_scan:, :],
                "05KM": nad_scan_angle_05km[first_scan:, :],
            },
            "OBL": {
                "1KM": obl_scan_angle_1km[first_scan:, :],
                "05KM": obl_scan_angle_05km[first_scan:, :],
            },
        },
        "eop": {
            "iers_bulletin_b": iers_data,
        },
    }

    return config


@pytest.fixture(name="slstr_204936", scope="module")
def slstr_204936_product(slstr_204936_config):  # pylint: disable=redefined-outer-name
    """
    Test fixture to produce a S3SLSTRGeometry with navatt and encoder angles and frame times from
    S3A_SL_0_SLT____20221101T204936
    """
    return S3SLSTRGeometry(**slstr_204936_config)


@pytest.mark.init_schema_example
def test_init_schema_example(slstr_204936_config):  # pylint: disable=redefined-outer-name
    """Generate JSON examples that implement the init_schema() methods"""
    try:
        import doc_init_schema  # pylint: disable=import-outside-toplevel

        doc_init_schema.generate_example(slstr_204936_config, "S3SLSTRGeometry.204936")
    except ImportError:
        pass


@pytest.fixture(name="img_coords", scope="module")
def generate_all_image_coords():
    """
    Fixture to generate image coordinates
    """
    coord_nad = np.zeros((10, 10, 2), dtype="int32")
    coord_obl = np.zeros((10, 10, 2), dtype="int32")
    for row in range(10):
        for col in range(10):
            coord_nad[row, col, 0] = 110 * col
            coord_nad[row, col, 1] = 70 * row
            coord_obl[row, col, 0] = 50 * col
            coord_obl[row, col, 1] = 70 * row

    img_05_nad = np.copy(coord_nad)
    img_05_obl = np.copy(coord_obl)

    img_05_nad[:, :, 0] *= 2
    img_05_obl[:, :, 0] *= 2

    return {
        "nad_1km": coord_nad,
        "obl_1km": coord_obl,
        "nad_05km": img_05_nad,
        "obl_05km": img_05_obl,
    }


@pytest.mark.slow
@pytest.mark.dem
def test_slstr_direct_loc_204936(slstr_204936, img_coords):
    """
    Unit test for S3SLSTRGeometry.direct_loc
    """
    out_folder = osp.join(TEST_DIR, "outputs/slstr")
    os.makedirs(out_folder, exist_ok=True)

    gnd_nad, _ = slstr_204936.direct_loc(img_coords["nad_1km"], geometric_unit="NAD/1KM/0")
    np.save(osp.join(out_folder, "sample_204936_gnd_nad.npy"), gnd_nad)

    gnd_obl, _ = slstr_204936.direct_loc(img_coords["obl_1km"], geometric_unit="OBL/1KM/0")
    np.save(osp.join(out_folder, "sample_204936_gnd_obl.npy"), gnd_obl)

    gnd_05_nad, _ = slstr_204936.direct_loc(img_coords["nad_05km"], geometric_unit="NAD/05KM_A/0")
    np.save(osp.join(out_folder, "sample_204936_gnd_05_nad.npy"), gnd_05_nad)

    gnd_05_obl, _ = slstr_204936.direct_loc(img_coords["obl_05km"], geometric_unit="OBL/05KM_A/0")
    np.save(osp.join(out_folder, "sample_204936_gnd_05_obl.npy"), gnd_05_obl)


@pytest.fixture(name="img_bloc_coords", scope="module")
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
def test_slstr_direct_loc_204936_perf(slstr_204936, img_bloc_coords):
    """
    Unit test for S3SLSTRGeometry.direct_loc performance
    """
    # call direct_loc
    tic = time.perf_counter()
    slstr_204936.direct_loc(img_bloc_coords, geometric_unit="NAD/1KM/0")
    slstr_204936.direct_loc(img_bloc_coords, geometric_unit="OBL/05KM_A/0")
    tac = time.perf_counter()
    print(f"SLSTR direct_loc on DEM speed: {img_bloc_coords.size / (tac-tic):.1f}")

    tic = time.perf_counter()
    slstr_204936.direct_loc(img_bloc_coords, geometric_unit="NAD/1KM/0", altitude=0.0)
    slstr_204936.direct_loc(img_bloc_coords, geometric_unit="OBL/05KM_A/0", altitude=0.0)
    tac = time.perf_counter()
    print(f"SLSTR direct_loc at constant height speed: {img_bloc_coords.size / (tac-tic):.1f}")


@pytest.fixture(name="orbit_scenario", scope="module")
def orbit_scenario():
    """
    Orbit_scenario from OSF
    """
    return ExplorerDriver.read_orbit_scenario_file(
        osp.join(
            TEST_DIR,
            "resources",
            "S3",
            "OSF",
            "S3A_OPER_MPL_ORBSCT_20160216T192404_99999999T999999_0006.EOF",
        )
    )


def test_slstr_init_osf(orbit_scenario, slstr, thermoelastic, geom_model, sample_time_array, img_coord_nad):
    """
    Test direct location with OSF accuracy by comparing to direct loc with NAVATT.
    """
    nb_scan = len(sample_time_array)
    config_osf = {
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_scenario": [orbit_scenario],
        },
        "resources": {"dem_path": GETAS_PATH, "dem_type": "ZARR"},
        "thermoelastic": thermoelastic,
        "geometry_model": geom_model,
        "sw_geocal": 3,
        "acquisition_times": {
            "NAD": {
                "scan_times": {"offsets": sample_time_array},
                "nb_pixels": 1500,
                "first_acquisition": [2200 for k in range(nb_scan)],
            },
            "OBL": {
                "scan_times": {"offsets": sample_time_array},
                "nb_pixels": 900,
                "first_acquisition": [1060 for k in range(nb_scan)],
            },
            "reference": "GPS",
        },
    }

    geometry_osf = S3SLSTRGeometry(**config_osf)
    geometry_navatt = slstr

    res_navatt, _ = geometry_navatt.direct_loc(img_coord_nad, geometric_unit="NAD/1KM/0")
    res_osf, _ = geometry_osf.direct_loc(img_coord_nad, geometric_unit="NAD/1KM/0")

    res_navatt = res_navatt.reshape(28, 3)
    res_osf = res_osf.reshape(28, 3)

    comp = GeodeticComparator(geometry_osf.propagation_model.body)

    error_2d = comp.planar_error(
        res_navatt[~np.isnan(res_navatt).any(axis=1), :], res_osf[~np.isnan(res_osf).any(axis=1), :]
    )

    np.testing.assert_array_less(error_2d, 260000)
