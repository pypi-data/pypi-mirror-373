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
S2geoGippSpamod implementation.
"""
from collections import defaultdict

import numpy as np
from drivers.xml_util import XmlUtil

from asgard.sensors.sentinel2.s2_detector import S2Detector


class S2geoGippSpamod:
    """
    S2Geo GIPP legacy loader for the spacecraft model parameters.

    :param d_config: output configuration JSON values
    """

    def __init__(self, d_config: dict):
        self.d_config = d_config

    def read_spacecraft(self, gip_spamod_path: str):
        """Init a class instance from a GIPP SPAMOD file"""

        # If the GIPP file is missing, do nothing
        if gip_spamod_path is None:
            return

        # Read XML file. Remove namespaces to facilitate reading.
        x_spamod = XmlUtil.read_with_etree(gip_spamod_path, remove_namespaces=True)

        # Init python lists
        piloting_to_msi = None  # single transform
        msi_to_focalplane = {}  # one by focal plane
        focalplane_to_sensor = defaultdict(dict)  # one by focal plane and detector

        # Read the spacecraft to MSI frame transformation
        piloting_to_msi = self.read_spamod_transformation(x_spamod.find("DATA/PILOTING_TO_MSI_FRAME"), combi_scale=True)

        # For each VNIR or SWIR detector
        for focal_plane in ["VNIR", "SWIR"]:
            # Read the MSI to focal plane transformations
            msi_to_focalplane[focal_plane] = self.read_spamod_transformation(
                x_spamod.find(f"DATA/MSI_TO_FOCAL_PLANE/MSI_TO_{focal_plane}"),
                combi_scale=True,
            )

            # For each detector
            for detector in S2Detector.VALUES:
                # Detector ID = detector name
                x_detector = x_spamod.find(
                    f"DATA/FOCAL_PLANE_TO_DETECTOR/FOCAL_PLANE_TO_DETECTOR_{focal_plane}"
                    f"[@detector_id={detector.legacy_name!r}]"
                )
                assert x_detector is not None

                # Read the focal plane to detector transformations
                focalplane_to_sensor[focal_plane][detector.name] = self.read_spamod_transformation(
                    x_detector, combi_scale=False
                )

        # group transformations together
        self.d_config["spacecraft"] = {
            "piloting_to_msi": self.gather_transforms(piloting_to_msi),
            "msi_to_focalplane": self.gather_transforms(msi_to_focalplane),
            "focalplane_to_sensor": self.gather_transforms(focalplane_to_sensor),
        }

    @staticmethod
    def read_spamod_transformation(x_node, combi_scale: bool) -> dict:
        """
        Read spacecraft model transformation from an XML node.

        :param x_node: XML node to read
        :param combi_scale: read combination order and scale ?
        """

        if x_node is None:
            return None

        # Read rotation values in X/Y/Z
        rotations = []
        axis = []
        units = []
        for x_rotation in (x_node.find("R1"), x_node.find("R2"), x_node.find("R3")):
            rotations.append(float(x_rotation.text))
            axis.append(x_rotation.get("axis"))
            units.append(x_rotation.get("unit"))

        # Read combination order and scale
        if combi_scale:
            combination_order = x_node.find("COMBINATION_ORDER").text
            if combination_order not in ("ROTATION_THEN_SCALE", "SCALE_THEN_ROTATION"):
                combination_order = "NO_SCALE"
            scale = float(x_node.find("SCALE_FACTOR").text)

        # Else, use default values
        else:
            combination_order = "NO_SCALE"
            scale = 1.0

        return {
            "rotations": {
                "values": rotations,
                "axis": axis,
                "units": units,
            },
            "combination_orders": combination_order,
            "scale_factors": scale,
        }

    @staticmethod
    def gather_transforms(transform_tree, level: int = 0) -> dict:
        """
        Group a tree of transforms into a transform containing arrays

        :param dict transform_tree: dict of transforms (support 0, 1 or 2 sub-levels)
        :param int level: current level inside the main tree
        :return: transform dict with arrays of values
        """

        output = {}

        values = []
        axis = []
        units = []
        order = []
        scale = []

        if "rotations" in transform_tree:
            # Already a transform dict, return it
            values = transform_tree["rotations"]["values"]
            axis = transform_tree["rotations"]["axis"]
            units = transform_tree["rotations"]["units"]
            order = transform_tree["combination_orders"]
            scale = transform_tree["scale_factors"]
        else:
            level_names = ["col_names", "row_names", "xxx"]
            cur_name = level_names[level]
            output[cur_name] = []

            keys = []
            for key, val in transform_tree.items():
                fused_val = S2geoGippSpamod.gather_transforms(val, level=level + 1)
                keys.append(key)

                values.append(fused_val["rotations"]["values"])
                axis.append(fused_val["rotations"]["axis"])
                units.append(fused_val["rotations"]["units"])
                order.append(fused_val["combination_orders"])
                scale.append(fused_val["scale_factors"])

                for name in level_names[level + 1 :]:
                    if name in fused_val:
                        output[name] = fused_val[name]

            # prepare output dict
            output[cur_name] = keys

        output["rotations"] = {}
        if level == 0:
            # list to numpy arrays
            output["rotations"]["values"] = np.array(values)
            output["rotations"]["axis"] = np.array(axis)
            output["rotations"]["units"] = np.array(units)
            output["combination_orders"] = order if isinstance(order, str) else np.array(order)
            output["scale_factors"] = scale if isinstance(scale, float) else np.array(scale)
        else:
            output["rotations"]["values"] = values
            output["rotations"]["axis"] = axis
            output["rotations"]["units"] = units
            output["combination_orders"] = order
            output["scale_factors"] = scale

        return output
