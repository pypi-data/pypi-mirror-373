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
Collection of miscellaneous helper functions
"""

from json import JSONEncoder

import numpy as np


def array_get(array, pos: int, default):
    """
    Equivalent of ``dict.get(key, default)``, but for array like structures.
    """
    return array[pos] if pos < len(array) else default


def check_precond(expected: bool, exception, message: str) -> None:
    """
    Helper function that checks preconditions and raises the exception specified on failure.

    :param bool expected:  Predicate asserted (expected to be ``True``)
    :param type exception: Type that inherit :class:`BaseException`
    :param str message:    Message to pass to the ``exception`` constructor on ``expected`` failure.
    :raises exception:     If ``expected`` is ``False``

    .. note::

        - This helper mainly permits to trick pylint in ignoring extra code branches dedicated to check pre-conditions.
    """
    if not expected:
        raise exception(message)


def check_if(expected: bool, message: str, exception: BaseException = RuntimeError) -> None:
    """
    Helper function that checks preconditions and raises the exception specified on failure.

    :param bool expected:  Predicate asserted (expected to be ``True``)
    :param str message:    Message to pass to the ``exception`` constructor on ``expected`` failure.
    :param type exception: Type that inherits :class:`BaseException`
    :raises exception:     If ``expected`` is ``False``

    .. note::

        - This helper replace standard assert where we want to throw a different exception
    """
    if not expected:
        raise exception(message)


def sub(dic: dict, keys: set[str | int]) -> dict:
    """
    Helper function that extracts a subdictionary with the requested keys.
    """
    return {k: dic[k] for k in keys}


class NumpyArrayEncoder(JSONEncoder):
    """Used to write Python dicts with numpy arrays into a JSON file"""

    def default(self, o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        return JSONEncoder.default(self, o)


class NumpyEncoder(JSONEncoder):
    """
    Encode numpy array into json dict, while preserving dtype.

    usage: ``json.dump(config, json_file, cls=NumpyEncoder, indent=1, sort_keys=True)``
    """
    def default(self, o):
        if isinstance(o, np.ndarray):
            return {
                "__numpy__": o.tolist(),
                "__dtype__": str(o.dtype),
            }
        return JSONEncoder.default(self, o)


def numpy_hook(dct: dict):
    """
    Decode numpy array from json, while preserving dtype.

    usage: ``config = json.load(json_file, object_hook=numpy_hook)``
    """
    if {"__numpy__", "__dtype__"} == dct.keys():
        return np.array(dct["__numpy__"], dtype=dct["__dtype__"])
    return dct
