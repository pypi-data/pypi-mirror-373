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
Full sequence of map_blocks tests of EOCFI cython wrappers from Dask workers.
"""

import numpy as np
from distributed import get_worker


def do_everything(
    gpd,
    ewr,
    los_times,
    los_az,
    los_el,
    # block_info=None
):
    """
    Function that do every direct_loc related computations.
    Mainly meant to be executed from Dask
    """
    # logger = logging.getLogger("distributed.worker")
    # if block_info is not None:
    #    extra_log = f" -- {block_info}"
    # else:
    #    extra_log = ""
    # logger.info(f"On {get_worker().id} -> {los_times.shape} elements for {gpd}{extra_log}")
    # logger.debug(f"times: {type(los_times)} -> {los_times}")
    # warning: using GPS time here...
    assert isinstance(los_times, np.ndarray)

    loc_result = gpd.direct_loc_optical(los_times, los_az, los_el, incidence_angles=True, sun_angles=True)

    result = loc_result
    # Inject los_times for indexing
    result["times"] = los_times
    # Inject worker id for test purpose
    result["worker"] = [get_worker().id] * los_times.shape[0]

    # check sun_angles with other functions
    sun_pos, _ = ewr.sun_position(los_times)
    ground_ef = ewr.change_coordinate_system(loc_result["ground"], cs_in=2, cs_out=1)
    sun_angles = ewr.ef_to_topocentric(ground_ef, sun_pos)
    # use zenith angle
    sun_angles[:, 1] = 90.0 - sun_angles[:, 1]
    result["sun_angles"] = sun_angles

    assert np.allclose(sun_angles[:, :2], loc_result["sun"])

    # check incidence_angles with other functions
    orb_pos, _ = gpd.orbit_state_vector(los_times)
    incidence_angles = ewr.ef_to_topocentric(ground_ef, orb_pos)
    # use zenith angle
    incidence_angles[:, 1] = 90.0 - incidence_angles[:, 1]
    result["incidence_angles"] = incidence_angles

    assert np.allclose(incidence_angles[:, :2], loc_result["incidence"])
    return result
