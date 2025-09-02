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

"""pyrugged geodesy functions for geodetic_point as numpy array [lat, lon, alt]"""


# pylint: disable=import-error
from typing import Union

import numpy as np

from pyrugged.utils.math_utils import normalize_geodetic_point_optim  # pylint: disable=no-name-in-module


def zenith(geodetic_point: np.ndarray) -> np.ndarray:
    """Get the direction above the point, expressed in parent shape frame.
    The zenith direction is defined as the normal to local horizontal plane.

    Returns
    -------
        zenith : unit vector in the zenith direction
    """

    if geodetic_point.ndim == 1:
        return np.array(
            [
                np.cos(geodetic_point[1]) * np.cos(geodetic_point[0]),
                np.sin(geodetic_point[1]) * np.cos(geodetic_point[0]),
                np.sin(geodetic_point[0]),
            ]
        )

    return np.array(
        [
            np.cos(geodetic_point[:, 1]) * np.cos(geodetic_point[:, 0]),
            np.sin(geodetic_point[:, 1]) * np.cos(geodetic_point[:, 0]),
            np.sin(geodetic_point[:, 0]),
        ]
    ).T


def nadir(geodetic_point: np.ndarray) -> np.ndarray:
    """Get the direction below the point, expressed in parent shape frame.
    The nadir direction is the opposite of zenith direction.

    Returns
    -------
        nadir : unit vector in the nadir direction
    """

    return -zenith(geodetic_point)


def north(geodetic_point: np.ndarray) -> np.ndarray:
    """Get the direction to the north of point, expressed in parent shape frame.
    The north direction is defined in the horizontal plane
    (normal to zenith direction) and following the local meridian.

    Returns
    -------
        north : unit vector in the north direction
    """

    if geodetic_point.ndim == 1:
        return np.array(
            [
                -np.cos(geodetic_point[1]) * np.sin(geodetic_point[0]),
                -np.sin(geodetic_point[1]) * np.sin(geodetic_point[0]),
                np.cos(geodetic_point[0]),
            ]
        )

    return np.array(
        [
            -np.cos(geodetic_point[:, 1]) * np.sin(geodetic_point[:, 0]),
            -np.sin(geodetic_point[:, 1]) * np.sin(geodetic_point[:, 0]),
            np.cos(geodetic_point[:, 0]),
        ]
    ).T


def south(geodetic_point: np.ndarray) -> np.ndarray:
    """Get the direction to the south of point, expressed in parent shape frame.
    The south direction is the opposite of north direction.

    Returns
    -------
        south : unit vector in the south direction
    """

    return -north(geodetic_point)


def east(geodetic_point: np.ndarray) -> np.ndarray:
    """Get the direction to the east of point, expressed in parent shape frame.
    The east direction is defined in the horizontal plane
    in order to complete direct triangle (east, north, zenith).

    Returns
    -------
        east : unit vector in the east direction
    """

    if geodetic_point.ndim == 1:
        return np.array([-np.sin(geodetic_point[1]), np.cos(geodetic_point[1]), 0])

    return np.array([-np.sin(geodetic_point[:, 1]), np.cos(geodetic_point[:, 1]), np.zeros(geodetic_point.shape[0])]).T


def west(geodetic_point: np.ndarray) -> np.ndarray:
    """Get the direction to the west of point, expressed in parent shape frame.
    The west direction is the opposite of east direction.

    Returns
    -------
        west : unit vector in the west direction
    """

    return -east(geodetic_point)


def normalize_geodetic_point(
    geodetic_point: np.ndarray, central_longitude: Union[np.ndarray, float] = None
) -> np.ndarray:
    """Normalize geodetic point longitude and latitude.

    Returns
    -------
        geodetic_point : point with normalized longitude and latitude
    """

    return normalize_geodetic_point_optim(geodetic_point, central_longitude)
