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
Common function use for validations tests
"""
import json
import logging
import os

import numpy as np
from helpers.compare import (  # pylint: disable=E0401
    planar_captor_error,
    pointing_error_azi_zen,
)
from lxml import etree
from termcolor import colored
from zarr.storage import FSStore

from asgard.sensors.sentinel2.msi import S2MSIGeometry

TEST_DIR = os.path.dirname(__file__)


def setup_remote_dem(dem_filename) -> FSStore:
    """
    Create a FSStore pointing to a DEM stored remotely on S3
    """

    dem_path_s3 = f"simplecache::s3://common/ADFstatic/{dem_filename}"
    s3_config = {
        "key": os.environ.get("S3_COMMON_ACCESS"),
        "secret": os.environ.get("S3_COMMON_SECRET"),
        "client_kwargs": {
            "endpoint_url": "https://s3.sbg.perf.cloud.ovh.net",
            "region_name": "sbg",
        },
    }
    logging.info("Using DEM : %s", dem_path_s3)

    return FSStore(dem_path_s3, mode="r", s3=s3_config)


def setup_remote_dem_geolib_input(dem_filename) -> FSStore:
    """
    Create a FSStore pointing to a DEM stored remotely on S3
    """

    dem_path_s3 = f"simplecache::s3://geolib-input/ADFstatic/{dem_filename}"
    s3_config = {
        "key": os.environ.get("S3_GEOLIB_INPUT_RO_ACCESS"),
        "secret": os.environ.get("S3_GEOLIB_INPUT_RO_SECRET"),
        "client_kwargs": {
            "endpoint_url": "https://s3.sbg.perf.cloud.ovh.net",
            "region_name": "sbg",
        },
    }
    logging.info("Using DEM : %s", dem_path_s3)

    return FSStore(dem_path_s3, mode="r", s3=s3_config)


def print_error(sensor, data_type, thresholds, error, list_diffs, all_diffs, precision=3, inverse=False):
    """
        Function to format and print error

    :param sensor:
    :param data_type:
    :param thresholds:
    :param error:
    :param list_diffs:
    :param all_diffs:
    :param precision:
    :param inverse:
    """
    error_type = "planar" if data_type == "ground" else data_type

    if any(i > thresholds[data_type] for i in error):
        with np.printoptions(precision=precision):
            error_str = str(error[:10]) + " [...]" if inverse and error.size > 10 else str(error)
            message = f"      ! Value superior for {sensor} in {error_type} error: {error_str}"
            print(colored(message, "yellow"))

        list_diffs[data_type] = np.append(list_diffs[data_type], sensor)

    all_diffs[data_type] = np.append(all_diffs[data_type], error)
    return list_diffs, all_diffs


def print_results(error_log, exec_times, ref_times=None, all_diffs=None, list_diffs=None, inverse=False):
    """
    Function to format and print results.

    :param error_log: Log of errors.
    :param exec_times: Execution times for different operations.
    :param ref_times: Reference execution times.
    :param all_diffs: All differences for each type.
    :param list_diffs: List of sensors with differences.
    :param inverse: Flag to indicate inverse comparison.
    """
    message = ""

    if all_diffs is not None:
        message += "\nMax Differences from reference:\n"

        # Define differences and descriptions
        diffs_info = [
            ("ground", "planar dist (m)"),
            ("altitude", "altitude (m)"),
            ("sun", "sun angles (angular diff (deg))"),
            ("incidence", "incidence angles (angular diff (deg))"),
            ("inverse_loc", "inverse loc (pixel)"),
            ("footprint_r", "footprint ratio"),
            ("footprint_d", "footprint max dist (pixel)"),
        ]

        for key, desc in diffs_info:
            if key in all_diffs and len(all_diffs[key]) > 0:
                message += f"    - {desc}: {all_diffs[key].max():.3g} ({np.quantile(all_diffs[key], 0.95):.3g})\n"

    if list_diffs is not None:
        message += "\nList Sensor that differs from reference:\n"
        for key, desc in [
            ("ground", "direct loc"),
            ("altitude", "altitude loc"),
            ("sun", "sun angles"),
            ("incidence", "incidence angles"),
            ("inverse_loc", "inverse loc"),
            ("footprint", "footprint"),
        ]:
            if key in list_diffs and len(list_diffs[key]) > 0:
                message += f"    - {desc}: {list_diffs[key]}\n"

    message += "\n\nExecution time for:\n"
    for type_, exec_time in exec_times.items():
        message += f"    - {type_}: {exec_time:.3g}s\n"

    if ref_times is not None:
        message += "\nReference execution time for:\n"
        if isinstance(ref_times, dict):
            for type_, ref_time in ref_times.items():
                message += f"    - {type_}: {ref_time:.3g}s\n"
        else:
            ref_desc = "inverse loc" if inverse else "direct loc + sun + viewing angles"
            message += f"    - {ref_desc}: {ref_times}\n"

    print(message)

    # ---------------------------------------
    # --------- Print error logs  -----------
    # ---------------------------------------
    if error_log:
        print(colored("  Error list:", "red"))
        print(colored(error_log, "red"))


def write_results_in_json(dict_to_write, dataset, dem_type, out_path):
    """
    Write results of validation MSI in json files
    """
    product_type = "REFACTORED" if dataset.product_class == S2MSIGeometry else "LEGACY"
    interface_path = "_".join(dataset.interface_path.split("/")[-2:])
    tds_name = "_".join(interface_path.split("_")[:4]) + "_" + product_type

    validation_folder = f"{out_path}/{dem_type}"
    os.makedirs(validation_folder, exist_ok=True)
    json_file = f"{validation_folder}/{tds_name}.json"

    if os.path.exists(json_file):
        logging.info("File %s.json already exists", tds_name)
    else:
        final_dict = {}

        # Assuming results is a dictionary with lists of equal length
        if "times" in dem_type:
            final_dict = dict(dict_to_write)
        else:
            for key, values in dict_to_write.items():
                if len(values) > 0:
                    values_to_add = {"max": values.max(), "C90": np.quantile(values, 0.95)}
                    final_dict[key] = values_to_add

        with open(json_file, "w", encoding="utf8") as output_file:
            json.dump(final_dict, output_file, indent=4)
        print(f"Results appended to {json_file}")


def check_with_reference(sensor, ref_data, test_output, all_diffs, comp, list_diffs, thresholds, footprint_ref):
    """
    Compare results with reference data

    :param sensor: ...
    :param ref_data: ...
    :param test_output: ...
    :param all_diffs: ...
    :param comp: ...
    :param list_diffs: ...
    :param thresholds: ...
    """
    sensor_name = sensor.name
    # Compare inverse loc results with original pixel values
    ref_data[sensor_name]["inverse_loc"] = test_output["pixels"]

    # Smarter diff between sxgeo and s2geo
    if len(test_output["ground"]) > 0:
        assert len(test_output["ground"]) == len(ref_data[sensor_name]["ground"])
        # assert np.all(np.isnan(ref_data[sensor]["ground"][0, 0, :]))

        # Lat/Long planar error
        error_2d = comp.planar_error(np.array(ref_data[sensor_name]["ground"]), np.array(test_output["ground"]))
        list_diffs, all_diffs = print_error(sensor_name, "ground", thresholds, error_2d, list_diffs, all_diffs)

        # Alt error
        error_alt = comp.height_error(np.array(ref_data[sensor_name]["ground"]), np.array(test_output["ground"]))
        list_diffs, all_diffs = print_error(sensor_name, "altitude", thresholds, error_alt, list_diffs, all_diffs)

    # Inverse Location errors
    if len(test_output["inverse_loc"]) > 0:
        error_inv_loc = planar_captor_error(
            np.array(ref_data[sensor_name]["inverse_loc"]), np.array(test_output["inverse_loc"])
        )
        list_diffs, all_diffs = print_error(
            sensor_name, "inverse_loc", thresholds, error_inv_loc, list_diffs, all_diffs
        )

    # Pointing error
    if len(test_output["incidence"]) > 0:
        error_incidence = pointing_error_azi_zen(
            np.array(ref_data[sensor_name]["incidence"]), np.array(test_output["incidence"])
        )
        list_diffs, all_diffs = print_error(
            sensor_name, "incidence", thresholds, error_incidence, list_diffs, all_diffs
        )

    # Sun error
    if len(test_output["sun"]) > 0:
        error_sun = pointing_error_azi_zen(np.array(ref_data[sensor_name]["sun"]), np.array(test_output["sun"]))
        list_diffs, all_diffs = print_error(
            sensor_name,
            "sun",
            thresholds,
            error_sun,
            list_diffs,
            all_diffs,
        )

    # Compute footprint comparison
    if len(test_output["footprint"]) > 0:
        poly_diff = np.array(comp.footprint_comparison(test_output["footprint"], footprint_ref))

        # Divide the distance part of diff by the resolution of the band in meter
        # to have the diff in pixel homogeneised between bands
        poly_diff[1:] = poly_diff[1:] / sensor.band.pixel_height

        # Verify if differences are higher than the thresholds.
        # If yes, log it and store it
        if poly_diff[0] <= thresholds["surface_ratio"] or poly_diff[1] > thresholds["max_footprint_diff"]:
            print(colored("      ! Value superior for " + sensor_name + " for footprint: " + str(poly_diff), "yellow"))
            list_diffs["footprint"] = np.concatenate((list_diffs["footprint"], [sensor_name]))
        # Save diff values fir final print with max and CE95.
        all_diffs["footprint_r"] = np.concatenate((all_diffs["footprint_r"], [poly_diff[0]]))
        all_diffs["footprint_d"] = np.concatenate((all_diffs["footprint_d"], [poly_diff[1]]))


def get_points_list_xml(metadata_file_path):
    """
        Convert GCP list read from XML file into a numpy array
    :param metadata_file_path: ...
    :return: a numpy array that contains all GCP found in metadata_file_path
    """
    namespaces_xml = {"gml": "http://www.opengis.net/gml", "ogr": "http://ogr.maptools.org/"}  # add more as needed

    tree = etree.parse(metadata_file_path)

    coords = etree.XPath(
        "/ogr:FeatureCollection/gml:featureMember/ogr:DETECTOR_FOOTPRINT/ogr:geometryProperty/"
        "gml:Polygon/gml:outerBoundaryIs/gml:LinearRing/gml:coordinates/text()",
        namespaces=namespaces_xml,
    )
    coords = coords(tree)

    return np.array(coords[0].replace(" ", ",").split(","), dtype=float).reshape(-1, 3)
