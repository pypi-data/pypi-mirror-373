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
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# pylint: disable=logging-fstring-interpolation
# +-> Ignore all pyint warning regarding the logging format used in this file, only!

"""
From the Gitlab CI/CD pipeline: download files and dirs from the S3 buckets.
"""
import logging
import os
import os.path as osp
import subprocess
import sys
import time
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import boto3

# The access keys are defined in Gitlab -> Settings -> CI/CD -> Variables


def download_one(bucket, folder, file, dest):
    """
    Download one file on S3 bucket with boto3.
    """
    key = osp.join(folder, file)
    dest_dir = osp.join(dest, folder)
    # assert (
    #     "/" not in file
    # ), f"Expect pure filenames, no path separators in file variable (={file} for {dest_dir})"
    assert osp.isdir(dest_dir), f"Expects the destination directory to exist ({dest_dir})"

    logging.debug("Downloading '%s' into '%s'", key, dest)
    bucket.download_file(key, osp.join(dest_dir, file))
    return "Success"


def _do_download_all_mt(bucket, folder, files, dest, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(download_one, bucket, folder, file, dest): file for file in files}

        for future in futures.as_completed(future_to_file):
            file = future_to_file[future]
            exception = future.exception()

            if not exception:
                yield file, future.result()
            else:
                yield file, exception


def download_all_mt(bucket, folder, files, dest, max_workers=4):
    """
    Download all requested files, in parallel.

    :param bucket: S3 bucket from which files are downloaded
    :param folder: Folder into which files are found (and need to be downloaded to).
                   Used for logging purposes only. ``folder`` path is expected to
                   already be part of the ``files`` to download.
    :param files:  List of files to download
    :param dest:   Root directory where files are downloaded to
    :param max_workers: Number max of workers to use in parallel
    """
    logging.info("Downloading all files from '%s' into '%s'", folder, dest)
    for file, result in _do_download_all_mt(bucket, "", files, dest, max_workers=max_workers):
        logging.debug("%s: download result: %s", file, result)


def unique_dirs(objects):
    dirs = {osp.dirname(str(o.key)) for o in objects}
    return dirs


def extract_archive(archive_path: str) -> bool:
    """
    Uncompress archive and remove it
    """

    archive_name = osp.basename(archive_path)
    archive_dir = osp.dirname(archive_path)

    if archive_name.endswith(".zip"):
        subprocess.run(["unzip", "-q", "-u", archive_name], cwd=archive_dir, check=True)
    elif archive_name.endswith(".tgz") or archive_name.endswith(".tar.gz"):
        subprocess.run(["tar", "-xzf", archive_name], cwd=archive_dir, check=True)
    else:
        return False

    # clean uncompressed archive
    subprocess.run(["rm", archive_name], cwd=archive_dir, check=True)
    return True


def _download_s3_dir(bucket, directory, destination):
    logging.debug(f"Checking files in {directory} and download them (sequentially) to {destination}")
    objects = bucket.objects.filter(Prefix=directory)
    dirs = unique_dirs(objects)
    for dir_ in dirs:
        logging.debug(f"mkdir({destination/dir_})")
        Path(destination / dir_).mkdir(parents=True, exist_ok=True)
    download_all_mt(bucket, directory, (o.key for o in objects), destination)
    # for o in objects:
    #     # logging.debug(f"Download from S3: {o} to {destination}")
    #     bucket.download_file(o.key, destination/str(o.key))


