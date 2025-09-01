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
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# pylint: disable=too-many-locals,import-error,too-many-branches,too-many-lines,too-many-arguments,too-many-statements,pointless-string-statement
"""
Unit tests for MSI Sentinel 2 products
"""

import json
import logging
import os
import os.path as osp
import re

# flake8: noqa ignore auto-generated bash code lines that are > 120 characters
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Type

import dill as pickle
import numpy as np
import pytest
import resources.S2MSIdataset.sentinel2_msi_datasets as tds
from drivers.s2geo_legacy.s2geo_interface import S2geoInterface
from helpers.compare import GeodeticComparator, planar_captor_error
from pyrugged.errors.pyrugged_exception import PyRuggedError
from termcolor import colored
from validations.common import (
    check_with_reference,
    get_points_list_xml,
    print_error,
    print_results,
    setup_remote_dem,
    write_results_in_json,
)

from asgard.core.toolbox import NumpyArrayEncoder
from asgard.sensors.sentinel2.msi import S2MSIGeometry
from asgard.sensors.sentinel2.s2_band import S2Band
from asgard.sensors.sentinel2.s2_detector import S2Detector
from asgard.sensors.sentinel2.s2_sensor import S2Sensor

# Resources directory
TEST_DIR = osp.dirname(__file__)
# RESOURCES = osp.join(TEST_DIR, "resources/S2MSIdataset") <= In resources.S2MSIdataset.test_sentinel2_msi_datasets now

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# Generate documentation for the "init_schema" methods
sys.path.append(osp.join(TEST_DIR, "../doc/scripts/init_schema"))

DEM_90_20240605 = "S0__ADF_DEM90_20000101T000000_21000101T000000_20240605T132601.zarr"
DEM_90_20240528 = "S0__ADF_DEM90_20000101T000000_21000101T000000_20240528T050715.zarr"
DEM_30_20240604 = "S0__ADF_DEM30_20000101T000000_21000101T000000_20240604T233343.zarr"

# Thresholds is a dictionary for thresholds for "ground", "altitude", "inverse_loc",
#         "incidence", "sun", "surface_ratio", "max_footprint_diff"
# Values used to compare and set tolerances
THRESHOLDS_LEGACY_BASED = {
    "ground": 1e-6,  # m
    "altitude": 1e-6,  # m
    "inverse_loc": 1e-2,  # pixel
    "incidence": 1e-3,
    "sun": 1e-3,  # Factor 10 below the precision of the model
    "surface_ratio": 0.95,
    "max_footprint_diff": 1,
}
THRESHOLDS_REFACTORED = {
    "ground": 1e-6,  # m
    "altitude": 1e-3,  # m
    "inverse_loc": 1e-2,  # pixel
    "incidence": 1e-3,
    "sun": 1e-3,  # Factor 10 below the precision of the model
    "surface_ratio": 0.95,
    "max_footprint_diff": 1,
}

THRESHOLDS_REFACTORED_REALITY = {
    "ground": 1,  # m
    "altitude": 4,  # m
    "inverse_loc": 0.1,  # pixel
    "incidence": 1e-3,
    "sun": 1e-3,  # Factor 10 below the precision of the model
    "footprint_r": 0.95,
    "footprint_d": 1,
}


