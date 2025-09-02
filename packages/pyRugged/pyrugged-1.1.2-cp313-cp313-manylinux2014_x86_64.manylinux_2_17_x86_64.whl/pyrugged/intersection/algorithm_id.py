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

"""pyrugged Class AlgorithmId"""

from enum import Enum, auto


class AlgorithmId(Enum):
    """Enumerate for Digital Elevation Model intersection."""

    # Fast algorithm due to Bernardt Duvenhage.
    # The algorithm is described in the 2009 paper:
    # href="http://researchspace.csir.co.za/dspace/bitstream/10204/3041/1/Duvenhage_2009.pdf"
    # Using An Implicit Min/Max KD-Tree for Doing Efficient Terrain Line of Sight Calculations.
    DUVENHAGE = auto()

    # Fast algorithm due to Bernardt Duvenhage.
    # The algorithm is described in the 2009 paper:
    # href="http://researchspace.csir.co.za/dspace/bitstream/10204/3041/1/Duvenhage_2009.pdf"
    # Using An Implicit Min/Max KD-Tree for Doing Efficient Terrain Line of Sight Calculations.
    # This version of the duvenhage's algorithm considers the body to be flat, i.e. lines computed
    # from entry/exit points in the Digital Elevation Model are considered to be straight lines
    # also in geodetic coordinates. The sagitta resulting from real ellipsoid curvature is therefore
    # not corrected in this case. As this computation is not costly (a few percents overhead),
    # the full DUVENHAGE is recommended instead of this one. This choice is mainly intended
    # for comparison purposes with other systems.
    DUVENHAGE_FLAT_BODY = auto()

    # Basic, very slow algorithm, designed only for tests and validation purposes.
    # The algorithm simply computes entry and exit points at high and low altitudes,
    # and scans all Digital Elevation Models in the sub-tiles defined by these two
    # corner points. It is not designed for operational use.
    BASIC_SLOW_EXHAUSTIVE_SCAN_FOR_TESTS_ONLY = auto()

    # Algorithm that simply uses a constant elevation over ellipsoid.
    # Intersections are computed only with respect to the reference ellipsoid
    # and a user-specified elevation. If the user-specified elevation is 0.0,
    # then this algorithm is equivalent to IGNORE_DEM_USE_ELLIPSOID,
    # only slower.
    CONSTANT_ELEVATION_OVER_ELLIPSOID = auto()

    # Dummy algorithm that simply ignores the Digital Elevation Model.
    # Intersections are computed only with respect to the reference ellipsoid.
    # This algorithm is equivalent to CONSTANT_ELEVATION_OVER_ELLIPSOID
    # when the elevation is set to 0.0, but this one is much faster in this
    # specific case.
    IGNORE_DEM_USE_ELLIPSOID = auto()
