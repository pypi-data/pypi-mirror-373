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
"""
Module for generic platform modelization
"""

from collections import defaultdict
from typing import List, Tuple, Union

from asgard import ASGARD_VALIDATE_SCHEMAS
from asgard.core import schema
from asgard.core.platform import AbstractPlatformModel
from asgard.core.transform import (
    HomothetyTransform,
    RigidTransform,
    StaticTransform,
    TimeBasedTransform,
)
from asgard.models.thermoelastic import (  # noqa: F401  # pylint: disable=unused-import
    ThermoelasticModel,
)

# Enumeration of different rotation representations
ROTATION_REPR_MAP = {
    "matrix": schema.generate_float64_array_schema(3, 3),
    "quaternion": schema.generate_float64_array_schema(4),
    "vector": schema.generate_float64_array_schema(3),
}


def find_shortest_path(graph: dict, start: str, goal: str):
    """
    Function to find the shortest path between two nodes of a graph. Source is
    https://www.geeksforgeeks.org/building-an-undirected-graph-and-finding-shortest-path-using-dictionaries-in-python

    :param graph: dict that stores related direct states for each state
    :type graph: collections.defaultdict
    :param str start: first state name
    :param str goal: last state name
    :return: list of state names from start to goal
    """
    explored = []

    # Queue for traversing the graph
    queue = [[start]]

    # If the desired node is reached
    if start == goal:
        return [start]

    # Loop to traverse the graph with the help of the queue
    while queue:
        path = queue.pop(0)
        node = path[-1]

        # Condition to check if the current node is not visited
        if node not in explored:
            neighbours = graph[node]

            # Loop to iterate over the neighbours of the node
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)

                # Condition to check if the neighbour node is the goal
                if neighbour == goal:
                    # new_path --> Shortest path
                    return new_path
            explored.append(node)

    # Condition when the nodes are not connected
    return []


