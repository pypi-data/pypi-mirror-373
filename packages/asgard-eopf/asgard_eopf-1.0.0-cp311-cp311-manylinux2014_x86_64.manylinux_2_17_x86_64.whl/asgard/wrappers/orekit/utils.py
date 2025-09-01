#!/usr/bin/env python
# coding: utf8
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
Orekit python utils module
"""

import os.path as osp
import sys
from collections.abc import Iterable
from functools import reduce
from os import walk
from typing import List, Tuple, Union

import numpy as np
from java.io import File  # pylint: disable=import-error
from org.orekit.data import (  # pylint: disable=import-error
    DirectoryCrawler,
    LazyLoadedDataContext,
)
from org.orekit.time import (  # pylint: disable=import-error
    AbsoluteDate,
    TimeScale,
    TimeScalesFactory,
)
from org.orekit.utils import Constants  # pylint: disable=import-error

from asgard.core.compat import resources_files

from . import JCC_MODULE

# Extend Python types (list, dict, ...) with utility methods to convert them to Java types
# (ArrayList, HashMap, ...)
from .jcc_util import JccUtil  # pylint: disable=unused-import # noqa : F401

TIMESCALE_MAP = {
    "TAI": TimeScalesFactory.getTAI,
    "UTC": TimeScalesFactory.getUTC,
    "GPS": TimeScalesFactory.getGPS,
}


def split_files_and_directory(path) -> Tuple[str, List[str]]:
    """
    Split filenames from directory. If the path is a file, simply return dirname and basename.
    If path is a directory, list files in this directory.

    :param path: input path (either file or directory)
    :return: tuple with directory and filenames
    """

    real_path = osp.realpath(path)

    # The caller passed a directory
    if osp.isdir(real_path):
        out_dir = real_path

        # Find files in this folder
        _, _, out_filenames = next(walk(real_path))

    # The caller passed a file
    elif osp.isfile(real_path):
        out_dir = osp.dirname(real_path)
        out_filenames = [osp.basename(real_path)]

    else:
        raise ValueError(f"Input path is missing: {real_path!r}")

    return out_dir, out_filenames


def get_orekit_resources() -> str:
    """
    Returns the path to Orekit resources
    """
    return str(resources_files(JCC_MODULE))


def attach_thread():
    """
    Function to attach the current thread to the current running JVM (needed for remote or
    mutlithreaded executions). This step needs to be call before each use of wrapped java object or
    else it will generate an error like the 'RuntimeError: attachCurrentThread() must be called first'.
    """

    if not JCC_MODULE.getVMEnv().isCurrentThreadAttached():
        JCC_MODULE.getVMEnv().attachCurrentThread()


def get_data_context(
    iers_a_path: str | None = None,
    iers_b_path: str | None = None,
    iers_csv_path: str | None = None,
    iers_rdc_path: str | None = None,
    orekit_data: str | None = None,
) -> LazyLoadedDataContext:
    """
    Generate a data context with preset Orekit files and IERS files

    :param iers_a_path: Path to IERS A bulletin
    """
    attach_thread()
    custom_context = LazyLoadedDataContext()

    orekit_data_path = None

    if orekit_data is None:
        # default to resources of JCC_MODULE
        orekit_data_path = osp.join(get_orekit_resources(), "resources", "orekit-data")
    elif osp.exists(orekit_data):
        # existing folder
        orekit_data_path = orekit_data
    elif len(orekit_data.split(":")) == 2:
        # detect syntax "module:path"
        origin_module, data_path = orekit_data.split(":")
        orekit_data_path = osp.join(
            str(resources_files(sys.modules[origin_module])),
            data_path,
        )

    if orekit_data_path is not None:
        custom_context.getDataProvidersManager().addProvider(DirectoryCrawler(File(orekit_data_path)))

    all_dirs = set()
    regex_list = [None, None, None, None, None, None]

    # detect Rapid Data Column
    if iers_rdc_path:
        directory, filenames = split_files_and_directory(iers_rdc_path)
        all_dirs.add(directory)
        regex_list[0] = "|".join(filenames)

    # detect IERS bulletin B
    if iers_b_path:
        directory, filenames = split_files_and_directory(iers_b_path)
        all_dirs.add(directory)
        regex_list[3] = "|".join(filenames)

    # detect IERS bulletin A
    if iers_a_path:
        directory, filenames = split_files_and_directory(iers_a_path)
        all_dirs.add(directory)
        regex_list[4] = "|".join(filenames)

    # detect csv bulletin
    if iers_csv_path:
        directory, filenames = split_files_and_directory(iers_csv_path)
        all_dirs.add(directory)
        regex_list[5] = "|".join(filenames)

    # check if at least 1 additional file is added
    if reduce(lambda x, y: bool(x) or bool(y), regex_list):
        custom_context.getFrames().addDefaultEOP2000HistoryLoaders(*regex_list)

        for directory in all_dirs:
            custom_context.getDataProvidersManager().addProvider(DirectoryCrawler(File(directory)))

    # When using a single IERS A bulletin some gaps may arise : to allow the use of such bulletin,
    # we fix the EOP continuity threshold to one year instead of the normal gap ...
    custom_context.getFrames().setEOPContinuityThreshold(Constants.JULIAN_YEAR)

    return custom_context


def dates_to_json(
    j_time_scale: TimeScale,
    j_epoch: AbsoluteDate,
    dates: List[Union[AbsoluteDate, List]],
) -> dict:
    """
    Convert dates to JSON format.

    :param time_scale: time scale in which the dates and epoch are expressed.
    :param j_epoch: reference date from which to express dates as offset values in seconds.
    :param dates: n-dim list of AbsoluteDate values.
    :return: n-dim dict of dates in the JSON format
    """

    # Epoch to string
    epoch = j_epoch.toString(j_time_scale)

    # Date offsets in relation to epoch. Handle multi-dimension lists.
    def to_offsets(cur_dates):
        if len(cur_dates) == 0:  # empty list
            return []
        if isinstance(cur_dates[0], Iterable):  # list of lists
            return [to_offsets(sub_dates) for sub_dates in cur_dates]
        # 1D list
        return [date.durationFrom(j_epoch) for date in cur_dates]

    offsets = to_offsets(dates)

    return {
        "offsets": np.array(offsets, np.double),
        "unit": "s",  # AbsoluteDate::durationFrom returns seconds
        "epoch": epoch,
    }


def dates_from_json(d_time_scales: dict, time_scale: str | None = None) -> List[Union[AbsoluteDate, List]]:
    """
    Read dates from JSON format.
    :param d_time_scales: dict of datetimes, which may contain multiple time scales, in the JSON format.
    :param time_scale: time scale in which the dates and epoch are expressed
    :return: n-dim list of AbsoluteDate values.
    """

    # Use the requested time scale
    if time_scale is not None:
        d_times = d_time_scales["times"][time_scale]

    # By default, use the first time scale
    else:
        time_scale, d_times = next(iter(d_time_scales["times"].items()))

    # Only handle seconds
    assert d_times["unit"] == "s"

    # Call TimeScalesFactory.getXxx() to get the time scale from string
    j_time_scale = TIMESCALE_MAP[time_scale]()

    # Epoch from string and time scale
    j_epoch = AbsoluteDate(d_times["epoch"], j_time_scale)

    # Dates from offsets in relation to epoch. Handle multi-dimension lists.
    def from_offsets(cur_offsets):
        if len(cur_offsets) == 0:  # empty list
            return []
        if isinstance(cur_offsets[0], Iterable):  # list of lists
            return [from_offsets(sub_offsets) for sub_offsets in cur_offsets]
        # 1D list
        return [j_epoch.shiftedBy(float(offset)) for offset in cur_offsets]

    return from_offsets(d_times["offsets"])
