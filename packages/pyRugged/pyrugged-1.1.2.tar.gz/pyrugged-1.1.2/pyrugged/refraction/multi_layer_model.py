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

"""pyrugged Class MultiLayerModel"""


import math

# pylint: disable=too-many-function-args, duplicate-code
from typing import List, Union

import numpy as np

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.bodies.geodesy import zenith
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.basic_scan_algorithm import BasicScanAlgorithm
from pyrugged.intersection.constant_elevation_algorithm import ConstantElevationAlgorithm
from pyrugged.intersection.duvenhage.duvenhage_algorithm import DuvenhageAlgorithm
from pyrugged.intersection.ignore_dem_algorithm import IgnoreDEMAlgorithm
from pyrugged.refraction.atmospheric_refraction import AtmosphericRefraction
from pyrugged.refraction.constant_refraction_layer import ConstantRefractionLayer
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    compute_low_prec_linear_combination_2,
    dot,
    get_norm,
)


class IntersectionLOS:
    """Container for the (position, LOS) of the intersection with the lowest atmospheric layer."""

    def __init__(self, intersection_pos: np.ndarray, intersection_los: np.ndarray):
        """Builds a new instance.

        Parameters
        ----------
            intersection_pos : position of the intersection
            intersection_los : line-of-sight of the intersection
        """

        self.intersection_pos = intersection_pos
        self.intersection_los = intersection_los

    def get_intersection_pos(self) -> np.ndarray:
        """Get intersection position"""

        return self.intersection_pos

    def get_intersection_los(self) -> np.ndarray:
        """Get intersection LOS"""

        return self.intersection_los


