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
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""pyrugged Class BasicScanAlgorithm"""

# pylint: disable=too-many-locals
import math
from typing import List, Tuple, Union

import numpy as np

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.bodies.geodesy import normalize_geodetic_point
from pyrugged.errors import dump_manager
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.raster.tile_updater import TileUpdater
from pyrugged.raster.tiles_cache import TilesCache
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    compute_linear_combination_2,
    compute_linear_combination_2_arr,
    dot,
    dot_n,
    get_norm_sq,
    get_norm_sq_n,
)


class BasicScanAlgorithm:
    """Intersection computation using a basic algorithm based on exhaustive scan.

    The algorithm simply computes entry and exit points at high and low altitudes,
    and scans all Digital Elevation Models in the sub-tiles defined by these two
    corner points. It is not designed for operational use.
    """

    def __init__(
        self,
        updater: TileUpdater,
        max_cached_tiles: int,
    ):
        """Builds a new instance.

        Parameters
        ----------
            updater : updater used to load Digital Elevation Model tiles
            max_cached_tiles : maximum number of tiles stored in the cache
        """
        self._cache = TilesCache(SimpleTile, updater, max_cached_tiles)
        self._h_min = float("inf")
        self._h_max = float("-inf")
        self._algorithm_id = AlgorithmId.BASIC_SLOW_EXHAUSTIVE_SCAN_FOR_TESTS_ONLY

    @property
    def algorithm_id(self) -> AlgorithmId:
        """Get the algorithm identifier."""

        return self._algorithm_id

    @staticmethod
    def compute_ground_point(
        ellipsoid: ExtendedEllipsoid,
        position: np.ndarray,
        los: np.ndarray,
        tile: SimpleTile,
        lat_index: int,
        lon_index: int,
        entry_point: np.ndarray,
    ) -> Union[None, Tuple[np.ndarray, float]]:
        """

        Parameters
        ----------
            ellipsoid : Reference ellipsoid
            position : Pixel position in ellipsoid frame
            los : Pixel line-of-sight in ellipsoid frame
            tile: DEM tile
            lat_index: latitude index of the Digital Elevation Model cell
            lon_index: longitude index of the Digital Elevation Model cell
            entry_point: entry point

        Returns
        -------
            Tuple made of te ground point and its dot product or None if no ground point is found
        """
        converted_los = ellipsoid.convert_los_from_point(entry_point, los)
        point_gp = tile.cell_intersection(entry_point, converted_los, lat_index, lon_index)

        if point_gp is not None:
            # Improve the point, by projecting it back on the 3D line,
            # fixing the small body curvature at cell level
            delta = ellipsoid.transform_vec(point_gp) - position
            s_val = dot(delta, los) / get_norm_sq(los)
            projected = ellipsoid.transform_vec(
                compute_linear_combination_2(1.0, position, s_val, los), ellipsoid.body_frame, None
            )

            normalized_projected = normalize_geodetic_point(projected, point_gp[1])

            gp_improved = tile.cell_intersection(
                normalized_projected, ellipsoid.convert_los_from_point(normalized_projected, los), lat_index, lon_index
            )

            if gp_improved is not None:
                point = ellipsoid.transform_vec(gp_improved)
                dot_p = dot(point - position, los)

                return gp_improved, dot_p

        return None

    @staticmethod
    def compute_ground_point_vec(
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
        tile: SimpleTile,
        lat_index_vec: np.ndarray,
        lon_index_vec: np.ndarray,
        entry_point: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """

        Parameters
        ----------
            ellipsoid : Reference ellipsoid
            positions : Pixel positions in ellipsoid frame
            los : Pixel lines-of-sight in ellipsoid frame
            tiles: DEM tile
            indexes: positions indexes corresponding to tiles
            lat_index_vec: latitude indexes of the Digital Elevation Model cells
            lon_index_vec: longitude indexes of the Digital Elevation Model cells
            entry_point: entry points

        Returns
        -------
            Tuple made of te ground point and its dot product or None if no ground point is found
        """
        converted_los = ellipsoid.convert_los_from_point_vec(entry_point, los)  # Optim of the day
        point_gp_vec = np.zeros(positions.shape)
        gp_improved = np.zeros(positions.shape) + np.nan
        dot_p = np.zeros(positions.shape[0]) + np.nan
        point_gp_vec[:, :] = tile.cell_intersection_vec(entry_point, converted_los, lat_index_vec, lon_index_vec)

        ind_not_nan = np.where(~np.isnan(point_gp_vec[:, 0]))[0]
        if len(ind_not_nan) > 0:
            delta = ellipsoid.transform_vec(point_gp_vec) - positions
            s_val = dot_n(delta, los) / get_norm_sq_n(los)
            projected = ellipsoid.transform_vec(
                compute_linear_combination_2_arr(np.ones_like(s_val), positions, s_val, los), ellipsoid.body_frame, None
            )

            normalized_projected = normalize_geodetic_point(projected, point_gp_vec[:, 1])

            gp_improved[:, :] = tile.cell_intersection_vec(
                normalized_projected,
                ellipsoid.convert_los_from_point_vec(normalized_projected, los),
                lat_index_vec,
                lon_index_vec,
            )

            point = ellipsoid.transform_vec(gp_improved)
            dot_p = dot_n(point - positions, los)

        return gp_improved, dot_p

    @staticmethod
    def compute_ground_point_lighter(
        ellipsoid: ExtendedEllipsoid,
        position: np.ndarray,
        los: np.ndarray,
        tile: SimpleTile,
        lat_indexes: np.ndarray,
        lon_indexes: np.ndarray,
        entry_point: np.ndarray,
        converted_los: np.ndarray,
    ) -> np.ndarray:
        """

        Parameters
        ----------
            ellipsoid : Reference ellipsoid
            position : Pixel position in ellipsoid frame
            los : Pixel line-of-sight in ellipsoid frame
            tile: DEM tile
            lat_indexes: latitude indexes of the Digital Elevation Model cell
            lon_indexes: longitude indexes of the Digital Elevation Model cell
            entry_point: entry point
            converted_los: converted line-of-sight

        Returns
        -------
            Ground points (nan if not found)
        """

        # compute cell_intersection for all lat/lon indexes
        point_gp = tile.cell_intersection_vec(entry_point, converted_los, lat_indexes, lon_indexes)

        gp_improved = np.zeros(point_gp.shape) + np.nan
        ind_ok = np.where(np.isfinite(point_gp[:, 0]))[0]
        if len(ind_ok) == 0:
            return np.zeros(3) + np.nan

        # Improve the point, by projecting it back on the 3D line,
        # fixing the small body curvature at cell level
        delta = ellipsoid.transform_vec(point_gp[ind_ok]) - position
        s_val = np.dot(delta, los) / get_norm_sq(los)
        projected = ellipsoid.transform_vec(
            compute_linear_combination_2_arr(np.ones_like(s_val), position, s_val, los), ellipsoid.body_frame, None
        )

        normalized_projected = normalize_geodetic_point(projected, point_gp[ind_ok, 1])

        gp_improved[ind_ok, :] = tile.cell_intersection_vec(
            normalized_projected,
            ellipsoid.convert_los_from_point_vec(normalized_projected, los),
            lat_indexes[ind_ok],
            lon_indexes[ind_ok],
        )

        # find minimum
        ind_ok = np.where(np.isfinite(gp_improved[:, 0]))[0]
        if len(ind_ok) == 0:
            return np.zeros(3) + np.nan

        point = ellipsoid.transform_vec(gp_improved[ind_ok])
        dot_p = np.dot(point - position, los)
        ind_min = np.argmin(dot_p)
        return gp_improved[ind_ok[ind_min]]

    def intersection(self, ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray) -> np.ndarray:
        """Compute intersection of line with Digital Elevation Model.

        Parameters
        ----------
            ellipsoid : reference ellipsoid
            position : pixel position in ellipsoid frame
            los : pixel line-of-sight in ellipsoid frame

        Returns
        -------
            intersection_gp : point at which the line first enters ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        # Find the tiles between the entry and exit point in the Digital Elevation Model
        entry_point = None
        exit_point = None
        min_latitude = float("nan")
        max_latitude = float("nan")
        min_longitude = float("nan")
        max_longitude = float("nan")
        scanned_tiles = []
        central_longitude = float("nan")

        changed_min_max = True
        while changed_min_max:
            # Clean scanned_tiles
            scanned_tiles = []

            # Compute entry and exit points
            entry_point = ellipsoid.transform_vec(
                ellipsoid.point_at_altitude(
                    position, los, 0.0 if (self._h_max == float("inf") or self._h_max == float("-inf")) else self._h_max
                ),
                ellipsoid.body_frame,
                0.0 if math.isnan(central_longitude) else central_longitude,
            )
            entry_tile = self._cache.get_tile(entry_point[0], entry_point[1])
            if math.isnan(central_longitude):
                central_longitude = entry_tile.minimum_longitude
                entry_point = normalize_geodetic_point(entry_point, central_longitude)

            self.add_if_not_present(scanned_tiles, entry_tile)

            exit_point = ellipsoid.transform_vec(
                ellipsoid.point_at_altitude(
                    position, los, 0.0 if (self._h_min == float("inf") or self._h_min == float("-inf")) else self._h_min
                ),
                ellipsoid.body_frame,
                central_longitude,
            )

            exit_tile = self._cache.get_tile(exit_point[0], exit_point[1])
            self.add_if_not_present(scanned_tiles, exit_tile)

            min_latitude = min(entry_point[0], exit_point[0])
            max_latitude = max(entry_point[0], exit_point[0])
            min_longitude = min(entry_point[1], exit_point[1])
            max_longitude = max(entry_point[1], exit_point[1])

            if len(scanned_tiles) > 1:
                # The entry and exit tiles are different, maybe other tiles should be added on the way
                # in the spirit of simple and exhaustive, we add all tiles in a rectangular area
                lat_step = 0.5 * min(
                    entry_tile.latitude_step * entry_tile.latitude_rows,
                    exit_tile.latitude_step * exit_tile.latitude_rows,
                )
                lon_step = 0.5 * min(
                    entry_tile.longitude_step * entry_tile.longitude_columns,
                    exit_tile.longitude_step * exit_tile.longitude_columns,
                )

                latitude = min_latitude
                while latitude <= max_latitude:
                    longitude = min_longitude
                    while longitude < max_longitude:
                        self.add_if_not_present(scanned_tiles, self._cache.get_tile(latitude, longitude))

                        longitude += lon_step

                    latitude += lat_step

            changed_min_max = self.check_min_max(scanned_tiles)

        # Scan the tiles
        intersection_gp = None
        intersection_dot = float("inf")

        for tile in scanned_tiles:
            for i in range(self.latitude_index(tile, min_latitude), self.latitude_index(tile, max_latitude) + 1):
                for j in range(
                    self.longitude_index(tile, min_longitude), self.longitude_index(tile, max_longitude) + 1
                ):
                    gp_improved = BasicScanAlgorithm.compute_ground_point(
                        ellipsoid, position, los, tile, i, j, entry_point
                    )

                    if gp_improved is not None:
                        dot_p = gp_improved[1]
                        if dot_p < intersection_dot:
                            intersection_gp = gp_improved[0]
                            intersection_dot = dot_p

        return intersection_gp

    def intersection_vec(self, ellipsoid: ExtendedEllipsoid, positions: np.ndarray, los: np.ndarray) -> np.ndarray:
        """Compute intersections of lines with Digital Elevation Model.

        Parameters
        ----------
            ellipsoid : reference ellipsoid
            positions : pixel position in ellipsoid frame
            los : pixels lines-of-sight in ellipsoid frame

        Returns
        -------
            intersection_gp : points at which the lines first enter ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        res = []
        for i, position in enumerate(positions):
            # TODO : try to really vectorize this
            res.append(self.intersection(ellipsoid, position, los[i]))

        return np.array(res)

    def refine_intersection(
        self, ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray, close_guess: np.ndarray
    ) -> np.ndarray:
        """Refine intersection of line with Digital Elevation Model.

        This method is used to refine an intersection when a close guess is
        already known. The intersection is typically looked for by a direct
        cell_intersection(np.ndarray, np.ndarray, int, int)
        in the tile which already contains the close guess,
        or any similar very fast algorithm.


        Parameters
        ----------
            ellipsoid : reference ellipsoid
            position : pixel position in ellipsoid frame
            los : pixel line-of-sight in ellipsoid frame
            close_guess : guess close to the real intersection

        Returns
        -------
            result : point at which lin first enters ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        delta = ellipsoid.transform_vec(close_guess) - position
        s_val = dot(delta, los) / get_norm_sq(los)
        projected = ellipsoid.transform_vec(
            compute_linear_combination_2(1.0, position, s_val, los), ellipsoid.body_frame, None
        )
        normalized_projected = normalize_geodetic_point(projected, close_guess[1])

        tile = self._cache.get_tile(normalized_projected[0], normalized_projected[1])

        return tile.cell_intersection(
            normalized_projected,
            ellipsoid.convert_los_from_point(normalized_projected, los),
            tile.get_floor_latitude_index(normalized_projected[0]),
            tile.get_floor_longitude_index(normalized_projected[1]),
        )

    def refine_intersection_vec(
        self,
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
        close_guesses: List[np.ndarray],
    ) -> np.ndarray:
        """Refine intersections of lines with Digital Elevation Model.

        This method is used to refine intersections when close guesses are
        already known. The intersection is typically looked for by a direct
        cell_intersection(np.ndarray, np.ndarray, int, int)
        in the tile which already contains the close guess,
        or any similar very fast algorithm.


        Parameters
        ----------
            ellipsoid : reference ellipsoid
            positions : pixel position in ellipsoid frame
            los : pixel line-of-sight in ellipsoid frame
            close_guesses : guess close to the real intersection

        Returns
        -------
            result : points at which lines first enter ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        res = []
        for i, position in enumerate(positions):
            # TODO: try to really vectorize this
            res.append(self.refine_intersection(ellipsoid, position, los[i], close_guesses[i]))

        return np.array(res)

    def get_elevation(self, latitudes: np.ndarray, longitudes: np.ndarray, complete_tile=True) -> np.ndarray:
        """Get elevation at ground points.

        Parameters
        ----------
            latitudes : ground point latitudes
            longitudes : ground point longitudes
            complete_tile : set to False for inverse location (optional)

        Returns
        -------
            result : elevation at specified points
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        altitudes = np.zeros_like(latitudes)

        (tiles, indexes) = self._cache.get_tiles(latitudes, longitudes, complete_tile=complete_tile)

        for i, tile in enumerate(tiles):
            altitudes[indexes[i]] = tile.interpolate_elevation_arr(latitudes[indexes[i]], longitudes[indexes[i]])

        return altitudes.reshape(-1)

    def check_min_max(self, tiles: List[SimpleTile]) -> bool:
        """Check the overall min and max altitudes.

        Parameters
        ----------
            tiles : tiles to check

        Returns
        -------
            result : true if the tile changed either min or max altitude
        """

        changed_min_max = False

        for tile in tiles:
            # Check minimum altitude
            if tile.min_elevation < self._h_min:
                self._h_min = tile.min_elevation
                changed_min_max = True

            # Check maximum altitude
            if tile.max_elevation > self._h_max:
                self._h_max = tile.max_elevation
                changed_min_max = True

        return changed_min_max

    def add_if_not_present(self, tiles: List[SimpleTile], tile: SimpleTile):
        """Add tile to a list if not already present.

        Parameters
        ----------
            tiles : tiles list
            tile : tile to add
        """

        # Look for existing tiles in the list
        for existing in tiles:
            if existing == tile:
                return None

        # The tile was not is the list, add it
        tiles.append(tile)
        return None

    def latitude_index(self, tile: SimpleTile, latitude: float) -> int:
        """Get latitude index.

        Parameters
        ----------
            tile : current tile
            latitude : current latitude

        Returns
        -------
            result : index of latitude, truncated at tiles limits
        """

        raw_index = tile.get_floor_latitude_index(latitude)

        return min(max(0, raw_index), tile.latitude_rows)

    def longitude_index(self, tile: SimpleTile, longitude: float) -> int:
        """Get longitude index.

        Parameters
        ----------
            tile : current tile
            longitude : index of longitude, truncated at tiles limits

        Returns
        -------
            result : index of longitude, truncated at tiles limits
        """

        raw_index = tile.get_floor_longitude_index(longitude)

        return min(max(0, raw_index), tile.longitude_columns)
