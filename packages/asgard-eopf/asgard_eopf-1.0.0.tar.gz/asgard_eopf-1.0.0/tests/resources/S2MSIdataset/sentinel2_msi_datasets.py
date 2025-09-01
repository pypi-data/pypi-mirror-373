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
# pylint: disable=too-many-locals,import-error,too-many-branches
"""
Datasets definition for ASGARD validation script for the Sentinel-2 MSI instrument.
"""

import os
import os.path as osp
from collections import namedtuple

from asgard.sensors.sentinel2.msi import S2MSIGeometry

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# Resources directory
FOLDER = osp.join(ASGARD_DATA, "S2MSIdataset")

# Test data.
# Pass the directory names from /tests/resources/propagation, the correction parameters
# and the TileUpdater from the corresponding pyrugged test.
# What Data contains
# - a class product_class: S2MSILegacyGeometry (legacy-base) ; S2MSIGeometry (refactored)
# - a str interface_path: Path to the 'S2GEO_Input_interface.xml' interface file
# - a float altitude: a constant altitude in meters, or None to use the DEM
# - a str ref_data_path: Path to the txt file that contains the S2Geo reference results.
#      ASGARD S2 MSI processing is run and results are compared to the reference.
# - a str Path to the folder that contains the S2Geo reference detector footprints:
#         DETFOO_DNN_BXX.gml.
# - a str config_dump_path: Path to a JSON file to dump ASGARD configuration after reading
#     the S2Geo interface file.
# - a str ref_script_path: Path to an output bash script that will contain the command lines
#     to generate the S2Geo reference results. ASGARD S2 MSI processing is not run.
# - an int line_count_margin: margin in seconds when estimating the line counts from min/max
#     dates without granule information.
Data = namedtuple(
    "Data",
    [
        "product_class",  # Set the product_class between S2MSILegacyGeometry (Legacybased implementation ) and
        # S2MSIGeometry (refactored implementation)
        "interface_path",  # Set path to xml file from legacy S2GEO_Inpu_interface.xml describing all inputs
        "altitude",  # Set a constant altitude
        "ref_data_path",  # Set path to the file containing references to be compared to
        "ref_footprint_path",  # Set path to the folder containing reference footprints
        "config_dump_path",
        "ref_script_path",
        "line_count_margin",
        "isInverseLocation",  # Either doiing inverse location grids, either doing 9 points
        # per band/detector with direct/inverse loc/ sun angles and footprint generation
        "steps",  # Set list of steps if not in inverse location grid mode
    ],
)

# -------------------------
# ----- S2MSI_TDS1 --------
# ---- Small Island -------
# -------------------------

S2MSI_TDS1_L0c_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS1/L0c_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS1/L0c_DEM_Legacy_s2geo_reference.txt"),
    osp.join(FOLDER, "S2MSI_TDS1/L0c_DEM_Legacy_FOOTPRINTS"),
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)

S2MSI_TDS1_L0c_CONST_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS1/L0c_CONST_S2GEO_Input_interface.xml"),
    3000.0,
    osp.join(FOLDER, "S2MSI_TDS1/L0c_CONST_s2geo_reference.txt"),
    None,
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)

S2MSI_TDS1_L1B_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS1/L1B_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS1/L1B_DEM_Legacy_s2geo_reference.txt"),
    osp.join(FOLDER, "S2MSI_TDS1/L1B_DEM_Legacy_FOOTPRINTS"),
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)


S2MSI_TDS1_L1C_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS1/L1C_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS1/L1C_DEM_Legacy_s2geo_reference.txt"),
    None,
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)


S2MSI_TDS1_L1C_DEM_INVLOC_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS1/L1C_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS1/s2geo_reference_grid_INVLOC_Full.pkl"),
    None,
    None,
    None,
    None,
    True,
    None,
)

# -------------------------
# ----- S2MSI_TDS2 --------
# ---- Antemeridian -------
# -------------------------

S2MSI_TDS2_L0c_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS2/L0c_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS2/L0c_DEM_Legacy_s2geo_reference.txt"),
    osp.join(FOLDER, "S2MSI_TDS2/L0c_DEM_Legacy_FOOTPRINTS"),
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)


