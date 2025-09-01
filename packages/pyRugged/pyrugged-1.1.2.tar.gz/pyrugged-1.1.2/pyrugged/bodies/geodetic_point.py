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

"""pyrugged Class GeodeticPoint"""


# pylint: disable=import-error
import math

import numpy as np

from pyrugged.utils.math_utils import normalize_angle, to_array  # pylint: disable=no-name-in-module


class GeodeticPoint:
    """GeodeticPoint object"""

    def __init__(self, latitude: float, longitude: float, altitude: float):
        """Constructor."""

        pi = math.pi  # pylint: disable=invalid-name
        pi_2 = pi / 2.0
        lat = normalize_angle(latitude, pi_2)
        lon = normalize_angle(longitude, 0.0)

        if lat > pi_2:
            # Latitude is beyond the pole -> add 180 to longitude

            lat = pi - lat
            lon = normalize_angle(longitude + pi, 0.0)

        self._latitude = lat
        self._longitude = lon
        self._altitude = altitude
        self._zenith = None
        self._nadir = None
        self._north = None
        self._south = None
        self._east = None
        self._west = None

    @property
    def latitude(self) -> float:
        """Get latitude parameter an angular value in the range [-π/2, π/2]."""

        return self._latitude

    @property
    def longitude(self) -> float:
        """Get longitude parameter an angular value in the range [-π, π]."""

        return self._longitude

    @property
    def altitude(self) -> float:
        """Get altitude of the point (m)."""

        return self._altitude

    @property
    def zenith(self) -> np.ndarray:
        """Get the direction above the point, expressed in parent shape frame.
        The zenith direction is defined as the normal to local horizontal plane.

        Returns
        -------
            zenith : unit vector in the zenith direction
        """

        if self._zenith is None:
            self._zenith = to_array(
                math.cos(self._longitude) * math.cos(self._latitude),
                math.sin(self._longitude) * math.cos(self._latitude),
                math.sin(self._latitude),
            )

        return self._zenith

    @property
    def nadir(self) -> np.ndarray:
        """Get the direction below the point, expressed in parent shape frame.
        The nadir direction is the opposite of zenith direction.

        Returns
        -------
            nadir : unit vector in the nadir direction
        """

        if self._nadir is None:
            self._nadir = -self.zenith  # pylint: disable=invalid-unary-operand-type

        return self._nadir

    @property
    def north(self) -> np.ndarray:
        """Get the direction to the north of point, expressed in parent shape frame.
        The north direction is defined in the horizontal plane
        (normal to zenith direction) and following the local meridian.

        Returns
        -------
            north : unit vector in the north direction
        """

        if self._north is None:
            self._north = to_array(
                -math.cos(self._longitude) * math.sin(self._latitude),
                -math.sin(self._longitude) * math.sin(self._latitude),
                math.cos(self._latitude),
            )

        return self._north

    @property
    def south(self) -> np.ndarray:
        """Get the direction to the south of point, expressed in parent shape frame.
        The south direction is the opposite of north direction.

        Returns
        -------
            south : unit vector in the south direction
        """

        if self._south is None:
            self._south = -self.north  # pylint: disable=invalid-unary-operand-type

        return self._south

    @property
    def east(self) -> np.ndarray:
        """Get the direction to the east of point, expressed in parent shape frame.
        The east direction is defined in the horizontal plane
        in order to complete direct triangle (east, north, zenith).

        Returns
        -------
            east : unit vector in the east direction
        """

        if self._east is None:
            self._east = to_array(-math.sin(self._longitude), math.cos(self._longitude), 0.0)

        return self._east

    @property
    def west(self) -> np.ndarray:
        """Get the direction to the west of point, expressed in parent shape frame.
        The west direction is the opposite of east direction.

        Returns
        -------
            west : unit vector in the west direction
        """

        if self._west is None:
            self._west = -self.east  # pylint: disable=invalid-unary-operand-type

        return self._west

    def __eq__(self, point: "GeodeticPoint") -> bool:
        """GeodeticPoint objects equality.

        Parameters
        ----------
            point : point to compare with
        Returns
        -------
            result : true if current GeodeticPoint object equals 'point' parameter
        """

        return self.latitude == point.latitude and self.longitude == point.longitude and self.altitude == point.altitude

    def to_string(self):
        """Get string format for GeodeticPoint object."""

        return (
            f'{"{lat: "}{float(np.degrees(self._latitude))}'
            f'{" deg, lon: "}{float(np.degrees(self._longitude))}'
            f'{" deg, alt: "}{self._altitude}{" m}"}'
        )
