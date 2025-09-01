#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2023 CS GROUP
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
S1 L0 Geometry
"""
import numpy as np

from asgard.core.math import apply_rotation_on_vector, get_roll_pitch_yaw_EF_axes
from asgard.core.product import L0Geometry
from asgard.core.schema import ORBIT_STATE_VECTORS_SCHEMA
from asgard.models.body import EarthBody
from asgard.models.orbit import GenericOrbitModel
from asgard.models.sar import SarPropagationModel
from asgard.models.time import compute_offset


class S1L0Geometry(L0Geometry):
    """
    Generic class for L0 geometry
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for constructor, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/S1L0Geometry.schema.json>`
        """
        return {
            "start_time": "string",
            "stop_time": "string",
            "orbit_state_vectors": ORBIT_STATE_VECTORS_SCHEMA,  # Expect orbit data in EF
            "angles": {
                "nearRange": {"type": "float", "description": "Near Angle for one side of the Swath. In degrees"},
                "farRange": {"type": "float", "description": "Far Angle for one side of the Swath. In degrees"},
            },
            "look_side": {
                "type": "string",
                "enum": ["LEFT", "RIGHT"],
                "description": "SAR looking side",
            },
            "required": [
                "start_time",
                "stop_time",
                "orbit_state_vectors",
                "angles",
                "look_side",
            ],
        }

    def __init__(self, **kwargs):
        """
        S1L0Geometry Constructor
        """
        super().__init__(**kwargs)

        # Get Beam angle info
        self.beam_angles = kwargs["angles"]

        # Get orbit info
        self.orbits = kwargs["orbit_state_vectors"]
        assert self.orbits["frame"] == "EF", "Expect orbit data in EF, no reprojection supported here"

        # Get start/stop time
        self.start_time = compute_offset(kwargs["start_time"], self.orbits["times"]["UTC"]["epoch"])
        self.stop_time = compute_offset(kwargs["stop_time"], self.orbits["times"]["UTC"]["epoch"])
        self.time_dataset = {
            "times": {
                "offsets": np.array([self.start_time, self.stop_time]),
                "ref": "UTC",
                "epoch": self.orbits["times"]["UTC"]["epoch"],
            },
        }

        # Look side
        self.look_side = -1 if kwargs["look_side"] == "RIGHT" else 1

        # Body model
        self.body_model = EarthBody(ellipsoid="WGS84")

        # orbit model
        orbit_config = {
            "orbit": self.orbits,
            "attitude": {"aocs_mode": "ZD", "frame": "EF"},  # zd=zero doppler
            "earth_body": self.body_model,
        }
        self.orbit_model = GenericOrbitModel(**orbit_config)

        # propagation model: Ellipsoide
        propagation_config = {
            "earth_body": self.body_model,
            "frame": "EF",
        }
        self.propagation_model = SarPropagationModel(**propagation_config)

    def footprint(self) -> np.ndarray:
        """
        Compute L0 product SSP coarse footprint

        :return: geodetics points (UL UR LR LL): np.ndarray:4x2
        """
        # get satellite position in EF cartesian
        self.orbit_model.get_osv(self.time_dataset, fields_out=["position", "velocity"])

        pos_start_time = self.time_dataset["position"][0]
        pos_stop_time = self.time_dataset["position"][1]
        vel_start_time = self.time_dataset["velocity"][0]
        vel_stop_time = self.time_dataset["velocity"][1]

        # Rotation axes start time (normalised)
        roll_axes_in_EF_start_time_norm, _, _ = get_roll_pitch_yaw_EF_axes(pos_start_time, vel_start_time)

        # Rotation axes stop time (normalised)
        roll_axes_in_EF_stop_time_norm, _, _ = get_roll_pitch_yaw_EF_axes(pos_stop_time, vel_stop_time)

        # Rotation by beam angle
        beam_nom_near = np.radians(self.look_side * self.beam_angles["nearRange"])
        beam_nom_far = np.radians(self.look_side * self.beam_angles["farRange"])

        los_start_time_near = apply_rotation_on_vector(-pos_start_time, roll_axes_in_EF_start_time_norm, beam_nom_near)
        los_start_time_far = apply_rotation_on_vector(-pos_start_time, roll_axes_in_EF_start_time_norm, beam_nom_far)

        los_stop_time_near = apply_rotation_on_vector(-pos_stop_time, roll_axes_in_EF_stop_time_norm, beam_nom_near)
        los_stop_time_far = apply_rotation_on_vector(-pos_stop_time, roll_axes_in_EF_stop_time_norm, beam_nom_far)

        # direct location
        gp_start_near = np.degrees(
            self.propagation_model.ellipsoid.point_on_ground(
                position=pos_start_time, los=los_start_time_near, central_longitude=None
            )
        )
        gp_start_far = np.degrees(
            self.propagation_model.ellipsoid.point_on_ground(
                position=pos_start_time, los=los_start_time_far, central_longitude=None
            )
        )
        gp_stop_near = np.degrees(
            self.propagation_model.ellipsoid.point_on_ground(
                position=pos_stop_time, los=los_stop_time_near, central_longitude=None
            )
        )
        gp_stop_far = np.degrees(
            self.propagation_model.ellipsoid.point_on_ground(
                position=pos_stop_time, los=los_stop_time_far, central_longitude=None
            )
        )

        return np.array([gp_start_far, gp_start_near, gp_stop_near, gp_stop_far])
