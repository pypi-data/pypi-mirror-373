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

"""pyrugged Class PyRugged"""


import logging
from typing import Dict, Union

from org.orekit.frames import Transform
from org.orekit.time import AbsoluteDate

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.sar_sensor.sar_sensor import SARSensor
from pyrugged.utils.spacecraft_to_observed_body import SpacecraftToObservedBody
from pyrugged.utils.spacecraft_to_observed_body_sar import SpacecraftToObservedBodySAR


class PyRugged:
    """Main class of Rugged library API. See PyRuggedBuilder."""

    def __init__(
        self,
        ellipsoid: ExtendedEllipsoid,
        sc_to_body: Union[SpacecraftToObservedBody, SpacecraftToObservedBodySAR],
        sensors: Dict[str, Union[LineSensor, SARSensor]],
        name: str,
    ):
        """Builds a new instance.

        Rugged object contains platform (frame transform between spacecraft,inertial and body frame),
        instrument and body elements.

        Parameters
        ----------
            ellipsoid : reference ellipsoid
            sc_to_body : transforms interpolator between spacecraft, inertial and body frame
            sensors : sensors
            name : PyRugged name

        """

        # Orbit/attitude to body converter
        self._sc_to_body = sc_to_body

        # PyRugged name
        self._name = name

        # PÿRugged Linesensors or SARSensors
        self._sensors = sensors

        # Space reference
        self._ellipsoid = ellipsoid

    @property
    def sc_to_body(self) -> Union[SpacecraftToObservedBody, SpacecraftToObservedBodySAR]:
        """Get converter between spacecraft and body."""

        return self._sc_to_body

    @property
    def name(self) -> str:
        """Get the PyRugged name."""

        return self._name

    @property
    def min_date(self) -> AbsoluteDate:
        """Get the start of search time span."""

        return self.sc_to_body.min_date

    @property
    def max_date(self) -> AbsoluteDate:
        """Get the end of search time span."""

        return self.sc_to_body.max_date

    @property
    def ellipsoid(self) -> ExtendedEllipsoid:
        """Get the observed body ellipsoid."""

        return self._ellipsoid

    @property
    def sensors(self) -> Dict[str, Union[LineSensor, SARSensor]]:
        """Get sensors"""

        return self._sensors

    def is_in_range(self, date: AbsoluteDate) -> bool:
        """Check if a date is in the supported range.

        The support range is given by the min_date and
        max_date construction parameters, with an
        overshoot_tolerance margin accepted (i.e. a date slightly
        before min_date or slightly after max_date
        will be considered in range if the overshoot does not exceed
        the tolerance set at construction).

        Parameters
        ----------
            date : date to check

        Returns
        -------
            result : true if date is in the supported range
        """

        return self.sc_to_body.is_in_range(date)

    def get_sc_to_inertial(self, date: AbsoluteDate) -> Transform:
        """Get transform from spacecraft to inertial frame.

        Parameters
        ----------
            date : date of the transform

        Returns
        -------
            result : transform from sacecraft to inertial frame
        """

        if isinstance(self.sc_to_body, SpacecraftToObservedBody):
            return self.sc_to_body.get_sc_to_inertial(date)

        raise PyRuggedError(PyRuggedMessages.NO_INERTIAL_FRAME_FOR_SAR_SENSOR.value)

    def get_inertial_to_body(self, date: AbsoluteDate) -> Transform:
        """Get transform from inertial frame to observed body frame.

        Parameters
        ----------
            date : date of the transform

        Returns
        -------
            result : transform from inertial frame to observed body frame
        """

        if isinstance(self.sc_to_body, SpacecraftToObservedBody):
            return self.sc_to_body.get_inertial_to_body(date)

        raise PyRuggedError(PyRuggedMessages.NO_INERTIAL_FRAME_FOR_SAR_SENSOR.value)

    def get_body_to_inertial(self, date: AbsoluteDate) -> Transform:
        """Get transform from observed body frame to inertial frame.

        Parameters
        ----------
            date : date of the transform

        Returns
        -------
            result : transform from observed body frame to inertial frame
        """

        if isinstance(self.sc_to_body, SpacecraftToObservedBody):
            return self.sc_to_body.get_body_to_inertial(date)

        raise PyRuggedError(PyRuggedMessages.NO_INERTIAL_FRAME_FOR_SAR_SENSOR.value)

    def add_sensor(self, sensor: Union[LineSensor, SARSensor]):
        """Set up sensor model.

        Parameters
        ----------
            sensor : sensor model
        """

        if sensor.name in self._sensors.keys():
            logging.warning(f'{"Sensor with name "}{sensor.name}{" is already registered."}')
        self._sensors[sensor.name] = sensor

    def get_sensor(self, sensor_name: str = None) -> Union[LineSensor, SARSensor]:
        """Get a sensor.

        Parameters
        ----------
            sensor_name : sensor name

        Returns
        -------
            sensor : selected sensor
            sensor_name : sensor name

        """
        if sensor_name is None:
            if len(self.sensors) == 1:
                sensor = next(iter(self.sensors.values()))
                sensor_name = sensor.name
            else:
                raise PyRuggedError(PyRuggedMessages.DEFAULT_SENSOR.value)

        else:
            if sensor_name not in self.sensors:
                raise PyRuggedError(PyRuggedMessages.UNKNOWN_SENSOR.value, sensor_name)

            sensor = self.sensors[sensor_name]
        if sensor is None:
            raise PyRuggedError(PyRuggedMessages.UNKNOWN_SENSOR.value, sensor_name)

        return sensor
