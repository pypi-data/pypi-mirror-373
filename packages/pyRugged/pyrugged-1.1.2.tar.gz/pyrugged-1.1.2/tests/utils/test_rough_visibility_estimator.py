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

"""Test of pyrugged Class RoughVisibilityEstimator"""

# pylint: disable=duplicate-code, redefined-outer-name
import os

import numpy as np
import pytest
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.frames import FramesFactory
from org.orekit.orbits import CircularOrbit, PositionAngleType
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import IERSConventions

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.utils.constants import Constants
from pyrugged.utils.coordinates_reader import extract_pv_from_txt
from pyrugged.utils.rough_visibility_estimator import RoughVisibilityEstimator


@pytest.fixture
def ellipsoid():
    """Ellipsoid to be used."""

    init_orekit()

    itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

    return ExtendedEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, itrf)


def test_one_orbits_span(ellipsoid):
    """Test one orbit span"""

    init_orekit()

    gravity_field = create_gravity_field()
    orbit = create_orbit(gravity_field.getMu())

    txt_file_path = os.path.join(os.path.dirname(__file__), "../data/ref/utils/testOneOrbitsSpan_pv.txt")
    pv_list = extract_pv_from_txt(txt_file_path)

    estimator = RoughVisibilityEstimator(ellipsoid, orbit.getFrame(), pv_list)

    d_estimation = estimator.estimate_visibility(np.array([float(np.radians(43.303)), float(np.radians(-46.126)), 0.0]))

    assert AbsoluteDate("2012-01-01T01:02:39.122526662", TimeScalesFactory.getUTC()).durationFrom(
        d_estimation
    ) == pytest.approx(0.0, abs=7.0e-8)


def test_three_orbits_span(ellipsoid):
    """Test three orbits span"""

    init_orekit()

    gravity_field = create_gravity_field()
    orbit = create_orbit(gravity_field.getMu())

    txt_file_path = os.path.join(os.path.dirname(__file__), "../data/ref/utils/testThreeOrbitsSpan_pv.txt")
    pv_list = extract_pv_from_txt(txt_file_path)

    estimator = RoughVisibilityEstimator(ellipsoid, orbit.getFrame(), pv_list)

    d_estimation = estimator.estimate_visibility(np.array([float(np.radians(-81.5)), float(np.radians(-2.0)), 0.0]))

    assert AbsoluteDate("2012-01-01T03:47:08.814121623", TimeScalesFactory.getUTC()).durationFrom(
        d_estimation
    ) == pytest.approx(0.0, abs=1.0e-8)


def create_gravity_field():

    return GravityFieldFactory.getNormalizedProvider(12, 12)


def create_orbit(mu_val):
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


if __name__ == "__main__":
    test_one_orbits_span(ellipsoid())
    test_three_orbits_span(ellipsoid())
