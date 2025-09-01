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

"""pyrugged Class SinusoidalRotation"""

from typing import List

import numpy as np
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.time import AbsoluteDate

from pyrugged.los.rotation import Rotation, RotationConvention
from pyrugged.utils.parameter_driver import ParameterDriver


class SinusoidalRotation:
    """LOS transform based on a rotation with sinusoidal function."""

    SCALE = 1.0 * (2 ** (-20))

    def __init__(
        self,
        name: str,
        axis: Vector3D,
        reference_date: AbsoluteDate,
        amplitude: float,
        frequency: float,
        phase: float,
    ):
        """Builds a new instance.

        Parameters
        ----------
            name : name of the rotation (used for estimated parameters identification)
            axis : rotation_axis
            reference_date : reference date for the polynomial angle
            amplitude: amplitude of the sinusoide
            frequency: frequency of the sinusoide,
            phase: phase of the sinusoide,
        """

        if isinstance(axis, Vector3D):
            self.axis = np.array(axis.toArray())
        else:
            self.axis = axis
        self.reference_date = reference_date
        self.coefficients_drivers = []
        self._axis_ds = None
        self._angle_ds = None
        self._amplitude = amplitude
        self._frequency = frequency
        self._phase = phase

        self.coefficients_drivers.append(
            ParameterDriver(f'{name}{"_amplitude"}', amplitude, self.SCALE, float("-inf"), float("inf"))
        )
        self.coefficients_drivers.append(
            ParameterDriver(f'{name}{"_frequency"}', frequency, self.SCALE, float("-inf"), float("inf"))
        )
        self.coefficients_drivers.append(
            ParameterDriver(f'{name}{"_phase"}', phase, self.SCALE, float(-2 * np.pi), float(2 * np.pi))
        )

    # pylint: disable=unused-argument
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
        amplitude_coef = self.coefficients_drivers[0].value
        frequency_coef = self.coefficients_drivers[1].value
        phase_coef = self.coefficients_drivers[2].value

        sinusoidal_time = date.durationFrom(self.reference_date)
        angle = amplitude_coef * np.sin(2 * np.pi * frequency_coef * sinusoidal_time + phase_coef)

        return Rotation(
            self.axis,
            float(angle),
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

        amplitude_coef = self.coefficients_drivers[0].value
        frequency_coef = self.coefficients_drivers[1].value
        phase_coef = self.coefficients_drivers[2].value

        angle_values = []
        for _, date in enumerate(dates):
            sinusoidal_time = date.durationFrom(self.reference_date)
            angle_values.append(amplitude_coef * np.sin(2 * np.pi * frequency_coef * sinusoidal_time + phase_coef))

        return Rotation(
            self.axis,
            angle_values,
            RotationConvention.VECTOR_OPERATOR,
        ).applyTo(los)

    def get_parameters_drivers(self) -> List[ParameterDriver]:
        """Get coefficient drivers parameter."""

        return self.coefficients_drivers
