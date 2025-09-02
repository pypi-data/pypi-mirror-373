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

"""pyrugged Class GridCreation"""


# pylint: disable=too-few-public-methods
from typing import List


class GridCreation:
    """Utility class for grids creation."""

    def __init__(self):
        """Builds a new instance."""

    def create_linear_grid(self, min_val: float, max_val: float, n_val: int) -> List[List[float]]:
        """Create a linear grid between min and max value for a number n of points.
        TBN: no checks are performed here. Must be done by the calling method.

        Parameters
        ----------
            min_val : min value for grid[0]
            max_val : max value for grid[n-1]
            n_val : number of points

        Returns
        -------
            grid : linear grid
        """

        grid = []
        for index in range(n_val):
            grid.append(((n_val - 1 - index) * min_val + index * max_val) / (n_val - 1))

        return grid
