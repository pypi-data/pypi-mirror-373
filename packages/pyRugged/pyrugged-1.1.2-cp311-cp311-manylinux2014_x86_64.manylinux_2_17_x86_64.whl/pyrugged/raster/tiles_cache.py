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

"""pyrugged Class TilesCache"""

from typing import List, Type, Union

# pylint: disable=import-error, too-few-public-methods
import numpy as np

from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.raster.location import Location
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.raster.tile_updater import TileUpdater


class TilesCache:
    """Cache for Digital Elevation Model tiles."""

    def __init__(
        self,
        tile: Type,
        updater: TileUpdater,
        max_tiles: int,
    ):
        """Builds a new instance.

        Parameters
        ----------
            tile : tile class to use
            updater : updater for retrieving tiles data
            max_tiles : maximum number of tiles stored simultaneously in the cache
        """

        self._tile_constructor = tile
        self._updater = updater
        self._tiles = [None] * max_tiles

    @property
    def tiles_count(self) -> int:
        """
        get number of tiles in cache
        """
        return sum(tile is not None for tile in self._tiles)

    def is_tile_in_cache(self, latitude: float, longitude: float) -> Union[int, None]:
        """
        Check if a tile in the cache covers the requested ground point and retrieve its position in the cache

        Parameters
        ----------
            latitude: Ground point latitude
            longitude: Ground point longitude
        Returns
        -------
            tile index in cache or None if no tile contains the point
        """
        for index, tile in enumerate(self._tiles):
            if tile is not None and tile.get_location(latitude, longitude) == Location.HAS_INTERPOLATION_NEIGHBORS:
                # We have found the tile in the cache

                # Put it on the front as it becomes the most recently used
                return index

        # no tile contains the point
        return None

    def are_tiles_in_cache_arr(self, latitudes: np.ndarray, longitudes: np.ndarray) -> dict:
        """
        Check if tiles in the cache cover the requested ground points and retrieve their positions in the cache

        Parameters
        ----------
            latitudes: Ground point latitudes
            longitudes: Ground point longitudes
        Returns
        -------
            tile indexes in cache or None if no tile contains the point
        """
        indexes = {}

        # avoid nan, and prevent points from being reported in 2 tiles
        status = np.isfinite(latitudes)
        ind_ok = np.where(status)[0]
        for index, tile in enumerate(self._tiles):
            if tile is not None:
                _, ind_has_neighbors = tile.get_location_arr(latitudes[ind_ok], longitudes[ind_ok])
                if len(ind_has_neighbors) > 0:
                    original_indexes = ind_ok[ind_has_neighbors]
                    indexes[index] = original_indexes
                    # disable recorded points
                    status[original_indexes] = False
                    ind_ok = np.where(status)[0]

        if len(indexes) == 0:
            return None

        return indexes

    def get_tiles(
        self, latitudes: np.ndarray, longitudes: np.ndarray, complete_tile=True
    ) -> (List[SimpleTile], List[np.ndarray]):
        """Get the tiles covering a series of ground points.

        Parameters
        ----------
            latitudes : float
                Ground point latitudes
            longitudes : float
                Ground point longitudes
            complete_tile : set to False in case of use for get_elevation before inverse_location

        Returns
        -------
            tiles : tiles covering the ground point
        """
        tiles = []
        indexes = []

        # exclude nan
        status = np.isfinite(latitudes)
        ind_ok = np.where(status)[0]

        present_tiles = self.are_tiles_in_cache_arr(latitudes[ind_ok], longitudes[ind_ok])

        # record tiles existing in cache
        for tile_idx, cur_indexes in (present_tiles or {}).items():
            tiles.append(self._tiles[tile_idx])
            original_indexes = ind_ok[cur_indexes]
            status[original_indexes] = False
            indexes.append(np.array(original_indexes, dtype="int32"))

        # explore for missing tiles
        ind_ok = np.where(status)[0]
        while len(ind_ok):
            # take the first remaining point
            pt_lat = latitudes[ind_ok[0]]
            pt_lon = longitudes[ind_ok[0]]
            # create new tile
            cur_tile = self.get_new_tile(pt_lat, pt_lon, complete_tile=complete_tile)
            tiles.append(cur_tile)
            # gather points belonging to this tile
            _, ind_has_neighbors = cur_tile.get_location_arr(latitudes[ind_ok], longitudes[ind_ok])
            original_indexes = ind_ok[ind_has_neighbors]
            # flag the detected points as "done"
            status[original_indexes] = False
            indexes.append(np.array(original_indexes, dtype="int32"))
            # update list of remaining points to process
            ind_ok = np.where(status)[0]

        return tiles, indexes

    def get_tile(self, latitude: float, longitude: float, complete_tile=True) -> SimpleTile:
        """Get the tile covering a ground point.

        Parameters
        ----------
            latitude : float
                Ground point latitude
            longitude : float
                Ground point longitude
            complete_tile : set False in case of inverse location

        Returns
        -------
            tile : tile covering the ground point
        """
        tile_index = self.is_tile_in_cache(latitude, longitude)
        if tile_index is not None:
            tile = self._tiles[tile_index]
            # We have found the tile in the cache
            # Put it on the front as it becomes the most recently used
            while tile_index > 0:
                self._tiles[tile_index] = self._tiles[tile_index - 1]
                tile_index -= 1

            self._tiles[0] = tile

            return tile  # end of the process

        # None of the tiles in the cache covers the specified points

        # Make some room in the cache, possibly evicting the least recently used one
        index = len(self._tiles) - 1
        while index > 0:
            self._tiles[index] = self._tiles[index - 1]
            index -= 1

        # Create the tile and retrieve its data
        tile = self._tile_constructor()

        # In case dump is asked for, suspend the dump manager as we don't need to dump anything here
        # For instance for SRTM DEM, the user needs to read Geoid data that are not useful in the dump
        if dump_manager.DUMP_VAR is not None:
            was_suspended = dump_manager.DUMP_VAR.suspend()

        self._updater.update_tile(latitude, longitude, tile)

        # Resume the dump manager if necessary
        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.resume(was_suspended)

        if complete_tile:
            tile.tile_update_completed()

        if tile.get_location(latitude, longitude) != Location.HAS_INTERPOLATION_NEIGHBORS:
            raise PyRuggedError(
                PyRuggedMessages.TILE_WITHOUT_REQUIRED_NEIGHBORS_SELECTED.value,
                float(np.degrees(latitude)),
                float(np.degrees(longitude)),
            )

        self._tiles[0] = tile
        return tile

    def get_new_tile(self, latitude: float, longitude: float, complete_tile=True) -> SimpleTile:
        """Get the tile covering a ground point without checking the cache

        Parameters
        ----------
            latitude : float
                Ground point latitude
            longitude : float
                Ground point longitude
            complete_tile : set False in case of inverse location

        Returns
        -------
            tile : tile covering the ground point
        """

        # Make some room in the cache, possibly evicting the least recently used one
        index = len(self._tiles) - 1
        while index > 0:
            self._tiles[index] = self._tiles[index - 1]
            index -= 1

        # Create the tile and retrieve its data
        tile = self._tile_constructor()

        # In case dump is asked for, suspend the dump manager as we don't need to dump anything here
        # For instance for SRTM DEM, the user needs to read Geoid data that are not useful in the dump
        if dump_manager.DUMP_VAR is not None:
            was_suspended = dump_manager.DUMP_VAR.suspend()

        self._updater.update_tile(latitude, longitude, tile)

        # Resume the dump manager if necessary
        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.resume(was_suspended)

        if complete_tile:
            tile.tile_update_completed()

        if tile.get_location(latitude, longitude) != Location.HAS_INTERPOLATION_NEIGHBORS:
            raise PyRuggedError(
                PyRuggedMessages.TILE_WITHOUT_REQUIRED_NEIGHBORS_SELECTED.value,
                float(np.degrees(latitude)),
                float(np.degrees(longitude)),
            )

        self._tiles[0] = tile
        return tile
