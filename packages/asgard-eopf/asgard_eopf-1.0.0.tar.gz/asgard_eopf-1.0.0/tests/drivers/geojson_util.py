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
Module for GEOJson conversion functions
"""

import json

import numpy as np

from asgard.core.math import antimeridian_crossing, flatten_array


def to_points(arr: np.ndarray, path: str, properties: dict | None = None) -> None:
    """
    Convert an array of WGS84 coordinates to GEOJson MultiPoint

    :param np.ndarray arr: Array of coordinates
    :param str path: Output GEOJson path
    :param dict|None properties: dict of properties to embed
    """

    output = {
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "geometry": {"type": "MultiPoint", "coordinates": []}}],
    }

    if properties:
        output["features"][0]["properties"] = properties

    out_list = output["features"][0]["geometry"]["coordinates"]
    flat_array = flatten_array(arr, 3)
    for point in flat_array:
        lon = ((point[0] + 180.0) % 360.0) - 180.0
        lat = point[1]
        out_list.append([lon, lat])

    with open(path, "w", encoding="utf-8") as out_fd:
        json.dump(output, out_fd)


def to_linestring(arr: np.ndarray, path: str, properties: dict | None = None) -> None:
    """
    Convert an array of WGS84 coordinates to GEOJson Linestring

    :param np.ndarray arr: Array of coordinates
    :param str path: Output GEOJson path
    :param dict|None properties: dict of properties to embed
    """

    output = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "MultiLineString", "coordinates": [[]]},
            }
        ],
    }

    if properties:
        output["features"][0]["properties"] = properties

    out_list = output["features"][0]["geometry"]["coordinates"][0]
    flat_array = flatten_array(arr, 3)
    # init prev with first longitude
    prev = [(flat_array[0, 0] + 180.0) % 360.0 - 180.0, 0.0]
    for point in flat_array:
        lon = ((point[0] + 180.0) % 360.0) - 180.0
        lat = point[1]
        # check antimeridian crossing
        if abs(lon - prev[0]) > 180.0:
            cross_lon, cross_lat = antimeridian_crossing(prev, point)
            out_list.append([cross_lon, cross_lat])
            next_list = [[-cross_lon, cross_lat]]
            output["features"][0]["geometry"]["coordinates"].append(next_list)
            out_list = next_list
        out_list.append([lon, lat])
        prev = [lon, lat]

    with open(path, "w", encoding="utf-8") as out_fd:
        json.dump(output, out_fd)
