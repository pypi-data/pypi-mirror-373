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
from drivers.sentinel_1_legacy import ExplorerDriver
from helpers.compare import GeodeticComparator

from asgard.sensors.sentinel1.l0 import S1L0Geometry

TEST_DIR = osp.dirname(__file__)
S1L0Geometry_DIR = osp.join(TEST_DIR, "resources/S1/S1L0Geometry/")


def get_start_stop_time(path: str) -> tuple:
    """
    Return start/stop from manifest.safe file

    :param: path: path to manifest.safe file
    :return: start_time, stop_time
    """
    tree = ET.parse(path)
    root = tree.getroot()

    namespace = {"ns": "http://www.esa.int/safe/sentinel-1.0"}

    # Time Ref = UTC (normalement)
    start_time = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/ns:acquisitionPeriod/ns:startTime", namespace
    ).text
    stop_time = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/ns:acquisitionPeriod/ns:stopTime", namespace
    ).text

    return start_time, stop_time


def get_beam_nominal_angles(path: str) -> dict:
    """
    Read beam nominal angle from calibration file

    :param: path: path to calibration xml file
    :return: dict swath name, polarisation, beam nominal angle (near and far)
    """
    tree = ET.parse(path)
    root = tree.getroot()

    swath_courant_name = ""
    res = {}
    for node in root.iterfind("calibrationParamsList/calibrationParams"):

        swath_name = node.find("swath").text
        dict_beam = {
            "beamNominalNearRange": float(node.find("elevationAntennaPattern/beamNominalNearRange").text),
            "beamNominalFarRange": float(node.find("elevationAntennaPattern/beamNominalFarRange").text),
        }

        if swath_name != swath_courant_name:
            swath_courant_name = swath_name
            res_courant = {swath_name: {**dict_beam}}
            res = {**res, **res_courant}

    return res


@pytest.fixture(name="calibration_file", scope="module")
def given_calibration_file():
    return osp.join(S1L0Geometry_DIR, "s1a-aux-cal.xml")


@pytest.fixture(name="orbits_file", scope="module")
def given_orbits_file():
    return osp.join(S1L0Geometry_DIR, "S1A_OPER_AUX_RESORB_OPOD_20250212T090850_V20250212T051523_20250212T083253.EOF")


@pytest.fixture(name="manifest", scope="module")
def given_manifest():
    return osp.join(S1L0Geometry_DIR, "manifest.safe")


def test_sentinel1_footprint_l0(calibration_file, orbits_file, manifest):
    """
    Test computation of S1 L0 footprint.
    """
    # Get data
    beam_angle = get_beam_nominal_angles(calibration_file)
    orbits = ExplorerDriver.read_orbit_file(orbits_file)
    start_time, stop_time = get_start_stop_time(manifest)

    # Get footprint reference (from manifest)
    tree = ET.parse(manifest)
    root = tree.getroot()
    namespace = {
        "ns": "http://www.esa.int/safe/sentinel-1.0",
        "qg": "http://www.opengis.net/gml",
    }

    gp_ref_str = root.find(
        "metadataSection/metadataObject/metadataWrap/xmlData/ns:frameSet/ns:frame/ns:footPrint/qg:coordinates",
        namespace,
    ).text

    gp_ref_str = gp_ref_str.split()
    gp_ref = [pair.split(",") for pair in gp_ref_str]
    gp_ref = np.array(gp_ref, dtype=float)[:-1]

    conf = {
        "start_time": start_time,
        "stop_time": stop_time,
        "orbit_state_vectors": orbits,
        "angles": {
            "nearRange": beam_angle["IW1"]["beamNominalNearRange"],
            "farRange": beam_angle["IW3"]["beamNominalFarRange"],
        },
        "look_side": "RIGHT",
    }
    S1L0Geom = S1L0Geometry(**conf)
    # Compute footprint
    gp_calc = S1L0Geom.footprint()[:, :-1]

    # np.savetxt("gp_ref_s1.csv", gp_ref, delimiter=',', fmt='%.8f')
    # np.savetxt("gp_calc_s1.csv", gp_calc, delimiter=',', fmt='%.8f')

    # print("\n--- Diff calc-estim ---")
    # print(abs(gp_ref - gp_calc))

    # Compare results
    comp = GeodeticComparator(S1L0Geom.propagation_model.body)

    poly_diff_L0_refL0 = np.array(comp.footprint_comparison(gp_calc, gp_ref))

    # Low tolerance as the Legacy L0 footprint is shifted
    # https://esa-cams.altassian.net/browse/GSANOM-14583
    # More tests to validate it with L1 Footprint are done in validation file test_sentinel1_l0_validation.py
    np.testing.assert_(poly_diff_L0_refL0[0] > 0.8)
