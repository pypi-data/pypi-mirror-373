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
Unit tests for OLCI Sentinel 3 products
"""

import logging
import os
import os.path as osp
import sys
import time

import netCDF4
import numpy as np
import pytest
from drivers.explorer_legacy import ExplorerDriver
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.compare import GeodeticComparator

from asgard.core.frame import FrameId
from asgard.core.logger import initialize
from asgard.models.body import EarthBody
from asgard.models.time import TimeReference
from asgard.sensors.sentinel3 import S3MWRGeometry

TEST_DIR = osp.dirname(__file__)
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")
# Generate documentation for the "init_schema" methods
# isort: off
sys.path.append(osp.join(TEST_DIR, "../doc/scripts/init_schema"))
# isort: on

initialize("eocfi")


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


@pytest.fixture(name="mwr", scope="module")
def mwr_product(fro_20220510, pointing_angles):
    """
    Test fixture to produce a S3MWRGeometry configuration with navatt and encoder angles and frame times
    """

    frames = {
        "offsets": np.array(
            [
                8168.02456,
                8168.02466,
                8168.02476,
                8168.02486,
                8168.02496,
            ],
            dtype="float64",
        ),
    }

    navatt_gps = np.load(osp.join(TEST_DIR, "resources/sample_timestamps_gps.npy"))
    navatt_oop = np.load(osp.join(TEST_DIR, "resources/sample_oop.npy"))
    navatt_orb = S3LegacyDriver.read_orbit_file(osp.join(TEST_DIR, "resources/sample_orbit_eme2000.xml"))
    navatt_att = S3LegacyDriver.read_attitude_file(osp.join(TEST_DIR, "resources/sample_attitude.xml"))

    # We set a common time scale for orbit and attitude -> GPS
    navatt_orb["time_ref"] = "GPS"
    navatt_att["times"]["GPS"] = navatt_orb["times"]["GPS"]
    navatt_att["time_ref"] = "GPS"

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "bulletinb-413.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    body = EarthBody(time_reference=time_model)

    fro_20220510_eme = body.transform_orbit(fro_20220510.copy(), FrameId.EME2000)
    fro_20220510_eme["time_ref"] = "GPS"

    navatt_att["times"]["GPS"] = navatt_orb["times"]["GPS"]
    navatt_att["time_ref"] = "GPS"

    config = {
        "eop": {
            "iers_bulletin_b": iers_data,
        },
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20220510_eme],
        },
        "pointing_angles": pointing_angles,
        "frame": {
            "times": frames,
        },
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

        doc_init_schema.generate_example(config, "S3MWRGeometry")
    except ImportError:
        pass

    return S3MWRGeometry(**config)


@pytest.fixture(name="img_coord", scope="module")
def img_coord_product():
    """
    Image coordinates for MWR
    """
    img_coord = np.zeros((500, 1, 2), dtype="int32")  # nb_frames, nb_pixels, lon_lat
    for row in range(500):
        for col in range(1):
            img_coord[row, col, 0] = col
            img_coord[row, col, 1] = row % 5
    return img_coord


@pytest.mark.perfo
def test_mwr_direct_loc(mwr, img_coord):
    """
    Unit test for S3MWRGeometry.direct_loc with navatt data.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    assert mwr is not None

    # shape gnd: nb_cams, nb_frames, lon_lat_alt
    tic = time.perf_counter()
    gnd_c1, times_c1 = mwr.direct_loc(img_coord, geometric_unit="C1", altitude=0.0)  # pylint: disable=unused-variable
    gnd_c2, times_c2 = mwr.direct_loc(img_coord, geometric_unit="C2", altitude=0.0)  # pylint: disable=unused-variable
    tac = time.perf_counter()
    print(f"MWR direct_loc at constant height speed: {img_coord.size / (tac-tic):.1f}")

    assert np.allclose(gnd_c1[0], [1.46868148e02, 3.25757760e01, 0.00000000e00], atol=1e-5)
    assert np.allclose(gnd_c2[0], [1.46733154e02, 3.20893161e01, 0.00000000e00], atol=1e-5)

    # ~ from cProfile import Profile
    # ~ from pyprof2calltree import convert
    # ~ profiler = Profile()
    # ~ profiler.runctx('mwr.direct_loc(img_coord, geometric_unit="C1", altitude=0.0)', locals(), globals())
    # ~ convert(profiler.getstats(), osp.join(TEST_DIR, "outputs", "test_mwr_product_perf.kgrind"))


