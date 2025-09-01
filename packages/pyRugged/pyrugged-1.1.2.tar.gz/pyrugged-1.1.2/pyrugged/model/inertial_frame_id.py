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

"""pyrugged Class InertialFrameId"""

from enum import Enum, auto


class InertialFrameId(Enum):
    """Enumerate for inertial frames."""

    # Constant for Geocentric Celestial Reference Frame.
    GCRF = auto()

    # Constant for Earth Mean Equator 2000 frame (aka J2000).
    EME2000 = auto()

    # Constant for Mean Of Date frame, with IERS 96 conventions (Lieske precession).
    MOD = auto()

    # Constant for True Of Date frame, with IERS 96 conventions (Wahr nutation).
    TOD = auto()

    # Constant for Veis 1950 frame.
    VEIS1950 = auto()
