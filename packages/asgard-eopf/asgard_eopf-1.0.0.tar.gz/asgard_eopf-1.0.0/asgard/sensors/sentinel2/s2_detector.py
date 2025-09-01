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
S2Detector implementation.
"""
from typing import ClassVar


class S2Detector:
    """
    Sentinel-2 detector information.

    :param str legacy_name: name used in Sentinel-2 as xx
    """

    VALUES: ClassVar[list] = []
    """
    All possible S2Detector static instances

    :meta hide-value:
    """

    def __init__(self, legacy_name: str):
        #: name used in Sentinel-2 as xx
        self.legacy_name: str = legacy_name  # xx
        #: name used in ASGARD as Dxx
        self.name: str = "D" + legacy_name  # Dxx

    @staticmethod
    def from_legacy_name(legacy_name: str):
        """Return static instance from its legacy name"""
        try:
            return [detector for detector in S2Detector.VALUES if detector.legacy_name == legacy_name][0]
        except IndexError as error:
            raise RuntimeError(f"Unknown Sentinel-2 detector name: {legacy_name!r}") from error

    @staticmethod
    def from_name(name: str):
        """Return static instance from its ASGARD name"""
        try:
            return [detector for detector in S2Detector.VALUES if detector.name == name][0]
        except IndexError as error:
            raise RuntimeError(f"Unknown Sentinel-2 detector ASGARD name: {name!r}") from error


# Init static instances from legacy_name: 01, 02, ... 12
S2Detector.VALUES = [S2Detector(f"{detector:02d}") for detector in range(1, 13)]
