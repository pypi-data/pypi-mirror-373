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

"""pyrugged Class Rotation"""
# pylint: disable=too-few-public-methods, invalid-name
import math
from enum import Enum, auto
from typing import List

import numpy as np

from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.utils.math_utils import rotate  # pylint: disable=no-name-in-module


class RotationConvention(Enum):
    VECTOR_OPERATOR = auto()
    FRAME_TRANSFORM = auto()


class Rotation:
    """LOS rotation transform application."""

    def __init__(self, axis: np.ndarray, angle: List[float], convention: RotationConvention):
        norm = np.linalg.norm(axis)
        if norm == 0:
            raise PyRuggedError("Zero norm for rotation axis")

        if isinstance(angle, float):
            if convention == RotationConvention.VECTOR_OPERATOR:
                half_angle = -0.5 * angle
            else:
                half_angle = 0.5 * angle

            coeff = math.sin(half_angle) / norm

            self.q = np.array([math.cos(half_angle)] + (coeff * axis).tolist())

        elif len(angle) == 1:
            angle = float(angle)
            if convention == RotationConvention.VECTOR_OPERATOR:
                half_angle = -0.5 * angle
            else:
                half_angle = 0.5 * angle

            coeff = math.sin(half_angle) / norm

            self.q = np.array([math.cos(half_angle)] + (coeff * axis).tolist())

        else:
            angle = np.array(angle)
            if convention == RotationConvention.VECTOR_OPERATOR:
                half_angle = -0.5 * angle
            else:
                half_angle = 0.5 * angle

            coeff = np.sin(half_angle) / norm

            self.q = np.array([np.cos(half_angle)] + [coeff * axis[i] for i in range(len(axis))])

    def applyTo(self, los: np.ndarray):
        return rotate(self.q, los)
