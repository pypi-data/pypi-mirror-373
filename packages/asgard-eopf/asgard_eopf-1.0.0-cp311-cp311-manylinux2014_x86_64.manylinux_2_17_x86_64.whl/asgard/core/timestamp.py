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
Module for timestamp model abstract class
"""

from abc import abstractmethod

from .model import AbstractModel


class AbstractTimestampModel(AbstractModel):
    """
    Model to retrieve the timestamp for each measurement.
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Input schema for AbstractTimestampModel.

        May be overriden by derived classes, default is:

        .. code-block:: json

            {
              "type": "object",
              "properties": {"coords": {"type": "ndarray"}, "geom": {"type": "string"}},
              "required": ["coords"],
            }

        :download:`JSON schema <doc/scripts/init_schema/schemas/AbstractTimestampModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {"coords": {"type": "ndarray"}, "geom": {"type": "string"}},
            "required": ["coords"],
        }

    @abstractmethod
    def acquisition_times(self, dataset, **kwargs):
        """
        Computes the acquisition times for each image coordinates

        :param dataset: Dataset with:

            - "coords": image coordinates
            - "geom": (optional) name of geometric unit

        :return: input dataset with "times"
        """
