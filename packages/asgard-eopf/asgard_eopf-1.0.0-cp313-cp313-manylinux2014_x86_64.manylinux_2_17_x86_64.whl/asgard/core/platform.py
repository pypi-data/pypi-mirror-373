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
Module for platform model abstract class
"""

from abc import abstractmethod

from .model import AbstractModel


class AbstractPlatformModel(AbstractModel):
    """
    Handles all transformations from Satellite Orbital Frame to the instrument reference frame.

    The model stores a list of states, which defines the transformations (rotation and translation)
    with respect to an initial state. The first state that can be used is "platform".
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for frame transformations

        May be overriden by derived classes, default is:

        .. code-block:: json

            {
              "type": "object",
              "properties": {"coords": {"type": "ndarray"}, "geom": {"type": "string"}},
              "required": ["coords"],
            }

        :download:`JSON schema <doc/scripts/init_schema/schemas/AbstractPlatformModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {"coords": {"type": "ndarray"}, "geom": {"type": "string"}},
            "required": ["coords"],
        }

    @abstractmethod
    def transform_position(
        self,
        dataset,
        frame_in: str,
        frame_out: str,
        **kwargs,
    ):
        """
        Transform positions...

        :param dataset: Dataset with:

            - "los_pos" array : 3D vectors of LOS origins
        :param str frame_in: Name of input frame
        :param str frame_out: Name of output frame
        :return: Same dataset with transformed coordinates

        :warning: All child classes are expected to define :meth:`transform_position`. However,
            variations about the actual parameters are expected between :class:`AbstractPlatformModel`
            and its child classes. This abstract method is not a *real* abstract method as far as OO
            design is concerned; several tools (like mypy, Pycharm) are likely to warn us about
            incorrect overriding. See this abstract :meth:`transform_position` as just a documentation
            artefact: "All *Platform Models* are expected to provide a method named
            ``transform_position``". And don't expect to be able to write generic code that calls
            ``transform_position`` and that will work with any specialization of
            :class:`AbstractPlatformModel`.
        """

    @abstractmethod
    def transform_direction(
        self,
        dataset,
        frame_in: str,
        frame_out: str,
        **kwargs,
    ):
        """
        Transform direction from an input frame to an output frame. The main difference with
        :meth:`transform_position` is that the translations involved in the frame change are skipped.

        :param dataset: Dataset with:

            - "los_vec" array : 3D vectors of LOS directions

        :param str frame_in: Name of input frame
        :param str frame_out: Name of output frame
        :return: Same dataset with transformed coordinates

        :warning: All child classes are expected to define :meth:`transform_direction`. However,
            variations about the actual parameters are expected between :class:`AbstractPlatformModel`
            and its child classes. This abstract method is not a *real* abstract method as far as OO
            design is concerned; several tools (like mypy, Pycharm) are likely to warn us about
            incorrect overriding. See this abstract :meth:`transform_direction` as just a documentation
            artefact: "All *Platform Models* are expected to provide a method named
            ``transform_direction``". And don't expect to be able to write generic code that calls
            ``transform_direction`` and that will work with any specialization of
            :class:`AbstractPlatformModel`.
        """

    @abstractmethod
    def get_transforms(
        self,
        dataset,
        frame_in: str,
        frame_out: str,
        **kwargs,
    ):
        """
        Compute translations :math:`T` and rotations :math:`R` to go from ``frame_in`` to ``frame_out``. The relation
        between coordinates :math:`X_{in}` and :math:`X_{out}` will be :math:`X_{out} = T + R( X_{in} )`. If a times
        array is used, translations and rotations are estimated for each time.

        :param dataset: Dataset with:

            - "time" array: for time-varying transforms (optional)

        :param str frame_in: Name of input frame
        :param str frame_out: Name of output frame
        :return: Same dataset with translations and rotations

        :warning: All child classes are expected to define :meth:`get_transforms`. However,
            variations about the actual parameters are expected between :class:`AbstractPlatformModel`
            and its child classes. This abstract method is not a *real* abstract method as far as OO
            design is concerned; several tools (like mypy, Pycharm) are likely to warn us about
            incorrect overriding. See this abstract :meth:`get_transforms` as just a documentation
            artefact: "All *Platform Models* are expected to provide a method named
            ``get_transforms``". And don't expect to be able to write generic code that calls
            ``get_transforms`` and that will work with any specialization of
            :class:`AbstractPlatformModel`.
        """
