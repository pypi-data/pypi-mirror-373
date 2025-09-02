#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2024 CS GROUP
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
JccUtil implementation.
"""

import numpy as np
from forbiddenfruit import curse

# pylint: disable=import-error
from java.lang import Boolean, Byte, Double, Float, Integer, Long, Object, Short, String
from java.util import ArrayList, HashMap

from . import JCC_MODULE

JArray = JCC_MODULE.JArray


class JccUtil:
    """
    Extend Python types (list, dict, ...) with utility methods to convert them
    to Java types (ArrayList, HashMap, ...)
    """

    #############################
    # Python to Java conversion #
    #############################

    @staticmethod
    def guess_element_type(element) -> tuple[type, str] | None:
        """
        Guess the Java type of an element inside a list or dict
        as (Java Object type, "Java primitive type") or None
        """

        if element is None:
            return None

        # Primitive types
        if isinstance(element, (bool, np.bool_)):
            obj_type = Boolean
            type_name = "bool"
        elif isinstance(element, (np.byte, np.ubyte)):
            obj_type = Byte
            type_name = "byte"
        elif isinstance(element, (np.short, np.ushort)):
            obj_type = Short
            type_name = "short"
        elif isinstance(element, (int, np.intc, np.uintc)):
            obj_type = Integer
            type_name = "int"
        elif isinstance(element, (np.int_, np.uint, np.longlong, np.ulonglong)):
            obj_type = Long
            type_name = "long"
        elif isinstance(element, (np.half, np.float16, np.single)):
            obj_type = Float
            type_name = "float"
        # python float -> java double by default (sxgeo uses double)
        elif isinstance(element, (float, np.double, np.longdouble)):
            obj_type = Double
            type_name = "double"
        elif isinstance(element, str):
            obj_type = String
            type_name = "string"
        else:
            # Else it would be a Java object, we return its type
            obj_type = type(element)
            type_name = "object"

        return obj_type, type_name

    @staticmethod
    def guess_list_type(list_) -> tuple[type, str]:
        """
        Guess the Java type of elements inside a list or dict
        as (Java Object type, "Java primitive type")
        """

        # Find unique types
        types = {JccUtil.guess_element_type(element) for element in list_}

        # Remove None from the types
        try:
            types.remove(None)
        except KeyError:
            pass

        # Return the single type or the generic Java Object type
        if len(types) == 1:
            return next(iter(types))
        return Object, "object"

    @staticmethod
    def to_jarray(pyobj, jtype: str | None = None) -> JArray:
        """
        Python iterable object (list, tuple, ...) into Java array conversion.
        :param pyobj: python object
        :param jtype: Java primitive array type as jtype[]. If None: guessed from the Python object.
        """

        # Empty input -> return an empty array
        if len(pyobj) == 0:
            return JArray(jtype or "object")([])

        # Handle n-dim input with n>1
        # Recursive call on each element + store results in a JArray('object')
        if isinstance(pyobj[0], (list, set, tuple, np.ndarray)):
            return JArray("object")([JccUtil.to_jarray(element, jtype) for element in pyobj])

        # Guess the Java primitive type from the first Python list element type
        if jtype is None:
            _, jtype = JccUtil.guess_list_type(pyobj)
        jarray_type = JArray(jtype)

        # Python to JArray conversion
        try:
            return jarray_type(pyobj)
        except TypeError as error:
            raise RuntimeError(f"Error converting python list: {pyobj}\n" f"into Java array: {jtype}[]") from error

    @staticmethod
    def to_array_list(pyobj, jtype: type | None = None) -> ArrayList:
        """
        Python iterable object (list, tuple, ...) into Java ArrayList conversion.
        :param pyobj: python object
        :param jtype: Java ArrayList element type as ArrayList<jtype>. If None: guessed from the Python object.
        """

        # TODO: handle n-dim input with n>1

        # Guess the Java Object type from the first Python list element type
        if jtype is None:
            jtype, _ = JccUtil.guess_list_type(pyobj)

        # Init a Java ArrayList and copy values
        jlist = ArrayList().of_(jtype)
        for value in pyobj:
            try:
                jlist.add(value)
            except Exception as exception:
                raise RuntimeError(
                    f"From python list: {pyobj}\n"
                    f"Error adding {value!r} as {type(value).__name__!r} into "
                    f"java.util.ArrayList<{jtype.__name__}>"
                ) from exception
        return jlist

    @staticmethod
    def to_hash_map(pyobj, jtype_key: type | None = None, jtype_value: type | None = None) -> HashMap:
        """
        Python dict into Java HashMap conversion.
        :param pyobj: python object
        :param jtype_key, jtype_value: Java HashMap key and value types as
        HashMap<jtype_key, jtype_value>. If None: guessed from the Python object.
        """
        # TODO: handle n-dim input with n>1

        # Guess the Java Object type from the first Python dict element types
        if jtype_key is None:
            jtype_key, _ = JccUtil.guess_list_type(pyobj.keys())
        if jtype_value is None:
            jtype_value, _ = JccUtil.guess_list_type(pyobj.values())

        # Init a Java HashMap and copy values
        jmap = HashMap().of_(jtype_key, jtype_value)
        for key, value in pyobj.items():
            try:
                jmap.put(key, value)
            except Exception as exception:
                raise RuntimeError(
                    f"From python dict: {pyobj}\n"
                    f"Error adding ({key},{value}) as "
                    f"({type(key).__name__},{type(value).__name__}) into "
                    f"java.util.HashMap<{jtype_key.__name__},{jtype_value.__name__}>"
                ) from exception
        return jmap

    #############################
    # Java to Python conversion #
    #############################

    @staticmethod
    def from_jarray(jobj: JArray, jarray_type: str) -> tuple:
        """
        Java array to Python tuple conversion.
        :param jobj: python object
        :param jarray_type: JArray type as a string e.g. "int", "double", "object", ...
        """

        # Empty jarray -> return empty tuple
        if not jobj:
            return ()

        # Input is the last-dimension 1D jarray of the requested type
        if JArray(jarray_type).instance_(jobj):
            # Cast to jarray of the requested type
            jobj_cast = JArray(jarray_type).cast_(jobj)

            # int, float, ... -> cast and convert to tuple.
            # For objects, we do it only if it's a 1D array = if the first element is not an array.
            if (jarray_type != "object") or (
                not JArray("object").instance_(jobj_cast[0])
            ):  # type_=='object' and 1st element!=array
                return tuple(jobj_cast)

        # Input is a n-dim jarray with n>1. Cast to JArray of objects.
        jobj_cast = JArray("object").cast_(jobj)

        # Make a recursive call and save results into a tuple
        return tuple(JccUtil.from_jarray(element, jarray_type) for element in jobj_cast)

    @staticmethod
    def add_methods() -> None:
        """
        Extend Python built-in type to convert them to Java types.
        See: https://pypi.org/project/forbiddenfruit/
        Examples:
        [1,2].java() returns java.util.ArrayList<Integer> [1,2]
        [1,2].java (Double) returns java.util.ArrayList<Double> [1.0,2.0]
        {1:'2',3:'4'}.java() returns java.util.HashMap<Integer,String> {1='2',3='4'}
        {1:'2',3:'4'}.java (Double,String) returns java.util.HashMap<Double,String> {1.0='2',3.0='4'}
        """

        curse(list, "array_list", JccUtil.to_array_list)
        curse(set, "array_list", JccUtil.to_array_list)
        curse(tuple, "array_list", JccUtil.to_array_list)
        curse(np.ndarray, "array_list", JccUtil.to_array_list)

        curse(list, "jarray", JccUtil.to_jarray)
        curse(set, "jarray", JccUtil.to_jarray)
        curse(tuple, "jarray", JccUtil.to_jarray)
        curse(np.ndarray, "jarray", JccUtil.to_jarray)

        curse(dict, "hash_map", JccUtil.to_hash_map)

        for jarray_type in (
            "bool",
            "byte",
            "short",
            "int",
            "long",
            "float",
            "double",
            "string",
            "object",
        ):
            # e.g. 1D java JArray<int> to 1D python Tuple[int] conversion
            if jarray_type != "object":
                curse(
                    JArray(jarray_type),
                    "tuple",
                    lambda self, type_=jarray_type: JccUtil.from_jarray(  # pylint: disable=unnecessary-lambda
                        self, type_
                    ),
                )

            # n-dim java JArray<object> to n-dim python Tuple conversion
            else:
                curse(
                    JArray("object"),
                    "tuple",
                    lambda self, last_dimension_type: JccUtil.from_jarray(  # pylint: disable=unnecessary-lambda
                        self, last_dimension_type
                    ),
                )


JccUtil.add_methods()
