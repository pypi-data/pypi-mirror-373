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
Module for SAR models
"""

import numpy as np
from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid

from asgard.core.frame import FrameId
from asgard.core.pointing import AbstractPointingModel
from asgard.core.propagation import AbstractPropagationModel
from asgard.core.schema import TIME_ARRAY_SCHEMA, generate_float64_array_schema
from asgard.core.timestamp import AbstractTimestampModel
from asgard.models.body import EarthBody

SPEED_LIGHT = 299792458.0


class SarTimestampModel(AbstractTimestampModel):
    """
    Timestamp model for SAR sensors, handles short time (range time) and azimuth time
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Input schema for SarTimestampModel.

        :download:`JSON schema <doc/scripts/init_schema/schemas/SarTimestampModel.schema.json>`
        """

        return {
            "type": "object",
            "properties": {
                "azimuth_times": TIME_ARRAY_SCHEMA,
                "azimuth_convention": {
                    "type": "string",
                    "description": "Convention for azimuth times: "
                    "TX for pulse transmit time, "
                    "RX for pulse reception time of first sample (not supported yet), "
                    "ZD for zero-doppler time at mid-range (not supported yet)",
                    "enum": ["TX"],
                },
                "azimuth_time_interval": {
                    "type": "number",
                    "description": "Time interval between lines [s]",
                },
                "slant_range_time": {
                    "type": "number",
                    "description": "Two way slant range time to first sample [s]",
                },
                "range_sampling_rate": {
                    "type": "number",
                    "description": "Range sample rate [Hz]",
                },
                "burst_lines": {
                    "type": "integer",
                    "description": "Number of lines per burst, along azimuth axis",
                },
                "burst_samples": {
                    "type": "integer",
                    "description": "Number of samples per burst, along range axis",
                },
            },
            "required": [
                "azimuth_times",
                "slant_range_time",
                "burst_samples",
                "burst_lines",
            ],
            "additionalProperties": False,
        }

    def acquisition_times(
        self,
        dataset: dict,
        field_in: str = "coords",
        field_out: str = "times",
        field_range_out: str = "range_times",
        **kwargs,
    ) -> dict:
        """
        Computes the acquisition times for each image coordinates

        :param dataset: Dataset with:

            - "coords": image coordinates

        :param str field_in: Name of the coordinates field
        :param str field_out: Name of the output field for azimuth times
        :param str field_range_out: Name of the output field for range times
        :return: input dataset with "times"
        """

        coords = dataset[field_in]

        # convert coordinates to azimuth time and slant range
        # assume azimuth time is in seconds
        burst_id = coords[:, 1] // self.config["burst_lines"]
        burst_id = np.clip(burst_id, 0, self.config["azimuth_times"]["offsets"].shape[0] - 1).astype(int)
        line_offset = coords[:, 1] % self.config["burst_lines"]

        azimuth_times = (
            self.config["azimuth_times"]["offsets"][burst_id] + line_offset * self.config["azimuth_time_interval"]
        )

        # range time (in s)
        range_times = self.config["slant_range_time"] + coords[:, 0] / self.config["range_sampling_rate"]

        # apply bi-static correction
        azimuth_times += range_times * 0.5

        # copy time epoch / unit / ref from azimuth_times
        dataset[field_out] = {}
        dataset[field_out].update(self.config["azimuth_times"])
        dataset[field_out]["offsets"] = azimuth_times

        dataset[field_range_out] = range_times

        return dataset


class SarPointingModel(AbstractPointingModel):
    """
    SAR pointing model
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Input schema for SarPointingModel.

        :download:`JSON schema <doc/scripts/init_schema/schemas/SarPointingModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "look_side": {"type": "string", "enum": ["LEFT", "RIGHT"]},
                "antenna_boresight_per_swath": {
                    "type": "object",
                    "patternProperties": {
                        "^.+$": {
                            "type": "array",
                            "shape": [3],
                            "dtype": "float64",
                            "description": "Antenna boresight direction in instrument frame",
                        },
                    },
                },
                "front_direction": {
                    "type": "array",
                    "shape": [3],
                    "dtype": "float64",
                    "description": "Satellite front direction in instrument frame",
                },
            },
            "required": ["look_side", "front_direction"],
        }

    def compute_los(  # pylint: disable=arguments-differ
        self,
        dataset,
        geom_in: str = "geom",
        los_pos: str = "los_pos",
        los_vec: str = "los_vec",
    ):
        """
        Computes the line of sight for a given measurement.

        :param dataset: Dataset with a field for geometric unit
        :param geom_in: Name of the geometric unit field in dataset
        :param los_pos: Name of the output field for antenna center
        :param los_vec: Name of the output field for antenna boresight direction
        :return: same dataset with line-of-sight
        """

        if dataset.get(geom_in) is None:
            raise RuntimeError(f"Missing geometric unit in dataset[{geom_in!r}]")

        dataset[los_pos] = np.zeros((3,), dtype="float64")
        dataset[los_vec] = self.config["front_direction"]


class SarPropagationModel(AbstractPropagationModel):
    """
    SAR propagation model
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """
        # Call parent constructor
        super().__init__(**kwargs)

        self.body = kwargs.get("earth_body", EarthBody())

        # detect rotating frame
        self.config["body_rotating_frame"] = kwargs.get("body_rotating_frame", "EF")
        self.rotating_frame_id = FrameId[self.config["body_rotating_frame"]]

        # detect input frame
        self.config.setdefault("frame", "EF")
        self.input_frame_id = FrameId[self.config["frame"]]

        self.config.setdefault("is_right", True)

        self.ellipsoid = ExtendedEllipsoid(
            self.body.rad_eq, self.body.flattening, self.body.frames[self.rotating_frame_id]
        )

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for SAR propagation.

        :download:`JSON schema <doc/scripts/init_schema/schemas/SarPropagationModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "earth_body": {"type": "asgard.models.body.EarthBody"},
                "terrain_height_lut": {
                    "type": "object",
                    "properties": {
                        "azimuth": TIME_ARRAY_SCHEMA,
                        "height": generate_float64_array_schema(":"),
                    },
                    "required": ["azimuth", "height"],
                },
                "is_right": {"type": "boolean"},
                "body_rotating_frame": {
                    "type": "string",
                    "description": "Frame of the Earth rotating frame",
                },
                "frame": {
                    "type": "string",
                    "description": "Frame of input LOS coordinates",
                },
            },
            "required": ["earth_body"],
        }

    def sensor_to_target(  # pylint: disable=arguments-differ
        self,
        dataset: dict,
        # LOS origins and directions keys
        los_pos_key: str = "los_pos",
        los_vec_key: str = "los_vec",
        # Acquisition times keys
        time_key: str = "times",
        range_key: str = "range_times",
        # Other keys
        gnd_coords_key: str = "gnd_coords",
        altitude: float | np.ndarray | None = None,
    ):
        """
        Compute range based intersection with the target

        :param dataset: Dataset

        Origins and directions in inertial frame for each datetime

        :param los_pos_key: Name of the field for input emission position
        :param los_vec_key: Name of the field for antenna looking direction

        Time inputs

        :param time_key: Name of the field for acquisition times (zero-doppler convention)
        :param range_key: Name of the field for range times (in seconds)
        :param gnd_coords_key: Name of output field for ground coordinates
        :param altitude:
            If a single float, use this value as constant altitude for intersection
            If an NDarray use it
        :return: same dataset with target coordinates
        """

        azimuth_times = dataset[time_key]["offsets"]
        # ~ coeff = 0.9999999996800182  # potential coeff to correct range to orthogonal range
        range_dist = dataset[range_key] * (SPEED_LIGHT / 2)
        is_right = self.config["is_right"]

        size = len(azimuth_times)

        # if provided altitudes will prevails
        if altitude is not None:
            if isinstance(altitude, (float, int)):
                altitudes = float(altitude) * np.ones(range_dist.shape, dtype="float64")
            elif isinstance(altitude, np.ndarray):
                altitudes = altitude
            else:
                raise NotImplementedError("Unrecognized type given for altitude")
        else:
            if "terrain_height_lut" not in self.config:
                raise RuntimeError("Missing terrain height LUT, no altitude given")
            # TODO: convert times in LUT to input times convention
            altitudes = np.interp(
                azimuth_times,
                self.config["terrain_height_lut"]["azimuth"]["offsets"],
                self.config["terrain_height_lut"]["height"],
            )

        if self.input_frame_id != self.rotating_frame_id:
            # convert pos and vel to rotating frame
            self.body.change_reference_frame(
                dataset,
                frame_in=self.input_frame_id,
                frame_out=self.rotating_frame_id,
                fields_in=(time_key, los_pos_key, los_vec_key),
                fields_out=("pos_body", "vel_body"),
            )
            pos_body = dataset["pos_body"]
            vel_body = dataset["vel_body"]
        else:
            pos_body = dataset[los_pos_key]
            vel_body = dataset[los_vec_key]

        # This value is constant for now
        doppler_contribution = np.zeros(size, dtype="float64")
        gnd = np.full((size, 3), np.nan, dtype="float64")
        # Compute intersection
        points = self.ellipsoid.point_at_altitude_sar_vec(
            pos_body, vel_body, range_dist, is_right, doppler_contribution, altitudes
        )

        gnd[:] = points[:, [1, 0, 2]]
        # convert to degrees
        gnd[:, 0:2] = np.rad2deg(gnd[:, 0:2])

        dataset[gnd_coords_key] = gnd

        return dataset
