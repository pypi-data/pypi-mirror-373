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

"""optical location"""
from typing import List, Tuple

import numpy as np
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.time import AbsoluteDate

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.constant_elevation_algorithm import ConstantElevationAlgorithm
from pyrugged.model.pyrugged import PyRugged
from pyrugged.utils.math_utils import to_array_v  # pylint: disable=no-name-in-module


class SARLocation:
    """SAR Localisation functions."""

    def __init__(self, rugged: PyRugged, algorithm: ConstantElevationAlgorithm):
        """Builds a new instance.

        Parameters
        ----------
            rugged : Pyrugged instance
        """

        # Orbit/attitude to body converter
        self._rugged = rugged

        # Intersection algorithm
        self._algorithm = algorithm

    @property
    def rugged(self) -> PyRugged:
        """Get rugged instance."""

        return self._rugged

    @property
    def ellipsoid(self) -> ExtendedEllipsoid:
        """Get the observed body ellipsoid."""

        return self.rugged.ellipsoid

    def direct_location(self, lines: List, pixels: List, sensor_name=None) -> Tuple:
        """Direct location lines and pixels.

        Parameters
        ----------
            sensor_name : the sensor name
            lines : list of lines index, np.array(line_1, line_2, line_..., col_n)
            pixels : list of pixels index, np.array(col_1, col_2, col_..., co_ln)
        Returns
        -------
            longitudes, latitudes, altitudes : ground position of intersection point with ground for pixels :
            [col_1, line_1] and [col_2, line_2] and ... and [col_n, line_n]
            Can be None if errors
        """
        sar_sensor = self.rugged.get_sensor(sensor_name)
        ellipsoid = self.rugged.ellipsoid
        couple_pixel_line = []
        longitudes = []
        latitudes = []
        altitudes = []

        for line, pixel in zip(lines, pixels):  # noqa: B905
            # Construction of pixel coordinates by associating col_n with line_n : [col_n, lin_n]
            couple_pixel_line.append([pixel, line])

        # List of Absolute date corresponding to each pixel [col], [line]
        dates = sar_sensor.get_date(couple_pixel_line)
        # List of range corresponding to each pixel [col], [line]
        d_ranges = sar_sensor.get_range(couple_pixel_line)
        # Only zero doppler model available
        doppler = sar_sensor.get_doppler

        sc_to_body = self.rugged.sc_to_body
        if self._algorithm.algorithm_id not in (
            AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID,
            AlgorithmId.IGNORE_DEM_USE_ELLIPSOID,
        ):
            raise PyRuggedError(PyRuggedMessages.SAR_LOCATION_ALGORITH_ALLOWED.value)

        # Iteration on dates to find  lon, lat, alt for each pixel's coordinates
        for date, d_range in zip(dates, d_ranges):  # noqa: B905
            point = self._algorithm.intersection_sar(
                ellipsoid,
                to_array_v(sc_to_body.get_sc_to_body(date).getCartesian().getPosition().toArray()),
                to_array_v(sc_to_body.get_sc_to_body(date).getCartesian().getVelocity().toArray()),
                d_range,
                sar_sensor.is_antenna_pointing_right,
                doppler,
            )

            longitudes.append(point[1])
            latitudes.append(point[0])
            altitudes.append(point[2])
        return longitudes, latitudes, altitudes

    def inverse_location(
        self,
        start_date: AbsoluteDate,
        end_date: AbsoluteDate,
        latitudes: np.ndarray,
        longitudes: np.ndarray,
        altitudes: np.ndarray = None,
        sensor_name: str = None,
        number_line: int = None,
    ) -> Tuple:
        """Inverse location of a ground point.


        Parameters
        ----------
            start_date: acquisition start date,
            end_date: acquisition end date
            sensor_name : name of the line sensor
            longitudes : surface-relative points longitudes [longi_point1, longi_point2, ..., longi_pointn] (rad)
            latitudes : surface-relative point latitudes [lat_point1, lat_point2, ..., lat_pointn], (rad)
            warning must be same length as longitudes
            altitudes : surface-relative point altitudes [alt_pix1, alt_pix2, ..., alt_pixn]
            warning must be same length as longitudes. (if  not specified use algorithm altitude)
            number_line: total number of lines

        Returns
        -------
            result : ([pixels columns], [pixels lines]), i.e. sensor pixels seeing points, or (None, None) if points
                     cannot be seen between the prescribed line numbers. pixel lines = [line_pix1, line_pix2, ...,
                     line_pixn] and pixel columns = [col_pix1, col_pix2, ..., col_pixn]
        """

        if altitudes is None:
            altitudes = self._algorithm.get_elevation(latitudes, longitudes)
        sensor = self.rugged.get_sensor(sensor_name)

        d_range, date = self.get_range_date_from_earth_coordinates(
            latitudes, longitudes, altitudes, start_date, end_date, self.ellipsoid, number_line
        )

        col = sensor.get_pix_from_range(np.array(d_range))
        row = sensor.get_row_from_date(np.array(date), np.array(col))

        return col, row

    def get_range_date_from_earth_coordinates(
        self,
        latitudes: np.ndarray,
        longitudes: np.ndarray,
        altitudes: np.ndarray,
        start_date: AbsoluteDate,
        end_date: AbsoluteDate,
        ellipsoid: ExtendedEllipsoid,
        number_line: int = None,
    ) -> Tuple:
        """Get range and date given a point (lat, lon, alt).

        Parameters
        ----------
            start_date: acquisition start date,
            end_date: acquisition end date
            longitudes : surface-relative points longitudes [longi_point1, longi_point2, ..., longi_pointn] (rad)
            latitudes : surface-relative point latitudes [lat_point1, lat_point2, ..., lat_pointn], (rad)
            warning must be same length as longitudes
            altitudes : surface-relative point altitudes [alt_pix1, alt_pix2, ..., alt_pixn]
            warning must be same length as longitudes. (if  not specified use algorithm altitude)
            ellipsoid: observed body ellipsoid
            number_line: total number of lines

        Returns
        -------
            result : ([ranges], [dates]), for given points on Earth surface, or (None, None) if points cannot be
                     seen between the prescribed line numbers. ranges = [range_pix1, range_pix2, ..., range_pixn] and
                     date = [date_pix1, date_pix2, ..., date_pixn]

        """

        d_ranges = []
        dates = []
        cartesian_surface_coord = ellipsoid.transform_from_point(latitudes, longitudes, altitudes)
        sc_to_body = self.rugged.sc_to_body

        # If total number of lines not given, by default the tolerance is set to 0.0001 second,
        # can be long if time interval is big, that is why it will always be prefered to specify the total line number
        # While parameters and initialization
        tolerance_on_date = 0.0001
        max_iter = 100

        # Time interval parameters
        number_point_per_time_interval = 100

        # If total number of lines not given, we do a point every 0.0001 second, can be long if time interval is big
        if number_line is not None:
            # to ensure sampling less than a half line size
            tolerance_on_date = end_date.durationFrom(start_date) / (3 * number_line)
        # sampling at half line size

        for x_coord, y_coord, z_coord in zip(  # noqa: B905
            cartesian_surface_coord[0], cartesian_surface_coord[1], cartesian_surface_coord[2]
        ):  # noqa: B905
            cartesian_surface_point = Vector3D(float(x_coord), float(y_coord), float(z_coord))
            start_time_duration_from_interval_start_time = 0.0
            start_time_duration_from_interval_end_time = end_date.durationFrom(start_date)

            date_step = 1000.0
            iter_while = 0

            # for each point for which we want to do the inverse location we do a dichotomia to find the date
            # (dichotomia to save computation time)
            while date_step > tolerance_on_date and iter_while < max_iter:
                date_step = (
                    start_time_duration_from_interval_end_time - start_time_duration_from_interval_start_time
                ) / number_point_per_time_interval
                iter_while += 1

                time_step = np.linspace(
                    start_time_duration_from_interval_start_time,
                    start_time_duration_from_interval_end_time,
                    number_point_per_time_interval,
                    endpoint=True,
                )

                # Time iteration to find the range and date, the correct range correspond
                # to minimum range between sat position
                # and point on ground. Time step = Time between 2 lines / 2 to be precise
                distances = []
                for time_gap in time_step:
                    sat_position = (
                        sc_to_body.get_sc_to_body(start_date.shiftedBy(float(time_gap))).getCartesian().getPosition()
                    )
                    distances.append(Vector3D.distance(sat_position, cartesian_surface_point))

                index_min = distances.index(np.array(distances).min())

                # Compute next reduced time interval by kind of dichotomie
                index_start = index_min - 1
                index_end = index_min + 1

                # If at the beginning or the end of the time interval --> particular treatement
                if index_start < 0:
                    index_start = 0
                    index_end = 2

                if index_end > len(time_step) - 1:
                    index_end = len(time_step) - 1
                    index_start = len(time_step) - 3

                start_time_duration_from_interval_start_time = time_step[index_start]
                start_time_duration_from_interval_end_time = time_step[index_end]

            d_ranges.append(distances[index_min])
            dates.append(start_date.shiftedBy(float(time_step[index_min])))

        return d_ranges, dates
