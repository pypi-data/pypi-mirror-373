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
S2Sensor implementation.
"""

from typing import Union

from asgard.sensors.sentinel2.s2_band import S2Band
from asgard.sensors.sentinel2.s2_detector import S2Detector


# pylint: disable=too-few-public-methods
class S2Sensor:
    """
    One Sentinel-2 sensor = the combination of one detector + one band.
    """

    def __init__(self, arg1: Union[S2Detector, str], band: S2Band | None = None):
        """
        Contructor from either a detector+band or sensor name.

        :param S2Detector|str arg1: Sentinel-2 detector or name used in ASGARD as B0x/D0y
        :param S2Band|None band: Sentinel-2 band (if arg1 = detector)
        """
        self.detector: S2Detector = None
        self.band: S2Band = None
        self.name: str = None

        # From detector + band
        if isinstance(arg1, S2Detector):
            self._from_detector(arg1, band)

        # From sensor name
        elif isinstance(arg1, str):
            self._from_str(arg1)

        else:
            raise ValueError(f"Invalid sensor arguments: {arg1!r}, {band!r}")

    def _from_detector(self, det: S2Detector, band: S2Band | None) -> None:
        """
        Reset instance from S2Detector and S2Band

        :param S2Detector det: S2Detector instance
        :param S2Band band: S2Band instance
        """
        if band is None:
            raise ValueError("Band is missing")
        self.detector = det
        self.band = band
        self.name = self.band.name + "/" + self.detector.name

    def _from_str(self, sensor_name: str) -> None:
        """
        Reset instance from string

        :param str sensor_name: string representation of sensor "band/detector"
        """
        # From ASGARD name
        if "/" in sensor_name:
            # Split by /
            band_name, detector_name = sensor_name.split("/")

            detector = S2Detector.from_name(detector_name)
            band = S2Band.from_name(band_name)

        else:
            raise ValueError(f"Unrecognized sensor name: {sensor_name!r}")

        # Call constructor from detector and band
        self._from_detector(detector, band)
