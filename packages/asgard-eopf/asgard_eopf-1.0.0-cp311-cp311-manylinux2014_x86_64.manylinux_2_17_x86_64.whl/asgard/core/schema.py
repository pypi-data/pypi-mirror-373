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
Schema module, provides functions to validate input data structures
"""

import sys

import numpy as np
import xarray as xr
from jsonschema import validators
from jsonschema.exceptions import ValidationError
from zarr.storage import FSStore

# Issue: we force the use of 2020 draft validator...
_OldValidator = validators.Draft202012Validator

# TODO: the reference to timescale should be removed here (except in ORBIT_STATE_VECTORS_SCHEMA.start_date...),
# since an additional "ref" field is added in time array schema
ASCII_TIMESTAMP_SCHEMA = {
    "type": "string",
    "pattern": "^(TAI=|UTC=|UT1=|GPS=)?[0-9]{4}-[0-9]{2}-[0-9]{2}(_|T)[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?$",
}
"""
Pattern that describes stringified timestamp format.

A simplified definition is:

.. code-block:: python

    "(TAI=|UTC=|UT1=|GPS=)?YYYY-MM-DD[_T]hh:mm:ss(.[0-9]+)?"

:meta hide-value:
"""

TIMESCALE_NAME_SCHEMA = {
    "enum": ["TAI", "UTC", "UT1", "GPS"],
}


def generate_array_schema(element_type: str, *shape) -> dict:
    """
    Generate a JSON schema for a numpy array based on the input type and shape

    Input args are used as array shape
    """
    output = {
        "type": "array",
        "dtype": element_type,
    }
    if shape:
        output["shape"] = shape
    return output


def generate_float64_array_schema(*shape) -> dict:
    """
    Generate a JSON schema for a float64 numpy array based on the input shape

    Input args are used as array shape
    """
    return generate_array_schema("float64", *shape)


def refining_axis(*axis):
    """
    Generate a JSON schema for a float64 numpy array for multiple axis

    Axis names are provided in input
    """
    return {
        "type": "object",
        "properties": {this_axis: generate_float64_array_schema(":") for this_axis in axis},
        "required": [*axis],
        "additionalProperties": False,
    }


def generate_time_array_schema(*shape) -> dict:
    """
    Generate a JSON schema for a time array based on the input shape.

    Input args are used as array shape
    """
    return {
        "type": "object",
        "properties": {
            "offsets": generate_float64_array_schema(*shape),
            "unit": {"type": "string", "pattern": "^(d|s)$"},
            "epoch": ASCII_TIMESTAMP_SCHEMA,
            "ref": TIMESCALE_NAME_SCHEMA,
        },
        "required": ["offsets"],
        "additionalProperties": False,
    }


TIME_ARRAY_SCHEMA = generate_time_array_schema(":")
"""
Pattern used to express one-dimensional arrays of processing times.

A simplified definition is:

.. code-block:: python

    {
        "type": "object",
        "properties": {
            "offsets": generate_float64_array_schema(*shape),
            "unit": {"type": "string", "pattern": "^(d|s)$"},
            "epoch": ASCII_TIMESTAMP_SCHEMA,
            "ref": TIMESCALE_NAME_SCHEMA,
        },
        "required": ["offsets"],
        "additionalProperties": False,
    }