"""
    [
        # S2MSI_TDS1 - Small Island
        (tds.S2MSI_TDS1_L0c_DEM_REFACTORED),
        (tds.S2MSI_TDS1_L0c_CONST_REFACTORED),
        (tds.S2MSI_TDS1_L1B_DEM_REFACTORED),
        (tds.S2MSI_TDS1_L1C_DEM_REFACTORED),
        # S2MSI_TDS2 - Antemeridian
        (tds.S2MSI_TDS2_L0c_DEM_REFACTORED),
        (tds.S2MSI_TDS2_L0c_CONST_REFACTORED),
        (tds.S2MSI_TDS2_L1B_DEM_REFACTORED),
        (tds.S2MSI_TDS2_L1C_DEM_REFACTORED),
        # S2MSI_TDS3 - Meridian 0
        (tds.S2MSI_TDS3_L1B_DEM_REFACTORED),
        # S2MSI_TDS4 - Equator
        (tds.S2MSI_TDS4_L1B_DEM_REFACTORED),
        # S2MSI_TDS5 - Long & High Latitude
        (tds.S2MSI_TDS5_L0u_DEM_REFACTORED),
        (tds.S2MSI_TDS5_L0c_DEM_REFACTORED),
        (tds.S2MSI_TDS5_L0c_CONST_REFACTORED),
        (tds.S2MSI_TDS5_L1B_DEM_REFACTORED),
        (tds.S2MSI_TDS5_L1C_DEM_REFACTORED),
    ],
    ids=[
        # S2MSI_TDS1 - Small Island
        "S2MSI_TDS1_L0c_DEM_REFACTORED",
        "S2MSI_TDS1_L0c_CONST_REFACTORED",
        "S2MSI_TDS1_L1B_DEM_REFACTORED",
        "S2MSI_TDS1_L1C_DEM_REFACTORED",
        # S2MSI_TDS2 - Antemeridian
        "S2MSI_TDS2_L0c_DEM_REFACTORED",
        "S2MSI_TDS2_L0c_CONST_REFACTORED",
        "S2MSI_TDS2_L1B_DEM_REFACTORED",
        "S2MSI_TDS2_L1C_DEM_REFACTORED",
        # S2MSI_TDS3 - Meridian 0
        "S2MSI_TDS3_L1B_DEM_REFACTORED",
        # S2MSI_TDS4 - Equator
        "S2MSI_TDS4_L1B_DEM_REFACTORED",
        # S2MSI_TDS5 - Long & High Latitude
        "S2MSI_TDS5_L0u_DEM_REFACTORED",
        "S2MSI_TDS5_L0c_DEM_REFACTORED",
        "S2MSI_TDS5_L0c_CONST_REFACTORED",
        "S2MSI_TDS5_L1B_DEM_REFACTORED",
        "S2MSI_TDS5_L1C_DEM_REFACTORED",
    ]

    [
        # S2MSI_TDS1 - small island
        (tds.S2MSI_TDS1_L1C_DEM_INVLOC_REFACTORED),
        # S2MSI_TDS2 - Antemeridian
        (tds.S2MSI_TDS2_L1C_DEM_INVLOC_REFACTORED),
        # S2MSI_TDS3 - Meridian 0
        (tds.S2MSI_TDS3_L1C_DEM_INVLOC_REFACTORED),
        # S2MSI_TDS4 - Equator
        (tds.S2MSI_TDS4_L1C_DEM_INVLOC_REFACTORED),
        # S2MSI_TDS5 - Long & High Latitude
        (tds.S2MSI_TDS5_L1C_DEM_INVLOC_REFACTORED)
    ],
    ids=[
        # S2MSI_TDS1 - small island
        "S2MSI_TDS1_L1C_DEM_INVLOC_REFACTORED",
        # S2MSI_TDS2 - Antemeridian
        "S2MSI_TDS2_L1C_DEM_INVLOC_REFACTORED",
        # S2MSI_TDS3 - Meridian 0
        "S2MSI_TDS3_L1C_DEM_INVLOC_REFACTORED",
        # S2MSI_TDS4 - Equator
        "S2MSI_TDS4_L1C_DEM_INVLOC_REFACTORED",
        # S2MSI_TDS5 - Long & High Latitude
        "S2MSI_TDS5_L1C_DEM_INVLOC_REFACTORED",
    ],
"""


@pytest.mark.parametrize(
    "data",
    [
        # S2MSI_TDS1 - Small Island
        (tds.S2MSI_TDS1_L0c_DEM_REFACTORED),
        # S2MSI_TDS2 - Antemeridian
        (tds.S2MSI_TDS2_L1B_DEM_REFACTORED),
        # S2MSI_TDS5 - Long & High Latitude
        (tds.S2MSI_TDS5_L1B_DEM_REFACTORED),
    ],
    ids=[
        # S2MSI_TDS1 - Small Island
        "S2MSI_TDS1_L0c_DEM_REFACTORED",
        # S2MSI_TDS2 - Antemeridian
        "S2MSI_TDS2_L1B_DEM_REFACTORED",
        # S2MSI_TDS5 - Long & High Latitude
        "2MSI_TDS5_L1B_DEM_REFACTORED",
    ],
)
@pytest.mark.slow
def test_sentinel2_msi_val(data):
    """
        Run general test for sentinel 2 msi or only the inverse location on grid sentinel 2 msi.

    :param data:
    :param general_test:
    """
    # Adapt thresholds to the implementation used
    thresholds = {"theory": THRESHOLDS_REFACTORED, "reality": THRESHOLDS_REFACTORED_REALITY}
    print("\n\n\n")
    print(
        colored(
            "Thresholds theorical = " + str(thresholds["theory"]) + "\nReal thresholds " + str(thresholds["reality"]),
            "green",
        )
    )
    error_log = ""

    if data.isInverseLocation:
        if data.altitude is not None:
            print(
                colored(
                    "InverseLocation grids doesn't support constant altitude, it will not be used",
                    "red",
                )
            )

        error_log = inverse_loc_grid_test_sentinel2_msi(
            product_class=data.product_class,
            interface_path=data.interface_path,
            ref_data_path=data.ref_data_path,
            line_count_margin=data.line_count_margin,
            thresholds=thresholds,
        )
    else:
        error_log = general_test_sentinel2_msi(data, thresholds)

    error_log = general_test_sentinel2_msi(data, thresholds)

    if error_log == "":
        print(colored("Test run to the end", "green"))
    else:
        print(colored("Error:\n" + error_log + ".", "red"))
        pytest.fail("There was an error during the execution of this test :\n")


