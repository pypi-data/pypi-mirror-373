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
# pylint: disable=C0302
"""
Module for orbit modelization
"""

import logging
import math
from enum import Enum
from itertools import dropwhile
from typing import Any, Tuple

import numpy as np
from scipy.spatial.transform import Rotation as R

from asgard import ASGARD_VALIDATE_SCHEMAS

# isort: off
# Orekit wrappers needs to be imported before any org.orekit module
# noqa: F401  # pylint: disable=unused-import,wrong-import-order,ungrouped-imports
from asgard.wrappers.orekit.utils import attach_thread

# noqa: F401  # pylint: disable=import-error,wrong-import-order
from org.hipparchus.geometry.euclidean.threed import (
    Vector3D,
    Rotation,
)
from org.orekit.attitudes import (
    NadirPointing,
    YawCompensation,
)

from org.orekit.propagation.analytical import (
    Ephemeris,
    EcksteinHechlerPropagator,
)
from org.orekit.orbits import (
    KeplerianOrbit,
)
from org.orekit.time import (
    AbsoluteDate,
)
from org.orekit.utils import (
    AbsolutePVCoordinates,
    AngularDerivativesFilter,
    CartesianDerivativesFilter,
    Constants,
    ImmutableTimeStampedCache,
    TimeStampedAngularCoordinates,
    TimeStampedPVCoordinates,
    TimeStampedPVCoordinatesHermiteInterpolator,
)
from org.orekit.tools import PVProcessor, AttitudeProcessor, TransformProcessor

# Specific includes for OrbitScenarioModel
from org.hipparchus.util import MathUtils
from org.orekit.time import TimeScalesFactory
from org.orekit.tools import OrbitPropagator

from asgard.core import schema
from asgard.models.time import TimeReference

from org.orekit.propagation import SpacecraftState

# isort: on

from asgard.core.frame import FrameId
from asgard.core.math import is_sorted, vector3d_to_list

# from asgard.core.logger import format_as_tree
from asgard.core.orbit import AbstractOrbitModel
from asgard.core.schema import (
    AOCS_MODEL_SCHEMA,
    ASCII_TIMESTAMP_SCHEMA,
    ATTITUDE_SCHEMA,
    ORBIT_SCENARIO_SCHEMA,
    ORBIT_STATE_VECTORS_SCHEMA,
    TIME_ARRAY_SCHEMA,
    does_validate,
    refining_axis,
    validate_or_throw,
)
from asgard.core.time import DEFAULT_EPOCH, DEFAULT_UNIT, TimeRef
from asgard.core.toolbox import array_get, check_if, check_precond
from asgard.core.transform import RigidTransform
from asgard.models.attitude import ZeroDopplerAttitudeProvider
from asgard.models.time import _extract_time_reference
from asgard.wrappers.orekit import to_nio_view  # pylint: disable=no-name-in-module

logger = logging.getLogger("asgard.models.orbit")


# Dirty hacks to inject missing functions in AbsoluteDate in order to make them comparable
# and thus usable from standard algorithms like np.searchsorted()
def _lt_abs_date(lhs: AbsoluteDate, rhs: AbsoluteDate) -> bool:
    assert isinstance(rhs, AbsoluteDate), f"Expecting AbsoluteDate, got {rhs}: {type(rhs)}"
    return lhs.compareTo(rhs) < 0


def _le_abs_date(lhs: AbsoluteDate, rhs: AbsoluteDate) -> bool:
    assert isinstance(rhs, AbsoluteDate), f"Expecting AbsoluteDate, got {rhs}: {type(rhs)}"
    return lhs.compareTo(rhs) <= 0


def _gt_abs_date(lhs: AbsoluteDate, rhs: AbsoluteDate) -> bool:
    assert isinstance(rhs, AbsoluteDate), f"Expecting AbsoluteDate, got {rhs}: {type(rhs)}"
    return lhs.compareTo(rhs) > 0


def _ge_abs_date(lhs: AbsoluteDate, rhs: AbsoluteDate) -> bool:
    assert isinstance(rhs, AbsoluteDate), f"Expecting AbsoluteDate, got {rhs}: {type(rhs)}"
    return lhs.compareTo(rhs) >= 0


def _add_abs_date(lhs: AbsoluteDate, rhs: float) -> AbsoluteDate:
    return lhs.shiftedBy(float(rhs))


def _sub_abs_date(lhs: AbsoluteDate, rhs: AbsoluteDate) -> float:
    if isinstance(rhs, AbsoluteDate):
        return lhs.durationFrom(rhs)
    return lhs.shiftedBy(-float(rhs))


AbsoluteDate.__lt__ = _lt_abs_date
AbsoluteDate.__le__ = _le_abs_date
AbsoluteDate.__gt__ = _gt_abs_date
AbsoluteDate.__ge__ = _ge_abs_date
AbsoluteDate.__add__ = _add_abs_date
AbsoluteDate.__sub__ = _sub_abs_date


def _altitude_is_positive(i_osv: tuple[int, TimeStampedPVCoordinates]) -> bool:
    """Tells when the altitude of a tuple (int, OSV) is positive"""
    return i_osv[1].getPosition().getZ() >= 0


def _next_positive_altitude(i_osvs: list[tuple[int, TimeStampedPVCoordinates]], start_idx: int) -> int:
    """
    Return index of the next OSV with a positive altitude.

    Meant to be called when the OSV at start_idx position has a negative altitude -- unchecked
    """
    idx, _ = next(filter(_altitude_is_positive, i_osvs[start_idx:]), (-1, None))
    return idx


def _next_negative_altitude(i_osvs: list[tuple[int, TimeStampedPVCoordinates]], start_idx: int) -> int:
    """
    Return index of the next OSV with a negative altitude.

    Meant to be called when the OSV at start_idx position has a positive altitude -- unchecked
    """
    idx, _ = next(dropwhile(_altitude_is_positive, i_osvs[start_idx:]), (-1, None))
    return idx


def clamp(date: AbsoluteDate, low: AbsoluteDate, high: AbsoluteDate) -> AbsoluteDate:
    """Clamp a ``date`` between two ``low`` and ``high`` bounds."""
    if date.compareTo(low) < 0:
        return low
    if high.compareTo(date) < 0:
        return high
    return date


class DerivativeMode(Enum):  # pylint: disable=too-few-public-methods
    """
    Enumerate for selecting which derivatives to use in interpolation:

    Similar/matches :class:`org.orekit.utils.CartesianDerivativesFilter` and
    :class:`org.orekit.utils.AngularDerivativesFilter`.
    """

    #: Equivalent to :attr:`org.orekit.utils.CartesianDerivativesFilter.USE_P` - Use only positions, ignoring velocities
    NO_DERIV = 0
    #: Equivalent to :attr:`org.orekit.utils.CartesianDerivativesFilter.USE_PV` - Use only positions and velocities
    FIRST_DERIV = 1
    #: Equivalent to :attr:`org.orekit.utils.CartesianDerivativesFilter.USE_PVA` - Use only positions, velocities and
    #: accelerations
    SECOND_DERIV = 2

    def to_cartesian(self) -> CartesianDerivativesFilter:
        """Convert this enum to the corresponding :class:`org.orekit.utils.CartesianDerivativesFilter`"""
        out = CartesianDerivativesFilter.USE_P
        if self == self.FIRST_DERIV:
            out = CartesianDerivativesFilter.USE_PV
        elif self == self.SECOND_DERIV:
            out = CartesianDerivativesFilter.USE_PVA
        return out

    def to_angular(self) -> AngularDerivativesFilter:
        """Convert this enum to the corresponding :class:`org.orekit.utils.AngularDerivativesFilter`"""
        out = AngularDerivativesFilter.USE_R
        if self == self.FIRST_DERIV:
            out = AngularDerivativesFilter.USE_RR
        elif self == self.SECOND_DERIV:
            out = AngularDerivativesFilter.USE_RRA
        return out


