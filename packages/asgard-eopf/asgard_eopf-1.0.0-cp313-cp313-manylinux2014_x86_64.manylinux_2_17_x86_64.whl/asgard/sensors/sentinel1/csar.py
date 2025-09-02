#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2024 CS GROUP
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
Module for Sentinel 1 SAR product
"""

import logging
from typing import Optional, Tuple, Union

import numpy as np
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.raster.tiles_cache import TilesCache
from scipy.spatial.transform import Rotation as R

from asgard.core.frame import FrameId
from asgard.core.math import angular_distance, flatten_array, restore_array
from asgard.core.product import AbstractRadarGeometry
from asgard.core.schema import (
    ATTITUDE_SCHEMA,
    DEM_DATASET_SCHEMA,
    ORBIT_STATE_VECTORS_SCHEMA,
)
from asgard.core.time import TimeRef
from asgard.core.transform import RigidTransform
from asgard.models.body import EarthBody
from asgard.models.dem import ElevationManager
from asgard.models.orbit import GenericOrbitModel
from asgard.models.platform import GenericPlatformModel
from asgard.models.sar import (
    SPEED_LIGHT,
    SarPointingModel,
    SarPropagationModel,
    SarTimestampModel,
)
from asgard.models.time import JD_TO_SECONDS, TimeReference

logger = logging.getLogger(__name__)


class S1SARGeometry(AbstractRadarGeometry):
    """
    S1 SAR Product
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        # call superclass constructor
        super().__init__(*args, **kwargs)

        # Identify input swaths (one geometric_unit for each)
        self._instr_list = []
        self.coordinates = {}

        # Setup time model
        self.time_model = TimeReference(**kwargs.get("eop", {}))

        # Setup body_model
        self.body_model = EarthBody(ellipsoid="WGS84", time_reference=self.time_model)

        self.epoch = None
        for key in kwargs["swaths"]:
            self._instr_list.append(key)

            # TODO: support other azimuth conventions : RX, ZD
            self.config["swaths"][key].setdefault("azimuth_convention", "TX")

            # set default time sampling for azimuth and range
            self.config["swaths"][key].setdefault("azimuth_time_interval", 2.919194958309765e-03)
            self.config["swaths"][key].setdefault("range_sampling_rate", 2.502314816000000e07)

            # number of pixel and lines (frames) in a SAR image relies on the processing and is not exactly the same
            # for all images of the same acquisition mode, the approx. image size is given on the
            # Sentinel-1-Product-Definition doc. avail. at:
            # https://sentinel.esa.int/documents/247904/1877131/Sentinel-1-Product-Definition.pdf/6049ee42-6dc7-4e76-9886-f7a72f5631f3?t=1461673251000
            # from which we have extracted the 'S4' swath of the SM mode (applicable in this test case):
            self.coordinates[key] = {
                "range": kwargs["swaths"][key]["burst_samples"],
                "azimuth": len(kwargs["swaths"][key]["azimuth_times"]["offsets"])
                * kwargs["swaths"][key]["burst_lines"],
            }

            self._azimuth_time_ref = TimeRef[kwargs["swaths"][key]["azimuth_times"].get("ref", "GPS")]

            # Check input azimuth times are in seconds
            if kwargs["swaths"][key]["azimuth_times"].get("unit", "d") == "d":
                self.config["swaths"][key]["azimuth_times"]["offsets"] *= JD_TO_SECONDS
                self.config["swaths"][key]["azimuth_times"]["unit"] = "s"

            # check epoch
            cur_epoch = kwargs["swaths"][key]["azimuth_times"].get("epoch", "2000-01-01T00:00:00")
            if self.epoch is None:
                self.epoch = cur_epoch
            elif self.epoch != cur_epoch:
                raise RuntimeError(
                    f"All swaths azimuth times must use the same epoch. Found {cur_epoch}, expected {self.epoch}"
                )

            # instanciate the timestamp model
            self.timestamp_models[key] = SarTimestampModel(**kwargs["swaths"][key])

        has_attitude = "attitude" in kwargs
        self.config["has_attitude"] = has_attitude

        # Setup orbit model
        orb_list = kwargs["orbits"]

        # check the frame of each orbit
        for orbit in orb_list:
            orb_frame = orbit.get("frame", "")
            if orb_frame != FrameId.EF.name:
                logger.warning("Orbit frame used is %r, S1SAR constructor converts it to Earth-Fixed frame", orb_frame)
                # Transform orbit to Earth-Fixed frame
                self.body_model.transform_orbit(orbit, FrameId.EF)

        fused_orbit = GenericOrbitModel.merge_orbits(orb_list)

        orbit_config = {
            "orbit": fused_orbit,
            "attitude": {"aocs_mode": "ZD", "frame": "EF"},
            "earth_body": self.body_model,
        }
        # Set time_orb with acquisition start
        orbit_config["time_orb"] = (
            self._azimuth_time_ref.name
            + "="
            + self.time_model.to_str(
                self.config["swaths"][self._instr_list[0]]["azimuth_times"]["offsets"][0],
                fmt="CCSDSA_MICROSEC",
                unit="s",
                epoch=self.epoch,
            )
        )
        self.orbit_model = GenericOrbitModel(**orbit_config)

        # Setup pointing model
        pointing_config = {"look_side": "RIGHT", "front_direction": np.array([0, -1, 0], dtype="float64")}
        self.pointing_model = SarPointingModel(**pointing_config)

        # Setup platform model
        platform_config = {
            "states": [
                {
                    "name": "dummy",
                    "origin": "platform",
                    "rotation": np.zeros((3,), dtype="float64"),
                }
            ],
            "aliases": {},
        }
        for instr in self._instr_list:
            platform_config["aliases"][instr] = "platform"
        self.platform_model = GenericPlatformModel(**platform_config)

        # Setup propagation model
        propagation_config = {
            "earth_body": self.body_model,
            "is_right": True,
            "frame": "EF",
        }
        self.propagation_model = SarPropagationModel(**propagation_config)

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for constructor, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/S1SARGeometry.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "sat": {"type": "string", "pattern": "^SENTINEL_1[A-C]?$"},
                "look_side": {
                    "type": "string",
                    "enum": ["LEFT", "RIGHT"],
                    "description": "SAR looking side",
                },
                "oper_mode": {"type": "string", "enum": ["SM", "IW", "EW", "WV"], "description": "Acquisition mode"},
                "orbits": {
                    "type": "array",
                    "items": ORBIT_STATE_VECTORS_SCHEMA,
                    "description": "List of input orbit sources, sorted by increasing precision",
                },
                "attitude": ATTITUDE_SCHEMA,
                "resources": {
                    "type": "object",
                    "properties": {
                        "geoid": DEM_DATASET_SCHEMA,
                        "dem_path": DEM_DATASET_SCHEMA,
                        "dem_type": {"type": "string"},
                    },
                    "required": ["dem_path", "dem_type"],
                },
                "swaths": {
                    "type": "object",
                    "patternProperties": {"^.+$": SarTimestampModel.init_schema()},
                    "minProperties": 1,
                },
                "eop": TimeReference.init_schema(),
            },
            "required": [
                "sat",
                "look_side",
                "oper_mode",
                "orbits",
                "resources",
                "swaths",
            ],
            "additionalProperties": False,
        }

    def slant_range_localisation(  # pylint: disable=too-many-positional-arguments
        self,
        azimuth_times: dict,
        range_distance: np.ndarray,
        altitude: Union[float, np.ndarray],
        compute_velocity: bool = False,
        geodetic_output: bool = False,
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Convert slant range to a ground position

        :param dict azimuth_times: Array of zero-doppler azimuth times (see TIME_ARRAY_SCHEMA)
        :param np.ndarray range_distance: Array of slant range distances (in m)
        :param Union[float, np.ndarray] altitude: Array or single float of terrain altitudes (in m)
        :param bool compute_velocity: flag to compute velocity
        :param bool geodetic_output: flag to produce geodetic coordinates, default to cartesian ECEF
        :return: Tuple with arrays of ground coordinates, and corresponding velocity (if requested)
        """
        # Assume flattened array
        size = len(range_distance)

        assert azimuth_times["offsets"].shape == (size,)
        assert range_distance.shape == (size,)
        assert isinstance(altitude, float) or altitude.shape == (size,)

        if compute_velocity and geodetic_output:
            raise NotImplementedError("Velocity in geodetic coordinates not implemented")

        if isinstance(altitude, float):
            altitudes = altitude * np.ones((size,), dtype="float64")
        else:
            altitudes = altitude

        # Here we simplify the direct_loc process, based on S1 assumptions

        # Line of sight wrt Instrument frame + time
        front_direction = self.pointing_model.config["front_direction"]

        # transform line of sight to Earth-Fixed frame
        dataset = {"times": azimuth_times}
        self.orbit_model.get_osv(dataset)
        self.orbit_model.compute_quaternions(dataset)

        assert self.orbit_model.frame == FrameId.EF, "Expect orbit data in EF, no reprojection supported here"

        pos_body = dataset["orb_pos"]

        # prepare transform from satellite frame to Earth
        sat_to_earth = RigidTransform(
            rotation=dataset["attitudes"],
        )
        vel_body = sat_to_earth.transform_direction(front_direction)

        gnd = np.full((size, 3), np.nan, dtype="float64")

        doppler_contribution = np.zeros(size)
        # propagation to target
        points = self.propagation_model.ellipsoid.point_at_altitude_sar_vec(
            pos_body, vel_body, range_distance, True, doppler_contribution, altitudes
        )
        gnd[:] = points[:, [1, 0, 2]]

        # convert to degrees
        # ~ gnd_rad = gnd.copy()
        gnd[:, 0:2] = np.rad2deg(gnd[:, 0:2])

        # pre-compute cartesian coordinates
        gnd_cart = None
        if compute_velocity or geodetic_output is False:
            out_dataset = {"position": gnd}
            self.body_model.geodetic_to_cartesian(out_dataset)
            gnd_cart = out_dataset["position"]

        # compute ground velocity
        out_velocity = None
        if compute_velocity:
            # ~ # use a simple model for projected velocity:
            # ~ #   gnd_vel = (|gnd_pos| / |orb_pos| ) * (orb_vel - orb_vel.gnd_zenith * gnd_zenith)
            # ~ gnd_zenith = np.zeros((size, 3), dtype="float64")
            # ~ gnd_zenith[:, 0] = np.cos(gnd_rad[:, 0]) * np.cos(gnd_rad[:, 1])
            # ~ gnd_zenith[:, 1] = np.sin(gnd_rad[:, 0]) * np.cos(gnd_rad[:, 1])
            # ~ gnd_zenith[:, 2] = np.sin(gnd_rad[:, 1])

            # ~ orb_vel = dataset["orb_vel"]
            # ~ zenith_component = gnd_zenith * np.sum(orb_vel*gnd_zenith, axis=1)[:, np.newaxis]
            # ~ velocity_scaling = np.linalg.norm(gnd_cart, axis=1) / np.linalg.norm(pos_body, axis=1)
            # ~ out_velocity = (orb_vel - zenith_component) * velocity_scaling[:, np.newaxis]

            # simulate a small time delta and compute shifted locations
            time_delta = 0.001  # 1ms delta (in S1SARGeometry, azimuth times are assumed to be in seconds)
            pos_body_shifted = pos_body + time_delta * dataset["orb_vel"]

            doppler_contribution = np.zeros(size)
            # project shifted coordinates
            gnd_shifted = np.full((size, 3), np.nan, dtype="float64")

            points = self.propagation_model.ellipsoid.point_at_altitude_sar_vec(
                pos_body_shifted, vel_body, range_distance, True, doppler_contribution, altitudes
            )
            gnd_shifted[:] = points[:, [1, 0, 2]]

            # convert to cartesian and compute target velocity
            gnd_shifted[:, 0:2] = np.rad2deg(gnd_shifted[:, 0:2])
            shift_dataset = {"position": gnd_shifted}
            self.body_model.geodetic_to_cartesian(shift_dataset)
            gnd_shifted = shift_dataset["position"]
            out_velocity = (gnd_shifted - gnd_cart) / time_delta

        # convert to cartesian if needed
        if geodetic_output is False:
            gnd = gnd_cart

        return gnd, out_velocity

    def incidence_angles(self, ground_coordinates: np.ndarray, times: np.ndarray) -> np.ndarray:
        """
        Implementation of the incidence_angles routine for S1 SAR

        Sentinel 1 uses an incidence angle between view vector and geocentric ground position vector
        (not geodetic).

        :param np.ndarray ground_coordinates: Array of ground coordinates
        :param np.ndarray times: Array of timestamp for each coordinates
        :return: Array of incidence angles (azimuth + zenith angles)
        """

        # assume all azimuth times have "s" units
        flat_coords = flatten_array(ground_coordinates, 3)
        flat_times = flatten_array(times)
        dataset = {
            "times": {
                "offsets": flat_times,
                "ref": self._azimuth_time_ref.name,
                "epoch": self.epoch,
                "unit": "s",
            },
            "ground": flat_coords,
        }

        # get satellite position in EF cartesian
        self.orbit_model.get_osv(dataset, fields_out=["position", "velocity"])

        # convert lon/lat/z to Earth Fixed cartesian X,Y,Z
        self.body_model.geodetic_to_cartesian(dataset, field_in="ground")

        # compute geodetic indicence and azimuth angles
        self.body_model.ef_to_topocentric(dataset)

        # compute geocentric incidence angle
        incidence_angles = dataset["topocentric"]
        incidence_angles[:, 1] = angular_distance(dataset["position"] - dataset["ground"], dataset["ground"])

        return restore_array(incidence_angles[:, :2], ground_coordinates.shape[:-1], last_dim=2)

    def viewing_angles(self, ground_coordinates: np.ndarray, times: np.ndarray) -> np.ndarray:
        """
        Sentinel 1 uses a viewing angles between view vector and geocentric satellite position vector
        (not geodetic).
        """
        flat_coords = flatten_array(ground_coordinates, 3)
        flat_times = flatten_array(times)
        dataset = {
            "times": {
                "offsets": flat_times,
                "ref": self._azimuth_time_ref.name,
                "epoch": self.epoch,
                "unit": "s",
            },
            "ground": flat_coords,
        }

        # get satellite position in EF cartesian
        self.orbit_model.get_osv(dataset, fields_out=["position", "velocity"])

        # convert lon/lat/z to Earth Fixed cartesian X,Y,Z
        self.body_model.geodetic_to_cartesian(dataset, field_in="ground")

        # compute geodetic indicence and azimuth angles
        self.body_model.ef_to_topocentric(dataset)

        # compute geocentric incidence and azimuth angles
        incidence_angles = dataset["topocentric"]

        # add 180° to the azimuth
        azimuth_angle = np.remainder(incidence_angles[..., 0] + 180.0, 360.0)

        # compute geocentric viewing angle
        view_angle = angular_distance(dataset["position"] - dataset["ground"], dataset["position"])

        angles = np.stack([azimuth_angle, view_angle], axis=1)

        return restore_array(angles, ground_coordinates.shape[:-1], last_dim=2)

    def terrain_height(  # pylint: disable=too-many-positional-arguments
        self,
        azimuth_times: np.ndarray,
        azimuth_block_size: int = 1,
        azimuth_subsampling: int = 1,
        range_subsampling: int = 10,
        geometric_unit: str | None = None,
    ) -> np.ndarray:
        """
        Compute a vector of terrain elevation for a set of azimuth times (cf DPM 4.4). An azimuth
        block is defined around each azimuth time. The whole range of the swath is used. The elevation
        is measured on a sub-sampled grid, then averaged.

        :param np.ndarray azimuth_times: Array of azimuth times where elevation is measured
        :param int azimuth_block_size: number of lines in an azimuth block where averaging is done
            (centered around azimuth times)
        :param int azimuth_subsampling: Distance (in lines) between two lines in an azimuth block
        :param int range_subsampling: Sub-sampling parameter (in pixels) in the stripe where averaging is done
        :param str geometric_unit: Name of the geometric unit (swath, ...)
        :return: terrain heights array
        """

        if geometric_unit is None:
            geometric_unit = self._instr_list[0]

        swath = self.config["swaths"][geometric_unit]

        # azimuth sampling
        nb_blocs = len(azimuth_times)
        az_delta_0 = (azimuth_block_size - 1) // 2
        az_delta = np.arange(az_delta_0, az_delta_0 + azimuth_block_size, dtype="float64")
        az_delta *= swath["azimuth_time_interval"] * azimuth_subsampling
        all_azimuths_times = np.stack(
            [azimuth_times + delta for delta in az_delta],
            axis=1,
        )
        all_azimuths_times = all_azimuths_times.reshape(azimuth_block_size * nb_blocs)

        # range sampling
        range_sampling_time = range_subsampling / swath["range_sampling_rate"]
        all_ranges = np.arange(
            swath["slant_range_time"],
            swath["slant_range_time"] + swath["burst_samples"] / swath["range_sampling_rate"],
            range_sampling_time,
        )
        all_ranges *= SPEED_LIGHT * 0.5
        nb_range = len(all_ranges)

        grid_range, grid_az = np.meshgrid(all_ranges, all_azimuths_times)
        flat_grid_range = grid_range.flatten()
        flat_grid_az = grid_az.flatten()

        # call slant_range_localisation() with altitude=0.0
        flat_grid_gnd, _ = self.slant_range_localisation(
            {
                "offsets": flat_grid_az,
                "unit": "s",
                "epoch": swath["azimuth_times"].get("epoch", "2000-01-01T00:00:00"),
                "ref": swath["azimuth_times"].get("ref", "GPS"),
            },
            flat_grid_range,
            0.0,
            geodetic_output=True,
        )

        # setup DEM handler
        tile_updater = ElevationManager(
            self.config["resources"]["dem_path"],
            tile_lon=500,
            tile_lat=500,
        )
        tiles_cache = TilesCache(SimpleTile, tile_updater, 10)
        for coord in flat_grid_gnd:
            lat_rad = np.radians(coord[1])
            lon_rad = np.radians(coord[0])
            tile = tiles_cache.get_tile(lat_rad, lon_rad)
            coord[2] = tile.interpolate_elevation(lat_rad, lon_rad)

        flat_grid_elev = flat_grid_gnd[:, 2]

        # average on each stripe
        grid_elev = flat_grid_elev.reshape((nb_blocs, azimuth_block_size * nb_range))
        return np.average(grid_elev, axis=1)

    def zero_doppler_to_attitude(self, time_array: dict) -> np.ndarray:
        """
        Compute roll/pitch/yaw angles between Zero-Doppler attitude and satellite actual attitude

        :param dict time_array: Time array structure where angles should be estimated.
        :return: 2D Array of roll/pitch/yaw angles, shape is (N, 3)
        """

        dataset = {"times": time_array}

        if self.config["has_attitude"] is False:
            raise RuntimeError("Missing attitude data to compute roll/pitch/yaw")

        orbit_config = self.orbit_model.config.copy()
        orbit_config["attitude"] = self.config["attitude"]
        attitude_model = GenericOrbitModel(**orbit_config)

        self.orbit_model.compute_quaternions(dataset, field_quat="zd")
        attitude_model.compute_quaternions(dataset, field_quat="att")

        zd_rot = R.from_quat(dataset["zd"])
        sat_rot = R.from_quat(dataset["att"])

        final_rot = sat_rot.inv() * zd_rot
        angles = final_rot.as_euler("YXZ", degrees=True)

        # convert to follow an ortho triplet: Y -> X -> -Z
        angles[:, 2] *= -1.0

        return angles
