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

"""
ASGARD helper script that downloads patches the minimal set of (GETASSE) DEM files used in tests.
"""

import argparse
import logging
import os
import subprocess
import sys
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

import boto3
import botocore.exceptions

HELPERS_DIR = os.path.dirname(__file__)
DEM_BUCKET = "geolib-input"
DEM_REMOTE_DIR = (
    "S3AOLCIdataset/"
    + "S3__AX___DEM_AX_20000101T000000_20991231T235959_20151214T120000___________________MPC_O_AL_001.SEN3/"
)

# Run tests with "strace -e openat -f pytest ..." to know which test uses which GETASSE30 data
dem_files_used_by_tests = {
    "eocfi": [
        "AX___DEM_AX.EEF",
        "00N090W.GETASSE30",
        "15N090W.GETASSE30",
        "30N090W.GETASSE30",
        "45N090W.GETASSE30",
        "45N105W.GETASSE30",
        "75N045E.GETASSE30",
        "75N045W.GETASSE30",
        "75N135E.GETASSE30",
        "75N135W.GETASSE30",
        "90S045E.GETASSE30",
        "90S045W.GETASSE30",
        "90S135E.GETASSE30",
        "90S135W.GETASSE30",
    ],
    "olci": [
        "AX___DEM_AX.EEF",
        "15N060W.GETASSE30",
        "15N075W.GETASSE30",
        "15N135E.GETASSE30",
        "30N135E.GETASSE30",
        "30N150E.GETASSE30",
        "75N045E.GETASSE30",
        "75N045W.GETASSE30",
        "75N135E.GETASSE30",
        "75N135W.GETASSE30",
        "90S045E.GETASSE30",
        "90S045W.GETASSE30",
        "90S135E.GETASSE30",
        "90S135W.GETASSE30",
    ],
    "slstr": [
        "AX___DEM_AX.EEF",
        "00N000E.GETASSE30",
        "00N015E.GETASSE30",
        "00N030E.GETASSE30",
        "15N000E.GETASSE30",
        "15N015E.GETASSE30",
        "75N045E.GETASSE30",
        "75N045W.GETASSE30",
        "75N135E.GETASSE30",
        "75N135W.GETASSE30",
        "90S045E.GETASSE30",
        "90S045W.GETASSE30",
        "90S135E.GETASSE30",
        "90S135W.GETASSE30",
    ],
}


def download_one(client, bucket, folder, file, dest):
    """
    Download one file on S3 bucket with boto3.
    """
    key = os.path.join(folder, file)
    dest_dir = os.path.join(dest, folder)
    assert "/" not in file, f"Expect pure filenames, no path separators in file variable (={file})"
    assert os.path.isdir(dest_dir), f"Expects the destination directory to exist ({dest_dir})"

    logging.debug("Downloading '%s' into '%s'", key, dest)
    client.download_file(bucket, key, os.path.join(dest_dir, file))
    return "Success"


def download_all_sequential(client, bucket, folder, files, dest):
    """
    Download all requested files, sequentially.

    :param client: S3 client on which files are downloaded
    :param bucket: S3 bucket from which files are downloaded
    :param folder: Folder into which files are found (and need to be downloaded to)
    :param files:  List of files to download
    :param dest:   Root directory where files are downloaded to
    """
    logging.info("Downloading all files from '%s' into '%s'", folder, dest)
    for file in files:
        try:
            result = download_one(client, bucket, folder, file, dest)
            logging.info("%s: download result: %s", file, result)
        except botocore.exceptions.ClientError as error:
            logging.error("%s: download result: %s", file, error)


def _do_download_all_mt(client, bucket, folder, files, dest, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(download_one, client, bucket, folder, file, dest): file for file in files}

        for future in futures.as_completed(future_to_file):
            file = future_to_file[future]
            exception = future.exception()

            if not exception:
                yield file, future.result()
            else:
                yield file, exception


def download_all_mt(client, bucket, folder, files, dest, max_workers=4):
    """
    Download all requested files, in parallel.

    :param client: S3 client on which files are downloaded
    :param bucket: S3 bucket from which files are downloaded
    :param folder: Folder into which files are found (and need to be downloaded to)
    :param files:  List of files to download
    :param dest:   Root directory where files are downloaded to
    :param max_workers: Number max of workers to use in parallel
    """
    logging.info("Downloading all files from '%s' into '%s'", folder, dest)
    for file, result in _do_download_all_mt(client, bucket, folder, files, dest, max_workers=max_workers):
        logging.info("%s: download result: %s", file, result)


