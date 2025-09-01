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
Unit tests for SRAL Sentinel 3 products
"""

import os
import os.path as osp
import time

import numpy as np
import pytest
from drivers.explorer_legacy import ExplorerDriver
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import GeodeticComparator

from asgard.sensors.sentinel3.sral import S3SRALGeometry

TEST_DIR = osp.dirname(__file__)

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")


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


@pytest.fixture(name="sral", scope="module")
def sral_product(fro_20220510):
    """
    Fixture to initialize a S3SRALGeometry with navatt
    """

    frames = {
        "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(10)], dtype="float64"),
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
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20220510],
        },
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

        doc_init_schema.generate_example(config, "S3SRALGeometry")
    except ImportError:
        pass

    return S3SRALGeometry(**config)


@pytest.fixture(name="img_coord", scope="module")
def img_coord_product():
    """
    Image coordinates for SRAL
    """
    return np.column_stack((np.arange(10), np.arange(10)))


@pytest.mark.dem
@pytest.mark.perfo
def test_sral_direct_loc(sral, img_coord):
    """
    Unit test for S3SRALGeometry.direct_loc with navatt data. Notice that for SRAL
    geolocation there is no need of propagation and DEM because the instrument view is nadir,
    thus we only need to compute orbit state vector
    """
    assert sral is not None

    # Compute of direct_loc (defined in S3SRALGeometry)
    tic = time.perf_counter()
    gnd = sral.direct_loc(img_coord)
    tac = time.perf_counter()
    print(f"SRAL direct_loc at constant height speed: {img_coord.size * 0.5 / (tac-tic):.1f}")

    np.allclose(gnd[0, :], [26.0023, 32.2143, 805908.358])


@pytest.mark.dem
def test_sral_compute_altitude_rate(sral, img_coord):
    """
    Unitary test for the computation of altitude rate
    """
    alt_rate = sral.compute_altitude_rate(img_coord)

    assert alt_rate.shape[0] == img_coord.shape[0]

    # assert on altitude rate
    # value from ASGARD-Legacy: -9.724125 (as of v0.6.1) delta=8.38e-4 m/s
    assert np.allclose(alt_rate[:3], [-9.72328708, -9.72219277, -9.72073758], rtol=0, atol=5e-4)


@pytest.mark.dem
def test_sral_sun_angles(sral):
    """
    Unit test for the computation of sun angles
    """

    ground_coords = np.array(
        [
            [26.0023, 32.2143, 0.0],
            [26.0012349, 32.2092592, 0.0],
            [26.0001672, 32.2041858, 0.0],
            [25.9990997, 32.1991124, 0.0],
            [25.9980322, 32.1940390, 0.0],
        ]
    )

    sun_angles = sral.sun_angles(ground_coords, sral.config["frame"]["times"]["offsets"][:5])

    assert isinstance(sun_angles, np.ndarray)

    assert sun_angles.shape[0] == ground_coords.shape[0]


@pytest.mark.dem
def test_sral_incidence_angles(sral):
    """
    Unit test for the computation of incidence angles
    """

    ground_coords = np.array(
        [
            [26.0023, 32.2143, 0.0],
            [26.0012349, 32.2092592, 0.0],
            [26.0001672, 32.2041858, 0.0],
            [25.9990997, 32.1991124, 0.0],
            [25.9980322, 32.1940390, 0.0],
        ]
    )

    incidence_angles = sral.incidence_angles(ground_coords, sral.config["frame"]["times"]["offsets"][:5])

    assert np.allclose(incidence_angles, np.zeros(ground_coords[..., :2].shape))


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


def test_sral_init_osf(sral, orbit_scenario, img_coord):
    """
    Test direct location with OSF accuracy by comparing to direct loc with NAVATT.
    """

    frames = {
        "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(10)], dtype="float64"),
    }

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources/bulletinb-413.txt"))

    config = {
        "eop": {
            "iers_bulletin_b": iers_data,
        },
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_scenario": [orbit_scenario],
        },
        "frame": {"times": frames},
    }

    geometry_osf = S3SRALGeometry(**config)
    geometry_navatt = sral

    res_osf = geometry_osf.direct_loc(img_coord)
    res_navatt = geometry_navatt.direct_loc(img_coord)

    comp = GeodeticComparator(geometry_osf.body_model)

    error_2d = comp.planar_error(res_navatt[:, :], res_osf[:, :])
    np.testing.assert_array_less(error_2d, 49000)
