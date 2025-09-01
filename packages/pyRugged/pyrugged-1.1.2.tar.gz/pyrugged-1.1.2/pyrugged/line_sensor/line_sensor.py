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

"""pyrugged Class LineSensor"""

import math
from typing import List, Union

import numpy as np
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.time import AbsoluteDate

from pyrugged.errors import dump_manager
from pyrugged.line_sensor.linear_line_datation import LinearLineDatation
from pyrugged.los.los_builder import FixedLOS, TransformsSequenceLOS
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    compute_low_prec_linear_combination_2,
    compute_low_prec_linear_combination_2_arr,
    to_array_v,
)
from pyrugged.utils.parameter_driver import ParameterDriver


class LineSensor:
    """Line sensor model."""

    def __init__(
        self,
        name: str,
        datation_model: LinearLineDatation,
        position: np.ndarray,
        los: Union[FixedLOS, TransformsSequenceLOS],
    ):
        """Builds a new instance.

        Parameters
        ----------
            name : name of the sensor
            datation_model : datation model
            position : sensor position in spacecraft frame
            los : line-of-sight in spacecraft frame
        """

        if isinstance(position, Vector3D):
            position = to_array_v(position.toArray())

        self._name = name
        self._datation_model = datation_model
        self._position = position
        self._los = los

    @property
    def los(self) -> Union[FixedLOS, TransformsSequenceLOS]:
        """Get the los built"""

        return self._los

    @property
    def name(self) -> str:
        """Get the name of the sensor."""

        return self._name

    @property
    def datation_model(self) -> LinearLineDatation:
        """Get datation model parameter."""

        return self._datation_model

    @property
    def position(self) -> np.ndarray:
        """Get the sensor position."""

        return self._position

    @property
    def nb_pixels(self) -> int:
        """Get the number of pixels."""

        return self._los.get_nb_pixels()

    @property
    def parameters_drivers(self) -> List[ParameterDriver]:
        """Get the drivers for LOS parameters."""

        return self._los.get_parameters_drivers()

    def get_los(self, date: AbsoluteDate, i: int) -> np.ndarray:
        """Get the pixel normalized line-of-sight at some date.

        Parameters
        ----------
            date : current date
            i : pixel index (must be between 0 and getNbPixels() - 1)

        Returns
        -------
            result : pixel normalized line-of-sight
        """

        los = self._los.get_los(i, date)

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_sensor_los(self, date, i, los)

        return los

    def get_los_arr(self, dates: List[AbsoluteDate], pixels: List[int]) -> List[np.ndarray]:
        """Get the pixel normalized line-of-sight at some date.

        Parameters
        ----------
            dates : current dates
            pixels : pixel indexes (must be between 0 and getNbPixels() - 1)

        Returns
        -------
            result : pixel normalized line-of-sight
        """

        los = self._los.get_los_arr(pixels, dates)

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_sensor_los_arr(self, dates, pixels, los)

        return los

    def get_interpolated_los(self, date: AbsoluteDate, i: float) -> np.ndarray:
        """Get the pixel normalized interpolated line-of-sight at some date.

        Parameters
        ----------
            date : current date
            i : pixel index (must be between 0 and getNbPixels() - 1)

        Returns
        -------
            interpolated_los : pixel normalized line-of-sight
        """

        i_inf = max(0, min(self.nb_pixels - 2, math.floor(i)))
        i_sup = i_inf + 1
        interpolated_los = compute_low_prec_linear_combination_2(
            i_sup - i, self._los.get_los(i_inf, date), i - i_inf, self._los.get_los(i_sup, date)
        )

        return interpolated_los

    def get_interpolated_los_arr(self, dates: List[AbsoluteDate], pixels: List[float]) -> np.ndarray:
        """Get the pixels normalized interpolated line-of-sight at some dates.

        Parameters
        ----------
            dates : current dates
            pixels : pixel indexes (must be between 0 and getNbPixels() - 1)

        Returns
        -------
            interpolated_los : pixel normalized line-of-sight
        """

        pixels = np.array(pixels)
        i_inf = np.fmax(0, np.fmin(self.nb_pixels - 2, np.int32(np.floor(pixels))))
        i_sup = i_inf + 1
        interpolated_los = compute_low_prec_linear_combination_2_arr(
            i_sup - pixels, self._los.get_los_arr(i_inf, dates), pixels - i_inf, self._los.get_los_arr(i_sup, dates)
        )

        return interpolated_los

    # def get_los_derivatives(self, date, i, generator):
    #     """Get the pixel normalized line-of-sight at some date,
    #     and their derivatives with respect to estimated parameters.

    #     Parameters
    #     ----------
    #         date : orekit.time.AbsoluteDate
    #             Current date
    #         i : int
    #             Pixel index (must be between 0 and getNbPixels() - 1)
    #         generator :
    #             Generator to use for building derivative instances

    #     Returns
    #     -------
    #         result : hipparchus.geometry.euclidean.threed.FieldVector3D
    #             Pixel normalized line-of-sight

    #     """

    #     return self.los.getLOSDerivatives(i, date, generator)

    # def get_interpolated_los_derivatives(self, date, i, generator):
    #     """Get the pixel normalized line-of-sight at some date,
    #     and their derivatives with respect to estimated parameters.

    #     Parameters
    #     ----------
    #         date : orekit.time.AbsoluteDate
    #             Current date
    #         i : int
    #             Pixel index (must be between 0 and getNbPixels() - 1)
    #         generator :
    #             Generator to use for building derivative instances

    #     Returns
    #     -------
    #         interpolated_los : hipparchus.geometry.euclidean.threed.FieldVector3D
    #             Pixel normalized line-of-sight

    #     """

    #     # Find surrounding pixels of pixelB (in order to interpolate LOS from pixelB (that is not an integer)
    #     i_inf = max(0, min(self.get_nb_pixels() - 2, np.floor(i)))
    #     i_sup = i_inf + 1

    #     interpolated_los = FieldVector3D(
    #         i_sup - i,
    #         self.los.getLOSDerivatives(i_inf, date, generator),
    #         i - i_inf,
    #         self.los.getLOSDerivatives(i_sup, date, generator),
    #     ).normalize()

    #     return interpolated_los

    def get_date(self, line_number: Union[float, np.array]) -> Union[AbsoluteDate, np.array]:
        """Get dates corresponding to all lines in lines np.array.

        Parameters
        ----------
            line_number : lines numbers

        Returns
        -------
            date : dates corresponding to lines numbers
        """

        dates = self._datation_model.get_date(line_number)

        if len(np.shape(line_number)) == 0:
            if dump_manager.DUMP_VAR is not None:
                dump_manager.DUMP_VAR.dump_sensor_datation(self, line_number, dates)

        return dates

    def get_line(self, date: AbsoluteDate) -> float:
        """Get the line number.

        Parameters
        ----------
            date : date

        Returns
        -------
            line_number : line number corresponding to date
        """

        line_number = self._datation_model.get_line(date)

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_sensor_datation(self, line_number, date)

        return line_number

    def get_rate(self, line_number: float = None) -> float:
        """Get the rate of lines scanning.

        Parameters
        ----------
            line_number : line number

        Returns
        -------
            rate : rate of lines scanning (lines / seconds)
        """

        rate = self._datation_model.get_rate(line_number)

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_sensor_rate(self, line_number, rate)

        return rate

    def dump_rate(self, line_number: float = None):
        """Dump sensor rate

        Parameters
        ----------
            line_number : line number

        """
        rate = self._datation_model.get_rate(line_number)

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_sensor_rate(self, line_number, rate)
