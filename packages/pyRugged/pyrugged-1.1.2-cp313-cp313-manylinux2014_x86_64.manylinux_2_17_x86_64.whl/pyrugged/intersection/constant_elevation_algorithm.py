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

"""pyrugged Class ConstantElevationAlgorithm"""
from typing import List

import numpy as np

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.bodies.geodesy import normalize_geodetic_point
from pyrugged.errors import dump_manager
from pyrugged.intersection.algorithm_id import AlgorithmId


class ConstantElevationAlgorithm:
    """Intersection ignoring Digital Elevation Model.
    This implementation uses a constant elevation over the ellipsoid.
    """

    def __init__(self, constant_elevation: float):
        """Constructor.

        Parameters
        ----------
            constant_elevation : constant elevation over ellipsoid
        """

        self._constant_elevation = constant_elevation
        self._algorithm_id = AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID

    @property
    def algorithm_id(self):
        """Get the Algorithm ID."""

        return self._algorithm_id

    def intersection(
        self, ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray, alt: float = None
    ) -> np.ndarray:
        """Compute intersection of line with Digital Elevation Model.

        Parameters
        ----------
            ellipsoid : reference ellipsoid
            position : pixel position in ellipsoid frame
            los : pixel line-of-sight in ellipsoid frame
            alt : altitudes at wich the intersection occurs

        Returns
        -------
            result : point at which the line first enters ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id, self._constant_elevation)

        fixed_altitude = self._constant_elevation if alt is None else alt

        point_p = ellipsoid.point_at_altitude(position, los, fixed_altitude)

        point_gp = ellipsoid.transform_from_frame(point_p)

        return normalize_geodetic_point(np.array([point_gp[0], point_gp[1], fixed_altitude]), 0.0)

    def intersection_vec(
        self, ellipsoid: ExtendedEllipsoid, positions: np.ndarray, los: np.ndarray, alt: np.ndarray = None
    ) -> np.ndarray:
        """Compute intersection of lines with Digital Elevation Model.

        Parameters
        ----------
            ellipsoid : reference ellipsoid
            positions : pixel positions in ellipsoid frame
            los : pixel lines-of-sight in ellipsoid frame
            alt : altitudes at wich the intersection occurs

        Returns
        -------
            result : points at which the line first enters ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id, self._constant_elevation)

        fixed_altitudes = self._constant_elevation * np.ones(positions.shape[0]) if alt is None else alt
        point_p = ellipsoid.point_at_altitude_vec(positions, los, fixed_altitudes)
        res = ellipsoid.transform_from_frame_vec(point_p)

        return normalize_geodetic_point(res, 0.0)

    def intersection_sar(
        self,
        ellipsoid_sysat: ExtendedEllipsoid,
        sat_position: np.ndarray,
        sat_velocity: np.ndarray,
        d_range: float,
        is_right: bool,
        doppler_contribution: float,
    ) -> np.ndarray:
        """Compute intersection of line with Digital Elevation Model.

        Parameters
        ----------
            ellipsoid_sysat : reference ellipsoid for satellite system on which altitude will be applied
            sat_position : satellite position (in body frame) (m)
            sat_velocity : satellite velocity (in body frame) (m)
            body_frame : observed body frame, in which satellite coordinates are given
            d_range : range
            is_right : True if antenna is pointing right, false if antenna pointing left
            doppler_contribution : doppler contribution, for now only zero doppler implemented (lambda * fd / 2)

        Returns
        -------
            result : point at which the line first enters ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id, self._constant_elevation)

        point_gp = ellipsoid_sysat.point_at_altitude_sar(
            sat_position, sat_velocity, d_range, is_right, doppler_contribution, self._constant_elevation
        )

        return normalize_geodetic_point(point_gp, 0.0)

    def refine_intersection(
        self,
        ellipsoid: ExtendedEllipsoid,
        position: np.ndarray,
        los: np.ndarray,
        close_guess: np.ndarray,
    ) -> np.ndarray:
        """Refine intersection of line with Digital Elevation Model. The intersection altitude is
        taken from the "close_guess".

        Parameters
        ----------
            ellipsoid : reference ellipsoid
            position : pixel position in ellipsoid frame
            los : pixel line-of-sight in ellipsoid frame
            close_guess : guess close to the real intersection

        Returns
        -------
            result : point at which the line first enters ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id, self._constant_elevation)

        if np.isnan(close_guess[2]):
            point_p = ellipsoid.point_at_altitude(position, los, self._constant_elevation)
        else:
            point_p = ellipsoid.point_at_altitude(position, los, close_guess[2])

        point_gp = ellipsoid.transform_from_frame(point_p)

        return normalize_geodetic_point(point_gp, close_guess[1])

    def refine_intersection_vec(
        self,
        ellipsoid: ExtendedEllipsoid,
        positions: np.ndarray,
        los: np.ndarray,
        close_guess: List,
    ) -> np.ndarray:
        """Refine intersections of lines with Digital Elevation Model. The intersection
        altitudes are taken from the close_guess list.

        Parameters
        ----------
            ellipsoid : reference ellipsoid
            positions : pixel positions in ellipsoid frame
            los : pixels lines-of-sight in ellipsoid frame
            close_guess : guess close to the real intersections

        Returns
        -------
            result : point at which the line first enters ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id, self._constant_elevation)

        # build array of altitudes
        constant_altitudes = close_guess[:, 2]
        constant_altitudes = np.nan_to_num(constant_altitudes, nan=self._constant_elevation)

        point_p = ellipsoid.point_at_altitude_vec(positions, los, constant_altitudes)
        res = ellipsoid.transform_from_frame_vec(point_p)

        return normalize_geodetic_point(res, close_guess[:, 1])

    # pylint: disable=unused-argument
    def get_elevation(self, latitudes: np.ndarray, longitudes: np.ndarray, complete_tile=True) -> np.ndarray:
        """Get elevations at  ground points.
        As this algorithm uses a constant elevation,
        this method always returns the same value.

        Parameters
        ----------
            latitudes : ground point latitudes
            longitudes : ground point longitudes
            complete_tile : False if inverse location

        Returns
        -------
            result : elevations
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id, self._constant_elevation)

        return self._constant_elevation * np.ones(latitudes.shape)
