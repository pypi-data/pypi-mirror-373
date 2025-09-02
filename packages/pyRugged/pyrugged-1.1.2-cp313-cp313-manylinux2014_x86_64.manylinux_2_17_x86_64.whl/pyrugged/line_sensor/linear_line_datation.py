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

"""pyrugged Class LinearLineDatation"""
from typing import Union

import numpy as np

# pylint: disable=unused-argument
from org.orekit.time import AbsoluteDate

try:
    from org.asgard.utils import AbsoluteDateArrayHandling
except ImportError:
    from org.orekit.rugged.utils import AbsoluteDateArrayHandling


class LinearLineDatation:
    """Linear model for line datation."""

    def __init__(self, reference_date: AbsoluteDate, reference_line: float, rate: float):
        """Builds a new instance.

        Parameters
        ----------
            reference_date : reference date
            reference_line : line number at reference date
            rate : rate of lines scanning (lines / seconds)
        """

        self._reference_date = reference_date
        self._reference_line = reference_line
        self._rate = rate

    @property
    def reference_line(self) -> float:
        """Get reference line parameter."""

        return self._reference_line

    @property
    def reference_date(self) -> AbsoluteDate:
        """Get reference line parameter."""

        return self._reference_date

    def get_rate(self, line_number: float = None) -> float:
        """Get the rate of lines scanning.

        Parameters
        ----------
            line_number : line number (not used but kept to respect API of LineDatation)

        Returns
        -------
            rate : rate of lines scanning (lines / seconds)
        """

        return self._rate

    def get_date(self, line_number: Union[float, np.array]) -> Union[AbsoluteDate, np.array]:
        """Get the date / dates for one line / several line.

        Parameters
        ----------
            line_number : line number float if only I date wants to be known for 1 line / np.array consisting of several
            line numbers if several dates want to be known in this c

        Returns
        -------
            result : date(s) at which line(s) are acquired
            (float if only 1 line number, np.array if several lines numbers)
        """

        if len(np.shape(line_number)) > 0:
            # If line number is an array then we use multipleShiftedBy to compute an array of dates corresponding to
            # the given np.array lines
            reference_date_array_handling = AbsoluteDateArrayHandling(
                np.array([self._reference_date] * len(line_number))
            )
            return reference_date_array_handling.shiftedBy(
                ((line_number.reshape(-1) - self._reference_line) / self._rate).tolist()
            )

        # If line_number is float then we use shiftedBy method of AbsoluteDate
        # which return an AbsoluteDate.
        return self._reference_date.shiftedBy(float((line_number - self._reference_line) / self._rate))

    def get_line(self, date: AbsoluteDate) -> float:
        """Get the line for a given date.

        Parameters
        ----------
            date : date

        Returns
        -------
            result : line number
        """

        return self._reference_line + self._rate * date.durationFrom(self._reference_date)
