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

"""pyrugged Class IgnoreDEMAlgorithm"""
import numpy as np

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.bodies.geodesy import normalize_geodetic_point
from pyrugged.errors import dump_manager
from pyrugged.intersection.algorithm_id import AlgorithmId


class IgnoreDEMAlgorithm:
    """Intersection ignoring Digital Elevation Model.
    This dummy implementation simply uses the ellipsoid itself.
    """

    def __init__(self):
        """Builds a new instance."""

        self._algorithm_id = AlgorithmId.IGNORE_DEM_USE_ELLIPSOID

    @property
    def algorithm_id(self):
        """Get the Algorithm ID."""

        return self._algorithm_id

    def intersection(self, ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray) -> np.ndarray:
        """Compute intersection of line with Digital Elevation Model.

        Parameters
        ----------
            ellipsoid : reference ellipsoid
            position : pixel position in ellipsoid frame
            los : pixel line-of-sight in ellipsoid frame

        Returns
        -------
            result : point at which the line first enters ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        return ellipsoid.point_on_ground(position, los, 0.0)

    def intersection_vec(self, ellipsoid: ExtendedEllipsoid, positions: np.ndarray, los: np.ndarray) -> np.ndarray:
        """Compute intersections of lines with Digital Elevation Model.

        Parameters
        ----------
            ellipsoid : reference ellipsoid
            positions : pixel positions in ellipsoid frame
            los : pixels lines-of-sight in ellipsoid frame

        Returns
        -------
            result : points at which the lines first enter ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        return ellipsoid.point_on_ground_vec(positions, los, 0.0)

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
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        point_gp = ellipsoid_sysat.point_at_altitude_sar(
            sat_position, sat_velocity, d_range, is_right, doppler_contribution, 0.0
        )

        return normalize_geodetic_point(point_gp, 0.0)

    def refine_intersection(  # pylint: disable=unused-argument
        self, ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray, close_guess: np.ndarray
    ) -> np.ndarray:
        """Refine intersection of line with Digital Elevation Model.

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
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        return self.intersection(ellipsoid, position, los)

    def refine_intersection_vec(  # pylint: disable=unused-argument
        self, ellipsoid: ExtendedEllipsoid, position: np.ndarray, los: np.ndarray, close_guess: np.ndarray
    ) -> np.ndarray:
        """Refine intersection of line with Digital Elevation Model.

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
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        return self.intersection_vec(ellipsoid, position, los)

    # pylint: disable=unused-argument
    def get_elevation(self, latitudes: np.ndarray, longitudes: np.ndarray, complete_tile=True) -> np.ndarray:
        """Get elevation at a given ground point.
        As this algorithm ignored the Digital Elevation Model,
        this method always returns 0.0.


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
            dump_manager.DUMP_VAR.dump_algorithm(self.algorithm_id)

        return np.zeros(latitudes.shape)
