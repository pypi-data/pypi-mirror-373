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
S2geoGipp implementation.
"""
from contextlib import suppress
from typing import Dict, List

import numpy as np
from drivers.xml_util import XmlUtil

from asgard.sensors.sentinel2.s2_band import S2Band
from asgard.sensors.sentinel2.s2_detector import S2Detector
from asgard.sensors.sentinel2.s2_sensor import S2Sensor


class S2geoGipp:
    """
    S2Geo GIPP files legacy loader.

    :param d_config: output configuration JSON values
    """

    def __init__(self, d_config: dict):
        self.d_config = d_config

    def read_viewing_directions(self, gip_viedir_paths: List[str], tdis: Dict[S2Band, str]):
        """
        Read the viewing direction GIPP files.

        :param view_dirs_files: viewing direction GIPP file paths.
        :param tdis: TDI configuration to use for each band
        """

        d_viewing_dirs = []
        self.d_config["viewing_directions"] = d_viewing_dirs

        # For each GIPP file
        for xml_path in gip_viedir_paths:
            # Read XML file. Remove namespaces to facilitate reading.
            x_viedir = XmlUtil.read_with_etree(xml_path, remove_namespaces=True)
            x_data = x_viedir.find("DATA")

            # Band ID = band index
            # Note: each GIPP file should be associated with a single band.
            band = S2Band.from_index(int(x_data.find("BAND_ID").text))

            # Read values for each TDI config
            x_tdis = x_data.findall("VIEWING_DIRECTIONS_LIST")

            # If the viewing directions file contains no TDI conf for the current band, do nothing
            if len(x_tdis) == 0:
                continue

            # If the viewing directions file contains multiple TDI confs for the current band
            if len(x_tdis) > 1:
                # Check that a specific TDI conf for this band was requested from the datastrip file
                if band not in tdis:
                    raise RuntimeError(
                        f"The viewing directions GIPP file: {xml_path!r}\n"
                        f"contains multiple TDI configurations for band index: {band.index}\n"
                        f"but the configuration to use is missing from the datastrip file "
                        f"under 'TDI_Configuration_List'"
                    )

            # If a specific TDI conf for this band was requested from the datastrip file
            if band in tdis:
                # Use the right TDI conf from the viewing directions file,
                # check that it exists and is unique
                tdi = tdis[band]
                x_keep = [node for node in x_tdis if node.get("tdi_config") == tdi]
                if len(x_keep) == 0:
                    raise RuntimeError(
                        f"TDI configuration: {tdi!r} " f"is missing from the viewing directions GIPP file: {xml_path!r}"
                    )
                if len(x_keep) > 1:
                    raise RuntimeError(
                        f"Multiple TDI configurations: {tdi!r} "
                        f"exist in the viewing directions GIPP file: {xml_path!r}"
                    )
                x_tdi = x_keep[0]

            # Else just use the single TDI conf
            else:
                x_tdi = x_tdis[0]

            # Read info for each detector
            x_detectors = x_tdi.findall("VIEWING_DIRECTIONS")
            for x_detector in x_detectors:
                # Detector ID = detector name
                detector = S2Detector.from_legacy_name(x_detector.get("detector_id"))

                # Read XML values
                pixel_count = int(x_detector.find("NB_OF_PIXELS").text)
                tan_psi_x = [float(v) for v in x_detector.find("TAN_PSI_X_LIST").text.split()]
                tan_psi_y = [float(v) for v in x_detector.find("TAN_PSI_Y_LIST").text.split()]
                assert pixel_count == len(tan_psi_x) == len(tan_psi_y)

                # Save values for the current detector/band
                sensor = S2Sensor(detector, band)
                d_viewing_dirs.append(
                    {
                        "sensor": sensor.name,
                        "values": np.array([tan_psi_x, tan_psi_y], np.double),
                    }
                )

    # Deprecated, not used for sxgeo
    @staticmethod
    def read_grid_step_parameters(gip_g2para_path: str):  # -> GridStepParameters:
        """Read the grid step parameters"""

        if gip_g2para_path is None:
            return None

        # Read XML file. Remove namespaces to facilitate reading.
        x_g2para = XmlUtil.read_with_etree(gip_g2para_path, remove_namespaces=True)

        # Mandatory
        x_resampling_grids = x_g2para.find("DATA.SIGMA_PARAMETERS.RESAMPLING_GRIDS")
        grid_step_factor_dem = float(x_resampling_grids.find("GRID_STEP_FACTOR_DEM").text)
        low_resolution_factor = float(x_resampling_grids.find("LOW_RESOLUTION_FACTOR").text)
        grid_max_step = float(x_resampling_grids.find("GRID_MAX_STEP").text)

        # Optional
        densificated_footprint_step = None
        with suppress(AttributeError):
            densificated_footprint_step = float(x_g2para.find("DATA.FOOTPRINT_STEP").text)

        # TODO, see the s2geo code:
        # if (levelInfo.getIndex() < LevelInfo.L1A.getIndex()) {
        #     return getInvLocDetectorFootPrintStep();
        # } else {
        #     return getPrdLocDetectorFootPrintStep();
        # }
        footprint_step = float(0)

        # Create and return the Java object
        return (  # GridStepParameters (
            grid_step_factor_dem,
            low_resolution_factor,
            grid_max_step,
            densificated_footprint_step,
            footprint_step,
        )

    # Deprecated, not used for sxgeo
    @staticmethod
    def read_angle_step_parameters(gip_r2abca_path: str):  # -> AngleStepParameters:
        """Read the angle step parameters"""

        if gip_r2abca_path is None:
            return None

        # Read XML file. Remove namespaces to facilitate reading.
        x_r2abca = XmlUtil.read_with_etree(gip_r2abca_path, remove_namespaces=True)

        x_sun = x_r2abca.find("DATA.RESAMPLE_SUN_ANGLE_GRID_STEPS")
        sun_angle_grid_along_column_step = float(x_sun.find("ALONG_COLUMNS").text)
        sun_angle_grid_along_line_step = float(x_sun.find("ALONG_LINES").text)

        # TODO: where to read ? See the s2geo code:
        # public double getIncidenceAngleAlongColumns() throws S2GeoException {
        #     return tilingParameters.getDATA().getINCIDENCE_ANGLES().getGRID_STEP().getALONG_COLUMNS();
        # }
        # public double getIncidenceAngleAlongLines() throws S2GeoException {
        #     return tilingParameters.getDATA().getINCIDENCE_ANGLES().getGRID_STEP().getALONG_LINES();
        # }
        sun_angle_grid_step = float(0)
        incidence_angle_grid_along_column_step = float(0)
        incidence_angle_grid_along_line_step = float(0)

        # Create and return the Java object
        return (  # AngleStepParameters(
            sun_angle_grid_step,
            sun_angle_grid_along_column_step,
            sun_angle_grid_along_line_step,
            incidence_angle_grid_along_column_step,
            incidence_angle_grid_along_line_step,
        )
