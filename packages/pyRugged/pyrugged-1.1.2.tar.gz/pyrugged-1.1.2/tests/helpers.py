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

"""pyrugged useful test functions"""

import os
from typing import Union

# pylint: disable=too-many-arguments, no-name-in-module
import numpy as np
from org.hipparchus.geometry.euclidean.threed import Rotation, RotationConvention, Vector3D
from org.hipparchus.ode.nonstiff import DormandPrince853Integrator
from org.orekit.attitudes import NadirPointing, YawCompensation
from org.orekit.bodies import CelestialBodyFactory
from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel, ThirdBodyAttraction
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.frames import FramesFactory, StaticTransform
from org.orekit.orbits import CircularOrbit, OrbitType, PositionAngleType
from org.orekit.propagation import SpacecraftState
from org.orekit.propagation.numerical import NumericalPropagator
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import (
    AngularDerivativesFilter,
    CartesianDerivativesFilter,
    PVCoordinates,
    TimeStampedAngularCoordinates,
    TimeStampedPVCoordinates,
)

from pyrugged.bodies.body_rotating_frame_id import BodyRotatingFrameId
from pyrugged.bodies.ellipsoid_id import EllipsoidId
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.line_sensor.linear_line_datation import LinearLineDatation
from pyrugged.los.los_builder import FixedLOS, LOSBuilder, TransformsSequenceLOS
from pyrugged.model.inertial_frame_id import InertialFrameId
from pyrugged.model.pyrugged import PyRugged
from pyrugged.model.pyrugged_builder import PyRuggedBuilder
from pyrugged.utils.coordinates_reader import extract_pv_from_txt, extract_q_from_txt
from pyrugged.utils.math_utils import to_array_v


def create_orbit(mu_val: float):
    """The following orbital parameters have been computed using
    Orekit tutorial about phasing, using the following configuration:
    orbit.date                          = 2012-01-01T00:00:00.000
    phasing.orbits.number               = 143
    phasing.days.number                 =  10
    sun.synchronous.reference[0]  = 0
    sun.synchronous.reference.ascending = false
    sun.synchronous.mean.solar.time     = 10:30:00
    gravity.field.degree                = 12
    gravity.field.order                 = 12

    Parameters
    ----------
        mu_val : float
            Earth gravitational constant

    Returns
    -------
        result : orekit.orbits.CircularOrbit
            The orbit

    """

    date = AbsoluteDate("2012-01-01T00:00:00.000", TimeScalesFactory.getUTC())
    eme2000 = FramesFactory.getEME2000()

    return CircularOrbit(
        7173352.811913891,
        -4.029194321683225e-4,
        0.0013530362644647786,
        float(np.radians(98.63218182243709)),
        float(np.radians(77.55565567747836)),
        float(np.pi),
        PositionAngleType.TRUE,
        eme2000,
        date,
        mu_val,
    )


def add_satellite_pv(gps, eme2000, itrf, satellite_pv_list, abs_date, p_x, p_y, p_z, v_x, v_y, v_z):
    """Add element to satellite_pv_list"""

    ephemeris_date = AbsoluteDate(abs_date, gps)
    position = Vector3D(p_x, p_y, p_z)
    velocity = Vector3D(v_x, v_y, v_z)
    pv_itrf = PVCoordinates(position, velocity)
    transform = itrf.getTransformTo(eme2000, ephemeris_date)
    p_eme_2000 = StaticTransform.cast_(transform).transformPosition(pv_itrf.getPosition())
    v_eme_2000 = StaticTransform.cast_(transform).transformVector(pv_itrf.getVelocity())
    satellite_pv_list.append(TimeStampedPVCoordinates(ephemeris_date, p_eme_2000, v_eme_2000, Vector3D.ZERO))


def add_satellite_q(gps, satellite_q_list, abs_date, q_0, q_1, q_2, q_3):
    """Add element to satellite_q_list argument"""

    attitude_date = AbsoluteDate(abs_date, gps)
    rotation = Rotation(q_0, q_1, q_2, q_3, True)
    pair = TimeStampedAngularCoordinates(attitude_date, rotation, Vector3D.ZERO, Vector3D.ZERO)
    satellite_q_list.append(pair)


