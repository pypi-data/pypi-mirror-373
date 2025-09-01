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
S2geoRefining implementation.
"""

from typing import Tuple

import numpy as np
from org.hipparchus.analysis.polynomials import (  # pylint: disable=import-error
    PolynomialFunction,
)
from org.orekit.data import DataContext  # pylint: disable=import-error
from org.orekit.time import AbsoluteDate  # pylint: disable=import-error


class S2geoRefining:
    """
    Refining information.

    :param is_refined:          refining flag
    :param j_acq_center_time:   acquisition center time (=mean time)
    :param spacecraft_position: [x,y,z] spacecraft positions (expressed in meters) in the local spacecraft
                                reference frame (EVG Euclidium state)
    :param d_config:            output configuration JSON values
    """

    def __init__(self, d_config: dict, context: DataContext):
        # Default values
        self.is_refined: bool = False
        self.j_acq_center_time: AbsoluteDate = None
        self.spacecraft_position = [None] * 3
        self.d_config: dict = d_config

        # initialize Orekit resources
        self.utc = context.getTimeScales().getUTC()

    @staticmethod
    def read_coefs(x_uncertain, to_poly: bool, *axis: Tuple[str]):
        """Read X,Y,Z values from XML into JSON"""

        coefs = []
        d_coefs = {}
        for this_axis in axis:
            # Read XML value for current axis
            x_coefs = x_uncertain.find(f"{this_axis}/COEFFICIENTS")

            # Convert space-separated string values to floats
            axis_coefs = [float(s) for s in x_coefs.text.split()]

            # Convert to Java polynomial functions
            if to_poly:
                coefs.append(PolynomialFunction(axis_coefs.jarray()))

            # Convert to JSON dict numpy array
            d_coefs[this_axis.lower()] = np.array(axis_coefs, np.double)

        if to_poly:
            return coefs, d_coefs
        return d_coefs

    def read_from_datastrip(self, x_root):
        """
        Read refining info from the datastrip XML file.

        :param x_root: XML root node read with lxml.objectify
        """

        # No refining by default
        self.is_refined = False

        # If the refining XML node is missing, do nothing more
        x_refining = x_root.find("Image_Data_Info/Geometric_Info/Image_Refining")
        if x_refining is None:
            return

        # If the XML node value is not REFINED, do nothing more
        if x_refining.get("flag").upper() != "REFINED":
            return

        # Else we are refining
        self.is_refined = True

        # Init JSON node
        d_refining = self.d_config["refining"]

        # Datastrip start and stop time
        x_time_info = x_root.find("General_Info/Datastrip_Time_Info")

        # Compute acquisition center time: the refining corrections are computed relative to this time.
        # Read absolute date values (from Gregorian to UTC scale)
        j_start_date = AbsoluteDate(x_time_info.find("DATASTRIP_SENSING_START").text, self.utc)
        j_stop_date = AbsoluteDate(x_time_info.find("DATASTRIP_SENSING_STOP").text, self.utc)

        # half datastrip duration (no test performed if the value is > 0)
        half_duration = j_stop_date.durationFrom(j_start_date) / 2

        # acquisition center time
        # Polynomial model of refining corrections are computed with that the time centered on this value;
        # i.e. this time is 0 for the polynoms
        self.j_acq_center_time = AbsoluteDate(j_start_date, half_duration)
        d_refining["center_time"] = {"UTC": self.j_acq_center_time.toString(self.utc)}

        # If the corrections are missing, do nothing more.
        # TBN: the list will always contain only one item although the XSD structure
        # (no node name="focal_plane_id_unique")
        x_correction = x_root.find("Image_Data_Info/Geometric_Info/Refined_Corrections_List/Refined_Corrections")
        if x_correction is None:
            return

        # Note: Spacecraft_Position and Focal_Plane_State don't seem to be used.

        # Read the spacecraft position.
        # The polynomial functions are used when reading the position/velocity values from the datastrip.
        x_uncertain = x_correction.find("Spacecraft_Position")
        try:
            self.spacecraft_position, d_coefs = self.read_coefs(x_uncertain, True, "X", "Y", "Z")
            d_refining["spacecraft_position"] = d_coefs
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        # Read other uncertainty values
        for xpath, json_fields, axis in (
            ("MSI_State/Rotation", ("msi_state", "rotation"), ("X", "Y", "Z")),
            ("MSI_State/Homothety", ("msi_state", "homothety"), ("Z",)),
            (
                "Focal_Plane_State[@focalPlaneId='VNIR']/Rotation",
                ("focalplane_state", "VNIR", "rotation"),
                ("X", "Y", "Z"),
            ),
            (
                "Focal_Plane_State[@focalPlaneId='VNIR']/Homothety",
                ("focalplane_state", "VNIR", "homothety"),
                ("Z",),
            ),
            (
                "Focal_Plane_State[@focalPlaneId='SWIR']/Rotation",
                ("focalplane_state", "SWIR", "rotation"),
                ("X", "Y", "Z"),
            ),
            (
                "Focal_Plane_State[@focalPlaneId='SWIR']/Homothety",
                ("focalplane_state", "SWIR", "homothety"),
                ("Z",),
            ),
        ):
            x_uncertain = x_correction.find(xpath)
            if x_uncertain is not None:
                d_coefs = d_refining
                for field in json_fields[:-1]:
                    d_coefs = d_coefs[field]
                d_coefs[json_fields[-1]] = self.read_coefs(x_uncertain, False, *axis)
