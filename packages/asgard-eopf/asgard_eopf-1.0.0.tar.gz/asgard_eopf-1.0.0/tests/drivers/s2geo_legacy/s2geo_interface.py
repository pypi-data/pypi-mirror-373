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
S2geoInterface implementation.
"""

import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from contextlib import suppress
from typing import List

from drivers.s2geo_legacy.s2geo_datastrip import S2geoDatastrip
from drivers.s2geo_legacy.s2geo_gipp import S2geoGipp
from drivers.s2geo_legacy.s2geo_gipp_spamod import S2geoGippSpamod
from drivers.xml_util import XmlUtil

from asgard.wrappers.orekit.utils import get_data_context  # JCC initVM()


class S2geoInterface:
    """
    S2Geo XML interface file legacy loader.

    :param xml_path: XML interface file path
    :param x_root: XML root node
    """

    def __init__(self, xml_path: str):
        """Constructor from XML interface file path"""

        self.xml_path: str = xml_path
        self.x_root: ET.Element = None
        self._data_context = None

    def read(self) -> dict:
        """
        Read interface file.

        :return: output configuration JSON values
        """

        # Init dict with default value for new keys
        def nested_dict():
            return defaultdict(nested_dict)

        d_config = nested_dict()

        # Read XML file. Remove namespaces to facilitate reading.
        self.x_root = XmlUtil.read_with_etree(self.xml_path, remove_namespaces=True)

        # Set the IERS directory in Orekit
        self._data_context = get_data_context(self.find_file("IERS"))

        # Read file resources
        d_res = d_config["resources"]
        with suppress(IndexError):
            d_res["iers"] = self.find_files("IERS")[0]
        with suppress(IndexError):
            d_res["geoid"] = self.find_files("GEOID")[0]
        with suppress(IndexError):
            if self.find_files("DEM_GLOBE")[0].endswith(".zarr"):
                d_res["dem_zarr"] = self.find_files("DEM_GLOBE")[0]
            else:  # DEM legacy
                d_res["dem_globe"] = self.find_files("DEM_GLOBE")[0]
        with suppress(IndexError):
            if self.find_files("DEM_SRTM")[0].endswith(".zarr"):
                d_res["dem_zarr"] = self.find_files("DEM_SRTM")[0]
            else:  # DEM legacy
                d_res["dem_srtm"] = self.find_files("DEM_SRTM")[0]

        # S2Geo globe and SRTM DEM tiles are always overlapping
        d_res["overlapping_tiles"] = True

        # Compute with refining ?
        with_refining = False

        # Is the datastrip info in an external file ? Test both parameter names.
        # TODO: to be tested and not sure of the difference between the two params.
        datastrip_file = (
            self.Parameter(self).find(self.x_root, "DATASTRIP").path
            or self.Parameter(self).find(self.x_root, "AncillaryDataFromDimap").path
        )

        # Init a datastrip legacy loader instance from the datastrip XML file
        datastrip = None
        if datastrip_file is not None:
            datastrip = S2geoDatastrip.from_xml_file(datastrip_file, d_config, self._data_context)

            # Read the refining flag
            with_refining = self.Parameter(self).find(self.x_root, "ComputeWithRefining").value

        # If no external file (=no ancillary data), we read the datastrip info from the interface file.
        else:
            # Read XML nodes
            x_sensor_conf = self.x_root.find("Sensor_Configuration")
            x_granules = self.x_root.find("Granules_Information")
            x_attitudes = self.x_root.find("Satellite_Ancillary_Data_Info/Attitudes")
            x_ephemeris = self.x_root.find("Satellite_Ancillary_Data_Info/Ephemeris")

            # Init a datastrip loader instance. The XML root node is None.
            datastrip = S2geoDatastrip.from_xml_nodes(
                None,
                x_sensor_conf,
                x_granules,
                x_attitudes,
                x_ephemeris,
                d_config,
                self._data_context,
            )

            # In this case, the level is always L0
            datastrip.level = "Level-0_DataStrip_ID"  # LevelInfo.L0

        # Read the datastrip info
        datastrip.read(with_refining)

        # Find the GIPP files that are listed in the interface file
        gip_viedir_paths = self.find_files("GIP_VIEDIR")  # viewing directions
        gip_spamod_path = self.find_file("GIP_SPAMOD")  # spacecraft model parameters

        # gip_g2para_path = self.find_file ("GIP_G2PARA")   # geo s2 parameters
        # gip_r2abca_path = self.find_file ("GIP_R2ABCA")   # absolute calibration parameters
        # gip_invloc_path = self.find_file ("GIP_INVLOC")     # inverse location parameters
        # gip_prdloc_path = self.find_file ("GIP_PRDLOC")     # init loc prod s2 parameters

        # Read the GIPP files
        S2geoGipp(d_config).read_viewing_directions(gip_viedir_paths, datastrip.tdis)
        S2geoGippSpamod(d_config).read_spacecraft(gip_spamod_path)

        # j_grid_step_parameters = S2geoGipp.read_grid_step_parameters (gip_g2para_path)
        # j_angle_step_parameters = S2geoGipp.read_angle_step_parameters (gip_r2abca_path)

        # Convert the default dicts to regular dicts for reading.
        def no_defaultdict(dict_):
            if isinstance(dict_, dict):
                dict_ = {key: no_defaultdict(value) for key, value in dict_.items()}
            return dict_

        return no_defaultdict(d_config)

    def find_files(self, type_: str) -> List[str]:
        """Find files (e.g. GIPP, DEM, ...) from type, return an empty list if not found."""

        # Use an XPath expression to find the files
        found = self.x_root.findall(f"File_Names[@type={type_!r}]/File_Name")

        # For each relative path, add the interface file directory
        files = []
        for file in found:
            if os.path.isabs(file.text):
                files.append(os.path.realpath(file.text))
            else:
                files.append(os.path.realpath(os.path.join(os.path.dirname(self.xml_path), file.text)))
        return files

    def find_file(self, type_: str) -> str:
        """Find a single file, return None if not found."""
        found = self.find_files(type_)
        return found[0] if found else None

    class Parameter:  # pylint: disable=too-few-public-methods
        """Parameter read from the interface file"""

        def __init__(self, interface: "S2geoInterface"):
            self.interface = interface
            self.name: str = None
            self.value: bool = False
            self.path: str = None
            self.type: str = None
            self.bands: list = None
            self.detectors: list = None

        def find(self, x_root, name: str):
            """Find parameter from interface file XML root and parameter name"""

            self.name = name

            # Use an XPath expression to find the parameter
            x_param = x_root.find(f"Parameters[Name={name!r}]")
            if x_param is None:
                return self

            # Read the XML nodes
            with suppress(Exception):
                self.value = x_param.find("Value").text.lower() == "true"
            with suppress(Exception):
                path = x_param.find("Path").text
                if os.path.isabs(path):
                    self.path = os.path.realpath(path)
                else:
                    self.path = os.path.realpath(os.path.join(os.path.dirname(self.interface.xml_path), path))
            with suppress(Exception):
                self.type = x_param.find("Type").text
            self.bands = [x.text for x in x_param.findall("Band_List/BandId")]
            self.detectors = [x.text for x in x_param.findall("Detector_List/DetectorId")]

            return self