def create_propagator(earth, gravity_field, orbit):
    """Create numerical propagator"""

    yaw_compensation = YawCompensation(orbit.getFrame(), NadirPointing(orbit.getFrame(), earth))
    state = SpacecraftState(orbit, yaw_compensation.getAttitude(orbit, orbit.getDate(), orbit.getFrame()), 1180.0)

    # Numerical model for improving orbit
    orbit_type = OrbitType.CIRCULAR
    tolerances = NumericalPropagator.tolerances(0.1, orbit, orbit_type)
    integrator = DormandPrince853Integrator(
        1.0e-4 * orbit.getKeplerianPeriod(), 1.0e-1 * orbit.getKeplerianPeriod(), tolerances[0], tolerances[1]
    )
    integrator.setInitialStepSize(1.0e-2 * orbit.getKeplerianPeriod())
    numerical_propagator = NumericalPropagator(integrator)
    numerical_propagator.addForceModel(HolmesFeatherstoneAttractionModel(earth.body_frame, gravity_field))
    numerical_propagator.addForceModel(ThirdBodyAttraction(CelestialBodyFactory.getSun()))
    numerical_propagator.addForceModel(ThirdBodyAttraction(CelestialBodyFactory.getMoon()))
    numerical_propagator.setOrbitType(orbit_type)
    numerical_propagator.setInitialState(state)
    numerical_propagator.setAttitudeProvider(yaw_compensation)

    return numerical_propagator


def create_gravity_field():
    """Create gravity field"""

    return GravityFieldFactory.getNormalizedProvider(12, 12)


def create_los_curved_line(center, normal, half_aperture, sagitta, n_val):
    """Create los curved line"""

    u_vect = Vector3D.crossProduct(center, normal)
    vect_list = []

    for index in range(n_val):
        x_val = (2.0 * index + 1.0 - n_val) / (n_val - 1)
        alpha = x_val * half_aperture
        beta = x_val * x_val * sagitta
        vect_list.append(
            to_array_v(
                Rotation(normal, alpha, RotationConvention.VECTOR_OPERATOR)
                .applyTo(
                    Rotation(
                        u_vect,
                        beta,
                        RotationConvention.VECTOR_OPERATOR,
                    ).applyTo(center)
                )
                .toArray()
            )
        )

    return LOSBuilder(vect_list).build()


def create_los_perfect_line(center, normal, half_aperture, n_val) -> Union[FixedLOS, TransformsSequenceLOS]:
    """Creates a perfect line of sight list."""

    vector_list = []
    for index in range(n_val):
        alpha = (half_aperture * (2 * index + 1 - n_val)) / (n_val - 1)
        vector_list.append(
            to_array_v(Rotation(normal, alpha, RotationConvention.VECTOR_OPERATOR).applyTo(center).toArray())
        )

    return LOSBuilder(vector_list)


def configure_rugged(
    los: Union[FixedLOS, TransformsSequenceLOS],
    line_datation: LinearLineDatation,
    lines_nb: int,
    position: Vector3D,
    suffix: str = "",
    ellipsoid_id=EllipsoidId.WGS84,
) -> PyRugged:
    """Direct location lines and pixels.

    Parameters
    ----------
       los : lines of sight
       line_datation : linear line datation
       lines_nb : number of lines
       position : sensor position
       suffix : file suffix
       ellipsoid_id : ellipsoid_id
    Returns
    -------
       rugged : pyrugged instance
    """

    first_line = 0
    last_line = lines_nb

    line_sensor = LineSensor(
        "line",
        line_datation,
        to_array_v(position.toArray()),
        los,
    )

    min_date = line_sensor.get_date(first_line)
    max_date = line_sensor.get_date(last_line)

    pv_file_path = os.path.join(
        os.path.dirname(__file__),
        "./data/ref/api/testRuggedAPI_pv_{}.txt".format(suffix),
    )
    q_file_path = os.path.join(
        os.path.dirname(__file__),
        "./data/ref/api/testRuggedAPI_q_{}.txt".format(suffix),
    )

    pv_list = extract_pv_from_txt(pv_file_path)
    q_list = extract_q_from_txt(q_file_path)

    builder = PyRuggedBuilder()
    builder.set_ellipsoid(
        new_ellipsoid=None, ellipsoid_id=ellipsoid_id, body_rotating_frame_id=BodyRotatingFrameId.ITRF
    )
    builder.set_time_span(min_date, max_date, 0.001, 5.0)
    builder.set_trajectory(
        pv_list,
        8,
        CartesianDerivativesFilter.USE_PV,
        q_list,
        2,
        AngularDerivativesFilter.USE_R,
        inertial_frame_id=InertialFrameId.EME2000,
    )
    builder.add_sensor(line_sensor)

    rugged = builder.build()
    return rugged
