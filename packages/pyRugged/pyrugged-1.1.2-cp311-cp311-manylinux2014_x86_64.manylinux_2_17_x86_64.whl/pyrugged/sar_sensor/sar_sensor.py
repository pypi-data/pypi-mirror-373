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

"""pyrugged Class SARSensor"""
from typing import List

import numpy as np
from org.orekit.time import AbsoluteDate

from pyrugged.sar_sensor.doppler_model import DopplerModel
from pyrugged.sar_sensor.range_from_pixel import RangeFromPixel
from pyrugged.sar_sensor.sar_line_datation import SARLineDatation


class SARSensor:
    """SAR sensor model."""

    def __init__(
        self,
        name: str,
        datation_model: SARLineDatation,
        range_model: RangeFromPixel,
        doppler_model: DopplerModel,
        antenna_pointing_right: bool,
    ):
        """Builds a new instance.

        Parameters
        ----------
            name : name of the sensor
            datation_model : datation model
            range_model : range (distance) model
            doppler_model : doppler model
            antenna_pointing_right : is antenna pointing right (True) or left (False)
        """

        self._name = name
        self._datation_model = datation_model
        self._range_model = range_model
        self._doppler_model = doppler_model
        self._antenna_pointing_right = antenna_pointing_right

    @property
    def name(self) -> str:
        """Get the name of the sensor."""

        return self._name

    @property
    def datation_model(self) -> SARLineDatation:
        """Get datation model parameter."""

        return self._datation_model

    @property
    def range_model(self) -> RangeFromPixel:
        """Get range model parameter."""

        return self._range_model

    @property
    def doppler_model(self) -> DopplerModel:
        """Get doppler model parameter."""

        return self._doppler_model

    @property
    def is_antenna_pointing_right(self) -> bool:
        """Get antenna pointing, True = right, False = left."""

        return self._antenna_pointing_right

    @property
    def get_doppler(self) -> float:
        """Get the doppler term, only Zero Doppler available,
        general Doppler model still to be developed."""

        return self._doppler_model.get_doppler

    def get_date(self, coordinates_pix_row: float) -> List[AbsoluteDate]:
        """Get the date.

        Parameters
        ----------
            coordinates_pix_row : coordinate for which the date wants to be known, must be given like this :
            np.array([[pix_col1, pix_lin1], [pix_col2, pix_line2]])

        Returns
        -------
            date corresponding to coordinates [pix, row]
        """

        return self._datation_model.get_date(coordinates_pix_row)

    def get_row_from_date(self, date: AbsoluteDate, pixel_column: float = None) -> float:
        """Get the row for a given date by interpolating (date). For inverse location rows  dimensions must match
        corresponding_date_gap dimension as we use scipy.griddata to retrieve pixel row (when building the instance).

        Parameters
        ----------
            date : date for which we want to know the row
            pixel_column : pixel number
        Returns
        -------
            corresponding row for date
        """

        return self._datation_model.get_row_from_date(date, pixel_column)

    def get_range(self, coordinates_pix_row: np.ndarray) -> List[float]:
        """Get the range.

        Parameters
        ----------
            coordinates_pix_row : coordinate for which the range wants to be known, must be given like this :
            np.array([[pix_col1, pix_lin1], [pix_col2, pix_line2]])

        Returns
        -------
            range corresponding to coordinates [pix, row]
        """

        return self._range_model.get_range(coordinates_pix_row)

    def get_pix_from_range(self, d_range: float) -> float:
        """Interpolate column for a given range. For inverse location rows  dimensions must match
        corresponding_date_gap dimension as we use scipy.griddata to retrieve pixel column (when building the instance).

        Parameters
        ----------
            d_range : range for which we want to know the column

        Returns
        -------
            column for a given range
        """
        return self._range_model.get_pix_from_range(d_range)
