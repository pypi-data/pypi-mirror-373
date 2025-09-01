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
# limitations under the Licen
#

"""pyrugged Class SimpleTile"""

import math

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals, too-many-public-methods, chained-comparison
# pylint: disable=no-name-in-module
from typing import List

import numpy as np

from pyrugged.bodies.geodesy import normalize_geodetic_point
from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.raster.location import Location
from pyrugged.utils.math_utils import (
    cell_intersection_func,
    cell_intersection_vec_func,
    interpolate_func,
    normalize_angle,
    normalize_angle_vec,
)


class SimpleTile:
    """Simple implementation of a tile."""

    TOLERANCE = 1.0 / 8.0

    def __init__(self):
        """Builds a new instance."""

        self._min_latitude = 0.0
        self._min_longitude = 0.0
        self._latitude_step = 0
        self._longitude_step = 0
        self._latitude_rows = 0
        self._longitude_columns = 0
        self._min_elevation = 0.0
        self._min_elevation_latitude_index = None
        self._min_elevation_longitude_index = None
        self._max_elevation = 0.0
        self._max_elevation_latitude_index = None
        self._max_elevation_longitude_index = None
        self._cached_elevation = True

        self._elevations = None

    # pylint: disable=unbalanced-tuple-unpacking
    def _eval_cache_elevation(self):
        self._min_elevation_latitude_index, self._min_elevation_longitude_index = np.unravel_index(
            np.nanargmin(self._elevations), self._elevations.shape
        )

        self._min_elevation = self._elevations[self._min_elevation_latitude_index, self._min_elevation_longitude_index]

        self._max_elevation_latitude_index, self._max_elevation_longitude_index = np.unravel_index(
            np.nanargmax(self._elevations), self._elevations.shape
        )
        self._max_elevation = self._elevations[self._max_elevation_latitude_index, self._max_elevation_longitude_index]

        self._cached_elevation = True

    def set_geometry(
        self,
        new_min_latitude: float,
        new_min_longitude: float,
        new_latitude_step: float,
        new_longitude_step: float,
        new_latitude_rows: int,
        new_longitude_columns: int,
    ):
        """Set the tile global geometry.

        Parameters
        ----------
            new_min_latitude : minimum latitude (rad)
            new_min_longitude : minimum longitude (rad)
            new_latitude_step : step in latitude (size of one raster element) (rad)
            new_longitude_step : step in longitude (size of one raster element) (rad)
            new_latitude_rows : number of latitude rows
            new_longitude_columns : number of longitude columns
        """

        self._min_latitude = new_min_latitude
        self._min_longitude = new_min_longitude
        self._latitude_step = new_latitude_step
        self._longitude_step = new_longitude_step
        self._latitude_rows = new_latitude_rows
        self._longitude_columns = new_longitude_columns
        self._min_elevation = float("inf")
        self._min_elevation_latitude_index = -1
        self._min_elevation_longitude_index = -1
        self._max_elevation = float("-inf")
        self._max_elevation_latitude_index = -1
        self._max_elevation_longitude_index = -1
        self._cached_elevation = True

        if new_latitude_rows < 1 or new_longitude_columns < 1:
            raise PyRuggedError(PyRuggedMessages.EMPTY_TILE.value, new_latitude_rows, new_longitude_columns)

        self._elevations = np.full((new_latitude_rows, new_longitude_columns), np.nan)  # more convenient for my test.

    def tile_update_completed(self):
        """Hook called at the end of tile update completion."""
        self.process_updated_elevation(self._elevations.reshape(-1))  # ravel = flatten no copy

    def process_updated_elevation(self, elevations_list: List[float]):
        """Process elevation array at completion.

        Method is called at tile update completion, it is
        expected to be overridden by subclasses. The default
        implementation does nothing.

        Parameters
        ----------
            elevations_list : elevations list
        """

        # Do nothing by default

    @property
    def minimum_latitude(self) -> float:
        """Get minimum latitude of grid interpolation points.

        Returns
        -------
            result : minimum latitude of grid interpolation points (rad)
                (latitude of the center of the cells of South row)
        """

        return self.get_latitude_at_index(0)

    def get_latitude_at_index(self, latitude_index: int) -> float:
        """Get the latitude at some index.

        Parameters
        ----------
            latitude_index : latitude index

        Returns
        -------
            result : latitude at the specified index (rad)
                (latitude of the center of the cells of specified row)
        """

        return self._min_latitude + self.latitude_step * latitude_index

    def get_latitude_at_index_arr(self, latitude_index: np.ndarray) -> np.array:
        """Get the latitude at some index.

        Parameters
        ----------
            latitude_index : latitude index

        Returns
        -------
            result : latitude at the specified index (rad)
                (latitude of the center of the cells of specified row)
        """

        return self._min_latitude + self.latitude_step * latitude_index

    @property
    def maximum_latitude(self) -> float:
        """Get maximum latitude.

        Beware that as a point at maximum latitude is the northernmost
        one of the grid, it doesn't have a northwards neighbor and
        therefore calling getLocation(double, double) getLocation
        on such a latitude will return either Location.NORTH_WEST,
        Location.NORTH or Location.NORTH_EAST, but can
        never return Location.HAS_INTERPOLATION_NEIGHBORS

        Returns
        -------
            result : maximum latitude (rad)
                (latitude of the center of the cells of North row)
        """

        return self.get_latitude_at_index(self.latitude_rows - 1)

    @property
    def minimum_longitude(self) -> float:
        """Get minimum longitude.

        Returns
        -------
            result : minimum longitude (rad)
                (longitude of the center of the cells of West column)
        """

        return self.get_longitude_at_index(0)

    @property
    def central_longitude(self) -> float:
        """Get central longitude.

        Returns
        -------
            result : central longitude (rad)
                (longitude of the mean)
        """

        return (self.get_longitude_at_index(0) + self.get_longitude_at_index(self.longitude_columns - 1)) / 2.0

    def get_longitude_at_index(self, longitude_index: int) -> float:
        """Get the longitude at some index.

        Parameters
        ----------
            longitude_index : longitude index

        Returns
        -------
            result : longitude at the specified index (rad)
                (longitude of the center of the cells of specified column)
        """

        return float(self._min_longitude + self.longitude_step * longitude_index)

    def get_longitude_at_index_arr(self, longitude_index: np.ndarray) -> np.array:
        """Get the longitude at some index. Array version.

        Parameters
        ----------
            longitude_index : longitude index

        Returns
        -------
            result : longitude at the specified index (rad)
                (longitude of the center of the cells of specified column)
        """

        return self._min_longitude + self.longitude_step * longitude_index

    @property
    def maximum_longitude(self) -> float:
        """Get the maximum longitude.

        Beware that as a point at maximum longitude is the easternmost
        one of the grid, it doesn't have an eastwards neighbor and
        therefore calling getLocation(double, double) getLocation
        on such a longitude will return either Location.SOUTH_EAST,
        Location.EAST or Location.NORTH_EAST, but can
        never return Location.HAS_INTERPOLATION_NEIGHBORS

        Returns
        -------
            result : maximum longitude (rad)
                (longitude of the center of the cells of East column)
        """

        return self.get_longitude_at_index(self.longitude_columns - 1)

    @property
    def latitude_step(self) -> float:
        """Get step in latitude (size of one raster element)."""

        return self._latitude_step

    @property
    def longitude_step(self) -> float:
        """Get step in longitude (size of one raster element)."""

        return self._longitude_step

    @property
    def latitude_rows(self) -> int:
        """Get number of latitude rows."""

        return self._latitude_rows

    @property
    def longitude_columns(self) -> int:
        """Get number of longitude columns."""

        return self._longitude_columns

    @property
    def min_elevation(self) -> float:
        """Get the minimum elevation in the tile."""
        if not self._cached_elevation:
            self._eval_cache_elevation()

        return self._min_elevation

    @property
    def min_elevation_latitude_index(self) -> int:
        """Get the latitude index of min elevation."""
        if not self._cached_elevation:
            self._eval_cache_elevation()

        return self._min_elevation_latitude_index

    @property
    def min_elevation_longitude_index(self) -> int:
        """Get the longitude index of min elevation."""
        if not self._cached_elevation:
            self._eval_cache_elevation()

        return self._min_elevation_longitude_index

    @property
    def max_elevation(self) -> float:
        """Get the maximum elevation in the tile."""
        if not self._cached_elevation:
            self._eval_cache_elevation()

        return self._max_elevation

    @property
    def max_elevation_latitude_index(self) -> int:
        """Get the latitude index of max elevation."""
        if not self._cached_elevation:
            self._eval_cache_elevation()

        return self._max_elevation_latitude_index

    @property
    def max_elevation_longitude_index(self) -> int:
        """Get the longitude index of max elevation."""
        if not self._cached_elevation:
            self._eval_cache_elevation()

        return self._max_elevation_longitude_index

    def set_elevation(self, latitude_index: int, longitude_index: int, elevation: float):
        """Set the elevation of one raster element.

        BEWARE! The order of the indices follows geodetic conventions, i.e.
        the latitude is given first and longitude afterwards, so the first
        index specifies a row index with zero at South and max value
        at North, and the second index specifies a column index
        with zero at West and max value at East. This is not the
        same as some raster conventions (as our row index increases from South
        to North) and this is also not the same as Cartesian coordinates as
        our ordinate index appears before our abscissa index).

        Parameters
        ----------
            latitude_index : index of latitude (row index)
            longitude_index : index of longitude (column index)
            elevation : elevation (m)
        """

        if (
            (latitude_index < 0 or latitude_index > (self.latitude_rows - 1))
            or (longitude_index < 0)
            or (longitude_index > (self.longitude_columns - 1))
        ):
            raise PyRuggedError(
                PyRuggedMessages.OUT_OF_TILE_INDICES.value,
                latitude_index,
                longitude_index,
                self.latitude_rows - 1,
                self.longitude_columns - 1,
            )

        self._cached_elevation = False

        self._elevations[latitude_index, longitude_index] = elevation

    def set_elevation_arr(self, latitude_index: np.ndarray, longitude_index: np.ndarray, elevation: np.ndarray):
        """Set the elevation of one raster element.

        BEWARE! The order of the indices follows geodetic conventions, i.e.
        the latitude is given first and longitude afterwards, so the first
        index specifies a row index with zero at South and max value
        at North, and the second index specifies a column index
        with zero at West and max value at East. This is not the
        same as some raster conventions (as our row index increases from South
        to North) and this is also not the same as Cartesian coordinates as
        our ordinate index appears before our abscissa index).

        Parameters
        ----------
            latitude_index : index of latitude (row index)
            longitude_index : index of longitude (column index)
            elevation : elevation (m)
        """

        ind_not_good = np.union1d(
            np.union1d(np.where(latitude_index < 0), np.where(latitude_index > (self.latitude_rows - 1))),
            np.union1d(np.where(longitude_index < 0), np.where(longitude_index > (self.longitude_columns - 1))),
        )

        if np.size(ind_not_good) > 0:
            raise PyRuggedError(
                PyRuggedMessages.OUT_OF_TILE_INDICES.value,
                latitude_index[ind_not_good],
                longitude_index[ind_not_good],
                self.latitude_rows - 1,
                self.longitude_columns - 1,
            )

        self._cached_elevation = False

        self._elevations[latitude_index, longitude_index] = elevation

    def set_elevation_block(self, elevation: np.ndarray):
        """Set the elevation.

        BEWARE! The order of the indices follows geodetic conventions, i.e.
        the latitude is given first and longitude afterwards, so the first
        index specifies a row index with zero at South and max value
        at North, and the second index specifies a column index
        with zero at West and max value at East. This is not the
        same as some raster conventions (as our row index increases from South
        to North) and this is also not the same as Cartesian coordinates as
        our ordinate index appears before our abscissa index).

        Parameters
        ----------
             elevation : elevation (m)
        """

        self._cached_elevation = False

        self._elevations = elevation

    def get_elevation_at_indices(self, latitude_index: int, longitude_index: int) -> float:
        """Get the elevation of an exact grid point.

        Parameters
        ----------
            latitude_index : grid point index along latitude
            longitude_index : grid point index along longitude

        Returns
        -------
            elevation : elevation at grid point (m)
        """

        elevation = self._elevations[latitude_index, longitude_index]

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_tile_cell(self, latitude_index, longitude_index, elevation)

        return float(elevation)

    def get_elevation_at_indices_arr(self, latitude_index: np.ndarray, longitude_index: np.ndarray) -> np.array:
        """Get the elevation of an exact grid point.

        Parameters
        ----------
            latitude_index : grid point index along latitude
            longitude_index : grid point index along longitude

        Returns
        -------
            elevation : elevation at grid point (m)
        """

        elevation_arr = self._elevations[latitude_index, longitude_index]

        if dump_manager.DUMP_VAR is not None:
            for elevation in elevation_arr:
                dump_manager.DUMP_VAR.dump_tile_cell(self, latitude_index, longitude_index, elevation)

        return elevation_arr

    def interpolate_elevation(self, latitude: float, longitude: float) -> float:
        """Interpolate elevation.

        In order to cope with numerical accuracy issues when computing
        points at tile boundary, a slight tolerance (typically 1/8 cell)
        around the tile is allowed. Elevation can therefore be interpolated
        (really extrapolated in this case) even for points slightly overshooting
        tile boundaries, using the closest tile cell. Attempting to interpolate
        too far from the tile will trigger an exception.

        Parameters
        ----------
            latitude : ground point latitude
            longitude : ground point longitude

        Returns
        -------
            result : interpolated elevation (m)
        """

        double_latitude_index = self.get_double_latitude_index(
            normalize_angle(latitude, self._min_latitude + self._latitude_step * self._latitude_rows / 2)
        )
        double_longitude_index = self.get_double_longitude_index(
            normalize_angle(longitude, self._min_longitude + self._longitude_step * self._longitude_columns / 2)
        )
        if (
            double_latitude_index < -self.TOLERANCE
            or double_latitude_index >= (self.latitude_rows - 1 + self.TOLERANCE)
        ) or (
            double_longitude_index < -self.TOLERANCE
            or double_longitude_index >= (self.longitude_columns - 1 + self.TOLERANCE)
        ):
            raise PyRuggedError(
                PyRuggedMessages.OUT_OF_TILE_ANGLES.value,
                float(np.degrees(latitude)),
                float(np.degrees(longitude)),
                float(np.degrees(self.minimum_latitude)),
                float(np.degrees(self.maximum_latitude)),
                float(np.degrees(self.minimum_longitude)),
                float(np.degrees(self.maximum_longitude)),
            )

        latitude_index = max(0, min(self.latitude_rows - 2, math.floor(double_latitude_index)))
        longitude_index = max(0, min(self.longitude_columns - 2, math.floor(double_longitude_index)))

        # Bilinear interpolation
        d_lat = double_latitude_index - latitude_index
        d_lon = double_longitude_index - longitude_index
        e_00 = self.get_elevation_at_indices(latitude_index, longitude_index)
        e_10 = self.get_elevation_at_indices(latitude_index, longitude_index + 1)
        e_01 = self.get_elevation_at_indices(latitude_index + 1, longitude_index)
        e_11 = self.get_elevation_at_indices(latitude_index + 1, longitude_index + 1)

        return (e_00 * (1.0 - d_lon) + d_lon * e_10) * (1.0 - d_lat) + (e_01 * (1.0 - d_lon) + d_lon * e_11) * d_lat

    def interpolate_elevation_arr(self, latitude: np.ndarray, longitude: np.ndarray) -> (np.ndarray, np.ndarray):
        """Interpolate elevation.

        In order to cope with numerical accuracy issues when computing
        points at tile boundary, a slight tolerance (typically 1/8 cell)
        around the tile is allowed. Elevation can therefore be interpolated
        (really extrapolated in this case) even for points slightly overshooting
        tile boundaries, using the closest tile cell. Attempting to interpolate
        too far from the tile will trigger an exception.

        Parameters
        ----------
            latitude : ground point latitude
            longitude : ground point longitude

        Returns
        -------
            result : interpolated elevation (m)
        """

        double_latitude_index = self.get_double_latitude_index_arr(
            normalize_angle_vec(latitude, self._min_latitude + self._latitude_step * self._latitude_rows / 2)
        )
        double_longitude_index = self.get_double_longitude_index_arr(
            normalize_angle_vec(longitude, self._min_longitude + self._longitude_step * self._longitude_columns / 2)
        )

        latitude_index = np.array(
            np.fmax(0, np.fmin(self.latitude_rows - 2, np.floor(double_latitude_index))), dtype=int
        )
        longitude_index = np.array(
            np.fmax(0, np.fmin(self.longitude_columns - 2, np.floor(double_longitude_index))), dtype=int
        )

        # Bilinear interpolation
        d_lat = double_latitude_index - latitude_index
        d_lon = double_longitude_index - longitude_index
        e_00 = self.get_elevation_at_indices_arr(latitude_index, longitude_index)
        e_10 = self.get_elevation_at_indices_arr(latitude_index, longitude_index + 1)
        e_01 = self.get_elevation_at_indices_arr(latitude_index + 1, longitude_index)
        e_11 = self.get_elevation_at_indices_arr(latitude_index + 1, longitude_index + 1)

        output = (e_00 * (1.0 - d_lon) + d_lon * e_10) * (1.0 - d_lat) + (e_01 * (1.0 - d_lon) + d_lon * e_11) * d_lat

        # we leave NaN where OUT_OF_TILE_ANGLES occur.
        ind_not_in_tol = np.union1d(
            np.union1d(
                np.where(double_latitude_index < -self.TOLERANCE)[0],
                np.where(double_latitude_index >= (self.latitude_rows - 1 + self.TOLERANCE))[0],
            ),
            np.union1d(
                np.where(double_longitude_index < -self.TOLERANCE)[0],
                np.where(double_longitude_index >= (self.longitude_columns - 1 + self.TOLERANCE))[0],
            ),
        )
        output[ind_not_in_tol] = np.nan

        return output

    def cell_intersection(
        self, point_p: np.ndarray, los: np.ndarray, latitude_index: int, longitude_index: int
    ) -> np.ndarray:
        """Find the intersection of a line-of-sight and a Digital Elevation Model cell.

        Beware that for continuity reasons, the point argument in {@code cellIntersection} is normalized
        with respect to other points used by the caller. This implies that the longitude may be
        outside of the [-π ; +π] interval (or the [0 ; 2π] interval, depending on the DEM). In particular,
        when a Line Of Sight crosses the antimeridian at  ±π longitude, the library may call the
        {@code cellIntersection} method with a point having a longitude of -π-ε to ensure this continuity.
        As tiles are stored with longitude clipped to a some DEM specific interval (either  [-π ; +π] or [0 ; 2π]),
        implementations MUST take care to clip the input point back to the tile interval using
        bodies.normalized_geodetic_point.normalize_angle(p[1], someLongitudeWithinTheTile).
        The output point normalization should also be made consistent with the current tile.

        Parameters
        ----------
            point_p : point on the line (beware its longitude is not normalized with respect to tile)
            los : line-of-sight, in the geodetic frame (North, East, Zenith) of the point,
                scaled to match radians in the horizontal plane and meters along the vertical axis
            latitude_index : latitude index of the Digital Elevation Model cell
            longitude_index : longitude index of the Digital Elevation Model cell

        Returns
        -------
            result : point corresponding to line-of-sight crossing the Digital Elevation Model surface
                if it lies within the cell, None otherwise
        """

        # Ensure neighboring cells to not fall out of tile
        i_lat = max(0, min(self.latitude_rows - 2, latitude_index))
        j_lon = max(0, min(self.longitude_columns - 2, longitude_index))

        # Digital elevation mode coordinates at cell vertices
        x_00 = self.get_longitude_at_index(j_lon)
        y_00 = self.get_latitude_at_index(i_lat)
        z_00 = self.get_elevation_at_indices(i_lat, j_lon)
        z_01 = self.get_elevation_at_indices(i_lat + 1, j_lon)
        z_10 = self.get_elevation_at_indices(i_lat, j_lon + 1)
        z_11 = self.get_elevation_at_indices(i_lat + 1, j_lon + 1)

        # Normalize back to tile coordinates
        tile_p = normalize_geodetic_point(point_p, x_00)

        # Line-of-sight coordinates at close points
        dx_a = (tile_p[1] - x_00) / self.longitude_step
        dy_a = (tile_p[0] - y_00) / self.latitude_step
        dz_a = tile_p[2]
        dx_b = dx_a + los[1] / self.longitude_step
        dy_b = dy_a + los[0] / self.latitude_step
        dz_b = dz_a + los[2]

        # Points along line-of-sight can be defined as a linear progression
        # along the line depending on free variable t: p(t) = p + t * los.
        # As the point latitude and longitude are linear with respect to t,
        # and as Digital Elevation Model is quadratic with respect to latitude
        # and longitude, the altitude of DEM at same horizontal position as
        # point is quadratic in t:
        # z_DEM(t) = u t² + v t + w

        return cell_intersection_func(
            dx_a,
            dx_b,
            dy_a,
            dy_b,
            dz_a,
            dz_b,
            los,
            tile_p,
            x_00,
            z_00,
            z_01,
            z_10,
            z_11,
            self.latitude_step,
            self.longitude_step,
            self.TOLERANCE,
        )

    def cell_intersection_vec(
        self,
        point_p: np.ndarray,
        los: np.ndarray,
        lat_index_vec: np.ndarray,
        lon_index_vec: np.ndarray,
    ) -> np.ndarray:
        """Find the intersection of lines-of-sight and a Digital Elevation Model cell. Vectorised version.

        Beware that for continuity reasons, the point argument in {@code cellIntersection} is normalized
        with respect to other points used by the caller. This implies that the longitude may be
        outside of the [-π ; +π] interval (or the [0 ; 2π] interval, depending on the DEM). In particular,
        when a Line Of Sight crosses the antimeridian at  ±π longitude, the library may call the
        {@code cellIntersection} method with a point having a longitude of -π-ε to ensure this continuity.
        As tiles are stored with longitude clipped to a some DEM specific interval (either  [-π ; +π] or [0 ; 2π]),
        implementations MUST take care to clip the input point back to the tile interval using
        bodies.normalized_geodetic_point.normalize_angle(p[1], someLongitudeWithinTheTile).
        The output point normalization should also be made consistent with the current tile.

        Parameters
        ----------
            point_p : points on the lines (beware its longitude is not normalized with respect to tile)
            los : lines-of-sight, in the geodetic frame (North, East, Zenith) of the point,
                scaled to match radians in the horizontal plane and meters along the vertical axis
            lat_index_vec : latitude indexes of the Digital Elevation Model cells
            lon_index_vec : longitude indexes of the Digital Elevation Model cells

        Returns
        -------
            result : point corresponding to line-of-sight crossing the Digital Elevation Model surface
                if it lies within the cell, None otherwise
        """

        # Ensure neighboring cells to not fall out of tile
        i_lat = np.fmax(0, np.fmin(self.latitude_rows - 2, lat_index_vec))
        j_lon = np.fmax(0, np.fmin(self.longitude_columns - 2, lon_index_vec))

        # Digital elevation mode coordinates at cell vertices
        x_00 = self.get_longitude_at_index_arr(j_lon)
        y_00 = self.get_latitude_at_index_arr(i_lat)
        z_00 = self.get_elevation_at_indices_arr(i_lat, j_lon).astype(float)
        z_01 = self.get_elevation_at_indices_arr(i_lat + 1, j_lon).astype(float)
        z_10 = self.get_elevation_at_indices_arr(i_lat, j_lon + 1).astype(float)
        z_11 = self.get_elevation_at_indices_arr(i_lat + 1, j_lon + 1).astype(float)

        # Normalize back to tile coordinates
        tile_p = normalize_geodetic_point(point_p, x_00)

        # Line-of-sight coordinates at close points
        dx_a = (tile_p[:, 1] - x_00) / self.longitude_step
        dy_a = (tile_p[:, 0] - y_00) / self.latitude_step
        dz_a = tile_p[:, 2]
        dx_b = dx_a + los[..., 1] / self.longitude_step
        dy_b = dy_a + los[..., 0] / self.latitude_step
        dz_b = dz_a + los[..., 2]

        # Points along line-of-sight can be defined as a linear progression
        # along the line depending on free variable t: p(t) = p + t * los.
        # As the point latitude and longitude are linear with respect to t,
        # and as Digital Elevation Model is quadratic with respect to latitude
        # and longitude, the altitude of DEM at same horizontal position as
        # point is quadratic in t:
        # z_DEM(t) = u t² + v t + w

        return cell_intersection_vec_func(
            dx_a,
            dx_b,
            dy_a,
            dy_b,
            dz_a,
            dz_b,
            los,
            tile_p,
            x_00,
            z_00,
            z_01,
            z_10,
            z_11,
            self.latitude_step,
            self.longitude_step,
            self.TOLERANCE,
        )

    def interpolate(
        self,
        t_val: float,
        tile_p: np.ndarray,
        dx_p: float,
        dy_p: float,
        los: np.ndarray,
        central_longitude: float,
    ) -> np.ndarray:
        """Interpolate point along a line.

        Parameters
        ----------
            t_val : abscissa along the line
            tile_p : start point, normalized to tile area
            dx_p : relative coordinate of the start point with respect to current cell
            dy_p : relative coordinate of the start point with respect to current cell
            los : direction of the line-of-sight, in geodetic space
            central_longitude : reference longitude lc such that the point longitude will
                be normalized between lc-π and lc+π

        Returns
        -------
            result : interpolated point along the line
        """

        res = interpolate_func(t_val, tile_p, dx_p, dy_p, los, self.latitude_step, self.longitude_step, self.TOLERANCE)

        res_ngp = None
        if res is not None:
            res_ngp = normalize_geodetic_point(res[0:-1], central_longitude)

        return res_ngp

    def interpolate_vec(
        self,
        t_val: np.ndarray,
        tile_p: np.ndarray,
        dx_p: np.ndarray,
        dy_p: np.ndarray,
        los: np.ndarray,
        central_longitude: np.ndarray,
    ) -> np.ndarray:
        """Interpolate points along lines.

        Parameters
        ----------
            t_val : abscissa along the lines
            tile_p : start points, normalized to tile area
            dx_p : relative coordinate of the start points with respect to current cell
            dy_p : relative coordinate of the start points with respect to current cell
            los : direction of the lines-of-sight, in geodetic space
            central_longitude : reference longitudes lc such that the point longitude will
                be normalized between lc-π and lc+π

        Returns
        -------
            result : interpolated points along the lines
        """

        res = self.interpolate_func_vec(t_val, tile_p, dx_p, dy_p, los, central_longitude)

        res_ngp = normalize_geodetic_point(res[:, 0:-1], res[:, 3])

        return res_ngp

    def interpolate_func_vec(
        self,
        t_val: np.ndarray,
        tile_p: np.ndarray,
        dx_p: np.ndarray,
        dy_p: np.ndarray,
        los: np.ndarray,
        central_longitude: np.ndarray,
    ) -> np.ndarray:
        """Interpolate points along lines.

        Parameters
        ----------
            t_val : abscissa along the lines
            tile_p : start points, normalized to tile area
            dx_p : relative coordinate of the start points with respect to current cell
            dy_p : relative coordinate of the start points with respect to current cell
            los : direction of the lines-of-sight, in geodetic space
            central_longitude : reference longitudes lc such that the point longitude will
                be normalized between lc-π and lc+π

        Returns
        -------
            result : interpolated points along the lines
        """
        size = tile_p[:, 0].size
        res = np.zeros((size, 4)) + np.nan
        ind_not_inf = np.where(t_val != np.inf)[0]

        d_x = dx_p[ind_not_inf] + t_val[ind_not_inf] * los[ind_not_inf, 1] / self.longitude_step
        d_y = dy_p[ind_not_inf] + t_val[ind_not_inf] * los[ind_not_inf, 0] / self.latitude_step

        ind_x_ok = np.intersect1d(np.where(d_x >= -self.TOLERANCE)[0], np.where(d_x <= 1 + self.TOLERANCE)[0])
        ind_y_ok = np.intersect1d(np.where(d_y >= -self.TOLERANCE)[0], np.where(d_y <= 1 + self.TOLERANCE)[0])
        ind_ok = np.intersect1d(ind_x_ok, ind_y_ok)

        if len(ind_ok) > 0:
            if not isinstance(central_longitude, np.ndarray):
                central_longitude = central_longitude * np.ones_like(t_val)

            res[ind_not_inf[ind_ok], :] = np.array(
                [
                    tile_p[ind_not_inf[ind_ok], 0] + t_val[ind_not_inf[ind_ok]] * los[ind_not_inf[ind_ok], 0],
                    tile_p[ind_not_inf[ind_ok], 1] + t_val[ind_not_inf[ind_ok]] * los[ind_not_inf[ind_ok], 1],
                    tile_p[ind_not_inf[ind_ok], 2] + t_val[ind_not_inf[ind_ok]] * los[ind_not_inf[ind_ok], 2],
                    central_longitude[ind_not_inf[ind_ok]],
                ]
            ).T

        return res

    def get_floor_latitude_index_arr(self, latitudes: np.ndarray) -> np.ndarray:
        """Get the floor latitude indexes of a series of points.
        The specified latitudes are always between index and index+1.

        Parameters
        ----------
            latitudes : geodetic latitudes

        Returns
        -------
            result : floor latitude indexes (it may lie outside of the tile)
        """

        return np.array(np.floor(self.get_double_latitude_index_arr(latitudes)), dtype=int)

    def get_floor_latitude_index(self, latitude: float) -> int:
        """Get the floor latitude index of a point.
        The specified latitude is always between index and index+1.

        Parameters
        ----------
            latitude : geodetic latitude

        Returns
        -------
            result : floor latitude index (it may lie outside of the tile)
        """

        return math.floor(self.get_double_latitude_index(latitude))

    def get_floor_longitude_index(self, longitude: float) -> int:
        """Get the floor longitude index of a point.
        The specified longitude is always between index and index+1.

        Parameters
        ----------
            longitude : geodetic longitude

        Returns
        -------
            result : floor longitude index (it may lie outside of the tile)
        """

        return math.floor(self.get_double_longitude_index(longitude))

    def get_floor_longitude_index_arr(self, longitudes: np.ndarray) -> np.ndarray:
        """Get the floor longitudes indexes of points.
        The specified longitude is always between index and index+1.

        Parameters
        ----------
            longitudes : geodetic longitudes

        Returns
        -------
            result : floor longitude index (it may lie outside of the tile)
        """

        return np.array(np.floor(self.get_double_longitude_index_arr(longitudes)), dtype=int)

    def get_double_latitude_index(self, latitude: float) -> float:
        """Get the latitude index of a point.

        Parameters
        ----------
            latitude : geodetic latitude (rad)

        Returns
        -------
            result : latitude index (it may lie outside of the tile)
        """

        return (latitude - self._min_latitude) / self.latitude_step

    def get_double_longitude_index(self, longitude: float) -> float:
        """Get the longitude index of a point.

        Parameters
        ----------
            longitude : geodetic longitude (rad)

        Returns
        -------
            result : longitude index (it may lie outside of the tile)
        """

        return (longitude - self._min_longitude) / self.longitude_step

    def get_double_latitude_index_arr(self, latitude: np.ndarray) -> np.ndarray:
        """Get the latitude indexes of an array of latitudes.

        Parameters
        ----------
            latitude : geodetic latitudes (rad)

        Returns
        -------
            result : latitude indexes (they may lie outside of the tile)
        """

        return (latitude - self._min_latitude) / self.latitude_step

    def get_double_longitude_index_arr(self, longitude: np.ndarray) -> np.ndarray:
        """Get the longitude indexes of an array of longitudes.

        Parameters
        ----------
            longitude : geodetic longitudes (rad)

        Returns
        -------
            result : longitude indexes (they may lie outside of the tile)
        """

        return (longitude - self._min_longitude) / self.longitude_step

    def get_location(self, latitude: float, longitude: float) -> Location:
        """Check if a tile covers a ground point.

        Parameters
        ----------
            latitude : ground point latitude
            longitude : ground point longitude

        Returns
        -------
            res : location of the ground point with respect to tile
        """

        norm_longitude = normalize_angle(longitude, self._min_longitude)
        max_lat = self.maximum_latitude
        if norm_longitude < self._min_longitude:
            if latitude < self._min_latitude:
                res = Location.SOUTH_WEST

            elif latitude <= max_lat:
                res = Location.WEST

            else:
                res = Location.NORTH_WEST

        elif norm_longitude <= self.maximum_longitude:
            if latitude < self._min_latitude:
                res = Location.SOUTH

            elif latitude <= max_lat:
                res = Location.HAS_INTERPOLATION_NEIGHBORS

            else:
                res = Location.NORTH

        else:
            if latitude < self._min_latitude:
                res = Location.SOUTH_EAST

            elif latitude <= max_lat:
                res = Location.EAST

            else:
                res = Location.NORTH_EAST

        return res

    def get_location_arr(self, latitudes: np.ndarray, longitudes: np.ndarray) -> (np.ndarray, np.ndarray):
        """Check if tiles cover ground points.

        Parameters
        ----------
            latitudes : ground point latitudes
            longitudes : ground point longitudes

        Returns
        -------
            res : locations of the ground points with respect to tiles
            ind_has_neighbors : array of indices where location is HAS_INTERPOLATE_NEIGHBORS
        """
        norm_longitudes = normalize_angle_vec(longitudes, self._min_longitude)

        ind_where_lon_min = np.where(norm_longitudes < self._min_longitude)
        ind_where_lon_max = np.where(norm_longitudes > self.maximum_longitude)

        ind_where_lat_min = np.where(latitudes < self._min_latitude)
        ind_where_lat_max = np.where(latitudes > self.maximum_latitude)

        out = np.zeros_like(latitudes, dtype="int16") + Location.HAS_INTERPOLATION_NEIGHBORS.value

        ind_south_west = np.intersect1d(ind_where_lon_min, ind_where_lat_min, assume_unique=True)
        out[ind_south_west] = Location.SOUTH_WEST.value

        ind_south_east = np.intersect1d(ind_where_lon_max, ind_where_lat_min, assume_unique=True)
        out[ind_south_east] = Location.SOUTH_EAST.value

        ind_north_west = np.intersect1d(ind_where_lon_min, ind_where_lat_max, assume_unique=True)
        out[ind_north_west] = Location.NORTH_WEST.value

        ind_north_east = np.intersect1d(ind_where_lon_max, ind_where_lat_max, assume_unique=True)
        out[ind_north_east] = Location.NORTH_EAST.value

        ind_south = np.setdiff1d(ind_where_lat_min, np.union1d(ind_south_west, ind_south_east), assume_unique=True)
        out[ind_south] = Location.SOUTH.value

        ind_north = np.setdiff1d(ind_where_lat_max, np.union1d(ind_north_west, ind_north_east), assume_unique=True)
        out[ind_north] = Location.NORTH.value

        ind_east = np.setdiff1d(ind_where_lon_max, np.union1d(ind_north_east, ind_south_east), assume_unique=True)
        out[ind_east] = Location.EAST.value

        ind_west = np.setdiff1d(ind_where_lon_min, np.union1d(ind_north_west, ind_south_west), assume_unique=True)
        out[ind_west] = Location.WEST.value

        ind_has_neighbors = np.where(out == Location.HAS_INTERPOLATION_NEIGHBORS.value)[0]

        return out, ind_has_neighbors
