#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022 CS GROUP
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

"""pyrugged Class RandomLandscapeUpdater"""
import math

# pylint: disable=too-many-arguments
import numpy as np

# from java.lang import Long
from org.hipparchus.random import Well19937a  # pylint: disable=import-error
from pyrugged.raster.tile_updater import TileUpdater


class RandomLandscapeUpdater(TileUpdater):
    """Elevation Updater for pyrugged/raster tests"""

    def __init__(self, base_h, initial_scale, reduction_factor, seed, size, n_val):
        """Builds a new instance."""

        if not math.log2(n_val - 1).is_integer():
            raise ValueError("Tile size must be a power of two plus one")

        self.size = size
        self.n_val = n_val

        # As we want to use this for testing and comparison purposes,
        # and as we don't control when tiles are generated, we generate
        # only ONCE a height map with continuity at the edges, and
        # reuse this single height map for ALL generated tiles
        self.height_map = np.zeros((n_val, n_val))
        # seed = Long(seed)
        random = Well19937a(seed)

        # Initialize corners in diamond-square algorithm
        self.height_map[0, 0] = base_h
        self.height_map[0, n_val - 1] = base_h
        self.height_map[n_val - 1, 0] = base_h
        self.height_map[n_val - 1, n_val - 1] = base_h

        scale = initial_scale

        span = self.n_val - 1
        while span > 1:
            # Perform squares step
            for i in np.arange(span / 2, self.n_val, span, dtype=int):
                for j in np.arange(span / 2, self.n_val, span, dtype=int):
                    middle_h = self.mean(
                        i - span / 2,
                        j - span / 2,
                        i - span / 2,
                        j + span / 2,
                        i + span / 2,
                        j - span / 2,
                        i + span / 2,
                        j + span / 2,
                    ) + scale * (random.nextDouble() - 0.5)

                    self.height_map[int(i), int(j)] = middle_h

            # Perform diamonds step
            flip_flop = False
            for i in np.arange(0, self.n_val - 1, span / 2, dtype=int):
                for j in np.arange(0 if flip_flop else span / 2, self.n_val - 1, span, dtype=int):
                    middle_h = self.mean(
                        i - span / 2,
                        j,
                        i + span / 2,
                        j,
                        i,
                        j - span / 2,
                        i,
                        j + span / 2,
                    ) + scale * (random.nextDouble() - 0.5)

                    self.height_map[int(i), int(j)] = middle_h

                    if i == 0:
                        self.height_map[int(self.n_val - 1), int(j)] = middle_h

                    if j == 0:
                        self.height_map[int(i), int(self.n_val - 1)] = middle_h

                flip_flop = not flip_flop

            # reduce scale
            scale *= reduction_factor

            span = span / 2

    def update_tile(self, latitude, longitude, tile):
        """Updates raster tile."""

        step = self.size / (self.n_val - 1)
        min_latitude = self.size * float(np.floor(latitude / self.size))
        min_longitude = self.size * float(np.floor(longitude / self.size))
        tile.set_geometry(min_latitude, min_longitude, step, step, self.n_val, self.n_val)

        for i in range(self.n_val):
            for j in range(self.n_val):
                tile.set_elevation(i, j, self.height_map[i, j])

    def mean(self, i_1, j_1, i_2, j_2, i_3, j_3, i_4, j_4):
        """Mean function"""

        i_1, j_1, i_2, j_2, i_3, j_3, i_4, j_4 = (
            int(i_1),
            int(j_1),
            int(i_2),
            int(j_2),
            int(i_3),
            int(j_3),
            int(i_4),
            int(j_4),
        )

        return (
            self.height_map[int((i_1 + self.n_val) % self.n_val), int(j_1 + self.n_val % self.n_val)]
            + self.height_map[int((i_2 + self.n_val) % self.n_val), int(j_2 + self.n_val % self.n_val)]
            + self.height_map[int((i_3 + self.n_val) % self.n_val), int(j_3 + self.n_val % self.n_val)]
            + self.height_map[int((i_4 + self.n_val) % self.n_val), int(j_4 + self.n_val % self.n_val)]
        ) / 4
