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
Module for time model implemented using orekit
"""

import logging
import os.path as osp
from collections.abc import Generator
from tempfile import TemporaryDirectory
from typing import Optional, Union

import numpy as np

from asgard import ASGARD_VALIDATE_SCHEMAS
from asgard.core.math import flatten_array, restore_array
from asgard.core.schema import (
    ASCII_TIMESTAMP_SCHEMA,
    TEXT_FILE_CONTENT,
    TIME_ARRAY_SCHEMA_ND,
    TIMESCALE_ARRAY_SCHEMA,
    validate_or_throw,
)
from asgard.core.time import (
    DEFAULT_EPOCH,
    DEFAULT_UNIT,
    JD_TO_MICROSECONDS,
    JD_TO_SECONDS,
    AbstractTimeReference,
    TimeRef,
)
from asgard.wrappers.orekit.utils import get_data_context

# isort: off
from asgard.wrappers.orekit.utils import attach_thread  # pylint: disable=wrong-import-order

from org.orekit.time import (  # pylint: disable=import-error, wrong-import-order
    AbsoluteDate,
    DateTimeComponents,
    TimeComponents,
    TimeScale,
)
from org.orekit.utils import (  # pylint: disable=import-error, wrong-import-order
    IERSConventions,
)

# isort: on

#: Number of second in a day
SEC_PER_DAY = 86400.0
#:
MJD_TO_GPS_EPOCH = 7300.0


ASCII_TIME_MAP = {
    "STD": "{Y:04}-{m:02}-{d:02}_{H:02}:{M:02}:{S:02}",
    "STD_MICROSEC": "{Y:04}-{m:02}-{d:02}_{H:02}:{M:02}:{S:02}.{f:06}",
    "COMPACT": "{Y:04}{m:02}{d:02}_{H:02}{M:02}{S:02}",
    "COMPACT_MICROSEC": "{Y:04}{m:02}{d:02}_{H:02}{M:02}{S:02}{f:06}",
    "CCSDSA": "{Y:04}-{m:02}-{d:02}T{H:02}:{M:02}:{S:02}",
    "CCSDSA_MICROSEC": "{Y:04}-{m:02}-{d:02}T{H:02}:{M:02}:{S:02}.{f:06}",
    "CCSDSA_COMPACT": "{Y:04}{m:02}{d:02}T{H:02}{M:02}{S:02}",
    "CCSDSA_COMPACT_MICROSEC": "{Y:04}{m:02}{d:02}T{H:02}{M:02}{S:02}{f:06}",
}
"""
List of supported output time formats:

    - "STD"                    : ``YYYY-MM-DD_hh:mm:ss``
    - "STD_MICROSEC"           : ``YYYY-MM-DD_hh:mm:ss.ffffff``
    - "COMPAT"                 : ``YYYYMMDD_hhmmss``
    - "COMPAT_MICROSEC"        : ``YYYYMMDD_hhmmss.ffffff``
    - "CCSDSA"                 : ``YYYY-MM-DDThh:mm:ss``
    - "CCSDSA_MICROSEC"        : ``YYYY-MM-DDThh:mm:ss.ffffff``
    - "CCSDSA_COMPACT"         : ``YYYYMMDDThhmmss``
    - "CCSDSA_COMPACT_MICROSEC": ``YYYYMMDDThhmmssffffff``

