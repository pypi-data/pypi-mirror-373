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
Defines helpers functions for use in pytest tests.
"""
from inspect import signature
from typing import List, Set

import numpy as np
import pytest
from shapely.geometry import Point, Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.ops import nearest_points
from shapely.validation import make_valid

from asgard.core.logger import format_as_tree
from asgard.models.body import EarthBody

# pylint: disable=invalid-name


@pytest.fixture
def allclose_dicts(pytestconfig):
    """
    Defines a ``allclose`` like function to compare dictionary structures -- unlike what :meth:`np.allclose` that is
    restricted to array-like and number data.

    :param dict a:         First dictionary to compare
    :param dict b:         Second dictionary to compare
    :param float rtol:     Relative tolerance
    :param float atol:     Absolute tolerance
    :param bool equal_nan: Whether to compare NaN's as equal.
                           If True, NaN's in a will be considered equal to NaN's in b in the output data.
    :param set ignore:     Set of dictionary keys to ignore when performing the comparison.
                           Examples: ".first-level", ".first-level.second-level.third-level", etc
    :param str a_name:     Alternate name to use for first dictionary.
    :param str b_name:     Alternate name to use for second dictionary.
    :return Whether the fields of the dictionaries are close enough (or equal for non floatting point types)

    .. note::

        - Comparison of numerical types is defered to :meth:`np.allclose`

    .. todo::

        - Improve the difference display (=> register hook on ``pytest_assertrepr_compare``; see pytest-icdiff)
        - Find how messages should be reported: Don't call pytest.fail for cases like ``assert not allclose_dicts(...)``
        - Fix the detection off non numerical types (for instance comparing AbsoluteDates will fail...)
    """
    verbose = pytestconfig.getoption("verbose")
    default_rtol = signature(np.allclose).parameters["rtol"].default
    default_atol = signature(np.allclose).parameters["atol"].default
    default_equal_nan = signature(np.allclose).parameters["equal_nan"].default

    def wrapper(  # pylint: disable=too-many-positional-arguments
        a,
        b,
        rtol: float = default_rtol,
        atol: float = default_atol,
        equal_nan: bool = default_equal_nan,
        ignore: Set[str | int] | None = None,
        a_name: str = "first dictionary",
        b_name: str = "second dictionary",
    ) -> bool:
        return _allclose(
            a,
            b,
            rtol,
            atol,
            equal_nan,
            ignore if ignore else set(),
            a_name,
            b_name,
            verbose,
        )

    return wrapper


def sub(d: dict, keys: Set[str | int]) -> dict:
    """
    Helper function that extracts a subdictionary with the requested keys.
    """
    return {k: d[k] for k in keys}


def _allclose(  # pylint: disable=too-many-positional-arguments, too-many-arguments
    a,
    b,
    rtol: float,
    atol: float,
    equal_nan: bool,
    ignore: Set[str | int],
    a_name: str,
    b_name: str,
    verbose,
) -> bool:
    msg_exclu_a: List[str] = []
    msg_exclu_b: List[str] = []
    msg_diff: List[str] = []
    _allclose_rec("", a, b, msg_exclu_a, msg_exclu_b, msg_diff, 0, rtol, atol, equal_nan, ignore)
    lines = []
    if msg_exclu_a:
        lines.append(f"\nKeys exclusive to {a_name}:")
        lines.extend(msg_exclu_a)
    if msg_exclu_b:
        lines.append(f"\nKeys exclusive to {b_name}:")
        lines.extend(msg_exclu_b)
    if msg_diff:
        lines.append(f"\nDifferences between {a_name} and {b_name}: (rtol: {rtol}, atol: {atol})")
        lines.extend(msg_diff)

    if not lines:
        return True
    if verbose > 0:
        pytest.fail("\n".join(lines))
    # else:
    #     pytest.fail(f"Dictionaries differ:\n{a}\n!= (rtol: {rtol}, atol: {atol})\n{b}")
    return False


def _allclose_rec(  # pylint: disable=too-many-positional-arguments, too-many-arguments
    key,
    a,
    b,
    msg_exclu_a: List[str],
    msg_exclu_b: List[str],
    msg_diff: List[str],
    level: int,
    rtol: float,
    atol: float,
    equal_nan: bool,
    ignore: Set[str | int],
) -> None:
    if isinstance(a, str) and isinstance(b, str):
        if a != b:
            msg_diff.append(f"+- {key!r} -> {a} != {b}")
    elif isinstance(a, dict) and isinstance(b, dict):
        # filter ignore set, to keep the keys that start with `key` parameter
        prefix = f"{key}."
        local_ignore = {str(k).removeprefix(prefix) for k in filter(lambda k: str(k).startswith(prefix), ignore)}
        # logging.info(f"key={key}\t| ignore ({ignore} ==> {local_ignore}")
        a_exclusive_keys = a.keys() - b.keys() - local_ignore
        b_exclusive_keys = b.keys() - a.keys() - local_ignore
        ab_keys = (a.keys() & b.keys()) - local_ignore
        # logging.info(f"common keys: {ab_keys}")
        prefix = f"{level* ' '}+- {key!r} = " if key else ""
        if a_exclusive_keys:
            msg_exclu_a.append(prefix + format_as_tree(sub(a, a_exclusive_keys), crt_indent=level, indent=4))
        if b_exclusive_keys:
            msg_exclu_b.append(prefix + format_as_tree(sub(b, b_exclusive_keys), crt_indent=level, indent=4))
        for k in ab_keys:
            _allclose_rec(
                f"{key}.{k}",
                a[k],
                b[k],
                msg_exclu_a,
                msg_exclu_b,
                msg_diff,
                level + 4,
                rtol,
                atol,
                equal_nan,
                ignore,
            )
    else:
        result = np.allclose(a, b, rtol, atol, equal_nan)
        if not result:
            msg_diff.append(f"+- {key!r} -> {a} != {b}")


class GeodeticComparator:
    """
    Helper class to compare sets of geodetic coordinates
    """

    def __init__(self, body_model: EarthBody):
        """
        Constructor with an EarthBody model
        """
        self.model = body_model

    def planar_error(self, first: np.ndarray, second: np.ndarray):
        """
        Compute planimetric error between two sets of geodetic coordinates
        The altitude used comes from the first set.

        :param first: First set of geodetic coordinates (using altitude from this one)
        :param second: Second set of geodetic coordinates
        :return: 2D distance (in m) between geodetic coordinates of "first" and "second"
        """
        output = list(
            map(
                lambda x, y: self.model.geodetic_distance(
                    float(x[0]), float(x[1]), float(y[0]), float(y[1]), float(x[2])
                )[0],
                first,
                second,
            )
        )
        return np.array(output)

    def height_error(self, first: np.ndarray, second: np.ndarray):
        """
        Compute altimetric error between two sets of geodetic coordinates

        :param first: First set of geodetic coordinates (using altitude from this one)
        :param second: Second set of geodetic coordinates
        :return: altitude difference between geodetic coordinates of "first" and "second"
        """
        return np.abs(first[..., 2] - second[..., 2])

    def footprint_comparison(self, first: np.ndarray, second: np.ndarray):
        """
        Compute:
            - A surface ratio between both olygon (1 => surfaces are identical)
            - A planar distance(max) at altitude 0 between each points of each polygons versus the other polygon
        :param first: First set of geodetic coordinates
        :param second: Second set of geodetic coordinates
        :return:
            - surface ratio geodetic coordinates of "first" and "second"
            - max distance(meters) at altitude 0 between each points of each polygons versus the other polygon
            - max distance(meters) at altitude 0 between each points of first versus second
            - max distance(meters) at altitude 0 between each points of second versus first
        """
        # Initialize Polygon object
        poly1 = Polygon(first[:, :2])
        poly2 = Polygon(second[:, :2])

        if not poly1.is_valid:
            poly1 = make_valid(poly1)  # type: ignore
        if not poly2.is_valid:
            poly2 = make_valid(poly2)  # type: ignore

        if poly1.geom_type == "MultiPolygon" and poly2.geom_type == "MultiPolygon":
            # Multipolygon case
            assert isinstance(poly1, MultiPolygon)  # help mypy find geoms
            assert isinstance(poly2, MultiPolygon)  # help mypy find geoms
            list_polygons1 = list(poly1.geoms)
            list_polygons2 = list(poly2.geoms)
            sum_relativeDiff = 0.0
            distancesmax1 = []
            distancesmax2 = []
            for polys1, polys2 in zip(list_polygons1, list_polygons2):
                # Computation of the surface ratio
                sum_relativeDiff += polys1.intersection(polys2).area / polys2.union(polys1).area

                # Computation of both distances
                distmax1 = max(
                    [
                        list(
                            self.planar_error(
                                np.array([list(p + (0,))]), np.array(nearest_points(polys2, Point(p))[0].coords)
                            )
                        )
                        for p in polys1.exterior.coords
                    ][0]
                )

                distmax2 = max(
                    [
                        list(
                            self.planar_error(
                                np.array([list(p + (0,))]), np.array(nearest_points(polys1, Point(p))[0].coords)
                            )
                        )
                        for p in polys2.exterior.coords
                    ][0]
                )

                distancesmax1.append(distmax1)
                distancesmax2.append(distmax2)

            return sum_relativeDiff, max(*distancesmax1, *distancesmax2), sum(distancesmax1), sum(distancesmax2)

        # Computation of the surface ratio
        relativeDiff = poly1.intersection(poly2).area / poly2.union(poly1).area

        # Computation of both distances
        distmax1 = max(
            [
                list(self.planar_error(np.array([list(p + (0,))]), np.array(nearest_points(poly2, Point(p))[0].coords)))
                for p in poly1.exterior.coords
            ][0]
        )

        distmax2 = max(
            [
                list(self.planar_error(np.array([list(p + (0,))]), np.array(nearest_points(poly1, Point(p))[0].coords)))
                for p in poly2.exterior.coords
            ][0]
        )

        return relativeDiff, max(distmax1, distmax2), distmax1, distmax2


def planar_captor_error(first: np.ndarray, second: np.ndarray):
    """
    Compute euclidian distance (error) between two sets of coordinates in row/col

    :param first: First set of captor coordinates (row/col)
    :param second: Second set of captor coordinates (row/col)
    :return: 2D distance (pixel) between geodetic coordinates of "first" and "second"
    """

    first_array = np.asarray(first)
    second_array = np.asarray(second)

    x_first = first_array[..., 0]
    y_first = first_array[..., 1]

    x_second = second_array[..., 0]
    y_second = second_array[..., 1]

    # Separate the difference, as optimisation on computation is
    # not handling weel having big and very small number in the same operation
    diff_x = x_first - x_second
    diff_y = y_first - y_second

    pow_x = diff_x**2
    pow_y = diff_y**2

    return np.square(pow_x + pow_y)


def pointing_error_azi_zen(direction1: np.ndarray, direction2: np.ndarray):
    """
    Pointing error in degrees between two pointing directions expressed as (azimuth, zenith)

    :param direction1: pointing directions of set 1
    :param direction2: pointing directions of set 2
    :return: angular distance between pointing directions (in deg)
    """
    dir1_array = np.asarray(direction1)
    dir2_array = np.asarray(direction2)

    azi1 = np.deg2rad(dir1_array[..., 0])
    zen1 = np.deg2rad(dir1_array[..., 1])
    x1 = np.cos(azi1) * np.sin(zen1)
    y1 = np.sin(azi1) * np.sin(zen1)
    z1 = np.cos(zen1)

    azi2 = np.deg2rad(dir2_array[..., 0])
    zen2 = np.deg2rad(dir2_array[..., 1])
    x2 = np.cos(azi2) * np.sin(zen2)
    y2 = np.sin(azi2) * np.sin(zen2)
    z2 = np.cos(zen2)

    return np.rad2deg(np.arccos(np.clip(x1 * x2 + y1 * y2 + z1 * z2, -1, 1)))
