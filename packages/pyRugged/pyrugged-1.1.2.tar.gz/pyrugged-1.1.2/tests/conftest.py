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
"""
test fixtures
"""

# pylint: disable=unused-import
import numpy as np
import orekit_jcc  # noqa: F401
import pytest
from org.hipparchus.geometry.euclidean.threed import Rotation, Vector3D
from org.orekit.attitudes import Attitude
from org.orekit.frames import FramesFactory
from org.orekit.orbits import CartesianOrbit
from org.orekit.propagation import SpacecraftState
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import IERSConventions, PVCoordinates

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.utils.constants import Constants
from tests.raster.cliffs_elevation_updater import CliffsElevationUpdater
from tests.raster.volcanic_cone_elevation_updater import VolcanicConeElevationUpdater


@pytest.fixture(scope="session")
def earth():
    """
    ellipsoid fixture
    """

    init_orekit()

    ellipsoid = ExtendedEllipsoid(
        Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
        Constants.WGS84_EARTH_FLATTENING,
        FramesFactory.getITRF(IERSConventions.IERS_2010, True),
    )

    return ellipsoid


@pytest.fixture(scope="session")
def mayon_volcano_context():
    """
    Mayon volcano context fixture
    """

    init_orekit()

    # Mayon Volcano location according to Wikipedia: 13°15′24″N 123°41′6″E
    summit = np.array([float(np.radians(13.25667)), float(np.radians(123.685)), 2463.0])
    updater = VolcanicConeElevationUpdater(summit, float(np.radians(30.0)), 16.0, float(np.radians(1.0)), 1201)

    # some orbital parameters have been computed using Orekit
    # tutorial about phasing, using the following configuration:
    #
    #  orbit.date                          = 2012-01-01T00:00:00.000
    #  phasing.orbits.number               = 143
    #  phasing.days.number                 =  10
    #  sun.synchronous.reference[0]  = 0
    #  sun.synchronous.reference.ascending = false
    #  sun.synchronous.mean.solar.time     = 10:30:00
    #  gravity.field.degree                = 12
    #  gravity.field.order                 = 12
    #
    # the resulting phased orbit has then been propagated to a date corresponding
    # to test point lying in the spacecraft (YZ) plane (with nadir pointing and yaw compensation)

    crossing = AbsoluteDate("2012-01-06T02:27:15.942757185", TimeScalesFactory.getUTC())
    state = SpacecraftState(
        CartesianOrbit(
            PVCoordinates(
                Vector3D(-649500.423763743, -6943715.537565755, 1657929.13706338),
                Vector3D(-1305.453711368668, -1600.627551928136, -7167.286855869801),
            ),
            FramesFactory.getEME2000(),
            crossing,
            Constants.EIGEN5C_EARTH_MU,
        ),
        Attitude(
            crossing,
            FramesFactory.getEME2000(),
            Rotation(-0.40904880353552850, 0.46125295378582530, -0.63525007056319790, -0.46516893361386025, True),
            Vector3D(-7.048568391860185e-05, -1.043582650222194e-03, 1.700400341147713e-05),
            Vector3D.ZERO,
        ),
    )

    context = {"state": state, "updater": updater}
    return context


@pytest.fixture(scope="session")
def cliffs_of_moher_context():
    """
    Cliffs of Moher context fixture
    """

    init_orekit()

    # Cliffs of Moher location according to Wikipedia: 52°56′10″N 9°28′15″ W
    north = np.array([float(np.radians(52.9984)), float(np.radians(-9.4072)), 120.0])

    south = np.array([float(np.radians(52.9625)), float(np.radians(-9.4369)), 120.0])

    # Cells are about 10m x 10m here and a tile covers 1km x 1km
    updater = CliffsElevationUpdater(north, south, 120.0, 0.0, float(np.radians(0.015)), 101)

    # some orbital parameters have been computed using Orekit
    # tutorial about phasing, using the following configuration:
    #
    #  orbit.date                          = 2012-01-01T00:00:00.000
    #  phasing.orbits.number               = 143
    #  phasing.days.number                 =  10
    #  sun.synchronous.reference[0]  = 0
    #  sun.synchronous.reference.ascending = false
    #  sun.synchronous.mean.solar.time     = 10:30:00
    #  gravity.field.degree                = 12
    #  gravity.field.order                 = 12
    #
    # the resulting phased orbit has then been propagated to a date corresponding
    # to test point lying in the spacecraft (YZ) plane (with nadir pointing and yaw compensation)

    crossing = AbsoluteDate("2012-01-07T11:50:04.935272115", TimeScalesFactory.getUTC())
    state = SpacecraftState(
        CartesianOrbit(
            PVCoordinates(
                Vector3D(412324.544397459, -4325872.329311633, 5692124.593989491),
                Vector3D(-1293.174701214779, -5900.764863603793, -4378.671036383179),
            ),
            FramesFactory.getEME2000(),
            crossing,
            Constants.EIGEN5C_EARTH_MU,
        ),
        Attitude(
            crossing,
            FramesFactory.getEME2000(),
            Rotation(-0.17806699079182878, 0.60143347387211290, -0.73251248177468900, -0.26456641385623986, True),
            Vector3D(-4.289600857433520e-05, -1.039151496480297e-03, 5.811423736843181e-05),
            Vector3D.ZERO,
        ),
    )

    context = {"state": state, "updater": updater}
    return context