:meta hide-value:
"""

logger = logging.getLogger("asgard.models.time")


def _extract_time_reference(dataset, time_fields):
    """
    Extracts the "time_ref" attribute from a ``TIMESCALE_ARRAY``.

    If not present, we take the first time reference key on the condition there is only one.

    If there are more, we look for GPS

    As a fallback, if no attribute is present, we take the first time reference key on the condition there is only one.

    :param dataset:    ``TIMESCALE_ARRAY`` from which the time reference will be extracted.
    :param time_fields: Key under which time field names are stored.
    """
    time_ref = dataset.get("time_ref", None)
    if not time_ref:
        possible_time_references = list(dataset[time_fields].keys())
        if len(possible_time_references) == 1:
            time_ref = possible_time_references[0]

    if not time_ref and "GPS" in possible_time_references:
        time_ref = "GPS"

    # logger.debug("Using time_ref: %s", time_ref)
    return time_ref


def _make_timestamp_compatible_with_orekit(timestamp: str) -> str:
    """
    Converts internal string format for timestamps into a format orekit can understand
    """
    # convert to ISO-8601
    start = 0
    if timestamp[3] == "=":
        # skip the optional 'RRR=' prefix
        start = 4
    epoch_iso = timestamp[start:].strip()
    if epoch_iso.count("_") == 1:
        epoch_iso = epoch_iso.replace("_", "T")
    if epoch_iso.count(" ") == 1:
        epoch_iso = epoch_iso.replace(" ", "T")
    return epoch_iso


def extract_date_time_components(epoch: Union[str, DateTimeComponents]) -> DateTimeComponents:
    """
    Converts a string epoch into an orekit :class:`org.orekit.time.DateTimeComponents`

    :param str epoch: String to convert, matching the :const:`asgard.core.schema.ASCII_TIMESTAMP_SCHEMA` format.
    """

    if isinstance(epoch, DateTimeComponents):
        # already a DateTimeComponents, nothing to do
        return epoch

    # parse date and time
    return DateTimeComponents.parseDateTime(_make_timestamp_compatible_with_orekit(epoch))


def generate_one_date(offset: float, timescale: TimeScale, epoch: DateTimeComponents | str, unit: str) -> AbsoluteDate:
    """
    Generate one :class:`org.orekit.time.AbsoluteDate` from a single offset.

    :param float offset: Offset from epoch to convert into a sequence of :class:`org.orekit.time.AbsoluteDate`.
    :param timescale:    Time scale to use to convert generated :class:`org.orekit.time.DateTimeComponents`
                         + offset into a :class:`org.orekit.time.AbsoluteDate`. Can't be ``None``.
    :type timescale:     org.orekit.time.TimeScale
    :param epoch:        Precomputed epoch. Can't be ``None``.
    :type epoch:         org.orekit.time.DateTimeComponents | str
    :rtype:              :class:`org.orekit.time.AbsoluteDate`

    .. important::

        The time offsets used by EOCFI are offsets independant of any time scale. This means they cannot be
        applied to a :class:`org.orekit.time.AbsoluteDate` with :meth:`org.orekit.time.AbsoluteDate.shiftedBy`
        method. Instead they must be applied to a :class:`org.orekit.time.DateTimeComponents`, which produces a new
        :class:`org.orekit.time.DateTimeComponents`, and then converted into a :class:`org.orekit.time.AbsoluteDate` by
        taking into account the relevant *time-scale*.

    .. seealso::

        :func:`asgard.models.time.generate_dates_from_offset_series`, :meth:`asgard.models.time.TimeReference.to_dates`
    """
    if isinstance(epoch, str):
        epoch = extract_date_time_components(epoch)
    convert_to_sec = 1 if unit == "s" else JD_TO_SECONDS
    dtc = DateTimeComponents(epoch, float(offset * convert_to_sec))
    date = AbsoluteDate(dtc, timescale)
    return date


def generate_dates_from_offset_series(
    offsets: np.ndarray, timescale: TimeScale, epoch: DateTimeComponents, unit: str
) -> Generator[AbsoluteDate, None, None]:
    """
    Low level :class:`org.orekit.time.AbsoluteDate` sequence generator from an offset array.

    :param offsets:   Time array offsets from ``epoch`` to convert into a sequence of
                      :class:`org.orekit.time.AbsoluteDate`.
    :type offsets:    np.ndarray[float]
    :param timescale: Time scale to use to convert generated :class:`org.orekit.time.DateTimeComponents`
                      + offset into a :class:`org.orekit.time.AbsoluteDate`. Can't be ``None``.
    :type timescale:  org.orekit.time.TimeScale
    :param epoch:     Precomputed epoch. Can't be ``None``.
    :type epoch:      org.orekit.time.DateTimeComponents
    :rtype:           Generator[AbsoluteDate, None, None]

    .. important::

        The time offsets used by EOCFI are offsets independant of any time scale. This means they cannot be
        applied to a :class:`org.orekit.time.AbsoluteDate` with :meth:`org.orekit.time.AbsoluteDate.shiftedBy`
        method. Instead they must be applied to a :class:`org.orekit.time.DateTimeComponents`, which produces a new
        :class:`org.orekit.time.DateTimeComponents`, and then converted into a :class:`org.orekit.time.AbsoluteDate` by
        taking into account the relevant *time-scale*.

    .. seealso::

        :func:`asgard.models.time.generate_one_date`, :meth:`asgard.models.time.TimeReference.to_dates`
    """
    validate_or_throw(offsets, {"type": "array", "shape": [":"]})
    # JCC breaks inheritance between TimeScale and TAIScale...
    # assert isinstance(timescale, TimeScale), f"Wrong type for timescale: {type(timescale)}"
    # assert isinstance(epoch, DateTimeComponents), f"Wrong type for epoch: {type(epoch)}"

    # Time conversion from days to seconds
    convert_to_sec = 1 if unit == "s" else JD_TO_SECONDS
    prev_time = None
    date = None
    for time_offset in offsets:
        if time_offset != prev_time:
            dtc = DateTimeComponents(epoch, float(time_offset * convert_to_sec))
            date = AbsoluteDate(dtc, timescale)
            prev_time = time_offset
        # logger.debug("Gen date = %s + %s * %s -> %s", dtc_start, time_offset, convert_to_sec, date)
        yield date


def compute_offset(
    date: str | DateTimeComponents,
    epoch: str | DateTimeComponents = DEFAULT_EPOCH,
    unit: str = DEFAULT_UNIT,
) -> float:
    """
    Return the *apparent offset* between the ``date`` and the ``epoch``.

    Do not confuse with physical durations between two dates. For instance, in between "2015-06-30_23:59:59" and
    "2015-07-01_00:00:00", while the apparent offset is of 1s, there are actually 2 physical seconds when the dates are
    considered in UTC. Indeed there is a leap second in between, which makes  "UTC=2015-06-30_23:59:60" valid.
    """
    epoch = extract_date_time_components(epoch)

    crt = extract_date_time_components(date)
    convert_to_sec = 1 if unit == "s" else JD_TO_SECONDS
    return crt.offsetFrom(epoch) / convert_to_sec


class TimeReference(AbstractTimeReference):
    """
    TimeReference based on Orekit.

    .. important::

        ``TimeReference`` construction depends on the current :class:`org.orekit.frames.EOPHistory`. This means that
        ``TimeReference`` objects need to be dumped and created anew every time the IERS directory is updated.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        # call superclass constructor
        super().__init__(*args, **kwargs)

        # Shall we receive the EOPHistory as a construction parameter of the TimeReference object?

        # prepare temporary folder
        self._tmp_dir = None
        if len(kwargs):
            self._tmp_dir = TemporaryDirectory(prefix="asgard-")  # pylint: disable=consider-using-with

        context_config = {}
        has_iers = False
        if "iers_bulletin_a" in kwargs:
            has_iers = True
            iers_a_path = osp.join(self._tmp_dir.name, "iers_bulletin_a.txt")
            with open(iers_a_path, "w", encoding="utf-8") as out_fd:
                out_fd.writelines(kwargs["iers_bulletin_a"])
            context_config["iers_a_path"] = iers_a_path
        if "iers_bulletin_b" in kwargs:
            has_iers = True
            iers_b_path = osp.join(self._tmp_dir.name, "iers_bulletin_b.txt")
            with open(iers_b_path, "w", encoding="utf-8") as out_fd:
                out_fd.writelines(kwargs["iers_bulletin_b"])
            context_config["iers_b_path"] = iers_b_path
        if "iers_rapid_data_col" in kwargs:
            has_iers = True
            iers_rdc_path = osp.join(self._tmp_dir.name, "iers_rapid_data_col.txt")
            with open(iers_rdc_path, "w", encoding="utf-8") as out_fd:
                out_fd.writelines(kwargs["iers_rapid_data_col"])
            context_config["iers_rdc_path"] = iers_rdc_path

        self.has_lut = "lut" in kwargs and not has_iers and "UT1" in kwargs.get("lut", {})
        if self.has_lut:
            for scale in self.config["lut"]:
                self.config["lut"][scale].setdefault("epoch", DEFAULT_EPOCH)
                self.config["lut"][scale].setdefault("unit", DEFAULT_UNIT)
            epoch = self.config["lut"]["UT1"]["epoch"]
            unit = self.config["lut"]["UT1"]["unit"]
            for scale in self.config["lut"]:
                # check we use the same unit and epoch for the different times scales
                if self.config["lut"][scale]["epoch"] != epoch:
                    raise RuntimeError(
                        f'Get a different {scale} epoch ({self.config["lut"][scale]["epoch"]}) from UT1 epoch ({epoch})'
                    )
                if self.config["lut"][scale]["unit"] != unit:
                    raise RuntimeError(
                        f'Get a different {scale} unit ({self.config["lut"][scale]["unit"]}) from UT1 unit ({unit})'
                    )

        if "orekit_data" in kwargs:
            context_config["orekit_data"] = kwargs["orekit_data"]

        #: Store dedicated Orekit data context
        self.context = get_data_context(**context_config)

        #: Cached :class:`TimeRef` -> :class`TimeScale` map
        self._time_ref_map = {
            TimeRef.TAI: self.context.getTimeScales().getTAI(),
            TimeRef.UTC: self.context.getTimeScales().getUTC(),
            TimeRef.UT1: self.context.getTimeScales().getUT1(
                self.context.getFrames().getEOPHistory(IERSConventions.IERS_2010, True)
            ),
            TimeRef.GPS: self.context.getTimeScales().getGPS(),
        }

    @classmethod
    def init_schema(cls) -> dict:
        """
        Description of the schema of the construction parameters, as a JSON schema

        A simplified definition is:

        .. code-block:: python

            {
                "iers_bulletin_a":     TEXT_FILE_CONTENT,
                "iers_bulletin_b":     TEXT_FILE_CONTENT,
                "iers_rapid_data_col": TEXT_FILE_CONTENT,
                "orekit_data": {"type": "string"},
            }

        :download:`JSON schema <doc/scripts/init_schema/schemas/TimeReference.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "iers_bulletin_a": TEXT_FILE_CONTENT,
                "iers_bulletin_b": TEXT_FILE_CONTENT,
                "iers_rapid_data_col": TEXT_FILE_CONTENT,
                "lut": TIMESCALE_ARRAY_SCHEMA,
                "orekit_data": {"type": "string"},
            },
            "additionalProperties": False,
        }

    def timeref_to_timescale(self, time_ref: TimeRef) -> TimeScale:
        """
        Utility function to convert an ASGARD :class:`asgard.core.TimeRef` into an Orekit :class:`TimeScale`.

        :param TimeRef time_ref: input time reference to convert
        :return: equivalent Orekit :class:`TimeScale`
        """
        attach_thread()
        output = self._time_ref_map.get(time_ref)
        if output is None:
            raise RuntimeError(f"Input TimeRef not supported: {time_ref}")
        return output

    def to_dates(
        self,
        times,
        time_ref: Optional[TimeRef] = None,
        epoch_dtc: Optional[DateTimeComponents] = None,
    ) -> Generator[AbsoluteDate, None, None]:
        """
        :class:`org.orekit.time.AbsoluteDate` sequence generator from a Time array.

        :param times:     Time array to convert into a sequence of :class:`org.orekit.time.AbsoluteDate`.
        :param time_ref:  Time reference/scale to use to convert generated :class:`org.orekit.time.DateTimeComponents`
                          + offset into a :class:`org.orekit.time.AbsoluteDate`.
        :type time_ref:   Optional[asgard.core.time.TimeRef]
        :param epoch_dtc: Precomputed epoch.
        :type epoch_dtc:  Optional[org.orekit.time.DateTimeComponents]
        :rtype:           Generator[AbsoluteDate, None, None]

        If not provived ``epoch_dtc`` and ``time_ref`` will be generated on the fly:

        * ``time_ref`` from ``times["time_ref"]``
        * ``epoch_dtc`` from ``extract_date_time_components(times["epoch"], time_ref)``.

        .. important::

            The time offsets used by EOCFI are offsets independant of any time scale. This means they cannot be
            applied to a :class:`org.orekit.time.AbsoluteDate` with :meth:`org.orekit.time.AbsoluteDate.shiftedBy`
            method. Instead they must be applied to a :class:`org.orekit.time.DateTimeComponents`, which produces a new
            :class:`org.orekit.time.DateTimeComponents`, and then converted into a :class:`org.orekit.time.AbsoluteDate`
            by taking into account the relevant *time-scale*.

        .. seealso::

            :func:`asgard.models.time.generate_dates_from_offset_series`, :func:`asgard.models.time.generate_one_date`
        """
        attach_thread()
        assert not time_ref or isinstance(time_ref, TimeRef), "Invalid type for time_ref: {type(time_ref)}"
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(times, TIME_ARRAY_SCHEMA_ND)

        dtc_start = epoch_dtc or extract_date_time_components(times.get("epoch", DEFAULT_EPOCH))
        time_ref = time_ref or TimeRef[times.get("ref", "GPS")]
        timescale = self.timeref_to_timescale(time_ref)
        flat_offsets = flatten_array(times["offsets"])
        unit = times.get("unit", DEFAULT_UNIT)

        return generate_dates_from_offset_series(flat_offsets, timescale, dtc_start, unit)

    def convert(
        self,
        time: float,
        ref_in: TimeRef,
        ref_out: TimeRef,
        unit: str = DEFAULT_UNIT,
        epoch: str = DEFAULT_EPOCH,
    ) -> float:
        """
        Convert an input time value to a different time reference

        :param float time:      Input time value (processing time format)
        :param TimeRef ref_in:  Input time reference
        :param TimeRef ref_out: Output time reference
        :param str unit:        Base unit of the processing format: 'd' -> day, 's' -> seconds.
        :param str epoch:       Reference epoch (ex: '2000-01-01_00:00:00')
        :return: converted time
        """
        dataset = {
            "time": {
                "offsets": np.array([time], dtype="float64"),
                "unit": unit,
                "epoch": epoch,
            }
        }
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(dataset["time"], TIME_ARRAY_SCHEMA_ND)

        self.convert_all(dataset, ref_in, ref_out, field_in="time", field_out="output")
        return dataset["output"]["offsets"][0]

    def convert_all(
        self,
        dataset,
        ref_in: TimeRef,
        ref_out: TimeRef,
        field_in: str = "time",
        field_out: Optional[str] = None,
    ) -> None:
        """
        Convert an input time array to a different time reference

        :param dict dataset:            Input dataset
        :param TimeRef ref_in:          Input time reference
        :param TimeRef ref_out:         Output time reference
        :param str field_in:            Input time fields, expect a :const:`asgard.core.schema.TIME_ARRAY` struct.
        :param Optional[str] field_out: Output field name, if ``None`` the input field is modified in-place.
        :return: converted datetime
        """
        attach_thread()
        assert dataset.get(field_in) is not None  # check dataset is here
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(dataset[field_in], TIME_ARRAY_SCHEMA_ND)

        # Time conversion from days to seconds
        unit = dataset[field_in].get("unit", "d")

        # Convert epoch in readable format for orekit
        epoch = dataset[field_in].get("epoch", "2000-01-01_00:00:00")
        dtc_epoch = extract_date_time_components(epoch)

        # Calculate time offset between both time reference
        flat_array = flatten_array(dataset[field_in]["offsets"])
        timescale_in = self.timeref_to_timescale(ref_in)
        timescale_out = self.timeref_to_timescale(ref_out)
        conv_array = np.zeros(flat_array.shape, dtype="float64")

        if self.has_lut and TimeRef.UT1 in [ref_in, ref_out]:
            # Only use lut for UT1 because Orekit probably have a longer history of leap seconds
            # Convert input times to lut epoch and unit
            time_in_lut_conv = self.change_epoch_and_unit(
                dataset[field_in],
                epoch=self.config["lut"]["UT1"]["epoch"],
                unit=self.config["lut"]["UT1"]["unit"],
            )
            # Compute shift between UT1 and output ref
            lut_times = self.config["lut"][ref_in.name]["offsets"]
            lut_shift = self.config["lut"][ref_out.name]["offsets"] - self.config["lut"][ref_in.name]["offsets"]
            time_in_lut_conv["offsets"] = time_in_lut_conv["offsets"] + np.interp(
                time_in_lut_conv["offsets"], lut_times, lut_shift
            )

            # Convert back to original epoch and unit
            time_in_input_conv = self.change_epoch_and_unit(
                time_in_lut_conv,
                epoch=epoch,
                unit=unit,
            )
            out_array = time_in_input_conv["offsets"]
        else:
            for idx, date in enumerate(
                generate_dates_from_offset_series(
                    flat_array,
                    timescale_in,
                    dtc_epoch,
                    unit,
                )
            ):
                dtc_current = date.getComponents(timescale_out)
                conv_array[idx] = dtc_current.offsetFrom(dtc_epoch)

            # handle conversion to days unit
            if unit == "d":
                conv_array /= JD_TO_SECONDS
            out_array = conv_array.reshape(dataset[field_in]["offsets"].shape)

        # Handle in-place conversion
        if not field_out:
            field_out = field_in
        # assign output array
        dataset[field_out] = {
            "offsets": out_array,
            "unit": unit,
            "epoch": epoch,
            "ref": ref_out.name,
        }

    def to_str(
        self,
        time: float,
        unit: str = "d",
        epoch: str | DateTimeComponents = "2000-01-01_00:00:00",
        fmt: str = "STD",
        ref_in: TimeRef = TimeRef.TAI,
        ref_out: Optional[TimeRef] = None,
    ) -> str:
        """
        Convert an input time in processing format into a string formatted time

        Since the processing format (epoch + offset) in UTC time scale cannot represent a time
        inside a leap second, this function allows to change the time scale before ASCII
        formatting. If you use an input TAI or GPS time inside a leap second, you can set ref_out
        to :const:`asgard.core.time.TimeRef.UTC` in order to have a proper UTC timestamp, like 2016-12-31_23:59:60.

        :param time:           Input time in processing format
        :type time:            float in day/second fraction since the epoch, in the input time reference
        :param str unit:       Base unit of the input processing time: 'd' -> day, 's' -> seconds.
        :param epoch:          Reference epoch of input processing time
        :type epoch:           str | preprocessed org.orekit.time.DateTimeComponents
        :param str fmt:        Output format (any of the keys of :const:`asgard.models.time.ASCII_TIME_MAP` dictionary)
        :param TimeRef ref_in: Input time reference into which ``time`` shall be interpreted
        :param ref_out:        Output time reference into which the resulting string is expected to be interpreted in.
                               The default ``None`` value will assume ``ref_out = ref_in``, and make ``to_str()`` behave
                               as a simple string convertion function.
                               Changing this parameter permits to change the time scale, and thus can be seen as an
                               optimized ``convert() + to_str()`` call..
        :type Optional[TimeRef] ref_out:
        :return:               Formatted string
        :rtype:                str
        """
        attach_thread()
        # Analyse parameters
        if isinstance(epoch, str):
            dtc_epoch = extract_date_time_components(epoch)
        else:
            dtc_epoch = epoch
        convert_to_sec = 1 if unit == "s" else JD_TO_SECONDS
        ref_out = ref_out or ref_in
        ts_in = self.timeref_to_timescale(ref_in)
        ts_out = self.timeref_to_timescale(ref_out)
        fmt_out = ASCII_TIME_MAP[fmt]
        if "{f:06}" in fmt_out:  # Depending on output format...
            precision = 6  # -> round to microsecond
        else:
            precision = 0  # -> round to second

        # Convert to DateTimeComponents
        if ref_in == ref_out:
            # No conversion needed
            dtc_in = DateTimeComponents(dtc_epoch, float(time * convert_to_sec))
            date = AbsoluteDate(dtc_in, ts_in)
            # At this point we still need to round the date accordinging to the fractional seconds
            # -> dtc_in is not enough
        else:
            # Do the actual convertion
            date = generate_one_date(time, ts_in, epoch, unit)
            dtc_in = date.getComponents(ts_out)
            # logger.debug("dtc_in=%s", dtc_in)

        # While offsets expressed in UTC time scale cannot permit to express leap seconds
        # (because they are "apparent offsets" and not "physical offsets"), it is still
        # possible to have an offset in TAI/... time scale that corresponds to a date with a
        # leap second once expressed in UTC. Hence the following code that takes care of that.
        #
        # compute minute duration (warning, only UTC can call minuteDuration(), inheritance
        # is kinda broken with JCC)
        minute_duration = ts_out.minuteDuration(date) if ref_out == TimeRef.UTC else 60
        # round to given precision
        tcmp_rounded = TimeComponents(
            dtc_in.getTime().getHour(),
            dtc_in.getTime().getMinute(),
            round(dtc_in.getTime().getSecond(), precision),
        )
        dtc_rounded = DateTimeComponents(
            dtc_in.getDate(),
            tcmp_rounded,
        ).roundIfNeeded(minute_duration, precision)
        # logger.debug(
        #     "to_str(%s=%s => %s) -> DTCin=%s -> DTCout=%s",
        #     ref_in.name, time, ref_out.name, dtc_in, dtc_rounded,
        # )

        # Format string template
        dtc_date = dtc_rounded.getDate()
        dtc_time = dtc_rounded.getTime()
        dtc_sec = int(dtc_time.getSecond())
        mapping = {
            "Y": dtc_date.getYear(),
            "m": dtc_date.getMonth(),
            "d": dtc_date.getDay(),
            "H": dtc_time.getHour(),
            "M": dtc_time.getMinute(),
            "S": dtc_sec,
            "f": int(1000000 * dtc_time.getSecond()) - 1000000 * dtc_sec,  # <- faster, exact enough
            # "f": int(1000000 * round(dtc_time.getSecond() % 1, precision)),
        }

        return fmt_out.format(**mapping)

    def from_str(
        self,
        time: str,
        unit: str = "d",
        epoch: str = "2000-01-01_00:00:00",
        fmt: str = "STD",
    ) -> float:
        """
        Convert a string formatted time into processing format

        :param str time:  Input time in string format
        :param str unit:  Unit of the output processing format
        :param str epoch: Reference epoch of the output time -- in the same time scale/reference as ``time``
        :param str fmt:   Input format (ignored)
        :return: Time in processing format (from ``epoch``, in ``unit``), actually an apparent offset from epoch.
        :rtype: float

        :raises jsonschema.exceptions.ValidationError: if ``time`` doesn't match
                                                       :const:`asgard.core.schema.ASCII_TIMESTAMP_SCHEMA`
        """
        attach_thread()
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(epoch, ASCII_TIMESTAMP_SCHEMA)

        # Import as datetime object
        dtc_time = extract_date_time_components(time)

        # Convert epoch to DateTimeComponents
        dtc_epoch = extract_date_time_components(epoch)

        # Get orekit time offset in seconds
        time_value = dtc_time.offsetFrom(dtc_epoch)
        # Manage time output in seconds or days
        time_value = time_value / JD_TO_SECONDS if unit == "d" else time_value

        return time_value

    def str_to_absolute_date(self, timestamp: str, default_timescale: TimeScale = None) -> AbsoluteDate:
        """
        Generates a :class:`org.orekit.time.AbsoluteDate` from a string in the format
        :py:CONST:`asgard.core.schema.ASCII_TIMESTAMP_SCHEMA`.

        :param str timestamp: time to convert
        :param TimeScale default_timescale:  Time-scale of timestamp if not self contained.

        :retrun AbsoluteDate date
        """
        attach_thread()
        if timestamp[3] == "=":
            time_ref = timestamp[:3]
            time_scale = self.timeref_to_timescale(TimeRef[time_ref])
        else:
            if default_timescale is None:
                raise ValueError("time scale must be set as input")
            time_scale = default_timescale
        timestamp = _make_timestamp_compatible_with_orekit(timestamp)
        date = AbsoluteDate(timestamp, time_scale)
        return date

    def from_date(
        self,
        date: AbsoluteDate,
        ref: TimeRef | TimeScale = TimeRef.GPS,
        unit: str = DEFAULT_UNIT,
        epoch: str = DEFAULT_EPOCH,
    ) -> float:
        """
        Returns the offset since epoch on an :class:`org.orekit.time.AbsoluteDate`.

        :param AbsoluteDate date:          Exact time point to extract offset from
        :param TimeRef|TimeScale ref:      Time-scale into which the offset from the epoch shall be expressed.
        :param str unit:                   "d"/"s"
        :param str epoch:                  Epoch from which the offset shal be computed.
        """
        attach_thread()
        # convert to DateTimeComponents in given time scale
        time_scale = self.timeref_to_timescale(ref) if isinstance(ref, TimeRef) else ref
        dtc_time = date.getComponents(time_scale)

        # Convert epoch to DateTimeComponents
        dtc_epoch = extract_date_time_components(epoch)
        delta_sec = dtc_time.offsetFrom(dtc_epoch)
        convert_to_sec = 1 if unit == "s" else JD_TO_SECONDS
        return delta_sec / convert_to_sec

    def leap_seconds(
        self,
        start: float,
        end: float,
        unit: str = "d",
        epoch: str = "2000-01-01_00:00:00",
    ) -> list:
        """
        Get list of leap seconds between a start and end time

        :param float start: Start of time range, in processing format
        :param float end:   End of time range, in processing format
        :param str unit:    Base unit of the processing format: 'd' -> day, 's' -> seconds.
        :param str epoch:   Reference epoch (follows :const:`asgard.core.schema.ASCII_TIMESTAMP_SCHEMA`)
        :return: List of leap seconds
        """
        attach_thread()
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(epoch, ASCII_TIMESTAMP_SCHEMA)
        utc = self.timeref_to_timescale(TimeRef["UTC"])

        start_date, end_date = generate_dates_from_offset_series(
            [start, end], utc, extract_date_time_components(epoch), unit
        )

        # Load offset data --> leap seconds
        utc_offsets = utc.getUTCTAIOffsets()
        # logger.debug("All leap_seconds: %s", [offset.getDate() for offset in utc_offsets])

        # λ to convert ISO dates into EOCFI legacy date strings...
        def iso_to_legacy(date) -> str:
            return date.toString().split(".")[0].replace("T", "_")

        # Keep leap seconds in time range [start, end]
        output = []
        for offset in utc_offsets:
            date_offset = offset.getDate()
            # Expect the utc_offsets to be chronologically sorted
            if date_offset.isBefore(start_date):
                continue
            if date_offset.isAfter(end_date):
                break
            date = iso_to_legacy(date_offset)
            validity_offset = offset.getValidityStart()
            validity_start = iso_to_legacy(validity_offset)
            output.append((int(offset.getLeap().getSeconds()), date, validity_start))
        logger.debug("leap_seconds found in [%s, %s] -> %s", start_date, end_date, output)
        return output

    @staticmethod
    def from_cuc(
        time: np.ndarray,
        unit: str = "d",
        epoch: str = "2000-01-01_00:00:00",
        fine_bits: int = 24,
    ) -> np.ndarray:
        """
        Convert input GPS time in CUC format to processing format

        :param np.ndarray time: Time array in CUC format (expect two integer components for coarse/fine)
        :param str unit:        Base unit of the processing format: 'd' -> day, 's' -> seconds.
        :param str epoch:       Reference epoch (follows :const:`asgard.core.schema.ASCII_TIMESTAMP_SCHEMA`)
        :param int fine_bits:   Number of bits used to encode the fine component
        :return: Times array in processing format
        """
        assert time.dtype == "int64"
        flat_times = flatten_array(time, last_dim=2)

        assert flat_times.shape[1] == 2

        # change to target epoch
        dtc_epoch = extract_date_time_components(epoch)
        gps_epoch = DateTimeComponents(1980, 1, 6, 0, 0, 0.0)
        epoch_shift = dtc_epoch.offsetFrom(gps_epoch)

        # compute time in seconds
        out_time = (flat_times[:, 0] - epoch_shift) + flat_times[:, 1] * (2**-fine_bits)

        # convert to MJD if needed
        if unit == "d":
            out_time /= SEC_PER_DAY

        return restore_array(out_time, time.shape[:-1])

    @staticmethod
    def from_transport(time: np.ndarray) -> np.ndarray:
        """
        Convert input time in transport format (days/seconds/microsec) to processing time
        """
        return time[..., 0] + time[..., 1] / JD_TO_SECONDS + time[..., 2] / JD_TO_MICROSECONDS

    def any_time_as_date(
        self,
        date: AbsoluteDate | str | float,
        time_ref: TimeRef | TimeScale | None = None,
        epoch: str = DEFAULT_EPOCH,
        unit: str = DEFAULT_UNIT,
    ) -> AbsoluteDate:
        """
        Helper method to convert any set of parameters into a :class:`org.orekit.time.AbsoluteDate`.

        This will factorize all the required processing to transform a string, or a date in processing time format
        (float) into an ``AbsoluteDate``.

        :param date:     Time to convert.
        :type date:      AbsoluteDate|str|float
        :param time_ref: Time scale to interpret ``date`` when passed in processing format (``float``)
                         -- ignored otherwise.
        :type time_ref:  TimeRef|TimeScale
        :param str unit: Unit ("d"/"s") to interpret ``date`` when passed in processing format (``float``)
                         -- ignored otherwise.
        :return: the date as an ``AbsoluteDate``
        """
        attach_thread()
        if isinstance(date, AbsoluteDate):
            return date

        assert time_ref is not None, "Need a time reference/scale to convert a date"
        time_scale: TimeScale = self.timeref_to_timescale(time_ref) if isinstance(time_ref, TimeRef) else time_ref
        if isinstance(date, str):  # date in string
            return self.str_to_absolute_date(date, time_scale)

        assert isinstance(
            date, float
        ), f"At this point the parameter should be in processing format (float); got {date}: {type(date)}"
        return generate_one_date(date, time_scale, epoch, unit)

    def to_eocfi(self, offsets: np.ndarray, unit: str, epoch: str) -> np.ndarray:
        """
        Convert times to EOCFI convention (MJD, epoch 2000-01-01T00:00:00)

        :param np.ndarray offsets: Input time offsets
        :param str unit: Input time unit ('d'/'s')
        :param str epoch: Input time epoch (ascii timestamp)
        :return: Array of times in EOCFI processing format
        """
        epoch_mjd = self.from_str(epoch, unit="d", epoch="2000-01-01T00:00:00")
        if unit == "s":
            output = offsets / JD_TO_SECONDS + epoch_mjd
        else:
            output = offsets + epoch_mjd
        return output

    def change_epoch_and_unit(self, time_array, epoch: str | None = None, unit: str | None = None) -> dict:
        """
        Convert a time array structure to a given epoch and unit (same time scale)

        :param time_array: Input time array structure (see TIME_ARRAY_SCHEMA)
        :param epoch: Target epoch (if None, the input epoch is used)
        :param unit: Target unit, "s"/"d" (if None, the input unit is used)
        :return: output time array with translated offsets
        """

        # detect source settings
        src_unit = time_array.get("unit", "d")
        src_epoch = time_array.get("epoch", "2000-01-01T00:00:00")

        # detect target settings
        target_unit = unit if unit else src_unit
        target_epoch = epoch if epoch else src_epoch

        # handle conversion to target epoch, unit
        offsets = time_array["offsets"]
        if src_unit != target_unit:
            unit_scale = JD_TO_SECONDS if src_unit == "d" else 1.0 / JD_TO_SECONDS
            offsets = offsets * unit_scale
        if src_epoch != target_epoch:
            epoch_shift = self.from_str(src_epoch, unit=target_unit, epoch=target_epoch)
            offsets = offsets + epoch_shift

        output = {
            "offsets": offsets,
            "epoch": target_epoch,
            "unit": target_unit,
        }
        if "ref" in time_array:
            output["ref"] = time_array["ref"]

        return output

    def epoch_to_date(self, time_array: dict, offset_utc_leaps: bool = True) -> AbsoluteDate:
        """
        Convert the reference epoch of a time array to AbsoluteDate

        :param time_array: Input time array structure (see TIME_ARRAY_SCHEMA)
        :param offset_utc_leaps: For UTC time scale, we can shift the default epoch by the number
                                 of leap seconds between epoch and the start of time offsets. It
                                 allows to generate the expected date by shifting the output epoch
                                 (`epoch.shiftedBy(time_array["offsets"][0])`).
        :return: AbsoluteDate object
        """
        epoch_str = time_array.get("epoch", "2000-01-01T00:00:00")
        time_ref = TimeRef[time_array.get("ref", "GPS")]

        epoch = self.str_to_absolute_date(epoch_str, self.timeref_to_timescale(time_ref))
        if offset_utc_leaps and time_ref == TimeRef.UTC:
            leaps = self.leap_seconds(
                0.0,
                time_array["offsets"][0],
                unit=time_array.get("unit", "d"),
                epoch=epoch_str,
            )
            nb_leaps = np.sum([leap[0] for leap in leaps])
            epoch = epoch.shiftedBy(float(nb_leaps))
        return epoch

    def offsets_to_seconds(self, time_array: dict) -> np.ndarray:
        """
        Convert the offsets to seconds

        :param time_array: Input time array structure (see TIME_ARRAY_SCHEMA)
        :return: Offsets in seconds
        """
        unit = time_array.get("unit", "d")
        return time_array["offsets"] if unit == "s" else time_array["offsets"] * JD_TO_SECONDS
