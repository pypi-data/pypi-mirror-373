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

"""pyrugged test Class for DynamicTransform"""

import numpy as np
import pytest
from org.orekit.frames import StaticTransform

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.los.transform import (
    DynamicTransform,
    array_to_vector3d,
    get_corresponding_orekit_transform,
    transform_to_numpy,
    vector3d_to_array,
)

init_orekit()


@pytest.fixture(name="mono_elements", scope="module")
def given_single_date_elements():
    """
    Fixture to generate single date transform elements
    """
    translation = np.random.rand(3) * 2.0 - 1.0
    velocity = np.random.rand(3) * 2.0 - 1.0
    acceleration = np.random.rand(3) * 2.0 - 1.0

    rotation = np.random.rand(4) * 2.0 - 1.0
    rotation /= np.linalg.norm(rotation)
    rotation_rate = np.random.rand(3) * 2.0 - 1.0
    rotation_acc = np.random.rand(3) * 2.0 - 1.0

    return [translation, velocity, acceleration, rotation, rotation_rate, rotation_acc]


@pytest.fixture(name="multi_elements", scope="module")
def given_multi_date_elements():
    """
    Fixture to generate dual date transform elements
    """
    translation = np.random.rand(6).reshape((2, 3)) * 2.0 - 1.0
    velocity = np.random.rand(6).reshape((2, 3)) * 2.0 - 1.0
    acceleration = None  # test with no acceleration

    rotation = np.random.rand(8).reshape((2, 4)) * 2.0 - 1.0
    rotation /= np.linalg.norm(rotation, axis=1, keepdims=True)
    rotation_rate = np.random.rand(6).reshape((2, 3)) * 2.0 - 1.0
    rotation_acc = np.random.rand(3) * 2.0 - 1.0  # leave the acceleration constant

    return [translation, velocity, acceleration, rotation, rotation_rate, rotation_acc]


@pytest.fixture(name="mono_transfo", scope="module")
def given_single_date_dynamic_transform(mono_elements):
    """
    Fixture to generate a mono-date DynamicTransform
    """
    return DynamicTransform(
        translation=mono_elements[0],
        velocity=mono_elements[1],
        acceleration=mono_elements[2],
        rotation=mono_elements[3],
        rotation_rate=mono_elements[4],
        rotation_acceleration=mono_elements[5],
    )


@pytest.fixture(name="multi_transfo", scope="module")
def given_multi_date_dynamic_transform(multi_elements):
    """
    Fixture to generate a mono-date DynamicTransform
    """
    return DynamicTransform(
        translation=multi_elements[0],
        velocity=multi_elements[1],
        acceleration=multi_elements[2],
        rotation=multi_elements[3],
        rotation_rate=multi_elements[4],
        rotation_acceleration=multi_elements[5],
    )


def test_size_mono(mono_transfo):
    """
    Unit test for DynamicTransform length with mono date
    """

    # Check size:
    assert len(mono_transfo) == 1


def test_size_multi(multi_transfo):
    """
    Unit test for DynamicTransform length with mono date
    """

    # Check size:
    assert len(multi_transfo) == 2


def test_orekit_counterpart(mono_elements, mono_transfo):
    """
    Unit test to check we can create an equivalent Orekit Transform
    """
    orekit_transform = get_corresponding_orekit_transform(mono_elements)

    ref_elements = transform_to_numpy(orekit_transform)

    # Check original elements are the same
    assert np.allclose(mono_transfo.translation, ref_elements[0], rtol=0, atol=1e-10)
    assert np.allclose(mono_transfo.velocity, ref_elements[1], rtol=0, atol=1e-10)
    assert np.allclose(mono_transfo.acceleration, ref_elements[2], rtol=0, atol=1e-10)
    assert np.allclose(mono_transfo.rotation, ref_elements[3], rtol=0, atol=1e-10)
    assert np.allclose(mono_transfo.rotation_rate, ref_elements[4], rtol=0, atol=1e-10)
    assert np.allclose(mono_transfo.rotation_acceleration, ref_elements[5], rtol=0, atol=1e-10)


