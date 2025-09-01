#!/usr/bin/env python
# coding: utf8
# Copyright 2022-2023 CS GROUP
#
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
Module for product abstract classes
"""


import logging
from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from functools import partial
from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy import ndarray

# isort: off
# pylint: disable=unused-import
import asgard.wrappers.orekit  # noqa: F401

# isort: on

# pylint: disable=wrong-import-order
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.raster.tiles_cache import TilesCache
from scipy.spatial.transform import Rotation as R

from asgard.core.body import BodyId
from asgard.core.frame import FrameId
from asgard.core.logger import ASGARD_LOGGER_NAME
from asgard.core.math import (
    CoordinatePredictor,
    flatten_array,
    numerical_jacobian,
    restore_array,
)
from asgard.core.transform import RigidTransform

from . import schema

logger = logging.getLogger(f"{ASGARD_LOGGER_NAME}.core.geometry")


class L0Geometry(ABC):  # for now it's an abstract class. It may change later
    """
    Generic L0 geometry product for footprint computation
    """

    def __init__(self, **kwargs):
        self.body_model = None
        self.orbit_model = None
        self.propagation_model = None
        self.osv_dict = None
        self.time_dataset = None
        schema.validate_or_throw(kwargs, self.init_schema())

    @classmethod
    @abstractmethod
    def init_schema(cls) -> dict:
        """
        Expected schema, as a JSON schema. Example:

        .. code-block:: json

            {
              "type": "object",
              "properties": {
                "orbit": {"type": "array"},
                "acquisition_time": {"type": "string"}
              }
            }
        """

    @abstractmethod
    def footprint(self) -> np.ndarray:
        """
        Compute L0 product coarse footprint

        :return: geodetics points composing the coarse footprint: np.ndarray:Nx2
        """


class AbstractGeometry(ABC):  # pylint: disable=too-many-instance-attributes
    """
    Generic product at level (L0)/L1
    """

    _instr_list = []

    def __init__(self, **kwargs):
        """
        Constructor

        Initialize empty internal models, axes and coordinates (may be filled by derived classes).
        """
        # initialize empty models (to be replaced by derived classes)
        self.timestamp_models = {}
        self.body_model = None
        self.orbit_model = None
        self.platform_model = None
        self.pointing_model = None
        self.propagation_model = None

        # initialize default time settings (may be overriden by derived classes)
        self.default_time = {
            "ref": "GPS",
            "unit": "d",
            "epoch": "2000-01-01_00:00:00",
        }

        self.predictor: Dict[str, CoordinatePredictor] = {}

        # Axes names to reference the measurement in the product
        self.axes = []
        # accessible coordinates, per geometric unit, and per axis
        self.coordinates = {"default": {}}
        # validate kwargs schema
        schema.validate_or_throw(kwargs, self.init_schema())
        self.config = kwargs
        # Keep this cache for getting altitudes in inverse loc, in order not to rebuild the cache between each calls
        self._cache: Optional[TilesCache] = None
        self._max_cached_tiles = 8  # default value

    def axes_names(self, geometric_unit: str) -> Tuple[str, str]:
        """
        Get the axes names of a given geometric unit

        :param str geometric_unit: Geometric unit
        :return: tuple of axes names
        """
        return tuple(self.coordinates[geometric_unit].keys())

    def _labeled_dataset(self, key: str, number_of_points: int):
        # creating input and output data to fit predictors :
        # - input data as matrix coordiantes : img_coords_flatten
        # - along with their corresponding ground coordinates : xy_coords
        first_axis, second_axis = self.axes_names(key)
        set_geounit_direct_loc = partial(self.partial_direct_loc, geometric_unit=key)
        if number_of_points > max(self.coordinates[key].values()):
            raise ValueError("allowed grid points number exceeded!")

        col_coords = (
            np.linspace(
                0,
                self.coordinates[key][first_axis] - 1,
                number_of_points,
                endpoint=True,
            )
            .round()
            .astype(int)
        )
        lig_coords = (
            np.linspace(
                0,
                self.coordinates[key][second_axis] - 1,
                number_of_points,
                endpoint=True,
            )
            .round()
            .astype(int)
        )
        array_x, array_y = np.meshgrid(col_coords, lig_coords, copy=False)
        img_coords_flatten = np.stack((array_x.flatten(), array_y.flatten()), axis=-1)

        xy_coords = set_geounit_direct_loc(img_coords_flatten)

        return img_coords_flatten, xy_coords

    def _init_predictor(self, key: str = "default", number_of_points: int = 4):
        img_coords_flatten, xy_coords = self._labeled_dataset(key, number_of_points)
        is_invalid = np.any(np.isnan(xy_coords), axis=-1)
        if np.any(is_invalid):
            logger.warning("Nan found during predictor estimation!")
            ok_idx = np.where(~is_invalid)
            img_coords_flatten = img_coords_flatten[ok_idx]
            xy_coords = xy_coords[ok_idx]
        self.predictor[key] = CoordinatePredictor(img_coords_flatten, xy_coords)

    @property
    def instruments(self) -> List[str]:
        """
        Return the list of instruments handled by the product
        """
        return self._instr_list

    @classmethod
    @abstractmethod
    def init_schema(cls) -> dict:
        """
        Expected schema, as a JSON schema. Example:

        .. code-block:: json

            {
              "type": "object",
              "properties": {
                "orbit": {"type": "array"},
                "acquisition_time": {"type": "string"}
              }
            }
        """

    def direct_loc(
        self,
        coordinates: ndarray,
        geometric_unit: str | None = None,
        altitude: float | ndarray | None = None,
        sort_lines: bool = False,
    ) -> Tuple[ndarray, ndarray]:
        """
        Direct location routine

        :param numpy.ndarray coordinates: Array of coordinates
        :param str geometric_unit: Name of a specific geometric unit to use (optional)
        :param float altitude: Constant altitude to use for direct location, if None the DEM is used
        :param ndarray altitudes: If float constant altitudes for each point to use for direct location,
                                  if numpy array altitude to use for each coordinate,
                                  if None the DEM is used
        :param sort_lines: try to sort lines before computation
        :return: array of projected coordinates, array of acquisition times
        """
        # initiate internal dataset

        # flatten coordinates
        flat_coord = flatten_array(coordinates, 2)

        flat_altitude = altitude
        if isinstance(altitude, ndarray):
            flat_altitude = flatten_array(altitude)

        if sort_lines:
            # sort by lines to expect faster results
            idx_sorted = np.argsort(flat_coord[:, 1])
            temp = flat_coord[idx_sorted]
            flat_coord = temp
            if isinstance(altitude, ndarray):
                temp = flat_altitude[idx_sorted]
                flat_altitude = temp

        dataset = {"coords": flat_coord}
        if geometric_unit is None:
            geometric_unit = self._instr_list[0]

        dataset["geom"] = geometric_unit

        sample = 0
        logger.debug("[direct_loc] Start on pixel %s ...", dataset["coords"][sample])

        # Estimate acquisition times (ndarray)
        self.timestamp_models[geometric_unit].acquisition_times(dataset)

        logger.debug("[direct_loc] Times: %s ...", dataset["times"]["offsets"][sample])

        # Line of sight wrt Instrument frame + time
        self.pointing_model.compute_los(dataset)

        logger.debug(
            "[direct_loc] LOS in instrument frame: %s ...",
            dataset["los_vec"][sample],
        )

        # transform line of sight to Satellite reference frame
        sensor_to_platform = self.platform_model.compute_transforms(
            geometric_unit,
            "platform",
            dataset.get("times"),
        )

        dataset["los_pos"] = sensor_to_platform.transform_position(dataset["los_pos"])
        dataset["los_vec"] = sensor_to_platform.transform_direction(dataset["los_vec"])

        logger.debug(
            "[direct_loc] LOS in platform frame: %s ...",
            dataset["los_vec"][sample],
        )

        # transform line of sight to Earth-Centered-Inertial frame
        self.orbit_model.get_osv(dataset)
        self.orbit_model.compute_quaternions(dataset)
        # prepare transform from satellite frame to Earth
        sat_to_earth = RigidTransform(
            translation=dataset["orb_pos"],
            rotation=dataset["attitudes"],
        )

        dataset["los_pos"] = sat_to_earth.transform_position(dataset["los_pos"])
        dataset["los_vec"] = sat_to_earth.transform_direction(dataset["los_vec"])

        logger.debug(
            "[direct_loc] LOS in inertial frame: %s ...",
            dataset["los_vec"][sample],
        )

        logger.debug("[direct_loc] Orbital position: %s ...", dataset["orb_pos"][sample])
        logger.debug("[direct_loc] Orbital velocity: %s ...", dataset["orb_vel"][sample])
        logger.debug("[direct_loc] Attitude: %s ...", dataset["attitudes"][sample])

        # Estimate some unit vectors for debug purpose
        if logger.getEffectiveLevel() == logging.DEBUG:
            unit_r = dataset["orb_pos"][sample] / np.linalg.norm(dataset["orb_pos"][sample])
            unit_v = dataset["orb_vel"][sample] / np.linalg.norm(dataset["orb_vel"][sample])
            unit_rv = np.cross(unit_r, unit_v)
            quat = R.from_quat(dataset["attitudes"][sample])
            sat_axes = {
                "X": quat.apply([1, 0, 0]),
                "Y": quat.apply([0, 1, 0]),
                "Z": quat.apply([0, 0, 1]),
            }
            for name, sat_axis in sat_axes.items():
                logger.debug(
                    "[direct_loc] Satellite %s alignment with r, v, rv: [%.3f, %.3f, %.3f]",
                    name,
                    np.inner(sat_axis, unit_r),
                    np.inner(sat_axis, unit_v),
                    np.inner(sat_axis, unit_rv),
                )

        # propagation to target
        self.propagation_model.sensor_to_target(dataset, altitude=flat_altitude)

        logger.debug("[direct_loc] Ground: %s ...", dataset["gnd_coords"][sample])

        gnd_coords = dataset["gnd_coords"]
        acq_times = dataset["times"]["offsets"]
        if sort_lines:
            # put the point back to original order
            reverse_pos = np.zeros_like(idx_sorted)
            reverse_pos[idx_sorted] = np.arange(len(idx_sorted))
            gnd_coords = gnd_coords[reverse_pos]
            acq_times = acq_times[reverse_pos]

        # restore shape
        gnd_coords = restore_array(gnd_coords, coordinates.shape[:-1], last_dim=3)
        acq_times = restore_array(acq_times, coordinates.shape[:-1])

        return gnd_coords, acq_times

    def direct_loc_bundle(
        self,
        coordinates: ndarray,
        geometric_unit: str | None = None,
        altitude: float | None = None,
    ) -> ndarray:
        """
        Direct location routine, with single output array (lon, lat, height, time)

        :param numpy.ndarray coordinates: Array of coordinates
        :param str geometric_unit: Name of a specific geometric unit to use (optional)
        :param float altitude: Constant altitude to use for direct location, if None the DEM is used
        :return: array of projected coordinates and acquisition times
        """
        ground, times = self.direct_loc(coordinates, geometric_unit=geometric_unit, altitude=altitude)
        return np.concatenate([ground, times[..., np.newaxis]], axis=-1)

    def _check_coords(self, coordinates: np.ndarray) -> np.ndarray:
        """checks the range of a matrix coordinates

        :param coordinates: matrix coordinates
        :type coordinates: numpy.ndarray
        :return: matrix coordinates within range
        :rtype: numpy.ndarray
        """

        if len(coordinates.shape) == 1:
            coordinates = coordinates[np.newaxis]

        output = coordinates

        # we round the line array to avoid too much computation when retrieve (PV,Q)
        output[:, 1] = np.round(output[:, 1])

        return output

    def inverse_loc(
        self,
        ground_coordinates: np.ndarray,
        tolerance: float = 1e-4,
        geometric_unit: str = "default",
        max_iterations: int = 10,
        altitude: float | np.ndarray | None = None,
    ) -> np.ndarray:
        """
        Computes the image coordinates of a set of ground coordinates by inverting the :meth:`direct_loc`
        method. The inverse is computed by iterating until the change in the image coordinates is
        within the specified tolerance, or the maximum number of iterations is reached.

        If altitudes are provided the altitude is ignored in ConstantDEMIntersection

        :param numpy.ndarray ground_coordinates: Array containing ground coordinates (any height component is ignored).
        :param str geometric_unit: unit of the ground coordinates.
        :param float tolerance: the maximum allowed change in the image coordinates during one
                          iteration, default is 1e-4.
        :param int max_iterations: maximum number of iterations allowed before stopping the
                               computation, default is 1.
        :param float altitude: If given in float, set the constant altitude to perform inverse locations
                               If given as numpy array use these altitudes for ground coordinates
        :return: 2D array of shape (n,2) containing the computed image coordinates
        """
        # Initialize predictor
        if geometric_unit not in self.predictor:
            self._init_predictor(geometric_unit)

        # if not bool(self.predictor):
        #     raise ValueError("predictor attribut must be initialized!")
        # if geometric_unit not in self.predictor:
        #     raise KeyError
        direct_loc_kwargs = {"geometric_unit": geometric_unit}

        # Function to call to evaluate direct loc
        set_geounit_direct_loc = partial(self.partial_direct_loc, **direct_loc_kwargs)
        # flatten input coords
        flat_ground_coords = flatten_array(ground_coordinates[..., :2], 2)
        # Initialize altitudes
        altitudes = None
        if altitude is not None:
            if isinstance(altitude, (float, int)):
                altitudes = float(altitude) * np.ones(flat_ground_coords.shape[0:1])
            elif isinstance(altitude, np.ndarray):
                altitudes = altitude
            else:
                raise NotImplementedError("Only float or numpy array allowed on altitudes")
        else:
            # generate the altitudes from TileUpdater from the propagation_model
            if self.propagation_model is not None:
                tile_updater = self.propagation_model.tile_updater
                if tile_updater is not None:
                    cache = (
                        TilesCache(SimpleTile, tile_updater, self._max_cached_tiles)
                        if self._cache is None
                        else self._cache  # reuse previous one
                    )
                    altitudes = np.array(
                        [
                            cache.get_tile(gp[1], gp[0]).interpolate_elevation(gp[1], gp[0])
                            for gp in np.deg2rad(flat_ground_coords)
                        ]
                    )

        # First iteration is done on all points

        # Compute first prediction
        predicted_image_coords = self.predictor[geometric_unit].predict(flat_ground_coords)

        # Manually do the first iteration on all pix
        # Check coords
        clipped_image_coords = self._check_coords(predicted_image_coords)

        current_ground_coord = set_geounit_direct_loc(clipped_image_coords, altitudes)

        # Compute the jacobian of the partial_direct function
        current_jac = numerical_jacobian(
            partial(set_geounit_direct_loc, altitude=np.repeat(altitudes, 2 * flat_ground_coords.shape[1], axis=0)),
            clipped_image_coords,
            epsilon=1,
        )
        # Compute the change in the ground coordinates
        delta_ground_coords = flat_ground_coords - current_ground_coord
        delta_ground_coords[:, 0] = (delta_ground_coords[:, 0] + 180) % 360 - 180
        # Compute the change in the image coordinates:
        #
        # current_jac is of shape (n, 2, 2)
        # Some functions in NumPy, have more flexible broadcasting options. For example,
        # numpy.linalg.inv can handle “stacked” arrays,
        # which is less expensive than inverting directly a (2*n, 2*n)-shaped matrix.
        # Also, the broadcasting mechanism in einsum allows us to perform matrix multiplication
        # operation efficiently, without having to loop over
        # each sample. delta_ground_coords : (n, 2), np.linalg.inv(current_jac): (n, 2, 2)

        delta_coords = np.einsum("ijk,ik->ij", np.linalg.inv(current_jac), delta_ground_coords)
        # Update the image coordinates
        # predicted_image_coords += delta_coords.astype(int)
        next_image_coords = clipped_image_coords + delta_coords

        # If the change in the image coordinates is within the tolerance, stop the computation here
        if np.all(np.abs(predicted_image_coords - next_image_coords) <= tolerance):
            return restore_array(predicted_image_coords, ground_coordinates.shape[:-1], last_dim=2)

        # Get the points indexes that have not yet converged
        pix_to_converge = np.where(np.any(np.abs(predicted_image_coords - next_image_coords) > tolerance, axis=1))[0]
        predicted_image_coords = next_image_coords

        # Perform the iterations only on pixel that have not concerged
        for itr in range(1, max_iterations):
            logger.debug(
                "Iteration %d : remaining points to converge : %d / %d",
                itr,
                pix_to_converge.shape[0],
                ground_coordinates.shape[0],
            )
            # Check closest integer coords
            clipped_image_coords[pix_to_converge] = self._check_coords(predicted_image_coords[pix_to_converge])
            # predicted_image_coords = self._check_coords_range(predicted_image_coords, geometric_unit)
            # current_ground_coord = set_geounit_direct_loc(integer_coordinates)
            # current_jac = numerical_jacobian(integer_coordinates)
            # estimated_ground_coord =
            #           current_ground_coord + current_jac_inv*(predicted_image_coords-current_ground_coord)
            # Compute the current ground coordinates based on the current image coordinates
            current_ground_coord[pix_to_converge] = set_geounit_direct_loc(
                clipped_image_coords[pix_to_converge], altitudes[pix_to_converge]
            )
            # Compute the jacobian of the partial_direct function
            current_jac[pix_to_converge] = numerical_jacobian(
                partial(
                    set_geounit_direct_loc,
                    altitude=np.repeat(altitudes[pix_to_converge], 2 * flat_ground_coords.shape[-1], axis=0),
                ),
                clipped_image_coords[pix_to_converge],
                epsilon=1,
            )
            # Compute the change in the ground coordinates
            delta_ground_coords = flat_ground_coords - current_ground_coord
            delta_ground_coords[:, 0] = (delta_ground_coords[:, 0] + 180) % 360 - 180
            # Compute the change in the image coordinates:
            #
            # current_jac is of shape (n, 2, 2)
            # Some functions in NumPy, have more flexible broadcasting options. For example,
            # numpy.linalg.inv can handle “stacked” arrays,
            # which is less expensive than inverting directly a (2*n, 2*n)-shaped matrix.
            # Also, the broadcasting mechanism in einsum allows us to perform matrix multiplication
            # operation efficiently, without having to loop over
            # each sample. delta_ground_coords : (n, 2), np.linalg.inv(current_jac): (n, 2, 2)

            delta_coords[pix_to_converge] = np.einsum(
                "ijk,ik->ij", np.linalg.inv(current_jac[pix_to_converge]), delta_ground_coords[pix_to_converge]
            )
            # Update the image coordinates
            # predicted_image_coords += delta_coords.astype(int)
            next_image_coords[pix_to_converge] = clipped_image_coords[pix_to_converge] + delta_coords[pix_to_converge]

            # re evaluate pixel list
            pix_to_converge = np.where(np.any(np.abs(predicted_image_coords - next_image_coords) > tolerance, axis=1))[
                0
            ]
            # If the change in the image coordinates is within the tolerance, stop the iteration
            if len(pix_to_converge) == 0:
                break
            # Update predicted for next iteration
            predicted_image_coords = next_image_coords
        if len(pix_to_converge) != 0:
            logger.warning(
                "Not all points have converged using %d iterations, remaining %d",
                max_iterations,
                len(pix_to_converge),
            )
        # restore to initial shape
        return restore_array(predicted_image_coords, ground_coordinates.shape[:-1], last_dim=2)

    def partial_direct_loc(
        self,
        coordinates: np.ndarray,
        altitude: float | ndarray | None = None,
        geometric_unit: str = "default",
    ):
        """
        The ``partial_direct_loc`` method takes image coordinates as input and returns ground
        coordinates only without the altitudes

        :param numpy.ndarray coordinates: Array of coordinates
        :param str geometric_unit: Name of a specific geometric unit to use (optional)
        :param float altitude: If float constant altitude to use for direct location,
                               if numpy array altitude to use for each coordinate,
                               if None the DEM is used
        :return: array of projected coordinates
        """
        ground_coords, _ = self.direct_loc(
            coordinates, altitude=altitude, geometric_unit=geometric_unit, sort_lines=True
        )
        if len(ground_coords.shape) == 1:
            ground_coords = ground_coords[np.newaxis]
        return ground_coords[:, :2]

    def sun_angles(self, ground_coordinates: ndarray, times: ndarray) -> ndarray:
        """
        Compute sun angles at the given location and times

        :param numpy.ndarray ground_coordinates: Array of ground coordinates
        :param numpy.ndarray times: Array of timestamp for each coordinate
        :return: Array of solar angles (azimuth + zenith angles)
        """
        flat_coords = flatten_array(ground_coordinates, 3)
        flat_times = flatten_array(times)
        assert flat_coords.shape[0] == flat_times.shape[0]

        dataset = {
            "position": flat_coords,
            "times": {
                "offsets": flat_times,
                "unit": self.default_time["unit"],
                "epoch": self.default_time["epoch"],
                "ref": self.default_time["ref"],
            },
        }
        # get sun position in EF cartesian ("times" -> "body_pos", "body_vel")
        self.body_model.body_pv(dataset, BodyId.SUN)

        # convert body position to topocentric ("body_pos", "position" -> "body_topo")
        # Note: the Orekit-based Earth body model uses geodetic coordinates for "position"
        self.body_model.ef_to_topocentric(
            dataset,
            coord_in="body_pos",
            ground_in="position",
            coord_out="body_topo",
        )
        assert "body_topo" in dataset
        angles = dataset["body_topo"]
        assert isinstance(angles, np.ndarray)

        # use zenith angle
        angles[:, 1] = 90.0 - angles[:, 1]

        # restore initial shape and drop last coord
        return restore_array(angles[:, :2], ground_coordinates.shape[:-1], last_dim=2)

    def sun_distances(self, ground_coordinates: Optional[ndarray], times: ndarray) -> ndarray:
        """
        Compute Sun distances to geodetic positions at given times.
        If `ground_coordinates` is None, compute Sun distances to center of Earth
        (Sun position vector norm in Earth-Fixed frame origin).

        :param numpy.ndarray ground_coordinates: Optional array of ground coordinates
        :param numpy.ndarray times: Array of timestamp for each coordinate
        :return: Array of solar distances, in meters
        """
        flat_times = flatten_array(times)
        dataset = {
            "times": {
                "offsets": flat_times,
                "unit": self.default_time["unit"],
                "epoch": self.default_time["epoch"],
                "ref": self.default_time["ref"],
            },
        }
        # get sun position in EF cartesian ("times" -> "body_pos", "body_vel")
        self.body_model.body_pv(dataset, BodyId.SUN)
        assert "body_pos" in dataset
        assert isinstance(dataset["body_pos"], np.ndarray)
        # sun coordinates
        vec = dataset["body_pos"]
        if ground_coordinates is not None:
            flat_coords = flatten_array(ground_coordinates, 3)
            assert flat_coords.shape[0] == flat_times.shape[0]
            dataset["position"] = flat_coords
            # convert ground coordinates of each point in EF
            self.body_model.geodetic_to_cartesian(dataset)
            assert isinstance(dataset["position"], np.ndarray)
            assert vec.shape == dataset["position"].shape
            # sun coordinates - EF coordinates
            vec -= dataset["position"]
        # compute the norm
        dist = np.linalg.norm(vec, axis=1)
        # restore initial shape
        return restore_array(dist, times.shape)

    def incidence_angles(self, ground_coordinates: ndarray, times: ndarray) -> ndarray:
        """
        Compute incidence angles (between local ground normal and ground to satellite vector)

        :param numpy.ndarray ground_coordinates: Array of ground coordinates
        :param numpy.ndarray times: Array of timestamp for each coordinates
        :return: Array of incidence angles (azimuth + zenith angles)
        """

        flat_coords = flatten_array(ground_coordinates, 3)
        flat_times = flatten_array(times)
        assert flat_coords.shape[0] == flat_times.shape[0]

        dataset = {
            "position": flat_coords,
            "times": {
                "offsets": flat_times,
                "unit": self.default_time["unit"],
                "epoch": self.default_time["epoch"],
                "ref": self.default_time["ref"],
            },
        }
        # get sun position in cartesian ("times" -> "orb_pos", "orb_vel")
        self.orbit_model.get_osv(dataset)

        # convert orb_pos to EF if needed
        if self.orbit_model.frame != FrameId.EF:
            self.body_model.change_reference_frame(
                dataset,
                frame_in=self.orbit_model.frame,
                frame_out=FrameId.EF,
                fields_in=["times", "orb_pos"],
            )

        # convert body position to topocentric ("orb_pos", "position" -> "orb_topo")
        # Note: the Orekit-based Earth body model uses geodetic coordinates for "position"
        self.body_model.ef_to_topocentric(
            dataset,
            coord_in="orb_pos",
            ground_in="position",
            coord_out="orb_topo",
        )
        incidence_angles = dataset["orb_topo"]

        # use zenith angle
        incidence_angles[:, 1] = 90.0 - incidence_angles[:, 1]

        # restore initial shape and drop last coord
        return restore_array(incidence_angles[:, :2], ground_coordinates.shape[:-1], last_dim=2)

    def viewing_angles(self, ground_coordinates: ndarray, times: ndarray) -> ndarray:
        """
        Compute viewing angles (between satellite nadir and satellite to ground vector)

        :param numpy.ndarray ground_coordinates: Array of ground coordinates
        :param numpy.ndarray times: Array of timestamp for each coordinates
        :return: Array of viewing angles (azimuth + zenith angles)
        """
        logging.getLogger(ASGARD_LOGGER_NAME).warning(
            "Viewing angles are not properly implemented. They are simply derived from incidence angles."
        )
        angles = self.incidence_angles(ground_coordinates, times)
        # add 180° to the azimuth
        angles[..., 0] = np.remainder(angles[..., 0] + 180.0, 360.0)
        return angles

    def footprint(self, sampling_step: int = 0, geometric_unit: str = "default") -> ndarray:
        """
        Compute the ground footprint of a geometric unit

        :param int sampling_step: Sampling step along each axis (in pixels), if 0 there is no sampling
                              between corners.
        :param str geometric_unit: Name of the geometric unit to use
        :return: Array of ground coordinates defining the footprint.
        """

        first_axis, second_axis = self.axes_names(geometric_unit)

        # check coordinates range
        max_value_col = self.coordinates[geometric_unit][first_axis] - 1
        max_value_lig = self.coordinates[geometric_unit][second_axis] - 1

        # build the footprint points
        step_col = max_value_col
        step_lig = max_value_lig
        if sampling_step > 0:
            step_col = sampling_step
            step_lig = sampling_step
        col_pts = list(range(0, max_value_col, step_col))
        lig_pts = list(range(0, max_value_lig, step_lig))
        points = []
        for col in col_pts:
            points.append([col, 0])
        for lig in lig_pts:
            points.append([max_value_col, lig])
        for col in col_pts:
            points.append([max_value_col - col, max_value_lig])
        for lig in lig_pts:
            points.append([0, max_value_lig - lig])
        img_coords = np.array(points, dtype="int32")

        # compute ground locations
        gnd_points, _ = self.direct_loc(img_coords, geometric_unit=geometric_unit)

        return gnd_points

    def pointing_angles(
        self,
        ground_coordinates: np.ndarray,
        reference_coordinates: np.ndarray,
        times: np.ndarray,
    ) -> np.array:
        """
        Compute the pointing angles between two targets seen from satellite. The angle computed is
        computed between vertices `TSR` where:

            - T: target ground point
            - S: spacecraft position
            - R: reference ground point

        Warning: the output pointing angles are always positive

        :param ground_coordinates: array of target ground geodetic coordinates (lon/lat/height)
        :param reference_coordinates: array of reference geodetic coordinate (lon/lat/height).
                                      Corresponds to a 0° pointing angle
        :param times: array of acquisition times for each pair of target point / reference point
        :return: array of pointing angles (in degrees)
        """

        flat_coords = flatten_array(ground_coordinates, 3)
        flat_ref_coords = flatten_array(reference_coordinates, 3)
        flat_times = flatten_array(times)

        nb_coords = flat_coords.shape[0]
        assert nb_coords == flat_times.shape[0]
        assert nb_coords == flat_ref_coords.shape[0]

        dataset = {
            "position": flat_coords,
            "reference": flat_ref_coords,
            "times": {
                "offsets": flat_times,
                "unit": self.default_time["unit"],
                "epoch": self.default_time["epoch"],
                "ref": self.default_time["ref"],
            },
        }
        # get satellite position in cartesian ("times" -> "orb_pos", "orb_vel")
        self.orbit_model.get_osv(dataset)

        # convert orb_pos to EF if needed
        if self.orbit_model.frame != FrameId.EF:
            self.body_model.change_reference_frame(
                dataset,
                frame_in=self.orbit_model.frame,
                frame_out=FrameId.EF,
                fields_in=["times", "orb_pos"],
            )

        # convert lon/lat/z to Earth Fixed cartesian X,Y,Z
        self.body_model.geodetic_to_cartesian(dataset, field_in="position", field_out="position_cart")
        self.body_model.geodetic_to_cartesian(dataset, field_in="reference", field_out="reference_cart")

        orb_pos = dataset["orb_pos"]
        ground_ef = dataset["position_cart"]
        reference_ef = dataset["reference_cart"]

        # compute angles
        vec_s_t = ground_ef - orb_pos
        vec_s_r = reference_ef - orb_pos
        norm_s_t = np.linalg.norm(vec_s_t, axis=1)
        norm_s_r = np.linalg.norm(vec_s_r, axis=1)
        unit_s_t = vec_s_t / norm_s_t.reshape((nb_coords, 1))
        unit_s_r = vec_s_r / norm_s_r.reshape((nb_coords, 1))

        scalar_product = np.clip(np.sum(unit_s_t * unit_s_r, axis=1), -1.0, 1.0)
        angles = np.rad2deg(np.arccos(scalar_product))

        return restore_array(angles, ground_coordinates.shape[:-1])


class AbstractOpticalGeometry(AbstractGeometry):
    """
    Common features for optical products
    """

    # TODO


class AbstractRadarGeometry(AbstractGeometry):
    """
    Common features for SAR and altimetry products
    """

    # TODO


class AbstractMicrowaveGeometry(AbstractGeometry):
    """
    Common features for microwave products
    """

    # TODO


def direct_location(product: AbstractGeometry, coordinates: ndarray, **kwargs) -> np.ndarray:
    """
    Wrapper function for AbstractProduct.direct_loc_bundle()

    :param AbstractProduct product: model class
    :param ndarray coordinates: Array of input image coordinates
    :return: array of projected coordinates and acquisition times
    """
    return product.direct_loc_bundle(coordinates, **kwargs)


def inverse_location(product: AbstractGeometry, coordinates: ndarray, **kwargs) -> np.ndarray:
    """
    Wrapper function for AbstractProduct.inverse_loc_bundle()

    :param AbstractProduct product: model class
    :param ndarray coordinates: Array of input image coordinates
    :return: array of projected coordinates and acquisition times
    """
    return product.inverse_loc(coordinates, **kwargs)


def sun_angles(product: AbstractGeometry, coordinates: ndarray) -> np.ndarray:
    """
    Wrapper function for AbstractProduct.sun_angles()

    :param AbstractProduct product: model class
    :param ndarray coordinates: Array of input image coordinates (lon, lat, alt, time)
    :return: array of Sun angles
    """
    return product.sun_angles(coordinates[..., 0:3], coordinates[..., 3])
