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
Drivers for Sentinel1 legacy products
"""

from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Tuple

import numpy as np
from drivers.explorer_legacy import ExplorerDriver

from asgard.core.time import JD_TO_SECONDS, TimeRef
from asgard.wrappers.dfdl.s1_ancillary import File as S1AncillaryFile
from asgard.wrappers.dfdl.s1_raw import File as S1RawFile

if TYPE_CHECKING:
    import dask


class S1LegacyDriver(ExplorerDriver):
    """
    Driver for Sentinel 1 legacy product
    """

    def read_sub_commutated_data(self, isp_path: str, abs_orbit: int = 0) -> Tuple[dict, dict]:
        """
        Extract sub-commutated data from ISP data

        :param str isp_path: Path to ISP binary file
        :param int abs_orbit: Number of absolute orbit at the start of ISP data
        :return: tuple with extracted orbit and attitude (see schemas ORBIT_STATE_VECTORS_SCHEMA and ATTITUDE_SCHEMA)
        """

        raw = S1RawFile(isp_path)

        data = [item["isp"]["secondaryHeader"]["subcommutatedAncillary"] for item in raw]

        # search for consecutive sequence of 64 elements
        bytes_sequence = []
        current_bytes = b""
        current_index = 0
        is_valid = False
        for item in data:
            if not is_valid:
                if item["wordIndex"] == 1:
                    is_valid = True
                    current_bytes = b""
                    current_index = 0
                else:
                    continue

            # check current index and add word to bytes
            current_index += 1
            if current_index != item["wordIndex"]:
                # incomplete sequence, drop it
                is_valid = False
                continue
            current_bytes += bytes.fromhex(item["word"])
            # record the sequence when reaching last element
            if current_index == 64:
                bytes_sequence.append(current_bytes)
                is_valid = False

        # write to temporary file
        with NamedTemporaryFile() as tmp_file:
            for bloc in bytes_sequence:
                tmp_file.write(bloc)

            # Parse with an other DFDL schema
            orbit, attitude = self.parse_ancillary_data(tmp_file.name)

            # close temporary file
            tmp_file.close()

        # compute UTC timestamps for start and stop
        orbit["start_date"] = "UTC=" + self.time_reference.to_str(
            orbit["times"]["GPS"]["offsets"][0],
            fmt="CCSDSA",
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
        )
        orbit["stop_date"] = "UTC=" + self.time_reference.to_str(
            orbit["times"]["GPS"]["offsets"][-1],
            fmt="CCSDSA",
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
        )
        attitude["start_date"] = "UTC=" + self.time_reference.to_str(
            attitude["times"]["GPS"]["offsets"][0],
            fmt="CCSDSA",
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
        )
        attitude["stop_date"] = "UTC=" + self.time_reference.to_str(
            attitude["times"]["GPS"]["offsets"][-1],
            fmt="CCSDSA",
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
        )

        # fill other timescales in orbit
        self.fill_other_timescales(orbit["times"])

        # complete the orbit object with a propagation of orbit numbers
        orbit["absolute_orbit"] = self.propagate_orbit_number(orbit["positions"], abs_orbit)

        return orbit, attitude

    def parse_ancillary_data(self, path: str) -> Tuple[dict, dict]:
        """
        Parse the ancillary binary data extracted from ISP secondary headers (sub-commutated)

        :param str path: Path to binary data file
        :return: tuple with orbit and attitude data
        """

        positions = []
        velocities = []
        times_gps = []
        prev_time_cuc = [0, 0]
        quaternions = []
        angular_rates = []
        att_times_gps = []
        prev_att_time_cuc = [0, 0]

        # Parse with an other DFDL schema
        ancillary_parser = S1AncillaryFile(path)
        for item in ancillary_parser:
            # check PVT time
            pvt_time = [
                item["ancillary"]["PVT_GPS_TIME"]["coarse"],
                item["ancillary"]["PVT_GPS_TIME"]["fine"],
            ]
            if pvt_time != prev_time_cuc:
                prev_time_cuc = pvt_time
                times_gps.append(pvt_time)
                positions.append(
                    [
                        item["ancillary"]["POS_X"],
                        item["ancillary"]["POS_Y"],
                        item["ancillary"]["POS_Z"],
                    ]
                )
                velocities.append(
                    [
                        item["ancillary"]["VEL_X"],
                        item["ancillary"]["VEL_Y"],
                        item["ancillary"]["VEL_Z"],
                    ]
                )

            # check attitude time
            att_time = [
                item["ancillary"]["ATT_GPS_TIME"]["coarse"],
                item["ancillary"]["ATT_GPS_TIME"]["fine"],
            ]
            if att_time != prev_att_time_cuc:
                prev_att_time_cuc = att_time
                att_times_gps.append(att_time)
                # quaternions recorded in scalar last convention
                quaternions.append(
                    [
                        item["ancillary"]["ATT_Q1"],
                        item["ancillary"]["ATT_Q2"],
                        item["ancillary"]["ATT_Q3"],
                        item["ancillary"]["ATT_Q0"],
                    ]
                )
                angular_rates.append(
                    [
                        item["ancillary"]["SC_RATE_WX"],
                        item["ancillary"]["SC_RATE_WY"],
                        item["ancillary"]["SC_RATE_WZ"],
                    ]
                )
        # close parser
        ancillary_parser = None

        orbit = {
            "times": {
                "GPS": {
                    "offsets": self.time_reference.from_cuc(np.array(times_gps, dtype="int64")),
                    "ref": "GPS",
                },
            },
            "positions": np.array(positions),
            "velocities": np.array(velocities),
            "frame": "EF",
            "time_ref": "GPS",
        }

        att_times = self.time_reference.from_cuc(np.array(att_times_gps, dtype="int64"))
        max_gap = np.max(np.diff(att_times)) * JD_TO_SECONDS

        attitude = {
            "times": {
                "GPS": {
                    "offsets": att_times,
                    "ref": "GPS",
                },
            },
            "quaternions": np.array(quaternions),
            "angular_rates": np.array(angular_rates),
            "frame": "EME2000",
            "time_ref": "GPS",
            "max_gap": max_gap,
        }

        return orbit, attitude

    @staticmethod
    def propagate_orbit_number(positions: np.ndarray, orbit_number: int) -> np.ndarray:
        """
        Propagate an initial orbit number through a series of orbital positions. The orbit
        number is incremented each time the orbital position crosses the Z=0 plane upwards.

        :param np.ndarray positions: Array of orbital positions (cartesian, shape (N,3))
        :param int orbit_number: Initial orbit number
        :return: Array of orbit numbers propagated
        """

        # detect crossing of Z=0 plane upwards
        crossing = (positions[:-1, 2] < 0.0) * (positions[1:, 2] > 0.0)
        # propagate orbit number
        output = np.concatenate([np.array([orbit_number], dtype=np.int32), orbit_number + np.cumsum(crossing)]).astype(
            np.int32
        )

        return output

    @staticmethod
    def propagate_orbit_number_dask(positions: "dask.array", orbit_number: int) -> "dask.array":
        """
        Dask version of the propagate_orbit_number
        Propagate an initial orbit number through a series of orbital positions. The orbit
        number is incremented each time the orbital position crosses the Z=0 plane upwards.

        Since the algorithm is purely sequential the speedup using Dask is bad and closer to 0.
        It spread the results on the workers RAM, allowing bigger datasets for the cost of
        network transfers.

        :param dask.array positions: Array of orbital positions (cartesian, shape (N,3))
        :param int orbit_number: Initial orbit number
        :return: lazy dask array of orbit numbers propagated
        :raises:
            Import error if dask is not installed
        """
        import dask.array as da

        # detect crossing of Z=0 plane upwards
        crossing = (positions[:-1, 2] < 0.0) * (positions[1:, 2] > 0.0)

        # propagate orbit number
        output = da.concatenate([da.array([orbit_number], dtype=np.int32), orbit_number + da.cumsum(crossing)]).astype(
            np.int32
        )

        return output

    def get_swath_name(self, tree) -> str:
        """
        Read the swath name from a parsed annotation XML file

        :param tree: XML tree
        :return: swath name
        """
        root = tree.getroot()
        name = root.find("adsHeader/swath").text
        if name.startswith("WV"):
            # add the image number to differentiate the WV patches
            name += "/" + root.find("adsHeader/imageNumber").text

        return name

    def get_swath(self, tree, epoch: str = None) -> dict:
        """
        Read the swath times definition from a parsed annotation XML file

        :param tree: XML tree
        :param epoch: Reference epoch as string to use when encoding azimuth datetimes (if None, anchorTime is used)
        :return: dict with swath time definitions
        """
        root = tree.getroot()

        # detect reference anchor date, and trim second
        if epoch is None:
            anchor_time = root.find("imageAnnotation/imageInformation/anchorTime").text
            anchor_time = anchor_time[:17] + "00"
        else:
            anchor_time = epoch

        swath = {}
        # parse time parameters
        azimuth_times = []
        burst_count = int(root.find("swathTiming/burstList").get("count"))
        if burst_count == 0:
            # image dimensions
            lines = int(root.find("imageAnnotation/imageInformation/numberOfLines").text)
            samples = int(root.find("imageAnnotation/imageInformation/numberOfSamples").text)
            # record a single "burst"
            time_ascii = root.find("imageAnnotation/imageInformation/productFirstLineUtcTime").text
            azimuth_times.append(self.time_reference.from_str(time_ascii, unit="s", epoch=anchor_time))
        else:
            # burst dimensions
            lines = int(root.find("swathTiming/linesPerBurst").text)
            samples = int(root.find("swathTiming/samplesPerBurst").text)
            # record all burst start times
            for burst_azimuth_node in root.iterfind("swathTiming/burstList/burst/azimuthTime"):
                azimuth_times.append(self.time_reference.from_str(burst_azimuth_node.text, unit="s", epoch=anchor_time))

        swath["azimuth_times"] = {
            "offsets": np.array(azimuth_times, dtype="float64"),
            "unit": "s",
            "epoch": anchor_time,
            "ref": "UTC",
        }

        swath["azimuth_convention"] = "ZD"
        swath["azimuth_time_interval"] = float(root.find("imageAnnotation/imageInformation/azimuthTimeInterval").text)
        swath["slant_range_time"] = float(root.find("imageAnnotation/imageInformation/slantRangeTime").text)
        swath["range_sampling_rate"] = float(root.find("generalAnnotation/productInformation/rangeSamplingRate").text)
        swath["burst_lines"] = lines
        swath["burst_samples"] = samples
        return swath

    def get_geolocation(self, tree, epoch: str = None) -> dict:
        """
        Extract the geolocation table from parsed annotation XML file

        :param tree: XML tree
        :param epoch: Reference epoch as string to use when encoding azimuth datetimes (if None, anchorTime is used)
        :return: dict with swath geolocation table
        """

        root = tree.getroot()

        # detect reference anchor date, and trim second
        if epoch is None:
            anchor_time = root.find("imageAnnotation/imageInformation/anchorTime").text
            anchor_time = anchor_time[:17] + "00"
        else:
            anchor_time = epoch

        count = int(root.find("geolocationGrid/geolocationGridPointList").get("count"))
        image = np.full((count, 2), np.nan, dtype="int32")
        ground = np.full((count, 3), np.nan, dtype="float64")
        azimuth_time = np.full((count,), np.nan, dtype="float64")
        range_time = np.full((count,), np.nan, dtype="float64")
        incidence = np.full((count,), np.nan, dtype="float64")
        elevation = np.full((count,), np.nan, dtype="float64")

        for idx, geoloc_node in enumerate(
            root.iterfind("geolocationGrid/geolocationGridPointList/geolocationGridPoint")
        ):
            image[idx] = [int(geoloc_node.find("pixel").text), int(geoloc_node.find("line").text)]
            ground[idx] = [
                float(geoloc_node.find("longitude").text),
                float(geoloc_node.find("latitude").text),
                float(geoloc_node.find("height").text),
            ]
            azimuth_time[idx] = self.time_reference.from_str(
                geoloc_node.find("azimuthTime").text, unit="s", epoch=anchor_time
            )
            range_time[idx] = float(geoloc_node.find("slantRangeTime").text)
            incidence[idx] = float(geoloc_node.find("incidenceAngle").text)
            elevation[idx] = float(geoloc_node.find("elevationAngle").text)

        geolocation = {
            "image": image,
            "ground": ground,
            "azimuth_time": {
                "offsets": azimuth_time,
                "unit": "s",
                "epoch": anchor_time,
                "ref": "UTC",
            },
            "range_time": range_time,
            "incidence_angle": incidence,
            "elevation_angle": elevation,
        }

        return geolocation

    def get_terrain_height(self, tree, epoch: str = None) -> dict:
        """
        Extract the terrain height table from parsed annotation XML file

        :param tree: XML tree
        :param epoch: Reference epoch as string to use when encoding azimuth datetimes (if None, anchorTime is used)
        :return: dict with terrain height
        """

        root = tree.getroot()

        # detect reference anchor date, and trim second
        if epoch is None:
            anchor_time = root.find("imageAnnotation/imageInformation/anchorTime").text
            anchor_time = anchor_time[:17] + "00"
        else:
            anchor_time = epoch

        count = int(root.find("generalAnnotation/terrainHeightList").get("count"))
        azimuth_time = np.full((count,), np.nan, dtype="float64")
        height = np.full((count,), np.nan, dtype="float64")

        for idx, node in enumerate(root.iterfind("generalAnnotation/terrainHeightList/terrainHeight")):
            height[idx] = float(node.find("value").text)
            azimuth_time[idx] = self.time_reference.from_str(node.find("azimuthTime").text, unit="s", epoch=anchor_time)

        return {
            "azimuth": {
                "offsets": azimuth_time,
                "unit": "s",
                "epoch": anchor_time,
                "ref": "UTC",
            },
            "height": height,
        }

    def get_attitude(self, tree, epoch: str = None) -> dict:
        """
        Read attitude from annotation

        :param tree: XML tree
        :param epoch: Reference epoch as string to use when encoding azimuth datetimes (if None, anchorTime is used)
        :return: dict with attitude data
        """

        root = tree.getroot()

        # detect reference anchor date, and trim second
        if epoch is None:
            anchor_time = root.find("imageAnnotation/imageInformation/anchorTime").text
            anchor_time = anchor_time[:17] + "00"
        else:
            anchor_time = epoch

        count = int(root.find("generalAnnotation/attitudeList").get("count"))
        time = np.full((count,), np.nan, dtype="float64")
        quaternion = np.full((count, 4), np.nan, dtype="float64")
        angular_rates = np.full((count, 3), np.nan, dtype="float64")
        platform_angles = np.full((count, 3), np.nan, dtype="float64")
        for idx, node in enumerate(root.iterfind("generalAnnotation/attitudeList/attitude")):
            time[idx] = self.time_reference.from_str(node.find("time").text, unit="s", epoch=anchor_time)
            quaternion[idx] = [
                float(node.find("q0").text),
                float(node.find("q1").text),
                float(node.find("q2").text),
                float(node.find("q3").text),
            ]
            angular_rates[idx] = [
                float(node.find("wx").text),
                float(node.find("wy").text),
                float(node.find("wz").text),
            ]
            platform_angles[idx] = [
                float(node.find("roll").text),
                float(node.find("pitch").text),
                float(node.find("yaw").text),
            ]

        return {
            "times": {
                "UTC": {
                    "offsets": time,
                    "unit": "s",
                    "epoch": anchor_time,
                    "ref": "UTC",
                },
            },
            "time_ref": "UTC",
            "frame": "EME2000",
            "quaternions": quaternion,
            "angular_rates": angular_rates,
            "platform_angles": platform_angles,
        }

    def get_antenna_pattern(self, tree, epoch: str = None) -> dict:
        """
        Read antenna pattern from annotation

        :param tree: XML tree
        :param epoch: Reference epoch as string to use when encoding azimuth datetimes (if None, anchorTime is used)
        :return: dict with antenna pattern
        """

        root = tree.getroot()

        # detect reference anchor date, and trim second
        if epoch is None:
            anchor_time = root.find("imageAnnotation/imageInformation/anchorTime").text
            anchor_time = anchor_time[:17] + "00"
        else:
            anchor_time = epoch

        count = int(root.find("antennaPattern/antennaPatternList").get("count"))
        azimuth_times = np.full((count,), np.nan, dtype="float64")
        slant_range_time = []
        elevation_angle = []
        elevation_pattern = []
        incidence_angle = []
        terrain_height = np.full((count,), np.nan, dtype="float64")
        roll = np.full((count,), np.nan, dtype="float64")
        for idx, node in enumerate(root.iterfind("antennaPattern/antennaPatternList/antennaPattern")):
            azimuth_times[idx] = self.time_reference.from_str(
                node.find("azimuthTime").text, unit="s", epoch=anchor_time
            )
            terrain_height[idx] = float(node.find("terrainHeight").text)
            roll[idx] = float(node.find("roll").text)

            slant_range_time.append([float(val) for val in node.find("slantRangeTime").text.split(" ")])
            elevation_angle.append([float(val) for val in node.find("elevationAngle").text.split(" ")])
            elevation_pattern.append([float(val) for val in node.find("elevationPattern").text.split(" ")])
            incidence_angle.append([float(val) for val in node.find("incidenceAngle").text.split(" ")])

        return {
            "azimuth_time": {
                "offsets": azimuth_times,
                "unit": "s",
                "epoch": anchor_time,
                "ref": "UTC",
            },
            "terrain_height": terrain_height,
            "roll": roll,
            "slant_range_time": np.array(slant_range_time, dtype="float64"),
            "elevation_angle": np.array(elevation_angle, dtype="float64"),
            "elevation_pattern": np.array(elevation_pattern, dtype="float64").view(np.complex128),
            "incidence_angle": np.array(incidence_angle, dtype="float64"),
        }
