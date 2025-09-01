#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022 CS GROUP
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
Module to define celestial frames
"""

from enum import Enum


class FrameId(Enum):
    """
    Enumeration of different reference frames
    """

    GCRF = 1  # Geocentric Celestial Reference Frame
    EME2000 = 2  # Geocentric mean of 2000, also known as J2000
    MOD = 3  # Mean of Date
    TOD = 4  # True of Date
    EF = 5  # Earth-Fixed, implemented by ITRF
    EF_EQUINOX = 6  # Earth-Fixed, based on older equinox paradigm
    GTOD = 7  # Greenwitch True of Date (named Pseudo Earth-Fixed in EOCFI)
