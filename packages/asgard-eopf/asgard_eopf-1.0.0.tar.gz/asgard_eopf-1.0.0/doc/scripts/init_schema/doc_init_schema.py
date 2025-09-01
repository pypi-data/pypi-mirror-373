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
Generate documentation for the "init_schema" methods
"""

import copy
import inspect
import json
import os
import os.path as osp
import pkgutil
import sys

import numpy as np

import asgard
from asgard.core.toolbox import NumpyArrayEncoder


def generate_example(example: dict, name: str, shorten=True, verbose=False):
    """
    Generate a JSON schema example implementation.
    """

    # Shorten too big data.
    if shorten:
        # Only keep the first n elements for each dimension
        def shorten_array(array):
            sub = [slice(0, 10)] * array.ndim
            return array[(..., *sub)]

        def shorten_rec(parent):
            #
            # Recursively parse the dict values and slice numpy arrays.
            if isinstance(parent, dict):
                for key, element in parent.items():
                    if isinstance(element, np.ndarray):
                        parent[key] = shorten_array(element)
                    else:
                        shorten_rec(element)

            # Recursive calls on list elements
            elif isinstance(parent, list):
                for element in parent:
                    shorten_rec(element)

        example = copy.deepcopy(example)
        shorten_rec(example)

    # "examples" directory in this module parent directory
    example_dir = osp.realpath(osp.join(osp.dirname(__file__), "examples"))
    os.makedirs(example_dir, exist_ok=True)

    # Pretty-print the dict into a file
    example_path = osp.join(example_dir, f"{name}.example.json")
    if verbose:
        print(f"Write: {example_path}")
    with open(example_path, "w", encoding="utf-8") as file_ptr:
        json.dump(example, file_ptr, ensure_ascii=False, indent=2, cls=NumpyArrayEncoder)


def generate_init_schema():
    """
    Generate all init_schemas
    """
    package = asgard

    classes = set()

    # "schemas" directory in this module parent directory
    schema_dir = osp.realpath(osp.join(osp.dirname(__file__), "schemas"))
    os.makedirs(schema_dir, exist_ok=True)

    # Recursively find all package modules
    for _, module_str, _ in pkgutil.walk_packages(path=package.__path__, prefix=package.__name__ + ".", onerror=None):
        #
        # Import and find all module classes
        __import__(module_str)
        for _, class_ in inspect.getmembers(sys.modules[module_str]):
            if inspect.isclass(class_) and (class_ not in classes):
                #
                # Save the class (classes are found several times when imported by other modules)
                classes.add(class_)

                # If the "init_schema" method exists
                init_schema = getattr(class_, "init_schema", None)
                if callable(init_schema):
                    #
                    # Call the method, get a dict
                    schema = init_schema()

                    # Pretty-print the dict into a file
                    schema_path = osp.join(schema_dir, f"{class_.__name__}.schema.json")
                    print(f"Write: {schema_path}")
                    with open(schema_path, "w", encoding="utf-8") as file_ptr:
                        json.dump(schema, file_ptr, ensure_ascii=False, indent=2, cls=NumpyArrayEncoder)


if __name__ == "__main__":
    # By default: generate init_schema() JSON schemas
    generate_init_schema()
