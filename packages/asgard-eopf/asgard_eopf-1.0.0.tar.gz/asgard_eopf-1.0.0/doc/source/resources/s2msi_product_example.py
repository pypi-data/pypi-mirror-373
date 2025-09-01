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
    Example of S2MSIGeometry instantiation and possible method as direct location
"""

import os
import os.path as osp

import numpy as np
from zarr.storage import FSStore

import sxgeo
from tests.drivers.s2geo_legacy.s2geo_interface import S2geoInterface
from asgard_legacy.sensors.sentinel2.msi import S2MSILegacyGeometry
from asgard.sensors.sentinel2.msi import S2MSIGeometry


def setup_remote_dem(dem_filename) -> FSStore:
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

    return FSStore(dem_path_s3, mode="r", s3=s3_config)


SAMPLE = 0
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")
interface_path = osp.join(ASGARD_DATA, "S2MSIdataset/S2MSI_TDS1/L0c_DEM_Legacy_S2GEO_Input_interface.xml")

config = S2geoInterface(interface_path).read()

# Initialization of a S2MSILegacyGeometry
config["resources"]["dem_srtm"] = osp.join(ASGARD_DATA, "DEM_natif/legacy/DEM_SRTM90")
config['resources']["geoid"] = osp.join(ASGARD_DATA, "DEM_natif/legacy/DEM_GEOID/S2__OPER_DEM_GEOIDF_MPC__20200112T130120_S20190507T000000.gtx")
product_legacy_DEM_legacy = S2MSILegacyGeometry(**config)

# Initialization of a S2MSIGeometry with DEM legacy
product_DEM_legacy = S2MSIGeometry(**config)

# Initialization of a S2MSIGeometry with DEM ZARR
dem_path_zarr = setup_remote_dem("S0__ADF_DEM90_20000101T000000_21000101T000000_20240528T050715.zarr")
config["resources"].pop("dem_srtm")
config["resources"]["dem_zarr"] = dem_path_zarr
config['resources']["geoid"] = osp.join(
            ASGARD_DATA,
            "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr",
        )
product_DEM_zarr = S2MSIGeometry(**config)

for product in [product_legacy_DEM_legacy, product_DEM_legacy, product_DEM_zarr]:
    print(f"Run with product {product} {type(product)}:")
    for sensor in ["B01/D08", "B01/D09"]:
        print(f"\nRun for sensor {sensor!r}")

        pixels_legacy = 3
        if isinstance(product, S2MSILegacyGeometry):
            pixels_legacy = 2

        # Instantiate an array of 9 pixels using the footprint of the sensor (in pixels)
        MAXLINE = product.coordinates[sensor]["lines"] - 1  # max line is included
        MAXCOL = product.coordinates[sensor]["pixels"] - 1  # max col is included
        pixels = np.array(
            [[col, row] for row in np.linspace(0, MAXLINE, pixels_legacy) for col in np.linspace(0, MAXCOL, pixels_legacy)],
            np.int32,
        )

        print(f"pixels={pixels[SAMPLE]}")

        # Call the direct location method
        grounds, acq_times = product.direct_loc(pixels, sensor)
        print(f"grounds={grounds[SAMPLE]}")

        # Call the inverse location method
        pixels_legacy = 2
        if isinstance(product, S2MSILegacyGeometry):
            pixels_legacy = 3
        inverse_pixels = product.inverse_loc(grounds[:, :pixels_legacy], geometric_unit=sensor)
        print(f"inverse_pixels={inverse_pixels[SAMPLE]}")

        # Call the sun angles compute method
        sun_angles = product.sun_angles(grounds, acq_times)
        print(f"sun_angles={sun_angles[SAMPLE]}")

        # Call the incidence angles compute method
        incidence_angles = product.incidence_angles(grounds, acq_times)
        print(f"incidence_angles={incidence_angles[SAMPLE]}")

        # Call the detector footprint compute method
        footprint = product.footprint(sampling_step=15, geometric_unit=sensor)
        print(f"footprint={footprint[SAMPLE]}")
