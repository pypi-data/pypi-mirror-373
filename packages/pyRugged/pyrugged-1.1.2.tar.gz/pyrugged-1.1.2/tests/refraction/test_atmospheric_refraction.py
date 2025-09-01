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

"""Test of pyrugged Class AtmosphericRefraction"""

# pylint: disable=no-name-in-module, too-many-locals
import os

import numpy as np
import pytest
from org.hipparchus.geometry.euclidean.threed import Rotation, RotationConvention, Vector3D
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import (
    AngularDerivativesFilter,
    CartesianDerivativesFilter,
    TimeStampedAngularCoordinates,
    TimeStampedPVCoordinates,
)

from pyrugged.bodies.body_rotating_frame_id import BodyRotatingFrameId
from pyrugged.bodies.ellipsoid_id import EllipsoidId
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.intersection_algorithm import create_intersection_algorithm
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.line_sensor.linear_line_datation import LinearLineDatation
from pyrugged.location.optical import CorrectionsParams, OpticalLocation
from pyrugged.los.los_builder import LOSBuilder
from pyrugged.model.inertial_frame_id import InertialFrameId
from pyrugged.model.pyrugged_builder import PyRuggedBuilder
from pyrugged.refraction.multi_layer_model import MultiLayerModel
from pyrugged.utils.coordinates_reader import extract_pv_from_txt, extract_q_from_txt
from pyrugged.utils.math_utils import compute_distance_in_meter_from_points
from tests import helpers
from tests.raster.random_landscape_updater import RandomLandscapeUpdater

MARGIN_LINE = 10
DEFAULT_STEP_LINE = 100


def setup_module():
    """
    setup : initVM
    """

    init_orekit()


def init_pyrugged_for_atmospheric_tests(dimension, sensor_name):
    """PyRugged instance initialization."""

    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    # los: swath in the (YZ) plane, looking at 5° roll, 2.6" per pixel

    position = Vector3D(1.5, 0.0, -0.2)
    los = helpers.create_los_perfect_line(
        Rotation(Vector3D.PLUS_I, float(np.radians(5.0)), RotationConvention.VECTOR_OPERATOR).applyTo(Vector3D.PLUS_K),
        Vector3D.PLUS_I,
        float(np.radians((dimension / 2.0) * 2.6 / 3600.0)),
        dimension,
    ).build()

    # With the orbit (795km), the size of the pixel on the ground is around : 10m

    # linear datation model: at reference time we get the middle line, and the rate is one line every 1.5ms
    crossing = AbsoluteDate("2012-01-01T12:30:00.000", TimeScalesFactory.getUTC())
    line_datation = LinearLineDatation(crossing, dimension / 2, 1.0 / 1.5e-3)
    first_line = 0
    last_line = dimension
    line_sensor = LineSensor(sensor_name, line_datation, position, los)
    min_date = line_sensor.get_date(first_line).shiftedBy(-1.0)
    max_date = line_sensor.get_date(last_line).shiftedBy(1.0)

    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/refraction/testAtmosphericRefraction_pv.txt"
    )
    q_txt_file_path = os.path.join(os.path.dirname(__file__), "../data/ref/refraction/testAtmosphericRefraction_q.txt")

    pv_list = extract_pv_from_txt(pv_txt_file_path)
    q_list = extract_q_from_txt(q_txt_file_path)

    builder = PyRuggedBuilder()
    builder.set_ellipsoid(
        new_ellipsoid=None, ellipsoid_id=EllipsoidId.WGS84, body_rotating_frame_id=BodyRotatingFrameId.ITRF
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

    updater = RandomLandscapeUpdater(3000.0, 6000.0, 0.1, 1234, float(np.radians(2.0)), 257)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)
    location = OpticalLocation(rugged, intersection_algorithm)
    return rugged, location


