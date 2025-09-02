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
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""pyrugged Class NormalizedGeodeticPoint"""


# pylint: disable=unused-import, import-error, missing-module-docstring, wrong-import-position
from pyrugged.bodies.geodetic_point import GeodeticPoint
from pyrugged.utils.math_utils import normalize_angle  # pylint: disable=no-name-in-module


class NormalizedGeodeticPoint(GeodeticPoint):
    """Geodetic point whose longitude can be selected with respect to the 2π boundary."""

    def __init__(self, latitude: float, longitude: float, altitude: float, central_longitude: float):
        """Builds a new instance. The angular coordinates will be normalized
        to ensure that the latitude is between ±π/2 and the longitude
        is between lc-π and lc+π.

        Parameters
        ----------
            latitude : latitude of the point
            longitude : longitude of the point
            altitude : altitude of the point
            central_longitude : central longitude lc
        """

        super().__init__(latitude, longitude, altitude)
        self._normalized_longitude = normalize_angle(longitude, central_longitude)

    @property
    def longitude(self) -> float:
        """Get the longitude.

        Returns
        -------
            normalized_longitude : an angular value in the range [lc-π, lc+π],
                where lc was selected at construction

        """

        return self._normalized_longitude
