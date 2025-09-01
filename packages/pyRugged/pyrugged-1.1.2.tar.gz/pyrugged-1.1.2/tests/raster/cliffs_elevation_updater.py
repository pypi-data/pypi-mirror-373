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

"""pyrugged Class CliffsElevationUpdater"""

# pylint: disable=too-few-public-methods
import numpy as np

from pyrugged.raster.tile_updater import TileUpdater


class CliffsElevationUpdater(TileUpdater):
    """Elevation Updater for pyrugged/raster tests"""

    def __init__(self, point_1, point_2, top, bottom, size, n_val):
        """Builds a new instance."""

        self.point_1 = point_1
        self.point_2 = point_2
        self.top = top
        self.bottom = bottom
        self.size = size
        self.n_val = n_val

    def update_tile(self, latitude, longitude, tile):
        """Updates raster tile."""

        step = self.size / (self.n_val - 1)
        min_latitude = self.size * float(np.floor(latitude / self.size))
        min_longitude = self.size * float(np.floor(longitude / self.size))
        x2_m_x1 = self.point_2[1] - self.point_1[1]
        y2_m_y1 = self.point_2[0] - self.point_1[0]
        tile.set_geometry(min_latitude, min_longitude, step, step, self.n_val, self.n_val)

        for i in range(self.n_val):
            cell_latitude = min_latitude + i * step
            for j in range(self.n_val):
                cell_longitude = min_longitude + j * step
                x_m_x1 = cell_longitude - self.point_1[1]
                y_m_y1 = cell_latitude - self.point_1[0]
                if y_m_y1 * x2_m_x1 > x_m_x1 * y2_m_y1:
                    # Left side of the point_1 to point_2 track
                    tile.set_elevation(i, j, self.top)

                else:
                    # Right side of the point_1 to point_2 track
                    tile.set_elevation(i, j, self.bottom)
