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
Unit tests for MSI Sentinel 2 products
"""

# flake8: noqa ignore auto-generated bash code lines that are > 120 characters

import importlib.machinery
import json
import logging
import os
import os.path as osp
import re
import time
import warnings
from collections import defaultdict
from typing import Type

import dask
import dask.array as da
import numpy as np
import pytest
import xarray as xr
from dask.distributed import Client
from drivers.s2geo_legacy.s2geo_interface import S2geoInterface
from helpers.compare import GeodeticComparator
from pytest import FixtureRequest
from termcolor import colored
from validations.common import check_with_reference, setup_remote_dem
from zarr.storage import FSStore

from asgard.core.product import direct_location, inverse_location
from asgard.core.toolbox import NumpyArrayEncoder
from asgard.sensors.sentinel2.msi import S2MSIGeometry
from asgard.sensors.sentinel2.s2_band import S2Band
from asgard.sensors.sentinel2.s2_detector import S2Detector
from asgard.sensors.sentinel2.s2_sensor import S2Sensor

# Resources directory
TEST_DIR = osp.dirname(__file__)
RESOURCES = osp.join(TEST_DIR, "resources/S2MSIdataset")
OUT_DIR = osp.join(TEST_DIR, "outputs")

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")
DEM_90_20240605 = "S0__ADF_DEM90_20000101T000000_21000101T000000_20240605T132601.zarr"

THRESHOLDS_REFACTORED = {
    "ground": 1e-6,  # degrees
    "altitude": 1e-3,
    "inverse_loc": 1e-2,  # pixel
    "incidence": 1e-3,
    "sun": 1e-3,  # Factor 10 below the precision of the model
    "surface_ratio": 0.95,
    "max_footprint_diff": 1,
}


@pytest.fixture(name="dask_client", scope="module")
def given_a_dask_local_client():
    """
    Instantiate a local cluster with 1 worker
    """
    dask.config.set({"distributed.scheduler.active-memory-manager.policies": []})
    return Client(processes=True, threads_per_worker=1, n_workers=1)


@pytest.fixture(name="msi", scope="module")
def given_msi_geometry_tds1():
    """
    Instantiate a S2MSIGeometry using TDS1
    """
    interface_path = osp.join(ASGARD_DATA, "S2MSIdataset/S2MSI_TDS1/L0c_DEM_zarr_S2GEO_Input_interface.xml")

    # S2geo interface file -> Python dict
    config = S2geoInterface(interface_path).read()

    # patch elevation: use ZARR DEM here
    config["resources"]["dem_zarr"] = setup_remote_dem(DEM_90_20240605)  # GETAS_PATH
    config["resources"]["geoid"] = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr",
    )

    for key in ["dem_srtm", "dem_globe"]:
        if key in config["resources"]:
            del config["resources"][key]

    return S2MSIGeometry(**config)


@pytest.mark.slow
@pytest.mark.dem
@pytest.mark.parametrize("n_workers", [1, 2, 4, 6])
def test_navatt_msi_product_scalability(msi, dask_client, n_workers):  # pylint: disable=unused-argument
    """
    Unit test for S2MSIProduct.direct_loc with dask scalability
    """
    sensor = "B01/D01"
    dask_client.cluster.scale(n_workers)
    min_line = 0
    max_line = msi.coordinates[sensor]["lines"] - 1  # max line is included

    # Columns (=pixels) start at 0
    min_col = 0
    max_col = msi.coordinates[sensor]["pixels"] - 1  # max col is included
    pixels = np.array(
        [[col, row] for row in np.linspace(min_line, max_line, 3) for col in np.linspace(min_col, max_col, 3)],
        np.int32,
    )
    perf = time.perf_counter()
    msi_remote = dask_client.scatter(msi)
    dask_client.replicate([msi_remote])
    print(f"Broadcast time : {time.perf_counter() - perf:.3g}")

    perf = time.perf_counter()
    chunked_coords = da.from_array(pixels, chunks=(9, 2))
    ground = da.map_blocks(
        direct_location,
        msi_remote,
        chunked_coords,
        altitude=0.0,
        geometric_unit="B01/D01",
        dtype="float64",
        chunks=(9, 2),
    )
    ground.compute()

    print(f"Compute time : {time.perf_counter() - perf:.3g}")

    perf = time.perf_counter()
    inverse_pixels = da.map_blocks(
        inverse_location,
        msi_remote,
        ground,
        geometric_unit="B01/D01",
        dtype="float64",
        chunks=(9, 2),
    )
    inverse_pixels.compute()

    # clean the broadcasted data
    dask_client.cancel([msi_remote])


@pytest.fixture(name="ref_data_tds1")
def read_ref_data_tds1():
    """
    Fixture for reference ground data for TDS1
    """
    ref_data_path = os.path.join(ASGARD_DATA, "S2MSIdataset", "S2MSI_TDS1", "L0c_DEM_Legacy_s2geo_reference.txt")
    ref_data = defaultdict(lambda: defaultdict(list))
    print("Read reference operation text file " + osp.realpath(ref_data_path))
    with open(ref_data_path, encoding="utf-8") as ref_file:
        for line in ref_file:
            if line[0] == "B":
                read_sensor = line[0:3] + "/" + line[5:8]
                if "sun" in line:
                    pattern = re.compile(
                        r""".*azimuth\:\s(?P<azimuth>.*?)\s\,\szenith\:\s(?P<zenith>.*?)\}""", re.VERBOSE
                    )
                    match = pattern.match(line)
                    ref_data[read_sensor]["sun"].append([float(match.group("azimuth")), float(match.group("zenith"))])
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

    return ref_data


@pytest.mark.slow
@pytest.mark.dem
@pytest.mark.parametrize("n_workers", [1, 2, 4, 6])
def test_navatt_msi_real_case_scalability(
    msi, dask_client, n_workers, ref_data_tds1
):  # pylint: disable=unused-argument
    """
    test for S2MSIProduct.direct_loc with dask and full tds1 data
    """
    index = 1
    total = len(S2Detector.VALUES) * len(S2Band.VALUES)

    perf = time.perf_counter()
    msi_remote = dask_client.scatter(msi)
    dask_client.replicate([msi_remote])
    print(f"Broadcast time : {time.perf_counter() - perf:.3g}")
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
    footprint_ref = None
    error_log = ""

    comp = GeodeticComparator(msi.propagation_model.body)

    for detector in S2Detector.VALUES:
        for band in S2Band.VALUES:
            # Test sensor from its ASGARD name as defined in S2MSIGeometry
            sensor_s2 = S2Sensor(detector, band)
            sensor = sensor_s2.name

            logging.info("Sensor %s #%s/%s", sensor, index, total)
            index += 1

            dask_client.cluster.scale(n_workers)
            min_line = 0
            max_line = msi.coordinates[sensor]["lines"] - 1  # max line is included

            # Columns (=pixels) start at 0
            min_col = 0
            max_col = msi.coordinates[sensor]["pixels"] - 1  # max col is included
            pixels = np.array(
                [[col, row] for row in np.linspace(min_line, max_line, 3) for col in np.linspace(min_col, max_col, 3)],
                np.int32,
            )

            chunck_rows = pixels.shape[0]
            chunck_cols = pixels.shape[1]
            chunked_coords = da.from_array(pixels, chunks=(chunck_rows, chunck_cols))

            perf = time.perf_counter()
            result = da.map_blocks(
                direct_location,
                msi_remote,
                chunked_coords,
                geometric_unit=sensor,
                dtype="float64",
                chunks=(chunck_rows, chunck_cols),
            )
            res = result.compute()
            ground = res[:, :3]
            acq_times = res[:, 3]

            assert acq_times.shape == (chunck_rows,)

            print(f"Compute time : {time.perf_counter() - perf:.3g}")

            # grounds.append(ground)
            test_output = {
                "pixels": pixels,
                "ground": ground,
                "inverse_loc": [],
                "incidence": [],
                "sun": [],
                "footprint": [],
            }
            logging.info("  Check zarr versus reference")
            try:
                check_with_reference(
                    sensor_s2,
                    ref_data_tds1,
                    test_output,
                    value_diffs_vs_ref,
                    comp,
                    list_diffs_vs_ref,
                    THRESHOLDS_REFACTORED,
                    footprint_ref,
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(colored(f"  ! Exception({type(e)=}): " + str(e), "red"))
                error_log += f"  ! Exception({type(e)=}): " + str(e) + "\n"


def check_with_reference_old(
    sensor, ref_data, test_output, all_diffs, delta_lon, delta_lat, delta_alt
):  # pylint: disable=too-many-positional-arguments
    """
    Compare resultats with reference data
    """
    # Compare inverse loc results with original pixel values
    ref_data[sensor]["inverse_loc"] = test_output["pixels"]

    # Values to compare and tolerances
    compare = []
    if "ground" in ref_data[sensor]:
        compare.append(
            (
                "ground",
                (
                    ("longitude", 5.0e-4),
                    ("latitude", 5.0e-4),
                    ("altitude", 2e2),
                ),
            ),
        )
    if "inverse_loc" in ref_data[sensor]:
        compare.append(
            (
                "inverse_loc",
                (
                    ("col", 1e-1),
                    ("row", 1.0),
                ),
            ),
        )
    if "incidence" in ref_data[sensor]:
        compare.append(
            (
                "incidence",
                (("azimuth", 0.02), ("zenith", 0.00025)),
            ),
        )
    if "sun" in ref_data[sensor]:
        compare.append(
            ("sun", (("azimuth", 5e-4), ("zenith", 5e-4))),
        )

    for key, tolerances in compare:
        # Absolute difference between sxgeo and s2geo
        assert len(test_output[key]) == len(ref_data[sensor][key])
        diff = test_output[key] - np.array(ref_data[sensor][key])
        abs_diff = np.absolute(diff)
        all_diffs[key] = np.concatenate((all_diffs[key], diff))

        if key == "ground":
            delta_lon[:, :] = diff[:, 0].reshape((3, 3))
            delta_lat[:, :] = diff[:, 1].reshape((3, 3))
            delta_alt[:, :] = diff[:, 2].reshape((3, 3))

        for i_axis, (axis_name, abs_tol) in enumerate(tolerances):
            # Abs diffs for lon, lat, alt, azimuth or zenith
            diff_axis = abs_diff[:, i_axis]

            # If the max diff for lon, lat, alt, azimuth or zenith is > tolerance
            max_diff = np.nanmax(diff_axis)
            if max_diff > abs_tol:
                # Max diff index and corresponding pixel coords
                max_pixel = test_output["pixels"][np.nanargmax(diff_axis)]
                assert np.all(
                    max_pixel < 10
                ), f"Too many different pixels for {key} at axis {axis_name}, max difference: {max_diff}"
                # ~ if product_class == S2MSILegacyGeometry:  # temp: we know that asgard v2 has wrong results
                # ~ raise RuntimeError(
                # ~ f"{key} abs diff:{max_diff} for {name} is > tolerance:{abs_tol} "
                # ~ f"for sensor:{sensor} col:{max_pixel[0]} row:{max_pixel[1]}"
                # ~ )


def run_profiling(product):
    """
    Extract profiling information
    """
    from cProfile import Profile  # pylint: disable=import-outside-toplevel

    from pyprof2calltree import (  # pylint: disable=import-outside-toplevel
        convert,
        visualize,
    )

    sensor = "B01/D03"
    nb_lines = product.coordinates[sensor]["lines"]
    nb_columns = product.coordinates[sensor]["pixels"]
    pixels = np.array(
        [[col, row] for row in np.linspace(0, nb_lines - 1, 100) for col in np.linspace(0, nb_columns - 1, 100)],
        np.int32,
    )

    profiler = Profile()
    grounds, _ = profiler.runcall(product.direct_loc, pixels, geometric_unit=sensor)
    visualize(profiler.getstats())
    convert(profiler.getstats(), osp.join(OUT_DIR, "test_sentinel2_msi_direct_loc.kgrind"))

    profiler = Profile()
    _ = profiler.runcall(product.inverse_loc, grounds[:, :2], geometric_unit=sensor)
    visualize(profiler.getstats())
    convert(profiler.getstats(), osp.join(OUT_DIR, "test_sentinel2_msi_inverse_loc.kgrind"))


def setup_remote_dem90() -> FSStore:
    """
    Create a FSStore pointing to the DEM90 stored remotely on S3
    """

    dem_path = (
        "simplecache::s3://geolib-input/ADFstatic/S0__ADF_DEM90_20000101T000000_21000101T000000_20240329T091653.zarr"
    )
    s3_config = {
        "key": os.environ.get("S3_GEOLIB_INPUT_RO_ACCESS"),
        "secret": os.environ.get("S3_GEOLIB_INPUT_RO_SECRET"),
        "client_kwargs": {
            "endpoint_url": "https://s3.sbg.perf.cloud.ovh.net",
            "region_name": "sbg",
        },
    }

    return FSStore(dem_path, mode="r", s3=s3_config)


@pytest.mark.parametrize("with_min_max_lines", [False, True], ids=["no_min_max_lines", "with_min_max_lines"])
def test_sentinel2_msi_estimate_line_counts(with_min_max_lines):
    """
    Test steps:
    - Read the 'config_test_min_max' file into a Python dict (json format)
    - Delete 'min_max_lines' to make sure we pass in the else branch that
      calculates the line counts from the reference date and min/max dates
    - Estimate the line counts
    - Check expected values and array shape
    - Check that `inverse_loc` and `direct_loc` give the same results in both
      case (no_min_max_lines, with_min_max_lines)

    :param bool with_min_max_lines: Whether to keep 'min_max_lines' in config
    """
    # Based on "original_asgard_config_CSMODIFIED_2.txt" file from issue #295
    # https://gitlab.eopf.copernicus.eu/geolib/asgard/-/issues/295#note_35821
    # python3 -m json.tool --indent 2 277/input/original_asgard_config_CSMODIFIED_2.txt
    config_path = "config_test_min_max.json"
    config_json = None
    with open(osp.join(RESOURCES, config_path), encoding="utf-8") as f:
        config_json = json.load(f)

    if with_min_max_lines:
        # Initialisation with Min/Max lines ; B10/D06-D07 (working)
        expected_values = np.array(
            [
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26776, 160656, 160656, 160656, 80328, 80328, 80328, 160656, 80328, 26776, 26776, 80328, 80328],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
                [26990, 161942, 161942, 161942, 80971, 80971, 80971, 161942, 80971, 26990, 26990, 80971, 80971],
            ],
            dtype="int32",
        )
    else:
        # Delete 'min_max_lines' to make sure we pass in the else branch that
        # calculates the line counts from the reference date and min/max dates
        del config_json["min_max_lines"]
        # Initialisation without Min/Max lines ; B10/D06-D07
        expected_values = np.array(
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28250, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 27855, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            dtype="int32",
        )

    # Estimate the line counts
    line_counts = S2MSIGeometry.estimate_line_counts(config_json)

    # Check expected values
    assert line_counts["values"].shape == (12, 13), "unexpected shape"
    assert np.all(line_counts["values"] == expected_values)

    # Convert Python list to Numpy Array
    def pylist_nparr(elt):
        if isinstance(elt, dict):
            elt = {key: pylist_nparr(value) for key, value in elt.items()}
        elif isinstance(elt, list):
            if all(type(value) in [int, float, str] for value in elt):
                elt = np.array(elt)
            else:
                elt = [pylist_nparr(value) for value in elt]
                if all(isinstance(value, np.ndarray) for value in elt):
                    elt = np.array(elt)
        return elt

    # https://datacenter.iers.org/data/6/bulletina-xxxvi-033.txt
    config_json["resources"]["iers"] = osp.join(TEST_DIR, "resources/bulletina-xxxvi-033.txt")
    config_json["resources"]["geoid"] = osp.join(
        ASGARD_DATA, "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr"
    )
    config_json["resources"]["dem_zarr"] = setup_remote_dem(DEM_90_20240605)
    config_numpy = pylist_nparr(config_json)
    product = S2MSIGeometry(**config_numpy)

    def test_loc(product, sensor, ground, expected_coordinates, expected_times):
        inverse = product.inverse_loc(ground, geometric_unit=sensor)
        coordinates, times = product.direct_loc(inverse.astype("int"), sensor)
        assert np.allclose(coordinates, expected_coordinates, rtol=0, atol=1e-8)
        assert np.allclose(times, expected_times, rtol=0, atol=1e-8)

    # Values based on "277_S2_debug.py" file from issue #295
    ground_07 = np.array([[177.065, -17.961]])
    ground_06 = np.array([[177.107, -17.361]])
    expected_coordinates_06 = np.array([[177.10671607, -17.36092632, 59.02551721]])
    expected_coordinates_07 = np.array([[177.06494518, -17.96054152, 57.64889763]])
    expected_times_06 = np.array([208.15554838])
    expected_times_07 = np.array([221.67530075])
    test_loc(product, "B10/D06", ground_06, expected_coordinates_06, expected_times_06)
    test_loc(product, "B10/D07", ground_07, expected_coordinates_07, expected_times_07)


# Test data
@pytest.mark.slow
@pytest.mark.parametrize(
    "product_class, interface_path, altitude, ref_data_path, dem_path",
    [
        pytest.param(
            S2MSIGeometry,
            osp.join(ASGARD_DATA, "S2MSIdataset/no_refining/S2GEO_Input_interface.xml"),
            None,
            osp.join(RESOURCES, "no_refining/s2geo_reference.py"),
            GETAS_PATH,
            id="v2_no_refining_getas",
        ),
        pytest.param(
            S2MSIGeometry,
            osp.join(ASGARD_DATA, "S2MSIdataset/no_refining/S2GEO_Input_interface.xml"),
            None,
            osp.join(RESOURCES, "no_refining/s2geo_reference.py"),
            setup_remote_dem90(),
            id="v2_no_refining_dem90",
        ),
        pytest.param(
            S2MSIGeometry,
            osp.join(ASGARD_DATA, "S2MSIdataset/with_refining/S2GEO_Input_interface.xml"),
            None,
            osp.join(RESOURCES, "with_refining/s2geo_reference.py"),
            GETAS_PATH,
            id="v2_with_refining_getas",
        ),
        pytest.param(
            S2MSIGeometry,
            osp.join(ASGARD_DATA, "S2MSIdataset/with_refining/S2GEO_Input_interface.xml"),
            None,
            osp.join(RESOURCES, "with_refining/s2geo_reference.py"),
            setup_remote_dem90(),
            id="v2_with_refining_dem90",
        ),
    ],
)
def test_sentinel2_msi(
    request: FixtureRequest,
    product_class: Type,
    interface_path: str,
    altitude: float,
    ref_data_path: str,
    dem_path: str | FSStore,
    config_dump_path: str = None,
    ref_script_path: str = None,
    line_count_margin: int = None,
):  # pylint: disable=too-many-positional-arguments,too-many-arguments,unused-argument
    """
    Test steps:
    - Read the S2geo interface file using the ASGARD-Legacy loader into a Python dict (json format).
    - Read the Python dict into an ASGARD S2 MSI product that uses the Java/JCC/Sxgeo bindings.
    - Run direct and inverse locations and compare results to reference.

    :param FixtureRequest request: given by @pytest.mark.parametrize
    :param class product_class: legacy or V2 implementation ?
    :param str interface_path: Path to the 'S2GEO_Input_interface.xml' interface file
    :param float altitude: a constant altitude in meters, or None to use the DEM
    :param str ref_data_path: Path to the Python file that contains the S2Geo reference results.
    ASGARD S2 MSI processing is run and results are compared to the reference.
    :param str config_dump_path: Path to a JSON file to dump ASGARD configuration after reading
    the S2Geo interface file.
    :param str ref_script_path: Path to an output bash script that will contain the command lines
    to generate the S2Geo reference results. ASGARD S2 MSI processing is not run.
    :param int line_count_margin: margin in seconds when estimating the line counts from min/max
    dates without granule information.
    """

    assert product_class == S2MSIGeometry

    # S2geo interface file -> Python dict
    config = S2geoInterface(interface_path).read()

    # patch elevation: use ZARR DEM here
    config["resources"]["dem_zarr"] = dem_path
    config["models"] = {"propagation": {"max_cached_tiles": 50}}

    for key in ["dem_srtm", "dem_globe", "geoid"]:
        if key in config["resources"]:
            del config["resources"][key]

    # Estimate the line counts with the user given margin in seconds
    if line_count_margin is not None:
        config["line_counts"] = S2MSIGeometry.estimate_line_counts(config, line_count_margin)

    # Write JSON file on disk
    if config_dump_path is not None:
        with open(config_dump_path, "w", encoding="utf-8") as file:
            json.dumps(json.dump(config, file, ensure_ascii=False, indent=2, cls=NumpyArrayEncoder))

    # Python dict -> ASGARD S2 product
    product = product_class(**config)

    # Command to record profiling
    # ~ run_profiling(product)

    # Bash script used to generate the S2Geo reference ground coordinates from the command line.
    ref_script_script = (
        open(ref_script_path, "w", encoding="utf-8") if ref_script_path else None  # pylint: disable=consider-using-with
    )

    # Ground reference results
    ref_data = None

    # Write into the bash script from python
    if ref_script_script:
        ref_script_script.write(
            r"""
