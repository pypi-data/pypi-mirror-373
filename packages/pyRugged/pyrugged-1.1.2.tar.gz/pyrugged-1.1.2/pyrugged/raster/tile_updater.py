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
"""
Tile updater module
"""
from abc import ABCMeta, abstractmethod

from pyrugged.raster.simple_tile import SimpleTile


# pylint: disable=too-few-public-methods
class TileUpdater(metaclass=ABCMeta):
    """
    Tile updater abstract class
    """

    @abstractmethod
    def update_tile(self, latitude: float, longitude: float, tile: SimpleTile):
        """
        Update the tile according to the Digital Elevation Model.

        This method is the hook used by the PyRugged library to delegate
        Digital Elevation Model loading to user-provided mission-specific
        code. When this method is called, the specified SimpleTile
        is empty and must be updated by calling the set_geometry method
        once at the start of the method to set up the tile
        geometry, and then calling the set_elevation method
        once for each cell in the tile to set the
        cell elevation.

        The implementation must fulfill the requirements:
         *  The tiles must overlap each other by one cell (i.e. cells
            that belong to the northernmost row of one tile must also belong
            to the sourthernmost row of another tile and cells that
            belong to the easternmost column of one tile must also belong
            to the westernmost column of another tile).
         *  As elevations are interpolated within Digital Elevation Model
            cells using four cells at indices (kLat, kLon), (kLat+1, kLon),
            (kLat, kLon+1), (kLat+1, kLon+1). A point in the northernmost row
            (resp. easternmost column) miss neighboring points at row kLat+1
            (resp. neighboring points at column kLon+1) and therefore cannot
            be interpolated. The method should therefore select the northernmost
            tile if the specified latitude is in the overlapping row between two
            tiles, and it should select the easternmost tile if the specified
            longitude is in the overlapping column between two tiles. Failing
            to do so will trigger an error at caller level mentioning the missing
            required neighbors.
         *  The elevation at cells as set when calling the set_elevation method
            must be the elevation corresponding to the latitude
            (minLatitude + kLat * latitudeStep) and longitude
            (minLongitude + kLon * longitudeStep), where minLatitude,
            latitudeStep, minLongitude and longitudeStep
            correspond to the parameter of the set_geometry method call.

        Parameters
        ----------
            latitude: latitude that must be covered by the tile (rad)
            longitude: longitude that must be covered by the tile (rad)
            tile: tile to update
        """
