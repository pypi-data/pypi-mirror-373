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
Unit tests for Daffodil cython wrappers
"""

import os.path as osp

from asgard.core.logger import initialize
from asgard.wrappers.dfdl.s3_navatt import DFDL_LOGGER_NAME
from asgard.wrappers.dfdl.s3_navatt import File as NavattFile
from asgard.wrappers.dfdl.s3_slstr_slt import File as SLTFile
from asgard.wrappers.dfdl.s3_timestamp_annotation import File as TimestampFile

TEST_DIR = osp.dirname(__file__)

initialize(DFDL_LOGGER_NAME)

REF_OUT = {
    "primaryHeader": {
        "packetVersionNumber": 0,
        "packetType": 0,
        "dataFieldHeaderFlag": 1,
        "PID": 22,
        "PCAT": 9,
        "groupingFlags": 3,
        "sequenceCount": 9358,
        "packetLength": 189,
    },
    "secondaryHeader": {
        "spareBit": 0,
        "PUSversion": 1,
        "spare4Bit": 0,
        "servicePacketType": 3,
        "servicePacketSubType": 25,
        "destinationID": 0,
        "time": {"coarse": 1336436015, "fine": 0},
        "timeStatus": 1,
    },
    "sourceData": {
        "cswField": "0000003c",
        "PM_DAT_GNSS_TIME_VALIDITY_FLAG": "01",
        "PM_DAT_NAVATT_CORRELATION_PPS_OBT": {"coarse": 1336436014, "fine": 0},
        "PM_DAT_NAVATT_CORRELATION_GNSS_TIME": {"coarse": 1336436014, "fine": 0},
        "SPACECRAFT_CENTRAL_TIME": {"coarse": 1336436015, "fine": 0},
        "AO_DAT_I_POS_I_SC_EST_1": -2680.644208449979,
        "AO_DAT_I_POS_I_SC_EST_2": 67.72363615604914,
        "AO_DAT_I_POS_I_SC_EST_3": 6653.211820784164,
        "AO_DAT_I_VEL_I_SC_EST_1": 6.412703832529737,
        "AO_DAT_I_VEL_I_SC_EST_2": 2.8159282114372903,
        "AO_DAT_I_VEL_I_SC_EST_3": 2.549271217030736,
        "AO_DAT_Q_I_SC_EST_1": 0.18437452937663587,
        "AO_DAT_Q_I_SC_EST_2": -0.19967632167615282,
        "AO_DAT_Q_I_SC_EST_3": 0.9613897079060351,
        "AO_DAT_Q_I_SC_EST_4": -0.04318829715761147,
        "AO_DAT_SC_RATE_I_SC_EST_1": -2.5486927308200045e-05,
        "AO_DAT_SC_RATE_I_SC_EST_2": 0.0010339776673983358,
        "AO_DAT_SC_RATE_I_SC_EST_3": 6.79654926242634e-05,
        "AO_DAT_Q_SC_ERR_1": 0.9999999998964121,
        "AO_DAT_Q_SC_ERR_2": -3.915825412446894e-06,
        "AO_DAT_Q_SC_ERR_3": -1.3644408245593737e-05,
        "AO_DAT_Q_SC_ERR_4": 2.3815966147689577e-06,
        "AO_DAT_GDCMODEFLG": 4,
        "SPACECRAFT_MODE": 4,
        "AO_DAT_THRUST_FLG": 0,
        "AO_AJ_IP_OP_FLG": 0,
        "AO_DAT_GNSS_VALIDDATA_ITG": 1,
        "AO_DAT_NAVATT_ORBITNUMBER_EST_ITG": 158,
        "AO_DAT_NAVATT_OOP_EST_ITG": 830410604,
        "AO_DAT_NEWGNSSDATAFLG_ITG": 0,
    },
    "errorControl": 43492,
}


def test_navatt_small_file():
    """
    Unit test for NavattFile with a single paquet
    """
    path = osp.join(TEST_DIR, "resources/S3/NAT", "ISPData_single.dat")
    nav = NavattFile(path)

    assert len(nav) == 1
    # iterate on paquets
    res = list(nav)

    test_out = res[0]["measurements"]

    assert test_out["errorControl"] == REF_OUT["errorControl"]
    assert test_out["primaryHeader"]["sequenceCount"] == REF_OUT["primaryHeader"]["sequenceCount"]
    assert test_out["sourceData"]["cswField"] == REF_OUT["sourceData"]["cswField"]
    assert test_out["sourceData"]["AO_DAT_I_POS_I_SC_EST_2"] == REF_OUT["sourceData"]["AO_DAT_I_POS_I_SC_EST_2"]
    assert test_out["sourceData"]["AO_DAT_Q_I_SC_EST_3"] == REF_OUT["sourceData"]["AO_DAT_Q_I_SC_EST_3"]


def test_navatt_file():
    """
    Unit test for NavattFile with a complete dataset
    """
    path = osp.join(TEST_DIR, "resources/S3/NAT", "ISPData.dat")
    nav = NavattFile(path)

    assert len(nav) == 6141
    # iterate on paquets
    res = list(nav)

    assert len(res) == 6141
    test_out = res[0]["measurements"]

    assert test_out["errorControl"] == REF_OUT["errorControl"]
    assert test_out["primaryHeader"]["sequenceCount"] == REF_OUT["primaryHeader"]["sequenceCount"]
    assert test_out["sourceData"]["cswField"] == REF_OUT["sourceData"]["cswField"]
    assert test_out["sourceData"]["AO_DAT_I_POS_I_SC_EST_2"] == REF_OUT["sourceData"]["AO_DAT_I_POS_I_SC_EST_2"]
    assert test_out["sourceData"]["AO_DAT_Q_I_SC_EST_3"] == REF_OUT["sourceData"]["AO_DAT_Q_I_SC_EST_3"]


def test_s3_olci_efr_annotation_file():
    """
    Unit test for S3 OLCI ERR annotation file with a complete dataset
    """
    path = osp.join(TEST_DIR, "resources/S3/OLCI/EFR_20220513T003504", "ISPAnnotation.dat")
    annot = TimestampFile(path)

    print(len(annot))
    # iterate on paquets
    res = list(annot)

    # First frame
    assert res[0]["annotation"]["gpsTime"] == {
        "days": 8168,
        "seconds": 2122,
        "microseconds": 71836,
    }

    assert res[0]["annotation"]["gpsTime"] == res[1]["annotation"]["gpsTime"]
    assert res[0]["annotation"]["gpsTime"] == res[2]["annotation"]["gpsTime"]
    assert res[0]["annotation"]["gpsTime"] == res[3]["annotation"]["gpsTime"]
    assert res[0]["annotation"]["gpsTime"] == res[4]["annotation"]["gpsTime"]

    # Next frame
    assert res[5]["annotation"]["gpsTime"] == {
        "days": 8168,
        "seconds": 2122,
        "microseconds": 115836,
    }


def test_s3_slstr_slt_file_small():
    """
    Unit test for
    """
    path = osp.join(TEST_DIR, "resources/S3/SLSTR/SLT_20221101T204936/ISPData_x41.dat")
    slt = SLTFile(path)

    data = []
    for item in slt:
        data.append(item)

    assert len(data) == 41

    assert list(data[0]["isp"]["sourceData"]["data"].keys()) == ["hk"]
    assert list(data[1]["isp"]["sourceData"]["data"].keys()) == ["band"]
    assert list(data[-1]["isp"]["sourceData"]["data"].keys()) == ["scanpos"]