def _download_common(destination: Path, targets=None):
    """
    Download resources from "common" bucket.

    :param destination: Where the resource will be downloaded to
    :param targets:     Filter to specify which exact (file) resource will be downloaded.
                        Possible values are:
                        - None: download everything: files **AND** directories
                        - S3ASLSTRdataset: only S3ASLSTRdataset/*.zip, no directory
                        - S3AOLCIdataset: only S3AOLCIdataset/*.zip, no directory
    """
    s3_common = boto3.resource(
        service_name="s3",
        region_name="sbg",
        endpoint_url="https://s3.sbg.perf.cloud.ovh.net",
        aws_access_key_id=os.environ["S3_COMMON_ACCESS"],
        aws_secret_access_key=os.environ["S3_COMMON_SECRET"],
    )
    bucket = s3_common.Bucket("common")

    locations = {
        "S3ASLSTRdataset": (
            "" "S3A_SL_0_SLT____20221101T204936_20221101T205436_20221101T212249_0299_091_314______PS1_O_NR_004.SEN3.zip"
        ),
        "S3AOLCIdataset": (
            "" "S3__AX___DEM_AX_20000101T000000_20991231T235959_20151214T120000___________________MPC_O_AL_001.SEN3.tgz"
        ),
        "ADFdynamic": "S0__ADF_IERSB_19920101T000000_20220630T000000_20220701T101100.txt",
        "S1ASARdataset": "S1A_EW_RAW__0SDH_20221111T114657_20221111T114758_045846_057C1E_9592.SAFE.zip",
    }
    if targets is None:
        target_keys = list(locations.keys())
    elif isinstance(targets, str):
        target_keys = [targets]
    else:
        target_keys = targets

    for key in target_keys:
        logging.info(f"mkdir({destination/key})")
        (destination / key).mkdir(parents=True, exist_ok=True)

        location = osp.join(key, locations[key])
        logging.info(f"Download from S3/common: {location} into {destination}")
        bucket.download_file(location, destination / location)
        extract_archive(destination / location)

    if targets is not None:
        return

    location = "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240529T142617.zarr"
    _download_s3_dir(bucket, location, destination)

    location = "ADFstatic/S0__ADF_GEOI8_20000101T000000_21000101T000000_20240513T160103.zarr"
    _download_s3_dir(bucket, location, destination)


def _download_geolib_input(destination: Path):
    geolib_input = boto3.resource(
        service_name="s3",
        region_name="sbg",
        endpoint_url="https://s3.sbg.perf.cloud.ovh.net",
        aws_access_key_id=os.environ["S3_GEOLIB_INPUT_RO_ACCESS"],
        aws_secret_access_key=os.environ["S3_GEOLIB_INPUT_RO_SECRET"],
    )
    bucket = geolib_input.Bucket("geolib-input")

    for dir_ in ("S2MSIdataset",):
        (destination / dir_).mkdir(parents=True, exist_ok=True)
    location = "S2MSIdataset/S2MSIdataset_flat.tgz"
    logging.info(f"Download from S3: {location} to {destination}")
    bucket.download_file(location, destination / location)
    extract_archive(destination / location)

    location = osp.join("DEM_natif", "legacy", "GETASSE30")
    _download_s3_dir(bucket, location, destination)

    location = "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20230428T185052.zarr"
    _download_s3_dir(bucket, location, destination)

    location = "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240325T113307.zarr"
    _download_s3_dir(bucket, location, destination)

    locations = [
        "S2MSIdataset/S2PDGS-TC-IPF-V2-ORCH-N-017_L0U_JUPITER_S2A_DT35",
        "S2MSIdataset/S2MSI_TDS1",
        "S2MSIdataset/S2MSI_TDS2",
        "S2MSIdataset/S2MSI_TDS3",
        "S2MSIdataset/S2MSI_TDS4",
        "S2MSIdataset/S2MSI_TDS5",
    ]
    for location in locations:
        logging.info(f"Download from S3: {location} to {destination}")
        _download_s3_dir(bucket, location, destination)


