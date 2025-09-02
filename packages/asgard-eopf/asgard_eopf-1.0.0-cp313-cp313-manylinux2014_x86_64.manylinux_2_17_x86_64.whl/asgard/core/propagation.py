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
Module for propagation model abstract class
"""

from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

from .model import AbstractModel

if TYPE_CHECKING:
    from pyrugged.raster.tile_updater import TileUpdater


class AbstractPropagationModel(AbstractModel):
    """
    Handles the propagation model of the electo-magnetic wave between the sensor and the "target"
    (earth, moon, star)
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for line-of-sight propagation.

        May be overriden by derived classes, default is:

        .. code-block:: json

            {
              "type": "object",
              "properties": {
                  "los_pos": {"type": "ndarray"},
                  "los_vec": {"type": "ndarray"},
                  "times": {"type": "ndarray"},
              },
              "required": ["los_pos", "los_vec", "times"],
            }

        :download:`JSON schema <doc/scripts/init_schema/schemas/AbstractPropagationModel.schema.json>`
        """
        return {
            "type": "object",
        }

    @abstractmethod
    def sensor_to_target(self, dataset, **kwargs):
        """
        Compute intersection of line-of-sight with the target

        :param dataset: Dataset with:

            - "los_pos" line-of-sight position array
            - "los_vec" line-of-sight vector array
            - "times" array

        :param field_out: Names of output field
        :return: same dataset with target coordinates
        """

    @property
    def tile_updater(self) -> Optional["TileUpdater"]:
        """
        Method to retrieve the tileupdater initialized in the propagation model to make altitude requests
        :return:
        TileUpdater
        """

        # base implementation doesn't provide it
        return None


# Possible implementations:
# - LightPropagationModel: Handles intersection of LOS with DEM (rugged)
# - SarPropagationModel: Handles conversion between slant range and ground range for SAR sensor
