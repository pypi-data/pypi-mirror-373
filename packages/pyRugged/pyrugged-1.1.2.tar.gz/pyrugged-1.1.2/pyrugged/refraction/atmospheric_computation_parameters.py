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

"""pyrugged Class AtmosphericComputationParameters"""
from typing import List

from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.utils.grid_creation import GridCreation


class AtmosphericComputationParameters:
    """Atmospheric refraction computation parameters.
    Defines for inverse location a set of parameters in order to be able to perform the computation.
    """

    MARGIN_LINE = 10
    DEFAULT_STEP_PIXEL = 100
    DEFAULT_STEP_LINE = 100
    DEFAULT_INVLOC_MARGIN = 0.8

    def __init__(self):
        """Builds a new instance."""

        self._pixel_step = self.DEFAULT_STEP_PIXEL
        self._line_step = self.DEFAULT_STEP_LINE
        self._invloc_margin = self.DEFAULT_INVLOC_MARGIN

        self._min_line_sensor = None
        self._max_line_sensor = None
        self._sensor_name = None
        self._nb_pixel_grid = None
        self._nb_line_grid = None
        self._u_grid = None
        self._v_grid = None

    @property
    def invloc_margin(self) -> float:
        """Get inverse location margin parameter."""

        return self._invloc_margin

    @invloc_margin.setter
    def invloc_margin(self, new_invloc_margin: float):
        """Set inverse location margin parameter."""

        self._invloc_margin = new_invloc_margin

    @property
    def nb_pixel_grid(self) -> int:
        """Get size of pixel grid."""

        return self._nb_pixel_grid

    @property
    def nb_line_grid(self) -> int:
        """Get size of line grid."""

        return self._nb_line_grid

    @property
    def u_grid(self) -> List[float]:
        """Get pixel grid."""

        return self._u_grid

    @property
    def v_grid(self) -> List[float]:
        """Get line grid."""

        return self._v_grid

    @property
    def min_line_sensor(self) -> float:
        """Get the min line used to compute the current grids."""

        return self._min_line_sensor

    @property
    def max_line_sensor(self) -> float:
        """Get the max line used to compute the current grids."""

        return self._max_line_sensor

    @property
    def sensor_name(self) -> str:
        """Get the sensor name used to compute the current grids."""

        return self._sensor_name

    def configure_correction_grid(self, sensor: LineSensor, min_line: int, max_line: int):
        """Configuration of the interpolation grid. This grid is associated to the given sensor,
        with the given min and max lines.

        Parameters
        ----------
            sensor : line sensor
            min_line : min line defined for the inverse location
            max_line : max line defined for the inverse location
        """

        # Keep information about the sensor and the required search lines.
        # Needed to test if the grid is initialized with this context.
        self._min_line_sensor = min_line
        self._max_line_sensor = max_line
        self._sensor_name = sensor.name

        # Compute the number of pixels and lines for the grid (round value is sufficient)
        sensor_nb_pxs = sensor.nb_pixels
        self._nb_pixel_grid = int(sensor_nb_pxs / self._pixel_step)

        # Check the validity of the min and max lines
        if (max_line - min_line + 1 - 2 * self.MARGIN_LINE) < 2 * self._line_step:
            info = f'{": (max_line - min_line + 1 - 2*"}{self.MARGIN_LINE}{") < 2*"}{self._line_step}'
            raise PyRuggedError(PyRuggedMessages.INVALID_RANGE_FOR_LINES.value, min_line, max_line, info)

        self._nb_line_grid = int((max_line - min_line + 1 - 2 * self.MARGIN_LINE) / self._line_step)

        # Compute the linear grids in pixel (u index) and line (v index)
        self._u_grid = GridCreation().create_linear_grid(0, sensor_nb_pxs - 1, self._nb_pixel_grid)
        self._v_grid = GridCreation().create_linear_grid(
            min_line + self.MARGIN_LINE, max_line - self.MARGIN_LINE, self._nb_line_grid
        )

    def set_grid_steps(self, grid_pixel_step: int, grid_line_step: int):
        """Set the grid steps in pixel and line (used to compute inverse location).
        Overwrite the default values, for time optimization if necessary.

        Parameters
        ----------
            grid_pixel_step : grid pixel step for the inverse location computation
            grid_line_step : grid line step for the inverse location computation
        """

        if grid_pixel_step <= 0:
            reason = f'{" pixel_step <= 0"}'
            raise PyRuggedError(PyRuggedMessages.INVALID_STEP.value, grid_pixel_step, reason)

        if grid_line_step <= 0:
            reason = f'{" line_step <= 0"}'
            raise PyRuggedError(PyRuggedMessages.INVALID_STEP.value, grid_line_step, reason)

        self._pixel_step = grid_pixel_step
        self._line_step = grid_line_step