@pytest.mark.dem
def test_mwr_sun_angles(mwr):
    """
    Unit test for the computation of sun angles
    """

    ground_coords = np.array(
        [
            [1.46868148e02, 3.25757760e01, 0.00000000e00],
            [1.46724351e02, 3.20686520e01, 2.18656190e-09],
            [1.46581781e02, 3.15613701e01, 0.00000000e00],
            [1.46440456e02, 3.10539244e01, 1.09833090e-09],
            [1.46300230e02, 3.05463320e01, 0.00000000e00],
        ]
    )

    sun_angles = mwr.sun_angles(ground_coords, mwr.config["frame"]["times"]["offsets"][:5])

    assert isinstance(sun_angles, np.ndarray)

    assert sun_angles.shape[0] == ground_coords.shape[0]


@pytest.mark.dem
def test_mwr_incidence_angles(mwr):
    """
    Unit test for the computation of incidence angles
    """

    ground_coords = np.array(
        [
            [1.46868148e02, 3.25757760e01, 0.00000000e00],
            [1.46724351e02, 3.20686520e01, 2.18656190e-09],
            [1.46581781e02, 3.15613701e01, 0.00000000e00],
            [1.46440456e02, 3.10539244e01, 1.09833090e-09],
            [1.46300230e02, 3.05463320e01, 0.00000000e00],
        ]
    )

    incidence_angles = mwr.incidence_angles(ground_coords, mwr.config["frame"]["times"]["offsets"][:5])

    assert isinstance(incidence_angles, np.ndarray)


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


def test_mwr_init_fro(fro_20220510, pointing_angles, mwr, img_coord):
    """
    Test direct location with FRO. Comparison to direct loc with NAVATT.
    """

    frames = {
        "offsets": np.array(
            [
                8168.02456,
                8168.02466,
                8168.02476,
                8168.02486,
                8168.02496,
            ],
            dtype="float64",
        ),
    }

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "bulletinb-413.txt"))

    config = {
        "eop": {
            "iers_bulletin_b": iers_data,
        },
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20220510],
        },
        "pointing_angles": pointing_angles,
        "frame": {
            "times": frames,
        },
    }

    geometry_fro = S3MWRGeometry(**config)
    geometry_navatt = mwr

    res_fro = np.squeeze(geometry_fro.direct_loc(img_coord, altitude=0.0)[0])
    res_navatt = np.squeeze(geometry_navatt.direct_loc(img_coord, altitude=0.0)[0])  # pylint: disable=unused-variable

    comp = GeodeticComparator(geometry_fro.propagation_model.body)

    error_2d = comp.planar_error(res_navatt, res_fro)
    np.testing.assert_array_less(error_2d, 1700)


def test_mwr_init_osf(orbit_scenario, pointing_angles, mwr, img_coord):
    """
    Test direct location with OSF accuracy by comparing to direct loc with NAVATT.
    """

    frames = {
        "offsets": np.array(
            [
                8168.02456,
                8168.02466,
                8168.02476,
                8168.02486,
                8168.02496,
            ],
            dtype="float64",
        ),
    }

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "bulletinb-413.txt"))

    config = {
        "eop": {
            "iers_bulletin_b": iers_data,
        },
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_scenario": [orbit_scenario],
        },
        "pointing_angles": pointing_angles,
        "frame": {
            "times": frames,
        },
    }

    geometry_osf = S3MWRGeometry(**config)
    geometry_navatt = mwr

    res_osf = np.squeeze(geometry_osf.direct_loc(img_coord, altitude=0.0)[0])  # pylint: disable=unused-variable
    res_navatt = np.squeeze(geometry_navatt.direct_loc(img_coord, altitude=0.0)[0])  # pylint: disable=unused-variable

    comp = GeodeticComparator(geometry_osf.propagation_model.body)

    error_2d = comp.planar_error(res_navatt, res_osf)
    np.testing.assert_array_less(error_2d, 45000)
