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
Module for pointing model abstract class
"""

from abc import abstractmethod

from .model import AbstractModel


class AbstractPointingModel(AbstractModel):
    """
    Handles the pointing model of the instrument
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for line-of-sight estimation.

        May be overriden by derived classes, default is:

        .. code-block:: json

            {
              "type": "object",
              "properties": {
                  "coords": {"type": "ndarray"},
                  "times": {"type": "ndarray"},
                  "geom": {"type": "string"},
              },
              "required": ["coords", "times"],
            }

        :download:`JSON schema <doc/scripts/init_schema/schemas/AbstractPointingModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "coords": {"type": "ndarray"},
                "times": {"type": "ndarray"},
                "geom": {"type": "string"},
            },
            "required": ["coords", "times"],
        }

    @abstractmethod
    def compute_los(self, dataset, **kwargs):
        """
        Computes the line of sight for a given measurement.

        :param dataset: Dataset with:

            - "coords" array
            - "times" array
            - "geom" name of geometric unit (optional)

        :param field_out: Names of output fields for LOS positions and direction
        :return: same dataset with line-of-sight
        """

    # TODO define LOS frame ?