S2MSI_TDS2_L0c_CONST_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS2/L0c_CONST_S2GEO_Input_interface.xml"),
    3000.0,
    osp.join(FOLDER, "S2MSI_TDS2/L0c_CONST_s2geo_reference.txt"),
    None,
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)


S2MSI_TDS2_L1B_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS2/L1B_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS2/L1B_DEM_Legacy_s2geo_reference.txt"),
    osp.join(FOLDER, "S2MSI_TDS2/L1B_DEM_Legacy_FOOTPRINTS"),
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)

S2MSI_TDS2_L1C_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS2/L1C_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS2/L1C_DEM_Legacy_s2geo_reference.txt"),
    None,
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)


S2MSI_TDS2_L1C_DEM_INVLOC_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS2/L1C_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS2/s2geo_reference_grid_INVLOC_Full.pkl"),
    None,
    None,
    None,
    None,
    True,
    None,
)

# -------------------------
# ----- S2MSI_TDS3 --------
# ----- Meridian 0 --------
# -------------------------
S2MSI_TDS3_L1B_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS3/L1B_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS3/L1B_DEM_Legacy_s2geo_reference.txt"),
    osp.join(FOLDER, "S2MSI_TDS3/L1B_DEM_Legacy_FOOTPRINTS"),
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)


S2MSI_TDS3_L1C_DEM_INVLOC_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS3/L1C_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS3/s2geo_reference_grid_INVLOC_Full.pkl"),
    None,
    None,
    None,
    None,
    True,
    None,
)

# -------------------------
# ----- S2MSI_TDS4 --------
# -----   Equator  --------
# -------------------------
S2MSI_TDS4_L1B_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS4/L1B_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS4/L1B_DEM_Legacy_s2geo_reference.txt"),
    osp.join(FOLDER, "S2MSI_TDS4/L1B_DEM_Legacy_FOOTPRINTS"),
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)

S2MSI_TDS4_L1C_DEM_INVLOC_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS4/L1C_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS4/s2geo_reference_grid_INVLOC_Full.pkl"),
    None,
    None,
    None,
    None,
    True,
    None,
)

# -------------------------
# ----- S2MSI_TDS5 --------
# -- Long & High Latitude -
# -------------------------
S2MSI_TDS5_L0u_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS5/L0u_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS5/L0u_DEM_Legacy_s2geo_reference.txt"),
    None,
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)

S2MSI_TDS5_L0c_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS5/L0c_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS5/L0c_DEM_Legacy_s2geo_reference.txt"),
    osp.join(FOLDER, "S2MSI_TDS5/L0c_DEM_Legacy_FOOTPRINTS"),
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)

S2MSI_TDS5_L0c_CONST_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS5/L0c_CONST_S2GEO_Input_interface.xml"),
    3000.0,
    osp.join(FOLDER, "S2MSI_TDS5/L0c_CONST_s2geo_reference.txt"),
    None,
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)


S2MSI_TDS5_L1B_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS5/L1B_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS5/L1B_DEM_Legacy_s2geo_reference.txt"),
    osp.join(FOLDER, "S2MSI_TDS5/L1B_DEM_Legacy_FOOTPRINTS"),
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)

S2MSI_TDS5_L1C_DEM_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS5/L1C_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS5/L1C_DEM_Legacy_s2geo_reference.txt"),
    None,
    None,
    None,
    None,
    False,
    {
        "direct_location": True,
        "inverse_location": True,
        "sun_angles": True,
        "incidence_angles": True,
        "footprint": False,
    },
)

S2MSI_TDS5_L1C_DEM_INVLOC_REFACTORED = Data(
    S2MSIGeometry,
    osp.join(FOLDER, "S2MSI_TDS5/L1C_DEM_Legacy_S2GEO_Input_interface.xml"),
    None,
    osp.join(FOLDER, "S2MSI_TDS5/s2geo_reference_grid_INVLOC_Full.pkl"),
    None,
    None,
    None,
    None,
    True,
    None,
)
