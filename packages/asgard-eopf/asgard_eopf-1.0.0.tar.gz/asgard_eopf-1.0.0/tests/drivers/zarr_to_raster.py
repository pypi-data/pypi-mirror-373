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
Module for zarr DEM manipulation / input / output class

"""
import logging
import os
import xml.etree.ElementTree as ET

import numpy as np
import zarr  # pylint: disable=import-error

from asgard.core.logger import ASGARD_LOGGER_NAME

logger = logging.getLogger(f"{ASGARD_LOGGER_NAME}.drivers.zarr_to_raster")

ARCSEC_PER_DEGREE = 3600


class ZarrToRaster:
    """
    zarr DEM data handler, mainly to convert zarr to raster tiles (15°x15°)
    save each tile into a file with adequate naming and data format.
    """

    # force target tile coverage
    tile_size_deg = {
        "lat": 15,
        "lon": 15,
    }  # as per PE-ID-ESA-GS-584-EO_Mission_SW_File_Format_Specs_latest.pdf

    # dict to handle the lat lon coverage and the tiles naming
    q_origin_deg = {
        "lat": {"S": -89.99166666666667, "N": 0},
        "lon": {"W": -180.0, "E": 0},
    }

    def __init__(self, raster_dtype="<i2", raster_fillval=0):
        """
        ZarrToRaster constructor

        :param raster_dtype: Binary encoding to use when producing the files. Dedault: 16bits little endian.
        :param raster_fillval:
        """
        # initialize empty properties
        self.raster_dtype = raster_dtype
        self.raster_fillval = raster_fillval

        self.lat_step_arcsec = None

        self.lon_step_arcsec = None

    def run(self, zarr_path: str, output_dir: str, debug_hook=None) -> str:
        """
        Convert the ZARR DEM and save it tile by tile to a binary format as per
        https://eop-cfi.esa.int/Repo/PUBLIC/DOCUMENTATION/SYSTEM_SUPPORT_DOCS/PE-ID-ESA-GS-584-EO_Mission_SW_File_Format_Specs_latest.pdf

        :param str zarr_path:  Path to the zarr DEM folder.
        :param str output_dir: Path where to store the raster DEM tiles.
        :param debug_hook: Callback hook to call on tiles extracted, meant for debug purpose only. A typical
                           hook will be :class:`asgard.extras.zarr.plotters.DebugDEMPlotter`.
        :return: full path to 'dem_config_file.xml' (the tiles are located in the very same folder)
        """
        # open zarr data and provides pointer to the zarr object
        dataset = zarr.open(zarr_path, mode="r")

        # Fix bug on coordinates (remove the 1 extra sample in lat and lon and
        # set the right range of values). CAUTION : this bug fix is applicable
        # only to the initial ZARR DEM (dated 2022-10-28) available at:
        #   s3:/common/ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20221028T093533.zarr
        # The first two code lines below need to be changed for the new DEM available at:
        #   s3:/common/ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20230428T185052.zarr
        # A switch will be implemented when migrating to the new .zarr so as to test and validate it.
        # lat = dataset.coordinates["lat_getasse"][:][::-1] - 90 * ARCSEC_PER_DEGREE
        # lon = dataset.coordinates["lon_getasse"][:] - 180.0 * ARCSEC_PER_DEGREE
        lat = dataset.latitude[:]
        lon = dataset.longitude[:]
        length = min([len(lat), dataset.getasse_height[:].shape[0]])
        lat = lat[-length:]
        lat_deg = lat / ARCSEC_PER_DEGREE

        length = min([len(lon), dataset.getasse_height[:].shape[1]])
        lon = lon[0:length]
        lon_deg = lon / ARCSEC_PER_DEGREE
        height_fill_value = dataset.getasse_height.fill_value

        # check sanity
        self._check_zarr(dataset, lat, lon)

        # compute the index arrays to cover each quadrant
        q_slicer = {
            "lat": {
                "S": np.where(lat_deg < 0.0)[0],
                "N": np.where(lat_deg >= 0.0)[0],
            },
            "lon": {
                "W": np.where(lon_deg < 0.0)[0],
                "E": np.where(lon_deg >= 0.0)[0],
            },
        }

        if debug_hook:
            debug_hook.plot_global_dem(
                dataset,
                lat_deg,
                lon_deg,
                q_slicer,
            )

        # iterate on target tile:
        #   - get target tile from zarr
        #   - dump to binary

        nb_files = 0
        for lat_key in q_slicer["lat"]:
            nb_tiles_lat = num_tiles(lat_deg, q_slicer["lat"][lat_key], self.tile_size_deg["lat"])

            for lon_key in q_slicer["lon"]:
                nb_tiles_lon = num_tiles(lon_deg, q_slicer["lon"][lon_key], self.tile_size_deg["lon"])

                for lat_tile in range(nb_tiles_lat):
                    # lat start indexes for the current tile in deg
                    lat_deg_orig = self.q_origin_deg["lat"][lat_key] + lat_tile * self.tile_size_deg["lat"]
                    ind_lat_orig = np.where(np.abs(lat_deg - lat_deg_orig) < 1e-6)[0][0]
                    # slice with decreasing latitude indexes
                    # => this flips the tile so that its 1st row is for the southern lat.
                    ind_lat_slice = ind_lat_orig + int(np.sign(self.lat_step_arcsec)) * np.arange(
                        int(abs(ARCSEC_PER_DEGREE / self.lat_step_arcsec)) * self.tile_size_deg["lat"]
                    )

                    for lon_tile in range(nb_tiles_lon):
                        # lon start indexes for the current tile in deg
                        lon_deg_orig = self.q_origin_deg["lon"][lon_key] + lon_tile * self.tile_size_deg["lon"]
                        ind_lon_orig = np.where(lon_deg == lon_deg_orig)[0][0]

                        # slice with increasing longitude indexes
                        ind_lon_slice = ind_lon_orig + np.arange(
                            int(abs(ARCSEC_PER_DEGREE / self.lon_step_arcsec)) * self.tile_size_deg["lon"]
                        )
                        height_tile = dataset.getasse_height.get_orthogonal_selection((ind_lat_slice, ind_lon_slice))

                        # make this slice contiguous and 'C' ordered
                        height_tile = height_tile.copy(order="C")

                        # build filename
                        filename = f"{int(abs(lat_deg_orig)):02}{lat_key}{int(abs(lon_deg_orig)):03}{lon_key}"
                        filepath = os.path.join(output_dir, filename)
                        nb_files += 1

                        if debug_hook:
                            debug_hook.plot_array(
                                lat_deg_slice=lat_deg[ind_lat_slice],
                                lon_deg_slice=lon_deg[ind_lon_slice],
                                height_tile=height_tile,
                                filename=filename,
                            )

                        # write tile as binary
                        logging.debug("writing file %s", filename)
                        self.write_binary(filepath, height_tile)

        logging.info("%s DEM files generated into %s from %s", nb_files, output_dir, zarr_path)

        # Make XML header file
        filepath = os.path.join(output_dir, "dem_raster_configuration.xml")
        self._mk_xml_raster_header(filepath, height_tile, height_fill_value)

        # return path to dem_config_file.xml
        return os.path.join(output_dir, "dem_raster_configuration.xml")

    def _check_zarr(self, dataset: zarr.core.Array, lat, lon):
        """
        Basic sanity checks of the fields read from the ZARR DEM file

        Sets ``lon_step_arcsec`` and ``lat_step_arcsec``.
        """
        lat_diff = np.diff(lat)
        self.lat_step_arcsec = np.mean(lat_diff)
        if len(np.where(lat_diff != self.lat_step_arcsec)[0]):
            raise ValueError("cannot proceed, irregularly sampled latitudes.")

        lon_diff = np.diff(lon)
        self.lon_step_arcsec = np.mean(lon_diff)
        if len(np.where(lon_diff != self.lon_step_arcsec)[0]):
            raise ValueError("cannot proceed, irregularly sampled longitudes.")

        # this code handles only ZARR DEM with lat, lon in "arcsecond"
        lat_unit = dataset.latitude.attrs["units"]
        if lat_unit != "arcseconds":
            raise ValueError(f"cannot proceed, lat_getasse is not arcsecond but {lat_unit}.")
        lon_unit = dataset.longitude.attrs["units"]
        if lon_unit != "arcseconds":
            raise ValueError(f"cannot proceed, lon_getasse is not arcsecond but {lon_unit}.")

    def _mk_xml_raster_header(self, filepath, height_tile, height_fill_value):
        """
        Make XML header file for the generic binary DEM.

        :param filepath:
        :param height_tile:
        :param height_fill_value:
        :return: XML file "dem_raster_configuration.xml"
        """
        # Create root element
        root = ET.Element("Data_Block", type="xml")

        # Add sub-elements
        dem_raster_conf = ET.SubElement(root, "DEM_Raster_Configuration")
        data_type = ET.SubElement(dem_raster_conf, "Data_Type")
        data_type.text = str(height_tile.dtype)  # "int16"
        data_unit = ET.SubElement(dem_raster_conf, "Data_Unit")
        data_unit.text = "meter"
        rows = ET.SubElement(dem_raster_conf, "Rows")
        rows.text = str(height_tile.shape[0])  # "1800"
        columns = ET.SubElement(dem_raster_conf, "Columns")
        columns.text = str(height_tile.shape[1])  # "1800"
        resolution = ET.SubElement(dem_raster_conf, "Resolution", unit="sec")
        resolution.text = str(int(np.abs(self.lat_step_arcsec)))  # "30"
        reference = ET.SubElement(dem_raster_conf, "Reference")
        reference.text = "WGS84"
        void_value = ET.SubElement(dem_raster_conf, "Void_Value")
        void_value.text = str(height_fill_value)  # should be "-32768" instead of "0"
        maximum_height_value = ET.SubElement(dem_raster_conf, "Maximum_Height_Value", unit="meter")
        maximum_height_value.text = "10000."
        flag_type = ET.SubElement(dem_raster_conf, "Flag_Type")
        flag_type.text = "int8"

        # Write the XML file
        tree = ET.ElementTree(root)
        tree.write(filepath)
        logging.info("xml raster header %s generated", filepath)

    def write_binary(self, filepath, height_tile):
        """
        Write the height_tile of the current DEM object into a binary file.

        :param filepath:    File produced
        :param height_tile: DEM data to write in the file.
        :return:
        """
        # force conversion to little endian int16
        height_tile = height_tile.astype(self.raster_dtype)

        with open(filepath, "wb") as newfile:
            newfile.write(height_tile.tobytes())

    @staticmethod
    def read_binary(filepath, arr_shape, arr_dtype):
        """
        Read DEM tile from a binary file into a (2D) numpy array.

        :param filepath:
        :param arr_shape: tuple with two elements (num samples lat, num samples lon)
        :param arr_dtype: dtype of the array to reconstruct from file typically dtype='i2'='int16'

        :return arr:

        """
        with open(filepath, "rb") as bin_file:
            buffer = bin_file.read()
            data = np.frombuffer(buffer, dtype=arr_dtype)
            height_tile = data.reshape(arr_shape)
            return height_tile


def num_tiles(val_arr, ind_arr, tile_size):
    """
    Compute the number of tiles in a selected sub-array of the array of interest, given a tile_size.

    :param val_arr:   array of interest
    :param ind_arr:   array of contiguous indexes that define the sub-array ot interest in 'val_array'
    :param tile_size: size of the tiles
    :return: num_tiles
    """
    return int(np.ceil(abs((val_arr[ind_arr[-1]] - val_arr[ind_arr[0]]) / tile_size)))