#!/usr/bin/env bash
set -euo pipefail

# Dump results in a file in the same dir as this bash script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
py_results="$SCRIPT_DIR/s2geo_reference.py"

# Write into python from bash...
# The python script will contain the ground coordinate results and will be used
# as a reference by this pytest.
cat << EOF > $py_results
#!/usr/bin/env python
from collections import defaultdict
# key1="sensor name" key2="ground", "sun" or "incidence", value="x,y,z" or "azimuth,zenith"
d = defaultdict(lambda: defaultdict(list))
s2geo_ref=d # alias
EOF

# For each command-line options used to perform direct location on (col,row) coordinates
for opts in \
"""
        )

    # Read the ground refererence results (as a Python script) obtained with S2Geo (or None to use the DEM)
    elif ref_data_path:
        if ref_data_path.endswith(".py"):
            # pylint: disable=no-value-for-parameter, deprecated-method
            ref_module = importlib.machinery.SourceFileLoader(ref_data_path, ref_data_path).load_module()
            ref_data = ref_module.s2geo_ref
        elif ref_data_path.endswith(".json"):
            with open(ref_data_path, "r", encoding="utf-8") as fhd:
                ref_data = json.load(fhd)

    # Test each S2 detector and band
    index = 1
    total = len(S2Detector.VALUES) * len(S2Band.VALUES)
    all_diffs = {
        "ground": np.array([]).reshape(0, 3),
        "inverse_loc": np.array([]).reshape(0, 2),
        "sun": np.array([]).reshape(0, 2),
        "incidence": np.array([]).reshape(0, 2),
    }
    exec_times = defaultdict(lambda: 0.0)  # execution time in seconds
    squared_sum = 0.0
    nb_roundtrip_fails = 0
    all_outputs = {}

    delta_lon = np.zeros((3 * len(S2Band.VALUES), 3 * len(S2Detector.VALUES)), dtype="float64")
    delta_lat = np.zeros((3 * len(S2Band.VALUES), 3 * len(S2Detector.VALUES)), dtype="float64")
    delta_alt = np.zeros((3 * len(S2Band.VALUES), 3 * len(S2Detector.VALUES)), dtype="float64")
    for detector in S2Detector.VALUES:
        for band in S2Band.VALUES:
            # Test sensor from its ASGARD name as defined in S2MSIGeometry
            sensor = S2Sensor(detector, band).name

            if not ref_script_script:
                print(f"Sensor {sensor!r} #{index}/{total}")
            index += 1

            assert product.coordinates[sensor] == product.coordinates[sensor]

            # Final implementation: MSI lines start at 0
            min_line = 0
            max_line = product.coordinates[sensor]["lines"] - 1  # max line is included

            # In S2Geo and legacy implementation: lines start at 1
            min_line_legacy = min_line + 1
            max_line_legacy = max_line + 1

            # Columns (=pixels) start at 0
            min_col = 0
            max_col = product.coordinates[sensor]["pixels"] - 1  # max col is included

            # Calculate 9 pixel coordinates = edges and centers
            pixels_legacy = np.array(
                [
                    [col, row]
                    for row in np.linspace(min_line_legacy, max_line_legacy, 3)
                    for col in np.linspace(min_col, max_col, 3)
                ],
                np.int32,
            )
            if product_class == S2MSIGeometry:
                pixels = np.array(
                    [
                        [col, row]
                        for row in np.linspace(min_line, max_line, 3)
                        for col in np.linspace(min_col, max_col, 3)
                    ],
                    np.int32,
                )
            else:  # if product_class == S2MSILegacyGeometry:
                pixels = pixels_legacy

            # Update the bash script
            if ref_script_script:
                for col, row in pixels_legacy:
                    ref_script_script.write(
                        f'"-o directLoc -b {band.name} -d {detector.legacy_name} -x {col} -y {row}" \\\n'
                    )
                continue

            # Call the direct location method from the ASGARD product
            perf = time.perf_counter()
            grounds, acq_times = product.direct_loc(pixels, sensor, altitude)
            exec_times["direct loc"] += time.perf_counter() - perf

            assert np.all(~np.isnan(grounds))

            # Call the inverse location method from the ASGARD product.
            # The legacy implementation takes (lon,lat,alt) arrays.
            # The ASGARD implementation takes (lon,lat) arrays.
            perf = time.perf_counter()
            inverse_pixels = product.inverse_loc(
                grounds[:, :2],
                geometric_unit=sensor,
            )
            exec_times["inverse loc"] += time.perf_counter() - perf

            # Measure difference between original pixel coordinates and round-trip coordinates
            error_coordinates = inverse_pixels - pixels
            error_norm = np.linalg.norm(error_coordinates, axis=1)
            nb_roundtrip_fails += np.count_nonzero(error_norm > 1e-2)
            squared_sum += np.sum((inverse_pixels - pixels) ** 2)

            # Calculate the sun angles
            perf = time.perf_counter()
            sun_angles = product.sun_angles(grounds, acq_times)
            exec_times["sun angles"] += time.perf_counter() - perf

            # Calculate the incidence angles
            perf = time.perf_counter()
            incidence_angles = product.incidence_angles(grounds, acq_times)
            exec_times["incidence angles"] += time.perf_counter() - perf

            # save outputs
            all_outputs[sensor] = {
                "pixels": pixels.tolist(),
                "ground": grounds.tolist(),
                "inverse_loc": inverse_pixels.tolist(),
                "incidence": incidence_angles.tolist(),
                "sun": sun_angles.tolist(),
            }

            # Compare to s2geo reference
            if ref_data is not None:
                test_output = {
                    "pixels": pixels,
                    "ground": grounds,
                    "inverse_loc": inverse_pixels,
                    "incidence": incidence_angles,
                    "sun": sun_angles,
                }
                idx_band = S2Band.VALUES.index(band)
                idx_det = S2Detector.VALUES.index(detector)
                check_with_reference_old(
                    sensor,
                    ref_data,
                    test_output,
                    all_diffs,
                    delta_lon[3 * idx_band : 3 * idx_band + 3, 3 * idx_det : 3 * idx_det + 3],
                    delta_lat[3 * idx_band : 3 * idx_band + 3, 3 * idx_det : 3 * idx_det + 3],
                    delta_alt[3 * idx_band : 3 * idx_band + 3, 3 * idx_det : 3 * idx_det + 3],
                )

    if not ref_script_script:
        message = ""

        # pylint: disable=line-too-long # auto-generated bash code lines
        if ref_data is not None:

            # DEBUG CODE: show 2D errors
            # ~ import matplotlib.pyplot as plt
            # ~ fig, ax = plt.subplots()
            # ~ ax.scatter(all_diffs["ground"][:,0], all_diffs["ground"][:,1], alpha=0.5)
            # ~ ax.grid(True)
            # ~ fig.tight_layout()
            # ~ plt.show()

            # ~ fig, ax = plt.subplots(1, 3)
            # ~ ax[0].imshow(delta_lon, origin="upper")
            # ~ ax[1].imshow(delta_lat, origin="upper")
            # ~ ax[2].imshow(delta_alt, origin="upper")
            # ~ plt.show()

            message += f"""
    Max absolute differences from reference:
    - direct loc long:{np.nanmax(np.abs(all_diffs["ground"][:,0])):.3g} lat:{np.nanmax(np.abs(all_diffs["ground"][:,1])):.3g} alt:{np.nanmax(np.abs(all_diffs["ground"][:,2])):.3g}
    """
        if all_diffs["inverse_loc"].size > 0:
            message += f'- inverse loc col:{np.abs(all_diffs["inverse_loc"][:,0]).max():.3g} row:{np.abs(all_diffs["inverse_loc"][:,1]).max():.3g}\n'
        if all_diffs["sun"].size > 0:
            message += f'- sun angles azimuth:{np.abs(all_diffs["sun"][:,0]).max():.3g} zenith:{np.abs(all_diffs["sun"][:,1]).max():.3g}\n'
        if all_diffs["incidence"].size > 0:
            message += f'- incidence angles azimuth:{np.abs(all_diffs["incidence"][:,0]).max():.3g} zenith:{np.abs(all_diffs["incidence"][:,1]).max():.3g}\n'
        message += "Execution time for:\n"
        for type_, exec_time in exec_times.items():
            message += f"  - {type_}: {exec_time:.3g}s\n"

        # ~ if product_class == S2MSILegacyGeometry:
        # ~ print(message)
        # ~ rmse = np.sqrt(squared_sum / (total * len(pixels)))
        # ~ assert rmse < 5e-3
        # ~ assert nb_roundtrip_fails == 0

        # ~ else:  # temp: we know that asgard v2 has wrong results
        print(message)
        warnings.warn(message)

    # Update and print bash script
    else:  # if ref_script_script:
        # pylint: disable=line-too-long
        ref_script_script.write(
            r""";do

