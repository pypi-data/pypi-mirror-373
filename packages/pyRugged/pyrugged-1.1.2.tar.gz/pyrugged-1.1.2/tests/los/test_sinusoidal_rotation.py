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

"""pyrugged Class SinusoidalRotationTest"""


import random

import numpy as np
import pytest
from org.hipparchus.geometry.euclidean.threed import Rotation, RotationConvention, Vector3D
from org.hipparchus.random import UncorrelatedRandomVectorGenerator, UniformRandomGenerator, Well19937a
from org.orekit.time import AbsoluteDate

# vm init before import for PolynomialRotation
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.los.los_builder import LOSBuilder
from pyrugged.los.sinusoidal_rotation import SinusoidalRotation


def setup_module():
    init_orekit(use_internal_data=False)


@pytest.fixture(name="raw")
def fixture_raw():
    """Raw list of vectors for LOS builder"""

    normal = Vector3D.PLUS_I
    fov_center = Vector3D.PLUS_K
    cross = Vector3D.crossProduct(normal, fov_center)

    raw_los = []
    for i in range(-100, 100):
        alpha = i * 0.17 / 1000
        raw_los.append(Vector3D(float(np.cos(alpha)), fov_center, float(np.sin(alpha)), cross))

    return raw_los


@pytest.fixture(name="refdate")
def fixture_refdate():
    """Phase parameter for SinusoidalRotation"""
    return AbsoluteDate.J2000_EPOCH


@pytest.mark.parametrize("amplitude", [0, 1e-4, 1, 10])
@pytest.mark.parametrize("frequency", [1, 10, 20, 40])
@pytest.mark.parametrize("phase", [0, np.pi / 4, np.pi / 2, np.pi])
def test_identity(raw, refdate, amplitude, frequency, phase):
    """Testing with identity transformation."""

    rng = UniformRandomGenerator(Well19937a(100))
    rvg = UncorrelatedRandomVectorGenerator(3, rng)

    period = 1 / frequency
    step = period / 99
    time = np.arange(0, period + step, step)  # list of 100 values unifomited repartion around a period of the sinusoide

    instant = time[random.randint(0, 99)]

    builder = LOSBuilder(raw)
    builder.add_los_transform(
        SinusoidalRotation("identity", Vector3D(rvg.nextVector()), refdate, amplitude * 0, frequency, phase)
    )

    tdl = builder.build()
    for index, raw_value in enumerate(raw):
        assert Vector3D.distance(
            raw_value, Vector3D(tdl.get_los(index, refdate.shiftedBy(float(instant))).tolist())
        ) == pytest.approx(0.0, abs=1.0e-12)

    assert len(tdl.get_parameters_drivers()) == 3
    assert tdl.get_parameters_drivers()[0].name == "identity_amplitude"
    assert tdl.get_parameters_drivers()[1].name == "identity_frequency"
    assert tdl.get_parameters_drivers()[2].name == "identity_phase"


@pytest.mark.parametrize("amplitude", [0, 1e-4, 1, 10])
@pytest.mark.parametrize("frequency", [1, 10, 20, 40])
@pytest.mark.parametrize("phase", [0, np.pi / 4, np.pi / 2, np.pi])
def test_phase_opposition(raw, refdate, amplitude, frequency, phase):
    """Testing with destructives interferences."""

    rng = UniformRandomGenerator(Well19937a(100))
    rvg = UncorrelatedRandomVectorGenerator(3, rng)

    period = 1 / frequency
    step = period / 99
    time = np.arange(0, period + step, step)

    for instant in time:
        axis = Vector3D(rvg.nextVector())

        builder0 = LOSBuilder(raw)
        builder0.add_los_transform(SinusoidalRotation("phase0", axis, refdate, amplitude, frequency, phase))
        builder0.add_los_transform(SinusoidalRotation("phase+pi", axis, refdate, amplitude, frequency, phase + np.pi))
        tdl = builder0.build()

        for index, raw_value in enumerate(raw):
            assert Vector3D.distance(
                raw_value, Vector3D(tdl.get_los(index, refdate.shiftedBy(float(instant))).tolist())
            ) == pytest.approx(0.0, abs=1.0e-12)


