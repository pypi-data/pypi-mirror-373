#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
Unit tests for ElevationManager and ZarrManager
"""

import logging
import math
import os
import os.path as osp

import numpy as np
import pytest
import xarray as xr
import zarr
from zarr.storage import FSStore

# isort: off
# pylint: disable=unused-import
import asgard.wrappers.orekit  # JCC initVM() # noqa: F401

# isort: on

# pylint: disable=wrong-import-order
from pyrugged.raster.location import Location
from pyrugged.raster.simple_tile import SimpleTile

from asgard.core.logger import ASGARD_LOGGER_NAME, initialize

# pylint: disable=ungrouped-imports
from asgard.core.math import TWO_PI
from asgard.models.dem import (
    MINUS_90,
    MINUS_180,
    ElevationManager,
    ZarrManager,
    crop_range,
)

logger = logging.getLogger(ASGARD_LOGGER_NAME)

# Resources directory
TEST_DIR = osp.dirname(__file__)

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

initialize(ASGARD_LOGGER_NAME)

# Some reference data, height is relative to MSL
CITIES_ELEVATION = {
    "Paris": {
        "location": [48.859444, 2.355556],
        "height": 46.0,
        "geoid": 44.6100,
    },
    "Toulouse": {
        "location": [43.601111, 1.449722],
        "height": 153.0,
        "geoid": 49.4387,
    },
    "Washington": {
        "location": [38.899722, -77.036944],
        "height": 19,
        "geoid": -32.9403,
    },
    "Pekin": {
        "location": [39.909167, 116.398611],
        "height": 51.0,
        "geoid": -9.0888,
    },
    "Vancouver": {
        "location": [49.276667, -123.111667],
        "height": 10.0,
        "geoid": -19.1758,
    },
    "Ushuaia": {
        "location": [-54.81834, -68.33903],
        "height": 16.0,
        "geoid": 13.2829,
    },
    "VancouverNorth": {
        "location": [50.0, -123.0],
        "height": 1545.0,
        "geoid": -15.0,
        "getasse_height": 1542.0,
    },
    "VancouverNorther": {"location": [50.00001, -123.0], "height": 1545.0, "geoid": -15.0, "getasse_height": 1542.0},
}


def copernicus_dem_latitudinal_zones(latitude) -> tuple[float, float, float]:
    """
    Return the latitudinal zone in Copernicus DEM

    :param latitude: input latitude (in degrees)
    :return: longitude resolution, minimum latitude, maximum latitude (in degrees)
    """

    zones_limits = [-90, -85, -80, -70, -60, -50, 50, 60, 70, 80, 85, 90]
    longitude_sampling = np.array([30.0, 15.0, 9.0, 6.0, 4.5, 3.0, 4.5, 6.0, 9.0, 15.0, 30.0]) / 3600.0

    for pos in range(11):
        if zones_limits[pos] < latitude <= zones_limits[pos + 1]:
            lon_resolution = longitude_sampling[pos]
            lat_min = zones_limits[pos]
            lat_max = zones_limits[pos + 1]
            break

    return lon_resolution, lat_min, lat_max


@pytest.mark.parametrize(
    "initial_range, bounds, expected",
    [
        ((2, 4), (1, 5), (2, 4)),
        ((2, 5), (1, 3), (2, 4)),
        ((1, 4), (3, 5), (2, 4)),
        ((2, 4), (4, 5), (3, 4)),
        ((0, 3), (-1, 0), (0, 1)),
        ((2, 4), (0, 2), (2, 3)),
    ],
    ids=["normal", "right", "left", "single", "zero", "single_left"],
)
def test_crop_range(initial_range, bounds, expected):
    """
    Unit test for crop_range function
    """
    output = crop_range(initial_range[0], initial_range[1], bounds[0], bounds[1])

    assert output == expected


@pytest.fixture(name="manager", scope="module")
def given_a_zarr_dem_manager():
    """
    Initialize a ZarrDemManager instance. This version has flipped coordinates values that we correct
    by default.
    """
    dem_path = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20230428T185052.zarr",
    )
    return ZarrManager(dem_path, tile_lon=1000, flip_lat=True, shift_lon=MINUS_180, shift_lat=MINUS_90)


def test_zarr_dem_manager_is_initialized(manager):
    """
    Check the instance is correctly initialized
    """

    assert isinstance(manager.dem, zarr.hierarchy.Group)

    assert "getasse_height" in manager.layers
    layer = manager.layers["getasse_height"]

    assert layer["chunks"] == (1800, 1000)

    assert isinstance(layer["lon"], np.ndarray)
    assert len(layer["lon"]) == 43201
    assert isinstance(layer["lat"], np.ndarray)

    assert np.allclose(layer["resolution"], (-np.radians(30.0 / 3600.0), np.radians(30.0 / 3600.0)))


@pytest.fixture(name="elev_geoid", scope="module")
def given_an_geoid_manager():
    """
    Initialize an ElevationManager instance with geoid
    """

    geoid_path = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr",
    )
    return ElevationManager(geoid_path)


@pytest.fixture(name="elev_getasse_old", scope="module")
def given_a_getasse_manager_with_flipped_coord():
    """
    Initialize a ElevationManager instance on GETASSE, which give elevation relative to ellipsoid.
    This version has flipped coordinates values that we correct by default.
    """
    dem_path = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20230428T185052.zarr",
    )
    return ElevationManager(dem_path, tile_lon=1000, flip_lat=True, shift_lon=MINUS_180, shift_lat=MINUS_90)


@pytest.fixture(name="elev_getasse", scope="module")
def given_a_getasse_manager():
    """
    Initialize a ElevationManager instance on GETASSE, which give elevation relative to ellipsoid.
    This version has correct coordinates values.
    """
    dem_path = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240325T113307.zarr",
    )
    return ElevationManager(dem_path, tile_lon=1000)


@pytest.fixture(name="elev_getasse_xarray", scope="module")
def given_a_getasse_xarray_manager():
    """
    Initialize a ElevationManager instance on GETASSE, which give elevation relative to ellipsoid.
    This version has correct coordinates values, and is xarray compatible
    """
    dem_path = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr",
    )
    return ElevationManager(dem_path, tile_lon=1000)


@pytest.fixture(name="elev_getasse_dataset", scope="module")
def given_a_getasse_dataset_manager():
    """
    Initialize a ElevationManager instance on GETASSE, which give elevation relative to ellipsoid.
    This version has correct coordinates values, and is xarray compatible. The DEM is passed directly
    as an opened xarray.Dataset
    """
    dem_path = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr",
    )
    dataset = xr.open_zarr(dem_path)
    return ElevationManager(dataset, tile_lon=1000)


@pytest.fixture(name="dem90_store", scope="module")
def given_a_remote_store():
    """
    Initialize the FSStore to DEM90
    """

    dem_path = "s3://geolib-input/ADFstatic/S0__ADF_DEM90_20000101T000000_21000101T000000_20240329T091653.zarr"
    s3_config = {
        "key": os.environ.get("S3_GEOLIB_INPUT_RO_ACCESS"),
        "secret": os.environ.get("S3_GEOLIB_INPUT_RO_SECRET"),
        "client_kwargs": {
            "endpoint_url": "https://s3.sbg.perf.cloud.ovh.net",
            "region_name": "sbg",
        },
    }
    return FSStore(dem_path, mode="r", **s3_config)


@pytest.fixture(name="geoid_store", scope="module")
def given_a_remote_geoid():
    """
    Initialize the FSStore to GEOI8
    """

    geoid_path = "s3://common/ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr"
    s3_config = {
        "key": os.environ.get("S3_COMMON_ACCESS"),
        "secret": os.environ.get("S3_COMMON_SECRET"),
        "client_kwargs": {
            "endpoint_url": "https://s3.sbg.perf.cloud.ovh.net",
            "region_name": "sbg",
        },
    }
    return FSStore(geoid_path, mode="r", **s3_config)


@pytest.fixture(name="elev_dem90", scope="module")
def given_an_elevation_manager_on_remote_zarr(dem90_store, geoid_store):
    """
    Initialize an ElevationManager instance on Copernicus DEM, which give elevation relative to MSL
    """

    return ElevationManager(
        dem90_store,
        geoid_path=geoid_store,
        tile_lon=1000,
        flip_lat=False,
        shift_lon=None,
        shift_lat=None,
    )


@pytest.fixture(name="elev_dem90_500x500", scope="module")
def given_an_elevation_manager_on_remote_zarr_500pix(dem90_store):
    """
    Initialize an ElevationManager instance on Copernicus DEM, which give elevation relative to MSL
    """

    geoid_path = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr",
    )
    return ElevationManager(
        dem90_store,
        geoid_path=geoid_path,
        tile_lon=500,
        tile_lat=500,
        flip_lat=False,
        shift_lon=None,
        shift_lat=None,
    )


@pytest.mark.parametrize("context", list(CITIES_ELEVATION.values()), ids=list(CITIES_ELEVATION.keys()))
def test_elevation_manager_geoid(context, elev_geoid):
    """
    Check elevation manager setup with only geoid
    """

    latitude = np.radians(context["location"][0])
    longitude = np.radians(context["location"][1])
    tile = SimpleTile()
    elev_geoid.update_tile(latitude, longitude, tile)

    lon_geoid = (longitude - tile.minimum_longitude + TWO_PI) % TWO_PI + tile.minimum_longitude

    altitude = tile.interpolate_elevation(latitude, lon_geoid)
    assert np.allclose(altitude, context["geoid"], rtol=0, atol=0.5)


@pytest.mark.parametrize("convention", ["flipped", "good", "xarray", "dataset"])
@pytest.mark.parametrize("context", list(CITIES_ELEVATION.values()), ids=list(CITIES_ELEVATION.keys()))
def test_elevation_manager_getasse(
    context,
    convention,
    elev_getasse_old,
    elev_getasse,
    elev_getasse_xarray,
    elev_getasse_dataset,
):
    """
    Check elevation manager setup with GETASSE
    """
    if convention == "flipped":
        elev = elev_getasse_old
        threshold = 40.0
    elif convention == "good":
        elev = elev_getasse
        threshold = 6.0
    elif convention == "xarray":
        elev = elev_getasse_xarray
        threshold = 6.0
    elif convention == "dataset":
        elev = elev_getasse_dataset
        threshold = 6.0

    latitude = np.radians(context["location"][0])
    longitude = np.radians(context["location"][1])
    tile = SimpleTile()
    elev.update_tile(latitude, longitude, tile)

    assert np.allclose(tile.latitude_step, np.radians(30.0 / 3600.0))
    assert np.allclose(tile.longitude_step, np.radians(30.0 / 3600.0))

    altitude = tile.interpolate_elevation(latitude, longitude)

    ref_from_ellipsoid = context.get("getasse_height", context["height"] + context["geoid"])

    # validate with large tolerance (6m) because the source of reference data is unknown
    assert np.allclose(altitude, ref_from_ellipsoid, rtol=0, atol=threshold)


@pytest.mark.parametrize("context", list(CITIES_ELEVATION.values()), ids=list(CITIES_ELEVATION.keys()))
def test_elevation_manager_dem90(context, elev_dem90):
    """
    Check elevation manager setup with Copernicus DEM90
    """
    latitude = np.radians(context["location"][0])
    longitude = np.radians(context["location"][1])
    tile = SimpleTile()
    elev_dem90.update_tile(latitude, longitude, tile)

    lat_resolution = 3.0 / 3600.0
    lon_resolution, lat_min, lat_max = copernicus_dem_latitudinal_zones(context["location"][0])

    assert tile.get_location(latitude, longitude) == Location.HAS_INTERPOLATION_NEIGHBORS

    assert np.allclose(tile.latitude_step, np.radians(lat_resolution))
    assert np.allclose(tile.longitude_step, np.radians(lon_resolution))

    assert lat_min - lat_resolution <= np.degrees(tile.minimum_latitude)
    assert np.degrees(tile.maximum_latitude) <= lat_max + lat_resolution

    altitude = tile.interpolate_elevation(latitude, longitude)

    ref_from_ellipsoid = context["height"] + context["geoid"]
    # validate with large tolerance (5m) because the source of reference data is unknown
    assert np.allclose(altitude, ref_from_ellipsoid, atol=5)


def test_bug_tile_extent(elev_dem90, elev_dem90_500x500):
    """
    Try to reproduce a problem at the edge of a tile
    """

    latitude = 0.9487219159192757
    longitude = 2.1816618439571145

    tile = SimpleTile()
    elev_dem90.update_tile(latitude, longitude, tile)
    assert tile.get_location(latitude, longitude) == Location.HAS_INTERPOLATION_NEIGHBORS

    latitude = 0.9235700369501136  # ~52.91666520198301°
    longitude = 2.1805477751044213  # ~124.93618454012514°

    tile = SimpleTile()
    elev_dem90_500x500.update_tile(latitude, longitude, tile)
    assert tile.get_location(latitude, longitude) == Location.HAS_INTERPOLATION_NEIGHBORS


def test_dem_tiling_mechanism():
    """
    Try to check the DEM tiling is covering the full globe
    """

    latitude = np.float32(0.9235700369501136)  # ~52.9°N
    longitude = np.float32(2.1816618439571145)

    coord_dir = osp.join(TEST_DIR, "resources", "dem_coordinates")
    lat_coord = np.load(osp.join(coord_dir, "lat.npy"))
    lon_coord = np.load(osp.join(coord_dir, "lon_height_50N_60N.npy"))

    lat_res = (lat_coord[-1] - lat_coord[0]) / (len(lat_coord) - 1)
    lon_res = (lon_coord[-1] - lon_coord[0]) / (len(lon_coord) - 1)

    lat_chunk = 500
    lon_chunk = 500

    lat_extent = lat_chunk * lat_res
    lon_extent = lon_chunk * lon_res

    grid_pos_lat = math.floor((latitude - lat_coord[0]) / lat_extent)
    delta_longitude = (longitude - lon_coord[0] + TWO_PI) % TWO_PI
    grid_pos_lon = math.floor(delta_longitude / lon_extent)

    start_lon_idx = grid_pos_lon * lon_chunk
    end_lon_idx = start_lon_idx + lon_chunk

    start_lat_idx = grid_pos_lat * lat_chunk
    end_lat_idx = min(start_lat_idx + lat_chunk, len(lat_coord) - 1)

    # check on actual coords: we do not expect a failure since numpy updates
    assert lon_coord[start_lon_idx] <= longitude <= lon_coord[end_lon_idx]
    assert lat_coord[end_lat_idx] <= latitude <= lat_coord[start_lat_idx]

    # source_lon = np.arange(start=-648000, stop=648000, step=4.5, dtype=np.float32) * (np.pi / 180 / 3600)

    # check made by pyrugged
    start_lon = lon_coord[0] + start_lon_idx * lon_res
    end_lon = start_lon + lon_chunk * lon_res
    assert start_lon <= longitude < end_lon

    # latitudes are flipped
    start_lat = lat_coord[0] + start_lat_idx * lat_res
    end_lat = start_lat + lat_chunk * lat_res
    assert end_lat <= latitude <= start_lat


@pytest.fixture(name="elev_dem90_xarray", scope="module")
def given_a_remote_store_xarray():
    """
    Initialize an elevation manager with xarray Dataset on remote DEM90 (version compatible with xarray)
    """

    dem_path = "s3://geolib-input/ADFstatic/S0__ADF_DEM90_20000101T000000_21000101T000000_20240528T050715.zarr"
    s3_config = {
        "key": os.environ.get("S3_GEOLIB_INPUT_RO_ACCESS"),
        "secret": os.environ.get("S3_GEOLIB_INPUT_RO_SECRET"),
        "client_kwargs": {
            "endpoint_url": "https://s3.sbg.perf.cloud.ovh.net",
            "region_name": "sbg",
        },
    }
    store = xr.open_zarr(dem_path, storage_options=s3_config)

    geoid_path = osp.join(
        ASGARD_DATA,
        "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr",
    )
    return ElevationManager(
        store,
        geoid_path=geoid_path,
        flip_lat=False,
        shift_lon=None,
        shift_lat=None,
    )


@pytest.mark.parametrize("context", list(CITIES_ELEVATION.values()), ids=list(CITIES_ELEVATION.keys()))
def test_elevation_manager_dem90_xarray(context, elev_dem90_xarray):
    """
    Check elevation manager setup with Copernicus DEM90
    """
    latitude = np.radians(context["location"][0])
    longitude = np.radians(context["location"][1])
    tile = SimpleTile()
    elev_dem90_xarray.update_tile(latitude, longitude, tile)

    lat_resolution = 3.0 / 3600.0
    lon_resolution, lat_min, lat_max = copernicus_dem_latitudinal_zones(context["location"][0])

    assert tile.get_location(latitude, longitude) == Location.HAS_INTERPOLATION_NEIGHBORS

    assert np.allclose(tile.latitude_step, np.radians(lat_resolution))
    assert np.allclose(tile.longitude_step, np.radians(lon_resolution))

    assert lat_min - lat_resolution <= np.degrees(tile.minimum_latitude)
    assert np.degrees(tile.maximum_latitude) <= lat_max + lat_resolution

    altitude = tile.interpolate_elevation(latitude, longitude)

    ref_from_ellipsoid = context["height"] + context["geoid"]
    # validate with large tolerance (5m) because the source of reference data is unknown
    assert np.allclose(altitude, ref_from_ellipsoid, atol=5)
