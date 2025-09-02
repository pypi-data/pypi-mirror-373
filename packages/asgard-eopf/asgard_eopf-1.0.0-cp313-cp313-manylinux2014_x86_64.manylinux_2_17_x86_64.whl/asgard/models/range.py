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
Module for range propagation model
"""

import numpy as np

from asgard.core.frame import FrameId
from asgard.models.propagation import PropagationModel


class GroundRangePropagationModel(PropagationModel):
    """
    Perform localisation of a target that lies:

      - inside a plane, containing the reference point, and orthogonal to spacecraft velocity
      - at a specific signed distance from the reference point

    The reference point is the intersection of the line of sight with body surface.
    """

    def sensor_to_target(
        self,
        # dict dataset values
        dataset: dict,
        # LOS origins and directions keys
        los_pos_key: str = "los_pos",
        los_vec_key: str = "los_vec",
        # Acquisition times keys
        time_key: str = "times",
        # Other keys
        spacecraft_velocities_key: str = "orb_vel",
        gnd_coords_key: str = "gnd_coords",
        altitude: float | np.ndarray | None = None,
        ac_dist_key: str = "ac_dist",
    ):  # pylint: disable=arguments-differ, too-many-arguments
        """
        Direct location with effect correction in inertial frame.

        :param dict dataset: dataset with the below keys

        LOS origins and directions in inertial frame for each datetime

        :param str los_pos_key: LOS origins as x,y,z, mandatory
        :param str los_vec_key: LOS directions as x,y,z, mandatory
        :param str time_key: LOS dates, as a time array structure, mandatory

        Others

        :param str spacecraft_velocities_key: Spacecraft velocities for each datetime as x,y,z,
            mandatory only for the aberration of light correction
        :param str gnd_coords_key: Output ground coordinates for each datetime as longitude,latitude,altitude
        :param float altitude: if not None, use this value as constant altitude for intersection

        """

        # prepare internal dataset
        sub_dataset = {}
        sub_dataset[los_pos_key] = dataset[los_pos_key]
        sub_dataset[los_vec_key] = dataset[los_vec_key]
        sub_dataset[time_key] = dataset[time_key]
        sub_dataset[spacecraft_velocities_key] = dataset.get(spacecraft_velocities_key, np.empty((0,)))

        super().sensor_to_target(
            sub_dataset,
            los_pos_key=los_pos_key,
            los_vec_key=los_vec_key,
            time_key=time_key,
            spacecraft_velocities_key=spacecraft_velocities_key,
            gnd_coords_key="ref_points",
            altitude=altitude,
        )

        # convert velocity to EF (replace orb_pos with los_pos, which should be an approximation
        # good enough). We are only using the velocity anyway.
        self.body.change_reference_frame(
            sub_dataset,
            frame_in=FrameId.EME2000,
            frame_out=FrameId.EF,
            fields_in=[time_key, los_pos_key, spacecraft_velocities_key],
            fields_out=["orb_pos_ef", "orb_vel_ef"],
        )

        # compute ground range from ref_points
        output_gnd = np.array(sub_dataset["ref_points"])
        pos = 0
        for pnt, dist, normal in zip(sub_dataset["ref_points"], dataset[ac_dist_key], sub_dataset["orb_vel_ef"]):
            if not np.any(np.isnan(pnt)):
                output_gnd[pos] = self.body.ground_range(pnt, dist, normal)
            pos += 1

        dataset[gnd_coords_key] = output_gnd

        return dataset