class MultiLayerModel(AtmosphericRefraction):
    """Atmospheric refraction model based on multiple layers with associated refractive index."""

    def __init__(self, ellipsoid: ExtendedEllipsoid, refraction_layers: List[ConstantRefractionLayer] = None):
        """Builds a new instance.

        Parameters
        ----------
            ellipsoid : ellipsoid to be used
            refraction_layers : the refraction layers to be used
                with this model (layers can be in any order).
        """

        super().__init__()
        self.ellipsoid = ellipsoid

        if refraction_layers is None:
            self.refraction_layers = []
            self.refraction_layers.append(ConstantRefractionLayer(100000.00, 1.000000))
            self.refraction_layers.append(ConstantRefractionLayer(50000.00, 1.000000))
            self.refraction_layers.append(ConstantRefractionLayer(40000.00, 1.000001))
            self.refraction_layers.append(ConstantRefractionLayer(30000.00, 1.000004))
            self.refraction_layers.append(ConstantRefractionLayer(23000.00, 1.000012))
            self.refraction_layers.append(ConstantRefractionLayer(18000.00, 1.000028))
            self.refraction_layers.append(ConstantRefractionLayer(14000.00, 1.000052))
            self.refraction_layers.append(ConstantRefractionLayer(11000.00, 1.000083))
            self.refraction_layers.append(ConstantRefractionLayer(9000.00, 1.000106))
            self.refraction_layers.append(ConstantRefractionLayer(7000.00, 1.000134))
            self.refraction_layers.append(ConstantRefractionLayer(5000.00, 1.000167))
            self.refraction_layers.append(ConstantRefractionLayer(3000.00, 1.000206))
            self.refraction_layers.append(ConstantRefractionLayer(1000.00, 1.000252))
            self.refraction_layers.append(ConstantRefractionLayer(0.00, 1.000278))
            self.refraction_layers.append(ConstantRefractionLayer(-1000.00, 1.000306))

        else:
            # Sort the layers from the highest (index = 0) to the lowest (index = size - 1)
            layers_dict = {}
            for layer in refraction_layers:
                layers_dict[layer.get_lowest_altitude()] = layer
            altitudes = layers_dict.keys()
            sorted_altitudes = sorted(altitudes, reverse=True)
            sorted_refraction_layers = [layers_dict[altitude] for altitude in sorted_altitudes]

            self.refraction_layers = sorted_refraction_layers

        # Get the lowest altitude of the atmospheric model
        self.atmosphere_lowest_altitude = self.refraction_layers[-1].get_lowest_altitude()

    def get_refraction_layers(self) -> List[ConstantRefractionLayer]:
        """Get refraction layers list."""

        return self.refraction_layers

    def compute_to_lowest_atmosphere_layer(
        self, sat_pos: np.ndarray, sat_los: np.ndarray, raw_intersection: np.ndarray
    ) -> IntersectionLOS:
        """Compute the (position, LOS) of the intersection with the lowest atmospheric layer.

        Parameters
        ----------
            sat_pos : satellite position, in body frame
            sat_los : satellite line-of-sight, in body frame
            raw_intersection : intersection point without refraction correction

        Returns
        -------
            result : the intersection position and LOS with the lowest atmospheric layer
        """

        if raw_intersection[2] < self.atmosphere_lowest_altitude:
            raise PyRuggedError(
                PyRuggedMessages.NO_LAYER_DATA.value, str(raw_intersection[2]), str(self.atmosphere_lowest_altitude)
            )

        pos = sat_pos
        los = sat_los / get_norm(sat_los)

        # Compute the intersection point with the lowest layer of atmosphere
        n_1 = -1
        point_gp = self.ellipsoid.transform(sat_pos, self.ellipsoid.body_frame, None)

        # Perform the exact computation (no optimization)
        # TBN: the refraction_layers is ordered from the highest to the lowest
        for refraction_layer in self.refraction_layers:
            if refraction_layer.get_lowest_altitude() > point_gp[2]:
                continue

            n_2 = refraction_layer.get_refractive_index()

            if n_1 > 0:
                # When we get here, we have already performed one iteration in the loop
                # so gp is the los intersection with the layers interface (it was a
                # point on ground at loop initialization, but is overridden at each iteration)

                # Get new los by applying Snell's law at atmosphere layers interfaces
                # we avoid computing sequences of inverse-trigo/trigo/inverse-trigo functions
                # we just use linear algebra and square roots, it is faster and more accurate

                # At interface crossing, the interface normal is z, the local zenith direction
                # the ray direction (i.e. los) is u in the upper layer and v in the lower layer
                # v is in the (u, zenith) plane, so we can say
                #  (1) v = α u + β z
                # with α>0 as u and v are roughly in the same direction as the ray is slightly bent

                # Let θ₁ be the los incidence angle at interface crossing
                # θ₁ = π - angle(u, zenith) is between 0 and π/2 for a downwards observation
                # let θ₂ be the exit angle at interface crossing
                # from Snell's law, we have n₁ sin θ₁ = n₂ sin θ₂ and θ₂ is also between 0 and π/2
                # we have:
                #   (2) u·z = -cos θ₁
                #   (3) v·z = -cos θ₂
                # combining equations (1), (2) and (3) and remembering z·z = 1 as z is normalized , we get
                #   (4) β = α cos θ₁ - cos θ₂
                # with all the expressions above, we can rewrite the fact v is normalized:
                #       1 = v·v
                #         = α² u·u + 2αβ u·z + β² z·z
                #         = α² - 2αβ cos θ₁ + β²
                #         = α² - 2α² cos² θ₁ + 2 α cos θ₁ cos θ₂ + α² cos² θ₁ - 2 α cos θ₁ cos θ₂ + cos² θ₂
                #         = α²(1 - cos² θ₁) + cos² θ₂
                # hence α² = (1 - cos² θ₂)/(1 - cos² θ₁)
                #          = sin² θ₂ / sin² θ₁
                # as α is positive, and both θ₁ and θ₂ are between 0 and π/2, we finally get
                #       α  = sin θ₂ / sin θ₁
                #   (5) α  = n₁/n₂
                # the α coefficient is independent from the incidence angle,
                # it depends only on the ratio of refractive indices!
                #
                # Back to equation (4) and using again the fact θ₂ is between 0 and π/2, we can now write
                #       β = α cos θ₁ - cos θ₂
                #         = n₁/n₂ cos θ₁ - cos θ₂
                #         = n₁/n₂ cos θ₁ - √(1 - sin² θ₂)
                #         = n₁/n₂ cos θ₁ - √(1 - (n₁/n₂)² sin² θ₁)
                #         = n₁/n₂ cos θ₁ - √(1 - (n₁/n₂)² (1 - cos² θ₁))
                #         = n₁/n₂ cos θ₁ - √(1 - (n₁/n₂)² + (n₁/n₂)² cos² θ₁)
                #   (6) β = -k - √(k² - ζ)
                # Where ζ = (n₁/n₂)² - 1 and k = n₁/n₂ u·z, which is negative, and close to -1 for
                # nadir observations. As we expect atmosphere models to have small transitions between
                # layers, we have to handle accurately the case where n₁/n₂ ≈ 1 so ζ ≈ 0. In this case,
                # a cancellation occurs inside the square root: √(k² - ζ) ≈ √k² ≈ -k (because k is negative).
                # So β ≈ -k + k ≈ 0 and another cancellation occurs, outside of the square root.
                # This means that despite equation (6) is mathematically correct, it is prone to numerical
                # errors when consecutive layers have close refractive indices. A better equivalent
                # expression is needed. The fact β is close to 0 in this case was expected because
                # equation (1) reads v = α u + β z, and α = n₁/n₂, so when n₁/n₂ ≈ 1, we have
                # α ≈ 1 and β ≈ 0, so v ≈ u: when two layers have similar refractive indices, the
                # propagation direction is almost unchanged.
                #
                # The first step for the accurate computation of β is to compute ζ = (n₁/n₂)² - 1
                # accurately and avoid a cancellation just after a division (which is the least accurate
                # of the four operations) and a squaring. We will simply use:
                #   ζ = (n₁/n₂)² - 1
                #     = (n₁ - n₂) (n₁ + n₂) / n₂²
                # The cancellation is still there, but it occurs in the subtraction n₁ - n₂, which are
                # the most accurate values we can get.
                # The second step for the accurate computation of β is to rewrite equation (6)
                # by both multiplying and dividing by the dual factor -k + √(k² - ζ):
                #     β = -k - √(k² - ζ)
                #       = (-k - √(k² - ζ)) * (-k + √(k² - ζ)) / (-k + √(k² - ζ))
                #       = (k² - (k² - ζ)) / (-k + √(k² - ζ))
                # (7) β = ζ / (-k + √(k² - ζ))
                # expression (7) is more stable numerically than expression (6), because when ζ ≈ 0
                # its denominator is about -2k, there are no cancellation anymore after the square root.
                # β is computed with the same accuracy as ζ

                alpha = n_1 / n_2
                k_val = alpha * dot(los, zenith(point_gp))
                zeta = (n_1 - n_2) * (n_1 + n_2) / (n_2 * n_2)
                beta = zeta / (math.sqrt(k_val * k_val - zeta) - k_val)
                los = compute_low_prec_linear_combination_2(alpha, los, beta, zenith(point_gp))
            # In case the altitude of the intersection without atmospheric refraction
            # is above the lowest altitude of the atmosphere: stop the search
            if raw_intersection[2] > refraction_layer.get_lowest_altitude():
                break

            # Get for the intersection point: the position and the LOS
            pos = self.ellipsoid.point_at_altitude(pos, los, refraction_layer.get_lowest_altitude())
            point_gp = self.ellipsoid.transform(pos, self.ellipsoid.body_frame, None)

            n_1 = n_2

        return IntersectionLOS(pos, los)

    def apply_correction(
        self,
        sat_pos: np.ndarray,
        sat_los: np.ndarray,
        raw_intersection: np.ndarray,
        algorithm: Union[BasicScanAlgorithm, ConstantElevationAlgorithm, IgnoreDEMAlgorithm, DuvenhageAlgorithm],
    ) -> np.ndarray:
        """Apply correction to the intersected point with an atmospheric refraction model.

        Parameters
        ----------
            sat_pos : satellite position, in body frame
            sat_los : satellite line of sight, in body frame
            raw_intersection : intersection point before refraction correction
            algorithm : intersection algorithm

        Returns
        -------
            result : corrected point with the effect of atmospheric refraction
        """

        intersection_los = self.compute_to_lowest_atmosphere_layer(sat_pos, sat_los, raw_intersection)
        pos = intersection_los.get_intersection_pos()
        los = intersection_los.get_intersection_los()

        # At this stage the pos belongs to the lowest atmospheric layer.
        # We can compute the intersection of line of sight (los) with Digital Elevation Model
        # as usual (without atmospheric refraction).
        return algorithm.refine_intersection(self.ellipsoid, pos, los, raw_intersection)
