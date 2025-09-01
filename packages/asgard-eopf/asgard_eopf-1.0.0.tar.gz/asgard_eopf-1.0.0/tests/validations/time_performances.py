#!/usr/bin/env python
# coding: utf8
#
# Copyright 2024 CS GROUP
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
Runtime performance analysis between EOCFI, ASGARD-Legacy and ASGARD implementations
"""
import json
import os
import os.path as osp
from math import floor, log10
from typing import List, Optional

import numpy as np
from mdutils.mdutils import MdUtils  # type: ignore
from tomark import Tomark  # type: ignore

# Dictionary containing the time in milliseconds for each EOCFI functions that are used
# in the high level functions of ASGARD.
# This times have been recovered from the EOCFI documentation
# using the MACIN64 platform with the following caracteristics:
# OS ID: MACIN64
# Processor: Intel Core i7 4 cores @2.6GHz
# OS: MACOSX 10.12
# RAM: 16 GB

unit_time_dict_ms = {
    # ----- EOCFI INITIALISATION FUNCTIONS
    # "ee_lib.xl_model_init": None,
    "ee_lib.xl_time_ref_init_file": 1.100000,
    "ee_lib.xl_time_ref_init": 0.000520,
    "ee_orb.xo_orbit_init_file": 0.289000,
    # Satellite nominal attitude initialisation
    "ee_pnt.xp_sat_nominal_att_init_file": 0.350000,  # (5 quaternions)
    "ee_pnt.xp_sat_nominal_att_init_model": 0.000200,
    "ee_pnt.xp_sat_nominal_att_init": 0.000230,
    # Satellite attitude initialisation
    "ee_pnt.xp_sat_att_init_file": 0.360000,
    "ee_pnt.xp_sat_att_init_harmonic": 0.000300,
    "ee_pnt.xp_sat_att_matrix_init": 0.000000,
    "ee_pnt.xp_sat_att_angle_init": 0.000190,
    # Instrument attitude initialisation
    "ee_pnt.xp_instr_att_init_file": 0.340000,
    "ee_pnt.xp_instr_att_init_harmonic": 0.000200,
    "ee_pnt.xp_instr_att_matrix_init": 0.000700,
    "ee_pnt.xp_instr_att_angle_init": 0.000250,
    # Initialize with reference files/model id
    # "ee_lib.xl_time_ref_init_file": 1.100000,
    # ----- EOCFI FUNCTIONS FOR DIRECT LOCATION
    # "ee_orb.xo_orbit_id_clone": None,
    # "ee_pnt.xp_instr_att_matrix_init": 0.000700,
    "ee_pnt.xp_attitude_init": 0.002000,
    "ee_orb.xo_osv_compute": 0.005000,  # Interpolate orbit position -> xo_osv_compute*(INTERPOLATION)
    # "ee_pnt.xp_instr_att_set_matrix": None,
    "ee_pnt.xp_attitude_compute": 0.012000,  # (target frame: XP_INSTR_ATT)
    "ee_pnt.xp_target_inter": 0.006000,
    "ee_pnt.xp_target_inter[dem]": 0.037
    - 0.006700,  # (target_inter_with_dem+target_extra_main_with_dem)-target_extra_main_with_dem
    "ee_pnt.xp_target_extra_main": 0.006700,
    "ee_pnt.xp_target_extra_vector": 0.000205,  # (Take the one for 1st Derivates??)
    "ee_pnt.xp_target_extra_target_to_sun": 0.008000,  # called in condition "if sun_angles")
    "ee_pnt.xp_target_range": 0.008000,  # called for sar direct loc
    "ee_pnt.xp_target_ground_range": 0.018000,  # called for slstr direct loc in quasi-cartesian grid
    # ----- EOCFI FUNCTIONS FOR INCIDENCE ANGLES
    # "ee_orb.xo_orbit_id_clone": None,
    # "ee_orb.xo_osv_compute": 0.005000,
    "ee_lib.xl_cart_to_geod": 0.000380,  # time for mode = XL_CALC_NO_ITER_POS
    "ee_lib.xl_geod_to_cart": 0.000340,
    "ee_lib.xl_ef_to_topocentric": 0.001800,
    # ----- EOCFI FUNCTIONS FOR SUN ANGLES
    # earth.sun_position
    # "ee_orb.xo_orbit_id_clone": None,
    # "ee_pnt.xp_instr_att_matrix_init": 0.000700,
    # "ee_orb.xo_osv_compute": 0.005000,
    # "ee_pnt.xp_instr_att_set_matrix": None #called in condition "if override_instr_matrix == InstrMatrixMode.full"
    "ee_lib.xl_sun": 0.005000,
    "ee_pnt.xp_change_frame": 0.012000,
    # earth.change_coordinate_system
    # "ee_lib.xl_geod_to_cart": 0.000340,
    # earth.ef_to_topocentric
    # "ee_lib.xl_ef_to_topocentric": 0.001800,
}
# Eocfi unit time dictionary in seconds
unit_time_dict = {key: value * 1e-3 for key, value in unit_time_dict_ms.items()}

# Average execution time (in seconds) of both ASGARD and ASGARD-Legacy implementations for each function
# (direct_loc, sun_angles, incidence_angles)
# For each function, we created a runtime list with the following format:
# [runtime_asgard_legacy, runtime_asgard_refactored]
# ----- Characteristics of the machine on which ASGARD runtime computation have been done -----
# width: 64 bits
# capabilities: smp vsyscall32
# memory size: 32GiB
# cpu:  Intel(R) Core(TM) i5-8350U CPU @ 1.70GHz
#       vendor: Intel Corp.
#       physical id: 1
#       bus info: cpu@0
#       size: 3143MHz
#       capacity: 3600MHz
#       width: 64 bits

asgard_exec_time = {  # ASGARD high-level functions runtime in seconds
    # Sentinel-1
    "sar": {
        "direct_loc": [0.026879151662190754, 0.4470713933308919],  # [runtime_asgard_legacy, runtime_asgard_refactored]
        "viewing_angles": [0.008290449778238932, 0.02508695920308431],
        "incidence_angles": [0.006953318913777669, 0.02782273292541504],
    },
    # Sentinel-2
    "msi": {"direct_loc": [None, None], "sun_angles": [None, None], "incidence_angles": [None, None]},
    # Sentinel-3
    "olci": {
        "direct_loc_without_dem_loading": [54.293734365039406, 327.4403296046787],
        "direct_loc_with_dem_loading": [None, 6401.355311155319],
        "sun_angles": [32.19779422548082, 91.34878126780193],
        "incidence_angles": [3.5301633146074085, 94.64675916565788],
    },
    "slstr": {
        "direct_loc_instrument_grid": [432.62326796849567, 279.45421584447223],
        "direct_loc_quasi_cartesian_grid": [1.9046387672424316, 11.255908091862997],
        "sun_angles": [0.32182836532592773, 0.644728422164917],
        "incidence_angles": [1.0778845151265461, 1.2014420827229817],
    },
    "sral": {
        "direct_loc": [0.007329384485880534, 0.007917960484822592],
        "sun_angles": [0.0028831164042154946, 0.012561877568562826],
        "incidence_angles": [0.007616837819417317, 8.900960286458334e-06],
    },
    "mwr": {
        "direct_loc": [9.082114378611246, 6.349605162938436],
        "sun_angles": [0.5025909741719564, 2.128701686859131],
        "incidence_angles": [2.6972618897755942, 3.4212682247161865],
    },
}


def compute_init_function_time():
    """
    Runtime computation for initialisation functions
    """
    # return unit_time_dict["ee_lib.xl_time_ref_init"] * 1 + \
    # unit_time_dict["ee_orb.xo_orbit_init_file"] * 1 + \
    # unit_time_dict["ee_pnt.xp_sat_nominal_att_init"] * 1 + \
    # unit_time_dict["ee_pnt.xp_sat_att_init_file"] * 1 + \
    # unit_time_dict["ee_pnt.xp_instr_att_init_file "] * 1 + \
    # unit_time_dict["ee_lib.xl_model_init"] * 1 \


# pylint: disable=too-many-positional-arguments


# Performances of direct location for different instruments
def compute_s3_mwr_time_direct_loc(
    nb_frames: int,
    nb_pixels: int,
    nb_sensor: int,
    instr_name: str,
    export_to_json_and_visualize_data: bool,
    json_folder: str,
) -> Optional[float]:
    """
    Runtime computation for mwr direct location
    :param nb_frames: number of input times to use
    :param nb_pixels: number of input pixels
    :param nb_sensor: number of sensors for a given instrument
    :param instr_name: name of the current instrument
    :param export_to_json_and_visualize_data: boolean to export runtimes to json file and then visulaize them
    in a markdown table
    :param json_folder: folder to write the json file

    :return total_time: total runtime of the function
    """
    current_function = "direct_loc"

    computation_list = [
        {
            "name": "ee_orb.xo_osv_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_attitude_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_inter",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_extra_main",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
    ]

    unit_time_list = [unit_time_dict[x["name"]] for x in computation_list]
    call_tmp_list = [np.multiply([nb_frames, nb_pixels], x["nb_call_vector"][:2]) for x in computation_list]
    call_list = [np.prod(call_vector[call_vector != 0]) for call_vector in call_tmp_list]
    for i, computation in enumerate(computation_list):
        computation["nb_call"] = call_list[i]
        computation["total_function_time"] = unit_time_list[i] * call_list[i]

    # Compute total runtime
    total_time_per_sensor = sum([x["total_function_time"] for x in computation_list])  # pylint: disable=R1728
    total_time = total_time_per_sensor * nb_sensor

    # Export data to json
    if export_to_json_and_visualize_data:
        json_path = os.path.join(json_folder, instr_name + ".json")
        export_data_to_json(
            computation_list, json_path, total_time_per_sensor, total_time, current_function, nb_sensor, instr_name
        )

    return total_time


def compute_s3_sral_time_direct_loc(
    nb_frames: int,
    nb_pixels: int,
    nb_sensor: int,
    instr_name: str,
    export_to_json_and_visualize_data: bool,
    json_folder: str,
) -> Optional[float]:
    """
    Runtime computation for sral direct location

    :param nb_frames: number of input times to use
    :param nb_pixels: number of input pixels
    :param nb_sensor: number of sensors for a given instrument
    :param instr_name: name of the current instrument
    :param export_to_json_and_visualize_data: boolean to export runtimes to json file and then visulaize them
    in a markdown table
    :param json_folder: folder to write the json file

    :return total_time: total runtime of the function
    """
    current_function = "direct_loc"

    computation_list = [
        {
            "name": "ee_orb.xo_osv_compute",
            "nb_call_vector": [1, 0],  # [[do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_lib.xl_cart_to_geod",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
    ]

    unit_time_list = [unit_time_dict[x["name"]] for x in computation_list]
    call_tmp_list = [np.multiply([nb_frames, nb_pixels], x["nb_call_vector"][:2]) for x in computation_list]
    call_list = [np.prod(call_vector[call_vector != 0]) for call_vector in call_tmp_list]
    for i, computation in enumerate(computation_list):
        computation["nb_call"] = call_list[i]
        computation["total_function_time"] = unit_time_list[i] * call_list[i]

    # Compute total runtime
    total_time_per_sensor = sum([x["total_function_time"] for x in computation_list])  # pylint: disable=R1728
    total_time = total_time_per_sensor * nb_sensor

    # Export data to json
    if export_to_json_and_visualize_data:
        json_path = os.path.join(json_folder, instr_name + ".json")
        export_data_to_json(
            computation_list, json_path, total_time_per_sensor, total_time, current_function, nb_sensor, instr_name
        )

    return total_time


def compute_s3_olci_time_direct_loc(
    nb_frames: int,
    nb_pixels: int,
    nb_sensor: int,
    instr_name: str,
    export_to_json_and_visualize_data: bool,
    json_folder: str,
) -> Optional[float]:
    """
    Runtime computation for olci direct location

    :param nb_frames: number of input times to use
    :param nb_pixels: number of input pixels
    :param nb_sensor: number of sensors for a given instrument
    :param instr_name: name of the current instrument
    :param export_to_json_and_visualize_data: boolean to export runtimes to json file and then visulaize them
    in a markdown table
    :param json_folder: folder to write the json file

    :return total_time: total runtime of the function
    """
    current_function = "direct_loc"

    computation_list = [
        {
            "name": "ee_orb.xo_osv_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_attitude_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_inter[dem]",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_extra_main",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
    ]

    unit_time_list = [unit_time_dict[x["name"]] for x in computation_list]
    call_tmp_list = [np.multiply([nb_frames, nb_pixels], x["nb_call_vector"][:2]) for x in computation_list]
    call_list = [np.prod(call_vector[call_vector != 0]) for call_vector in call_tmp_list]
    for i, computation in enumerate(computation_list):
        computation["nb_call"] = call_list[i]
        computation["total_function_time"] = unit_time_list[i] * call_list[i]

    # Compute total runtime
    total_time_per_sensor = sum([x["total_function_time"] for x in computation_list])  # pylint: disable=R1728
    total_time = total_time_per_sensor * nb_sensor

    # Export data to json
    if export_to_json_and_visualize_data:
        json_path = os.path.join(json_folder, instr_name + ".json")
        export_data_to_json(
            computation_list, json_path, total_time_per_sensor, total_time, current_function, nb_sensor, instr_name
        )

    return total_time


def compute_s3_slstr_time_direct_loc(
    nb_frames: int,
    nb_pixels: int,
    nb_sensor: int,
    instr_name: str,
    export_to_json_and_visualize_data: bool,
    json_folder: str,
) -> Optional[float]:
    """
    Runtime computation for slstr direct location

    :param nb_frames: number of input times to use
    :param nb_pixels: number of input pixels
    :param nb_sensor: number of sensors for a given instrument
    :param instr_name: name of the current instrument
    :param export_to_json_and_visualize_data: boolean to export runtimes to json file and then visulaize them
    in a markdown table
    :param json_folder: folder to write the json file

    :return total_time: total runtime of the function
    """
    current_function = "direct_loc_instrument_grid"

    computation_list = [
        {
            "name": "ee_orb.xo_osv_compute",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_attitude_compute",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_inter[dem]",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_extra_main",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
    ]

    unit_time_list = [unit_time_dict[x["name"]] for x in computation_list]
    call_tmp_list = [np.multiply([nb_frames, nb_pixels], x["nb_call_vector"][:2]) for x in computation_list]
    call_list = [np.prod(call_vector[call_vector != 0]) for call_vector in call_tmp_list]
    for i, computation in enumerate(computation_list):
        computation["nb_call"] = call_list[i]
        computation["total_function_time"] = unit_time_list[i] * call_list[i]

    # Compute total runtime
    total_time_per_sensor = sum([x["total_function_time"] for x in computation_list])  # pylint: disable=R1728
    total_time = total_time_per_sensor * nb_sensor

    # Export data to json
    if export_to_json_and_visualize_data:
        json_path = os.path.join(json_folder, instr_name + ".json")
        export_data_to_json(
            computation_list, json_path, total_time_per_sensor, total_time, current_function, nb_sensor, instr_name
        )

    return total_time


def compute_s3_slstr_time_direct_loc_qc_grid(
    nb_frames: int,
    nb_pixels: int,
    nb_sensor: int,
    instr_name: str,
    export_to_json_and_visualize_data: bool,
    json_folder: str,
) -> Optional[float]:
    """
    Runtime computation for slstr direct location in quasi-cartesian grid context

    :param nb_frames: number of input times to use
    :param nb_pixels: number of input pixels
    :param nb_sensor: number of sensors for a given instrument
    :param instr_name: name of the current instrument
    :param export_to_json_and_visualize_data: boolean to export runtimes to json file and then visulaize them
    in a markdown table
    :param json_folder: folder to write the json file

    :return total_time: total runtime of the function
    """
    current_function = "direct_loc_quasi_cartesian_grid"

    computation_list = [
        {
            "name": "ee_orb.xo_osv_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_attitude_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_ground_range",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_extra_main",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
    ]

    unit_time_list = [unit_time_dict[x["name"]] for x in computation_list]
    call_tmp_list = [np.multiply([nb_frames, nb_pixels], x["nb_call_vector"][:2]) for x in computation_list]
    call_list = [np.prod(call_vector[call_vector != 0]) for call_vector in call_tmp_list]
    for i, computation in enumerate(computation_list):
        computation["nb_call"] = call_list[i]
        computation["total_function_time"] = unit_time_list[i] * call_list[i]

    # Compute total runtime
    total_time_per_sensor = sum([x["total_function_time"] for x in computation_list])  # pylint: disable=R1728
    total_time = total_time_per_sensor * nb_sensor

    # Export data to json
    if export_to_json_and_visualize_data:
        json_path = os.path.join(json_folder, instr_name + ".json")
        export_data_to_json(
            computation_list, json_path, total_time_per_sensor, total_time, current_function, nb_sensor, instr_name
        )

    return total_time


def compute_s2_msi_time_direct_loc():
    """
    Runtime computation for s2 msi direct location
    """
    return None


def compute_s1_sar_time_direct_loc(
    nb_frames: int,
    nb_pixels: int,
    nb_sensor: int,
    instr_name: str,
    export_to_json_and_visualize_data: bool,
    json_folder: str,
) -> Optional[float]:
    """
    Runtime computation for s1 sar direct location

    :param nb_frames: number of input times to use
    :param nb_pixels: number of input pixels
    :param nb_sensor: number of sensors for a given instrument
    :param instr_name: name of the current instrument
    :param export_to_json_and_visualize_data: boolean to export runtimes to json file and then visulaize them
    in a markdown table
    :param json_folder: folder to write the json file

    :return total_time: total runtime of the function
    """
    current_function = "direct_loc"

    computation_list = [
        {
            "name": "ee_orb.xo_osv_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_attitude_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_range",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_pnt.xp_target_extra_main",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
    ]

    unit_time_list = [unit_time_dict[x["name"]] for x in computation_list]
    call_tmp_list = [np.multiply([nb_frames, nb_pixels], x["nb_call_vector"][:2]) for x in computation_list]
    call_list = [np.prod(call_vector[call_vector != 0]) for call_vector in call_tmp_list]
    for i, computation in enumerate(computation_list):
        computation["nb_call"] = call_list[i]
        computation["total_function_time"] = unit_time_list[i] * call_list[i]

    # Compute total runtime
    total_time_per_sensor = sum([x["total_function_time"] for x in computation_list])  # pylint: disable=R1728
    total_time = total_time_per_sensor * nb_sensor

    # Export data to json
    if export_to_json_and_visualize_data:
        json_path = os.path.join(json_folder, instr_name + ".json")
        export_data_to_json(
            computation_list, json_path, total_time_per_sensor, total_time, current_function, nb_sensor, instr_name
        )

    return total_time


# Performances for incidence_angles function
def compute_time_incidence_angles(
    nb_frames: int,
    nb_pixels: int,
    nb_sensor: int,
    instr_name: str,
    export_to_json_and_visualize_data: bool,
    json_folder: str,
) -> Optional[float]:
    """
    Runtime computation for incidence_angles method

    :param nb_frames: number of input times to use
    :param nb_pixels: number of input pixels
    :param nb_sensor: number of sensors for a given instrument
    :param instr_name: name of the current instrument
    :param export_to_json_and_visualize_data: boolean to export runtimes to json file and then visulaize them
    in a markdown table
    :param json_folder: folder to write the json file

    :return total_time: total runtime of the function
    """
    current_function = "incidence_angles"

    computation_list = [
        {
            "name": "ee_orb.xo_osv_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_lib.xl_geod_to_cart",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_lib.xl_ef_to_topocentric",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
    ]
    unit_time_list = [unit_time_dict[x["name"]] for x in computation_list]

    call_tmp_list = [np.multiply([nb_frames, nb_pixels], x["nb_call_vector"][:2]) for x in computation_list]
    call_list = [np.prod(call_vector[call_vector != 0]) for call_vector in call_tmp_list]

    for i, computation in enumerate(computation_list):
        computation["nb_call"] = call_list[i]
        computation["total_function_time"] = unit_time_list[i] * call_list[i]

    # Compute total runtime
    total_time_per_sensor = sum([x["total_function_time"] for x in computation_list])  # pylint: disable=R1728
    total_time = total_time_per_sensor * nb_sensor

    # Export data to json
    if export_to_json_and_visualize_data:
        json_path = os.path.join(json_folder, instr_name + ".json")
        export_data_to_json(
            computation_list, json_path, total_time_per_sensor, total_time, current_function, nb_sensor, instr_name
        )

    return total_time


# Performances for sun_angles function
def compute_time_sun_angles(
    nb_frames: int,
    nb_pixels: int,
    nb_sensor: int,
    instr_name: str,
    export_to_json_and_visualize_data: bool,
    json_folder: str,
) -> Optional[float]:
    """
    Runtime computation for sun_angles method

    :param nb_frames: number of input times to use
    :param nb_pixels: number of input pixels
    :param nb_sensor: number of sensors for a given instrument
    :param instr_name: name of the current instrument
    :param export_to_json_and_visualize_data: boolean to export runtimes to json file and then visulaize them
    in a markdown table
    :param json_folder: folder to write the json file

    :return total_time: total runtime of the function
    """
    current_function = "sun_angles"

    computation_list = [
        {
            "name": "ee_lib.xl_sun",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_lib.xl_geod_to_cart",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_lib.xl_ef_to_topocentric",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
    ]
    unit_time_list = [unit_time_dict[x["name"]] for x in computation_list]

    call_tmp_list = [np.multiply([nb_frames, nb_pixels], x["nb_call_vector"][:2]) for x in computation_list]
    call_list = [np.prod(call_vector[call_vector != 0]) for call_vector in call_tmp_list]

    for i, computation in enumerate(computation_list):
        computation["nb_call"] = call_list[i]
        computation["total_function_time"] = unit_time_list[i] * call_list[i]

    # Compute total runtime
    total_time_per_sensor = sum([x["total_function_time"] for x in computation_list])  # pylint: disable=R1728
    total_time = total_time_per_sensor * nb_sensor

    # Export data to json
    if export_to_json_and_visualize_data:
        json_path = os.path.join(json_folder, instr_name + ".json")
        export_data_to_json(
            computation_list, json_path, total_time_per_sensor, total_time, current_function, nb_sensor, instr_name
        )

    return total_time


# Performances for viewing_angles function
def compute_time_viewing_angles(
    nb_frames: int,
    nb_pixels: int,
    nb_sensor: int,
    instr_name: str,
    export_to_json_and_visualize_data: bool,
    json_folder: str,
) -> Optional[float]:
    """
    Runtime computation for viewing_angles method

    :param nb_frames: number of input times to use
    :param nb_pixels: number of input pixels
    :param nb_sensor: number of sensors for a given instrument
    :param instr_name: name of the current instrument
    :param export_to_json_and_visualize_data: boolean to export runtimes to json file and then visulaize them
    in a markdown table
    :param json_folder: folder to write the json file

    :return total_time: total runtime of the function
    """
    current_function = "viewing_angles"

    computation_list = [
        {
            "name": "ee_orb.xo_osv_compute",
            "nb_call_vector": [1, 0],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_lib.xl_geod_to_cart",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
        {
            "name": "ee_lib.xl_ef_to_topocentric",
            "nb_call_vector": [1, 1],  # [do_multiply_by_nb_frames, do_multiply_by_nb_pixels]
        },
    ]
    unit_time_list = [unit_time_dict[x["name"]] for x in computation_list]

    call_tmp_list = [np.multiply([nb_frames, nb_pixels], x["nb_call_vector"][:2]) for x in computation_list]
    call_list = [np.prod(call_vector[call_vector != 0]) for call_vector in call_tmp_list]

    for i, computation in enumerate(computation_list):
        computation["nb_call"] = call_list[i]
        computation["total_function_time"] = unit_time_list[i] * call_list[i]

    # Compute total runtime
    total_time_per_sensor = sum([x["total_function_time"] for x in computation_list])  # pylint: disable=R1728
    total_time = total_time_per_sensor * nb_sensor

    # Export data to json
    if export_to_json_and_visualize_data:
        json_path = os.path.join(json_folder, instr_name + ".json")
        export_data_to_json(
            computation_list, json_path, total_time_per_sensor, total_time, current_function, nb_sensor, instr_name
        )

    return total_time


def sig_figs(x: float, precision: int):
    """
    Rounds a number to number of significant figures

    :param x: the number to be rounded
    :param precision: (integer) the number of significant figures

    :return: result of the rounding
    """
    return str(round(float(x), -int(floor(log10(abs(float(x))))) + (int(precision) - 1))) if x != "" else x


def export_data_to_json(  # pylint: disable=R0912
    computation_list: List,
    json_path: str,
    total_time_per_sensor: float,
    total_time: float,
    current_function: str,
    nb_sensor: int,
    instr_name: str,
):
    """
    Export runtime data for a specific function of a given instrument to a json file

    :param computation_list: list containing runtimes data for each called eocfi function
    :param json_path: path to write the json file
    :param total_time_per_sensor: total runtime per sensor
    :param total_time: total runtime
    :param current_function: current function on which we do the runtime analysis
    :param instr_name: name of the current instrument
    """

    results_precision = 4  # Number of significant figures to use for the results
    # Add dictionaries to sum all runtimes together
    computation_list += [
        {
            "name": "total_time_per_sensor",
            "nb_call_vector": "",
            "nb_call": "",
            "total_function_time": sig_figs(total_time_per_sensor, results_precision),
        },
        {
            "name": f"TOTAL_TIME (total_time_per_sensor x {nb_sensor})",
            "nb_call_vector": "",
            "nb_call": "",
            "total_function_time": sig_figs(total_time, results_precision),
        },
    ]

    # Add information of each EOCFI function in the table
    final_data_list = []
    for i, eocfi_function in enumerate(computation_list):

        call_str_list = ["nb_frames", "nb_pixels"]
        call_litteral_formula = ""
        for i, x in enumerate(eocfi_function["nb_call_vector"]):
            if x == 1:
                call_litteral_formula += " x " + call_str_list[i] if call_litteral_formula != "" else call_str_list[i]

        if eocfi_function["name"] in list(unit_time_dict.keys()):
            unit_time = unit_time_dict[eocfi_function["name"]]
        else:
            unit_time = ""

        # Write in bold for total runtimes
        if eocfi_function["name"] == "total_time_per_sensor" or "TOTAL_TIME" in eocfi_function["name"]:
            current_dict = {
                "EOCFI function name": f"**{eocfi_function['name']}**",
                "Unit time (seconds)": sig_figs(unit_time, results_precision),
                "Number of calls": "",
                "Total time (seconds)": f"**{sig_figs(eocfi_function['total_function_time'], results_precision)}**",
            }

        else:
            current_dict = {
                "EOCFI function name": eocfi_function["name"],
                "Unit time (seconds)": sig_figs(unit_time, results_precision),
                "Number of calls": (
                    call_litteral_formula + " = " + str(eocfi_function["nb_call"])
                    if eocfi_function["nb_call"] != ""
                    else ""
                ),
                "Total time (seconds)": sig_figs(eocfi_function["total_function_time"], results_precision),
            }

        final_data_list.append(current_dict)

    # Add a separator
    final_data_list.append({})

    # Add ASGARD-Legacy and ASGARD runtimes in the json file
    titles = ["ASGARD-Legacy runtime (one sensor)", "ASGARD runtime (one sensor)"]

    for index, title in enumerate(titles):
        # Handle slstr and olci cases
        if instr_name in ["slstr", "olci"] and current_function == "direct_loc":
            direct_loc_list = (
                ["_instrument_grid", "_quasi_cartesian_grid"]
                if instr_name == "slstr"
                else ["_without_dem_loading", "_with_dem_loading"]
            )
            for dl_type in direct_loc_list:
                if not (index == 0 and dl_type == "_with_dem_loading"):
                    current_dict = {
                        "EOCFI function name": f"**{title} {current_function}{dl_type}**",
                        "Unit time (seconds)": "",
                        "Number of calls": "",
                        "Total time (seconds)": sig_figs(
                            asgard_exec_time[instr_name][current_function + dl_type][index], results_precision
                        ),
                    }
                    final_data_list.append(current_dict)
        else:
            current_dict = {
                "EOCFI function name": f"**{title}**",
                "Unit time (seconds)": "",
                "Number of calls": "",
                "Total time (seconds)": sig_figs(
                    asgard_exec_time[instr_name][current_function][index], results_precision
                ),
            }
            final_data_list.append(current_dict)

    # Update json if already exists
    if os.path.isfile(json_path) and current_function != "direct_loc":
        with open(json_path, "r+", encoding="utf-8") as fp:  # pylint: disable=C0103
            try:
                json_data = json.load(fp)
            except ValueError as exp:
                raise TypeError("Cannot update an unvalid json file") from exp
            json_data[current_function] = final_data_list
            fp.seek(0)  # reset file position to the beginning
            json.dump(json_data, fp)
            fp.truncate()  # remove remaining part
    # Else create json file from scratch
    else:
        # Write the final dictionary to a Python file
        with open(json_path, "w", encoding="utf-8") as fp:  # pylint: disable=C0103
            json.dump({current_function: final_data_list}, fp)


def generate_markdown_from_json(json_path: str, md_path: str, nb_frames: int, nb_pixels: int, nb_sensor: int):
    """
    Generate a markdown performance table from the json data previously generated. If several json are
    given in input, the generated markdown table are concantenated in one markdown file


    Runtime computation for sun_angles method

    :param json_path: path to the input json file to read
    :param md_path: path to the output markdown file to write
    :param nb_frames: number of input times
    :param nb_pixels: number of pixels associated with the sensor
    :param nb_sensor: number of instruments
    """
    with open(json_path, encoding="utf-8") as json_file:
        runtime_dict = json.load(json_file)
        # Generate the structure of our markdown file
        md_file = MdUtils(
            file_name=md_path,
            title="EOCFI runtime analysis for " + json_path.split("/")[-1].replace(".json", "") + " instrument",
        )

        for key in list(runtime_dict.keys()):
            md_file.new_header(level=1, title="Runtime table for " + key, style="setext")
            md_file.new_line(
                "nb_sensor = " + str(nb_sensor) + ", nb_frames = " + str(nb_frames) + ", nb_pixels = " + str(nb_pixels)
            )
            md_file.new_line("\n")
            markdown = Tomark.table(runtime_dict[key])
            md_file.write(markdown)
            md_file.new_line("\n")

        md_file.create_md_file()


if __name__ == "__main__":

    EXPORT_TO_JSON_AND_VISUALIZE_DATA = True
    ASGARD_DIR = os.environ.get("asgard_dir", "")
    data_folder = osp.join(ASGARD_DIR, "tests", "validations", "time_performance_data")

    if not osp.exists(data_folder):
        os.makedirs(data_folder, exist_ok=True)

    # ----------- OLCI runtime
    NB_SENSOR, NB_FRAMES, NB_PIXELS = 5, 2731, 740
    INSTR_NAME = "olci"
    direct_loc_olci = compute_s3_olci_time_direct_loc(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    incidence_angles_olci = compute_time_incidence_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    sun_angles_olci = compute_time_sun_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )

    common_path = osp.join(ASGARD_DIR, "time_performance_data", INSTR_NAME)
    JSON_PATH = osp.join(data_folder, INSTR_NAME + ".json")
    markdown_path = osp.join(data_folder, INSTR_NAME + ".md")
    generate_markdown_from_json(JSON_PATH, markdown_path, NB_FRAMES, NB_PIXELS, NB_SENSOR)
    print(
        f"OLCI: runtime direct_loc = {direct_loc_olci} sec, incidence_angles = {incidence_angles_olci} sec,"
        f" sun_angles = {sun_angles_olci} sec"
    )

    # ----------- SRAL runtime
    NB_SENSOR, NB_FRAMES, NB_PIXELS = 1, 120, 1
    INSTR_NAME = "sral"
    direct_loc_sral = compute_s3_sral_time_direct_loc(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    incidence_angles_sral = compute_time_incidence_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    sun_angles_sral = compute_time_sun_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )

    common_path = osp.join(ASGARD_DIR, "time_performance_data", INSTR_NAME)
    JSON_PATH = osp.join(data_folder, INSTR_NAME + ".json")
    markdown_path = osp.join(data_folder, INSTR_NAME + ".md")
    generate_markdown_from_json(JSON_PATH, markdown_path, NB_FRAMES, NB_PIXELS, NB_SENSOR)
    print(
        f"SRAL: runtime direct_loc = {direct_loc_sral} sec, incidence_angles = {incidence_angles_sral} sec,"
        f" sun_angles = {sun_angles_sral} sec"
    )

    # ----------- MWR runtime
    NB_SENSOR, NB_FRAMES, NB_PIXELS = 2, 39057, 1
    INSTR_NAME = "mwr"
    direct_loc_mwr = compute_s3_mwr_time_direct_loc(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    incidence_angles_mwr = compute_time_incidence_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    sun_angles_mwr = compute_time_sun_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )

    common_path = osp.join(ASGARD_DIR, "time_performance_data", INSTR_NAME)
    JSON_PATH = osp.join(data_folder, INSTR_NAME + ".json")
    markdown_path = osp.join(data_folder, INSTR_NAME + ".md")
    generate_markdown_from_json(JSON_PATH, markdown_path, NB_FRAMES, NB_PIXELS, NB_SENSOR)
    print(
        f"MWR: runtime direct_loc = {direct_loc_mwr} sec, incidence_angles = {incidence_angles_mwr} sec,"
        f" sun_angles = {sun_angles_mwr} sec"
    )

    # ----------- SLSTR instrument grid runtime
    NB_SENSOR, NB_FRAMES, NB_PIXELS = 1, 902, 1199
    INSTR_NAME = "slstr"
    direct_loc_slstr = compute_s3_slstr_time_direct_loc(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    incidence_angles_slstr = compute_time_incidence_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    sun_angles_slstr = compute_time_sun_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    common_path = osp.join(ASGARD_DIR, "time_performance_data", INSTR_NAME)
    JSON_PATH = osp.join(data_folder, INSTR_NAME + ".json")
    markdown_path = osp.join(data_folder, INSTR_NAME + ".md")
    generate_markdown_from_json(JSON_PATH, markdown_path, NB_FRAMES, NB_PIXELS, NB_SENSOR)
    print(
        f"SLSTR instrument grid : runtime direct_loc = {direct_loc_slstr} sec,"
        f"incidence_angles = {incidence_angles_slstr} sec, sun_angles = {sun_angles_slstr} sec"
    )

    # ----------- SLSTR Quasi-cartesian grid runtime
    NB_SENSOR, NB_FRAMES, NB_PIXELS = 1, 115, 130
    INSTR_NAME = "slstr"
    direct_loc_slstr = compute_s3_slstr_time_direct_loc_qc_grid(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    common_path = osp.join(ASGARD_DIR, "time_performance_data", INSTR_NAME)
    JSON_PATH = osp.join(data_folder, INSTR_NAME + ".json")
    markdown_path = osp.join(data_folder, INSTR_NAME + ".md")
    generate_markdown_from_json(JSON_PATH, markdown_path, NB_FRAMES, NB_PIXELS, NB_SENSOR)
    print(f"SLSTR quasi-cartesian grid: runtime direct_loc = {direct_loc_slstr} sec")

    # ----------- SAR runtime
    NB_SENSOR, NB_FRAMES, NB_PIXELS = 1, 21, 22
    INSTR_NAME = "sar"
    direct_loc_sar = compute_s1_sar_time_direct_loc(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )  # pylint: disable=E1121
    incidence_angles_sar = compute_time_incidence_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )
    viewing_angles_sar = compute_time_viewing_angles(  # pylint: disable=E1121
        NB_FRAMES, NB_PIXELS, NB_SENSOR, INSTR_NAME, EXPORT_TO_JSON_AND_VISUALIZE_DATA, data_folder
    )

    common_path = osp.join(ASGARD_DIR, "time_performance_data", INSTR_NAME)
    JSON_PATH = osp.join(data_folder, INSTR_NAME + ".json")
    markdown_path = osp.join(data_folder, INSTR_NAME + ".md")
    generate_markdown_from_json(JSON_PATH, markdown_path, NB_FRAMES, NB_PIXELS, NB_SENSOR)
    print(
        f"SAR: runtime direct_loc = {direct_loc_sar} sec, incidence_angles ="
        f" {incidence_angles_sar} sec, viewing_angles = {viewing_angles_sar} sec"
    )