class GenericPlatformModel(AbstractPlatformModel):
    """
    Handles all transformations from Orbital frame to the instrument frame for a generic platform model.

    The model store a list of states, which defines the transformations (rotation and translation)
    with respect to an initial state. The first state that can be used is "platform".
    """

    def __init__(self, **kwargs):
        """
        Constructor

        Checks the parameters valides the model schema.
        """
        super().__init__(**kwargs)
        # Definition of edges for every state transition (direct and inverse)
        # Format storage in edges can be "quaternion" or "quaternion_lut"
        # - Get state transition graph
        # - Duplicates config with all states in specific format and all directions
        self.states, self.graph = self.get_states_link()
        self.aliases = kwargs.get("aliases", {})

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for frame transformations defined in GenericPlatformModel

        .. code-block:: json

            {
              "type": "object",
              "properties": {
                "name": {"type": "string"},
                "origin": {"type": "string"},
                "rotation": {"type": "ndarray"},
                "translation": {"type": "ndarray"},
              },
              "required": ["name", "origin", "rotation"],
            }

        :download:`JSON schema <doc/scripts/init_schema/schemas/GenericPlatformModel.schema.json>`
        """
        return {
            "type": "object",
            "required": ["states"],
            "properties": {
                "states": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "origin": {"type": "string"},
                            "rotation": {
                                "oneOf": [
                                    ROTATION_REPR_MAP["matrix"],
                                    ROTATION_REPR_MAP["quaternion"],
                                    ROTATION_REPR_MAP["vector"],
                                ]
                            },
                            "translation": ROTATION_REPR_MAP["vector"],
                            "homothety": ROTATION_REPR_MAP["vector"],  # support homotheties (=scale) for S2
                            "euler_order": {
                                "type": "string",
                                "enum": ["XYZ", "YZX", "ZXY", "YXZ", "XZY", "ZYX"],
                            },
                            "time_based_transform": {
                                "oneOf": [
                                    {"type": "object"},
                                    {"type": "asgard.core.transform.TimeBasedTransform"},
                                ],
                            },
                        },
                        "anyOf": [
                            {"required": ["homothety"]},
                            {"required": ["rotation"]},
                            {"required": ["translation"]},
                            {"required": ["time_based_transform"]},
                        ],
                        "required": ["name", "origin"],
                        "additionalProperties": False,
                    },
                },
                "aliases": {
                    "type": "object",
                    "patternProperties": {"^.+$": {"type": "string"}},
                },
            },
        }

    def check_frame_names(self, frame_in, frame_out) -> Tuple[str, str]:
        """
        Check if specified frames in input exists and resolve aliases

        :param str frame_in: Name of input frame
        :param str frame_out: Name of output frame
        :return: tuple with resolved frame_in and frame_out
        """

        # resolve aliases
        solved_frame_in = self.aliases.get(frame_in, frame_in)
        solved_frame_out = self.aliases.get(frame_out, frame_out)

        assert solved_frame_in in self.get_states_list(), (
            f"Input frame {solved_frame_in} " f"doesn't exist. Available states : {self.get_states_list()}"
        )
        assert solved_frame_out in self.get_states_list(), (
            f"Output frame {solved_frame_out} " f"doesn't exist. Available states : {self.get_states_list()}"
        )

        return solved_frame_in, solved_frame_out

    def get_states_list(self):
        """
        Get list of states defined in GenericPlatformModel

        :return: list of referenced states
        """
        state_names = {state["name"] for state in self.states}
        return list(state_names)

    @staticmethod
    def parse_transform(state: dict) -> Union[StaticTransform, TimeBasedTransform]:
        """
        Instanciate the transform corresponding to current "state"

        :param dict state: current state definition
        :return: transform (either static or time-based)
        """
        if "time_based_transform" in state:
            input_transfo = state["time_based_transform"]
            if isinstance(input_transfo, TimeBasedTransform):
                transform = input_transfo
            else:
                transform = TimeBasedTransform.build(**input_transfo)
        elif "homothety" in state:
            transform = HomothetyTransform(homothety=state["homothety"])
        else:
            transform = RigidTransform(
                translation=state.get("translation"),
                rotation=state.get("rotation"),
                euler_order=state.get("euler_order"),
            )
        return transform

    def get_states_link(self):
        """
        Creates a graph storing links between states

        :return: list of links between states
        """
        graph = defaultdict(list)
        states = []
        for state in self.config["states"]:
            name, origin = state["name"], state["origin"]
            # Add state origin and name to graph for later scan_data function
            graph[name].append(origin)
            graph[origin].append(name)
            # Decode transform
            transform = self.parse_transform(state)

            states.append(
                {
                    "name": name,
                    "origin": origin,
                    "transform": transform,
                }
            )
            # Add inverse state transformation into edges dataset
            states.append(
                {
                    "name": origin,
                    "origin": name,
                    "transform": transform.inv(),
                }
            )

        return states, graph

    def scan_data(self, frame_in: str, frame_out: str) -> List[Union[StaticTransform, TimeBasedTransform]]:
        """
        Search in platform config for transformations from one state to another

        :param str frame_in: Name of input frame
        :param str frame_out: Name of output frame
        :return: data_of_interest, list of transforms from frame_in to frame_out
        """

        # Finds shortest path from frame_in to frame_out state
        shortest_path = find_shortest_path(self.graph, frame_in, frame_out)

        data_of_interest = []
        for ind in range(1, len(shortest_path)):
            for state in self.states:
                if shortest_path[ind] == state["name"] and shortest_path[ind - 1] == state["origin"]:
                    data_of_interest.append(state["transform"])
                    break
            else:
                raise ValueError("No match found for state origin and name in self.states")

        return data_of_interest

    def compute_transforms(self, frame_in: str, frame_out: str, time_in) -> StaticTransform:
        """
        Compute equivalent transformation to switch from one given state to another

        :param str frame_in: Name of input frame
        :param str frame_out: Name of output frame
        :param time_in: Array containing times for dynamic transforms; see :const:`asgard.cord.schema.TIME_ARRAY_SCHEMA`
        :return: equivalent transform object
        """

        if time_in is not None and ASGARD_VALIDATE_SCHEMAS:
            schema.validate_or_throw(time_in, schema.TIME_ARRAY_SCHEMA)

        # Checks if frame_in and frame_out are in self.states and manages upper/lower case
        frame_in_checked, frame_out_checked = self.check_frame_names(frame_in, frame_out)

        # Early stop if both frames are the same
        if frame_in_checked == frame_out_checked:
            # produce an identity transform
            return RigidTransform()

        # Finds all states of interest from frame_in to frame_out in self.states
        raw_transfo_list = self.scan_data(frame_in_checked, frame_out_checked)

        # First filtering: compose consecutive static transforms
        refined_transfo_list = [raw_transfo_list[0]]
        for transfo in raw_transfo_list[1:]:
            prev_transfo = refined_transfo_list[-1]
            if isinstance(transfo, StaticTransform) and isinstance(prev_transfo, StaticTransform):
                refined_transfo_list[-1] = transfo * prev_transfo
            else:
                refined_transfo_list.append(transfo)

        # Second step: evaluate time-base transforms
        for index, transfo in enumerate(refined_transfo_list):
            if isinstance(transfo, TimeBasedTransform):
                refined_transfo_list[index] = transfo.estimate(time_in)

        # Third step: combine all transforms
        final_transform = refined_transfo_list[0]
        for transfo in refined_transfo_list[1:]:
            final_transform = transfo * final_transform

        return final_transform

    def get_transforms(
        self,
        dataset,
        frame_in: str,
        frame_out: str,
        time_in_key: str = "times",
        rotation_key: str = "rotations",
        translation_key: str = "translations",
        matrix_key: str = "matrix",
        homothety_key: str = "homothety",
    ):  # pylint: disable=arguments-differ,too-many-arguments
        """
        Store the equivalent transforms into the dataset

        :param dataset: Dataset with an optional time array
        :param str frame_in: Name of input frame
        :param str frame_out: Name of output frame
        :param str time_in_key: Name of the key for time array to use with any time-based transform
        :param str rotation_key: Name of the key to use to write the list of rotations
        :param str translation_key: Name of the key to use to write the list of translations
        :return dataset: input dataset now containing the new transform operations
        """

        transform = self.compute_transforms(frame_in, frame_out, dataset.get(time_in_key))
        transform_data = transform.dump()
        field_mapping = {
            "translation": translation_key,
            "rotation": rotation_key,
            "matrix": matrix_key,
            "homothety": homothety_key,
        }
        for key in transform_data:
            dataset[field_mapping[key]] = transform_data[key]
        return dataset

    def transform_position(
        self,
        dataset,
        frame_in: str,
        frame_out: str,
        vec_in_key: str = "los_pos",
        time_in_key: str = "times",
        vec_out_key: str | None = None,
    ):  # pylint: disable=arguments-differ
        """
        Transform positions

        :param dataset: Dataset with:

            - "los_pos" array of LOS origins
            - "times" vector of LOS acquisition times (optional)

        :param str frame_in:         Name of input frame
        :param str frame_out:        Name of output frame
        :param str vec_in_key:       Key name of input data to consider for transformation
        :param str time_in_key:      Key name of input data for los_times in dataset
        :param str|None vec_out_key: Key name for output data storage in dataset after transformation
                                     (if None, vec_in_key will be used)
        :return: same dataset with transformed coordinates
        """
        # Compute equivalent transformations
        time_in = dataset.get(time_in_key)
        transform = self.compute_transforms(frame_in, frame_out, time_in)

        # Apply equivalent transformations to input data
        input_array = dataset[vec_in_key]
        output = transform.transform_position(input_array)

        # Select output key
        if vec_out_key:
            out_key = vec_out_key
        else:
            out_key = vec_in_key
        dataset[out_key] = output

        return dataset

    def transform_direction(
        self,
        dataset,
        frame_in: str,
        frame_out: str,
        vec_in_key: str = "los_vec",
        time_in_key: str = "times",
        vec_out_key: str | None = None,
    ):  # pylint: disable=arguments-differ
        """
        Transform direction from an input frame to an output frame. The main difference with
        transform_position is that the translations involved in the frame change are skipped.

        :param dataset: Dataset with:

            - "los_vec" array of LOS directions
            - "times" vectors of LOS acquisition times (optional)

        :param str frame_in:         Name of input frame
        :param str frame_out:        Name of output frame
        :param str vec_in_key:       Key name of input data to consider for transformation
        :param str time_in_key:      Key name of input data for los_times in dataset
        :param str|None vec_out_key: Key name for output data storage in dataset after transformation (if
                                     None, vec_in_key will be used)
        :return: same dataset with transformed coordinates
        """
        # Compute equivalent transformations
        time_in = dataset.get(time_in_key)
        transform = self.compute_transforms(frame_in, frame_out, time_in)

        # Apply equivalent transformations to input data
        input_array = dataset[vec_in_key]
        output = transform.transform_direction(input_array)

        # Select output key
        if vec_out_key:
            out_key = vec_out_key
        else:
            out_key = vec_in_key
        dataset[out_key] = output

        return dataset
