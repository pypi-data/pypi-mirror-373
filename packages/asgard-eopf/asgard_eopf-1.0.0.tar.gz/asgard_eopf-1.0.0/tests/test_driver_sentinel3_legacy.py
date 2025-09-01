#!/usr/bin/env python
# coding: utf8
#
# Copyright 2023 CS GROUP
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
Unit tests for drivers.sentinel_3_legacy
"""

import os
import os.path as osp

import numpy as np
import pytest
from drivers.explorer_legacy import ExplorerDriver
from drivers.sentinel_3_legacy import S3LegacyDriver
from org.orekit.time import (  # pylint: disable=import-error, wrong-import-order
    AbsoluteDate,
    TimeScalesFactory,
)

from asgard.core.frame import FrameId
from asgard.core.logger import initialize
from asgard.core.time import JD_TO_SECONDS, TimeRef
from asgard.models.body import EarthBody
from asgard.models.time import TimeReference

TEST_DIR = osp.dirname(__file__)

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")


SAMPLE_IERS = [osp.join(f"{TEST_DIR}/resources/bulletinb-348.txt"), osp.join(f"{TEST_DIR}/resources/bulletinb-413.txt")]

initialize("dfdl")


@pytest.fixture(name="driver", scope="module")
def s3_olci_driver():
    """
    Test fixture to create a S3 OLCI driver
    """
    iers_data = S3LegacyDriver.read_iers_file(SAMPLE_IERS[0])
    time_model = TimeReference(iers_bulletin_b=iers_data)
    config = {"time_reference": time_model}
    return S3LegacyDriver(EarthBody(**config))


def test_driver_s3_legacy_navatt(driver):
    """
    Unit test for S3LegacyDriver.parse_navatt()
    """
    output = driver.parse_navatt([osp.join(TEST_DIR, "resources/S3/NAT/ISPData.dat")])

    assert output["time_gps"]["offsets"].shape[0] == 6141
    assert output["positions"].shape[0] == 6141
    assert output["velocities"].shape[0] == 6141
    assert output["orb_rev"].shape[0] == 6141
    assert output["oop"].shape[0] == 6141

    assert np.allclose(output["time_gps"]["offsets"][0], 8168.00943287)
    assert np.allclose(output["time_gps"]["offsets"][-1], 8168.08049769)

    assert np.allclose(output["positions"][0], [-2680644.20845, 67723.63616, 6653211.82078])
    assert np.allclose(output["velocities"][0], [6412.70383, 2815.92821, 2549.27122])
    assert np.allclose(output["quaternions"][0], [-0.19967632, 0.96138971, -0.0431883, 0.18437453])
    assert output["orb_rev"][0] == 158
    assert output["orb_rev"][-1] == 159
    assert np.allclose(output["oop"][0], 69.60421275)
    assert np.allclose(output["oop"][-1], 74.4154565)

    output_fitlered = driver.parse_navatt(
        [osp.join(TEST_DIR, "resources/S3/NAT/ISPData.dat")],
        start_time=8168.024,
        end_time=8168.026,
    )

    assert output_fitlered["time_gps"]["offsets"][0] >= 8168.024
    assert output_fitlered["time_gps"]["offsets"][-1] <= 8168.026

    assert output_fitlered["time_gps"]["offsets"].shape[0] == 173
    assert output_fitlered["positions"].shape[0] == 173
    assert output_fitlered["velocities"].shape[0] == 173
    assert output_fitlered["orb_rev"].shape[0] == 173
    assert output_fitlered["oop"].shape[0] == 173

    assert np.allclose(
        output["time_gps"]["offsets"][1259:1432],
        output_fitlered["time_gps"]["offsets"],
    )


def test_driver_s3_legacy_timestamp(driver):
    """
    Unit test for S3LegacyDriver.parse_timestamps()
    """
    output = driver.parse_timestamps(osp.join(TEST_DIR, "resources/S3/OLCI/EFR_20220513T003504/ISPAnnotation.dat"))

    assert output.shape[0] == 13640
    assert np.allclose(output[0], 8168.02456102)
    assert np.allclose(output[-1], 8168.02594981)


def test_driver_s3_legacy_olci(driver):
    """
    Test case from navatt parsing to orbit file and attitude file
    """

    # delta_jd read from OL_1_INS dataset ("time_parameters/midacquisition_offset")
    timestamps = driver.parse_timestamps(
        osp.join(TEST_DIR, "resources/S3/OLCI/EFR_20220513T003504/ISPAnnotation.dat"),
        delta_jd=21390 / 8.64e10,
    )

    # use the full timestamp interval + margins
    orbit, attitude, oop = driver.read_navatt_file(
        [osp.join(TEST_DIR, "resources/S3/NAT/ISPData.dat")],
        start_time=timestamps[0] - 4 / JD_TO_SECONDS,
        end_time=timestamps[-1] + 4 / JD_TO_SECONDS,
        abs_orbit=32472,
    )

    # create output folder
    out_folder = osp.join(TEST_DIR, "outputs/olci")
    os.makedirs(out_folder, exist_ok=True)

    # Save EME2000 orbit file
    driver.write_orbit_file(orbit, osp.join(out_folder, "sample_orbit_eme2000_python.xml"))

    # convert orbit to Earth Fixed
    orbit_ef = driver.change_orbit_frame(orbit, FrameId.EF)

    # Save EF orbit file
    driver.write_orbit_file(orbit_ef, osp.join(out_folder, "sample_orbit_python.xml"))

    nb_missing, max_gap = driver.check_missing_navatt(orbit["times"]["GPS"]["offsets"])

    assert nb_missing == 0
    assert np.allclose(max_gap, 1.0)

    driver.write_attitude_file(attitude, osp.join(out_folder, "sample_attitude_python.xml"))

    # save timestamps GPS and On-Orbit Positions
    np.save(
        osp.join(out_folder, "sample_timestamps_gps.npy"),
        orbit["times"]["GPS"]["offsets"],
    )
    np.save(osp.join(out_folder, "sample_oop.npy"), oop)


@pytest.fixture(name="driver_slstr", scope="module")
def s3_slstr_driver():
    """
    Fixture to instanciate a S3SLSTRDriver
    """
    iers_data = S3LegacyDriver.read_iers_file(SAMPLE_IERS[1])
    time_model = TimeReference(iers_bulletin_b=iers_data)
    config = {"time_reference": time_model}
    return S3LegacyDriver(EarthBody(**config))


@pytest.mark.parametrize(
    "iers_path, navatt_path",
    [
        ("resources/bulletinb-348.txt", "resources/S3/NAT/ISPData.dat"),
        ("resources/bulletinb-413.txt", "resources/S3/SLSTR/NAT/ISPData.dat"),
    ],
    ids=[
        "S3/NAT-b-348",
        "S3/SLSTR/NAT-b-413",
    ],
)
def test_change_orbit_frame_fortran(iers_path: str, navatt_path: str):
    """test change_orbit_frame with Fortran style array, ref. issue #319
    * https://numpy.org/doc/stable/reference/generated/numpy.ascontiguousarray.html
    * https://numpy.org/doc/stable/reference/generated/numpy.ndarray.flags.html
    """
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, iers_path))
    time_model = TimeReference(iers_bulletin_b=iers_data)
    driver = S3LegacyDriver(EarthBody(time_reference=time_model))
    orbit, attitude, oop = driver.read_navatt_file([osp.join(TEST_DIR, navatt_path)])
    assert attitude is not None
    assert oop is not None
    assert isinstance(orbit["positions"], np.ndarray)
    assert orbit["positions"].data.c_contiguous  # A bool indicating whether the memory is C contiguous.
    assert orbit["positions"].strides == (24, 8)
    orbit_in_ef = driver.change_orbit_frame(orbit, frame=FrameId.EF)
    orbit_fortran = orbit.copy()
    # Copy orbit in Fortran style memory layout
    # order: Controls the memory layout of the copy. 'F' means F-order, Fortran contiguous
    orbit_fortran["positions"] = np.copy(orbit["positions"], order="F")
    assert orbit_fortran["positions"].data.f_contiguous  # A bool indicating whether the memory is Fortran contiguous.
    assert orbit_fortran["positions"].strides in [(8, 48216), (8, 49128)]
    orbit_fortran_in_ef = driver.change_orbit_frame(orbit_fortran, frame=FrameId.EF)
    # assert non zero positions
    assert np.sum(np.abs(orbit_fortran_in_ef["positions"])) > 1e-6
    # assert no diff between EF in C-style and Fortran
    assert np.allclose(orbit_fortran_in_ef["positions"], orbit_in_ef["positions"], rtol=0, atol=1e-9)


def test_driver_s3_legacy_slstr(driver_slstr):
    """
    Test case from navatt parsing to orbit file and attitude file for a SLSTR product
    """

    timestamps_204936 = driver_slstr.parse_timestamps(
        osp.join(TEST_DIR, "resources/S3/SLSTR/SLT_20221101T204936/ISPAnnotation.dat"),
    )
    timestamps_205436 = driver_slstr.parse_timestamps(
        osp.join(TEST_DIR, "resources/S3/SLSTR/SLT_20221101T205436/ISPAnnotation.dat"),
    )

    # ~ print(f"Granule 18: {timestamps_204936[0]} -> {timestamps_204936[-1]}")
    # ~ print(f"Granule 19: {timestamps_205436[0]} -> {timestamps_205436[-1]}")

    # Delay in second between SSP associated with a scan and the crossing point between scan and
    # track (from SL_1_PCP_AX)
    delta_t_nad = 15
    delta_t_obl = 150

    # define L1 processing time range
    jd_start_l1 = timestamps_204936[300 * 41]  # first guess: pass the first 300 scans
    jd_end_l1 = timestamps_204936[-1]  # must match the last scan of the L0 granule

    assert len(timestamps_204936) == 41000
    unique_times = np.unique(timestamps_204936)
    assert len(unique_times) == 1000

    assert len(timestamps_205436) == 41000
    # ~ print(unique_times[300:350])

    # apply margins
    jd_isp_first = jd_start_l1 - delta_t_nad / JD_TO_SECONDS
    jd_isp_last = jd_end_l1 + delta_t_obl / JD_TO_SECONDS

    # completeness of scan cycle: not checked here!

    # search ISP timestamps to find index of first and last ISP: not needed here to filter navatt

    # use the requested timestamp interval + margins
    orbit, attitude, oop = driver_slstr.read_navatt_file(
        [osp.join(TEST_DIR, "resources/S3/SLSTR/NAT/ISPData.dat")],
        start_time=jd_isp_first - 4 / JD_TO_SECONDS,
        end_time=jd_isp_last + 4 / JD_TO_SECONDS,
        abs_orbit=34937,
    )

    # create output folder
    out_folder = osp.join(TEST_DIR, "outputs/slstr")
    os.makedirs(out_folder, exist_ok=True)

    # Save EME2000 orbit file
    driver_slstr.write_orbit_file(orbit, osp.join(out_folder, "sample_orbit_eme2000.xml"))

    # Convert orbit to Earth Fixed
    orbit_ef = driver_slstr.change_orbit_frame(orbit, FrameId.EF)

    # Save EF orbit file
    driver_slstr.write_orbit_file(orbit_ef, osp.join(out_folder, "sample_orbit.xml"))

    nb_missing, max_gap = driver_slstr.check_missing_navatt(orbit["times"]["GPS"]["offsets"])

    assert nb_missing == 0
    assert np.allclose(max_gap, 1.0)

    driver_slstr.write_attitude_file(attitude, osp.join(out_folder, "sample_attitude.xml"))

    # save timestamps GPS and On-Orbit Positions
    np.save(
        osp.join(out_folder, "sample_timestamps_gps.npy"),
        orbit["times"]["GPS"]["offsets"],
    )
    np.save(osp.join(out_folder, "sample_oop.npy"), oop)


@pytest.mark.slow
def test_driver_s3_legacy_scanpos(driver_slstr):
    """
    Test case from navatt parsing to orbit file and attitude file for a SLSTR product
    """

    # create output folder
    out_folder = osp.join(TEST_DIR, "outputs/slstr")
    os.makedirs(out_folder, exist_ok=True)

    timestamps_204936 = driver_slstr.parse_timestamps(
        osp.join(TEST_DIR, "resources/S3/SLSTR/SLT_20221101T204936/ISPAnnotation.dat"),
    )
    frame_times = np.unique(timestamps_204936)
    assert len(frame_times) == 1000

    isp_204936 = osp.join(
        ASGARD_DATA,
        "S3ASLSTRdataset",
        "S3A_SL_0_SLT____20221101T204936_20221101T205436_20221101T212249_0299_091_314______"
        "PS1_O_NR_004.SEN3/ISPData.dat",
    )

    ancilary_file = osp.join(TEST_DIR, "resources/S3/SLSTR/ANC/SL_1_ANC_AX.nc")

    # parse scan positions
    nad_scanpos = driver_slstr.slstr_scanpos(isp_204936, view="NAD", scene="EO")
    obl_scanpos = driver_slstr.slstr_scanpos(isp_204936, view="OBL", scene="EO")

    # extract scan angles
    driver_slstr.encoder_to_scan_angles(nad_scanpos, ancilary_file)
    driver_slstr.encoder_to_scan_angles(obl_scanpos, ancilary_file)

    # dump results
    np.save(osp.join(out_folder, "sample_frame_times.npy"), frame_times)
    np.save(
        osp.join(out_folder, "sample_nad_first_acq.npy"),
        nad_scanpos["target_first_acq"],
    )
    np.save(
        osp.join(out_folder, "sample_obl_first_acq.npy"),
        obl_scanpos["target_first_acq"],
    )
    np.save(
        osp.join(out_folder, "sample_nad_scan_angle_1km.npy"),
        nad_scanpos["scan_angles_1km"],
    )
    np.save(
        osp.join(out_folder, "sample_nad_scan_angle_05km.npy"),
        nad_scanpos["scan_angles_05km"],
    )
    np.save(
        osp.join(out_folder, "sample_obl_scan_angle_1km.npy"),
        obl_scanpos["scan_angles_1km"],
    )
    np.save(
        osp.join(out_folder, "sample_obl_scan_angle_05km.npy"),
        obl_scanpos["scan_angles_05km"],
    )


def test_driver_osf_file():
    """
    Test parsing of OSF files
    """
    osf_path = os.path.join(
        ASGARD_DATA,
        "S3AOLCIdataset",
        "S3A_AX___OSF_AX_20160216T192404_99991231T235959_20220330T090651___________________EUM_O_AL_001.SEN3",
        "S3A_OPER_MPL_ORBSCT_20160216T192404_99999999T999999_0006.EOF",
    )

    osf = ExplorerDriver.read_orbit_scenario_file(osf_path)
    times = {"offsets": osf["anx_time"]["TAI"], "unit": osf["anx_time"]["unit"], "epoch": osf["anx_time"]["epoch"]}
    abs_dates = list(TimeReference().to_dates(times, TimeRef.TAI))
    # date of first orbit change
    ref_date_tai = AbsoluteDate("2016-02-16T19:24:39.629918", TimeScalesFactory.getTAI())
    assert ref_date_tai.isCloseTo(abs_dates[0], float(1e-7))

    assert "Absolute_Orbit" in osf["orbit"]
    assert len(osf["orbit"]["Absolute_Orbit"]) == 6
    assert "Relative_Orbit" in osf["orbit"]
    assert "Cycle_Number" in osf["orbit"]
    assert "Phase_Number" in osf["orbit"]
    assert "Repeat_Cycle" in osf["cycle"]
    assert "Cycle_Length" in osf["cycle"]
    assert "ANX_Longitude" in osf["cycle"]
    assert "MLST" in osf["cycle"]
    assert "MLST_Drift" in osf["cycle"]