def test_shift_mono(mono_elements, mono_transfo):
    """
    Unit test for DynamicTransform
    """

    orekit_transform = get_corresponding_orekit_transform(mono_elements)

    # shift both transforms by 0.5s
    shifted = mono_transfo.shifted(0.5)
    orekit_shift = orekit_transform.shiftedBy(0.5)

    # Check elements of shifted transforms are the same
    ref_elements = transform_to_numpy(orekit_shift)
    assert np.allclose(shifted.translation, ref_elements[0], rtol=0, atol=1e-10)
    assert np.allclose(shifted.velocity, ref_elements[1], rtol=0, atol=1e-10)
    assert np.allclose(shifted.acceleration, ref_elements[2], rtol=0, atol=1e-10)
    assert np.allclose(shifted.rotation, ref_elements[3], rtol=0, atol=1e-10)
    assert np.allclose(shifted.rotation_rate, ref_elements[4], rtol=0, atol=1e-10)
    assert np.allclose(shifted.rotation_acceleration, ref_elements[5], rtol=0, atol=1e-10)


def test_shift_multi(multi_elements, multi_transfo):
    """
    Unit test for DynamicTransform
    """

    orekit_first_transform = get_corresponding_orekit_transform(multi_elements, sub_index=0)
    orekit_second_transform = get_corresponding_orekit_transform(multi_elements, sub_index=1)

    # shift all transforms by 0.5s
    shifted = multi_transfo.shifted(0.5)
    orekit_first_shift = orekit_first_transform.shiftedBy(0.5)
    orekit_second_shift = orekit_second_transform.shiftedBy(0.5)

    # Check elements of shifted transforms are the same
    ref_elements = transform_to_numpy([orekit_first_shift, orekit_second_shift])

    assert np.allclose(shifted.translation, ref_elements[0], rtol=0, atol=1e-10)
    assert np.allclose(shifted.velocity, ref_elements[1], rtol=0, atol=1e-10)
    assert shifted.acceleration is None
    assert np.allclose(shifted.rotation, ref_elements[3], rtol=0, atol=1e-10)
    assert np.allclose(shifted.rotation_rate, ref_elements[4], rtol=0, atol=1e-10)
    assert np.allclose(shifted.rotation_acceleration, ref_elements[5], rtol=0, atol=1e-10)


def test_shift_multi_2times(multi_elements, multi_transfo):
    """
    Unit test for DynamicTransform.shift with 2 different times
    """

    orekit_first_transform = get_corresponding_orekit_transform(multi_elements, sub_index=0)
    orekit_second_transform = get_corresponding_orekit_transform(multi_elements, sub_index=1)

    # shift transforms by 0.4s (resp. 0.7s)
    shifted = multi_transfo.shifted([0.4, 0.7])
    orekit_first_shift = orekit_first_transform.shiftedBy(0.4)
    orekit_second_shift = orekit_second_transform.shiftedBy(0.7)

    # Check elements of shifted transforms are the same
    ref_elements = transform_to_numpy([orekit_first_shift, orekit_second_shift])

    assert np.allclose(shifted.translation, ref_elements[0], rtol=0, atol=1e-10)
    assert np.allclose(shifted.velocity, ref_elements[1], rtol=0, atol=1e-10)
    assert shifted.acceleration is None
    assert np.allclose(shifted.rotation, ref_elements[3], rtol=0, atol=1e-10)
    assert np.allclose(shifted.rotation_rate, ref_elements[4], rtol=0, atol=1e-10)
    assert np.allclose(shifted.rotation_acceleration, ref_elements[5], rtol=0, atol=1e-10)


def test_transform_position_mono(mono_elements, mono_transfo):
    """
    Unit test for DynamicTransform.transform_position
    """

    position = np.array([1.0, 2.0, 3.0])
    out_position = mono_transfo.transform_position(position)

    # compare with Orekit
    orekit_transform = get_corresponding_orekit_transform(mono_elements)
    static_transfo = StaticTransform.cast_(orekit_transform)
    ref_out = vector3d_to_array(static_transfo.transformPosition(array_to_vector3d(position)))
    assert np.allclose(out_position, ref_out, rtol=0, atol=1e-10)


