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

"""pyrugged Class DumpManager"""

import os
import threading
from typing import List

from pyrugged.errors.dump import Dump
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages

DUMP_VAR = None


class DumpManager:
    """Class managing debug dumps."""

    def __init__(self):
        """Builds a new instance."""

        self.dump = threading.local()
        self.dump.x = None
        self.is_suspended = False

    def activate(self, dump_file):
        """Activate debug dump.

        Parameters
        ----------
            dump_file : pathlib.Path(<user_dump_file_path>).open("a")
                Dump file (text file)

        """

        if self.is_active():
            raise PyRuggedError(PyRuggedMessages.DEBUG_DUMP_ALREADY_ACTIVE.value)

        try:

            self.dump.x = Dump(dump_file)
        except IOError as ioe:
            if hasattr(ioe, "message"):
                error_message = ioe.message
            else:
                error_message = ioe
            raise PyRuggedError(
                PyRuggedMessages.DEBUG_DUMP_ACTIVATION_ERROR.value, os.path.abspath(dump_file), error_message
            ) from ioe

    def deactivate(self):
        """Deactivate debug dump."""

        if self.is_active():
            self.dump.x.deactivate()
            self.dump.x = None

        else:
            raise PyRuggedError(PyRuggedMessages.DEBUG_DUMP_ALREADY_ACTIVE.value)

    def suspend(self):
        """Suspend the dump.
        In case the dump is already suspended, keep the previous status in order to
        correctly deal the resume stage.

        Returns
        -------
            res : flag to tell if the dump is already suspended (true; false otherwise)

        """

        if self.is_suspended:
            res = self.is_suspended
        else:
            self.is_suspended = True
            res = False

        return res

    def resume(self, was_suspended):
        """Resume the dump, only if it was not already suspended.

        Parameters
        ----------
            was_suspended : flag to tell if the dump was already suspended (true; false otherwise)
        """

        if not was_suspended:
            self.is_suspended = False

    def end_nicely(self):
        """In case dump is suspended and an exception is thrown,
        allows the dump to end nicely.
        """

        self.is_suspended = False
        if self.is_active():
            self.deactivate()

    def is_active(self):
        """Check if dump is active for this thread.

        Returns
        -------
            result : true if dump is active for this thread

        """

        return self.dump.x is not None and not self.is_suspended

    def dump_tile_cell(self, tile, latitude_index, longitude_index, elevation):
        """Dump DEM cell data.

        Parameters
        ----------
            tile : tile to which the cell belongs
            latitude_index : latitude index of the cell
            longitudeIndex : longitude index of the cell
            elevation : elevation of the cell
        """

        if self.is_active():
            self.dump.x.dump_tile_cell(tile, latitude_index, longitude_index, elevation)

    def dump_algorithm(self, algorithm_id, specific=None):
        """Dump algorithm data.

        Parameters
        ----------
            algorithm_id : algorithm identifier
            specific : algorithm specific extra data
        """

        if self.is_active():
            self.dump.x.dump_algorithm(algorithm_id, specific)

    def dump_ellipsoid(self, ellipsoid):
        """Dump ellipsoid data.

        Parameters
        ----------
            ellipsoid : ellipsoid to dump
        """

        if self.is_active():
            self.dump.x.dump_ellipsoid(ellipsoid)

    def dump_direct_location(
        self,
        date,
        sensor_position,
        los,
        light_time_correction,
        aberration_of_light_correction,
        refraction_correction,
    ):
        """Dump a direct location computation.

        Parameters
        ----------
            date : date of the location
            sensor_position : sensor position in spacecraft frame
            los : normalized line-of-sight in spacecraft frame
            light_time_correction : flag for light time correction
            aberration_of_light_correction : flag for aberration of light correction
            refraction_correction : flag for refraction correction
        """

        if self.is_active():
            self.dump.x.dump_direct_location(
                date, sensor_position, los, light_time_correction, aberration_of_light_correction, refraction_correction
            )

    def dump_direct_location_result(self, point_gp):
        """Dump a direct location result.

        Parameters
        ----------
            point_gp : resulting geodetic point
        """

        if self.is_active():
            self.dump.x.dump_direct_location_result(point_gp)

    # pylint: disable=too-many-arguments
    def dump_inverse_location(
        self,
        sensor,
        point,
        ellipsoid,
        min_line,
        max_line,
        light_time_correction,
        aberration_of_light_correction,
        refraction_correction,
    ):
        """Dump an inverse location computation.

        Parameters
        ----------
            sensor : sensor
            point : point to localize
            ellipsoid : the used ellipsoid
            min_line : minimum line number
            max_line : maximum line number
            light_time_correction : flag for light time correction
            aberration_of_light_correction : flag for aberration of light correction
            refraction_correction : flag for refraction correction
        """

        if self.is_active():
            self.dump.x.dump_inverse_location(
                sensor,
                point,
                min_line,
                max_line,
                light_time_correction,
                aberration_of_light_correction,
                refraction_correction,
            )
            self.dump.x.dump_ellipsoid(ellipsoid)

    def dump_inverse_location_result(self, pixel):
        """Dump an inverse location result.

        Parameters
        ----------
            pixel : resulting sensor pixel
        """

        if self.is_active():
            self.dump.x.dump_inverse_location_result(pixel)

    def dump_transform(
        self,
        sc_to_body,
        index,
        body_to_inertial,
        sc_to_inertial,
    ):
        """Dump an observation transform.

        Parameters
        ----------
            sc_to_body : provider for observation
            index : index of the transform
            body_to_inertial : transform from body frame to inertial frame
            sc_to_inertial : transfrom from spacecraft frame to inertial frame
        """

        if self.is_active():
            self.dump.x.dump_transform(sc_to_body, index, body_to_inertial, sc_to_inertial)

    def dump_sensor_mean_plane(self, mean_plane):
        """Dump a sensor mean plane.

        Parameters
        ----------
            mean_plane : mean plane associated with sensor
        """

        if self.is_active():
            self.dump.x.dump_sensor_mean_plane(mean_plane)

    def dump_sensor_los(self, sensor, date, i: int, los):
        """Dump a sensor LOS.

        Parameters
        ----------
            sensor : sensor
            date : date
            i : pixel index
            los : pixel normalized line-of-sight
        """

        if self.is_active():
            self.dump.x.dump_sensor_los(sensor, date, i, los)

    def dump_sensor_los_arr(self, sensor, dates, pixels: List[int], los):
        """Dump a sensor LOS.

        Parameters
        ----------
            sensor : sensor
            dates : dates
            pixels : pixel indexes
            los : pixel normalized line-of-sight
        """

        if self.is_active():
            for i, pixel in enumerate(pixels):
                self.dump.x.dump_sensor_los(sensor, dates[i], pixel, los[i])

    def dump_sensor_datation(self, sensor, line_number, date):
        """Dump a sensor datation.

        Parameters
        ----------
            sensor : sensor
            line_number : line Number
            date : date
        """

        if self.is_active():
            self.dump.x.dump_sensor_datation(sensor, line_number, date)

    def dump_sensor_rate(self, sensor, line_number, rate):
        """Dump a sensor rate.

        Parameters
        ----------
            sensor : sensor
            line_number : line Number
            rate : rate
        """

        if self.is_active():
            self.dump.x.dump_sensor_rate(sensor, line_number, rate)
