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
S2Band implementation.
"""
from typing import ClassVar

import asgard.sensors.sentinel2.s2_constants as S2C


class S2Band:
    """
    Sentinel-2 band information

    :param str name: name used in ASGARD as Bxx
    :param int index: band index from 0.
    :param int pixel_height:
    :param str focal_plane: VNIR or SWIR.
    """

    VALUES: ClassVar[list] = []
    """
    All possible S2Band static instances

    :meta hide-value:
    """

    def __init__(
        self,
        name: str,
        index: int,
        pixel_height: int,
        focal_plane: str,
    ):
        self.name = name
        self.index = index
        self.pixel_height = pixel_height
        self.focal_plane = focal_plane  # VNIR or SWIR

    @staticmethod
    def from_name(name: str):
        """Return static instance from its ASGARD name"""
        try:
            return [band for band in S2Band.VALUES if band.name == name][0]
        except IndexError as error:
            raise RuntimeError(f"Unknown Sentinel-2 band ASGARD name: {name!r}") from error

    @staticmethod
    def from_index(index: int):
        """Return static instance from its index"""
        try:
            return [band for band in S2Band.VALUES if band.index == index][0]
        except IndexError as error:
            raise RuntimeError(f"Unknown Sentinel-2 band index: {index}") from error


# Init static instances
S2Band.VALUES = [
    S2Band("B01", 0, int(S2C.PIXEL_HEIGHT_60), "VNIR"),
    S2Band("B02", 1, int(S2C.PIXEL_HEIGHT_10), "VNIR"),
    S2Band("B03", 2, int(S2C.PIXEL_HEIGHT_10), "VNIR"),
    S2Band("B04", 3, int(S2C.PIXEL_HEIGHT_10), "VNIR"),
    S2Band("B05", 4, int(S2C.PIXEL_HEIGHT_20), "VNIR"),
    S2Band("B06", 5, int(S2C.PIXEL_HEIGHT_20), "VNIR"),
    S2Band("B07", 6, int(S2C.PIXEL_HEIGHT_20), "VNIR"),
    S2Band("B08", 7, int(S2C.PIXEL_HEIGHT_10), "VNIR"),
    S2Band("B8A", 8, int(S2C.PIXEL_HEIGHT_20), "VNIR"),
    S2Band("B09", 9, int(S2C.PIXEL_HEIGHT_60), "VNIR"),
    S2Band("B10", 10, int(S2C.PIXEL_HEIGHT_60), "SWIR"),
    S2Band("B11", 11, int(S2C.PIXEL_HEIGHT_20), "SWIR"),
    S2Band("B12", 12, int(S2C.PIXEL_HEIGHT_20), "SWIR"),
]