:meta hide-value:
"""

TIME_ARRAY_SCHEMA_2D = generate_time_array_schema(":", ":")

TIME_ARRAY_SCHEMA_ND = generate_time_array_schema()


def generate_timescale_array_schema(*shape) -> dict:
    """
    Generate a JSON schema for a timescale array with custom shape

    Input args are used as time array shape
    """
    return {
        "type": "object",
        "properties": {
            "TAI": generate_time_array_schema(*shape),
            "UTC": generate_time_array_schema(*shape),
            "UT1": generate_time_array_schema(*shape),
            "GPS": generate_time_array_schema(*shape),
        },
        "minProperties": 1,
        "additionalProperties": False,
    }


TIMESCALE_ARRAY_SCHEMA = generate_timescale_array_schema(":")

TIMESCALE_ARRAY_SCHEMA_2D = generate_timescale_array_schema(":", ":")


# dict returns from ExplorerDriver.read_orbit_scenario_file
ORBIT_SCENARIO_SCHEMA = {
    "type": "object",
    "properties": {
        "orbit": {
            "type": "object",
            "properties": {
                "Absolute_Orbit": generate_array_schema("int", [":", 1]),
                "Relative_Orbit": generate_array_schema("int", [":", 1]),
                "Cycle_Number": generate_array_schema("int", [":", 1]),
                "Phase_Number": generate_array_schema("int", [":", 1]),
            },
            "required": ["Absolute_Orbit", "Relative_Orbit", "Cycle_Number", "Phase_Number"],
            "additionalProperties": False,
        },
        "cycle": {
            "type": "object",
            "properties": {
                "Repeat_Cycle": generate_float64_array_schema(":"),
                "Cycle_Length": generate_float64_array_schema(":"),
                "ANX_Longitude": generate_float64_array_schema(":"),
                "MLST": generate_array_schema("<U15", [":", 1]),
                "MLST_Drift": generate_float64_array_schema(":"),
            },
            "required": ["Repeat_Cycle", "Cycle_Length", "ANX_Longitude", "MLST", "MLST_Drift"],
            "additionalProperties": False,
        },
        "anx_time": {
            "type": "object",
            "properties": {
                "TAI": generate_float64_array_schema(":"),
                "UTC": generate_float64_array_schema(":"),
                "UT1": generate_float64_array_schema(":"),
                "unit": {"type": "string", "pattern": "^(d|s)$"},
                "epoch": ASCII_TIMESTAMP_SCHEMA,
            },
            "required": ["TAI", "unit", "epoch"],
            "additionalProperties": False,
        },
        "required": [
            "orbit",
            "cycle",
            "anx_time",
        ],
        "additionalProperties": False,
    },
}

ORBIT_STATE_VECTORS_SCHEMA = {
    "type": "object",
    "properties": {
        "times": TIMESCALE_ARRAY_SCHEMA,
        "positions": generate_float64_array_schema(":", 3),
        "velocities": generate_float64_array_schema(":", 3),
        "accelerations": generate_float64_array_schema(":", 3),
        "absolute_orbit": {"type": "array", "dtype": "int32", "shape": (":",)},
        "frame": {"type": "string"},
        "time_ref": TIMESCALE_NAME_SCHEMA,
        "start_date": ASCII_TIMESTAMP_SCHEMA,
        "stop_date": ASCII_TIMESTAMP_SCHEMA,
    },
    "required": [
        "times",
        "positions",
        "velocities",
    ],
    "additionalProperties": False,
}
"""
Schema for defining orbits:

A simplified definition is:

.. code-block:: python

    {
       "type": "object",
       "properties": {
           "times": asgard.core.schema.TIMESCALE_ARRAY_SCHEMA,
           "positions": {"type": "array", "shape": [":", 3], "dtype": "float64"},
           "velocities": {"type": "array", "shape": [":", 3], "dtype": "float64"},
           "accelerations": {"type": "array", "shape": [":", 3], "dtype": "float64"},
           "absolute_orbit": {"type": "array", "dtype": "int32", "shape": (":",)},
           "frame": {"type": "string"},
           "time_ref": TIMESCALE_NAME_SCHEMA,
           "start_date": ASCII_TIMESTAMP_SCHEMA,
           "stop_date": ASCII_TIMESTAMP_SCHEMA,
           },
       "required": ["positions", "velocities", "times"],
    }

