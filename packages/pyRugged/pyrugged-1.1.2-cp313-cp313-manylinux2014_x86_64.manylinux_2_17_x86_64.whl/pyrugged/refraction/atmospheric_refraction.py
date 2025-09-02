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

"""pyrugged Class AtmosphericRefraction"""

import abc
from typing import List, Union

# pylint: disable=duplicate-code, too-few-public-methods
import numpy as np
from scipy import interpolate

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.basic_scan_algorithm import BasicScanAlgorithm
from pyrugged.intersection.constant_elevation_algorithm import ConstantElevationAlgorithm
from pyrugged.intersection.ignore_dem_algorithm import IgnoreDEMAlgorithm
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.refraction.atmospheric_computation_parameters import AtmosphericComputationParameters

init_orekit(use_internal_data=False)


class BilinearInterpolator:
    """Performs bilinear interpolation on regular grids."""

    def __init__(
        self,
        col_positions: np.ndarray,
        row_positions: np.ndarray,
        values: np.ndarray,
        bound_errors: bool = False,
        fill_value: float = None,
    ):
        """Constructor."""

        self._col_positions = col_positions
        self._row_positions = row_positions
        self._values = values
        self._bound_errors = bound_errors
        self._fill_value = fill_value

    def value(self, positions: np.ndarray):
        """Bilinear interpolation of 'positions'."""

        interp = interpolate.interpn(
            (self._col_positions, self._row_positions),
            self._values,
            positions,
            method="linear",
            bounds_error=False,
            fill_value=None,
        )

        return interp[0]


