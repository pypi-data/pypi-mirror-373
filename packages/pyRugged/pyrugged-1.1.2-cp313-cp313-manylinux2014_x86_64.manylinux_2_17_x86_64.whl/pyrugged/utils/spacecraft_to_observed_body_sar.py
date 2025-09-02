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

"""pyrugged Class SpacecraftToObservedBodySAR"""


from typing import List

# pylint: disable=duplicate-code
import numpy as np
from java.util import ArrayList
from org.orekit.frames import Frame, Transform
from org.orekit.time import AbsoluteDate
from org.orekit.utils import (
    CartesianDerivativesFilter,
    ImmutableTimeStampedCache,
    TimeStampedPVCoordinates,
    TimeStampedPVCoordinatesHermiteInterpolator,
)

from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages


class SpacecraftToObservedBodySAR:
    """Provider for observation transforms."""

    # pylint: disable=too-many-branches, too-many-locals, too-many-arguments
    def __init__(  # noqa: C901
        self,
        body_frame: Frame,
        min_date: AbsoluteDate,
        max_date: AbsoluteDate,
        t_step: float,
        overshoot_tolerance: float,
        positions_velocities: List[TimeStampedPVCoordinates] = None,
        pv_interpolation_number: int = None,
        pv_filter: CartesianDerivativesFilter = None,
        sc_to_body: List[Transform] = None,
    ):
        """Builds a new instance.

        Parameters
        ----------
            body_frame : observed body frame
            min_date : start of search time span
            max_date : end of search time span
            t_step : step to use for spacecraft to body frame transforms cache computations
            overshoot_tolerance : tolerance in seconds allowed for 'min_date' and 'max_date' overshooting
                slightly the position and velocity ephemerides
            positions_velocities : satellite position and velocity
            pv_interpolation_number : number of points to use for position/velocity interpolation
            pv_filter : filter for derivatives from the sample to use in position/velocity interpolation
            sc_to_body: transforms sample from spacecraft frame to body frame
        """

        arg_set_1 = [
            positions_velocities,
            pv_interpolation_number,
            pv_filter,
        ]
        arg_set_2 = [sc_to_body]

        if all(arg is None for arg in arg_set_1) and all(arg is not None for arg in arg_set_2):
            self._body_frame = body_frame
            self._min_date = min_date
            self._max_date = max_date
            self._t_step = t_step
            self._overshoot_tolerance = overshoot_tolerance

            self._sc_to_body = sc_to_body
            self._body_to_sc = []
            for element in self._sc_to_body:
                self._body_to_sc.append(element.getInverse())

        elif all(arg is not None for arg in arg_set_1) and all(arg is None for arg in arg_set_2):
            self._body_frame = body_frame
            self._min_date = min_date
            self._max_date = max_date
            self._overshoot_tolerance = overshoot_tolerance

            # Safety checks
            min_pv_date = positions_velocities[0].getDate()
            max_pv_date = positions_velocities[-1].getDate()
            if min_pv_date.durationFrom(self._min_date) > self._overshoot_tolerance:
                raise PyRuggedError(PyRuggedMessages.OUT_OF_TIME_RANGE.value, self._min_date, min_pv_date, max_pv_date)
            if self._max_date.durationFrom(max_pv_date) > self._overshoot_tolerance:
                raise PyRuggedError(PyRuggedMessages.OUT_OF_TIME_RANGE.value, self._max_date, min_pv_date, max_pv_date)

            java_positions_velocities = ArrayList()
            for element in positions_velocities:
                java_positions_velocities.add(element)

            java_positions_velocities = ArrayList()
            for element in positions_velocities:
                java_positions_velocities.add(element)

            # Set up the cache for position-velocities
            pv_cache = ImmutableTimeStampedCache(pv_interpolation_number, java_positions_velocities)

            n_val = int(np.ceil(self._max_date.durationFrom(self._min_date) / t_step))

            self._t_step = t_step
            self._sc_to_body = []
            self._body_to_sc = []

            # Set 'date' value
            date = self._min_date
            while len(self._body_to_sc) < n_val:
                # Interpolate position-velocity, allowing slight extrapolation near the boundaries
                if date.compareTo(pv_cache.getEarliest().getDate()) < 0:
                    pv_interpolation_date = pv_cache.getEarliest().getDate()
                elif date.compareTo(pv_cache.getLatest().getDate()) > 0:
                    pv_interpolation_date = pv_cache.getLatest().getDate()
                else:
                    pv_interpolation_date = date

                time_interpolator = TimeStampedPVCoordinatesHermiteInterpolator(
                    min(pv_cache.getNeighbors(pv_interpolation_date, pv_interpolation_number).count(), 15), pv_filter
                )  # 15 => Maximum recommended by doc
                interpolated_pv = time_interpolator.interpolate(
                    pv_interpolation_date, pv_cache.getNeighbors(pv_interpolation_date, pv_interpolation_number)
                )

                pv_val = interpolated_pv.shiftedBy(date.durationFrom(pv_interpolation_date))

                # Store transform from spacecraft frame to body frame
                self._sc_to_body.append(Transform(date, pv_val))

                # Store transform from body frame to spacecraft frame
                self._body_to_sc.append(Transform(date, pv_val).getInverse())

                # Update 'date' value
                date = date.shiftedBy(self._t_step)
        else:
            print("WARNING : Wrong arguments sequence for SpacecraftToObservedBody")

    @property
    def body_frame(self) -> Frame:
        """Get the body frame."""

        return self._body_frame

    @property
    def min_date(self) -> AbsoluteDate:
        """Get the start of search time span."""

        return self._min_date

    @property
    def max_date(self) -> AbsoluteDate:
        """Get the end of search time span."""

        return self._max_date

    @property
    def t_step(self) -> float:
        """Get the step to use for spacecraft frame to body frame transforms cache computations."""

        return self._t_step

    @property
    def overshoot_tolerance(self) -> float:
        """Get the tolerance in seconds allowed for {@link #getMinDate()} and {@link #getMaxDate()} overshooting."""

        return self._overshoot_tolerance

    def get_sc_to_body(self, date: AbsoluteDate) -> Transform:
        """Get transform from spacecraft to observed body frame.

        Parameters
        ----------
            date : date of the transform

        Returns
        -------
            result : transform from spacecraft to observed body frame
        """

        return self.interpolate(date, self._sc_to_body)

    def get_body_to_sc(self, date: AbsoluteDate) -> Transform:
        """Get transform from observed body frame to spacecraft frame.

        Parameters
        ----------
            date : date of the transform

        Returns
        -------
            result : transform from observed body frame to spacecraft frame
        """

        return self.interpolate(date, self._body_to_sc)

    def interpolate(self, date: AbsoluteDate, transforms_list: List[Transform]) -> Transform:
        """Interpolate transform.

        Parameters
        ----------
            date : date of the transform
            transforms_list: transforms list to interpolate from

        Returns
        -------
            result : interpolated transform
        """

        # Check date range
        if not self.is_in_range(date):
            raise PyRuggedError(PyRuggedMessages.OUT_OF_TIME_RANGE.value, date, self.min_date, self.max_date)

        s_val = date.durationFrom(transforms_list[0].getDate()) / self.t_step
        index = int(max(0.0, min(float(len(transforms_list) - 1), float(np.rint(s_val)))))

        close = transforms_list[index]
        return close.shiftedBy(date.durationFrom(close.getDate()))

    def is_in_range(self, date: AbsoluteDate) -> bool:
        """Check if a date is in the supported range.

        Parameters
        ----------
            date : date to check

        Returns
        -------
            result : true if date is in the supported range
        """

        return (
            self.min_date.durationFrom(date) <= self.overshoot_tolerance
            and date.durationFrom(self.max_date) <= self.overshoot_tolerance
        )
