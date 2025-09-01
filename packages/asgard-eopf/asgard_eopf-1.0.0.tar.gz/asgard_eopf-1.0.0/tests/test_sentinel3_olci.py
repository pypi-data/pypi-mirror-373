#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022 CS GROUP
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
Unit tests for OLCI Sentinel 3 products
"""

import os
import os.path as osp
import time

import dask
import dask.array as da
import numpy as np
import numpy.testing as npt
import pytest
from dask.distributed import Client
from drivers.explorer_legacy import ExplorerDriver
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import GeodeticComparator
from helpers.serde import repickle

from asgard.core.product import direct_location, sun_angles
from asgard.sensors.sentinel3 import S3OLCIGeometry

TEST_DIR = osp.dirname(__file__)

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")


@pytest.fixture(name="pointing_vectors", scope="module")
def read_pointing_vectors():
    """
    Fixture to extract pointing vectors
    """
    calibration_file = osp.join(TEST_DIR, "resources/S3/OLCI/CAL", "OL_1_CAL_AX.nc")
    return S3LegacyDriver.olci_pointing_angles(calibration_file)


@pytest.fixture(name="thermoelastic", scope="module")
def read_thermoelastic():
    """
    Fixture to extract thermoelastic grids
    """
    calibration_file = osp.join(TEST_DIR, "resources/S3/OLCI/CAL", "OL_1_CAL_AX.nc")
    return S3LegacyDriver.s3_thermoelastic_tables(calibration_file, group="thermoelastic_model_EO")


@pytest.fixture(name="fro_20221030", scope="module")
def read_fro_20221030():
    """
    Fixture to extract FRO orbit from 2022-10-30
    """
    orbit_file = osp.join(
        TEST_DIR,
        "resources/S3/FRO",
        "S3A_OPER_MPL_ORBRES_20221030T000000_20221109T000000_0001.EOF",
    )

    return S3LegacyDriver.read_orbit_file(orbit_file)


@pytest.fixture(name="fro_20220510", scope="module")
def read_fro_20220510():
    """
    Fixture to extract FRO orbit from 2022-05-10
    """
    orbit_file = osp.join(
        TEST_DIR,
        "resources/S3/FRO",
        "S3A_OPER_MPL_ORBRES_20220510T000000_20220520T000000_0001.EOF",
    )
    return S3LegacyDriver.read_orbit_file(orbit_file)


@pytest.fixture(name="olci")  # (name="olci", scope="module")
def olci_product(fro_20220510, pointing_vectors, thermoelastic):
    """
    Fixture to initialize a S3OLCIGeometry with navatt
    """

    frames = {
        "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(100)], dtype="float64"),
    }

    navatt_gps = np.load(osp.join(TEST_DIR, "resources/sample_timestamps_gps.npy"))
    navatt_oop = np.load(osp.join(TEST_DIR, "resources/sample_oop.npy"))

    # Note: here we use inertial coordinates for orbit PV
    navatt_orb = S3LegacyDriver.read_orbit_file(osp.join(TEST_DIR, "resources/sample_orbit_eme2000.xml"))
    # Note: convertion to EOCFI convention not needed, already accounted in platform model
    navatt_att = S3LegacyDriver.read_attitude_file(osp.join(TEST_DIR, "resources/sample_attitude.xml"))
    # We set a common time scale for orbit and attitude -> GPS
    navatt_orb["time_ref"] = "GPS"
    navatt_att["times"]["GPS"] = navatt_orb["times"]["GPS"]
    navatt_att["time_ref"] = "GPS"

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources/bulletinb-413.txt"))

    config = {
        "eop": {
            "iers_bulletin_b": iers_data,
        },
        "resources": {"dem_path": GETAS_PATH, "dem_type": "ZARR"},
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20220510],
        },
        "pointing_vectors": pointing_vectors,
        "thermoelastic": thermoelastic,
        "frame": {"times": frames},
        "navatt": {
            "orbit": navatt_orb,
            "attitude": navatt_att,
            "times": {
                "offsets": navatt_gps,
                "ref": "GPS",
            },
            "oop": navatt_oop,
        },
    }

    # Write JSON file on disk for the init_schema documentation
    try:
        import doc_init_schema  # pylint: disable=import-outside-toplevel

        doc_init_schema.generate_example(config, "S3OLCIGeometry")
    except ImportError:
        pass

    return S3OLCIGeometry(**config)


@pytest.mark.dem
def test_navatt_olci_direct_loc(olci):
    """
    Unit test for S3OLCIGeometry.direct_loc with navatt data
    """

    assert olci is not None

    # call direct_loc
    img_coords = np.zeros((5, 10, 2), dtype="int32")
    for row in range(5):
        for col in range(10):
            img_coords[row, col, 0] = col
            img_coords[row, col, 1] = row

    gnd, times = olci.direct_loc(img_coords, geometric_unit="C2")
    npt.assert_allclose(
        [141.12276167, 33.3462977],
        gnd[0, 0, :2],
        atol=2e-4,
    )

    gnd_to_sun = olci.sun_angles(gnd, times)
    npt.assert_allclose(
        [112.58355177, 30.1135155],
        gnd_to_sun[0, 0, :],
        atol=2e-4,
    )

    gnd_to_sun_dist = olci.sun_distances(gnd, times)
    npt.assert_allclose(
        [
            1.51129181e11,
            1.51129181e11,
            1.51129181e11,
            1.51129181e11,
            1.51129181e11,
            1.51129180e11,
            1.51129180e11,
            1.51129180e11,
            1.51129180e11,
            1.51129180e11,
        ],
        gnd_to_sun_dist[0],
        rtol=1e-4,
        atol=0,
    )

    sat_to_gnd = olci.viewing_angles(gnd, times)
    npt.assert_allclose(
        [280.48809433, 38.06801833],
        sat_to_gnd[0, 0, :],
        atol=2e-4,
    )

    gnd_to_sat = olci.incidence_angles(gnd, times)
    npt.assert_allclose(
        [100.48809433, 38.06801833],
        gnd_to_sat[0, 0, :],
        atol=2e-4,
    )


@pytest.fixture(name="img_coord", scope="module")
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
def test_navatt_olci_product_perf(olci, img_coord):
    """
    Unit test for S3OLCIGeometry.direct_loc with navatt data, with 740000 points
    """

    # ~ from cProfile import Profile
    # ~ from pyprof2calltree import convert
    # ~ profiler = Profile()
    # ~ profiler.runctx('olci.direct_loc(img_coord, geometric_unit="C2")', locals(), globals())
    # ~ convert(profiler.getstats(), osp.join(TEST_DIR, "outputs", "test_navatt_olci_product_perf.kgrind"))

    # call direct_loc
    tic = time.perf_counter()
    gnd, times = olci.direct_loc(img_coord, geometric_unit="C2")
    tac = time.perf_counter()
    print(f"OLCI direct_loc speed: {img_coord.size * 0.5 / (tac-tic):.1f}")

    tic = time.perf_counter()
    olci.sun_angles(gnd, times)
    tac = time.perf_counter()
    print(f"Sun angles speed: {img_coord.size * 0.5 / (tac-tic):.1f}")

    tic = time.perf_counter()
    olci.incidence_angles(gnd, times)
    tac = time.perf_counter()
    print(f"Incidence angles speed: {img_coord.size * 0.5 / (tac-tic):.1f}")


@pytest.fixture(name="dask_client", scope="module")
def given_a_dask_local_client():
    """
    Instantiate a local cluster with 1 worker
    """
    dask.config.set({"distributed.scheduler.active-memory-manager.policies": []})
    return Client(processes=True, threads_per_worker=1, n_workers=1)


def test_pickle_olci(olci):
    """
    Pickle / unpickle ocli object
    """
    repickle(olci)


def test_pickle_coords(img_coord):
    """
    Pickle / unpickle ocli object
    """
    repickle(img_coord)


@pytest.mark.slow
@pytest.mark.dem
@pytest.mark.parametrize("n_workers", [1, 2, 4, 6])
def test_navatt_olci_product_scalability(olci, img_coord, dask_client, n_workers):  # pylint: disable=unused-argument
    """
    Unit test for S3OLCIProduct.direct_loc with navatt data, with 740000 points
    """
    dask_client.cluster.scale(n_workers)

    perf = time.perf_counter()
    olci_remote = dask_client.scatter(olci)
    dask_client.replicate([olci_remote])
    print(f"Broadcast time : {time.perf_counter() - perf:.3g}")

    perf = time.perf_counter()
    chunked_coords = da.from_array(img_coord, chunks=(5, 740, 2))
    ground = da.map_blocks(
        direct_location,
        olci_remote,
        chunked_coords,
        dtype="float64",
        chunks=(5, 740, 4),
        geometric_unit="C2",
    )
    ground.compute()

    print(f"Compute time : {time.perf_counter() - perf:.3g}")

    # clean the broadcasted data
    dask_client.cancel([olci_remote])


@pytest.mark.skip
@pytest.mark.parametrize("n_workers", [1, 2, 4, 6])
def test_numpy_scalability(img_coord, dask_client, n_workers):  # pylint: disable=unused-argument
    """
    Unit test with basic Numpy operations, with 740000 points, skipped by default
    """
    dask_client.cluster.scale(n_workers)

    def my_job(array):
        """
        Small worker function relying on Numpy
        """
        output = array
        for _ in range(10000):
            output[..., 0] = np.sin(output[..., 1])
            output[..., 1] = np.cos(output[..., 0])
        return output

    # ~ with performance_report(filename="dask-report.html"):
    perf = time.perf_counter()
    chunked_coords = da.from_array(img_coord, chunks=(5, 740, 2))
    ground = da.map_blocks(
        my_job,
        chunked_coords,
        dtype="float64",
        chunks=(5, 740, 2),
    )
    ground.compute()

    print(f"Compute time : {time.perf_counter() - perf:.3g}")


@pytest.mark.slow
@pytest.mark.dem
def test_navatt_olci_product_scalability_dem_cached(olci, img_coord, dask_client):
    """
    Unit test for S3OLCIProduct.direct_loc with navatt data, with 740000 points
    """
    # call direct_loc to have cached dem
    olci.direct_loc(img_coord, geometric_unit="C2")

    # scale to maximum number of worker
    dask_client.cluster.scale(6)

    perf = time.perf_counter()
    olci_remote = dask_client.scatter(olci)
    dask_client.replicate([olci_remote])
    print(f"Broadcast time : {time.perf_counter() - perf}")

    chunked_coords = da.from_array(img_coord, chunks=(5, 740, 2))
    compute_time = {}
    for n_workers in [6, 4, 2, 1]:
        # scale the number of workers
        dask_client.cluster.scale(n_workers)

        perf = time.perf_counter()
        ground = da.map_blocks(
            direct_location,
            olci_remote,
            chunked_coords,
            dtype="float64",
            chunks=(5, 740, 4),
            geometric_unit="C2",
        )
        ground.compute()
        compute_time[n_workers] = time.perf_counter() - perf

    # clean the broadcasted data
    dask_client.cancel([olci_remote])
    print(f"Compute times : {compute_time}")


@pytest.mark.slow
@pytest.mark.dem
def test_navatt_olci_product_scalability_all_cams(olci, img_coord, dask_client):
    """
    Unit test for S3OLCIProduct.direct_loc with navatt data, with 740000 points and all cams in parallel
    """
    dask_client.cluster.scale(5)

    perf = time.perf_counter()
    olci_remote = dask_client.scatter(olci)
    dask_client.replicate([olci_remote])
    print(f"Broadcast time : {time.perf_counter() - perf:.3g}")

    results = []
    for cam in range(1, 6):
        results.append(dask_client.submit(direct_location, olci_remote, img_coord, geometric_unit=f"C{cam}"))

    outputs = []
    for res in results:
        outputs.append(res.result()[0])

    # clean the broadcasted data
    dask_client.cancel([olci_remote])


@pytest.mark.slow
@pytest.mark.dem
def test_navatt_olci_product_scalability_angles(olci, img_coord, dask_client):
    """
    Unit test for S3OLCIProduct.direct_loc with navatt data, with 740000 points
    """
    # call direct_loc to have cached dem
    ground_and_times = olci.direct_loc_bundle(img_coord, geometric_unit="C2")
    chunked_all = da.from_array(ground_and_times, chunks=(10, 740, 4))

    # scale to maximum number of worker
    dask_client.cluster.scale(6)

    perf = time.perf_counter()
    olci_remote = dask_client.scatter(olci)
    dask_client.replicate([olci_remote])
    print(f"Broadcast time : {time.perf_counter() - perf:.3g}")

    compute_time = {}
    for n_workers in [6, 4, 2, 1]:
        # scale the number of workers
        dask_client.cluster.scale(n_workers)

        perf = time.perf_counter()
        angles = da.map_blocks(
            sun_angles,
            olci_remote,
            chunked_all,
            dtype="float64",
            chunks=(10, 740, 2),
        )
        angles.compute()
        compute_time[n_workers] = time.perf_counter() - perf

    print(f"Compute times : {compute_time}")

    # clean the broadcasted data
    dask_client.cancel([olci_remote])


@pytest.mark.dem
def test_navatt_olci_product_footprint(olci):
    """
    Unit test for S3OLCIGeometry.footprint
    """

    # call footprint
    footprint_corners = olci.footprint(geometric_unit="C4")

    ref_corners = np.array(
        [
            [145.91120418, 32.50662257, 27.00850593],
            [147.97587189, 32.08275196, 23.00083229],
            [147.82780109, 31.58144251, 23.00897123],
            [145.77424161, 32.00409191, 28.01657936],
        ]
    )

    npt.assert_allclose(ref_corners[:, :2], footprint_corners[:, :2], atol=1e-4)

    footprint_100pix = olci.footprint(sampling_step=100, geometric_unit="C4")

    ref_100pix = np.array(
        [
            [145.91120418, 32.50662257, 27.00850593],
            [146.19081705, 32.45140203, 26.73638325],
            [146.47013166, 32.395559, 26.02295944],
            [146.74926515, 32.33907096, 25.00686928],
            [147.02834844, 32.28191143, 25.00972319],
            [147.30751898, 32.22405135, 24.00130674],
            [147.58691238, 32.16546071, 23.01030726],
            [147.86665379, 32.10611044, 23.00475624],
            [147.97587189, 32.08275196, 23.00083229],
            [147.82780109, 31.58144251, 23.00897123],
            [147.54937343, 31.64089258, 24.00083167],
            [147.2713469, 31.69958406, 24.00953571],
            [146.99359908, 31.75754589, 25.00320014],
            [146.71599865, 31.81480766, 26.00363234],
            [146.43840851, 31.87139894, 26.01996713],
            [146.16069515, 31.92734724, 27.0092133],
            [145.882735, 31.9826769, 27.00064213],
            [145.77424161, 32.00409191, 28.01657936],
        ]
    )

    npt.assert_allclose(ref_100pix[:, :2], footprint_100pix[:, :2], atol=1e-4)


@pytest.mark.dem
def test_inverse_loc(olci):
    """
    Unit test for S3OLCIGeometry.inverse_loc()
    """

    # generate a subsampled grid of the fullres image
    img_coords = np.zeros((10, 37, 2), dtype="int32")
    for row in range(10):
        for col in range(20):
            img_coords[row, col, 0] = col * 37
            img_coords[row, col, 1] = row * 10

    # compute direct loc of this grid
    gnd, _ = olci.direct_loc(img_coords, geometric_unit="C2")
    xy_coords = gnd[..., :2]

    # invert the ground locations
    inverse_coords = olci.inverse_loc(xy_coords, geometric_unit="C2")

    # we should get back original image coordinates
    error_coords = inverse_coords - img_coords
    error_norm = np.linalg.norm(error_coords, axis=2)
    assert np.max(error_norm) < 0.1
    assert np.count_nonzero(error_norm > 1e-3) < 5


@pytest.mark.dem
def test_inverse_loc_extra(olci):
    """
    Unit test for S3OLCIGeometry.inverse_loc() with corner cases coordinates
    """

    # geolocate the first 2x2 cell
    img_coords = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype="int32")
    gnd, _ = olci.direct_loc(img_coords, geometric_unit="C2")
    xy_coords = gnd[..., :2]

    extra_coords = np.array(
        [
            0.25 * (xy_coords[0] + xy_coords[1] + xy_coords[2] + xy_coords[3]),  # middle of the cell
            2 * xy_coords[0] - xy_coords[3],  # virtual position (-1,-1)
        ],
        dtype="float64",
    )

    inverse_coords = olci.inverse_loc(extra_coords, geometric_unit="C2")

    assert np.allclose(inverse_coords, [[0.5, 0.5], [-1.0, -1.0]], atol=2e-3)


def test_inverse_loc_constant_altitude(olci):
    """
    Unit test for S3OLCIGeometry.inverse_loc() at constant altitude
    """

    # generate a subsampled grid of the fullres image
    img_coords = np.zeros((10, 37, 2), dtype="int32")
    for row in range(10):
        for col in range(20):
            img_coords[row, col, 0] = col * 37
            img_coords[row, col, 1] = row * 10

    # compute direct loc of this grid
    gnd, _ = olci.direct_loc(img_coords, geometric_unit="C2", altitude=300)

    # invert the ground locations
    inverse_coords = olci.inverse_loc(gnd, geometric_unit="C2", altitude=300)

    # we should get back original image coordinates
    error_coords = inverse_coords - img_coords
    error_norm = np.linalg.norm(error_coords, axis=2)
    assert np.max(error_norm) < 0.1
    assert np.count_nonzero(error_norm > 1e-3) < 5


@pytest.mark.dem
def test_instrument_to_sun(olci):
    """
    Unit test for S3OLCIGeometry.instrument_to_sun

    Note: the output coordinates are already in OLCI instrument frame, no need to flip x/y and
    invert z (see OC-GE_5-2a)
    """
    times = np.array([8168.024560769051 + 0.00001 * k for k in range(10)], dtype="float64")

    sun_pos = olci.instrument_to_sun(times)

    npt.assert_allclose([-1.59373968e10, 6.27600397e10, -1.36563226e11], sun_pos[0], atol=1e7)


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


def test_olci_init_osf(olci, pointing_vectors, thermoelastic, orbit_scenario):
    """
    Test direct location with OSF accuracy by comparing to direct loc with NAVATT.
    """

    frames = {
        "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(100)], dtype="float64"),
    }

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources/bulletinb-413.txt"))

    config = {
        "eop": {
            "iers_bulletin_b": iers_data,
        },
        "resources": {"dem_path": GETAS_PATH, "dem_type": "ZARR"},
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_scenario": [orbit_scenario],
        },
        "pointing_vectors": pointing_vectors,
        "thermoelastic": thermoelastic,
        "frame": {"times": frames},
    }

    geometry_osf = S3OLCIGeometry(**config)
    geometry_navatt = olci

    img_coords = np.zeros((10, 37, 2), dtype="int32")
    for row in range(10):
        for col in range(20):
            img_coords[row, col, 0] = col * 37
            img_coords[row, col, 1] = row * 10

    res_navatt, _ = geometry_navatt.direct_loc(img_coords, geometric_unit="C2", altitude=300)
    res_osf, _ = geometry_osf.direct_loc(img_coords, geometric_unit="C2", altitude=300)

    comp = GeodeticComparator(geometry_osf.propagation_model.body)

    error_2d = comp.planar_error(res_navatt[:, 0, :], res_osf[:, 0, :])

    np.testing.assert_array_less(error_2d, 72000)