class AtmosphericRefraction:
    """Base class for atmospheric refraction model."""

    def __init__(self):
        """Builds a new instance."""

        # Set up the atmospheric parameters ... with lazy evaluation of the grid (done only if necessary)
        self._atmospheric_params = AtmosphericComputationParameters()
        self._must_be_computed = True
        self._bif_pixel = None
        self._bif_line = None

    @property
    def atmospheric_params(self):
        """Get atmospheric params parameter."""

        return self._atmospheric_params

    @property
    def must_be_computed(self):
        """Get must_be_computed parameter."""

        return self._must_be_computed

    @property
    def bif_pixel(self) -> BilinearInterpolator:
        """Get bilinear interpolating function for pixel correction."""

        return self._bif_pixel

    @property
    def bif_line(self) -> BilinearInterpolator:
        """Get bilinear interpolating function for line correction."""

        return self._bif_line

    @abc.abstractmethod
    def apply_correction(
        self,
        sat_pos: np.ndarray,
        sat_los: np.ndarray,
        raw_intersection: np.ndarray,
        algorithm: Union[
            BasicScanAlgorithm,
            ConstantElevationAlgorithm,
            IgnoreDEMAlgorithm,
            # TODO DuvenhageAlgorithm
        ],
    ) -> np.ndarray:
        """Apply correction to the intersected point with an atmospheric refraction model.

        Parameters
        ----------
            sat_pos : satellite position, in body frame
            sat_los : satellite line of sight, in body frame
            raw_intersection : intersection point before refraction correction
            algorithm : intersection algorithm

        Returns
        -------
            result : corrected point with the effect of atmospheric refraction
        """

    def deactivate_computation(self):
        """Deactivate computation (needed for the inverse location computation)."""

        self._must_be_computed = False

    def reactivate_computation(self):
        """Reactivate computation (needed for the inverse location computation)."""

        self._must_be_computed = True

    def configure_correction_grid(self, sensor: LineSensor, min_line: int, max_line: int):
        """Configuration of the interpolation grid. This grid is associated to the given sensor,
        with the given min and max lines.

        Parameters
        ----------
            sensor : line sensor
            min_line : min line defined for the inverse location
            max_line : max line defined for the inverse location
        """

        self._atmospheric_params.configure_correction_grid(sensor, min_line, max_line)

    def is_same_context(self, sensor_name: str, min_line: int, max_line: int) -> bool:
        """Check if the current atmospheric parameters are the same as the asked ones.

        Parameters
        ----------
            sensor_name : the asked sensor name
            min_line : the asked min line
            max_line : the asked max line

        Returns
        -------
            result : true if same context; False otherwise
        """

        return (
            self._atmospheric_params.min_line_sensor == min_line
            and self._atmospheric_params.max_line_sensor == max_line
            and self._atmospheric_params.sensor_name == sensor_name
        )

    def get_computation_parameters(self) -> AtmosphericComputationParameters:
        """Get the computation parameters."""

        return self._atmospheric_params

    def set_grid_steps(self, pixel_step: int, line_step: int):
        """Set the grid steps in pixel and line (used to compute inverse location).
        Overwrite the default values, for time optimization for instance.

        Parameters
        ----------
            pixel_step : pixel step for the inverse location computation
            line_step : line step for the inverse location computation
        """

        self._atmospheric_params.set_grid_steps(pixel_step, line_step)

    def compute_grid_correction_functions(self, sensor_pixel_grid_inverse_without: List[List[float]]):
        """Compute the correction functions for pixel and lines.
        The corrections are computed for pixels and lines, on a regular grid at sensor level.
        The corrections are based on the difference on grid nodes (where direct loc is known with atmosphere refraction)
        and the sensor pixel found by inverse loc without atmosphere refraction.
        The bilinear interpolating functions are then computed for pixel and for line.
        Need to be computed only once for a given sensor with the same minLine and maxLine.

        Parameters
        ----------
            sensor_pixel_grid_inverse_without : inverse location grid WITHOUT atmospheric refraction
        """

        nb_pixel_grid = self._atmospheric_params.nb_pixel_grid
        nb_line_grid = self._atmospheric_params.nb_line_grid
        pixel_grid = self._atmospheric_params.u_grid
        line_grid = self._atmospheric_params.v_grid

        # Initialize the needed diff functions
        grid_diff_pixel = [[0 for i in range(nb_line_grid)] for j in range(nb_pixel_grid)]
        grid_diff_line = [[0 for i in range(nb_line_grid)] for j in range(nb_pixel_grid)]

        # Compute the difference between grids nodes WITH - without atmosphere
        for line_index in range(nb_line_grid):
            for pixel_index in range(nb_pixel_grid):
                if sensor_pixel_grid_inverse_without[pixel_index][line_index] is not None:
                    diff_line = line_grid[line_index] - sensor_pixel_grid_inverse_without[pixel_index][line_index][0]
                    diff_pixel = pixel_grid[pixel_index] - sensor_pixel_grid_inverse_without[pixel_index][line_index][1]
                    grid_diff_pixel[pixel_index][line_index] = diff_pixel
                    grid_diff_line[pixel_index][line_index] = diff_line

                else:
                    # Impossible to find the point in the given min line and max line
                    raise PyRuggedError(
                        PyRuggedMessages.INVALID_RANGE_FOR_LINES.value,
                        self._atmospheric_params.min_line_sensor,
                        self._atmospheric_params.max_line_sensor,
                        "",
                    )

        # TODO dumping matrices
        # with open("log_matrix.txt", "a", encoding="utf-8") as log_matrix:
        #     log_matrix.write(f'{"GRID DIFF PIXEL = "}{grid_diff_pixel}\n')
        #     log_matrix.write("===" * 25)
        #     log_matrix.write("\n")
        #     log_matrix.write(f'{"GRID DIFF LINE = "}{grid_diff_line}')

        # Definition of the interpolating function for pixel and for line
        self._bif_pixel = BilinearInterpolator(np.array(pixel_grid), np.array(line_grid), np.array(grid_diff_pixel))
        self._bif_line = BilinearInterpolator(np.array(pixel_grid), np.array(line_grid), np.array(grid_diff_line))
