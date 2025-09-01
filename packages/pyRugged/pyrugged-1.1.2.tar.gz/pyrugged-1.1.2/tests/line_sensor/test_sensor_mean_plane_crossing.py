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

"""Test of pyrugged Class SensorMeanPlaneCrossing"""

import math
import os

# pylint: disable=too-many-locals
import numpy as np
import pytest
from org.hipparchus.geometry import Vector
from org.hipparchus.geometry.euclidean.threed import Line, Vector3D
from org.hipparchus.random import Well19937a
from org.orekit.frames import FramesFactory, StaticTransform, Transform
from org.orekit.orbits import CircularOrbit, PositionAngleType
from org.orekit.time import AbsoluteDate
from org.orekit.utils import AngularDerivativesFilter, CartesianDerivativesFilter, IERSConventions, PVCoordinates

from pyrugged.bodies.one_axis_ellipsoid import OneAxisEllipsoid
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.line_sensor.linear_line_datation import LinearLineDatation
from pyrugged.line_sensor.sensor_mean_plane_crossing import SensorMeanPlaneCrossing
from pyrugged.los.los_builder import LOSBuilder
from pyrugged.utils.constants import Constants
from pyrugged.utils.coordinates_reader import extract_pv_from_txt, extract_q_from_txt
from pyrugged.utils.math_utils import distance, get_norm, to_array_v  # pylint: disable=no-name-in-module
from pyrugged.utils.spacecraft_to_observed_body import SpacecraftToObservedBody


def setup_module():
    """
    setup : initVM
    """

    init_orekit(use_internal_data=True)


def test_slow_find():
    """Test SensorMeanPlaneCrossing.slow_find()"""

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
    # assert sensor.get_date(0.0) == AbsoluteDate.J2000_EPOCH
    assert distance(to_array_v(position.toArray()), sensor.position) == pytest.approx(0.0, abs=1.0e-6)

    mean = SensorMeanPlaneCrossing(sensor, create_interpolator(sensor), 0, 2000, True, True, 50, 1.0e-6)

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
    gp_cartesian_coord = earth.transform_from_point(
        np.array([ground_point[0]]), np.array([ground_point[1]]), np.array([ground_point[2]])
    )
    gp_cartesian = Vector3D(float(gp_cartesian_coord[0]), float(gp_cartesian_coord[1]), float(gp_cartesian_coord[2]))
    result = mean.find(gp_cartesian_coord[0], gp_cartesian_coord[1], gp_cartesian_coord[2])[0]

    slow_result = mean.slow_find(PVCoordinates(gp_cartesian, Vector3D.ZERO), 400.0)

    assert result.line == pytest.approx(slow_result.line, abs=1.0e-10)


def create_interpolator(sensor):
    """Creates interpolator"""

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

    pv_txt_file = os.path.join(os.path.dirname(__file__), "../data/ref/line_sensor/testLinesensor_pv.txt")
    q_txt_file = os.path.join(os.path.dirname(__file__), "../data/ref/line_sensor/testLinesensor_q.txt")

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


def test_perfect_line():
    """Test perfect line"""

    init_orekit()

    position = Vector3D(1.5, Vector3D.PLUS_I)
    normal = Vector3D.PLUS_I
    fov_center = Vector3D.PLUS_K
    cross = Vector3D.crossProduct(normal, fov_center)

    # Build lists of pixels regularly spread on a perfect plane
    los = []
    for index in range(-1000, 1001):
        alpha = index * 0.17 / 1000
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

    assert Vector3D.angle(normal, Vector3D(mean.mean_plane_normal.tolist())) == pytest.approx(0.0, abs=1.0e-15)


def test_noisy_line():
    """Test noisy line"""

    random = Well19937a(1234)
    position = Vector3D(1.5, Vector3D.PLUS_I)
    normal = Vector3D.PLUS_I
    fov_center = Vector3D.PLUS_K
    cross = Vector3D.crossProduct(normal, fov_center)

    # Build lists of pixels regularly spread on a perfect plane
    los = []
    for index in range(-1000, 1000):
        alpha = index * 0.17 / 10 + 1.0e-5 * random.nextDouble()
        delta = 1.0e-5 * random.nextDouble()
        c_a = float(np.cos(alpha))
        s_a = float(np.sin(alpha))
        c_d = float(np.cos(delta))
        s_d = float(np.sin(delta))

        los.append(Vector3D(c_a * c_d, fov_center, s_a * c_d, cross, s_d, normal))

    sensor = LineSensor(
        "noisy line", LinearLineDatation(AbsoluteDate.J2000_EPOCH, 0.0, 1.0 / 1.5e-3), position, LOSBuilder(los).build()
    )

    assert sensor.name == "noisy line"
    assert str(sensor.get_date(0.0)) == str(AbsoluteDate.J2000_EPOCH)
    assert distance(to_array_v(position.toArray()), sensor.position) == pytest.approx(0.0, abs=1.0e-5)

    mean = SensorMeanPlaneCrossing(sensor, create_interpolator(sensor), 0, 2000, True, True, 50, 0.01)

    assert Vector3D.angle(normal, Vector3D(mean.mean_plane_normal.tolist())) == pytest.approx(0.0, abs=8.0e-7)


