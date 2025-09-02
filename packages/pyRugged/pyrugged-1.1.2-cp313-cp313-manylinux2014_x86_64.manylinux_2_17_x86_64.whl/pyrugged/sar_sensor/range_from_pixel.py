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

"""pyrugged Class RangeFromColumn"""
from typing import List, Union

import numpy as np
from scipy.interpolate import griddata, interpn

from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.utils.constants import Constants


class RangeGridCreation:
    """Range grid creation tools."""

    def __init__(self, total_number_pix: float, polynom_coef: np.ndarray):
        """Builds a new instance.

        Parameters
        ----------
            total_number_pix : total number of pixels
            polynom_coef : array containing polynom coefficient for gr -> sr (RADARSAT),
            from highest degree to the constant term
        """

        self._total_number_pix = total_number_pix
        self._polynom_coef = polynom_coef

    @property
    def get_total_pix_number(self):
        """Get total number of pixels."""

        return self._total_number_pix

    def ground_range_to_slant_range_polynom_application(
        self, pixel_size, ground_range_origin, pixel, increasing
    ) -> Union[np.ndarray, np.poly1d]:
        """Build range grid to interpolate for range from pixel class for RADARSAT given polynom coefficient.

        Parameters
        ----------
            pixel_size : pixel size
            ground_range_origin : ground range origin for polynom computation
            pixel : pixel number for which the distance wants to be known, pixels must be indexed from 0
            to total_pix_number - 1
            increasing : given pixel time ordering range values should be reorganised (increasing false)
            or not (increasing true)

        Returns
        -------
            result : range for pixel (distance)
        """

        if not increasing:
            pixel = self._total_number_pix - (pixel + 1)

        # Adding 1 to have pixel number between 1 and pix number, adding 0.5 because of radarsat conventions
        return np.polyval(self._polynom_coef, (pixel + 1.0 - 0.5) * pixel_size - ground_range_origin)


class RangeFromPixel:
    """Range from pixel computation."""

    def __init__(
        self,
        pixels_cols: np.ndarray,
        rows: np.ndarray,
        corresponding_range: np.ndarray,
        conversion_to_distance_needed: bool = False,
        interpolation_method: str = "linear",
    ):
        """Builds a new instance.

        Parameters
        ----------
            pixels_cols : array of pixels column numbers. For RADARSAT information given in product are given for
            pixel halves, but for column it is already taken into account in the pyrugged model so no need to take
            into account when initializing.

            rows : array of pixels row numbers.

            corresponding_range : corresponding range for each pixel in order to interpolate. For RadarSat
            images this can be obtained by applying distSR polynoms for Sentinel by interpolation in given grids. For
            sentinel 1 it is okay to give a corresponding_range in sec (slant range time) in this case the boolean

            conversion_to_distance_needed must be set to true to convert time to distance when the range is asked

            interpolation_method: interpolation method, "linear" by default fast but imprecise. Use "cubic_legacy"
            for better precision.
        """

        self._pixels_cols = pixels_cols
        self._rows = rows
        self._corresponding_range = corresponding_range
        self._conversion_to_distance_needed = conversion_to_distance_needed
        # By default linear interpolation. For RADARSAT product don't need cubic interpolation,
        # so for RADARSAT no need to give values for several pixel and line range value
        self._interpolation_method = interpolation_method
        if self._interpolation_method == "cubic":
            if len(self._rows) < 4 or len(self._pixels_cols) < 4:
                raise PyRuggedError(PyRuggedMessages.SAR_NOT_ENOUGH_PIXEL_LINE_VALUES_FOR_CUBIC_INTERP.value)

    @property
    def get_pixel_rows(self) -> np.array:
        """Get number of lines of pixels."""

        return self._rows

    @property
    def get_pixel_columns(self) -> np.array:
        """Get number of columns of pixels."""

        return self._pixels_cols

    @property
    def get_ranges_matrix(self) -> np.array:
        """Get number of columns of pixels."""

        return self._corresponding_range

    def get_range(self, coordinates: np.ndarray) -> List[float]:
        """Interpolate range at pixel

        Parameters
        ----------
            coordinates : np.ndarray containing pixel coordinates [col, row] for which the range wants to be known, must
            be given like this : np.ndarray([[pix_col1, pix_lin1], [pix_col2, pix_line2]]) if multiple coordinates

        Returns
        -------
            interp[0] : range for given pixel, in distance (m) (for sentinel for example, the interpolated time will
             be converted to distance)
        """
        interp = interpn(
            (self._pixels_cols, self._rows),
            self._corresponding_range,
            coordinates,
            method=self._interpolation_method,
            bounds_error=False,
            fill_value=None,
        )
        distance_range = interp
        if self._conversion_to_distance_needed:
            distance_range = Constants.SPEED_OF_LIGHT * distance_range / 2.0
        return distance_range

    def get_pix_from_range(self, d_range: List[float]) -> List[float]:
        """Interpolate column for a given range.

        Parameters
        ----------
            d_range : range for which we want to know the column

        Returns
        -------
            interp : column for a given range
        """
        if self._conversion_to_distance_needed:
            d_range = 2.0 * d_range / Constants.SPEED_OF_LIGHT
        interp = griddata(
            self._corresponding_range,
            self._pixels_cols,
            d_range,
            method=self._interpolation_method,
            fill_value=None,
        )
        return interp
