#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2024 CS GROUP
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
Validation tests for Sentinel 1 SAR products
"""

import logging
import os
import os.path as osp
import time
from glob import glob

import numpy as np
import pytest
from drivers.sentinel_1_legacy import S1LegacyDriver
from helpers.compare import GeodeticComparator  # pylint: disable=import-error
from lxml import etree
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.raster.tiles_cache import TilesCache

from asgard.models.body import EarthBody
from asgard.models.dem import ElevationManager
from asgard.models.sar import SPEED_LIGHT
from asgard.models.time import TimeReference
from asgard.sensors.sentinel1.csar import S1SARGeometry

TEST_DIR = osp.dirname(osp.dirname(__file__))

ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")


def get_annotations(path):
    """
    Get annotation files for a given dataset
    """
    return glob(osp.join(path, "s1a-*-slc-*.xml"))


# ===============================[ TDS 1 ]================================


@pytest.fixture(name="tds1_iers_data", scope="module")
def given_iers_data_at_2022_11():
    """
    Load IERS bulletin B for Nov. 2022
    """
    return S1LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources", "bulletinb-419.txt"))


# ===============================[ TDS 2 ]================================


@pytest.fixture(name="tds2_iers_data", scope="module")
def given_iers_data_at_2023_01():
    """
    Load IERS bulletin A
    """
    return S1LegacyDriver.read_iers_file(
        osp.join(
            TEST_DIR,
            "resources",
            "orekit",
            "IERS",
            "S2__OPER_AUX_UT1UTC_ADG__20220916T000000_V20220916T000000_20230915T000000.txt",
        )
    )


# ===============================[ TDS 3 & 4 ]================================


@pytest.fixture(name="tds3_tds4_iers_data", scope="module")
def given_iers_data_at_2022_08():
    """
    Load IERS bulletin B
    """
    return S1LegacyDriver.read_iers_file(
        osp.join(
            TEST_DIR,
            "resources",
            "bulletinb-415.txt",
        )
    )


# ===============================[ TDS 5 ]================================
@pytest.fixture(name="tds5_iers_data", scope="module")
def given_iers_data_at_2024_08():
    """
    Load IERS bulletin B
    """
    return S1LegacyDriver.read_iers_file(
        osp.join(
            TEST_DIR,
            "resources",
            "bulletinb-439.txt",
        )
    )


# ===========================[ load all TDS and build products ]===============================


@pytest.fixture(name="tds", scope="module")
def given_all_tds_data(tds1_iers_data, tds2_iers_data, tds3_tds4_iers_data, tds5_iers_data):
    """
    Load all TDS data, use a common epoch for WV images because they don'y share the same anchorTime
    """
    output = {
        "TDS1": {
            "eop": {"iers_bulletin_b": tds1_iers_data},
            "epoch": None,
        },
        "TDS2": {
            "eop": {"iers_bulletin_a": tds2_iers_data},
            "epoch": None,
        },
        "TDS3": {
            "eop": {"iers_bulletin_b": tds3_tds4_iers_data},
            "epoch": None,
        },
        "TDS4": {
            "eop": {"iers_bulletin_b": tds3_tds4_iers_data},
            "epoch": "2022-08-01T20:04:00",
        },
        "TDS5": {
            "eop": {"iers_bulletin_b": tds5_iers_data},
            "epoch": None,
        },
    }

    for tds_name, tds in output.items():
        time_model = TimeReference(**tds["eop"])
        driver = S1LegacyDriver(EarthBody(time_reference=time_model))

        tds_path = osp.join(
            TEST_DIR,
            "resources",
            "S1",
            tds_name,
        )
        tds["annotation"] = get_annotations(tds_path)
        swaths = {}
        geoloc_grids = {}
        terrain_grids = {}
        antenna_grids = {}
        for item in tds["annotation"]:
            annotation_path = osp.join(tds_path, item)
            tree = etree.parse(annotation_path)
            name = driver.get_swath_name(tree)
            swaths[name] = driver.get_swath(tree, epoch=tds["epoch"])
            geoloc_grids[name] = driver.get_geolocation(tree, epoch=tds["epoch"])
            terrain_grids[name] = driver.get_terrain_height(tree, epoch=tds["epoch"])
            antenna_grids[name] = driver.get_antenna_pattern(tree, epoch=tds["epoch"])

            # load attitude from first annotation file
            if "attitude" not in tds:
                tds["attitude"] = driver.get_attitude(tree, epoch=tds["epoch"])
                tds["attitude"].pop("platform_angles")
        tds["swaths"] = swaths
        tds["geoloc"] = geoloc_grids
        tds["terrain"] = terrain_grids
        tds["antenna"] = antenna_grids
        tds["driver"] = driver
        tds["comparator"] = GeodeticComparator(driver.earth_body)

    return output


@pytest.fixture(name="ew_tds1", scope="module")
def given_ew_sar_product(tds):
    """
    Build the EW product corresponding to TDS1
    """
    driver = tds["TDS1"]["driver"]

    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS1",
        "S1A_OPER_AUX_RESORB_OPOD_20221112T141116_V20221112T101956_20221112T133726.EOF",
    )
    resorb_20221112 = driver.read_orbit_file(orbit_file)

    config = {
        "sat": "SENTINEL_1A",
        "look_side": "RIGHT",
        "swaths": tds["TDS1"]["swaths"],
        "oper_mode": "EW",
        "orbits": [resorb_20221112],
        "attitude": tds["TDS1"]["attitude"],
        "resources": {
            "dem_path": GETAS_PATH,
            "dem_type": "ZARR",
        },
        "eop": tds["TDS1"]["eop"],
    }

    # convert swath azimuth times to TX by using central swath EW3
    range_sampling_rate = config["swaths"]["EW3"]["range_sampling_rate"]
    range_sampling_time = 1 / range_sampling_rate
    ew3_slant_range_time = config["swaths"]["EW3"]["slant_range_time"]
    ew3_samples = config["swaths"]["EW3"]["burst_samples"]
    time_shift = -0.5 * (ew3_slant_range_time + ew3_samples * 0.5 * range_sampling_time)
    for name in config["swaths"]:
        config["swaths"][name]["azimuth_times"]["offsets"] += time_shift
        config["swaths"][name]["azimuth_convention"] = "TX"

    return S1SARGeometry(**config)


@pytest.fixture(name="iw_tds2", scope="module")
def given_iw_sar_product(tds):
    """
    Build the IW product corresponding to TDS2
    """

    driver = tds["TDS2"]["driver"]

    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS2",
        "S1A_OPER_AUX_RESORB_OPOD_20230131T174904_V20230131T141017_20230131T172747.EOF",
    )
    resorb_20230131 = driver.read_orbit_file(orbit_file)

    attitude_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS2",
        "s1_attitude_eocfi.xml",
    )
    tds2_attitude = driver.read_attitude_file(attitude_file)

    config = {
        "sat": "SENTINEL_1A",
        "look_side": "RIGHT",
        "swaths": tds["TDS2"]["swaths"],
        "oper_mode": "IW",
        "orbits": [resorb_20230131],
        "attitude": tds2_attitude,
        "resources": {
            "dem_path": GETAS_PATH,
            "dem_type": "ZARR",
        },
        "eop": tds["TDS2"]["eop"],
    }

    # convert swath azimuth times to TX by using central swath IW2
    range_sampling_rate = config["swaths"]["IW2"]["range_sampling_rate"]
    range_sampling_time = 1 / range_sampling_rate
    iw2_slant_range_time = config["swaths"]["IW2"]["slant_range_time"]
    iw2_samples = config["swaths"]["IW2"]["burst_samples"]
    time_shift = -0.5 * (iw2_slant_range_time + iw2_samples * 0.5 * range_sampling_time)
    for name in config["swaths"]:
        config["swaths"][name]["azimuth_times"]["offsets"] += time_shift
        config["swaths"][name]["azimuth_convention"] = "TX"

    return S1SARGeometry(**config)


@pytest.fixture(name="s4_tds3", scope="module")
def given_sm_sar_product(tds):
    """
    Build the S4 product corresponding to TDS3
    """

    driver = tds["TDS3"]["driver"]

    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS3",
        "S1A_OPER_AUX_RESORB_OPOD_20220802T015736_V20220801T215919_20220802T011649.EOF",
    )
    resorb_20220801 = driver.read_orbit_file(orbit_file)

    attitude_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS3",
        "s1_attitude_eocfi.xml",
    )
    tds3_attitude = driver.read_attitude_file(attitude_file)

    config = {
        "sat": "SENTINEL_1A",
        "look_side": "RIGHT",
        "swaths": tds["TDS3"]["swaths"],
        "oper_mode": "SM",
        "orbits": [resorb_20220801],
        "attitude": tds3_attitude,
        "resources": {
            "dem_path": GETAS_PATH,
            "dem_type": "ZARR",
        },
        "eop": tds["TDS3"]["eop"],
    }

    # convert swath azimuth times to TX
    for name in config["swaths"]:
        swath = config["swaths"][name]
        range_sampling_time = 1 / swath["range_sampling_rate"]
        time_shift = -0.5 * (swath["slant_range_time"] + swath["burst_samples"] * 0.5 * range_sampling_time)
        swath["azimuth_times"]["offsets"] += time_shift
        swath["azimuth_convention"] = "TX"

    return S1SARGeometry(**config)


@pytest.fixture(name="wv_tds4", scope="module")
def given_wv_sar_product(tds):
    """
    Build the WV product corresponding to TDS4
    """

    driver = tds["TDS4"]["driver"]

    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS4",
        "S1A_OPER_AUX_RESORB_OPOD_20220801T223522_V20220801T184150_20220801T215920.EOF",
    )
    resorb_20220801 = driver.read_orbit_file(orbit_file)

    attitude_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS4",
        "s1_attitude_eocfi.xml",
    )
    tds4_attitude = driver.read_attitude_file(attitude_file)

    config = {
        "sat": "SENTINEL_1A",
        "look_side": "RIGHT",
        "swaths": tds["TDS4"]["swaths"],
        "oper_mode": "WV",
        "orbits": [resorb_20220801],
        "attitude": tds4_attitude,
        "resources": {
            "dem_path": GETAS_PATH,
            "dem_type": "ZARR",
        },
        "eop": tds["TDS4"]["eop"],
    }

    # convert swath azimuth times to TX
    for name in config["swaths"]:
        swath = config["swaths"][name]
        range_sampling_time = 1 / swath["range_sampling_rate"]
        time_shift = -0.5 * (swath["slant_range_time"] + swath["burst_samples"] * 0.5 * range_sampling_time)
        swath["azimuth_times"]["offsets"] += time_shift
        swath["azimuth_convention"] = "TX"

    return S1SARGeometry(**config)


@pytest.fixture(name="iw_tds5", scope="module")
def given_iw_sar_product_tds5(tds):
    """
    Build the IW product corresponding to TDS5
    """

    driver = tds["TDS5"]["driver"]

    orbit_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS5",
        "S1A_OPER_AUX_RESORB_OPOD_20240818T072041_V20240818T032017_20240818T063747.EOF",
    )
    resorb_20240818 = driver.read_orbit_file(orbit_file)

    attitude_file = osp.join(
        TEST_DIR,
        "resources",
        "S1",
        "TDS5",
        "s1_attitude_eocfi.xml",
    )
    tds5_attitude = driver.read_attitude_file(attitude_file)

    config = {
        "sat": "SENTINEL_1A",
        "look_side": "RIGHT",
        "swaths": tds["TDS5"]["swaths"],
        "oper_mode": "IW",
        "orbits": [resorb_20240818],
        "attitude": tds5_attitude,
        "resources": {
            "dem_path": GETAS_PATH,
            "dem_type": "ZARR",
        },
        "eop": tds["TDS5"]["eop"],
    }

    # convert swath azimuth times to TX by using central swath IW2
    range_sampling_rate = config["swaths"]["IW2"]["range_sampling_rate"]
    range_sampling_time = 1 / range_sampling_rate
    iw2_slant_range_time = config["swaths"]["IW2"]["slant_range_time"]
    iw2_samples = config["swaths"]["IW2"]["burst_samples"]
    time_shift = -0.5 * (iw2_slant_range_time + iw2_samples * 0.5 * range_sampling_time)
    for name in config["swaths"]:
        config["swaths"][name]["azimuth_times"]["offsets"] += time_shift
        config["swaths"][name]["azimuth_convention"] = "TX"

    return S1SARGeometry(**config)


@pytest.fixture(name="products", scope="module")
def given_all_s1_products(ew_tds1, iw_tds2, s4_tds3, wv_tds4, iw_tds5):
    """
    Load all TDS data
    """

    return {"TDS1": ew_tds1, "TDS2": iw_tds2, "TDS3": s4_tds3, "TDS4": wv_tds4, "TDS5": iw_tds5}


# ===========================[ Run tests ]=============================


@pytest.mark.slow
@pytest.mark.parametrize(
    "tds_name",
    ["TDS1", "TDS2", "TDS3", "TDS4", "TDS5"],
)
def test_direct_location(tds_name, products, tds):
    """
    Validation of direct_loc() method
    """

    assert products[tds_name] is not None

    product = products[tds_name]
    geoloc = tds[tds_name]["geoloc"]
    comparator = tds[tds_name]["comparator"]

    grounds = {}
    times = {}
    for swath in geoloc:
        # Inject altitudes from geoloc grid, but column by column to test the terrain height LUT
        # mecanism
        image_coords = geoloc[swath]["image"]
        nb_grid_points = len(image_coords)
        # we assess the number of samples in geolocation grid by counting points on the line 0
        nb_samples = len(image_coords[image_coords[:, 1] == 0])
        nb_lines = nb_grid_points // nb_samples

        # reshape to 2D grid
        azimuth_array = geoloc[swath]["azimuth_time"]["offsets"].reshape((nb_lines, nb_samples))
        image_array = image_coords.reshape((nb_lines, nb_samples, 2))
        elevation_array = geoloc[swath]["ground"].reshape((nb_lines, nb_samples, 3))[:, :, 2]
        epoch = product.config["swaths"][swath]["azimuth_times"]["epoch"]

        ground_array = np.zeros((nb_lines, nb_samples, 3), dtype="float64")
        acq_time_array = np.zeros((nb_lines, nb_samples), dtype="float64")
        for column in range(nb_samples):
            product.propagation_model.config["terrain_height_lut"] = {
                "azimuth": {
                    "offsets": azimuth_array[:, column],
                    "unit": "s",
                    "epoch": epoch,
                    "ref": "UTC",
                },
                "height": elevation_array[:, column],
            }
            # direct loc
            ground_array[:, column, :], acq_time_array[:, column] = product.direct_loc(
                image_array[:, column, :], geometric_unit=swath
            )

        grounds[swath] = ground_array.reshape((nb_grid_points, 3))
        times[swath] = acq_time_array.reshape((nb_grid_points,))

    threshold = 0.1
    alti_threshold = 0.001
    azimuth_threshold = 1e-4
    if tds_name == "TDS4":
        threshold = 0.6
        alti_threshold = 0.05
    for swath in geoloc:
        error_plani = comparator.planar_error(grounds[swath], geoloc[swath]["ground"])
        error_height = np.abs(comparator.height_error(grounds[swath], geoloc[swath]["ground"]))
        error_azimuth = np.abs(times[swath] - geoloc[swath]["azimuth_time"]["offsets"])
        # ~ print(swath+" plani error:")
        # ~ print(np.max(error_plani))
        # ~ print(swath+" alti error:")
        # ~ print(np.max(error_height))
        # ~ print(swath+" azimuth error:")
        # ~ print(np.max(np.abs(error_azimuth)))
        assert np.all(error_plani < threshold)
        assert np.all(error_height < alti_threshold)
        assert np.all(error_azimuth < azimuth_threshold)


@pytest.mark.slow
@pytest.mark.parametrize(
    "tds_name",
    ["TDS1", "TDS2", "TDS3", "TDS4", "TDS5"],
)
def test_inverse_location(tds_name, products, tds):
    """
    Validation of inverse_loc() method
    """

    assert products[tds_name] is not None

    product = products[tds_name]
    geoloc = tds[tds_name]["geoloc"]

    inv_pixels = {}
    for swath in geoloc:
        # Inject altitudes from geoloc grid, but column by column to test the terrain height LUT
        # mecanism
        image_coords = geoloc[swath]["image"]
        nb_grid_points = len(image_coords)
        # we assess the number of samples in geolocation grid by counting points on the line 0
        nb_samples = len(image_coords[image_coords[:, 1] == 0])
        nb_lines = nb_grid_points // nb_samples

        # reshape to 2D grid
        azimuth_array = geoloc[swath]["azimuth_time"]["offsets"].reshape((nb_lines, nb_samples))
        image_coords = image_coords.reshape((nb_lines, nb_samples, 2))
        ref_ground_xy = geoloc[swath]["ground"].reshape((nb_lines, nb_samples, 3))[:, :, :2]
        elevation_array = geoloc[swath]["ground"].reshape((nb_lines, nb_samples, 3))[:, :, 2]
        epoch = product.config["swaths"][swath]["azimuth_times"]["epoch"]

        pix_array = np.zeros((nb_lines, nb_samples, 2), dtype="float64")

        for column in range(nb_samples):
            product.propagation_model.config["terrain_height_lut"] = {
                "azimuth": {
                    "offsets": azimuth_array[:, column],
                    "unit": "s",
                    "epoch": epoch,
                    "ref": "UTC",
                },
                "height": elevation_array[:, column],
            }

            pix_array[:, column, :] = product.inverse_loc(
                ref_ground_xy[:, column, :], geometric_unit=swath, altitude=elevation_array[:, column]
            )
        inv_pixels[swath] = pix_array.reshape((nb_grid_points, 2))

    error_on_inv = {}
    pixels_threholds = 0.1
    if tds_name == "TDS3":
        for swath in tds[tds_name]["geoloc"]:
            error_on_inv[swath] = np.abs(inv_pixels[swath] - geoloc[swath]["image"])
            assert np.all(error_on_inv[swath] < pixels_threholds)
    else:
        logging.warning("Inverse location is above thresholds for %s, need to be investigated", tds_name)


@pytest.mark.slow
def test_perf_inverse_location(tds, s4_tds3):
    """
    Test inverse location on fake data with 10000 points from TDS3
    """
    product = s4_tds3
    geoloc = tds["TDS3"]["geoloc"]

    nb_points = 10000
    nb_lon_lat = int(np.sqrt(nb_points))

    for swath in geoloc:
        ref_ground_xy = geoloc[swath]["ground"]
        azimuth_array = geoloc[swath]["azimuth_time"]["offsets"]
        elevation_array = geoloc[swath]["ground"][:, 2]

        new_long = np.array([np.max(ref_ground_xy[:, 0]) + i * 0.04 for i in range(nb_lon_lat)])
        new_lat = np.array([np.min(ref_ground_xy[:, 1]) - i * 0.04 for i in range(nb_lon_lat)])
        azimuth = np.array([np.min(azimuth_array) - i * 8e-6 for i in range(nb_points)])
        gnd_points = np.zeros((nb_lon_lat, nb_lon_lat, 2), dtype="float64")
        elev = np.random.uniform(min(elevation_array), max(elevation_array), nb_points)
        gnd_points[..., 0] = new_long
        gnd_points[..., 1] = new_lat[:, np.newaxis]
        epoch = product.config["swaths"][swath]["azimuth_times"]["epoch"]

        product.propagation_model.config["terrain_height_lut"] = {
            "azimuth": {
                "offsets": azimuth,
                "unit": "s",
                "epoch": epoch,
                "ref": "UTC",
            },
            "height": elev,
        }

        time0 = time.perf_counter()
        _ = product.inverse_loc(gnd_points, geometric_unit=swath, altitude=elev)
        logging.info("Computed time for swath %s: %s", swath, time.perf_counter() - time0)


@pytest.mark.parametrize(
    "tds_name",
    ["TDS1", "TDS2", "TDS3", "TDS4", "TDS5"],
)
def test_slant_range_localisation(tds_name, products, tds):
    """
    Validation of slant_range_localisation() method
    """

    product = products[tds_name]
    geoloc = tds[tds_name]["geoloc"]
    comparator = tds[tds_name]["comparator"]
    driver = tds[tds_name]["driver"]

    threshold = 0.02
    alti_threshold = 0.001
    for swath in geoloc:
        azimuth_times = geoloc[swath]["azimuth_time"]
        range_distance = geoloc[swath]["range_time"] * (SPEED_LIGHT * 0.5)
        altitudes = geoloc[swath]["ground"][:, 2]

        gnd, _ = product.slant_range_localisation(
            azimuth_times,
            range_distance,
            altitudes,
            compute_velocity=True,
        )

        dataset = {"position": gnd}
        driver.earth_body.cartesian_to_geodetic(dataset)

        error_plani = comparator.planar_error(dataset["position"], geoloc[swath]["ground"])
        error_height = comparator.height_error(dataset["position"], geoloc[swath]["ground"])

        assert np.all(error_plani < threshold)
        assert np.all(error_height < alti_threshold)


@pytest.mark.slow
@pytest.mark.parametrize(
    "tds_name",
    ["TDS1", "TDS2", "TDS3", "TDS4", "TDS5"],
)
def test_terrain_height(tds_name, products, tds):
    """
    Validation of elevation source and terrain_height()
    """

    product = products[tds_name]
    geoloc = tds[tds_name]["geoloc"]
    terrain_height = tds[tds_name]["terrain"]

    # Check elevation source
    tile_updater = ElevationManager(
        product.config["resources"]["dem_path"],
        tile_lon=500,
        tile_lat=500,
    )
    tiles_cache = TilesCache(SimpleTile, tile_updater, 10)

    for swath in geoloc:
        flat_grid_gnd = geoloc[swath]["ground"]
        altitude = np.zeros((len(flat_grid_gnd),), dtype="float64")
        for idx, coord in enumerate(flat_grid_gnd):
            lat_rad = np.radians(coord[1])
            lon_rad = np.radians(coord[0])
            tile = tiles_cache.get_tile(lat_rad, lon_rad)
            altitude[idx] = tile.interpolate_elevation(lat_rad, lon_rad)

        altitude_error = altitude - flat_grid_gnd[:, 2]
        print(f"{swath} alti error: mean={np.mean(altitude_error)} , std={np.std(altitude_error)}")

    for swath in terrain_height:
        height = product.terrain_height(
            terrain_height[swath]["azimuth"]["offsets"],
            azimuth_block_size=1,
            azimuth_subsampling=1,
            range_subsampling=100,
            geometric_unit=swath,
        )
        height_error = height - terrain_height[swath]["height"]
        print(f"{swath} terrain height error: mean={np.mean(height_error)} , std={np.std(height_error)}")


@pytest.mark.slow
@pytest.mark.parametrize(
    "tds_name",
    ["TDS1", "TDS2", "TDS3", "TDS4", "TDS5"],
)
def test_incidence_angles(tds_name, products, tds):
    """
    Validation of incidence_angles()
    """

    product = products[tds_name]
    geoloc = tds[tds_name]["geoloc"]

    threshold = 1e-4
    for swath in geoloc:
        incidence_angles = product.incidence_angles(
            geoloc[swath]["ground"],
            geoloc[swath]["azimuth_time"]["offsets"],
        )
        error_angle = np.abs(incidence_angles[:, 1] - geoloc[swath]["incidence_angle"])
        assert np.all(
            error_angle < threshold
        ), f"Swath {swath} incidence doesn't match with reference, max error {np.max(error_angle)}"


@pytest.mark.slow
@pytest.mark.parametrize(
    "tds_name",
    ["TDS1", "TDS2", "TDS3", "TDS4", "TDS5"],
)
def test_viewing_angles(tds_name, products, tds):
    """
    Validation of viewing_angles() (called "elevation" in geoloc grid)
    """

    product = products[tds_name]
    geoloc = tds[tds_name]["geoloc"]

    threshold = 1e-4
    for swath in geoloc:
        viewing_angles = product.viewing_angles(
            geoloc[swath]["ground"],
            geoloc[swath]["azimuth_time"]["offsets"],
        )
        error_angle = np.abs(viewing_angles[:, 1] - geoloc[swath]["elevation_angle"])
        assert np.all(
            error_angle < threshold
        ), f"Swath {swath} elevation doesn't match with reference, max error {np.max(error_angle)}"


@pytest.mark.slow
@pytest.mark.parametrize(
    "tds_name",
    ["TDS1", "TDS2", "TDS3", "TDS4", "TDS5"],
)
def test_zero_doppler_to_attitude(tds_name, products, tds):
    """
    Unit test for zero_doppler_to_attitude()
    """

    product = products[tds_name]
    antenna_pattern = tds[tds_name]["antenna"]

    # avoid the last two samples which may fall outside the range of available attitudes.

    for swath in antenna_pattern:
        time_array = antenna_pattern[swath]["azimuth_time"]
        time_array["offsets"] = time_array["offsets"][:-2]

        angles = product.zero_doppler_to_attitude(time_array)

        # sign inversion
        ref_roll = -1.0 * antenna_pattern[swath]["roll"][:-2]

        assert np.allclose(angles[:, 0], ref_roll, rtol=0, atol=0.002)