def test_atmospheric_refraction_correction():
    """Test for atmospheric refraction correction."""

    sensor_name = "line"
    dimension = 4000

    rugged, location = init_pyrugged_for_atmospheric_tests(dimension, sensor_name)

    line_sensor = rugged.get_sensor(sensor_name)
    min_line = float(np.floor(line_sensor.get_line(rugged.min_date)))
    max_line = float(np.ceil(line_sensor.get_line(rugged.max_date)))

    pixel_threshold = 1.0e-3
    line_threshold = 1.02e-2
    epsilon_pixel = pixel_threshold
    epsilon_line = line_threshold
    earth_radius = rugged.ellipsoid.equatorial_radius

    # Direct loc on a line WITHOUT and WITH atmospheric correction
    # ============================================================

    chosen_line = 200.0
    gp_without_atmospheric_refraction_correction = location.direct_location_of_sensor_line(chosen_line)

    # Defines atmospheric refraction model (with the default multi layers model)
    atmospheric_refraction = MultiLayerModel(rugged.ellipsoid)
    pixel_step = 100
    line_step = 100
    atmospheric_refraction.set_grid_steps(pixel_step, line_step)

    # Build Rugged with atmospheric refraction model
    correction_params_with_refraction = CorrectionsParams(False, False, atmospheric_refraction)
    location.corrections_params = correction_params_with_refraction

    gp_with_atmospheric_refraction_correction = location.direct_location_of_sensor_line(chosen_line)

    # Check the shift on the ground due to atmospheric correction
    for index, (_, _, alt_corr) in enumerate(gp_with_atmospheric_refraction_correction):
        lon, lat, alt = gp_without_atmospheric_refraction_correction[index]
        current_radius = earth_radius + (alt_corr + alt) / 2.0

        distance = compute_distance_in_meter_from_points(
            current_radius,
            gp_with_atmospheric_refraction_correction[index],
            gp_without_atmospheric_refraction_correction[index],
        )

        # Check if the distance is not 0 and < 2m
        assert distance > 0.0
        assert distance < 2.0

    # Inverse loc WITH atmospheric correction
    # =======================================

    latitudes = []
    longitudes = []
    altitudes = []
    for lon_corr, lat_corr, alt_corr in gp_with_atmospheric_refraction_correction:
        latitudes.append(lat_corr)
        longitudes.append(lon_corr)
        altitudes.append(alt_corr)

    sensor_pixel_reverse_with = location.inverse_location(min_line, max_line, latitudes, longitudes, altitudes)

    for index, _ in enumerate(gp_with_atmospheric_refraction_correction):
        # To check if we go back to the initial point when taking the geodetic point with atmospheric correction
        # sensor_pixel_reverse_with = location.inverse_location(min_line, max_line, [lat_corr], [lon_corr], [alt_corr])

        if sensor_pixel_reverse_with != ([None], [None]):
            assert sensor_pixel_reverse_with[1][index] == pytest.approx(index, abs=epsilon_pixel)
            assert sensor_pixel_reverse_with[0][index] == pytest.approx(chosen_line, abs=epsilon_line)

        else:
            pytest.fail(
                f'{"Inverse location failed for pixel "}{index}'
                f'{" with atmospheric refraction correction for geodetic point computed with"}'
            )

    # For test coverage
    dummy_lat = gp_with_atmospheric_refraction_correction[0][1] + float(np.pi) / 4.0
    dummy_lon = gp_with_atmospheric_refraction_correction[0][0] - float(np.pi) / 4.0
    dummy_gp = np.array([dummy_lat, dummy_lon, 0.0])

    try:
        location.inverse_location(min_line, max_line, [dummy_gp[0]], [dummy_gp[1]], [dummy_gp[2]])
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.INVALID_RANGE_FOR_LINES.value.format(min_line, max_line, "")

    try:
        lon, lat, alt = gp_with_atmospheric_refraction_correction[0]

        location.inverse_location(
            210,
            max_line,
            [lat],
            [lon],
            [alt],
        )
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.INVALID_RANGE_FOR_LINES.value.format(210, max_line, "")

    try:
        lon, lat, alt = gp_with_atmospheric_refraction_correction[0]

        location.inverse_location(
            min_line,
            190,
            [lat],
            [lon],
            [alt],
        )
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.INVALID_RANGE_FOR_LINES.value.format(min_line, 190, "")


