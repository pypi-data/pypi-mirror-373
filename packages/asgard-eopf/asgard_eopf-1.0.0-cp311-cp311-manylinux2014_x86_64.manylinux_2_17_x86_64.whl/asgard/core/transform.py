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
Module for transform classes
"""

from abc import ABC, abstractmethod

import numpy as np
from scipy.spatial.transform import Rotation as R

from asgard.core.math import reorder_euler_angles
from asgard.core.schema import (
    ASCII_TIMESTAMP_SCHEMA,
    TIMESCALE_NAME_SCHEMA,
    does_validate,
    validate_or_throw,
)


class StaticTransform:
    """
    Static transformation, either a single one or a batch
    """

    def __init__(
        self,
        translation: np.ndarray | None = None,
        matrix: np.ndarray | None = None,
    ):
        """
        Constructor

        :param np.ndarray translation: translation to apply (single 3D vector or Nx3 array)
        :param np.ndarray matrix: 3x3 matrix to apply (single or a stack)
        """

        if translation is None:
            self.translation = np.zeros((3,), dtype="float64")
        elif isinstance(translation, np.ndarray):
            self.translation = translation
        else:
            self.translation = np.array(translation)

        self._matrix = None
        if matrix is None:
            self._matrix = np.eye(3, dtype="float64")
        elif isinstance(matrix, np.ndarray):
            self._matrix = matrix
        else:
            self._matrix = np.array(matrix)

        # check shapes
        assert self.translation.shape[-1] == 3, "Expect 3 components as last dimension for translation"
        assert (
            len(self._matrix.shape) >= 2 and self._matrix.shape[-1] == 3 and self._matrix.shape[-2] == 3
        ), "Expect 3x3 matrices"

        # check sizes
        nb_translation = self.translation.size // 3
        nb_matrices = self._matrix.size // 9

        # check determinant
        min_det = np.min(np.abs(np.linalg.det(self._matrix)))
        if min_det < 1e-9:
            raise RuntimeError(f"Matrix determinant too small ({min_det})")

        if nb_translation > 1 and nb_matrices > 1 and nb_translation != nb_matrices:
            raise RuntimeError(
                f"Mismatch between sizes of translation array ({nb_translation})" f" and matrices array ({nb_matrices})"
            )

    @property
    def matrix(self):
        """
        Accessor to internal matrix
        """
        return self._matrix

    def transform_position(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a position

        :param np.ndarray vec: 3D vector to transform
        """
        return self.translation + self.transform_direction(vec)

    def transform_direction(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a direction (i.e. no translation applied)

        :param np.ndarray vec: 3D vector to transform
        """

        vec_array = vec if isinstance(vec, np.ndarray) else np.array(vec, dtype="float64")
        if len(vec_array.shape) > 1:
            output = self._matrix @ vec_array[..., np.newaxis]
            return output[..., 0]
        return self._matrix @ vec_array

    def __len__(self) -> int:
        """
        Length operator
        """
        nb_translation = self.translation.size // 3
        nb_matrices = self._matrix.size // 9

        return max(nb_translation, nb_matrices)

    def inv(self):
        """
        Compute inverse transform

        :return: Inverse transform
        :rtype: StaticTransform
        """
        inv_trans = StaticTransform(matrix=np.linalg.inv(self.matrix))
        inv_trans.translation = -inv_trans.transform_direction(self.translation)
        return inv_trans

    def __mul__(self, other):
        """
        Compose with an other transform
        """
        # check other instance
        if not isinstance(other, StaticTransform):
            return NotImplemented

        # check they have the same length if both are arrays
        my_length = len(self)
        their_length = len(other)
        if my_length > 1 and their_length > 1 and my_length != their_length:
            raise RuntimeError("Can't combine two transformation arrays of different size")

        combined = StaticTransform(matrix=self.matrix @ other.matrix)
        combined.translation = self.translation + self.transform_direction(other.translation)

        return combined

    def dump(self) -> dict:
        """
        Dump the transform content to a dict
        """
        return {"translation": self.translation, "matrix": self.matrix}


class RigidTransform(StaticTransform):
    """
    Rigid transformation (translation + rotation), either a single one or a batch
    """

    def __init__(
        self,
        translation: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        euler_order: str | None = None,
    ):
        """
        Constructor

        :param np.ndarray translation: translation to apply (single 3D vector or Nx3 array)
        :param np.ndarray rotation: rotation to apply (single or a stack)
        :param str euler_order: Order of rotation for Euler angles (default to "XYZ")
        """

        # Call parent constructor
        super().__init__(translation=translation)

        self.rotation = None
        self._build_rotation(rotation, euler_order)

        # check sizes
        nb_translation = self.translation.size // 3
        try:
            nb_rotation = len(self.rotation)
        except TypeError:
            nb_rotation = 1
        if nb_translation > 1 and nb_rotation > 1 and nb_translation != nb_rotation:
            raise RuntimeError(
                f"Mismatch between sizes of translation array ({nb_translation})" f" and rotation array ({nb_rotation})"
            )

    def _build_rotation(self, rotation: np.ndarray, euler_order: str):
        """
        Build the rotation and choose between different kind of definition (quaternion, ...)

        :param np.ndarray rotation: rotation coefficients
        :param str euler_order: Order of rotation for Euler angles (default to "XYZ"). When given,
            the arrays of shape (3, 3) are understood as 3 rotations with Euler angles. Otherwise,
            it is a single 3x3 rotation matrix.
        """
        if rotation is None:
            rot_shape = ()
        elif isinstance(rotation, np.ndarray):
            rot_shape = rotation.shape
        else:
            rot_shape = np.array(rotation).shape

        order = euler_order or "XYZ"

        if rot_shape == (3, 3) and not euler_order:
            # check determinant is close to 1
            det = np.linalg.det(rotation)
            if np.abs(det - 1) > 0.1:
                raise RuntimeError(f"Matrix determinant too far from 1 for a rotation ({det})")
            self.rotation = R.from_matrix(rotation)
        elif rot_shape == (4,):
            self.rotation = R.from_quat(rotation)
        elif rot_shape == (3,):
            self.rotation = R.from_euler(order, reorder_euler_angles(rotation, order))
        elif len(rot_shape) == 3 and rot_shape[1:] == (3, 3):
            # check determinant is close to 1
            det = np.linalg.det(rotation)
            min_det = np.min(det)
            max_det = np.max(det)
            if np.max(np.abs(det - 1)) > 0.1:
                raise RuntimeError(f"Matrix determinants too far from 1 for a rotation [{min_det}, {max_det}]")
            self.rotation = R.from_matrix(rotation)
        elif len(rot_shape) == 2 and rot_shape[1:] == (4,):
            self.rotation = R.from_quat(rotation)
        elif len(rot_shape) == 2 and rot_shape[1:] == (3,):
            self.rotation = R.from_euler(order, reorder_euler_angles(rotation, order))
        else:
            self.rotation = R.identity()

    @property
    def matrix(self):
        """
        Accessor to internal matrix
        """
        return self.rotation.as_matrix()

    def transform_position(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a position

        :param np.ndarray vec: 3D vector to transform
        """
        return self.translation + self.rotation.apply(vec)

    def transform_direction(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a direction (i.e. no translation applied)

        :param np.ndarray vec: 3D vector to transform
        """
        return self.rotation.apply(vec)

    def __len__(self) -> int:
        """
        Length operator
        """
        nb_translation = self.translation.size // 3
        try:
            nb_rotation = len(self.rotation)
        except TypeError:
            nb_rotation = 1

        return max(nb_translation, nb_rotation)

    def inv(self):
        """
        Compute inverse transform

        :return: Inverse transform
        :rtype: RigidTransform
        """
        inv_trans = RigidTransform()
        inv_trans.rotation = self.rotation.inv()
        inv_trans.translation = -inv_trans.rotation.apply(self.translation)
        return inv_trans

    def __mul__(self, other):
        """
        Compose with an other transform
        """
        # check other instance
        if not isinstance(other, StaticTransform):
            return NotImplemented

        if not isinstance(other, RigidTransform):
            return super().__mul__(other)

        # check they have the same length if both are arrays
        my_length = len(self)
        their_length = len(other)
        if my_length > 1 and their_length > 1 and my_length != their_length:
            raise RuntimeError("Can't combine two transformation arrays of different size")

        # R_out = self.R * other.R
        combined = RigidTransform()
        combined.rotation = self.rotation * other.rotation
        combined.translation = self.translation + self.rotation.apply(other.translation)

        return combined

    def dump(self) -> dict:
        """
        Dump the transform content to a dict
        """
        return {"translation": self.translation, "rotation": self.rotation.as_quat()}


class HomothetyTransform(StaticTransform):
    """
    Homothety transformation, either a single one or a batch
    """

    def __init__(
        self,
        homothety: np.ndarray | None = None,
    ):
        """
        Constructor

        :param np.ndarray homothety: homothety to apply (single or a stack)
        """

        # Call parent constructor
        super().__init__()

        if homothety is None:
            self.homothety = np.ones((3,), dtype="float64")
        elif isinstance(homothety, np.ndarray):
            self.homothety = homothety
        else:
            self.homothety = np.array(homothety)

        # check sizes
        if self.homothety.shape[-1] != 3:
            raise RuntimeError(f"Wrong number of components in homothety, got {self.homothety.shape[-1]}, expected 3")

    @property
    def matrix(self):
        """
        Accessor to internal matrix
        """
        return np.eye(3) * self.homothety[..., np.newaxis]

    def transform_position(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a position

        :param np.ndarray vec: 3D vector to transform
        """

        vec_array = vec if isinstance(vec, np.ndarray) else np.array(vec, dtype="float64")
        if len(self) != 1 and self.homothety.shape != vec_array.shape:
            raise ValueError(
                f"Mismatch between transform shape ({self.homothety.shape}) and coordinates shape ({vec_array.shape})"
            )
        return self.homothety * vec_array

    def transform_direction(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a direction (i.e. no translation applied)

        :param np.ndarray vec: 3D vector to transform
        """
        return self.transform_position(vec)

    def __len__(self) -> int:
        """
        Length operator
        """
        return self.homothety.size // 3

    def inv(self):
        """
        Compute inverse transform

        :return: Inverse transform
        :rtype: HomothetyTransform
        """
        inv_trans = HomothetyTransform()
        inv_trans.homothety = 1.0 / self.homothety
        return inv_trans

    def __mul__(self, other):
        """
        Compose with an other transform
        """
        # check other instance
        if not isinstance(other, StaticTransform):
            return NotImplemented

        if not isinstance(other, HomothetyTransform):
            return super().__mul__(other)

        # check they have the same length if both are arrays
        my_length = len(self)
        their_length = len(other)
        if my_length > 1 and their_length > 1 and my_length != their_length:
            raise RuntimeError("Can't combine two transformation arrays of different size")

        combined = HomothetyTransform()
        combined.homothety = self.homothety * other.homothety

        return combined

    def dump(self) -> dict:
        """
        Dump the transform content to a dict
        """
        return {"homothety": self.homothety}


class TimeBasedTransform(ABC):
    """
    Time based transformation
    """

    @classmethod
    def build(cls, **kwargs):
        """
        Create a TimeBasedTransform from a config dictionnary
        """
        for subcls in cls.__subclasses__():
            if does_validate(kwargs, subcls.init_schema()):
                return subcls(**kwargs)

        raise RuntimeError("No model found")

    @classmethod
    @abstractmethod
    def init_schema(cls):
        """
        Define the initialization schema
        """

    @abstractmethod
    def estimate(self, time_array: dict) -> StaticTransform:
        """
        Estimate a series of transforms for input given times

        :param dict time_array: input time array structure (see TIME_ARRAY)
        :return: a :class:`StaticTransform` object with all the transforms stacked
        """

    @abstractmethod
    def inv(self):
        """
        Generate a new :class:`Thermoelastic` model with inversed quaternions
        """


class DynamicRotation(TimeBasedTransform):
    """
    Dynamic rotation with polynomial coefficients
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """

        # check input args
        validate_or_throw(kwargs, DynamicRotation.init_schema())

        self.polynomial = kwargs["rotation"]
        self.epoch = kwargs.get("epoch", "2000-01-01T00:00:00")
        self.unit = kwargs.get("unit", "d")
        self.time_scale = kwargs.get("ref", "GPS")
        self.central_time = kwargs.get("central_time", 0.0)
        self.euler_order = kwargs.get("euler_order", "XYZ")

    @classmethod
    def init_schema(cls):
        """
        Define the initialization schema
        """
        return {
            "type": "object",
            "properties": {
                "rotation": {
                    "type": "array",
                    "shape": [":", 3],
                    "description": "Polynomial coefficient for rotation angles (in radians) of shape "
                    "(D, 3) where D is the maximum degree of the polynomial",
                },
                "epoch": ASCII_TIMESTAMP_SCHEMA,
                "unit": {"type": "string", "pattern": "^(d|s)$"},
                "ref": TIMESCALE_NAME_SCHEMA,
                "central_time": {
                    "type": "number",
                    "description": "Time offset corresponding to x=0 in polynome",
                },
                "euler_order": {"type": "string", "description": "Axis order for Euler angles (default: 'XYZ')"},
            },
            "required": ["rotation"],
            "additionalProperties": False,
        }

    def estimate(self, time_array: dict) -> StaticTransform:
        """
        Estimate a series of transforms for input given times

        :param dict time_array: input time array structure (see TIME_ARRAY)
        :return: a :class:`StaticTransform` object with all the transforms stacked
        """

        scale = time_array.get("ref", "GPS")
        if scale != self.time_scale:
            raise RuntimeError(f"The time scale given ({scale}) is different from the expected one ({self.time_scale})")

        size = len(time_array["offsets"])

        # handle conversion to target epoch, unit

        # pylint: disable=import-outside-toplevel
        from asgard.models.time import TimeReference

        tr = TimeReference()
        target_time_array = tr.change_epoch_and_unit(time_array, epoch=self.epoch, unit=self.unit)

        # center times around central_time
        time_offsets = target_time_array["offsets"] - self.central_time

        # compute angles
        time_exp = np.ones((size,), dtype="float64")
        angles = np.outer(time_exp, self.polynomial[0])
        for coeff in self.polynomial[1:]:
            time_exp = time_exp * time_offsets
            angles += np.outer(time_exp, coeff)

        # build rotations
        return RigidTransform(rotation=angles, euler_order=self.euler_order)

    def inv(self):
        """
        Generate a new :class:`DynamicRotation` model with inversed rotations. All polynomial
        coefficients are multiplied by -1, and the Euler order is reversed.

        :return: DynamicRotation with inversed rotations
        """

        config = {
            "rotation": -self.polynomial,
            "epoch": self.epoch,
            "unit": self.unit,
            "ref": self.time_scale,
            "central_time": self.central_time,
            "euler_order": self.euler_order[::-1],
        }

        return DynamicRotation(**config)
