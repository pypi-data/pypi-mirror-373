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

"""pyrugged Class EllipsoidId"""

from enum import Enum, auto


class EllipsoidId(Enum):
    """Enumerate for ellipsoid."""

    # Constant for GRS 80 ellipsoid.
    GRS80 = auto()

    # Constant for WGS 84 ellipsoid.
    WGS84 = auto()

    # Constant for IERS 96 ellipsoid.
    IERS96 = auto()

    # Constant for IERS 2003 ellipsoid.
    IERS2003 = auto()
