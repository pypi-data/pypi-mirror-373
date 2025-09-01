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

"""pyrugged Class Ellipsoid"""

# pylint: disable=import-error, too-many-locals
import math
from decimal import Decimal

import numpy as np
from org.orekit.frames import Frame

from pyrugged.bodies.ellipse import Ellipse
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    compute_linear_combination_2,
    compute_linear_combination_3,
    cross,
    distance,
    get_norm,
    orthogonal,
    to_array,
)


class Ellipsoid:
    """Modeling of a general three-axes ellipsoid."""

    SAFE_MIN = 2 ** (-1022)

    def __init__(self, frame: Frame, a_val: float, b_val: float, c_val: float):
        """
        Constructor.

        Parameters
        ----------
            frame : frame at the ellipsoid center, aligned with principal axes
            a_val : first semi-axis length
            b_val : second semi-axis length
            c_val : third semi-axis length
        """

        self._frame = frame
        self._a_val = a_val
        self._b_val = b_val
        self._c_val = c_val

    @property
    def frame(self) -> Frame:
        """Get the ellipsoid central frame."""

        return self._frame

    @property
    def a_val(self) -> float:
        """Get first semi-axis length."""

        return self._a_val

    @property
    def b_val(self) -> float:
        """Get second semi-axis length."""

        return self._b_val

    @property
    def c_val(self) -> float:
        """Get third semi-axis length."""

        return self._c_val

    def is_inside(self, point: np.ndarray) -> bool:
        """
        Check if a point is inside the ellipsoid.

        Parameters
        ----------
            point : point to check, in the ellipsoid frame

        Returns
        -------
            result : true if the point is inside the ellipsoid
        """

        scaled_x = point[0] / self._a_val
        scaled_y = point[1] / self._b_val
        scaled_z = point[2] / self._c_val

        return scaled_x * scaled_x + scaled_y * scaled_y + scaled_z * scaled_z <= 1.0

    def get_plane_section(self, plane_point: np.ndarray, plane_normal: np.ndarray) -> Ellipse:
        """
        Compute the 2D ellipse at the intersection of the 3D ellipsoid and a plane.

        Parameters
        ----------
            plane_point : point belonging to the plane, in the ellipsoid frame
            plane_normal : normal of the plane, in the ellipsoid frame

        Returns
        -------
            result : plane section or null if there are no intersections
        """

        # we define the points Q in the plane using two free variables τ and υ as:
        # Q = P + τ u + υ v
        # where u and v are two unit vectors belonging to the plane
        # Q belongs to the 3D ellipsoid so:
        # (xQ / a)² + (yQ / b)² + (zQ / c)² = 1
        # combining both equations, we get:
        #   (xP² + 2 xP (τ xU + υ xV) + (τ xU + υ xV)²) / a²
        # + (yP² + 2 yP (τ yU + υ yV) + (τ yU + υ yV)²) / b²
        # + (zP² + 2 zP (τ zU + υ zV) + (τ zU + υ zV)²) / c²
        # = 1
        # which can be rewritten:
        # α τ² + β υ² + 2 γ τυ + 2 δ τ + 2 ε υ + ζ = 0
        # with
        # α =  xU²  / a² +  yU²  / b² +  zU²  / c² > 0
        # β =  xV²  / a² +  yV²  / b² +  zV²  / c² > 0
        # γ = xU xV / a² + yU yV / b² + zU zV / c²
        # δ = xP xU / a² + yP yU / b² + zP zU / c²
        # ε = xP xV / a² + yP yV / b² + zP zV / c²
        # ζ =  xP²  / a² +  yP²  / b² +  zP²  / c² - 1
        # this is the equation of a conic (here an ellipse)
        # Of course, we note that if the point P belongs to the ellipsoid
        # then ζ = 0 and the equation holds at point P since τ = 0 and υ = 0
        u_vect = orthogonal(plane_normal)
        v_vect = cross(plane_normal, u_vect)
        v_vect *= 1.0 / get_norm(v_vect)
        xu_o_a = float(Decimal(u_vect[0])) / self._a_val
        yu_o_b = float(Decimal(u_vect[1])) / self._b_val
        zu_o_c = float(Decimal(u_vect[2])) / self._c_val
        xv_o_a = float(Decimal(v_vect[0])) / self._a_val
        yv_o_b = float(Decimal(v_vect[1])) / self._b_val
        zv_o_c = float(Decimal(v_vect[2])) / self._c_val
        xp_o_a = float(Decimal(plane_point[0])) / self._a_val
        yp_o_b = float(Decimal(plane_point[1])) / self._b_val
        zp_o_c = float(Decimal(plane_point[2])) / self._c_val
        alpha = xu_o_a * xu_o_a + yu_o_b * yu_o_b + zu_o_c * zu_o_c
        beta = xv_o_a * xv_o_a + yv_o_b * yv_o_b + zv_o_c * zv_o_c
        gamma = xu_o_a * xv_o_a + yu_o_b * yv_o_b + zu_o_c * zv_o_c
        delta = xp_o_a * xu_o_a + yp_o_b * yu_o_b + zp_o_c * zu_o_c
        epsilon = xp_o_a * xv_o_a + yp_o_b * yv_o_b + zp_o_c * zv_o_c
        zeta = xp_o_a * xp_o_a + yp_o_b * yp_o_b + zp_o_c * zp_o_c + 1.0 * -1.0

        # reduce the general equation α τ² + β υ² + 2 γ τυ + 2 δ τ + 2 ε υ + ζ = 0
        # to canonical form (λ/l)² + (μ/m)² = 1
        # using a coordinates change
        #       τ = τC + λ cosθ - μ sinθ
        #       υ = υC + λ sinθ + μ cosθ
        # or equivalently
        #       λ =   (τ - τC) cosθ + (υ - υC) sinθ
        #       μ = - (τ - τC) sinθ + (υ - υC) cosθ
        # τC and υC are the coordinates of the 2D ellipse center with respect to P
        # 2l and 2m and are the axes lengths (major or minor depending on which one is greatest)
        # θ is the angle of the 2D ellipse axis corresponding to axis with length 2l

        # choose θ in order to cancel the coupling term in λμ
        # expanding the general equation, we get: A λ² + B μ² + C λμ + D λ + E μ + F = 0
        # with C = 2[(β - α) cosθ sinθ + γ (cos²θ - sin²θ)]
        # hence the term is cancelled when θ = arctan(t), with γ t² + (α - β) t - γ = 0
        # As the solutions of the quadratic equation obey t₁t₂ = -1, they correspond to
        # angles θ in quadrature to each other. Selecting one solution or the other simply
        # exchanges the principal axes. As we don't care about which axis we want as the
        # first one, we select an arbitrary solution
        if math.fabs(gamma) < self.SAFE_MIN:
            tan_theta = 0.0

        else:
            b_ma = beta - alpha

            if b_ma >= 0:
                tan_theta = -2 * gamma / (b_ma + math.sqrt(b_ma * b_ma + 4 * gamma * gamma))
            else:
                tan_theta = -2 * gamma / (b_ma - math.sqrt(b_ma * b_ma + 4 * gamma * gamma))

        tan_2 = tan_theta * tan_theta
        cos_2 = 1 / (1 + tan_2)
        sin_2 = tan_2 * cos_2
        cos_sin = tan_theta * cos_2
        cos = math.sqrt(cos_2)
        sin = tan_theta * cos

        # choose τC and υC in order to cancel the linear terms in λ and μ
        # expanding the general equation, we get: A λ² + B μ² + C λμ + D λ + E μ + F = 0
        # with D = 2[ (α τC + γ υC + δ) cosθ + (γ τC + β υC + ε) sinθ]
        #      E = 2[-(α τC + γ υC + δ) sinθ + (γ τC + β υC + ε) cosθ]
        # θ can be eliminated by combining the equations
        # D cosθ - E sinθ = 2[α τC + γ υC + δ]
        # E cosθ + D sinθ = 2[γ τC + β υC + ε]
        # hence the terms D and E are both cancelled (regardless of θ) when
        #     τC = (β δ - γ ε) / (γ² - α β)
        #     υC = (α ε - γ δ) / (γ² - α β)
        denom = gamma * gamma - alpha * beta
        tau_c = (beta * delta - gamma * epsilon) / denom
        nu_c = (alpha * epsilon - gamma * delta) / denom

        # compute l and m
        # expanding the general equation, we get: A λ² + B μ² + C λμ + D λ + E μ + F = 0
        # with A = α cos²θ + β sin²θ + 2 γ cosθ sinθ
        #      B = α sin²θ + β cos²θ - 2 γ cosθ sinθ
        #      F = α τC² + β υC² + 2 γ τC υC + 2 δ τC + 2 ε υC + ζ
        # hence we compute directly l = √(-F/A) and m = √(-F/B)
        two_g_cs = 2 * gamma * cos_sin
        big_a = alpha * cos_2 + beta * sin_2 + two_g_cs
        big_b = alpha * sin_2 + beta * cos_2 - two_g_cs
        big_f = (alpha * tau_c + 2 * (gamma * nu_c + delta)) * tau_c + (beta * nu_c + 2 * epsilon) * nu_c + zeta

        l_val = math.sqrt(-big_f / big_a)
        m_val = math.sqrt(-big_f / big_b)

        if math.isnan(l_val + m_val):
            # The plane does not intersect the ellipsoid
            return None

        if l_val > m_val:
            return Ellipse(
                compute_linear_combination_3(1.0, plane_point, tau_c, u_vect, nu_c, v_vect),
                compute_linear_combination_2(cos, u_vect, sin, v_vect),
                compute_linear_combination_2(-sin, u_vect, cos, v_vect),
                l_val,
                m_val,
                self._frame,
            )

        return Ellipse(
            compute_linear_combination_3(1.0, plane_point, tau_c, u_vect, nu_c, v_vect),
            compute_linear_combination_2(sin, u_vect, -cos, v_vect),
            compute_linear_combination_2(cos, u_vect, sin, v_vect),
            m_val,
            l_val,
            self._frame,
        )

    def point_on_limb(self, observer: np.ndarray, outside: np.ndarray) -> np.ndarray:
        """
        Find a point on ellipsoid limb, as seen by an external observer.

        Parameters
        ----------
            observer : observer position in ellipsoid frame
            outside : point outside ellipsoid in ellipsoid frame, defining the phase around limb

        Returns
        -------
            result : point on ellipsoid limb
        """

        # There is no limb if we are inside the ellipsoid
        if self.is_inside(observer):
            raise ValueError("point is inside ellipsoid")

        # Cut the ellipsoid, to find an elliptical plane section
        normal = cross(observer, outside)
        section = self.get_plane_section(to_array(0.0, 0.0, 0.0), normal)

        # the point on limb is tangential to the ellipse
        # if T(xt, yt) is an ellipse point at which the tangent is drawn
        # if O(xo, yo) is a point outside of the ellipse belonging to the tangent at T,
        # then the two following equations holds:
        # (1) a² yt²   + b² xt²   = a² b²  (T belongs to the ellipse)
        # (2) a² yt yo + b² xt xo = a² b²  (TP is tangent to the ellipse)
        # using the second equation to eliminate yt from the first equation, we get
        # b² (a² - xt xo)² + a² xt² yo² = a⁴ yo²
        # (3) (a² yo² + b² xo²) xt² - 2 a² b² xo xt + a⁴ (b² - yo²) = 0
        # which can easily be solved for xt

        # To avoid numerical errors, the x and y coordinates in the ellipse plane are normalized using:
        # x' = x / a and y' = y / b
        #
        # This gives:
        # (1) y't² + x't² = 1
        # (2) y't y'o + x't x'o = 1
        #
        # And finally:
        # (3) (x'o² + y'o²) x't² - 2 x't x'o + 1 - y'o² = 0
        #
        # Solving for x't, we get the reduced discriminant:
        # delta' = beta'² - alpha' * gamma'
        #
        # With:
        # beta' = x'o
        # alpha' = x'o² + y'o²
        # gamma' = 1 - y'o²
        #
        # Simplifying to  cancel a term of x'o².
        # delta' = y'o² (x'o² + y'o² - 1) = y'o² (alpha' - 1)
        #
        # After solving for xt1, xt2 using (3) the values are substituted into (2) to
        # compute yt1, yt2. Then terms of x'o may be canceled from the expressions for
        # yt1 and yt2. Additionally a point discontinuity is removed at y'o=0 from both
        # yt1 and yt2.
        #
        # y't1 = (y'o - x'o d) / (x'o² + y'o²)
        # y't2 = (x'o y'o + d) / (x + sqrt(delta'))
        #
        # where:
        # d = sign(y'o) sqrt(alpha' - 1)

        # Get the point in ellipse plane frame (2D)
        observer_2d = section.to_plane(observer)

        # Normalize and compute intermediary terms
        a_p = section.a_val
        b_p = section.b_val
        xpo = float(observer_2d[0]) / a_p
        ypo = float(observer_2d[1]) / b_p
        xpo_2 = xpo * xpo
        ypo_2 = ypo * ypo
        alpha_p = ypo_2 + xpo_2
        gamma_p = 1.0 - ypo_2

        # Compute the roots
        # We know there are two solutions as we already checked the point is outside ellipsoid
        sqrt = math.sqrt(alpha_p - 1)
        sqrt_p = math.fabs(ypo) * sqrt
        sqrt_signed = float(np.copysign(sqrt, ypo))

        # Compute the roots (ordered by value)
        if xpo > 0:
            s_val = xpo + sqrt_p
            # xpt1 = (beta' + sqrt(delta')) / alpha' (with beta' = x'o)
            x_pt_1 = s_val / alpha_p
            # x't2 = gamma' / (beta' + sqrt(delta')) since x't1 * x't2 = gamma' / alpha'
            x_pt_2 = gamma_p / s_val
            # Get the corresponding values of y't
            y_pt_1 = (ypo - xpo * sqrt_signed) / alpha_p
            y_pt_2 = (xpo * ypo + sqrt_signed) / s_val

        else:
            s_val = xpo - sqrt_p
            # x't1 and x't2 are reverted compared to previous solution
            x_pt_1 = gamma_p / s_val
            x_pt_2 = s_val / alpha_p
            # Get the corresponding values of y't
            y_pt_2 = (ypo + xpo * sqrt_signed) / alpha_p
            y_pt_1 = (xpo * ypo - sqrt_signed) / s_val

        # De-normalize and express the two solutions in 3D
        tp_1 = section.to_space(np.array([a_p * x_pt_1, b_p * y_pt_1]))
        tp_2 = section.to_space(np.array([a_p * x_pt_2, b_p * y_pt_2]))

        # Return the limb point in the direction of the outside point
        result = tp_1 if distance(tp_1, outside) <= distance(tp_2, outside) else tp_2
        return result
