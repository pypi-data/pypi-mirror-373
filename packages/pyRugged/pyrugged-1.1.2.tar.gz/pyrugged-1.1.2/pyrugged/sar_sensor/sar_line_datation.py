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

"""pyrugged Class SARLineDatation"""
from typing import List

import numpy as np

# pylint: disable=unused-argument
from org.orekit.time import AbsoluteDate
from scipy.interpolate import griddata, interpn


class SARLineDatation:
    """Linear model for sar line datation."""

    def __init__(
        self, pixels: np.ndarray, rows: np.ndarray, reference_date: AbsoluteDate, corresponding_date_gap: np.ndarray
    ):
        """Builds a new instance.

        Parameters
        ----------
            rows : array of lines number considered for which we know the date. For RADARSAT
            information given in product are given for pixel halves, so we have to take into account when building
            sar_line_datation.

            pixels : array of columns / pixels number for which we know the date. For RADARSAT information given in
            product are given for pixel halves, but for column it is already taken
            into account of the pyrruged model so no need to take into account when initializing

            reference_date : reference date, can be whatever.

            corresponding_date_gap : array of difference with reference_date in second for each line[i] pixel[j]

            corresponding date - reference date.
        """

        self._rows = rows
        self._pixels = pixels
        self._reference_date = reference_date
        self._corresponding_date_gap = corresponding_date_gap

    @property
    def get_rows(self) -> np.array:
        """Get lines which were used to build the date model."""

        return self._rows

    @property
    def get_pixels(self) -> np.array:
        """Get pixles which were used to build the date model."""

        return self._pixels

    @property
    def get_corresponding_dates(self) -> np.array:
        """Get dates which were used to build the date model."""

        return self._corresponding_date_gap

    def get_date(self, pixel_row: np.ndarray) -> List[AbsoluteDate]:
        """Get the date for a line by interpolating (pixel, row).

        Parameters
        ----------
            pixel_row : array [pixel, row] for which the date wants to be known, must be given like this :
            np.array([[pix_col1, pix_lin1], [pix_col2, pix_line2], ..., [pix_coln, pi_linen])
            if multiples pixel coordinates

        Returns
        -------
            result : date for [pixel, row]
        """

        interp = interpn(
            (self._pixels, self._rows),
            self._corresponding_date_gap,
            pixel_row,
            method="linear",
            bounds_error=False,
            fill_value=None,
        )

        dates = []
        for date_gap in interp:
            dates.append(self._reference_date.shiftedBy(float(date_gap)))
        return dates

    def get_row_from_date(self, dates: List[AbsoluteDate], pix_column: float = 0.0) -> List[float]:
        """Get the row for a given date by interpolating (date).

        Parameters
        ----------
            dates : date for which we want to know the row
            pix_column : can be omitted for RADARSAT, if not given for Sentinel will be set to 0.0 which is fine as
            date doesn't vary a lot along columns. Can be obtained with sar_sensor.get_pix_from_range

        Returns
        -------
            result : corresponding row for date
        """

        rows = self._rows
        dates_for_pix = self._corresponding_date_gap

        # If Sentinel case, date depends not only on the line but also depends on the column
        if len(np.shape(self._corresponding_date_gap)) > 1:
            # In order to use griddata the dates_for_pixels is flatten, and in order to interpolatte, the
            # rows is repeted ([row1, ..., rown, row1, ..., rown, row1, ..., rown ...]
            dates_for_pix = dates_for_pix.reshape(-1)
            for _col_count in range(0, np.shape(self._corresponding_date_gap)[1]):
                rows = np.concatenate((rows, self._rows))

        # Compute dates gap with reference date
        date_gap_from_ref_date = []
        for date in dates:
            date_gap_from_ref_date.append(date.durationFrom(self._reference_date))
        # Only range_values restricted to column pix_column are interpolated (still kept range_values for each lines)
        interp = griddata(
            dates_for_pix,
            rows,
            np.array(date_gap_from_ref_date),
            method="linear",
            fill_value=0,
        )
        return interp
