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
Unit tests for models implemented with orekit
"""

import logging  # pylint: disable=unused-import  # noqa : F401
import os
import os.path as osp

import numpy as np
import pytest  # pylint: disable=import-error
from drivers.sentinel_3_legacy import S3LegacyDriver
from helpers.serde import repickle

from asgard.core.time import JD_TO_SECONDS, TimeRef  # pylint: disable=import-error
from asgard.models.time import (  # pylint: disable=import-error
    TimeReference,
    compute_offset,
)

# isort: off
import asgard.wrappers.orekit  # pylint: disable=unused-import, wrong-import-order  # noqa : F401

from org.orekit.time import (  # pylint: disable=import-error, wrong-import-order
    AbsoluteDate,
)

# isort: on

TEST_DIR = osp.dirname(__file__)

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")


@pytest.fixture(name="trf", scope="module")  # pylint: disable=invalid-name
def time_reference():
    """
    Fixture to produce an TimeReference
    """
    return TimeReference()


def test_time_reference_convert(trf):  # pylint: disable=invalid-name
    """
    Unit test for TimeReference.convert
    """

    tai_array = 8360.890787037037 * np.ones((2, 3), dtype="float64")
    utc_array = 8360.890358796296 * np.ones((2, 3), dtype="float64")
    ut1_array = 8360.890358796296 * np.ones((2, 3), dtype="float64")
    gps_array = 8360.890567129629 * np.ones((2, 3), dtype="float64")

    default_epoch = "2000-01-01_00:00:00"
    default_unit = "d"

    dataset = {
        "input_tai": {
            "offsets": tai_array,
            "unit": default_unit,
            "epoch": default_epoch,
        },
        "input_utc": {
            "offsets": utc_array,
            "unit": default_unit,
            "epoch": default_epoch,
        },
        "input_ut1": {
            "offsets": ut1_array,
            "unit": default_unit,
            "epoch": default_epoch,
        },
        "input_gps": {
            "offsets": gps_array,
            "unit": default_unit,
            "epoch": default_epoch,
        },
    }

    # Convert from TAI
    trf.convert_all(dataset, TimeRef.TAI, TimeRef.UTC, "input_tai", "output_tai2utc")
    trf.convert_all(dataset, TimeRef.TAI, TimeRef.UT1, "input_tai", "output_tai2ut1")
    trf.convert_all(dataset, TimeRef.TAI, TimeRef.GPS, "input_tai", "output_tai2gps")

    assert np.allclose(dataset["output_tai2utc"]["offsets"], utc_array, rtol=1e-9)
    assert np.allclose(dataset["output_tai2ut1"]["offsets"], ut1_array, rtol=1e-9)
    assert np.allclose(dataset["output_tai2gps"]["offsets"], gps_array, rtol=1e-9)

    # Convert from UTC
    trf.convert_all(dataset, TimeRef.UTC, TimeRef.TAI, "input_utc", "output_utc2tai")
    trf.convert_all(dataset, TimeRef.UTC, TimeRef.UT1, "input_utc", "output_utc2ut1")
    trf.convert_all(dataset, TimeRef.UTC, TimeRef.GPS, "input_utc", "output_utc2gps")

    assert np.allclose(dataset["output_utc2tai"]["offsets"], tai_array, rtol=1e-9)
    assert np.allclose(dataset["output_utc2ut1"]["offsets"], ut1_array, rtol=1e-9)
    assert np.allclose(dataset["output_utc2gps"]["offsets"], gps_array, rtol=1e-9)

    # Convert from GPS
    trf.convert_all(dataset, TimeRef.GPS, TimeRef.TAI, "input_gps", "output_gps2tai")
    trf.convert_all(dataset, TimeRef.GPS, TimeRef.UTC, "input_gps", "output_gps2utc")
    trf.convert_all(dataset, TimeRef.GPS, TimeRef.UT1, "input_gps", "output_gps2ut1")

    assert np.allclose(dataset["output_gps2tai"]["offsets"], tai_array, rtol=1e-9)
    assert np.allclose(dataset["output_gps2utc"]["offsets"], utc_array, rtol=1e-9)
    assert np.allclose(dataset["output_gps2ut1"]["offsets"], ut1_array, rtol=1e-9)


def test_time_reference_leap_second(trf):  # pylint: disable=invalid-name
    """
    Unit test for TimeReference.leap_second
    """
    # Check leap_second
    ref_leap_seconds = [
        (1, "2015-06-30_23:59:60", "2015-07-01_00:00:00"),
        (1, "2016-12-31_23:59:60", "2017-01-01_00:00:00"),
    ]
    assert trf.leap_seconds(4745.0, 6570.0) == ref_leap_seconds

    # Test at limit conditions, i.e. between 2015-06-30T23:59:59 and 2015-07-01T00:00:00
    utc = trf.timeref_to_timescale(TimeRef.UTC)
    epoch = AbsoluteDate("2000-01-01T00:00:00", utc)
    before = AbsoluteDate("2015-06-30T23:59:59", utc)
    after = AbsoluteDate("2015-07-01T00:00:00", utc)
    offset_before = before.offsetFrom(epoch, utc) / JD_TO_SECONDS
    offset_after = after.offsetFrom(epoch, utc) / JD_TO_SECONDS
    # logging.debug("%s, offset: %s", before, offset_before)
    # logging.debug("%s, offset: %s", after, offset_after)
    assert trf.leap_seconds(offset_before, offset_after) == ref_leap_seconds[:1]


def test_time_reference_ascii(trf):  # pylint: disable=invalid-name
    """
    Unit test for TimeReference.to_str and from_str
    """
    # Check processing to ASCII
    tai_tm = 8360.890787037037
    assert trf.to_str(tai_tm, fmt="STD") == "2022-11-21_21:22:44"
    assert trf.to_str(tai_tm, fmt="STD_MICROSEC") == "2022-11-21_21:22:44.000000"
    assert trf.to_str(tai_tm, fmt="COMPACT") == "20221121_212244"
    assert trf.to_str(tai_tm, fmt="CCSDSA_MICROSEC") == "2022-11-21T21:22:44.000000"

    assert trf.from_str("2022-11-21_21:22:44", fmt="STD") == tai_tm
    assert trf.from_str("2022-11-21T21:22:44.000000", fmt="CCSDSA_MICROSEC") == tai_tm

    assert trf.to_str(8338, fmt="STD", ref_in=TimeRef.UTC) == "2022-10-30_00:00:00"

    # Case of 2022-10-30_00:00:30; of rounded offset: 8338.00034722
    # - using the real offset from the epoch...
    off = compute_offset("2022-10-30_00:00:30")
    assert trf.to_str(off, fmt="STD", ref_in=TimeRef.UTC) == "2022-10-30_00:00:30"

    # (Apparent) Offsets are actually applied to DateTimeComponents, => if we use the same input and output time_ref, it
    # makes no difference
    assert trf.to_str(8338.00034722, fmt="STD", ref_in=TimeRef.TAI) == "2022-10-30_00:00:30"
    assert trf.to_str(8338.00034722, fmt="STD", ref_in=TimeRef.UTC) == "2022-10-30_00:00:30"

    # This particular flavour of to_str can convert on-the-fly as well.
    assert trf.to_str(8338.00042824, fmt="STD", ref_in=TimeRef.TAI, ref_out=TimeRef.UTC) == "2022-10-30_00:00:00"
    assert trf.to_str(8338.00077546, fmt="STD", ref_in=TimeRef.TAI, ref_out=TimeRef.UTC) == "2022-10-30_00:00:30"

    def _test_time_offset_convertion_back_and_forth(
        fmt: str, trf: TimeReference, epochs
    ):  # pylint: disable=invalid-name
        """
        Direct massive test date_as_string -> offset -> date_as_string
        """
        for epoch_exact, epoch_target in epochs:
            offset = compute_offset(epoch_exact)
            for time_ref in [TimeRef.UTC, TimeRef.TAI, TimeRef.GPS]:
                offset_to_str = trf.to_str(offset, fmt=fmt, ref_in=time_ref)
                # logging.debug(" + %s", time_ref.name)
                assert (
                    offset_to_str == epoch_target
                ), f"string convertion of {time_ref.name}={epoch_exact} to {epoch_target} fails (~~> {offset_to_str})"

    def _test_time_offset_convertion_back_and_forth_round7(
        fmt: str, trf: TimeReference, epochs
    ):  # pylint: disable=invalid-name
        """
        Massive tests
        - date_as_string -> epoch
        - epoch + [0..9] * 100µs -> correctly rounded date_as_string
        """
        # 1E-7 of a second is not that precise to express a date.
        # That means we cannot expect "59.{epoch_low}5" (6+1 fractional subsecond) to be precisely
        # rounded to the next 1e-6th of a second.
        # For instance, the offset for 2015-06-30_23:59:59.1234565 (7digits!) is 489023999.1234565
        # and instead of returning 0.1234565, math.modf(sec) (/ sec % 1/ sec-int(sec)/...) return 0.12345647811889648
        # which rounds to epoch_low instead of the expected epoch_high...
        # => the result to expect will not depend of the {sub7} digit appended -- because of floatting point operation
        # imprecisions.
        # => hence the convoluted way to determine the assertion expectation
        # Corollary: Trying to be more precise than a 1e-6th of a second is not really possible with 64bits
        # floating-point numbers.
        for epoch_low, epoch_high in epochs:
            offset_low = compute_offset(epoch_low, unit="s")
            middle_microsec = int((offset_low % 1) * 1e9) + 500  # reference middle point to test whether we round up
            for sub7 in range(10):
                sub_epoch = f"{epoch_low}{sub7}"
                offset = compute_offset(sub_epoch, unit="s")
                crt_microsec = int((offset % 1) * 1e9)
                rounding_is_up = crt_microsec >= middle_microsec
                # logging.debug(
                #     "*[%s] %s ; Δ=%s ; rounding up? %s (%s =>? %s)",
                #     sub7,
                #     sub_epoch,
                #     offset,
                #     rounding_is_up,
                #     crt_microsec,
                #     middle_microsec,
                # )
                # logging.debug(
                #     "%s --> %s ~~> sec= %s / %s",
                #     sub_epoch, offset, offset % 60, round(offset % 60, 6),
                # )
                for time_ref in [TimeRef.UTC, TimeRef.TAI, TimeRef.GPS]:
                    offset_to_str = trf.to_str(offset, fmt=fmt, ref_in=time_ref, unit="s")
                    # logging.debug(" + %s", time_ref.name)
                    epoch = epoch_high if rounding_is_up else epoch_low
                    # logging.debug("   expecting %s, generated %s", epoch, offset_to_str)
                    assert (
                        offset_to_str == epoch
                    ), f"string convertion of {time_ref.name}={sub_epoch} fails (~~> {offset_to_str})"

    _test_time_offset_convertion_back_and_forth(
        "STD",
        trf,
        [  # exact date --> target date
            ["2015-06-30_23:59:59.123456", "2015-06-30_23:59:59"],
            ["2022-11-21_21:22:44.123456", "2022-11-21_21:22:44"],
            ["2015-07-01_00:00:00.123456", "2015-07-01_00:00:00"],
            ["2015-07-31_23:59:59.987654", "2015-08-01_00:00:00"],
            # Let's not use 30 june 2015 as there is a leap second there in UTC
            # ["2015-06-30_23:59:59.987654", "2015-07-01_00:00:00"], # TAI, GPS...
            # ["2015-06-30_23:59:59.987654", "2015-06-30_23:59:60"], # UTC
            ["2022-11-21_21:22:44.987654", "2022-11-21_21:22:45"],
            ["2015-07-01_00:00:00.987654", "2015-07-01_00:00:01"],
        ],
    )
    _test_time_offset_convertion_back_and_forth(
        "STD_MICROSEC",
        trf,
        [  # exact date --> target date  # no rounding...
            ["2015-06-30_23:59:59.123456", "2015-06-30_23:59:59.123456"],
            ["2022-11-21_21:22:44.123456", "2022-11-21_21:22:44.123456"],
            ["2015-07-01_00:00:00.123456", "2015-07-01_00:00:00.123456"],
            ["2015-06-30_23:59:59.987654", "2015-06-30_23:59:59.987654"],
            ["2022-11-21_21:22:44.987654", "2022-11-21_21:22:44.987654"],
            ["2015-07-01_00:00:00.987654", "2015-07-01_00:00:00.987654"],
        ],
    )

    _test_time_offset_convertion_back_and_forth_round7(
        "STD_MICROSEC",
        trf,
        [  # exact_date/round_low_target ; round_high_target # some rounding...
            ["2015-06-30_23:59:59.123456", "2015-06-30_23:59:59.123457"],
            ["2022-11-21_21:22:44.123456", "2022-11-21_21:22:44.123457"],
            ["2015-07-01_00:00:00.123456", "2015-07-01_00:00:00.123457"],
            ["2015-06-30_23:59:59.987654", "2015-06-30_23:59:59.987655"],
            ["2022-11-21_21:22:44.987654", "2022-11-21_21:22:44.987655"],
            ["2015-07-01_00:00:00.987654", "2015-07-01_00:00:00.987655"],
        ],
    )


def test_time_reference_ascii_leap(trf):  # pylint: disable=invalid-name
    """
    Unit test for TimeReference.to_str and from_str handling leap seconds
    """
    assert trf.from_str("2016-12-31_23:59:59", fmt="STD") == 6209.999988425926
    assert trf.from_str("2016-12-31_23:59:60", fmt="STD") == 6210.0
    assert trf.from_str("2017-01-01_00:00:00", fmt="STD") == 6210.0

    # plain string conversion to UTC timestamp doesn't reflect leap second
    assert trf.to_str(6210.0, ref_in=TimeRef.UTC) == "2017-01-01_00:00:00"

    # need to convert from TAI
    tai_offset = trf.convert(6210.0, TimeRef.UTC, TimeRef.TAI)
    utc_leap_timestamp = trf.to_str(tai_offset - 1.0 / 86400.0, ref_in=TimeRef.TAI, ref_out=TimeRef.UTC)
    assert utc_leap_timestamp == "2016-12-31_23:59:60"


def test_time_reference_cuc(trf):  # pylint: disable=invalid-name
    """
    Unit test for TimeReference.from_cuc
    """
    cuc = np.array(
        [
            [1336436015, 0],
            [1336436015, 1000],
            [1336436015, 1000000],
            [1336436015, 10000000],
            [1336522415, 0],
        ],
        dtype="int64",
    )
    proc_ref = np.array([8168.00943287, 8168.00943287, 8168.00943356, 8168.00943977, 8169.00943287])
    proc_out = trf.from_cuc(cuc)
    assert np.allclose(proc_out, proc_ref, rtol=1e-9)


def test_time_reference_transport(trf):  # pylint: disable=invalid-name
    """
    Unit test for TimeReference.from_transport
    """
    trans = np.array(
        [
            [8320, 2122, 71836],
            [8320, 2122, 115836],
            [8320, 2122, 159835],
            [8320, 2122, 203835],
        ],
        dtype="int64",
    )
    proc_ref = np.array([8320.02456102, 8320.02456153, 8320.02456204, 8320.02456254])
    proc_out = trf.from_transport(trans)
    assert np.allclose(proc_out, proc_ref, rtol=1e-9)


def test_time_reference_pickling(trf):
    """
    Unit test to validate pickle protocol on TimeReference
    """
    trf_copy = repickle(trf)

    # We check that the copied object has an Orekit DataContext, different from the original object
    copy_context = getattr(trf_copy, "context", None)
    assert copy_context is not None
    assert copy_context is not trf.context


def test_time_reference_to_dates(trf):
    """
    Unit test to validate the behaviour of TimeReference.to_dates() iterator
    """
    time_array = {
        "offsets": np.array([0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 3.0]),
        "unit": "s",
        "epoch": "2012-01-01T12:30:00",
    }
    abs_dates = list(trf.to_dates(time_array))

    assert abs_dates[1] == abs_dates[2], "Same AbsoluteDate object expected for times 1 and 2"
    assert abs_dates[1] == abs_dates[3], "Same AbsoluteDate object expected for times 1 and 3"

    assert abs_dates[4] == abs_dates[5], "Same AbsoluteDate object expected for times 4 and 5"

    assert abs_dates[1].durationFrom(abs_dates[0]) == 1.0, "Expected 1s duration between times 0 and 1"
    assert abs_dates[4].durationFrom(abs_dates[3]) == 1.0, "Expected 1s duration between times 3 and 4"
    assert abs_dates[6].durationFrom(abs_dates[5]) == 1.0, "Expected 1s duration between times 5 and 6"


def given_time_reference_iers_a():
    """
    Fixture to produce a TimeReference with IERS A bulletin
    """

    # Read orekit-compatible IERS bulletin
    iers_path = osp.join(
        TEST_DIR,
        "resources",
        "orekit",
        "IERS",
        "S2__OPER_AUX_UT1UTC_ADG__20220916T000000_V20220916T000000_20230915T000000.txt",
    )

    iers_data = S3LegacyDriver.read_iers_file(iers_path)

    return TimeReference(iers_bulletin_a=iers_data)


def given_time_reference_iers_b():
    """
    Fixture to produce an TimeReference with IERS B bulletin
    """

    # Read orekit-compatible IERS bulletin
    iers_path = osp.join(TEST_DIR, "resources", "207_BULLETIN_B207.txt")

    iers_data = S3LegacyDriver.read_iers_file(iers_path)

    return TimeReference(iers_bulletin_b=iers_data)


def given_time_reference_rapid_data():
    """
    Fixture to produce an TimeReference with IERS Rapid Data Columns file
    """

    # Read orekit-compatible IERS rapid data columns
    rdc_path = osp.join(
        ASGARD_DATA,
        "ADFdynamic",
        "S0__ADF_IERSB_19920101T000000_20220630T000000_20220701T101100.txt",
    )

    iers_data = S3LegacyDriver.read_iers_file(rdc_path)

    return TimeReference(iers_rapid_data_col=iers_data)


@pytest.mark.parametrize(
    "trf_model, ut1",
    [
        (given_time_reference_iers_a(), 8330.890358713033),
        (given_time_reference_iers_b(), 8330.890358722061),
        (given_time_reference_rapid_data(), 8330.890358932897),
    ],
    ids=[
        "iers_a",
        "iers_b",
        "rapid_data",
    ],
)
def test_time_reference_convert_single_date(trf_model, ut1):
    """
    Unit test for time conversion with IERS B

    Value of UT1 time is more sensitive to the data source
    """

    tai_value = 8330.890787037037
    utc_value = 8330.890358796296
    ut1_value = ut1
    gps_value = 8330.890567129629

    # Convert from TAI
    assert np.allclose(
        trf_model.convert(tai_value, TimeRef.TAI, TimeRef.UTC),
        utc_value,
        rtol=0.0,
        atol=1e-9,
    )
    assert np.allclose(
        trf_model.convert(tai_value, TimeRef.TAI, TimeRef.UT1),
        ut1_value,
        rtol=0.0,
        atol=1e-9,
    )
    assert np.allclose(
        trf_model.convert(tai_value, TimeRef.TAI, TimeRef.GPS),
        gps_value,
        rtol=0.0,
        atol=1e-9,
    )

    # Convert from UTC
    assert np.allclose(
        trf_model.convert(utc_value, TimeRef.UTC, TimeRef.TAI),
        tai_value,
        rtol=0.0,
        atol=1e-9,
    )
    assert np.allclose(
        trf_model.convert(utc_value, TimeRef.UTC, TimeRef.UT1),
        ut1_value,
        rtol=0.0,
        atol=1e-9,
    )
    assert np.allclose(
        trf_model.convert(utc_value, TimeRef.UTC, TimeRef.GPS),
        gps_value,
        rtol=0.0,
        atol=1e-9,
    )

    # Convert from GPS
    assert np.allclose(
        trf_model.convert(gps_value, TimeRef.GPS, TimeRef.TAI),
        tai_value,
        rtol=0.0,
        atol=1e-9,
    )
    assert np.allclose(
        trf_model.convert(gps_value, TimeRef.GPS, TimeRef.UTC),
        utc_value,
        rtol=0.0,
        atol=1e-9,
    )
    assert np.allclose(
        trf_model.convert(gps_value, TimeRef.GPS, TimeRef.UT1),
        ut1_value,
        rtol=0.0,
        atol=1e-9,
    )


def test_time_reference_to_eocfi(trf):
    """
    Unit test for TimeReference.to_eocfi
    """
    offsets = np.array([1.5, 2.5, 4.0], dtype="float64")
    epoch = "2012-02-10T09:40:03"
    unit = "s"
    mjd_offsets = trf.to_eocfi(offsets, unit, epoch)

    # Epoch in MJD convention:
    #  - 12 years (2 of them are bissextile)
    #  - 31 january days
    #  - 10 february days
    #  - 9 hours
    #  - 40 minutes
    #  - 3 seconds
    epoch_mjd = 12 * 365 + 2 + 31 + 10 + (9 + (40 + 3 / 60) / 60) / 24
    ref_offsets = epoch_mjd + offsets / 86400.0

    assert np.allclose(mjd_offsets, ref_offsets, rtol=0, atol=1e-7)


def test_time_reference_change_epoch_and_unit(trf):
    """
    Unit test for TimeReference.change_epoch_and_unit
    """
    offsets = np.array([1.5, 2.5, 4.0], dtype="float64")
    epoch = "2012-02-10T09:40:03"
    unit = "s"
    time_array = {
        "offsets": offsets,
        "epoch": epoch,
        "unit": unit,
    }
    mjd_time_array = trf.change_epoch_and_unit(time_array, epoch="2000-01-01T00:00:00", unit="d")

    # Epoch in MJD convention:
    #  - 12 years (2 of them are bissextile)
    #  - 31 january days
    #  - 10 february days
    #  - 9 hours
    #  - 40 minutes
    #  - 3 seconds
    epoch_mjd = 12 * 365 + 2 + 31 + 10 + (9 + (40 + 3 / 60) / 60) / 24
    ref_offsets = epoch_mjd + offsets / 86400.0

    assert np.allclose(mjd_time_array["offsets"], ref_offsets, rtol=0, atol=1e-7)
    assert mjd_time_array["epoch"] == "2000-01-01T00:00:00"
    assert mjd_time_array["unit"] == "d"

    initial_time_array = trf.change_epoch_and_unit(time_array, epoch="2012-02-10T09:40:03", unit="s")
    assert np.allclose(initial_time_array["offsets"], offsets, rtol=0, atol=1e-7)
    assert initial_time_array["epoch"] == "2012-02-10T09:40:03"
    assert initial_time_array["unit"] == "s"


def test_epoch_to_date(trf):
    """
    Unit test for TimeReference.epoch_to_date
    """

    # Build a time array
    time_array = {
        "offsets": np.array([1.0, 2.0, 3.0]),
        "epoch": "2012-02-10T09:40:03",
        "unit": "s",
    }

    epoch_date = trf.epoch_to_date(time_array)
    ref_date = AbsoluteDate(2012, 2, 10, 9, 40, 3.0, trf.timeref_to_timescale(TimeRef.GPS))

    assert epoch_date.durationFrom(ref_date) < 1.0

    # specific timeRef
    time_array = {
        "offsets": np.array([1.0, 2.0, 3.0]),
        "epoch": "2012-02-10T09:40:03",
        "unit": "s",
        "ref": "TAI",
    }

    epoch_date = trf.epoch_to_date(time_array)
    ref_date = AbsoluteDate(2012, 2, 10, 9, 40, 3.0, trf.timeref_to_timescale(TimeRef.TAI))

    assert epoch_date.durationFrom(ref_date) < 1.0

    # no epoch
    time_array = {
        "offsets": np.array([1.0, 2.0, 3.0]),
        "unit": "s",
        "ref": "TAI",
    }

    epoch_date = trf.epoch_to_date(time_array)
    ref_date = AbsoluteDate(2000, 1, 1, 0, 0, 0.0, trf.timeref_to_timescale(TimeRef.TAI))

    assert epoch_date.durationFrom(ref_date) < 1.0


def test_offsets_to_seconds(trf):
    """
    Unit test for TimeReference.offsets_to_seconds
    """
    # seconds
    time_array = {
        "offsets": np.array([1.0, 2.0, 3.0]),
        "epoch": "2012-02-10T09:40:03",
        "unit": "s",
    }

    times = trf.offsets_to_seconds(time_array)
    assert np.all(times == time_array["offsets"])

    # days
    time_array = {
        "offsets": np.array([1.0, 2.0, 3.0]),
        "epoch": "2012-02-10T09:40:03",
        "unit": "d",
    }

    times = trf.offsets_to_seconds(time_array)
    assert np.all(times == time_array["offsets"] * 86400.0)


@pytest.fixture(name="fro_20221030", scope="module")
def read_fro_20221030():
    """
    Fixture to extract FRO orbit from 2022-10-30
    """
    orbit_file = osp.join(
        TEST_DIR,
        "resources/S3/FRO",
        "S3A_OPER_MPL_ORBRES_20221030T000000_20221109T000000_0001.EOF",
    )

    return S3LegacyDriver.read_orbit_file(orbit_file)


@pytest.fixture(name="trf_lut", scope="module")  # pylint: disable=invalid-name
def time_reference_from_lut(fro_20221030):
    """
    Fixture to produce an TimeReference
    """
    return TimeReference(lut=fro_20221030["times"])


def test_ut1_from_lut(trf_lut):
    """
    Unit test for UT1 time conversion from look-up table
    """
    ascii_time = "2022-10-30T00:02:00.0"  # in UTC
    epoch = "2022-10-30T00:00:00.0"
    unit = "s"
    proc_time = trf_lut.from_str(ascii_time, epoch=epoch, unit=unit)

    assert proc_time == 120.0

    ut1_time = trf_lut.convert(proc_time, TimeRef.UTC, TimeRef.UT1, epoch=epoch, unit=unit)

    assert np.allclose(ut1_time, 119.989567, rtol=0, atol=1e-5)

    tai_time = trf_lut.convert(ut1_time, TimeRef.UT1, TimeRef.TAI, epoch=epoch, unit=unit)

    assert np.allclose(tai_time, 157.0, rtol=0, atol=1e-5)
