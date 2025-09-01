#!/usr/bin/env python
# coding: utf8
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
asgard module init file
"""

# Standard imports
import sys
from os import environ

# ** VERSION **
# pylint: disable=import-error,no-name-in-module

# Depending on python version get importlib standard lib or backported package
if sys.version_info[:2] >= (3, 8):
    # when python3 > 3.8
    from importlib.metadata import PackageNotFoundError  # pragma: no cover
    from importlib.metadata import version
else:
    from importlib_metadata import PackageNotFoundError  # pragma: no cover
    from importlib_metadata import version
# Get asgard package version (installed from setuptools_scm)
try:
    __version__ = version("asgard_eopf")
except PackageNotFoundError:
    __version__ = "unknown"  # pragma: no cover
finally:
    del version, PackageNotFoundError


ASGARD_VALIDATE_SCHEMAS = False
# Activate the schemas validation
if "ASGARD_DEBUG" in environ:
    ASGARD_VALIDATE_SCHEMAS = True
