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

TEST_DIR = osp.dirname(osp.dirname(__file__))
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


def get_footprint_from_manifest(manifest):
    """
    Return footPrint from manifest.safe file

    :param: path: path to manifest.safe file
    :return: footPrint coorinates
    """
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
    return np.array(gp_ref, dtype=float)


@pytest.fixture(name="calibration_file", scope="module")
def given_calibration_file():
    return osp.join(S1L0Geometry_DIR, "s1a-aux-cal.xml")


@pytest.fixture(name="orbits_file", scope="module")
def given_orbits_file():

    # TDS Test L0
    # orbit_file = osp.join(S1L0Geometry_DIR,
    #                        "S1A_OPER_AUX_RESORB_OPOD_20250212T090850_V20250212T051523_20250212T083253.EOF")

    # TDS1
    # orbit_file = osp.join(
    #     TEST_DIR,
    #     "resources",
    #     "S1",
    #     "TDS1",
    #     "S1A_OPER_AUX_RESORB_OPOD_20221112T141116_V20221112T101956_20221112T133726.EOF",
    # )

    # TDS2
    # orbit_file = osp.join(
    #     TEST_DIR,
    #     "resources",
    #     "S1",
    #     "TDS2",
    #     "S1A_OPER_AUX_RESORB_OPOD_20230131T174904_V20230131T141017_20230131T172747.EOF",
    # )

    # TDS3
    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS3",
        "S1A_OPER_AUX_RESORB_OPOD_20220802T015736_V20220801T215919_20220802T011649.EOF",
    )

    return orbit_file


@pytest.fixture(name="manifest", scope="module")
def given_manifest():
    # TDS L0
    # manifest = osp.join(S1L0Geometry_DIR, "manifest.safe")

    # TDS1
    # manifest = "/home/aburie/Projets/ASGARD/results/S1/L0/TDS1/manifest_L0.safe"

    # TDS2
    # manifest = "/home/aburie/Projets/ASGARD/results/S1/L0/TDS2/S1A_IW_RAW__0SDV_20230131T155748_20230131T155820_047030_05A42A_1AA8.SAFE/manifest.safe"

    # TDS3
    manifest = {
        "manifest_L0": osp.join(TEST_DIR, "resources", "S1", "TDS3", "manifest_L0.safe"),
        "manifest_L1": osp.join(TEST_DIR, "resources", "S1", "TDS3", "manifest_L1.safe"),
    }

    return manifest


def test_sentinel1_l0_footprints(calibration_file, orbits_file, manifest):
    """
    Test computation of S1 L0 footprint.
    """
    # Get data
    beam_angle = get_beam_nominal_angles(calibration_file)
    orbits = ExplorerDriver.read_orbit_file(orbits_file)

    # Get start and stop time
    start_time_L0, stop_time_L0 = get_start_stop_time(manifest["manifest_L0"])
    start_time_L1, stop_time_L1 = get_start_stop_time(manifest["manifest_L1"])

    # Get footprint reference (from manifest)
    footprint_L0_not_ordered = get_footprint_from_manifest(manifest["manifest_L0"])
    footprint_L0 = np.array(
        [
            footprint_L0_not_ordered[2],
            footprint_L0_not_ordered[3],
            footprint_L0_not_ordered[0],
            footprint_L0_not_ordered[1],
        ]
    )
    footprint_L1_not_ordered = get_footprint_from_manifest(manifest["manifest_L1"])
    footprint_L1 = np.array(
        [
            footprint_L1_not_ordered[2],
            footprint_L1_not_ordered[3],
            footprint_L1_not_ordered[0],
            footprint_L1_not_ordered[1],
        ]
    )

    # Compute footprint from L0 information
    conf_L0 = {
        "start_time": start_time_L0,
        "stop_time": stop_time_L0,
        "orbit_state_vectors": orbits,
        "angles": {
            "nearRange": beam_angle["S4"]["beamNominalNearRange"],
            "farRange": beam_angle["S4"]["beamNominalFarRange"],
        },
        "look_side": "RIGHT",
    }
    S1L0Geom_L0 = S1L0Geometry(**conf_L0)
    gp_calc_L0 = S1L0Geom_L0.footprint()[:, :-1]

    # Compute footprint from L1 information
    conf_L1 = {
        "start_time": start_time_L1,
        "stop_time": stop_time_L1,
        "orbit_state_vectors": orbits,
        "angles": {  # Angles are coarsly (rounded) read from L1 annotation file
            "nearRange": 30.68,
            "farRange": 35.02,
        },
        "look_side": "RIGHT",
    }
    S1L0Geom_L1 = S1L0Geometry(**conf_L1)
    gp_calc_L1 = S1L0Geom_L1.footprint()[:, :-1]

    # Save some footprints
    # np.savetxt("gp_ref_s1.csv", gp_ref, delimiter=',', fmt='%.8f')
    # np.savetxt("gp_calc_s1.csv", gp_calc, delimiter=',', fmt='%.8f')

    # Compare results
    comp = GeodeticComparator(S1L0Geom_L0.propagation_model.body)

    # poly_diff_L0_refL0 = np.array(comp.footprint_comparison(gp_calc_L0, footprint_L0))
    # poly_diff_L1_refL0 = np.array(comp.footprint_comparison(gp_calc_L1, footprint_L0))
    poly_diff_L0_refL1 = np.array(comp.footprint_comparison(gp_calc_L0, footprint_L1))
    poly_diff_L1_refL1 = np.array(comp.footprint_comparison(gp_calc_L1, footprint_L1))
    # poly_diff_L0_L1 = np.array(comp.footprint_comparison(gp_calc_L0, gp_calc_L1))
    poly_diff_refL0_refL1 = np.array(comp.footprint_comparison(footprint_L0, footprint_L1))

    # Print all computations
    # print()
    # print("footprint_L0: ", footprint_L0)
    # print("footprint_L1: ", footprint_L1)
    # print("footprint calculated L0: ", gp_calc_L0)
    # print("footprint calculated L0: ", gp_calc_L1)
    # print("Compare L0_refL0: ", poly_diff_L0_refL0)
    # print("Compare L1_refL0: ", poly_diff_L1_refL0)
    # print("Compare L0_refL1: ", poly_diff_L0_refL1)
    # print("Compare L1_refL1: ", poly_diff_L1_refL1)
    # print("Compare L0_L1: ", poly_diff_L0_L1)
    # print("Compare refL0_refL1: ", poly_diff_refL0_refL1)

    # VALIDATION

    # Low tolerance as the Legacy (ref) L0 footprint is shifted
    # https://esa-cams.altassian.net/browse/GSANOM-14583

    # First we assess that the refL0 is more shifted from refL1 that the computed L0 footprint
    np.testing.assert_(poly_diff_refL0_refL1[0] < poly_diff_L0_refL1[0])

    # Then we assess that taking information from L1 give results closer
    # to L1 footprint than taking information from the L0
    np.testing.assert_(poly_diff_L0_refL1[0] < poly_diff_L1_refL1[0])

    # Then we assess that the computed footprint taking information from the Level1
    # is very close to the one generated in the L1 manifest (refL1)
    np.testing.assert_(0.97 < poly_diff_L1_refL1[0])
