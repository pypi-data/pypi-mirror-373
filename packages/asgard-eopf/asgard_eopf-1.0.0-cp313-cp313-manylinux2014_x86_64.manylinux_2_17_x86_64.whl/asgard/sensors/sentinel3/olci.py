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
Module for Sentinel 3 OLCI instrument
"""

import logging

import numpy as np

from asgard.core.body import BodyId
from asgard.core.frame import FrameId

# from asgard.core.logger import format_as_tree
from asgard.core.math import flatten_array, restore_array
from asgard.core.product import AbstractOpticalGeometry
from asgard.core.schema import (
    DEM_DATASET_SCHEMA,
    NAVATT_SCHEMA,
    ORBIT_AUX_INFO_SCHEMA,
    TIME_ARRAY_SCHEMA,
    TIMESCALE_NAME_SCHEMA,
)
from asgard.core.time import JD_TO_SECONDS, TimeRef
from asgard.core.transform import RigidTransform
from asgard.models.body import EarthBody
from asgard.models.linedetector import (
    LineDetectorPointingModel,
    LineDetectorTimestampModel,
)
from asgard.models.orbit import GenericOrbitModel, OrbitScenarioModel
from asgard.models.platform import GenericPlatformModel
from asgard.models.propagation import PropagationModel
from asgard.models.thermoelastic import ThermoelasticModel
from asgard.models.time import TimeReference

logger = logging.getLogger("asgard.models.orbit")


class S3OLCIGeometry(AbstractOpticalGeometry):
    """
    Sentinel 3 OLCI product
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        # call superclass constructor
        super().__init__(*args, **kwargs)
        # logger.debug("S3OLCIGeometry() <-- %s", format_as_tree(self.config))

        self._instr_list = ["C1", "C2", "C3", "C4", "C5"]
        valid_navatt = "navatt" in kwargs
        self.config["valid_navatt"] = valid_navatt

        coord_definition = {
            "pixel": 740,  # pixel position on detector
            "frame": len(kwargs["frame"]["times"]["offsets"]),  # scan frame
        }
        # TODO: document the time unit for frame input
        self.coordinates = {k: coord_definition for k in self._instr_list}

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

        # Set time_orb with acquisition start
        time_orb = "UTC=" + self.time_model.to_str(
            self.config["acquisition_start"],
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
            fmt="CCSDSA_MICROSEC",
            unit=self.default_time["unit"],
            epoch=self.default_time["epoch"],
        )

        # Setup orbit model
        if "orbit_state_vectors" in kwargs["orbit_aux_info"]:
            orb_list = kwargs["orbit_aux_info"]["orbit_state_vectors"]
            if valid_navatt:
                orb_list.append(kwargs["navatt"]["orbit"])
            for orbit in orb_list:
                orb_frame = orbit.get("frame", "EME2000")
                if orb_frame != "EME2000":
                    logging.warning("Orbit frame used is %s, OLCI constructor converts it to EME2000 frame", orb_frame)
                    self.body_model.transform_orbit(orbit, FrameId.EME2000)

            fused_orbit = GenericOrbitModel.merge_orbits(orb_list)
            orbit_config = {
                "orbit": fused_orbit,
                "attitude": kwargs["navatt"]["attitude"] if valid_navatt else None,
                "earth_body": self.body_model,
                "time_orb": time_orb,
            }

            self.orbit_model = GenericOrbitModel(**orbit_config)
        elif "orbit_scenario" in kwargs["orbit_aux_info"]:  # initialize with OSF
            self.body_model = EarthBody(ellipsoid="WGS84")
            orbit_config = {
                "orbit_scenario": kwargs["orbit_aux_info"]["orbit_scenario"][0],
                "orbit_frame": "EME2000",
                "attitude": {
                    "aocs_mode": "YSM",
                    "frame": "EME2000",
                },
                "earth_body": self.body_model,
                "time_orb": time_orb,
            }

            self.orbit_model = OrbitScenarioModel(**orbit_config)
        else:
            raise TypeError("Missing, at least one orbit file")

        orb_info = self.orbit_model.info

        # Setup platform model
        platform_config = {"states": []}

        # on-orbit position LUT
        if valid_navatt:
            lut_times = np.unique(self.config["navatt"]["times"]["offsets"])
            lut_oop = np.unique(self.config["navatt"]["oop"])
        else:
            # build a custom LUT based on start/end acquisition
            lut_times = np.arange(
                self.config["acquisition_start"] - 4 / JD_TO_SECONDS,
                self.config["acquisition_end"] + 4 / JD_TO_SECONDS,
                1 / JD_TO_SECONDS,
            )
            lut_oop = self.orbit_model.position_on_orbit({"offsets": lut_times})

        # Initialize computations for Sat_to_OLCI_Trans at JD_mid = JD_anx + Torb / 2
        thermoelastic = ThermoelasticModel(
            thermoelastic=kwargs["thermoelastic"],
            doy=(orb_info["utc_anx"] + orb_info["period_jd"] / 2.0) % 365.24,
            instruments=self._instr_list,
            lut_times=lut_times,
            lut_oop=lut_oop,
        )
        # Thermoelastic quaternions are in the direction OLCI_to_S3, but the thermoelastic model
        # already invert them, so we need to invert twice
        thermoelastic = thermoelastic.inv()
        # TODO : or we remove the inversion in ThermoelasticModel
        thermo_map = thermoelastic.split()

        for cam, thermo in thermo_map.items():
            platform_config["states"].append(
                {
                    "name": cam,
                    "origin": "platform",
                    "time_based_transform": thermo,
                }
            )
        # record a special state "all_cam" for the average of thermoelastic effects
        platform_config["states"].append(
            {
                "name": "all_cam",
                "origin": "platform",
                "time_based_transform": thermoelastic,
            }
        )
        self.platform_model = GenericPlatformModel(**platform_config)

        # Setup pointing model
        pointing_config = {
            "unit_vectors": self.init_pointing_angles(
                kwargs["pointing_vectors"]["X"],
                kwargs["pointing_vectors"]["Y"],
            )
        }
        self.pointing_model = LineDetectorPointingModel(**pointing_config)

        # Setup propagation model
        propagation_config = self.config.get("models", {}).get("propagation", {})
        propagation_config["earth_body"] = self.body_model
        if "geoid" in kwargs["resources"]:
            propagation_config["geoid_path"] = kwargs["resources"]["geoid"]
        self.config["dem_type"] = kwargs["resources"].get("dem_type", "ZARR")

        if self.config["dem_type"] == "ZARR":
            propagation_config.setdefault("zarr_dem", {})
            propagation_config["zarr_dem"]["path"] = kwargs["resources"]["dem_path"]
        else:
            propagation_config["native_dem"] = {
                "path": kwargs["resources"]["dem_path"],
                "source": self.config["dem_type"],
                "overlapping_tiles": bool(self.config["dem_type"] == "SRTM"),
            }
        self.propagation_model = PropagationModel(**propagation_config)

        # Can be done after if too long ...
        # ~ for instr in self._instr_list:
        # ~ self._init_predictor(instr)

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for constructor, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/S3OLCIGeometry.schema.json>`

        :download:`JSON example <doc/scripts/init_schema/examples/S3OLCIGeometry.example.json>`
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
                "pointing_vectors": {
                    "type": "object",
                    "properties": {
                        "X": {"type": "array", "shape": (5, 740)},
                        "Y": {"type": "array", "shape": (5, 740)},
                    },
                    "required": ["X", "Y"],
                },
                "thermoelastic": ThermoelasticModel.get_schema(5),
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
                "models": {
                    "type": "object",
                    "properties": {
                        "propagation": {
                            "type": "object",
                            "description": "Settings passed to underlying PropagationModel",
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "required": [
                "sat",
                "orbit_aux_info",
                "resources",
                "pointing_vectors",
                "thermoelastic",
                "frame",
            ],
        }

    def init_pointing_angles(self, vector_x: np.ndarray, vector_y: np.ndarray) -> dict:
        """
        Compute the pointing angles (azimuth, elevation) in instrument frame for each camera

        :param np.ndarray vector_x: X coordinates of pointing vector, array of size (5,740)
        :param np.ndarray vector_y: Y coordinates of pointing vector, array of size (5,740)
        """

        pointing_vectors = {}
        for idx, instr in enumerate(self._instr_list):
            vec_x = np.array(vector_x[idx], dtype="float64")
            vec_y = np.array(vector_y[idx], dtype="float64")
            # compute U_z
            vec_z = np.sqrt(1 - (vec_x**2) - (vec_y**2))
            # stack components
            pointing_vectors[instr] = np.stack([vec_x, vec_y, vec_z], axis=-1)

        return pointing_vectors

    def instrument_to_sun(self, times: np.ndarray) -> np.ndarray:
        """
        Compute Sun position in instrument frame.

        Note: the output coordinates are already in OLCI instrument frame, no need to flip x/y and
        invert z (see OC-GE_5-2a)

        :param np.ndarray times: array of times to compute Sun positions (same time scale as frame times)
        :return: Array of Sun positions in instrument frame
        """

        flat_times = flatten_array(times)

        dataset = {
            "times": {
                "offsets": flat_times,
                "unit": self.default_time["unit"],
                "epoch": self.default_time["epoch"],
                "ref": self.default_time["ref"],
            },
        }
        # get sun position in cartesian ("times" -> "body_pos", "body_vel"), use the same frame
        # as the orbit model
        self.body_model.body_pv(dataset, BodyId.SUN, frame_out=self.orbit_model.frame)

        # convert from earth to satellite frame ("times" -> "orb_pos", "orb_vel", "attitudes")
        self.orbit_model.get_osv(dataset)
        self.orbit_model.compute_quaternions(dataset)
        # prepare transform from satellite frame to Earth
        sat_to_earth = RigidTransform(
            translation=dataset["orb_pos"],
            rotation=dataset["attitudes"],
        )
        earth_to_sat = sat_to_earth.inv()
        dataset["body_pos"] = earth_to_sat.transform_position(dataset["body_pos"])

        # convert from satellite to "all_cam" instrument frame
        self.platform_model.transform_position(
            dataset,
            frame_in="platform",
            frame_out="all_cam",
            vec_in_key="body_pos",
        )
        sun_pos = dataset["body_pos"]
        return restore_array(sun_pos, times.shape, last_dim=3)