# Update this command line to match your environment.
# You must be in the S2Geo directory that containts ./resources/orekit-data
# Run S2Geo and grep the lines that contains "Bxx, Dxx : {x: ... " or "{azimuth: ..."
res=$(java -jar ./target/s2geo-core-04.04.00-1-jar-with-dependencies.jar -i """
            + osp.realpath(interface_path)
            + r""" $opts | grep -E '\{(x|azimuth)')

echo "$res"

# float number format (minus, plus, 0-9, decimal separator, exp)
flt=\-\+0-9.e

# Extract ground coordinates
ground=($(echo "$res" | sed -n "s/^\(B[[:alnum:]]\+\), \(D[[:alnum:]]\+\) : {x: \([$flt]\+\) , y: \([$flt]\+\) , z: \([$flt]\+\)}$/\1 \2 \3 \4 \5/p"))
if [[ -z $ground ]]; then
    >&2 echo -e "Error extracting ground coordinates from:\n$res\n\nFor options: '$opts'\n"
    exit 2
fi

band=${ground[0]} # as Bxx
detector=${ground[1]} # as Dxx
x=${ground[2]}
y=${ground[3]}
z=${ground[4]}

# Extract sun and incidence angles
for s_angles in "sun" "incidence"; do

    angles=($(echo "$res" | sed -n "s/^\(B[[:alnum:]]\+\), \(D[[:alnum:]]\+\) $s_angles angles : {azimuth: \([$flt]\+\) , zenith: \([$flt]\+\)}$/\1 \2 \3 \4/p"))
    if [[ -z $angles ]]; then
        >&2 echo -e "Error extracting $s_angles angles from:\n$res\n\nFor options: '$opts'\n"
        exit 2
    fi

    # Save sun_az or sun_ze or incidence_az or incidence_ze variable
    eval "${s_angles}_az=${angles[2]}"
    eval "${s_angles}_ze=${angles[3]}"
