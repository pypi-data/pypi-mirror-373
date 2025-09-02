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
Module for Sentinel 3 SLSTR instrument
"""

import copy
import logging
import math

import numpy as np

from asgard.core.frame import FrameId
from asgard.core.product import AbstractOpticalGeometry
from asgard.core.schema import (
    DEM_DATASET_SCHEMA,
    NAVATT_SCHEMA,
    ORBIT_AUX_INFO_SCHEMA,
    TIME_ARRAY_SCHEMA,
    TIMESCALE_NAME_SCHEMA,
)
from asgard.core.time import JD_TO_MICROSECONDS, JD_TO_SECONDS, TimeRef
from asgard.models.body import EarthBody
from asgard.models.orbit import GenericOrbitModel, OrbitScenarioModel
from asgard.models.platform import GenericPlatformModel
from asgard.models.propagation import PropagationModel
from asgard.models.scanningdetector import (
    ScanningDetectorPointingModel,
    ScanningDetectorTimestampModel,
)
from asgard.models.thermoelastic import ThermoelasticModel
from asgard.models.time import TimeReference
from asgard.sensors.synthetic import GroundTrackGrid

GEOCAL_MISALIGNMENT = 0b01
GEOCAL_THERMOELASTIC = 0b10
# Constant for curvature of the mirror in oblique view, in ADF the value is equal to 50
# but the computation lead to have 51 values.
OBL_TP_MARGIN = 50


class S3SLSTRGeometry(AbstractOpticalGeometry):
    """
    Sentinel 3 SLSTR product
    """

    _view_list = ["NAD", "OBL"]
    _detector_count = {"1KM": 2, "1KM_F1": 2, "05KM_A": 4, "05KM_B": 4}

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        # call superclass constructor
        super().__init__(*args, **kwargs)

        # SLSTR constants
        self._constants = {}
        self._constants["num_acq_per_scan"] = 3670  # number of samples per scan
        self._constants["scan_period_s"] = 0.2999858  # duration of a scan in s (also called delta_t_theor)
        self._constants["scan_period_mjd"] = self._constants["scan_period_s"] / JD_TO_SECONDS
        self._constants["scan_angle_1km_step"] = 360.0 / 3670.0

        # Geometric units: <view>/<spectral_group>/<detector_index>
        #   with <view> in ["NAD", "OBL"]
        #        <spectral_group> in ["1KM", "F1", "05KM_A", "05KM_B"]
        #        <detector_index> in [0, 1, 2, 3]  (some spectral groups only have 2 detectors)
        self._spectral_group = ["1KM", "1KM_F1", "05KM_A", "05KM_B"]

        # filter optional groups F1 et stripe B
        self.config["enable_f1"] = kwargs.get("enable_f1", True)
        self.config["enable_stripe_b"] = kwargs.get("enable_stripe_b", True)
        if not self.config["enable_f1"]:
            self._spectral_group.remove("1KM_F1")
        if not self.config["enable_stripe_b"]:
            self._spectral_group.remove("05KM_B")

        # build list of instruments
        self._build_instrument_list()

        # Consolidate the time parameters
        self._build_consolidated_times()

        # fill coordinates definition
        self._build_coordinate_definitions()

        # Setup time model
        self.time_model = TimeReference(**kwargs.get("eop", {}))

        # Setup body model
        self.body_model = EarthBody(ellipsoid="WGS84", time_reference=self.time_model)

        # Setup timestamp model
        self._build_timestamp_models()

        # Set time_orb with acquisition start
        time_orb = "UTC=" + self.time_model.to_str(
            self.config["acquisition_times"]["start"],
            ref_in=TimeRef.GPS,
            ref_out=TimeRef.UTC,
            fmt="CCSDSA_MICROSEC",
            unit=self.default_time["unit"],
            epoch=self.default_time["epoch"],
        )

        # Setup orbit model
        if "orbit_state_vectors" in kwargs["orbit_aux_info"]:
            valid_navatt = "navatt" in kwargs
            self.config["valid_navatt"] = valid_navatt
            orb_list = kwargs["orbit_aux_info"]["orbit_state_vectors"]

            if valid_navatt:
                orb_list.append(kwargs["navatt"]["orbit"])
            # check the frame of each orbit
            for orbit in orb_list:
                orb_frame = orbit.get("frame", "EME2000")
                if orb_frame != "EME2000":
                    logging.warning("Orbit frame used is %s, SLSTR constructor converts it to EME2000 frame", orb_frame)
                    self.body_model.transform_orbit(orbit, FrameId.EME2000)

            fused_orbit = GenericOrbitModel.merge_orbits(orb_list)

            assert len(fused_orbit["positions"]) == len(fused_orbit["velocities"])
            assert len(fused_orbit["velocities"]) == len(fused_orbit["times"]["GPS"]["offsets"])
            orbit_config = {
                "orbit": fused_orbit,
                "attitude": kwargs["navatt"]["attitude"] if valid_navatt else None,
                "earth_body": self.body_model,
                "time_orb": time_orb,
            }

            self.orbit_model = GenericOrbitModel(**orbit_config)

        elif "orbit_scenario" in kwargs["orbit_aux_info"]:  # initialize with OSF
            self.body_model = EarthBody(ellipsoid="WGS84")  # is this EME2000 ?
            orbit_config = {
                "orbit_scenario": kwargs["orbit_aux_info"]["orbit_scenario"][0],  # Asgard support only one OSF for now
                "orbit_frame": "EME2000",
                "attitude": {
                    "aocs_mode": "YSM",
                    "frame": "EME2000",
                },
                "earth_body": self.body_model,
                "time_orb": time_orb,
            }
            self.orbit_model = OrbitScenarioModel(**orbit_config)

        else:
            raise TypeError("Missing, at least one orbit file")

        # Possibility to overwrite the anx gps time for tie point and quasi-cartesian grid
        if "jd_anx" in self.config:
            self.orbit_model.info["gps_anx"] = self.config["jd_anx"]

        # Setup platform model

        # set default geocalibration mode (sw_geocal)
        #  sw_geocal & 0b01 = use misalignment angles
        #  sw_geocal & 0b10 = use thermoelastic effects
        self.config["sw_geocal"] = kwargs.get("sw_geocal", GEOCAL_MISALIGNMENT)

        self._build_platform_model()

        # Setup pointing model
        self.pointing_model = ScanningDetectorPointingModel(geometry_model=kwargs["geometry_model"])

        # Setup propagation model
        propagation_config = self.config.get("models", {}).get("propagation", {})
        propagation_config["earth_body"] = self.body_model
        if "geoid" in kwargs["resources"]:
            propagation_config["geoid_path"] = kwargs["resources"]["geoid"]
        self.config["dem_type"] = kwargs["resources"].get("dem_type", "ZARR")
        if self.config["dem_type"] == "ZARR":
            propagation_config.setdefault("zarr_dem", {})
            propagation_config["zarr_dem"]["path"] = kwargs["resources"]["dem_path"]
        else:
            propagation_config["native_dem"] = {
                "path": kwargs["resources"]["dem_path"],
                "source": self.config["dem_type"],
                "overlapping_tiles": bool(self.config["dem_type"] == "SRTM"),
            }
        self.propagation_model = PropagationModel(**propagation_config)

    def _build_consolidated_times(self):
        """
        Process time parameters and fill default values
        """

        # detect start/end times
        conf_times = self.config["acquisition_times"]
        conf_times["reference"] = self.config["acquisition_times"].get("reference", "GPS")
        self.default_time["ref"] = conf_times["reference"]
        conf_times["pix10sync"] = self.config["acquisition_times"].get("pix10sync", 81.74)
        conf_times["start"] = self.config["acquisition_times"].get(
            "start",
            min(
                np.min(conf_times["NAD"]["scan_times"]["offsets"]),
                np.min(conf_times["OBL"]["scan_times"]["offsets"]),
            ),
        )
        conf_times["end"] = self.config["acquisition_times"].get(
            "end",
            max(
                np.max(conf_times["NAD"]["scan_times"]["offsets"]),
                np.max(conf_times["OBL"]["scan_times"]["offsets"]),
            )
            + self._constants["scan_period_mjd"],
        )

        # prepare first_acquisition as np.ndarray
        for view in self._view_list:
            first_acq = conf_times[view]["first_acquisition"]
            if not isinstance(first_acq, np.ndarray):
                first_acq = np.array(first_acq, dtype="int32")
            # Apply modulus with Nacq
            first_acq = first_acq % self._constants["num_acq_per_scan"]

            assert len(first_acq) in [
                1,
                len(conf_times[view]["scan_times"]["offsets"]),
            ]

            # Compact array if there is a single value
            if len(first_acq) > 1 and len(np.unique(first_acq)) == 1:
                first_acq = first_acq[0:1]

            conf_times[view]["first_acquisition"] = first_acq

        # set default step to 1
        conf_times["NAD"]["step"] = self.config["acquisition_times"]["NAD"].get("step", 1)
        conf_times["OBL"]["step"] = self.config["acquisition_times"]["OBL"].get("step", 1)

    def _build_timestamp_models(self):
        """
        Setup the map of ScanningDetectorTimestampModel
        """

        model_cache = {}
        time_delta = self.config["acquisition_times"]["pix10sync"] / JD_TO_MICROSECONDS
        nb_acq = self._constants["num_acq_per_scan"]
        for instr in self._instr_list:
            view, group, _ = instr.split("/")
            # handle cache, all detectors share the same timestamp model
            view_group = view + "/" + group
            if view_group in model_cache:
                self.timestamp_models[instr] = model_cache[view_group]  # noqa: B909
                continue

            # compute pixel start
            first_acq = self.config["acquisition_times"][view]["first_acquisition"]
            step = self.config["acquisition_times"][view]["step"]
            if group.startswith("05KM"):
                # shift to 500m pixel indexing
                scale = 2
                if step > 1:
                    # for TPix grid (sub-sampled grid), we need to double the step
                    step *= 2
                # For native instrument grid (step=1), we assume input coordinates already have 500m
                # indexing
            else:
                scale = 1

            if len(first_acq) == 1:
                first_acq = int(first_acq[0])
            pixel_start = (first_acq % nb_acq) * scale

            # compute pixel period
            pixel_period = time_delta / scale
            config_timestamp = {
                "scan_times": self.config["acquisition_times"][view]["scan_times"],
                "pixel_period": pixel_period,
                "pixel_start": pixel_start,
                "step": step,
            }

            model_cache[view_group] = ScanningDetectorTimestampModel(**config_timestamp)  # noqa: B909
            self.timestamp_models[instr] = model_cache[view_group]  # noqa: B909

    def _build_thermoelastic_model(self):
        """
        Setup the thermoelastic model and return it (if needed)
        """

        assert "thermoelastic" in self.config

        orb_info = self.orbit_model.info

        # setup on-orbit position LUT
        if "navatt" in self.config:
            lut_times = self.config["navatt"]["times"]["offsets"]
            lut_oop = self.config["navatt"]["oop"]
        else:
            # build a custom LUT based on start/end acquisition
            lut_times = np.arange(
                self.config["acquisition_times"]["start"] - 4 / JD_TO_SECONDS,
                self.config["acquisition_times"]["end"] + 4 / JD_TO_SECONDS,
                1 / JD_TO_SECONDS,
            )
            lut_oop = self.orbit_model.position_on_orbit({"offsets": lut_times})

        # Instrument indexing: NAD -> 0,  OBL -> 1
        return ThermoelasticModel(
            thermoelastic=self.config["thermoelastic"],
            doy=(orb_info["utc_anx"] + orb_info["period_jd"] / 2.0) % 365.24,
            instruments=self._view_list,
            lut_times=lut_times,
            lut_oop=lut_oop,
        )

    def _build_platform_model(self):
        """
        Setup the GenericPlatformModel
        """

        platform_config = {"states": [], "aliases": {}}

        if self.config["sw_geocal"] & GEOCAL_THERMOELASTIC:
            # Case: thermoelastic effect
            thermoelastic = self._build_thermoelastic_model()

            # Thermoelastic quaternions are in the direction SLSTR_to_S3, but the thermoelastic model
            # already invert them, so we need to invert twice
            thermoelastic = thermoelastic.inv()
            # TODO : or we remove the inversion in ThermoelasticModel
            thermo_map = thermoelastic.split()
            for view, thermo in thermo_map.items():
                platform_config["states"].append(
                    {
                        "name": view,
                        "origin": "platform",
                        "time_based_transform": thermo,
                    }
                )
        elif self.config["sw_geocal"] & GEOCAL_MISALIGNMENT:
            for view in self._view_list:
                # use misalignment correction
                platform_config["states"].append(
                    {
                        "name": view,
                        "origin": "platform",
                        "rotation": self.compute_misalignment_rotation(self.config["geometry_model"], view),
                    }
                )
        else:
            # Case: no geocalibraiton, setup a dummy state and aliases to platform
            platform_config["states"].append(
                {
                    "name": "dummy",
                    "origin": "platform",
                    "translation": np.array([0.0, 0.0, 0.0]),
                }
            )

        # fill aliases for all instruments
        for instr in self._instr_list:
            view, _, _ = instr.split("/")
            if self.config["sw_geocal"]:
                platform_config["aliases"][instr] = view
            else:
                platform_config["aliases"][instr] = "platform"
        self.platform_model = GenericPlatformModel(**platform_config)

    def _build_instrument_list(self):
        """
        Fill the instrument list
        """
        self._instr_list = []
        for view in self._view_list:
            for group in self._spectral_group:
                for det in range(self._detector_count[group]):
                    self._instr_list.append(f"{view}/{group}/{det}")

    def _build_coordinate_definitions(self):
        """
        Fill the coordinate range for each instrument
        """
        self.coordinates = {}
        for instr in self._instr_list:
            geom_parts = instr.split("/")
            view = geom_parts[0]
            group = geom_parts[1]
            nb_scan = len(self.config["acquisition_times"][view]["scan_times"]["offsets"])
            nb_pix = self.config["acquisition_times"][view]["nb_pixels"]
            if group.startswith("05KM") and self.config["acquisition_times"][view]["step"] == 1:
                # for 500m native resolution, we take twice the number of 1km pixels
                nb_pix *= 2

            self.coordinates[instr] = {  # noqa: B909
                "pixel": nb_pix,
                "scan": nb_scan,
            }

    @classmethod
    def init_schema(cls) -> dict:
        """
        Expected schema for constructor, as a JSON schema

        :download:`JSON schema <doc/scripts/init_schema/schemas/S3SLSTRGeometry.schema.json>`

        :download:`JSON example <doc/scripts/init_schema/examples/S3SLSTRGeometry.204936.example.json>`
        """
        return {
            "type": "object",
            "definitions": {
                "slstr_time_array": {
                    "type": "object",
                    "properties": {
                        "scan_times": TIME_ARRAY_SCHEMA,
                        "nb_pixels": {"type": "integer"},
                        "first_acquisition": {
                            "type": "array",
                            "items": {"type": "number"},
                        },
                        "step": {"type": "integer"},
                    },
                    "required": ["scan_times", "nb_pixels", "first_acquisition"],
                },
                "slstr_scan_encoder_array": {
                    "type": "array",
                    "dtype": "float64",
                    "description": (
                        "2D array of scan angles (deg) given by the encoder, " "lines are scans, columns are pixels"
                    ),
                },
                "slstr_geometry_model": {
                    "type": "object",
                    "properties": {
                        "scans_inclination_nadir": {"type": "number"},
                        "F1_scanangle_offset": {"type": "number"},
                        "X_misalignment_correction": {"type": "number"},
                        "Y_misalignment_correction": {"type": "number"},
                        "Z_misalignment_correction": {"type": "number"},
                        "X_misalignment_correction_OB": {"type": "number"},
                        "Y_misalignment_correction_OB": {"type": "number"},
                        "Z_misalignment_correction_OB": {"type": "number"},
                        "scans_mirror_offset": {"type": "array", "shape": (2,)},
                        "scans_cone_angle": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_1km": {"type": "array", "shape": (2,)},
                        "cos_mu_centre_1km": {"type": "array", "shape": (2,)},
                        "cos_nu_centre_1km": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_F1": {"type": "array", "shape": (2,)},
                        "cos_mu_centre_F1": {"type": "array", "shape": (2,)},
                        "cos_nu_centre_F1": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_500m": {"type": "array", "shape": (8,)},
                        "cos_mu_centre_500m": {"type": "array", "shape": (8,)},
                        "cos_nu_centre_500m": {"type": "array", "shape": (8,)},
                        "cos_lambda_centre_1km_OB": {"type": "array", "shape": (2,)},
                        "cos_mu_centre_1km_OB": {"type": "array", "shape": (2,)},
                        "cos_nu_centre_1km_OB": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_F1_OB": {"type": "array", "shape": (2,)},
                        "cos_mu_centre_F1_OB": {"type": "array", "shape": (2,)},
                        "cos_nu_centre_F1_OB": {"type": "array", "shape": (2,)},
                        "cos_lambda_centre_500m_OB": {"type": "array", "shape": (8,)},
                        "cos_mu_centre_500m_OB": {"type": "array", "shape": (8,)},
                        "cos_nu_centre_500m_OB": {"type": "array", "shape": (8,)},
                    },
                    "required": [
                        "scans_inclination_nadir",
                        "F1_scanangle_offset",
                        "X_misalignment_correction",
                        "Y_misalignment_correction",
                        "Z_misalignment_correction",
                        "X_misalignment_correction_OB",
                        "Y_misalignment_correction_OB",
                        "Z_misalignment_correction_OB",
                        "scans_mirror_offset",
                        "scans_cone_angle",
                        "cos_lambda_centre_1km",
                        "cos_mu_centre_1km",
                        "cos_nu_centre_1km",
                        "cos_lambda_centre_F1",
                        "cos_mu_centre_F1",
                        "cos_nu_centre_F1",
                        "cos_lambda_centre_500m",
                        "cos_mu_centre_500m",
                        "cos_nu_centre_500m",
                        "cos_lambda_centre_1km_OB",
                        "cos_mu_centre_1km_OB",
                        "cos_nu_centre_1km_OB",
                        "cos_lambda_centre_F1_OB",
                        "cos_mu_centre_F1_OB",
                        "cos_nu_centre_F1_OB",
                        "cos_lambda_centre_500m_OB",
                        "cos_mu_centre_500m_OB",
                        "cos_nu_centre_500m_OB",
                    ],
                },
            },
            "properties": {
                "sat": {"type": "string", "pattern": "^SENTINEL_3[A-C]?$"},
                "resources": {
                    "type": "object",
                    "properties": {
                        "geoid": DEM_DATASET_SCHEMA,
                        "dem_path": DEM_DATASET_SCHEMA,
                        "dem_type": {"type": "string"},
                    },
                    "required": ["dem_path", "dem_type"],
                },
                "orbit_aux_info": {"type": "object", "items": ORBIT_AUX_INFO_SCHEMA},
                "abs_orbit": {"type": "integer", "minimum": 0},
                "jd_anx": {"type": "number"},
                "thermoelastic": ThermoelasticModel.get_schema(2),
                "geometry_model": {"$ref": "#/definitions/slstr_geometry_model"},
                "sw_geocal": {"type": "integer", "minimum": 1, "maximum": 3},
                "enable_f1": {"type": "boolean"},
                "enable_stripe_b": {"type": "boolean"},
                "navatt": NAVATT_SCHEMA,
                "acquisition_times": {
                    "type": "object",
                    "properties": {
                        "NAD": {
                            "$ref": "#/definitions/slstr_time_array",
                        },
                        "OBL": {
                            "$ref": "#/definitions/slstr_time_array",
                        },
                        "reference": TIMESCALE_NAME_SCHEMA,
                        "pix10sync": {"type": "number"},
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                    },
                    "required": [
                        "NAD",
                        "OBL",
                    ],
                },
                "scan_encoder": {
                    "type": "object",
                    "properties": {
                        "NAD": {
                            "type": "object",
                            "properties": {
                                "1KM": {"$ref": "#/definitions/slstr_scan_encoder_array"},
                                "05KM": {"$ref": "#/definitions/slstr_scan_encoder_array"},
                            },
                            "required": ["1KM", "05KM"],
                        },
                        "OBL": {
                            "type": "object",
                            "properties": {
                                "1KM": {"$ref": "#/definitions/slstr_scan_encoder_array"},
                                "05KM": {"$ref": "#/definitions/slstr_scan_encoder_array"},
                            },
                            "required": ["1KM", "05KM"],
                        },
                    },
                    "required": ["NAD", "OBL"],
                },
                "eop": TimeReference.init_schema(),
                "models": {
                    "type": "object",
                    "properties": {
                        "propagation": {
                            "type": "object",
                            "description": "Settings passed to underlying PropagationModel",
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "required": [
                "sat",
                "orbit_aux_info",
                "resources",
                "geometry_model",
                "acquisition_times",
            ],
        }

    @staticmethod
    def group_to_resolution(group: str) -> int:
        """
        Convert spectral group to resolution (in meters)

        :param str group: Group name ("1KM"/"1KM_F1"/"05KM_A"/"05KM_B")
        :return: resolution in meters
        """
        output = 1000
        if group.startswith("05KM"):
            output = 500
        return output

    def compute_misalignment_rotation(self, geom_model: dict, view: str) -> np.ndarray:
        """
        Compute the misalignment matrix for a given view

        :param dict geom_model: Geometry model with keys "X_misalignment_correction", "Y_misalignment..."
        :param str view: View ("NAD"/"OBL")
        :return: 3x3 alignement matrix
        """
        assert view in self._view_list
        assert "X_misalignment_correction" in geom_model
        assert "Y_misalignment_correction" in geom_model
        assert "Z_misalignment_correction" in geom_model
        assert "X_misalignment_correction_OB" in geom_model
        assert "Y_misalignment_correction_OB" in geom_model
        assert "Z_misalignment_correction_OB" in geom_model

        if view == "NAD":
            xi_angle = geom_model["X_misalignment_correction"]
            eta_angle = geom_model["Y_misalignment_correction"]
            zeta_angle = geom_model["Z_misalignment_correction"]
        else:
            xi_angle = geom_model["X_misalignment_correction_OB"]
            eta_angle = geom_model["Y_misalignment_correction_OB"]
            zeta_angle = geom_model["Z_misalignment_correction_OB"]

        return np.deg2rad([xi_angle, eta_angle, zeta_angle])

    def subsample_scan_positions(
        self,
        scan_per_tp: int = 8,
    ) -> dict:
        """
        Subsample the scan position by taking the ANX as a time origin.

        :param str view: chosen view (NAD/OBL)
        :param int scan_per_tp: number of scans per tie point
        :return: tuple with:

            - tie point start index (with respect to time origin)
            - number of tie points
            - first scan tie point index (with respect to time origin)
            - time origin
            - time step between tie points
        """
        scan_info = {"NAD": {}, "OBL": {}}

        jd_anx = self.orbit_model.info["gps_anx"]

        time_first_scan = [
            self.config["acquisition_times"][view]["scan_times"]["offsets"][0] for view in self._view_list
        ]

        num_scan = [len(self.config["acquisition_times"][view]["scan_times"]["offsets"]) for view in self._view_list]
        delta_t_anx = [abs(time_first_scan[i] - jd_anx) for i, _ in enumerate(self._view_list)]
        delta_scan_anx = [
            int(delta_t_anx[i] / self._constants["scan_period_mjd"]) for i, _ in enumerate(self._view_list)
        ]

        # Take into account curvature and start the oblique TPix grid before
        tpix_margin = OBL_TP_MARGIN
        tp_first_scan, tp_last_scan = np.zeros(len(self._view_list)), np.zeros(len(self._view_list))

        # Compute also QC grids limits which are the same as nadir view
        if delta_scan_anx[0] >= 0:
            # Track tie points start at the ANX location
            # added +1 to last_tp to have one extra TP as margin
            last_tp = [
                math.ceil((num_scan[i] + delta_scan_anx[i]) / scan_per_tp) + 2 for i, _ in enumerate(self._view_list)
            ]
            track_n_tp = max(last_tp[0], last_tp[1])
            start_pos = 0
            # Compute nadir TPix grid
            tp_first_scan[0] = int(delta_scan_anx[0] / scan_per_tp)
            tp_last_scan[0] = last_tp[0] - 1
            # Start the oblique TPix grid tpix_margin TPs before, to take into account the curvature
            tp_first_scan[1] = int(delta_scan_anx[1] / scan_per_tp) - tpix_margin
            tp_first_scan[1] = max(0, tp_first_scan[1])
            tp_last_scan[1] = last_tp[1] - 1
        else:
            # QC Grids start before ANX location
            r_margin_scans = int(scan_per_tp - (-delta_scan_anx[0] % scan_per_tp))
            last_tp = [
                math.ceil((num_scan[i] + r_margin_scans) / scan_per_tp) + 2 for i, _ in enumerate(self._view_list)
            ]

            track_n_tp = max(last_tp[0], last_tp[1])
            start_pos = int((-delta_scan_anx[0] + r_margin_scans) / scan_per_tp)

            # TPix grid limits
            tp_first_scan[0] = 0
            tp_last_scan[0] = last_tp[0] - 1
            # Start the oblique TPix grid tpix_margin TPs before, to take into account the curvature
            tp_first_scan[1] = int((delta_scan_anx[1] - delta_scan_anx[0]) / scan_per_tp - tpix_margin)
            tp_first_scan[1] = max(0, tp_first_scan[1])
            tp_last_scan[1] = last_tp[1] - 1

        # QC grid limits (given by NADIR Tpix limits)
        qc_first_scan = tp_first_scan[0]
        qc_last_scan = tp_last_scan[0]
        num_times_tp_list = [int(tp_last_scan[i] - max(0, tp_first_scan[i])) + 1 for i, _ in enumerate(self._view_list)]

        for i, view in enumerate(self._view_list):
            scan_info[view]["tp_first_scan"] = int(tp_first_scan[i])
            scan_info[view]["tp_last_scan"] = int(tp_last_scan[i])

            end_pos = start_pos + num_times_tp_list[i] - 1
            delta_t_tp = scan_per_tp * self._constants["scan_period_mjd"]

            # filter times inside the orbit validity range
            valid_start_time, valid_end_time = (self.orbit_model.valid_range[0], self.orbit_model.valid_range[1])
            valid_start_pos = math.ceil((valid_start_time - jd_anx) / delta_t_tp)
            valid_end_pos = math.floor((valid_end_time - jd_anx) / delta_t_tp)

            start_pos = max(start_pos, valid_start_pos)
            end_pos = min(end_pos, valid_end_pos)

            # update number of tie points
            num_times_tp = end_pos - start_pos + 1
            scan_info[view]["num_times_tp"] = num_times_tp

        scan_info["jd_anx"] = jd_anx
        scan_info["start_pos"] = start_pos
        scan_info["delta_t_tp"] = delta_t_tp
        scan_info["track_n_tp"] = track_n_tp
        scan_info["qc_first_scan"] = int(qc_first_scan)
        scan_info["qc_last_scan"] = int(qc_last_scan)

        return scan_info

    def quasi_cartesian_grid(  # pylint: disable=too-many-positional-arguments
        self,
        ac_samples: int = 130,
        ac_center_position: int = 64,
        ac_resolution: float = 16000.0,
        scan_per_tp: int = 8,
        view: str = "NAD",
    ) -> GroundTrackGrid:
        """
        Generates the quasi-cartesian grid

        :param int ac_samples: number of across-track samples
        :param int ac_center_position: index of center position
        :param float ac_resolution: ground across-track resolution
        :param int scan_per_tp: number of scans per tie point
        :param str view: chosen view (NAD/OBL)
        :return: GroundTrackGrid object
        """
        assert view in self._view_list

        orbit_list = self.config["orbit_aux_info"]["orbit_state_vectors"]
        if "navatt" in self.config:
            orbit_list.append(self.config["navatt"]["orbit"])

        scan_info = self.subsample_scan_positions(scan_per_tp=scan_per_tp)

        assert scan_info["start_pos"] <= scan_info["qc_first_scan"]
        times = np.array(
            [
                scan_info["jd_anx"] + (ak - scan_info["start_pos"]) * scan_info["delta_t_tp"]
                for ak in range(scan_info["track_n_tp"])
            ]
        )

        config = {
            "sat": self.config["sat"],
            "orbits": orbit_list,
            "ac_samples": ac_samples,
            "ac_center_position": ac_center_position,
            "ac_resolution": ac_resolution,
            "times": {"offsets": times},
            "time_reference": self.config["acquisition_times"]["reference"],
            "time_origin": scan_info["jd_anx"],
            "qc_first_scan": scan_info["qc_first_scan"],
            "qc_last_scan": scan_info["qc_last_scan"],
        }
        if "eop" in self.config:
            config["eop"] = self.config["eop"]
        return GroundTrackGrid(**config)

    def tie_points_grid(  # pylint: disable=too-many-positional-arguments
        self,
        scan_per_tp: int = 8,
        num_ac_tie_nad: int = 101,
        num_ac_tie_obl: int = 40,
        pixel_tie_start_nad: int = 2260,
        pixel_tie_start_obl: int = 1066,
        int_p: int = 16,
    ):
        """
        Generates the tie points grid

        :param int scan_per_tp: Number of scans per tie point (along track resolution)
        :param int num_ac_tie_nad: number of across-track tie points for nadir view
        :param int num_ac_tie_obl: number of across-track tie points for oblique view
        :param int pixel_tie_start_nad: pixel absolute start position (at 1km resolution, nadir view)
        :param int pixel_tie_start_obl: pixel absolute start position (at 1km resolution, oblique view)
        :param int int_p: tie point pixel interval across-track (at 1km resolution)
        :return: an initialized S3SLSTRGeometry object
        """

        # copy configuration from original product
        tpix_config = copy.deepcopy(self.config)

        scan_info = self.subsample_scan_positions(scan_per_tp=scan_per_tp)

        for view in self._view_list:
            assert scan_info["start_pos"] <= scan_info[view]["tp_first_scan"]
            track_times_tp = [
                scan_info["jd_anx"] + (ak - scan_info["start_pos"]) * scan_info["delta_t_tp"]
                for ak in range(scan_info["track_n_tp"])
            ]
            tpix_config["acquisition_times"][view]["scan_times"]["offsets"] = np.array(
                [
                    track_times_tp[tpix_ak + scan_info[view]["tp_first_scan"]]
                    for tpix_ak in range(scan_info[view]["num_times_tp"])
                ],
            )

        tpix_config["acquisition_times"]["NAD"]["first_acquisition"] = [pixel_tie_start_nad]
        tpix_config["acquisition_times"]["NAD"]["nb_pixels"] = num_ac_tie_nad
        tpix_config["acquisition_times"]["NAD"]["step"] = int_p

        tpix_config["acquisition_times"]["OBL"]["first_acquisition"] = [pixel_tie_start_obl]
        tpix_config["acquisition_times"]["OBL"]["nb_pixels"] = num_ac_tie_obl
        tpix_config["acquisition_times"]["OBL"]["step"] = int_p

        # disable F1 on TPix
        tpix_config["enable_f1"] = False

        return S3SLSTRGeometry(**tpix_config)
