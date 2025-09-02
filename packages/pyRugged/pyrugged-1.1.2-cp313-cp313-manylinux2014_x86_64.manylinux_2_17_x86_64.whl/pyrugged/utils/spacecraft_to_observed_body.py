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

"""pyrugged Class SpacecraftToObservedBody"""

from typing import List, Union

# pylint: disable=duplicate-code
import numpy as np
from java.util import ArrayList
from java.util.stream import Collectors
from org.orekit.frames import Frame, Transform
from org.orekit.time import AbsoluteDate
from org.orekit.utils import (
    AngularDerivativesFilter,
    CartesianDerivativesFilter,
    ImmutableTimeStampedCache,
    TimeStampedAngularCoordinates,
    TimeStampedAngularCoordinatesHermiteInterpolator,
    TimeStampedPVCoordinates,
    TimeStampedPVCoordinatesHermiteInterpolator,
)

try:
    from org.asgard.utils import AbsoluteDateArrayHandling
except ImportError:
    from org.orekit.rugged.utils import AbsoluteDateArrayHandling

from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages


class SpacecraftToObservedBody:
    """Provider for observation transforms."""

    # pylint: disable=too-many-branches, too-many-locals, too-many-arguments
    def __init__(  # noqa: C901
        self,
        inertial_frame: Frame,
        body_frame: Frame,
        min_date: AbsoluteDate,
        max_date: AbsoluteDate,
        t_step: float,
        overshoot_tolerance: float,
        positions_velocities: List[TimeStampedPVCoordinates] = None,
        pv_interpolation_number: int = None,
        pv_filter: CartesianDerivativesFilter = None,
        quaternions: List[TimeStampedAngularCoordinates] = None,
        a_interpolation_number: int = None,
        a_filter: AngularDerivativesFilter = None,
        body_to_inertial: List[Transform] = None,
        sc_to_inertial: List[Transform] = None,
    ):
        """Builds a new instance.

        Parameters
        ----------
            inertial_frame : inertial frame
            body_frame : observed body frame
            min_date : start of search time span
            max_date : end of search time span
            t_step : step to use for inertial frame to body frame transforms cache computations
            overshoot_tolerance : tolerance in seconds allowed for 'min_date' and 'max_date' overshooting
                slightly the position, velocity and quaternions ephemerides
            positions_velocities : satellite position and velocity
            pv_interpolation_number : number of points to use for position/velocity interpolation
            pv_filter : filter for derivatives from the sample to use in position/velocity interpolation
            quaternions : satellite quaternions
            a_interpolation_number : number of points to use for attitude interpolation
            a_filter : filter for derivatives from the sample to use in attitude interpolation
            body_to_inertial : transforms sample from observed body frame to inertial frame
            sc_to_inertial : transforms sample from spacecraft frame to inertial frame
        """

        arg_set_1 = [
            positions_velocities,
            pv_interpolation_number,
            pv_filter,
            quaternions,
            a_interpolation_number,
            a_filter,
        ]
        arg_set_2 = [body_to_inertial, sc_to_inertial]

        if all(arg is None for arg in arg_set_1) and all(arg is not None for arg in arg_set_2):
            self._inertial_frame = inertial_frame
            self._body_frame = body_frame
            self._min_date = min_date
            self._max_date = max_date
            self._t_step = t_step
            self._overshoot_tolerance = overshoot_tolerance

            self._body_to_inertial = body_to_inertial
            self._sc_to_inertial = sc_to_inertial
            self._inertial_to_body = []
            for element in self._body_to_inertial:
                self._inertial_to_body.append(element.getInverse())

        elif all(arg is not None for arg in arg_set_1) and all(arg is None for arg in arg_set_2):
            self._inertial_frame = inertial_frame
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

            min_q_date = quaternions[0].getDate()
            max_q_date = quaternions[-1].getDate()
            if min_q_date.durationFrom(self._min_date) > self._overshoot_tolerance:
                raise PyRuggedError(PyRuggedMessages.OUT_OF_TIME_RANGE.value, self._min_date, min_q_date, max_q_date)
            if self._max_date.durationFrom(max_q_date) > self._overshoot_tolerance:
                raise PyRuggedError(PyRuggedMessages.OUT_OF_TIME_RANGE.value, self._max_date, min_q_date, max_q_date)

            java_positions_velocities = ArrayList()
            for element in positions_velocities:
                java_positions_velocities.add(element)

            java_quaternions = ArrayList()
            for element in quaternions:
                java_quaternions.add(element)

            java_positions_velocities = ArrayList()
            for element in positions_velocities:
                java_positions_velocities.add(element)

            java_quaternions = ArrayList()
            for element in quaternions:
                java_quaternions.add(element)

            # Set up the cache for position-velocities
            pv_cache = ImmutableTimeStampedCache(pv_interpolation_number, java_positions_velocities)

            # Set up the cache for attitudes
            a_cache = ImmutableTimeStampedCache(a_interpolation_number, java_quaternions)

            n_val = int(np.ceil(self._max_date.durationFrom(self._min_date) / t_step))

            self._t_step = t_step
            self._body_to_inertial = []
            self._inertial_to_body = []
            self._sc_to_inertial = []

            # Set 'date' value
            date = self._min_date
            while len(self._body_to_inertial) < n_val:
                # Interpolate position-velocity, allowing slight extrapolation near the boundaries
                if date.compareTo(pv_cache.getEarliest().getDate()) < 0:
                    pv_interpolation_date = pv_cache.getEarliest().getDate()
                elif date.compareTo(pv_cache.getLatest().getDate()) > 0:
                    pv_interpolation_date = pv_cache.getLatest().getDate()
                else:
                    pv_interpolation_date = date

                time_interpolator = TimeStampedPVCoordinatesHermiteInterpolator(
                    min(
                        pv_cache.getNeighbors(pv_interpolation_date, pv_interpolation_number).count(),
                        15,  # 15 => Maximum recommended by doc
                    ),
                    pv_filter,
                )
                interpolated_pv = time_interpolator.interpolate(
                    pv_interpolation_date, pv_cache.getNeighbors(pv_interpolation_date, pv_interpolation_number)
                )

                pv_val = interpolated_pv.shiftedBy(date.durationFrom(pv_interpolation_date))

                # Interpolate attitude, allowing slight extrapolation near the boundaries
                if date.compareTo(a_cache.getEarliest().getDate()) < 0:
                    a_interpolation_date = a_cache.getEarliest().getDate()
                elif date.compareTo(a_cache.getLatest().getDate()) > 0:
                    a_interpolation_date = a_cache.getLatest().getDate()
                else:
                    a_interpolation_date = date

                time_interpolator_angular = TimeStampedAngularCoordinatesHermiteInterpolator(
                    min(
                        a_cache.getNeighbors(a_interpolation_date, a_interpolation_number).count(),
                        15,  # 15 => Maximum recommended by doc
                    ),
                    a_filter,
                )
                interpolated_quaternion = time_interpolator_angular.interpolate(
                    a_interpolation_date,
                    a_cache.getNeighbors(a_interpolation_date, a_interpolation_number).collect(Collectors.toList()),
                )

                quaternion = interpolated_quaternion.shiftedBy(date.durationFrom(a_interpolation_date))

                # Store transform from spacecraft fram to inertial frame
                self._sc_to_inertial.append(
                    Transform(date, Transform(date, quaternion.revert()), Transform(date, pv_val))
                )

                # Store transform from body frame to inertial frame
                b2i_element = self._body_frame.getTransformTo(self._inertial_frame, date)
                self._body_to_inertial.append(b2i_element)
                self._inertial_to_body.append(b2i_element.getInverse())

                # Update 'date' value
                date = date.shiftedBy(self._t_step)
        else:
            print("WARNING : Wrong arguments sequence for SpacecraftToObservedBody")

    @property
    def inertial_frame(self) -> Frame:
        """Get the inertial frame."""

        return self._inertial_frame

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
        """Get the step to use for inertial frame to body frame transforms cache computations."""

        return self._t_step

    @property
    def overshoot_tolerance(self) -> float:
        """Get the tolerance in seconds allowed for {@link #getMinDate()} and {@link #getMaxDate()} overshooting."""

        return self._overshoot_tolerance

    def get_sc_to_inertial(self, date: AbsoluteDate) -> Transform:
        """Get transform from spacecraft to inertial frame.

        Parameters
        ----------
            date : date of the transform

        Returns
        -------
            result : transform from spacecraft to inertial frame
        """

        return self.interpolate(date, self._sc_to_inertial)

    def get_inertial_to_body(self, date: AbsoluteDate) -> Transform:
        """Get transform from inertial frame to observed body frame.

        Parameters
        ----------
            date : date of the transform

        Returns
        -------
            result : transform from observed body frame to inertial frame
        """

        return self.interpolate(date, self._inertial_to_body)

    def get_body_to_inertial(self, date: Union[AbsoluteDate, np.array]) -> Union[Transform, np.array]:
        """Get transform from observed body frame to inertial frame.

        Parameters
        ----------
            date : date of the transform

        Returns
        -------
            result : transform from observed body frame to inertial frame
        """

        return self.interpolate(date, self._body_to_inertial)

    def interpolate(
        self, date: Union[AbsoluteDate, np.array], transforms_list: List[Transform]
    ) -> Union[Transform, np.array]:
        """Interpolate transform.

        Parameters
        ----------
            date : date of the transform
            transforms_list: transforms list to interpolate from

        Returns
        -------
            result : interpolated transform
        """

        if len(np.shape(date)) > 0:
            # If date is an array then we use interpolate_for_several_dates
            return self.interpolate_for_several_dates(date, transforms_list)

        # If date is float then we use interpolate_for_one_date
        return self.interpolate_for_one_date(date, transforms_list)

    def interpolate_for_one_date(self, date: AbsoluteDate, transforms_list: List[Transform]) -> Transform:
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

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_transform(
                self, index, self._body_to_inertial[index], self._sc_to_inertial[index]
            )

        close = transforms_list[index]
        return close.shiftedBy(date.durationFrom(close.getDate()))

    def interpolate_for_several_dates(self, dates: np.ndarray, transforms_list: List[Transform]) -> np.array:
        """Interpolate transform.

        Parameters
        ----------
            dates : date of the transform
            transforms_list: transforms list to interpolate from

        Returns
        -------
            result : interpolated transform
        """
        # Check date range
        for date in dates:
            if not self.is_in_range(date):
                raise PyRuggedError(PyRuggedMessages.OUT_OF_TIME_RANGE.value, date, self.min_date, self.max_date)

        dates_array_handling = AbsoluteDateArrayHandling(dates)
        durations_from = dates_array_handling.durationFrom([transforms_list[0].getDate()] * len(dates))
        # s_val = np.array([elem / self.t_step for elem in durations_from])
        # indexes = np.array(
        #     [int(max(0.0, min(float(len(transforms_list) - 1), float(np.rint(s_val_elem))))) for s_val_elem in s_val]
        # )
        s_val = np.array(durations_from) / self.t_step
        indexes = np.fmax(0.0, np.fmin(len(transforms_list) - 1, np.rint(s_val))).astype(int)

        transforms_list_shifted = []
        date_index = 0
        durations_from = dates_array_handling.durationFrom([transforms_list[index].getDate() for index in indexes])
        for index in indexes:
            if dump_manager.DUMP_VAR is not None:
                dump_manager.DUMP_VAR.dump_transform(
                    self, index, self._body_to_inertial[index], self._sc_to_inertial[index]
                )

            # close = transforms_list[index]
            # transforms_list_shifted.append(close.shiftedBy(dates[date_index].durationFrom(close.getDate())))
            close = transforms_list[index]
            transforms_list_shifted.append(close.shiftedBy(durations_from[date_index]))
            date_index += 1

        return np.array(transforms_list_shifted)

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
