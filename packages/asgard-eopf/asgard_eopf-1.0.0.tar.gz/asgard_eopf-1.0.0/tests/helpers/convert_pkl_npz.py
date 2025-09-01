#!/usr/bin/env python
# coding: utf8
#
# Copyright 2025 CS GROUP
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
Convert pkl to npz

WHY: dill seems verry slow and its codebase not production ready, many comments:
https://github.com/uqfoundation/dill/blob/0.4.0/dill/_dill.py#L431-L467

usage: python tests/helpers/convert_pkl_npz.py $ASGARD_DATA/S2MSIdataset/S2MSI_TDS*/s2geo_reference_grid_INVLOC_Full.pkl

PKL_FILE=/DATA/ASGARD_DATA/S2MSIdataset/S2MSI_TDS3/s2geo_reference_grid_INVLOC_Full.pkl
ls -lh ${PKL_FILE}*
... 791M Oct 31  2024 /DATA/ASGARD_DATA/S2MSIdataset/S2MSI_TDS3/s2geo_reference_grid_INVLOC_Full.pkl
... 646M Jun 16 07:57 /DATA/ASGARD_DATA/S2MSIdataset/S2MSI_TDS3/s2geo_reference_grid_INVLOC_Full.pkl.npz

time python3 -c"import numpy;numpy.load('${PKL_FILE}.npz')"
real    0m0,206s
user    0m1,113s
sys     0m0,056s

time python3 -c"import dill;dill.load(open('${PKL_FILE}', 'rb'))"
real    0m34,051s
user    0m29,654s
sys     0m4,395s

---> speedup = 165x
"""
import logging
from pathlib import Path

import dill  # type: ignore
import numpy as np


def load_dill_dict(ref_data_path: str | Path) -> dict:
    """load ref_data from dill pkl file"""
    assert str(ref_data_path).endswith(".pkl")
    logging.debug("load_dill_dict %s", ref_data_path)
    with open(ref_data_path, "rb") as file_pkl:
        return dill.load(file_pkl)


def convert_ref_data_pkl_to_npz(path_pkl: str | Path):
    """Convert dill pkl file to npz arry object, faster to load.
    Save several arrays into a single file in uncompressed .npz format.
    * https://numpy.org/doc/stable/reference/generated/numpy.savez.html
    `savez_compressed` uses ZIP_DEFLATED, gives poor perf, high CPU usage for low gain.
    """
    logging.info("convert_ref_data_pkl_to_npz %s", path_pkl)
    desstination = Path(f"{path_pkl!s}.npz")
    assert not desstination.exists(), f"{desstination} already exits"
    data = load_dill_dict(path_pkl)
    kwargs = {sensor: np.array(value["inverse_loc"]) for sensor, value in data.items() if sensor not in ["ref_time"]}
    np.savez(desstination, allow_pickle=False, ref_time=data["ref_time"], **kwargs)
    del data  # try to avoid leaks


def load_ref_data(ref_data_path_npz: str | Path):
    """load ref_data from numpy npz file"""
    logging.debug("load_ref_data %s", ref_data_path_npz)
    data: dict = np.load(ref_data_path_npz, allow_pickle=False)
    ref_data = {sensor: {"inverse_loc": value} for sensor, value in data.items() if sensor not in ["ref_time"]}
    ref_data["ref_time"] = data["ref_time"]
    return ref_data


def test_tds_keys_length(max_length: int = 92):
    """
    time python -c"import ...;test_tds_keys_length()"
    2025-06-23 15:11:50,410 DEBUG npz_test_keys.py:29 92 S2MSI_TDS1: KeysView(NpzFile
        '/data/asgard/S2MSIdataset/S2MSI_TDS1/s2geo_reference_grid_INVLOC_Full.pkl.npz'
        with keys: ref_time, B03/D03, B02/D03, B08/D03, B04/D03...)
    2025-06-23 15:11:50,415 INFO npz_test_keys.py:27 79 S2MSI_TDS2: KeysView(NpzFile
        '/data/asgard/S2MSIdataset/S2MSI_TDS2/s2geo_reference_grid_INVLOC_Full.pkl.npz'
        with keys: ref_time, B08/D04, B03/D04, B02/D04, B04/D04...)
    2025-06-23 15:11:50,420 INFO npz_test_keys.py:27 53 S2MSI_TDS3: KeysView(NpzFile
        '/data/asgard/S2MSIdataset/S2MSI_TDS3/s2geo_reference_grid_INVLOC_Full.pkl.npz'
        with keys: ref_time, B04/D09, B03/D09, B02/D09, B08/D09...)
    2025-06-23 15:11:50,426 DEBUG npz_test_keys.py:29 92 S2MSI_TDS4: KeysView(NpzFile
        '/data/asgard/S2MSIdataset/S2MSI_TDS4/s2geo_reference_grid_INVLOC_Full.pkl.npz'
        with keys: ref_time, B03/D01, B03/D02, B02/D01, B02/D02...)
    2025-06-23 15:11:50,432 DEBUG npz_test_keys.py:29 92 S2MSI_TDS5: KeysView(NpzFile
        '/data/asgard/S2MSIdataset/S2MSI_TDS5/s2geo_reference_grid_INVLOC_Full.pkl.npz'
        with keys: ref_time, B03/D03, B02/D03, B08/D03, B04/D03...)
    python npz_test_keys.py  2.08s user 0.05s system 941% cpu 0.226 total
    """
    import os

    base = Path(os.environ.get("ASGARD_DATA", "/data/asgard"), "S2MSIdataset")
    for tds in base.glob("S2MSI_TDS*/s2geo_reference_grid_INVLOC_Full.pkl.npz"):
        az: dict = np.load(tds)
        length = len(az.keys())
        if length < max_length:
            logging.info("%02i %s: %r", length, tds.parent.name, az.keys())
        else:
            logging.debug("%02i %s: %r", length, tds.parent.name, az.keys())


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(filename)s:%(lineno)i %(message)s")

    for path in sys.argv[1:]:
        if not Path(f"{path!s}.npz").exists():
            convert_ref_data_pkl_to_npz(path)
        else:
            logging.debug("%s.npz already exists", path)
