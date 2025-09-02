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
Sentinel-2 constant values.
"""

#: Pixel size for band (in meters)
PIXEL_HEIGHT_10 = 10.0
#: Pixel size for band (in meters)
PIXEL_HEIGHT_20 = 20.0
#: Pixel size for band (in meters)
PIXEL_HEIGHT_60 = 60.0

#: Granule line (for a 10m resolution band)
GRANULE_NB_LINE_10_M = 2304.0
#: Granule line (for a 60m resolution band) ??
GRANULE_NB_LINE_60_M = 384.0

#: The interval is split in 1/4 parts.
MINMAX_LINES_INTERVAL_QUARTER = 10.0 * GRANULE_NB_LINE_10_M
#: Number of lines between min/max line for inverse computation (for a 10m resolution band)
MINMAX_LINES_INTERVAL = 4.0 * MINMAX_LINES_INTERVAL_QUARTER