def _download_validation_input(destination: Path):
    geolib_input = boto3.resource(
        service_name="s3",
        region_name="sbg",
        endpoint_url="https://s3.sbg.perf.cloud.ovh.net",
        aws_access_key_id=os.environ["S3_GEOLIB_INPUT_RO_ACCESS"],
        aws_secret_access_key=os.environ["S3_GEOLIB_INPUT_RO_SECRET"],
    )
    bucket = geolib_input.Bucket("geolib-input")

    locations = ["OLCI_validation", "OLCI_RAC_validation", "SLSTR_validation", "SRAL_validation", "MWR_validation"]

    for location in locations:
        _download_s3_dir(bucket, location, destination)

    olci_dirs = ["OLCI_TDS1", "OLCI_TDS2"]
    slstr_dirs = ["SLSTR_TDS1", "SLSTR_TDS2", "SLSTR_TDS3"]

    (destination / "S3AOLCIdataset").mkdir(parents=True, exist_ok=True)
    logging.info("Downloading directory OLCI_TDS* from 'S3AOLCIdataset' into '%s'", destination)
    for olci_dir in olci_dirs:
        _download_s3_dir(bucket, osp.join("S3AOLCIdataset", olci_dir), destination)

    (destination / "S3ASLSTRdataset").mkdir(parents=True, exist_ok=True)
    logging.info("Downloading directory SLSTR_TDS* from 'S3SLSTRdataset' into '%s'", destination)
    for slstr_dir in slstr_dirs:
        _download_s3_dir(bucket, osp.join("S3ASLSTRdataset", slstr_dir), destination)

    olci_files = {
        "S3A_OL_1_INS_AX_20201030T120000_20991231T235959_20220505T120000___________________MPC_O_AL_009.SEN3.tgz",
        "S3A_OL_1_CAL_AX_20230620T000000_20991231T235959_20230616T120000___________________MPC_O_AL_028.SEN3.tgz",
        "S3A_AX___OSF_AX_20160216T192404_99991231T235959_20220330T090651___________________EUM_O_AL_001.SEN3.tgz",
    }

    slstr_files = [
        "S3A_AX___FRO_AX_20221030T000000_20221109T000000_20221102T065450___________________EUM_O_AL_001.SEN3.zip",
        "S3A_SL_1_GEC_AX_20190101T000000_20991231T235959_20191010T120000___________________MPC_O_AL_009.SEN3.zip",
        "S3A_SL_1_GEO_AX_20160216T000000_20991231T235959_20190912T120000___________________MPC_O_AL_008.SEN3.zip",
        "S3A_SL_0_SLT____20221101T204936_20221101T205436_20221101T212249_0299_091_314______PS1_O_NR_004.SEN3.zip",
    ]

    sral_files = [
        "S3B_AX___FRO_AX_20200708T000000_20200718T000000_20200711T065100___________________EUM_O_AL_001.SEN3.zip"
    ]

    mwr_files = [
        "S3A_AX___FRO_AX_20221030T000000_20221109T000000_20221102T065450___________________EUM_O_AL_001.SEN3.zip",
        "S3A_MW___CHDNAX_20160216T000000_20991231T235959_20210929T120000___________________MPC_O_AL_005.SEN3.zip",
    ]

    (destination / "S3AOLCIdataset").mkdir(parents=True, exist_ok=True)
    logging.info("Downloading all files from 'S3AOLCIdataset' into '%s'", destination)
    for file in olci_files:
        loc = osp.join("S3AOLCIdataset", file)
        bucket.download_file(loc, destination / loc)
        extract_archive(destination / loc)

    (destination / "S3ASLSTRdataset").mkdir(parents=True, exist_ok=True)
    logging.info("Downloading all files from 'S3ASLSTRdataset' into '%s'", destination)
    for file in slstr_files:
        loc = osp.join("S3ASLSTRdataset", file)
        bucket.download_file(loc, destination / loc)
        extract_archive(destination / loc)

    (destination / "S3BSRALdataset").mkdir(parents=True, exist_ok=True)
    logging.info("Downloading all files from 'S3BSRALdataset' into '%s'", destination)
    for file in sral_files:
        loc = osp.join("S3BSRALdataset", file)
        bucket.download_file(loc, destination / loc)
        extract_archive(destination / loc)

    (destination / "S3AMWRdataset").mkdir(parents=True, exist_ok=True)
    logging.info("Downloading all files from 'S3AMWRdataset' into '%s'", destination)
    for file in mwr_files:
        loc = osp.join("S3AMWRdataset", file)
        bucket.download_file(loc, destination / loc)
        extract_archive(destination / loc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    # Download files into the current directory. They will be extracted by the gitlab CI.
    DESTINATION = Path(os.environ.get("ASGARD_DATA", "ASGARD_DATA"))
    logging.info("Downloading ASGARD data into %s", DESTINATION.absolute())
    start = time.time()

    # For the CI "build" stage
    if "build" in sys.argv:
        pass

    # For the CI "test" stage
    elif "test" in sys.argv:
        _download_common(DESTINATION)
        _download_geolib_input(DESTINATION)
        _download_validation_input(DESTINATION)

    # For the CI "test/dask" stage
    elif "S3AOLCIdataset" in sys.argv:
        _download_common(DESTINATION, "S3AOLCIdataset")
    end = time.time()
    logging.info(f"Finished S3 data retrieval in  {end-start}")
