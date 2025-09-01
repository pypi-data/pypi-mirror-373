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

"""pyrugged Class ConstantElevationAlgorithmTest"""


import math

import numpy as np
import pytest

from pyrugged.bodies.geodesy import normalize_geodetic_point
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.constant_elevation_algorithm import ConstantElevationAlgorithm
from pyrugged.intersection.duvenhage.duvenhage_algorithm import DuvenhageAlgorithm
from pyrugged.intersection.ignore_dem_algorithm import IgnoreDEMAlgorithm
from pyrugged.utils.math_utils import to_array_v  # pylint: disable=no-name-in-module

from ..raster.checked_pattern_elevation_updater import CheckedPatternElevationUpdater


def setup_module():
    """
    setup : initVM
    """
    init_orekit(use_internal_data=False)


def test_ignore_dem_comparison(cliffs_of_moher_context, earth):
    """
    Tests ConstantElevationAlgorithm and IgnoreDEMAlgorithm
    """
    state = cliffs_of_moher_context["state"]
    los = np.array([-0.626242839, 0.0124194184, -0.7795291301])
    ignore = IgnoreDEMAlgorithm()
    constant_elevation = ConstantElevationAlgorithm(0.0)

    gp_ref = ignore.intersection(earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los)
    gp_const = constant_elevation.intersection(earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los)

    assert gp_ref[0] == pytest.approx(gp_const[0], abs=1e-6)
    assert gp_ref[1] == pytest.approx(gp_const[1], abs=1e-6)
    assert gp_ref[2] == pytest.approx(gp_const[2], abs=1e-3)
    assert constant_elevation.get_elevation(np.array([0.0]), np.array([0.0]))[0] == pytest.approx(0.0, abs=1e-3)

    # Shift longitude 2π
    shifted = constant_elevation.refine_intersection(
        earth,
        to_array_v(state.getPVCoordinates().getPosition().toArray()),
        los,
        normalize_geodetic_point(gp_const, 2 * float(np.pi)),
    )

    assert 2 * float(np.pi) + gp_const[1] == pytest.approx(shifted[1], abs=1e-6)

    # Simple test for test coverage purpose
    elevation0 = ignore.get_elevation(np.array([gp_ref[0]]), np.array([gp_const[0]]))
    assert elevation0[0] == pytest.approx(0.0, abs=1e-15)


def test_duvenhage_comparison(earth, cliffs_of_moher_context):
    """
    Test comparison with Duvenhage algorithm
    """
    state = cliffs_of_moher_context["state"]
    los = np.array([-0.626242839, 0.0124194184, -0.7795291301])
    duvenhage = DuvenhageAlgorithm(CheckedPatternElevationUpdater(np.radians(1.0), 256, 150.0, 150.0), 8, False)
    constant_elevation = ConstantElevationAlgorithm(150.0)

    # NormalizedGeodeticPoint objects
    gp_ref = duvenhage.intersection(earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los)
    gp_const = constant_elevation.intersection(earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los)

    assert gp_ref[0] == pytest.approx(gp_const[0], abs=1e-6)
    assert gp_ref[1] == pytest.approx(gp_const[1], abs=1e-6)
    assert gp_ref[2] == pytest.approx(gp_const[2], abs=1e-3)
    assert constant_elevation.get_elevation(np.array([0.0]), np.array([0.0]))[0] == pytest.approx(150.0, abs=1e-3)

    # Shift longitude 2π
    shifted = constant_elevation.refine_intersection(
        earth,
        to_array_v(state.getPVCoordinates().getPosition().toArray()),
        los,
        normalize_geodetic_point(gp_const, 2 * math.pi),
    )

    assert 2 * math.pi + gp_const[1] == pytest.approx(shifted[1], abs=1e-6)


def test_algorithm_id():
    """
    Tests ConstantElevationAlgorithm and IgnoreDEMAlgorithm algorithm_id parameters
    """

    constant_elevation = ConstantElevationAlgorithm(0.0)
    assert AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID == constant_elevation.algorithm_id

    ignore = IgnoreDEMAlgorithm()
    assert AlgorithmId.IGNORE_DEM_USE_ELLIPSOID == ignore.algorithm_id


@pytest.mark.parametrize("altitudes", [0.0, 10.0, 25.4, 50.1])
def test_altitudes(cliffs_of_moher_context, earth, altitudes):
    """
    Tests ConstantElevationAlgorithm with alt
    """
    state = cliffs_of_moher_context["state"]
    los = np.array([-0.626242839, 0.0124194184, -0.7795291301])
    constant_elevation_0 = ConstantElevationAlgorithm(0.0)
    constant_elevation_alt = ConstantElevationAlgorithm(altitudes)

    gp_const_alt = constant_elevation_alt.intersection(
        earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los
    )
    gp_const_0_alt = constant_elevation_0.intersection(
        earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los, altitudes
    )

    assert gp_const_alt[0] == gp_const_0_alt[0]
    assert gp_const_alt[1] == gp_const_0_alt[1]


def test_altitudes_addition(cliffs_of_moher_context, earth):
    """
    Tests additon of altitudes between default_elev and altitudes
    """
    state = cliffs_of_moher_context["state"]
    los = np.array([-0.626242839, 0.0124194184, -0.7795291301])
    constant_elevation_0 = ConstantElevationAlgorithm(0.0)
    constant_elevation_10 = ConstantElevationAlgorithm(10.0)
    constant_elevation_254 = ConstantElevationAlgorithm(25.4)

    gp_const_10 = constant_elevation_10.intersection(
        earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los
    )
    gp_const_254 = constant_elevation_254.intersection(
        earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los
    )

    gp_const_0_10 = constant_elevation_0.intersection(
        earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los, 10.0
    )
    gp_const_0_254 = constant_elevation_0.intersection(
        earth, to_array_v(state.getPVCoordinates().getPosition().toArray()), los, 25.4
    )

    print(abs(gp_const_10[0] - gp_const_0_10[0]))
    print(abs(gp_const_10[1] - gp_const_0_10[1]))

    print(abs(gp_const_254[0] - gp_const_0_254[0]))
    print(abs(gp_const_254[1] - gp_const_0_254[1]))

    assert gp_const_10[0] == gp_const_0_10[0]
    assert gp_const_10[1] == gp_const_0_10[1]

    assert gp_const_254[0] == gp_const_0_254[0]
    assert gp_const_254[1] == gp_const_0_254[1]
