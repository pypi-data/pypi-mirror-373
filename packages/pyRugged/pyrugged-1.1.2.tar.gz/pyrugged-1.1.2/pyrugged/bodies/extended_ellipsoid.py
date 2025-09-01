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

"""pyrugged Class ExtendedEllipsoid"""

# pylint: disable=too-many-locals
import math
from decimal import Decimal
from typing import List, Tuple, Union

import numpy as np
from org.hipparchus.geometry.euclidean.threed import Line, Vector3D
from org.orekit.frames import Frame

from pyrugged.bodies.geodesy import east, normalize_geodetic_point, north, zenith
from pyrugged.bodies.one_axis_ellipsoid import OneAxisEllipsoid
from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    compute_linear_combination_2,
    compute_linear_combination_2_arr,
    convert_los_from_point_func,
    convert_los_from_point_vec_func,
    cross,
    cross_n,
    dot,
    dot_n,
    get_norm,
    get_norm_n,
    get_norm_sq,
    get_norm_sq_n,
    scalar_multiply,
    to_array,
    to_array_v,
)


class ExtendedEllipsoid(OneAxisEllipsoid):
    """Transform provider from Spacecraft frame to observed body frame."""

    ALTITUDE_CONVERGENCE = 1.0e-3

    # Maximum iteration allowed
    MAX_ITER_LAT = 20

    # Tolerance on latitude 0,01 degree
    TOLERANCE_LAT = 0.000001 * math.pi / 180.0

    # Tolerance on altitude 1m
    TOLERANCE_ALT = 0.01

    def __init__(self, radius: float, flattening: float, body_frame: Frame):
        """Builds a new instance.

        Parameters
        ----------
            radius : equatorial radius (m)
            flattening : the flattening (f = (a-b)/a)
            body_frame : body frame related to body shape

        """

        super().__init__(radius, flattening, body_frame)

        self._a_2 = radius * radius
        self._b_1 = radius * (1 - flattening)
        self._b_2 = self._b_1 * self._b_1

    # pylint: disable=too-many-branches
    def transform(
        self,
        point: Union[np.ndarray, Tuple, List],
        frame: Frame = None,
        central_longitude: float = None,
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """Transform a point (cartesian or geodetic) to a surface-relative point. Point can be 1 GeodeticPoint/Vector3D
         or can be several points given in Tuple([latitudes], [longitudes], [altitudes]). If several points are given
         in tuple ([lats], [longs], [alts]) then frame should not be given (None) because for now it is only possible
         to use the transform_from_frame method for 1 Geodetic/Vector3D point.

        Parameters
        ----------
            point : cartesian point (m) or GeodeticPoint if frame and date are None, can be also be several points
            coordinates given in Tuple(np.array[latitudes], np.array[longitudes], np.array[altitudes]) if frame and
            date are None
            frame : frame in which cartesian point is expressed
            date : date of the computation (used for frames conversions)
            central_longitude : reference longitude lc such that the point longitude will
                be normalized between lc-π and lc+π (rad)

        Returns
        -------
            point at the same location but as a surface-relative point

        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        if point is not None:
            if frame is None:
                if isinstance(point, tuple):
                    # If point is tuple (np.array[lats], np.array[lons], np.array[alts]),
                    # can contain several coordinates
                    cartesian_coord = self.transform_from_point(point[0], point[1], point[2])
                    return cartesian_coord
                if isinstance(point, list):
                    # If point is List[GeodeticPoint]
                    point = np.array(point)
                    cartesian_coord = self.transform_from_point(point[:, 0], point[:, 1], point[:, 2])
                    return cartesian_coord

                # If point is GeodeticPoint
                cartesian_coord = self.transform_from_point(
                    np.array([point[0]]), np.array([point[1]]), np.array([point[2]])
                )
                return cartesian_coord

            if isinstance(point, tuple):
                raise PyRuggedError(PyRuggedMessages.TRANSFORM_FROM_FRAME_NOT_ALLOWED.value)
            if len(np.shape(point)) == 2:
                res = self.transform_from_frame_vec(point)
                if central_longitude is not None:
                    res = normalize_geodetic_point(res, central_longitude)
            else:
                res = self.transform_from_frame(point)
                if central_longitude is not None:
                    res = normalize_geodetic_point(res, central_longitude)

        else:
            raise ValueError("Wrong arguments sequence in ExtendedEllipsoid.transform")
        return res

    def transform_vec(
        self,
        points: np.ndarray,
        frame: Frame = None,
        central_longitude: Union[float, np.ndarray] = None,
    ) -> np.ndarray:
        """Transform points (cartesian or geodetic) to surface-relative points. Points are given in shape (N, 3).

        Parameters
        ----------
            points : cartesian point (m) or GeodeticPoint if frame and date are None, can be also be several points
            coordinates given in Tuple(np.array[latitudes], np.array[longitudes], np.array[altitudes]) if frame and
            date are None
            frame : frame in which cartesian point is expressed
            date : date of the computation (used for frames conversions)
            central_longitude : reference longitude lc such that the point longitude will
                be normalized between lc-π and lc+π (rad)

        Returns
        -------
            point at the same location but as a surface-relative point

        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        to_flatten = False
        if points.ndim == 1:
            points = points[np.newaxis, :]
            to_flatten = True

        res = np.zeros(points.shape) + np.nan
        ind_not_nan = np.where(~np.isnan(points[:, 0]))[0]

        if len(ind_not_nan) > 0:

            if frame is None:
                cartesian_coord = self.transform_from_point_vec(points[ind_not_nan, :])
                res[ind_not_nan, :] = cartesian_coord
            else:
                res[ind_not_nan, :] = normalize_geodetic_point(
                    self.transform_from_frame_vec(points[ind_not_nan, :]), central_longitude
                )

        if to_flatten:
            return res[0]

        return res

    def point_at_latitude(
        self, position: np.ndarray, los: np.ndarray, latitude: float, close_reference: np.ndarray
    ) -> np.ndarray:
        """Get point at some latitude along a pixel line of sight.

        Parameters
        ----------
            position : cell position (in body frame) (m)
            los : line of sight, not necessarily normalized (in body frame)
            latitude : latitude with respect to ellipsoid (rad)
            close_reference : reference point used to select the closest solution

                When there are two points at the desired latitude along the line, it should
                be close to los surface intersection (m)

        Returns
        -------
            point at latitude (m)
        """
        # todo: issue #61 optimize execution time with Decimal
        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        # Find apex of iso-latitude cone, somewhere along polar axis
        sin_phi = math.sin(latitude)
        sin_phi_2 = sin_phi * sin_phi
        e_2 = self.flattening * (2 - self.flattening)
        apex_z = -self.a_val * e_2 * sin_phi / math.sqrt(1 - e_2 * sin_phi_2)

        # Quadratic equation representing line intersection with iso-latitude cone
        # a k² + 2 b k + c = 0
        # When line of sight is almost along an iso-latitude generatrix, the quadratic
        # equation above may become unsolvable due to numerical noise (we get catastrophic
        # cancellation when computing b # b - a # c). So we set up the model in two steps,
        # first searching k₀ such that position + k₀ los is close to closeReference, and
        # then using position + k₀ los as the new initial position, which should be in
        # the neighborhood of the solution

        cos_phi = math.cos(latitude)
        cos_phi_2 = cos_phi * cos_phi

        # use Decimal for accurate mathematical operations using decimal float
        k_0 = Decimal(dot(close_reference - position, los) / get_norm_sq(los))
        sin_phi_2 = Decimal(sin_phi_2)
        cos_phi_2 = Decimal(cos_phi_2)
        los_x = Decimal(los[0])
        los_y = Decimal(los[1])
        los_z = Decimal(los[2])

        delta_x = Decimal(position[0]) + k_0 * los_x
        delta_y = Decimal(position[1]) + k_0 * los_y
        delta_z = Decimal(position[2]) + k_0 * los_z - Decimal(apex_z)
        delta = to_array(float(delta_x), float(delta_y), float(delta_z))

        a_val = sin_phi_2 * (los_x * los_x + los_y * los_y) - cos_phi_2 * los_z * los_z
        b_val = sin_phi_2 * (delta_x * los_x + delta_y * los_y) - cos_phi_2 * delta_z * los_z
        c_val = sin_phi_2 * (delta_x * delta_x + delta_y * delta_y) - cos_phi_2 * delta_z * delta_z

        # Find the two intersections along the line
        if b_val * b_val < a_val * c_val:
            raise PyRuggedError(PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_LATITUDE.value, str(np.degrees(latitude)))

        s_root = math.sqrt(b_val * b_val - a_val * c_val)

        # return to regular float type
        a_val = float(a_val)
        b_val = float(b_val)
        c_val = float(c_val)
        k_0 = float(k_0)

        k_1 = -(s_root + b_val) / a_val if b_val > 0 else c_val / (s_root - b_val)
        k_2 = c_val / (a_val * k_1)

        # The quadratic equation has two solutions
        k_1_is_ok = (delta[2] + k_1 * los[2]) * latitude >= 0
        k_2_is_ok = (delta[2] + k_2 * los[2]) * latitude >= 0

        if k_1_is_ok:
            if k_2_is_ok:
                k_ref = dot(los, close_reference - position) / get_norm_sq(los) - k_0
                selected_k = k_1 if (math.fabs(k_1 - k_ref) <= math.fabs(k_2 - k_ref)) else k_2

            else:
                selected_k = k_1

        else:
            if k_2_is_ok:
                selected_k = k_2

            else:
                raise PyRuggedError(
                    PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_LATITUDE.value, str(np.degrees(latitude))
                )

        return compute_linear_combination_2(1.0, position, k_0 + selected_k, los)

    def point_at_latitude_vec(
        self, positions: np.ndarray, los: np.ndarray, latitudes: np.ndarray, close_references: np.ndarray
    ) -> np.ndarray:
        """Get points at some latitudes along pixels lines of sight.

        Parameters
        ----------
            positions : cell positions (in body frame) (m)
            los : lines of sight, not necessarily normalized (in body frame)
            latitudes : latitudes with respect to ellipsoid (rad)
            close_references : reference points used to select the closest solution

                When there are two points at the desired latitude along the line, it should
                be close to los surface intersection (m)

        Returns
        -------
            point at latitude (m)
        """
        # todo: issue #61 optimize execution time with Decimal
        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        # Find apex of iso-latitude cone, somewhere along polar axis
        sin_phi = np.sin(latitudes)
        sin_phi_2 = sin_phi * sin_phi
        e_2 = self.flattening * (2 - self.flattening)
        apex_z = -self.a_val * e_2 * sin_phi / np.sqrt(1 - e_2 * sin_phi_2)

        # Quadratic equation representing line intersection with iso-latitude cone
        # a k² + 2 b k + c = 0
        # When line of sight is almost along an iso-latitude generatrix, the quadratic
        # equation above may become unsolvable due to numerical noise (we get catastrophic
        # cancellation when computing b # b - a # c). So we set up the model in two steps,
        # first searching k₀ such that position + k₀ los is close to closeReference, and
        # then using position + k₀ los as the new initial position, which should be in
        # the neighborhood of the solution

        cos_phi = np.cos(latitudes)
        cos_phi_2 = cos_phi * cos_phi

        # use Decimal for accurate mathematical operations using decimal float
        k_0 = (dot_n(close_references - positions, los) / get_norm_sq_n(los)).astype(Decimal)
        sin_phi_2 = sin_phi_2.astype(Decimal)
        cos_phi_2 = cos_phi_2.astype(Decimal)
        los_x = (los[:, 0]).astype(Decimal)
        los_y = (los[:, 1]).astype(Decimal)
        los_z = (los[:, 2]).astype(Decimal)

        delta_x = (positions[:, 0]).astype(Decimal) + k_0 * los_x
        delta_y = (positions[:, 1]).astype(Decimal) + k_0 * los_y
        delta_z = (positions[:, 2]).astype(Decimal) + k_0 * los_z - apex_z.astype(Decimal)
        delta = to_array_v([delta_x.astype(float), delta_y.astype(float), delta_z.astype(float)])

        a_val = sin_phi_2 * (los_x * los_x + los_y * los_y) - cos_phi_2 * los_z * los_z
        b_val = sin_phi_2 * (delta_x * los_x + delta_y * los_y) - cos_phi_2 * delta_z * los_z
        c_val = sin_phi_2 * (delta_x * delta_x + delta_y * delta_y) - cos_phi_2 * delta_z * delta_z

        # Filter points that have two solutions
        two_solutions = b_val * b_val >= a_val * c_val

        # return to regular float type
        a_val = a_val[two_solutions].astype(float)
        b_val = b_val[two_solutions].astype(float)
        c_val = c_val[two_solutions].astype(float)
        k_0 = k_0[two_solutions].astype(float)

        s_root = np.sqrt(b_val * b_val - a_val * c_val)

        k_1 = np.where(b_val > 0, -(s_root + b_val) / a_val, c_val / (s_root - b_val))
        k_2 = c_val / (a_val * k_1)

        # The quadratic equation has two solutions
        k_1_is_ok = (delta[2][two_solutions] + k_1 * los[two_solutions, 2]) * latitudes[two_solutions] >= 0
        k_2_is_ok = (delta[2][two_solutions] + k_2 * los[two_solutions, 2]) * latitudes[two_solutions] >= 0

        k_ref = (
            dot_n(los[two_solutions], close_references[two_solutions] - positions[two_solutions])
            / get_norm_sq_n(los[two_solutions])
            - k_0
        )
        selected_k = np.where(
            k_1_is_ok,
            np.where(
                k_2_is_ok,
                np.where(
                    (np.fabs(k_1 - k_ref) <= np.fabs(k_2 - k_ref)),
                    k_1,
                    k_2,
                ),
                k_1,
            ),
            np.where(
                k_2_is_ok,
                k_2,
                np.nan,
            ),
        )

        output = np.full(positions.shape, np.nan, dtype="float64")

        ind_sol = np.where(two_solutions)[0]
        ind = np.where(~np.isnan(selected_k))[0]
        ind_final = ind_sol[ind]

        output[ind_final] = compute_linear_combination_2_arr(
            np.ones_like(k_0[ind]),
            positions[ind_final],
            k_0[ind] + selected_k[ind],
            los[ind_final],
        )

        return output

    def point_at_longitude(self, position: np.ndarray, los: np.ndarray, longitude: float) -> np.ndarray:
        """Get point at some longitude along a pixel line of sight.

        Parameters
        ----------
            position : cell position (in body frame) (m)
            los : pixel line-of-sight, not necessarily normalized (in body frame)
            longitude : longitude with respect to ellipsoid (rad)

        Returns
        -------
            point at longitude (m)
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        # Normal to meridian
        normal = to_array(-math.sin(longitude), math.cos(longitude), 0.0)
        d_prod = dot(los, normal)

        if math.fabs(d_prod) < 1e-12:
            raise PyRuggedError(
                PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_LONGITUDE.value, str(np.degrees(longitude))
            )

        # Compute point
        return compute_linear_combination_2(1.0, position, -dot(position, normal) / d_prod, los)

    def point_at_longitude_vec(self, positions: np.ndarray, los: np.ndarray, longitudes: np.ndarray) -> np.ndarray:
        """Get points at some longitudes along a pixel line of sight.

        Parameters
        ----------
            positions : cell positions (in body frame) (m)
            los : pixels lines-of-sight, not necessarily normalized (in body frame)
            longitudes : longitudes with respect to ellipsoid (rad)

        Returns
        -------
            points at longitudes (m)
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        # Normal to meridian
        normal = np.zeros_like(los)
        normal[..., 0] = -np.sin(longitudes)
        normal[..., 1] = np.cos(longitudes)
        d_prod = dot_n(los, normal)

        # Avoid points where abs(d_prod) < 1.e-12, they correspond to error case LINE_OF_SIGHT_NEVER_CROSSES_LONGITUDE
        ind = np.where(np.fabs(d_prod) >= 1.0e-12)[0]

        output = np.full(positions.shape, np.nan, dtype="float64")
        output[ind] = compute_linear_combination_2_arr(
            np.ones_like(d_prod[ind]),
            positions[ind],
            -dot_n(positions[ind], normal[ind]) / d_prod[ind],
            los[ind],
        )
        return output

    def point_on_ground(self, position: np.ndarray, los: np.ndarray, central_longitude: float) -> np.ndarray:
        """Get point on ground along a pixel line of sight.

        Parameters
        ----------
            position : cell position (in body frame) (m)
            los : pixel line-of-sight, not necessarily normalized (in body frame)
            central_longitude : reference longitude lc such that the point longitude will
                be normalized between lc-π and lc+π (rad)

        Returns
        -------
            point on ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        point_gp = self.get_intersection_point(
            Line(
                Vector3D(position.tolist()),
                Vector3D(compute_linear_combination_2(1.0, position, 1e6, los).tolist()),
                1.0e-12,
            ),
            position,
            self.body_frame,
            None,
        )

        if point_gp is None:
            raise PyRuggedError(PyRuggedMessages.LINE_OF_SIGHT_DOES_NOT_REACH_GROUND.value)

        return normalize_geodetic_point(point_gp, central_longitude)

    def point_on_ground_vec(self, positions: np.ndarray, los: np.ndarray, central_longitude: float) -> np.ndarray:
        """Get points on ground along pixels lines of sight.

        Parameters
        ----------
            positions : cell positions (in body frame) (m)
            los : pixels lines-of-sight, not necessarily normalized (in body frame)
            central_longitude : reference longitude lc such that the point longitude will
                be normalized between lc-π and lc+π (rad)

        Returns
        -------
            points on ground
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        points_gp = self.get_intersection_point_vec(
            positions,
            np.array(
                compute_linear_combination_2_arr(
                    np.ones_like(positions[0]), positions.T, 1e6 * np.ones_like(positions[0]), los.T
                )
            ).T,
        )

        if points_gp is None:
            raise PyRuggedError(PyRuggedMessages.LINE_OF_SIGHT_DOES_NOT_REACH_GROUND.value)

        return normalize_geodetic_point(points_gp, central_longitude)

    def point_at_altitude(self, position: np.ndarray, los: np.ndarray, altitude: float) -> np.ndarray:
        """Get point at some altitude along a pixel line of sight.

        Parameters
        ----------
            position : cell position (in body frame) (m)
            los : pixel line-of-sight, not necessarily normalized (in body frame)
            altitude : altitude with respect to ellipsoid (m)

        Returns
        -------
            point at altitude (m)
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        # Point on line closest to origin
        los_2 = get_norm_sq(los)
        dot_p = dot(position, los)
        k_0 = -dot_p / los_2
        close_0 = compute_linear_combination_2(1.0, position, k_0, los)

        # Very rough guess: if body is spherical, the desired point on line
        # is at distance ae + altitude from origin
        r_val = self.equatorial_radius + altitude
        delta_2 = float(r_val * r_val - get_norm_sq(close_0))

        if delta_2 < 0:
            raise PyRuggedError(PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_ALTITUDE.value, str(altitude))

        delta_k = math.sqrt(delta_2 / los_2)
        k_1 = k_0 + delta_k
        k_2 = k_0 - delta_k
        k = k_1 if (math.fabs(k_1) <= math.fabs(k_2)) else k_2

        # ?? This loop generally converges in 3 iterations ??
        for _i in range(100):
            point = compute_linear_combination_2(1.0, position, k, los)
            gp_k = self.transform_vec(point, self.body_frame, None)
            delta_h = float(altitude - gp_k[2])

            if math.fabs(delta_h) <= self.ALTITUDE_CONVERGENCE:
                return point

            # Improve the offset using linear ratio between
            # altitude variation and displacement along line-of-sight
            k += delta_h / dot(zenith(gp_k), los)

        # This should never happen
        raise PyRuggedError(PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_ALTITUDE.value)

    def point_at_altitude_vec(self, positions: np.ndarray, los: np.ndarray, altitudes: np.ndarray) -> np.ndarray:
        """Get points at some altitude along the pixel lines of sight.

        Parameters
        ----------
            positions : cell positions (in body frame) (m)
            los : pixel lines-of-sight, not necessarily normalized (in body frame)
            altitudes : altitudes with respect to ellipsoid (m) 1D array

        Returns
        -------
            point at altitude (m)
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        # A =len(altitudes) & (3,N)=np.shape(los)=np.shape(positions))

        if altitudes is not None and isinstance(altitudes, (list, np.ndarray)):
            nbr_altitudes = len(altitudes)
            nbr_position, _ = np.shape(los)

            if nbr_altitudes != nbr_position:
                raise ValueError("Altitudes must be the same length as min(len(lon),lan(lat))")

        # Point on line closest to origin
        los_2 = get_norm_sq_n(los)  # (N,)
        dot_p = dot_n(positions, los)
        k_0 = -dot_p / los_2  # (N,)
        close_0 = np.array(compute_linear_combination_2_arr(np.ones_like(k_0), positions, k_0, los)).T

        # Very rough guess: if body is spherical, the desired point on line
        # is at distance ae + altitude from origin
        r_val = self.equatorial_radius + altitudes

        delta_2 = r_val * r_val - get_norm_sq(close_0)  # (N,) = (N,) - (N,)

        if np.size(np.where(delta_2 < 0)) > 0:
            raise PyRuggedError(PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_ALTITUDE.value, str(altitudes))

        delta_k = np.sqrt(delta_2 / los_2)
        k_1 = k_0 + delta_k
        k_2 = k_0 - delta_k
        k = np.where(np.abs(k_1) <= np.abs(k_2), k_1, k_2)

        # ?? This loop generally converges in 3 iterations ??
        for _i in range(100):
            points = np.array(compute_linear_combination_2_arr(np.ones_like(k), positions, k, los))
            gp_k = self.transform_vec(points, self.body_frame, None)
            # if isinstance(gp_k, list):
            #     gp_k = np.array([[gp_k_i[0], gp_k_i[1], gp_k_i[2]] for gp_k_i in gp_k]).T

            delta_h = altitudes - gp_k[:, 2]

            # if np.size(np.where(np.abs(delta_h) <= self.ALTITUDE_CONVERGENCE)) == np.size(delta_h):
            if np.all(np.abs(delta_h) <= self.ALTITUDE_CONVERGENCE):
                return points

            # Improve the offset using linear ratio between
            # altitude variation and displacement along line-of-sight
            k += delta_h / dot_n(zenith(gp_k), los)

        # This should never happen
        raise PyRuggedError(PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_ALTITUDE.value, str(altitudes))

    def inters_circle_ellipsoid(
        self,
        sat_position: np.ndarray,
        sat_velocity: np.ndarray,
        d_range: float,
        is_right: bool,
        doppler_contribution: float,
    ) -> np.ndarray:
        """Intersection between sar viewing circle and altitude ellipsoid, this function returns a_axis cartesian point
        expressed in satellite measurements reference frame.

        Parameters
        ----------
            sat_position : satellite position (in body frame) (m)
            sat_velocity : satellite velocity (in body frame) (m)
            d_range : range
            is_right : True if antenna is pointing right, false if antenna pointing left
            doppler_contribution : doppler contribution, for now only zero doppler implemented (lambda * fd / 2)

        Returns
        -------
            cartesian coordinates (x_coord, y_coord, z) corresponding to intersection between sar viewing circle and
            ellipsoid
            expressed in satellite measurements reference frame.
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        # Opening angle du to Doppler (should be zero as only zero doppler is implemented)
        sin_alpha = doppler_contribution / get_norm(sat_velocity)

        # Reference linked to velocity construction
        vit_vect_pos = cross(sat_velocity, sat_position)
        b_axis = scalar_multiply(1.0 / get_norm(vit_vect_pos), vit_vect_pos)
        c_axis = scalar_multiply(1.0 / get_norm(sat_velocity), sat_velocity)
        a_axis = cross(b_axis, c_axis)

        rot = [
            [a_axis[0], b_axis[0], c_axis[0]],
            [a_axis[1], b_axis[1], c_axis[1]],
            [a_axis[2], b_axis[2], c_axis[2]],
        ]

        dist_center_ref_center_ellipsoid_oop = dot(sat_position, c_axis) + d_range * sin_alpha
        rb_satpos_proj_on_a = dot(sat_position, a_axis)

        latitude = 0.0
        iteration = 0.0

        # Iteration on latitudes
        for _i in range(100):
            iteration += 1
            radius_at_lat = self.compute_ellipsoid_radius_at_latitude(latitude)
            ra2 = radius_at_lat**2 - dist_center_ref_center_ellipsoid_oop**2

            x_coord = (ra2 + rb_satpos_proj_on_a**2 - d_range**2 * (1.0 - sin_alpha**2)) / (2.0 * rb_satpos_proj_on_a)
            if is_right:
                y_coord = math.sqrt(ra2 - x_coord**2)
            else:
                y_coord = -1.0 * math.sqrt(ra2 - x_coord**2)
            surface_point_in_abc_frame = [[x_coord], [y_coord], [dist_center_ref_center_ellipsoid_oop]]
            surface_point_in_ellipsoid_frame = np.dot(np.array(rot), np.array(surface_point_in_abc_frame))

            i_x = surface_point_in_ellipsoid_frame[0][0]
            i_y = surface_point_in_ellipsoid_frame[1][0]
            i_z = surface_point_in_ellipsoid_frame[2][0]

            # Conversion from cartesian to latitude
            lambda_val = math.atan2(i_y, i_x)
            delta_lat = lambda_val - latitude
            latitude = lambda_val

            if math.fabs(delta_lat) <= self.TOLERANCE_LAT:
                return to_array(float(i_x), float(i_y), float(i_z))

        raise PyRuggedError(PyRuggedMessages.SAR_AIMING_CIRCLE_NEVER_CROSSES_LATITUDE.value, str(latitude))

    def inters_circle_ellipsoid_vec(
        self,
        flattening: np.ndarray,
        equatorial_radius: np.ndarray,
        sat_position: np.ndarray,
        sat_velocity: np.ndarray,
        d_range: np.ndarray,
        is_right: bool,
        doppler_contribution: np.ndarray,
    ) -> np.ndarray:
        """Intersection between sar viewing circle and altitude ellipsoid, this function returns a_axis cartesian point
        expressed in satellite measurements reference frame (vectorised version).

        Parameters
        ----------
            flattening : the flattening (f = (a-b)/a) with shape (N,)
            equatorial_radius: equatorial radius (m) with shape (N,)
            sat_position : satellite position (in body frame) (m) with shape (N,3)
            sat_velocity : satellite velocity (in body frame) (m) with shape (N,3)
            d_range : range with shape (N,)
            is_right : True if antenna is pointing right, false if antenna pointing left
            doppler_contribution : doppler contribution, for now only zero dopplerimplemented
            (lambda * fd / 2) with shape (N,)

        Returns
        -------
            batch of cartesian coordinates (x_coord, y_coord, z) corresponding to intersection between sar
            viewing circle and ellipsoid expressed in satellite measurements reference frame with shape (N, 3)
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        # Opening angle du to Doppler (should be zero as only zero doppler is implemented)
        sin_alpha = doppler_contribution / get_norm_n(sat_velocity)

        # Reference linked to velocity construction
        vit_vect_pos = cross_n(sat_velocity, sat_position)
        b_axis = ((1.0 / get_norm_n(vit_vect_pos)) * vit_vect_pos.T).T
        c_axis = ((1.0 / get_norm_n(sat_velocity)) * sat_velocity.T).T
        a_axis = cross_n(b_axis, c_axis)

        rot = [
            [a_axis[..., 0], b_axis[..., 0], c_axis[..., 0]],
            [a_axis[..., 1], b_axis[..., 1], c_axis[..., 1]],
            [a_axis[..., 2], b_axis[..., 2], c_axis[..., 2]],
        ]

        dist_center_ref_center_ellipsoid_oop = dot_n(sat_position, c_axis) + d_range * sin_alpha
        rb_satpos_proj_on_a = dot_n(sat_position, a_axis)
        latitude = np.zeros(sat_position.shape[0])
        output = np.full(sat_position.shape, np.nan, dtype="float64")
        iteration = 0.0

        # Iteration on latitudes
        for _i in range(100):
            iteration += 1

            radius_at_lat = self.compute_ellipsoid_radius_at_latitude_vec(flattening, equatorial_radius, latitude)
            ra2 = radius_at_lat**2 - dist_center_ref_center_ellipsoid_oop**2
            x_coord = (ra2 + rb_satpos_proj_on_a**2 - d_range**2 * (1.0 - sin_alpha**2)) / (2.0 * rb_satpos_proj_on_a)

            if is_right:
                y_coord = np.sqrt(ra2 - x_coord**2)
            else:
                y_coord = -1.0 * np.sqrt(ra2 - x_coord**2)

            surface_point_in_abc_frame = [[x_coord], [y_coord], [dist_center_ref_center_ellipsoid_oop]]
            surface_point_in_ellipsoid_frame = np.matmul(
                np.array(rot).transpose(2, 0, 1), np.array(surface_point_in_abc_frame).transpose(2, 0, 1)
            )

            i_x = surface_point_in_ellipsoid_frame[:, 0, 0]
            i_y = surface_point_in_ellipsoid_frame[:, 1, 0]
            i_z = surface_point_in_ellipsoid_frame[:, 2, 0]

            # Conversion from cartesian to latitude
            lambda_val = np.arctan2(i_y, i_x)
            delta_lat = lambda_val - latitude
            idx_ok = np.where(np.abs(delta_lat) <= self.TOLERANCE_LAT)[0]
            latitude = np.copy(lambda_val)

            output[idx_ok, :] = np.vstack((i_x, i_y, i_z))[:, idx_ok].T

            if np.all(~np.isnan(output)):
                return output

        raise PyRuggedError(PyRuggedMessages.SAR_AIMING_CIRCLE_NEVER_CROSSES_LATITUDE.value, str(latitude))

    def compute_ellipsoid_radius_at_latitude(self, latitude: float):
        """Compute ellipsoid radius at specific latitude

        Parameters
        ----------
            latitude : latitude for which the ellipsoid radius wants to be known (rad)

        Returns
        -------
            Ellipsoid radius for given latitude
        """

        eccentricity2 = self.flattening * (2.0 - self.flattening)
        w_factor = math.sqrt(1 - eccentricity2 * np.sin(latitude) ** 2)
        r_factor = self.equatorial_radius * math.cos(latitude) / w_factor
        z_coord = self.equatorial_radius * (1 - eccentricity2) * math.sin(latitude) / w_factor

        return math.sqrt(r_factor**2 + z_coord**2)

    @staticmethod
    def compute_ellipsoid_radius_at_latitude_vec(
        flattening: np.ndarray, equatorial_radius: np.ndarray, latitudes: np.ndarray
    ):
        """Compute ellipsoid radius at specific numpy array of latitudes

        Parameters
        ----------
            flattening : the flattening (f = (a-b)/a) with shape (N,)
            equatorial_radius: equatorial radius (m) with shape (N,)
            latitudes : latitudes for which the ellipsoid radius wants to be known (rad) with shape (N,)

        Returns
        -------
            Ellipsoid radius with shape (N,) for given ndarray of latitudes
        """

        eccentricity2 = flattening * (2.0 - flattening)
        w_factor = np.sqrt(1 - eccentricity2 * np.sin(latitudes) ** 2)
        r_factor = equatorial_radius * np.cos(latitudes) / w_factor
        z_coord = equatorial_radius * (1 - eccentricity2) * np.sin(latitudes) / w_factor

        return np.sqrt(r_factor**2 + z_coord**2)

    def point_at_altitude_sar(
        self,
        sat_position: np.ndarray,
        sat_velocity: np.ndarray,
        d_range: float,
        is_right: bool,
        doppler_contribution: float,
        altitude: float,
    ) -> np.ndarray:
        """Intersection between sar viewing circle and altitude ellipsoid.

        Parameters
        ----------
            sat_position : satellite position (in body frame) (m)
            sat_velocity : satellite velocity (in body frame) (m)
            body_frame : observed body frame, in which satellite coordinates are given
            d_range : range
            is_right : True if antenna is pointing right, false if antenna pointing left
            doppler_contribution : doppler contribution, for now only zero doppler implemented (lambda * fd / 2)
            altitude: altitude of the wanted point

        Returns
        -------
            point (lon, lat, alt) corresponding to intersection between sar viewing circle and ellipsoid
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        altitude_correction = altitude

        # Iteration on altitude
        # ?? This loop generally converges in 3 iterations ??
        for _i in range(100):
            substitution_ellipsoid = ExtendedEllipsoid(
                self.equatorial_radius + altitude_correction,
                self.flattening * self.equatorial_radius / (self.equatorial_radius + altitude_correction),
                self.body_frame,
            )
            inters_circle_ellips_sat_ref_frame = substitution_ellipsoid.inters_circle_ellipsoid(
                sat_position, sat_velocity, d_range, is_right, doppler_contribution
            )

            point_gp = self.transform_from_frame(inters_circle_ellips_sat_ref_frame)
            dh_dz = 1
            delta_h = altitude - point_gp[2]

            altitude_correction += 1.0 / dh_dz * delta_h

            if math.fabs(delta_h) <= self.ALTITUDE_CONVERGENCE:
                return point_gp

        raise PyRuggedError(PyRuggedMessages.SAR_AIMING_CIRCLE_NEVER_CROSSES_ALTITUDE.value)

    def point_at_altitude_sar_vec(
        self,
        sat_position: np.ndarray,
        sat_velocity: np.ndarray,
        d_range: np.ndarray,
        is_right: bool,
        doppler_contribution: np.ndarray,
        altitude: np.ndarray,
    ) -> np.ndarray:
        """Intersection between sar viewing circle and altitude ellipsoid vectorised.

        Parameters
        ----------
            sat_position : satellite position (in body frame) (m) with shape (N, 3)
            sat_velocity : satellite velocity (in body frame) (m) with shape (N, 3)
            body_frame : observed body frame, in which satellite coordinates are given
            d_range : range with shape (N,)
            is_right : True if antenna is pointing right, false if antenna pointing left
            doppler_contribution : doppler contribution, for now only zero doppler implemented
            (lambda * fd / 2) with shape (N,)
            altitude: altitude of the wanted point with shape (N,)

        Returns
        -------
            point (lon, lat, alt) corresponding to intersection between sar viewing circle and ellipsoid
            with shape (N, 3)
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_ellipsoid(self)

        altitude_correction = np.copy(altitude)
        output = np.full(sat_position.shape, np.nan, dtype="float64")

        # Iteration on altitude
        # ?? This loop generally converges in 3 iterations ??
        for _i in range(100):
            new_equatorial_radius = self.equatorial_radius + altitude_correction
            new_flattening = self.flattening * self.equatorial_radius / (self.equatorial_radius + altitude_correction)

            inters_circle_ellips_sat_ref_frame = self.inters_circle_ellipsoid_vec(
                new_flattening,
                new_equatorial_radius,
                sat_position,
                sat_velocity,
                d_range,
                is_right,
                doppler_contribution,
            )
            point_gp = self.transform_from_frame_vec(inters_circle_ellips_sat_ref_frame)

            dh_dz = 1.0
            delta_h = altitude - point_gp[:, 2]
            idx_ok = np.where(np.abs(delta_h) <= self.ALTITUDE_CONVERGENCE)[0]

            altitude_correction += 1.0 / dh_dz * delta_h

            output[idx_ok, :] = point_gp[idx_ok, :]

            if np.all(~np.isnan(output)):
                return output

        raise PyRuggedError(PyRuggedMessages.SAR_AIMING_CIRCLE_NEVER_CROSSES_ALTITUDE.value)

    def convert_los_from_point(self, point: np.ndarray, los: np.ndarray) -> np.ndarray:
        """Convert a line-of-sight from Cartesian to geodetic.

        Parameters
        ----------
            point : geodetic point on the line-of-sight
            los : line-of-sight, not necessarily normalized (in body frame and Cartesian coordinates)

        Returns
        -------
            line-of-sight in geodetic frame (North, East, Zenith) of the point,
                scaled to match radians in the horizontal plane and meters along the vertical axis
        """
        # Cartesian coordinates of the topocentric frame origin
        p_3d = self.transform_vec(point)
        r_val, rho = convert_los_from_point_func(p_3d[0], p_3d[1], p_3d[2], self._a_2, self._b_2)
        norm = get_norm(los)

        return (
            to_array(
                dot(los, north(point)) / rho, dot(los, east(point)) / r_val, dot(los, zenith(point)) * np.ones_like(rho)
            )
            / norm
        )

    def convert_los_from_point_vec(self, points: np.ndarray, los: np.ndarray) -> np.ndarray:
        """Convert a line-of-sight from Cartesian to geodetic.

        Parameters
        ----------
            points : geodetic points on the line-of-sight
            los : lines-of-sight, not necessarily normalized (in body frame and Cartesian coordinates)

        Returns
        -------
            lines-of-sight in geodetic frame (North, East, Zenith) of the point,
                scaled to match radians in the horizontal plane and meters along the vertical axis
        """

        # Cartesian coordinates of the topocentric frame origin
        p_3d = self.transform_vec(points)

        r_val, rho = convert_los_from_point_vec_func(p_3d[:, 0], p_3d[:, 1], p_3d[:, 2], self._a_2, self._b_2)
        norm = get_norm_n(los)
        geod = np.stack(
            [
                dot_n(los, north(points)) / rho,
                dot_n(los, east(points)) / r_val,
                dot_n(los, zenith(points)),
            ],
            axis=1,
        )
        return geod / norm[:, np.newaxis]

    def convert_los_from_vector(self, primary: np.ndarray, secondary: np.ndarray) -> np.ndarray:
        """Convert a line-of-sight from Cartesian to geodetic.

        Parameters
        ----------
            primary : reference point on the line-of-sight (in body frame and Cartesian coordinates)
            secondary : secondary point on the line-of-sight, only used to define a direction
                with respect to the primary point (in body frame and Cartesian coordinates)

        Returns
        -------
            line-of-sight in topocentric frame (East, North, Zenith) of the point,
                scaled to match radians in the horizontal plane and meters along the vertical axis

        """

        # Switch to geodetic coordinates using primary point as reference
        point = self.transform_vec(primary, self.body_frame, None)
        los = secondary - primary

        # Convert line of sight
        return self.convert_los_from_point(point, los)

    def convert_los_from_vector_vec(self, primaries: np.ndarray, secondaries: np.ndarray) -> np.ndarray:
        """Convert lines-of-sight from Cartesian to geodetic.

        Parameters
        ----------
            primaries : reference points on the lines-of-sight (in body frame and Cartesian coordinates)
            secondaries : secondary points on the lines-of-sight, only used to define a direction
                with respect to the primary points (in body frame and Cartesian coordinates)

        Returns
        -------
            lines-of-sight in geodetic frame (North, East, Zenith) of the point,
                scaled to match radians in the horizontal plane and meters along the vertical axis

        """

        # Switch to geodetic coordinates using primary point as reference
        points = self.transform_vec(primaries, self.body_frame, None)
        los = secondaries - primaries

        # Convert line of sight
        return self.convert_los_from_point_vec(points, los)
