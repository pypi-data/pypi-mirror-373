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
Drivers for EOCFI based formats
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List

import netCDF4
import numpy as np
from drivers.xml_util import XmlUtil
from scipy.spatial.transform import Rotation as R

from asgard.core.frame import FrameId
from asgard.core.schema import TIMESCALE_ARRAY_SCHEMA, validate_or_throw
from asgard.models.body import EarthBody
from asgard.models.time import DEFAULT_EPOCH, DEFAULT_UNIT, TimeRef, TimeReference

DELTA_GPS_TAI = 19 / 86400.0


FRAME_MAP_ASGARD = {"GEO_MEAN_2000": "EME2000", "GM2000": "EME2000", "EARTH_FIXED": "EF"}

FRAME_MAP = {
    FrameId.GCRF: "GEO_MEAN_2000",
    FrameId.EME2000: "GEO_MEAN_2000",
    FrameId.EF: "EARTH_FIXED",
    FrameId.MOD: "MEAN_DATE",
    FrameId.TOD: "TRUE_DATE",
}


def load_header(path: str) -> dict:
    """
    Load header informations from XML file

    :param str path: path to the orbit/attitude xml file
    :return: dict containing header info
    """
    root = XmlUtil.read_with_objectify(path, remove_namespaces=True)
    validity = root.xpath("//Validity_Period")[0]
    source = root.xpath("//Source")[0]

    output = {
        "file_description": root.xpath("//File_Description")[0].text,
        "mission": root.xpath("//Mission")[0].text,
        "file_class": root.xpath("//File_Class")[0].text,
        "file_type": root.xpath("//File_Type")[0].text,
        "version": root.xpath("//File_Version")[0].pyval,
        "val_start_date": validity.Validity_Start.text,
        "val_stop_date": validity.Validity_Stop.text,
        "system": source.System.text,
        "creator": source.Creator.text,
        "creator_version": source.Creator_Version.text,
        "creation_date": source.Creation_Date.text,
    }

    return output


def populate_element_from_dict(element, data):
    """
    Fill xml file by recursive function
    """
    for key, value in data.items():
        if isinstance(value, dict):
            # Recursive call for nested dictionaries
            sub_element = ET.SubElement(element, key)
            populate_element_from_dict(sub_element, value)
        else:
            sub_element = ET.SubElement(element, key)
            if key in ["X", "Y", "Z"]:
                # Add the unit attribute for X, Y, and Z
                sub_element.set("unit", "m")
            elif key in ["VX", "VY", "VZ"]:
                sub_element.set("unit", "m/s")
            elif key in ["Time"]:
                if value[:3] in ["TAI", "GPS", "UTC", "UT1"]:
                    sub_element.set("ref", value[:3])
                else:
                    sub_element.set("ref", "UTC")
            sub_element.text = str(value)


