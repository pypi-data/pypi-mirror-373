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
Module for Sentinel 3 MWR instrument
"""

import logging

import numpy as np
from scipy.spatial.transform import Rotation as R

from asgard.core.frame import FrameId
from asgard.core.product import AbstractRadarGeometry
from asgard.core.schema import (
    DEM_DATASET_SCHEMA,
    NAVATT_SCHEMA,
    ORBIT_AUX_INFO_SCHEMA,
    TIME_ARRAY_SCHEMA,
    TIMESCALE_NAME_SCHEMA,
)
from asgard.core.time import TimeRef
from asgard.models.body import EarthBody
from asgard.models.linedetector import (
    LineDetectorPointingModel,
    LineDetectorTimestampModel,
)
from asgard.models.orbit import GenericOrbitModel, OrbitScenarioModel
from asgard.models.platform import GenericPlatformModel
from asgard.models.propagation import PropagationModel
from asgard.models.time import TimeReference

logging.getLogger().setLevel(logging.INFO)


class S3MWRGeometry(AbstractRadarGeometry):
    """
    Sentinel 3 MWR product
    """

    def __init__(self, *args, **kwargs):
        # call superclass constructor
        super().__init__(*args, **kwargs)

        self._instr_list = ["C1", "C2"]
        valid_navatt = "navatt" in kwargs
        self.config["valid_navatt"] = valid_navatt

        coord_definition = {
            "frame": len(kwargs["frame"]["times"]["offsets"]),  # scan frame
        }
        self.coordinates = {k: coord_definition for k in self._instr_list}

        # Setup time model
        self.time_model = TimeReference(**kwargs.get("eop", {}))

        # Setup body_model
        self.body_model = EarthBody(ellipsoid="WGS84", time_reference=self.time_model)

        # Setup timestamp model
        line_detector_timestamp = LineDetectorTimestampModel(times=kwargs["frame"]["times"])
        for key in self._instr_list:
            self.timestamp_models[key] = line_detector_timestamp  # noqa: B909

        # detect start/end times
        self.config.setdefault("acquisition_start", kwargs["frame"]["times"]["offsets"][0])
        self.config.setdefault("acquisition_end", kwargs["frame"]["times"]["offsets"][-1])

        # Setup orbit model
        ysm_mode = {"frame": "EME2000", "aocs_mode": "YSM"}
        if "orbit_state_vectors" in kwargs["orbit_aux_info"]:
            orb_list = kwargs["orbit_aux_info"]["orbit_state_vectors"]
            if valid_navatt:
                orb_list.append(kwargs["navatt"]["orbit"])

            for orbit in orb_list:
                orb_frame = orbit.get("frame", "EME2000")
                if orb_frame != "EME2000":
                    logging.warning("Orbit frame used is %s, MWR constructor converts it to EME2000 frame", orb_frame)
                    self.body_model.transform_orbit(orbit, FrameId.EME2000)

            fused_orbit = GenericOrbitModel.merge_orbits(orb_list)
            orbit_config = {
                "orbit": fused_orbit,
                "attitude": kwargs["navatt"]["attitude"] if valid_navatt else ysm_mode,
                "earth_body": self.body_model,
            }
            # Set time_orb with acquisition start
            orbit_config["time_orb"] = "UTC=" + self.time_model.to_str(
                self.config["acquisition_start"],
                ref_in=TimeRef.GPS,
                ref_out=TimeRef.UTC,
                fmt="CCSDSA_MICROSEC",
                unit=self.default_time["unit"],
                epoch=self.default_time["epoch"],
            )
            self.orbit_model = GenericOrbitModel(**orbit_config)
        elif "orbit_scenario" in kwargs["orbit_aux_info"]:  # initialize with OSF
            self.body_model = EarthBody(ellipsoid="WGS84")
            orbit_config = {
                "orbit_scenario": kwargs["orbit_aux_info"]["orbit_scenario"][0],  # Asgard support only one OSF for now
                "orbit_frame": "EME2000",
                "attitude": ysm_mode,
                "earth_body": self.body_model,
            }
            self.orbit_model = OrbitScenarioModel(**orbit_config)
        else:
            raise TypeError("Missing, at least one orbit file")

        # detect start/end times
        if "acquisition_start" not in self.config:
            self.config["acquisition_start"] = kwargs["frame"]["times"]["offsets"][0]
        if "acquisition_end" not in self.config:
            self.config["acquisition_end"] = kwargs["frame"]["times"]["offsets"][-1]
        self._frame_times = np.array(kwargs["frame"]["times"]["offsets"])

        # Setup platform model
        platform_config = {"states": []}

        rotation = np.radians(np.array([-180.0, 0.0, 90.0]))

        for instr in self._instr_list:
            platform_config["states"].append(
                {
                    "name": instr,
                    "origin": "platform",
                    "rotation": rotation,
                    "euler_order": "XYZ",
                }
            )

        self.platform_model = GenericPlatformModel(**platform_config)
        # Setup pointing model
        pointing_config = {
            "unit_vectors": self.init_pointing_angles(
                kwargs["pointing_angles"]["along_angle"],
                kwargs["pointing_angles"]["across_angle"],
            )
        }

        self.pointing_model = LineDetectorPointingModel(**pointing_config)

        # Setup propagation model
        propagation_config = {
            "earth_body": self.body_model,
        }
        self.propagation_model = PropagationModel(**propagation_config)
        self._max_cached_tiles = self.propagation_model.max_cached_tiles

        logging.info("MWR product instantiation succeeded !")

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for constructor, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/S3MWRGeometry.schema.json>`
        :download:`JSON example <doc/scripts/init_schema/examples/S3MWRGeometry.example.json>`
        """

        return {
            "type": "object",
            "properties": {
                "sat": {"type": "string", "pattern": "^SENTINEL_3[A-C]?$"},
                "resources": {
                    "type": "object",
                    "properties": {
                        "geoid": DEM_DATASET_SCHEMA,
                        "dem_path": DEM_DATASET_SCHEMA,
                        "dem_type": {"type": "string"},
                    },
                    "required": ["dem_path", "dem_type"],
                },
                "orbit_aux_info": {
                    "type": "object",
                    "items": ORBIT_AUX_INFO_SCHEMA,
                },
                "abs_orbit": {"type": "integer", "minimum": 0},
                "pointing_angles": {
                    "type": "object",
                    "properties": {
                        "along_angle": {"type": "array", "shape": (2,)},
                        "across_angle": {"type": "array", "shape": (2,)},
                    },
                    "required": ["along_angle", "across_angle"],
                },
                "acquisition_start": {
                    "type": "number",
                    "description": "Acquisition start GPS time (in processing format)",
                },
                "acquisition_end": {
                    "type": "number",
                    "description": "Acquisition end GPS time (in processing format)",
                },
                "frame": {
                    "type": "object",
                    "properties": {
                        "times": TIME_ARRAY_SCHEMA,
                        "ref": TIMESCALE_NAME_SCHEMA,
                    },
                    "required": ["times"],
                },
                "navatt": NAVATT_SCHEMA,
                "eop": TimeReference.init_schema(),
            },
            "required": [
                "sat",
                "orbit_aux_info",
                "pointing_angles",
                "frame",
            ],
        }

    def init_pointing_angles(self, theta_al, theta_ac):
        """
        Compute the pointing angles (azimuth, elevation) in instrument frame for each camera
        :param theta_al: Main antenna beam pointing in along-track direction for channels 1 and 2
        :param theta_ac: Main antenna beam pointing in across-track direction for channels 1 and 2
        """
        pointing_vectors = {}
        for idx, instr in enumerate(self._instr_list):

            # Caution: to obtain the correct pointing vector, reverse the sign of the along-track angles
            # defined in eocfi
            along = -theta_al[idx]
            across = theta_ac[idx]

            nadir = np.array([0.0, 0.0, -1.0], dtype="float64")
            euler_angles = np.stack([along, across, np.zeros(along.shape)], axis=-1)
            rotation = R.from_euler("XYZ", euler_angles, degrees=True)  # xyz=persistent axis <> XYZ=moving axis
            pointing_vectors[instr] = np.expand_dims(rotation.apply(nadir), axis=0)

        return pointing_vectors
