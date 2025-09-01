#!/usr/bin/env python
# coding: utf8
#
# Copyright 2023 CS GROUP
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
Unit tests for core.schema
"""

import numpy as np
import pytest
from jsonschema.exceptions import ValidationError

import asgard.core.schema as sch


# ====================[ array
def test_schemas_with_lists():
    """
    Simple validation of "array" type with :class:`list`.
    """
    schema = {
        "type": "object",
        "properties": {"coords": {"type": "array"}, "geom": {"type": "string"}},
    }
    # List are OK
    assert sch.does_validate({"coords": [1, 2, 3, 4], "geom": "some geom"}, schema)
    sch.validate_or_throw({"coords": [1, 2, 3, 4], "geom": "some geom"}, schema)

    # Tuples are not
    assert not sch.does_validate({"coords": (1, 2, 3, 4), "geom": "some geom"}, schema)
    with pytest.raises(ValidationError):
        sch.validate_or_throw({"coords": (1, 2, 3, 4), "geom": "some geom"}, schema)


def test_schemas_with_ndarrays():
    """
    Simple validation of "array" type with :class:`numpy.ndarray`
    """
    schema = {
        "type": "object",
        "properties": {"coords": {"type": "array"}, "geom": {"type": "string"}},
    }

    assert sch.does_validate({"coords": np.array([1, 2, 3, 4]), "geom": "some geom"}, schema)
    sch.validate_or_throw({"coords": np.array([1, 2, 3, 4]), "geom": "some geom"}, schema)


def test_schemas_with_constrained_1d_arrays():
    """
    Validation of "ndarray" type with a 1d shape.
    """
    schema = {
        "type": "object",
        "properties": {"coords": {"type": "array", "shape": (4,)}},
    }

    # Valid shapes
    assert sch.does_validate({"coords": [1, 2, 3, 4]}, schema)
    assert sch.does_validate({"coords": np.array([1, 2, 3, 4])}, schema)
    sch.validate_or_throw({"coords": [1, 2, 3, 4]}, schema)
    sch.validate_or_throw({"coords": np.array([1, 2, 3, 4])}, schema)

    # Invalid shapes
    assert not sch.does_validate({"coords": [1, 2, 3]}, schema)
    assert not sch.does_validate({"coords": np.array([1, 2, 3])}, schema)

    with pytest.raises(ValidationError):
        sch.validate_or_throw({"coords": [1, 2, 3]}, schema)
        sch.validate_or_throw({"coords": np.array([1, 2, 4])}, schema)


def test_schemas_with_constrained_2d_arrays():
    """
    Validation of "ndarray" type with a 2d shape.
    """
    schema = {
        "type": "object",
        "properties": {
            "coords": {"type": "array", "shape": (2, 4)},
        },
    }

    # Wrong number of dimensions...
    assert not sch.does_validate({"coords": [1, 2, 3, 4]}, schema)
    assert not sch.does_validate({"coords": [1, 2, 3]}, schema)

    assert not sch.does_validate({"coords": np.array([1, 2, 3, 4])}, schema)
    assert not sch.does_validate({"coords": np.array([1, 2, 3])}, schema)

    with pytest.raises(ValidationError):
        # Invalid shape
        sch.validate_or_throw({"coords": [1, 2, 3]}, schema)
        sch.validate_or_throw({"coords": np.array([1, 2, 4])}, schema)
        sch.validate_or_throw({"coords": np.array([1, 2, 3, 4])}, schema)
        # Don't use lists for n dimension arrays
        sch.validate_or_throw({"coords": [1, 2, 3, 4]}, schema)
        # 2d OK; but list of lists...
        sch.validate_or_throw({"coords": [[1, 2, 3, 4], [1, 2, 3, 4]]}, schema)

        # 2D OK; but wrong shape
        sch.validate_or_throw({"coords": np.array([[1, 2, 3], [2, 3, 4]])}, schema)

    # Right number of dimensions, but list of lists are rejected n dim arrays
    assert not sch.does_validate({"coords": [[1, 2, 3, 4], [1, 2, 3, 4]]}, schema)
    assert not sch.does_validate({"coords": [[1, 2, 3]]}, schema)

    sch.validate_or_throw({"coords": np.array([[1, 2, 3, 4], [2, 3, 4, 4]])}, schema)
    assert sch.does_validate({"coords": np.array([[1, 2, 3, 4], [2, 3, 4, 4]])}, schema)
    assert not sch.does_validate({"coords": np.array([[1, 2, 3], [2, 3, 4]])}, schema)

    # redefine schema with a wildcard
    schema = {
        "type": "object",
        "properties": {
            "coords": {"type": "array", "shape": (":", 4)},
        },
    }
    assert sch.does_validate({"coords": np.array([[1, 2, 3, 4]])}, schema)
    assert sch.does_validate({"coords": np.array([[1, 2, 3, 4], [2, 3, 4, 4]])}, schema)
    assert sch.does_validate(
        {"coords": np.array([[1, 2, 3, 4], [2, 3, 4, 4], [0, 2, 4, 6]])},
        schema,
    )
    assert not sch.does_validate({"coords": np.array([[1, 2, 3], [2, 3, 4]])}, schema)


def test_schemas_with_constrained_dtype():
    """
    Validation of "ndarray" type with expected dtype for array elements.
    """
    schema = {
        "type": "object",
        "properties": {
            "coords": {"type": "array", "dtype": "int64"},
        },
    }
    # List are rejected...
    assert not sch.does_validate({"coords": [1, 2]}, schema)
    assert not sch.does_validate({"coords": [1.0, 2.0]}, schema)

    # Test w/ np.ndarray
    assert sch.does_validate({"coords": np.array([1, 2])}, schema)
    assert not sch.does_validate({"coords": np.array([1.0, 2.0])}, schema)

    with pytest.raises(ValidationError):
        sch.validate_or_throw({"coords": [1.0, 2.0]}, schema)
        sch.validate_or_throw({"coords": np.array([1.0, 2.0])}, schema)
