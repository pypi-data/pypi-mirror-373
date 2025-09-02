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

"""pyrugged Class SensorMeanPlaneCrossing"""

# pylint: disable=too-many-instance-attributes, too-many-arguments
# pylint: disable=chained-comparison, too-many-branches, too-many-nested-blocks
import math
from typing import List

import numpy as np
from org.hipparchus.geometry import Vector
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.frames import StaticTransform, Transform
from org.orekit.time import AbsoluteDate
from org.orekit.utils import PVCoordinates
from scipy.optimize import brentq

from pyrugged.errors.pyrugged_exception import PyRuggedError, PyRuggedInternalError
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.utils.constants import Constants
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    compute_svd,
    cross,
    dot,
    get_norm,
    matrix_solve,
    to_array,
    to_array_v,
)
from pyrugged.utils.spacecraft_to_observed_body import SpacecraftToObservedBody


class CrossingResult:
    """Container for mean plane crossing result."""

    def __init__(
        self,
        crossing_date: AbsoluteDate,
        crossing_line: float,
        target: np.ndarray,
        target_direction: np.ndarray,
        target_direction_derivative: np.ndarray,
    ):
        """Builds a new instance.

        Parameters
        ----------
            crossing_date : crossing date
            crossing_line : crossing Line
            target : target ground point
            target_direction : target direction in spacecraft frame
            target_direction_derivative : derivative of the target direction
                in spacecraft frame with respect to line number
        """

        self._crossing_date = crossing_date
        self._crossing_line = crossing_line
        self._target = target
        if isinstance(target, Vector3D):
            self._target = to_array_v(target.toArray())
        self._target_direction = to_array(target_direction[0], target_direction[1], target_direction[2])
        self._target_direction_derivative = to_array(
            target_direction_derivative[0], target_direction_derivative[1], target_direction_derivative[2]
        )

    @property
    def date(self) -> AbsoluteDate:
        """Get the crossing date."""

        return self._crossing_date

    @property
    def line(self) -> float:
        """Get the crossing line."""

        return self._crossing_line

    @property
    def target(self) -> np.ndarray:
        """Get the target ground point."""

        return self._target

    @property
    def target_direction(self) -> np.ndarray:
        """Get the normalized target direction in spacecraft frame at crossing."""

        return self._target_direction

    @property
    def target_direction_derivative(self) -> np.ndarray:
        """Get the derivative of the normalized target direction in spacecraft frame at crossing."""

        return self._target_direction_derivative


