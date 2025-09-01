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
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Module for Body abstraction
"""

from abc import abstractmethod
from enum import Enum
from typing import List, Tuple

from numpy import ndarray

from asgard.core.frame import FrameId

from .model import AbstractModel


class BodyId(Enum):
    """
    Enumeration of different types of celestial body
    """

    EARTH = 1
    SUN = 2
    MOON = 3


class CoordinateType(Enum):
    """
    Enumeration of different types of coordinates relative to a celestial body
    """

    CARTESIAN = 1
    GEODETIC = 2
    GEOCENTRIC = 3  # may not be useful


BODY_GEOMETRY_SCHEMA = {
    "type": "object",
    "properties": {
        "equatorial_radius": {"type": "number"},
        "flattening": {"type": "number"},
    },
    "required": ["equatorial_radius", "flattening"],
}


class AbstractBody(AbstractModel):
    """
    Abstract body class, represent a celestial body (Earth, Moon, Sun)
    """

    @abstractmethod
    def convert(
        self,
        point_3d: ndarray,
        coord_in: CoordinateType = CoordinateType.CARTESIAN,
        coord_out: CoordinateType = CoordinateType.GEODETIC,
    ) -> ndarray:
        """
        Transform between coordinate systems

        :param point_3d: ndarray with 3 coordinates
        :param coord_in: Type of input coordinates
        :param coord_out: Type of output coordinates
        :return: Array of transformed coordinates
        """

    @abstractmethod
    def cartesian_to_geodetic(
        self,
        dataset,
        field_in: str = "position",
        field_out: str = None,
    ):
        """
        Transform cartesian coordinates to geodetic coordinates

        :param dataset: Dataset with:

            - "<field_in>" array of 3D coordinates to transform
        :param field_in: Name of the table to transform (expect 3D coordinates)
        :param field_out: Name of output field (optional).
        :return: same dataset with transformed coordinates
        """

    @abstractmethod
    def geodetic_to_cartesian(
        self,
        dataset,
        field_in: str = "position",
        field_out: str = None,
    ):
        """
        Transform to cartesian coordinate systems

        :param dataset: Dataset with:

            - "<field_in>" array of 3D coordinates to transform
        :param field_in: Name of the table to transform (expect 3D coordinates)
        :param field_out: Name of output field (optional).
        :return: same dataset with transformed coordinates
        """

    @abstractmethod
    def geodetic_distance(self, lon1, lat1, lon2, lat2, height) -> Tuple[float, float, float]:
        """
        Compute geodetic distance between 2 geodetic coordinates

        :param lon1: Geodetic longitude of point 1
        :param lat1: Geodetic lattitude of point 1
        :param lon2: Geodetic longitude of point 2
        :param lat2: Geodetic lattitude of point 2
        :param height: Geodetic height
        :return: Tuple with geodetic distance (m), and relative azimths (1_to_2, and 2_to_1)
        """

    @abstractmethod
    def change_reference_frame(
        self,
        dataset,
        frame_in: FrameId = FrameId.EME2000,
        frame_out: FrameId = FrameId.EF,
        fields_in: List[str] = ("times", "position"),
        fields_out: List[str] = None,
    ):
        """
        Convert coordinates between frames

        :param dataset: Dataset with the fields to transform
        :param frame_in: Input frame (see FrameId enum)
        :param frame_out: Output frame (see FrameId enum)
        :param fields_in: List of input field names, with the following order:

            - [REQUIRED] times (in processing format)
            - [REQUIRED] position (cartesian X/Y/Z)
            - [OPTIONAL] velocity (cartesian X/Y/Z)
            - [OPTIONAL] acceleration (cartesian X/Y/Z)

        :param fields_out: List of output field names, in the order [position, velocity, acceleration].
                     As for inputs, velocity and acceleration are optional.
        :return: array of converted coordinates
        """
