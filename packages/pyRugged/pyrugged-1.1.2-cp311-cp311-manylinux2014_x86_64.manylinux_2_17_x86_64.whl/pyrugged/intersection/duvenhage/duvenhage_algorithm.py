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

"""
Digital Elevation Model intersection using Bernardt Duvenhage's algorithm.

The algorithm is described in the 2009 paper:
http://researchspace.csir.co.za/dspace/bitstream/10204/3041/1/Duvenhage_2009.pdf
Using an Implicit Min/Max KD-Tree for Doing Efficient Terrain Line of Sight Calculations.
"""
import math

# pylint: disable=too-many-lines, too-many-locals
from collections import namedtuple
from typing import List, Tuple, Union

import numpy as np

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.bodies.geodesy import normalize_geodetic_point
from pyrugged.errors.dump import Dump
from pyrugged.errors.pyrugged_exception import PyRuggedError, PyRuggedInternalError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.basic_scan_algorithm import BasicScanAlgorithm
from pyrugged.intersection.duvenhage.min_max_tree_tile import MinMaxTreeTile
from pyrugged.raster.location import Location
from pyrugged.raster.tiles_cache import TilesCache
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    distance,
    dot,
    dot_n,
    get_norm_sq,
    get_norm_sq_n,
    to_array,
)

# named tuple composed of
# * the NormalizedGeodeticPoint (accessible by .point attribute)
# * latitude index to use for interpolating exit point elevation (accessible by .lat_index attribute)
# * longitude index to use for interpolating exit point elevation (accessible by .lon_index attribute)
PointLatLonIndexes = namedtuple("PointLatLonIndexes", ["point", "lat_index", "lon_index"])


def select_closest(p_1: np.ndarray, p_2: np.ndarray, position: np.ndarray) -> np.ndarray:
    """
    Select point closest to line-of-sight start.

    Parameters
    ----------
        p_1: first point to consider
        p_2: second point to consider
        position: pixel position in ellipsoid frame

    Returns
    -------
        either p1 or p2, depending on which is closest to position

    """
    closest_point = p_2
    if distance(p_1, position) <= distance(p_2, position):
        closest_point = p_1

    return closest_point


def select_closest_vec(p_1: np.ndarray, p_2: np.ndarray, positions: np.ndarray) -> np.ndarray:
    """
    Select points closest to lines-of-sight start.

    Parameters
    ----------
        p_1: first points to consider
        p_2: second points to consider
        positions: pixel positions in ellipsoid frame

    Returns
    -------
        either p1 or p2, depending on which is closest to position

    """
    return np.where(
        np.repeat(distance(p_1.T, positions.T), 3).reshape(p_1.shape)
        <= np.repeat(distance(p_2.T, positions.T), 3).reshape(p_1.shape),
        p_1,
        p_2,
    )


def latitude_crossing(
    ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray, latitude: float, close_reference: np.ndarray
) -> np.ndarray:
    """
    Get point at some latitude along a pixel line of sight.

    Parameters
    ----------
        ellipsoid: reference ellipsoid
        position: pixel position (in body frame)
        los: pixel line-of-sight, not necessarily normalized (in body frame)
        latitude: latitude with respect to ellipsoid
        close_reference: reference point used to select the closest solution when there
            are two points at the desired latitude along the line

    Returns
    -------
        point at latitude, or closeReference if no such point can be found

    """
    point = close_reference
    try:
        point = ellipsoid.point_at_latitude(position, los, latitude, close_reference)
    except PyRuggedError:
        pass

    return point


def latitude_crossing_vec(
    ellipsoid: ExtendedEllipsoid,
    positions: np.ndarray,
    los: np.ndarray,
    latitudes: np.ndarray,
    close_references: np.ndarray,
) -> np.ndarray:
    """
    Get point at some latitude along a pixel line of sight.

    Parameters
    ----------
        ellipsoid: reference ellipsoid
        positions: pixels positions (in body frame)
        los: pixels lines-of-sight, not necessarily normalized (in body frame)
        latitudes: latitudes with respect to ellipsoid
        close_references: reference points used to select the closest solution when there
            are two points at the desired latitude along the line

    Returns
    -------
        point at latitude, or closeReference if no such point can be found

    """

    point = ellipsoid.point_at_latitude_vec(positions, los, latitudes, close_references)
    return np.where(np.isnan(point), close_references, point)


def longitude_crossing(
    ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray, longitude: float, close_reference: np.ndarray
) -> np.ndarray:
    """
    Get point at some latitude along a pixel line of sight.

    Parameters
    ----------
        ellipsoid: reference ellipsoid
        position: pixel position (in body frame)
        los: pixel line-of-sight, not necessarily normalized (in body frame)
        longitude: longitude with respect to ellipsoid
        close_reference:
            reference point used to select the closest solution when there are two points at
            the desired longitude along the line

    Returns
    -------
        point at longitude, or closeReference if no such point can be found
    """
    point = close_reference
    try:
        point = ellipsoid.point_at_longitude(position, los, longitude)
    except PyRuggedError:
        pass

    return point


def longitude_crossing_vec(
    ellipsoid: ExtendedEllipsoid,
    positions: np.ndarray,
    los: np.ndarray,
    longitudes: np.ndarray,
    close_references: np.ndarray,
) -> np.ndarray:
    """
    Get points at some longitudes along pixels lines of sight.

    Parameters
    ----------
        ellipsoid: reference ellipsoid
        positions: pixels positions (in body frame)
        los: pixels lines-of-sight, not necessarily normalized (in body frame)
        longitudes: longitudes with respect to ellipsoid
        close_references:
            reference points used to select the closest solutions when there are two points at
            the desired longitude along the line

    Returns
    -------
        points at longitude, or closeReferences if no such point can be found
    """

    point = ellipsoid.point_at_longitude_vec(positions, los, longitudes)
    return np.where(np.isnan(point), close_references, point)


def search_domain_size(entry_lat: int, entry_lon: int, exit_lat: int, exit_lon: int):
    """
    Compute the size of a search domain.

    Parameters
    ----------
        entry_lat: index to use for interpolating entry point elevation
        entry_lon: index to use for interpolating entry point elevation
        exit_lat: index to use for interpolating exit point elevation
        exit_lon: index to use for interpolating exit point elevation

    Returns
    -------
        size of the search domain

    """
    size = (abs(entry_lat - exit_lat) + 1) * (abs(entry_lon - exit_lon + 1))
    return size


def search_domain_size_vec(entry_lat: np.ndarray, entry_lon: np.ndarray, exit_lat: np.ndarray, exit_lon: np.ndarray):
    """
    Compute the size of a search domain.

    Parameters
    ----------
        entry_lat: indexes to use for interpolating entry point elevation
        entry_lon: indexes to use for interpolating entry point elevation
        exit_lat: indexes to use for interpolating exit point elevation
        exit_lon: indexes to use for interpolating exit point elevation

    Returns
    -------
        sizes of the search domain

    """
    sizes = (np.fabs(entry_lat - exit_lat) + 1) * (np.fabs(entry_lon - exit_lon + 1))
    return sizes


def in_range(i: int, bound_1: int, bound_2: int):
    """
    Check if an index is inside a range.

    Parameters
    ----------
        i: index to check
        bound_1: first bound of the range (may be either below or above b)
        bound_2: second bound of the range (may be either below or above a)

    Returns
    -------
        true if i is between a and b (inclusive)

    """
    i_min = i >= min(bound_1, bound_2)
    i_max = i <= max(bound_1, bound_2)
    return i_min and i_max


def in_range_vec(i: np.ndarray, bound_1: np.ndarray, bound_2: np.ndarray):
    """
    Check if indexes are inside ranges.

    Parameters
    ----------
        i: indexes to check
        bound_1: first bounds of the range (may be either below or above b)
        bound_2: second bounds of the range (may be either below or above a)

    Returns
    -------
        true if i is between a and b (inclusive)

    """
    bound_min = np.minimum(bound_1, bound_2)
    bound_max = np.maximum(bound_1, bound_2)
    return (bound_min <= i) * (i <= bound_max)


class LimitPoint:
    """
    Point at tile boundary class
    """

    def __init__(self, point: np.ndarray, side: bool):
        """
        Initialize LimitPoint object

        Parameters
        ----------
            point: coordinates
            side: if true, the point is on a side limit, otherwise it is on a top/bottom limit
        """
        # set coordinates
        self._point = point
        # set limit status
        self._side = side

    @property
    def point(self) -> np.ndarray:
        """
        Get point attribute
        """
        return self._point

    @property
    def side(self) -> bool:
        """
        Get side attribute
        """
        return self._side

    @staticmethod
    def instantiate_from_cartesian_point(
        ellipsoid: ExtendedEllipsoid, reference_longitude: float, cartesian: np.ndarray, side: bool
    ):
        """
        Create limit point from cartesian point

        Parameters
        ----------
            ellipsoid: reference ellipsoid
            reference_longitude:
                reference longitude lc such that the point longitude will be normalized between
                lc-π and lc+π
            cartesian: Cartesian point
            side: if true, the point is on a side limit, otherwise it is on a top/bottom limit

        Returns
        -------
            the corresponding limit point object
        """
        point = ellipsoid.transform_vec(cartesian, ellipsoid.body_frame, reference_longitude)
        return LimitPoint(point, side)

    @staticmethod
    def instantiate_from_cartesian_point_vec(
        ellipsoid: ExtendedEllipsoid, reference_longitudes: np.ndarray, cartesians: np.ndarray, side: np.ndarray
    ) -> np.ndarray:
        """
        Create limit points from cartesian points

        Parameters
        ----------
            ellipsoid: reference ellipsoid
            reference_longitudes:
                reference longitudes lc such that the point longitude will be normalized between
                lc-π and lc+π
            cartesians: Cartesian points
            side: if true, the point is on a side limit, otherwise it is on a top/bottom limit

        Returns
        -------
            the corresponding limit point object
        """
        points = ellipsoid.transform_vec(cartesians, ellipsoid.body_frame, reference_longitudes)
        if points.ndim == 1:
            points = points[np.newaxis, :]
        shape = (points.shape[0], 4)
        limit_points = np.zeros(shape, dtype=float)
        limit_points[:, 0:3] = points[:, :]
        limit_points[:, 3] = side[:].astype(float)
        return limit_points


