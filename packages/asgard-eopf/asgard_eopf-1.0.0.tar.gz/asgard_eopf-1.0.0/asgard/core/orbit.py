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
Module for orbit abstraction
"""

from abc import abstractmethod
from typing import List

import numpy as np

from .frame import FrameId
from .model import AbstractModel
from .schema import ORBIT_STATE_VECTORS_SCHEMA
from .time import DEFAULT_EPOCH, DEFAULT_UNIT, TimeRef
from .toolbox import sub


class AbstractOrbitModel(AbstractModel):
    """
    Model to handle the orbit propagation and interpolation
    """

    @property
    @abstractmethod
    def frame(self) -> FrameId:
        """Get the frame of orbit coordinates."""

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for orbit estimation

        May be overriden by derived classes, default is: :py:CONST:`asgard.core.schema.ORBIT_STATE_VECTORS_SCHEMA`

        :download:`JSON schema <doc/scripts/init_schema/schemas/AbstractOrbitModel.schema.json>`
        """
        return ORBIT_STATE_VECTORS_SCHEMA

    @abstractmethod
    def get_osv(self, dataset, **kwargs):
        """
        Return the orbit state vector for a given time. The output fields are computed respectively
        as position, velocity and acceleration.

        :param dataset: Dataset with:

            - "times" array

        :param *: Any other parameters that will be understood by concrete implementation of ``get_osv``.
        :return: same dataset with orbit state vector

        :warning: All child classes are expected to define :meth:`get_osv`. However, variations about the actual
            parameters are expected between :class:`AbstractOrbitModel` and its child classes. This abstract method is
            not a *real* abstract method as far as OO design is concerned; several tools (like mypy, Pycharm) are likely
            to warn us about incorrect overriding. See this abstract :meth:`get_osv` as just a documentation artefact:
            "All *Orbit Models* are expected to provide a method named ``get_osv``". And don't expect to be able to
            write generic code that calls ``get_osv`` and that will work with any specialization of
            :class:`AbstractOrbitModel`.
        """

    @abstractmethod
    def compute_quaternions(self, dataset, **kwargs):
        """
        Computes the attitude quaternions of the platform for a given times. The output is added
        to the dataset.

        :param dataset: Dataset with:

            - "times" array

        :param *: Any other parameters that will be understood by concrete implementation of ``compute_quaternions``.
        :return: same dataset with orbit state vector

        :warning: All child classes are expected to define :meth:`compute_quaternions`. However, variations about the
            actual parameters are expected between :class:`AbstractOrbitModel` and its child classes. This abstract
            method is not a *real* abstract method as far as OO design is concerned; several tools (like mypy, Pycharm)
            are likely to warn us about incorrect overriding. See this abstract :meth:`compute_quaternions` as just a
            documentation artefact: "All *Orbit Models* are expected to provide a method named ``compute_quaternions``".
            And don't expect to be able to write generic code that calls ``compute_quaternions`` and that will work with
            any specialization of :class:`AbstractOrbitModel`.
        """

    @property
    @abstractmethod
    def info(self) -> dict:
        """
        Compute orbit info elements, like:
          - "utc_anx"
          - "period_jd"

        :return: dictionary with orbit elements
        """

    @staticmethod
    def merge_orbits(orbit_list: List[dict], time_ref: TimeRef | str = TimeRef.GPS) -> dict:
        """
        Concatenate the measurements from different orbits structures. The orbits source should
        be sorted from the least precise to the most precise, in the same frame.

        :param list[dict]  orbit_list: List of orbits, sorted by increasing precision
        :param TimeRef|str time_ref:   Time reference to keep in output orbit
        :return: concatenated orbit
        """
        assert len(orbit_list) > 0
        properties = {"frame", "start_date", "stop_date"}
        output_orbit = sub(orbit_list[0], orbit_list[0].keys() & properties)
        # Make sure all orbits are in the same frame #296
        if any(orbit["frame"] != output_orbit["frame"] for orbit in orbit_list):
            raise ValueError("Please use EarthBody.transform_orbit to provide orbits in the same frame")

        # select single time_scale
        if isinstance(time_ref, str):
            time_ref = TimeRef[time_ref]
        scale = time_ref.name
        epoch = orbit_list[0]["times"][scale].get("epoch", DEFAULT_EPOCH)
        unit = orbit_list[0]["times"][scale].get("unit", DEFAULT_UNIT)
        scale_list = list(orbit_list[0]["times"].keys())
        output_orbit["time_ref"] = scale
        output_orbit["times"] = {
            k: {
                "offsets": np.zeros((0,), dtype="float64"),
                "epoch": epoch,
                "unit": unit,
                "ref": k,
            }
            for k in scale_list
        }

        fields = ["positions", "velocities"]
        output_orbit["positions"] = np.zeros((0, 3), dtype="float64")
        output_orbit["velocities"] = np.zeros((0, 3), dtype="float64")
        if "accelerations" in orbit_list[0]:
            fields.append("accelerations")
            output_orbit["accelerations"] = np.zeros((0, 3), dtype="float64")
        if "absolute_orbit" in orbit_list[0]:
            fields.append("absolute_orbit")
            output_orbit["absolute_orbit"] = np.zeros((0,), dtype="int32")

        # fill with orbits
        for cur_obt in orbit_list:
            cur_times = cur_obt["times"][scale]
            cur_start = cur_times["offsets"][0]
            cur_end = cur_times["offsets"][-1]

            # sanity checks on epoch and unit: no mixing
            cur_epoch = cur_times.get("epoch", DEFAULT_EPOCH)
            cur_unit = cur_times.get("unit", DEFAULT_UNIT)
            assert cur_epoch == epoch
            assert cur_unit == unit

            # Check previous PV that must be concatenated before or after
            out_times = output_orbit["times"][scale]["offsets"]
            before_pos = np.searchsorted(out_times, cur_start)
            after_pos = np.searchsorted(out_times, cur_end, side="right")

            # update times
            for key in scale_list:
                output_orbit["times"][key]["offsets"] = np.concatenate(
                    [
                        output_orbit["times"][key]["offsets"][:before_pos],
                        cur_obt["times"][key]["offsets"],
                        output_orbit["times"][key]["offsets"][after_pos:],
                    ]
                )

            # update position/velocity/acceleration
            for field in fields:
                output_orbit[field] = np.concatenate(
                    [
                        output_orbit[field][:before_pos],
                        cur_obt[field],
                        output_orbit[field][after_pos:],
                    ]
                )

            # Update start and stop times.
            if "start_date" in output_orbit:
                output_orbit["start_date"] = min(output_orbit["start_date"], cur_obt["start_date"])
            if "stop_date" in output_orbit:
                output_orbit["stop_date"] = max(output_orbit["stop_date"], cur_obt["stop_date"])

        return output_orbit
