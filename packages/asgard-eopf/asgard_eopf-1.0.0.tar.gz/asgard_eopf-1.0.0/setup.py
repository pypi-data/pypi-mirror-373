#!/usr/bin/env python
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
# pylint: disable=C0412
"""
This setup.py file is needed to build cython extensions (dfdl and math).
The main configuration to build and install the package is done in the
pyproject.toml file.

If your run into the configuration error: `project.license` must be valid ...
* https://github.com/pypa/setuptools/issues/4903

Please do not run this file directly, use modern `pip wheel` or wheel's `build`.
They will install the package in an isolated environment, with the required
build-system dependencies.
* https://packaging.python.org/en/latest/discussions/setup-py-deprecated/
"""
import glob
import os
import shutil

from Cython.Build.Dependencies import cythonize
from setuptools import Extension, __version__, setup


# Check setuptools>=77 to support license expression (PEP-639)
# https://setuptools.pypa.io/en/latest/history.html#v77-0-0
# https://peps.python.org/pep-0639/#add-license-expression-field
if 77 > int(__version__[: __version__.index(".")]):
    raise ImportError(f"Please use `pip` to install. Unsupported setuptools {__version__} < 77")

# Check "python3.11/Python.h" for building cython extensions
# Give a hint if build fails in minimal environement
if not os.path.exists("/usr/include/python3.11/Python.h"):
    import warnings
    warnings.warn("Could not find 'Python.h' header file. Please install python3.11-dev for cython", stacklevel=3)

# Check & set GCC for building cython extensions
path_to_gcc = shutil.which("gcc")
if path_to_gcc is None:
    raise RuntimeError("Please install gcc")

os.environ["CC"] = path_to_gcc
os.environ["CFLAGS"] = "-pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -m64 -fopenmp"

# Setup dfdl and asgard.core.math binary extensions
# detect generated C files
generated_code = glob.glob("asgard/wrappers/dfdl/generated_*.c")
# create pyx files from template
pyx_files = [path.replace("/generated_", "/").replace(".c", ".pyx") for path in generated_code]
for path in pyx_files:
    shutil.copyfile("asgard/wrappers/dfdl/template.pyx", path)

# DFDL parser source files
common_source_files = [
    f"asgard/wrappers/dfdl/{filename}"
    for filename in [
        "errors.c",
        "infoset.c",
        "parsers.c",
        "unparsers.c",
        "validators.c",
    ]
]
# declare extensions
extensions = [
    Extension(pyx[:-4].replace("/", "."), [pyx, gen_c] + common_source_files)
    for pyx, gen_c in zip(pyx_files, generated_code)
] + [
    Extension(
        "asgard.core.math",
        ["asgard/core/math.pyx"],
        extra_compile_args=["-O3"],
    )
]

# Setup Cython extensions
setup(
    ext_modules=cythonize(
        extensions,
        include_path=["asgard/wrappers/dfdl"],
        annotate=True,
    )
)
