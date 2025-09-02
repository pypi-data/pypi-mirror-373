#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2023 CS GROUP
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
Module for DEM loading classes
"""

import logging
import math
import re
from abc import abstractmethod

import numpy as np
import xarray as xr
import zarr
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.raster.tile_updater import TileUpdater
from zarr.storage import FSStore

from asgard.core.logger import ASGARD_LOGGER_NAME
from asgard.core.math import RADIANS_SCALING_FACTORS, TWO_PI
from asgard.wrappers.orekit import JCC_MODULE_NAME

MINUS_180 = np.radians(-180.0)

MINUS_90 = np.radians(-90.0)

LAT_GROUP_REGEX = "^[0-9a-zA-Z]+_([0-9]+)(N|S)_([0-9]+)(N|S)$"


def find_matching_coordinate(name: str, coordinates: list[str]) -> str:
    """
    Find the coordinate matching the requested variable name

    :param str name: Variable name to match
    :param list[str] coordinates: list of candidate coordinates vector
    :return: Name of selected coordinate, empty string if not successful
    """

    if len(coordinates) == 1:
        # single candidate, return it
        return coordinates[0]

    # detect latitude groups "height_50N_60N"
    matcher = re.compile(LAT_GROUP_REGEX)
    result = matcher.match(name)
    if result is not None:
        latitude_max = max([result.group(1), result.group(3)])
        for candidate in coordinates:
            if candidate.endswith("_" + latitude_max):
                return candidate

    return ""


def detect_latitude_group(name: str) -> tuple[float, float]:
    """
    Detect latitude group from variable name

    :param name: Name of the height variable
    :return: tuple with minimum latitude and maximum latitude of the group (in radians, defaults to [-pi, +pi])
    """
    matcher = re.compile(LAT_GROUP_REGEX)
    result = matcher.match(name)
    if result is not None:
        min_lat = float(result.group(1)) * np.pi / 180.0
        if result.group(2) == "S":
            min_lat *= -1.0
        max_lat = float(result.group(3)) * np.pi / 180.0
        if result.group(4) == "S":
            max_lat *= -1.0
    else:
        min_lat = -np.pi
        max_lat = np.pi

    return min_lat, max_lat


def find_lon_lat(
    table_name: str, axes_names: list[str], coord_attrs: dict, coord_raw: dict
) -> tuple[np.ndarray, np.ndarray]:
    """
    Find longitude and latitude coordinate variables

    :param str table_name: Name of the height map variable
    :param list[str] axes_names: Axes names for the current height map
    :param dict coord_attrs: Attributes of each coordinate variable, per variable name
    :param dict coord_raw: Values of coordinate variables, per variable name
    :return: longitude and latitude coordinates
    """

    lon = None
    lat = None
    coord_names = list(coord_raw.keys())
    for axis in axes_names:
        if axis in coord_names:
            match = axis
        else:
            candidate_name = [name for name in coord_names if axis in coord_attrs[name]["_ARRAY_DIMENSIONS"]]
            match = find_matching_coordinate(table_name, candidate_name)
            if not match:
                raise RuntimeError(f"Can't find coordinates for axis {axis!r}")
        unit = coord_attrs[match]["units"]
        if unit not in RADIANS_SCALING_FACTORS:
            raise RuntimeError(f"No conversion known for unit {unit!r}")
        coord_rad = coord_raw[match] * RADIANS_SCALING_FACTORS[unit]
        if "lon" in axis:
            lon = coord_rad
        elif "lat" in axis:
            lat = coord_rad

    return lon, lat


def find_latitude_index_bounds(lat_coords, lat_min, lat_max) -> tuple[int, int]:
    """
    Search the latitude coordinates to find the index bounds of a latitude zone. Maximum latitude
    is included. Minimum latitude is excluded.

    :param lat_coords: Latitude coordinates values
    :param lat_min: Minimum latitude value of the zone
    :param lat_max: Maximum latitude value of the zone
    :return: tuple with latitude start index and end index
    """

    if lat_coords[1] > lat_coords[0]:
        # latitudes already sorted
        start_lat_idx = np.searchsorted(lat_coords, lat_min, side="left")
        end_lat_idx = np.searchsorted(lat_coords, lat_max, side="right") - 1
    else:
        sorted_lat = np.flip(lat_coords)
        last_idx = len(lat_coords) - 1

        start_lat_idx = last_idx - np.searchsorted(sorted_lat, lat_max, side="left")
        end_lat_idx = last_idx - np.searchsorted(sorted_lat, lat_min, side="right")

    return start_lat_idx, end_lat_idx


def crop_range(start: int, end: int, lower_bound: int, upper_bound: int) -> tuple[int, int]:
    """
    Crop the index range to lower and upper bound, while ensuring that 1 index at most lies outside
    the bounds.

    :param start: initial start of the range
    :param end: initial end of the range (included)
    :param lower_bound: minimal value
    :param upper_bound: maximum value
    :return: tuple with cropped range
    """
    start = max(start, lower_bound - 1)
    end = min(end, upper_bound + 1)

    return start, end


class BaseManager:
    """
    BaseManager for elevation source
    """

    def __init__(self):
        """
        Constructor
        """

        self.layers = {}

    @abstractmethod
    def read_slice(self, slice_lat: np.ndarray, slice_lon: np.ndarray, layer: str) -> np.ndarray:
        """
        Read a portion of the DEM
        """

    def get_tile_geometry(self, latitude: float, longitude: float) -> dict:
        """
        Compute tile geometry for a given lat/lon

        :param float latitude: latitude that must be covered by the tile (rad)
        :param float longitude: longitude that must be covered by the tile (rad)
        :return: dictionary with tile definition, contains keys:

            - min_lat
            - min_lon
            - start_lat_idx
            - start_lon_idx
            - end_lat_idx
            - end_lon_idx

        """

        # identify target layer
        layer_name = None
        crop_geometry = False
        if len(self.layers) == 1:
            layer_name = next(iter(self.layers))
        else:
            crop_geometry = True
            closest_dist = 1e9
            for name, layer in self.layers.items():
                dist = abs(latitude - 0.5 * (layer["min_lat"] + layer["max_lat"]))
                if dist < closest_dist:
                    layer_name = name
                    closest_dist = dist
                if layer["min_lat"] < latitude <= layer["max_lat"]:
                    layer_name = name
                    break

        if layer_name is None:
            raise RuntimeError(f"Can't find elevation layer at lat={np.degrees(latitude)}, lon={np.degrees(longitude)}")

        lon = self.layers[layer_name]["lon"]
        lat = self.layers[layer_name]["lat"]
        tiles_extent = self.layers[layer_name]["tiles_extent"]
        chunks = self.layers[layer_name]["chunks"]
        resolution = self.layers[layer_name]["resolution"]
        shape = self.layers[layer_name]["shape"]

        # check latitude is inside bounds
        if (latitude - lat[0]) * (latitude - lat[-1]) > 0:
            _lat_0_deg = np.degrees(min(lat[0], lat[-1]))
            _lat_1_deg = np.degrees(max(lat[0], lat[-1]))
            raise RuntimeError(
                f"Latitude {np.degrees(latitude)} is outside accessible range" f" [{_lat_0_deg}, {_lat_1_deg}]"
            )
        # filter longitude to dataset convention ([-pi, pi], [0, 2pi], ...)
        delta_longitude = (longitude - lon[0] + TWO_PI) % TWO_PI

        # find which tile to use
        grid_pos_lat = math.floor((latitude - lat[0]) / tiles_extent[0])
        grid_pos_lon = math.floor(delta_longitude / tiles_extent[1])

        # compute index positions in full dataset
        start_lat_idx = grid_pos_lat * chunks[0]
        start_lon_idx = grid_pos_lon * chunks[1]
        end_lat_idx = min(start_lat_idx + chunks[0], shape[0] - 1)  # no cycling
        end_lon_idx = start_lon_idx + chunks[1]

        # crop latitude if several zones
        if crop_geometry:
            start_lat_idx, end_lat_idx = crop_range(
                start_lat_idx,
                end_lat_idx,
                self.layers[layer_name]["min_lat_idx"],
                self.layers[layer_name]["max_lat_idx"],
            )

        min_lat_idx = start_lat_idx if resolution[0] > 0.0 else end_lat_idx
        min_latitude = lat[0] + min_lat_idx * resolution[0]
        min_longitude = lon[0] + (start_lon_idx % shape[1]) * resolution[1]

        # gather the definition of the tile
        return {
            "layer": layer_name,
            "min_lat": min_latitude,
            "min_lon": min_longitude,
            "start_lat_idx": start_lat_idx,
            "start_lon_idx": start_lon_idx,
            "end_lat_idx": end_lat_idx,
            "end_lon_idx": end_lon_idx,
        }

    def get_slices(
        self, start_lat_idx: int, end_lat_idx: int, start_lon_idx: int, end_lon_idx: int, layer: str
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Extract tile data from indexes, wrap around East-West if needed

        :param int start_lat_idx: Latitude start index
        :param int end_lat_idx: Latitude end index
        :param int start_lon_idx: Longitude start index
        :param int end_lon_idx: Longitude end index
        :param layer: Layer name to read
        :return: slices for latitude and longitude
        """

        resolution = self.layers[layer]["resolution"]
        shape = self.layers[layer]["shape"]

        # latitude slice: flip if needed
        if resolution[0] > 0.0:
            slice_lat = start_lat_idx + np.arange(end_lat_idx - start_lat_idx + 1)
        else:
            # flip lines to provide a buffer with increasing latitudes
            slice_lat = end_lat_idx - np.arange(end_lat_idx - start_lat_idx + 1)

        # longitude slice: handle cycling
        slice_lon = start_lon_idx + np.arange(end_lon_idx - start_lon_idx + 1)
        slice_lon = slice_lon % shape[1]

        return slice_lat, slice_lon

    def get_neighbor_patch(self, end_lat_idx: int, slice_lon: np.ndarray, layer: str) -> np.ndarray:
        """
        Extract neighbor patch to fill missing value
        """

        assert end_lat_idx == self.layers[layer]["max_lat_idx"] + 1

        # assume the layers have the same latitude axis, otherwise the search for next layer is more complex
        neighbor_layer = None
        neighbor_name = None
        patch_line = None
        for next_name, next_layer in self.layers.items():
            if next_layer["min_lat_idx"] <= end_lat_idx <= next_layer["max_lat_idx"]:
                neighbor_layer = next_layer
                neighbor_name = next_name
                break
        if neighbor_layer is not None:
            # search the longitude interval to read
            first_lon = self.layers[layer]["lon"][slice_lon[0]]
            last_lon = self.layers[layer]["lon"][slice_lon[-1]]

            nbr_start_lon_idx = np.searchsorted(neighbor_layer["lon"], first_lon, side="right") - 1
            nbr_end_lon_idx = np.searchsorted(neighbor_layer["lon"], last_lon, side="left")
            if nbr_end_lon_idx < nbr_start_lon_idx:
                # handle cycling on lon
                nbr_end_lon_idx += neighbor_layer["shape"][1]

            nbr_start_lat_idx = self.layers[layer]["max_lat_idx"] + 1
            nbr_end_lat_idx = end_lat_idx

            nbr_slice_lat, nbr_slice_lon = self.get_slices(
                nbr_start_lat_idx,
                nbr_end_lat_idx,
                nbr_start_lon_idx,
                nbr_end_lon_idx,
                neighbor_name,
            )

            nbr_patch = self.read_slice(nbr_slice_lat, nbr_slice_lon, neighbor_name)

            # interpolate patch
            target_lon = self.layers[layer]["lon"][slice_lon]
            target_lon[target_lon < first_lon] += 2 * np.pi  # for cycling

            source_lon = self.layers[neighbor_name]["lon"][nbr_slice_lon]
            first_nbr_lon = source_lon[0]
            source_lon[source_lon < first_nbr_lon] += 2 * np.pi  # for cycling

            patch_line = np.interp(target_lon, source_lon, nbr_patch[0, :])

        return patch_line

    def get_tile(
        self, start_lat_idx: int, end_lat_idx: int, start_lon_idx: int, end_lon_idx: int, layer: str
    ) -> np.ndarray:
        """
        Extract tile data from indexes, wrap around East-West if needed

        :param int start_lat_idx: Latitude start index
        :param int end_lat_idx: Latitude end index
        :param int start_lon_idx: Longitude start index
        :param int end_lon_idx: Longitude end index
        :param layer: Layer name to read
        :return: tile with extract values
        """

        slice_lat, slice_lon = self.get_slices(start_lat_idx, end_lat_idx, start_lon_idx, end_lon_idx, layer)

        height = self.read_slice(slice_lat, slice_lon, layer)

        # Detect overlapping region
        if end_lat_idx > self.layers[layer]["max_lat_idx"]:
            patch_line = self.get_neighbor_patch(end_lat_idx, slice_lon, layer)
            if patch_line is not None:
                height[0, :] = patch_line

        # output tile
        return height