:meta hide-value:
"""

ORBIT_AUX_INFO_SCHEMA = {
    "type": "object",
    "properties": {"orbit_state_vectors": ORBIT_STATE_VECTORS_SCHEMA, "orbit_scenario": ORBIT_SCENARIO_SCHEMA},
    "oneOf": [{"required": ["orbit_state_vector"]}, {"required": ["orbit_scenario"]}],
}

QUATERNION_ARRAY = {
    "type": "array",
    "dtype": "float64",
    "shape": [":", 4],
    "description": "Quaternion follow the scalar-last convention",
}

ANGULAR_RATES_ARRAY = {
    "type": "array",
    "dtype": "float64",
    "shape": [":", 3],
    "description": "Angular rates wx, wy, wz",
}

ATTITUDE_SCHEMA = {
    "type": "object",
    "properties": {
        "times": TIMESCALE_ARRAY_SCHEMA,
        "quaternions": QUATERNION_ARRAY,
        "angular_rates": ANGULAR_RATES_ARRAY,
        "frame": {"type": "string"},
        "time_ref": TIMESCALE_NAME_SCHEMA,
        "max_gap": {"type": "number"},
        "start_date": ASCII_TIMESTAMP_SCHEMA,
        "stop_date": ASCII_TIMESTAMP_SCHEMA,
    },
    "required": [
        "times",
        "quaternions",
    ],
    "additionalProperties": False,
}

AOCS_MODEL_SCHEMA = {
    "type": "object",
    "properties": {
        "frame": {"type": "string"},
        "aocs_mode": {"type": "string", "enum": ["YSM", "ZD"]},
    },
    "required": [
        "aocs_mode",
    ],
    "additionalProperties": False,
}
"""
Alternative ways to express attitude configuration

    .. code-block:: python

        {
          "aocs_mode": "GPM|LNP|YSM|ZDOPPLER"
        }

    .. note::

        * Only YSM (Yaw Steering Mode) is supported at the moment

