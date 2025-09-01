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

"""Test of pyrugged Class MultiLayerModel"""


# pylint: disable=useless-super-delegation
# pylint: disable=no-name-in-module
import numpy as np
import pytest

from pyrugged.bodies.geodesy import nadir
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.duvenhage.duvenhage_algorithm import DuvenhageAlgorithm
from pyrugged.los.rotation import Rotation, RotationConvention
from pyrugged.refraction.constant_refraction_layer import ConstantRefractionLayer
from pyrugged.refraction.multi_layer_model import MultiLayerModel
from pyrugged.utils.math_utils import angle, distance, orthogonal  # pylint: disable=no-name-in-module

init_orekit(use_internal_data=False)


def reference(alpha):
    """Reference function."""

    return 1.17936 * float(np.tan((2.94613 - 1.40162 * alpha) * alpha))


def los_func(position, angle_from_nadir, ellipsoid):
    """LOS function."""

    nadir_p = nadir(ellipsoid.transform_vec(position, ellipsoid.body_frame, None))
    los_rotation = Rotation(orthogonal(nadir_p), angle_from_nadir, RotationConvention.VECTOR_OPERATOR)

    return los_rotation.applyTo(nadir_p)


def test_almost_nadir(mayon_volcano_context, earth):
    """Test almost nadir."""

    updater = mayon_volcano_context["updater"]
    algorithm = DuvenhageAlgorithm(updater, 8, False)

    position = np.array([-3787079.6453602533, 5856784.405679551, 1655869.0582939098])
    los = np.array([0.5127552821932051, -0.8254313129088879, -0.2361041470463311])
    raw_intersection = algorithm.refine_intersection(earth, position, los, algorithm.intersection(earth, position, los))

    model = MultiLayerModel(earth)
    corrected_intersection = model.apply_correction(position, los, raw_intersection, algorithm)
    distance1 = distance(earth.transform_vec(raw_intersection), earth.transform_vec(corrected_intersection))

    # This is almost a Nadir observation (LOS deviates between 1.4 and 1.6 degrees from vertical)
    # so the refraction correction is small
    assert distance1 == pytest.approx(0.0553796, abs=1.0e-6)


def test_no_op_refraction(mayon_volcano_context, earth):
    """Test no op refraction."""

    updater = mayon_volcano_context["updater"]
    algorithm = DuvenhageAlgorithm(updater, 8, False)

    position = np.array([-3787079.6453602533, 5856784.405679551, 1655869.0582939098])
    los = los_func(position, float(np.radians(50.0)), earth)
    raw_intersection = algorithm.refine_intersection(earth, position, los, algorithm.intersection(earth, position, los))

    model = MultiLayerModel(earth)

    # A test with indices all set to 1.0 - correction must be zero
    number_of_layers = 16
    refraction_layers = []

    for i in range(number_of_layers - 1, -1, -1):
        refraction_layers.append(ConstantRefractionLayer(i * 1.0e4, 1.0))

    model = MultiLayerModel(earth, refraction_layers)

    corrected_intersection = model.apply_correction(position, los, raw_intersection, algorithm)
    distance1 = distance(earth.transform_vec(raw_intersection), earth.transform_vec(corrected_intersection))

    assert distance1 == pytest.approx(0.0, abs=7.0e-9)  # 1.7 in rugged JAVA


def test_reversed_atmosphere(mayon_volcano_context, earth):
    """Test reversed atmosphere."""

    updater = mayon_volcano_context["updater"]
    algorithm = DuvenhageAlgorithm(updater, 8, False)

    position = np.array([-3787079.6453602533, 5856784.405679551, 1655869.0582939098])
    los = los_func(position, float(np.radians(50.0)), earth)
    raw_intersection = algorithm.refine_intersection(earth, position, los, algorithm.intersection(earth, position, los))

    base_model = MultiLayerModel(earth)
    corrected_intersection = base_model.apply_correction(position, los, raw_intersection, algorithm)

    # An intentionally flawed atmosphere with refractive indices decreasing with altitude,
    # that should exhibit a LOS bending upwards

    base_refraction_layers = base_model.get_refraction_layers()
    denser_refraction_layers = []
    for layer in base_refraction_layers:
        denser_refraction_layers.append(
            ConstantRefractionLayer(layer.get_lowest_altitude(), 1.0 / layer.get_refractive_index())
        )

    reversed_model = MultiLayerModel(earth, denser_refraction_layers)
    reversed_intersection = reversed_model.apply_correction(position, los, raw_intersection, algorithm)

    angle_pos_raw_intersection = angle(position, earth.transform_vec(raw_intersection))
    angle_pos_corrected_intersection = angle(position, earth.transform_vec(corrected_intersection))
    angle_pos_reversed_intersection = angle(position, earth.transform_vec(reversed_intersection))

    # With regular atmosphere, the ray bends downwards,
    # so the ground point is closer to the sub-satellite point than the raw intersection
    assert angle_pos_corrected_intersection < angle_pos_raw_intersection

    # With reversed atmosphere, the ray bends upwards,
    # so the ground point is farther from the sub-satellite point than the raw intersection
    assert angle_pos_reversed_intersection > angle_pos_raw_intersection

    # The points are almost aligned (for distances around 20m, Earth curvature is small enough)
    d_raw_corrected = distance(earth.transform_vec(raw_intersection), earth.transform_vec(corrected_intersection))
    d_raw_reversed = distance(earth.transform_vec(raw_intersection), earth.transform_vec(reversed_intersection))
    d_reversed_corrected = distance(
        earth.transform_vec(reversed_intersection), earth.transform_vec(corrected_intersection)
    )
    assert d_raw_corrected + d_raw_reversed == pytest.approx(d_reversed_corrected, 1.0e-12)


