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

""" pyrugged Class PyRuggedBuilder.
"""

# pylint: disable=too-many-instance-attributes, too-many-arguments
# pylint: disable=consider-iterating-dictionary
import logging
from typing import Dict, List, Union

from org.orekit.frames import Frame, FramesFactory
from org.orekit.time import AbsoluteDate
from org.orekit.utils import (
    AngularDerivativesFilter,
    CartesianDerivativesFilter,
    IERSConventions,
    TimeStampedAngularCoordinates,
    TimeStampedPVCoordinates,
)

from pyrugged.bodies.body_rotating_frame_id import BodyRotatingFrameId
from pyrugged.bodies.ellipsoid_id import EllipsoidId
from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.bodies.one_axis_ellipsoid import OneAxisEllipsoid
from pyrugged.errors.pyrugged_exception import PyRuggedError, PyRuggedInternalError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.model.inertial_frame_id import InertialFrameId
from pyrugged.model.pyrugged import PyRugged
from pyrugged.sar_sensor.sar_sensor import SARSensor
from pyrugged.utils.constants import Constants
from pyrugged.utils.spacecraft_to_observed_body import SpacecraftToObservedBody
from pyrugged.utils.spacecraft_to_observed_body_sar import SpacecraftToObservedBodySAR


def select_body_rotating_frame(body_rotating_frame: BodyRotatingFrameId) -> Frame:
    """Select body rotating frame.

    Parameters
    ----------
        body_rotating_frame : body rotating frame identifier

    Returns
    -------
        res : selected body rotating frame
    """

    # Set up the rotating frame
    if body_rotating_frame == BodyRotatingFrameId.ITRF:
        res = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

    elif body_rotating_frame == BodyRotatingFrameId.ITRF_EQUINOX:
        res = FramesFactory.getITRFEquinox(IERSConventions.IERS_1996, True)

    elif body_rotating_frame == BodyRotatingFrameId.GTOD:
        res = FramesFactory.getGTOD(IERSConventions.IERS_1996, True)

    else:
        # This should never happen
        raise PyRuggedInternalError

    return res


def select_ellipsoid(ellipsoid_id: EllipsoidId, body_frame: Frame) -> OneAxisEllipsoid:
    """Select Ellipsoid.

    Parameters
    ----------
        ellipsoid_id : reference ellipsoid identifier
        body_frame : body rotating frame

    Returns
    -------
        res : selected ellipsoid
    """

    # Set up the ellipsoid
    if ellipsoid_id == EllipsoidId.GRS80:
        res = OneAxisEllipsoid(Constants.GRS80_EARTH_EQUATORIAL_RADIUS, Constants.GRS80_EARTH_FLATTENING, body_frame)

    elif ellipsoid_id == EllipsoidId.WGS84:
        res = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, body_frame)

    elif ellipsoid_id == EllipsoidId.IERS96:
        res = OneAxisEllipsoid(Constants.IERS96_EARTH_EQUATORIAL_RADIUS, Constants.IERS96_EARTH_FLATTENING, body_frame)

    elif ellipsoid_id == EllipsoidId.IERS2003:
        res = OneAxisEllipsoid(
            Constants.IERS2003_EARTH_EQUATORIAL_RADIUS, Constants.IERS2003_EARTH_FLATTENING, body_frame
        )

    else:
        # This should never happen
        raise PyRuggedInternalError

    return res


def select_inertial_frame(inertial_frame_id: InertialFrameId) -> Frame:
    """Select inertial frame.

    Parameters
    ----------
        inertial_frame_id : inertial frame identifier

    Returns
    -------
        res : selected frame identifier
    """

    if inertial_frame_id == InertialFrameId.GCRF:
        res = FramesFactory.getGCRF()

    elif inertial_frame_id == InertialFrameId.EME2000:
        res = FramesFactory.getEME2000()

    elif inertial_frame_id == InertialFrameId.MOD:
        res = FramesFactory.getMOD(IERSConventions.IERS_1996)

    elif inertial_frame_id == InertialFrameId.TOD:
        res = FramesFactory.getTOD(IERSConventions.IERS_1996, True)

    elif inertial_frame_id == InertialFrameId.VEIS1950:
        res = FramesFactory.getVeis1950()

    else:
        # This should never happen
        raise PyRuggedInternalError

    return res


