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

"""pyrugged Class FixedRotation"""

# pylint: disable=import-error
import math
from typing import List, Union

import numpy as np
from org.hipparchus.geometry.euclidean.threed import (
    FieldVector3D,
    Vector3D,
)
from org.orekit.time import AbsoluteDate

from pyrugged.los.rotation import Rotation, RotationConvention
from pyrugged.utils.derivative_generator import DerivativeGenerator
from pyrugged.utils.math_utils import to_array_v  # pylint: disable=no-name-in-module
from pyrugged.utils.parameter_driver import ParameterDriver
from pyrugged.utils.parameter_observer import ParameterObserver


class FixedRotationParameterObserver(ParameterObserver):
    """Custom ParameterObserver class for FixedRotation"""

    def __init__(self, fixed_rotation):
        self._cls = fixed_rotation

    def value_changed(self, previous_value):
        self._cls.rotation = None
        self._cls.rds = None


class FixedRotation:
    """LOS transform based on a fixed rotation."""

    SCALE = 1.0 * (2 ** (-20))

    def __init__(self, name: str, axis: np.ndarray, angle: float):
        """Builds a new instance.

        Parameters
        ----------
            name : name of the rotation (used for estimated parameters identification)
            axis : rotation axis
            angle : rotation angle
        """

        if isinstance(axis, Vector3D):
            self._axis = to_array_v(axis.toArray())
        else:
            self._axis = axis

        self._rotation = None
        self._r_ds = None
        self._angle_driver = ParameterDriver(name, angle, self.SCALE, -2 * math.pi, 2 * math.pi)
        observer = FixedRotationParameterObserver(self)
        self._angle_driver.add_observer(observer)

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value

    @property
    def r_ds(self):
        return self._r_ds

    @r_ds.setter
    def r_ds(self, value):
        self._r_ds = value

    def get_parameters_drivers(self) -> List[ParameterDriver]:
        """Get angle_driver parameter."""

        return [self._angle_driver]

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
        if self._rotation is None:
            # Lazy evaluation of the rotation
            self._rotation = Rotation(self._axis, float(self._angle_driver.value), RotationConvention.VECTOR_OPERATOR)
        return self._rotation.applyTo(los)

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
        if self._rotation is None:
            # Lazy evaluation of the rotation
            self._rotation = Rotation(self._axis, float(self._angle_driver.value), RotationConvention.VECTOR_OPERATOR)
        return self._rotation.applyTo(los)

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

        # if self._r_ds is None or not self._r_ds.getQ0().getField().equals(generator.getField()):
        #
        #     # Lazy evaluation of the rotation
        #     axis_ds = FieldVector3D(
        #         generator.constant(self._axis.getX()),
        #         generator.constant(self._axis.getY()),
        #         generator.constant(self._axis.getZ()),
        #     )
        #
        #     angle_ds = generator.variable(self._angle_driver)
        #
        #     r_d = FieldRotation(axis_ds, angle_ds, RotationConvention.VECTOR_OPERATOR)
        #
        #     # Cache evaluated rotation
        #     self._r_ds = r_d
        #
        # return self._r_ds.applyTo(los)

        raise NotImplementedError("Derivatives generator not supported yet")
