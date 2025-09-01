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

"""pyrugged Class Location"""

from enum import Enum, auto


class Location(Enum):
    """Enumerate for point location with respect to the interpolation grid of a tile.

    Elevations in a tile are interpolated using the four neighboring points
    in a grid: (i, j), (i+1, j), (i, j+1), (i+1), (j+1). This implies that a point
    can be interpolated only if the elevation for these four points is available
    in the tile. A consequence is that a point in the northernmost row (resp.
    easternmost column) miss neighboring points at row j+1 (resp. neighboring points
    at column i+1) and therefore cannot be interpolated.

    This enumerate represent the position of a point taking this off-by-one property
    into account, the value HAS_INTERPOLATION_NEIGHBORS correspond to points that
    do have the necessary four neightbors, whereas the other values correspond to points
    that are either completely outside of the tile or within the tile but in either the
    northernmost row or easternmost column.

    """

    # Location for points out of tile interpolation grid, in the South-West corner direction.
    SOUTH_WEST = auto()

    # Location for points out of tile interpolation grid, in the West edge direction.
    WEST = auto()

    # Location for points out of tile interpolation grid, in the North-West corner direction.
    # The point may still be in the tile, but in the northernmost row thus missing required
    # interpolation points.
    NORTH_WEST = auto()

    # Location for points out of tile interpolation grid, in the North edge direction.
    # The point may still be in the tile, but in the northernmost row thus missing required
    # interpolation points.
    NORTH = auto()

    # Location for points out of tile interpolation grid, in the North-East corner direction.
    # The point may still be in the tile, but either in the northernmost row or in the
    # easternmost column thus missing required interpolation points.
    NORTH_EAST = auto()

    # Location for points out of tile interpolation grid, in the East edge direction.
    # The point may still be in the tile, but in the easternmost column thus missing required
    # interpolation points.
    EAST = auto()

    # Location for points out of tile interpolation grid, in the South-East corner direction.
    # The point may still be in the tile, but in the easternmost column thus missing required
    # interpolation points.
    SOUTH_EAST = auto()

    # Location for points out of tile interpolation grid, in the South edge direction.
    SOUTH = auto()

    # Location for points that do have interpolation neighbors.
    # The value corresponds to points that can be interpolated using their four
    # neighboring points in the grid at indices (i, j), (i+1, j), (i, j+1), (i+1),
    # (j+1). This implies that these points are neither in the northernmost latitude
    # row nor in the easternmost longitude column.
    HAS_INTERPOLATION_NEIGHBORS = auto()