:meta hide-value:
"""

# ~ #:
# ~ ATTITUDE_SCHEMA = {
# ~ "type": "object",
# ~ "oneOf": [
# ~ ATTITUDE_SCHEMA,
# ~ AOCS_MODEL_SCHEMA,
# ~ ],
# ~ }

NAVATT_SCHEMA = {
    "type": "object",
    "properties": {
        "orbit": ORBIT_STATE_VECTORS_SCHEMA,
        "attitude": ATTITUDE_SCHEMA,
        "times": TIME_ARRAY_SCHEMA,  # expect GPS
        "oop": {
            "type": "array",
            "description": "On-orbit position  for each navatt packet (deg)",
            "minItems": 1,
            "items": {"type": "number"},
        },
    },
    "required": [
        "orbit",
        "attitude",
        "times",
        "oop",
    ],
    "additionalProperties": False,
}

TEXT_FILE_CONTENT = {"type": "array", "minItems": 1, "items": {"type": "string"}}

COMMON_DEFINITIONS = {
    "ascii_timestamp": ASCII_TIMESTAMP_SCHEMA,
    "timescale_name": TIMESCALE_NAME_SCHEMA,
    "time_array": TIME_ARRAY_SCHEMA,
    "time_array_2d": TIME_ARRAY_SCHEMA_2D,
    "timescale_array": TIMESCALE_ARRAY_SCHEMA,
    "timescale_array_2d": TIMESCALE_ARRAY_SCHEMA_2D,
    "orbit": ORBIT_STATE_VECTORS_SCHEMA,
    "attitude": ATTITUDE_SCHEMA,
    "navatt": NAVATT_SCHEMA,
}

DEM_DATASET_SCHEMA = {
    "oneOf": [
        {"type": "string", "description": "Local path to DEM (zarr of legacy format)"},
        {"type": "zarr.storage.FSStore", "description": "Store pointing to a remote to Zarr dataset"},
        {"type": "xarray.Dataset", "description": "Xarray dataset opened from a Zarr dataset"},
    ],
}


def _is_ndarray(checker, instance) -> bool:  # pylint: disable=unused-argument
    """
    Type checker for arrays that accepts :class:`list` and :class:`numpy.ndarray`.
    """
    return _OldValidator.TYPE_CHECKER.is_type(instance, "array") or isinstance(instance, np.ndarray)


def _has_the_right_shape(validator, expected_shape, array_instance, schema):  # pylint: disable=unused-argument
    """
    Check whether the expected shape matches the :class:`numpy.ndarray` shape.

    :param validator:      instance of the validator calling this checker
    :param expected_shape: value the shape of the expected (tuple/list)
    :param array_instance: :class:`numpy.ndarray` to check
    :param schema:         the part of the schema where this validator is used

    Will be rejected:
    - Shapes not expressed as a :class:`list` or a :class:`tuple`,
    - :class:`list` instances while a multi-dimensional shape is expected
    - 1d :class:`list` of the wrong shape.
    - :class:`numpy.ndarray` of the wrong shape.
    """
    current_shape = None
    dict_type = False
    if not isinstance(expected_shape, (tuple, list)):
        yield ValidationError(
            f"The expected shape ({expected_shape}) isn't a list but a {expected_shape.__class__.__name__}"
        )
    elif isinstance(array_instance, list):
        if len(expected_shape) > 1:
            # Let's reject list of lists, and force the use of ndarrays!
            yield ValidationError(
                f"A list of lists has been received while a {len(expected_shape)}d shape is expected "
                f"{expected_shape}. Use a np.ndarray instead!"
            )
        current_shape = (len(array_instance),)
    elif isinstance(array_instance, dict):
        # We will checked when going through dict
        dict_type = True
    else:
        current_shape = array_instance.shape

    if not dict_type:
        nb_dim = len(current_shape)
        if nb_dim != len(expected_shape):
            yield ValidationError(f"Wrong number of dimensions in array, got {nb_dim}, expected {len(expected_shape)}")

        for idx, cur_dim, exp_dim in zip(range(nb_dim), current_shape, expected_shape):
            if isinstance(exp_dim, int) and cur_dim != exp_dim:
                yield ValidationError(f"Dimension {idx} differs, got {cur_dim}, expected {exp_dim}")

    # else : pass


def _has_the_right_element_dtype(validator, expected_dtype, array_instance, schema):  # pylint: disable=unused-argument
    """
    Check whether the expected elements dtype matches the :method:`numpy.ndarray.dtype`

    :param validator:      instance of the validator calling this checker
    :param expected_dtype: expected dtype for the array elements
    :param array_instance: :class:`numpy.ndarray` to check
    :param schema:         the part of the schema where this validator is used

    Will be rejected:
    - arrays for which element dtype are not compatible with the expected dtype. In other words narrowing convertions
      from the array dtype toward the expected dtype would be rejected.
      i.e. the function yields a :class:`jsonschema.exceptions.ValidationError` when
      ``np.find_common_type([array_dtype, expected_dtype], []) != expected_dtype``
    - :class:`list` instances -- "dtype" property is only accepted on :class:`numpy.ndarray` instances.
    """
    actual_dtype = None
    dict_type = False
    # 1. Extract the actual dtype that depends on the kind of array
    if isinstance(array_instance, np.ndarray):
        actual_dtype = array_instance.dtype
    elif isinstance(array_instance, list):
        # Note: we could convert the list into a np.ndarray to check the dtype. But then this
        # would imply on-the-fly convertions to arrays that may be "heavy".
        # instead, we force the end-user code to use np.ndarray objets from the start.
        yield ValidationError(
            f"Unexpected array type for 'dtype' property: {array_instance.__class__.__name__}."
            " Only numpy.ndarray support 'dtype' property"
        )
    elif isinstance(array_instance, dict):
        # We will checked when going through dict
        dict_type = True
    else:
        yield ValidationError(f"Unexpected array type for 'dtype' property: {array_instance.__class__.__name__}.")

    # 2. Then check this is compatible with the expressed contraint
    # Several policies are possible:
    # - the actual dtype shall be more relaxed than the expected dtype
    #   ~> narrowing (passing doubles while ints are expected) seems a bad idea
    #   => reject
    # - the actual dtype shall be exactly the expected dtype
    #   => of course!!
    # - the actual dtype shall be more constrained than the expected dtype
    #   ~> let's do that for now thanks to np.promote_types()
    # Note: find_common_dtype() becomes deprecated in Numpy 1.25
    if not dict_type:
        if np.promote_types(actual_dtype, expected_dtype) != expected_dtype:
            yield ValidationError(
                f"Expecting {expected_dtype} for elements dtype, but array contain {actual_dtype} elements."
                f" They cannot be converted to {expected_dtype} without precision loss."
            )


def _is_earth_body(checker, instance) -> bool:  # pylint: disable=unused-argument
    """
    Check if a given instance is a :class:`asgard.models.body.EarthBody`
    """
    target_class = sys.modules["asgard.models.body"].EarthBody
    return isinstance(instance, target_class)


def _is_time_reference(checker, instance) -> bool:  # pylint: disable=unused-argument
    """
    Check if a given instance is a :class:`asgard.models.time.TimeReference`
    """
    target_class = sys.modules["asgard.models.time"].TimeReference
    return isinstance(instance, target_class)


def _is_time_based_transform(checker, instance) -> bool:  # pylint: disable=unused-argument
    """
    Check if a given instance is a TimeBasedTransform
    """
    target_class = sys.modules["asgard.core.transform"].TimeBasedTransform
    return isinstance(instance, target_class)


def _is_zarr_fsstore(checker, instance) -> bool:  # pylint: disable=unused-argument
    """
    Check if a given instance is a zarr.storage.FSStore
    """
    return isinstance(instance, FSStore)


def _is_xr_dataset(checker, instance) -> bool:  # pylint: disable=unused-argument
    """
    Check if a given instance is a xarray.Dataset
    """
    return isinstance(instance, xr.Dataset)


def _setup_validator_class():
    """
    Wrapper that make sure ASGARD schema validators are properly configured.

    Initialize type checkers and validators
    """

    type_checker = _OldValidator.TYPE_CHECKER.redefine_many(
        {
            "array": _is_ndarray,
            "asgard.models.time.TimeReference": _is_time_reference,
            "asgard.core.transform.TimeBasedTransform": _is_time_based_transform,
            "asgard.models.body.EarthBody": _is_earth_body,
            "zarr.storage.FSStore": _is_zarr_fsstore,
            "xarray.Dataset": _is_xr_dataset,
        }
    )
    # To support another type name, use for instance "ndarray" + _is_ndarray for instance.

    validators_map = dict(_OldValidator.VALIDATORS)
    validators_map["shape"] = _has_the_right_shape
    validators_map["dtype"] = _has_the_right_element_dtype

    return validators.extend(
        _OldValidator,
        validators=validators_map,
        type_checker=type_checker,
    )


_AsgardValidator = _setup_validator_class()


def validate_or_throw(instance, schema: dict, *args, **kwargs) -> None:
    """
    Check if the input dataset is valid. An exception is raised when:

        - the instance is invalid (jsonschema.exceptions.ValidationError)
        - the schema itself is invalid (jsonschema.exceptions.SchemaError)

    The schema is based on the official syntax, with the following changes:

        - "array": accepts :class:`list`, or Numpy or Numpy-like :class:`numpy.ndarray`. It will be usefull to avoid
          converting large datasets into lists of lists to match the standard JSON syntax.

    More custom type may be defined if needed (such as "dataset" for xarray.Dataset)
    Validation is performed by jsonschema.

    :param instance: Python structure to validate
    :raises jsonschema.exceptions.ValidationError: if the instance is invalid
    :raises jsonschema.exceptions.SchemaError: if the schema is invalid
    :param schema: validation schema
    """
    validator = _AsgardValidator(schema)
    validator.validate(instance, *args, **kwargs)


def does_validate(instance, schema: dict) -> bool:
    """
    Check if the input dataset is valid.

    The schema is based on the official syntax, with the following changes:

        - "array": accepts :class:`list`, or Numpy or Numpy-like :class:`numpy.ndarray`. It will be usefull to avoid
          converting large datasets into lists of lists to match the standard JSON syntax.


    More custom type may be defined if needed (such as "dataset" for xarray.Dataset)
    Validation is performed by jsonschema.

    :param instance: Python structure to validate
    :param schema: validation schema
    :return: true/false
    """
    try:
        validate_or_throw(instance, schema)
        return True
    except ValidationError:
        return False