def test_derivative_without_correction():
    """Test derivative without correction"""

    do_test_derivative(False, False, 3.3e-11)


def test_derivative_light_time_correction():
    """Test derivative whith light time correction"""

    do_test_derivative(True, False, 2.4e-7)


def test_derivative_aberration_of_light_correction():
    """Test derivative with aberration of ligth correction"""

    do_test_derivative(False, True, 1.1e-7)


def test_derivative_with_all_corrections():
    """Test derivative with all corrections"""

    do_test_derivative(True, True, 1.4e-7)


def do_test_derivative(light_time_correction, aberration_of_light_correction, tol):
    """Test derivative"""

    position = Vector3D(1.5, Vector3D.PLUS_I)
    normal = Vector3D.PLUS_I
    fov_center = Vector3D.PLUS_K
    cross = Vector3D.crossProduct(normal, fov_center)

    # Build lists of pixels regularly spread on a perfect plane
    los = []
    for index in range(-1000, 1000):
        alpha = index * 0.17 / 1000
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

    mean = SensorMeanPlaneCrossing(
        sensor, create_interpolator(sensor), 0, 2000, light_time_correction, aberration_of_light_correction, 50, 1.0e-6
    )

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

    gp_cartesian_coord = earth.transform_from_point(
        np.array([ground_point[0]]), np.array([ground_point[1]]), np.array([ground_point[2]])
    )
    gp_cartesian = Vector3D(float(gp_cartesian_coord[0]), float(gp_cartesian_coord[1]), float(gp_cartesian_coord[2]))
    result = mean.find(gp_cartesian_coord[0], gp_cartesian_coord[1], gp_cartesian_coord[2])[0]

    if light_time_correction:
        # Applying corrections shifts the point with respect
        # to the reference result computed from a simple model above
        assert result.line - ref_line > 0.02

    elif aberration_of_light_correction:
        # Applying corrections shifts the point with respect
        # to the reference result computed from a simple model above
        assert result.line - ref_line > 1.9

    else:
        # The simple model from which reference results have been compute applies here
        assert result.line == pytest.approx(ref_line, abs=5.0e-11 * ref_line)
        assert result.date.durationFrom(ref_date) == pytest.approx(0.0, abs=1.0e-9)
        assert Vector3D.angle(los[ref_pixel], Vector3D(result.target_direction.tolist())) == pytest.approx(
            0.0, abs=5.4e-15
        )

    delta_l = 0.5
    b_2_sc_plus = sc_2_b.getInverse().shiftedBy(delta_l / sensor.get_rate(ref_line))
    dir_plus = Vector.cast_(
        StaticTransform.cast_(b_2_sc_plus).transformPosition(gp_cartesian).subtract(position)
    ).normalize()
    b_2_sc_minus = sc_2_b.getInverse().shiftedBy(-delta_l / sensor.get_rate(ref_line))
    dir_minus = Vector.cast_(
        StaticTransform.cast_(b_2_sc_minus).transformPosition(gp_cartesian).subtract(position)
    ).normalize()
    dir_der = to_array_v(Vector3D(1.0 / (2 * delta_l), dir_plus.subtract(dir_minus)).toArray())

    assert distance(result.target_direction_derivative, dir_der) == pytest.approx(0.0, abs=tol * get_norm(dir_der))

    try:
        mean.sc_to_body.get_body_to_inertial(ref_date.shiftedBy(-Constants.JULIAN_CENTURY))
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.OUT_OF_TIME_RANGE.value.format(
            ref_date.shiftedBy(-Constants.JULIAN_CENTURY),
            mean.sc_to_body.min_date,
            mean.sc_to_body.max_date,
        )

    try:
        mean.sc_to_body.get_body_to_inertial(ref_date.shiftedBy(Constants.JULIAN_CENTURY))
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.OUT_OF_TIME_RANGE.value.format(
            ref_date.shiftedBy(Constants.JULIAN_CENTURY),
            mean.sc_to_body.min_date,
            mean.sc_to_body.max_date,
        )

    assert mean.sc_to_body.get_body_to_inertial(ref_date) is not None