class SensorMeanPlaneCrossing:
    """Class dedicated to find when ground point crosses mean sensor plane.
    This class is used in the first stage of inverse location.
    """

    NB_CACHED_RESULTS = 6

    def __init__(
        self,
        sensor: LineSensor,
        sc_to_body: SpacecraftToObservedBody,
        min_line: int,
        max_line: int,
        light_time_correction: bool,
        aberration_of_light_correction: bool,
        max_eval: int,
        accuracy: float,
        mean_plane_normal: np.ndarray = None,
        cached_results: List[CrossingResult] = None,
    ):
        """Builds a new instance.

        Parameters
        ----------
            sensor : sensor to consider
            sc_to_body : converter between spacecraft and body
            min_line : minimum line number
            max_line : maximum line number
            light_time_correction : flag for light time correction
            aberration_of_light_correction : flag for aberration of light correction
            max_eval : maximum number of evaluations
            accuracy : accuracy to use for finding crossing line number
            mean_plane_normal :  mean plane normal
            cached_results : cached results
        """

        self._sensor = sensor
        self._sc_to_body = sc_to_body
        self._min_line = min_line
        self._max_line = max_line
        self._light_time_correction = light_time_correction
        self._aberration_of_light_correction = aberration_of_light_correction
        self._max_eval = max_eval
        self._accuracy = accuracy

        self._mid_line = 0.5 * (self.min_line + self.max_line)

        if mean_plane_normal is None and cached_results is None:
            self._mean_plane_normal = self.compute_mean_plane_normal(self.sensor, self.min_line, self.max_line)
            self._cached_results = [None] * self.NB_CACHED_RESULTS

        elif mean_plane_normal is not None and cached_results is not None:
            self._mean_plane_normal = mean_plane_normal
            self._cached_results = cached_results

        else:
            raise ValueError("Wrong arguments sequence.")

        mid_date = self._sensor.get_date(self._mid_line)

        self._mid_body_to_inert = self._sc_to_body.get_body_to_inertial(mid_date)
        self._mid_sc_to_inert = self._sc_to_body.get_sc_to_inertial(mid_date)

    @property
    def sensor(self) -> LineSensor:
        """Get the underlying sensor."""

        return self._sensor

    @property
    def sc_to_body(self) -> SpacecraftToObservedBody:
        """Get converter between spacecraft and body."""

        return self._sc_to_body

    @property
    def min_line(self) -> int:
        """Get the minimum line number in the search interval."""

        return self._min_line

    @property
    def max_line(self) -> int:
        """Get the maximum line number in the search interval."""

        return self._max_line

    @property
    def max_eval(self) -> int:
        """Get the maximum number of evaluations."""

        return self._max_eval

    @property
    def accuracy(self) -> float:
        """Get the accuracy to use for finding crossing line number."""

        return self._accuracy

    @property
    def mean_plane_normal(self) -> np.ndarray:
        """Get the mean plane normal.

        The normal is oriented such traversing pixels in increasing indices
        order corresponds is consistent with trigonometric order (i.e.
        counterclockwise).
        """

        return self._mean_plane_normal

    @property
    def cached_results(self) -> List[CrossingResult]:
        """Get cached previous results."""

        return self._cached_results

    def compute_mean_plane_normal(self, sensor: LineSensor, min_line: int, max_line: int) -> np.ndarray:
        """Compute the plane containing origin that best fits viewing directions point cloud.

        The normal is oriented such that traversing pixels in increasing indices
        order corresponds to trigonometric order (i.e. counterclockwise).

        Parameters
        ----------
            sensor : line sensor
            min_line : minimum line number
            max_line : maximum line number

        Returns
        -------
            res : normal of the mean plane
        """

        mid_date = sensor.get_date(0.5 * min_line + max_line)

        # build a centered data matrix
        # (for each viewing direction, we add both the direction and its
        # opposite, thus ensuring the plane will contain origin)
        matrix = np.zeros((3, 2 * sensor.nb_pixels))
        los_sensor = sensor.get_los_arr([mid_date] * sensor.nb_pixels, list(range(sensor.nb_pixels)))
        for i in range(sensor.nb_pixels):
            matrix[:, 2 * i] = los_sensor[i][:]
            matrix[:, 2 * i + 1] = -los_sensor[i][:]

        # Compute Singular Value Decomposition
        m_u = compute_svd(matrix)

        # Extract the left singular vector corresponding to least singular value
        # (i.e. last vector since Hipparchus returns the values
        # in non-increasing order)
        singular_vector = to_array(float(m_u[0, 2]), float(m_u[1, 2]), float(m_u[2, 2]))
        singular_vector *= 1 / get_norm(singular_vector)

        # Check rotation order
        first = sensor.get_los(mid_date, 0)
        last = sensor.get_los(mid_date, sensor.nb_pixels - 1)
        if dot(singular_vector, cross(first, last)) >= 0:
            res = singular_vector
        else:
            res = -singular_vector

        return res

    # pylint: disable=R0914, R0915
    def find(  # noqa:C901, R0914
        self, targets_x_coord: np.ndarray, targets_y_coord: np.ndarray, targets_z_coord: np.ndarray
    ) -> list:
        """Find mean plane crossing.

        Parameters
        ----------
            targets_x_coord : targets ground points x coordinates
                              (np.array = np.array([point1_x, point2_x, .., pointn_x])
            targets_y_coord : targets ground points y coordinates
                              (np.array = np.array([point1_y, point2_y, .., pointn_y])
            targets_z_coord : targets ground points z coordinates
                              (np.array = np.array([point1_z, point2_z, .., pointn_z])

        Returns
        -------
            crossing_result : line number and target direction at mean plane crossing,
                or null if search interval does not bracket a solution
        """

        if isinstance(targets_x_coord, (list, np.ndarray)):
            number_of_points = len(targets_x_coord)
        else:
            number_of_points = 1
            targets_x_coord = np.array([targets_x_coord])
            targets_y_coord = np.array([targets_y_coord])
            targets_z_coord = np.array([targets_z_coord])

        crossing_line, body_to_inert, sc_to_inert = (
            [self._mid_line] * number_of_points,
            [self._mid_body_to_inert] * number_of_points,
            [self._mid_sc_to_inert] * number_of_points,
        )

        # Count the number of available results
        if sum(element is not None for element in self.cached_results) >= 4:
            # we already have computed at least 4 values, we attempt to build a linear
            # model to guess a better start line
            guessed_crossing_line = self.guess_start_line(targets_x_coord, targets_y_coord, targets_z_coord)

            crossing_line = np.array(
                [
                    self._mid_line if (elem < self.min_line or elem > self.max_line) else elem
                    for elem in guessed_crossing_line
                ]
            )

            # dates, body_to_inert, sc_to_inert are all np.array as guessed_crossing_line is an array
            dates = self.sensor.get_date(crossing_line)
            body_to_inert = self.sc_to_body.get_body_to_inertial(dates)
            sc_to_inert = self.sc_to_body.get_sc_to_inertial(dates)

        # We don't use an Hipparchus solver here because we are more interested in reducing the number of evaluations
        # than being accurate as we know the solution is improved in the second stage of inverse location.
        # We expect two or three evaluations only. Each new evaluation shows up quickly in
        # the performances as it involves frames conversions.

        # We need array to be able to do following operations (l332) and store the previous values for each evaluation
        # loop evaluation and each point (lat, lon, alt) that is why we use matrix
        crossing_line_history, beta_history, beta_der_history, indexes_crossing_line, finished = (
            np.array([np.array([0.0] * number_of_points)] * self._max_eval),
            np.array([np.array([0.0] * number_of_points)] * self._max_eval),
            np.array([np.array([0.0] * number_of_points)] * self._max_eval),
            list(range(number_of_points)),
            np.array([False] * number_of_points),
        )

        at_min, at_max = np.array([False] * number_of_points), np.array([False] * number_of_points)
        crossing_results = [None] * number_of_points
        for i in range(self._max_eval):  # pylint: disable=too-many-nested-blocks
            # We store each point parameters in list for each evaluation, at the end of the evaluation the list/line
            # is updated in the general matrix defined above
            crossing_line_history[i] = crossing_line
            target_direction_i, target_vector3d_i, beta_history_i, beta_der_history_i, s_val_i = [], [], [], [], []
            # crossing_line_iteration = 0
            # first loop on coordinates
            for index_crossing_line_element in indexes_crossing_line:
                target = Vector3D(
                    float(targets_x_coord[index_crossing_line_element]),
                    float(targets_y_coord[index_crossing_line_element]),
                    float(targets_z_coord[index_crossing_line_element]),
                )

                target_direction = self.evaluate_line(
                    crossing_line[index_crossing_line_element],
                    PVCoordinates(target, Vector3D.ZERO),
                    body_to_inert[index_crossing_line_element],
                    sc_to_inert[index_crossing_line_element],
                )
                # crossing_line_iteration += 1
                target_direction_i.append(target_direction)
                target_vector3d_i.append(target)
                beta_history_i.append(float(np.arccos(dot(target_direction[0], self.mean_plane_normal))))
                s_val = dot(target_direction[1], self.mean_plane_normal)
                s_val_i.append(s_val)
                beta_der_history_i.append(-s_val / float(np.sqrt(1 - s_val * s_val)))

            # From now it is possible to use vectorized operation that is why the for loop is stop and will be
            # resumed later
            beta_history[i] = np.array(beta_history_i)
            beta_der_history[i] = np.array(beta_der_history_i)

            if i == 0:
                # Simple Newton iteration, for first iteration
                delta_l = (0.5 * float(np.pi) - beta_history[i]) / beta_der_history[i]
                crossing_line += delta_l

            else:
                # Inverse cubic iteration
                a_0 = beta_history[i - 1] - 0.5 * math.pi
                l_0 = crossing_line_history[i - 1]
                d_0 = beta_der_history[i - 1]
                a_1 = beta_history[i] - 0.5 * math.pi
                l_1 = crossing_line_history[i]
                d_1 = beta_der_history[i]
                a1_m_a0 = a_1 - a_0
                crossing_line = (
                    (l_0 * (a_1 - 3 * a_0) - a_0 * a1_m_a0 / d_0) * a_1 * a_1
                    + (l_1 * (3 * a_1 - a_0) - a_1 * a1_m_a0 / d_1) * a_0 * a_0
                ) / (a1_m_a0 * a1_m_a0 * a1_m_a0)

                delta_l = crossing_line - l_1

            delta_l = np.abs(delta_l)

            elem_index_delta_l = 0
            # elem_index_delta_l, indices_to_delete = 0, []
            crossing_lines_dates = self.sensor.get_date(crossing_line)

            # Resume for loop on "coordinates"
            for elem_delta_l in delta_l:
                current_element_finished = False
                if float(elem_delta_l) <= self.accuracy:
                    # Stop immediately computation for this element, without doing any additional evaluation!
                    crossing_result = CrossingResult(
                        crossing_lines_dates[elem_index_delta_l],
                        crossing_line[elem_index_delta_l],
                        target_vector3d_i[elem_index_delta_l],
                        target_direction_i[elem_index_delta_l][0],
                        target_direction_i[elem_index_delta_l][1],
                    )

                    is_new = True
                    for existing in self.cached_results:
                        if existing is not None:  # TODO CHANGEMENT
                            is_new = (
                                is_new
                                and float(np.abs(crossing_line[elem_index_delta_l] - existing.line)) > self.accuracy
                            )

                    if is_new:
                        # This result is different from the existing ones,
                        # it brings new sampling data to the cache
                        if len(self.cached_results) >= self.NB_CACHED_RESULTS:
                            self.cached_results.pop(-1)

                        self.cached_results.insert(0, crossing_result)

                    # Search is finished for this element so we store its index to be able to remove it from our
                    # lists in order to stop any computation for this element and to continue the search for other
                    # elements. We store the crossing result (what will be returned)
                    # indices_to_delete.append(elem_index_delta_l)
                    current_element_finished = True
                    finished[indexes_crossing_line[elem_index_delta_l]] = current_element_finished
                    crossing_results[indexes_crossing_line[elem_index_delta_l]] = crossing_result

                if not current_element_finished:
                    for j_index in range(i):
                        if (
                            float(
                                np.abs(
                                    crossing_line[elem_index_delta_l]
                                    - crossing_line_history[j_index][elem_index_delta_l]
                                )
                            )
                            <= 1.0
                        ):
                            # Rare case: we are stuck in a loop!
                            # switch to a more robust (but slower) algorithm in this case

                            slow_result = self.slow_find(
                                PVCoordinates(
                                    target_vector3d_i[indexes_crossing_line[elem_index_delta_l]], Vector3D.ZERO
                                ),
                                crossing_line[elem_index_delta_l],
                            )
                            if slow_result is None:
                                # indices_to_delete.append(elem_index_delta_l)
                                current_element_finished = True
                                finished[indexes_crossing_line[elem_index_delta_l]] = current_element_finished
                                crossing_results[indexes_crossing_line[elem_index_delta_l]] = None

                                if len(self.cached_results) >= self.NB_CACHED_RESULTS:
                                    self.cached_results.pop(-1)

                            else:
                                self.cached_results.insert(0, slow_result)
                                # indices_to_delete.append(elem_index_delta_l)
                                current_element_finished = True
                                finished[indexes_crossing_line[elem_index_delta_l]] = current_element_finished
                                crossing_results[indexes_crossing_line[elem_index_delta_l]] = self.cached_results[0]

                    if crossing_line[elem_index_delta_l] < self.min_line and not current_element_finished:
                        if at_min[elem_index_delta_l]:
                            # We were already trying at minLine and we need to go below that
                            # give up as the solution is out of search interval
                            # indices_to_delete.append(elem_index_delta_l)
                            current_element_finished = True
                            finished[indexes_crossing_line[elem_index_delta_l]] = current_element_finished
                            crossing_results[indexes_crossing_line[elem_index_delta_l]] = None

                        at_min[elem_index_delta_l] = True
                        crossing_line[elem_index_delta_l] = self.min_line

                    elif crossing_line[elem_index_delta_l] > self.max_line and not current_element_finished:
                        if at_max[elem_index_delta_l]:
                            # We were already trying at maxLine and we need to go above that
                            # give up as the solution is out of search interval

                            # indices_to_delete.append(elem_index_delta_l)
                            current_element_finished = True
                            finished[indexes_crossing_line[elem_index_delta_l]] = current_element_finished
                            crossing_results[indexes_crossing_line[elem_index_delta_l]] = None

                        at_max[elem_index_delta_l] = True
                        crossing_line[elem_index_delta_l] = self.max_line

                    else:
                        # The next evaluation will be a regular point
                        at_min[elem_index_delta_l] = False
                        at_max[elem_index_delta_l] = False

                # To take into account next element parameters in the for loop
                elem_index_delta_l += 1

            # For every element/coordinates for which the search is finished we remove it from our
            # lists in order to stop any computation (their results have already been saved in crossing_results
            # for these elements and to continue the search for other
            # elements.
            # indices_to_delete.sort(reverse=True)
            # for index_to_delete in indices_to_delete:
            #     crossing_line = np.delete(crossing_line, index_to_delete, 0)
            #     beta_history = np.delete(beta_history, index_to_delete, 1)
            #     crossing_line_history = np.delete(crossing_line_history, index_to_delete, 1)
            #     beta_der_history = np.delete(beta_der_history, index_to_delete, 1)
            #     at_min = np.delete(at_min, index_to_delete, 0)
            #     at_max = np.delete(at_max, index_to_delete, 0)
            #
            #     indexes_crossing_line = list(range(len(crossing_line)))

            if finished.all():
                return crossing_results

            date = self.sensor.get_date(crossing_line)
            body_to_inert = self.sc_to_body.get_body_to_inertial(date)
            sc_to_inert = self.sc_to_body.get_sc_to_inertial(date)

        return crossing_results

    def guess_start_line(self, targetx: np.ndarray, targety: np.ndarray, targetz: np.ndarray) -> np.array:
        """Guess a start line using the last four results.

        Parameters
        ----------
            targetx : target ground points x coordinate (array)
            targety : target ground points y coordinate (array)
            targetz : target ground points z coordinate (array)

        Returns
        -------
            result : guessed start line
        """

        # Assume a linear model of the form l = ax + by + cz + d
        n_val = sum(element is not None for element in self.cached_results)

        m_matrix = np.zeros((n_val, 4))
        v_vector = np.zeros(n_val)
        i = 0

        for crossing_result in self.cached_results:
            if crossing_result is not None:
                m_matrix[i, 0] = crossing_result.target[0]
                m_matrix[i, 1] = crossing_result.target[1]
                m_matrix[i, 2] = crossing_result.target[2]
                m_matrix[i, 3] = 1.0
                v_vector[i] = crossing_result.line
                i += 1

        # compute QR decomposition and solve qr * x = b equation
        v_x = matrix_solve(m_matrix, v_vector)
        # Apply the linear model
        return targetx * v_x[0] + targety * v_x[1] + targetz * v_x[2] + v_x[3]

    def univariate_function(self, x_val: float, target_pv: PVCoordinates) -> float:
        """Univariate function"""

        try:
            date = self.sensor.get_date(x_val)
            target_direction = self.evaluate_line(
                np.array([x_val]),
                target_pv,
                self.sc_to_body.get_body_to_inertial(date),
                self.sc_to_body.get_sc_to_inertial(date),
            )
            return 0.5 * math.pi - math.acos(dot(target_direction[0], self.mean_plane_normal))

        except PyRuggedError as pre:
            raise PyRuggedInternalError from pre

    # pylint: disable=unused-argument
    def slow_find(self, target_pv: PVCoordinates, initial_guess: float) -> CrossingResult:
        """Find mean plane crossing using a slow but robust method.

        Parameters
        ----------
            target_pv : target ground point
            initial_guess : initial guess for the crossing line

        Returns
        -------
            result : line number and target direction at mean plane crossing,
                or null if search interval does not bracket a solution
        """

        crossing_line = brentq(
            self.univariate_function, self.min_line, self.max_line, maxiter=self._max_eval, args=(target_pv)
        )

        date = self.sensor.get_date(crossing_line)
        target_direction = self.evaluate_line(
            np.array([crossing_line]),
            target_pv,
            self.sc_to_body.get_body_to_inertial(date),
            self.sc_to_body.get_sc_to_inertial(date),
        )
        return CrossingResult(
            self.sensor.get_date(crossing_line),
            crossing_line,
            target_pv.getPosition(),
            target_direction[0],
            target_direction[1],
        )

    def evaluate_line(
        self, line_number: float, target_pv: PVCoordinates, body_to_inert: Transform, sc_to_inert: Transform
    ) -> List[np.ndarray]:
        """Evaluate geometry for a given line number.

        Parameters
        ----------
            line_number : current lines numbers of wanted pixels np.array([line_pix1, line_pix2, line_pix_3])
            target_pv : target ground point
            body_to_inert : transform from observed body to inertial frame, for current line
            sc_to_inert : transform from inertial frame to spacecraft frame, for current line

        Returns
        -------
            result : target direction in spacecraft frame, with its first derivative
                with respect to line number
        """

        # Compute the transform between spacecraft and observed body
        ref_inert = sc_to_inert.transformPVCoordinates(
            PVCoordinates(Vector3D(self.sensor.position.tolist()), Vector3D.ZERO)
        )

        if self._light_time_correction:
            # Apply light time correction
            i_t = StaticTransform.cast_(body_to_inert).transformPosition(target_pv.getPosition())
            delta_t = ref_inert.getPosition().distance(i_t) / Constants.SPEED_OF_LIGHT
            target_inert = body_to_inert.shiftedBy(-delta_t).transformPVCoordinates(target_pv)

        else:
            # Don't apply light time correction
            target_inert = body_to_inert.transformPVCoordinates(target_pv)

        l_inert = PVCoordinates(ref_inert, target_inert)
        inert_to_sc = sc_to_inert.getInverse()

        if self._aberration_of_light_correction:
            # Apply aberration of light correction
            # as the spacecraft velocity is small with respect to speed of light,
            # we use classical velocity addition and not relativistic velocity addition
            # we have: c * lInert + vsat = k * obsLInert

            spacecraft_pv = sc_to_inert.transformPVCoordinates(PVCoordinates.ZERO)
            l_val = Vector.cast_(l_inert.getPosition()).normalize()
            l_dot = self.normalized_dot(l_inert.getPosition(), l_inert.getVelocity())
            k_obs = Vector3D(Constants.SPEED_OF_LIGHT, l_val, +1.0, spacecraft_pv.getVelocity())
            obs_l_inert = Vector.cast_(k_obs).normalize()

            # The following derivative is computed under the assumption the spacecraft velocity
            # is constant in inertial frame ... It is obviously not true, but as this velocity
            # is very small with respect to speed of light, the error is expected to remain small
            obs_l_inert_dot = self.normalized_dot(k_obs, Vector3D(Constants.SPEED_OF_LIGHT, l_dot))

        else:
            # Don't apply aberration of light correction
            obs_l_inert = Vector.cast_(l_inert.getPosition()).normalize()
            obs_l_inert_dot = self.normalized_dot(l_inert.getPosition(), l_inert.getVelocity())

        direction = StaticTransform.cast_(inert_to_sc).transformVector(obs_l_inert)
        direction_dot = Vector3D(
            +1.0,
            StaticTransform.cast_(inert_to_sc).transformVector(obs_l_inert_dot),
            -1.0,
            Vector3D.crossProduct(inert_to_sc.getRotationRate(), direction),
        )

        # Combine vector value and derivative
        rate = self.sensor.get_rate(line_number)

        direction_dot_rate = direction_dot.scalarMultiply(1.0 / rate)

        return [to_array_v(direction.toArray()), to_array_v(direction_dot_rate.toArray())]

    def normalized_dot(self, u_vector: Vector3D, u_dot: Vector3D) -> Vector3D:
        """Compute the derivative of normalized vector.

        Parameters
        ----------
            u_vector : base vector
            u_dot : derivative of the base vector

        Returns
        -------
            result : vDot, where v = u / ||u||
        """

        n_val = u_vector.getNorm()
        return Vector3D(1.0 / n_val, u_dot, -Vector3D.dotProduct(u_vector, u_dot) / (n_val * n_val * n_val), u_vector)
