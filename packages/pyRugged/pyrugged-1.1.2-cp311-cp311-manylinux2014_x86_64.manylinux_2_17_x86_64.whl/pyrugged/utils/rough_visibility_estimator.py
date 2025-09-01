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

"""pyrugged Class RoughVisibilityEstimator"""

# pylint: disable="import-error"
import math
import sys
from typing import List

import numpy as np
from org.orekit.frames import Frame
from org.orekit.time import AbsoluteDate
from org.orekit.utils import TimeStampedPVCoordinates

from pyrugged.bodies.one_axis_ellipsoid import OneAxisEllipsoid
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    angle,
    cross,
    distance,
    dot,
    get_norm,
    to_array_v,
)


class RoughVisibilityEstimator:
    """Class estimating very roughly when a point may be visible from spacecraft.

    The class only uses spacecraft position to compute a very rough sub-satellite
    point. It assumes the position-velocities are regular enough and without holes.
    It is intended only as a quick estimation in order to set up search
    boundaries in inverse location.

    """

    def __init__(self, ellipsoid: OneAxisEllipsoid, frame: Frame, positions_velocities: List[TimeStampedPVCoordinates]):
        """Builds a new instance.

        Parameters
        ----------
            ellipsoid : ground ellipsoid
            frame : frame in which position and velocity are defined (may be inertial or body frame)
            positions_velocities : satellite position and velocity (m and m/s in specified frame)
        """

        self._ellipsoid = ellipsoid

        # Project spacecraft position-velocity to ground
        body_frame = self._ellipsoid.body_frame
        n_val = len(positions_velocities)
        self._pv_ground = []
        for pv_val in positions_velocities:
            transform = frame.getTransformTo(body_frame, pv_val.getDate())
            self._pv_ground.append(
                ellipsoid.project_to_ground_from_pv(transform.transformPVCoordinates(pv_val), body_frame)
            )

        # Initialize first search at mid point
        self._last = int(n_val / 2)
        # Estimate mean angular rate with respect to indices
        alpha = 0
        for index in range(n_val - 1):
            # Angular motion between points index and index+1
            alpha += angle(
                to_array_v(self._pv_ground[index].getPosition().toArray()),
                to_array_v(self._pv_ground[index + 1].getPosition().toArray()),
            )

        self._rate_vs_indices = alpha / n_val

        # Estimate mean angular rate with respect to time
        first_date = self._pv_ground[0].getDate()
        last_date = self._pv_ground[-1].getDate()
        self._rate_vs_time = alpha / last_date.durationFrom(first_date)

    def estimate_visibility(self, ground_point: np.ndarray) -> AbsoluteDate:
        """Estimate very roughly when spacecraft comes close to a ground point.

        Parameters
        ----------
            ground_point : ground point to check

        Returns
        -------
            result : rough date at which spacecraft comes close to ground point (never null,
                but may be really far from reality if ground point is away from trajectory)
        """

        point = self._ellipsoid.transform(ground_point)
        close_index = self.find_close(self._last, point)

        # Check if there are closer points in previous periods
        repeat = float(np.rint(2.0 * math.pi / self._rate_vs_indices))
        index = int(close_index - repeat)
        while index > 0:
            other_index = self.find_close(index, point)
            if other_index != close_index and distance(
                to_array_v(self._pv_ground[other_index].getPosition().toArray()), point
            ) < distance(to_array_v(self._pv_ground[close_index].getPosition().toArray()), point):
                close_index = other_index

            index -= repeat

        # Check if there are closer points in next periods
        index = int(close_index + repeat)
        while index < len(self._pv_ground):
            other_index = self.find_close(index, point)
            if other_index != close_index and distance(
                to_array_v(self._pv_ground[other_index].getPosition().toArray()), point
            ) < distance(to_array_v(self._pv_ground[close_index].getPosition().toArray()), point):
                close_index = other_index

            index += repeat

        # We have found the closest sub-satellite point index
        self._last = close_index

        # Final adjustment
        closest = self._pv_ground[close_index]
        alpha = self.needed_motion(closest, point)

        return closest.getDate().shiftedBy(alpha / self._rate_vs_time)

    def find_close(self, start: int, point: np.ndarray) -> int:
        """Find the index of a close sub-satellite point.

        Parameters
        ----------
            start : start index for the search
            point : test point

        Returns
        -------
            current : index of a sub-satellite point close to the test point
        """

        current = start
        previous = -sys.maxsize + 100000
        max_loop = 1000
        while max_loop > 0 and math.fabs(current - previous) > 1:
            previous = current
            alpha = self.needed_motion(self._pv_ground[current], point)
            shift = float(np.rint(alpha / self._rate_vs_indices))
            current = int(max(0.0, min(len(self._pv_ground), current + shift)))

            max_loop -= 1

        return current

    def needed_motion(self, sub_satellite: TimeStampedPVCoordinates, point: np.ndarray) -> float:
        """Estimate angular motion needed to go past test point.
        This estimation is quite crude. The sub-satellite point is properly on the
        ellipsoid surface, but we compute the angle assuming a spherical shape.

        Parameters
        ----------
            sub_satellite : current sub-satellite position-velocity
            point : test point

        Returns
        -------
            result : angular motion to go past test point (positive if
                test point is ahead, negative if it is behind)

        """

        ss_p = to_array_v(sub_satellite.getPosition().toArray())
        norm = get_norm(ss_p)
        momentum = to_array_v(sub_satellite.getMomentum().toArray())
        cross_p = cross(momentum, ss_p)
        norm_cross = get_norm(cross_p)
        y_val = dot(point, cross_p / norm_cross)
        x_val = dot(point, ss_p / norm)

        return math.atan2(y_val, x_val)