download_types = {
    "sequential": download_all_sequential,
    "mt": download_all_mt,  # download_all_mt is slightly faster
}


def _var_or_env(key, *args, **kwargs):
    """
    Internal helper function that returns in priority:

    1. kwargs[key] if it exists
    2. ${key} if it's defined
    3. Any optional parameter thats acts as a default value otherwise.
    """
    if key in kwargs:
        return kwargs[key]
    return os.environ.get(key, *args)


def download_dems(download_mode="mt", **kwargs):
    """
    Root function to download all DEM from S3 server.
    """
    s3_client = boto3.client(
        service_name="s3",
        region_name=_var_or_env("RCLONE_CONFIG_GEOLIB_INPUT_REGION", "sbg", **kwargs),
        # region_name="serco-dias1",
        endpoint_url="https://s3.sbg.perf.cloud.ovh.net",
        # Defined in Gitlab -> Settings -> CI/CD -> Variables
        aws_access_key_id=_var_or_env("RCLONE_CONFIG_GEOLIB_INPUT_ACCESS_KEY_ID", **kwargs),
        aws_secret_access_key=_var_or_env("RCLONE_CONFIG_GEOLIB_INPUT_SECRET_ACCESS_KEY", **kwargs),
    )
    # download_file() doesn't work w/o the list_objects_v2 if the region isn't set to sbg
    # (the region can be found by activating the logs, and executing first list_objects_v2)
    # boto3.set_stream_logger('', logging.DEBUG)
    # objects = s3.list_objects_v2(Bucket=bucket,)

    asgard_data = kwargs.get("asgard_data", os.environ["ASGARD_DATA"])
    dest_dir = f"{asgard_data}"
    os.makedirs(os.path.join(dest_dir, DEM_REMOTE_DIR), exist_ok=True)

    dem_groups = kwargs.get("dem_groups", "*")
    if dem_groups == "*":
        dem_files = set(sum(dem_files_used_by_tests.values(), []))
    else:
        assert isinstance(dem_groups, list)
        dem_files = set(sum([dem_files_used_by_tests[k] for k in dem_groups], []))

    logging.debug("Downloading: %s", dem_files)

    downloader = download_types[download_mode]
    downloader(s3_client, DEM_BUCKET, DEM_REMOTE_DIR, dem_files, dest_dir)

    # Fix the EEF file
    eef_fixer = os.path.join(HELPERS_DIR, "fix-EEF.sh")
    logging.info("$> %s", " ".join([eef_fixer, dest_dir]))
    subprocess.run([eef_fixer, dest_dir], check=True)
    logging.info("%s patched!", dem_files)


def _cli_parse():
    asgard_data = os.environ.get("ASGARD_DATA", None)
    parser = argparse.ArgumentParser(description="Download GETASSE DEM file from S3 server")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument(
        "ASGARD_DATA",
        type=str,
        nargs="?",
        default=asgard_data,
        help="Path to where ASGARD data (like DEM) are expected. Required when $ASGARD_DATA isn't set.",
    )
    parallel_group = parser.add_mutually_exclusive_group()
    parallel_group.add_argument("--seq", action="store_true", help="Download one file after the other")
    parallel_group.add_argument("--par", action="store_true", help="Download files in parallel")
    parser.add_argument(
        "--dem_groups",
        type=str,
        nargs="*",
        default="*",
        choices=dem_files_used_by_tests.keys(),
        help="Groups of DEM files to download depending on the identified tests. Default: all",
    )

    args = parser.parse_args()
    args.download_mode = "sequential" if args.seq else "mt"

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        boto3.set_stream_logger("", logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    logging.debug("ASGARD_DATA   = %s", args.ASGARD_DATA)
    logging.debug("Download mode = %s", args.download_mode)
    logging.debug("DEM groups    = %s", args.dem_groups)
    if not args.ASGARD_DATA:
        parser.error("ERROR: Please set $ASGARD_DATA or pass the equivalent value as parameter")
    return args


if __name__ == "__main__":
    try:
        params = _cli_parse()
        download_dems(
            download_mode=params.download_mode,
            asgard_data=params.ASGARD_DATA,
            dem_groups=params.dem_groups,
        )
    except (argparse.ArgumentTypeError, FileNotFoundError) as e:
        logging.error(e)
        sys.exit(127)
    finally:
        logging.shutdown()