def test_inverse_location_margin():
    """Test for Rugged issue #391."""

    start = AbsoluteDate.ARBITRARY_EPOCH
    end = start.shiftedBy(10.0)
    middle = start.shiftedBy(end.durationFrom(start) / 2.0)

    h = 500e3
    position = Vector3D(6378137.0 + h, 0.0, 0.0)
    velocity = Vector3D.ZERO

    pv_list = []
    pv_list.append(TimeStampedPVCoordinates(start, position, velocity))
    pv_list.append(TimeStampedPVCoordinates(end, position, velocity))
    rotation = Rotation(Vector3D.MINUS_I, Vector3D.MINUS_K, Vector3D.PLUS_K, Vector3D.PLUS_I)
    attitude = TimeStampedAngularCoordinates(middle, rotation, Vector3D.PLUS_I.scalarMultiply(0.1), Vector3D.ZERO)

    q_list = []
    q_list.append(attitude.shiftedBy(start.durationFrom(attitude.getDate())))
    q_list.append(attitude)
    q_list.append(attitude.shiftedBy(end.durationFrom(attitude.getDate())))

    builder = PyRuggedBuilder()
    builder.set_ellipsoid(
        new_ellipsoid=None, ellipsoid_id=EllipsoidId.WGS84, body_rotating_frame_id=BodyRotatingFrameId.ITRF
    )
    builder.set_time_span(start, end, 1e-3, 1e-3)
    builder.set_trajectory(
        pv_list,
        2,
        CartesianDerivativesFilter.USE_PV,
        q_list,
        2,
        AngularDerivativesFilter.USE_R,
        inertial_frame_id=InertialFrameId.EME2000,
    )

    n_pixels = 1000
    i_fov = 1e-6
    vector_list = []
    for index in range(n_pixels):
        center = n_pixels / 2.0
        los = (index - center) * i_fov
        vector_list.append(Vector3D(los, 0.0, 1.0))

    los_vector = LOSBuilder(vector_list).build()
    line_datation = LinearLineDatation(middle, 0, 1000)
    line_sensor = LineSensor("line", line_datation, Vector3D.ZERO, los_vector)

    builder.add_sensor(line_sensor)
    rugged = builder.build()

    intersection_algorithm = create_intersection_algorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)
    atmospheric_refraction = MultiLayerModel(rugged.ellipsoid)
    correction_params = CorrectionsParams(True, True, atmospheric_refraction)

    location = OpticalLocation(rugged, intersection_algorithm, correction_params)
    lon, lat, alt = location.direct_location([1000], [500])

    max_line = 4999
    try:
        location.inverse_location(0, max_line, np.array(lat), np.array(lon), np.array(alt))
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        pixel = -0.81
        invloc_margin = atmospheric_refraction.atmospheric_params.invloc_margin
        assert str(pre) == PyRuggedMessages.SENSOR_PIXEL_NOT_FOUND_IN_PIXELS_LINE.value.format(
            pixel, -invloc_margin, invloc_margin + 999, invloc_margin
        )

    atmospheric_refraction.atmospheric_params.invloc_margin = 0.81
    location = OpticalLocation(rugged, intersection_algorithm, correction_params)
    line, pixel = location.inverse_location(0, max_line, np.array(lat), np.array(lon), np.array(alt))
    assert line[0] is not None
    assert pixel[0] is not None