class ZarrManager(BaseManager):
    """
    Handle tile definition over a Zarr dataset
    """

    def __init__(
        self,
        path: str | FSStore,
        tile_lon: int | None = None,
        tile_lat: int | None = None,
        flip_lat: bool = False,
        shift_lon: float | None = None,
        shift_lat: float | None = None,
    ):
        """
        Constructor.

        :param str|FSStore path: DEM path
        :param int|None tile_lon: tile size along longitude in pixels
        :param int|None tile_lat: tile size along latitude in pixels
        :param bool flip_lat: flag to flip the latitude coordinates when reading the dataset
        :param float|None shift_lon: shift to apply on longitude coordinates
        :param float|None shift_lat: shift to apply on latitude coordinates
        """

        # call superclass constructor
        super().__init__()

        self.dem = zarr.open_consolidated(path, mode="r")

        # Check scenario: coordinates/maps groups or xarray structure
        groups = list(self.dem.group_keys())
        if "maps" in groups and "coordinates" in groups:
            self.height_maps = self.dem.maps
            coordinates = self.dem.coordinates
        else:
            # Xarray case, both variable and coordinate are in the same group
            self.height_maps = self.dem
            coordinates = self.dem

        # list availables coordinates
        coord_raw = {}
        coord_attrs = {}
        for name in coordinates.keys():
            if "lat" not in name and "lon" not in name:
                continue
            val = coordinates[name]
            coord_attrs[name] = val.attrs.asdict()
            coord_raw[name] = np.array(val, dtype="float64")

        # parse height tables
        self.layers = {}
        for table_name in self.height_maps.keys():
            if "height" not in table_name:
                continue

            table = self.height_maps[table_name]
            axes_names = table.attrs["_ARRAY_DIMENSIONS"]
            layer = {}

            # store shape
            layer["shape"] = table.shape

            # store chunking (keep in mind that effective tiles will have an extra element)
            chunks_lat, chunks_lon = table.chunks
            layer["chunks"] = (tile_lat or chunks_lat, tile_lon or chunks_lon)

            # detect latitude groups
            layer["min_lat"], layer["max_lat"] = detect_latitude_group(table_name)

            # find corresponding coordinates
            lon, lat = find_lon_lat(table_name, axes_names, coord_attrs, coord_raw)

            if flip_lat:
                lat = np.flip(lat)
            if shift_lon:
                lon += shift_lon
            if shift_lat:
                lat += shift_lat

            # find lon/lat resolution
            layer["resolution"] = (
                (lat[-1] - lat[0]) / (len(lat) - 1),
                (lon[-1] - lon[0]) / (len(lon) - 1),
            )
            # store tile extent
            layer["tiles_extent"] = (
                layer["chunks"][0] * layer["resolution"][0],
                layer["chunks"][1] * layer["resolution"][1],
            )

            # safety check
            assert layer["resolution"][1] > 0, "Longitude is expected to go eastward"
            longitude_coverage = lon[-1] - lon[0]
            if longitude_coverage < (TWO_PI - 2.0 * layer["resolution"][1]):
                logging.getLogger("asgard.models.dem").warning(
                    "Low longitude coverage: %f", np.degrees(longitude_coverage)
                )

            # pad longitudes with 1 extra sample if vector is not circular
            start_lon_2pi = lon[0] + 2 * np.pi
            end_lon = lon[-1]
            if end_lon < start_lon_2pi:
                lon = np.concatenate([lon, [start_lon_2pi]])

            layer["lon"] = lon
            layer["lat"] = lat

            # store min/max latitude indexes
            layer["min_lat_idx"], layer["max_lat_idx"] = find_latitude_index_bounds(
                layer["lat"],
                layer["min_lat"],
                layer["max_lat"],
            )

            self.layers[table_name] = layer

    def read_slice(self, slice_lat: np.ndarray, slice_lon: np.ndarray, layer: str) -> np.ndarray:
        """
        Read a portion of the DEM
        """

        return np.nan_to_num(self.height_maps[layer].get_orthogonal_selection((slice_lat, slice_lon)))


