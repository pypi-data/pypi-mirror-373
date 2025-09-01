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
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""pyrugged  intersection helpers"""

import math

from pyrugged.errors.pyrugged_exception import PyRuggedError, PyRuggedInternalError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.basic_scan_algorithm import BasicScanAlgorithm
from pyrugged.intersection.constant_elevation_algorithm import ConstantElevationAlgorithm
from pyrugged.intersection.duvenhage.duvenhage_algorithm import DuvenhageAlgorithm
from pyrugged.intersection.ignore_dem_algorithm import IgnoreDEMAlgorithm
from pyrugged.raster.tile_updater import TileUpdater


def create_intersection_algorithm(
    algorithm_id: AlgorithmId,
    tile_updater: TileUpdater = None,
    max_cached_tiles: int = 8,
    constant_elevation: float = 0.0,
):
    """Create intersection algorithm.

    Parameters
    ----------
        algorithm_id : intersection algorithm identifier
        tile_updater : updater used to load Digital Elevation Model tiles
        max_cached_tiles : maximum number of tiles stored in the cache
        constant_elevation : constant elevation over ellipsoid

    Returns
    -------
        res: selected algorithm
    """

    if algorithm_id is None:
        raise PyRuggedError(PyRuggedMessages.INTERSECTION_ALGORITHM_ERROR.value, "algorithm Id is None")

    if algorithm_id == AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID:
        if math.isnan(constant_elevation):
            raise PyRuggedError(PyRuggedMessages.INTERSECTION_ALGORITHM_ERROR.value, "constant elevation is not set")

    elif algorithm_id != AlgorithmId.IGNORE_DEM_USE_ELLIPSOID:
        if tile_updater is None:
            raise PyRuggedError(PyRuggedMessages.INTERSECTION_ALGORITHM_ERROR.value, "dem without tile_updater")

    # Set up the algorithm
    if algorithm_id == AlgorithmId.DUVENHAGE:
        res = DuvenhageAlgorithm(tile_updater, max_cached_tiles, False)

    elif algorithm_id == AlgorithmId.DUVENHAGE_FLAT_BODY:
        res = DuvenhageAlgorithm(tile_updater, max_cached_tiles, True)

    elif algorithm_id == AlgorithmId.BASIC_SLOW_EXHAUSTIVE_SCAN_FOR_TESTS_ONLY:
        res = BasicScanAlgorithm(tile_updater, max_cached_tiles)

    elif algorithm_id == AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID:
        res = ConstantElevationAlgorithm(constant_elevation)

    elif algorithm_id == AlgorithmId.IGNORE_DEM_USE_ELLIPSOID:
        res = IgnoreDEMAlgorithm()

    else:
        raise PyRuggedInternalError

    return res