def general_test_sentinel2_msi(data, thresholds):
    """
    Test steps:
    - Read the Python dict into an ASGARD S2 MSI product that uses the Java/JCC/Sxgeo bindings.
    - Run direct and inverse locations and compare results to reference.

    :param class data: ..
    :param dict thresholds: ..
    """
    if data.altitude is not None:
        logging.info("Constant altitude set at: %s m.", str(data.altitude))

    # S2geo interface file -> Python dict
    config = S2geoInterface(data.interface_path).read()

    # Estimate the line counts with the user given margin in seconds
    if data.line_count_margin is not None:
        config["line_counts"] = S2MSIGeometry.estimate_line_counts(config, data.line_count_margin)

    # Write JSON file on disk
    if data.config_dump_path is not None:
        with open(data.config_dump_path, "w", encoding="utf-8") as file:
            json.dumps(json.dump(config, file, ensure_ascii=False, indent=2, cls=NumpyArrayEncoder))

    config["resources"].pop("geoid", "")
    config["resources"].pop("dem_srtm", "")
    config["resources"].pop("dem_globe", "")
    # Configure DEM Zarr
    config["resources"]["dem_zarr"] = setup_remote_dem(DEM_90_20240605)
    config["resources"]["geoid"] = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr",
    )

    # Python dict -> ASGARD S2 product
    product = data.product_class(**config)
    comp = GeodeticComparator(product.propagation_model.body)

    # Define structure to store processing results
    value_diffs_vs_ref = {
        "ground": np.array([]),
        "altitude": np.array([]),
        "inverse_loc": np.array([]),
        "sun": np.array([]),
        "incidence": np.array([]),
        "footprint_r": np.array([]),
        "footprint_d": np.array([]),
    }
    list_diffs_vs_ref = {
        "ground": np.array([]),
        "altitude": np.array([]),
        "inverse_loc": np.array([]),
        "sun": np.array([]),
        "incidence": np.array([]),
        "footprint": np.array([]),
    }

    # Define strucutre to store processing results
    exec_times = defaultdict(lambda: 0.0)  # execution time in seconds

    # Bash script used to generate the S2Geo reference ground coordinates from the command line.
    ref_script_script = (
        open(data.ref_script_path, "w", encoding="utf-8")  # pylint: disable=consider-using-with
        if data.ref_script_path
        else None
    )

    if ref_script_script is not None:
        logging.info("Generate the points to call Legacy S2GEO ; ref_script_script=%s", ref_script_script)

    # Ground reference results
    ref_data = None
    loc_time = None

    error_log = ""
    # Read the ground reference results (as a Python script) obtained with S2Geo (or None to use
    # the DEM). Read the ground refererence results (as a Python script) obtained with S2Geo (or
    # None to use the DEM)
    if data.ref_data_path:
        ref_data = defaultdict(lambda: defaultdict(list))
        print("Read reference operation text file " + osp.realpath(data.ref_data_path))
        with open(data.ref_data_path, encoding="utf-8") as ref_file:
            for line in ref_file:
                if line[0] == "B":
                    read_sensor = line[0:3] + "/" + line[5:8]
                    if "sun" in line:
                        pattern = re.compile(
                            r""".*azimuth\:\s(?P<azimuth>.*?)\s\,\szenith\:\s(?P<zenith>.*?)\}""", re.VERBOSE
                        )
                        match = pattern.match(line)
                        ref_data[read_sensor]["sun"].append(
                            [float(match.group("azimuth")), float(match.group("zenith"))]
                        )
                    elif "incidence" in line:
                        pattern = re.compile(
                            r""".*azimuth\:\s(?P<azimuth>.*?)\s\,\szenith\:\s(?P<zenith>.*?)\}""", re.VERBOSE
                        )
                        match = pattern.match(line)
                        ref_data[read_sensor]["incidence"].append(
                            [float(match.group("azimuth")), float(match.group("zenith"))]
                        )
                    else:
                        pattern = re.compile(
                            r""".*x\:\s(?P<x>.*?)\s\,\sy\:\s(?P<y>.*?)\s\,\sz\:\s(?P<z>.*?)\}""", re.VERBOSE
                        )
                        match = pattern.match(line)
                        ref_data[read_sensor]["ground"].append(
                            [float(match.group("x")), float(match.group("y")), float(match.group("z"))]
                        )
                elif "Run time for SimpleLocEngine" in line:
                    loc_time = line[30:]

    # Test each S2 detector and band
    index = 1
    total = len(S2Detector.VALUES) * len(S2Band.VALUES)
    for detector in S2Detector.VALUES:
        for band in S2Band.VALUES:
            # Test sensor from its ASGARD name as defined in S2MSIGeometry
            sensor_s2 = S2Sensor(detector, band)
            sensor = sensor_s2.name

            logging.info("Sensor %s #%s/%s", sensor, index, total)
            index += 1

            # Final implementation: MSI lines start at 0
            min_line = 0
            max_line = product.coordinates[sensor]["lines"] - 1  # max line is included

            # Columns (=pixels) start at 0
            min_col = 0
            max_col = product.coordinates[sensor]["pixels"] - 1  # max col is included

            # Calculate 9 pixel coordinates = edges and centers
            pixels = np.array(
                [[col, row] for row in np.linspace(min_line, max_line, 3) for col in np.linspace(min_col, max_col, 3)],
                np.int32,
            )

            if ref_script_script is not None:
                for col, row in pixels:
                    ref_script_script.write(f"{band.name} {detector.legacy_name} {col} {row}\n")
                continue

            grounds = []
            acq_times = []
            inverse_pixels = []
            incidence_angles = []
            sun_angles = []
            footprint = []
            # Call the direct location method from the ASGARD product
            if data.steps["direct_location"]:
                try:
                    perf = time.perf_counter()
                    if data.altitude:  # the condition here is to make sure that we locate
                        # at constant altitude only over GEOID
                        grounds, acq_times = product.direct_loc_over_geoid(pixels, sensor, data.altitude)
                    else:
                        grounds, acq_times = product.direct_loc(pixels, sensor)
                    exec_times["direct loc"] += time.perf_counter() - perf
                except PyRuggedError as exp:
                    print(colored("    ! PyRuggedError: " + str(exp), "red"))
                    error_log += "   ! PyRuggedError: " + sensor + " [direct_loc]: " + str(exp) + "\n"

            # Call the inverse location method from the ASGARD product.
            # The legacy implementation takes (lon,lat,alt) arrays.
            # The ASGARD implementation takes (lon,lat) arrays.
            if data.steps["inverse_location"]:
                if len(grounds) > 0:
                    perf = time.perf_counter()
                    inverse_pixels = product.inverse_loc(
                        np.array(ref_data[sensor]["ground"])[:, :2],
                        geometric_unit=sensor,
                        altitude=data.altitude if (data.product_class == S2MSIGeometry) else None,
                    )
                    exec_times["inverse loc"] += time.perf_counter() - perf

            # Calculate the sun angles
            if data.steps["sun_angles"]:
                perf = time.perf_counter()
                sun_angles = product.sun_angles(grounds, acq_times)
                exec_times["sun_angles"] += time.perf_counter() - perf

            # Calculate the incidence angles
            if data.steps["incidence_angles"]:
                perf = time.perf_counter()
                incidence_angles = product.incidence_angles(grounds, acq_times)
                exec_times["incidence_angles"] += time.perf_counter() - perf

            # calculate detector footprint
            footprint_ref = None
            if data.steps["footprint"]:
                # Compute footprint path for current sensor
                sensor_footprint_path = osp.join(
                    data.ref_footprint_path, "DETFOO_" + detector.name + "_" + band.name + ".gml"
                )

                # Read footprint's points
                footprint_ref = get_points_list_xml(sensor_footprint_path)

                footprint_step = int(product.coordinates[sensor]["lines"] / footprint_ref.shape[0]) * 2
                # Compute footprint
                try:
                    perf = time.perf_counter()
                    footprint = product.footprint(sampling_step=footprint_step, geometric_unit=sensor)
                    exec_times["footprint"] += time.perf_counter() - perf
                except PyRuggedError as exp:
                    print(colored("  ! PyRuggedError: footprint " + str(exp), "red"))
                    error_log += "  ! PyRuggedError: " + sensor + " [footprint]: " + str(exp) + "\n"
                    list_diffs_vs_ref["footprint"] = np.concatenate((list_diffs_vs_ref["footprint"], [sensor]))
                    value_diffs_vs_ref["footprint_r"] = np.concatenate(
                        (value_diffs_vs_ref["footprint_r"], [float("nan")])
                    )
                    value_diffs_vs_ref["footprint_d"] = np.concatenate(
                        (value_diffs_vs_ref["footprint_d"], [float("nan")])
                    )

            # Compare to s2geo reference
            if ref_data is not None:
                test_output = {
                    "pixels": pixels,
                    "ground": grounds,
                    "inverse_loc": inverse_pixels,
                    "incidence": incidence_angles,
                    "sun": sun_angles,
                    "footprint": footprint,
                }
                logging.info("  Check zarr versus reference")
                try:
                    check_with_reference(
                        sensor_s2,
                        ref_data,
                        test_output,
                        value_diffs_vs_ref,
                        comp,
                        list_diffs_vs_ref,
                        thresholds["theory"],
                        footprint_ref,
                    )
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(colored(f"  ! Exception({type(e)=}): " + str(e), "red"))
                    error_log += f"  ! Exception({type(e)=}): " + str(e) + "\n"

                number_of_points = pixels.shape[0]
                for function_key, errors in value_diffs_vs_ref.items():
                    try:
                        if function_key == "footprint_r":
                            assert all(errors[-number_of_points:] > thresholds["reality"][function_key])
                        else:
                            assert all(errors[-number_of_points:] <= thresholds["reality"][function_key])
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        error_log += (
                            f"{type(e)}: {function_key} error superior to {thresholds['reality'][function_key]} "
                            f"with {sensor}\n"
                        )

    # end of loops over sensors

    # Print results
    if exec_times is not None:
        print(colored("Differences versus ref", "blue"))
        print_results(
            error_log,
            exec_times,
            ref_times=loc_time,
            all_diffs=value_diffs_vs_ref,
            list_diffs=list_diffs_vs_ref,
            inverse=False,
        )

        out_path = os.path.join(TEST_DIR, "msi_validation")
        dem_resolution = product.config["resources"]["dem_zarr"].path.split("/")[-1].split("_")[3].lower()
        write_results_in_json(value_diffs_vs_ref, data, f"results_{dem_resolution}", out_path)
        write_results_in_json(exec_times, data, f"times_{dem_resolution}", out_path)

    return error_log


