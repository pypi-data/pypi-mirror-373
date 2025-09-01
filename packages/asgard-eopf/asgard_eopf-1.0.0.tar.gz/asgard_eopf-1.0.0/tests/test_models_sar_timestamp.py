#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2024 CS GROUP
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
Unit test for SAR Timestamp model
"""

import os
import os.path as osp

import numpy as np
import pytest
from drivers.sentinel_1_legacy import S1LegacyDriver

from asgard.models.body import EarthBody
from asgard.models.sar import SarTimestampModel
from asgard.models.time import TimeReference

TEST_DIR = osp.dirname(__file__)
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")


@pytest.fixture(name="driver", scope="module")
def given_legacy_driver():
    """
    Create a S1LegacyDriver with IERS bulletin for 2022-11-11
    """
    iers_data = S1LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt"))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    return S1LegacyDriver(EarthBody(time_reference=time_model))


@pytest.fixture(name="tref", scope="module")
def given_time_correlation_model(driver):
    """
    Create a TimeReference with IERS bulletin for 2022-11-11
    """

    return driver.time_reference


@pytest.fixture(name="ew1_azimuth", scope="module")
def given_ew1_azimuth_times(tref):
    """
    Generate input azimuth times for product S1A_EW_RAW__0SDH_20221111T114657_20221111T114758
    """

    # from annotations, this is the azimuth time at mid slant range (of EW3) for each burst
    first_line_utc = [
        "2022-11-11T11:47:01.513329",
        "2022-11-11T11:47:04.552211",
        "2022-11-11T11:47:07.591093",
        "2022-11-11T11:47:10.629975",
        "2022-11-11T11:47:13.665937",
        "2022-11-11T11:47:16.704819",
        "2022-11-11T11:47:19.746620",
        "2022-11-11T11:47:22.779664",
        "2022-11-11T11:47:25.815627",
        "2022-11-11T11:47:28.857428",
        "2022-11-11T11:47:31.893391",
        "2022-11-11T11:47:34.935192",
        "2022-11-11T11:47:37.974074",
        "2022-11-11T11:47:41.010037",
        "2022-11-11T11:47:44.051838",
        "2022-11-11T11:47:47.087800",
        "2022-11-11T11:47:50.123763",
        "2022-11-11T11:47:53.162645",
    ]

    range_sampling_rate = 2.502314816000000e07
    range_sampling_time = 1 / range_sampling_rate
    ew3_slant_range_time = 5.556849666167215e-03
    ew3_samples = 8457

    azimuth_zd_times = np.array(
        [tref.from_str(item, unit="s", epoch="2022-11-11T11:47:00") for item in first_line_utc],
        dtype="float64",
    )
    azimuth_tx_times = azimuth_zd_times - 0.5 * (ew3_slant_range_time + ew3_samples * 0.5 * range_sampling_time)

    return {"offsets": azimuth_tx_times, "ref": "UTC", "unit": "s", "epoch": "2022-11-11T11:47:00"}


@pytest.fixture(name="ew1_swath", scope="module")
def given_sentinel1_ew1_swath(ew1_azimuth):
    """
    Fixture to generate a Sentinel 1 context
    """
    return {
        "azimuth_times": ew1_azimuth,
        "azimuth_convention": "TX",
        "azimuth_time_interval": 2.919194958309765e-03,
        "burst_lines": 1168,
        "slant_range_time": 4.969473533235427e-03,
        "range_sampling_rate": 2.502314816000000e07,
        "burst_samples": 8337,
    }


def test_sar_timestamp_model(ew1_swath):
    """
    Unit test for SarTimestampModel.acquisition_times
    """

    model = SarTimestampModel(**ew1_swath)

    assert model.config == ew1_swath

    dataset = {
        "coords": np.array(
            [
                [0, 0],
                [100, 0],
                [5000, 0],
                [0, 100],
                [100, 100],
                [5000, 100],
                [0, 1500],
                [100, 1500],
                [5000, 1500],
            ],
            dtype="int32",
        ),
    }

    model.acquisition_times(dataset)

    assert "times" in dataset
    assert "range_times" in dataset

    ref_azimuth_times = np.array(
        [
            1.51295082,
            1.51295282,
            1.51305073,
            1.80487032,
            1.80487231,
            1.80497022,
            5.52100555,
            5.52100754,
            5.52110545,
        ]
    )
    assert np.allclose(dataset["times"]["offsets"], ref_azimuth_times, rtol=0, atol=1e-6)

    single_range_times = [0.00496947, 0.00497347, 0.00516929]
    ref_range_times = single_range_times + single_range_times + single_range_times
    assert np.allclose(dataset["range_times"], ref_range_times, rtol=0, atol=1e-6)
