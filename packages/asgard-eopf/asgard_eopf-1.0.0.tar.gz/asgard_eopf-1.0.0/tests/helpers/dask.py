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
Helper classes and function for ASGARD tests
"""

import logging
import os
from glob import glob

from distributed import Client, LocalCluster
from distributed.diagnostics.plugin import UploadDirectory


def clean_logs(config, nb_workers):
    """
    Clean all the log files.
    Meant to be called once, at startup
    """
    filenames = []
    for _, cfg in config["handlers"].items():
        if "filename" in cfg and "%" in cfg["filename"]:
            pattern = cfg["filename"] % ("worker-%s",)
            filenames += [pattern % (w,) for w in range(nb_workers)]


def setup_worker_logs(config, dask_worker):
    """
    Set-up the logger on Dask Worker.
    """
    d_logger = logging.getLogger("distributed.worker")
    r_logger = logging.getLogger()
    old_handlers = d_logger.handlers[:]

    for _, cfg in config.get("handlers", {}).items():
        if "filename" in cfg and "%" in cfg["filename"]:
            cfg["mode"] = "a"  # Make sure to not reset worker log file
            cfg["filename"] = cfg["filename"] % ("worker-" + str(dask_worker.name),)

    logging.config.dictConfig(config)

    # Restore old dask.distributed handlers, and inject them in root handler as well
    for hdlr in old_handlers:
        d_logger.addHandler(hdlr)
        r_logger.addHandler(hdlr)  # <-- this way we send asgard messages to dask channel

    # From now on, redirect stdout/stderr messages to asgard
    # Utils.RedirectStdToLogger(logging.getLogger('asgard'))


class DaskContext:
    """
    Custom context manager for :class:`dask.distributed.Client` +
    :class:`dask.distributed.LocalCluster` classes.

    :param config: Expects a dictionary with a ``nb_workers`` integer key.
    """

    def __init__(self, config):
        self.__client = None
        self.__cluster = None
        self.__config = config

    def __enter__(self):
        # clean_logs(self.__config['log_config'], self.__config.nb_workers)
        self.__cluster = LocalCluster(
            threads_per_worker=1,
            processes=True,
            n_workers=self.__config["nb_workers"],
            silence_logs=False,
        )
        self.__client = Client(self.__cluster)
        # TODO: copy asgard logger configuration to dask.distributed logger
        # Work around: Cannot pickle local object in lambda...
        # global the_config
        # the_config = self.__config
        # self.__client.register_worker_callbacks(
        #         lambda dask_worker: setup_worker_logs(the_config['log_config'], dask_worker))
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.__client:
            self.__client.close()
            self.__cluster.close()
            self.__client.shutdown()
        return False

    @property
    def cluster(self):
        """
        Return a :class:`dask.distributed.Cluster`
        """
        return self.__cluster

    @property
    def client(self):
        """
        Return a :class:`dask.distributed.Client`
        """
        return self.__client


class UploadAsgardData(UploadDirectory):
    """
    Worker plugin dedicated to upload ASGARD_DATA files.

    Note: We override :class:`distributed.diagnostics.plugin.UploadDirectory` as
    :method:`distributed.worker.Worker.register_worker_plugin` expects plugins named differently and helper source files
    are already uploaded directly with :class:`distributed.diagnostics.plugin.UploadDirectory`.

    :param path: Expected to point to ``$ASGARD_DATA``.
    """

    def __init__(self, path, **kwargs):
        super().__init__(path, update_path=False, **kwargs)
        self.abs_path = path

    async def setup(self, nanny):
        """
        Upload the ``$ASGARD_DATA`` archive, expand it, and move it to the right directory (expected to be exactly the
        same as on the client node.
        """
        logging.info("Uploading ASGARD_DATA to %s ...", self.abs_path)
        await super().setup(nanny)  # Important to make sure the extraction has finished...
        upload_path = os.path.join(nanny.local_directory, self.path)
        assert os.path.isdir(
            upload_path
        ), f"{upload_path} is not a directory; contain: -> {glob(nanny.local_directory+'/**/*', recursive=True)}"
        os.rename(upload_path, self.abs_path)
        logging.info("ASGARD_DATA: %s uploaded", self.abs_path)