@pytest.mark.parametrize("amplitude", [0, 1e-4, 1, 10])
@pytest.mark.parametrize("frequency", [1, 10, 20, 40])
@pytest.mark.parametrize("phase", [0, np.pi / 4, np.pi / 2, np.pi])
def test_real_value(raw, refdate, amplitude, frequency, phase):
    """Testing the value of the rotation."""

    axis = Vector3D.PLUS_I

    period = 1 / frequency
    step = period / 99
    time = np.arange(0, period + step, step)

    for instant in time:
        builder0 = LOSBuilder(raw)
        builder0.add_los_transform(SinusoidalRotation("real_value", axis, refdate, amplitude, frequency, phase))
        tdl = builder0.build()

        angle = float(amplitude * np.sin(2 * np.pi * frequency * instant + phase))
        angle = abs(angle % (2 * np.pi))

        rot = Rotation(axis, angle, RotationConvention.VECTOR_OPERATOR)

        # 2 ways to evaluate de real value
        for index, raw_value in enumerate(raw):
            if np.pi < angle <= 2 * np.pi:  # for th 2 mesurement to mesure the same angle not the complementary one
                assert abs(
                    2 * np.pi
                    - Vector3D.angle(
                        Vector3D(tdl.get_los(index, refdate.shiftedBy(float(instant))).tolist()), raw_value
                    )
                ) == pytest.approx(angle, abs=1.0e-12)
            else:
                assert abs(
                    Vector3D.angle(Vector3D(tdl.get_los(index, refdate.shiftedBy(float(instant))).tolist()), raw_value)
                ) == pytest.approx(angle, abs=1.0e-12)
            assert Vector3D.distance(
                rot.applyTo(raw_value), Vector3D(tdl.get_los(index, refdate.shiftedBy(float(instant))).tolist())
            ) == pytest.approx(0.0, abs=1.0e-12)


@pytest.mark.parametrize("amplitude", [0, 1e-4, 1, 10])
@pytest.mark.parametrize("frequency", [1, 10, 20, 40])
@pytest.mark.parametrize("phase", [0, np.pi / 4, np.pi / 2, np.pi])
def test_driver(raw, refdate, amplitude, frequency, phase):
    """Testing drivers."""

    rng = UniformRandomGenerator(Well19937a(100))
    rvg = UncorrelatedRandomVectorGenerator(3, rng)

    period = 1 / frequency
    step = period / 99
    time = np.arange(0, period + step, step)  # list of 100 values unifomited repartion around a period of the sinusoide

    for instant in time:
        builder = LOSBuilder(raw)
        builder.add_los_transform(
            SinusoidalRotation("driver", Vector3D(rvg.nextVector()), refdate, amplitude, frequency, phase)
        )

        tdl = builder.build()

        drivers = tdl.get_parameters_drivers()
        assert len(drivers) == 3

        driver_1 = drivers[0]
        driver_2 = drivers[1]
        driver_3 = drivers[2]

        assert driver_1.name == "driver_amplitude"
        assert driver_1.min_value == float("inf") or driver_1.min_value == float("-inf")
        assert driver_1.min_value < 0
        assert driver_1.max_value == float("inf") or driver_1.max_value == float("-inf")
        assert driver_1.max_value > 0
        assert driver_1.value == pytest.approx(amplitude, abs=2.0e-15)

        assert driver_2.name == "driver_frequency"
        assert driver_2.min_value == float("inf") or driver_2.min_value == float("-inf")
        assert driver_2.min_value < 0
        assert driver_2.max_value == float("inf") or driver_2.max_value == float("-inf")
        assert driver_2.max_value > 0
        assert driver_2.value == pytest.approx(frequency, abs=2.0e-15)

        assert driver_3.name == "driver_phase"
        assert driver_3.min_value == float(2 * np.pi) or driver_3.min_value == float(-2 * np.pi)
        assert driver_3.min_value < 2 * np.pi
        assert driver_3.max_value == float(2 * np.pi) or driver_3.max_value == float(-2 * np.pi)
        assert driver_3.max_value > -2 * np.pi
        assert driver_3.value == pytest.approx(phase, abs=2.0e-15)

        driver_1.value = 0.0
        driver_2.value = 0.0
        driver_3.value = 0.0

        for index, value in enumerate(raw):
            assert Vector3D.distance(
                value, Vector3D(tdl.get_los(index, refdate.shiftedBy(float(instant))).tolist())
            ) == pytest.approx(0.0, abs=2.0e-15)