def test_two_atmospheres(mayon_volcano_context, earth):
    """Test two atmospheres."""

    updater = mayon_volcano_context["updater"]
    algorithm = DuvenhageAlgorithm(updater, 8, False)

    position = np.array([-3787079.6453602533, 5856784.405679551, 1655869.0582939098])
    los = los_func(position, float(np.radians(50.0)), earth)
    raw_intersection = algorithm.refine_intersection(earth, position, los, algorithm.intersection(earth, position, los))

    # A comparison between two atmospheres, one more dense than the other and showing correction
    # is more important with high indices
    base_model = MultiLayerModel(earth)
    base_refraction_layers = base_model.get_refraction_layers()
    denser_refraction_layers = []

    previous_base_n = 1.0
    previous_denser_n = 1.0
    factor = 1.00001
    for layer in base_refraction_layers:
        current_base_n = layer.get_refractive_index()
        base_ratio = current_base_n / previous_base_n
        current_denser_n = previous_denser_n * factor * base_ratio

        denser_refraction_layers.append(ConstantRefractionLayer(layer.get_lowest_altitude(), current_denser_n))

        previous_base_n = current_base_n
        previous_denser_n = current_denser_n

    denser_model = MultiLayerModel(earth, denser_refraction_layers)
    base_intersection = base_model.apply_correction(position, los, raw_intersection, algorithm)
    denser_intersection = denser_model.apply_correction(position, los, raw_intersection, algorithm)

    base_distance = distance(earth.transform_vec(raw_intersection), earth.transform_vec(base_intersection))
    denser_distance = distance(earth.transform_vec(raw_intersection), earth.transform_vec(denser_intersection))

    assert denser_distance > base_distance


def test_missing_layers(mayon_volcano_context, earth):
    """Test missing layers."""

    updater = mayon_volcano_context["updater"]
    algorithm = DuvenhageAlgorithm(updater, 8, False)

    position = np.array([-3787079.6453602533, 5856784.405679551, 1655869.0582939098])
    los = los_func(position, float(np.radians(50.0)), earth)
    raw_intersection = algorithm.refine_intersection(earth, position, los, algorithm.intersection(earth, position, los))

    h_val = raw_intersection[2]

    model = MultiLayerModel(earth, [ConstantRefractionLayer(h_val + 100.0, 1.5)])

    try:
        model.apply_correction(position, los, raw_intersection, algorithm)
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.NO_LAYER_DATA.value.format(h_val, h_val + 100.0)


def test_layers_below_dem(mayon_volcano_context, earth):
    """Test layers below DEM."""

    updater = mayon_volcano_context["updater"]
    algorithm = DuvenhageAlgorithm(updater, 8, False)

    position = np.array([-3787079.6453602533, 5856784.405679551, 1655869.0582939098])
    los = los_func(position, float(np.radians(50.0)), earth)
    raw_intersection = algorithm.refine_intersection(earth, position, los, algorithm.intersection(earth, position, los))

    model = MultiLayerModel(earth, [ConstantRefractionLayer(raw_intersection[2] - 100.0, 1.5)])

    corrected_intersection = model.apply_correction(position, los, raw_intersection, algorithm)
    distance1 = distance(earth.transform_vec(raw_intersection), earth.transform_vec(corrected_intersection))

    assert distance1 == pytest.approx(0.0, abs=1.3e-9)


def test_diving_angle_change(mayon_volcano_context, earth):
    """Test diving angle change."""

    updater = mayon_volcano_context["updater"]
    algorithm = DuvenhageAlgorithm(updater, 8, False)

    position = np.array([-3787079.6453602533, 5856784.405679551, 1655869.0582939098])
    model = MultiLayerModel(earth)

    # Deviation should increase from 0 to about 17m
    # as the angle between los and nadir increases from 0 to 50 degrees
    # the reference model below has been obtained by fitting the test results themselves
    # it is NOT considered a full featured model, it's just a helper function for this specific test

    alpha = 0.0
    while alpha < float(np.radians(50.0)):
        rotating_los = los_func(position, alpha, earth)
        raw_intersection = algorithm.refine_intersection(
            earth, position, rotating_los, algorithm.intersection(earth, position, rotating_los)
        )

        corrected_intersection = model.apply_correction(position, rotating_los, raw_intersection, algorithm)
        distance1 = distance(earth.transform_vec(raw_intersection), earth.transform_vec(corrected_intersection))

        assert distance1 == pytest.approx(reference(alpha), abs=0.12)

        alpha += 0.1
