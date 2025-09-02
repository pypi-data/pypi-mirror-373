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
Module for Sentinel 3 instruments
"""

import numpy as np

from asgard.core.frame import FrameId
from asgard.core.math import flatten_array, restore_array
from asgard.core.product import AbstractGeometry
from asgard.core.schema import (
    DEM_DATASET_SCHEMA,
    NAVATT_SCHEMA,
    ORBIT_STATE_VECTORS_SCHEMA,
    TIME_ARRAY_SCHEMA,
    TIMESCALE_NAME_SCHEMA,
)
from asgard.core.time import JD_TO_SECONDS, TimeRef
from asgard.models.body import EarthBody
from asgard.models.crosstrack import CrossTrackPointingModel
from asgard.models.linedetector import LineDetectorTimestampModel
from asgard.models.orbit import GenericOrbitModel
from asgard.models.platform import GenericPlatformModel
from asgard.models.range import GroundRangePropagationModel
from asgard.models.thermoelastic import ThermoelasticModel
from asgard.models.time import TimeReference


class GroundTrackGrid(AbstractGeometry):  # pylint: disable=R0902
    """
    Synthetic quasi-cartesian grid based on the ground track:

        - axes aligned with across-track (X) and along-track (Y) directions
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        # call superclass constructor
        super().__init__(*args, **kwargs)

        self._instr_list = ["default"]
        self.coordinates = {
            "default": {
                "x": kwargs["ac_samples"],  # across-track axis
                "y": len(kwargs["times"]["offsets"]),  # along-track axis
            }
        }

        # Setup time model
        self.time_model = TimeReference(**kwargs.get("eop", {}))

        # Setup body model
        self.body_model = EarthBody(ellipsoid="WGS84", time_reference=self.time_model)

        # Setup timestamp model
        times_qc_grid = {
            "times": {"offsets": kwargs["times"]["offsets"][kwargs["qc_first_scan"] : kwargs["qc_last_scan"] + 1]}
        }
        self.timestamp_models["default"] = LineDetectorTimestampModel(times=times_qc_grid["times"])
        time_values = np.array(kwargs["times"]["offsets"])

        # Setup orbit model
        valid_navatt = "navatt" in kwargs
        self.config["valid_navatt"] = valid_navatt
        orb_list = kwargs["orbits"]

        if valid_navatt:
            orb_list.append(kwargs["navatt"]["orbit"])
        # check the frame of each orbit
        orb_frames = {orbit.get("frame", "EME2000") for orbit in orb_list}
        assert orb_frames == {"EME2000"}, f"Expect orbit data in EME2000, but got {orb_frames}"
        fused_orbit = GenericOrbitModel.merge_orbits(orb_list)

        assert len(fused_orbit["positions"]) == len(fused_orbit["velocities"])
        assert len(fused_orbit["velocities"]) == len(fused_orbit["times"]["GPS"]["offsets"])
        orbit_config = {
            "orbit": fused_orbit,
            "earth_body": self.body_model,
        }
        orbit_config["attitude"] = kwargs["navatt"]["attitude"] if valid_navatt else {"aocs_mode": "YSM"}
        orbit_config["time_orb"] = "UTC=" + self.time_model.to_str(
            time_values[0],
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
            fmt="CCSDSA_MICROSEC",
            unit=self.default_time["unit"],
            epoch=self.default_time["epoch"],
        )
        self.orbit_model = GenericOrbitModel(**orbit_config)
        orb_info = self.orbit_model.info

        # Setup platform model
        platform_config = {"states": [], "aliases": {}}

        if "thermoelastic" in kwargs:
            # setup on-orbit position LUT
            if valid_navatt:
                lut_times = self.config["navatt"]["times"]["offsets"]
                lut_oop = self.config["navatt"]["oop"]
            else:
                # build a custom LUT based on start/end acquisition
                lut_times = np.arange(
                    time_values[0] - 4 / JD_TO_SECONDS,
                    time_values[-1] + 4 / JD_TO_SECONDS,
                    1 / JD_TO_SECONDS,
                )
                lut_oop = self.orbit_model.position_on_orbit(lut_times)

            # Case: thermoelastic effect
            thermoelastic = ThermoelasticModel(
                thermoelastic=kwargs["thermoelastic"],
                doy=(orb_info["utc_anx"] + orb_info["period_jd"] / 2.0) % 365.24,
                lut_times=lut_times,
                lut_oop=lut_oop,
            )

            # Thermoelastic quaternions are in the direction SLSTR_to_S3, but the thermoelastic model
            # already invert them, so we need to invert twice
            thermoelastic = thermoelastic.inv()
            # TODO : or we remove the inversion in ThermoelasticModel

            platform_config["states"].append(
                {
                    "name": "default",
                    "origin": "platform",
                    "time_based_transform": thermoelastic,
                }
            )
        else:
            # Case: no geocalibraiton, setup a dummy state and aliases to platform
            platform_config["states"].append(
                {
                    "name": "dummy",
                    "origin": "platform",
                    "translation": np.array([0.0, 0.0, 0.0]),
                }
            )
            platform_config["aliases"]["default"] = "platform"
        self.platform_model = GenericPlatformModel(**platform_config)

        # Setup pointing model
        num_ac_tp1 = self.config["ac_center_position"]
        ac_res = self.config["ac_resolution"]
        self.track_x = np.array([ac_res * (num_ac_tp1 - idx) for idx in range(kwargs["ac_samples"])])
        self.pointing_model = CrossTrackPointingModel(resolution=ac_res, center_position=num_ac_tp1)

        # Setup propagation model
        propagation_config = {"earth_body": self.body_model}
        if "geoid_path" in kwargs:
            propagation_config["geoid_path"] = kwargs["geoid_path"]
        self.config["dem_type"] = kwargs.get("dem_type", "ZARR")
        if "dem_path" in kwargs:
            if self.config["dem_type"] == "ZARR":
                propagation_config["zarr_dem"] = {"path": kwargs["dem_path"]}
            else:
                propagation_config["native_dem"] = {
                    "path": kwargs["dem_path"],
                    "source": self.config["dem_type"],
                    "overlapping_tiles": bool(self.config["dem_type"] == "SRTM"),
                }
        self.propagation_model = GroundRangePropagationModel(**propagation_config)

        # TODO: create a new pointing model "CrossTrackPointingModel" producing
        #   - los_vec : [0, 0, 1]
        #   - los_pos : [0, 0, 0]
        #   - ac_dist : across-track signed distance

        # Setup propagation model
        # TODO: create a new propagation model equivalent to target ground range:
        #  - classic propagation of a LOS at zero altitude
        #  - range propagation from the reference point

        # Workflow:
        #   - [ConstantPointingModel]  ->   los_vec + los_pos (instrument)
        #   - [PlatformModel]          ->   los_vec + los_pos (platform)
        #   - [OrbitModel]             ->   los_vec + los_pos (inertial)
        #   - [PropagationModel]       ->   ref_point
        #
        #   - ref_point + orb_vel + ac_dist ---[GroundRangePropagationModel]-->  gnd_coord
        # ---------------------------------------------------------------------------------------

        # these attributes are initialized to None, but they can be computed by
        # compute_along_track_coordinates
        self.track_y = None
        self.track_az = None
        self.track_points = None
        self.qc_first_scan = kwargs["qc_first_scan"]
        self.qc_last_scan = kwargs["qc_last_scan"]

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for constructor, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/GroundTrackGrid.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "sat": {"type": "string"},
                "orbits": {"type": "array", "items": ORBIT_STATE_VECTORS_SCHEMA},
                "ac_samples": {"type": "integer"},
                "ac_center_position": {"type": "integer"},
                "ac_resolution": {"type": "number"},
                "times": TIME_ARRAY_SCHEMA,
                "time_origin": {"type": "number"},
                "time_reference": TIMESCALE_NAME_SCHEMA,
                "thermoelastic": ThermoelasticModel.get_schema(),
                "navatt": NAVATT_SCHEMA,
                "eop": TimeReference.init_schema(),
                "dem_path": DEM_DATASET_SCHEMA,
                "dem_type": {"type": "string", "enum": ["ZARR", "SRTM", "GLOBE"]},
                "geoid_path": DEM_DATASET_SCHEMA,
            },
            "required": [
                "sat",
                "orbits",
                "ac_samples",
                "ac_center_position",
                "ac_resolution",
                "times",
                "time_origin",
            ],
        }

    def compute_along_track_coordinates(self):
        """
        Estimate Y coordinates vector of the grid in the quasi-cartesian space. The time_origin is
        used to set the Y origin. The sub-satellite points are computed for each time.

        :return: vector of Y coordinates
        """

        time_values = np.asarray(self.config["times"]["offsets"])

        has_navatt = "navatt" in self.config
        has_thermoelastic = "thermoelastic" in self.config
        if has_navatt or has_thermoelastic:
            # compute "along-track position" as the target seen with azimuth=0 and elevation=90
            coords = np.zeros((len(time_values), 2), dtype="int32")
            coords[:, 0] = self.config["ac_center_position"]
            coords[:, 1] = range(len(time_values))
            self.track_points, _ = self.direct_loc(coords)
        else:
            # compute sub-satellite point from orbital position
            dataset = {"times": self.config["times"]}
            self.orbit_model.get_osv(dataset)
            # convert to EF if needed
            if self.orbit_model.frame != FrameId.EF:
                self.body_model.change_reference_frame(
                    dataset,
                    frame_in=self.orbit_model.frame,
                    frame_out=FrameId.EF,
                    fields_in=("times", "orb_pos"),
                    fields_out=["orb_pos"],
                )
            # convert to geodetic
            self.body_model.cartesian_to_geodetic(dataset, field_in="orb_pos")
            self.track_points = dataset["orb_pos"]
            # reset altitude to 0
            self.track_points[:, 2] = 0.0

        dataset = {"positions": self.track_points}
        self.body_model.geodetic_path(dataset)
        raw_path = dataset["distance"]
        self.track_az = dataset["azimuth"]

        # Compute shift
        time_orig = self.config["time_origin"]
        if time_orig in time_values:
            (idx_orig,) = np.where(time_values == time_orig)
            pos_orig = raw_path[idx_orig[0]]
        elif time_orig < time_values[0]:
            pos_orig = raw_path[1] * (time_orig - time_values[0]) / (time_values[1] - time_values[0])
        else:
            raise RuntimeError(f"Unable to compute Y coordinates with origin time {time_orig}")

        self.track_y = raw_path - pos_orig
        return self.track_y

    def ground_to_xy(self, ground_coordinates: np.ndarray) -> np.ndarray:
        """
        Convert ground coordinates into (X,Y) quasi-cartesian coordinates. X refers to the across
        track direction, Y refers to along track direction.

        :param np.ndarray ground_coordinates: Array of lon/lat coordinates
        :return: array of X/Y coordinates
        """
        assert self.track_points is not None
        assert self.track_y is not None
        assert self.track_az is not None

        # change shape, leave 2 components at the end
        flat_coord = flatten_array(ground_coordinates, 2)

        dataset = {
            "coords": flat_coord,
            "track_points": self.track_points,
            "track_distance": self.track_y,
            "track_azimuth": self.track_az,
        }
        self.body_model.project_to_track(dataset)

        return restore_array(dataset["xy_coords"], ground_coordinates.shape[:-1], last_dim=2)

    def across_track_pointing(
        self,
        ground_coordinates: np.ndarray,
        img_coordinates: np.ndarray,
        times: np.ndarray,
    ) -> np.ndarray:
        """
        Compute the across track oriented pointing angle

        :param np.ndarray ground_coordinates: array of target ground coordinates
        :param np.ndarray img_coordinates: array of corresponding image coordinates
        :param np.ndarray times: array of acquisition times
        :return: array of pointing angles
        """

        # need self.track_points from compute_along_track_coordinates
        assert self.track_points is not None

        # compute reference points
        reference_coordinates = np.zeros(ground_coordinates.shape, dtype="float64")

        flat_coords = flatten_array(img_coordinates, 2)
        flat_ref_coords = flatten_array(reference_coordinates, 3)
        flat_ref_coords[:] = self.track_points[flat_coords[:, 1]]

        pointing = self.pointing_angles(
            ground_coordinates,
            reference_coordinates,
            times,
        )
        # make the pointing angle signed
        pointing[img_coordinates[..., 0] > self.config["ac_center_position"]] *= -1.0

        return pointing
