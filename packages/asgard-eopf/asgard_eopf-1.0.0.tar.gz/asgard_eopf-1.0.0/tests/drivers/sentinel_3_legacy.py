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
Drivers for Sentinel3 legacy products
"""

from itertools import chain
from typing import List, Tuple

import netCDF4
import numpy as np
from drivers.explorer_legacy import ExplorerDriver

from asgard.core.math import extend_circular_lut
from asgard.core.time import JD_TO_SECONDS, TimeRef
from asgard.wrappers.dfdl.s3_navatt import File as NavattFile
from asgard.wrappers.dfdl.s3_slstr_slt import File as SLTFile
from asgard.wrappers.dfdl.s3_timestamp_annotation import File as S3_AnnotFile

#: Factor to convert km to meters
KM_TO_M = 1000.0
#:
OOP_DN_TO_DEG = 8.381903171539307e-08

SLT_TARGET_ID = {
    "NAD": {
        "EO": 228,
        "BB+Y": 225,
        "BB-Y": 231,
        "VISCAL": 224,
    },
    "OBL": {
        "EO": 226,
        "BB+Y": 230,
        "BB-Y": 227,
        "VISCAL": 229,
    },
}


class S3LegacyDriver(ExplorerDriver):
    """
    Sentinel3 legacy driver, handles legacy format to feed into ASGARD
    :class:`asgard.sensors.sentinel3.S3OLCIGeometry`, :class:`asgard.sensors.sentinel3.S3SLSTRGeometry`
    """

    def parse_timestamps(self, annotation_file, delta_jd: float = 0.0) -> np.ndarray:
        """
        Parse the annotation binary file to get ISP timestamps

        :param annotation_file: path to binary annotation file
        :param float delta_jd: Delta with middle acquisition time (in MJD processing format)
        :return: array of timestamps in processing format
        :rtype: np.ndarray
        """
        annot = S3_AnnotFile(annotation_file)
        size = len(annot)

        times_trans = np.zeros((size, 3), dtype="int64")
        for idx, item in enumerate(annot):
            times_trans[idx] = [
                item["annotation"]["gpsTime"]["days"],
                item["annotation"]["gpsTime"]["seconds"],
                item["annotation"]["gpsTime"]["microseconds"],
            ]

        # convert to processing format
        times = self.time_reference.from_transport(times_trans)

        # correct JD to middle acquisition time
        times = times - delta_jd

        return times

    def parse_navatt(
        self,
        navatt_files: List[str],
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> dict:
        """
        Parse the navatt paquets and write orbit and attitude scratch files

        :param List[str] navatt_files: list of input Navatt file path (ISP format) sorted by date
        :param float|None start_time: Start time (GPS MJD) to filter Navatt measurements
        :param float|None end_time: End time (GPS MJD) to filter Navatt measurements
        :return: Dataset with the extracted and filtered values
        """
        nav_list = [NavattFile(path) for path in navatt_files]
        size = 0
        for nav in nav_list:
            size += len(nav)

        # ISP packet times (CUC)
        pus_times_cuc = np.zeros((size, 2), dtype="int64")
        # Position vector
        position = np.zeros((size, 3), dtype="float64")
        # Velocity vector
        velocity = np.zeros((size, 3), dtype="float64")
        # Attitude quaternions
        attitude = np.zeros((size, 4), dtype="float64")
        # orbit revolution number
        orb_rev = np.zeros((size), dtype="int32")
        # on orbit position
        oop = np.zeros((size), dtype="float64")

        # Extract times, position, velocity, attitude, orbital revolution, on-orbit position
        for idx, item in enumerate(chain(*nav_list)):
            pus_times_cuc[idx] = [
                item["measurements"]["secondaryHeader"]["time"]["coarse"],
                item["measurements"]["secondaryHeader"]["time"]["fine"],
            ]
            position[idx] = [
                item["measurements"]["sourceData"]["AO_DAT_I_POS_I_SC_EST_1"] * KM_TO_M,
                item["measurements"]["sourceData"]["AO_DAT_I_POS_I_SC_EST_2"] * KM_TO_M,
                item["measurements"]["sourceData"]["AO_DAT_I_POS_I_SC_EST_3"] * KM_TO_M,
            ]
            velocity[idx] = [
                item["measurements"]["sourceData"]["AO_DAT_I_VEL_I_SC_EST_1"] * KM_TO_M,
                item["measurements"]["sourceData"]["AO_DAT_I_VEL_I_SC_EST_2"] * KM_TO_M,
                item["measurements"]["sourceData"]["AO_DAT_I_VEL_I_SC_EST_3"] * KM_TO_M,
            ]
            # Put already the quaternion array in scalar-last convention
            attitude[idx] = [
                item["measurements"]["sourceData"]["AO_DAT_Q_I_SC_EST_2"],
                item["measurements"]["sourceData"]["AO_DAT_Q_I_SC_EST_3"],
                item["measurements"]["sourceData"]["AO_DAT_Q_I_SC_EST_4"],
                item["measurements"]["sourceData"]["AO_DAT_Q_I_SC_EST_1"],
            ]
            orb_rev[idx] = item["measurements"]["sourceData"]["AO_DAT_NAVATT_ORBITNUMBER_EST_ITG"]
            oop[idx] = float(item["measurements"]["sourceData"]["AO_DAT_NAVATT_OOP_EST_ITG"]) * OOP_DN_TO_DEG

        # convert to processing format
        pus_times = self.time_reference.from_cuc(pus_times_cuc)

        # filter on the interval [start_time, end_time]
        start_pos = 0
        end_pos = size
        if start_time is not None:
            start_pos = np.searchsorted(pus_times, start_time)
        assert start_pos < size
        if end_time is not None:
            end_pos = np.searchsorted(pus_times, end_time, side="right")
        assert end_pos > 0
        # apply filter if needed
        if start_pos > 0 or end_pos < size:
            pus_times = pus_times[start_pos:end_pos]
            position = position[start_pos:end_pos]
            velocity = velocity[start_pos:end_pos]
            attitude = attitude[start_pos:end_pos]
            orb_rev = orb_rev[start_pos:end_pos]
            oop = oop[start_pos:end_pos]

        # return a complete dataset
        return {
            "time_gps": {
                "offsets": pus_times,
                "ref": "GPS",
            },
            "positions": position,
            "velocities": velocity,
            "quaternions": attitude,
            "orb_rev": orb_rev,
            "oop": oop,
        }

    @staticmethod
    def check_missing_navatt(time: np.ndarray) -> Tuple[int, float]:
        """
        Check time delta between consecutive records

        :param np.ndarray time: Time array of NAVATT records
        :return: tuple with number of missing records and maximum gap (in s)
        """
        prev_time = time[0]
        max_gap = 0.0
        nb_missing = 0
        # missing navatt threshold is 1.5 second
        threshold = 1.5 / JD_TO_SECONDS

        for cur_time in time:
            delta = cur_time - prev_time
            max_gap = max(max_gap, delta)
            if delta > threshold:
                nb_missing += round(delta * JD_TO_SECONDS) - 1
            prev_time = cur_time

        return nb_missing, max_gap * JD_TO_SECONDS

    def read_navatt_file(
        self,
        navatt_files: List[str],
        start_time: float | None = None,
        end_time: float | None = None,
        abs_orbit: int | None = None,
    ) -> Tuple[dict, dict, np.ndarray]:
        """
        Read NAVATT data from a binary NAT dataset, extract orbit and attitude structures

        :param List[str] navatt_files: list of input Navatt file path (ISP format) sorted by date
        :param float|None start_time: Start time (GPS MJD) to filter Navatt measurements
        :param float|None end_time: End time (GPS MJD) to filter Navatt measurements
        :param int|None abs_orbit: Number of first absolute orbit, used to convert from relative orbit
        :return: tuple with orbit object, attitude object, and on-orbit positions array
        """
        navatt = self.parse_navatt(navatt_files, start_time=start_time, end_time=end_time)

        if abs_orbit is not None:
            navatt["orb_rev"] += abs_orbit - navatt["orb_rev"][0]

        time_start_ascii = "UTC=" + self.time_reference.to_str(
            navatt["time_gps"]["offsets"][0],
            fmt="CCSDSA",
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
        )
        time_stop_ascii = "UTC=" + self.time_reference.to_str(
            navatt["time_gps"]["offsets"][-1],
            fmt="CCSDSA",
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
        )

        max_gap = np.max(np.diff(navatt["time_gps"]["offsets"])) * JD_TO_SECONDS

        orbit = {
            "times": {
                "GPS": navatt["time_gps"],
            },
            "positions": navatt["positions"],
            "velocities": navatt["velocities"],
            "absolute_orbit": navatt["orb_rev"],
            "frame": "EME2000",
            "time_ref": "TAI",
            "start_date": time_start_ascii,
            "stop_date": time_stop_ascii,
        }

        self.fill_other_timescales(orbit["times"])

        attitude = {
            "times": {
                "GPS": navatt["time_gps"],
                "UTC": orbit["times"]["UTC"],
            },
            "quaternions": navatt["quaternions"],
            "max_gap": max_gap,
            "frame": "EME2000",
            "time_ref": "UTC",
            "start_date": time_start_ascii,
            "stop_date": time_stop_ascii,
        }

        return orbit, attitude, navatt["oop"]

    @staticmethod
    def slstr_scanpos(isp_path: str, view: str = "NAD", scene: str = "EO") -> dict:
        """
        Extract scan positions from "SLT" ISPData.dat, corresponding to a given view and scene

        :param str isp_path: Path to instrument space packets "SLT"
        :param str view: SLSTR instrument view ("NAD"/"OBL")
        :param str scene: SLSTR instrument scene ("EO"/"BB+Y"/"BB-Y"/"VISCAL")
        :return: Array of scan positions in encoder steps (nb_scans, np_pixels)
        """
        assert view in ["NAD", "OBL"]
        assert scene in ["EO", "BB+Y", "BB-Y", "VISCAL"]

        target_id = SLT_TARGET_ID[view][scene]
        view_lower = view.lower()

        slt = SLTFile(isp_path)
        temp = [
            item["isp"]["sourceData"]
            for item in slt
            if (
                "scanpos" in item["isp"]["sourceData"]["data"]
                and item["isp"]["sourceData"]["header"]["TARGET_ID"] == target_id
            )
        ]
        nb_scans = len(temp)
        nb_pixels = len(temp[0]["data"]["scanpos"]["array"])

        output = {
            "view": view,
            "scene": scene,
            "nb_scans": nb_scans,
            "nb_pixels": nb_pixels,
        }

        # read scan positions
        output["scanpos"] = np.zeros((nb_scans, nb_pixels), dtype="int32")
        for idx, scan in enumerate(temp):
            output["scanpos"][idx] = [item[view_lower] for item in scan["data"]["scanpos"]["array"]]

        output["target_first_acq"] = np.array([scan["header"]["TARGET_FIRST_ACQ"] for scan in temp], dtype="int32")

        return output

    @staticmethod
    def encoder_to_scan_angles(dataset: dict, anc_file: str):
        """
        Convert scan encoder position to angles using LUT

        :param dict dataset: dict generated by self.slstr_scanpos()
        :param str anc_file: path to SLSTR ancilary file (ANC)
        """
        assert "view" in dataset
        assert "scanpos" in dataset
        view = dataset["view"]
        assert view in ["NAD", "OBL"]

        # prepare "encoder to angle" LUT
        with netCDF4.Dataset(anc_file) as anc:
            if view == "NAD":
                lut_encoder = np.array(anc["ISP_mirror_angles_encoder_LUTs"]["nadir_scan_mirror_encoded_angles"])
                lut_angles = np.array(anc["ISP_mirror_angles_encoder_LUTs"]["nadir_scan_mirror_angles"])
            else:
                lut_encoder = np.array(anc["ISP_mirror_angles_encoder_LUTs"]["oblique_scan_mirror_encoded_angles"])
                lut_angles = np.array(anc["ISP_mirror_angles_encoder_LUTs"]["oblique_scan_mirror_angles"])

        ext_lut_encoder, ext_lut_angles = extend_circular_lut(lut_encoder, lut_angles, end=0x100000)
        unw_lut_angles = np.unwrap(ext_lut_angles, period=360.0)

        # Compute mid-acquisition encoder values:
        #   - unwrap encoder values to avoid discontinuites
        start_pos = np.unwrap(dataset["scanpos"], period=0x100000)

        #   - position at acquisition end
        end_pos = np.zeros(start_pos.shape, dtype=start_pos.dtype)
        end_pos[:, :-1] = start_pos[:, 1:]
        #   - fix last column
        end_pos[:, -1] = 2 * start_pos[:, -1] - start_pos[:, -2]

        #   - mid position for 1km pixels
        mid_pos = ((start_pos + end_pos) // 2) % 0x100000
        dataset["scan_angles_1km"] = np.interp(mid_pos, ext_lut_encoder, unw_lut_angles)

        #   - mid position for 0.5km pixels
        mid_pos = np.zeros((start_pos.shape[0], 2 * start_pos.shape[1]), dtype=start_pos.dtype)
        mid_pos[:, ::2] = ((3 * start_pos + end_pos) // 4) % 0x100000
        mid_pos[:, 1::2] = ((start_pos + 3 * end_pos) // 4) % 0x100000
        dataset["scan_angles_05km"] = np.interp(mid_pos, ext_lut_encoder, unw_lut_angles)

    @staticmethod
    def olci_pointing_angles(calibration_file: str) -> dict:
        """
        Compute the pointing angles (azimuth, elevation) in instrument frame for each camera

        :param str calibration_file: Calibration file (netCDF format)
        :return: dict with the tables "pixel_pointing_vectors_IF/X" and
                 "pixel_pointing_vectors_IF/Y" as numpy array
        """
        # - compute 'los_az' and 'los_el' from coordinates (O1-GR_1-12, O1-GR_1-13, O1-GR_1-14)
        with netCDF4.Dataset(calibration_file) as cal_dataset:
            output = {}
            S3LegacyDriver.read_netcdf_array_fields(
                cal_dataset["pixel_pointing_vectors_IF"],
                output,
                ["X", "Y"],
            )
        return output

    @staticmethod
    def s3_thermoelastic_tables(calibration_file: str, group: str | None = None) -> dict:
        """
        Extract thermoelastic tables

        :param str calibration_file: Calibration file (netCDF format)
        :param str|None group: name of the group containing thermoelastic model
        :return: dict with tables "julian_days", "quaternions_1", "quaternions_2", "quaternions_3",
                 "quaternions_4", "on_orbit_positions_angle"
        """
        with netCDF4.Dataset(calibration_file) as cal_dataset:
            if group:
                dataset = cal_dataset[group]
            else:
                dataset = cal_dataset

            output = {}
            S3LegacyDriver.read_netcdf_array_fields(
                dataset,
                output,
                [
                    "julian_days",
                    "quaternions_1",
                    "quaternions_2",
                    "quaternions_3",
                    "quaternions_4",
                    "on_orbit_positions_angle",
                ],
            )

        return output

    @staticmethod
    def slstr_geometry_model(geometry_model_file: str) -> dict:
        """
        Extract the geometry model for SLSTR

        :param str geometry_model_file: Path to geometry model file (netCDF format)
        :return: dict with geometric parameters and tables
        """
        output = {}
        array_fields = ["scans_mirror_offset", "scans_cone_angle"]
        for angle in ["lambda", "mu", "nu"]:
            for band in ["1km", "F1", "500m"]:
                for suffix in ["", "_OB"]:
                    array_fields.append("cos_" + angle + "_centre_" + band + suffix)

        with netCDF4.Dataset(geometry_model_file) as geom_dataset:
            S3LegacyDriver.read_netcdf_array_fields(geom_dataset, output, array_fields)

            float_fields = ["F1_scanangle_offset", "scans_inclination_nadir"]
            for axis in ["X", "Y", "Z"]:
                for suffix in ["", "_OB"]:
                    float_fields.append(axis + "_misalignment_correction" + suffix)
            S3LegacyDriver.read_netcdf_float_fields(geom_dataset, output, float_fields)

        return output
