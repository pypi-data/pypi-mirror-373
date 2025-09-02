#!/usr/bin/env python
# coding: utf8
# Copyright 2022-2024 CS GROUP
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
Orekit wrappers init file
"""

import os
import sys

from asgard.core.compat import resources_files

if "java.io" not in sys.modules:
    import orekit_jcc  # pylint: disable=unused-import # noqa : F401

_jcc_modules = [name for name in ["orekit_jcc", "sxgeo"] if name in sys.modules]
if len(_jcc_modules) > 1:
    raise RuntimeError(f"Several JCC modules imported, expect only one: {_jcc_modules}")
JCC_MODULE_NAME = _jcc_modules[0]
JCC_MODULE = sys.modules[JCC_MODULE_NAME]

if JCC_MODULE_NAME == "orekit_jcc":
    # expose binder
    from orekit_jcc.binder import *  # pylint: disable=unused-import # noqa : F401
elif JCC_MODULE_NAME == "sxgeo":
    # JCC bindinds come from sxgeo
    from sxgeo.binder import *  # pylint: disable=unused-import # noqa : F401

# Init the JVM (Java Virtual Machine) for the JCC bindings.
# With a GraalVM build, there is no real JVM behind but this call is still needed for JCC.

if not JCC_MODULE.getVMEnv():  # pylint: disable=no-member
    # VisualVM profiling options, if the env var is set.
    # In VisualVM, go to File -> Add JMX Connection -> enter: localhost:9090
    if "VISUAL_VM_OPTS" in os.environ:
        visual_vm_opts = [
            "-Dcom.sun.management.jmxremote.rmi.port=9090",
            "-Dcom.sun.management.jmxremote=true",
            "-Dcom.sun.management.jmxremote.port=9090",
            "-Dcom.sun.management.jmxremote.ssl=false",
            "-Dcom.sun.management.jmxremote.authenticate=false",
            "-Dcom.sun.management.jmxremote.local.only=false",
            "-Djava.rmi.server.hostname=localhost",
        ]
    else:
        visual_vm_opts = []

    # Init the Java Virtual Machine in debug mode if the JAVA_DEBUG_PORT env var is set, e.g. 5005
    try:
        JCC_MODULE.initVM(  # pylint: disable=no-member
            vmargs=[
                f"-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address={os.environ['JAVA_DEBUG_PORT']}",
                *visual_vm_opts,
            ]
        )
    except KeyError:
        JCC_MODULE.initVM(vmargs=[*visual_vm_opts])  # pylint: disable=no-member

    # Init orekit resource directory
    from java.io import File  # pylint: disable=import-error
    from org.orekit.data import (  # pylint: disable=import-error
        DataContext,
        DirectoryCrawler,
    )

    DataContext.getDefault().getDataProvidersManager().addProvider(
        DirectoryCrawler(File(str(resources_files(JCC_MODULE)) + "/resources/orekit-data"))
    )