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
Unit tests for scanning detetector timestamp model
"""

import os.path as osp

import numpy as np
import pytest
from drivers.sentinel_3_legacy import S3LegacyDriver

from asgard.models.scanningdetector import (
    ScanningDetectorPointingModel,
    ScanningDetectorTimestampModel,
)

TEST_DIR = osp.dirname(__file__)
SLSTR_DIR = osp.join(TEST_DIR, "resources/S3/SLSTR")


@pytest.fixture(name="scanner", scope="module")
def scanningdetector_model():
    """
    Fixture to instanciate an ScanningDetectorTimestampModel with nadir view
    """
    sample_time_array = np.array(
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

    jd_to_microseconds = 86400.0e6
    model_map = {}
    conf = {
        "scan_times": {"offsets": sample_time_array},
        "pixel_period": 81.74 / jd_to_microseconds,
        "pixel_start": 2200,
    }
    model_map["NAD/1KM"] = ScanningDetectorTimestampModel(**conf)
    conf = {
        "scan_times": {"offsets": sample_time_array},
        "pixel_period": 81.74 / jd_to_microseconds,
        "pixel_start": 1060,
    }
    model_map["OBL/1KM"] = ScanningDetectorTimestampModel(**conf)
    conf = {
        "scan_times": {"offsets": sample_time_array},
        "pixel_period": 81.74 * 0.5 / jd_to_microseconds,
        "pixel_start": 4400,
    }
    model_map["NAD/05KM"] = ScanningDetectorTimestampModel(**conf)
    conf = {
        "scan_times": {"offsets": sample_time_array},
        "pixel_period": 81.74 * 0.5 / jd_to_microseconds,
        "pixel_start": 2120,
    }
    model_map["OBL/05KM"] = ScanningDetectorTimestampModel(**conf)
    return model_map


def test_scanning_acquisition_times(scanner):
    """
    Unit test for acquisition_times instanciated scan detector
    """
    img_coords = np.zeros((6, 2), dtype="int32")
    # scan coordinates
    img_coords[:, 1] = [0, 0, 40, 40, 49, 49]

    # 1km NAD pixel coordinates
    img_coords[:, 0] = [0, 1499, 500, 501, 500, 1499]

    dataset = {"coords": img_coords}
    scanner["NAD/1KM"].acquisition_times(dataset)

    assert np.allclose(
        dataset["times"]["offsets"],
        [
            8340.86903163,
            8340.86903305,
            8340.86917098,
            8340.86917099,
            8340.86920223,
            8340.86920318,
        ],
    )
    assert np.all(dataset["abs_pos"] == img_coords[:, 0] + 2200)

    # 1km OBL pixel coordinates
    img_coords[:, 0] = [0, 899, 440, 441, 440, 899]

    scanner["OBL/1KM"].acquisition_times(dataset)

    assert np.allclose(
        dataset["times"]["offsets"],
        [
            8340.86903055,
            8340.8690314,
            8340.86916985,
            8340.86916985,
            8340.8692011,
            8340.86920153,
        ],
    )
    assert np.all(dataset["abs_pos"] == img_coords[:, 0] + 1060)

    # 0.5km NAD pixel coordinates
    img_coords[:, 0] = [0, 2999, 1000, 1001, 1000, 2999]

    scanner["NAD/05KM"].acquisition_times(dataset)

    assert np.allclose(
        dataset["times"]["offsets"],
        [
            8340.86903163,
            8340.86903305,
            8340.86917098,
            8340.86917099,
            8340.86920223,
            8340.86920318,
        ],
    )
    assert np.all(dataset["abs_pos"] == img_coords[:, 0] + 4400)

    # 0.5km OBL pixel coordinates
    img_coords[:, 0] = [0, 1799, 880, 881, 880, 1799]

    dataset = scanner["OBL/05KM"].acquisition_times(dataset)

    assert np.allclose(
        dataset["times"]["offsets"],
        [
            8340.86903055,
            8340.8690314,
            8340.86916985,
            8340.86916985,
            8340.8692011,
            8340.86920153,
        ],
    )
    assert np.all(dataset["abs_pos"] == img_coords[:, 0] + 2120)


@pytest.fixture(name="geom_model", scope="module")
def read_geometry_model():
    """
    Fixture to extract geometric model for SLSTR
    """
    return S3LegacyDriver.slstr_geometry_model(osp.join(SLSTR_DIR, "GEO/SL_1_GEO_AX.nc"))


@pytest.fixture(name="pointing", scope="module")
def slstr_product(geom_model):
    """
    Test fixture to product a S3SLSTRProduct
    """

    config = {
        "pixel_start": {
            "NAD/1KM": 2200,
            "OBL/1KM": 1060,
            "NAD/05KM_A": 4400,
            "OBL/05KM_A": 2120,
        },
        "geometry_model": geom_model,
    }
    return ScanningDetectorPointingModel(**config)


@pytest.fixture(name="img_coord_nad", scope="module")
def img_coord_product_nad():
    """
    Image coordinates for SLSTR with NAD view
    """

    img_coords = np.zeros((6, 2), dtype="int32")
    # scan coordinates
    img_coords[:, 1] = [0, 0, 40, 40, 49, 49]

    # 1km NAD pixel coordinates
    img_coords[:, 0] = [0, 1499, 500, 501, 500, 1499]

    return img_coords


@pytest.fixture(name="img_coord_obl", scope="module")
def img_coord_product_obl():
    """
    Image coordinates for SLSTR with OBL view
    """

    img_coords = np.zeros((6, 2), dtype="int32")
    # scan coordinates
    img_coords[:, 1] = [0, 0, 40, 40, 49, 49]

    # 1km OBL pixel coordinates
    img_coords[:, 0] = [0, 899, 440, 441, 440, 899]

    return img_coords


def test_pointing_slstr_product_nad(pointing, img_coord_nad):
    """
    Unit test for pointing on S3 SLSTR Product
    """

    dataset = {"coords": img_coord_nad, "geom": "NAD/1KM/0"}
    pointing.compute_los(dataset)
    los_out = dataset["los_vec"]

    los_ref = np.array(
        [
            [0.54739953, -0.7150035, 0.43488361],
            [0.07586478, 0.53067992, 0.84417022],
            [0.10625802, -0.56531473, 0.81800275],
            [0.10552744, -0.56453275, 0.81863712],
            [0.10625802, -0.56531473, 0.81800275],
            [0.07586478, 0.53067992, 0.84417022],
        ]
    )
    assert np.allclose(los_out, los_ref)


def test_pointing_slstr_product_obl(pointing, img_coord_obl):
    """
    Unit test for pointing on S3 SLSTR Product
    """

    dataset = {"coords": img_coord_obl, "geom": "OBL/1KM/0"}
    pointing.compute_los(dataset)
    los_out = dataset["los_vec"]

    los_ref = np.array(
        [
            [0.61700584, 0.3848434, 0.68643962],
            [0.40467126, -0.60386561, 0.68672229],
            [0.71338094, -0.14089693, 0.68646608],
            [0.71313855, -0.14211708, 0.68646642],
            [0.71338094, -0.14089693, 0.68646608],
            [0.40467126, -0.60386561, 0.68672229],
        ]
    )
    assert np.allclose(los_out, los_ref)
