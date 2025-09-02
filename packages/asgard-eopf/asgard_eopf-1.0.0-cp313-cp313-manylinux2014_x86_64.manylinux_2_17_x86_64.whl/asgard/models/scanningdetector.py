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
Module to implement a ScanningDetectorTimestampModel for sensors
based on optical line detector
"""

from typing import Union

import numpy as np

from asgard.core.math import flatten_array, rotation_matrix
from asgard.core.pointing import AbstractPointingModel
from asgard.core.schema import TIME_ARRAY_SCHEMA
from asgard.core.timestamp import AbstractTimestampModel


def _coordinate_to_absolute_position(
    coordinates: np.ndarray, pixel_start: Union[np.ndarray, int], step: int
) -> np.ndarray:
    """
    Compute the absolute position of each coordinate in a scan, based on pixel start and step

    :param coordinates: (pixel, scan) coordinates array, of shape (N, 2)
    :param pixel_start: Target acquisition start, either a constant or a 1D array
    :param step: stepping between samples
    :return: array of absolute positions
    """

    if isinstance(pixel_start, int):
        start_pos = pixel_start
    else:
        start_pos = pixel_start[coordinates[..., 1]]

    return start_pos + coordinates[..., 0] * step


class ScanningDetectorTimestampModel(AbstractTimestampModel):
    """Model to retrieve the timestamp for scanning detector"""

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for dataset, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/ScanningDetectorTimestampModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "scan_times": TIME_ARRAY_SCHEMA,
                "pixel_period": {"type": "number"},
                "pixel_start": {
                    "oneOf": [
                        {"type": "integer"},
                        {"type": "array", "dtype": "int32", "shape": (":",)},
                    ],
                },
                "step": {"type": "integer"},
            },
            "required": ["scan_times", "pixel_period", "pixel_start"],
        }

    def acquisition_times(
        self,
        dataset,
        field_in: str = "coords",
        field_out: str = "times",
        abs_pos_out: str = "abs_pos",
    ):  # pylint: disable=arguments-differ
        # add this comment to avoid pylint warning coming from non respect of OO principles
        """Compute acquisition times for a dataset of coordinates

        :param dataset: dataset with coords of shape (N, 2) and geom unit containing view and group
        :param str field_in: key for array of coordinates
        :param str field_out: key for array of times
        :param str abs_pos_out: key for array of absolute positions
        :return: Array of acquisition times
        """

        scan_coords = flatten_array(dataset[field_in], 2)

        out_times = {key: value for key, value in self.config["scan_times"].items() if key != "offsets"}

        scan_times = np.array(self.config["scan_times"]["offsets"])
        time_delta = self.config["pixel_period"]
        start = self.config["pixel_start"]
        step = self.config.get("step", 1)

        abs_pos = _coordinate_to_absolute_position(scan_coords, start, step)

        out_times["offsets"] = scan_times[scan_coords[:, 1]] + time_delta * (abs_pos + 0.5)
        dataset[field_out] = out_times
        dataset[abs_pos_out] = abs_pos

        return dataset


class ScanningDetectorPointingModel(AbstractPointingModel):
    """Model to compute line of sight for scanning detector sensors"""

    def __init__(self, **kwargs):
        """Constructor for scanning product"""
        super().__init__(**kwargs)

        self._view_list = ["NAD", "OBL"]
        self._spectral_group = ["1KM", "1KM_F1", "05KM_A", "05KM_B"]
        self._constants = {}
        self._constants["scan_angle_1km_step"] = 360.0 / 3670.0
        self._constants["scan_mirror_offset"] = {
            "NAD": kwargs["geometry_model"]["scans_mirror_offset"][0],
            "OBL": kwargs["geometry_model"]["scans_mirror_offset"][1],
        }

        # init reflection matrices
        half_cone_angle = kwargs["geometry_model"]["scans_cone_angle"] * 0.5
        self._constants["scan_cone_matrix"] = {
            "NAD": rotation_matrix(np.deg2rad(half_cone_angle[0]), "x"),
            "OBL": rotation_matrix(np.deg2rad(half_cone_angle[1]), "x"),
        }
        self._constants["scan_cone_matrix_inv"] = {
            "NAD": rotation_matrix(np.deg2rad(-half_cone_angle[0]), "x"),
            "OBL": rotation_matrix(np.deg2rad(-half_cone_angle[1]), "x"),
        }
        scan_inclination_nadir = kwargs["geometry_model"]["scans_inclination_nadir"]
        self._constants["scans_inclination_matrix"] = {
            "NAD": rotation_matrix(np.deg2rad(scan_inclination_nadir), "y"),
            "OBL": np.eye(3, dtype="float64"),
        }

        flip_matrix = np.array([[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]], dtype="float64")

        # pre-compute the 3x3 matrix results of: scan_cone_inv x flip x scan_cone (S1-L1A_5_3-4)
        self._constants["reflection_matrix"] = {}
        for view in self._view_list:
            self._constants["reflection_matrix"][view] = (
                self._constants["scan_cone_matrix_inv"][view] @ flip_matrix @ self._constants["scan_cone_matrix"][view]
            )

        # init line of sight matrices
        self._constants["los_matrices"] = {}
        for view in self._view_list:
            self._constants["los_matrices"][view] = self.compute_los_matrices(kwargs["geometry_model"], view)

    @classmethod
    def init_schema(cls) -> dict:
        """
        :download:`JSON schema <doc/scripts/init_schema/schemas/ScanningDetectorPointingModel.schema.json>`
        """
        return {
            "type": "object",
            "definitions": {
                "slstr_geometry_model": {
                    "type": "object",
                    "properties": {
                        "scans_inclination_nadir": {"type": "number"},
                        "F1_scanangle_offset": {"type": "number"},
                        "scans_mirror_offset": {"type": "array", "shape": (2,)},
                        "scans_cone_angle": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_1km": {"type": "array", "shape": (2,)},
                        "cos_mu_centre_1km": {"type": "array", "shape": (2,)},
                        "cos_nu_centre_1km": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_F1": {"type": "array", "shape": (2,)},
                        "cos_mu_centre_F1": {"type": "array", "shape": (2,)},
                        "cos_nu_centre_F1": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_500m": {"type": "array", "shape": (8,)},
                        "cos_mu_centre_500m": {"type": "array", "shape": (8,)},
                        "cos_nu_centre_500m": {"type": "array", "shape": (8,)},
                        "cos_lambda_centre_1km_OB": {"type": "array", "shape": (2,)},
                        "cos_mu_centre_1km_OB": {"type": "array", "shape": (2,)},
                        "cos_nu_centre_1km_OB": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_F1_OB": {"type": "array", "shape": (2,)},
                        "cos_mu_centre_F1_OB": {"type": "array", "shape": (2,)},
                        "cos_nu_centre_F1_OB": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_500m_OB": {"type": "array", "shape": (8,)},
                        "cos_mu_centre_500m_OB": {"type": "array", "shape": (8,)},
                        "cos_nu_centre_500m_OB": {"type": "array", "shape": (8,)},
                    },
                    "required": [
                        "scans_inclination_nadir",
                        "F1_scanangle_offset",
                        "scans_mirror_offset",
                        "scans_cone_angle",
                        "cos_lambda_centre_1km",
                        "cos_mu_centre_1km",
                        "cos_nu_centre_1km",
                        "cos_lambda_centre_F1",
                        "cos_mu_centre_F1",
                        "cos_nu_centre_F1",
                        "cos_lambda_centre_500m",
                        "cos_mu_centre_500m",
                        "cos_nu_centre_500m",
                        "cos_lambda_centre_1km_OB",
                        "cos_mu_centre_1km_OB",
                        "cos_nu_centre_1km_OB",
                        "cos_lambda_centre_F1_OB",
                        "cos_mu_centre_F1_OB",
                        "cos_nu_centre_F1_OB",
                        "cos_lambda_centre_500m_OB",
                        "cos_mu_centre_500m_OB",
                        "cos_nu_centre_500m_OB",
                    ],
                },
            },
            "properties": {
                "pixel_start": {
                    "type": "object",
                    "patternProperties": {
                        "^.+$": {
                            "oneOf": [
                                {"type": "integer"},
                                {"type": "array", "dtype": "int32", "shape": (":",)},
                            ],
                        }
                    },
                },
                "step": {
                    "type": "object",
                    "patternProperties": {"^.+$": {"type": "integer"}},
                },
                "geometry_model": {"$ref": "#/definitions/slstr_geometry_model"},
            },
            "required": ["geometry_model"],
        }

    def scan_angles(self, abs_position: np.ndarray, group: str, view: str) -> np.ndarray:
        """
        Compute the mirror angle (deg) for input coordinates

        :param abs_position: Array of absolute pixel position inside a scan
        :return: Array of scan angles in degrees (in the range [0.0; 360.0[)
        """

        # 1km resolution grid
        scan_angle_step = self._constants["scan_angle_1km_step"]
        if group.startswith("05KM"):
            # 500m resolution grid
            scan_angle_step *= 0.5

        # Compute scan angles
        output = np.remainder(
            (abs_position + 0.5) * scan_angle_step + self._constants["scan_mirror_offset"][view] + 360.0,
            360.0,
        )

        if group.endswith("_F1"):  #
            # apply shift for F1 channel
            output += -self.config["geometry_model"]["F1_scanangle_offset"]

        return output

    def compute_los_matrices(self, geom_model: dict, view: str) -> dict:
        """
        Compute the line-of-sight matrices for a given view

        :param dict geom_model: geometry model with pointing vectors lambda/mu/nu
        :param str view: View ("NAD"/"OBL")
        :return: a dictionary with line-of-sight matrices mapped by spectral group (1KM/05KM_A/...)
        """
        assert view in self._view_list

        suffix = ""
        if view == "OBL":
            suffix = "_OB"
        los = {
            "1KM": np.array(
                [
                    geom_model["cos_lambda_centre_1km" + suffix],
                    geom_model["cos_mu_centre_1km" + suffix],
                    geom_model["cos_nu_centre_1km" + suffix],
                ]
            ),
            "05KM_A": np.array(
                [
                    geom_model["cos_lambda_centre_500m" + suffix][0:4],
                    geom_model["cos_mu_centre_500m" + suffix][0:4],
                    geom_model["cos_nu_centre_500m" + suffix][0:4],
                ]
            ),
        }
        # handle optional groups F1 and strip B
        if "1KM_F1" in self._spectral_group:
            los["1KM_F1"] = np.array(
                [
                    geom_model["cos_lambda_centre_F1" + suffix],
                    geom_model["cos_mu_centre_F1" + suffix],
                    geom_model["cos_nu_centre_F1" + suffix],
                ]
            )
        if "05KM_B" in self._spectral_group:
            los["05KM_B"] = np.array(
                [
                    geom_model["cos_lambda_centre_500m" + suffix][4:8],
                    geom_model["cos_mu_centre_500m" + suffix][4:8],
                    geom_model["cos_nu_centre_500m" + suffix][4:8],
                ]
            )
        return los

    def compute_los(  # pylint: disable=arguments-differ
        self,
        dataset,
        coord_in: str = "coords",
        abs_pos_in: str = "abs_pos",
        geometry: str = "geom",
        los_pos: str = "los_pos",
        los_vec: str = "los_vec",
    ):
        """
        Compute the pointing angles (azimuth, elevation) in instrument frame for each camera

        :param dataset: containing "coords" X and Y oordinates of pointing vector, array of size (N,2)
        :param str coord_in: name of the image coordinate field
        :param str abs_pos_in: key of the absolute position dataset (used only if no pixel_start
            information was given)
        :param str geometry: name of the geometric unit field
        :param str los_pos: name of output field for line of sight position in instrument frame
        :param str los_vec: name of output field for line of sight direction in instrument frame
        """

        geom_unit = dataset[geometry]
        geom_parts = geom_unit.split("/")
        view = geom_parts[0]
        group = geom_parts[1]
        detector = int(geom_parts[2])

        scan_coords = flatten_array(dataset[coord_in], 2)

        if "pixel_start" not in self.config:
            # use the "abs_pos" table to get absolute position without recomputing them
            abs_pos = dataset[abs_pos_in]
        else:
            # Compute absolute position from pixel_start/step parameters

            # get the pixel start (handles partial geom_unit like NAD/1KM)
            if geom_unit in self.config["pixel_start"]:
                start = self.config["pixel_start"][geom_unit]
            elif view + "/" + group in self.config["pixel_start"]:
                start = self.config["pixel_start"][view + "/" + group]
            else:
                raise RuntimeError(f"Can't find pixel start for {geom_unit}")
            # get step
            step_dict = self.config.get("step", {})
            if geom_unit in step_dict:
                step = step_dict[geom_unit]
            elif view + "/" + group in step_dict:
                step = step_dict[view + "/" + group]
            else:
                step = 1

            abs_pos = _coordinate_to_absolute_position(scan_coords, start, step)

        # get scan angles
        angles = self.scan_angles(abs_pos, group, view)

        # compute line of sight matrices
        rad_angles = np.deg2rad(angles)
        mirror_m = rotation_matrix(rad_angles, "z")
        mirror_inv_m = rotation_matrix(-rad_angles, "z")
        reflect_m = self._constants["reflection_matrix"][view]
        scan_incl_m = self._constants["scans_inclination_matrix"][view]
        los_vector = self._constants["los_matrices"][view][group][:, detector : detector + 1]

        assert mirror_inv_m.shape == (scan_coords.shape[0], 3, 3)
        assert mirror_m.shape == (scan_coords.shape[0], 3, 3)

        los_m = scan_incl_m @ mirror_inv_m @ reflect_m @ mirror_m @ los_vector
        # drop last dimension of size 1
        los_m = np.squeeze(los_m, axis=2)

        dataset[los_vec] = los_m
        dataset[los_pos] = np.zeros(los_m.shape, dtype="float64")
        return dataset
