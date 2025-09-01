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
Base model class that defines input schema for the dataset
"""

from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module

from . import schema


class AbstractModel(ABC):  # pylint: disable=too-few-public-methods
    """
    AbstractModel class, defines input schema and dataset validation
    """

    def __init__(self, **kwargs):
        """
        Model constructor.

        Checks the parameters validate the model schema returned by :meth:`init_schema`. And fill :attr:`config` with
        the input parameters on success.

        :raises jsonschema.exceptions.ValidationError: if the parameters don't valide the schema.
        :raises jsonschema.exceptions.SchemaError: if the schema is invalid
        """
        # validate kwargs schema
        schema.validate_or_throw(kwargs, self.init_schema())
        #: Full model configuration (shallow copy of all construction parameters)
        self.config = kwargs

    @classmethod
    @abstractmethod
    def init_schema(cls) -> dict:
        """
        Expected schema of the dataset, as a JSON schema. Example:

        .. code-block:: json

            {
              "type": "object",
              "properties": {
                "coords": {"type": "ndarray"},
                "geom": {"type": "string"}
              }
            }

        :download:`JSON schema <doc/scripts/init_schema/schemas/AbstractModel.schema.json>`
        """

    def __getstate__(self):
        """
        Called at serialization.
        """

        # When deserializing this class with pickle: call the constructor...
        return self.config

    def __setstate__(self, state):
        """
        Called at deserialization.
        """
        # Force call to constructor to get a coherent object state
        self.__init__(**state)