class ExplorerDriver:
    """
    Explorer driver, handles EOCFI formats
    """

    def __init__(
        self,
        earth_body: EarthBody | None = None,
    ):
        """
        Constructor

        :param EarthBody|None earth_body: EarthBody instance, to convert coordinates
            between frames and compute geodetic distance using Orekit library
        """
        self.earth_body = earth_body if earth_body else EarthBody()
        self.time_reference = self.earth_body.time_reference_model

    @staticmethod
    def read_iers_file(path: str) -> List[str]:
        """
        Read an IERS bulletin file. For now, we simply read all the file as a list of strings

        :param str path: Path to an IERS bulletin file
        :return: List of lines in the file
        """
        with open(path, "r", encoding="utf-8") as input_fd:
            iers_data = input_fd.readlines()
        return iers_data

    @staticmethod
    def read_orbit_file(path) -> dict:
        """
        Read orbit file

        :param path: Path to an orbit file
        :return: dict of orbit info
        """
        header = load_header(path)

        root = XmlUtil.read_with_objectify(path, remove_namespaces=True)

        frame = root.xpath("//Ref_Frame")[0].text

        time_ref = root.xpath("//Time_Reference")[0].text

        positions, velocities, absolute_orbit, tai, utc, ut1, gps = ([] for i in range(7))

        tr = TimeReference()
        for osv in root.xpath("//OSV"):
            positions.append([osv.X.pyval, osv.Y.pyval, osv.Z.pyval])
            velocities.append([osv.VX.pyval, osv.VY.pyval, osv.VZ.pyval])
            absolute_orbit.append(osv.Absolute_Orbit.pyval)
            tai.append(tr.from_str(osv.TAI.text, fmt="CCSDSA_MICROSEC"))
            utc.append(tr.from_str(osv.UTC.text, fmt="CCSDSA_MICROSEC"))
            ut1.append(tr.from_str(osv.UT1.text, fmt="CCSDSA_MICROSEC"))
            gps.append(tai[-1] - DELTA_GPS_TAI)

        orbit = {
            "time_tai": np.array(tai),
            "time_utc": np.array(utc),
            "time_ut1": np.array(ut1),
            "time_gps": np.array(gps),
            "positions": np.array(positions),
            "velocities": np.array(velocities),
            "absolute_orbit": np.array(absolute_orbit, dtype="int32"),
            "frame": frame,
            "time_ref": time_ref,
        }

        return {
            "times": {
                "TAI": {
                    "epoch": DEFAULT_EPOCH,
                    "unit": DEFAULT_UNIT,
                    "offsets": orbit["time_tai"],
                    "ref": "TAI",
                },
                "GPS": {
                    "epoch": DEFAULT_EPOCH,
                    "unit": DEFAULT_UNIT,
                    "offsets": orbit["time_gps"],
                    "ref": "GPS",
                },
                "UTC": {
                    "epoch": DEFAULT_EPOCH,
                    "unit": DEFAULT_UNIT,
                    "offsets": orbit["time_utc"],
                    "ref": "UTC",
                },
                "UT1": {
                    "epoch": DEFAULT_EPOCH,
                    "unit": DEFAULT_UNIT,
                    "offsets": orbit["time_ut1"],
                    "ref": "UT1",
                },
            },
            "positions": orbit["positions"],
            "velocities": orbit["velocities"],
            "absolute_orbit": orbit["absolute_orbit"],
            "frame": FRAME_MAP_ASGARD[orbit["frame"]],
            "time_ref": orbit["time_ref"],
            "start_date": header["val_start_date"],
            "stop_date": header["val_stop_date"],
        }

    @staticmethod
    def read_orbit_scenario_file(file_path):
        """
        Read an orbit scenario file (OSF)

        :param path: Path to an orbit scenario file
        :return: dict of orbit scenario file info
        """
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Define the namespace
        name_space = {"cfi": "http://eop-cfi.esa.int/CFI"}

        # Initialize lists to store extracted data
        orbit_data = {"Absolute_Orbit": [], "Relative_Orbit": [], "Cycle_Number": [], "Phase_Number": []}
        cycle_data = {"Repeat_Cycle": [], "Cycle_Length": [], "ANX_Longitude": [], "MLST": [], "MLST_Drift": []}
        time_of_anx_data = {"TAI": [], "UTC": [], "UT1": []}

        # Iterate through each Orbit_Change section
        for orbit_change in root.findall(".//cfi:Orbit_Change", name_space):
            # Extract Orbit data
            orbit = orbit_change.find("cfi:Orbit", name_space)
            orbit_data["Absolute_Orbit"].append(int(orbit.find("cfi:Absolute_Orbit", name_space).text))
            orbit_data["Relative_Orbit"].append(int(orbit.find("cfi:Relative_Orbit", name_space).text))
            orbit_data["Cycle_Number"].append(int(orbit.find("cfi:Cycle_Number", name_space).text))
            orbit_data["Phase_Number"].append(int(orbit.find("cfi:Phase_Number", name_space).text))

            # Extract Cycle data
            cycle = orbit_change.find("cfi:Cycle", name_space)
            cycle_data["Repeat_Cycle"].append(float(cycle.find("cfi:Repeat_Cycle", name_space).text))
            cycle_data["Cycle_Length"].append(float(cycle.find("cfi:Cycle_Length", name_space).text))
            cycle_data["ANX_Longitude"].append(float(cycle.find("cfi:ANX_Longitude", name_space).text))
            cycle_data["MLST"].append(cycle.find("cfi:MLST", name_space).text)
            cycle_data["MLST_Drift"].append(float(cycle.find("cfi:MLST_Drift", name_space).text))

            tr = TimeReference()
            # Extract Time_of_ANX data
            time_of_anx = orbit_change.find("cfi:Time_of_ANX", name_space)
            time_of_anx_data["TAI"].append(
                tr.from_str(time_of_anx.find("cfi:TAI", name_space).text, fmt="CCSDSA_MICROSEC")
            )
            time_of_anx_data["UTC"].append(
                tr.from_str(time_of_anx.find("cfi:UTC", name_space).text, fmt="CCSDSA_MICROSEC")
            )
            time_of_anx_data["UT1"].append(
                tr.from_str(time_of_anx.find("cfi:UT1", name_space).text, fmt="CCSDSA_MICROSEC")
            )

        # Convert lists to numpy arrays
        orbit_data = {key: np.array(value) for key, value in orbit_data.items()}
        cycle_data = {key: np.array(value) for key, value in cycle_data.items()}
        time_of_anx_data = {key: np.array(value) for key, value in time_of_anx_data.items()}
        time_of_anx_data["epoch"] = DEFAULT_EPOCH
        time_of_anx_data["unit"] = DEFAULT_UNIT
        validity_dict = {
            "Ref": root.find(".//cfi:Validity_Start", name_space).text[:3],
            "Validity_Start": root.find(".//cfi:Validity_Start", name_space).text[4:],
            "Validity_Stop": root.find(".//cfi:Validity_Stop", name_space).text[4:],
        }
        return {"orbit": orbit_data, "cycle": cycle_data, "anx_time": time_of_anx_data, "validity": validity_dict}

    @staticmethod
    def read_attitude_file(path) -> dict:
        """
        Read attitude file

        :param path: Path to an attitude file
        :return: dict of attitude info
        """
        header = load_header(path)

        tr = TimeReference()
        root = XmlUtil.read_with_objectify(path, remove_namespaces=True)

        max_gap = root.xpath("//Max_Gap")[0].pyval
        frame = root.xpath("//Reference_Frame")[0].text
        validity = root.xpath("//Validity_Period")[0]
        start_date = validity.Validity_Start.text
        stop_date = validity.Validity_Stop.text
        time_ref = root.xpath("//Quaternions")[0].Time.attrib["ref"]

        quaternions = []
        time_data = []
        for quat_elem in root.xpath("//Quaternions"):
            quaternions.append([quat_elem.Q1.pyval, quat_elem.Q2.pyval, quat_elem.Q3.pyval, quat_elem.Q4.pyval])
            time_elem = quat_elem.Time.text
            time_data.append(tr.from_str(time_elem, fmt="CCSDSA_MICROSEC"))

        attitude = {
            "times": np.array(time_data),
            "quaternions": np.array(quaternions, dtype=np.float64),
            "frame": frame,
            "time_ref": time_ref,
            "max_gap": max_gap,
            "start_date": start_date,
            "stop_date": stop_date,
        }

        return {
            "times": {
                time_ref: {
                    "epoch": DEFAULT_EPOCH,
                    "unit": DEFAULT_UNIT,
                    "offsets": attitude["times"],
                },
            },
            "quaternions": attitude["quaternions"],
            "frame": FRAME_MAP_ASGARD[attitude["frame"]],
            "time_ref": time_ref,
            "max_gap": attitude["max_gap"],
            "start_date": header["val_start_date"],
            "stop_date": header["val_stop_date"],
        }

    @staticmethod
    def read_netcdf_array_fields(source: netCDF4.Dataset, output: dict, fields: List[str]):
        """
        Read a list of fields into an output dict. Each field is converted to a np.array

        :param netCDF4.Dataset source: Source netCDF dataset
        :param dict output:            Output dict
        :param List[str] fields:       List of field names
        """
        for field in fields:
            output[field] = (
                np.array(source[field])
                if source[field].dtype != np.float32
                else np.array(source[field]).astype(np.float64)
            )

    @staticmethod
    def read_netcdf_float_fields(source: netCDF4.Dataset, output: dict, fields: List[str]):
        """
        Read a list of fields into an output dict. Each field is converted to a float

        :param netCDF4.Dataset source: Source netCDF dataset
        :param dict output:            Output dict
        :param List[str] fields:       List of field names
        """

        for field in fields:
            output[field] = float(source[field][...])

    @staticmethod
    def write_orbit_file(orbit: dict, path: str, mission: str = "SENTINEL-3"):  # pylint: disable=too-many-locals
        """
        Write an orbit file corresponding to an orbit object.

        :param dict orbit: Orbit object (see ORBIT_STATE_VECTORS_SCHEMA)
        :param str path: Output file path
        :param str mission: Mission name
        """

        header = {
            "mission": mission,
            "creator": "ASGARD",
        }
        if "start_date" in orbit:
            header["val_start_date"] = orbit["start_date"]
        if "stop_date" in orbit:
            header["val_stop_date"] = orbit["stop_date"]

        # Create the root element
        root = ET.Element(
            "Earth_Observation_File",
            attrib={
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xmlns": "http://eop-cfi.esa.int/CFI",
                "xsi:schemaLocation": "http://eop-cfi.esa.int/CFI ",
            },
        )

        # Create the Earth_Observation_Header element
        earth_observation_header = ET.SubElement(root, "Earth_Observation_Header")

        # Create the Fixed_Header element
        fixed_header = ET.SubElement(earth_observation_header, "Fixed_Header")

        # Add child elements to <Fixed_Header>
        file_name = ET.SubElement(fixed_header, "File_Name")
        file_name.text = "sample_orbit"

        file_description = ET.SubElement(fixed_header, "File_Description")
        file_description.text = header.get("file_description", "SCRATCH ORBIT FILE FROM NAVATT")

        ET.SubElement(fixed_header, "Notes")

        mission_elt = ET.SubElement(fixed_header, "Mission")
        mission_elt.text = header.get("mission", "SENTINEL-3")

        file_class = ET.SubElement(fixed_header, "File_Class")
        file_class.text = header.get("file_class", "OPER")

        file_type = ET.SubElement(fixed_header, "File_Type")
        file_type.text = header.get("file_type", "NAVATT_ORB")

        # Validity_Period
        validity_period = ET.SubElement(fixed_header, "Validity_Period")
        validity_start = ET.SubElement(validity_period, "Validity_Start")
        validity_start.text = header.get("val_start_date", "missing")

        validity_stop = ET.SubElement(validity_period, "Validity_Stop")
        validity_stop.text = header.get("val_stop_date", "missing")

        file_version = ET.SubElement(fixed_header, "File_Version")
        file_version.text = "0001"

        eoffs_version = ET.SubElement(fixed_header, "EOFFS_Version")
        eoffs_version.text = "3.0"

        # Source
        source = ET.SubElement(fixed_header, "Source")
        system = ET.SubElement(source, "System")
        system.text = header.get("system", "SENTINEL-3 L1 IPF")

        creator = ET.SubElement(source, "Creator")
        creator.text = header.get("creator", "OLCI L1B EO")

        creator_version = ET.SubElement(source, "Creator_Version")
        creator_version.text = header.get("creator_version", "-")

        creation_date = ET.SubElement(source, "Creation_Date")
        creation_date.text = datetime.now().strftime("UTC=%Y-%m-%dT%H:%M:%S")

        # Create the Variable_Header element
        variable_header = ET.SubElement(earth_observation_header, "Variable_Header")
        ref_frame = ET.SubElement(variable_header, "Ref_Frame")
        ref_frame.text = FRAME_MAP[FrameId[orbit.get("frame", "EME2000")]]
        time_reference = ET.SubElement(variable_header, "Time_Reference")
        time_reference.text = orbit.get("time_ref", "TAI").replace("GPS", "TAI")

        # Create the Data_Block element
        data_block = ET.SubElement(root, "Data_Block", type="xml")
        list_of_osvs = ET.SubElement(data_block, "List_of_OSVs", count=str(len(orbit["positions"])))

        tr = TimeReference()
        # # Populate List_of_OSVs with OSV elements
        for i in range(len(orbit["positions"])):
            osv = ET.SubElement(list_of_osvs, "OSV")

            tai_str = tr.to_str(orbit["times"]["TAI"]["offsets"][i], fmt="CCSDSA_MICROSEC")
            ut1_str = tr.to_str(orbit["times"]["UT1"]["offsets"][i], fmt="CCSDSA_MICROSEC")
            utc_str = tr.to_str(
                orbit["times"]["TAI"]["offsets"][i],
                fmt="CCSDSA_MICROSEC",
                ref_in=TimeRef.TAI,
                ref_out=TimeRef.UTC,
            )

            # Populate OSV with data from the input dictionary
            osv_data = {
                "TAI": f"TAI={tai_str}",
                "UTC": f"UTC={utc_str}",
                "UT1": f"UT1={ut1_str}",
                "Absolute_Orbit": orbit["absolute_orbit"][i],
                "X": orbit["positions"][i][0],
                "Y": orbit["positions"][i][1],
                "Z": orbit["positions"][i][2],
                "VX": orbit["velocities"][i][0],
                "VY": orbit["velocities"][i][1],
                "VZ": orbit["velocities"][i][2],
                "Quality": "0000000000000",
            }

            populate_element_from_dict(osv, osv_data)

        # Create the XML tree
        tree = ET.ElementTree(root)

        ET.indent(tree)

        # Write the XML tree to a file
        tree.write(path, xml_declaration=True, encoding="utf-8", method="html")

    @staticmethod
    def write_attitude_file(attitude: dict, path: str, mission: str = "SENTINEL-3"):  # pylint: disable=too-many-locals
        """
        Write an attitude file corresponding to an attitude object.

        :param dict attitude: Attitude object (see ATTITUDE_SCHEMA)
        :param str path: Output file path
        :param str mission: Mission name
        """

        header = {
            "mission": mission,
            "creator": "ASGARD",
        }
        if "start_date" in attitude:
            header["val_start_date"] = attitude["start_date"]
        if "stop_date" in attitude:
            header["val_stop_date"] = attitude["stop_date"]

        # Create the root element
        root = ET.Element(
            "Earth_Observation_File",
            attrib={
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xmlns": "http://eop-cfi.esa.int/CFI",
                "xsi:schemaLocation": "http://eop-cfi.esa.int/CFI ",
            },
        )

        # Setup time ref to use:
        target_scale = attitude.get("time_ref", "UTC")
        source_scale = target_scale
        if source_scale == "UTC" and "GPS" in attitude["times"]:
            source_scale = "GPS"
        if source_scale == "UTC" and "TAI" in attitude["times"]:
            source_scale = "TAI"

        # Create the Earth_Observation_Header element
        earth_observation_header = ET.SubElement(root, "Earth_Observation_Header")

        # Create the Fixed_Header element
        fixed_header = ET.SubElement(earth_observation_header, "Fixed_Header")

        # Add child elements to <Fixed_Header>
        file_name = ET.SubElement(fixed_header, "File_Name")
        file_name.text = "sample_attitude"

        file_description = ET.SubElement(fixed_header, "File_Description")
        file_description.text = header.get("file_description", "SCRATCH ATTITUDE FILE FROM NAVATT")

        ET.SubElement(fixed_header, "Notes")

        mission_elt = ET.SubElement(fixed_header, "Mission")
        mission_elt.text = header.get("mission", "SENTINEL-3")

        file_class = ET.SubElement(fixed_header, "File_Class")
        file_class.text = header.get("file_class", "OPER")

        file_type = ET.SubElement(fixed_header, "File_Type")
        file_type.text = header.get("file_type", "NAVATT_ATT")

        # Validity_Period
        validity_period = ET.SubElement(fixed_header, "Validity_Period")
        validity_start = ET.SubElement(validity_period, "Validity_Start")
        validity_start.text = header.get("val_start_date", "missing")

        validity_stop = ET.SubElement(validity_period, "Validity_Stop")
        validity_stop.text = header.get("val_stop_date", "missing")

        file_version = ET.SubElement(fixed_header, "File_Version")
        file_version.text = "0001"

        eoffs_version = ET.SubElement(fixed_header, "EOFFS_Version")
        eoffs_version.text = "3.0"

        # Source
        source = ET.SubElement(fixed_header, "Source")  # TODO: Close the bracket automatically
        system = ET.SubElement(source, "System")
        system.text = header.get("system", "SENTINEL-3 L1 IPF")

        creator = ET.SubElement(source, "Creator")
        creator.text = header.get("creator", "OLCI L1B EO")

        creator_version = ET.SubElement(source, "Creator_Version")
        creator_version.text = header.get("creator_version", "-")

        creation_date = ET.SubElement(source, "Creation_Date")
        creation_date.text = datetime.now().strftime("UTC=%Y-%m-%dT%H:%M:%S")

        ET.SubElement(earth_observation_header, "Variable_Header")

        # Create the Data_Block element
        data_block = ET.SubElement(root, "Data_Block", type="xml")

        attitude_file_type = ET.SubElement(data_block, "Attitude_File_Type")
        attitude_file_type.text = "Sat_Attitude"

        attitude_data_type = ET.SubElement(data_block, "Attitude_Data_Type")
        attitude_data_type.text = "Quaternions"

        max_gap_value = ET.SubElement(data_block, "Max_Gap", attrib={"unit": "s"})
        max_gap_value.text = f'{attitude.get("max_gap", 0.0):.6f}'

        quaternion_data = ET.SubElement(data_block, "Quaternion_Data")

        reference_frame = ET.SubElement(quaternion_data, "Reference_Frame")
        reference_frame.text = FRAME_MAP[FrameId[attitude.get("frame", "EME2000")]]

        list_of_quaternions = ET.SubElement(
            quaternion_data, "List_of_Quaternions", count=str(len(attitude["quaternions"]))
        )

        tr = TimeReference()
        # # Populate List_of_Quaternions with quaternions elements
        for i, quat in enumerate(attitude["quaternions"]):
            elem = ET.SubElement(list_of_quaternions, "Quaternions")

            time_str = tr.to_str(
                attitude["times"][source_scale]["offsets"][i],
                fmt="CCSDSA_MICROSEC",
                ref_in=TimeRef[source_scale],
                ref_out=TimeRef[target_scale],
            )

            # Populate OSV with data from the input dictionary
            elem_data = {
                "Time": f"{target_scale}={time_str}",
                "Q1": quat[0],
                "Q2": quat[1],
                "Q3": quat[2],
                "Q4": quat[3],
            }

            populate_element_from_dict(elem, elem_data)

        # Create the XML tree
        tree = ET.ElementTree(root)

        ET.indent(tree)

        # Write the XML tree to a file
        tree.write(path, xml_declaration=True, encoding="utf-8", method="html")

    def change_orbit_frame(self, orbit: dict, frame: FrameId) -> dict:
        """
        Change the frame used to express orbit position and velocities

        :param dict orbit: Input orbit structure (see schema ORBIT_STATE_VECTORS_SCHEMA)
        :param FrameId frame: output frame to use
        :return: Transformed orbit structure, or input orbit if no transformation needed
        """

        output = orbit
        # convert to a different frame if needed, raise KeyError if no "frame"
        if orbit["frame"] != frame.name:
            # reprojection needed
            output = self.earth_body.transform_orbit(orbit.copy(), frame)

        return output

    def fill_other_timescales(self, timescale_array: dict) -> None:
        """
        Takes the first available timescale in a TIMESCALE_ARRAY_SCHEMA to generate other missing
        timescales among GPS, TAI, UTC, UT1.

        :param dict timescale_array: dict with timescales (see TIMESCALE_ARRAY_SCHEMA)
        """

        validate_or_throw(timescale_array, TIMESCALE_ARRAY_SCHEMA)

        first_scale = TimeRef[next(iter(timescale_array))]

        for other_scale in [TimeRef.GPS, TimeRef.TAI, TimeRef.UTC, TimeRef.UT1]:
            if other_scale.name not in timescale_array:
                self.time_reference.convert_all(
                    timescale_array,
                    first_scale,
                    other_scale,
                    field_in=first_scale.name,
                    field_out=other_scale.name,
                )

    @staticmethod
    def apply_attitude_rotation(attitude: dict, matrix: np.ndarray) -> dict:
        """
        Apply a rotation to all attitude quaternions

        :param dict attitude: Input attitude structure (see schema ATTITUDE_SCHEMA)
        :param np.ndarray matrix: rotation matrix to use
        :return: Transformed attitude structure, or input attitude if no transformation needed
        """
        assert matrix.shape == (3, 3)
        if np.all(matrix == np.eye(3)):
            return attitude
        convert_rotation = R.from_matrix(matrix)
        att_rotations = R.from_quat(attitude["quaternions"])
        out_rotations = att_rotations * convert_rotation
        output = {}
        output.update(attitude)
        output["quaternions"] = out_rotations.as_quat()
        return output
