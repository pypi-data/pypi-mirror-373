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
Module for propagation model class implementation
"""

import os.path as osp
import warnings

import numpy as np

# isort: off
# pylint: disable=unused-import
from asgard.wrappers.orekit import to_nio_view, JCC_MODULE  # sxgeo.initVM() # pylint: disable=no-name-in-module

# isort: on

# pylint: disable=import-error, wrong-import-order, ungrouped-imports
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.tools import TransformProcessor
from pyrugged.bodies.body_rotating_frame_id import BodyRotatingFrameId
from pyrugged.bodies.ellipsoid_id import EllipsoidId
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.intersection_algorithm import create_intersection_algorithm
from pyrugged.location.optical import CorrectionsParams, OpticalLocation
from pyrugged.los.transform import DynamicTransform
from pyrugged.model.pyrugged import PyRugged
from pyrugged.model.pyrugged_builder import PyRuggedBuilder
from pyrugged.raster.tile_updater import TileUpdater
from pyrugged.refraction.multi_layer_model import MultiLayerModel

from asgard import ASGARD_VALIDATE_SCHEMAS
from asgard.core.compat import resources_files
from asgard.core.frame import FrameId
from asgard.core.propagation import AbstractPropagationModel
from asgard.core.schema import DEM_DATASET_SCHEMA, TIME_ARRAY_SCHEMA, validate_or_throw
from asgard.models.body import EarthBody
from asgard.models.dem import ElevationManager

ROTATING_FRAME_MAP = {
    "EF": "ITRF",
    "EF_EQUINOX": "ITRF_EQUINOX",
    "TOD": "GTOD",
}

MULTILAYERMODEL_SCHEMA = {
    "type": "object",
    "properties": {
        "pixel_step": {"type": "integer"},
        "line_step": {"type": "integer"},
    },
    "required": ["pixel_step", "line_step"],
}


class PropagationModel(AbstractPropagationModel):
    """
    Optical propagation model. Handles the propagation model of the electro-magnetic wave
    between the sensor and the target (Earth, Moon, star). This model uses Duvenhage algorithm
    for DEM intersection.
    """

    def __init__(self, **kwargs):
        """
        Constructor

        Keyword args for the Duvenhage intersection algorithm and TileUpdater

        :param str geoid_path: geoid path. if None, we use the default geoid from the sxgeo resources.
        :param str dem_globe_path: DEM globe path. If None, then the SRTM path must be set.
        :param str dem_srtm_path: DEM SRTM path.
        :param bool overlapping_tiles: are the DEM globe or SRTM tiles overlapping ?
        :param int max_cached_tiles: maximum number of tiles stored in the cache. 8 by default.

        Keyword args for the ellipsoid

        :param dict body: configuration of ellipsoid and EOP.
        :param str body_rotating_frame_id: of type BodyRotatingFrameId. "ITRF" by default.

        Keyword args for the correction parameters

        :param bool light_time_correction: apply light time correction ? False by default.
        :param bool aberration_of_light_correction: apply aberration of light correction ? False by default.
        :param dict atmospheric_refraction: atmospheric refraction parameter.

        """

        # Call parent constructor
        super().__init__(**kwargs)

        #
        # Read the keyword args or default values

        # ----------------------[ Ellipsoid parameters ]--------------------------
        # initialize an internal EarthBody model
        self.body = kwargs.get("earth_body", EarthBody())

        ellipsoid_id = self.body.config["ellipsoid"]
        # detect rotating frame
        self.config["body_rotating_frame"] = kwargs.get("body_rotating_frame", "EF")

        # Init the ellipsoid
        builder = PyRuggedBuilder()
        builder.set_ellipsoid(
            new_ellipsoid=None,
            ellipsoid_id=EllipsoidId[ellipsoid_id],
            body_rotating_frame_id=BodyRotatingFrameId[ROTATING_FRAME_MAP[self.config["body_rotating_frame"]]],
        )
        self.ellipsoid = builder.ellipsoid

        # -------------------------[ DEM parameters ]------------------------------
        self.config.setdefault("max_cached_tiles", 8)

        # detect geoid file, or use a default one in Sxgeo resources (gtx format)
        geoid_path = kwargs.get("geoid_path")

        # detect DEM
        dem_is_native = bool("native_dem" in kwargs)
        dem_is_zarr = bool("zarr_dem" in kwargs)
        self.max_cached_tiles = self.config["max_cached_tiles"]
        self._tile_updater = None

        if dem_is_zarr:
            dem_path = kwargs["zarr_dem"]["path"]
            if isinstance(dem_path, str):
                assert osp.exists(dem_path), "DEM path doesn't exist!"

            # detect geoid file, or use a default one in Sxgeo resources (gtx format)
            if isinstance(geoid_path, str) and not geoid_path.endswith(".zarr"):
                raise RuntimeError("Only zarr geoid is supported with zarr DEM")

            self.config["zarr_dem"].setdefault("tile_size", 1000)

            self._tile_updater = ElevationManager(
                dem_path,
                geoid_path=geoid_path,
                tile_lon=self.config["zarr_dem"]["tile_size"],
                tile_lat=self.config["zarr_dem"]["tile_size"],
                flip_lat=self.config["zarr_dem"].get("flip_lat", False),
                shift_lon=self.config["zarr_dem"].get("shift_lon"),
                shift_lat=self.config["zarr_dem"].get("shift_lat"),
            )
        elif dem_is_native:
            dem_path = kwargs["native_dem"]["path"]
            assert osp.exists(dem_path), "DEM path doesn't exist!"

            # Init a Java DEM globe or SRTM manager that will update the Pyrugged Python tiles.
            warnings.warn(
                "Support of native DEM will be removed, use Zarr versions",
                DeprecationWarning,
                stacklevel=2,
            )
            # for native DEM, use a default geoid in Sxgeo resources (gtx format)
            geoid_path = geoid_path or str(resources_files(JCC_MODULE).joinpath("resources/GEOID/egm96_15.gtx"))
            assert isinstance(geoid_path, str), "Only local geoid path is supported with native DEM"
            assert osp.exists(geoid_path), "Geoid path doesn't exist!"

            try:
                # pylint: disable=import-outside-toplevel
                from org.sxgeo.input.dem import (
                    DemGlobeFileManager,
                    GeoidManager,
                    SrtmFileManager,
                )

                from asgard.models.dem import SxgeoDemManager
            except ImportError as err:
                raise RuntimeError("Can't use native DEM without SXGEO, import SXGEO before Orekit-JCC") from err

            overlapping_tiles = kwargs["native_dem"]["overlapping_tiles"]
            dem_source = kwargs["native_dem"]["source"]
            dem_file_manager = None
            if dem_source == "GLOBE":
                dem_file_manager = DemGlobeFileManager(dem_path)
            elif dem_source == "SRTM":
                dem_file_manager = SrtmFileManager(dem_path)
            else:
                raise RuntimeError("DEM globe or SRTM must be set")
            dem_file_manager.findRasterFile()
            self._tile_updater = SxgeoDemManager(
                dem_file_manager,
                GeoidManager(geoid_path, True),
                # geoid is a single file (not tiles) so set overlap to True by default
                overlapping_tiles,
            )

        if geoid_path:
            self.config["geoid_path"] = geoid_path

        # ------------------------[ Algorithm parameters ]-----------------------------

        # Init the intersection algorithm for DEM
        duvenhage = None
        if self._tile_updater is not None:
            duvenhage = create_intersection_algorithm(AlgorithmId.DUVENHAGE, self._tile_updater, self.max_cached_tiles)

        constant_elevation = create_intersection_algorithm(AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID)

        # ----------------------[ Correction parameters ]--------------------------
        self.light_time_correction = kwargs.get("light_time_correction", False)
        self.aberration_of_light_correction = kwargs.get("aberration_of_light_correction", False)

        # setup atmospheric refraction model
        atmo_config = kwargs.get("atmospheric_refraction", {})
        self.atmospheric_refraction = None
        if "MultiLayerModel" in atmo_config:
            self.atmospheric_refraction = MultiLayerModel(self.ellipsoid)
            self.atmospheric_refraction.set_grid_steps(
                atmo_config["MultiLayerModel"]["pixel_step"],
                atmo_config["MultiLayerModel"]["line_step"],
            )

        # ----------------------[ OpticalLocation instance ]--------------------------

        # Init the OpticalLocation instance
        self.optical_loc = None
        if duvenhage is not None:
            self.optical_loc = OpticalLocation(
                rugged=PyRugged(ellipsoid=self.ellipsoid, sc_to_body=None, sensors=None, name=None),
                algorithm=duvenhage,
                corrections_params=CorrectionsParams(
                    self.light_time_correction,
                    self.aberration_of_light_correction,
                    self.atmospheric_refraction,
                ),
            )

        self.optical_loc_constant = OpticalLocation(
            rugged=PyRugged(ellipsoid=self.ellipsoid, sc_to_body=None, sensors=None, name=None),
            algorithm=constant_elevation,
            corrections_params=CorrectionsParams(
                self.light_time_correction,
                self.aberration_of_light_correction,
                self.atmospheric_refraction,
            ),
        )

    @property
    def tile_updater(self):
        return self._tile_updater

    @classmethod
    def init_schema(cls) -> dict:
        """
        Validate the constructor kwargs.

        :download:`JSON schema <doc/scripts/init_schema/schemas/PropagationModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "earth_body": {"type": "asgard.models.body.EarthBody"},
                "geoid_path": DEM_DATASET_SCHEMA,
                "zarr_dem": {
                    "type": "object",
                    "description": "DEM converted in Zarr format",
                    "properties": {
                        "path": DEM_DATASET_SCHEMA,
                        "tile_size": {
                            "type": "integer",
                            "description": "Size of the DEM tiles passed to pyrugged (pixels)",
                        },
                        "flip_lat": {
                            "type": "boolean",
                            "description": "Flag to flip the latitude coordinates",
                        },
                        "shift_lon": {
                            "type": "number",
                            "description": "Shift to apply to longitudes coordinates (radians)",
                        },
                        "shift_lat": {
                            "type": "number",
                            "description": "Shift to apply to latitudes coordinates (radians)",
                        },
                    },
                    "required": ["path"],
                },
                "native_dem": {
                    "type": "object",
                    "description": "DEM in native format",
                    "properties": {
                        "path": {"type": "string"},
                        "source": {"type": "string", "enum": ["SRTM", "GLOBE"]},
                        "overlapping_tiles": {"type": "boolean"},
                    },
                    "required": ["path", "source", "overlapping_tiles"],
                },
                "max_cached_tiles": {"type": "integer"},
                "body_rotating_frame": {
                    "type": "string",
                    "enum": ["EF", "EF_EQUINOX", "TOD"],
                },
                "light_time_correction": {"type": "boolean"},
                "aberration_of_light_correction": {"type": "boolean"},
                "atmospheric_refraction": {
                    "type": "object",
                    "properties": {
                        "MultiLayerModel": MULTILAYERMODEL_SCHEMA,
                    },
                    "required": ["MultiLayerModel"],
                },
            },
            "additionalProperties": False,
        }

    def _build_inert_to_body_transforms(self, time_array) -> DynamicTransform:
        """
        Compute the list of transforms inertial to body for a given time array

        :param time_array: input times to compute the transforms
        :return: list of transforms
        """

        inertial_frame = self.body.frames[FrameId.EME2000]
        body_frame = self.body.frames[FrameId[self.config["body_rotating_frame"]]]
        epoch = self.body.time_reference_model.epoch_to_date(time_array)
        times = self.body.time_reference_model.offsets_to_seconds(time_array)
        nb_times = times.size

        translation = np.zeros((nb_times, 3), dtype="float64")
        velocity = np.zeros((nb_times, 3), dtype="float64")
        acceleration = np.zeros((nb_times, 3), dtype="float64")
        rotation = np.zeros((nb_times, 4), dtype="float64")
        rotation_rate = np.zeros((nb_times, 3), dtype="float64")
        rotation_acc = np.zeros((nb_times, 3), dtype="float64")

        TransformProcessor.estimate(
            inertial_frame,
            body_frame,
            epoch,
            to_nio_view(times),
            to_nio_view(translation),
            to_nio_view(velocity),
            to_nio_view(acceleration),
            to_nio_view(rotation),
            to_nio_view(rotation_rate),
            to_nio_view(rotation_acc),
        )

        return DynamicTransform(
            translation=translation,
            velocity=velocity,
            acceleration=acceleration,
            rotation=rotation,
            rotation_rate=rotation_rate,
            rotation_acceleration=rotation_acc,
        )

    def _build_geoid_elevation_manager(self, altitude: float | int) -> TileUpdater:
        """
        Setup an elevation manager for geoid

        :param altitude: constant altitude over geoid
        :return: instance of elevation manager
        """
        if not isinstance(altitude, (float, int)):
            raise NotImplementedError("Only float/number allowed for altitude in geoid mode")
        # DEM use is a geoid
        if not self.config.get("geoid_path"):
            raise RuntimeError("Geoid path doesn't exist!")
        if self.config["geoid_path"].endswith(".zarr"):
            manager = ElevationManager(
                self.config["geoid_path"],
                tile_lon=500,
                tile_lat=500,
                offset_height=float(altitude),
            )
        else:
            try:
                # pylint: disable=import-outside-toplevel
                from asgard.models.dem import SxgeoGeoidManager
            except ImportError as err:
                raise RuntimeError("Can't use native DEM without SXGEO, import SXGEO before Orekit-JCC") from err

            # geoid is a single file (not tiles) so set overlap to True by default
            manager = SxgeoGeoidManager(self.config["geoid_path"], True, altitude)

        return manager

    def _build_altitude_array(self, altitude, shape) -> np.ndarray:
        """
        Build an array of input altitudes with the desired shape

        :param altitude: input altitude value (scalar or array)
        :param shape: target shape
        :return: output altitude array
        """
        if isinstance(altitude, (float, int)):
            altitudes = float(altitude) * np.ones(shape)
        elif not isinstance(altitude, np.ndarray):
            raise NotImplementedError("Only float or np array allowed for altitude")
        elif altitude.shape != shape:
            raise ValueError(f"Provided altitudes doesn't have the correct shape:  {altitude.shape} != {shape}")
        else:
            altitudes = altitude

        return altitudes

    # pylint: disable=too-many-arguments, too-many-locals, too-many-positional-arguments
    def sensor_to_target(
        self,
        # dict dataset values
        dataset: dict,
        # LOS origins and directions keys
        los_pos_key: str = "los_pos",
        los_vec_key: str = "los_vec",
        # Acquisition times keys
        time_key: str = "times",
        # Other keys
        spacecraft_velocities_key: str = "orb_vel",
        gnd_coords_key: str = "gnd_coords",
        altitude: float | np.ndarray | None = None,
        altitude_reference: str = "ellipsoid",
    ):  # pylint: disable=arguments-differ
        """
        Direct location with effect correction in inertial frame.

        :param dict dataset: dataset with the below keys

        LOS origins and directions in inertial frame for each datetime

        :param str los_pos_key: LOS origins as x,y,z, mandatory
        :param str los_vec_key: LOS directions as x,y,z, mandatory
        :param str time_key: LOS dates, as a time array structure, mandatory

        Others

        :param str spacecraft_velocities_key: Spacecraft velocities for each datetime as x,y,z,
            mandatory only for the aberration of light correction
        :param str gnd_coords_key: Output ground coordinates for each datetime as longitude,latitude,altitude
        :param float altitude: if not None, use this value as constant altitude for intersection
        :param str altitude_reference: support ellipsoid or geoid but is set to ellipsoid if not supplied.
            This is a complement whenever you want to intersect at a constant altitude.
            You can do it over the ellipsoid which is the default behaviour or over the geoid.
        """

        # Read dataset values
        pos_inert = dataset[los_pos_key]
        los_inert = dataset[los_vec_key]
        acq_time_array = dataset[time_key]
        spacecraft_velocities = dataset.get(spacecraft_velocities_key, np.empty((0,)))

        # Expected shapes for 3d vectors and quaternions.
        # 1st dimension = number of datetimes.
        shape_vec = (len(pos_inert), 3)

        # Check numpy array shapes
        assert pos_inert.shape == shape_vec
        assert los_inert.shape == shape_vec

        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(acq_time_array, TIME_ARRAY_SCHEMA)
        assert acq_time_array["offsets"].shape == (shape_vec[0],)

        # Build the list of "inertial to body" transforms
        inert_to_body = self._build_inert_to_body_transforms(acq_time_array)

        if self.optical_loc is None and altitude is None:
            # No DEM, force to altitude=0
            altitude = 0.0

        # call the OpticalLocation class
        if altitude is None:
            # DEM case
            ground_point = self.optical_loc.direct_location_inert_fast(
                inert_to_body,
                spacecraft_velocities,
                pos_inert,
                los_inert,
                altitudes=None,
            )
        # Constant altitude case
        elif altitude_reference == "geoid":
            tmp_tile_updater = self._build_geoid_elevation_manager(altitude)

            tmp_optical_loc = OpticalLocation(
                rugged=PyRugged(ellipsoid=self.ellipsoid, sc_to_body=None, sensors=None, name=None),
                algorithm=create_intersection_algorithm(AlgorithmId.DUVENHAGE, tmp_tile_updater, self.max_cached_tiles),
                corrections_params=CorrectionsParams(
                    self.light_time_correction,
                    self.aberration_of_light_correction,
                    self.atmospheric_refraction,
                ),
            )
            ground_point = tmp_optical_loc.direct_location_inert_fast(
                inert_to_body,
                spacecraft_velocities,
                pos_inert,
                los_inert,
                altitudes=None,
            )
        elif altitude_reference == "ellipsoid":
            altitudes = self._build_altitude_array(altitude, shape_vec[0:1])

            ground_point = self.optical_loc_constant.direct_location_inert_fast(
                inert_to_body,
                spacecraft_velocities,
                pos_inert,
                los_inert,
                altitudes=altitudes,
            )
        else:
            raise RuntimeError("Direct location at constant altitude only possible over ellipsoid or geoid.")

        # convert to degrees
        ground_point[:, 0:2] = np.rad2deg(ground_point[:, 0:2])

        # Swap lon/lat as pyrugged uses lat/lon/z convention
        ground_point[:, [0, 1]] = ground_point[:, [1, 0]]

        # Save results into dataset
        dataset[gnd_coords_key] = ground_point


#
# Util functions.
# @TODO put in a common module ?


def np_to_vec3d(array):
    """Numpy array to Vector3D conversion"""
    return Vector3D(*array.tolist())
