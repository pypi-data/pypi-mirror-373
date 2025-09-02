#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022 CS GROUP
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
Module for thermoelastic model
"""

import math
from typing import List

import numpy as np

from asgard.core import schema
from asgard.core.math import (
    collapse_siblings,
    expand_siblings,
    extend_circular_lut,
    quat_to_matrix,
    slerp_n,
    slerp_vec,
)
from asgard.core.transform import RigidTransform, StaticTransform, TimeBasedTransform


class ThermoelasticModel(TimeBasedTransform):
    """
    Support class for Sentinel 3 platform. Handles thermoelastic model
    """

    def __init__(self, **kwargs):
        """
        Compute data related to the instrument geometric model (thermoelastic effects).

        :param thermoelastic: dataset with thermoelastic tables, should contain "julian_days",
                        "quaternions_1", "quaternions_2", "quaternions_3", "quaternions_4",
                        "on_orbit_positions_angle"
        :param doy: L0 product middle time (UTM, processing format)
        :param instruments: list of instruments names to index the thermoelastic models. If not
                            specified, a default list of instrument will be used with the pattern
                            "instr_<idx>", where "idx" is the index starting with 1
        :param np.ndarray lut_times: Time values of the "time to OOP" LUT
        :param np.ndarray lut_oop: OOP values of the "time to OOP" LUT
        :param extract_instr: only use this instrument from the list.
        """

        # check input args
        schema.validate_or_throw(kwargs, ThermoelasticModel.init_schema())

        lut_times = kwargs["lut_times"]
        lut_oop = kwargs["lut_oop"]

        # compute pDoY
        thermoelastic = kwargs["thermoelastic"]
        doy = kwargs["doy"]
        doy_values = thermoelastic["julian_days"]
        if doy < doy_values[0] or doy > doy_values[-1]:
            idoy1 = len(doy_values) - 1
            idoy2 = 0
            if doy > doy_values[-1]:
                pdoy = (doy - doy_values[idoy1]) / (doy_values[idoy2] - doy_values[idoy1] + 365.25)
            else:
                pdoy = (doy - doy_values[idoy1] + 365.25) / (doy_values[idoy2] - doy_values[idoy1] + 365.25)
        else:
            idoy2 = np.searchsorted(doy_values, doy)
            idoy1 = idoy2 - 1
            pdoy = (doy - doy_values[idoy1]) / (doy_values[idoy2] - doy_values[idoy1])
        # compute quaternion_model LUT and grid
        quaternion_lut = {}
        oop_grid = {}
        # indexing is:
        #   quaternion_lut[module][iidoy][oop][iquat]
        #   oop_grid[module][iidoy][oop]
        # with:
        #   module = module index, in [0, 4]
        #   iidoy = DoY before/after, in [0,1]
        #   iquat = quaternion component, in [0, 3]
        #   oop = position on-orbit, in [0, 17]
        quat_1 = thermoelastic["quaternions_1"]
        quat_2 = thermoelastic["quaternions_2"]
        quat_3 = thermoelastic["quaternions_3"]
        quat_4 = thermoelastic["quaternions_4"]
        xmodel = thermoelastic["on_orbit_positions_angle"]
        nb_instr = len(quat_1)

        # If the instrument list is missing: build it with pattern "instr_<idx>" with idx from 1 to nb_instr.
        instruments = kwargs.get("instruments", [f"instr_{idx+1}" for idx in range(nb_instr)])

        # If the caller gave the instrument list and a specific instrument: only use this one
        extract_instr = kwargs.get("extract_instr")
        if extract_instr is not None:
            assert extract_instr in instruments, "Input specified instrument is invalid."
            instruments = [instr if instr == extract_instr else None for instr in instruments]

        # we extend the oop grid by one value on each side to cope with cases where oop < grid[0]
        # or oop > grid[-1]. The input grid is supposed to cover most of the [0.0, 360.0] interval
        for idx, instr in enumerate(instruments):
            if instr is None:
                continue
            # extend LUT for idoy1
            quat_lut_1 = np.stack(
                [
                    quat_1[idx][idoy1],
                    quat_2[idx][idoy1],
                    quat_3[idx][idoy1],
                    quat_4[idx][idoy1],
                ],
                axis=1,
            )
            oop_grid_1 = np.array(xmodel[idx][idoy1])
            ext_oop_grid_1, ext_quat_lut_1 = extend_circular_lut(oop_grid_1, quat_lut_1, end=360)
            # extend LUT for idoy2
            quat_lut_2 = np.stack(
                [
                    quat_1[idx][idoy2],
                    quat_2[idx][idoy2],
                    quat_3[idx][idoy2],
                    quat_4[idx][idoy2],
                ],
                axis=1,
            )
            oop_grid_2 = np.array(xmodel[idx][idoy2])
            ext_oop_grid_2, ext_quat_lut_2 = extend_circular_lut(oop_grid_2, quat_lut_2, end=360)
            # record extended LUTs
            quaternion_lut[instr] = [ext_quat_lut_1, ext_quat_lut_2]
            oop_grid[instr] = np.array([ext_oop_grid_1, ext_oop_grid_2])

        # record into the instance
        self.setup_model(pdoy, quaternion_lut, oop_grid, lut_times, lut_oop)

    def setup_model(
        self,
        pdoy,
        quaternion_lut,
        oop_grid,
        lut_times,
        lut_oop,
    ):
        """
        Record the computed input into the model
        """
        self.pdoy = pdoy
        self.quaternion_lut = quaternion_lut
        self.oop_grid = oop_grid
        self.lut_times = lut_times
        self.lut_oop = lut_oop

    @staticmethod
    def get_schema(number_instr: int | None = None) -> dict:
        """
        Return the expected schema for 'number_instr'

        :param int|None number_instr: Number of instruments in the thermoelastic model
        :return: JSON schema to validate thermoelastic model
        """
        if number_instr is None:
            number_instr = ":"
        return {
            "type": "object",
            "properties": {
                "julian_days": {"type": "array", "shape": (":",)},
                "quaternions_1": {"type": "array", "shape": (number_instr, ":", ":")},
                "quaternions_2": {"type": "array", "shape": (number_instr, ":", ":")},
                "quaternions_3": {"type": "array", "shape": (number_instr, ":", ":")},
                "quaternions_4": {"type": "array", "shape": (number_instr, ":", ":")},
                "on_orbit_positions_angle": {
                    "type": "array",
                    "shape": (number_instr, ":", ":"),
                },
            },
            "required": [
                "julian_days",
                "quaternions_1",
                "quaternions_2",
                "quaternions_3",
                "quaternions_4",
                "on_orbit_positions_angle",
            ],
        }

    @classmethod
    def init_schema(cls) -> dict:
        """
        Initialization schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/ThermoelasticModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "thermoelastic": ThermoelasticModel.get_schema(),
                "doy": {"type": "number"},
                "lut_times": {"type": "array", "shape": (":",)},
                "lut_oop": {"type": "array", "shape": (":",)},
                "instruments": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "thermoelastic",
                "doy",
                "lut_times",
                "lut_oop",
            ],
        }

    @staticmethod
    def get_specific_instr_schema() -> dict:
        """
        Return the expected schema for one instrument

        :return: JSON schema to validate thermoelastic model
        """
        return {
            "type": "object",
            "properties": {
                "all_instr": {"type": "array", "items": {"type": "string"}},
                "instr": {"type": "string"},
                "L0_product_middle_time": {"type": "number"},
                "julian_days": {"type": "array", "dtype": "int16", "shape": (":",)},
                "quaternions_1": {
                    "type": "array",
                    "dtype": "float64",
                    "shape": (":", ":", ":"),
                },
                "quaternions_2": {
                    "type": "array",
                    "dtype": "float64",
                    "shape": (":", ":", ":"),
                },
                "quaternions_3": {
                    "type": "array",
                    "dtype": "float64",
                    "shape": (":", ":", ":"),
                },
                "quaternions_4": {
                    "type": "array",
                    "dtype": "float64",
                    "shape": (":", ":", ":"),
                },
                "on_orbit_positions_angle": {
                    "type": "array",
                    "dtype": "float64",
                    "shape": (":", ":", ":"),
                },
            },
            "required": [
                "instr",
                "all_instr",
                "L0_product_middle_time",
                "julian_days",
                "quaternions_1",
                "quaternions_2",
                "quaternions_3",
                "quaternions_4",
                "on_orbit_positions_angle",
            ],
        }

    @property
    def instruments(self) -> List[str]:
        """
        Returns the list of instruments known by the thermoelastic model
        """
        return list(self.oop_grid.keys())

    def sat_to_instr_trans(
        self,
        oop: np.ndarray,
        instr: str,
        s3_to_cfi_convention: bool = False,
        quat_output: bool = False,
    ) -> List[np.ndarray]:
        """
        Compute the instrument alignment matrix for a given on-orbit position

        :param oop: 1D array position on-orbit (deg)
        :param int instr: Camera name, or "all" to compute the average
        :param bool s3_to_cfi_convention: Flag to change axes convention from S3 to EOCFI
        :param bool quat_output: Get output as quaternions instead of matrices
        :return: list of instrument alignment matrices. Each matrix
                 corresponds to a position on-orbit. Expected shape: [len(oop)][3, 3]
        """
        # interpolate model
        if instr == "all":
            instrs = self.instruments
        else:
            assert instr in self.instruments
            instrs = [instr]

        nb_oop = len(oop)
        nb_instr = len(instrs)
        quat_int = np.zeros((nb_instr, nb_oop, 4), dtype="float64")  # indexing is [cam, oop, 4]
        for icam, cam in enumerate(instrs):
            quat_int[icam] = self.oop_to_rotation(oop, self.oop_grid[cam], self.quaternion_lut[cam], self.pdoy)

        matrices = []
        for ioop in range(nb_oop):
            if nb_instr > 1:
                quat_s3 = np.zeros((4), dtype="float64")
                for quat in quat_int:
                    quat_s3 += quat[ioop]
                scale_quat = 1.0 / np.linalg.norm(quat_s3)
                quat_s3 *= scale_quat
            else:
                quat_s3 = quat_int[0, ioop]

            # compute EOCFI quaternion
            if s3_to_cfi_convention:
                # WARNING: check the formula with Navatt quaternion, there is obviously a change
                # in the axes, which is incompatible with the cases "valid_navatt = false"
                quat_cfi = (
                    1.0
                    / math.sqrt(2)
                    * np.array(
                        [
                            -(quat_s3[0] + quat_s3[3]),
                            -(quat_s3[0] - quat_s3[3]),
                            quat_s3[1] - quat_s3[2],
                            -(quat_s3[1] + quat_s3[2]),
                        ]
                    )
                )
            else:
                quat_cfi = np.array([-quat_s3[1], -quat_s3[2], -quat_s3[3], quat_s3[0]])
            # compute matrix from quaternion or do simple storage
            matrices.append(quat_cfi if quat_output else quat_to_matrix(quat_cfi))

        return matrices

    def time_to_oop(
        self,
        times: np.ndarray,
    ) -> np.ndarray:
        """
        For each LOS time, return the corresponding on-orbit position from Navatt data.

        :param np.ndarray times: LOS times at which to evaluate the interpolated on-orbit positions.
        """
        return np.interp(times, self.lut_times, self.lut_oop)

    @classmethod
    def oop_to_rotation(
        cls,
        oop: np.ndarray,
        oop_grid: np.ndarray,
        quaternion_lut: List[np.ndarray],
        pdoy: float,
    ) -> np.ndarray:
        """
        For each on-orbit position, return the corresponding rotation quaternion from the quaternion LUT.

        :param np.ndarray oop: on-orbit positions
        :param np.ndarray oop_grid: TODO TO BE COMPLETED
        :param List[np.ndarray] quaternion_lut: quaternion LUT
        :param float pdoy: TODO TO BE COMPLETED (day of year of what ? in days from 1st january 2020 GPS ?
        """

        nb_oop = len(oop)

        nb_grid_points = oop_grid.shape[1]
        ext_idx = list(range(nb_grid_points))

        quat_temp = []  # indexing will be [step][nb_oop, 4]

        for step in [0, 1]:
            ext_grid = oop_grid[step]
            ext_px = np.interp(oop, ext_grid, ext_idx)  # shape: (nb_oop)
            # floor(ext_px) = iX
            # ext_px - floor(ext_px) = px
            quat_temp.append(slerp_n(ext_px, quaternion_lut[step]))  # shape (nb_oop, 4)

        quat_int = np.zeros((nb_oop, 4), dtype="float64")  # indexing is [oop, 4]

        # for ioop in range(nb_oop):
        #     quat_int[ioop, :] = slerp(pdoy, quat_temp[0][ioop], quat_temp[1][ioop])

        quat_int[:, :] = slerp_vec(np.repeat(pdoy, nb_oop), quat_temp[0], quat_temp[1])

        return quat_int

    def inv(self):
        """
        Generate a new Thermoelastic model with inversed quaternions
        """
        output = super().__new__(ThermoelasticModel)
        inv_quat_lut = {}
        for item in self.instruments:
            quat_doy1, quat_doy2 = self.quaternion_lut[item]
            inv_doy1 = quat_doy1.copy()
            inv_doy1[:, 1:] *= -1.0
            inv_doy2 = quat_doy2.copy()
            inv_doy2[:, 1:] *= -1.0
            inv_quat_lut[item] = [inv_doy1, inv_doy2]

        output.setup_model(self.pdoy, inv_quat_lut, self.oop_grid, self.lut_times, self.lut_oop)
        return output

    def split(self) -> dict:
        """
        Split this model into individual models (one for each instrument), and return them in a dict

        :return: dict of "instrument" -> individual ThermoelasticModel
        """

        output = {}
        for item in self.instruments:
            sub_model = super().__new__(ThermoelasticModel)
            quat_lut = {item: self.quaternion_lut[item]}
            oop_grid = {item: self.oop_grid[item]}
            sub_model.setup_model(self.pdoy, quat_lut, oop_grid, self.lut_times, self.lut_oop)
            output[item] = sub_model
        return output

    def estimate(self, time_array: dict) -> StaticTransform:
        """
        Estimate a series of transforms for input given times

        :param dict time_array: input time array structure (see TIME_ARRAY)
        :return: a RigidTransform object with all the transforms stacked
        """
        collapsed_times = collapse_siblings(time_array["offsets"])
        oop = self.time_to_oop(collapsed_times)
        quat = self.sat_to_instr_trans(oop, "all", quat_output=True)

        out_quat = expand_siblings(time_array["offsets"], quat)
        return RigidTransform(rotation=out_quat)