class PyRuggedBuilder:
    """Builder for PyRugged instances.

    This class implements the builder pattern to create PyRugged instances.
    It does so by using a fluent API in order to clarify reading and allow
    later extensions with new configuration parameters.

    A typical use would be:

    |    rugged = PyRuggedBuilder()
    |    rugged.set_ellipsoid(EllipsoidId.WGS84, BodyRotatingFrameId.IRTF)
    |    rugged.set_time_span(min_date, max_date, t_step, overshoot_tolerance)
    |    rugged.set_trajectory(positions_velocities, pv_interpolation_number,
    |        pv_filter, quaternions, a_interpolation_number, a_filter)
    |
    |    rugged.add_line_sensor(sensor_1)
    |    rugged.add_line_sensor(sensor_2)
    |    rugged.add_line_sensor(sensor_3)
    |
    |    rugged.build()


    If a configuration parameter has not been set prior to the call to build(), then
    an exception will be triggered with an explicit error message.

    """

    def __init__(self):
        """Create a non-configured builder.

        The builder must be configured before calling the
        build() method, otherwise an exception will be triggered
        at build time.

        """

        self._sensors = {}
        self._name = "Rugged"

        self._ellipsoid = None

        self._tile_updater = None
        self._max_cached_tiles = None

        self._min_date = None
        self._max_date = None
        self._t_step = None
        self._overshoot_tolerance = None

        self._inertial = None
        self._pv_sample = None
        self._pv_neighbors_size = None
        self._pv_derivatives = None
        self._a_sample = None
        self._a_neighbors_size = None
        self._a_derivatives = None
        self._pva_propagator = None
        self._i_step = float("nan")
        self._i_n = -1
        self._sc_to_body = None

    def set_ellipsoid(
        self,
        new_ellipsoid: OneAxisEllipsoid = None,
        ellipsoid_id: EllipsoidId = None,
        body_rotating_frame_id: BodyRotatingFrameId = None,
    ):
        """Set the reference ellipsoid.

        Parameters
        ----------
            new_ellipsoid : existing ellipsoid to be forked (using equatorial_radius, flattening and body frame)
            ellipsoid_id : reference ellipsoid
            body_rotating_frame_id : body rotating frame identifier from an earlier run and frames mismatch
        """

        if new_ellipsoid is None and ellipsoid_id is not None and body_rotating_frame_id is not None:
            new_ellipsoid = select_ellipsoid(ellipsoid_id, select_body_rotating_frame(body_rotating_frame_id))

        self._ellipsoid = ExtendedEllipsoid(
            new_ellipsoid.equatorial_radius,
            new_ellipsoid.flattening,
            new_ellipsoid.body_frame,
        )

        self.check_frames_consistency()

    @property
    def sc_to_body(self) -> Union[SpacecraftToObservedBody, SpacecraftToObservedBodySAR]:
        """Get SpacacraftToObservedBody"""

        return self._sc_to_body

    @property
    def ellipsoid(self) -> ExtendedEllipsoid:
        """Get the ellipsoid."""

        return self._ellipsoid

    @property
    def name(self) -> str:
        """Get the Rugged name."""

        return self._name

    @name.setter
    def name(self, name: str):
        """Set the Rugged name."""

        self._name = name

    def set_time_span(
        self, new_min_date: AbsoluteDate, new_max_date: AbsoluteDate, new_t_step: float, new_overshoot_tolerance: float
    ):
        """Set the time span to be covered for direct and inverse location calls.

        This method set only the time span and not the trajectory, therefore it
        must be used together with either
        set_trajectory(InertialFrameId, List, int, CartesianDerivativesFilter, List, int, AngularDerivativesFilter),
        set_trajectory(Frame, List, int, CartesianDerivativesFilter, List, int, AngularDerivativesFilter),
        or set_trajectory(double, int, CartesianDerivativesFilter, AngularDerivativesFilter, Propagator)
        but should not be mixed with set_trajectory_and_time_span(InputStream).

        Parameters
        ----------
            new_min_date : start of search time span
            new_max_date : end of search time span
            new_t_step : step to use for inertial frame to body frame transforms cache computations (s)
            new_overshoot_tolerance : tolerance in seconds allowed for min_date and max_date overshooting (s)
        """

        self._min_date = new_min_date
        self._max_date = new_max_date
        self._t_step = new_t_step
        self._overshoot_tolerance = new_overshoot_tolerance
        self._sc_to_body = None

    @property
    def min_date(self) -> AbsoluteDate:
        """Get the start of search time span."""

        return self._min_date

    @property
    def max_date(self) -> AbsoluteDate:
        """Get the end of search time span."""

        return self._max_date

    @property
    def t_step(self) -> float:
        """Get the step to use for inertial frame to body frame transforms cache computations."""

        return self._t_step

    @property
    def overshoot_tolerance(self) -> float:
        """Get the tolerance in seconds allowed for get_min_date() and get_max_date() overshooting."""

        return self._overshoot_tolerance

    def set_trajectory(
        self,
        positions_velocities: List[TimeStampedPVCoordinates],
        pv_interpolation_number: int,
        pv_filter: CartesianDerivativesFilter,
        quaternions: List[TimeStampedAngularCoordinates] = None,
        a_interpolation_number: int = None,
        a_filter: AngularDerivativesFilter = None,
        inertial_frame_id: InertialFrameId = None,
        inertial_frame: Frame = None,
    ):
        """Set the spacecraft trajectory.

        This method set only the trajectory and not the time span, therefore it
        must be used together with the set_time_span(AbsoluteDate, AbsoluteDate, float, float)
        but should not be mixed with set_trajectory_and_time_span(InputStream).

        Parameters
        ----------
            inertial_frame_id : inertial frame identifier used for spacecraft positions/velocities/quaternions
            positions_velocities : satellite position and velocity (m and m/s in inertial frame)
            pv_interpolation_number : number of points to use for position/velocity interpolation
            pv_filter : filter for derivatives from the sample to use in position/velocity interpolation
            quaternions : satellite quaternions with respect to inertial frame
            a_interpolation_number : number of points to use for attitude interpolation
            a_filter : filter for derivatives from the sample to use in attitude interpolation
            inertial_frame_id : inertial frame identifier (optional)
            inertial_frame : inertial frame (optional)

        """

        if inertial_frame is None and inertial_frame_id is not None:
            inertial_frame = select_inertial_frame(inertial_frame_id)

        self._inertial = inertial_frame
        self._pv_sample = positions_velocities
        self._pv_neighbors_size = pv_interpolation_number
        self._pv_derivatives = pv_filter
        self._a_sample = quaternions
        self._a_neighbors_size = a_interpolation_number
        self._a_derivatives = a_filter
        self._pva_propagator = None
        self._i_step = float("nan")
        self._i_n = -1
        self._sc_to_body = None

    @property
    def inertial_frame(self) -> Frame:
        """Get the inertial frame."""

        return self._inertial

    @property
    def positions_velocities(self) -> List[TimeStampedPVCoordinates]:
        """Get the satellite position and velocity (m and m/s in inertial frame)."""

        return self._pv_sample

    @property
    def pv_interpolation_number(self) -> int:
        """Get the number of points to use for position/velocity interpolation."""

        return self._pv_neighbors_size

    @property
    def pv_filter(self) -> CartesianDerivativesFilter:
        """Get the filter for derivatives from the sample to use in position/velocity interpolation."""

        return self._pv_derivatives

    @property
    def quaternions(self) -> List[TimeStampedAngularCoordinates]:
        """Get the satellite quaternions with respect to inertial frame."""

        return self._a_sample

    @property
    def interpolation_number(self) -> int:
        """Get the number of points to use for attitude interpolation."""

        return self._a_neighbors_size

    @property
    def a_filter(self) -> AngularDerivativesFilter:
        """Get the filter for derivatives from the sample to use in attitude interpolation."""

        return self._a_derivatives

    def check_frames_consistency(self):
        """Check frames consistency."""

        if (
            self.ellipsoid is not None
            and self._sc_to_body is not None
            and not self.ellipsoid.body_frame.getName() == self._sc_to_body.body_frame.getName()
        ):
            # If frames have been set both by direct calls
            # and by deserializing an interpolator dump and a mismatch occurs
            raise PyRuggedError(
                PyRuggedMessages.FRAMES_MISMATCH_WITH_INTERPOLATOR_DUMP.value,
                self.ellipsoid.body_frame.getName(),
                self._sc_to_body.body_frame.getName(),
            )

    def create_interpolator_if_needed(self):
        """Create a transform interpolator if needed."""

        if self.ellipsoid is None:
            raise PyRuggedError(PyRuggedMessages.UNINITIALIZED_CONTEXT.value, "PyRuggedBuilder.set_ellipsoid()")

        if self._sc_to_body is None:
            if self._pv_sample is not None:
                self._sc_to_body = self.create_interpolator_from_positions(
                    self._inertial,
                    self._ellipsoid.body_frame,
                    self._min_date,
                    self._max_date,
                    self._t_step,
                    self._overshoot_tolerance,
                    self._pv_sample,
                    self._pv_neighbors_size,
                    self._pv_derivatives,
                    self._a_sample,
                    self._a_neighbors_size,
                    self._a_derivatives,
                )

            # elif self.pva_propagator is not None:
            #     self.sc_to_body = self.create_interpolator_from_propagator(
            #         self.inertial,
            #         self.ellipsoid.body_frame,
            #         self.min_date,
            #         self.max_date,
            #         self.t_step,
            #         self.overshoot_tolerance,
            #         self.i_step,
            #         self.i_n,
            #         self.pv_derivatives,
            #         self.a_derivatives,
            #         self.pva_propagator,
            #     )

            else:
                raise PyRuggedError(PyRuggedMessages.UNINITIALIZED_CONTEXT.value, "PyRuggedBuilder.set_trajectory()")

    def create_interpolator_from_positions(
        self,
        inertial_frame: Frame,
        body_frame: Frame,
        min_date: AbsoluteDate,
        max_date: AbsoluteDate,
        t_step: float,
        overshoot_tolerance: float,
        positions_velocities: List[TimeStampedPVCoordinates],
        pv_interpolation_number: int,
        pv_filter: CartesianDerivativesFilter,
        quaternions: List[TimeStampedAngularCoordinates] = None,
        a_interpolation_number: int = None,
        a_filter: AngularDerivativesFilter = None,
    ):
        """Create a transform interpolator from positions and quaternions lists. If attitude parameter are not given
        the return object is SpacecraftToObservedBodySAR

        Parameters
        ----------
            inertial_frame : inertial frame (can be None if we work with SAR)
            body_frame : observed body frame
            min_date : start of search time span
            max_date : end of search time span
            t_step : step to use for inertial frame to body frame transforms cache computations
            overshoot_tolerance : tolerance in seconds allowed for min_date and max_date overshooting
            positions_velocities : satellite position and velocity
            pv_interpolation_number : number of points to use for position/velocity interpolation
            pv_filter : filter for derivatives from the sample to use in position/velocity interpolation
            quaternions : satellite quaternions
            a_interpolation_number : number of points to use for attitude interpolation
            a_filter : filter for derivatives from the sample to use in attitude interpolation

        Returns
        -------
            result : transform interpolator
        """
        if quaternions is None:
            return SpacecraftToObservedBodySAR(
                body_frame,
                min_date,
                max_date,
                t_step,
                overshoot_tolerance,
                positions_velocities,
                pv_interpolation_number,
                pv_filter,
            )
        return SpacecraftToObservedBody(
            inertial_frame,
            body_frame,
            min_date,
            max_date,
            t_step,
            overshoot_tolerance,
            positions_velocities,
            pv_interpolation_number,
            pv_filter,
            quaternions,
            a_interpolation_number,
            a_filter,
        )

    # # pylint: disable=unused-argument
    # def create_interpolator_from_propagator(
    #     self,
    #     inertial_frame: Frame,
    #     body_frame: Frame,
    #     min_date: AbsoluteDate,
    #     max_date: AbsoluteDate,
    #     t_step: float,
    #     overshoot_tolerance: float,
    #     interpolation_step: float,
    #     interpolation_number: int,
    #     pv_filter: CartesianDerivativesFilter,
    #     a_filter: AngularDerivativesFilter,
    #     propagator: Propagator,
    # ):
    #     """Create a transform interpolator from a propagator.

    #     Parameters
    #     ----------
    #         inertial_frame : inertial frame
    #         body_frame : observed body frame
    #         min_date : start of search time span
    #         max_date : end of search time span
    #         t_step : step to use for inertial frame to body frame transforms cache computations
    #         overshoot_tolerance : tolerance in seconds allowed for min_date and max_date overshooting
    #         interpolation_step : step to use for inertial/Earth/spacecraft transforms interpolations
    #         interpolation_number : number of points of to use for inertial/Earth/spacecraft transforms interpolations
    #         pv_filter : filter for derivatives from the sample to use in position/velocity interpolation
    #         a_filter : filter for derivatives from the sample to use in attitude interpolation
    #         propagator : global propagator

    #     Returns
    #     -------
    #         result : transform interpolator
    #     """

    #     # TODO
    #     raise ValueError("Functionality not implemented yet.")

    def add_sensor(self, sensor: Union[LineSensor, SARSensor]):
        """Set up line sensor model.

        Parameters
        ----------
            sensor : line sensor model
        """

        if sensor.name in self._sensors.keys():
            logging.warning(f'{"Sensor with name "}{sensor.name}{" is already registered."}')
        self._sensors[sensor.name] = sensor

    def clear_line_sensors(self):
        """Remove all line sensors."""

        self._sensors = {}

    @property
    def sensors(self) -> Dict[str, Union[LineSensor, SARSensor]]:
        """Get all sensors."""

        return self._sensors

    def build(self) -> PyRugged:
        """Build a PyRugged instance.

        Returns
        -------
            result : PyRugged instance
        """

        self.create_interpolator_if_needed()

        return PyRugged(
            self.ellipsoid,
            self._sc_to_body,
            self._sensors,
            self._name,
        )
