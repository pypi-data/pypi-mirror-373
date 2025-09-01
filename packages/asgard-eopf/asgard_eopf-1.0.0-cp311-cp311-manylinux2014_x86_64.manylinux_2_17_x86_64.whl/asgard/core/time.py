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
Module for time reference abstract class
"""

from abc import abstractmethod
from enum import Enum

from .model import AbstractModel

JD_TO_SECONDS = 86400.0  #: scale factor between julian days and seconds
JD_TO_MICROSECONDS = 86400.0e6  #: scale factor between julian days and microseconds

DEFAULT_EPOCH = "2000-01-01_00:00:00"  #: Default epoch assumed by most time related functions
DEFAULT_UNIT = "d"  #: Default time unit assumed on processing format times.


class TimeRef(Enum):
    """
    Enumeration of different time references
    """

    TAI = 0
    UTC = 1
    UT1 = 2
    GPS = 3
    OBT = 4  # On-board time, maybe not usefull


class AbstractTimeReference(AbstractModel):
    """
    Specify interface for  conversions between time references, time formats...
    """

    @abstractmethod
    def convert(
        self,
        time: float,
        ref_in: TimeRef,
        ref_out: TimeRef,
        unit: str = "s",
        epoch: str = "2000-01-01_00:00:00",
    ) -> float:
        """
        Convert an input time value to a different time reference

        :param float time: Input time value (processing time format)
        :param TimeRef ref_in: Input time reference
        :param TimeRef ref_out: Output time reference
        :param str unit: Base unit of the processing format: 'd' -> day, 's' -> seconds.
        :param str epoch: Reference epoch (ex: '2000-01-01_00:00:00')
        :return: converted time
        """

    @abstractmethod
    def convert_all(
        self,
        dataset,
        ref_in: TimeRef,
        ref_out: TimeRef,
        field_in: str = "time",
        field_out: str | None = None,
    ):
        """
        Convert an input time array to a different time reference

        :param dict dataset: Input dataset
        :param TimeRef ref_in: Input time reference
        :param TimeRef ref_out: Output time reference
        :param str field_in: input time fields, expect a TIME_ARRAY struct.
        :param str field_out: Output field name, if null the input field is modified in-place.
        :return: converted datetime
        """

    @abstractmethod
    def to_str(
        self,
        time: float,
        unit: str = "s",
        epoch: str = "2000-01-01_00:00:00",
        fmt: str = "ASCII",
        ref_in: TimeRef = TimeRef.TAI,
        ref_out: TimeRef | None = None,
    ) -> str:
        """
        Convert an input time in processing format into a string formatted time

        Since the processing format (epoch + offset) in UTC time scale cannot represent a time
        inside a leap second, this function allows to change the time scale before ASCII
        formatting. If you use an input TAI or GPS time inside a leap second, you can set ref_out
        to :const:`TimeRef.UTC` in order to have a proper UTC timestamp, like 2016-12-31_23:59:60.

        :param time:      Input time in processing format
        :type time:       float in day/second fraction since the epoch, in the input time reference
        :param str unit:  Base unit of the input processing time: 'd' -> day, 's' -> seconds.
        :param str epoch: Reference epoch of the input time
        :param str fmt: Output format (choices are: ASCII, ... TBD)
        :param TimeRef ref_in:  Input time reference into which ``time`` shall be interpreted
        :param TimeRef ref_out: Output time reference into which the resulting string is expected to be interpreted in.
                          The default ``None`` value will assume ``ref_out = ref_in``, and make ``to_str()`` behave as a
                          simple string convertion function. Changing this parameter permits to change the time scale,
                          and thus can be seen as an optimized ``convert() + to_str()`` call..
        :return: Formatted string
        """

    @abstractmethod
    def from_str(
        self,
        time: str,
        unit: str = "s",
        epoch: str = "2000-01-01_00:00:00",
        fmt: str = "ASCII",
    ) -> float:
        """
        Convert a string formatted time into processing format

        :param str time: Input time in string format
        :param str unit: Unit of the output processing format
        :param str epoch: Reference epoch of the output time -- in the same time scale/reference as ``time``
        :param str fmt: Input format (choices are: ASCII, ... TBD)
        :return: Time in processing format (from ``epoch``, in ``unit``), actually an apparent offset from epoch.
        :rtype: float
        """

    @abstractmethod
    def leap_seconds(
        self,
        start: float,
        end: float,
        unit: str = "s",
        epoch: str = "2000-01-01_00:00:00",
    ) -> list:
        """
        Get list of leap seconds between a start and end time

        :param float start: Start of time range, in processing format
        :param float end: End of time range, in processing format
        :param str unit: Unit of the input processing format
        :param str unit: Base unit of the processing format: 'd' -> day, 's' -> seconds.
        :return: List of leap seconds
        """