# Warning: possible shift of origin convention between DEM and GEOID
# GEOID seems to be a "grid image" model
# So is the Zarr georeferencing model?


class XarrayDatasetManager(BaseManager):
    """
    Handle tile definition over a xarray dataset
    """

    def __init__(
        self,
        data: xr.Dataset,
        tile_lon: int | None = None,
        tile_lat: int | None = None,
    ):
        """
        Constructor.

        :param xr.Dataset data: opened xr.Dataset
        :param int|None tile_lon: tile size along longitude in pixels
        :param int|None tile_lat: tile size along latitude in pixels
        """

        # call superclass constructor
        super().__init__()

        self.dem = data

        # list availables coordinates
        coord_raw = {}
        coord_attrs = {}
        for name, val in self.dem.coords.items():
            if "lat" not in name and "lon" not in name:
                continue
            coord_attrs[name] = val.attrs
            coord_raw[name] = np.array(val, dtype="float64")

        # parse height tables
        self.layers = {}
        for table_name in self.dem.keys():
            if "height" not in table_name:
                continue

            table = self.dem[table_name]
            axes_names = table.dims
            layer = {}

            # store shape
            layer["shape"] = table.shape

            # store chunking (keep in mind that effective tiles will have an extra element)
            chunks_lat, chunks_lon = table.chunks
            layer["chunks"] = (tile_lat or chunks_lat[0], tile_lon or chunks_lon[0])

            # detect latitude groups
            layer["min_lat"], layer["max_lat"] = detect_latitude_group(table_name)

            # find corresponding coordinates
            lon, lat = find_lon_lat(table_name, axes_names, coord_attrs, coord_raw)

            # find lon/lat resolution
            layer["resolution"] = (
                (lat[-1] - lat[0]) / (len(lat) - 1),
                (lon[-1] - lon[0]) / (len(lon) - 1),
            )
            # store tile extent
            layer["tiles_extent"] = (
                layer["chunks"][0] * layer["resolution"][0],
                layer["chunks"][1] * layer["resolution"][1],
            )

            # safety check
            assert layer["resolution"][1] > 0, "Longitude is expected to go eastward"
            longitude_coverage = lon[-1] - lon[0]
            if longitude_coverage < (TWO_PI - 2.0 * layer["resolution"][1]):
                logging.getLogger("asgard.models.dem").warning(
                    "Low longitude coverage: %f", np.degrees(longitude_coverage)
                )

            # pad longitudes with 1 extra sample if vector is not circular
            start_lon_2pi = lon[0] + 2 * np.pi
            end_lon = lon[-1]
            if end_lon < start_lon_2pi:
                lon = np.concatenate([lon, [start_lon_2pi]])

            layer["lon"] = lon
            layer["lat"] = lat

            # store min/max latitude indexes
            layer["min_lat_idx"], layer["max_lat_idx"] = find_latitude_index_bounds(
                layer["lat"],
                layer["min_lat"],
                layer["max_lat"],
            )

            self.layers[table_name] = layer

    def read_slice(self, slice_lat: np.ndarray, slice_lon: np.ndarray, layer: str) -> np.ndarray:
        """
        Read a portion of the DEM
        """
        return np.nan_to_num(np.array(self.dem[layer][slice_lat, slice_lon]))