def test_transform_position_multi(multi_elements, multi_transfo):
    """
    Unit test for DynamicTransform.transform_position with multiple transforms
    """

    position = np.array([1.0, 2.0, 3.0])
    out_position = multi_transfo.transform_position(position)

    # compare with Orekit
    orekit_first_transform = get_corresponding_orekit_transform(multi_elements, sub_index=0)
    orekit_second_transform = get_corresponding_orekit_transform(multi_elements, sub_index=1)

    static_first_transfo = StaticTransform.cast_(orekit_first_transform)
    static_second_transfo = StaticTransform.cast_(orekit_second_transform)

    ref_first = vector3d_to_array(static_first_transfo.transformPosition(array_to_vector3d(position)))
    ref_second = vector3d_to_array(static_second_transfo.transformPosition(array_to_vector3d(position)))
    ref_out = np.stack([ref_first, ref_second])
    assert np.allclose(out_position, ref_out, rtol=0, atol=1e-10)


def test_transform_position_multi_2pos(multi_elements, multi_transfo):
    """
    Unit test for DynamicTransform.transform_position with multiple transforms and 2 positions
    """

    position = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    out_position = multi_transfo.transform_position(position)

    # compare with Orekit
    orekit_first_transform = get_corresponding_orekit_transform(multi_elements, sub_index=0)
    orekit_second_transform = get_corresponding_orekit_transform(multi_elements, sub_index=1)

    static_first_transfo = StaticTransform.cast_(orekit_first_transform)
    static_second_transfo = StaticTransform.cast_(orekit_second_transform)

    ref_first = vector3d_to_array(static_first_transfo.transformPosition(array_to_vector3d(position[0])))
    ref_second = vector3d_to_array(static_second_transfo.transformPosition(array_to_vector3d(position[1])))
    ref_out = np.stack([ref_first, ref_second])
    assert np.allclose(out_position, ref_out, rtol=0, atol=1e-10)


def test_transform_direction_mono(mono_elements, mono_transfo):
    """
    Unit test for DynamicTransform.transform_direction
    """

    direction = np.array([1.0, 2.0, 3.0])
    out_direction = mono_transfo.transform_direction(direction)

    # compare with Orekit
    orekit_transform = get_corresponding_orekit_transform(mono_elements)
    static_transfo = StaticTransform.cast_(orekit_transform)
    ref_out = vector3d_to_array(static_transfo.transformVector(array_to_vector3d(direction)))
    assert np.allclose(out_direction, ref_out, rtol=0, atol=1e-10)


def test_transform_direction_multi(multi_elements, multi_transfo):
    """
    Unit test for DynamicTransform.transform_direction with multiple transforms
    """

    direction = np.array([1.0, 2.0, 3.0])
    out_direction = multi_transfo.transform_direction(direction)

    # compare with Orekit
    orekit_first_transform = get_corresponding_orekit_transform(multi_elements, sub_index=0)
    orekit_second_transform = get_corresponding_orekit_transform(multi_elements, sub_index=1)

    static_first_transfo = StaticTransform.cast_(orekit_first_transform)
    static_second_transfo = StaticTransform.cast_(orekit_second_transform)

    ref_first = vector3d_to_array(static_first_transfo.transformVector(array_to_vector3d(direction)))
    ref_second = vector3d_to_array(static_second_transfo.transformVector(array_to_vector3d(direction)))
    ref_out = np.stack([ref_first, ref_second])
    assert np.allclose(out_direction, ref_out, rtol=0, atol=1e-10)


def test_transform_direction_multi_2pos(multi_elements, multi_transfo):
    """
    Unit test for DynamicTransform.transform_direction with multiple transforms and 2 directions
    """

    direction = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    out_direction = multi_transfo.transform_direction(direction)

    # compare with Orekit
    orekit_first_transform = get_corresponding_orekit_transform(multi_elements, sub_index=0)
    orekit_second_transform = get_corresponding_orekit_transform(multi_elements, sub_index=1)

    static_first_transfo = StaticTransform.cast_(orekit_first_transform)
    static_second_transfo = StaticTransform.cast_(orekit_second_transform)

    ref_first = vector3d_to_array(static_first_transfo.transformVector(array_to_vector3d(direction[0])))
    ref_second = vector3d_to_array(static_second_transfo.transformVector(array_to_vector3d(direction[1])))
    ref_out = np.stack([ref_first, ref_second])
    assert np.allclose(out_direction, ref_out, rtol=0, atol=1e-10)
