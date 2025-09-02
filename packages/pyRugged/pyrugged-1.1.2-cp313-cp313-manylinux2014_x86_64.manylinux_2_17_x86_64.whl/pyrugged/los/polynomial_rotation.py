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

"""pyrugged Class PolynomialRotation"""

from typing import List, Union

import numpy as np
from numpy.polynomial.polynomial import polyval
from org.hipparchus.geometry.euclidean.threed import (
    FieldVector3D,
    Vector3D,
)
from org.orekit.time import AbsoluteDate

from pyrugged.los.rotation import Rotation, RotationConvention
from pyrugged.utils.derivative_generator import DerivativeGenerator
from pyrugged.utils.parameter_driver import ParameterDriver


class PolynomialRotation:
    """LOS transform based on a rotation with polynomial angle."""

    SCALE = 1.0 * (2 ** (-20))

    def __init__(
        self,
        name: str,
        axis: np.ndarray,
        reference_date: AbsoluteDate,
        polynomial_coeff: List[float],
    ):
        """Builds a new instance.

        Parameters
        ----------
            name : name of the rotation (used for estimated parameters identification)
            axis : rotation_axis
            reference_date : reference date for the polynomial angle
            polynomial_coeff : polynomial coefficients of the polynomial angle, with the constant term at index 0
        """

        if isinstance(axis, Vector3D):
            self.axis = np.array(axis.toArray())
        else:
            self.axis = axis
        self.reference_date = reference_date
        self.coefficients_drivers = []
        self._axis_ds = None
        self._angle_ds = None

        for index, value in enumerate(polynomial_coeff):
            self.coefficients_drivers.append(
                ParameterDriver(f'{name}{"["}{index}{"]"}', value, self.SCALE, float("-inf"), float("inf"))
            )

        # resetting_observer = CustomParameterObserver()
        # for driver in self.coefficients_drivers:
        #     driver.addObserver(resetting_observer)

    # pylint: disable="unused-argument"
    def transform_los(self, i: int, los: np.ndarray, date: AbsoluteDate = None) -> np.ndarray:
        """Transform a line-of-sight.

        Parameters
        ----------
            i : LOS pixel index
            los : line-of-sight to transform
            date : current date

        Returns
        -------
            result : transformed line-of-sight
        """

        # Lazy evaluation of the rotation
        coefficients = []
        for _index, driver in enumerate(self.coefficients_drivers):
            coefficients.append(driver.value)

        return Rotation(
            self.axis,
            float(polyval(date.durationFrom(self.reference_date), coefficients)),
            RotationConvention.VECTOR_OPERATOR,
        ).applyTo(los)

    def transform_los_arr(self, pixels: List[int], los: np.ndarray, dates: List[AbsoluteDate] = None) -> np.ndarray:
        """Transform a series of line-of-sight.

        Parameters
        ----------
            pixels : LOS pixel index
            los : line-of-sight to transform
            dates : current dates

        Returns
        -------
            result : transformed line-of-sight
        """

        # Lazy evaluation of the rotation
        coefficients = []
        for _index, driver in enumerate(self.coefficients_drivers):
            coefficients.append(driver.value)

        angle_values = []
        for _, date in enumerate(dates):
            angle_values.append(float(polyval(date.durationFrom(self.reference_date), coefficients)))

        return Rotation(
            self.axis,
            angle_values,
            RotationConvention.VECTOR_OPERATOR,
        ).applyTo(los)

    # pylint: disable="unused-argument"
    def transform_los_derivatives(
        self, i: int, los: np.ndarray, date: AbsoluteDate, generator: DerivativeGenerator
    ) -> Union[np.ndarray, FieldVector3D]:
        """Transform a line-of-sight's' derivatives.

        Used for LOS calibration purposes. It allows to compute
        the Jacobian matrix of the LOS with respect to the parameters, which
        are typically polynomials coefficients representing rotation angles.
        These polynomials can be used for example to model thermo-elastic effects.

        Parameters
        ----------
            i : LOS pixel index
            los : line-of-sight to transform
            date : current date
            generator : generator to use for building Derivative instances

        Returns
        -------
            result : Line of sight, and its first partial derivatives with respect to the parameters
        """
        # todo: add test for this function when derivative generator are available
        # field = generator.getField()
        #
        # if self._axis_ds is None or not self._axis_ds.getField().equals(field):
        #     # Lazy evaluation of the rotation
        #     axis_d = FieldVector3D(
        #         generator.constant(self.axis.getX()),
        #         generator.constant(self.axis.getY()),
        #         generator.constant(self.axis.getZ()),
        #     )
        #
        #     angle_d = MathArrays.buildArray(field, len(self.coefficients_drivers))
        #
        #     for index in angle_d.length:
        #         angle_d[index] = generator.variable(self.coefficients_drivers[index])
        #
        #     # Cache evaluated rotation parameters
        #     axis_ds = axis_d
        #     angle_ds = angle_d
        #
        # else:
        #     # Reuse cached values
        #     axis_d = self._axis_ds
        #     angle_d = self._angle_ds
        #
        # # Evaluate polynomial, with all its partial derivatives
        # t_val = date.durationFrom(self.reference_date)
        # alpha = field.getZero()
        #
        # k_val = self._angle_ds.length - 1
        # while k_val >= 0:
        #     alpha = alpha.multiply(t_val).add(angle_d[k_val])
        #
        #     k_val -= 1
        #
        # return FieldRotation(axis_d, alpha, RotationConvention.VECTOR_OPERATOR).applyTo(los)

        raise NotImplementedError("Derivatives generator not supported yet")

    def get_parameters_drivers(self) -> List[ParameterDriver]:
        """Get coefficient drivers parameter."""

        return self.coefficients_drivers