def inverse_loc_grid_test_sentinel2_msi(
    product_class: Type,
    interface_path: str,
    ref_data_path: str,
    line_count_margin: int = None,
    thresholds: dict = None,
):
    """
    Test steps:
    - Read the S2geo interface file using the ASGARD-Legacy loader into a Python dict (json format).
    - Read the Python dict into an ASGARD S2 MSI product that uses the Java/JCC/Sxgeo bindings.
    - Run inverse locations and compare results to reference.

    :param class product_class: S2MSILegacyGeometry (legacy-base) ; S2MSIGeometry (refactored)
    :param str interface_path: Path to the 'S2GEO_Input_interface.xml' interface file
    :param str ref_data_path: Path to the txt file that contains the S2Geo reference results.
    ASGARD S2 MSI processing is run and results are compared to the reference.
    :param int line_count_margin: margin in seconds when estimating the line counts from min/max
    dates without granule information.
    :param dict thresholds: ...
    """
    # S2geo interface file -> Python dict
    config = S2geoInterface(interface_path).read()

    # Estimate the line counts with the user given margin in seconds
    if line_count_margin is not None:
        config["line_counts"] = S2MSIGeometry.estimate_line_counts(config, line_count_margin)

    # Initialize results structures
    value_diffs_vs_ref = {"inverse_loc": np.array([])}
    list_diffs_vs_ref = {"inverse_loc": np.array([])}
    exec_times = defaultdict(lambda: 0.0)  # execution time in seconds
    error_log = ""

    # Configure config and Product with zarr DEM

    # Configure DEM Zarr
    # config_zarr["resources"]["dem_zarr"] = setup_remote_dem_geolib_input(DEM_90_20240528)
    config["resources"]["dem_zarr"] = setup_remote_dem(DEM_90_20240605)
    config["resources"]["geoid"] = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr",
    )

    # Python dict -> ASGARD S2 product
    product = product_class(**config)

    # Ground reference results
    ref_data = None

    # Read the ground refererence results (as a Python script) obtained with S2Geo (or None to
    # use the DEM)
    if Path(ref_data_path).exists():
        ref_data = defaultdict(lambda: defaultdict(list))
        print("Read reference operation text file " + osp.realpath(ref_data_path))
        print("This might take a while as the parsed file is big.")

        with open(ref_data_path, "rb") as fhd:
            ref_data = pickle.load(fhd)
            ref_time = ref_data["ref_time"]
            print("ref_time read from pkl file:" + ref_time)
    else:
        print(
            colored(
                ref_data_path
                + ": is supposed to be a pkl file containing the dictionnary as it defines the list of points",
                "red",
            )
        )
        return ""

    # Test each S2 detector and band
    index = 1
    total = len(S2Detector.VALUES) * len(S2Band.VALUES)
    for detector in S2Detector.VALUES:
        for band in S2Band.VALUES:
            # Test sensor from its ASGARD name as defined in S2MSIGeometry
            sensor = S2Sensor(detector, band).name

            print(f"Sensor {sensor!r} #{index}/{total}")
            index += 1
            assert product.coordinates[sensor] == product.coordinates[sensor]

            if sensor in ref_data.keys() and np.array(ref_data[sensor]["inverse_loc"]).size != 0:
                print("    Number of inverse locations: " + str(np.array(ref_data[sensor]["inverse_loc"]).size))
            else:
                continue

            # Inverse location method from the ASGARD product takes diiferent inputs depending on product type
            # The legacy implementation takes (lon,lat,alt) arrays.
            # The ASGARD implementation takes (lon,lat) arrays.
            if product_class == S2MSIGeometry:
                pixels = np.array(ref_data[sensor]["inverse_loc"])[:, :2]
            else:
                pixels = np.array(ref_data[sensor]["inverse_loc"])[:, :3]

            # Call inverse location method
            print("    Compute inverse loc grid.")
            inverse_pixels = None
            perf = time.perf_counter()
            try:
                inverse_pixels = product.inverse_loc(pixels, geometric_unit=sensor)
            except AttributeError as exp:
                print(colored(f"  ! AttributError({type(exp)=}): inverse loc " + str(exp), "red"))
                error_log += f"  ! AttributError({type(exp)=}): inverse loc " + str(exp) + "\n"
                list_diffs_vs_ref["inverse_loc"] = np.concatenate((list_diffs_vs_ref["inverse_loc"], [sensor]))
                value_diffs_vs_ref["inverse_loc"] = np.concatenate((value_diffs_vs_ref["inverse_loc"], [float("nan")]))
            exec_times["inverse_loc"] += time.perf_counter() - perf
            print("      time ~ " + str(time.perf_counter() - perf) + "s")

            # Inverse Location errors
            error_invloc = (
                planar_captor_error(np.array(ref_data[sensor]["inverse_loc"])[:, 3:], inverse_pixels)
                / band.pixel_height
            )
            # Divide by resolution to have distance in pixel
            # regardless of the resolution of the band

            list_diffs_vs_ref, value_diffs_vs_ref = print_error(
                sensor,
                "inverse_loc",
                thresholds["theory"],
                error_invloc,
                list_diffs_vs_ref,
                value_diffs_vs_ref,
                precision=3,
                inverse=True,
            )
            try:
                assert all(value_diffs_vs_ref["inverse_loc"] <= thresholds["reality"]["inverse_loc"])
            except Exception as e:  # pylint: disable=broad-exception-caught
                error_log += (
                    f"{type(e)}: Inverse loc grid error superior to {thresholds['reality']['inverse_loc']} "
                    f"with {sensor}\n"
                )

    if exec_times["inverse_loc"]:
        print(colored("Differences versus ref", "blue"))
        print_results(error_log, exec_times, ref_time, value_diffs_vs_ref, list_diffs_vs_ref, True)

    return "There was an error during the nominal execution of this test"
