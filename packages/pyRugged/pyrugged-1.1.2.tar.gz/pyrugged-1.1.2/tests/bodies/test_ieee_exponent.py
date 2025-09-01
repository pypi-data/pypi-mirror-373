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

"""Test for pyrugged method get_exponent"""

import numpy as np
from org.hipparchus.util import FastMath

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.utils.math_utils import get_exponent  # pylint: disable=no-name-in-module

init_orekit(use_internal_data=False)


def test_get_exponent_value():
    for i in np.arange(-1.0e5, 1.0e5):
        if float(i) == 0.0:
            continue
        assert get_exponent(float(i)) == FastMath.getExponent(float(i))
