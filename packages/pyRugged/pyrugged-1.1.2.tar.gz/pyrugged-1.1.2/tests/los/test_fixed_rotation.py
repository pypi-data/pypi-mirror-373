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

"""pyrugged test Class for FixedRotation"""

# pylint: disable=duplicate-code
# pylint: disable=redefined-outer-name
import numpy as np
import pytest
from org.hipparchus.geometry.euclidean.threed import Rotation, RotationConvention, Vector3D
from org.hipparchus.random import UncorrelatedRandomVectorGenerator, UniformRandomGenerator, Well19937a
from org.orekit.time import AbsoluteDate

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.los.fixed_rotation import FixedRotation
from pyrugged.los.los_builder import LOSBuilder

init_orekit(use_internal_data=False)


normal = Vector3D.PLUS_I
fov_center = Vector3D.PLUS_K
cross = Vector3D.crossProduct(normal, fov_center)


@pytest.fixture
def raw():
    """Raw list of vectors for LOS builder"""

    raw = []
    for i in range(-100, 100):
        alpha = i * 0.17 / 1000
        raw.append(Vector3D(float(np.cos(alpha)), fov_center, float(np.sin(alpha)), cross))

    return raw


def test_identity(raw):
    """Test with identity transformation."""

    rng = UniformRandomGenerator(Well19937a(100))
    rvg = UncorrelatedRandomVectorGenerator(3, rng)

    for _index in range(20):
        builder = LOSBuilder(raw)
        builder.add_ti_los_transform(FixedRotation("identity", Vector3D(rvg.nextVector()), 0.0))

        tdl = builder.build()
        for index, raw_value in enumerate(raw):
            assert Vector3D.distance(
                raw_value, Vector3D(tdl.get_los(index, AbsoluteDate.J2000_EPOCH).tolist())
            ) == pytest.approx(0.0, abs=2.0e-15)

        assert len(tdl.get_parameters_drivers()) == 1
        assert tdl.get_parameters_drivers()[0].name == "identity"


def test_fixed_combination(raw):
    """Test fixed combinations."""

    rng = UniformRandomGenerator(Well19937a(1234))
    rvg = UncorrelatedRandomVectorGenerator(3, rng)

    for _ in range(20):
        builder = LOSBuilder(raw)

        axis_1 = Vector3D(rvg.nextVector())
        angle_1 = 2 * float(np.pi) * rng.nextNormalizedDouble() / float(np.sqrt(3.0))
        builder.add_ti_los_transform(FixedRotation("r1", axis_1, angle_1))
        r_1 = Rotation(axis_1, angle_1, RotationConvention.VECTOR_OPERATOR)

        axis_2 = Vector3D(rvg.nextVector())
        angle_2 = 2 * float(np.pi) * rng.nextNormalizedDouble() / float(np.sqrt(3.0))
        builder.add_ti_los_transform(FixedRotation("r2", axis_2, angle_2))
        r_2 = Rotation(axis_2, angle_2, RotationConvention.VECTOR_OPERATOR)

        axis_3 = Vector3D(rvg.nextVector())
        angle_3 = 2 * float(np.pi) * rng.nextNormalizedDouble() / float(np.sqrt(3.0))
        builder.add_ti_los_transform(FixedRotation("r3", axis_3, angle_3))
        r_3 = Rotation(axis_3, angle_3, RotationConvention.VECTOR_OPERATOR)

        tdl = builder.build()
        combined = r_3.applyTo(r_2.applyTo(r_1))

        for i, item in enumerate(raw):
            assert Vector3D.distance(
                combined.applyTo(item), Vector3D(tdl.get_los(i, AbsoluteDate.J2000_EPOCH).tolist())
            ) == pytest.approx(0.0, abs=2.0e-15)

        drivers = tdl.get_parameters_drivers()
        assert len(drivers) == 3

        driver_1 = drivers[0]
        driver_2 = drivers[1]
        driver_3 = drivers[2]

        assert driver_1.name == "r1"
        assert driver_1.min_value == pytest.approx(-2 * float(np.pi), abs=2.0e-15)
        assert driver_1.max_value == pytest.approx(2 * float(np.pi), abs=2.0e-15)
        assert driver_1.value == pytest.approx(angle_1, abs=2.0e-15)
        assert driver_2.name == "r2"
        assert driver_2.min_value == pytest.approx(-2 * float(np.pi), abs=2.0e-15)
        assert driver_2.max_value == pytest.approx(2 * float(np.pi), abs=2.0e-15)
        assert driver_2.value == pytest.approx(angle_2, abs=2.0e-15)
        assert driver_3.name == "r3"
        assert driver_3.min_value == pytest.approx(-2 * float(np.pi), abs=2.0e-15)
        assert driver_3.max_value == pytest.approx(2 * float(np.pi), abs=2.0e-15)
        assert driver_3.value == pytest.approx(angle_3, abs=2.0e-15)

        driver_1.value = 0.0
        driver_2.value = 0.0
        driver_3.value = 0.0

        for index, value in enumerate(raw):
            assert Vector3D.distance(
                value, Vector3D(tdl.get_los(index, AbsoluteDate.J2000_EPOCH).tolist())
            ) == pytest.approx(0.0, abs=2.0e-15)
