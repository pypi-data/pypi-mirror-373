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

"""Test of pyrugged Class SpacecraftToObservedBody"""

# pylint: disable=redefined-outer-name

import os

import numpy as np
import pytest
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.frames import FramesFactory, StaticTransform
from org.orekit.time import AbsoluteDate
from org.orekit.utils import AngularDerivativesFilter, CartesianDerivativesFilter

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.line_sensor.linear_line_datation import LinearLineDatation
from pyrugged.los.los_builder import LOSBuilder
from pyrugged.utils.constants import Constants
from pyrugged.utils.coordinates_reader import extract_pv_from_txt, extract_q_from_txt
from pyrugged.utils.spacecraft_to_observed_body import SpacecraftToObservedBody
from tests.helpers import create_orbit

init_orekit(use_internal_data=False)


@pytest.fixture
def orbit():
    """Orbit to be used."""

    return create_orbit(Constants.EIGEN5C_EARTH_MU)


@pytest.fixture
def sensor():
    """Sensor to be used."""

    # Build lists of pixels regularly spread on a perfect plane
    position = Vector3D(1.5, Vector3D.PLUS_I)
    normal = Vector3D.PLUS_I
    fov_center = Vector3D.PLUS_K
    cross = Vector3D.crossProduct(normal, fov_center)

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

    return sensor


# pylint: disable=unused-variable
def do_test_out_of_time_range(sensor, earth, pv_txt_file_path, q_txt_file_path):
    """Test out of time range"""

    min_sensor_date = sensor.get_date(0)
    max_sensor_date = sensor.get_date(2000)

    pv_list = extract_pv_from_txt(pv_txt_file_path)
    q_list = extract_q_from_txt(q_txt_file_path)

    try:
        sc_to_body = SpacecraftToObservedBody(  # noqa:F841
            FramesFactory.getEME2000(),
            earth.body_frame,
            min_sensor_date,
            max_sensor_date,
            0.01,
            5.0,
            pv_list,
            8,
            CartesianDerivativesFilter.USE_PV,
            q_list,
            2,
            AngularDerivativesFilter.USE_R,
        )

        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.OUT_OF_TIME_RANGE.value.format(
            min_sensor_date,
            pv_list[0].getDate(),
            pv_list[-1].getDate(),
        )


def test_transform_position(sensor, earth):
    """Test position transformation"""

    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBody_pv_0_0.txt"
    )
    q_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBody_q_0_0.txt"
    )

    min_sensor_date = sensor.get_date(0)
    max_sensor_date = sensor.get_date(2000)

    pv_list = extract_pv_from_txt(pv_txt_file_path)
    q_list = extract_q_from_txt(q_txt_file_path)

    sc_to_body = SpacecraftToObservedBody(
        FramesFactory.getEME2000(),
        earth.body_frame,
        min_sensor_date,
        max_sensor_date,
        0.01,
        5.0,
        pv_list,
        8,
        CartesianDerivativesFilter.USE_PV,
        q_list,
        2,
        AngularDerivativesFilter.USE_R,
    )

    mid_sensor_date = sensor.get_date(1000)

    # From spacecraft to inertial
    sc_to_inert = sc_to_body.get_sc_to_inertial(mid_sensor_date)
    # From inertial to body
    inert_to_body = sc_to_body.get_inertial_to_body(mid_sensor_date)

    # Compute spacecraft velocity in inertial frame
    # spacecraft_velocity = sc_to_inert.transformPVCoordinates(PVCoordinates.ZERO).getVelocity()

    # Compute sensor position in inertial frame
    # TBN: for simplicity, due to the size of sensor, we consider each pixel to be at sensor position
    p_inert = StaticTransform.cast_(sc_to_inert).transformPosition(Vector3D(sensor.position.tolist()))

    # Compute DEM intersection without light time correction
    p_body = StaticTransform.cast_(inert_to_body).transformPosition(p_inert)

    assert p_body.getX() == pytest.approx(5666161.84187, abs=1.0e-4)
    assert p_body.getY() == pytest.approx(-1698531.94598, abs=1.0e-4)
    assert p_body.getZ() == pytest.approx(4043889.63805, abs=1.0e-4)


def test_sc_to_body_out_of_time_range_1(sensor, earth):
    """Test bad configuration"""

    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBody_pv_10_1.txt"
    )
    q_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBody_q_-1_1.txt"
    )

    do_test_out_of_time_range(sensor, earth, pv_txt_file_path, q_txt_file_path)
