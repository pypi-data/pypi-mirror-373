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
S3 L0 Geometry
"""
import numpy as np

from asgard.core.math import apply_rotation_on_vector
from asgard.core.product import (
    AbstractGeometry,
    L0Geometry,
)
from asgard.core.schema import ORBIT_AUX_INFO_SCHEMA
from asgard.models.body import EarthBody
from asgard.models.linedetector import (
    LineDetectorPointingModel,
    LineDetectorTimestampModel,
)
from asgard.models.orbit import GenericOrbitModel
from asgard.models.platform import GenericPlatformModel
from asgard.models.propagation import PropagationModel
from asgard.models.time import compute_offset


class S3L0Geometry(L0Geometry, AbstractGeometry):
    """
    Generic class for L0 geometry
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for constructor, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/S3L0Geometry.schema.json>`
        """
        return {
            "start_time": "string",
            "stop_time": "string",
            "orbit_aux_info": ORBIT_AUX_INFO_SCHEMA,  # Expect orbit data in EME2000 for YSM
            "angles": {
                "nearRange": "float",  # in degrees
                "farRange": "float",  # in degrees
            },
            "pairs_number": "int",
            "required": [
                "start_time",
                "stop_time",
                "orbit_aux_info",
                "angles",
                "pairs_number",
            ],
        }

    def __init__(self, **kwargs):
        """
        S3L0Geometry Constructor
        """
        L0Geometry.__init__(self, **kwargs)

        # Get number of pairs
        self.pairs_number = kwargs["pairs_number"]

        # Get orbit info
        if "orbit_state_vectors" not in kwargs["orbit_aux_info"]:
            raise NotImplementedError(
                "'orbit_state_vectors' are mandatory for S3 Geometry. "
                "Init through OSF is not yet handled in ASGARD, "
                "please use ASGARD-Legacy instead."
            )
        self.orbits = kwargs["orbit_aux_info"]["orbit_state_vectors"]
        assert self.orbits["frame"] == "EME2000"  # YSM need inertial frame

        # Body model
        self.body_model = EarthBody(ellipsoid="WGS84")

        # Orbit model
        orbit_config = {
            "orbit": self.orbits,
            "attitude": {"aocs_mode": "YSM"},
            "earth_body": self.body_model,
        }
        self.orbit_model = GenericOrbitModel(**orbit_config)

        # propagation model: Ellipsoid
        propagation_config = {"earth_body": self.body_model}
        # we could set up the following parameter for better precision
        # body_rotating_frame,light_time_correction,aberration_of_light_correction,atmospheric_refraction
        self.propagation_model = PropagationModel(**propagation_config)

        # Setup instrument list
        # Creation of a 2-pixel detectors, one pointing at nadir, the other off-axis
        self._instr_list = ["virtual_instr"]

        # Setup GenericPlatformModel
        platform_config = {
            "states": [
                {
                    "name": self._instr_list[0],
                    "origin": "platform",
                    "rotation": np.eye(3, 3),
                }
            ]
        }

        self.platform_model = GenericPlatformModel(**platform_config)

        # Setup pointing model
        pointing_config = {
            "unit_vectors": {
                self._instr_list[0]: np.array(
                    [
                        apply_rotation_on_vector(
                            np.array([0, 0, 1]), np.array([1, 0, 0]), -np.deg2rad(kwargs["angles"]["nearRange"])
                        ),  # LOS 1st pixel
                        apply_rotation_on_vector(
                            np.array([0, 0, 1]), np.array([1, 0, 0]), -np.deg2rad(kwargs["angles"]["farRange"])
                        ),  # LOS 2nd pixel
                    ]
                ),
            },
        }
        self.pointing_model = LineDetectorPointingModel(**pointing_config)

        # Setup TimestampModel
        self.start_time = compute_offset(kwargs["start_time"], self.orbits["times"]["UTC"]["epoch"])
        self.stop_time = compute_offset(kwargs["stop_time"], self.orbits["times"]["UTC"]["epoch"])
        self.time_dataset = {
            "times": {
                "offsets": np.linspace(self.start_time, self.stop_time, self.pairs_number),
                "ref": "UTC",
                "epoch": self.orbits["times"]["UTC"]["epoch"],
            },
        }
        self.timestamp_models = {
            self._instr_list[0]: LineDetectorTimestampModel(times=self.time_dataset["times"]),
        }

    def footprint(self) -> np.ndarray:
        """
        Compute S3 L0 product coarse footprint

        :return: geodetics points (): np.ndarray: shape: pairs_numberx2
        """
        coords_nadir = np.zeros((self.pairs_number, 2), dtype=int)
        coords_nadir[:, 1] = np.arange(self.pairs_number, dtype=int)  # col,row

        coords_offaxis = np.ones((self.pairs_number, 2), dtype=int)
        coords_offaxis[:, 1] = np.arange(self.pairs_number, dtype=int)  # col,row

        gp_footprint, _ = self.direct_loc(np.vstack((coords_nadir, coords_offaxis)), "virtual_instr")
        return gp_footprint
