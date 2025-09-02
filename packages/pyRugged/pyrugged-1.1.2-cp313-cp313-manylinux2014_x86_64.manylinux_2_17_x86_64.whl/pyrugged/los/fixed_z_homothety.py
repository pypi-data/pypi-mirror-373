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

"""pyrugged Class FixedZHomothety"""

# pylint: disable=import-error
from typing import List, Union

import numpy as np
from org.hipparchus.geometry.euclidean.threed import FieldVector3D
from org.orekit.time import AbsoluteDate

from pyrugged.utils.derivative_generator import DerivativeGenerator
from pyrugged.utils.math_utils import to_array  # pylint: disable=no-name-in-module
from pyrugged.utils.parameter_driver import ParameterDriver


class FixedZHomothety:
    """Time independent los transform based on a homothety along the Z axis."""

    SCALE = 1.0 * (2**0)

    def __init__(self, name: str, factor_value: float):
        """Builds a new instance.

        Parameters
        ----------
            name : name of the homothety (used for estimated parameters identification)
            factor_value : Homothety factor
        """

        self.factor = factor_value
        self.factor_ds = None
        self.factor_driver = ParameterDriver(name, factor_value, self.SCALE, 0, float("inf"))

        # self.factor_driver.addObserver(CustomParameterObserver())

    def get_parameters_drivers(self) -> List[ParameterDriver]:
        """Get factor_driver parameter."""

        return [self.factor_driver]

    # pylint: disable=unused-argument
    def transform_los(self, i: int, los: np.ndarray, date: AbsoluteDate = None) -> np.ndarray:
        """Transform a line-of-sight.

        Parameters
        ----------
            i : LOS pixel index
            los : line-of-sight to transform
            date : None (set for transform_los prototype coherence with polynomial rotation)

        Returns
        -------
            result : transformed line-of-sight
        """

        if self.factor == 0.0:
            # Lazy evaluation of the homothety
            self.factor = self.factor_driver.value()

        return to_array(los[0], los[1], self.factor * los[2])

    def transform_los_arr(self, pixels: List[int], los: np.ndarray, dates: List[AbsoluteDate] = None) -> np.ndarray:
        """Transform a series of line-of-sight.

        Parameters
        ----------
            pixels : LOS pixel indexes
            los : line-of-sight to transform
            dates : None (set for transform_los prototype coherence with polynomial rotation)

        Returns
        -------
            result : transformed line-of-sight
        """

        if self.factor == 0.0:
            # Lazy evaluation of the homothety
            self.factor = self.factor_driver.value()

        return np.array([los[0], los[1], self.factor * los[2]])

    # pylint: disable=unused-argument
    def transform_los_derivatives(
        self, i: int, los: np.ndarray, generator: DerivativeGenerator
    ) -> Union[np.ndarray, FieldVector3D]:
        """Transform a line-of-sight's derivatives.

        Used for LOS calibration purposes. It allows to compute
        the Jacobian matrix of the LOS with respect to the parameters, which
        are typically polynomials coefficients representing rotation angles.
        These polynomials can be used for example to model thermo-elastic effects.

        Note that in order for the partial derivatives to be properly set up, the
        ParameterDriver.selected(arg)
        method must have been set to True for the various parameters returned
        by get_parameters_drivers() that should be estimated.

        Parameters
        ----------
            i : LOS pixel index
            los : line-of-sight to transform
            generator : generator to use for building Derivative instances

        Returns
        -------
            result : line of sight, and its first partial derivatives with respect to the parameters
        """
        # todo: add test for this function when derivative generator are available
        # if self.factor_ds is None or not self.factor_ds.getField().equals(generator.getField()):
        #     # Lazy evaluation of the homothety
        #     factor_d = generator.variable(self.factor_driver)
        #
        #     # Cache evaluated homothety
        #     self.factor_ds = factor_d
        #
        # else:
        #     # Reuse cache value
        #     factor_d = self.factor_ds
        #
        # return FieldVector3D(los.getX(), los.getY(), factor_d.multiply(los.getZ()))

        raise NotImplementedError("Derivatives generator not supported yet")