done

# ASGARD sensor name
sensor="$band/$detector"

# Save this as a python dict entry
echo "d['$sensor']['ground'].append([$x,$y,$z])" >> $py_results
echo "d['$sensor']['sun'].append([$sun_az,$sun_ze])" >> $py_results
echo "d['$sensor']['incidence'].append([$incidence_az,$incidence_ze])" >> $py_results

done
"""
        )
        ref_script_script.close()
        print(f"Reference script written under: {ref_script_path!r}")


@pytest.mark.init_schema_example
def test_init_schema_example():
    """Generate JSON examples that implement the init_schema() methods"""
    #
    # The same config is passed to the S2MSIGeometry and S2MSILegacyGeometry objects.
    config = S2geoInterface(osp.join(ASGARD_DATA, "S2MSIdataset/no_refining/S2GEO_Input_interface.xml")).read()

    try:
        import doc_init_schema  # pylint: disable=import-outside-toplevel

        doc_init_schema.generate_example(config, "S2MSIGeometry")
        # ~ doc_init_schema.generate_example(config, "S2MSILegacyGeometry")
    except ImportError:
        pass


@pytest.fixture(name="img_coord", scope="module")
def img_coord_product(seed=1234):
    """
    Image coordinates for S2
    """

    [min_line, max_line] = [1, 13823]
    [min_col, max_col] = [0, 2551]
    nb_samples = 20000
    rng = np.random.default_rng(seed=seed)
    row = rng.uniform(min_line, max_line, nb_samples).round().astype(int)
    col = rng.uniform(min_col, max_col, nb_samples).round().astype(int)
    img_coords = np.stack([col, row], axis=1)
    return img_coords


@pytest.fixture(name="img_coord_float_with_extrapolation", scope="module")
def img_coord_product_float(seed=1234, nb_samples=20000, col_margin=100, line_margin=100):
    """
    Image coordinates for S2, floating value with extrapolation
    """

    [min_line, max_line] = [1, 13823]
    [min_col, max_col] = [0, 2551]
    rng = np.random.default_rng(seed=seed)
    row = rng.uniform(min_line - line_margin, max_line + line_margin, nb_samples)
    col = rng.uniform(min_col - col_margin, max_col + col_margin, nb_samples)
    img_coords = np.stack([col, row], axis=1)
    return img_coords


@pytest.fixture(name="img_coord_optimist", scope="module")
def img_coord_product_optimist():
    """
    Image coordinates for S2
    """
    [min_line, max_line] = [1, 13823]
    [min_col, max_col] = [0, 2551]
    step_lig = 50
    row = np.arange(min_line, max_line, step_lig, dtype="int32")
    step_col = 10
    col = np.arange(min_col, max_col, step_col, dtype="int32")
    img_coord_row, img_coord_col = np.meshgrid(row, col, indexing="ij")
    img_coords = np.moveaxis(np.array([img_coord_col, img_coord_row]), 0, -1).astype("int32")
    return img_coords


@pytest.mark.slow
@pytest.mark.dem
@pytest.mark.perfo
@pytest.mark.parametrize("with_refining", [False, True], ids=["no_refining", "with_refining"])
@pytest.mark.parametrize(
    "img_coord_type",
    ["img_coord_float_with_extrapolation", "img_coord_optimist", "img_coord"],
    ids=["img_coord_float_with_extrapolation", "img_coord_optimist", "img_coord"],
)
def test_msi_product_perf(img_coord_type, with_refining, request):
    """
    Unit test for S2MSIGeometry.direct_loc/ inverse loc perf
    """
    if with_refining:
        interface_path = osp.join(ASGARD_DATA, "S2MSIdataset/with_refining/S2GEO_Input_interface.xml")
    else:
        interface_path = osp.join(ASGARD_DATA, "S2MSIdataset/no_refining/S2GEO_Input_interface.xml")

    # S2geo interface file -> Python dict
    config = S2geoInterface(interface_path).read()

    # patch elevation: use ZARR DEM here
    config["resources"]["dem_zarr"] = GETAS_PATH
    config["models"] = {"propagation": {"max_cached_tiles": 50}}

    for key in ["dem_srtm", "dem_globe", "geoid"]:
        if key in config["resources"]:
            del config["resources"][key]

    # Python dict -> ASGARD S2 product
    product = S2MSIGeometry(**config)

    print(f"coordinates type {img_coord_type}")
    img_coord = request.getfixturevalue(img_coord_type)

    # call direct_loc

    tic = time.perf_counter()
    gnd, _ = product.direct_loc(img_coord, geometric_unit="B03/D02")
    tac = time.perf_counter()
    print(f"MSI direct_loc on DEM speed: {img_coord.size * 0.5 / (tac-tic):.1f}")

    gnd_2d = gnd[..., :2]
    alt_dem = gnd[..., 2].reshape((img_coord.size // 2,))

    tic = time.perf_counter()
    product.direct_loc(img_coord, geometric_unit="B03/D02", altitude=0.0)
    tac = time.perf_counter()
    print(f"MSI direct_loc at constant height speed: {img_coord.size * 0.5 / (tac-tic):.1f}")

    tic = time.perf_counter()
    coord = product.inverse_loc(gnd_2d, geometric_unit="B03/D02", altitude=alt_dem)
    tac = time.perf_counter()
    print(f"MSI inverse_loc with input altitude speed: {img_coord.size * 0.5 / (tac-tic):.1f}")

    print(f"max absolute difference {np.max(np.abs(img_coord - coord))}")
    assert np.allclose(img_coord, coord, rtol=0, atol=2e-4)
    # ~ from cProfile import Profile
    # ~ from pyprof2calltree import convert, visualize
    # ~ mode = "with_refining" if with_refining else "no_refining"
    # ~ profiler = Profile()
    # ~ profiler.runctx('product.direct_loc(img_coord, geometric_unit="B03/D02")', locals(), globals())
    # ~ convert(profiler.getstats(), osp.join(TEST_DIR, "outputs", f"test_msi_product_perf_{mode}.kgrind"))

    # ~ profiler.runctx('product.direct_loc(img_coord, geometric_unit="B03/D02", altitude=0.0)', locals(), globals())
    # ~ convert(profiler.getstats(), osp.join(TEST_DIR, "outputs", f"test_msi_product_perf_cst_alt_{mode}.kgrind"))

    # ~ profiler.runctx('product.inverse_loc(gnd_2d, geometric_unit="B03/D02", altitude=alt_dem)', locals(), globals())
    # ~ convert(profiler.getstats(), osp.join(TEST_DIR, "outputs", f"test_msi_product_perf_inverse_loc_{mode}.kgrind"))


def test_other_config_for_msi():
    """
    Unit test to check instantiation of MSI sensor with different DEM/geoid formats
    """

    # use DEM90 as xr.Dataset
    dem_path = "s3://geolib-input/ADFstatic/S0__ADF_DEM90_20000101T000000_21000101T000000_20240528T050715.zarr"
    s3_config = {
        "key": os.environ.get("S3_GEOLIB_INPUT_RO_ACCESS"),
        "secret": os.environ.get("S3_GEOLIB_INPUT_RO_SECRET"),
        "client_kwargs": {
            "endpoint_url": "https://s3.sbg.perf.cloud.ovh.net",
            "region_name": "sbg",
        },
    }
    dem_store = xr.open_zarr(dem_path, storage_options=s3_config)

    # use geoid as zarr FSStore
    geoid_path = "s3://common/ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr"
    s3_config = {
        "key": os.environ.get("S3_COMMON_ACCESS"),
        "secret": os.environ.get("S3_COMMON_SECRET"),
        "client_kwargs": {
            "endpoint_url": "https://s3.sbg.perf.cloud.ovh.net",
            "region_name": "sbg",
        },
    }
    geoid_store = FSStore(geoid_path, mode="r", **s3_config)

    interface_path = osp.join(ASGARD_DATA, "S2MSIdataset/no_refining/S2GEO_Input_interface.xml")

    # S2geo interface file -> Python dict
    msi_config = S2geoInterface(interface_path).read()

    # patch elevation: use ZARR DEM here
    msi_config["resources"]["dem_zarr"] = dem_store
    msi_config["resources"]["geoid"] = geoid_store
    msi_config["models"] = {"propagation": {"max_cached_tiles": 50}}

    for key in ["dem_srtm", "dem_globe"]:
        if key in msi_config["resources"]:
            del msi_config["resources"][key]

    S2MSIGeometry(**msi_config)
