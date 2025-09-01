#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022 CS GROUP
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
Unit tests for Orekit wrappers ( through SXGeo for now)
"""

import logging
import os
import os.path as osp
import time

import dask.array as da  # pylint: disable=import-error,no-name-in-module
import numpy as np
import pytest
from distributed import Client, LocalCluster
from helpers.serde import repickle

# isort: off
# JCC initVM()
from asgard.wrappers.orekit import to_nio_view  # pylint: disable=wrong-import-order, no-name-in-module

# isort: on


# pylint: disable=ungrouped-imports
from drivers.sentinel_3_legacy import S3LegacyDriver

# pylint: disable=import-error, wrong-import-order
from java.util import Arrays as JArrays
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.data import DataContext
from org.orekit.time import AbsoluteDate
from org.orekit.tools import PVProcessor
from org.orekit.utils import (
    CartesianDerivativesFilter,
    IERSConventions,
    TimeStampedPVCoordinates,
    TimeStampedPVCoordinatesHermiteInterpolator,
)

from asgard.models.time import TimeReference, extract_date_time_components
from asgard.sensors.sentinel3 import S3OLCIGeometry
from asgard.wrappers.orekit.utils import get_data_context, get_orekit_resources

# Resources directory
TEST_DIR = osp.dirname(__file__)
RESOURCES = osp.join(TEST_DIR, "resources")

# ASGARD_DATA directory
ASGARD_DATA = os.environ.get("ASGARD_DATA", "/data/asgard")

# GETAS dem path
GETAS_PATH = osp.join(ASGARD_DATA, "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr")


def get_loaded_items(context: DataContext = None):
    """
    Return loaded items by Orekit

    :param context: data context to use, if None we use the default one from Orekit
    """

    current_context = context if (context is not None) else DataContext.getDefault()
    loaded_raw = current_context.getDataProvidersManager().getLoadedDataNames().toString()
    return [item.strip() for item in loaded_raw[1:-1].split(",")]


def test_setup_different_iers_bulletin():
    """
    Check if we can setup 2 different IERS bulletin.
    """
    first_bulletin = osp.join(
        ASGARD_DATA,
        "S2MSIdataset",
        "iers",
        "S2__OPER_AUX_UT1UTC_ADG__20220916T000000_V20220916T000000_20230915T000000.txt",
    )

    # first line GPS time : 2022-09-18T02:52:51.175593913
    context_1 = get_data_context(first_bulletin)

    utc_scale = context_1.getTimeScales().getUTC()
    ut1_scale = context_1.getTimeScales().getUT1(context_1.getFrames().getEOPHistory(IERSConventions.IERS_2010, True))

    dtc_in = extract_date_time_components("2022-09-18T02:52:51")
    abs_date = AbsoluteDate(dtc_in, utc_scale)

    dtc_out = abs_date.getComponents(ut1_scale)
    ut1utc_delta = dtc_out.offsetFrom(dtc_in)
    ref_delta = -0.00935
    assert abs(ut1utc_delta - ref_delta) < 0.001

    loaded_items = get_loaded_items(context_1)
    print(loaded_items)

    # second time : in 2009
    second_bulletin = osp.join(
        RESOURCES,
        "orekit",
        "IERS",
        "S2A_OPER_AUX_UT1UTC_CGS1_20091211T165851_V20091211T165851_20091211T165851.DBL",
    )

    context_2 = get_data_context(second_bulletin)

    utc_scale = context_2.getTimeScales().getUTC()
    ut1_scale = context_2.getTimeScales().getUT1(context_2.getFrames().getEOPHistory(IERSConventions.IERS_2010, True))

    dtc_in = extract_date_time_components("2009-11-30T10:23:04")
    abs_date = AbsoluteDate(dtc_in, utc_scale)

    dtc_out = abs_date.getComponents(ut1_scale)
    ut1utc_delta = dtc_out.offsetFrom(dtc_in)
    ref_delta = 0.14409
    assert abs(ut1utc_delta - ref_delta) < 0.001

    loaded_items = get_loaded_items(context_2)
    print(loaded_items)


@pytest.mark.pickle
def test_generic_product_pickle():
    """
    Unit test for TimeReference pickle/unpickle
    """
    # Read file contents and init the TimeReference instance
    iers_file = osp.join(
        ASGARD_DATA,
        "S2MSIdataset",
        "iers",
        "S2__OPER_AUX_UT1UTC_ADG__20220916T000000_V20220916T000000_20230915T000000.txt",
    )
    iers_data = S3LegacyDriver.read_iers_file(iers_file)
    orekit_data = osp.join(get_orekit_resources(), "resources", "orekit-data")
    tr = TimeReference(iers_bulletin_a=iers_data, orekit_data=orekit_data)
    repickled = repickle(tr)

    # Test equality
    tr_orekit_data, tr_iers_bulletin_a = get_loaded_items(tr.context)
    repickled_orekit_data, repickled_iers_bulletin_a = get_loaded_items(repickled.context)
    assert tr_orekit_data == repickled_orekit_data
    assert osp.dirname(tr_iers_bulletin_a) != osp.dirname(repickled_iers_bulletin_a)
    assert tr.__dict__["config"]["iers_bulletin_a"] == repickled.__dict__["config"]["iers_bulletin_a"]


@pytest.fixture(name="olci")  # (name="olci", scope="module")
def olci_product():
    """
    Fixture to initialize a S3OLCIGeometry with navatt
    """
    frames = {
        "offsets": np.array([8168.024560769051 + 0.000001 * k for k in range(100)], dtype="float64"),
    }

    navatt_gps = np.load(osp.join(TEST_DIR, "resources/sample_timestamps_gps.npy"))
    navatt_oop = np.load(osp.join(TEST_DIR, "resources/sample_oop.npy"))

    # Note: here we use inertial coordinates for orbit PV
    navatt_orb = S3LegacyDriver.read_orbit_file(osp.join(TEST_DIR, "resources/sample_orbit_eme2000.xml"))
    # Note: convertion to EOCFI convention not needed, already accounted in platform model
    navatt_att = S3LegacyDriver.read_attitude_file(osp.join(TEST_DIR, "resources/sample_attitude.xml"))
    # We set a common time scale for orbit and attitude -> GPS
    navatt_orb["time_ref"] = "GPS"
    navatt_att["times"]["GPS"] = navatt_orb["times"]["GPS"]
    navatt_att["time_ref"] = "GPS"

    # Read EOP data
    iers_data = S3LegacyDriver.read_iers_file(osp.join(TEST_DIR, "resources/bulletinb-413.txt"))

    orbit_file = osp.join(
        TEST_DIR,
        "resources/S3/FRO",
        "S3A_OPER_MPL_ORBRES_20220510T000000_20220520T000000_0001.EOF",
    )
    fro_20220510 = S3LegacyDriver.read_orbit_file(orbit_file)
    calibration_file = osp.join(TEST_DIR, "resources/S3/OLCI/CAL", "OL_1_CAL_AX.nc")
    pointing_vectors = S3LegacyDriver.olci_pointing_angles(calibration_file)
    thermoelastic = S3LegacyDriver.s3_thermoelastic_tables(calibration_file, group="thermoelastic_model_EO")

    config = {
        "eop": {
            "iers_bulletin_b": iers_data,
        },
        "sat": "SENTINEL_3",
        "orbit_aux_info": {
            "orbit_state_vectors": [fro_20220510],
        },
        "resources": {"dem_path": GETAS_PATH, "dem_type": "ZARR"},
        "pointing_vectors": pointing_vectors,
        "thermoelastic": thermoelastic,
        "frame": {"times": frames},
        "navatt": {
            "orbit": navatt_orb,
            "attitude": navatt_att,
            "times": {
                "offsets": navatt_gps,
                "ref": "GPS",
            },
            "oop": navatt_oop,
        },
    }

    return S3OLCIGeometry(**config)


@pytest.mark.pickle
def test_pickle_s3olcigeometry(olci):
    """
    Unit test for S3OLCIGeometry pickle/unpickle
    """
    repickled = repickle(olci)

    assert olci.__dict__.keys() == repickled.__dict__.keys()
    assert olci.coordinates == repickled.coordinates


@pytest.mark.slow
@pytest.mark.dask
@pytest.mark.dask_orekit
def test_direct_loc_with_a_local_dask_cluster(olci):
    """
    Unit test for S3OLCIGeometry.direct_loc with navatt data
    """
    img_coords = np.array(
        [[col, row] for row in np.linspace(0, 10, 5) for col in np.linspace(0, 10, 5)],
        np.int32,
    )

    # Direct location with Dask. Uses the same arguments as the local version.
    def direct_loc(olci, img_coords):
        loc_result = olci.direct_loc(img_coords, geometric_unit="C2")
        return loc_result[0][:, :2]

    nb_workers = 2
    chunks = 5
    with (
        LocalCluster(threads_per_worker=1, processes=True, n_workers=nb_workers, silence_logs=False) as cluster,
        Client(cluster) as dask_client,
    ):
        logging.info("Dask dashboard URL: %s", str(dask_client.dashboard_link))
        da_img_coords = da.from_array(img_coords, chunks=(chunks, 2))
        da_results = da.map_blocks(
            direct_loc,
            olci,
            da_img_coords,
            dtype="float64",
        )
        loc_result = da_results.compute()

        baseline_loc_result = np.asarray(
            [
                [141.12281313, 33.34639929],
                [141.13161906, 33.34503346],
                [141.14480504, 33.34298703],
                [141.15358201, 33.34162404],
                [141.16673919, 33.33957961],
                [141.12058833, 33.33624243],
                [141.12939321, 33.33487654],
                [141.14258073, 33.33282955],
                [141.15136041, 33.33146593],
                [141.16450917, 33.32942248],
            ]
        )
        assert np.allclose(loc_result[:10, :], baseline_loc_result, atol=1e-6)


def test_interpolate_batch_binder():
    """
    Test interpolate_batch() defined in orekit_tools with respect to interpolate_one_osv()
    """

    orbit_file = osp.join(
        TEST_DIR,
        "resources/S3/FRO",
        "S3A_OPER_MPL_ORBRES_20220510T000000_20220520T000000_0001.EOF",
    )
    fro_20220510 = S3LegacyDriver.read_orbit_file(orbit_file)

    time_processing = {}
    time_model = TimeReference()

    time_processing["offsets"] = fro_20220510["times"]["GPS"]["offsets"][:10]
    dates = list(time_model.to_dates(time_processing))
    positions = fro_20220510["positions"][:10]
    velocities = fro_20220510["velocities"][:10]

    pv_coords = [
        TimeStampedPVCoordinates(
            time,
            Vector3D(*position.tolist()),
            Vector3D(*velocity.tolist()),
        )
        for time, position, velocity in zip(dates, positions, velocities)
    ]

    nb_points = 1500
    shifts = np.linspace(0.0, 300.0, nb_points)  # shifts in seconds from the first sample time

    new_pos = np.zeros((nb_points, 3), dtype="float64")
    new_vel = np.zeros((nb_points, 3), dtype="float64")

    pv_processor = PVProcessor(pv_coords)
    perf = time.perf_counter()
    pv_processor.interpolate_batch(
        to_nio_view(shifts),
        to_nio_view(new_pos),
        to_nio_view(new_vel),
    )
    print(f"interpolate_batch duration : {time.perf_counter() - perf:.3g}")

    # Generate reference data
    ref_pos = np.zeros((nb_points, 3), dtype="float64")
    ref_vel = np.zeros((nb_points, 3), dtype="float64")
    first_date = dates[0]
    perf = time.perf_counter()
    for idx in range(nb_points):
        date = AbsoluteDate(first_date, float(shifts[idx]))
        pv_time_interpolator = TimeStampedPVCoordinatesHermiteInterpolator(
            min(
                JArrays.asList(pv_coords).size(),
                15,  # 15 => Maximum recommended by doc
            ),
            CartesianDerivativesFilter.USE_PV,
        )
        interpolated = pv_time_interpolator.interpolate(date, JArrays.asList(pv_coords))

        pos = interpolated.getPosition()
        vel = interpolated.getVelocity()
        ref_pos[idx, :] = [pos.getX(), pos.getY(), pos.getZ()]
        ref_vel[idx, :] = [vel.getX(), vel.getY(), vel.getZ()]

    print(f"Python loop duration : {time.perf_counter() - perf:.3g}")

    assert np.allclose(new_pos, ref_pos, rtol=0, atol=1e-6)
    assert np.allclose(new_vel, ref_vel, rtol=0, atol=1e-6)
