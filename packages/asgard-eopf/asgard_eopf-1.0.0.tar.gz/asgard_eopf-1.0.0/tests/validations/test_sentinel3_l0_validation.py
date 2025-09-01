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
Unit tests for S1L0Geometry footprint computation
"""
import os.path as osp
import xml.etree.ElementTree as ET

import numpy as np
import pytest
from drivers.sentinel_3_legacy import ExplorerDriver, S3LegacyDriver
from helpers.compare import GeodeticComparator

from asgard.core.frame import FrameId
from asgard.core.toolbox import sub
from asgard.models.body import EarthBody
from asgard.models.time import TimeReference
from asgard.sensors.sentinel3.l0 import S3L0Geometry

TEST_DIR = osp.dirname(osp.dirname(__file__))
S3L0Geometry_DIR = osp.join(TEST_DIR, "resources/S3/S3L0Geometry/")


def get_start_stop_time(path: str) -> tuple:
    """
    Return start/stop from xfdumanifest.xml file

    :param: path: path to xfdumanifest.xml file
    :return: start_time, stop_time
    """
    tree = ET.parse(path)
    root = tree.getroot()
    namespace = {"sentinel-safe": "http://www.esa.int/safe/sentinel/1.1"}

    # Time Ref = UTC (normalement)
    start_time = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/sentinel-safe:acquisitionPeriod/sentinel-safe:startTime",
        namespace,
    ).text
    stop_time = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/sentinel-safe:acquisitionPeriod/sentinel-safe:stopTime",
        namespace,
    ).text

    return start_time, stop_time


@pytest.fixture(name="orbits_file", scope="module")
def given_orbits_file():
    return osp.join(S3L0Geometry_DIR, "S3A_OPER_MPL_ORBRES_20220510T000000_20220520T000000_0001.EOF")


@pytest.fixture(name="manifest", scope="module")
def given_manifest():
    return osp.join(S3L0Geometry_DIR, "xfdumanifest.xml")


# TODO: It could be good to add Test regarding other acquisition in the validation tests
def test_sentinel3_l0_footprint(orbits_file, manifest):
    """
    Test computation of S3 L0 footprint.
    """

    # Get data
    orbits = ExplorerDriver.read_orbit_file(orbits_file)
    start_time, stop_time = get_start_stop_time(manifest)

    # convert EF to EME2000 needed to use YSM
    iers_bulletin = osp.join(f"{TEST_DIR}/resources/bulletinb-413.txt")
    iers_data = S3LegacyDriver.read_iers_file(iers_bulletin)
    time_model = TimeReference(iers_bulletin_b=iers_data)
    config = {"time_reference": time_model}
    ebm = EarthBody(**config)
    orbits_eme2000 = ebm.transform_orbit(orbits, FrameId.EME2000)

    # Get footprint reference (from manifest)
    tree = ET.parse(manifest)
    root = tree.getroot()
    namespace = {
        "sentinel-safe": "http://www.esa.int/safe/sentinel/1.1",
        "gml": "http://www.opengis.net/gml",
    }

    footprint = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/sentinel-safe:frameSet/sentinel-safe:footPrint/gml:posList",
        namespace,
    ).text.split()

    gp_ref = []
    for i in range(0, len(footprint), 2):
        gp_ref.append([float(footprint[i]), float(footprint[i + 1])])
    gp_ref = np.array(gp_ref)
    gp_ref[:, [0, 1]] = gp_ref[:, [1, 0]]  # Swap columns

    # Compute footprint
    conf = {
        "start_time": start_time,
        "stop_time": stop_time,
        "orbit_aux_info": {
            "orbit_state_vectors": orbits_eme2000,
        },
        "angles": {"nearRange": 0.0000, "farRange": np.rad2deg(-0.00035)},
        "pairs_number": 12,
    }
    S3L0Geom = S3L0Geometry(**conf)
    gp_calc = S3L0Geom.footprint()

    # Saving as .csv
    # np.savetxt("gp_ref_s3.csv", gp_ref, delimiter=',', fmt='%.8f')
    # np.savetxt("gp_calc_s3.csv", gp_calc, delimiter=',', fmt='%.8f')

    # Order the footprint as a loop
    gp_calc_2 = np.array(
        [
            gp_calc[0],
            gp_calc[1],
            gp_calc[2],
            gp_calc[3],
            gp_calc[4],
            gp_calc[5],
            gp_calc[6],
            gp_calc[7],
            gp_calc[8],
            gp_calc[9],
            gp_calc[10],
            gp_calc[11],
            gp_calc[23],
            gp_calc[22],
            gp_calc[21],
            gp_calc[20],
            gp_calc[19],
            gp_calc[18],
            gp_calc[17],
            gp_calc[16],
            gp_calc[15],
            gp_calc[14],
            gp_calc[13],
            gp_calc[12],
        ]
    )
    comp = GeodeticComparator(S3L0Geom.propagation_model.body)
    poly_diff = np.array(comp.footprint_comparison(gp_calc_2, gp_ref))

    # The coverage is close. But as footprint is small, the ratio is not above 0.9
    np.testing.assert_(poly_diff[0] > 0.87)
    # We look at the maximal distance
    np.testing.assert_(poly_diff[1] < 27)

    # # Set up for comparison
    # gp_calc = gp_calc[:, :2]
    # gp_calc = gp_calc[np.argsort(gp_calc[:, 0])]

    # gp_ref = gp_ref[np.argsort(gp_ref[:, 0])]
    # # The gp_ref points form a closed loop, so there is a duplicate point.
    # gp_ref = np.delete(gp_ref, -2, axis=0)  # delete duplicates

    # # print("gp_ref :\n", gp_ref)
    # # print("gp_calc :\n", gp_calc)
    # np.testing.assert_allclose(gp_calc, gp_ref, atol=1e-3)
