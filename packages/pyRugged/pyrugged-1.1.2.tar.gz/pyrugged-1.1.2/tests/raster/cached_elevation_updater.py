#!/usr/bin/env python
# coding: utf8
#
# Copyright 2024 CS GROUP
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

"""pyrugged Class CachedElevationUpdater"""

from typing import List

import numpy as np

from pyrugged.raster.location import Location
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.raster.tile_updater import TileUpdater


# pylint: disable="too-few-public-methods"
class CachedElevationUpdater(TileUpdater):
    """
    Tile updater based on internal cache
    """

    def __init__(self, tile_list: List[SimpleTile]):
        """
        Constructor
        """
        self._tiles = tile_list

    def update_tile(self, latitude, longitude, tile: SimpleTile):
        """
        Check among recorded tiles (like a cache)
        """
        for cached in self._tiles:
            if cached.get_location(latitude, longitude) == Location.HAS_INTERPOLATION_NEIGHBORS:
                tile.set_geometry(
                    cached.minimum_latitude,
                    cached.minimum_longitude,
                    cached.latitude_step,
                    cached.longitude_step,
                    cached.latitude_rows,
                    cached.longitude_columns,
                )
                cols, rows = np.meshgrid(np.arange(cached.longitude_columns), np.arange(cached.latitude_rows))
                elevation = cached.get_elevation_at_indices_arr(rows, cols)
                tile.set_elevation_block(elevation)
                return

        raise RuntimeError(f"No recorded tile to cover lat={np.degrees(latitude)}, lon={np.degrees(longitude)}")
