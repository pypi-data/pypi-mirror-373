#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2024 CS GROUP
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
Module for attitude models
"""

import numpy as np
from scipy.spatial.transform import Rotation as R

# isort: off
# Orekit wrappers needs to be imported before any org.orekit module
from asgard.wrappers.orekit import to_nio_view  # pylint: disable=no-name-in-module

# isort: on

# noqa: F401  # pylint: disable=import-error,wrong-import-order
from org.hipparchus.geometry.euclidean.threed import Rotation
from org.orekit.attitudes import Attitude
from org.orekit.frames import Frame
from org.orekit.time import AbsoluteDate
from org.orekit.tools import PVProcessor, TransformProcessor
from org.orekit.utils import AbsolutePVCoordinates, AngularCoordinates


class ZeroDopplerAttitudeProvider:
    """
    Attitude provider modeling Zero-Doppler AOCS mode
    """

    def __init__(
        self,
        date: AbsoluteDate,
        tod_frame: Frame,
        target_frame: Frame,
        beta: float = 0.0060611,
        omega: float = -0.729211585e-4,
    ):
        """
        Constructor

        :param date: Acquisition date to estimate "ToD to EME2000" transform
        :param tod_frame: ToD frame
        :param target_frame: Reference frame in which attitudes are computed
        :param beta: Local normal coefficient
        :param omega: Earth's angular velocity (rad/s)
        """
        self.tod_frame = tod_frame
        self.target_frame = target_frame
        self.date = date

        if self.target_frame.isPseudoInertial():
            # we can estimate the TOD to target rotation only once
            self.tod_to_target = target_frame.getTransformTo(tod_frame, date)
        else:
            self.tod_to_target = None

        self.beta = beta
        self.omega_vec = np.array([0.0, 0.0, omega], dtype="float64")

    def compute_frame_tod(self, pos: np.ndarray, vel: np.ndarray) -> R:
        """
        Compute ZD attitude in TOD frame

        :param pos: Orbital position in TOD frame
        :param vel: Orbital velocity in TOD frame
        :return: ZD attitude quaternion with TOD as reference frame
        """

        pos_prime = pos.copy()
        pos_prime[..., 2] *= 1 + self.beta
        vel_prime = vel + np.cross(self.omega_vec, pos)

        x_zd = np.cross(pos_prime, vel_prime)
        x_zd /= np.linalg.norm(x_zd, axis=-1, keepdims=True)

        y_zd = -vel_prime / np.linalg.norm(vel_prime, axis=-1, keepdims=True)

        z_zd = np.cross(x_zd, y_zd)

        matrix = np.stack([x_zd, y_zd, z_zd], axis=-1)

        return R.from_matrix(matrix)

    def getAttitude(  # pylint: disable=invalid-name
        self,
        pvcoord: AbsolutePVCoordinates,
        date: AbsoluteDate,
        frame: Frame,
    ) -> Attitude:
        """
        Compute platform attitude at a given date in a reference frame

        :param pvcoord: Position and velocity of the satellite
        :param date: Absolute date
        :param frame: reference frame
        """

        assert frame == self.target_frame

        tod_pv = pvcoord.getPVCoordinates(self.tod_frame)
        tod_pos = tod_pv.getPosition()
        tod_vel = tod_pv.getVelocity()

        rot_zd_to_tod = self.compute_frame_tod(
            np.array([tod_pos.getX(), tod_pos.getY(), tod_pos.getZ()], dtype="float64"),
            np.array([tod_vel.getX(), tod_vel.getY(), tod_vel.getZ()], dtype="float64"),
        )

        # Fix for non-inertial target frame
        if self.tod_to_target is None:
            rot = self.target_frame.getStaticTransformTo(self.tod_frame, date).getRotation()
        else:
            rot = self.tod_to_target.staticShiftedBy(date.durationFrom(self.date)).getRotation()
        tod_to_target = R.from_quat([rot.getQ1(), rot.getQ2(), rot.getQ3(), rot.getQ0()])

        rot_zd_to_target = tod_to_target * rot_zd_to_tod
        quat = rot_zd_to_target.as_quat()

        return Attitude(
            date,
            frame,
            AngularCoordinates(Rotation(float(quat[3]), float(quat[0]), float(quat[1]), float(quat[2]), False)),
        )

    def getAttitudes(  # pylint: disable=invalid-name
        self,
        pos: np.ndarray,
        vel: np.ndarray,
        pv_frame: Frame,
        epoch: AbsoluteDate,
        times: np.ndarray,
        frame: Frame,
    ) -> np.ndarray:
        """
        Compute a batch of attitudes for given input times

        :param pos: Spacecraft position
        :param vel: Spacecraft velocity
        :param pv_frame: Frame where PV coordinates are expressed
        :param epoch: reference epoch for input times
        :param times: Input times
        :param frame: Frame to compute attitudes
        """

        assert frame == self.target_frame

        tod_pos = np.zeros_like(pos)
        tod_vel = np.zeros_like(vel)

        PVProcessor.reprojectPV(
            pv_frame,
            self.tod_frame,
            epoch,
            to_nio_view(times),
            to_nio_view(pos),
            to_nio_view(vel),
            to_nio_view(tod_pos),
            to_nio_view(tod_vel),
        )

        rot_zd_to_tod = self.compute_frame_tod(tod_pos, tod_vel)

        # Fix for non-inertial target frame
        rot = np.zeros((times.size, 4), dtype="float64")
        if self.tod_to_target is None:
            TransformProcessor.estimateStatic(
                self.target_frame,
                self.tod_frame,
                epoch,
                to_nio_view(times),
                None,
                to_nio_view(rot),
            )
        else:
            TransformProcessor.interpolate(self.tod_to_target, epoch, to_nio_view(times), None, to_nio_view(rot))

        tod_to_target = R.from_quat(rot)

        rot_zd_to_target = tod_to_target * rot_zd_to_tod
        quat = rot_zd_to_target.as_quat()

        return quat
