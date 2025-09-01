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

"""Test of pyrugged Class SensorPixelCrossing"""

# pylint: disable=duplicate-code
import os

import numpy as np
import pytest
from org.hipparchus.geometry.euclidean.threed import Line, Vector3D
from org.orekit.frames import FramesFactory, StaticTransform, Transform
from org.orekit.orbits import CircularOrbit, PositionAngleType
from org.orekit.time import AbsoluteDate
from org.orekit.utils import AngularDerivativesFilter, CartesianDerivativesFilter, IERSConventions

from pyrugged.bodies.one_axis_ellipsoid import OneAxisEllipsoid
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.line_sensor.linear_line_datation import LinearLineDatation
from pyrugged.line_sensor.sensor_mean_plane_crossing import SensorMeanPlaneCrossing
from pyrugged.line_sensor.sensor_pixel_crossing import SensorPixelCrossing
from pyrugged.los.los_builder import LOSBuilder
from pyrugged.utils.constants import Constants
from pyrugged.utils.coordinates_reader import extract_pv_from_txt, extract_q_from_txt
from pyrugged.utils.math_utils import distance, to_array_v  # pylint: disable=no-name-in-module
from pyrugged.utils.spacecraft_to_observed_body import SpacecraftToObservedBody

init_orekit(use_internal_data=False)


def test_crossing():
    """Crossing test"""

    init_orekit()

    position = Vector3D(1.5, Vector3D.PLUS_I)
    normal = Vector3D.PLUS_I
    fov_center = Vector3D.PLUS_K
    cross = Vector3D.crossProduct(normal, fov_center)

    # Build lists of pixels regularly spread on a perfect plane
    los = []
    for i in range(-1000, 1000):
        alpha = i * 0.17 / 1000
        los.append(Vector3D(float(np.cos(alpha)), fov_center, float(np.sin(alpha)), cross))

    sensor = LineSensor(
        "perfect line",
        LinearLineDatation(AbsoluteDate.J2000_EPOCH, 0.0, 1.0 / 1.5e-3),
        position,
        LOSBuilder(los).build(),
    )

    assert sensor.name == "perfect line"
    assert str(sensor.get_date(0.0)) == str(AbsoluteDate.J2000_EPOCH)
    assert distance(to_array_v(position.toArray()), sensor.position) == pytest.approx(0.0, abs=1.0e-15)

    mean = SensorMeanPlaneCrossing(sensor, create_interpolator(sensor), 0, 2000, True, True, 50, 0.01)

    ref_line = 1200.0
    ref_date = sensor.get_date(ref_line)
    ref_pixel = 1800
    b_2_i = mean.sc_to_body.get_body_to_inertial(ref_date)
    sc_2_i = mean.sc_to_body.get_sc_to_inertial(ref_date)
    sc_2_b = Transform(ref_date, sc_2_i, b_2_i.getInverse())
    p_1 = StaticTransform.cast_(sc_2_b).transformPosition(position)
    p_2 = StaticTransform.cast_(sc_2_b).transformPosition(Vector3D(1.0, position, 1.0e6, los[ref_pixel]))

    line = Line(p_1, p_2, 0.001)
    earth = OneAxisEllipsoid(
        Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
        Constants.WGS84_EARTH_FLATTENING,
        mean.sc_to_body.body_frame,
    )

    ground_point = earth.get_intersection_point(line, to_array_v(p_1.toArray()), mean.sc_to_body.body_frame, ref_date)

    gp_cartesian_x, gp_cartesian_y, gp_cartesian_z = earth.transform_from_point(
        np.array([ground_point[0]]), np.array([ground_point[1]]), np.array([ground_point[2]])
    )

    crossing_result = mean.find(gp_cartesian_x, gp_cartesian_y, gp_cartesian_z)[0]

    assert Vector3D.angle(normal, Vector3D(mean.mean_plane_normal.tolist())) == pytest.approx(0.0, abs=1.0e-15)

    # Find approximately the pixel along this sensor line
    pixel_crossing = SensorPixelCrossing(sensor, mean.mean_plane_normal, crossing_result.target_direction, 50, 0.01)

    pixel = pixel_crossing.locate_pixel(crossing_result.date)
    assert pixel == pytest.approx(ref_pixel, abs=2.0e-3)


def create_interpolator(sensor):
    """Creates interpolator."""

    orbit = CircularOrbit(
        7173352.811913891,
        -4.029194321683225e-4,
        0.0013530362644647786,
        float(np.radians(98.63218182243709)),
        float(np.radians(77.55565567747836)),
        float(np.pi),
        PositionAngleType.TRUE,
        FramesFactory.getEME2000(),
        sensor.get_date(1000),
        Constants.EIGEN5C_EARTH_MU,
    )

    earth = OneAxisEllipsoid(
        Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
        Constants.WGS84_EARTH_FLATTENING,
        FramesFactory.getITRF(IERSConventions.IERS_2010, True),
    )

    min_date = sensor.get_date(0)
    max_date = sensor.get_date(2000)

    pv_txt_file = os.path.join(os.path.dirname(__file__), "../data/ref/line_sensor/testSensorPixelCrossing_pv.txt")
    q_txt_file = os.path.join(os.path.dirname(__file__), "../data/ref/line_sensor/testSensorPixelCrossing_q.txt")

    return SpacecraftToObservedBody(
        orbit.getFrame(),
        earth.body_frame,
        min_date,
        max_date,
        0.01,
        5.0,
        extract_pv_from_txt(pv_txt_file),
        2,
        CartesianDerivativesFilter.USE_P,
        extract_q_from_txt(q_txt_file),
        2,
        AngularDerivativesFilter.USE_R,
    )


if __name__ == "__main__":
    test_crossing()
