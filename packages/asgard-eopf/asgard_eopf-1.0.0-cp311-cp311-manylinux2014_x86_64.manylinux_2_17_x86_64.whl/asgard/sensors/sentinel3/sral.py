#!/usr/bin/env python
# coding: utf8
#
# Copyright 2024 CS GROUP
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
Module for Sentinel-3 SRAL instrument
"""

import logging

import numpy as np

from asgard.core.frame import FrameId
from asgard.core.math import flatten_array
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
from asgard.models.linedetector import LineDetectorTimestampModel
from asgard.models.orbit import GenericOrbitModel, OrbitScenarioModel
from asgard.models.time import TimeReference

logger = logging.getLogger(__name__)


class S3SRALGeometry(AbstractRadarGeometry):
    """
    Sentinel 3 SRAL product
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        # call superclass constructor
        super().__init__(*args, **kwargs)

        valid_navatt = "navatt" in kwargs
        self.config["valid_navatt"] = valid_navatt

        coord_definition = {
            "frame": len(kwargs["frame"]["times"]["offsets"]),  # scan frame
        }
        self.coordinates = {"default": coord_definition}

        # Setup time model
        self.time_model = TimeReference(**kwargs.get("eop", {}))

        # Setup body_model
        self.body_model = EarthBody(ellipsoid="WGS84", time_reference=self.time_model)

        # Setup timestamp model
        line_detector_timestamp = LineDetectorTimestampModel(times=kwargs["frame"]["times"])
        for key in self._instr_list:
            self.timestamp_models[key] = line_detector_timestamp

        # detect start/end times
        self.config.setdefault("acquisition_start", kwargs["frame"]["times"]["offsets"][0])
        self.config.setdefault("acquisition_end", kwargs["frame"]["times"]["offsets"][-1])

        # Setup orbit model
        if "orbit_state_vectors" in kwargs["orbit_aux_info"]:
            orb_list = kwargs["orbit_aux_info"]["orbit_state_vectors"]
            if valid_navatt:
                orb_list.append(kwargs["navatt"]["orbit"])

            for orbit in orb_list:
                orb_frame = orbit.get("frame", "")
                if orb_frame != FrameId.EF.name:
                    logger.warning(
                        "Orbit frame used is %r, SRAL constructor converts it to Earth-Fixed frame", orb_frame
                    )
                    # Transform orbit to Earth-Fixed frame
                    self.body_model.transform_orbit(orbit, FrameId.EF)

            fused_orbit = GenericOrbitModel.merge_orbits(orb_list)

            orbit_config = {
                "orbit": fused_orbit,
                "attitude": kwargs["navatt"]["attitude"] if valid_navatt else None,
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
        elif "orbit_scenario" in kwargs["orbit_aux_info"]:
            self.body_model = EarthBody(ellipsoid="WGS84")
            orbit_config = {
                "orbit_scenario": kwargs["orbit_aux_info"]["orbit_scenario"][0],  # use first OSF
                "orbit_frame": "EF",
                "attitude": {  # not used
                    "aocs_mode": "YSM",
                    "frame": "EME2000",
                },
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

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for constructor, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/S3SRALGeometry.schema.json>`

        :download:`JSON example <doc/scripts/init_schema/examples/S3SRALGeometry.example.json>`
        """
        return {
            "type": "object",
            "properties": {
                "sat": {"type": "string", "pattern": "^SENTINEL_3[A-C]?$"},
                "orbit_aux_info": {
                    "type": "object",
                    "items": ORBIT_AUX_INFO_SCHEMA,
                },
                "abs_orbit": {"type": "integer", "minimum": 0},
                "resources": {
                    "type": "object",
                    "properties": {
                        "geoid": DEM_DATASET_SCHEMA,
                        "dem_path": DEM_DATASET_SCHEMA,
                        "dem_type": {"type": "string"},
                    },
                    "required": ["dem_path", "dem_type"],
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
                "frame",
            ],
        }

    def compute_altitude_rate(self, coordinates, eps_value: float = 1e-5):
        """
        Implementation of altitude rate computation
        """
        flat_coord = flatten_array(coordinates, 2)

        #  - compute JD_f : frame times and unique times
        times = self._frame_times[flat_coord[..., 1]]
        dataset = {"times": {"offsets": times}}

        self.orbit_model.get_osv(dataset, fields_out=["positions", "velocities"])
        pos_next = dataset.copy()

        ground = self.body_model.cartesian_to_geodetic(dataset, field_in="positions", field_out="geod_pos")

        eps = np.full(ground["positions"].shape, eps_value)
        pos_next["positions"] = ground["positions"] + ground["velocities"] * eps

        # Change coordinate system to compute altitude rate
        ground_next = self.body_model.cartesian_to_geodetic(pos_next, field_in="positions", field_out="geod_pos")

        # Compute of altitude rate
        altitude_rate = (ground_next["geod_pos"][:, -1] - ground["geod_pos"][:, -1]) / eps_value

        return altitude_rate

    def direct_loc(
        self,
        coordinates,
        geometric_unit: str | None = None,
        altitude: float | None = None,
        sort_lines: bool = False,
    ) -> np.ndarray:
        """
        Compute direct location for SRAL product, note that this instrument does not need
        propagation model and DEM as it is using only orbit state vector of the satellite
        because of his nadir view
        """
        assert list(self.coordinates.keys())[0] == "default"
        if self.orbit_model.frame != FrameId.EF:
            raise ValueError("Please transform orbit to Earth-Fixed frame")

        # Compute a direct location using get_osv
        flat_coord = flatten_array(coordinates, 2)

        times = self._frame_times[flat_coord[..., 1]]
        dataset = {"times": {"offsets": times}}

        self.orbit_model.get_osv(dataset, fields_out=["positions", "velocities"])

        assert dataset["positions"].shape[0] == len(times)

        self.body_model.cartesian_to_geodetic(dataset, field_in="positions")

        if altitude is not None:
            dataset["positions"][:, 2] = altitude

        return dataset["positions"]

    def incidence_angles(self, ground_coordinates: np.ndarray, times: np.ndarray) -> np.ndarray:
        """
        As SRAL is nadir view the incidence angles are equal to zero
        """
        return np.zeros(ground_coordinates[..., :2].shape)

    def viewing_angles(self, ground_coordinates: np.ndarray, times: np.ndarray) -> np.ndarray:
        """
        As SRAL is nadir view the viewing angles are equal to zero
        """
        return np.zeros(ground_coordinates[..., :2].shape)
