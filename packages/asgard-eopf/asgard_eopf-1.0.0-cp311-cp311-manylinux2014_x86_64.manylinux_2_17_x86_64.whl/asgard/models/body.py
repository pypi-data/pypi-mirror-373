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
Module for models implemented using Orekit library
"""
import math
from typing import List, Tuple

import numpy as np
import numpy.linalg as npl

# isort: off
from asgard.wrappers.orekit.utils import attach_thread  # pylint: disable=wrong-import-order

# isort: on

# pylint: disable=import-error
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.bodies import CelestialBodyFactory, GeodeticPoint, OneAxisEllipsoid
from org.orekit.frames import TopocentricFrame
from org.orekit.time import AbsoluteDate
from org.orekit.tools import PVProcessor
from org.orekit.utils import Constants, IERSConventions

# pylint: disable=ungrouped-imports
from asgard import ASGARD_VALIDATE_SCHEMAS
from asgard.core.body import BODY_GEOMETRY_SCHEMA, AbstractBody, BodyId, CoordinateType
from asgard.core.frame import FrameId
from asgard.core.math import flatten_array, restore_array, spherical_triangle_height
from asgard.core.schema import (
    TIME_ARRAY_SCHEMA,
    TIME_ARRAY_SCHEMA_ND,
    validate_or_throw,
)
from asgard.models.time import TimeReference
from asgard.wrappers.orekit import to_nio_view  # pylint: disable=no-name-in-module

GEODETIC_DISTANCE_EPSILON = 1e-6  #: Minimal distance (in m) between two points to compute relative azimuth
GEODETIC_DISTANCE_PLANAR = 1000.0  #: Maximum distance (in m) between two points to use planar approximation

THRESHOLD_GROUND_RANGE = 0.1  #: Convergence threshold (in m) to perform cross-track lookup

THRESHOLD_PROJECT_TO_TRACK = 1  #: Convergence threshold (in m) to search projection on track
MAX_ITER_PROJECT_TO_TRACK = 1000  #: maximum number of iterations when searching projection on track

#: List of ellipsoid models
ELLIPSOID_MODELS = ["GRS80", "WGS84", "IERS96", "IERS2003"]


class EarthBody(AbstractBody):
    """
    EarthBody class, that allows to convert coordinates between
    frames and compute geodetic distance using Orekit library.
    """

    def __init__(self, *args, **kwargs):
        # call superclass constructor
        super().__init__(*args, **kwargs)

        self.kind = BodyId.EARTH

        # detect ellipsoid type
        if "geometry" in kwargs:
            # Explicit geometry parameters have priority ...
            self.rad_eq = kwargs["equatorial_radius"]
            self.flattening = kwargs["flattening"]
        elif "ellipsoid" in kwargs:
            # Then we detect well known ellipsoids ...
            self.rad_eq = getattr(Constants, kwargs["ellipsoid"] + "_EARTH_EQUATORIAL_RADIUS")
            self.flattening = getattr(Constants, kwargs["ellipsoid"] + "_EARTH_FLATTENING")
        else:
            # Default with WGS84
            self.config["ellipsoid"] = "WGS84"
            self.rad_eq = Constants.WGS84_EARTH_EQUATORIAL_RADIUS
            self.flattening = Constants.WGS84_EARTH_FLATTENING

        assert isinstance(self.rad_eq, float)
        assert isinstance(self.flattening, float)
        # Compute other ellipsoid parameters
        self.rad_pol = self.rad_eq * (1.0 - self.flattening)
        self.ecc = math.sqrt(self.flattening * (2.0 - self.flattening))
        self.ecc2 = self.ecc**2  # squared excentricity

        #: TimeReference model to perform floating point to absolute date conversions and share its DataContext
        self._time_ref = kwargs.get("time_reference", None)
        if self._time_ref is None:
            self._time_ref = TimeReference()
        else:
            assert isinstance(self._time_ref, TimeReference)

        # setup frames
        frames_loader = self._time_ref.context.getFrames()
        #: Frames map (from asgard enum to Orekit Frame objects)
        self.frames = {
            FrameId.GCRF: frames_loader.getGCRF(),
            FrameId.EF: frames_loader.getITRF(IERSConventions.IERS_2010, True),
            FrameId.EME2000: frames_loader.getEME2000(),
            FrameId.EF_EQUINOX: frames_loader.getITRFEquinox(IERSConventions.IERS_2010, True),
            FrameId.MOD: frames_loader.getMOD(IERSConventions.IERS_1996),
            FrameId.TOD: frames_loader.getTOD(IERSConventions.IERS_2010, True),
            FrameId.GTOD: frames_loader.getGTOD(IERSConventions.IERS_2010, True),
        }
        #: OneAxisEllipsoid: ellipsoid attribute
        self.ellipsoid = OneAxisEllipsoid(
            self.rad_eq,
            self.flattening,
            self.frames[FrameId.EF],
        )

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for dataset, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/EarthBody.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "geometry": BODY_GEOMETRY_SCHEMA,
                "time_reference": {"type": "asgard.models.time.TimeReference"},
                "ellipsoid": {"type": "string", "enum": ELLIPSOID_MODELS},
            },
            "additionalProperties": False,
        }

    @property
    def time_reference_model(self):
        """
        Access to the internal TimeReference object
        """
        return self._time_ref

    def convert(
        self,
        point_3d: np.ndarray,
        coord_in: CoordinateType = CoordinateType.CARTESIAN,
        coord_out: CoordinateType = CoordinateType.GEODETIC,
    ) -> np.ndarray:
        """
        Transform between coordinate systems (distance in meters, angles in degrees)

        :param np.ndarray point_3d: ndarray with 3 coordinates.
        :param CoordinateType coord_in: Type of input coordinates
        :param CoordinateType coord_out: Type of output coordinates
        :return: Array of transformed coordinates (distance in meters, angles in degrees)
        :rtype: np.ndarray
        """
        dataset = {"position": point_3d}
        if coord_in == CoordinateType.CARTESIAN and coord_out == CoordinateType.GEODETIC:
            self.cartesian_to_geodetic(dataset, field_out=None)
        elif coord_in == CoordinateType.GEODETIC and coord_out == CoordinateType.CARTESIAN:
            self.geodetic_to_cartesian(dataset, field_out=None)
        return dataset["position"]

    def cartesian_to_geodetic(
        self,
        dataset,
        field_in: str = "position",
        field_out: str | None = None,
    ):
        """
        Transform to geodetic coordinate systems

        :param dataset: Dataset with:

            - "<field_in>" array of 3D coordinates to transform
        :param str field_in: Name of the table to transform (expect 3D coordinates in meters)
        :param str|None field_out: Name of output field (optional).
        :return: same dataset with transformed coordinates in degrees and meters
        """
        attach_thread()
        assert isinstance(dataset, dict)
        assert field_in in dataset  # check dataset is here
        assert isinstance(dataset[field_in], np.ndarray)
        assert dataset[field_in].dtype == "float64"

        # change shape, leave 3 components at the end
        flat_cartesian = flatten_array(dataset[field_in], last_dim=3)

        # cartesian to geodetic
        geodetic_positions_list = []
        for pos_x, pos_y, pos_z in flat_cartesian:
            # velocity not used, then use Vector3D only + body frame with ITRF
            vector = Vector3D(float(pos_x), float(pos_y), float(pos_z))
            geodetic_point = self.to_geodetic(vector)
            geodetic_positions_list.append(
                [
                    math.degrees(geodetic_point.getLongitude()),
                    math.degrees(geodetic_point.getLatitude()),
                    geodetic_point.getAltitude(),
                ]
            )
        geodetic_positions = np.array(geodetic_positions_list)
        geodetic_positions = geodetic_positions.reshape(dataset[field_in].shape)
        # Handle in-place conversion
        if not field_out:
            field_out = field_in
        # assign output array
        dataset[field_out] = geodetic_positions
        return dataset

    def to_geodetic(
        self,
        point: Vector3D,
        date: AbsoluteDate = AbsoluteDate.JULIAN_EPOCH,
    ) -> GeodeticPoint:
        """
        Helper method to convert a single :class:`org.hipparchus.geometry.euclidean.threed.Vector3D` cartesian point
        into a surface-relative :class:`org.orekit.bodies.GeodeticPoint`

        :param Vector3D point:    Cartesian point (in meters)
        :param AbsoluteDate date: Date of the computation (used for frames conversions)
        :return:                  Point at the same location but as a surface-relative point (in radians and meter)

        The frame is assumed to be Earth-Fixed.
        """
        geodetic_point = self.ellipsoid.transform(point, self.frames[FrameId.EF], date)
        return geodetic_point

    def geodetic_to_cartesian(
        self,
        dataset,
        field_in: str = "position",
        field_out: str | None = None,
    ):
        """
        Transform to cartesian coordinate systems

        :param dataset: Dataset with:

            - "<field_in>" array of 3D coordinates to transform
        :param str field_in: Name of the table to transform (expect 3D geodetic coordinates in degrees and meter)
        :param str|None field_out: Name of output field (optional).
        :return: same dataset with transformed coordinates in meters
        """
        attach_thread()
        # dataset[field_in] is an array of coordinates in degrees
        assert isinstance(dataset, dict)
        assert field_in in dataset  # check dataset is here
        assert isinstance(dataset[field_in], np.ndarray)
        assert dataset[field_in].dtype == "float64"
        # change shape, leave 3 components at the end
        flat_geodetic = flatten_array(dataset[field_in], last_dim=3)

        # geodetic to cartesian
        cartesian_positions_list = []
        for longitude, latitude, altitude in flat_geodetic:
            geodetic_point = GeodeticPoint(math.radians(latitude), math.radians(longitude), float(altitude))
            cartesian_point = self.ellipsoid.transform(geodetic_point)
            cartesian_positions_list.append([cartesian_point.getX(), cartesian_point.getY(), cartesian_point.getZ()])
        cartesian_positions = np.array(cartesian_positions_list)
        cartesian_positions = cartesian_positions.reshape(dataset[field_in].shape)
        # Handle in-place conversion
        if not field_out:
            field_out = field_in
        # assign output array
        dataset[field_out] = cartesian_positions
        return dataset

    def curvature_radius(self, sin_lat: float, azimuth: float) -> float:
        """
        Compute the curvature radius at a given latitude and along an azimuth

        :param sin_lat: Sinus of latitude
        :param azimuth: Azimuth angle with north direction (deg)
        :return: curvature radius (m)
        """

        radius_n = self.rad_eq / math.sqrt(1.0 - self.ecc2 * sin_lat**2)
        radius_m = ((1.0 - self.ecc2) * (radius_n / self.rad_eq) ** 2) * radius_n
        assert isinstance(radius_n, float)
        assert isinstance(radius_m, float)

        cos_az_2 = (math.cos(math.radians(azimuth))) ** 2
        sin_az_2 = (math.sin(math.radians(azimuth))) ** 2

        return 1.0 / (cos_az_2 / radius_m + sin_az_2 / radius_n)

    @staticmethod
    def get_local_azimuth(point: GeodeticPoint, direction: np.ndarray) -> float:
        """
        Compute the local azimuth of a given cartesian direction at a local geodetic point

        :param GeodeticPoint point: local geodetic point (rad, rad, m)
        :param np.ndarray direction: direction unit-vector in cartesian coordinates
        :return: azimuth relative to North, in degrees (between 0° and 360°)
        """
        attach_thread()
        north = np.array(point.getNorth().toArray())
        east = np.array(point.getEast().toArray())

        # extract of org.hipparchus.geometry.euclidean.threed.Vector3D angle subroutine
        norm_product = npl.norm(north) * npl.norm(direction)
        assert isinstance(norm_product, float)

        if norm_product == 0.0:
            raise RuntimeError("Zero norm vector product")

        dot_prod = np.vdot(north, direction)

        threshold = norm_product * 0.9999

        if dot_prod < -threshold or dot_prod > threshold:
            # the vectors are almost aligned, compute using the sine
            v3 = np.cross(north, direction)
            if dot_prod >= 0.0:
                azimuth = np.arcsin(npl.norm(v3) / norm_product)
                azimuth = np.rad2deg(azimuth)
                if np.dot(east, direction) < 0.0:
                    azimuth = 360.0 - azimuth
                return azimuth
            azimuth = np.pi - np.arcsin(npl.norm(v3) / norm_product)
            azimuth = np.rad2deg(azimuth)
            if np.dot(east, direction) < 0.0:
                azimuth = 360.0 - azimuth
            return azimuth

        azimuth = np.arccos(dot_prod / norm_product)
        azimuth = np.rad2deg(azimuth)
        if np.dot(east, direction) < 0.0:
            azimuth = 360.0 - azimuth
        return azimuth

    def geodetic_distance(
        self, lon1: float, lat1: float, lon2: float, lat2: float, height: float
    ) -> Tuple[float, float, float]:
        """
        Compute geodetic distance between 2 geodetic coordinates

        :param float lon1:  longitude of point 1 in degrees
        :param float lat1:  latitude of point 1 in degrees
        :param float lon2:  longitude of point 2 in degrees
        :param float lat2:  latitude of point 2 in degrees
        :param float height:  height in meters
        :return: Tuple with geodetic distance in meters and relative azimuths in degrees (1_to_2, and 2_to_1)
        :rtype: Tuple
        """
        # A
        geod1 = GeodeticPoint(math.radians(lat1), math.radians(lon1), float(height))
        # B
        geod2 = GeodeticPoint(math.radians(lat2), math.radians(lon2), float(height))

        # convert to cartesian
        cart1 = np.array(self.ellipsoid.transform(geod1).toArray())
        cart2 = np.array(self.ellipsoid.transform(geod2).toArray())

        return self._compute_single_geodetic_distance(geod1, geod2, cart1, cart2, height)

    def change_reference_frame(
        self,
        dataset,
        frame_in: FrameId = FrameId.EME2000,
        frame_out: FrameId = FrameId.EF,
        fields_in: List[str] | tuple[str, ...] = ("times", "position"),
        fields_out: List[str] | tuple[str, ...] | None = None,
    ):
        """
        Convert coordinates between frames

        :param dataset: Dataset with the fields to transform
        :param FrameId frame_in: Input frame (see FrameId enum)
        :param FrameId frame_out: Output frame (see FrameId enum)
        :param tuple(str,...) fields_in: List of input field names, with the following order:

            - [REQUIRED] times (in processing format)
            - [REQUIRED] position (cartesian X/Y/Z)
            - [OPTIONAL] velocity (cartesian X/Y/Z)
            - [OPTIONAL] acceleration (cartesian X/Y/Z)

        :param fields_out: List of output field names, in the order [position, velocity, acceleration].
                     As for inputs, velocity and acceleration are optional.
        :return: input dataset with converted coordinates
        """
        attach_thread()
        # get time table
        assert len(fields_in) >= 2
        time_array = dataset[fields_in[0]]
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(time_array, TIME_ARRAY_SCHEMA_ND)

        # NOTE use np.ascontiguousarray to fix #319:
        #   when the data is in a Fortran-style contiguous segment.
        # This check should probably be done in flatten_array and to_nio_view.
        # * https://numpy.org/doc/stable/reference/generated/numpy.ascontiguousarray.html
        # * https://numpy.org/doc/stable/reference/generated/numpy.ndarray.flags.html

        # get positions table
        inputs = {"pos": np.ascontiguousarray(dataset[fields_in[1]])}
        assert isinstance(inputs["pos"], np.ndarray)
        assert inputs["pos"].dtype == "float64"
        original_shape = inputs["pos"].shape
        inputs["pos"] = flatten_array(inputs["pos"], last_dim=3)
        outputs = {"pos": np.zeros(inputs["pos"].shape, dtype="float64")}

        epoch = self._time_ref.epoch_to_date(time_array)
        times = self._time_ref.offsets_to_seconds(time_array)

        # Prepare array views
        inputs_view = {}
        outputs_view = {}

        inputs_view["pos"] = to_nio_view(inputs["pos"])
        inputs_view["time"] = to_nio_view(times)
        outputs_view["pos"] = to_nio_view(outputs["pos"])

        # get optional velocity and acceleration
        if len(fields_in) >= 3:
            inputs["vel"] = np.ascontiguousarray(dataset.get(fields_in[2]))
            assert isinstance(inputs["vel"], np.ndarray)
            assert original_shape == inputs["vel"].shape
            inputs["vel"] = flatten_array(inputs["vel"], last_dim=3)
            outputs["vel"] = np.zeros(inputs["vel"].shape, dtype="float64")

            inputs_view["vel"] = to_nio_view(inputs["vel"])
            outputs_view["vel"] = to_nio_view(outputs["vel"])
        if len(fields_in) >= 4:
            inputs["acc"] = np.ascontiguousarray(dataset.get(fields_in[3]))
            assert isinstance(inputs["acc"], np.ndarray)
            assert original_shape == inputs["acc"].shape
            inputs["acc"] = flatten_array(inputs["acc"], last_dim=3)
            outputs["acc"] = np.zeros(inputs["acc"].shape, dtype="float64")

            inputs_view["acc"] = to_nio_view(inputs["acc"])
            outputs_view["acc"] = to_nio_view(outputs["acc"])

        PVProcessor.reproject(
            self.frames[frame_in],
            self.frames[frame_out],
            epoch,
            inputs_view["time"],
            inputs_view["pos"],
            inputs_view.get("vel"),
            inputs_view.get("acc"),
            outputs_view["pos"],
            outputs_view.get("vel"),
            outputs_view.get("acc"),
        )

        # fields_in: times position [velocity [acceleration]]
        # fields_tmp:      position [velocity [acceleration]]
        fields_tmp = list(fields_in[1:])
        if fields_out is None:
            fields_out = []
        common_length = min(len(fields_out), len(fields_tmp))
        # override with given output fields
        fields_tmp[:common_length] = fields_out[:common_length]
        # output position
        dataset[fields_tmp[0]] = outputs["pos"].reshape(original_shape)
        # output velocity
        if len(fields_tmp) >= 2:
            dataset[fields_tmp[1]] = outputs["vel"].reshape(original_shape)
        # output acceleration
        if len(fields_tmp) >= 3:
            dataset[fields_tmp[2]] = outputs["acc"].reshape(original_shape)
        return dataset

    def transform_orbit(self, orbit: dict, dest_frame: FrameId) -> dict:
        """
        Makes sure the orbit is in the ``dest_frame``. If not, convert it.

        :param orbit:                Orbit data expressed as :py:CONST:`asgard.core.schema.ORBIT_STATE_VECTORS_SCHEMA`.
        :param FrameId dest_frame:   Destination frame for the ``orbit`` data.
        :param EarthBody body_model: Body model used for the possible frame change.

        :return: The transformation is done in-place (in ``orbit``), and still returned.
        """
        crt_frame = orbit.get("frame", "EME2000")
        if crt_frame != dest_frame.name:
            fields = ["times", "positions"]  # REQUIRED input fields
            ds_chg_frame = {
                "times": orbit["times"][orbit["time_ref"]],
                "positions": orbit["positions"],
            }
            if "velocities" in orbit:
                ds_chg_frame["velocities"] = orbit["velocities"]
                fields.append("velocities")
                if "accelerations" in orbit:
                    ds_chg_frame["accelerations"] = orbit["accelerations"]
                    fields.append("accelerations")
            self.change_reference_frame(
                ds_chg_frame,
                frame_in=FrameId[crt_frame],
                frame_out=dest_frame,
                fields_in=fields,
            )
            times = ds_chg_frame.pop("times", None)
            assert times is not None
            orbit.update(ds_chg_frame)
            orbit["frame"] = dest_frame.name

        return orbit

    def body_pv(
        self,
        dataset,
        body_id: BodyId,
        frame_out: FrameId = FrameId.EF,
        field_in: str = "times",
        fields_out: List[str] | tuple[str, ...] = ("body_pos", "body_vel"),
    ):
        """
        Compute the body position and velocity in the given frame, at given times

        :param dataset: Input dataset.
        :param BodyId body_id: Id of the body (SUN/EARTH/MOON/...)
        :param FrameId frame_out: Output frame to express coordinates
        :param str field_in: Name of the time field in dataset, with a TIME_ARRAY structure
        :param tuple[str, ...] fields_out: List of output fields for body position and velocity
        :return: same dataset with computed coordinates
        """
        attach_thread()
        assert len(fields_out) == 2
        # get time table
        time_array = dataset[field_in]
        assert time_array is not None
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(time_array, TIME_ARRAY_SCHEMA_ND)
        epoch = self._time_ref.epoch_to_date(time_array)
        times = self._time_ref.offsets_to_seconds(time_array)

        if body_id == BodyId.SUN:
            body = CelestialBodyFactory.getSun()
        elif body_id == BodyId.MOON:
            body = CelestialBodyFactory.getMoon()
        elif body_id == BodyId.EARTH:
            body = CelestialBodyFactory.getEarth()
        else:
            raise RuntimeError(f"Body {body_id} is not handled yet!")

        output_pos = np.zeros((times.size, 3), dtype="float64")
        output_vel = np.zeros((times.size, 3), dtype="float64")

        PVProcessor.computeBody(
            body,
            self.frames[frame_out],
            epoch,
            to_nio_view(np.ascontiguousarray(times)),
            to_nio_view(output_pos),
            to_nio_view(output_vel),
        )

        dataset[fields_out[0]] = restore_array(output_pos, times.shape, 3)
        dataset[fields_out[1]] = restore_array(output_vel, times.shape, 3)

        return dataset

    def ef_to_topocentric(
        self,
        dataset,
        coord_in: str = "position",
        ground_in: str = "ground",
        coord_out: str = "topocentric",
    ):
        """
        Convert EF position to topocentric.

        .. warning::
            the ground coordinates to define the topocentric frame are GEODESIC (whereas in EOCFI, they use cartesian).

        :param dataset: Input dataset.
        :param str coord_in: Field name of input coordinates in cartesian EF
        :param str ground_in: Field name of ground coordinates for topocentric frame (geodetic)
        :param str coord_out: Output field name for topocentric coordinates
        :return: same dataset with computed coordinates
        """
        attach_thread()
        pos_arr = dataset.get(coord_in)
        topo_arr = dataset.get(ground_in)
        assert isinstance(pos_arr, np.ndarray)
        assert pos_arr.dtype == "float64"
        original_shape = pos_arr.shape

        assert isinstance(topo_arr, np.ndarray)
        assert topo_arr.dtype == "float64"
        assert topo_arr.shape == original_shape

        pos_arr = flatten_array(pos_arr, last_dim=3)
        topo_arr = flatten_array(topo_arr, last_dim=3)
        out_arr = np.zeros(pos_arr.shape, dtype="float64")
        date = AbsoluteDate.J2000_EPOCH
        ef_frame = self.frames[FrameId.EF]
        for idx, [pos_in, topo_in] in enumerate(zip(pos_arr, topo_arr)):
            # ground location for topocentric frame
            pt_topo = GeodeticPoint(math.radians(topo_in[1]), math.radians(topo_in[0]), float(topo_in[2]))
            topo_frame = TopocentricFrame(self.ellipsoid, pt_topo, "local_frame")
            ext_pt = Vector3D(float(pos_in[0]), float(pos_in[1]), float(pos_in[2]))
            out_arr[idx] = [
                math.degrees(topo_frame.getAzimuth(ext_pt, ef_frame, date)),
                math.degrees(topo_frame.getElevation(ext_pt, ef_frame, date)),
                topo_frame.getRange(ext_pt, ef_frame, date),
            ]

        dataset[coord_out] = out_arr.reshape(original_shape)
        return dataset

    def geodetic_path(
        self,
        dataset,
        position_in: str = "positions",
        distance_out: str = "distance",
        azimuth_out: str = "azimuth",
        height: float = 0.0,
    ):
        """
        Compute distance and azimuth along a geodetic path

        :param dataset: input dataset
        :param str position_in: field name for input positions (deg, deg, m)
        :param str distance_out: output field name for path distance (m)
        :param str azimuth_out: output field name for azimuth (deg)
        :param float height: altitude (m)
        :return: dataset with output tables
        """

        coordinates = dataset[position_in]
        assert len(coordinates) >= 2

        geodetic_points = [
            GeodeticPoint(math.radians(point[1]), math.radians(point[0]), height) for point in coordinates
        ]

        cartesian_points = [np.array(self.ellipsoid.transform(point).toArray()) for point in geodetic_points]

        # create output arrays
        distances = np.zeros((len(coordinates),), dtype="float64")
        azimuths = np.zeros((len(coordinates),), dtype="float64")

        geod1 = geodetic_points[0]
        cart1 = cartesian_points[0]
        position = 1

        for geod2, cart2 in zip(geodetic_points[1:], cartesian_points[1:]):
            # only need distance and azimuth from 1 to 2
            distance, azimuth, _ = self._compute_single_geodetic_distance(geod1, geod2, cart1, cart2, height)

            distances[position] = distance + distances[position - 1]
            azimuths[position - 1] = azimuth

            # don't forget to update point 1 for next iteration
            geod1 = geod2
            cart1 = cart2
            position += 1

        # propagate before-to-last azimuth to last point
        azimuths[-1] = azimuths[-2]

        # store outputs to dataset
        dataset[distance_out] = distances
        dataset[azimuth_out] = azimuths
        return dataset

    def _compute_single_geodetic_distance(
        self,
        geod1: GeodeticPoint,
        geod2: GeodeticPoint,
        cart1: np.ndarray,
        cart2: np.ndarray,
        height: float,
    ) -> Tuple[float, float, float]:
        """
        Internal function to compute a geodetic distance and azimuth

        :param GeodeticPoint geod1: First point as geodetic point (rad, rad, m)
        :param GeodeticPoint geod2: Second point as geodetic point (rad, rad, m)
        :param np.ndarray cart1: First point as cartesian point (m)
        :param np.ndarray cart2: Second point as cartesian point (m)
        :param float height: altitude in meters (m)
        :return: distance (m), azimuth 1 to 2 (deg), azimuth 2 to 1 (deg)
        """

        # geodetic distance and azimuth between 1 and 2
        vec_12 = cart2 - cart1
        dist_12 = np.sqrt(np.dot(vec_12, vec_12))
        assert isinstance(dist_12, float)

        if dist_12 < GEODETIC_DISTANCE_EPSILON:
            # points too close, no azimuth estimation
            return dist_12, 0.0, 180.0

        if dist_12 < GEODETIC_DISTANCE_PLANAR:
            # Plane approximation: using euclidian distance
            # need to compute azimuth
            dir_b = vec_12 / dist_12
            dir_a = -dir_b

            # in degrees
            azimuth12 = self.get_local_azimuth(geod1, dir_b)
            azimuth21 = self.get_local_azimuth(geod2, dir_a)
            return dist_12, azimuth12, azimuth21

        # compute normal to plane AOB (watch out for aligned points)
        norm_vec_aob = np.cross(cart1, cart2)
        length_vec_aob = np.sqrt(np.dot(norm_vec_aob, norm_vec_aob))
        if length_vec_aob < 1e-6:
            raise RuntimeError("Can't compute distance for two opposite points")
        norm_vec_aob *= 1.0 / length_vec_aob

        # get local zenith, north and west directions at A and B
        # TODO: avoid twice computation of Zenith ?
        zenith_a = np.array(geod1.getZenith().toArray())
        zenith_b = np.array(geod2.getZenith().toArray())

        # compute azimuth A->B and B->A
        dir_b = np.cross(norm_vec_aob, zenith_a)
        dir_b *= 1.0 / np.sqrt(np.dot(dir_b, dir_b))
        dir_a = np.cross(zenith_b, norm_vec_aob)
        dir_a *= 1.0 / np.sqrt(np.dot(dir_a, dir_a))

        # in degrees
        azimuth12 = self.get_local_azimuth(geod1, dir_b)
        azimuth21 = self.get_local_azimuth(geod2, dir_a)

        # Compute mean curvature radius
        sin_lat_1 = math.sin(geod1.getLatitude())
        sin_lat_2 = math.sin(geod2.getLatitude())

        # Precision can be improved by taking more samples to estimate the curvature radius along
        # the arc. For the moment, only the initial points A and B are used.
        # ...

        radius_1 = self.curvature_radius(sin_lat_1, azimuth12)
        radius_2 = self.curvature_radius(sin_lat_2, azimuth21)

        radius_mean = 0.5 * (radius_1 + radius_2) + height

        angle = 2.0 * math.asin(dist_12 * 0.5 / radius_mean)

        # in meters
        distance = radius_mean * angle

        return distance, azimuth12, azimuth21

    @staticmethod
    def normalize_long(lon_deg) -> float:
        """Normalize longitude in degrees to ]-π, +π]

        :param float lon_deg: longitude in degrees
        :return: longitude in radian in ]-π, +π]
        :rtype: float
        """
        lon_rad = math.radians(lon_deg)
        normalized_lon = (lon_rad + math.pi) % (2 * math.pi) - math.pi
        return normalized_lon

    def ground_range(self, point: np.ndarray, distance: int, normal: np.ndarray) -> np.ndarray:
        """
        Compute the geodetic point that is:

            - at a given altitude over the ellipsoid
            - inside a cut-plane defined by the input point and the plane normal vector
            - at a given signed distance from input point

        :param point: geodetic coordinates of start point (deg, deg, m)
        :param distance: signed distance along the range direction
        :param normal: cartesian vector (nx, ny, nz) defining the normal to cut plane
        :return: computed geodetic point (deg, deg, m)
        """
        attach_thread()
        geod = GeodeticPoint(math.radians(point[1]), math.radians(point[0]), float(point[2]))

        # convert to cartesian
        cart = np.array(self.ellipsoid.transform(geod).toArray())

        # find range direction: normal x zenith
        range_direction = np.cross(normal, cart)
        range_direction *= 1.0 / np.sqrt(np.dot(range_direction, range_direction))

        radius = np.sqrt(np.dot(cart, cart))
        geod_direction = cart / radius
        date = AbsoluteDate.JULIAN_EPOCH
        cur_range = distance
        for _i in range(10):
            angle = cur_range / radius
            moved_point = radius * (geod_direction * math.cos(angle) + range_direction * math.sin(angle))
            moved_vector = Vector3D(float(moved_point[0]), float(moved_point[1]), float(moved_point[2]))
            moved_geod = self.ellipsoid.transform(moved_vector, self.frames[FrameId.EF], date)
            moved_lon = math.degrees(moved_geod.getLongitude())
            moved_lat = math.degrees(moved_geod.getLatitude())

            # check actual distance
            raw_dist, _, _ = self.geodetic_distance(
                moved_lon,
                moved_lat,
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )
            dist_gap = distance - np.sign(distance) * raw_dist

            if dist_gap < THRESHOLD_GROUND_RANGE:
                break
            cur_range += dist_gap

        return np.array([moved_lon, moved_lat, point[2]])

    def _geocentric_radius(self, lat: float):
        """
        Compute the geocentric radius at a given latitude

        :param lat: Latitude in degrees
        :return: Earth geocentric radius (in meters)
        """

        cos_lat = math.cos(math.radians(lat))
        return self.rad_eq * math.sqrt(1.0 - self.ecc2) / math.sqrt(1.0 - self.ecc2 * cos_lat * cos_lat)

    def project_to_track(
        self,
        dataset,
        coord_in_key: str = "coords",
        track_pts_key: str = "track_points",
        track_dist_key: str = "track_distance",
        track_azi_key: str = "track_azimuth",
        xy_coord_key: str = "xy_coords",
    ):
        """
        Compute the projection of individual lon/lat coordinates on a ground track. The ground track
        is defined by a sequence of lon/lat coordinates of A_k track points. For each input
        lon/lat coordinate P, the function finds the closest point X along the track point, then
        computes distance XP, as well as the petric position of X along the track. The reference
        positions of A_k track points should be given as input.

        :param coordinates: ground coordinates to project on the track
        :param track_points: positions of track points (lon/lat)
        :param track_distance: distance of the track points along the track
        :param track_azimuth: azimuth angle along the track segments (output from geodetic_path())
        :return: array of across-track and along-track positions
        """

        coordinates = dataset[coord_in_key]
        track_points = dataset[track_pts_key]
        track_distance = dataset[track_dist_key]
        track_azimuth = dataset[track_azi_key]

        size = coordinates.shape[0]
        assert size >= 1
        assert coordinates.shape[1] >= 2

        track_count = track_points.shape[0]
        assert track_count >= 2
        assert track_distance.shape[0] == track_count
        assert track_azimuth.shape[0] == track_count
        assert track_points.shape[1] >= 2

        output = np.full((size, 2), np.nan, dtype="float64")

        beta_inter = 0.0

        # initialize default position at middle position
        prev_pos = track_count // 2

        for x in range(size):
            interval_not_found = 1
            nb_iter = 0
            direction = 0
            prev_direction = 0
            prev_dist = 0.0

            # start search at the previous position
            cur_pos = prev_pos

            # iterative search of the closest track segment
            while 0 <= cur_pos < track_count and interval_not_found and nb_iter < MAX_ITER_PROJECT_TO_TRACK:
                # get local track azimuth
                beta_12 = track_azimuth[cur_pos]

                # compute distance and azimuth to current point
                dist, az_1_to_2, _ = self.geodetic_distance(
                    track_points[cur_pos, 0],
                    track_points[cur_pos, 1],
                    coordinates[x, 0],
                    coordinates[x, 1],
                    0.0,
                )

                # check distance threshold
                if dist < THRESHOLD_PROJECT_TO_TRACK:
                    direction = 0
                    interval_not_found = 0
                    break

                # compute angle with track
                beta_inter = beta_12 - az_1_to_2
                if beta_inter <= -180.0:
                    beta_inter += 360.0
                if beta_inter > 180.0:
                    beta_inter -= 360.0

                # compute next direction
                direction = 1 if abs(beta_inter) < 90.0 else -1

                # detect direction change
                if nb_iter == 0:
                    prev_direction = direction

                if prev_direction == direction:
                    nb_iter += 1
                    cur_pos += direction
                    prev_dist = dist
                else:
                    interval_not_found = 0

            # handle points not found
            if interval_not_found:
                cur_pos = max(cur_pos, 0)
                cur_pos = min(cur_pos, track_count - 1)
                prev_pos = cur_pos
                continue

            # update previous position
            prev_pos = cur_pos

            # move to the previous point if needed
            if direction == -1:
                cur_pos += direction
                # swap cached distances 'dist' and 'prev_dist' so that:
                #  - 'dist' corresponds to Q1P
                #  - 'prev_dist' corresponds to Q2P
                dist, prev_dist = (prev_dist, dist)
            elif direction == 0:
                output[x, 0] = 0.0
                output[x, 1] = track_distance[cur_pos]
                continue

            # get mean geocentric radius
            radius = self._geocentric_radius(
                (track_points[cur_pos, 1] + track_points[cur_pos + 1, 1] + coordinates[x, 1]) / 3.0
            )

            # Solve spherical triangle
            xp_angle, q1x_angle = spherical_triangle_height(
                (track_distance[cur_pos + 1] - track_distance[cur_pos]) / radius,  # angle Q1Q2
                prev_dist / radius,  # angle Q2P
                dist / radius,  # angle Q1P
            )

            output[x, 0] = np.sign(-beta_inter) * round(radius * xp_angle)
            output[x, 1] = track_distance[cur_pos] + radius * q1x_angle

        dataset[xy_coord_key] = output
        return dataset

    def frame_transform(
        self,
        dataset,
        frame_in: FrameId = FrameId.EME2000,
        frame_out: FrameId = FrameId.EF,
        field_in: str = "times",
        fields_out: List[str] | tuple[str, ...] = ("translation", "rotation"),
    ):
        """
        Compute the translation T and rotation R between two frames at given times, so that:
            P_out = T + R( P_in )

        :param dataset: input dataset
        :param frame_in: input frame
        :param frame_out: output frame
        :param field_in: Input field name for times
        :param fields_out: Output fields names for translation vectors and rotation quaternions
        """
        attach_thread()
        time_array = dataset[field_in]
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(time_array, TIME_ARRAY_SCHEMA)

        assert len(fields_out) == 2
        size = len(time_array["offsets"])

        out_trans = np.zeros((size, 3), dtype="float64")
        out_rot = np.zeros((size, 4), dtype="float64")

        for idx, date in enumerate(self._time_ref.to_dates(time_array)):
            # the convention used in Orekit are such that we need to ask for transform from frame_out
            # to frame_in.
            transfo = self.frames[frame_out].getTransformTo(self.frames[frame_in], date)
            translation = transfo.getTranslation()
            rot = transfo.getRotation()
            translation_rotated = rot.applyTo(translation)
            out_trans[idx, :] = [translation_rotated.getX(), translation_rotated.getY(), translation_rotated.getZ()]
            out_rot[idx, :] = [rot.getQ1(), rot.getQ2(), rot.getQ3(), rot.getQ0()]

        dataset[fields_out[0]] = out_trans
        dataset[fields_out[1]] = out_rot