def test_refraction_and_light_time_correction():
    """Test for issue #117: Correct light time bug."""

    sensor_name = "line"
    dimension = 4000

    rugged, location = init_pyrugged_for_atmospheric_tests(dimension, sensor_name)

    # Build Rugged without atmospheric refraction but with light time correction
    correction_params_with_light_time_wo_refaction = CorrectionsParams(True, False, None)
    location.corrections_params = correction_params_with_light_time_wo_refaction

    # Defines atmospheric refraction model (with the default multi layers model)
    atmospheric_refraction = MultiLayerModel(rugged.ellipsoid)
    pixel_step = 100
    line_step = 100
    atmospheric_refraction.set_grid_steps(pixel_step, line_step)

    # Compare direct loc on a line :
    # * with atmospheric refraction, WITHOUT and WITH light time correction:
    #   distance on ground must be not null and < 1.2 m (max shift at the equator for orbit at 800km)
    # * with light time correction, WITHOUT and WITH atmospheric refraction
    #   distance on ground must be not null and < 2 m (max shift due to atmospheric refraction)
    # =========================================================================================
    chosen_line = 200.0

    gp_with_lighttime_without_refraction = location.direct_location_of_sensor_line(chosen_line)

    correction_params_wo_light_time_with_refaction = CorrectionsParams(False, False, atmospheric_refraction)
    location.corrections_params = correction_params_wo_light_time_with_refaction
    gp_without_lighttime = location.direct_location_of_sensor_line(chosen_line)

    correction_params_with_light_time_with_refaction = CorrectionsParams(True, False, atmospheric_refraction)
    location.corrections_params = correction_params_with_light_time_with_refaction
    gp_with_lighttime = location.direct_location_of_sensor_line(chosen_line)

    earth_radius = rugged.ellipsoid.equatorial_radius

    for index, (_, _, alt_corr) in enumerate(gp_with_lighttime):
        alt = gp_without_lighttime[index][2]
        current_radius = earth_radius + (alt_corr + alt) / 2.0

        # Compute distance between point (with atmospheric refraction) with light time correction and without
        distance = compute_distance_in_meter_from_points(
            current_radius,
            gp_with_lighttime[index],
            gp_without_lighttime[index],
        )

        # Check if the distance is between 1.0 and < 1.2m (at equator max of shift)
        assert distance > 1.0
        assert distance <= 1.2

        # Compute distance between point (with light time correction) with refraction and without refraction
        distance = compute_distance_in_meter_from_points(
            current_radius,
            gp_with_lighttime[index],
            gp_with_lighttime_without_refraction[index],
        )

        # Check if the distance is not 0  and < 2m
        assert distance > 0.1
        assert distance < 2.0


def test_bad_config():
    """Test bad configuration."""

    dimension = 400

    los = LOSBuilder([None] * dimension).build()
    line_sensor = LineSensor("line", None, Vector3D.ZERO, los)

    # Defines atmospheric refraction model (with the default multi layers model)
    atmospheric_refraction = MultiLayerModel(None)

    # Check the context
    atmospheric_refraction.set_grid_steps(100, 100)
    atmospheric_refraction.configure_correction_grid(line_sensor, 0, 300)
    assert not atmospheric_refraction.is_same_context("other sensor", 0, 300)
    assert not atmospheric_refraction.is_same_context("line", 42, 300)
    assert not atmospheric_refraction.is_same_context("line", 0, 42)

    # Check the test of validity of min / max line vs line step
    try:
        atmospheric_refraction.set_grid_steps(100, 100)
        atmospheric_refraction.configure_correction_grid(line_sensor, 0, 100)
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        info = f'{": (max_line - min_line + 1 - 2*"}{MARGIN_LINE}{") < 2*"}{DEFAULT_STEP_LINE}'
        assert str(pre) == PyRuggedMessages.INVALID_RANGE_FOR_LINES.value.format(0, 100, info)

    # Bad pixel step
    try:
        atmospheric_refraction.set_grid_steps(-5, 100)
        atmospheric_refraction.configure_correction_grid(line_sensor, 0, 100)
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        reason = f'{" pixel_step <= 0"}'
        assert str(pre) == PyRuggedMessages.INVALID_STEP.value.format(-5, reason)

    # Bad line step
    try:
        atmospheric_refraction.set_grid_steps(10, -42)
        atmospheric_refraction.configure_correction_grid(line_sensor, 0, 100)
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        reason = f'{" line_step <= 0"}'
        assert str(pre) == PyRuggedMessages.INVALID_STEP.value.format(-42, reason)
