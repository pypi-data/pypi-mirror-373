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
Module for Sentinel 2 instruments
"""

import copy
import logging
import math
import os.path as osp
from collections import defaultdict
from os import walk
from typing import Dict, List, Tuple

import numpy as np
from numpy import ndarray

# Must be done before orekit/jcc imports. Ignore isort formatting.
# isort: off
# JCC initVM()
import asgard.wrappers.orekit  # pylint: disable=unused-import # noqa: F401

# isort: on

from org.orekit.time import (  # pylint: disable=import-error,wrong-import-order
    AbsoluteDate,
)

# pylint: disable=ungrouped-imports
import asgard.sensors.sentinel2.s2_constants as S2C
from asgard.core.math import RADIANS_SCALING_FACTORS, flatten_array, restore_array
from asgard.core.product import AbstractOpticalGeometry
from asgard.core.schema import (
    COMMON_DEFINITIONS,
    DEM_DATASET_SCHEMA,
    generate_array_schema,
    generate_float64_array_schema,
    refining_axis,
)
from asgard.core.time import DEFAULT_EPOCH, DEFAULT_UNIT, TimeRef
from asgard.core.transform import RigidTransform

# from tests.drivers.sentinel_3_legacy import S3LegacyDriver
from asgard.models.body import ELLIPSOID_MODELS, EarthBody
from asgard.models.linedetector import (
    LineDetectorPointingModel,
    LineDetectorTimestampModel,
)
from asgard.models.orbit import GenericOrbitModel
from asgard.models.platform import GenericPlatformModel
from asgard.models.propagation import MULTILAYERMODEL_SCHEMA, PropagationModel
from asgard.models.time import TimeReference
from asgard.sensors.sentinel2.s2_band import S2Band
from asgard.sensors.sentinel2.s2_detector import S2Detector
from asgard.sensors.sentinel2.s2_sensor import S2Sensor
from asgard.wrappers.orekit.utils import TIMESCALE_MAP, get_orekit_resources


class S2MSIGeometry(AbstractOpticalGeometry):  # pylint: disable=R0902
    """
    Sentinel 2 MSI legacy product.
    """

    default_timescale = "GPS"

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        # Call superclass constructor. Copy the keyword arguments.
        super().__init__(*args, **copy.deepcopy(kwargs))

        ########
        # Init #
        ########

        # Find IERS data
        iers_path = self.config["resources"].get("iers")
        eop = self.config.get("eop")

        if eop is not None:
            self.time_reference = TimeReference(eop)
        elif iers_path is not None:
            logging.debug("Loading IERS file with path is deprecated")
            if osp.isfile(iers_path):
                iers_file = iers_path
            elif osp.isdir(iers_path):
                for dirpath, dirnames, filenames in walk(iers_path):
                    if not filenames:
                        raise RuntimeError(f"IERS directory is empty: {iers_path!r}")
                    if dirnames or (len(filenames) > 1):
                        raise RuntimeError(f"Only one file is accepted in the IERS directory: {iers_path!r}")
                    for filename in filenames:
                        iers_file = osp.join(dirpath, filename)
            else:
                raise RuntimeError(f"IERS path is missing: {iers_path!r}")

            # Read file contents and init the TimeReference instance
            with open(iers_file, "r", encoding="utf-8") as input_fd:
                iers_data = input_fd.readlines()
            self.time_reference = TimeReference(iers_bulletin_a=iers_data)
        else:
            self.time_reference = TimeReference()

        # Create EarthBody
        body_config = self.config.get("models", {}).get("body", {})
        body_config["time_reference"] = self.time_reference
        self.body_model = EarthBody(**body_config)

        # Use a common epoch value for all config fields
        self._use_common_epoch()

        # Read line count
        self._build_min_max_lines()

        # Read pixel count
        for d_viewing in self.config["viewing_directions"]:
            values = d_viewing["values"]
            sensor_name = d_viewing["sensor"]
            self.coordinates[sensor_name]["pixels"] = len(values[0])

        # Build the sensor list
        self._instr_list = list(self.coordinates.keys())

        ################
        # Build models #
        ################
        # Build the LineDetectorTimestampModel instances
        self._build_timestamp_models()

        # Build the GenericOrbitModel instance
        self._build_orbit_model()

        # Build the GenericPlatformModel instance
        self._build_platform_model()

        # Build the LineDetectorPointingModel instance
        self._build_pointing_model()

        # Build the PropagationModel instance
        self._build_propagation_model()

    def _use_common_epoch(self) -> None:
        """
        Check that all the time fields use GPS time scale and units in seconds,
        and use a common epoch value.
        """

        # Epoch values and related offset values, and also save the parent dict
        epochs_offsets = []

        # Unique unit values
        units = set()

        # Recursively find all "offset" fields from the input config.
        def find_offsets(sub_dict: Dict, parents: List) -> None:
            # Read current fields, or None if missing
            offsets = sub_dict.get("offsets")
            epoch = sub_dict.get("epoch", DEFAULT_EPOCH)
            ref = sub_dict.get("ref")

            # Stop condition: we found an offset field
            if offsets is not None:
                # Check the time scale (=parent node or 'ref' child node) is GPS
                if parents[-1] in ["TAI", "UTC", "UT1"]:
                    raise RuntimeError(f"Time scale should be 'GPS' under: {'.'.join(parents)!r}")
                if (ref is not None) and (ref != self.default_timescale):
                    raise RuntimeError(f"'ref' should be 'GPS' not {ref!r} under: {'.'.join(parents)!r}")

                # Save epoch and related offset values, and units
                epochs_offsets.append([epoch, offsets, sub_dict])
                units.add(sub_dict.get("unit", DEFAULT_UNIT))

            # Else make a recursive call for each dict value
            else:
                for key, sub_dict2 in sub_dict.items():
                    if isinstance(sub_dict2, dict):
                        find_offsets(sub_dict2, parents + [key])

        find_offsets(self.config, [])

        # If no times are defined (this should not happen), do nothing
        if not epochs_offsets:
            return

        if len(units) > 1:
            raise RuntimeError(f"All times should use the same units. Input units are: {units}")
        unit = units.pop()

        # Find the min epoch from those in config and express all offset values from that epoch.
        first_epoch_str = epochs_offsets[0][0]  # arbitrary epoch; the other epochs are compared to this one
        min_epoch_str = first_epoch_str  # min epoch as a string
        min_epoch_float = 0  # min offset from the first epoch

        # Compare each epoch to the first epoch
        for epoch_str, _, _ in epochs_offsets[1:]:
            epoch_float = self.time_reference.from_str(time=epoch_str, unit=unit, epoch=first_epoch_str)
            if epoch_float < min_epoch_float:
                min_epoch_float = epoch_float
                min_epoch_str = epoch_str

        # Now compare each epoch to the min epoch, adjust the offset values and save the epoch.
        for epoch_str, offsets, parent_dict in epochs_offsets:
            if epoch_str == min_epoch_str:  # current epoch is the min epoch
                continue
            diff = self.time_reference.from_str(time=epoch_str, unit=unit, epoch=min_epoch_str)
            offsets += diff  # in-place numpy array modification
            parent_dict["epoch"] = min_epoch_str

        # Save the default time
        self.default_time = {
            "ref": self.default_timescale,
            "unit": unit,
            "epoch": min_epoch_str,
        }

    def _build_min_max_lines(self) -> Tuple[dict, dict]:
        """
        Build the min max lines for each sensor, and fill the self.coordinate map
        """

        # Line counts for each detector and band, if given by the caller
        try:
            line_counts = self.config["line_counts"]

        # Else estimate the line counts with a 4s margin when granules are missing
        except KeyError:
            line_counts = S2MSIGeometry.estimate_line_counts(self.config, margin_seconds=4)

        # Init coordinates for each sensor
        self.coordinates = {
            S2Sensor(detector, band).name: {"pixels": 0, "lines": 0}
            for detector in S2Detector.VALUES
            for band in S2Band.VALUES
        }

        # Save the line counts
        for det_name, dim1 in zip(line_counts["col_names"], line_counts["values"]):
            detector = S2Detector.from_name(det_name)
            for band_name, line_count in zip(line_counts["row_names"], dim1):
                sensor = S2Sensor(detector, S2Band.from_name(band_name)).name
                self.coordinates[sensor]["lines"] = line_count

        # These min and max line values are passed only to the ASGARD-Legacy objects.
        # I'm not sure they are used by the ASGARD processings.
        min_lines = {}
        max_lines = {}

        # Read the "min_max_lines" if present, filled from the granule information
        if "min_max_lines" in self.config:
            d_min_max = self.config["min_max_lines"]

            detectors = d_min_max["row_names"]
            i_min = list(d_min_max["col_names"]).index("min")  # should be 0
            i_max = list(d_min_max["col_names"]).index("max")  # should be 1
            values = d_min_max["values"]

            # One min/max value by detector
            assert len(values) == len(detectors)

            # Read values
            for det_name, min_max in zip(detectors, values):
                # Repeat the information for each band = for each sensor
                for band in S2Band.VALUES:
                    sensor = S2Sensor(S2Detector.from_name(det_name), band)
                    sensor_name = sensor.name

                    # Apply margins for validity range.
                    min_lines[sensor_name] = min_max[i_min] - S2C.MINMAX_LINES_INTERVAL_QUARTER
                    max_lines[sensor_name] = min_max[i_max] + S2C.MINMAX_LINES_INTERVAL_QUARTER

        # Used only by legacy
        return min_lines, max_lines

    @classmethod
    def estimate_line_counts(  # pylint: disable=too-many-locals
        cls,
        config,
        margin_seconds: int = 0,
    ) -> Dict[str, np.ndarray]:
        """
        Estimate the line counts either from the granule information or from the reference date and min/max dates.

        :param int margin_seconds: margin in seconds if calculating from the min/max dates.
        :return: line count for each detector and band as a JSON dict.
        """

        # Line counts for each detector and band
        line_counts = defaultdict(dict)

        # Read the "min_max_lines" if present, filled from the granule information
        if "min_max_lines" in config:
            d_min_max = config["min_max_lines"]

            detectors = d_min_max["row_names"]
            i_min = list(d_min_max["col_names"]).index("min")  # should be 0
            i_max = list(d_min_max["col_names"]).index("max")  # should be 1
            values = d_min_max["values"]

            # One min/max value by detector
            assert len(values) == len(detectors)

            # Read values
            for det_name, min_max in zip(detectors, values):
                # Repeat the information for each band = for each sensor
                for band in S2Band.VALUES:
                    # convert line number from 10m to band resolution
                    line_counts[det_name][band.name] = int(
                        math.floor((min_max[i_max] - min_max[i_min] + 1) * S2C.PIXEL_HEIGHT_10 / band.pixel_height)
                    )

            # For detectors NOT in "min_max_lines": copy info from reference detector
            for detector in S2Detector.VALUES:
                if detector.name not in detectors:
                    line_counts[detector.name] = line_counts[detectors[0]]

        # With no granules, we calculate the line counts from the reference date and min/max dates
        else:
            # Read the GPS values
            timescale = TIMESCALE_MAP[cls.default_timescale]()
            d_line_detectors = config["line_datations"]
            config_lines = d_line_detectors["times"][cls.default_timescale]
            config_q = config["attitudes"]["times"][cls.default_timescale]  # quaternions
            config_pv = config["orbits"]["times"][cls.default_timescale]  # PV = position vitesse

            # Only accept offsets as seconds
            assert config_lines["unit"] == "s"
            assert config_q["unit"] == "s"
            assert config_pv["unit"] == "s"

            # Epochs as Orekit AbsoluteDate instances
            lines_epoch, q_epoch, pv_epoch = [
                AbsoluteDate(config_.get("epoch", DEFAULT_EPOCH), timescale)
                for config_ in (config_lines, config_q, config_pv)
            ]

            # Get the max datetimes from the offset values
            q_max = q_epoch.shiftedBy(float(np.max(config_q["offsets"])))
            pv_max = pv_epoch.shiftedBy(float(np.max(config_pv["offsets"])))

            # The smallest max date is used to determine the valid range
            max_time = q_max if q_max.isBefore(pv_max) else pv_max

            # Read the other line_detectors fields
            detector_names = d_line_detectors["col_names"]
            band_names = d_line_detectors["row_names"]
            rates = d_line_detectors["rates"]
            line_offsets = config_lines["offsets"]

            # One offset by detector and band
            assert len(line_offsets) == len(rates) == len(detector_names)
            if len(line_offsets) > 0:
                assert len(line_offsets[0]) == len(rates[0]) == len(band_names)

            # Initialize line_counts to 0, fix issue #295
            for detector in S2Detector.VALUES:
                for band in S2Band.VALUES:
                    line_counts[detector.name][band.name] = 0

            # For each sensor line detector offset = acquisition time of the first line
            for (
                det_name,
                det_offsets,
                det_rates,
            ) in zip(detector_names, line_offsets, rates):
                detector = S2Detector.from_name(det_name)

                for band_name, sensor_offset, rate in zip(band_names, det_offsets, det_rates):
                    band = S2Band.from_name(band_name)

                    # Acquisition time of the first line of the current sensor
                    sensor_first_time = lines_epoch.shiftedBy(float(sensor_offset))

                    # Rate = number of lines acquired each second.
                    # max_time = valid range
                    # line_count = (max_time - sensor_first_time) * rate + 1
                    # Remove the margin in seconds.
                    line_count = ((max_time.offsetFrom(sensor_first_time, timescale) - margin_seconds) * rate) + 1

                    # Save value
                    assert (
                        line_count >= 0
                    ), f"Line count:{line_count} has negative value for detector:{det_name!r} band:{band.name!r}"
                    line_counts[det_name][band.name] = int(math.floor(line_count))

        # Return values as a JSON dict
        return {
            "col_names": np.array([detector.name for detector in S2Detector.VALUES]),
            "row_names": np.array([band.name for band in S2Band.VALUES]),
            # 2D array detectors*bands
            "values": np.array([list(band.values()) for band in line_counts.values()], np.int32),
        }

    def _build_timestamp_models(self) -> None:
        """
        Build the LineDetectorTimestampModel instances.

        The input configuration contains:
          line_datations:
            col_names: [D01, ..., D12]
            row_names: [B01, ..., B12]
            times:
              [for each time scale e.g. GPS]:
                offsets: [[offset of ref_line from epoch for each detector and band]]
                unit: s (mandatory)
                epoch: "datetime"
            ref_lines: [[ref_line for each detector and band]]
            rates: [[rate for each detector and band]]

        Excepted output is:
          [for each detector and band]:
            LineDetectorTimestampModel init with:
              offsets: [offset for each row]
              unit: same as input
              epoch: same as input
              ref: input time scale
        """

        # Read configuration
        d_line_detectors = self.config["line_datations"]
        detector_names = d_line_detectors["col_names"]
        band_names = d_line_detectors["row_names"]
        ref_lines = d_line_detectors["ref_lines"]
        rates = d_line_detectors["rates"]

        # By default, try to read the GPS time scale
        try:
            time_scale = "GPS"
            d_times = d_line_detectors["times"][time_scale]

        # Else use the first time scale
        except KeyError:
            time_scale, d_times = next(iter(d_line_detectors["times"].items()))

        offsets = d_times["offsets"]  # mandatory
        unit = d_times.get("unit", DEFAULT_UNIT)  # optional
        epoch = d_times.get("epoch", DEFAULT_EPOCH)  # optional

        # One offset by detector and band
        assert len(offsets) == len(ref_lines) == len(rates) == len(detector_names)
        if len(offsets) > 0:
            assert len(offsets[0]) == len(ref_lines[0]) == len(rates[0]) == len(band_names)

        self._start_acq_gps = 1e9
        self._end_acq_gps = 0

        # Convert 2D list into dict of sensor:LineDetectorTimestampModel instances
        self.j_ref_date = None  #: reference date from the first sensor line datation
        for (
            det_name,
            det_offsets,
            det_ref_lines,
            det_rates,
        ) in zip(detector_names, offsets, ref_lines, rates):
            detector = S2Detector.from_name(det_name)

            for band_name, in_offset, ref_line, rate in zip(band_names, det_offsets, det_ref_lines, det_rates):
                band = S2Band.from_name(band_name)
                sensor = S2Sensor(detector, band).name

                # TODO: don't know what we should do in that case.
                # In S2Geo, the first line = reference line.
                # In ASGARD the first line is always 0 = the first numpy array index.
                assert ref_line == 1

                # The input offset value corresponds to the acquisition time of the ref_line since the epoch.
                # Rate = 1/acquisition time between two adjacent lines.
                # Each line offset value = input_offset + (line / rate)
                num_lines = int(self.coordinates[sensor]["lines"])
                out_offsets = in_offset + np.arange(num_lines) / rate
                out_offsets = np.array(out_offsets, dtype=np.double)

                # Init a LineDetectorTimestampModel instance for the current sensor.
                # Pass the offsets for each row + the input unit, epoch and time scale
                self.timestamp_models[sensor] = LineDetectorTimestampModel(
                    times={
                        "offsets": out_offsets,
                        "unit": unit,
                        "epoch": epoch,
                        "ref": time_scale,
                    },
                    ref=time_scale,
                )

                # record the start and end of acquisitions
                self._start_acq_gps = min(self._start_acq_gps, out_offsets[0])
                self._end_acq_gps = max(self._start_acq_gps, out_offsets[-1])

    def _build_orbit_model(self):
        """
        Build the GenericOrbitModel instance.
        """
        # Copy the optional arguments for the model
        model_kwargs = self.config.get("models", {}).get("orbit", {})

        # Add the mandatory arguments
        model_kwargs.update(
            {
                "orbit": self.config["orbits"],  # MSI product input value
                "earth_body": self.body_model,
                "attitude": self.config["attitudes"],  # MSI product input value
            }
        )

        # Add refining configuration parameters if they exist in the configuration
        if "refining" in self.config and "spacecraft_position" in self.config["refining"]:
            # Get the center_time from the input config file
            key_central_time, val_central_time = list(self.config["refining"]["center_time"].items())[0]
            # Convert it into a shift versus the the reference epoch
            center_time_gps = AbsoluteDate(val_central_time, TIMESCALE_MAP[key_central_time]()).durationFrom(
                AbsoluteDate(self.default_time["epoch"], TIMESCALE_MAP["GPS"]())
            )

            model_kwargs.update(
                {
                    "refining": {
                        "center_time": {"GPS": center_time_gps},  # central time
                        "default_time": self.default_time,  # default epoch
                        "spacecraft_corr_coeff": self.config["refining"][
                            "spacecraft_position"
                        ],  # refining coefficients
                    }
                }
            )

        # Set time_orb with acquisition start
        model_kwargs["time_orb"] = "UTC=" + self.time_reference.to_str(
            self._start_acq_gps,
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
            fmt="CCSDSA_MICROSEC",
            unit=self.default_time["unit"],
            epoch=self.default_time["epoch"],
        )

        # Init the GenericOrbitModel instance
        self.orbit_model = GenericOrbitModel(**model_kwargs)

    def _translate_one_transform(  # pylint: disable=too-many-positional-arguments
        self,
        name: str,
        origin: str,
        rotations: Tuple[np.ndarray, np.ndarray, np.ndarray],
        combination_order: str,
        scale: float,
        refining: dict = None,
        center_time: str = None,
    ) -> list:
        """
        Translate one transform defined by GIPP SPAMOD into states to implement asgard transforms.
        When there is a scaling, we use an intermediate step to compose a rotation and an homothety.

        :param str name: Name of target state
        :param str origin: Name of origin state
        :param rotations: rotations defined by a tuple with (rotation angles, axes, units)
        :param combination_order: composition order for rotation and homothety
        :param scale: Scaling factor on Z axis
        :param refining: Dict with refining parameters (if supplied)
        :return: List of state transitions
        """

        central_time = None
        refining = refining or {}

        if center_time:
            # Get the center_time from the input config file
            key_central_time, val_central_time = list(center_time.items())[0]
            # Convert it into a shift versus the the reference epoch
            central_time = AbsoluteDate(val_central_time, TIMESCALE_MAP[key_central_time]()).durationFrom(
                AbsoluteDate(self.default_time["epoch"], TIMESCALE_MAP[self.default_time["ref"]]())
            )

        # prepare rotation
        rotation = np.zeros((3,), dtype="float64")
        axis_map = {"X": 0, "Y": 1, "Z": 2}
        for axis_name, angle, unit in zip(rotations[1], rotations[0], rotations[2]):
            angle_rad = angle * RADIANS_SCALING_FACTORS[unit]
            rotation[axis_map[axis_name]] = angle_rad
        euler_order = "YXZ"
        rotation_config = {"rotation": rotation, "euler_order": euler_order}

        if "rotation" in refining:
            x_coeff = refining["rotation"].get("x", [])
            y_coeff = refining["rotation"].get("y", [])
            z_coeff = refining["rotation"].get("z", [])
            max_degree = max(len(x_coeff), len(y_coeff), len(z_coeff)) - 1
            xyz_coeff = np.zeros((max_degree + 1, 3), dtype="float64")
            xyz_coeff[: len(x_coeff), 0] = x_coeff
            xyz_coeff[: len(y_coeff), 1] = y_coeff
            xyz_coeff[: len(z_coeff), 2] = z_coeff
            # Like other rotation angles for spacecraft transformations, they need to be reversed
            xyz_coeff *= -1.0

            if max_degree == 0:
                # Add static correction to current rotation angles
                rotation_config["rotation"] += xyz_coeff[0]
            elif max_degree > 0:
                # Create a DynamicRotation
                xyz_coeff[0] += rotation_config["rotation"]
                rotation_config = {
                    "time_based_transform": {
                        "rotation": xyz_coeff,
                        "euler_order": euler_order,
                        "epoch": self.default_time["epoch"],
                        "unit": self.default_time["unit"],
                        "ref": self.default_time["ref"],
                        "central_time": central_time,
                    }
                }

        # prepare scaling (only for Z)
        scale_vector = np.array([1.0, 1.0, scale], dtype="float64")
        homothety_config = {"homothety": scale_vector}

        if "homothety" in refining:
            x_coeff = refining["homothety"].get("x", [])
            y_coeff = refining["homothety"].get("y", [])
            z_coeff = refining["homothety"].get("z", [])
            max_degree = max(len(x_coeff), len(y_coeff), len(z_coeff)) - 1
            xyz_coeff = np.zeros((max_degree + 1, 3), dtype="float64")
            xyz_coeff[: len(x_coeff), 0] = x_coeff
            xyz_coeff[: len(y_coeff), 1] = y_coeff
            xyz_coeff[: len(z_coeff), 2] = z_coeff
            if max_degree == 0:
                # Add static correction to current rotation angles
                homothety_config["homothety"] += xyz_coeff[0]
            elif max_degree > 0:
                raise NotImplementedError("Dynamic homothety not implemented yet")

        # fill states
        output = []

        if combination_order == "NO_SCALE":
            rotation_config["name"] = name
            rotation_config["origin"] = origin
            output.append(rotation_config)

        elif combination_order == "ROTATION_THEN_SCALE":
            intermediate_state = name + "_rot"

            # finish rotation config
            rotation_config["name"] = intermediate_state
            rotation_config["origin"] = origin
            output.append(rotation_config)

            # finish homothety config
            homothety_config["name"] = name
            homothety_config["origin"] = intermediate_state
            output.append(homothety_config)

        elif combination_order == "SCALE_THEN_ROTATION":
            intermediate_state = name + "_scale"

            # finish rotation config
            rotation_config["name"] = name
            rotation_config["origin"] = intermediate_state
            output.append(rotation_config)

            # finish homothety config
            homothety_config["name"] = intermediate_state
            homothety_config["origin"] = origin
            output.append(homothety_config)

        else:
            raise ValueError("Unknown combination order: " + combination_order)
        return output

    def _build_platform_model(self):
        """
        Build the GenericPlatformModel instance.
        """

        # Convert input args into states and aliases
        d_spacecraft = self.config["spacecraft"]
        all_states = []
        all_aliases = {}

        # Detect refining informations
        d_refining = self.config.get("refining", {})

        # translate transform "piloting_to_msi"
        states = self._translate_one_transform(
            "platform",
            "msi",
            (
                -d_spacecraft["piloting_to_msi"]["rotations"]["values"],
                d_spacecraft["piloting_to_msi"]["rotations"]["axis"],
                d_spacecraft["piloting_to_msi"]["rotations"]["units"],
            ),
            d_spacecraft["piloting_to_msi"]["combination_orders"],
            d_spacecraft["piloting_to_msi"]["scale_factors"],
            refining=d_refining.get("msi_state"),
            center_time=d_refining.get("center_time", None),
        )
        all_states.extend(states)

        # translate transforms "msi_to_focalplane"
        for idx, plane in enumerate(d_spacecraft["msi_to_focalplane"]["col_names"]):
            states = self._translate_one_transform(
                "msi",
                plane,
                (
                    -d_spacecraft["msi_to_focalplane"]["rotations"]["values"][idx],
                    d_spacecraft["msi_to_focalplane"]["rotations"]["axis"][idx],
                    d_spacecraft["msi_to_focalplane"]["rotations"]["units"][idx],
                ),
                d_spacecraft["msi_to_focalplane"]["combination_orders"][idx],
                d_spacecraft["msi_to_focalplane"]["scale_factors"][idx],
                refining=d_refining.get("focalplane_state", {}).get(plane),
                center_time=d_refining.get("center_time", None),
            )
            all_states.extend(states)

        # translate transforms "focalplane_to_sensor"
        for idx, plane in enumerate(d_spacecraft["focalplane_to_sensor"]["col_names"]):
            for det, det_name in enumerate(d_spacecraft["focalplane_to_sensor"]["row_names"]):
                target = plane + "_" + det_name
                states = self._translate_one_transform(
                    plane,
                    target,
                    (
                        -d_spacecraft["focalplane_to_sensor"]["rotations"]["values"][idx, det],
                        d_spacecraft["focalplane_to_sensor"]["rotations"]["axis"][idx, det],
                        d_spacecraft["focalplane_to_sensor"]["rotations"]["units"][idx, det],
                    ),
                    d_spacecraft["focalplane_to_sensor"]["combination_orders"][idx, det],
                    d_spacecraft["focalplane_to_sensor"]["scale_factors"][idx, det],
                )
                all_states.extend(states)

                # create aliases
                for band in S2Band.VALUES:
                    if band.focal_plane == plane:
                        # e.g. aliases["B01/D01"]=VNIR_D01 or aliases["B12/D01"]=SWIR_D01
                        all_aliases[band.name + "/" + det_name] = target

        # Init the GenericPlatformModel instance
        self.platform_model = GenericPlatformModel(states=all_states, aliases=all_aliases)

    def _build_pointing_model(self):
        """
        Build the LineDetectorPointingModel instance.
        """

        # Argument passed to the LineDetectorPointingModel constructor
        unit_vectors = {}

        # For each input viewing direction sensor and tan psi x and y values
        for view_dir in self.config["viewing_directions"]:
            sensor = view_dir["sensor"]
            in_values = view_dir["values"]

            tan_psi_x, tan_psi_y = in_values
            los_vectors = np.column_stack((tan_psi_y, -tan_psi_x, np.ones(len(tan_psi_y))))
            normalized_los_vectors = los_vectors / np.linalg.norm(los_vectors, axis=1)[:, np.newaxis]

            # Save all values for the current sensor
            unit_vectors[sensor] = normalized_los_vectors

        # Init the LineDetectorPointingModel instance
        self.pointing_model = LineDetectorPointingModel(unit_vectors=unit_vectors)

    def _build_propagation_model(self):
        """
        Build the PropagationModel instance.
        """

        # Read configuration
        geoid_path = self.config["resources"].get("geoid")
        dem_globe_path = self.config["resources"].get("dem_globe")
        dem_srtm_path = self.config["resources"].get("dem_srtm")
        dem_zarr_path = self.config["resources"].get("dem_zarr")
        overlapping_tiles = self.config["resources"].get("overlapping_tiles")

        # Save DEM information
        if dem_zarr_path is None:
            if dem_globe_path:  # overlap = true
                dem_path = dem_globe_path
                dem_source = "GLOBE"
            elif dem_srtm_path:  # overlap = false
                dem_path = dem_srtm_path
                dem_source = "SRTM"

            # Use the default geoid
            if not geoid_path:
                geoid_path = osp.join(get_orekit_resources(), "resources/GEOID/egm96_15.gtx")
                assert osp.isfile(geoid_path)

        # Copy the optional arguments for the model
        model_kwargs = self.config.get("models", {}).get("propagation", {})  # read input "models/propagation" field
        model_kwargs["earth_body"] = self.body_model
        if geoid_path:
            model_kwargs["geoid_path"] = geoid_path
        model_kwargs["body_rotating_frame"] = "EF"  # hard-coded, Earth-Fixed = ITRF

        if dem_zarr_path is not None:
            model_kwargs.setdefault("zarr_dem", {})
            model_kwargs["zarr_dem"]["path"] = dem_zarr_path
        else:
            model_kwargs.update(
                {
                    "native_dem": {
                        "path": dem_path,  # pylint: disable=E0601
                        "source": dem_source,  # pylint: disable=E0601
                        "overlapping_tiles": overlapping_tiles,
                    },
                }
            )

        # Init the PropagationModel instance
        self.propagation_model = PropagationModel(**model_kwargs)
        self.__max_cached_tiles = self.propagation_model.max_cached_tiles  # pylint: disable=W0238

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for constructor, as a JSON schema.

        :download:`JSON schema <doc/scripts/init_schema/schemas/S2MSIGeometry.schema.json>`

        :download:`JSON example <doc/scripts/init_schema/examples/S2MSIGeometry.example.json>`
        """
        # Const reusable objects

        detectors_enum = {"enum": [detector.name for detector in S2Detector.VALUES]}
        bands_enum = {"enum": [band.name for band in S2Band.VALUES]}
        sensors_enum = {
            "enum": [S2Sensor(detector, band).name for detector in S2Detector.VALUES for band in S2Band.VALUES]
        }
        focal_planes_enum = {"enum": ["VNIR", "SWIR"]}

        def object_array(*shape):
            return {
                "type": "array",
                "dtype": "object",
                "shape": shape,
            }

        refining_state = {
            "type": "object",
            "properties": {
                "rotation": refining_axis("x", "y", "z"),
                "homothety": refining_axis("z"),
            },
            "additionalProperties": False,
        }

        # base_shape = combination orders and scale factors shape
        def spacecraft_schema(col_names, row_names, *base_shape):
            return {
                "type": "object",
                "properties": {
                    **col_names,
                    **row_names,
                    "matrices": {
                        "type": "object",
                        "properties": {
                            "axis": generate_float64_array_schema(*base_shape, 3, 3),  # 3 matrices * 3 axis
                            "angles": object_array(*base_shape, 3),  # 3 matrices
                        },
                        "required": ["axis", "angles"],
                    },
                    "rotations": {
                        "type": "object",
                        "properties": {
                            "values": generate_float64_array_schema(*base_shape, 3),  # 3 axis
                            "axis": object_array(*base_shape, 3),  # 3 axis
                            "units": object_array(*base_shape, 3),  # 3 axis
                        },
                        "required": ["values", "axis", "units"],
                    },
                    "combination_orders": ({"type": "string"} if not base_shape else object_array(*base_shape)),
                    "scale_factors": (
                        {"type": "number"} if not base_shape else generate_float64_array_schema(*base_shape)
                    ),
                },
                "oneOf": [{"required": ["matrices"]}, {"required": ["rotations"]}],
                "required": ["combination_orders", "scale_factors"],
                "additionalProperties": False,
            }

        ###############
        # MAIN SCHEMA #
        ###############

        return {
            "type": "object",
            "definitions": COMMON_DEFINITIONS,
            "properties": {
                "resources": {
                    "type": "object",
                    "properties": {
                        "iers": {"type": "string"},
                        "geoid": DEM_DATASET_SCHEMA,
                        "dem_globe": {"type": "string"},
                        "dem_srtm": {"type": "string"},
                        "dem_zarr": DEM_DATASET_SCHEMA,
                        "overlapping_tiles": {"type": "boolean"},
                    },
                    "anyOf": [
                        {"required": ["dem_globe"]},
                        {"required": ["dem_srtm"]},
                        {"required": ["dem_zarr"]},
                    ],
                    "required": ["overlapping_tiles"],
                    "additionalProperties": False,
                },
                "line_datations": {
                    "type": "object",
                    "properties": {
                        "col_names": {"type": "array", "items": detectors_enum},
                        "row_names": {"type": "array", "items": bands_enum},
                        "times": {"$ref": "#/definitions/timescale_array_2d"},
                        "ref_lines": generate_float64_array_schema(":", ":"),
                        "rates": generate_float64_array_schema(":", ":"),
                    },
                    "required": [
                        "col_names",
                        "row_names",
                        "times",
                        "ref_lines",
                        "rates",
                    ],
                    "additionalProperties": False,
                },
                "refining": {
                    "type": "object",
                    "properties": {
                        "center_time": {
                            "type": "object",
                            "properties": {
                                "UTC": {"$ref": "#/definitions/ascii_timestamp"},
                                "UT1": {"$ref": "#/definitions/ascii_timestamp"},
                                "GPS": {"$ref": "#/definitions/ascii_timestamp"},
                            },
                            "minProperties": 1,
                            "additionalProperties": False,
                        },
                        "spacecraft_position": refining_axis("x", "y", "z"),
                        "msi_state": refining_state,
                        "focalplane_state": {
                            "type": "object",
                            "properties": {
                                "VNIR": refining_state,
                                "SWIR": refining_state,
                            },
                            "additionalProperties": False,
                        },
                        "additionalProperties": False,
                    },
                    "required": ["center_time"],
                    "additionalProperties": False,
                },
                "attitudes": {"$ref": "#/definitions/attitude"},
                "orbits": {"$ref": "#/definitions/orbit"},
                "eop": TimeReference.init_schema(),
                "min_max_lines": {
                    "type": "object",
                    "properties": {
                        "row_names": {
                            "type": "array",
                            "minItems": 1,
                            "items": detectors_enum,
                        },
                        "col_names": {
                            "type": "array",
                            "minItems": 2,
                            "maxItems": 2,
                            "items": {"enum": ["min", "max"]},
                        },
                        "values": generate_float64_array_schema(":", 2),
                    },
                    "required": ["col_names", "row_names", "values"],
                    "additionalProperties": False,
                },
                "line_counts": {
                    "type": "object",
                    "properties": {
                        "col_names": {"type": "array", "items": detectors_enum},
                        "row_names": {"type": "array", "items": bands_enum},
                        "values": generate_array_schema("int32", 12, 13),
                    },
                    "required": [
                        "col_names",
                        "row_names",
                        "values",
                    ],
                    "additionalProperties": False,
                },
                "viewing_directions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sensor": sensors_enum,
                            "values": generate_float64_array_schema(2, ":"),
                        },
                        "required": ["sensor", "values"],
                        "additionalProperties": False,
                    },
                },
                "spacecraft": {
                    "type": "object",
                    "properties": {
                        "piloting_to_msi": spacecraft_schema({}, {}),  # single occurrence
                        "msi_to_focalplane": spacecraft_schema(
                            {
                                "col_names": {
                                    "type": "array",
                                    "items": focal_planes_enum,
                                }
                            },
                            {},
                            2,
                        ),  # 2 focal planes
                        "focalplane_to_sensor": spacecraft_schema(
                            {
                                "col_names": {
                                    "type": "array",
                                    "items": focal_planes_enum,
                                }
                            },
                            {"row_names": {"type": "array", "items": detectors_enum}},
                            2,
                            12,
                        ),  # 2 focal planes * 12 detectors
                    },
                    "required": [
                        "piloting_to_msi",
                        "msi_to_focalplane",
                        "focalplane_to_sensor",
                    ],
                    "additionalProperties": False,
                },
                "models": {  # ASGARD low-level model optional arguments
                    "type": "object",
                    "properties": {
                        "body": {  # EarthBody
                            "type": "object",
                            "properties": {
                                "ellipsoid": {
                                    "type": "string",
                                    "enum": ELLIPSOID_MODELS,
                                },
                            },
                        },
                        "orbit": {  # GenericOrbitModel
                            "type": "object",
                            "properties": {
                                "interpolation_window": {"type": "integer"},  # default=10
                            },
                        },
                        "propagation": {  # PropagationModel
                            "type": "object",
                            "properties": {
                                "max_cached_tiles": {"type": "integer"},
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
                        },
                    },
                },
            },
            "required": [
                "resources",
                "line_datations",
                "attitudes",
                "orbits",
                "viewing_directions",
                "spacecraft",
            ],
            "additionalProperties": False,
        }

    def direct_loc_over_geoid(
        self,
        coordinates: ndarray,
        geometric_unit: str | None = None,
        altitude: float | None = None,
    ) -> Tuple[ndarray, ndarray]:
        """
        Direct location at constant altitude over geoid

        :param numpy.ndarray coordinates: Array of coordinates
        :param str geometric_unit: Name of a specific geometric unit to use (optionnal)
        :param float altitude: Constant altitude to use for direct location, if None the DEM is used
        :return: array of projected coordinates, array of acquisition times
        """

        # flatten coordinates
        flat_coord = flatten_array(coordinates, 2)
        dataset = {"coords": flat_coord}
        if geometric_unit is None:
            geometric_unit = self._instr_list[0]

        dataset["geom"] = geometric_unit

        # Estimate acquisition times (ndarray)
        self.timestamp_models[geometric_unit].acquisition_times(dataset)

        # Line of sight wrt Instrument frame + time
        self.pointing_model.compute_los(dataset)

        # transform line of sight to Satellite reference frame
        self.platform_model.transform_position(
            dataset,
            frame_in=geometric_unit,
            frame_out="platform",
        )
        self.platform_model.transform_direction(
            dataset,
            frame_in=geometric_unit,
            frame_out="platform",
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

        # propagation to target
        self.propagation_model.sensor_to_target(dataset, altitude=altitude, altitude_reference="geoid")

        # restore outputs
        gnd_coords = restore_array(dataset["gnd_coords"], coordinates.shape[:-1], last_dim=3)
        gnd_coords[..., 0] = (gnd_coords[..., 0] + 180) % 360 - 180
        gnd_coords[..., 1] = (gnd_coords[..., 1] + 90) % 180 - 90

        acq_times = restore_array(dataset["times"]["offsets"], coordinates.shape[:-1])

        return gnd_coords, acq_times
