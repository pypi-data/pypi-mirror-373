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

"""pyrugged Class OneAxisEllipsoid"""

# pylint: disable=import-error, too-many-locals
import math
from decimal import Decimal
from typing import Union

import numpy as np
from org.hipparchus.geometry.euclidean.threed import Line, Vector3D
from org.orekit.frames import Frame, StaticTransform
from org.orekit.time import AbsoluteDate
from org.orekit.utils import TimeStampedPVCoordinates

from pyrugged.bodies.ellipse import Ellipse
from pyrugged.bodies.ellipsoid import Ellipsoid
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    compute_linear_combination_2,
    compute_linear_combination_2_arr,
    cross,
    dot_n,
    get_norm,
    get_norm_sq_n,
    to_array,
    to_array_v,
    transform_from_frame_cy,
    transform_from_point_optim,
)


class OneAxisEllipsoid(Ellipsoid):
    """
    Modeling of a one-axis ellipsoid.

    One-axis ellipsoids is a good approximate model for most planet-size
    and larger natural bodies. It is the equilibrium shape reached by
    a fluid body under its own gravity field when it rotates. The symmetry
    axis is the rotation or polar axis.
    """

    # Threshold for polar and equatorial points detection.
    POL_EQU_ANGULAR_THRESHOLD = 1.0e-4

    def __init__(self, radius, flattening, body_frame):
        """Constructor."""

        super().__init__(body_frame, radius, radius, radius * (1.0 - flattening))

        self._flattening = flattening
        self._radius_2 = radius * radius
        self._e_2 = flattening * (2.0 - flattening)
        self._g_val = 1.0 - flattening
        self._g_2 = self._g_val * self._g_val
        self._ap_2 = self._radius_2 * self._g_2
        self._angular_threshold = 1.0e-12
        self._body_frame = body_frame

    @property
    def angular_threshold(self) -> float:
        """
        Get the angular convergence threshold.

        The angular threshold is used both to identify points close to
        the ellipse axes and as the convergence threshold used to
        stop the iterations in the transform(Vector3D, Frame,
        AbsoluteDate)
        """

        return self._angular_threshold

    @angular_threshold.setter
    def angular_threshold(self, angular_threshold: float):
        """Set the angular convergence threshold."""

        self._angular_threshold = angular_threshold

    @property
    def equatorial_radius(self) -> float:
        """Get the equatorial radius of the body."""

        return self._a_val

    @property
    def flattening(self):
        """Get the flattening of the body: f = (a-b)/a."""

        return self._flattening

    @property
    def body_frame(self):
        """Get body frame."""

        return self._body_frame

    def get_cartesian_intersection_point(
        self,
        line: Line,
        close: np.ndarray,
        frame: Frame,
        date: AbsoluteDate,
    ) -> np.ndarray:
        """
        Get the intersection point of a line with the surface of the body.
        A line may have several intersection points with a closed
        surface (we consider the one point case as a degenerated two
        points case). The close parameter is used to select which of
        these points should be returned. The selected point is the one
        that is closest to the close point.

        Parameters
        ----------
            line : test line (may intersect the body or not)
            close : point used for intersections selection
            frame : frame in which line is expressed
            date : date of the line in given frame

        Returns
        -------
            result : intersection point at altitude zero or null if the line does
                not intersect the surface
        """

        # Transform line and close to body frame
        frame_to_body_frame = frame.getTransformTo(self._body_frame, date)
        line_in_body_frame = StaticTransform.cast_(frame_to_body_frame).transformLine(line)

        # Compute some miscellaneous variables
        point = line_in_body_frame.getOrigin()
        x_val = point.getX()
        y_val = point.getY()
        z_val = point.getZ()
        z_2 = z_val * z_val
        r_2 = x_val * x_val + y_val * y_val

        direction = line_in_body_frame.getDirection()
        d_x = direction.getX()
        d_y = direction.getY()
        d_z = direction.getZ()
        cz_2 = d_x * d_x + d_y * d_y

        # Abscissa of the intersection as a root of a 2nd degree polynomial :
        # a k^2 - 2 b k + c = 0
        a_val = 1.0 - self._e_2 * cz_2
        b_val = -(self._g_2 * (x_val * d_x + y_val * d_y) + z_val * d_z)
        c_val = self._g_2 * (r_2 - self._radius_2) + z_2
        b_2 = b_val * b_val
        a_c = a_val * c_val

        if b_2 < a_c:
            return None

        s_val = math.sqrt(b_2 - a_c)
        k_1 = (b_val - s_val) / a_val if b_val < 0 else c_val / (b_val + s_val)
        k_2 = c_val / (a_val * k_1)

        # Select the right point
        close_in_body_frame = StaticTransform.cast_(frame_to_body_frame).transformPosition(Vector3D(close.tolist()))
        close_abscissa = line_in_body_frame.getAbscissa(close_in_body_frame)
        k_val = k_1 if math.fabs(k_1 - close_abscissa) < math.fabs(k_2 - close_abscissa) else k_2

        return to_array_v(line_in_body_frame.pointAt(k_val).toArray())

    def get_cartesian_intersection_point_vec(self, close: np.ndarray, points: np.ndarray) -> np.ndarray:
        """
        Get the intersection points of lines with the surface of the body.
        A line may have several intersection points with a closed
        surface (we consider the one point case as a degenerated two
        points case). The close parameter is used to select which of
        these points should be returned. The selected point is the one
        that is closest to the close point.

        Parameters
        ----------
            close : point used for intersections selection
            points : necessary to get the line origin

        Returns
        -------
            result : intersection points at altitude zero or null if the lines does
                not intersect the surface
        """

        # Get the lines origins
        delta = points - close
        norm_sq = get_norm_sq_n(delta)

        # Compute some miscellaneous variables
        zero = compute_linear_combination_2_arr(np.ones_like(norm_sq), close, -dot_n(close, delta) / norm_sq, delta)
        x_val = zero[..., 0]
        y_val = zero[..., 1]
        z_val = zero[..., 2]
        z_2 = z_val * z_val
        r_2 = x_val * x_val + y_val * y_val

        factor = 1.0 / np.sqrt(norm_sq)
        direction = factor[..., np.newaxis] * delta
        d_x = direction[..., 0]
        d_y = direction[..., 1]
        d_z = direction[..., 2]
        cz_2 = d_x * d_x + d_y * d_y

        # Abscissa of the intersection as a root of a 2nd degree polynomial :
        # a k^2 - 2 b k + c = 0
        a_val = 1.0 - self._e_2 * cz_2
        b_val = -(self._g_2 * (x_val * d_x + y_val * d_y) + z_val * d_z)
        c_val = self._g_2 * (r_2 - self._radius_2) + z_2
        b_2 = b_val * b_val
        a_c = a_val * c_val

        res = np.zeros_like(delta) + np.nan
        ind_not_none = np.where(b_2 >= a_c)[0]

        if np.size(ind_not_none) > 0:
            s_val = np.sqrt(b_2[ind_not_none] - a_c[ind_not_none])
            ind_b_val_neg = np.where(b_val[ind_not_none] < 0)
            ind_b_val_pos = np.where(b_val[ind_not_none] >= 0)
            k_1 = np.zeros_like(s_val)
            k_1[ind_b_val_neg] = (b_val[ind_not_none][ind_b_val_neg] - s_val[ind_b_val_neg]) / a_val[ind_not_none][
                ind_b_val_neg
            ]
            k_1[ind_b_val_pos] = c_val[ind_not_none][ind_b_val_pos] / (
                b_val[ind_not_none][ind_b_val_pos] + s_val[ind_b_val_pos]
            )
            k_2 = c_val[ind_not_none] / (a_val[ind_not_none] * k_1)

            # Select the right point
            close_abscissa = dot_n(close - zero, direction)[ind_not_none]
            k_val = np.where(np.abs(k_1 - close_abscissa) < np.abs(k_2 - close_abscissa), k_1, k_2)

            cart_points = compute_linear_combination_2_arr(
                np.ones_like(k_val), zero[ind_not_none], k_val, direction[ind_not_none]
            )

            res[ind_not_none] = cart_points

        return res

    def get_intersection_point(
        self,
        line: Line,
        close: np.ndarray,
        frame: Frame,
        date: AbsoluteDate,
    ) -> Union[None, np.ndarray]:
        """
        Get the intersection point of a line with the surface of the body.
        A line may have several intersection points with a closed
        surface (we consider the one point case as a degenerated two
        points case). The close parameter is used to select which of
        these points should be returned. The selected point is the one
        that is closest to the close point.

        Parameters
        ----------
            line : test line (may intersect the body or not)
            close : point used for intersections selection
            frame : frame in which line is expressed
            date : date of the line in given frame

        Returns
        -------
            result : intersection point at altitude zero or null if the line does
                not intersect the surface
        """

        intersection = self.get_cartesian_intersection_point(line, close, frame, date)

        if intersection is None:
            return None

        i_x = intersection[0]
        i_y = intersection[1]
        i_z = intersection[2]

        lambda_val = math.atan2(i_y, i_x)
        phi = math.atan2(i_z, self._g_2 * math.sqrt(i_x * i_x + i_y * i_y))

        return np.array([phi, lambda_val, 0.0])

    def get_intersection_point_vec(self, close: np.ndarray, points: np.ndarray) -> Union[None, np.ndarray]:
        """
        Get the intersection points of lines with the surface of the body.
        A line may have several intersection points with a closed
        surface (we consider the one point case as a degenerated two
        points case). The close parameter is used to select which of
        these points should be returned. The selected point is the one
        that is closest to the close point.

        Parameters
        ----------
            close : points used for intersections selection
            points : necessary to compute line origin

        Returns
        -------
            result : intersection point at altitude zero or null if the line does
                not intersect the surface
        """

        intersection = self.get_cartesian_intersection_point_vec(close, points)

        if np.all(np.isnan(intersection)):
            return None

        i_x = intersection[:, 0]
        i_y = intersection[:, 1]
        i_z = intersection[:, 2]

        lambda_val = np.arctan2(i_y, i_x)
        phi = np.arctan2(i_z, self._g_2 * np.sqrt(i_x * i_x + i_y * i_y))

        return np.array([phi, lambda_val, np.zeros(phi.shape[0])]).T

    def transform_from_point(self, latitudes: np.ndarray, longitudes: np.ndarray, h_vals: np.ndarray) -> np.ndarray:
        """
        Transform a surface-relative point to a Cartesian point.

        Parameters
        ----------
            latitudes : surface-relative point latitudes [lat_point1, lat_point2, ..., lat_pointn],
            longitudes : surface-relative points longitudes [longi_point1, longi_point2, ..., longi_pointn]
            warning must be same length as latitudes
            h_vals : surface-relative point altitudes [alt_pix1, alt_pix2, ..., alt_pixn]
            warning must be same length as latitudes

        Returns
        -------
            result : points cartesian coordinates at the same location (but as a cartesian points)
            [x_point1, x_point2,..., x_pointn], [y_point1, y_point2, ..., y_pointn], [z_point1, z_point2, ..., z_pointn]
        """

        if not isinstance(latitudes, np.ndarray):
            latitudes = np.asarray(latitudes)
            longitudes = np.asarray(longitudes)
            h_vals = np.asarray(h_vals)

        return transform_from_point_optim(latitudes, longitudes, h_vals, self.a_val, self._e_2, self._g_2)

    def transform_from_point_vec(self, geodetic_point: np.ndarray) -> np.ndarray:
        """
        Transform a surface-relative point to a Cartesian point.

        Parameters
        ----------
            geodetic_point[0] : surface-relative point latitudes [lat_point1, lat_point2, ..., lat_pointn],
            geodetic_point[1] : surface-relative points longitudes [longi_point1, longi_point2, ..., longi_pointn]
            warning must be same length as latitudes
            geodetic_point[2] : surface-relative point altitudes [alt_pix1, alt_pix2, ..., alt_pixn]
            warning must be same length as latitudes

        Returns
        -------
            result : points cartesian coordinates at the same location (but as a cartesian points)
            [x_point1, x_point2,..., x_pointn], [y_point1, y_point2, ..., y_pointn], [z_point1, z_point2, ..., z_pointn]
        """

        return transform_from_point_optim(
            geodetic_point[:, 0], geodetic_point[:, 1], geodetic_point[:, 2], self.a_val, self._e_2, self._g_2
        ).T

    def transform_from_frame(self, point: np.ndarray) -> np.ndarray:
        """
        Transform a Cartesian point to a surface-relative point.

        Parameters
        ----------
            point : cartesian point
            frame : frame in which cartesian point is expressed
            date : date of the computation (used for frame conversions)

        Returns
        -------
            result : point at the same location but as a surface-relative point
        """

        output = self.transform_from_frame_vec(point[np.newaxis, ...])
        return output.reshape((3,))

    def transform_from_frame_vec(self, point: np.ndarray) -> np.ndarray:
        """
        Transform Cartesian points to surface-relative points.

        Parameters
        ----------
            point : cartesian points

        Returns
        -------
            result : point at the same location but as a surface-relative point
        """
        assert point.shape[1] == 3

        return transform_from_frame_cy(
            point,
            self.POL_EQU_ANGULAR_THRESHOLD,
            self._radius_2,
            self.c_val,
            self.a_val,
            self._e_2,
            self._g_val,
            self._ap_2,
        )

    def project_to_ground_from_point(
        self,
        point: np.ndarray,
        date: AbsoluteDate,
        frame: Frame,
    ) -> np.ndarray:
        """
        Project a point to the ground

        Parameters
        ----------
            point : point to project
            date : current date
            frame : frame in which moving point is expressed

        Returns
        -------
            result : ground point exactly at the local vertical of specified point,
                in the same frame as specified point
        """

        # Transform point to body frame
        to_body = frame.getTransformTo(self._body_frame, date)
        p_vect = StaticTransform.cast_(to_body).transformPosition(Vector3D(point.tolist()))
        z_val = p_vect.getZ()
        r_val = math.hypot(p_vect.getX(), p_vect.getY())

        # Set up the 2D meridian ellipse
        meridian = Ellipse(
            to_array(0.0, 0.0, 0.0),
            to_array(1.0, 0.0, 0.0) if r_val == 0 else to_array(p_vect.getX() / r_val, p_vect.getY() / r_val, 0.0),
            to_array(0.0, 0.0, 1.0),
            self._a_val,
            self._c_val,
            self._body_frame,
        )

        # Find the closest point in the meridian plane
        ground_point = meridian.to_space(meridian.project_to_ellipse_from_point(np.array([r_val, z_val])))

        res = to_body.getInverse().transformPosition(Vector3D(ground_point.tolist()))
        resp = to_array(res.getX(), res.getY(), res.getZ())
        # Transform point back to initial frame
        return resp

    def project_to_ground_from_pv(
        self,
        pv_coordinates: TimeStampedPVCoordinates,
        frame: Frame,
    ) -> TimeStampedPVCoordinates:
        """
        Project a moving point to the ground

        Parameters
        ----------
            pv_coordinates : moving point
            frame : frame in which Cartesian point is expressed

        Returns
        -------
            result : ground point exactly at the local vertical of specified point,
                in the same frame as specified point
        """

        # Transform point to body frame
        to_body = frame.getTransformTo(self._body_frame, pv_coordinates.getDate())
        pv_in_body_frame = to_body.transformPVCoordinates(pv_coordinates)
        p_vect = pv_in_body_frame.getPosition()
        r_val = math.hypot(p_vect.getX(), p_vect.getY())

        # Set up the 2D ellipse corresponding to first principal curvature along meridian
        meridian = (
            to_array(1.0, 0.0, 0.0) if r_val == 0 else to_array(p_vect.getX() / r_val, p_vect.getY() / r_val, 0.0)
        )
        first_principal_curvature = Ellipse(
            to_array(0.0, 0.0, 0.0),
            meridian,
            to_array(0.0, 0.0, 1.0),
            self.a_val,
            self.c_val,
            self._body_frame,
        )

        # Project coordinates in the meridian plane
        gp_first = first_principal_curvature.project_to_ellipse_from_pv(pv_in_body_frame)
        gp_p = gp_first.getPosition()

        gp_p_x = Decimal(gp_p.getX())
        gp_p_y = Decimal(gp_p.getY())
        meridian_x = Decimal(meridian[0])
        meridian_y = Decimal(meridian[1])

        g_r = float(gp_p_x * meridian_x + gp_p_y * meridian_y)
        g_z = float(Decimal(gp_p.getZ()))

        # Topocentric frame
        east = to_array(-float(meridian_y), float(meridian_x), 0.0)
        zenith = compute_linear_combination_2(
            g_r * self.c_val / self.a_val,
            meridian,
            g_z * self.a_val / self.c_val,
            to_array(0.0, 0.0, 1.0),
        )
        zenith *= 1.0 / get_norm(zenith)
        north = cross(zenith, east)

        # Set up the ellipse corresponding to second principal curvature in the zenith/east plane
        second_principal_curvature = self.get_plane_section(to_array_v(gp_p.toArray()), north)
        gp_second = second_principal_curvature.project_to_ellipse_from_pv(pv_in_body_frame)

        gp_v = gp_first.getVelocity().add(gp_second.getVelocity())
        gp_a = gp_first.getAcceleration().add(gp_second.getAcceleration())

        # Moving projected point
        ground_pv = TimeStampedPVCoordinates(
            pv_coordinates.getDate(),
            gp_p,
            gp_v,
            gp_a,
        )

        # Transform moving projected point back to initial frame
        return to_body.getInverse().transformPVCoordinates(ground_pv)
