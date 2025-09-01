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
Helper functions for plotting various figures and images.
"""
import json
import logging
import os
import os.path as osp

import matplotlib.pyplot as plt
import numpy as np

from asgard.core.logger import ASGARD_LOGGER_NAME

logger = logging.getLogger(ASGARD_LOGGER_NAME)


def disp_array(
    arr,
    arr_extent=None,
    title="",
    xlabel="",
    ylabel="",
    clim=None,
    fig_save_path=None,
    fig_save_fmt="png",
):
    """
    Display the array 'arr' that is provided, with Upper Left corner = 0,0 and axes ticks tuned by 'arr_extent'.
    :param arr:
    :param arr_extent:
    :param title:
    :param xlabel:
    :param ylabel:
    :param clim: None or list of [min, max] height values (in m) to clip the display and set the extent of the colorbar.
    :param fig_save_path:
    :param fig_save_fmt:
    :return:
    """
    plt.imshow(arr, extent=arr_extent, origin="upper")
    # ~ plt.imshow(arr, extent=arr_extent , origin="lower", cmap="terrain", vmin=0, vmax=3500)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if clim is not None:
        plt.clim(clim[0], clim[-1])
    plt.colorbar()
    if fig_save_path is not None:
        fig_handle = plt.gcf()
        fig_handle.savefig(fig_save_path, format=fig_save_fmt)
        logger.debug("plotting into file %s", fig_save_path)
    else:
        plt.ion()
        plt.show()
    plt.close()


def disp_global_dem(dataset, lat_deg, lon_deg, q_slicer_lat, q_slicer_lon, png_path_out):
    """
    Display and save the whole DEM as a .png file.
    :param lat_deg:
    :param lon_deg:
    :param q_slicer_lat:
    :param q_slicer_lon:
    :param png_path_out:
    :return:
    """
    # display the height array alone to check its content
    fig_save_path = os.path.join(png_path_out, "ZARR_DEM.png")
    fig_save_fmt = "png"
    disp_array(
        dataset.getasse_height[:],
        clim=[-100, 100],
        fig_save_path=fig_save_path,
        fig_save_fmt=fig_save_fmt,
    )

    for lat_key in q_slicer_lat:
        for lon_key in q_slicer_lon:
            # visual check of the DEM per quadrant
            hgt_slice_lat_lon = dataset.getasse_height.get_orthogonal_selection(
                (q_slicer_lat[lat_key], q_slicer_lon[lon_key])
            )

            lat_deg_slice = lat_deg[q_slicer_lat[lat_key]]
            lon_deg_slice = lon_deg[q_slicer_lon[lon_key]]
            cur_extent = [
                lon_deg_slice[0],
                lon_deg_slice[-1],
                lat_deg_slice[-1],
                lat_deg_slice[0],
            ]
            title = lat_key + lon_key + " quadrant of the ZARR GETASSE DEM"
            xlabel = "lon (deg)"
            ylabel = "lat (deg)"
            fig_save_path = os.path.join(png_path_out, lat_key + lon_key + "_extract_of_zarr_getasse.png")
            disp_array(
                hgt_slice_lat_lon,
                arr_extent=cur_extent,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                clim=[-100, 100],
                fig_save_path=fig_save_path,
                fig_save_fmt="png",
            )


class DebugDEMPlotter:
    """
    Helper class for plotting DEM tiles as PNG images.
    Meant to be used as a callback in :class:`asgard.drivers.zarr_to_raster.ZarrToRaster.run`
    """

    def __init__(self, png_path_out):
        """
        constructor
        """
        self.__png_path_out = png_path_out

    def plot_global_dem(self, dataset, lat_deg, lon_deg, slicer):
        """
        Plot the full DEM as a small image.
        """
        disp_global_dem(
            dataset,
            lat_deg,
            lon_deg,
            slicer["lat"],
            slicer["lon"],
            self.__png_path_out,
        )

    def plot_array(self, lat_deg_slice, lon_deg_slice, height_tile, filename, clip_values=None):
        """
        Plot tile, seen as an array.
        """
        # visual check of the tiling
        cur_extent = [
            lon_deg_slice[0],
            lon_deg_slice[-1],
            lat_deg_slice[-1],
            lat_deg_slice[0],
        ]
        xlabel = "lon (deg)"
        ylabel = "lat (deg)"
        fig_save_path = os.path.join(self.__png_path_out, ".".join([filename, "png"]))

        disp_array(
            height_tile,
            arr_extent=cur_extent,
            title=filename,
            xlabel=xlabel,
            ylabel=ylabel,
            clim=clip_values,
            fig_save_path=fig_save_path,
            fig_save_fmt="png",
        )


def create_plugin(png_path_out):
    """
    Plugin creation function for plotting DEMs with :class:`helpers.plotters.DebugDEMPlotter`.
    """
    return DebugDEMPlotter(png_path_out)


def read_pyrugged_tiles(pytile):
    """
    From pyrugged tile return a dict containing corners of the tile in degrees in a dict

    Parameters:
        pytile: a pyrugged tile
    """
    return {
        "min_lat": np.rad2deg(pytile.minimum_latitude),
        "max_lat": np.rad2deg(pytile.maximum_latitude),
        "min_lon": np.rad2deg(pytile.minimum_longitude),
        "max_lon": np.rad2deg(pytile.maximum_longitude),
    }


def generate_geojson_tile(pytiles, output_path):
    """
    Generate GeoJSON data for a pytile object and save it to a file.

    Parameters:
        pytiles: List of objects with attributes minimum_latitude, maximum_latitude,
                minimum_longitude, maximum_longitude.
        output_file: Path to the output GeoJSON file.

    """

    # Extract the bounding box
    for i, pytile in enumerate(pytiles):
        tile = read_pyrugged_tiles(pytile)
        min_lon = tile["min_lon"]
        max_lon = tile["max_lon"]
        min_lat = tile["min_lat"]
        max_lat = tile["max_lat"]

        # Check if the tile crosses the antimeridian
        features = []
        if tile["max_lon"] > 180:
            logging.debug("Tile crosses the antimeridian.")

            # First polygon: from min_lon to 180
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [min_lon, min_lat],  # Bottom-left
                                [180, min_lat],  # Bottom-right
                                [180, max_lat],  # Top-right
                                [min_lon, max_lat],  # Top-left
                                [min_lon, min_lat],  # Close the polygon
                            ]
                        ],
                    },
                    "properties": {"name": "Bounding Box Part 1", "source": "pytile"},
                }
            )

            # Second polygon: from -180 to the remaining part
            overflow_lon = max_lon - 360  # Wrap longitude around
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-180, min_lat],  # Bottom-left
                                [overflow_lon, min_lat],  # Bottom-right
                                [overflow_lon, max_lat],  # Top-right
                                [-180, max_lat],  # Top-left
                                [-180, min_lat],  # Close the polygon
                            ]
                        ],
                    },
                    "properties": {"name": "Bounding Box Part 2", "source": "pytile"},
                }
            )
        else:
            # Regular polygon: no crossing
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [min_lon, min_lat],  # Bottom-left
                                [max_lon, min_lat],  # Bottom-right
                                [max_lon, max_lat],  # Top-right
                                [min_lon, max_lat],  # Top-left
                                [min_lon, min_lat],  # Close the polygon
                            ]
                        ],
                    },
                    "properties": {"name": "Bounding Box", "source": "pytile"},
                }
            )

        # Create the GeoJSON structure
        geojson_data = {"type": "FeatureCollection", "features": features}

        # Write the GeoJSON to the output file
        output_file = osp.join(output_path, f"tile_{i}.geojson")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, indent=4)

        logging.info("GeoJSON file successfully written to %s", output_file)


def plot_elevation_tile(pytiles, output_path):
    """
    Plot and save a figure of the elevations for a list of pyrugged tiles

    Parameters:
        pytile: a pyrugged tile
        output_path: path directory to save elevations array
    """

    for i, pytile in enumerate(pytiles):
        tile = read_pyrugged_tiles(pytile)

        output_elev = f"elevations_{i}.png"
        dem_plotter = DebugDEMPlotter(output_path)
        lat_slice = (tile["min_lat"], tile["max_lat"])
        long_slice = (tile["min_lon"], tile["max_lon"])
        dem_plotter.plot_array(lat_slice, long_slice, pytile._elevations, output_elev)
