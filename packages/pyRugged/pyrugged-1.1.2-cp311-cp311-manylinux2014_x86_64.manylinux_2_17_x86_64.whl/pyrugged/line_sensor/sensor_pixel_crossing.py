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

"""pyrugged Class SensorPixelCrossing"""
import math

import numpy as np
from org.orekit.time import AbsoluteDate
from scipy.optimize import brentq

from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    angle,
    compute_low_prec_linear_combination_2,
    cross,
    get_norm,
)


class SensorPixelCrossing:
    """Class devoted to locate where ground point crosses a sensor line.
    This class is used in the first stage of inverse location.
    """

    MARGIN = 10.0

    def __init__(
        self, sensor: LineSensor, mean_normal: np.ndarray, target_direction: np.ndarray, max_eval: int, accuracy: float
    ):
        """Builds a new instance.

        Parameters
        ----------
            sensor : sensor to consider
            mean_normal : mean plane normal of the line sensor
            target_direction : target direction in spacecraft frame
            max_eval : maximum number of evaluations
            accuracy : accuracy to use for finding crossing line number
        """

        self._sensor = sensor
        self._cross = cross(mean_normal, target_direction)
        self._cross *= 1.0 / get_norm(self._cross)
        self._max_eval = max_eval
        self._accuracy = accuracy

    def univariate_function(self, x_val: float, date: AbsoluteDate) -> float:
        """Univariate function"""

        return angle(self._cross, self.get_los(date, x_val)) - 0.5 * math.pi

    def locate_pixel(self, date: AbsoluteDate) -> float:
        """Locate pixel along sensor line.

        Parameters
        ----------
            date : current date

        Returns
        -------
            result : pixel location (NaN if the first and last
                pixels of the line do not bracket a location)
        """
        try:
            res = brentq(
                self.univariate_function,
                -self.MARGIN,
                self._sensor.nb_pixels - 1 + self.MARGIN,
                maxiter=self._max_eval,
                args=date,
            )
        except ValueError:
            res = math.nan

        return res

    def get_los(self, date: AbsoluteDate, x_val: float) -> np.ndarray:
        """Interpolate sensor pixels at some pixel index.

        Parameters
        ----------
            date : current date
            x_val : pixel index

        Returns
        -------
            result : interpolated direction for specified index
        """

        # Find surrounding pixels
        i_inf = int(max(0.0, min(float(self._sensor.nb_pixels - 2), math.floor(x_val))))
        i_sup = int(i_inf + 1)

        # Interpolate
        res = compute_low_prec_linear_combination_2(
            i_sup - x_val, self._sensor.get_los(date, i_inf), x_val - i_inf, self._sensor.get_los(date, i_sup)
        )
        return res / get_norm(res)
