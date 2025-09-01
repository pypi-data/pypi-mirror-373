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
S2geoDatastrip implementation.
"""
import xml.etree.ElementTree as ET
from typing import Dict, List

import numpy as np

# isort: off
# JCC initVM()
import asgard.wrappers.orekit  # pylint: disable=unused-import # noqa: F401

# isort: on

from drivers.s2geo_legacy.s2geo_refining import S2geoRefining
from drivers.xml_util import XmlUtil
from org.hipparchus.geometry.euclidean.threed import (  # pylint: disable=import-error, wrong-import-order
    Rotation,
    Vector3D,
)
from org.orekit.data import (  # pylint: disable=import-error, wrong-import-order
    DataContext,
)
from org.orekit.frames import (  # pylint: disable=import-error, wrong-import-order
    Transform,
)
from org.orekit.time import (  # pylint: disable=import-error, wrong-import-order
    AbsoluteDate,
    TimeScale,
)
from org.orekit.utils import (  # pylint: disable=import-error, wrong-import-order
    IERSConventions,
    PVCoordinates,
    TimeStampedPVCoordinates,
)

# pylint: disable=ungrouped-imports
import asgard.sensors.sentinel2.s2_constants as S2C
from asgard.sensors.sentinel2.s2_band import S2Band
from asgard.sensors.sentinel2.s2_detector import S2Detector
from asgard.wrappers.orekit.utils import dates_to_json


def truncate_epoch(abs_date: AbsoluteDate, scale: TimeScale) -> AbsoluteDate:
    """
    Truncate an absolute date to remove decimal seconds (ex: 10:30:45.8241 -> 10:30:45)

    :param abs_date: Input absolute date
    :param scale: Timescale to be used
    :return: date with truncated decimal seconds
    """

    j_dt_components = abs_date.getComponents(scale)
    seconds = int(j_dt_components.getTime().getSecond())
    return AbsoluteDate(
        j_dt_components.getDate().getYear(),
        j_dt_components.getDate().getMonth(),
        j_dt_components.getDate().getDay(),
        j_dt_components.getTime().getHour(),
        j_dt_components.getTime().getMinute(),
        float(seconds),
        scale,
    )


class S2geoDatastrip:
    """
    S2Geo XML datastrip file legacy loader.

    :param x_root: XML root element
    :param x_sensor_conf: XML node for sensor configuration
    :param x_granules: XML node for granules
    :param x_attitudes: XML for attitudes
    :param x_ephemeris: XML for ephemeris
    :param level: L0, L1A, L1B or L1C
    :param tdis: TDI configuration to use for each band
    :param refining_info: refining information
    :param d_config: output configuration JSON values
    """

    def __init__(self, d_config: dict, context: DataContext):
        """Constructor"""

        # Input XML nodes
        self.x_root: ET.Element = None
        self.x_sensor_conf: ET.Element = None
        self.x_granules: ET.Element = None
        self.x_attitudes: ET.Element = None
        self.x_ephemeris: ET.Element = None

        # Nodes and values calculated by this class
        self.level: str = None
        self.tdis: Dict[S2Band, str] = {}
        self.refining_info = S2geoRefining(d_config, context)

        self.d_config: dict = d_config

        # init Orekit resources
        self.frames = {
            "EME2000": context.getFrames().getEME2000(),
            "ITRF": context.getFrames().getITRF(IERSConventions.IERS_2010, True),
        }

        self.time_scales = {
            "GPS": context.getTimeScales().getGPS(),
            "TAI": context.getTimeScales().getTAI(),
        }

    @classmethod
    def from_xml_nodes(
        cls,
        x_root: ET.Element,
        x_sensor_conf: ET.Element,
        x_granules: ET.Element,
        x_attitudes: ET.Element,
        x_ephemeris: ET.Element,
        d_config: dict,
        context: DataContext,
    ) -> "S2geoDatastrip":
        """Init a class instance from XML nodes."""

        # Init a class instance
        datastrip = cls(d_config, context)

        # Save the input XML nodes
        datastrip.x_root = x_root
        datastrip.x_sensor_conf = x_sensor_conf
        datastrip.x_granules = x_granules
        datastrip.x_attitudes = x_attitudes
        datastrip.x_ephemeris = x_ephemeris

        return datastrip

    @classmethod
    def from_xml_file(cls, path: str, d_config: dict, context: DataContext) -> "S2geoDatastrip":
        """Init a class instance from a datastrip XML file."""

        # Read XML file. Remove namespaces to facilitate reading.
        x_root = XmlUtil.read_with_etree(path, remove_namespaces=True)

        # Read XML nodes
        x_sensor_conf = x_root.find("Image_Data_Info/Sensor_Configuration")
        x_granules = x_root.find("Image_Data_Info/Granules_Information")
        x_attitudes = x_root.find("Satellite_Ancillary_Data_Info/Attitudes")
        x_ephemeris = x_root.find("Satellite_Ancillary_Data_Info/Ephemeris")

        # Init a class instance from the XML nodes
        datastrip = cls.from_xml_nodes(
            x_root,
            x_sensor_conf,
            x_granules,
            x_attitudes,
            x_ephemeris,
            d_config,
            context,
        )

        # Read level
        level = x_root.tag
        if level == "Level-0_DataStrip_ID":
            # datastrip.level = LevelInfo.L0
            pass
        elif level == "Level-1A_DataStrip_ID":
            # datastrip.level = LevelInfo.L1A
            pass
        elif level == "Level-1B_DataStrip_ID":
            # datastrip.level = LevelInfo.L1B
            pass
        elif level == "Level-1C_DataStrip_ID":
            # datastrip.level = LevelInfo.L1C
            pass
        else:
            raise RuntimeError(f"Invalid level:{level!r} in: {path!r}")
        datastrip.level = level

        return datastrip

    def read(self, with_refining: bool = True):
        """
        Read values from the XML nodes into the JSON dict.
        :param with_refining: read refining info ?
        """

        self.read_sensor_configuration()
        if with_refining:
            self.refining_info.read_from_datastrip(self.x_root)
        self.read_granules()
        self.read_attitudes()
        self.read_ephemeris()

    def read_sensor_configuration(self):
        """Read the sensor configuration values"""

        # Do nothing if sensor configuration info is missing
        if self.x_sensor_conf is None:
            return

        # Read the TDI configurations = the viewing directions that must be used
        for x_tdi in self.x_sensor_conf.findall("Acquisition_Configuration/TDI_Configuration_List/TDI_CONFIGURATION"):
            band = S2Band.from_index(int(x_tdi.get("bandId")))  # bandId = band index
            self.tdis[band] = x_tdi.text

        # Read the time stamp info
        x_time_stamp = self.x_sensor_conf.find("Time_Stamp")
        line_period = float(x_time_stamp.find("LINE_PERIOD").text)

        # Default reference line value
        ref_line_datation = 1.0

        # Reference date for the line datations
        j_epoch = None

        # Init 2D lists
        ref_dates_all = []
        ref_lines_all = []
        rates_all = []

        # For each existing detector and band
        for detector in S2Detector.VALUES:
            # Init 1D lists
            ref_dates = []
            ref_lines = []
            rates = []
            ref_dates_all.append(ref_dates)
            ref_lines_all.append(ref_lines)
            rates_all.append(rates)

            for band in S2Band.VALUES:
                # Find the sensor time stamp for the current detector and band
                x_detector_time_stamp = x_time_stamp.find(
                    f"Band_Time_Stamp[@bandId={str(band.index)!r}]/Detector[@detectorId={detector.legacy_name!r}]"
                )
                if x_detector_time_stamp is None:
                    raise RuntimeError(
                        f"Line datation is missing for detector name: {detector.legacy_name} "
                        f"and band index: {band.index}"
                    )

                # We get the value of a half line period for the given band resolution
                band_line_period = line_period / S2C.PIXEL_HEIGHT_10 * band.pixel_height
                half_line_period = band_line_period / 2

                j_ref_date = AbsoluteDate(x_detector_time_stamp.find("GPS_TIME").text, self.time_scales["GPS"])

                # We shift the date of a half line period to be in the middle of the line
                j_ref_date = j_ref_date.shiftedBy(half_line_period / 1000.0)

                # Use the first date as reference
                if j_epoch is None:
                    j_epoch = truncate_epoch(j_ref_date, self.time_scales["GPS"])

                ref_line_int = int(x_detector_time_stamp.find("REFERENCE_LINE").text)
                # Update the reference line value for the line datation
                if ref_line_int not in (0, 1):
                    ref_line_datation = ref_line_int * S2C.PIXEL_HEIGHT_10 / band.pixel_height

                # Save the line datation info
                ref_dates.append(j_ref_date)
                ref_lines.append(ref_line_datation)
                rates.append(1000.0 / band_line_period)

        # Save JSON values
        self.d_config["line_datations"] = {
            "col_names": np.array([detector.name for detector in S2Detector.VALUES]),
            "row_names": np.array([band.name for band in S2Band.VALUES]),
            "times": {"GPS": dates_to_json(self.time_scales["GPS"], j_epoch, ref_dates_all)},
            "ref_lines": np.array(ref_lines_all, np.double),
            "rates": np.array(rates_all, np.double),
        }

    def read_granules(self):
        """
        Read the granule values.
        """

        # If no granules, do nothing
        if self.x_granules is None:
            return

        # Granules min and max lines for each detector
        granule_lines: Dict[S2Detector, List[float]] = {}

        # For each detector
        for x_detector in self.x_granules.findall("Detector_List/Detector"):
            # Check at least one granule exists
            if x_detector.find("Granule_List/Granule") is None:
                pass

            detector_name = x_detector.get("detectorId")
            detector = S2Detector.from_legacy_name(detector_name)

            # Save and sort granule positions
            positions = sorted([int(pos.text) for pos in x_detector.findall("Granule_List/Granule/POSITION")])
            first_granule = positions[0]
            last_granule = positions[-1]

            min_line = (
                self.granule_first_line(first_granule, S2C.PIXEL_HEIGHT_10)
                # ~ - self.granule_line_count(S2C.PIXEL_HEIGHT_10) * 10
            )
            max_line = (
                self.granule_last_line(last_granule, S2C.PIXEL_HEIGHT_10)
                # ~ + self.granule_line_count(S2C.PIXEL_HEIGHT_10) * 10
            )

            # Save the min and max lines
            granule_lines[detector] = (float(min_line), float(max_line))

        # Save min and max line values for each detector from the granule lines.
        d_min_max = self.d_config["min_max_lines"]
        d_min_max["row_names"] = np.array([detector.name for detector in granule_lines])
        d_min_max["col_names"] = ["min", "max"]
        d_min_max["values"] = np.array(list(granule_lines.values()))

    def read_attitudes(self):
        """Read the attitude values"""

        # To check duplicate dates in the quaternions
        dates = set()

        # Reference date for the line datations
        j_epoch = None

        times = []
        rotations = []

        # For each corrected attitude
        for x_attitude in self.x_attitudes.findall("Corrected_Attitudes/Values"):
            # GPS time is mandatory
            gps_time = x_attitude.find("GPS_TIME").text

            # Check GPS time unicity
            if gps_time in dates:
                raise RuntimeError(f"Duplicate corrected attitude with GPS time: {gps_time!r}")
            dates.add(gps_time)

            # Convert to AbsoluteDate
            j_time = AbsoluteDate(gps_time, self.time_scales["GPS"])
            times.append(j_time)

            # Use the first date as reference
            if j_epoch is None:
                j_epoch = truncate_epoch(j_time, self.time_scales["GPS"])

            # Read quaternion values as q1, q2, q3, q0
            (quat1, quat2, quat3, quat0) = [float(q) for q in x_attitude.find("QUATERNION_VALUES").text.split()]

            # Create normalized Rotation from q0, q1, q2, q3
            rotations.append(Rotation(quat0, quat1, quat2, quat3, True))

        # Convert normalized rotations back to quaternions, in scalar-last convention
        quaternions = [(rot.getQ1(), rot.getQ2(), rot.getQ3(), rot.getQ0()) for rot in rotations]

        # Save JSON values
        self.d_config["attitudes"] = {
            "times": {"GPS": dates_to_json(self.time_scales["GPS"], j_epoch, times)},
            "quaternions": np.array(quaternions, np.double),
        }

    def read_ephemeris(self):
        """Read the ephemeris values"""

        # To switch between dummy computation or real computation of velocity.
        dummy_pv_transform = False

        # To check duplicate dates in the quaternions
        dates = set()

        # Reference date for the line datations
        j_epoch = None

        times = []
        positions = []
        velocities = []

        # For each GPS point
        for x_ephemeris in self.x_ephemeris.findall("GPS_Points_List/GPS_Point"):
            # GPS time is optional
            gps_time = x_ephemeris.find("GPS_TIME").text
            if not gps_time:
                continue  # do nothing if GPS time is empty or missing

            # Check GPS time unicity
            if gps_time in dates:
                raise RuntimeError(f"Duplicate ephemeris with GPS time: {gps_time!r}")
            dates.add(gps_time)

            # Convert to AbsoluteDate
            j_ephemeris_date = AbsoluteDate(gps_time, self.time_scales["GPS"])
            times.append(j_ephemeris_date)

            # Use the first date as reference
            if j_epoch is None:
                j_epoch = truncate_epoch(j_ephemeris_date, self.time_scales["GPS"])

            # Get position values in ITRF (defined in mm)
            (posx, posy, posz) = [float(p) / 1000 for p in x_ephemeris.find("POSITION_VALUES").text.split()]

            # Get velocity values in ITRF (defined in mm/s)
            (velx, vely, velz) = [float(v) / 1000 for v in x_ephemeris.find("VELOCITY_VALUES").text.split()]

            j_pv_itrf = PVCoordinates(Vector3D(posx, posy, posz), Vector3D(velx, vely, velz))

            # Compute the transformation from ITRF to EME2000 at the ephemeris date
            j_transform = self.frames["ITRF"].getTransformTo(self.frames["EME2000"], j_ephemeris_date)

            # Convert PV from ITRF to EME2000
            j_pv_coord = None

            # For CNES data (without kinematic effects for the velocity)
            if dummy_pv_transform:
                # dummy transform to counteract the bad transform for the velocity:
                # simple rotation for velocity
                # WITHOUT kinematic correction
                j_pv_coord = TimeStampedPVCoordinates(
                    j_ephemeris_date,
                    j_transform.transformPosition(j_pv_itrf.getPosition()),
                    j_transform.transformVector(j_pv_itrf.getVelocity()),
                    Vector3D.ZERO,
                )

            # For real data (with kinematic effects for the velocity)
            else:
                # WITH kinematic correction
                pv_eme2000 = j_transform.transformPVCoordinates(j_pv_itrf)
                j_pv_coord = TimeStampedPVCoordinates(
                    j_ephemeris_date,
                    pv_eme2000.getPosition(),
                    pv_eme2000.getVelocity(),
                    Vector3D.ZERO,
                )

            # Compute refining corrections
            if self.refining_info.is_refined:
                # Test if the polynoms and the acquisition center time are not null before applying them
                if (
                    (self.refining_info.j_acq_center_time is not None)
                    and (self.refining_info.spacecraft_position[0] is not None)
                    and (self.refining_info.spacecraft_position[1] is not None)
                    and (self.refining_info.spacecraft_position[2] is not None)
                ):
                    # Simple way to compute the transformation from EME2000 to LOF,
                    # as we need only to perform the transform for the current point
                    j_eme2000_to_lof = self.eme2000_to_lof(j_ephemeris_date, j_pv_coord)

                    # compute in seconds the delta t wrt acquisition time center
                    center_time = j_ephemeris_date.durationFrom(self.refining_info.j_acq_center_time)

                    # compute the XYZ corrections in LOF (unit : m)
                    corrections_lof = [poly.value(center_time) for poly in self.refining_info.spacecraft_position]
                    j_pos_corrections = Vector3D(*corrections_lof)
                    j_pv_lof_corrections = TimeStampedPVCoordinates(j_ephemeris_date, j_pos_corrections, Vector3D.ZERO)

                    # update the current pair of PV in EME2000
                    j_pv_coord = j_eme2000_to_lof.getInverse().transformPVCoordinates(j_pv_lof_corrections)

            # Save position and velocity values
            pos = j_pv_coord.getPosition()
            vel = j_pv_coord.getVelocity()
            positions.append([pos.getX(), pos.getY(), pos.getZ()])
            velocities.append([vel.getX(), vel.getY(), vel.getZ()])

        # Save JSON values
        self.d_config["orbits"] = {
            "times": {"GPS": dates_to_json(self.time_scales["GPS"], j_epoch, times)},
            "positions": np.array(positions, np.double),
            "velocities": np.array(velocities, np.double),
            "frame": "EME2000",
        }

    @staticmethod
    def eme2000_to_lof(date, pv_coord):
        """
        Get the transform from an inertial frame defining position-velocity and the local orbital frame.
        :param date: current date
        :param pv_coord: position-velocity of the spacecraft in inertial frame EME2000
        :return: transform from the frame where position-velocity are defined to local orbital frame
        """
        # compute the translation part of the transform
        translation = Transform(date, pv_coord.negate())

        # compute the rotation from inertial to LOF
        # where LOF is defined by:
        # Z axis aligned with opposite of position, X axis aligned with orbital
        # momentum [cross product of speed vector ^ Z axis]
        rotation_eme2000_to_lof = Rotation(
            pv_coord.getPosition(),
            pv_coord.getMomentum(),
            Vector3D.MINUS_K,
            Vector3D.PLUS_I,
        )

        # compute the rotation part of the transform
        position = pv_coord.getPosition()
        momentum = pv_coord.getMomentum()
        rotation = Transform(
            date,
            rotation_eme2000_to_lof,
            Vector3D(1.0 / position.getNormSq(), rotation_eme2000_to_lof.applyTo(momentum)),
        )
        return Transform(date, translation, rotation)

    ############
    # Granules #
    ############

    @staticmethod
    def granule_line_count(pixel_size):
        """Return the number of lines for a granule for a given pixel size in meters"""
        return S2C.GRANULE_NB_LINE_10_M * S2C.PIXEL_HEIGHT_10 / pixel_size

    @classmethod
    def granule_first_line(cls, position, pixel_size, line_count=None):
        """Get granule first line for given pixel size and line count"""

        if line_count is None:
            line_count = cls.granule_line_count(pixel_size)

        # for band with 10 resolution : first line number = granule position
        if pixel_size == S2C.PIXEL_HEIGHT_10:
            return position

        # For other bands : FirstLine = (((granulePosition -1) / 2304) * granuleNbLine) +1
        return (((position - 1) / S2C.GRANULE_NB_LINE_10_M) * line_count) + 1

    @classmethod
    def granule_last_line(cls, position, pixel_size, line_count=None):
        """Get granule last line for given pixel size and line count"""

        if line_count is None:
            line_count = cls.granule_line_count(pixel_size)

        # for band with 10 resolution : last line number = granule position + granuleNbLine - 1
        last_line = position + S2C.GRANULE_NB_LINE_10_M - 1

        if pixel_size == S2C.PIXEL_HEIGHT_10:
            return last_line
        return (last_line / S2C.GRANULE_NB_LINE_10_M) * line_count