class DuvenhageAlgorithm(BasicScanAlgorithm):
    """
    DuvenhageAlgortihm class
    """

    # Step size when skipping from one tile to a neighbor one, in meters.
    STEP = 0.01

    # Maximum number of attempts to refine intersection.
    # This parameter is intended to prevent infinite loops.
    MAX_REFINING_ATTEMPTS = 100

    def __init__(self, updater, max_cached_tiles: int, flat_body: bool, dump_file: str = None):
        """
        Initiate DuvenhageAlgorithm object

        Parameters
        ----------
            updater: updater used to load Digital Elevation Model tiles
            max_cached_tiles: maximum number of tiles stored in the cache
            flat_body:
                if true, the body is considered flat, i.e. lines computed
                from entry/exit points in the DEM are considered to be straight lines also
                in geodetic coordinates. The sagitta resulting from real ellipsoid curvature
                is therefore **not** corrected in this case. As this computation is not
                costly (a few percents overhead), it is highly recommended to set this parameter
                to **False**. This flag is mainly intended for comparison purposes with other systems.
            dump_file: path to the dump file
        """
        super().__init__(updater, max_cached_tiles)

        # set flag for flat-body hypothesis.
        self._flat_body = flat_body

        # set algorithm id
        if flat_body:
            self._algorithm_id = AlgorithmId.DUVENHAGE_FLAT_BODY
        else:
            self._algorithm_id = AlgorithmId.DUVENHAGE

        # set cache for DEM tiles.
        self._cache = TilesCache(MinMaxTreeTile, updater, max_cached_tiles)
        self._updater = updater
        self._max_cached_tiles = max_cached_tiles

        # set dump
        self._dump = None
        if dump_file is not None:
            self._dump = Dump(dump_file)

    @property
    def dump(self) -> Union[None, Dump]:
        """
        Get dump

        Returns
        -------
            dump file path
        """
        return self._dump

    def find_los_crosses_tile_max_h(
        self,
        ellipsoid: ExtendedEllipsoid,
        position: np.ndarray,
        los: np.ndarray,
    ) -> Tuple[np.ndarray, MinMaxTreeTile]:
        """
        Find point where los crosses the tile maximum

        Parameters
        ----------
            ellipsoid : Reference ellipsoid
            position : Pixel position in ellipsoid frame
            los : Pixel line-of-sight in ellipsoid frame

        Returns
        -------
            Tuple composed of the point at which the los crosses the maximum altitude
            of the tile and the tile
        """
        current = None

        # compute intersection with ellipsoid
        gp0 = ellipsoid.point_on_ground(position, los, 0.0)

        tile = self._cache.get_tile(gp0[0], gp0[1])
        h_max = tile.max_elevation

        while current is None:
            # find where line-of-sight crosses tile max altitude
            entry_p = ellipsoid.point_at_altitude(position, los, h_max + self.STEP)

            if dot(entry_p - position, los) < 0:
                # the entry point is behind spacecraft!

                # let's see if at least we are above DEM
                try:
                    position_gp = ellipsoid.transform_vec(position, ellipsoid.body_frame, tile.central_longitude)

                    elevation_at_position = tile.interpolate_elevation(position_gp[0], position_gp[1])

                    if position_gp[2] >= elevation_at_position:
                        # we can use the current position as the entry point
                        current = position_gp
                    else:
                        current = None
                except PyRuggedError as pre:
                    if str(pre) == PyRuggedMessages.OUT_OF_TILE_ANGLES:
                        current = None

                if current is None:
                    raise PyRuggedError(PyRuggedMessages.DEM_ENTRY_POINT_IS_BEHIND_SPACECRAFT.value)
            else:
                current = ellipsoid.transform_vec(entry_p, ellipsoid.body_frame, tile.central_longitude)

            if tile.get_location(current[0], current[1]) != Location.HAS_INTERPOLATION_NEIGHBORS:
                # the entry point is in another tile
                tile = self._cache.get_tile(current[0], current[1])
                h_max = max(h_max, tile.max_elevation)
                current = None

        return current, tile

    def find_los_crosses_tile_max_h_vec(
        self,
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
    ) -> Tuple[np.ndarray, List[MinMaxTreeTile], List[np.ndarray]]:
        """
        Find point where los crosses the tile maximum

        Parameters
        ----------
            ellipsoid : Reference ellipsoid
            positions : Pixels positions in ellipsoid frame
            los : Pixels lines-of-sight in ellipsoid frame

        Returns
        -------
            Tuple composed of the points at which the los cross the maximum altitude
            of the tiles and the tiles
        """
        current = np.zeros(positions.shape) + np.nan

        # compute intersection with ellipsoid
        gp0 = ellipsoid.point_on_ground_vec(positions, los, 0.0)

        tiles, indexes = self._cache.get_tiles(gp0[:, 0], gp0[:, 1])
        h_max = np.zeros(positions.shape[0])
        central_longitudes = np.zeros(positions.shape[0])
        for i, tile in enumerate(tiles):
            h_max[indexes[i]] = tile.max_elevation
            central_longitudes[indexes[i]] = tile.central_longitude

        while np.any(np.isnan(current[:, 0])):
            # Optim: todo: only recompute points that are NaN

            # find where line-of-sight crosses tile max altitude
            entry_p = ellipsoid.point_at_altitude_vec(positions, los, h_max + self.STEP)

            front_of_spacecraft_flag = dot_n(entry_p - positions, los) >= 0
            ind_neg = np.where(~front_of_spacecraft_flag)[0]
            if len(ind_neg) > 0:
                # the entry point is behind spacecraft!

                # let's see if at least we are above DEM
                position_gp = ellipsoid.transform_vec(
                    positions[ind_neg, :], ellipsoid.body_frame, central_longitudes[ind_neg]
                )
                elevation_at_positions = np.zeros(position_gp.shape[0])

                for i, tile in enumerate(tiles):
                    # compute indices from ind_neg that are in current tile
                    _, cur_indices, _ = np.intersect1d(ind_neg, indexes[i], assume_unique=True, return_indices=True)
                    if len(cur_indices) == 0:
                        continue

                    # in the interpolated elevation, we may expect NaN if the point is too far from tile extent
                    elevation_at_positions[cur_indices] = tile.interpolate_elevation_arr(
                        position_gp[cur_indices, 0], position_gp[cur_indices, 1]
                    )

                # any NaN in the 'elevation_at_positions' will give a False flag after this comparison
                # so they fall in the error case
                above_dem_flag = position_gp[:, 2] >= elevation_at_positions
                # points above DEM get the LOS origin
                current[ind_neg[above_dem_flag], :] = position_gp[above_dem_flag, :]
                # points with error get a NaN
                current[ind_neg[~above_dem_flag], :] = np.nan

                if np.any(np.isnan(current[ind_neg, :])):
                    raise PyRuggedError(PyRuggedMessages.DEM_ENTRY_POINT_IS_BEHIND_SPACECRAFT.value)

            # nominal case: in front of spacecraft
            current[front_of_spacecraft_flag, :] = ellipsoid.transform_vec(
                entry_p[front_of_spacecraft_flag, :], ellipsoid.body_frame, central_longitudes[front_of_spacecraft_flag]
            )

            # compute indices of points without neighborhood in their tile
            indices_list_no_neighbors = []
            for i, tile in enumerate(tiles):
                _, ind_has_neighbors = tile.get_location_arr(current[indexes[i], 0], current[indexes[i], 1])
                nb_pts_on_tile = len(indexes[i])
                if len(ind_has_neighbors) == nb_pts_on_tile:
                    # all points have neighborhood, nothing to do for this tile tile
                    continue

                ind_no_neighbors = np.setdiff1d(np.arange(nb_pts_on_tile), ind_has_neighbors, assume_unique=True)
                indices_list_no_neighbors.append(indexes[i][ind_no_neighbors])

                # remove these indices from original tile
                indexes[i] = indexes[i][ind_has_neighbors]

            if len(indices_list_no_neighbors) == 0:
                continue
            all_ind_no_neighbors = np.sort(np.concatenate(indices_list_no_neighbors))

            # Get new tiles to check
            tiles2, indexes2 = self._cache.get_tiles(current[all_ind_no_neighbors, 0], current[all_ind_no_neighbors, 1])
            tiles = tiles + tiles2
            for ind in indexes2:
                indexes.append(all_ind_no_neighbors[ind])

            # update hMax
            for i, tile in enumerate(tiles2):
                original_indices = all_ind_no_neighbors[indexes2[i]]
                h_max[original_indices] = np.fmax(h_max[original_indices], tile.max_elevation)
                central_longitudes[original_indices] = tile.central_longitude

            # reset current location to NaN for points without neighbors
            current[all_ind_no_neighbors, :] = np.nan

        # remove tile without any points
        empty_tiles = [pos for pos, ind in enumerate(indexes) if len(ind) == 0]
        output_tiles = [tile for pos, tile in enumerate(tiles) if pos not in empty_tiles]
        output_indices = [ind for pos, ind in enumerate(indexes) if pos not in empty_tiles]

        # Optim: todo: consolidate output tiles, maybe duplicated tiles to merge

        return current, output_tiles, output_indices

    def find_exit(
        self, tile: MinMaxTreeTile, ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray
    ) -> LimitPoint:
        """
        Compute a line-of-sight exit point from a tile.

        Parameters
        ----------
            tile: tile to consider
            ellipsoid: reference ellipsoid
            position: pixel position in ellipsoid frame
            los: pixel line-of-sight in ellipsoid frame

        Returns
        -------
            exit point
        """
        # look for an exit at bottom
        reference = tile.central_longitude
        close_exit_p = ellipsoid.point_at_altitude(position, los, tile.min_elevation - self.STEP)
        exit_gp = ellipsoid.transform_vec(close_exit_p, ellipsoid.body_frame, reference)

        tile_location = tile.get_location(exit_gp[0], exit_gp[1])
        cartesian = None
        if tile_location == Location.SOUTH_WEST:
            cartesian = select_closest(
                latitude_crossing(ellipsoid, position, los, tile.minimum_latitude, close_exit_p),
                longitude_crossing(ellipsoid, position, los, tile.minimum_longitude, close_exit_p),
                position,
            )
        elif tile_location == Location.WEST:
            cartesian = longitude_crossing(ellipsoid, position, los, tile.minimum_longitude, close_exit_p)
        elif tile_location == Location.NORTH_WEST:
            cartesian = select_closest(
                latitude_crossing(ellipsoid, position, los, tile.maximum_latitude, close_exit_p),
                longitude_crossing(ellipsoid, position, los, tile.minimum_longitude, close_exit_p),
                position,
            )
        elif tile_location == Location.NORTH:
            cartesian = latitude_crossing(ellipsoid, position, los, tile.maximum_latitude, close_exit_p)
        elif tile_location == Location.NORTH_EAST:
            cartesian = select_closest(
                latitude_crossing(ellipsoid, position, los, tile.maximum_latitude, close_exit_p),
                longitude_crossing(ellipsoid, position, los, tile.maximum_longitude, close_exit_p),
                position,
            )
        elif tile_location == Location.EAST:
            cartesian = longitude_crossing(ellipsoid, position, los, tile.maximum_longitude, close_exit_p)
        elif tile_location == Location.SOUTH_EAST:
            cartesian = select_closest(
                latitude_crossing(ellipsoid, position, los, tile.minimum_latitude, close_exit_p),
                longitude_crossing(ellipsoid, position, los, tile.maximum_longitude, close_exit_p),
                position,
            )
        elif tile_location == Location.SOUTH:
            cartesian = latitude_crossing(ellipsoid, position, los, tile.minimum_latitude, close_exit_p)

        if cartesian is not None:
            exit_p = LimitPoint.instantiate_from_cartesian_point(ellipsoid, reference, cartesian, True)
        elif tile_location == Location.HAS_INTERPOLATION_NEIGHBORS:
            exit_p = LimitPoint(exit_gp, False)
        else:
            # this should never happen
            raise PyRuggedInternalError

        return exit_p

    def find_exit_vec(  # pylint: disable=too-many-locals
        self,
        tiles: List[MinMaxTreeTile],
        indexes: List[np.ndarray],
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
    ) -> np.ndarray:
        """
        Compute a line-of-sight exit point from a tile.

        Parameters
        ----------
            tiles: tiles to consider
            indexes: positions indexes corresponding to tiles
            ellipsoid: reference ellipsoid
            positions: pixels positions in ellipsoid frame
            los: pixels lines-of-sight in ellipsoid frame

        Returns
        -------
            exit points
        """
        # look for an exit at bottom
        reference = np.zeros(positions.shape[0])
        tile_locations = np.zeros(positions.shape[0], dtype=object)
        min_elevation = np.zeros(positions.shape[0])
        min_latitude = np.zeros(positions.shape[0])
        min_longitude = np.zeros(positions.shape[0])
        max_latitude = np.zeros(positions.shape[0])
        max_longitude = np.zeros(positions.shape[0])
        exit_p = np.zeros((positions.shape[0], 4)) + np.nan

        for i, tile in enumerate(tiles):
            reference[indexes[i]] = tile.central_longitude
            min_elevation[indexes[i]] = tile.min_elevation
            min_latitude[indexes[i]] = tile.minimum_latitude
            min_longitude[indexes[i]] = tile.minimum_longitude
            max_latitude[indexes[i]] = tile.maximum_latitude
            max_longitude[indexes[i]] = tile.maximum_longitude

        close_exit_p = ellipsoid.point_at_altitude_vec(positions, los, min_elevation - self.STEP)
        exit_gp = ellipsoid.transform_vec(close_exit_p, ellipsoid.body_frame, reference)

        for i, tile in enumerate(tiles):
            tile_locations[indexes[i]], _ = tile.get_location_arr(exit_gp[indexes[i], 0], exit_gp[indexes[i], 1])

        cartesian = np.zeros(positions.shape) + np.nan
        ind_sw = np.where(tile_locations == Location.SOUTH_WEST.value)[0]
        ind_w = np.where(tile_locations == Location.WEST.value)[0]
        ind_nw = np.where(tile_locations == Location.NORTH_WEST.value)[0]
        ind_n = np.where(tile_locations == Location.NORTH.value)[0]
        ind_ne = np.where(tile_locations == Location.NORTH_EAST.value)[0]
        ind_e = np.where(tile_locations == Location.EAST.value)[0]
        ind_se = np.where(tile_locations == Location.SOUTH_EAST.value)[0]
        ind_s = np.where(tile_locations == Location.SOUTH.value)[0]

        if len(ind_sw) > 0:
            cartesian[ind_sw, :] = select_closest_vec(
                latitude_crossing_vec(
                    ellipsoid, positions[ind_sw, :], los[ind_sw, :], min_latitude[ind_sw], close_exit_p[ind_sw, :]
                ),
                longitude_crossing_vec(
                    ellipsoid, positions[ind_sw, :], los[ind_sw, :], min_longitude[ind_sw], close_exit_p[ind_sw, :]
                ),
                positions[ind_sw, :],
            )

        if len(ind_w) > 0:
            cartesian[ind_w, :] = longitude_crossing_vec(
                ellipsoid, positions[ind_w, :], los[ind_w, :], min_longitude[ind_w], close_exit_p[ind_w, :]
            )

        if len(ind_nw) > 0:
            cartesian[ind_nw, :] = select_closest_vec(
                latitude_crossing_vec(
                    ellipsoid, positions[ind_nw, :], los[ind_nw, :], min_latitude[ind_nw], close_exit_p[ind_nw, :]
                ),
                longitude_crossing_vec(
                    ellipsoid, positions[ind_nw, :], los[ind_nw, :], min_longitude[ind_nw], close_exit_p[ind_nw, :]
                ),
                positions[ind_nw, :],
            )

        if len(ind_n) > 0:
            cartesian[ind_n, :] = latitude_crossing_vec(
                ellipsoid, positions[ind_n, :], los[ind_n, :], max_latitude[ind_n], close_exit_p[ind_n, :]
            )

        if len(ind_ne) > 0:
            cartesian[ind_ne, :] = select_closest_vec(
                latitude_crossing_vec(
                    ellipsoid, positions[ind_ne, :], los[ind_ne, :], max_latitude[ind_ne], close_exit_p[ind_ne, :]
                ),
                longitude_crossing_vec(
                    ellipsoid, positions[ind_ne, :], los[ind_ne, :], max_longitude[ind_ne], close_exit_p[ind_ne, :]
                ),
                positions[ind_ne, :],
            )

        if len(ind_e) > 0:
            cartesian[ind_e, :] = longitude_crossing_vec(
                ellipsoid, positions[ind_e, :], los[ind_e, :], max_longitude[ind_e], close_exit_p[ind_e, :]
            )

        if len(ind_se) > 0:
            cartesian[ind_se, :] = select_closest_vec(
                latitude_crossing_vec(
                    ellipsoid, positions[ind_se, :], los[ind_se, :], min_latitude[ind_se], close_exit_p[ind_se, :]
                ),
                longitude_crossing_vec(
                    ellipsoid, positions[ind_se, :], los[ind_se, :], max_longitude[ind_se], close_exit_p[ind_se, :]
                ),
                positions[ind_se, :],
            )

        if len(ind_s) > 0:
            cartesian[ind_s, :] = latitude_crossing_vec(
                ellipsoid, positions[ind_s, :], los[ind_s, :], min_latitude[ind_s], close_exit_p[ind_s, :]
            )

        side = np.ones_like(cartesian[:, 0])
        ind_not_nan = np.where(~np.isnan(cartesian[:, 0]))[0]
        ind_nan = np.where(np.isnan(cartesian[:, 0]))[0]

        exit_p[ind_not_nan, :] = LimitPoint.instantiate_from_cartesian_point_vec(
            ellipsoid, reference[ind_not_nan], cartesian[ind_not_nan, :], side[ind_not_nan]
        )

        exit_p[ind_nan, 0:3] = exit_gp[ind_nan, :]
        exit_p[ind_nan, 3] = float(False)

        return exit_p

    def intersection(self, ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray) -> np.ndarray:
        """
        Compute intersection of line with Digital Elevation Model.

        Parameters
        ----------
            ellipsoid : Reference ellipsoid
            position : Pixel position in ellipsoid frame
            los : Pixel line-of-sight in ellipsoid frame

        Returns
        -------
            Point at which the line first enters ground

        """
        if self.dump is not None:
            self.dump.dump_algorithm(self.algorithm_id)

        # locate the entry tile along the line-of-sight
        current, tile = self.find_los_crosses_tile_max_h(ellipsoid, position, los)

        # loop along the path
        while True:
            # find where line-of-sight exit tile
            tile_exit_point = self.find_exit(tile, ellipsoid, position, los)

            # compute intersection with Digital Elevation Model
            entry_lat = max(0, min(tile.latitude_rows - 1, tile.get_floor_latitude_index(current[0])))
            entry_lon = max(
                0,
                min(tile.longitude_columns - 1, tile.get_floor_longitude_index(current[1])),
            )
            exit_lat = max(
                0,
                min(tile.latitude_rows - 1, tile.get_floor_latitude_index(tile_exit_point.point[0])),
            )
            exit_lon = max(
                0,
                min(
                    tile.longitude_columns - 1,
                    tile.get_floor_longitude_index(tile_exit_point.point[1]),
                ),
            )

            intersection = self.recurse_intersection(
                0,
                ellipsoid,
                position,
                los,
                tile,
                PointLatLonIndexes(current, entry_lat, entry_lon),
                PointLatLonIndexes(tile_exit_point.point, exit_lat, exit_lon),
            )
            final_intersection = None
            if intersection is not None:
                # we have found the intersection
                final_intersection = intersection
            elif tile_exit_point.side:
                # no intersection on this tile, we can proceed to next part of the line-of-sight

                # select next tile after current point
                t_exit = ellipsoid.transform_vec(tile_exit_point.point)
                forward = to_array(
                    t_exit[0] + self.STEP * los[0],
                    t_exit[1] + self.STEP * los[1],
                    t_exit[2] + self.STEP * los[2],
                )
                current = ellipsoid.transform_vec(forward, ellipsoid.body_frame, tile.central_longitude)
                tile = self._cache.get_tile(current[0], current[1])

                if tile.interpolate_elevation(current[0], current[1]) >= current[2]:
                    # extremely rare case! The line-of-sight traversed the Digital Elevation Model
                    # during the very short forward step we used to move to next tile
                    # we consider this point to be OK
                    final_intersection = current
            else:
                # this should never happen
                # we should have left the loop with an intersection point
                # try a fallback non-recursive search
                intersection = DuvenhageAlgorithm.no_recurse_intersection(
                    ellipsoid,
                    position,
                    los,
                    tile,
                    PointLatLonIndexes(current, entry_lat, entry_lon),
                    exit_lat,
                    exit_lon,
                )

                if intersection is not None:
                    final_intersection = intersection
                else:
                    raise PyRuggedInternalError()

            if final_intersection is not None:
                return final_intersection

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

        if self.dump is not None:
            self.dump.dump_algorithm(self.algorithm_id)

        # intersections = []
        # for i, position in enumerate(positions):
        #     intersections.append(self.intersection(ellipsoid, position, los[i, :]))

        # locate the entry tile along the line-of-sight
        current, tiles, indexes = self.find_los_crosses_tile_max_h_vec(ellipsoid, positions, los)

        floor_latitude_index = np.zeros(positions[:, 0].shape, dtype="int64")
        floor_longitude_index = np.zeros(positions[:, 0].shape, dtype="int64")
        floor_latitude_index_exit = np.zeros(positions[:, 0].shape, dtype="int64")
        floor_longitude_index_exit = np.zeros(positions[:, 0].shape, dtype="int64")
        central_longitude = np.zeros(positions[:, 0].shape)

        elevation_at_positions = np.zeros(positions[:, 0].shape)
        intersections = np.zeros(positions.shape) + np.nan
        t_exit = np.zeros(positions.shape)

        # Here we choose to make a single iteration on the intersected tiles. However, points that
        # are changing tiles are appended to the original "tiles" and "indexes" lists. We control the
        # end of this iteration by allowing a maximum of MAX_REFINING_ATTEMPTS new tiles.
        iter_stop = len(tiles) + self.MAX_REFINING_ATTEMPTS

        # process each tiles
        i = -1
        while True:
            # handle loop increment here because of multiple "continue" statements
            i += 1
            # all tiles processed => exit
            if i >= len(tiles):
                break

            # safety stop here: we reached the maximum number of allowed tiles
            if i >= iter_stop:
                # TODO: issue a warning? raise an exception?
                break

            # current tile
            tile = tiles[i]

            ind_nok = np.where(np.isnan(intersections[indexes[i], 0]))[0]
            if len(ind_nok) == 0:
                continue

            # find where line-of-sight exit tile
            # TODO: provide a find_exit_vec function working on a single tile
            tile_exit_points = self.find_exit_vec([tile], [indexes[i]], ellipsoid, positions, los)

            floor_latitude_index[indexes[i]] = tile.get_floor_latitude_index_arr(current[indexes[i], 0])
            floor_longitude_index[indexes[i]] = tile.get_floor_longitude_index_arr(current[indexes[i], 1])
            floor_latitude_index_exit[indexes[i]] = tile.get_floor_latitude_index_arr(tile_exit_points[indexes[i], 0])
            floor_longitude_index_exit[indexes[i]] = tile.get_floor_longitude_index_arr(tile_exit_points[indexes[i], 1])
            central_longitude[indexes[i]] = tile.central_longitude

            # compute intersection with Digital Elevation Model
            entry_lat = np.clip(floor_latitude_index[indexes[i]], 0, tile.latitude_rows - 1)
            entry_lon = np.clip(floor_longitude_index[indexes[i]], 0, tile.longitude_columns - 1)
            exit_lat = np.clip(floor_latitude_index_exit[indexes[i]], 0, tile.latitude_rows - 1)
            exit_lon = np.clip(floor_longitude_index_exit[indexes[i]], 0, tile.longitude_columns - 1)

            intersections[indexes[i][ind_nok], :] = self.recurse_intersection_vec(
                0,
                ellipsoid,
                positions[indexes[i][ind_nok], :],
                los[indexes[i][ind_nok], :],
                tile,
                PointLatLonIndexes(current[indexes[i][ind_nok], :], entry_lat[ind_nok], entry_lon[ind_nok]),
                PointLatLonIndexes(tile_exit_points[indexes[i][ind_nok], 0:3], exit_lat[ind_nok], exit_lon[ind_nok]),
            )

            nan_flag = np.isnan(intersections[indexes[i], 0])
            side_flag = tile_exit_points[indexes[i], 3] == 1

            ind_side_true = np.where(np.logical_and(side_flag, nan_flag))[0]
            ind_exceptional = np.where(np.logical_and(np.logical_not(side_flag), nan_flag))[0]

            if len(ind_side_true) > 0:
                # move forward past the tile exit point
                t_exit[indexes[i][ind_side_true], :] = ellipsoid.transform_vec(
                    tile_exit_points[indexes[i][ind_side_true], 0:3]
                )
                forward = t_exit[indexes[i][ind_side_true], :] + self.STEP * los[indexes[i][ind_side_true], :]
                current[indexes[i][ind_side_true], :] = ellipsoid.transform_vec(
                    forward, ellipsoid.body_frame, central_longitude[indexes[i][ind_side_true]]
                )

                # get the new tiles to explore
                tiles2, indexes2 = self._cache.get_tiles(
                    current[indexes[i][ind_side_true], 0], current[indexes[i][ind_side_true], 1]
                )

                for j, tile2 in enumerate(tiles2):
                    cur_indices = indexes[i][ind_side_true][indexes2[j]]
                    elevation_at_positions[cur_indices] = tile2.interpolate_elevation_arr(
                        current[cur_indices, 0],
                        current[cur_indices, 1],
                    )

                    ind_down = np.where(elevation_at_positions[cur_indices] >= current[cur_indices, 2])[0]

                    intersections[cur_indices[ind_down], :] = current[cur_indices[ind_down], :]

                    # update the tile and index for "up" points
                    ind_up = np.where(elevation_at_positions[cur_indices] < current[cur_indices, 2])[0]

                    if len(ind_up) == 0:
                        continue

                    # we choose to append the tile2 anyway so they are processed after the original ones.
                    # the cache will make sure that existing tiles are no reloaded.
                    obsolete_indices = cur_indices[ind_up]
                    indexes.append(obsolete_indices)
                    tiles.append(tile2)

            if len(ind_exceptional) > 0:
                # this should never happen
                # we should have left the loop with an intersection point
                # try a fallback non-recursive search

                intersections[indexes[i][ind_exceptional], :] = self.no_recurse_intersection_vec(
                    ellipsoid,
                    positions[indexes[i][ind_exceptional], :],
                    los[indexes[i][ind_exceptional], :],
                    tile,
                    PointLatLonIndexes(
                        current[indexes[i][ind_exceptional], :], entry_lat[ind_exceptional], entry_lon[ind_exceptional]
                    ),
                    exit_lat[ind_exceptional],
                    exit_lon[ind_exceptional],
                )

                ind_nok = np.where(np.isnan(intersections[indexes[i][ind_exceptional], 0]))[0]
                if len(ind_nok) > 0:
                    raise PyRuggedInternalError()

        return intersections

    def refine_intersection(
        self, ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray, close_guess: np.ndarray
    ) -> Union[np.ndarray, None]:
        """
        Refine intersection of line with Digital Elevation Model.

        This method is used to refine an intersection when a close guess is
        already known. The intersection is typically looked for by a direct
        cell_intersection(NormalizedGeodeticPoint, np.ndarray, int, int)
        in the tile which already contains the close guess,
        or any similar very fast algorithm.


        Parameters
        ----------
            ellipsoid : Reference ellipsoid
            position : Pixel position in ellipsoid frame
            los : Pixel line-of-sight in ellipsoid frame
            close_guess : Guess close to the real intersection

        Returns
        -------
            Point at which lin first enters ground
        """
        if self.dump is not None:
            self.dump.dump_algorithm(self.algorithm_id)

        final_intersection = None
        if self._flat_body:
            # under the (bad) flat-body assumption, the reference point must remain
            # at DEM entry and exit, even if we already have a much better close guess :-(
            # this is in order to remain consistent with other systems
            tile = self._cache.get_tile(close_guess[0], close_guess[1])
            exit_p = ellipsoid.point_at_altitude(position, los, tile.min_elevation)
            entry_p = ellipsoid.point_at_altitude(position, los, tile.max_elevation)
            entry = ellipsoid.transform_vec(entry_p, ellipsoid.body_frame, tile.central_longitude)

            final_intersection = tile.cell_intersection(
                entry,
                ellipsoid.convert_los_from_vector(entry_p, exit_p),
                tile.get_floor_latitude_index(close_guess[0]),
                tile.get_floor_longitude_index(close_guess[1]),
            )
        else:
            # regular curved ellipsoid model
            current_guess = close_guess

            # normally, we should succeed at first attempt but in very rare cases
            # we may loose the intersection (typically because some corrections introduced
            # between the first intersection and the refining have slightly changed the
            # relative geometry between Digital Elevation Model and Line Of Sight).
            # In these rare cases, we have to recover a new intersection

            for _ in range(self.MAX_REFINING_ATTEMPTS):
                delta = ellipsoid.transform_vec(current_guess) - position
                s_val = dot(delta, los) / get_norm_sq(los)
                projected_p = to_array(
                    position[0] + s_val * los[0],
                    position[1] + s_val * los[1],
                    position[2] + s_val * los[2],
                )
                projected = ellipsoid.transform_vec(projected_p, ellipsoid.body_frame, None)
                normalized_projected = normalize_geodetic_point(
                    projected,
                    current_guess[1],
                )

                tile = self._cache.get_tile(normalized_projected[0], normalized_projected[1])

                topos_los = ellipsoid.convert_los_from_point(normalized_projected, los)
                i_lat = tile.get_floor_latitude_index(normalized_projected[0])
                i_lon = tile.get_floor_longitude_index(normalized_projected[1])

                found_intersection = tile.cell_intersection(normalized_projected, topos_los, i_lat, i_lon)

                if found_intersection is not None:
                    # nominal case, we were able to refine the intersection
                    final_intersection = found_intersection
                else:
                    # extremely rare case: we have lost the intersection

                    # find a start point for new search, leaving the current cell behind
                    cell_boundary_latitude = tile.get_latitude_at_index(
                        i_lat if tile.get_latitude_at_index(topos_los[1]) <= 0 else i_lat + 1
                    )

                    cell_boundary_longitude = tile.get_longitude_at_index(
                        i_lon if tile.get_longitude_at_index(topos_los[0]) <= 0 else i_lon + 1
                    )

                    closest = select_closest(
                        latitude_crossing(ellipsoid, projected_p, los, cell_boundary_latitude, projected_p),
                        longitude_crossing(ellipsoid, projected_p, los, cell_boundary_longitude, projected_p),
                        projected_p,
                    )
                    cell_exit = to_array(
                        closest[0] + self.STEP * los[0],
                        closest[1] + self.STEP * los[1],
                        closest[2] + self.STEP * los[2],
                    )
                    egp = ellipsoid.transform_vec(cell_exit, ellipsoid.body_frame, None)
                    cell_exit_gp = normalize_geodetic_point(egp, close_guess[1])

                    if tile.interpolate_elevation(cell_exit_gp[0], cell_exit_gp[1]) >= cell_exit_gp[2]:
                        # extremely rare case! The line-of-sight traversed the Digital Elevation Model
                        # during the very short forward step we used to move to next cell
                        # we consider this point to be OK
                        final_intersection = cell_exit_gp
                    else:
                        # We recompute fully a new guess, starting from the point after current cell
                        current_guess_gp = self.intersection(ellipsoid, cell_exit, los)
                        current_guess = normalize_geodetic_point(
                            current_guess_gp,
                            projected[1],
                        )

                if final_intersection is not None:
                    break

        # no intersection found
        return final_intersection

    def refine_intersection_vec(  # pylint: disable=too-many-locals
        self, ellipsoid: ExtendedEllipsoid, positions: np.ndarray, los: np.ndarray, close_guesses: np.ndarray
    ) -> np.ndarray:
        """Refine intersections of lines with Digital Elevation Model.

        This method is used to refine intersections when close guesses are
        already known. The intersection is typically looked for by a direct
        cell_intersection(NormalizedGeodeticPoint, np.ndarray, int, int)
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

        # if self.dump is not None:
        #     self.dump.dump_algorithm(self.algorithm_id)
        #
        # res = []
        # if positions.ndim == 1:
        #     positions = positions[np.newaxis, :]
        #     los = los[np.newaxis, :]
        #     close_guesses = close_guesses[np.newaxis, :]
        # for i, position in enumerate(positions):
        #     # TODO: try to really vectorize this
        #     if close_guesses[i] is not None:
        #         res.append(self.refine_intersection(ellipsoid, position, los[i], close_guesses[i]))
        #     else:
        #         res.append(None)
        #
        # return np.array(res)

        if self.dump is not None:
            self.dump.dump_algorithm(self.algorithm_id)

        final_intersection = np.zeros(positions.shape) + np.nan
        if self._flat_body:
            # under the (bad) flat-body assumption, the reference point must remain
            # at DEM entry and exit, even if we already have a much better close guess :-(
            # this is in order to remain consistent with other systems
            tiles, indexes = self._cache.get_tiles(close_guesses[:, 0], close_guesses[:, 1])
            for i, tile in enumerate(tiles):
                exit_p = ellipsoid.point_at_altitude_vec(
                    positions[indexes[i], :], los[indexes[i], :], tile.min_elevation
                )
                entry_p = ellipsoid.point_at_altitude_vec(
                    positions[indexes[i], :], los[indexes[i], :], tile.max_elevation
                )
                entry = ellipsoid.transform_vec(entry_p, ellipsoid.body_frame, tile.central_longitude)

                final_intersection[indexes[i], :] = tile.cell_intersection_vec(
                    entry,
                    ellipsoid.convert_los_from_vector_vec(entry_p, exit_p),
                    tile.get_floor_latitude_index_vec(close_guesses[indexes[i], 0]),
                    tile.get_floor_longitude_index_vec(close_guesses[indexes[i], 1]),
                )
        else:
            # regular curved ellipsoid model
            current_guess = close_guesses

            # normally, we should succeed at first attempt but in very rare cases
            # we may loose the intersection (typically because some corrections introduced
            # between the first intersection and the refining have slightly changed the
            # relative geometry between Digital Elevation Model and Line Of Sight).
            # In these rare cases, we have to recover a new intersection
            for _ in range(self.MAX_REFINING_ATTEMPTS):
                delta = ellipsoid.transform_vec(current_guess) - positions
                s_val = dot_n(delta, los) / get_norm_sq_n(los)
                projected_p = positions + s_val[:, np.newaxis] * los
                projected = ellipsoid.transform_vec(projected_p, ellipsoid.body_frame, None)

                tiles, indexes = self._cache.get_tiles(projected[:, 0], projected[:, 1])
                topos_los = ellipsoid.convert_los_from_point_vec(projected, los)

                found_intersection = final_intersection
                for i, tile in enumerate(tiles):
                    # normalize with respect to current tile
                    normalized_projected = normalize_geodetic_point(
                        projected[indexes[i]],
                        tile.minimum_longitude,
                    )
                    i_lat = tile.get_floor_latitude_index_arr(normalized_projected[:, 0])
                    i_lon = tile.get_floor_longitude_index_arr(normalized_projected[:, 1])

                    found_intersection[indexes[i], :] = tile.cell_intersection_vec(
                        normalized_projected, topos_los[indexes[i], :], i_lat, i_lon
                    )

                    ind_not_nan = np.where(~np.isnan(found_intersection[indexes[i], 0]))[0]
                    ind_nan = np.where(np.isnan(found_intersection[indexes[i], 0]))[0]
                    final_intersection[indexes[i][ind_not_nan], :] = found_intersection[indexes[i][ind_not_nan], :]
                    if len(ind_nan) == 0:
                        continue

                    # extremely rare case: we have lost the intersection

                    # filter to keep only indices without intersections
                    ind_lost_inter = indexes[i][ind_nan]
                    i_lat = i_lat[ind_nan]
                    i_lon = i_lon[ind_nan]

                    cell_boundary_latitude = np.zeros(topos_los[ind_lost_inter, 0].shape)
                    cell_boundary_longitude = np.zeros(topos_los[ind_lost_inter, 0].shape)

                    # find a start point for new search, leaving the current cell behind
                    lat_neg_flag = tile.get_latitude_at_index_arr(topos_los[ind_lost_inter, 1]) <= 0
                    cell_boundary_latitude[lat_neg_flag] = tile.get_latitude_at_index_arr(i_lat[lat_neg_flag])
                    cell_boundary_latitude[~lat_neg_flag] = tile.get_latitude_at_index_arr(i_lat[~lat_neg_flag] + 1)

                    lon_neg_flag = tile.get_longitude_at_index_arr(topos_los[ind_lost_inter, 0]) <= 0
                    cell_boundary_longitude[lon_neg_flag] = tile.get_longitude_at_index_arr(i_lon[lon_neg_flag])
                    cell_boundary_longitude[~lon_neg_flag] = tile.get_longitude_at_index_arr(i_lon[~lon_neg_flag] + 1)

                    closest = select_closest_vec(
                        latitude_crossing_vec(
                            ellipsoid,
                            projected_p[ind_lost_inter, :],
                            los[ind_lost_inter, :],
                            cell_boundary_latitude,
                            projected_p[ind_lost_inter, :],
                        ),
                        longitude_crossing_vec(
                            ellipsoid,
                            projected_p[ind_lost_inter, :],
                            los[ind_lost_inter, :],
                            cell_boundary_longitude,
                            projected_p[ind_lost_inter, :],
                        ),
                        projected_p[ind_lost_inter, :],
                    )
                    cell_exit = closest + self.STEP * los[ind_lost_inter, :]
                    egp = ellipsoid.transform_vec(cell_exit, ellipsoid.body_frame, None)
                    cell_exit_gp = normalize_geodetic_point(egp, close_guesses[ind_lost_inter, 1])

                    exit_above_flag = (
                        tile.interpolate_elevation_arr(cell_exit_gp[:, 0], cell_exit_gp[:, 1]) >= cell_exit_gp[:, 2]
                    )
                    final_intersection[ind_lost_inter[exit_above_flag], :] = cell_exit_gp[exit_above_flag]

                    if np.all(~np.isnan(final_intersection[:, 0])):
                        break

                    ind_nok = ind_lost_inter[~exit_above_flag]
                    if len(ind_nok) > 0:

                        # We recompute fully a new guess, starting from the point after current cell
                        current_guess_gp = self.intersection_vec(
                            ellipsoid, cell_exit[~exit_above_flag, :], los[ind_nok, :]
                        )
                        current_guess[ind_nok, :] = normalize_geodetic_point(
                            current_guess_gp,
                            projected[ind_nok, 1],
                        )

                if np.all(~np.isnan(final_intersection[:, 0])):
                    break

        # no intersection found
        return final_intersection

    def recurse_intersection_longitude_crossings(
        self,
        ellipsoid: ExtendedEllipsoid,
        position: np.ndarray,
        los: np.ndarray,
        tile: MinMaxTreeTile,
        entry_point_lat_lon: PointLatLonIndexes,
        exit_point_lat_lon: PointLatLonIndexes,
        depth: int,
    ) -> Union[np.ndarray, None]:
        """
        Recurse intersection through longitude crossings

        Parameters
        ----------
            ellipsoid: reference ellipsoid
            position: pixel position in ellipsoid frame
            los: pixel line-of-sight in ellipsoid frame
            tile: Digital Elevation Model tile
            entry_point_lat_lon: entry point with its latitude and longitude indexes
            exit_point_lat_lon: exit point with its latitude and longitude indexes
            depth: recursion depth

        Returns
        -------
            point at which the line first enters ground,
            or null if does not enter ground in the search sub-tile
        """
        # recurse through longitude crossings
        entry_point = entry_point_lat_lon.point
        entry_lat = entry_point_lat_lon.lat_index
        entry_lon = entry_point_lat_lon.lon_index

        exit_point = exit_point_lat_lon.point
        exit_lat = exit_point_lat_lon.lat_index
        exit_lon = exit_point_lat_lon.lon_index

        previous_gp = entry_point
        previous_lat = entry_lat
        previous_lon = entry_lon

        # find the deepest level in the min/max kd-tree at which entry and exit share a sub-tile
        level = tile.get_merge_level(entry_lat, entry_lon, exit_lat, exit_lon)

        crossings = tile.get_crossed_boundary_columns(previous_lon, exit_lon, level + 1)

        for crossing_lon in crossings:
            # compute segment endpoints
            longitude = tile.get_longitude_at_index(crossing_lon)

            crossing_gp = None
            if not self._flat_body:
                try:
                    # full computation of crossing point
                    crossing_p = ellipsoid.point_at_longitude(position, los, longitude)
                    crossing_gp = ellipsoid.transform_vec(crossing_p, ellipsoid.body_frame, tile.central_longitude)
                except PyRuggedError:
                    # in some very rare cases of numerical noise, we miss the crossing point
                    crossing_gp = None

            if crossing_gp is None:
                # linear approximation of crossing point
                c_n = (exit_point[1] - longitude) / (exit_point[1] - entry_point[1])
                c_x = (longitude - entry_point[1]) / (exit_point[1] - entry_point[1])

                crossing_gp = normalize_geodetic_point(
                    np.array(
                        [
                            c_n * entry_point[0] + c_x * exit_point[0],
                            longitude,
                            c_n * entry_point[2] + c_x * exit_point[2],
                        ]
                    ),
                    tile.central_longitude,
                )

            crossing_lat = max(
                0,
                min(tile.latitude_rows - 1, tile.get_floor_latitude_index(crossing_gp[0])),
            )

            # adjust indices as the crossing point is by definition between the sub-tiles
            crossing_lon_before = crossing_lon - 1 if entry_lon <= exit_lon else crossing_lon
            crossing_lon_after = crossing_lon if entry_lon <= exit_lon else crossing_lon - 1

            if in_range(crossing_lon_before, entry_lon, exit_lon):
                # look for intersection
                if search_domain_size(
                    previous_lat, previous_lon, crossing_lat, crossing_lon_before
                ) < search_domain_size(entry_lat, entry_lon, exit_lat, exit_lon):
                    intersection = self.recurse_intersection(
                        depth + 1,
                        ellipsoid,
                        position,
                        los,
                        tile,
                        PointLatLonIndexes(previous_gp, previous_lat, previous_lon),
                        PointLatLonIndexes(crossing_gp, crossing_lat, crossing_lon_before),
                    )
                else:
                    # we failed to reduce domain size, probably due to numerical problems
                    intersection = DuvenhageAlgorithm.no_recurse_intersection(
                        ellipsoid,
                        position,
                        los,
                        tile,
                        PointLatLonIndexes(previous_gp, previous_lat, previous_lon),
                        crossing_lat,
                        crossing_lon_before,
                    )

                if intersection is None:
                    return intersection

            # prepare next segment
            previous_gp = crossing_gp
            previous_lat = crossing_lat
            previous_lon = crossing_lon_after

        return None

    def recurse_intersection_longitude_crossings_vec(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
        tiles: List[MinMaxTreeTile],
        indexes: List[np.ndarray],
        entry_point_lat_lon: PointLatLonIndexes,
        exit_point_lat_lon: PointLatLonIndexes,
        depth: int,
    ) -> Union[np.ndarray, None]:
        """
        Recurse intersection through longitude crossings

        Parameters
        ----------
            ellipsoid: reference ellipsoid
            positions: pixels positions in ellipsoid frame
            los: pixels lines-of-sight in ellipsoid frame
            tiles: Digital Elevation Model tile
            indexes: indexes
            entry_point_lat_lon: entry points with its latitude and longitude indexes
            exit_point_lat_lon: exit points with its latitude and longitude indexes
            depth: recursion depth

        Returns
        -------
            points at which the lines first enter ground,
            or null if does not enter ground in the search sub-tile
        """
        # recurse through longitude crossings
        entry_point = entry_point_lat_lon.point
        entry_lat = entry_point_lat_lon.lat_index
        entry_lon = entry_point_lat_lon.lon_index

        exit_point = exit_point_lat_lon.point
        exit_lat = exit_point_lat_lon.lat_index
        exit_lon = exit_point_lat_lon.lon_index

        intersection = np.zeros(positions.shape) + np.nan

        for i, tile in enumerate(tiles):
            previous_lon = entry_lon
            # find the deepest level in the min/max kd-tree at which entry and exit share a sub-tile
            level = tile.get_merge_level_vec(
                entry_lat[indexes[i]], entry_lon[indexes[i]], exit_lat[indexes[i]], exit_lon[indexes[i]]
            )

            crossings_tab = tile.get_crossed_boundary_columns_vec(
                previous_lon[indexes[i]], exit_lon[indexes[i]], level + 1
            )

            for crossings in crossings_tab:
                previous_gp = entry_point
                previous_lat = entry_lat
                previous_lon = entry_lon
                for crossing_lon in crossings:
                    # compute segment endpoints
                    longitude = tile.get_longitude_at_index(crossing_lon)

                    crossing_gp = np.zeros(positions.shape) + np.nan
                    if not self._flat_body:
                        # full computation of crossing point
                        # (point_at_longitude_vec() outputs nan where no crossing happens)
                        crossing_p = ellipsoid.point_at_longitude_vec(
                            positions, los, np.repeat(longitude, positions[:, 0].size)
                        )
                        # in some very rare cases of numerical noise, we miss the crossing point
                        ind_cross = np.where(~np.isnan(crossing_p[:, 0]))[0]
                        crossing_gp[ind_cross] = ellipsoid.transform_vec(
                            crossing_p[ind_cross], ellipsoid.body_frame, tile.central_longitude
                        )

                    ind_nan = np.where(np.isnan(crossing_gp[:, 0]))[0]
                    if len(ind_nan) > 0:
                        # linear approximation of crossing point
                        c_n = (exit_point[ind_nan, 1] - longitude) / (exit_point[ind_nan, 1] - entry_point[ind_nan, 1])
                        c_x = (longitude - entry_point[ind_nan, 1]) / (exit_point[ind_nan, 1] - entry_point[ind_nan, 1])

                        crossing_gp[ind_nan, :] = normalize_geodetic_point(
                            np.array(
                                [
                                    c_n * entry_point[ind_nan, 0] + c_x * exit_point[ind_nan, 0],
                                    np.repeat(longitude, len(ind_nan)),
                                    c_n * entry_point[ind_nan, 2] + c_x * exit_point[ind_nan, 2],
                                ]
                            ).T,
                            tile.central_longitude,
                        )

                    crossing_lat = np.fmax(
                        0,
                        np.fmin(tile.latitude_rows - 1, tile.get_floor_latitude_index_arr(crossing_gp[:, 0])),
                    )

                    # adjust indices as the crossing point is by definition between the sub-tiles
                    crossing_lon_before = np.where(entry_lon <= exit_lon, crossing_lon - 1, crossing_lon)
                    crossing_lon_after = np.where(entry_lon <= exit_lon, crossing_lon, crossing_lon - 1)

                    ind_in_range = np.where(in_range_vec(crossing_lon_before, entry_lon, exit_lon))[0]

                    ind_search_domain_inf = np.where(
                        search_domain_size_vec(
                            previous_lat[ind_in_range],
                            previous_lon[ind_in_range],
                            crossing_lat[ind_in_range],
                            crossing_lon_before[ind_in_range],
                        )
                        < search_domain_size_vec(
                            entry_lat[ind_in_range],
                            entry_lon[ind_in_range],
                            exit_lat[ind_in_range],
                            exit_lon[ind_in_range],
                        )
                    )[0]
                    ind_search_domain_sup = np.where(
                        search_domain_size_vec(
                            previous_lat[ind_in_range],
                            previous_lon[ind_in_range],
                            crossing_lat[ind_in_range],
                            crossing_lon_before[ind_in_range],
                        )
                        >= search_domain_size_vec(
                            entry_lat[ind_in_range],
                            entry_lon[ind_in_range],
                            exit_lat[ind_in_range],
                            exit_lon[ind_in_range],
                        )
                    )[0]

                    if len(ind_in_range) > 0:
                        if len(ind_search_domain_inf) > 0:
                            # sub_indexes = np.intersect1d(indexes[i], ind_in_range[ind_search_domain_inf])
                            intersection[ind_in_range[ind_search_domain_inf], :] = self.recurse_intersection_vec(
                                depth + 1,
                                ellipsoid,
                                positions,
                                los,
                                tile,
                                PointLatLonIndexes(previous_gp, previous_lat, previous_lon),
                                PointLatLonIndexes(crossing_gp, crossing_lat, crossing_lon_before),
                            )[ind_in_range[ind_search_domain_inf], :]

                        if len(ind_search_domain_sup) > 0:
                            # sub_indexes = np.intersect1d(indexes[i], ind_in_range[ind_search_domain_sup])
                            intersection[ind_in_range[ind_search_domain_sup], :] = self.no_recurse_intersection_vec(
                                ellipsoid,
                                positions[ind_in_range[ind_search_domain_sup], :],
                                los[ind_in_range[ind_search_domain_sup], :],
                                tile,
                                PointLatLonIndexes(
                                    previous_gp[ind_in_range[ind_search_domain_sup], :],
                                    previous_lat[ind_in_range[ind_search_domain_sup]],
                                    previous_lon[ind_in_range[ind_search_domain_sup]],
                                ),
                                crossing_lat[ind_in_range[ind_search_domain_sup]],
                                crossing_lon_before[ind_in_range[ind_search_domain_sup]],
                            )

                        # sub_indexes = np.intersect1d(indexes[i], ind_in_range)
                        if not np.all(np.isnan(intersection[ind_in_range, :])):
                            return intersection

                    # prepare next segment
                    previous_gp = crossing_gp
                    previous_lat = crossing_lat
                    previous_lon = crossing_lon_after

        return None

    def recurse_intersection_latitude_crossings(
        self,
        ellipsoid: ExtendedEllipsoid,
        position: np.ndarray,
        los: np.ndarray,
        tile: MinMaxTreeTile,
        entry_point_lat_lon: PointLatLonIndexes,
        exit_point_lat_lon: PointLatLonIndexes,
        depth: int,
    ) -> Union[np.ndarray, None]:
        """
        recurse intersection through latitude crossings

        Parameters
        ----------
            ellipsoid: reference ellipsoid
            position: pixel position in ellipsoid frame
            los: pixel line-of-sight in ellipsoid frame
            tile: Digital Elevation Model tile
            entry_point_lat_lon: entry point with its latitude and longitude indexes
            exit_point_lat_lon: exit point with its latitude and longitude indexes
            depth: recursion depth

        Returns
        -------
            point at which the line first enters ground,
            or null if does not enter ground in the search sub-tile
        """
        entry_point = entry_point_lat_lon.point
        entry_lat = entry_point_lat_lon.lat_index
        entry_lon = entry_point_lat_lon.lon_index

        exit_point = exit_point_lat_lon.point
        exit_lat = exit_point_lat_lon.lat_index
        exit_lon = exit_point_lat_lon.lon_index

        previous_gp = entry_point
        previous_lat = entry_lat
        previous_lon = entry_lon

        # find the deepest level in the min/max kd-tree at which entry and exit share a sub-tile
        level = tile.get_merge_level(entry_lat, entry_lon, exit_lat, exit_lon)

        # recurse through latitude crossings
        angular_margin = DuvenhageAlgorithm.STEP / ellipsoid.equatorial_radius
        crossings = tile.get_crossed_boundary_rows(previous_lat, exit_lat, level + 1)

        for crossing_lat in crossings:
            # compute segment endpoints
            latitude = tile.get_latitude_at_index(crossing_lat)

            if (latitude >= min(entry_point[0], exit_point[0] - angular_margin)) & (
                latitude <= max(entry_point[0], exit_point[0] + angular_margin)
            ):
                crossing_gp = None
                if self._flat_body:
                    # full computation of crossing point
                    try:
                        crossing_p = ellipsoid.point_at_latitude(
                            position,
                            los,
                            tile.get_latitude_at_index(crossing_lat),
                            ellipsoid.transform_vec(entry_point),
                        )
                        crossing_gp = ellipsoid.transform_vec(crossing_p, ellipsoid.body_frame, tile.central_longitude)
                    except PyRuggedError:
                        # in some very rare cases of numerical noise, we miss the crossing point
                        crossing_gp = None

                if crossing_gp is None:
                    # linear approximation of crossing point
                    c_n = (exit_point[0] - latitude) / (exit_point[0] - entry_point[0])
                    c_x = (latitude - entry_point[0]) / (exit_point[0] - entry_point[0])

                    crossing_gp = normalize_geodetic_point(
                        np.array(
                            [
                                latitude,
                                c_n * entry_point[1] + c_x * exit_point[1],
                                c_n * entry_point[2] + c_x * exit_point[2],
                            ]
                        ),
                        tile.central_longitude,
                    )

                crossing_lon = max(
                    0,
                    min(tile.longitude_columns - 1, tile.get_floor_longitude_index(crossing_gp[1])),
                )

                # adjust indices as the crossing point is by definition between the sub-tiles
                crossing_lat_before = crossing_lat - 1 if entry_lat <= exit_lat else crossing_lat
                crossing_lat_after = crossing_lat if entry_lat <= exit_lat else crossing_lat - 1

                if in_range(crossing_lat_before, entry_lat, exit_lat):
                    # look for intersection
                    if search_domain_size(
                        previous_lat, previous_lon, crossing_lat_before, crossing_lon
                    ) < search_domain_size(entry_lat, entry_lon, exit_lat, exit_lon):
                        intersection = self.recurse_intersection(
                            depth + 1,
                            ellipsoid,
                            position,
                            los,
                            tile,
                            PointLatLonIndexes(previous_gp, previous_lat, previous_lon),
                            PointLatLonIndexes(crossing_gp, crossing_lat_before, crossing_lon),
                        )
                    else:
                        intersection = DuvenhageAlgorithm.no_recurse_intersection(
                            ellipsoid,
                            position,
                            los,
                            tile,
                            PointLatLonIndexes(previous_gp, previous_lat, previous_lon),
                            crossing_lat_before,
                            crossing_lon,
                        )

                    if intersection is not None:
                        return intersection

                # prepare next segment
                previous_gp = crossing_gp
                previous_lat = crossing_lat_after
                previous_lon = crossing_lon

        return None

    def recurse_intersection_latitude_crossings_vec(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
        tiles: List[MinMaxTreeTile],
        indexes: List[np.ndarray],
        entry_point_lat_lon: PointLatLonIndexes,
        exit_point_lat_lon: PointLatLonIndexes,
        depth: int,
    ) -> Union[np.ndarray, None]:
        """
        recurse intersection through latitude crossings

        Parameters
        ----------
            ellipsoid: reference ellipsoid
            positions: pixel position in ellipsoid frame
            los: pixel line-of-sight in ellipsoid frame
            tiles: Digital Elevation Model tiles
            indexes: indexes
            entry_point_lat_lon: entry point with its latitude and longitude indexes
            exit_point_lat_lon: exit point with its latitude and longitude indexes
            depth: recursion depth

        Returns
        -------
            points at which the lines first enter ground,
            or null if does not enter ground in the search sub-tile
        """
        entry_point = entry_point_lat_lon.point
        entry_lat = entry_point_lat_lon.lat_index
        entry_lon = entry_point_lat_lon.lon_index

        exit_point = exit_point_lat_lon.point
        exit_lat = exit_point_lat_lon.lat_index
        exit_lon = exit_point_lat_lon.lon_index

        previous_lat = entry_lat

        angular_margin = DuvenhageAlgorithm.STEP / ellipsoid.equatorial_radius
        intersection = np.zeros(positions.shape) + np.nan

        for i, tile in enumerate(tiles):
            # find the deepest level in the min/max kd-tree at which entry and exit share a sub-tile
            level = tile.get_merge_level_vec(
                entry_lat[indexes[i]], entry_lon[indexes[i]], exit_lat[indexes[i]], exit_lon[indexes[i]]
            )

            crossings_tab = tile.get_crossed_boundary_rows_vec(
                previous_lat[indexes[i]], exit_lat[indexes[i]], level + 1
            )

            for crossings in crossings_tab:
                previous_gp = entry_point
                previous_lat = entry_lat
                previous_lon = entry_lon
                for crossing_lat in crossings:
                    # compute segment endpoints
                    latitude = tile.get_latitude_at_index(crossing_lat)

                    lat_min = np.fmin(entry_point[:, 0], exit_point[:, 0] - angular_margin)
                    lat_max = np.fmax(entry_point[:, 0], exit_point[:, 0] + angular_margin)
                    ind_ok = np.intersect1d(np.where(latitude >= lat_min)[0], np.where(latitude <= lat_max)[0])
                    crossing_gp = np.zeros(positions.shape) + np.nan
                    if not self._flat_body:
                        # full computation of crossing point
                        # point_at_latitude_vec() returns NaN where no crossing has been found
                        crossing_p = ellipsoid.point_at_latitude_vec(
                            positions[ind_ok, :],
                            los[ind_ok, :],
                            np.repeat(latitude, ind_ok.size),
                            ellipsoid.transform_vec(entry_point[ind_ok, :]),
                        )
                        # in some very rare cases of numerical noise, we miss the crossing point
                        ind_cross = np.where(~np.isnan(crossing_p[:, 0]))[0]
                        crossing_gp[ind_ok[ind_cross], :] = ellipsoid.transform_vec(
                            crossing_p[ind_cross], ellipsoid.body_frame, tile.central_longitude
                        )

                    ind_nan = np.where(np.isnan(crossing_gp[ind_ok, 0]))[0]
                    # linear approximation of crossing point
                    c_n = (exit_point[ind_ok[ind_nan], 0] - latitude) / (
                        exit_point[ind_ok[ind_nan], 0] - entry_point[ind_ok[ind_nan], 0]
                    )
                    c_x = (latitude - entry_point[ind_ok[ind_nan], 0]) / (
                        exit_point[ind_ok[ind_nan], 0] - entry_point[ind_ok[ind_nan], 0]
                    )

                    crossing_gp[ind_ok[ind_nan], :] = normalize_geodetic_point(
                        np.array(
                            [
                                np.repeat(latitude, len(ind_ok[ind_nan])),
                                c_n * entry_point[ind_ok[ind_nan], 1] + c_x * exit_point[ind_ok[ind_nan], 1],
                                c_n * entry_point[ind_ok[ind_nan], 2] + c_x * exit_point[ind_ok[ind_nan], 2],
                            ]
                        ).T,
                        tile.central_longitude,
                    )

                    crossing_lon = np.fmax(
                        0,
                        np.fmin(
                            tile.longitude_columns - 1, tile.get_floor_longitude_index_arr(crossing_gp[:, 1][ind_ok])
                        ),
                    )

                    # adjust indices as the crossing point is by definition between the sub-tiles
                    crossing_lat_before = np.where(
                        entry_lat[ind_ok] <= exit_lat[ind_ok], crossing_lat - 1, crossing_lat
                    )
                    crossing_lat_after = np.where(entry_lat[ind_ok] <= exit_lat[ind_ok], crossing_lat, crossing_lat - 1)

                    ind_in_range = np.where(in_range_vec(crossing_lat_before, entry_lat[ind_ok], exit_lat[ind_ok]))[0]

                    ind_search_domain_inf = np.where(
                        search_domain_size_vec(
                            previous_lat[ind_ok[ind_in_range]],
                            previous_lon[ind_ok[ind_in_range]],
                            crossing_lat_before[ind_in_range],
                            crossing_lon[ind_in_range],
                        )
                        < search_domain_size_vec(
                            entry_lat[ind_ok[ind_in_range]],
                            entry_lon[ind_ok[ind_in_range]],
                            exit_lat[ind_ok[ind_in_range]],
                            exit_lon[ind_ok[ind_in_range]],
                        )
                    )[0]
                    ind_search_domain_sup = np.where(
                        search_domain_size_vec(
                            previous_lat[ind_ok[ind_in_range]],
                            previous_lon[ind_ok[ind_in_range]],
                            crossing_lat_before[ind_in_range],
                            crossing_lon[ind_in_range],
                        )
                        >= search_domain_size_vec(
                            entry_lat[ind_ok[ind_in_range]],
                            entry_lon[ind_ok[ind_in_range]],
                            exit_lat[ind_ok[ind_in_range]],
                            exit_lon[ind_ok[ind_in_range]],
                        )
                    )[0]

                    sub_indexes = np.intersect1d(indexes[i], ind_ok[ind_in_range[ind_search_domain_inf]])
                    intersection[sub_indexes, :] = self.recurse_intersection_vec(
                        depth + 1,
                        ellipsoid,
                        positions,
                        los,
                        tile,
                        PointLatLonIndexes(previous_gp, previous_lat, previous_lon),
                        PointLatLonIndexes(crossing_gp, crossing_lat_before, crossing_lon),
                    )

                    sub_indexes = np.intersect1d(indexes[i], ind_ok[ind_in_range[ind_search_domain_sup]])
                    intersection[sub_indexes, :] = self.no_recurse_intersection_vec(
                        ellipsoid,
                        positions[sub_indexes, :],
                        los[sub_indexes, :],
                        tile,
                        PointLatLonIndexes(
                            previous_gp[sub_indexes, :], previous_lat[sub_indexes], previous_lon[sub_indexes]
                        ),
                        crossing_lat_before[sub_indexes],
                        crossing_lon[sub_indexes],
                    )

                    if np.all(intersection[indexes[i][ind_ok[ind_in_range]], :] != np.nan):
                        return intersection

                    # prepare next segment
                    previous_gp = crossing_gp
                    previous_lat = crossing_lat_after
                    previous_lon = crossing_lon

        return None

    def recurse_intersection(
        self,
        depth: int,
        ellipsoid: ExtendedEllipsoid,
        position: np.ndarray,
        los: np.ndarray,
        tile: MinMaxTreeTile,
        entry_point_lat_lon: PointLatLonIndexes,
        exit_point_lat_lon: PointLatLonIndexes,
    ) -> Union[None, np.ndarray]:
        """
        Compute intersection of line with Digital Elevation Model in a sub-tile.


        Parameters
        ----------
            depth: recursion depth
            ellipsoid: reference ellipsoid
            position: pixel position in ellipsoid frame
            los: pixel line-of-sight in ellipsoid frame
            tile: Digital Elevation Model tile
            entry_point_lat_lon: line-of-sight entry point in the sub-tile
            exit_point_lat_lon: line-of-sight exit point from the sub-tile

        Returns
        -------
            point at which the line first enters ground, or null if does not enter ground in
            the search sub-tile

        """
        entry_point = entry_point_lat_lon.point
        entry_lat = entry_point_lat_lon.lat_index
        entry_lon = entry_point_lat_lon.lon_index
        exit_point = exit_point_lat_lon.point
        exit_lat = exit_point_lat_lon.lat_index
        exit_lon = exit_point_lat_lon.lon_index

        if depth > 30:
            # this should never happen
            raise PyRuggedInternalError

        if search_domain_size(entry_lat, entry_lon, exit_lat, exit_lon) < 4:
            # we have narrowed the search down to a few cells
            return DuvenhageAlgorithm.no_recurse_intersection(
                ellipsoid,
                position,
                los,
                tile,
                PointLatLonIndexes(entry_point, entry_lat, entry_lon),
                exit_lat,
                exit_lon,
            )

        # find the deepest level in the min/max kd-tree at which entry and exit share a sub-tile
        level = tile.get_merge_level(entry_lat, entry_lon, exit_lat, exit_lon)

        if level >= 0 and exit_point[2] >= tile.get_max_elevation(exit_lat, exit_lon, level):
            # the line-of-sight segment is fully above Digital Elevation Model
            # we can safely reject it and proceed to next part of the line-of-sight
            return None

        previous_gp = entry_point
        previous_lat = entry_lat
        previous_lon = entry_lon

        # introduce all intermediate points corresponding to the line-of-sight
        # intersecting the boundary between level 0 sub-tiles
        if tile.is_column_merging(level + 1):
            self.recurse_intersection_longitude_crossings(
                ellipsoid, position, los, tile, entry_point_lat_lon, exit_point_lat_lon, depth
            )

        else:
            self.recurse_intersection_latitude_crossings(
                ellipsoid, position, los, tile, entry_point_lat_lon, exit_point_lat_lon, depth
            )

        if in_range(previous_lat, entry_lat, exit_lat) and in_range(previous_lon, entry_lon, exit_lon):
            # last part of the segment, up to exit point
            if search_domain_size(previous_lat, previous_lon, exit_lat, exit_lon) < search_domain_size(
                entry_lat, entry_lon, exit_lat, exit_lon
            ):
                intersection = self.recurse_intersection(
                    depth + 1,
                    ellipsoid,
                    position,
                    los,
                    tile,
                    PointLatLonIndexes(previous_gp, previous_lat, previous_lon),
                    PointLatLonIndexes(exit_point, exit_lat, exit_lon),
                )
            else:
                intersection = DuvenhageAlgorithm.no_recurse_intersection(
                    ellipsoid,
                    position,
                    los,
                    tile,
                    PointLatLonIndexes(previous_gp, previous_lat, previous_lon),
                    exit_lat,
                    exit_lon,
                )

        else:
            intersection = None

        return intersection

    def recurse_intersection_vec(
        self,
        depth: int,
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
        tile: MinMaxTreeTile,
        entry_point_lat_lon: PointLatLonIndexes,
        exit_point_lat_lon: PointLatLonIndexes,
    ) -> Union[None, np.ndarray]:
        """
        Compute intersection of line with Digital Elevation Model in a sub-tile.


        Parameters
        ----------
            depth: recursion depth
            ellipsoid: reference ellipsoid
            positions: pixels positions in ellipsoid frame
            los: pixels lines-of-sight in ellipsoid frame
            tile: Digital Elevation Model tile
            entry_point_lat_lon: lines-of-sight entry points in the sub-tiles
            exit_point_lat_lon: line-sof-sight exit points from the sub-tiles

        Returns
        -------
            points at which the line first enters ground, or null if does not enter ground in
            the search sub-tiles

        """
        entry_point = entry_point_lat_lon.point
        entry_lat = entry_point_lat_lon.lat_index
        entry_lon = entry_point_lat_lon.lon_index
        exit_point = exit_point_lat_lon.point
        exit_lat = exit_point_lat_lon.lat_index
        exit_lon = exit_point_lat_lon.lon_index

        intersections = np.zeros(positions.shape) + np.nan
        if depth > 30:
            # this should never happen
            raise PyRuggedInternalError

        sizes = search_domain_size_vec(entry_lat, entry_lon, exit_lat, exit_lon)
        ind_inf_4 = np.where(sizes < 4)[0]
        ind_sup_4 = np.where(sizes >= 4)[0]
        if len(ind_inf_4) > 0:
            intersections[ind_inf_4, :] = self.no_recurse_intersection_vec(
                ellipsoid,
                positions[ind_inf_4, :],
                los[ind_inf_4, :],
                tile,
                PointLatLonIndexes(entry_point[ind_inf_4, :], entry_lat[ind_inf_4], entry_lon[ind_inf_4]),
                exit_lat[ind_inf_4],
                exit_lon[ind_inf_4],
            )

        if len(ind_sup_4) > 0:
            level = np.zeros(entry_lat.shape)
            # is_column_merging = np.zeros(entry_lat.shape)
            # find the deepest level in the min/max kd-tree at which entry and exit share a sub-tile
            level[ind_sup_4] = tile.get_merge_level_vec(
                entry_lat[ind_sup_4], entry_lon[ind_sup_4], exit_lat[ind_sup_4], exit_lon[ind_sup_4]
            )
            max_elevation = tile.get_max_elevation_vec(exit_lat[ind_sup_4], exit_lon[ind_sup_4], level[ind_sup_4])
            # is_column_merging[indexes[i]] = tile.is_column_merging_vec(level[indexes[i]] + 1)

            ind_reject = np.intersect1d(
                np.where(level[ind_sup_4] >= 0)[0], np.where(exit_point[ind_sup_4, 2] >= max_elevation)[0]
            )
            intersections[ind_sup_4[ind_reject], :] = np.nan

            previous_gp = entry_point
            previous_lat = entry_lat
            previous_lon = entry_lon

            # # introduce all intermediate points corresponding to the line-of-sight
            # # intersecting the boundary between level 0 sub-tiles
            # ind_lon_crossings = np.where(is_column_merging)[0]
            # ind_lat_crossings = np.where(is_column_merging is False)[0]
            # if len(ind_lon_crossings) > 0:
            #     # sub_indexes = [np.intersect1d(indexes[j], ind_lon_crossings) for j in range(len(indexes))]
            #     res = self.recurse_intersection_longitude_crossings_vec(
            #         ellipsoid, positions,
            #         los, tiles, indexes,
            #         PointLatLonIndexes(entry_point,
            #                            entry_lat,
            #                            entry_lon),
            #         PointLatLonIndexes(exit_point,
            #                            exit_lat,
            #                            exit_lon),
            #         depth
            #     )
            #     if res is not None:
            #         intersections[ind_lon_crossings, :] = res[ind_lon_crossings, :]
            #
            # if len(ind_lat_crossings) > 0:
            #     # sub_indexes = [np.intersect1d(indexes[j], ind_lat_crossings) for j in range(len(indexes))]
            #     res = self.recurse_intersection_latitude_crossings_vec(
            #         ellipsoid, positions,
            #         los, tiles, indexes,
            #         PointLatLonIndexes(entry_point,
            #                            entry_lat,
            #                            entry_lon),
            #         PointLatLonIndexes(exit_point,
            #                            exit_lat,
            #                            exit_lon),
            #         depth
            #     )
            #     if res is not None:
            #         intersections[ind_lat_crossings, :] = res[ind_lat_crossings, :]

            ind_in_range = np.intersect1d(
                np.where(in_range_vec(previous_lat[ind_sup_4], entry_lat[ind_sup_4], exit_lat[ind_sup_4]))[0],
                np.where(in_range_vec(previous_lon[ind_sup_4], entry_lon[ind_sup_4], exit_lon[ind_sup_4]))[0],
            )

            ind_not_in_range = np.union1d(
                np.where(~in_range_vec(previous_lat[ind_sup_4], entry_lat[ind_sup_4], exit_lat[ind_sup_4]))[0],
                np.where(~in_range_vec(previous_lon[ind_sup_4], entry_lon[ind_sup_4], exit_lon[ind_sup_4]))[0],
            )

            ind_search_domain_inf = np.where(
                search_domain_size_vec(
                    previous_lat[ind_sup_4][ind_in_range],
                    previous_lon[ind_sup_4][ind_in_range],
                    exit_lat[ind_sup_4][ind_in_range],
                    exit_lon[ind_sup_4][ind_in_range],
                )
                < search_domain_size_vec(
                    entry_lat[ind_sup_4][ind_in_range],
                    entry_lon[ind_sup_4][ind_in_range],
                    exit_lat[ind_sup_4][ind_in_range],
                    exit_lon[ind_sup_4][ind_in_range],
                )
            )[0]
            ind_search_domain_sup = np.where(
                search_domain_size_vec(
                    previous_lat[ind_sup_4][ind_in_range],
                    previous_lon[ind_sup_4][ind_in_range],
                    exit_lat[ind_sup_4][ind_in_range],
                    exit_lon[ind_sup_4][ind_in_range],
                )
                >= search_domain_size_vec(
                    entry_lat[ind_sup_4][ind_in_range],
                    entry_lon[ind_sup_4][ind_in_range],
                    exit_lat[ind_sup_4][ind_in_range],
                    exit_lon[ind_sup_4][ind_in_range],
                )
            )[0]

            if len(ind_in_range) > 0:
                if len(ind_search_domain_inf) > 0:
                    ind_to_apply = ind_sup_4[ind_in_range][ind_search_domain_inf]
                    intersections[ind_to_apply, :] = self.recurse_intersection_vec(
                        depth + 1,
                        ellipsoid,
                        positions[ind_to_apply, :],
                        los[ind_to_apply, :],
                        tile,
                        PointLatLonIndexes(
                            previous_gp[ind_to_apply, :], previous_lat[ind_to_apply], previous_lon[ind_to_apply]
                        ),
                        PointLatLonIndexes(exit_point[ind_to_apply, :], exit_lat[ind_to_apply], exit_lon[ind_to_apply]),
                    )

                if len(ind_search_domain_sup) > 0:
                    ind_to_apply = ind_sup_4[ind_in_range][ind_search_domain_sup]
                    intersections[ind_to_apply, :] = self.no_recurse_intersection_vec(
                        ellipsoid,
                        positions[ind_to_apply, :],
                        los[ind_to_apply, :],
                        tile,
                        PointLatLonIndexes(
                            previous_gp[ind_to_apply, :], previous_lat[ind_to_apply], previous_lon[ind_to_apply]
                        ),
                        exit_lat[ind_to_apply],
                        exit_lon[ind_to_apply],
                    )

            if len(ind_not_in_range) > 0:
                intersections[ind_sup_4[ind_not_in_range], :] = np.nan

        return intersections

    @staticmethod
    def no_recurse_intersection(
        ellipsoid: ExtendedEllipsoid,
        position: np.ndarray,
        los: np.ndarray,
        tile: MinMaxTreeTile,
        entry: PointLatLonIndexes,
        exit_lat: int,
        exit_lon: int,
    ) -> Union[None, np.ndarray]:
        """
        Compute intersection of line with Digital Elevation Model in a sub-tile, without recursion.

        Parameters
        ----------
            ellipsoid: reference ellipsoid
            position: pixel position in ellipsoid frame
            los: pixel line-of-sight in ellipsoid frame
            tile: Digital Elevation Model tile
            entry: line-of-sight entry point in the sub-tile
            exit_lat: index to use for interpolating exit point elevation
            exit_lon: index to use for interpolating exit point elevation

        Returns
        -------
            point at which the line first enters ground,
            or null if does not enter ground in the search sub-tile
        """
        entry_point = entry.point
        entry_lat = entry.lat_index
        entry_lon = entry.lon_index

        intersection_gp = None
        intersection_dot = math.inf

        for i in range(min(entry_lat, exit_lat), max(entry_lat, exit_lat) + 1):
            for j in range(min(entry_lon, exit_lon), max(entry_lon, exit_lon) + 1):
                gp_improved = DuvenhageAlgorithm.compute_ground_point(ellipsoid, position, los, tile, i, j, entry_point)
                if gp_improved is not None:
                    dot_p = gp_improved[1]
                    if dot_p < intersection_dot:
                        intersection_gp = gp_improved[0]
                        intersection_dot = dot_p
        return intersection_gp

    @staticmethod
    def no_recurse_intersection_vec_alt(
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
        tile: MinMaxTreeTile,
        entry: PointLatLonIndexes,
        exit_lat: np.ndarray,
        exit_lon: np.ndarray,
    ) -> Union[None, np.ndarray]:
        """
        Compute intersection of line with Digital Elevation Model in a sub-tile, without recursion.

        Parameters
        ----------
            ellipsoid: reference ellipsoid
            positions: pixel positions in ellipsoid frame
            los: pixels lines-of-sight in ellipsoid frame
            tile: Digital Elevation Model tile
            entry: line-of-sight entry points in the sub-tile
            exit_lat: indexes to use for interpolating exit point elevation
            exit_lon: indexes to use for interpolating exit point elevation

        Returns
        -------
            point at which the line first enters ground,
            or null if does not enter ground in the search sub-tile
        """
        entry_point = entry.point
        entry_lat = entry.lat_index
        entry_lon = entry.lon_index

        min_lat = np.fmin(entry_lat, exit_lat)
        max_lat = np.fmax(entry_lat, exit_lat)
        min_lon = np.fmin(entry_lon, exit_lon)
        max_lon = np.fmax(entry_lon, exit_lon)

        intersection_gp = np.zeros(positions.shape) + np.nan

        converted_los = ellipsoid.convert_los_from_point_vec(entry_point, los)

        ind_ok = np.where(np.isfinite(entry_point[:, 0]))[0]

        for i in ind_ok:
            lat_range = np.arange(int(min_lat[i]), int(max_lat[i]) + 1)
            lon_range = np.arange(int(min_lon[i]), int(max_lon[i]) + 1)
            # interleave ranges
            lat_indexes = np.repeat(lat_range, lon_range.size)
            lon_indexes = np.tile(lon_range, lat_range.size)

            intersection_gp[i, :] = DuvenhageAlgorithm.compute_ground_point_lighter(
                ellipsoid,
                positions[i, :],
                los[i, :],
                tile,
                lat_indexes,
                lon_indexes,
                entry_point[i, :],
                converted_los[i, :],
            )

        return intersection_gp

    def no_recurse_intersection_vec(
        self,  # pylint: disable=too-many-locals
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
        tile: MinMaxTreeTile,
        entry: PointLatLonIndexes,
        exit_lat: np.ndarray,
        exit_lon: np.ndarray,
    ) -> Union[None, np.ndarray]:
        """
        Compute intersection of line with Digital Elevation Model in a sub-tile, without recursion.

        Parameters
        ----------
            ellipsoid: reference ellipsoid
            positions: pixel positions in ellipsoid frame
            los: pixels lines-of-sight in ellipsoid frame
            tile: Digital Elevation Model tile
            entry: line-of-sight entry points in the sub-tile
            exit_lat: indexes to use for interpolating exit point elevation
            exit_lon: indexes to use for interpolating exit point elevation

        Returns
        -------
            point at which the line first enters ground,
            or null if does not enter ground in the search sub-tile
        """
        entry_point = entry.point
        entry_lat = entry.lat_index
        entry_lon = entry.lon_index

        np_points = len(entry_lat)
        min_lat = np.fmin(entry_lat, exit_lat).astype(int)
        max_lat = np.fmax(entry_lat, exit_lat).astype(int)
        min_lon = np.fmin(entry_lon, exit_lon).astype(int)
        max_lon = np.fmax(entry_lon, exit_lon).astype(int)

        size_i = max_lat - min_lat + 1
        size_j = max_lon - min_lon + 1

        len_i = np.max(size_i)
        len_j = np.max(size_j)

        # build per-point exploration ranges
        i_range_vec = np.tile(np.arange(len_i), np_points).reshape((np_points, len_i))
        j_range_vec = np.tile(np.arange(len_j), np_points).reshape((np_points, len_j))

        i_range_vec = i_range_vec % size_i[..., np.newaxis]
        j_range_vec = j_range_vec % size_j[..., np.newaxis]

        i_range_vec += min_lat[..., np.newaxis]
        j_range_vec += min_lon[..., np.newaxis]

        i_lat_range = np.repeat(i_range_vec, len_j, axis=1)
        i_lon_range = np.tile(j_range_vec, len_i)

        # Note: for the sake of having a square exploration matrix (lat/lon range), it is possible
        # that some exploration values are duplicated. It would be better to leave NaNs and skip
        # them in the loop

        intersection_gp = np.zeros(positions.shape) + np.nan
        intersection_dot = np.zeros(positions.shape[0]) + np.inf

        for j in range(len_i * len_j):
            res = DuvenhageAlgorithm.compute_ground_point_vec(
                ellipsoid, positions[:, :], los[:, :], tile, i_lat_range[:, j], i_lon_range[:, j], entry_point[:, :]
            )

            if np.any(~np.isnan(res[1])):
                gp_res_vec, dotp_vec = res

                ind = np.where(dotp_vec < intersection_dot)
                intersection_gp[ind, :] = gp_res_vec[ind, :]
                intersection_dot[ind] = dotp_vec[ind]

        # for i in range(len(entry_lat)):
        #     for i_vec in i_range_vec[i]:
        #         for j_vec in j_range_vec[i]:
        #             if not np.isnan(entry_point[i, 0]):
        #                 res = DuvenhageAlgorithm.compute_ground_point(
        #                     ellipsoid, positions[i, :], los[i, :], tile, i_vec, j_vec,
        #                     entry_point[i, :]
        #                 )
        #                 if res is not None:
        #                     gp_res_vec[i, :], dotp_vec[i] = res
        #
        #                     if dotp_vec[i] < intersection_dot[i]:
        #                         intersection_gp[i, :] = gp_res_vec[i, :]
        #                         intersection_dot[i] = dotp_vec[i]
        #                     # ind = np.where(dotp_vec < intersection_dot)
        #                     # intersection_gp[ind, :] = gp_res_vec[ind, :]
        #                     # intersection_dot[ind] = dotp_vec[ind]

        return intersection_gp
