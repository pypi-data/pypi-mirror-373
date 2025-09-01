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
Module to implement a LineDetectorTimestampModel for sensors
based on optical line detector
"""

import numpy as np
from scipy import interpolate

from asgard.core.pointing import AbstractPointingModel
from asgard.core.schema import TIME_ARRAY_SCHEMA, TIMESCALE_NAME_SCHEMA
from asgard.core.timestamp import AbstractTimestampModel


class LineDetectorTimestampModel(AbstractTimestampModel):
    """Model to retrieve the timestamp for Line detector

    Constructor is inherited from parent class :class:`core.models.AbstractTimestampModel`
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for dataset, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/LineDetectorTimestampModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {"times": TIME_ARRAY_SCHEMA, "ref": TIMESCALE_NAME_SCHEMA},
            "required": ["times"],
        }

    def acquisition_times(self, dataset, field_in: str = "coords", field_out: str = "times", **kwargs):
        """Compute acquisition times for a dataset of coordinates

        :param dataset: dataset with coords of shape (N, 2), N being the number of coordinates
        :param str field_in: Field name where input times are read
        :param str field_out: Field name where output times are written
        :return: Array of acquisition times
        """
        timestamp = np.array(self.config["times"]["offsets"])
        nof_timestamp = len(timestamp)

        out_times = {key: value for key, value in self.config["times"].items() if key != "offsets"}

        if np.issubdtype(dataset[field_in].dtype, np.integer):
            out_times["offsets"] = timestamp[dataset[field_in][:, 1]]
        elif np.issubdtype(dataset[field_in].dtype, np.float64):
            interp_function = interpolate.interp1d(
                np.arange(0, nof_timestamp), timestamp, bounds_error=False, fill_value="extrapolate"
            )
            out_times["offsets"] = interp_function(dataset[field_in][:, 1])

        dataset[field_out] = out_times
        return dataset


class LineDetectorPointingModel(AbstractPointingModel):
    """Model to compute line of sight for Line detector sensors"""

    @classmethod
    def init_schema(cls) -> dict:
        """
        Specializes expected construction parameters.

        :download:`JSON schema <doc/scripts/init_schema/schemas/LineDetectorPointingModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "unit_vectors": {
                    "type": "object",
                    "patternProperties": {"^.+$": {"type": "array", "dtype": "float64", "shape": [":", 3]}},
                },
            },
            "required": ["unit_vectors"],
        }

    def compute_los(  # pylint: disable=arguments-differ
        self,
        dataset,
        coord_in: str = "coords",
        geom_in: str = "geom",
        los_pos: str = "los_pos",
        los_vec: str = "los_vec",
    ):
        """
        Get the line of sight vectors for each input coordinate

        :param dataset: dataset to read
        :param str coord_in: name of image coordinates field to use in dataset
        :param str geom_in: name of field containing geometric unit
        :param str los_pos: name of output field for line of sight position in instrument frame
        :param str los_vec: name of output field for line of sight direction in instrument frame
        """
        assert geom_in in dataset
        geometric_unit = dataset[geom_in]
        assert geometric_unit in self.config["unit_vectors"]

        nb_los = self.config["unit_vectors"][geometric_unit].shape[0]
        if nb_los > 1:
            los_index = np.arange(0, nb_los)
            interp_function = interpolate.interp1d(
                los_index,
                self.config["unit_vectors"][geometric_unit],
                axis=0,
                bounds_error=False,
                fill_value="extrapolate",
            )
            los_array = interp_function(dataset[coord_in][:, 0])
        else:
            los_array = self.config["unit_vectors"][geometric_unit][dataset[coord_in][:, 0].astype(int)]

        dataset[los_vec] = los_array
        dataset[los_pos] = np.zeros(los_array.shape, dtype="float64")
        return dataset