class GenericOrbitModel(AbstractOrbitModel):
    """
    Generic Orbit Model, implemented with :class:`org.orekit.utils.TimeStampedPVCoordinates`.
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for orbit estimation

        :download:`JSON schema <doc/scripts/init_schema/schemas/GenericOrbitModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "orbit": ORBIT_STATE_VECTORS_SCHEMA,
                "attitude": {
                    "type": "object",
                    "oneOf": [
                        ATTITUDE_SCHEMA,
                        AOCS_MODEL_SCHEMA,
                    ],
                },
                "refining": {
                    "center_time": {
                        "type": "object",
                        "properties": {
                            "TAI": {},
                            "UTC": {},
                            "UT1": {},
                            "GPS": {},
                        },
                        "minProperties": 1,
                        "additionalProperties": False,
                    },
                    "default_time": {
                        "type": "object",
                        "properties": {
                            "ref": {},
                            "unit": {},
                            "epoch": {},
                        },
                    },
                    "spacecraft_corr_coeff": refining_axis("x", "y", "z"),
                },
                "interpolation_window": {"type": "integer"},  # default=10
                "earth_body": {"type": "asgard.models.body.EarthBody"},
                "time_orb": ASCII_TIMESTAMP_SCHEMA,
            },
            "required": ["orbit", "attitude", "earth_body"],
            "additionalProperties": False,
        }

    def __init__(self, **kwargs):
        """
        Orbit model constructor.

        :param orbit:                        Orbit definition,
                                             see :py:CONST:`asgard.core.schema.ORBIT_STATE_VECTORS_SCHEMA`
        :param attitude:                     Attitude definition, see :py:CONST:`asgard.core.schema.ATTITUDE_SCHEMA`
        :param int interpolation_window:     Window size used for Hermitian interpolations (default: 10)
        :param EarthBody earth_body:         Model used for frames conversions, and to define time model
        :param str time_orb:                 A reference time to compute orbit information -- if not specified,
                                             :attr:`info` cannot be evaluated.
        """
        super().__init__(**kwargs)
        logger.debug("Initialize orbit...")
        # logger.debug("... from %s", format_as_tree(self.config))
        self.__init_orbit()
        self.__init_attitude()

        logger.debug(
            "Orbit model initialized with %s points between %s and %s (frame: %s)",
            len(self._cached["times"]),
            self._earliest_time,
            self._latest_time,
            self._frame,
        )

    def __init_orbit(self) -> None:
        """Constructor part dedicated to Orbit attributes initialization"""
        orbit_cfg = self.config["orbit"]
        #: Internal reference to the EarthBody model used
        self._earth_body = self.config["earth_body"]
        #: Internal reference to the TimeReference model used
        self._time_model = self._earth_body.time_reference_model
        #: Frame into which the orbit is defined
        self._frame: FrameId = FrameId[orbit_cfg.get("frame", "EME2000")]
        #: Store orbit & attitude frame as an Orekit object
        self._orekit_frame = self._earth_body.frames[self._frame]
        logger.debug("Frame: %s (%s)", self._orekit_frame, type(self._orekit_frame))

        positions = orbit_cfg["positions"]
        velocities = orbit_cfg["velocities"]
        # TODO: Use acceleration if set, or ignore velocities if absent.
        # accelerations = orbit_cfg["accelerations"]

        # Setup time settings to use
        self._time = {}
        #: TimeRef used for the times offsets, and the attitude quaternions
        self._time["ref"] = TimeRef[_extract_time_reference(orbit_cfg, "times")]
        #: Associated time scale object (orekit data type: TimeScale)
        self._time["scale"] = self._time_model.timeref_to_timescale(self._time["ref"])

        times = orbit_cfg["times"][self._time["ref"].name]
        self._time["epoch"] = times.get("epoch", DEFAULT_EPOCH)
        self._time["unit"] = times.get("unit", DEFAULT_UNIT)
        check_if(is_sorted(times["offsets"]), "Invalid time offsets: they were expected sorted, but they are not")

        dates = list(self._time_model.to_dates(times, time_ref=self._time["ref"]))

        # Check data are consistent
        len_times = len(dates)
        len_pos = len(positions)
        len_vel = len(velocities)
        check_if(
            len_times == len_pos and len_times == len_vel,
            f"Mismatching number of times ({len_times}), positions ({len_pos}) and velocities ({len_vel})",
        )

        assert len_times > 0, "Please initialize the OrbitModel with a strictly positive number of data"

        pv_coords = [
            TimeStampedPVCoordinates(
                time,
                Vector3D(*position.tolist()),
                Vector3D(*velocity.tolist()),
                Vector3D.ZERO,  # Can we have an acceleration?
            )
            for time, position, velocity in zip(dates, positions, velocities)
        ]
        interpolation_window = self.config.setdefault("interpolation_window", 10)
        #: Cache/memorize information for later use (OSV, times, ...)
        self._cached = {
            #: "osv" caches PV coordinates already known/computed for different frames
            "osv": {self._frame: pv_coords},
            "pv": ImmutableTimeStampedCache(interpolation_window, pv_coords.array_list()),
            "times": dates,
        }
        # Add refining parameter if provided
        self.refining_info = self.config.get("refining")
        #: First date of the orbit samples (!= start_date)
        self._earliest_time: AbsoluteDate = dates[0]
        #: Last date of the orbit samples (!= stop_date)
        self._latest_time: AbsoluteDate = dates[-1]

        #: Reference time to compute orbit information -- defaults to None
        # logger.debug("orbit config: %s", format_as_tree(self.config))
        self._time_orb: AbsoluteDate = self.__extract_time("time_orb", self.config, None)

        # Analyse indices where new absolut orbits start
        if "absolute_orbit" in self.config["orbit"]:
            absolute_orbit_list = self.config["orbit"]["absolute_orbit"]
            assert isinstance(absolute_orbit_list, np.ndarray)
            orbit_changes = np.where(absolute_orbit_list[:-1] != absolute_orbit_list[1:])[0] + 1
            self._cached["absolute_orbit_indices"] = np.concatenate(([0], orbit_changes, [len(absolute_orbit_list)]))

    def __init_attitude(self) -> None:
        """
        Constructor part dedicated to Attitude attributes initialization

        For now, only attitudes and YSM are supported.
        """
        attitude_cfg = self.config["attitude"]
        att_frame = FrameId[attitude_cfg.get("frame", "EME2000")]
        self._att_frame = att_frame
        if self._frame != att_frame:
            logger.warning(
                "Orbit state vector and attitudes have different frames: %s vs %s",
                self._frame.name,
                self._att_frame.name,
            )

        if does_validate(attitude_cfg, ATTITUDE_SCHEMA):
            self.__init_attitude_samples()
        elif does_validate(attitude_cfg, AOCS_MODEL_SCHEMA):
            self.__init_attitude_model()
        else:
            logger.warning("Cannot initialize attitudes!")

    def __init_attitude_samples(self) -> None:
        """
        Constructor part dedicated to Attitude attributes initialization from samples of actual attitudes.
        """
        attitude_cfg = self.config["attitude"]
        att_time_ref = TimeRef[_extract_time_reference(attitude_cfg, "times")]
        if self._time["ref"] != att_time_ref:
            logger.warning(
                "Time scale for attitudes (%s) is different from orbit one (%s)",
                att_time_ref,
                self._time["ref"],
            )

        times = attitude_cfg["times"][att_time_ref.name]
        check_if(is_sorted(times["offsets"]), "Invalid time offsets: they were expected sorted, but they are not")

        dates = list(self._time_model.to_dates(times, time_ref=att_time_ref))
        quaternions = attitude_cfg["quaternions"]
        len_times = len(dates)
        len_quaternions = len(quaternions)
        check_if(
            len_times == len_quaternions,
            f"Mismatching number of times ({len_times}) and quaternions ({len_quaternions})",
        )

        assert len_times > 0, "Please initialize the OrbitModel with a strictly positive number of attitude data"

        angular_coords = [
            TimeStampedAngularCoordinates(
                time,
                Rotation(float(quat[3]), float(quat[0]), float(quat[1]), float(quat[2]), False),
                Vector3D.ZERO,
                Vector3D.ZERO,
            )
            for time, quat in zip(dates, quaternions)
        ]

        # interpolation_window corresponds to the parameter aNeighborsSize
        # in orekit.rugged.api.RuggedBuilder
        # it represents the number of points to use for attitude interpolation
        interpolation_window = self.config.setdefault("interpolation_window", 4)
        if interpolation_window > len(angular_coords):  # pylint: disable=R1730
            interpolation_window = len(angular_coords)
        self._cached["a"] = ImmutableTimeStampedCache(interpolation_window, angular_coords.array_list())

    def __init_attitude_model(self) -> None:
        """
        Constructor part dedicated to Attitude attributes initialization from YSM model.

        From Rugged:
        https://gitlab.orekit.org/orekit/rugged/-/blob/master/src/tutorials/java/fr/cs/examples/refiningPleiades/models/OrbitModel.java#L235
        """
        aocs_mode = self.config["attitude"].get("aocs_mode")

        if aocs_mode == "YSM":
            ground_pointng_law = NadirPointing(self._orekit_frame, self.earth_body_model.ellipsoid)
            attitude_provider = YawCompensation(self._orekit_frame, ground_pointng_law)
            self._cached["attitude_provider"] = attitude_provider
        elif aocs_mode == "ZD":
            self._cached["attitude_provider"] = ZeroDopplerAttitudeProvider(
                self._earliest_time,
                self._earth_body.frames[FrameId.TOD],
                self._orekit_frame,
            )
        else:
            raise ValueError(f"Unsupported AOCS mode: {aocs_mode}")

    def __extract_time(self, key: str, config: dict, default: AbsoluteDate | None = None) -> AbsoluteDate | None:
        """
        Helper function for extracting time values from configurations
        """
        if key in config:
            return self._time_model.str_to_absolute_date(config[key], self._time["scale"])
        return default

    @property
    def earth_body_model(self):
        """Access to the internal :class:`asgard.models.EarthBody` object"""
        return self._earth_body

    @property
    def time_reference_model(self):
        """Access to the internal :class:`asgard.models.TimeReference` object"""
        return self._time_model

    @property
    def frame(self) -> FrameId:
        """Get the frame of orbit coordinates."""
        return self._frame

    @property
    def valid_range(self) -> Tuple[float, float]:
        """Get the orbit validity range"""

        # convert to offsets using the same settings as the orbit times
        start = self._time_model.from_date(
            self._earliest_time,
            ref=self._time["ref"],
            epoch=self._time["epoch"],
            unit=self._time["unit"],
        )
        end = self._time_model.from_date(
            self._latest_time,
            ref=self._time["ref"],
            epoch=self._time["epoch"],
            unit=self._time["unit"],
        )
        return start, end

    def _absolute_orbit_index(self, absolute_orbit_number: int) -> int:
        """Return the relative index of ``absolute_orbit_number`` from the first known absolute orbit."""
        return absolute_orbit_number - self.config["orbit"]["absolute_orbit"][0]

    @staticmethod
    def _interpolate_one_osv(
        date: AbsoluteDate,
        cartesian_derivative_filter: CartesianDerivativesFilter,
        earliest_time: Any,
        latest_time: Any,
        cached_pv: Any,
    ) -> TimeStampedPVCoordinates:
        """
        Internal function to interpolate one OSV on the orbit -- takes Orekit types.

        :param AbsoluteDate date: date of the point to interpolate
        :param CartesianDerivativesFilter cartesian_derivative_filter: Derivative mode to use
        :return: Actual date (may be clamped to min-max dates), position and velocity
        """

        pv_interpolation_date = clamp(date, earliest_time, latest_time)

        # use ImmutableTimeStampedCache
        pv_time_interpolator = TimeStampedPVCoordinatesHermiteInterpolator(
            min(
                cached_pv.getNeighbors(
                    pv_interpolation_date, ImmutableTimeStampedCache.cast_(cached_pv).getMaxNeighborsSize()
                ).count(),
                15,  # 15 => Maximum recommended by doc
            ),
            cartesian_derivative_filter,
        )

        interpolated_pv = pv_time_interpolator.interpolate(
            pv_interpolation_date,
            cached_pv.getNeighbors(
                pv_interpolation_date, ImmutableTimeStampedCache.cast_(cached_pv).getMaxNeighborsSize()
            ),
        )

        pos_vel = interpolated_pv.shiftedBy(date.durationFrom(pv_interpolation_date))
        # logger.debug("Interpolate orbit @ %s -> XYZ=%s, V=%s", date, pos, vel)
        return pos_vel

    def get_osv(
        self,
        dataset,
        field_time: str = "times",
        fields_out: Tuple[str, str] = ("orb_pos", "orb_vel"),
        derivative_mode: DerivativeMode = DerivativeMode.FIRST_DERIV,
    ):  # pylint: disable=arguments-differ
        """
        Return the orbit state vector at a given time. The output fields are computed respectively
        as position, velocity and acceleration.

        :param dataset: Dataset with:

            - a :py:CONST:`asgard.core.schema.TIME_ARRAY_SCHEMA` under ``field_time`` key.  If no ``ref`` sub key is
              provided, "GPS" will be assumed.

        :param str field_time:       Field names where time offsets are stored in the ``dataset``
        :param List[str] fields_out: Field names where computed positions and velocities will be stored in ``dataset``
        :param DerivativeMode derivative_mode: filter for derivatives from the sample to use in interpolation.
        :return: same dataset with orbit state vector

        .. note::

            From Orekit documentation:  The interpolated state vector are created by polynomial Hermite interpolation
            ensuring velocity remains the exact derivative of position.

            Note that even if first time derivatives (velocities) from sample can be ignored, the interpolated instance
            always includes interpolated derivatives. This feature can be used explicitly to compute these derivatives
            when it would be too complex to compute them from an analytical formula: just compute a few sample points
            from the explicit formula and set the derivatives to zero in these sample points, then use interpolation to
            add derivatives consistent with the positions.

        :warning: All child classes are expected to define :meth:`get_osv`. However, variations about the actual
            parameters are expected between :class:`AbstractOrbitModel` and its child classes. This abstract method is
            not a *real* abstract method as far as OO design is concerned; several tools (like mypy, Pycharm) are likely
            to warn us about incorrect overriding. See this abstract :meth:`get_osv` as just a documentation artefact:
            "All *Orbit Models* are expected to provide a method named ``get_osv``". And don't expect to be able to
            write generic code that calls ``get_osv`` and that will work with any specialization of
            :class:`asgard.core.orbit.AbstractOrbitModel`.
        """
        attach_thread()
        # logger.debug("OSV on %s", format_as_tree(dataset))
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(dataset, {field_time: TIME_ARRAY_SCHEMA})
        times = dataset[field_time]
        time_ref = times.get("ref", "GPS")
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(times, TIME_ARRAY_SCHEMA)
        epoch = self._time_model.epoch_to_date(times)
        offsets_sec = self._time_model.offsets_to_seconds(times)

        nb_epochs = len(times["offsets"])
        cartesian_derivative_filter = derivative_mode.to_cartesian()
        logger.debug(
            "Interpolate orbit state vectors for %s points, with a maximum derivation order of %s",
            nb_epochs,
            cartesian_derivative_filter.getMaxOrder(),
        )

        # Apply refining if refining data have been provided
        pos_corrections_lof = None
        if self.refining_info:
            pos_corrections_lof = self._estimate_lof_corrections(times["offsets"])

        # Prepare outputs
        out_pos = np.ndarray(shape=(nb_epochs, 3))
        out_vel = np.ndarray(shape=(nb_epochs, 3))

        # Interpolate pos/vel for each time offset in the list
        pv_processor = PVProcessor(self._cached["pv"])
        pv_processor.interpolatePV(epoch, to_nio_view(offsets_sec), to_nio_view(out_pos), to_nio_view(out_vel))

        # apply refining corrections
        pos = None
        vel = None
        prev_date = None
        if pos_corrections_lof is not None:
            for i, date in enumerate(self._time_model.to_dates(times, time_ref=TimeRef[time_ref])):
                # TODO: be able to take a sequence of AbsoluteDate, or a TIME_ARRAY_SCHEMA
                #       or define a generator that takes a sequence of orekit data types, and yields Orekit OSV type.
                if prev_date != date:
                    prev_date = date
                    pos = out_pos[i]
                    vel = out_vel[i]

                    # Define and apply transformation from Local Orbital Frame (lof) to eme2000
                    transfo_lof_to_body = self.transform_lof_to_body(pos, vel)

                    # Use the corrected position in eme2000 frame as the new position
                    pos = transfo_lof_to_body.transform_position(pos_corrections_lof[i])

                out_pos[i] = pos

        # add position and velocity to selected dataset fields
        dataset[fields_out[0]] = out_pos
        dataset[fields_out[1]] = out_vel
        return dataset

    @staticmethod
    def transform_lof_to_body(pos, vel):
        """
        Get the transform from the local orbital (LOF) frame to the body frame

        :param pos: satellite position in body frame
        :param vel: satellite velocity in body frame

        :return: transformation object between lof and body frame
        """
        # Define translation vectors
        translation = pos

        # Define rotation vectors
        z_axis = -(pos / np.linalg.norm(pos))

        x_axis = np.cross(vel, z_axis)
        x_axis = x_axis / np.linalg.norm(x_axis)

        y_axis = np.cross(z_axis, x_axis)

        # Get rotation matrix for transform lof -> eme2000
        rotation = np.stack([x_axis, y_axis, z_axis], axis=1)

        # Create transform object
        return RigidTransform(translation, rotation)

    def compute_quaternions(
        self,
        dataset,
        field_time: str = "times",
        field_quat: str = "attitudes",
        derivative_mode: DerivativeMode = DerivativeMode.NO_DERIV,
        field_pos: str = "orb_pos",
        field_vel: str = "orb_vel",
        s3_convention: bool = True,
    ):  # pylint: disable=arguments-differ,too-many-positional-arguments
        """
        Computes the attitude quaternions of the platform for given times. The output is added
        to the dataset. The output quaternions follow the scalar-last convention.

        :param dataset: Dataset with:

            - "times" array

        :param str field_time: name of the time field
        :param str field_quat: name of the output quaternion field
        :param DerivativeMode derivative_mode: number of derivatives to use in interpolation.
        :param orb_pos: name of orbit position field (may be used to estimate attitude models)
        :param orb_vel: name of orbit velocity field (may be used to estimate attitude models)
        :param s3_convention: spacecraft axis follow s3 convention
        :return: same dataset with attitudes

        :warning: All child classes are expected to define :meth:`compute_quaternions`. However, variations about the
            actual parameters are expected between :class:`AbstractOrbitModel` and its child classes. This abstract
            method is not a *real* abstract method as far as OO design is concerned; several tools (like mypy, Pycharm)
            are likely to warn us about incorrect overriding. See this abstract :meth:`compute_quaternions` as just a
            documentation artefact: "All *Orbit Models* are expected to provide a method named ``compute_quaternions``".
            And don't expect to be able to write generic code that calls ``compute_quaternions`` and that will work with
            any specialization of :class:`AbstractOrbitModel`.
        """
        attach_thread()
        time_array = dataset[field_time]
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(time_array, TIME_ARRAY_SCHEMA)
        epoch = self._time_model.epoch_to_date(time_array)
        times = self._time_model.offsets_to_seconds(time_array)

        if derivative_mode != DerivativeMode.NO_DERIV:
            raise NotImplementedError("Only NO_DERIV mode is supported for now")

        # Prepare outputs
        out_quat = np.ndarray(shape=(len(time_array["offsets"]), 4))

        att_frame_obj = self._earth_body.frames[self._att_frame]

        # Determine how attitudes are computed
        if "a" in self._cached:
            quat_processor = AttitudeProcessor(self._cached["a"])
            quat_processor.interpolateR(epoch, to_nio_view(times), to_nio_view(out_quat))

            # See corrections based on OSV done in
            # https://www.orekit.org/site-orekit-11.3.3/jacoco/org.orekit.attitudes/TabulatedLofOffset.java.html#L123
        else:
            if dataset.get(field_pos) is None or dataset.get(field_vel) is None:
                # Maybe check the dimensions matches with input times
                # We need to generate PV coordinates
                self.get_osv(
                    dataset,
                    field_time=field_time,
                    fields_out=(field_pos, field_vel),
                )

            if getattr(self._cached["attitude_provider"], "getAttitudes", None):
                # We can use the vectorized function to compute attitudes
                out_quat = self._cached["attitude_provider"].getAttitudes(
                    dataset[field_pos],
                    dataset[field_vel],
                    self._orekit_frame,
                    epoch,
                    times,
                    att_frame_obj,
                )

            else:
                logger.warning("Attitude model doesn't provide vectorized function, iteration done in Python")
                # Evaluate quaternion for each time offset in the list
                prev_date = None
                rot = None
                pos = dataset[field_pos]
                vel = dataset[field_vel]
                for i, date in enumerate(self._time_model.to_dates(time_array)):
                    if prev_date != date:
                        prev_date = date
                        interp_pv = TimeStampedPVCoordinates(
                            date,
                            Vector3D(*pos[i].tolist()),
                            Vector3D(*vel[i].tolist()),
                        )

                        rot = self._cached["attitude_provider"].getAttitudeRotation(
                            AbsolutePVCoordinates(
                                att_frame_obj,  # self._orekit_frame,
                                interp_pv,
                            ),
                            date,
                            att_frame_obj,
                        )

                    assert rot is not None
                    q = rot.getQ1(), rot.getQ2(), rot.getQ3(), rot.getQ0()
                    if s3_convention:
                        conv_mat = np.array([[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]])

                        quat_composed = R.from_quat(q) * R.from_matrix(conv_mat)
                        q = quat_composed.as_quat()
                    out_quat[i] = q

        # Change frame if needed
        if self._att_frame != self._frame:
            quat_att_to_pv = np.ndarray(shape=(len(time_array["offsets"]), 4), dtype="float64")
            TransformProcessor.estimateStatic(
                self._orekit_frame,
                att_frame_obj,
                epoch,
                to_nio_view(times),
                None,
                to_nio_view(quat_att_to_pv),
            )
            rot_att_to_pv = R.from_quat(quat_att_to_pv)
            out_rot = rot_att_to_pv * R.from_quat(out_quat)
            out_quat = out_rot.as_quat()

        dataset[field_quat] = out_quat
        return dataset

    def _instantiate_keplerian_orbit(self, date: AbsoluteDate) -> KeplerianOrbit:
        """
        Internal function to instantiate a :class:`org.orekit.orbits.KeplerianOrbit` object at the selected date.
        :param AbsoluteDate date: Date at which the KeplerianOrbit is evaluated.

        .. note::

            - The actual OSV for the evaluation will be interpolated from the actual orbit sampled.
            - The OSV will be converted on-the-fly into the pseudo-inertial True Of Date reference frame.
        """
        point0 = GenericOrbitModel._interpolate_one_osv(
            date, CartesianDerivativesFilter.USE_PV, self._earliest_time, self._latest_time, self._cached["pv"]
        )
        # logger.debug("Keplerian Orbit @ %s", point0)
        if self._frame != FrameId.TOD:
            # Legacy was using "True of Date" reference frame for computing Keplerian element.
            # It happens to be a pseudo-inertial frame, which is a requirement for Orekit Kepler related computations.
            # Then we need to convert the OSV into a pseudo inertial frame as KeplerianOrbit doesn't support non
            # pseudo-inertial frames
            # Let's use True of Date frame reference that legacy was using.
            frame = self._earth_body.frames[FrameId.TOD]
            assert (
                frame.isPseudoInertial()
            ), f"Orekit require frame to be pseudo-inertial for computing Kepler elements. {frame} is not."
            to_gcrf_transform = self._orekit_frame.getTransformTo(frame, date)
            point = to_gcrf_transform.transformPVCoordinates(point0)
        else:
            point = point0
            frame = self._orekit_frame

        orbit = KeplerianOrbit(point, frame, Constants.WGS84_EARTH_MU)
        return orbit

    def _get_osv_samples_in(self, frame: FrameId):
        """
        Return the (cached on the fly) OSV samples used to define the orbit in the specified frame.
        """
        if frame not in self._cached["osv"]:
            frame_dst = self._earth_body.frames[frame]
            osvs = [
                self._orekit_frame.getTransformTo(frame_dst, pv.getDate()).transformPVCoordinates(pv)
                for pv in self._cached["osv"][self._frame]
            ]
            self._cached["osv"][frame] = osvs
        return self._cached["osv"][frame]

    def _instantiate_ephemeris(self) -> Ephemeris:
        if self._frame != FrameId.TOD:
            # Legacy was using "True of Date" reference frame for computing Keplerian element.
            # It happens to be a pseudo-inertial frame, which is a requirement for Orekit Kepler related computations.
            # Then we need to convert the OSV into a pseudo inertial frame as KeplerianOrbit doesn't support non
            # pseudo-inertial frames
            # Let's use True of Date frame reference that legacy was using.
            frame = self._earth_body.frames[FrameId.TOD]
            assert (
                frame.isPseudoInertial()
            ), f"Orekit require frame to be pseudo-inertial for computing Kepler elements. {frame} is not."

            osvs = [
                self._orekit_frame.getTransformTo(frame, pv.getDate()).transformPVCoordinates(pv)
                for pv in self._cached["osv"]
            ]
        else:
            osvs = self._cached["osv"]
            frame = self._orekit_frame
        spacecraft_states = [SpacecraftState(AbsolutePVCoordinates(frame, pv)) for pv in osvs]
        eph = Ephemeris(spacecraft_states.array_list(), self.config.get("interpolation_window", 10))
        return eph

    def get_info(  # pylint: disable=too-many-positional-arguments
        self,
        date: AbsoluteDate | str | float | None,
        time_ref: TimeRef | None = None,
        epoch: str = DEFAULT_EPOCH,
        unit: str = DEFAULT_UNIT,
        abs_orbit: int | None = None,
    ) -> dict:
        """
        Evaluate the Ascending Node Crossing (ANX) in Earth-Fixed frame (as with EOCFI).

        Also compute the nodal period in days, plus other Keplerian parameters that can be extracted at chosen date.

        :param date:             Time at which the parameters will be extracted
        :type date:              AbsoluteDate|str|float
        :param TimeRef time_ref: Time scale to interpret ``date`` when passed in processing format (``float``) --
                                 ignored otherwise.
        :param str epoch:         Epoch
        :param str unit:         Unit ("d"/"s") to interpret ``date`` when passed in processing format (``float``) --
                                 ignored otherwise.
        :param int abs_orbit:  Optional absolute orbit number for which ANX will be searched.
                               By default, the absolute orbit number associated to ``date`` will be computed and used.
        :return: a dictionary of the Keplerian parameters, and other information:

            - "anx_date": :class:`org.orekit.time.AbsoluteDate` of the ANX,
            - "abs_orbit": Absolute orbit number computed/used to search for the ANX -- only if "absolute_orbit"
              information was fed into the ``GenericOrbitModel`` construction.
            - "track_direction": tracking direction at the requested ``date`` ("ascending" or "descending")
            - "anx_long": Longitude of the ANX in degrees, ∈ [0, 360]
            - "utc_anx": float offset from UTC epoch, expressed in days
            - "gps_anx": float offset from GPS epoch, expressed in days
            - "pox_anx": Cartesian position coordinates of the ANX, in Earth-Fixed frame (meters)
            - "vel_anx": Cartesian velocity coordinates of the ANX, in Earth-Fixed frame (meters/second)
            - "osc_kepl": Osculating Kepler elements at the ANX

                - "a" : Semi-major axis,
                - "e" : Eccentricity,
                - "i" : Inclination (degrees -- not normalized, yet),
                - "m" : Mean anomaly (degrees, ∈ [0, 360]),
                - "w" : Argument of Perigee (degrees -- not normalized, yet),
                - "ra" : Right ascension of the ascending node (degrees -- not normalized, yet),
            - "mean_kepl": Mean Kepler elements at the ANX. Same keys as the "osc_kepl",
            - "period_jd": duration of the current orbit, expressed in days,
            - "nodal_period": duration of the current orbit, expressed in seconds,

        :rtype: dict
        :raise NotImplementedError: if ``date`` is outside the range of ``earliest`` and ``latest`` times.
        """
        attach_thread()
        assert abs_orbit or date, "orbit.get_info() shall be called on an absolute_orbit number or a date!"

        if date is not None:
            date = self._time_model.any_time_as_date(date, time_ref, epoch, unit)
            logger.debug("Evaluate Orbit information at %s", date)
            check_precond(
                self._earliest_time < date,
                NotImplementedError,
                "Cannot search orbit information outside the range of the sample orbit: "
                f"requested date {date} <= first point ({self._earliest_time}). "
                "Have you initialized the orbit model with an 'time_orb'?",
            )
            check_precond(
                date <= self._latest_time,
                NotImplementedError,
                "Cannot search orbit information outside the range of the sample orbit: "
                f"requested date {date} >= last point ({self._latest_time})",
            )

            (
                abs_orbit_computed,
                first_abs_orbit_point,
                last_abs_orbit_point,
            ) = self._search_time_interval_around_anx(date)

            if abs_orbit:  # called with abs_orbit and date
                assert abs_orbit == abs_orbit_computed, (
                    f"Orbit information requested on incompatible date {date} and orbit #{abs_orbit}. "
                    "The date belongs to orbit #{abs_orbit_computed} "
                )
            else:  # called with just date
                abs_orbit = abs_orbit_computed
        else:  # called with just abs_orbit
            assert abs_orbit is not None, "we know abs_orbit can't be None in that case"
            logger.debug("Evaluate Orbit information for orbit #%s", abs_orbit)
            abs_orbit_idx = self._absolute_orbit_index(abs_orbit)
            absolute_orbit_indices = self._cached["absolute_orbit_indices"]
            first_abs_orbit_point = absolute_orbit_indices[abs_orbit_idx]
            last_abs_orbit_point = array_get(absolute_orbit_indices, abs_orbit_idx + 1, -1)
            date = self._cached["times"][first_abs_orbit_point]

        # Propagation before the first OSV sampled is required for this purpose.
        check_if(
            first_abs_orbit_point > 0,
            f"(not-supported) Cannot search the ANX of the first absolute orbit (#{abs_orbit})",
            exception=NotImplementedError,
        )

        # Do compute the first ANX
        anx_info = self._search_anx_earth_fixed(abs_orbit, first_abs_orbit_point)

        if date >= anx_info["date"]:  # usual case
            logger.debug("-> ANX (orbit=%s): %s", abs_orbit, anx_info)

            # The nodal period will be calculated as the Δ (in seconds) between current ANX and the next
            if 0 <= last_abs_orbit_point < len(self._cached["times"]):
                anx2_info = self._search_anx_earth_fixed(abs_orbit + 1 if abs_orbit else None, last_abs_orbit_point)
            else:
                logger.warning(
                    "Orbit info requested on the last orbit (#%s) of the sample. "
                    "We can not evaluate the ANX of the following orbit (yet). "
                    "And thus we cannot calculate the nodal period.",
                    abs_orbit,
                )
                anx2_info = None
        else:  # Case where the date given is in between 2 orbits, and before the ANX of the second orbit
            anx2_info = anx_info
            assert (
                abs_orbit is not None
            ), "This situation can only happen when sign searching orbit change in orbit list"
            abs_orbit -= 1
            abs_orbit_idx = self._absolute_orbit_index(abs_orbit)
            absolute_orbit_indices = self._cached["absolute_orbit_indices"]
            first_abs_orbit_point = absolute_orbit_indices[abs_orbit_idx]
            anx_info = self._search_anx_earth_fixed(abs_orbit, first_abs_orbit_point)

        # Nodal period is computed exactly on ANX'es found
        if anx2_info:

            nodal_period_seconds = anx2_info["date"] - anx_info["date"]
            # Nodal period, in days
            nodal_period_days = nodal_period_seconds / Constants.JULIAN_DAY
        else:
            nodal_period_days = NotImplemented
            nodal_period_seconds = NotImplemented

        orbit = self._instantiate_keplerian_orbit(anx_info["date"])

        # TODO: ---- fix MSLT computation...
        # (applying a final modulo 24 seems to yield close results. But is it correct???)
        # ts_UT1 =  self._time_model.timeref_to_timescale(TimeRef.UT1)
        # t_ut1_mjd2000 = date.offsetFrom(AbsoluteDate.J2000_EPOCH, ts_UT1)
        # L = 280.46592 + 0.9856473516 * (t_ut1_mjd2000/JD_TO_SECONDS - 0.5) # degree
        # mlst = (ra - math.radians(L) + math.pi) * 12 / math.pi

        # TODO: ---- Compute Spacecraft Midnight (SMX)
        # -> Halfway moment between the nadir transitions: day->night and night->day (after tge ANX of the orbit)
        #    - Transition day->night == transition Sun Zenith Angle goes over 90°
        #    - Transition night->day == transition Sun Zenith Angle goes under 90°

        req_osv = GenericOrbitModel._interpolate_one_osv(
            date, CartesianDerivativesFilter.USE_PV, self._earliest_time, self._latest_time, self._cached["pv"]
        )
        track_direction = "descending" if req_osv.getVelocity().getZ() < 0 else "ascending"

        anx_pos = anx_info["osv"].getPosition()
        anx_geo_pt = self._earth_body.to_geodetic(anx_pos, anx_info["date"])

        info = {
            "anx_date": anx_info["date"],
            "abs_orbit": abs_orbit,
            "track_direction": track_direction,
            # "mlst": mlst,
            "anx_long": math.degrees(anx_geo_pt.getLongitude()) % 360,
            "utc_anx": self._time_model.from_date(anx_info["date"], TimeRef.UTC),
            "pos_anx": vector3d_to_list(anx_pos),
            "vel_anx": vector3d_to_list(anx_info["osv"].getVelocity()),
            "osc_kepl": {
                "a": orbit.getA(),  # semi-major axis
                "e": orbit.getE(),  # Eccentricity
                # TODO: check/compare-with-eocfi if these angles need to be in [0, 360]
                "i": math.degrees(orbit.getI()),  # Inclination
                "m": math.degrees(orbit.getMeanAnomaly()) % 360,
                "w": math.degrees(orbit.getPerigeeArgument()),
                "ra": math.degrees(orbit.getRightAscensionOfAscendingNode()),
            },
            "period_jd": nodal_period_days,
            "nodal_period": nodal_period_seconds,
            # "utc_smx": None,  # TODO: UTC time of spacecraft midnight (unit: processing format: days)
            "gps_anx": self._time_model.from_date(anx_info["date"], TimeRef.GPS),
        }

        # ---- Computation of Keplerian mean elements
        info = info | _compute_mean_keplerian_elements(orbit, anx_info["date"])

        return info

    def _search_time_interval_around_anx(
        self, date_post_anx, abs_orbit: int | None = None
    ) -> tuple[int | None, int, int]:
        """
        Searches the time interval that surrounds the ANX that happens before the specified date.

        Let's call:

        - A_i the time interval of the OSV that belongs to the i-th absolute date (/ in between two ANX)
        - t_b{i} the first sampled PV from A_i -- b for begin
        - t_e{i} the last sampled PV from A_i -- e for end

        Possible cases:

        - t < t_e0: propagation will be needed before the very first PV sampled t_b0 in order to find the exact ANX
        - t ∈ [t_e{i}, t_b{i+1}]: there only one ANX, we cannot known beforehand whether t belongs to A_i or A{i+1}, we
          return [t_e{i}, t_b{i+1}]
        - t ∈ [t_b{i}, t_e{i}] == A_i: we look for t_e{i-1} and return [t_e{i-1}, t_b{i}]
        - t > t_e{N-1}, ANX for A_n will belong to [t_e{n-1}, t_b{n}], there is no A_{n+1} after that, we cannot compute
          manually the nodel_period between A_n and A_{n+1}

        :return: absolute orbit, index of the first point before the ANX, same for the next ANX

        .. precondition::

            - ``self._earliest_time < date_post_anx <= self._latest_time``
        """
        # Search the index of next nearest point in cached OSV
        date_position = np.searchsorted(self._cached["times"], date_post_anx)
        # logger.debug("%s -> %s-th position", date_post_anx, date_position)
        assert not (date_position == 0 and date_post_anx < self._cached["times"][0]), (
            "Cannot search orbit information outside the range of the sample orbit: "
            f"requested date {date_post_anx} < last point ({self._cached['times'][0]})"
        )
        nb_samples = len(self._cached["times"])
        assert date_position < nb_samples, (
            "Cannot search orbit information outside the range of the sample orbit: "
            f"requested date {date_post_anx} > last point ({self._cached['times'][-1]})"
        )

        # Let's reduce the time range searched thanks to absolute_orbit numbers (if provided)
        # Indeed, each time the ascending node is crossed, the absolute orbit number is incremented by one.
        if "absolute_orbit" in self.config["orbit"]:
            absolute_orbit_list = self.config["orbit"]["absolute_orbit"]
            absolute_orbit_indices = self._cached["absolute_orbit_indices"]

            # Absolute orbit of the next OSV sampled
            if abs_orbit is None:  # if not forced by parameter => compute it
                abs_orbit = absolute_orbit_list[date_position]
            logger.debug("Absolute orbit of the next OSV sampled after %s: #%s", date_post_anx, abs_orbit)

            # in between 2 orbits <= different orbits at, and before date_position, unless date_post_anx is a sampled
            # date
            # is_in_between_two_orbits = (absolute_orbit_list[date_position - 1] != abs_orbit
            #                            ) and (
            #                             not date_post_anx == self._cached["times"][date_position]
            #                            )
            abs_orbit_idx = abs_orbit - absolute_orbit_list[0]

            first_abs_orbit_point = absolute_orbit_indices[abs_orbit_idx]  # =~ t_bi; included
            assert (
                absolute_orbit_list[first_abs_orbit_point] == abs_orbit
            ), f"{absolute_orbit_list[first_abs_orbit_point]} != {abs_orbit}"

            assert abs_orbit_idx + 1 < len(
                absolute_orbit_indices
            ), "By construction, the post last index is in the list"
            last_abs_orbit_point = absolute_orbit_indices[abs_orbit_idx + 1]  # =~ t_ei; excluded
            # next ANX belongs to ]last_abs_orbit_point -1, last_abs_orbit_point], if not last orbit

        else:
            # Handle case when we have no absolute_orbit information => search for sign increase on Z
            abs_orbit = None
            osvs = self._get_osv_samples_in(FrameId.EF)
            i_osvs = list(enumerate(osvs))  # -> zip(index + osv)
            # search last z<0 before date_position
            start, _ = next(
                filter(
                    lambda i_osv: i_osv[1].getPosition().getZ() < 0,
                    reversed(i_osvs[:date_position]),
                ),
                (-1, None),
            )
            logger.debug("index of last z<0 before #%s -> %s", date_position, start)
            logger.debug(
                "checks [%s..%s[ -> %s",
                start,
                start + 2,
                [osv.getPosition().getZ() for osv in osvs[start : start + 2]],
            )
            # search next Z positive after that negative Z.
            first_abs_orbit_point = _next_positive_altitude(i_osvs, start)
            assert start + 1 == first_abs_orbit_point
            # For next ANX, need to search again; dropwhile > 0 + next > 0
            dnx_idx = _next_negative_altitude(i_osvs, first_abs_orbit_point)
            last_abs_orbit_point = _next_positive_altitude(i_osvs, dnx_idx)
        # next ANX belongs to ]last_abs_orbit_point -1, last_abs_orbit_point], if not last orbit
        logger.debug(
            "%s (%s-th) belongs to orbit #%s. Concerns points [%s, %s[ ([%s, %s[)",
            date_post_anx,
            date_position,
            abs_orbit,
            first_abs_orbit_point,
            last_abs_orbit_point,
            self._cached["times"][first_abs_orbit_point],
            self._cached["times"][last_abs_orbit_point] if last_abs_orbit_point < nb_samples else "Ω",
        )
        return abs_orbit, first_abs_orbit_point, last_abs_orbit_point

    def _start_of_second_orbit(self) -> AbsoluteDate:
        """
        Search the start of the second (absolute) orbit
        """
        if "absolute_orbit" in self.config["orbit"]:
            absolute_orbit_indices = self._cached["absolute_orbit_indices"]
            assert len(
                absolute_orbit_indices
            ), "At least two absolute orbits are required to return the start of the second one"
            return absolute_orbit_indices[1]

        # Else: Handle case when we have no absolute_orbit information => search for the 2nd sign increase on Z
        osvs = self._get_osv_samples_in(FrameId.EF)
        i_osvs = list(enumerate(osvs))  # -> zip(index + osv)
        if i_osvs[0][1].getPosition().getZ() < 0:  # unexpected situation, let's ignore the first points
            start = _next_positive_altitude(i_osvs, 0)
        else:  # situation expected
            start = 0
        # search one negative, then next positive
        dnx_idx = _next_negative_altitude(i_osvs, start)
        second_orbit = _next_positive_altitude(i_osvs, dnx_idx)
        return i_osvs[second_orbit][1].getDate()

    def _search_anx_earth_fixed(
        self,
        abs_orbit,
        idx_osv_in_new_abs_orbit,
        z_precision=1e-4,
        time_precision=1e-9,
    ) -> dict:
        """
        Binary search of ANX between known points expressed in Earth-Fixed frame.

        .. note::

            - thanks to Earth-Fixed frame, we can search when Z position becomes positive.

        .. pre-conditions::

            - the indexes match OSV sampled

        .. todo::

            - Implement the search with other more efficient methods Newton...
            - We only need to evaluate the Z axis, and none of X, Y, VX, VY, VZ...
        """
        # TODO: try to search to use a barycenter instead of middle...
        idx_osv_in_last_abs_orbit = idx_osv_in_new_abs_orbit - 1
        first_time = self._cached["times"][idx_osv_in_last_abs_orbit]
        last_time = self._cached["times"][idx_osv_in_new_abs_orbit]
        logger.debug(
            "- We search for ANX before orbit #%s; i.e. within [%s, %s] ([%s, %s])",
            abs_orbit,
            idx_osv_in_last_abs_orbit,
            idx_osv_in_new_abs_orbit,
            first_time,
            last_time,
        )
        osvs = self._get_osv_samples_in(FrameId.EF)

        first_osv = osvs[idx_osv_in_last_abs_orbit]
        last_osv = osvs[idx_osv_in_new_abs_orbit]
        if np.isclose(first_osv.getPosition().getZ(), 0.0, atol=z_precision):
            # First is the anx
            return {"date": first_time, "osv": first_osv}
        if np.isclose(last_osv.getPosition().getZ(), 0.0, atol=z_precision):
            # Last is the anx
            return {"date": last_time, "osv": last_osv}
        assert first_osv.getPosition().getZ() < 0
        assert last_osv.getPosition().getZ() >= 0
        delta_time = last_time - first_time
        assert delta_time > time_precision, "at least one iteration is expected"
        nb_iter = 0
        # While the neighbors used for the interpolation don't change during all the following calls to
        # _interpolate_one_osv
        # (indeed we always interpolate between the same two OSV from the original orbit samples),
        # caching them doesn't make a sensible performance difference.

        # prepare neighbors from the EF OSV (as they don't change)
        pv_time = self._time_model.from_date(
            first_time + (delta_time) / 2,
            ref=self._time["ref"],
            epoch=self._time["epoch"],
            unit=self._time["unit"],
        )
        osv_times = self.config["orbit"]["times"][self._time["ref"].name]["offsets"]
        interp_pos = np.searchsorted(osv_times, pv_time)
        neighbor_start = max(0, interp_pos - self.config["interpolation_window"] // 2)
        neighbor_end = min(len(self._cached["times"]), neighbor_start + self.config["interpolation_window"])
        neighbor_start = neighbor_end - self.config["interpolation_window"]
        neighbors = self._cached["osv"][FrameId.EF][neighbor_start:neighbor_end].array_list()

        while delta_time > time_precision:
            middle_time = first_time + delta_time / 2

            pv_time_interpolator = TimeStampedPVCoordinatesHermiteInterpolator(
                min(
                    neighbors.size(),
                    15,  # 15 => Maximum recommended by doc
                ),
                CartesianDerivativesFilter.USE_PV,
            )

            osv = pv_time_interpolator.interpolate(
                middle_time,
                neighbors,
            )
            z = osv.getPosition().getZ()
            if z < 0:
                first_time = middle_time
            elif 0 <= z < z_precision:
                first_time = middle_time
                break
            else:
                last_time = middle_time
            nb_iter += 1
            delta_time = last_time - first_time

        # logger.debug("  -> ANX found in %s iterations", nb_iter)
        return {"date": first_time, "osv": osv}

    @property
    def info(self) -> dict:
        """
        Compute orbit info elements at `time_orb` construction parameter.

        :raises RuntimeError: If ``time_orb`` hasn't been specified at construction.
        :return: dictionary with orbit elements, as described in :meth:`get_info`

        .. warning::

            - ``time_orb`` needs to be specified at construction. If it wasn't possible, you'll need to explicitly call
              :meth:`get_info` with an explicit date or an explicit absolute orbit number.
            - Orbit information is computed on the fly, and results from previous calls are cached -- as ``time_orb``
              isn't supposed to change in between two call to ``info``.
        """
        if "info" not in self._cached:
            check_if(
                self._time_orb is not None,
                "GenericOrbitModel.info requires the orbit model to be initialized with a 'time_orb' information. "
                "If you cannot provide this information at construction, then use "
                "GenericOrbitModel.getinfo(time|absolute orbit)",
            )
            self._cached["info"] = self.get_info(self._time_orb)
        return self._cached["info"]

    def position_on_orbit(self, time_array: dict) -> np.ndarray:
        """
        Compute position on-orbit (in degrees).

        :param time_array: time array structure (see :py:CONST:`asgard.core.schema.TIME_ARRAY_SCHEMA`)
        :return: array of positions on orbit
        """
        if ASGARD_VALIDATE_SCHEMAS:
            validate_or_throw(time_array, TIME_ARRAY_SCHEMA)

        dataset = {
            "times": time_array,
        }
        self.get_osv(dataset)
        pos = dataset["orb_pos"]
        pos_anx = np.array([self.info["pos_anx"]])
        dist_anx = np.linalg.norm(pos_anx)
        oop = np.rad2deg(
            np.arccos((pos @ pos_anx.transpose()).transpose()[0] / (np.linalg.norm(pos, axis=1) * dist_anx))
        )

        # hardcoded "gps_anx"
        half_orbit = self.info["gps_anx"] + 0.5 * self.info["period_jd"]
        oop[time_array["offsets"] > half_orbit] *= -1.0
        oop[time_array["offsets"] > half_orbit] += 360.0

        return oop

    def _estimate_lof_corrections(self, times: np.ndarray) -> np.ndarray:
        """
        Compute the orbit corrections in LOF frame, based on refining information

        :param times: input GPS times to estimate LOF corrections (shape (N,))
        :return: Array of corrections in LOF (shape (N, 3)), or None if invalid data
        """
        central_time_gps = self.refining_info["center_time"]["GPS"]

        x_correction_in_lof = self.refining_info["spacecraft_corr_coeff"]["x"]
        y_correction_in_lof = self.refining_info["spacecraft_corr_coeff"]["y"]
        z_correction_in_lof = self.refining_info["spacecraft_corr_coeff"]["z"]

        # Check that both polynom coefficients and acquisition center time exist before using them
        if central_time_gps and (
            len(x_correction_in_lof) == 2 and len(y_correction_in_lof) == 2 and len(z_correction_in_lof) == 2
        ):
            # Generate polynoms from correction coefficients
            get_x_corr_poly = np.poly1d([x_correction_in_lof[1], x_correction_in_lof[0]])
            get_y_corr_poly = np.poly1d([y_correction_in_lof[1], y_correction_in_lof[0]])
            get_z_corr_poly = np.poly1d([z_correction_in_lof[1], z_correction_in_lof[0]])

            # Compute the time delta wrt the acquisition time center
            time_from_acq_center_time = times - central_time_gps

            # Convert back central time to UTC
            tmp = {
                "time": {
                    "offsets": time_from_acq_center_time,
                    "unit": "s",
                    "epoch": self.refining_info["default_time"]["epoch"],
                },
            }
            self.time_reference_model.convert_all(
                tmp,
                ref_in=TimeRef.GPS,
                ref_out=TimeRef.UTC,
            )
            time_from_acq_center_time = tmp["time"]["offsets"]

            # Create a position correction vector
            return np.stack(
                [
                    get_x_corr_poly(time_from_acq_center_time),
                    get_y_corr_poly(time_from_acq_center_time),
                    get_z_corr_poly(time_from_acq_center_time),
                ],
                axis=-1,
            )

        return None


def _check_eckstein_hechler_preconditions(eccentricity: float, inclination: float, date: AbsoluteDate) -> bool:
    """
    Check Eckstein Hechler analytical model can be used to compute Mean Keplerian elements
    """
    if eccentricity >= 0.1:
        logger.warning(
            "Mean Keplerian elements at ANX (%s) can't be computed."
            "Indeed, EcksteinHechlerPropagator requires orbit eccentricity (%s) < 0.1.",
            date,
            eccentricity,
        )
        return False
    sin2i = np.square(np.sin(inclination))
    if sin2i < 1e-10:
        logger.warning(
            "Mean Keplerian elements at ANX (%s) can't be computed. "
            "Indeed, EcksteinHechlerPropagator requires a not equatorial orbit. (sin²(%s) = %s < 1e-10)",
            date,
            math.degrees(inclination) % 360,
            sin2i,
        )
        return False
    if np.abs(sin2i - 4 / 5) < 1e-3:
        logger.warning(
            "Mean Keplerian elements at ANX (%s) can't be computed. "
            "Indeed, EcksteinHechlerPropagator requires a non critical inclination (%s ∈ [~63.43°, ~116.57°])",
            date,
            math.degrees(inclination) % 360,
        )
        return False
    if eccentricity >= 0.05:
        logger.warning(
            "Mean Keplerian elements at ANX (%s) can't be trusted. "
            "Indeed, they are computed with EcksteinHechlerPropagator while orbit eccentricity is %s (> 0.05)",
            date,
            eccentricity,
        )
    return True


def _compute_mean_keplerian_elements(orbit, anx_date: AbsoluteDate) -> dict:
    """
    Compute Mean Keplerian Elements with EcksteinHechlerPropagator
    """
    if not _check_eckstein_hechler_preconditions(orbit.getE(), orbit.getI(), anx_date):
        return {}
    # TODO: Check Mean Keplerian elements are correctly computed!!
    mean_circular = EcksteinHechlerPropagator.computeMeanOrbit(
        orbit,  # osculating=
        Constants.WGS84_EARTH_EQUATORIAL_RADIUS,  # referenceRadius=
        Constants.WGS84_EARTH_MU,  # mu=
        # Following constants took in Orekit documentation.
        # TODO: Support other earth models
        Constants.WGS84_EARTH_C20,  # c20=
        +2.53e-6,  # c30=+2.53e-6
        +1.62e-6,  # c40=+1.62e-6
        +2.28e-7,  # c50=+2.28e-7
        5.41e-7,  # c60=-5.41e-7
        1.0e-11,  # epsilon=
        100,  # maxIterations=
    )
    mean_orbit = KeplerianOrbit(mean_circular.getPVCoordinates(), mean_circular.getFrame(), Constants.WGS84_EARTH_MU)
    return {
        "mean_kepl": {
            "a": mean_circular.getA(),  # semi-major axis
            "e": mean_circular.getE(),  # Eccentricity
            "i": math.degrees(mean_circular.getI()),  # Inclination
            "m": math.degrees(mean_orbit.getMeanAnomaly()) % 360,
            "w": math.degrees(mean_orbit.getPerigeeArgument()),
            "ra": math.degrees(mean_orbit.getRightAscensionOfAscendingNode()),
        }
    }


class OrbitScenarioModel(GenericOrbitModel):  # pylint: disable=too-many-instance-attributes
    """
    Orbit Scenario Model.
    """

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for orbit estimation

        :download:`JSON schema <doc/scripts/init_schema/schemas/GenericOrbitModel.schema.json>`
        """
        return {
            "type": "object",
            "properties": {
                "orbit_scenario": ORBIT_SCENARIO_SCHEMA,
                "attitude": AOCS_MODEL_SCHEMA,
                "earth_body": {"type": "asgard.models.body.EarthBody"},
                "time_orb": ASCII_TIMESTAMP_SCHEMA,
                "orbit_frame": {"type": "string"},
            },
            "required": ["orbit_scenario", "earth_body"],
            "additionalProperties": False,
        }

    def __init__(self, **kwargs):
        """
        Orbit model constructor.
        """

        # validate kwargs schema
        schema.validate_or_throw(kwargs, self.init_schema())
        #: Full model configuration (shallow copy of all construction parameters)

        self.config = kwargs

        self._orbit_propagator = None

        self.__init_orbit()
        if self._time_orb is not None:
            self.__init_propagator_info(self._time_orb)
        self.__init_attitude()

    def __init_orbit(self) -> None:
        """Constructor part dedicated to Orbit attributes initialization"""

        #: Internal reference to the EarthBody model used
        self._earth_body = self.config["earth_body"]

        #: Internal reference to the TimeReference model used
        self._time_model: TimeReference = self._earth_body.time_reference_model

        #: Frame into which the orbit is defined
        self._frame: FrameId = FrameId[self.config["orbit_frame"]]

        #: Store orbit & attitude frame as an Orekit object
        self._orekit_frame = self._earth_body.frames[FrameId.EME2000]

        #  ---- TIME TO USE ----
        self._time = {}
        #: TimeRef used for the times offsets, and the attitude quaternions
        if len(self.config["orbit_scenario"]["anx_time"]["TAI"]) >= 1:
            self._time["ref"] = TimeRef["TAI"]
        else:
            raise ValueError("No TAI times in OSF")
        self._time["epoch"] = self.config["orbit_scenario"]["anx_time"]["epoch"]
        self._time["unit"] = self.config["orbit_scenario"]["anx_time"]["unit"]

        #  ---- CACHED ----
        self._osf_dates = []  # list[AbsolutDate]
        for offset in self.config["orbit_scenario"]["anx_time"]["TAI"]:
            self._osf_dates.append(
                self._time_model.str_to_absolute_date(
                    self._time_model.to_str(offset, fmt="CCSDSA_MICROSEC"), default_timescale=TimeScalesFactory.getTAI()
                )
            )

        #: Cache/memorize information for later use (OSV, times, ...)
        self._cached = {
            "osv": {},
            "pv": None,
            "times": self._osf_dates,
        }

        #  ---- VALIDITY RANGE ----
        if self.config["orbit_scenario"]["validity"]["Ref"] != "UTC":
            raise ValueError(
                "Asgard supports only OSF validity time in UTC not in "
                + self.config["orbit_scenario"]["validity"]["Ref"]
            )

        #: Validity_Start time of OSF in UTC (!= start_date)
        earliest_time_utc: str = self.config["orbit_scenario"]["validity"]["Validity_Start"]
        self._earliest_time: AbsoluteDate = AbsoluteDate(earliest_time_utc, TimeScalesFactory.getUTC())
        self._earliest_time = self._earliest_time.shiftedBy(-1.0)
        # OSF round up their validity range, so to avoid been outside the validity range for the first
        # orbit change, we substract 1sec

        #: Validity_Stop time of OSF in UTC (!= stop_date)
        latest_time: str = self.config["orbit_scenario"]["validity"]["Validity_Stop"]
        if latest_time == "9999-99-99T99:99:99":
            latest_time = "9000-01-01T01:01:01"
        self._latest_time: AbsoluteDate = AbsoluteDate(latest_time, TimeScalesFactory.getUTC())

        self._time_orb = None
        if "time_orb" in self.config:
            self._time_orb = self._time_model.str_to_absolute_date(self.config["time_orb"])

    def __init_attitude(self) -> None:
        """
        Constructor part dedicated to Attitude attributes initialization

        For now, only YSM is supported.
        """
        attitude_cfg = self.config["attitude"]
        self._att_frame = FrameId[attitude_cfg.get("frame", "EME2000")]
        if self._frame != self._att_frame:
            logger.warning(
                "Orbit state vector and attitudes have different frames: %s vs %s, attitude frame is forced to EME2000",
                self._frame.name,
                self._att_frame.name,
            )
        self._GenericOrbitModel__init_attitude_model()

    def __init_propagator_info(self, time: AbsoluteDate) -> None:
        """
        Initialise orbital propagator information from osf data

        param time: time of orbit
        """

        osf_date, idx_osf_date, propagation_delta = self.get_closest_osf_date_before_date(time)

        # Get data from OSF needed by the propagator
        cycle_dict = self.config["orbit_scenario"]["cycle"]
        orbit_dict = self.config["orbit_scenario"]["orbit"]

        mlst = self.get_mlst_in_base_10(cycle_dict["MLST"][idx_osf_date])
        nb_orbits_cycle = int(cycle_dict["Cycle_Length"][idx_osf_date])
        kday_to_rep = int(cycle_dict["Repeat_Cycle"][idx_osf_date])
        phase_id = int(orbit_dict["Phase_Number"][idx_osf_date])
        cycle_number = int(orbit_dict["Cycle_Number"][idx_osf_date])
        abs_orb = int(orbit_dict["Absolute_Orbit"][idx_osf_date])
        rel_orb = int(orbit_dict["Relative_Orbit"][idx_osf_date])

        propagation_days = -propagation_delta / 86400

        logging.info(
            f"propagation performed using orbit date : {osf_date.toString()}, "
            f" initialisation date is {propagation_days:.1f} days after orbit scenario file event."
        )

        self._cached["osf_info"] = {
            "date": osf_date,
            "idx": idx_osf_date,
            "propagation_delta": propagation_delta,
            "absolute_orbit": abs_orb,
            "relative_orbit": rel_orb,
            "cycle_length": nb_orbits_cycle,
            "mlst": mlst,
            "phase_id": phase_id,
            "cycle_number": cycle_number,
            "repeat_cycle": kday_to_rep,
        }
        self.compute_info_from_osf_event()

    def compute_info_from_osf_event(self):
        """
        return the orbit info

        :return: a dictionary of the Keplerian parameters, and other information:

            - "phase_id":  phase number (int)
            - "cycle_number": cycle_number (int)
            - "abs_orbit": absolute orbit (int),
            - "rel_orbit": relative orbit (int),

        using from OSF information, for extensive information like ANX infos use get_info(date,light=False)

        """

        if "osf_info" not in self._cached:
            raise RuntimeError("__init_propagator_info() must be performed first.")

        propagation_days = -self._cached["osf_info"]["propagation_delta"] / 86400

        phase_id = self._cached["osf_info"]["phase_id"]
        osf_absolute_orbit = self._cached["osf_info"]["absolute_orbit"]
        osf_relative_orbit = self._cached["osf_info"]["relative_orbit"]
        repeat_cycle = self._cached["osf_info"]["repeat_cycle"]
        cycle_length = self._cached["osf_info"]["cycle_length"]
        absolute_orbit = int(osf_absolute_orbit + np.floor(propagation_days * cycle_length / repeat_cycle))
        relative_orbit = int(osf_relative_orbit + (absolute_orbit - osf_absolute_orbit) % cycle_length)
        osf_cycle_number = self._cached["osf_info"]["cycle_number"]
        cycle_number = int(osf_cycle_number + np.floor(propagation_days / repeat_cycle))
        self._cached["info"] = {
            "phase_id": phase_id,
            "cycle_number": cycle_number,
            "abs_orbit": absolute_orbit,
            "rel_orbit": relative_orbit,
        }
        return self._cached["info"]

    def __init_propagator(self):
        """
        Fit orbit propagator with orbital information

        """

        if "osf_info" not in self._cached:
            raise RuntimeError("__init_propagator_info() must be performed first.")

        osf_info = self._cached["osf_info"]

        # Initiate the Orbit Propagator
        self._orbit_propagator = OrbitPropagator(
            osf_info["date"],
            osf_info["absolute_orbit"],
            osf_info["mlst"],
            osf_info["cycle_length"],
            osf_info["repeat_cycle"],
        )

    @property
    def valid_range(self) -> Tuple[float, float]:
        """
        Get the validity range of the OSF
        """
        start = self._time_model.from_date(
            self._earliest_time,
            ref=TimeRef["UTC"],
            epoch=self._time["epoch"],
            unit=self._time["unit"],
        )
        end = self._time_model.from_date(
            self._latest_time,
            ref=TimeRef["UTC"],
            epoch=self._time["epoch"],
            unit=self._time["unit"],
        )
        return start, end

    def check_crossing_osf_event(self, times: np.array, time_ref: TimeRef = TimeRef.TAI):
        """
        Check if times crosses OSF event

        param times: input times
        param time_ref : time_reference, default is TAI

        return True if all element are on the same orbit scenario
        """

        index_list = []
        if "osf_info" in self._cached:
            index_list.append(self._cached["osf_info"]["idx"])
        time_scale = self._time_model.timeref_to_timescale(time_ref)

        for _, time in enumerate(times):
            target_date = self._time_model.str_to_absolute_date(
                self._time_model.to_str(time, fmt="CCSDSA_MICROSEC", ref_in=time_ref), default_timescale=time_scale
            )
            _, idx_closest_osf_date_before_date, _ = self.get_closest_osf_date_before_date(target_date)
            index_list.append(idx_closest_osf_date_before_date)
        return len(np.unique(np.array(index_list))) == 1

    def get_osv(
        self,
        dataset,
        field_time: str = "times",
        fields_out: Tuple[str, str] = ("orb_pos", "orb_vel"),
    ):  # pylint: disable=arguments-differ
        """
        Return the orbit state vector at a given time. The output fields are computed respectively
        as position, and velocity.

        :param dataset: Dataset with:

            - a :py:CONST:`asgard.core.schema.TIME_ARRAY_SCHEMA` under ``field_time`` key.  If no ``ref`` sub key is
              provided

        :param str field_time:       Field names where time offsets are stored in the ``dataset``
        :param List[str] fields_out: Field names where computed positions and velocities will be stored in ``dataset``
        :return: same dataset with orbit state vector
        """

        # attach_thread()
        # --- Input managing ---

        validate_or_throw(dataset, {field_time: TIME_ARRAY_SCHEMA})
        input_times = dataset[field_time]
        time_ref = input_times.get("ref", "GPS")
        time_scale = self._time_model.timeref_to_timescale(TimeRef[time_ref])

        validate_or_throw(input_times, TIME_ARRAY_SCHEMA)
        input_times = input_times["offsets"]

        # Remove duplicates and select those with more than one second apart.
        unique_time = np.unique(input_times)

        times = unique_time
        nbr_times = np.shape(times)[0]

        dataset[fields_out[0]] = []
        dataset[fields_out[1]] = []
        pos_view = np.zeros((1, 3 * nbr_times))
        vel_view = np.zeros((1, 3 * nbr_times))
        acc_view = np.zeros((1, 3 * nbr_times))

        time_view = np.zeros(nbr_times)
        if not self.check_crossing_osf_event(times, TimeRef[time_ref]):
            logging.warning("input times cross osf event. First time wil be used to initialise orbit propagator.")

        if self._orbit_propagator is None:
            if "osf_info" not in self._cached:
                date = self._time_model.str_to_absolute_date(
                    self._time_model.to_str(times[0], fmt="CCSDSA_MICROSEC", ref_in=TimeRef[time_ref]),
                    default_timescale=time_scale,
                )  # to_str accurate at 1e-6 sec
                logging.info(f"propagator will be initialized with {date.toString()}.")
                self.__init_propagator_info(date)
            self.__init_propagator()
        osf_date = self._cached["osf_info"]["date"]

        for idx_time, time in enumerate(times):
            date = self._time_model.str_to_absolute_date(
                self._time_model.to_str(time, fmt="CCSDSA_MICROSEC", ref_in=TimeRef[time_ref]),
                default_timescale=time_scale,
            )

            time_view[idx_time] = date.durationFrom(osf_date) + date.timeScalesOffset(
                time_scale, TimeScalesFactory.getUTC()
            )

        self._orbit_propagator.propagate(
            to_nio_view(time_view), to_nio_view(pos_view), to_nio_view(vel_view), to_nio_view(acc_view)
        )

        pos_view = pos_view.reshape((nbr_times, 3))
        vel_view = vel_view.reshape((nbr_times, 3))

        # propagation is done in EME200 test if conversion needed
        if self._frame.name != FrameId.EME2000.name:
            dataset2 = {
                "times": {
                    time_ref: {
                        "offsets": times,
                    },
                },
                "time_ref": time_ref,
                fields_out[0]: pos_view,
                fields_out[1]: vel_view,
                "frame": "EME2000",
            }
            # transform to orbit frame
            self._earth_body.transform_orbit(dataset2, self._frame)

            output_pos = dataset2[fields_out[0]]
            output_vel = dataset2[fields_out[1]]
        else:
            output_pos = pos_view
            output_vel = vel_view

        # re assign PV at input times
        # for each input time get the closest time that was used in propagation
        distances = np.abs(input_times[:, np.newaxis] - times)
        indexes = np.argmin(distances, axis=1)

        output_pos = output_pos[indexes]
        output_vel = output_vel[indexes]

        dataset[fields_out[0]] = output_pos
        dataset[fields_out[1]] = output_vel

        return dataset

    def get_anx_lon(self, anx_spacecraft_state) -> float:
        """
        get anx longitude in degrees with convention [0, 360°[

        :param anx_spacecraft_state:  spacecraft state

        :return anx longitude
        """

        gp = self._earth_body.ellipsoid.transform(
            anx_spacecraft_state.getPVCoordinates().getPosition(),
            anx_spacecraft_state.getFrame(),
            anx_spacecraft_state.getDate(),
        )
        normalized_angle = MathUtils.normalizeAngle(gp.getLongitude(), math.pi)
        return math.degrees(normalized_angle)

    def reset_propagator(self):
        """
        Reset propagator.
        """
        self._orbit_propagator = None
        self._cached.pop("osf_info", None)

    def get_info(
        self,
        date: AbsoluteDate | str | float | None,
        time_ref: TimeRef | None = None,
        epoch: str = DEFAULT_EPOCH,
        unit: str = DEFAULT_UNIT,
        abs_orbit: int | None = None,
        ref_orbit: int | None = None,
        light: bool = False,
    ) -> dict:
        """
        Evaluate the Ascending Node Crossing (ANX) in Earth-Fixed frame (as with EOCFI).

        Also compute the nodal period in days, plus other Keplerian parameters that can be extracted at chosen date.

        :param date:             Time at which the parameters will be extracted
        :type date:              AbsoluteDate|str|float
        :param TimeRef time_ref: Time scale to interpret ``date`` when passed in processing format (``float``) --
                                 ignored otherwise.
        :param str epoch:       time_ref epoc
        :param str unit:         Unit ("d"/"s") to interpret ``date`` when passed in processing format (``float``) --
                                 ignored otherwise.
        :param int abs_orbit:   not used. kept for interface compatibility
        :param int ref_orbit:   not used. kept for interface compatibility
        :param bool light: lightweight information to avoid extensive time duration
        :return: a dictionary of the Keplerian parameters, and other information:
            If light = False :

                - "phase_id":  phase number (int),
                - "cycle_number": cycle_number (int),
                - "abs_orbit":  Absolute orbit number computed/used to search for the ANX (int),
                - "rel_orbit": relative orbit (int),
                - "anx_date": :class:`org.orekit.time.AbsoluteDate` of the ANX,
                - "track_direction": tracking direction at the requested ``date`` ("ascending" or "descending")
                - "anx_long": Longitude of the ANX in degrees, ∈ [0, 360]
                - "utc_anx": float offset from UTC epoch, expressed in days
                - "gps_anx": float offset from GPS epoch, expressed in days
                - "pos_anx": Cartesian position coordinates of the ANX, in Earth-Fixed frame (meters)
                - "vel_anx": Cartesian velocity coordinates of the ANX, in Earth-Fixed frame (meters/second)
                - "osc_kepl": Osculating Kepler elements at the ANX :

                    - "a" : Semi-major axis,
                    - "e" : Eccentricity,
                    - "i" : Inclination (degrees -- not normalized, yet),
                    - "m" : Mean anomaly (degrees, ∈ [0, 360]),
                    - "w" : Argument of Perigee (degrees -- not normalized, yet),
                    - "ra" : Right ascension of the ascending node (degrees -- not normalized, yet),

                - "period_jd": duration of the current orbit, expressed in days,
                - "nodal_period": duration of the current orbit, expressed in seconds,

            If Light = True :

                - "phase_id":  phase number (int),
                - "cycle_number": cycle_number (int),
                - "abs_orbit": absolute orbit (int),
                - "rel_orbit": relative orbit (int),

        :rtype: dict
        :raise NotImplementedError: if ``date`` is outside the range of ``earliest`` and ``latest`` times.
        """
        # attach_thread()
        if abs_orbit is not None or ref_orbit is not None:
            raise ValueError("get_info method need date as input")

        if date is None:
            raise TypeError("a date should be set as input ")
        date = self._time_model.any_time_as_date(date, time_ref, epoch, unit)

        if self._orbit_propagator is None:
            if "osf_info" not in self._cached:
                logging.info(f"propagator will be initialized with {date.toString()}.")
                self.__init_propagator_info(date)
            if light:
                return self._cached["info"]
            self.__init_propagator()

        if light:
            return self._cached["info"]

        # Call the Orbit Propagator to get ANX information
        orb_view = np.zeros((1, 1))
        sc_anx = self._orbit_propagator.getAnxInfo(date, to_nio_view(orb_view))

        # anx info
        anx_long = self.get_anx_lon(sc_anx)
        anx_date = sc_anx.getDate()
        anx_position = sc_anx.getPVCoordinates().getPosition()
        anx_velocity = sc_anx.getPVCoordinates().getVelocity()
        # Store the output in dedicated structure

        # Define the orbit as Kelperian to get the information
        kep_orbit = KeplerianOrbit(sc_anx.getOrbit())

        a = kep_orbit.getA()
        i = kep_orbit.getI()  # Inclination in rad

        # Nodale period
        j2 = 1.08263e-3
        t_orbital = 2 * math.pi * math.sqrt(math.pow(a, 3) / Constants.WGS84_EARTH_MU)
        d_omega = (
            -2
            / 3
            * j2
            * (math.pow(Constants.WGS84_EARTH_EQUATORIAL_RADIUS, 2) * math.sqrt(Constants.WGS84_EARTH_MU))
            / math.pow(a, 7 / 2)
            * math.cos(i)
        )
        t_nodal = t_orbital / (1 - d_omega * (t_orbital / 2 * math.pi))

        track_direction = "descending" if anx_velocity.getZ() < 0 else "ascending"

        self._cached["info"].update(
            {
                "anx_date": anx_date,
                "abs_orbit": int(orb_view[0, 0]),
                "track_direction": track_direction,
                "anx_long": anx_long,
                "utc_anx": self._time_model.from_date(anx_date, TimeRef.UTC, unit="d"),
                "gps_anx": self._time_model.from_date(anx_date, TimeRef.GPS, unit="d"),
                "pos_anx": np.array(vector3d_to_list(anx_position)),
                "vel_anx": np.array(vector3d_to_list(anx_velocity)),
                "osc_kepl": {
                    "a": a,
                    "e": kep_orbit.getE(),
                    "i": math.degrees(i),
                    "m": math.degrees(kep_orbit.getMeanAnomaly()) % 360,
                    "w": math.degrees(kep_orbit.getPerigeeArgument()),
                    "ra": math.degrees(kep_orbit.getRightAscensionOfAscendingNode()),
                },
                "period_jd": t_nodal / 60 / 60 / 24,
                "nodal_period": t_nodal,
            }
        )

        return self._cached["info"]

    @property
    def info(self) -> dict:
        """
        Compute orbit info elements at `time_orb` construction parameter.

        :raises RuntimeError: If ``time_orb`` hasn't been specified at construction.
        :return: dictionary with orbit elements, as described in :meth:`get_info`

        .. warning::

            - ``time_orb`` needs to be specified at construction. If it wasn't possible, you'll need to explicitly call
              :meth:`get_info` with an explicit date.
        """
        if self._orbit_propagator is None:
            if "osf_info" not in self._cached:
                raise RuntimeError(
                    "OrbitScenarioModel.info requires the orbit model to be initialized with a 'time_orb' information. "
                    "If you cannot provide this information at construction, then use "
                    "OrbitScenarioModel.getinfo(time|absolute orbit)",
                )
            self.__init_propagator()

        return self.get_info(self._time_orb)

    def get_closest_osf_date_before_date(self, date: AbsoluteDate):
        """
        Get the closest OSF date before a given date
        Assuming osf date are in chronologic order

        :param AbsoluteDate date: input date

        :return: Tuple(AbsoluteDate,int,float):closest osf_date to input date,
            index of closest osf_date before input date,
            duration between input date and closest osf_date before input date
        """
        epsilon = 1e-12
        closest_osf_date_before_date = 0
        idx_closest_osf_date_before_date = None
        for idx, osf_date in enumerate(self._osf_dates):
            duration = osf_date.durationFrom(date)
            if idx == len(self._osf_dates) - 1:
                closest_osf_date_before_date = self._osf_dates[idx]
                idx_closest_osf_date_before_date = idx
                break
            if duration >= epsilon:
                if idx != 0:
                    closest_osf_date_before_date = self._osf_dates[idx - 1]
                    idx_closest_osf_date_before_date = idx - 1
                    duration = self._osf_dates[idx - 1].durationFrom(date)
                else:
                    closest_osf_date_before_date = self._osf_dates[idx]
                    idx_closest_osf_date_before_date = idx
                break

        if closest_osf_date_before_date == 0:
            raise ValueError("Can't find the closest osf before get_info date")
        return closest_osf_date_before_date, idx_closest_osf_date_before_date, duration

    def get_closest_osf_date_to_date(self, date: AbsoluteDate):
        """
        Get the closest OSF date to a given date

        :param AbsoluteDate date: input date

        :return: Tuple(AbsoluteDate,int,float):closest osf_date to input date, index of closest osf_date to input date,
            duration between input date and closest osf_date to input date
        """
        closest_osf_date_to_date = 0
        idx_closest_osf_date_to_date = None

        duration_closest = float("inf")
        for idx, osf_date in enumerate(self._osf_dates):
            duration = osf_date.durationFrom(date)
            if abs(duration) < abs(duration_closest):
                duration_closest = duration
                idx_closest_osf_date_to_date = idx
                closest_osf_date_to_date = self._osf_dates[idx]

        if closest_osf_date_to_date == 0:
            raise ValueError("Can't find the closest osf before get_info date")

        return closest_osf_date_to_date, idx_closest_osf_date_to_date, duration_closest

    @staticmethod
    def get_mlst_in_base_10(mlst: str) -> float:
        """
        Get MLST date in base 10

        :param str mlst: Read date
        :return: same dataset with orbit state vector
        """
        hours = float(mlst[:2])
        minutes = float(mlst[3:5])
        sec = float(mlst[6:])

        return (minutes * 60 + sec) / (60 * 60) + hours
