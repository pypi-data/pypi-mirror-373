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
Module to implement a CrossTrackPointingModel for range localisation
"""

import numpy as np

from asgard.core.pointing import AbstractPointingModel


class CrossTrackPointingModel(AbstractPointingModel):
    """Model to compute line of sight for Line detector sensors"""

    @classmethod
    def init_schema(cls) -> dict:
        """
        :download:`JSON schema <doc/scripts/init_schema/schemas/CrossTrackPointingModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "resolution": {"type": "number"},
                "center_position": {"type": "number"},
            },
            "required": ["resolution", "center_position"],
        }

    def compute_los(  # pylint: disable=arguments-differ, too-many-positional-arguments
        self,
        dataset,
        coord_in: str = "coords",
        los_pos: str = "los_pos",
        los_vec: str = "los_vec",
        ac_dist: str = "ac_dist",
    ):
        """
        Get the line of sight vectors for each input coordinate

        :param dataset: dataset to read
        :param coord_in: name of image coordinates field to use in dataset
        :param los_pos: name of output field for line of sight position in instrument frame
        :param los_vec: name of output field for line of sight direction in instrument frame
        :param ac_dist: name of output field for across-track signed distance
        """

        coord_array = dataset[coord_in]

        pos_array = np.zeros((len(coord_array), 3), dtype="float64")
        vec_array = np.zeros((len(coord_array), 3), dtype="float64")
        vec_array[:, 2] = 1

        dist_array = (self.config["center_position"] - coord_array[:, 0]) * self.config["resolution"]

        dataset[los_vec] = vec_array
        dataset[los_pos] = pos_array
        dataset[ac_dist] = dist_array
        return dataset