class ElevationManager(TileUpdater):  # pylint: disable=too-few-public-methods
    """
    Inherits the Pyrugged Python :class:`pyrugged.raster.tile_updater.TileUpdater` class.

    Uses a Zarr dataset to load DEM tiles
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        dem_path: str | FSStore | xr.Dataset,
        geoid_path: str | FSStore | xr.Dataset | None = None,
        tile_lon: int | None = None,
        tile_lat: int | None = None,
        flip_lat: bool = False,
        shift_lon: float | None = None,
        shift_lat: float | None = None,
        offset_height: float = 0.0,
    ):
        """
        Constructor.

        :param str dem_path: DEM path
        :param str|None geoid_path: DEM path
        :param int|None tile_lon: tile size along longitude in pixels
        :param int|None tile_lat: tile size along latitude in pixels
        :param bool flip_lat: flag to flip the latitude coordinates when reading the dataset
        :param float shift_lon: shift to apply on longitude coordinates
        :param float shift_lat: shift to apply on latitude coordinates
        :param float offset_height: offset for the altitude
        """
        if isinstance(dem_path, xr.Dataset):
            self.dem = XarrayDatasetManager(
                dem_path,
                tile_lon=tile_lon,
                tile_lat=tile_lat,
            )
        else:
            self.dem = ZarrManager(
                dem_path,
                tile_lon=tile_lon,
                tile_lat=tile_lat,
                flip_lat=flip_lat,
                shift_lon=shift_lon,
                shift_lat=shift_lat,
            )

        self.offset_height = offset_height

        if geoid_path:
            # The geoid zarr is expected to have correct coordinates vectors
            if isinstance(geoid_path, xr.Dataset):
                geoid_manager = XarrayDatasetManager(geoid_path)
            else:
                geoid_manager = ZarrManager(geoid_path)

            self.geoid_tile = SimpleTile()
            geom = geoid_manager.get_tile_geometry(0.0, 0.0)
            geoid_layer = geoid_manager.layers[geom["layer"]]

            geoid_resolution = geoid_layer["resolution"]

            self.geoid_tile.set_geometry(
                geoid_layer["lat"][-1],
                geoid_layer["lon"][0],
                abs(geoid_resolution[0]),
                geoid_resolution[1],
                geoid_layer["shape"][0],  # geom["end_lat_idx"] - geom["start_lat_idx"] + 1,
                geoid_layer["shape"][1],  # geom["end_lon_idx"] - geom["start_lon_idx"] + 1,
            )
            height_tile = geoid_manager.get_tile(
                0,
                geoid_layer["shape"][0] - 1,
                0,
                geoid_layer["shape"][1] - 1,
                geom["layer"],
            )
            self.geoid_tile.set_elevation_block(height_tile)
        else:
            self.geoid_tile = None

    def update_tile(self, latitude: float, longitude: float, tile: SimpleTile):
        """
        Implementation of the :meth:`update_tile` method.

        :param float latitude: latitude that must be covered by the tile (rad)
        :param float longitude: longitude that must be covered by the tile (rad)
        :param SimpleTile tile: Pyrugged Python tile to update
        """

        logging.getLogger(ASGARD_LOGGER_NAME).debug(
            "ElevationManager.update_tile(%f, %f)",
            latitude * 180 / np.pi,
            longitude * 180 / np.pi,
        )

        geom = self.dem.get_tile_geometry(latitude, longitude)

        dem_resolution = self.dem.layers[geom["layer"]]["resolution"]

        # call set_geometry
        tile.set_geometry(
            geom["min_lat"],
            geom["min_lon"],
            abs(dem_resolution[0]),
            dem_resolution[1],
            geom["end_lat_idx"] - geom["start_lat_idx"] + 1,
            geom["end_lon_idx"] - geom["start_lon_idx"] + 1,
        )

        height_tile = self.dem.get_tile(
            geom["start_lat_idx"],
            geom["end_lat_idx"],
            geom["start_lon_idx"],
            geom["end_lon_idx"],
            geom["layer"],
        )

        if self.geoid_tile is not None:
            # Add the geoid elevation to convert MSL-based elevation into ellipsoid based elevation
            lat_vector = np.arange(
                tile.minimum_latitude,
                tile.minimum_latitude + tile.latitude_step * (tile.latitude_rows - 0.5),
                tile.latitude_step,
            )
            lon_vector = np.arange(
                tile.minimum_longitude,
                tile.minimum_longitude + tile.longitude_step * (tile.longitude_columns - 0.5),
                tile.longitude_step,
            )
            # align longitudes to geoid longitude interval
            lon_vector = (
                lon_vector - self.geoid_tile.minimum_longitude + TWO_PI
            ) % TWO_PI + self.geoid_tile.minimum_longitude

            lon_array, lat_array = np.meshgrid(lon_vector, lat_vector)

            geoid_height = self.geoid_tile.interpolate_elevation_arr(lat_array, lon_array)

            height_tile = height_tile + geoid_height
        elif self.offset_height:
            height_tile += self.offset_height

        # call set_elevation_block or set_elevation
        tile.set_elevation_block(height_tile)


if JCC_MODULE_NAME == "sxgeo":
    # pylint: disable=import-error
    from org.sxgeo.input.dem import DemManager, GeoidManager
    from org.sxgeo.python import PyUpdatableTile

    # pylint: disable=too-few-public-methods
    class SxgeoDemManager(TileUpdater):
        """
        Inherits the Pyrugged Python TileUpdater class.
        Uses the Java DemManager from Rugged (that inherits the Java TileUpdater) to update a Pyrugged Python Tile.

        :param DemManager dem_manager: Java DemManager instance.
        """

        def __init__(self, *args):
            """
            Constructor.

            :param args: DemManager args
            """
            self.dem_manager = DemManager(*args)

        def update_tile(self, latitude: float, longitude: float, tile: SimpleTile):
            """
            Implementation of the update_tile method of the Pyrugged Python TileUpdater.


            :param latitude: latitude that must be covered by the tile (rad)
            :param longitude: longitude that must be covered by the tile (rad)
            :param tile: Pyrugged Python tile to update
            """

            # Call the Java updateTile method by passing it a Python SxgeoUpdatableTile instance.
            # When the Java code will call setGeometry and setElevation, it will call the Python
            # implementation of these methods and update the Pyrugged Python tile.
            return self.dem_manager.updateTile(float(latitude), float(longitude), SxgeoUpdatableTile(tile))

    class SxgeoUpdatableTile(PyUpdatableTile):
        """
        Implements the Java UpdatableTile class.
        The methods are called from Java, they call their Python counterparts by passing them their input arguments.

        :param SimpleTile pyTile: Pyrugged Python tile.
        """

        def __init__(self, pytile):
            """Constructor"""
            super().__init__()
            # pylint: disable=invalid-name
            self.setGeometry = pytile.set_geometry
            self.setElevation = pytile.set_elevation

    class SxgeoGeoidManager(TileUpdater):
        """
        Inherits the Pyrugged Python TileUpdater class.
        Uses the Java GeoidManager from Rugged (that inherits the Java TileUpdater) to update a Pyrugged Python Tile.

        :param GeoidManager dem_manager: Java GeoidManager instance.
        """

        def __init__(self, *args):
            """
            Constructor.

            """
            self.geoid_manager = GeoidManager(*args)

        def update_tile(self, latitude: float, longitude: float, tile: SimpleTile):
            """
            Implementation of the update_tile method of the Pyrugged Python TileUpdater.


            :param latitude: latitude that must be covered by the tile (rad)
            :param longitude: longitude that must be covered by the tile (rad)
            :param tile: Pyrugged Python tile to update
            """

            # Call the Java updateTile method by passing it a Python SxgeoUpdatableTile instance.
            # When the Java code will call setGeometry and setElevation, it will call the Python
            # implementation of these methods and update the Pyrugged Python tile.

            return self.geoid_manager.updateTile(float(latitude), float(longitude), SxgeoUpdatableTile(tile))
