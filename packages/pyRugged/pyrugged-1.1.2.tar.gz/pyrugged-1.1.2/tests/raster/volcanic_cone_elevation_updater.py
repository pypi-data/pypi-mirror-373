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

"""pyrugged Class VolcanicConeElevationUpdater"""

# pylint: disable=too-few-public-methods
import numpy as np

from pyrugged.raster.tile_updater import TileUpdater
from pyrugged.utils.constants import Constants


class VolcanicConeElevationUpdater(TileUpdater):
    """Elevation Updater for pyrugged/raster tests"""

    def __init__(self, summit, slope, base, size, n_val):
        """builds a new instance."""

        self.summit = summit
        self.slope = slope
        self.base = base
        self.size = size
        self.n_val = n_val

    def update_tile(self, latitude, longitude, tile):
        """Updates raster tile."""

        step = self.size / (self.n_val - 1)
        min_latitude = self.size * float(np.floor(latitude / self.size))
        min_longitude = self.size * float(np.floor(longitude / self.size))
        sin_slope = float(np.sin(self.slope))
        tile.set_geometry(min_latitude, min_longitude, step, step, self.n_val, self.n_val)

        for i in range(self.n_val):
            cell_latitude = min_latitude + i * step
            for j in range(self.n_val):
                cell_longitude = min_longitude + j * step
                distance = Constants.WGS84_EARTH_EQUATORIAL_RADIUS * float(
                    np.hypot(cell_latitude - self.summit[0], cell_longitude - self.summit[1])
                )

                altitude = max(self.summit[2] - distance * sin_slope, self.base)

                tile.set_elevation(i, j, altitude)