def test_use_guess_start_line():
    """Test SensorMeanPlaneCrossing.guess_start_line()"""

    init_orekit()

    position = Vector3D(1.5, Vector3D.PLUS_I)
    normal = Vector3D.PLUS_I
    fov_center = Vector3D.PLUS_K
    cross = Vector3D.crossProduct(normal, fov_center)

    # Build lists of pixels regularly spread on a perfect plane
    los = []
    for i in range(-1000, 1000):
        alpha = i * 0.17 / 1000
        los.append(Vector3D(math.cos(alpha), fov_center, math.sin(alpha), cross))

    sensor = LineSensor(
        "perfect line",
        LinearLineDatation(AbsoluteDate.J2000_EPOCH, 0.0, 1.0 / 1.5e-3),
        position,
        LOSBuilder(los).build(),
    )

    assert sensor.name == "perfect line"
    # assert sensor.get_date(0.0) == AbsoluteDate.J2000_EPOCH
    assert distance(to_array_v(position.toArray()), sensor.position) == pytest.approx(0.0, abs=1.0e-6)

    mean = SensorMeanPlaneCrossing(sensor, create_interpolator(sensor), 0, 2000, True, True, 50, 1.0e-6)

    # create no reg references
    ref_crossing_line = [
        1201.99996125136,
        1261.999953344315,
        1321.9999456122462,
        1381.99996739669,
        1441.9999595323034,
        1501.999981080891,
        1561.9999730840238,
    ]

    ref_target = [
        Vector3D(5926224.4818808595, -2357932.676322251, -25379.793503793604),
        Vector3D(5926173.715041195, -2358053.800965174, -25969.5292614004),
        Vector3D(5926122.894796946, -2358174.9039920354, -26559.2678601558),
        Vector3D(5926072.021758787, -2358295.983944975, -27149.0024878673),
        Vector3D(5926021.095491362, -2358417.041863439, -27738.7380093226),
        Vector3D(5925970.115821087, -2358538.0781595283, -28328.4763534711),
        Vector3D(5925919.08350889, -2358659.091025565, -28918.2089028326),
    ]
    ref_target_direction = [
        Vector3D(0.0, -0.1355813364, 0.9907662193),
        Vector3D(0.0, -0.1355813367, 0.9907662192),
        Vector3D(0.0, -0.135581337, 0.9907662192),
        Vector3D(0.0, -0.1355813365, 0.9907662192),
        Vector3D(0.0, -0.1355813368, 0.9907662192),
        Vector3D(0.0, -0.1355813362, 0.9907662193),
        Vector3D(0.0, -0.1355813365, 0.9907662192),
    ]
    ref_target_direction_derivative = [
        Vector3D(-0.0000125772, 0.0000000025, 0.0000000003),
        Vector3D(-0.0000125772, 0.0000000025, 0.0000000003),
        Vector3D(-0.0000125773, 0.0000000025, 0.0000000003),
        Vector3D(-0.0000125771, 0.0000000025, 0.0000000003),
        Vector3D(-0.0000125772, 0.0000000025, 0.0000000003),
        Vector3D(-0.000012577, 0.0000000025, 0.0000000003),
        Vector3D(-0.0000125771, 0.0000000025, 0.0000000003),
    ]

    def check_vector3d(vector_1: Vector3D, vector_2: Vector3D):
        """
        Assert that 2 Vector3D are equal
        """
        assert vector_1[0] == pytest.approx(vector_2[0], abs=2.0e-6)
        assert vector_1[1] == pytest.approx(vector_2[1], abs=2.0e-6)
        assert vector_1[2] == pytest.approx(vector_2[2], abs=5.0e-5)

    ref_nb = 0
    # test guess_start_line function by finding several ground points
    for ref_line in range(1200, 1600, 60):
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

        ground_point = earth.get_intersection_point(
            line, to_array_v(p_1.toArray()), mean.sc_to_body.body_frame, ref_date
        )
        gp_cartesian_coord = earth.transform_from_point(
            np.array([ground_point[0]]), np.array([ground_point[1]]), np.array([ground_point[2]])
        )

        result = mean.find(gp_cartesian_coord[0], gp_cartesian_coord[1], gp_cartesian_coord[2])[0]

        assert result.line == pytest.approx(ref_crossing_line[ref_nb], abs=3.0e-5)
        check_vector3d(result.target, to_array_v(ref_target[ref_nb].toArray()))
        check_vector3d(result.target_direction, to_array_v(ref_target_direction[ref_nb].toArray()))
        check_vector3d(
            result.target_direction_derivative, to_array_v(ref_target_direction_derivative[ref_nb].toArray())
        )
        ref_nb += 1
