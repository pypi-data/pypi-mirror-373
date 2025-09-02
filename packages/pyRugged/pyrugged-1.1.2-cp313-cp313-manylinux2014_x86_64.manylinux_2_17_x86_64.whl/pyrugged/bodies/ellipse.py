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

"""pyrugged Class Ellipse"""

# pylint: disable=import-error, too-many-instance-attributes, too-many-locals
import math

import numpy as np
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.frames import Frame
from org.orekit.utils import TimeStampedPVCoordinates

from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    compute_linear_combination_2,
    compute_linear_combination_3,
    dot,
    to_array_v,
)


class Ellipse:
    """
    Model of a 2D ellipse in 3D space.

    These ellipses are mainly created as plane sections of general 3D ellipsoids,
    but can be used for other purposes.
    """

    ANGULAR_THRESHOLD = 1.0e-12

    def __init__(
        self, center: np.ndarray, u_vect: np.ndarray, v_vect: np.ndarray, a_val: float, b_val: float, frame: Frame
    ):
        """
        Constructor.

        Parameters
        ----------
            center : Center of the 2D ellipse
            u_vect : unit vector along the major axis
            v_vect : unit vector along the minor axis
            a_val : semi major axis
            b_val : semi minor axis
            frame : frame in which the ellipse is defined
        """

        self._center = center
        self._u_vect = u_vect
        self._v_vect = v_vect
        self._a_val = a_val
        self._b_val = b_val
        self._frame = frame
        self._a_2 = a_val * a_val
        self._g_val = b_val / a_val
        self._g_2 = self._g_val * self._g_val
        self._e_2 = 1 - self._g_2
        self._b_2 = b_val * b_val
        self._evolute_factor_x = (self._a_2 - self._b_2) / (self._a_2 * self._a_2)
        self._evolute_factor_y = (self._b_2 - self._a_2) / (self._b_2 * self._b_2)

    @property
    def center(self) -> np.ndarray:
        """Get the center of the 2D ellipse."""

        return self._center

    @property
    def u_vect(self) -> np.ndarray:
        """Get the unit vector along the major axis."""

        return self._u_vect

    @property
    def v_vect(self) -> np.ndarray:
        """Get the unit vector along the minor axis."""

        return self._v_vect

    @property
    def a_val(self) -> float:
        """Get the semi major axis."""

        return self._a_val

    @property
    def b_val(self) -> float:
        """Get the semi minor axis."""

        return self._b_val

    @property
    def frame(self) -> Frame:
        """Get the defining frame."""

        return self._frame

    def point_at(self, theta: float) -> np.ndarray:
        """
        Get a point of the 2D ellipse.

        Parameters
        ----------
            theta : angular parameter on the ellipse (really the eccentric anomaly)

        Returns
        -------
            result : ellipse point at theta, in underlying ellipsoid frame
        """

        return self.to_space(np.array([self._a_val * float(np.cos(theta)), self._b_val * float(np.sin(theta))]))

    def to_space(self, point: np.array) -> np.ndarray:
        """
        Create a point from its ellipse-relative coordinates.

        Parameters
        ----------
            point : point defined with respect to ellipse

        Returns
        -------
            result : point defined with respect to 3D frame
        """

        return compute_linear_combination_3(
            1.0, self._center, float(point[0]), self._u_vect, float(point[1]), self._v_vect
        )

    def to_plane(self, point: np.ndarray) -> np.array:
        """
        Project a point to the ellipse plane.

        Parameters
        ----------
            point : point defined with respect to 3D frame

        Returns
        -------
            result : point defined with respect to ellipse
        """

        delta = point - self._center
        return np.array([dot(delta, self._u_vect), dot(delta, self._v_vect)])

    def project_to_ellipse_from_point(self, point: np.ndarray) -> np.ndarray:
        """
        Find the closest ellipse point.

        Parameters
        ----------
            point : point in the ellipse plane to project on the ellipse itself

        Returns
        -------
            result : closest point belonging to 2D meridian ellipse
        """

        x_val = math.fabs(point[0])
        y_val = float(point[1])

        if x_val <= self.ANGULAR_THRESHOLD * math.fabs(y_val):

            # The point is almost on the minor axis, approximate the ellipse with
            # the osculating circle whose center is at evolute cusp along minor axis
            osculating_radius = self._a_2 / self._b_val
            evolute_cusp_z = float(np.copysign(self._a_val * self._e_2 / self._g_val, -y_val))
            delta_z = y_val - evolute_cusp_z
            ratio = osculating_radius / math.hypot(delta_z, x_val)

            return np.array([float(np.copysign(ratio * x_val, float(point[0]))), evolute_cusp_z + ratio * delta_z])

        if math.fabs(y_val) <= self.ANGULAR_THRESHOLD * x_val:

            # The point is almost on the major axis
            osculating_radius = self._b_2 / self._a_val
            evolute_cusp_r = self._a_val * self._e_2
            delta_r = x_val - evolute_cusp_r

            if delta_r >= 0:

                # The point is outside of the ellipse evolute, approximate the ellipse
                # with the osculating circle whose center is at evolute cusp along major axis
                ratio = osculating_radius / math.hypot(y_val, delta_r)
                return np.array([float(np.copysign(evolute_cusp_r + ratio * delta_r, float(point[0]))), ratio * y_val])

            # The point is on the part of the major axis within ellipse evolute
            # we can compute the closest ellipse point analytically
            r_ellipse = x_val / self._e_2
            return np.array(
                [
                    float(np.copysign(r_ellipse, float(point[0]))),
                    float(np.copysign(self._g_val * math.sqrt(self._a_2 - r_ellipse * r_ellipse), y_val)),
                ]
            )

        # Initial point at evolute cusp along major axis
        omega_x = self._a_val * self._e_2
        omega_y = 0.0

        projected_x = x_val
        projected_y = y_val
        delta_x = float("inf")
        delta_y = float("inf")
        count = 0
        threshold = self.ANGULAR_THRESHOLD * self.ANGULAR_THRESHOLD * self._a_2

        # This loop usually converges in 3 iterations
        while ((delta_x * delta_x + delta_y * delta_y) > threshold) and ((count + 1) < 100):

            # Find point at the intersection of ellipse and line going from query point to evolute point
            d_x = x_val - omega_x
            d_y = y_val - omega_y
            alpha = self._b_2 * d_x * d_x + self._a_2 * d_y * d_y
            beta_prime = self._b_2 * omega_x * d_x + self._a_2 * omega_y * d_y
            gamma = self._b_2 * omega_x * omega_x + self._a_2 * omega_y * omega_y - self._a_2 * self._b_2
            delta_prime = beta_prime * beta_prime - alpha * gamma

            if beta_prime <= 0:
                ratio = (math.sqrt(delta_prime) - beta_prime) / alpha

            else:
                ratio = -gamma / (math.sqrt(delta_prime) + beta_prime)

            previous_x = projected_x
            previous_y = projected_y

            projected_x = omega_x + ratio * d_x
            projected_y = omega_y + ratio * d_y

            # Find new evolute point
            omega_x = self._evolute_factor_x * projected_x * projected_x * projected_x
            omega_y = self._evolute_factor_y * projected_y * projected_y * projected_y

            # Compute convergence parameters
            delta_x = projected_x - previous_x
            delta_y = projected_y - previous_y

        return np.array([float(np.copysign(projected_x, float(point[0]))), projected_y])

    def project_to_ellipse_from_pv(self, pv_coordinates: TimeStampedPVCoordinates) -> TimeStampedPVCoordinates:
        """
        Project position-velocity-acceleration on an ellipse.

        Parameters
        ----------
            pv_coordinates : position-velocity-acceleration to project, in the reference frame

        Returns
        -------
            result : projected position-velocity-acceleration
        """

        # Find the closest point in the meridian plane
        p_2d = self.to_plane(to_array_v(pv_coordinates.getPosition().toArray()))
        e_2d = self.project_to_ellipse_from_point(p_2d)

        # Tangent to the ellipse
        f_x = -self._a_2 * float(e_2d[1])
        f_y = self._b_2 * float(e_2d[0])
        f_2 = f_x * f_x + f_y * f_y
        f_val = math.sqrt(f_2)
        tangent = np.array([f_x / f_val, f_y / f_val])

        # Normal to the ellipse (towards interior)
        normal = np.array([-tangent[1], tangent[0]])

        # Center of curvature
        x_2 = float(e_2d[0]) * float(e_2d[0])
        y_2 = float(e_2d[1]) * float(e_2d[1])
        e_x = self._evolute_factor_x * x_2
        e_y = self._evolute_factor_y * y_2
        omega_x = e_x * float(e_2d[0])
        omega_y = e_y * float(e_2d[1])

        # Velocity projection ratio
        rho = math.hypot(float(e_2d[0]) - omega_x, float(e_2d[1]) - omega_y)
        d_val = math.hypot(float(p_2d[0]) - omega_x, float(p_2d[1]) - omega_y)
        projection_ratio = rho / d_val

        # Tangential velocity
        p_dot_2d = np.array(
            [
                dot(to_array_v(pv_coordinates.getVelocity().toArray()), self._u_vect),
                dot(to_array_v(pv_coordinates.getVelocity().toArray()), self._v_vect),
            ]
        )
        p_dot_tangent = float(p_dot_2d[0] * tangent[0] + p_dot_2d[1] * tangent[1])
        p_dot_normal = float(p_dot_2d[0] * normal[0] + p_dot_2d[1] * normal[1])
        e_dot_tangent = projection_ratio * p_dot_tangent
        e_dot_2d = e_dot_tangent * tangent

        tangent_dot = (
            self._a_2 * self._b_2 * (float(e_2d[0]) * float(e_dot_2d[1]) - float(e_2d[1]) * float(e_dot_2d[0])) / f_2
        ) * normal

        # Velocity of the center of curvature in the meridian plane
        omega_x_dot = 3 * e_x * e_dot_tangent * float(tangent[0])
        omega_y_dot = 3 * e_y * e_dot_tangent * float(tangent[1])

        # Derivative of the projection ratio
        voz = omega_x_dot * float(tangent[1]) - omega_y_dot * float(tangent[0])
        vsz = -p_dot_normal
        projection_ratio_dot = ((rho - d_val) * voz - rho * vsz) / (d_val * d_val)

        # Acceleration
        p_dot_dot_2d = np.array(
            [
                dot(to_array_v(pv_coordinates.getAcceleration().toArray()), self._u_vect),
                dot(to_array_v(pv_coordinates.getAcceleration().toArray()), self._v_vect),
            ]
        )

        p_dot_dot_tangent = float(p_dot_dot_2d[0] * tangent[0] + p_dot_dot_2d[1] * tangent[1])
        p_dot_tangent_dot = float(p_dot_2d[0] * tangent_dot[0] + p_dot_2d[1] * tangent_dot[1])
        e_dot_dot_tangent = (
            projection_ratio * (p_dot_dot_tangent + p_dot_tangent_dot) + projection_ratio_dot * p_dot_tangent
        )
        e_dot_dot_2d = e_dot_dot_tangent * tangent + e_dot_tangent * tangent_dot

        # Back to 3D
        e_3d = self.to_space(e_2d)
        e_dot_3d = compute_linear_combination_2(
            float(e_dot_2d[0]),
            self._u_vect,
            float(e_dot_2d[1]),
            self._v_vect,
        )
        e_dot_dot_3d = compute_linear_combination_2(
            float(e_dot_dot_2d[0]),
            self._u_vect,
            float(e_dot_dot_2d[1]),
            self._v_vect,
        )

        return TimeStampedPVCoordinates(
            pv_coordinates.getDate(),
            Vector3D(e_3d.tolist()),
            Vector3D(e_dot_3d.tolist()),
            Vector3D(e_dot_dot_3d.tolist()),
        )

    def get_center_of_curvature(self, point: np.ndarray) -> np.ndarray:
        """
        Find the center of curvature (point on the evolute) at the nadir of a point.

        Parameters
        ----------
            point : point in the ellipse frame

        Returns
        -------
            result : center of curvature of the ellipse directly at point nadir
        """

        projected = self.project_to_ellipse_from_point(point)
        return np.array(
            [
                self._evolute_factor_x * float(projected[0]) * float(projected[0]) * float(projected[0]),
                self._evolute_factor_y * float(projected[1]) * float(projected[1]) * float(projected[1]),
            ]
        )
