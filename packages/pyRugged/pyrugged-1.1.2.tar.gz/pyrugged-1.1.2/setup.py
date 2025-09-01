#!/usr/bin/env python
# Copyright 2022-2025 CS GROUP
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
setup.py builds cython extension, see `Cython.Build.cythonize`:
Compile a set of source modules into C/C++ files and return a list of distutils Extension objects for them.
"""
import numpy
from Cython.Build import cythonize
from setuptools import __version__, setup

# Check setuptools>=77 to support license expression (PEP-639)
# https://setuptools.pypa.io/en/latest/history.html#v77-0-0
# https://peps.python.org/pep-0639/#add-license-expression-field
if 77 > int(__version__[: __version__.index(".")]):
    raise ImportError(f"Please use `pip` to install. Unsupported setuptools {__version__} < 77")

# import Cython.Compiler.Options
# Cython.Compiler.Options.annotate = True
setup(
    use_scm_version=True,
    ext_modules=cythonize("pyrugged/utils/math_utils.pyx"),
    # ext_modules = cythonize("pyrugged/utils/math_utils.pyx", annotate=True),
    include_dirs=[numpy.get_include()],
    extra_compile_args=["-O3"],
)
