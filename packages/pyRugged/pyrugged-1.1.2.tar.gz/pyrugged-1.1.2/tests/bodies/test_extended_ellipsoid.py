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

"""Test of pyrugged Class ExtendedEllipsoid"""
import math

# pylint: disable=consider-using-with, redefined-outer-name
import numpy as np
import pytest
from org.hipparchus.geometry.euclidean.threed import Line, Vector3D
from org.orekit.frames import FramesFactory
from org.orekit.utils import IERSConventions

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.utils.constants import Constants
from pyrugged.utils.math_utils import distance  # pylint: disable=no-name-in-module
from pyrugged.utils.math_utils import compute_linear_combination_2, dot, get_norm  # pylint: disable=no-name-in-module


def setup_module():
    """
    setup : initVM and reset DUMP_VAR
    """

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None

    init_orekit(use_internal_data=False)


def teardown_module():
    """
    teardown : reset DUMP_VAR
    """
    dump_manager.DUMP_VAR = None


@pytest.fixture
def ellipsoid():
    """Ellipsoid fixture"""

    init_orekit()

    itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

    return ExtendedEllipsoid(
        Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
        Constants.WGS84_EARTH_FLATTENING,
        itrf,
    )


def test_point_at_longitude(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_longitude()"""

    init_orekit()

    p_vect = np.array([3220103.0, 69623.0, -6449822.0])
    d_vect = np.array([1.0, 2.0, 3.0])

    for longitude in np.arange(-1.0, 1.0, 0.01):
        point_gp = ellipsoid.transform_vec(
            ellipsoid.point_at_longitude(p_vect, d_vect, float(longitude)), ellipsoid.body_frame, None
        )

        assert point_gp[1] == pytest.approx(longitude, abs=1.0e-15)


def test_point_at_longitude_error(ellipsoid):
    """Testing exceptions for ExtendedEllipsoid.point_at_longitude()"""

    init_orekit()

    p_vect = np.array([3220103.0, 69623.0, -6449822.0])
    longitude = 1.25
    parallel_to_longitude_plane = np.array([float(np.cos(longitude)), float(np.sin(longitude)), -2.4])

    try:
        ellipsoid.transform_vec(ellipsoid.point_at_longitude(p_vect, parallel_to_longitude_plane, longitude))
        pytest.fail("An error should have been triggered")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_LONGITUDE.value.format(
            float(np.degrees(longitude))
        )


def test_point_at_longitude_vec(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_longitude_vec()"""

    init_orekit()

    longitude = np.concatenate((np.arange(-1.0, 1.0, 0.01), [1.25]))
    nb_pts = len(longitude)

    p_vect = np.tile(np.array([3220103.0, 69623.0, -6449822.0]), nb_pts).reshape((nb_pts, 3))
    d_vect = np.tile(np.array([1.0, 2.0, 3.0]), nb_pts).reshape((nb_pts, 3))
    # parallel to longitude plane at 1.25
    d_vect[-1, :] = np.array([float(np.cos(1.25)), float(np.sin(1.25)), -2.4])

    pts = ellipsoid.point_at_longitude_vec(p_vect, d_vect, longitude)

    assert np.all(np.isnan(pts[-1, :]))

    point_gp = ellipsoid.transform_vec(pts[:-1], ellipsoid.body_frame, None)

    assert np.allclose(point_gp[:, 1], longitude[:-1], rtol=0, atol=1.0e-15)


def test_point_at_longitude_vec_consistency(ellipsoid):
    """Testing consistency between vec and non-vec versions of point_at_longitude()"""

    init_orekit()

    longitude = np.array([2.495820830351891])
    p_vect = np.array([[-4701449.94849119, 3542804.77405781, -2443906.88617671]])
    d_vect = np.array([[0.9318507417866662, 0.3552173406409792, 0.07399213327707135]])
    # vec version
    pts = ellipsoid.point_at_longitude_vec(p_vect, d_vect, longitude)

    # check with single pt version
    ref_pt = ellipsoid.point_at_longitude(p_vect[0, :], d_vect[0, :], float(longitude[0]))
    print(f"Diff : {pts[0] - ref_pt}")
    assert np.all(pts[0] == ref_pt)


def test_point_at_latitude(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_latitude()"""

    init_orekit()

    p_vect = np.array([3220103.0, 69623.0, -6449822.0])
    d_vect = np.array([1.0, 2.0, 3.0])
    d_vect_delta = math.asin(d_vect[2] / get_norm(d_vect))

    for latitude in np.arange(-d_vect_delta + 1.0e-5, d_vect_delta, 0.1):
        point_gp = ellipsoid.transform_vec(
            ellipsoid.point_at_latitude(p_vect, d_vect, float(latitude), p_vect), ellipsoid.body_frame, None
        )

        assert point_gp[0] == pytest.approx(latitude, abs=6.0e-15)


def test_point_at_latitude_two_points_same_side(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_latitude()"""

    # the line of sight is almost parallel an iso-latitude cone generatrix
    # the spacecraft is at latitude lTarget - 0.951", and altitude 794.6km
    # so at a latitude slightly less than the target
    # the line of sight crosses the latitude cone first about 70km along line of sight
    # (so still at a very high altitude) and a second time about 798km along line of sight,
    # only a few hundreds meters above allipsoid
    # Note that this happens despite the line of sight is not along nadir, the longitudes
    # of the spacecraft and crossing points span in a 0.88° wide longitude range

    init_orekit()

    position = np.array([-748528.2769999998, -5451658.432000002, 4587158.354])
    los = np.array([0.010713435156834539, 0.7688536080293823, -0.6393350856376809])
    h_transform = ellipsoid.transform_vec(position, ellipsoid.body_frame, None)[2]
    l_target = 0.6978408125890662

    # Spacecraft is in LEO
    assert h_transform == pytest.approx(794652.782, abs=0.001)

    p_high = ellipsoid.point_at_latitude(position, los, l_target, position)
    gp_high = ellipsoid.transform_vec(p_high, ellipsoid.body_frame, None)
    assert gp_high[0] == pytest.approx(l_target, abs=1.0e-12)
    # First crossing point is high, but below spacecraft and along positive line of sight
    assert gp_high[2] == pytest.approx(724335.409, abs=0.001)
    assert dot(p_high - position, los) > 0

    p_low = ellipsoid.point_at_latitude(
        position, los, l_target, compute_linear_combination_2(1.0, position, 900000.0, los)
    )
    gp_low = ellipsoid.transform_vec(p_low, ellipsoid.body_frame, None)
    assert gp_low[0] == pytest.approx(l_target, abs=1.0e-12)
    # Second crossing point is almost on ground, also along positive line of sight
    assert gp_low[2] == pytest.approx(492.804, abs=0.001)
    assert dot(p_low - position, los) > 0


def test_point_at_latitude_two_points_opposite_side(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_latitude()"""

    init_orekit()

    p_vect = np.array([3220103.0, 69623.0, -6449822.0])
    d_vect = np.array([1.0, 2.0, 0.1])

    latitude = -0.5

    p_plus = ellipsoid.point_at_latitude(
        p_vect, d_vect, latitude, compute_linear_combination_2(1.0, p_vect, 2.0e7, d_vect)
    )
    gp_plus = ellipsoid.transform_vec(p_plus, ellipsoid.body_frame, None)
    assert gp_plus[0] == pytest.approx(latitude, abs=4.0e-16)
    assert dot(d_vect, p_plus - p_vect) == pytest.approx(20646364.047, abs=0.001)

    p_minus = ellipsoid.point_at_latitude(
        p_vect, d_vect, latitude, compute_linear_combination_2(1.0, p_vect, -3.0e7, d_vect)
    )
    gp_minus = ellipsoid.transform_vec(p_minus, ellipsoid.body_frame, None)
    assert gp_minus[0] == pytest.approx(latitude, 3.0e-16)
    assert dot(d_vect, p_minus - p_vect) == pytest.approx(-31797895.234, abs=0.001)


def test_point_at_latitude_almost_equator(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_latitude()"""

    init_orekit()

    p_vect = np.array([5767483.098580201, 4259689.325372237, -41553.67750784925])
    d_vect = np.array([-0.7403523952347795, -0.6701811835520302, 0.05230212180799747])
    latitude = -3.469446951953614e-18
    close_reference = np.array([5177991.74844521, 3726070.452427455, 90.88067547897226])
    intersection = ellipsoid.point_at_latitude(p_vect, d_vect, latitude, close_reference)
    point_gp = ellipsoid.transform_vec(intersection, ellipsoid.body_frame, None)

    assert point_gp[0] == pytest.approx(latitude, abs=1.0e-10)
    assert point_gp[2] == pytest.approx(2866.297, abs=1.0e-3)


def test_point_at_latitude_error_quadratic_equation(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_latitude()"""

    init_orekit()

    p_vect = np.array([3220103.0, 69623.0, -6449822.0])
    d_vect = np.array([1.0, 2.0, 3.0])
    latitude = 1.4

    try:
        ellipsoid.point_at_latitude(p_vect, d_vect, latitude, p_vect)
        pytest.fail("An error should have been triggered")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_LATITUDE.value.format(
            float(np.degrees(latitude))
        )


def test_point_at_latitude_error_nappe(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_latitude()"""

    init_orekit()

    p_vect = np.array([3220103.0, 69623.0, -6449822.0])
    d_vect = np.array([1.0, 2.0, 0.1])
    latitude = 0.5

    try:
        ellipsoid.point_at_latitude(p_vect, d_vect, latitude, p_vect)
        pytest.fail("An error should have been triggered")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_LATITUDE.value.format(
            float(np.degrees(latitude))
        )


def test_point_at_latitude_error(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_latitude()"""

    init_orekit()

    p_vect = np.array([-3052690.88784496, 6481300.309857268, 25258.7478104745])
    d_vect = np.array([0.6, -0.8, 0.0])
    latitude = 0.1
    c_vect = np.array([-2809972.5765414005, 5727461.020250551, 26.163518446261833])

    try:
        ellipsoid.point_at_latitude(p_vect, d_vect, latitude, c_vect)
        pytest.fail("An error should have been triggered")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_LATITUDE.value.format(
            float(np.degrees(latitude))
        )


def test_point_at_latitude_vec(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_latitude_vec()"""

    init_orekit()

    p_vect_ok = np.array([3220103.0, 69623.0, -6449822.0])
    d_vect_ok = np.array([1.0, 2.0, 3.0])
    d_vect_delta = math.asin(d_vect_ok[2] / get_norm(d_vect_ok))
    latitude_ok = np.arange(-d_vect_delta + 1.0e-5, d_vect_delta, 0.1)
    nb_ok = len(latitude_ok)

    # concatenate with error case
    p_vect_err = np.array([-3052690.88784496, 6481300.309857268, 25258.7478104745])
    d_vect_err = np.array([0.6, -0.8, 0.0])
    latitude_err = 0.1
    c_vect_err = np.array([-2809972.5765414005, 5727461.020250551, 26.163518446261833])

    # final buffers
    p_vect = np.concatenate((np.tile(p_vect_ok, nb_ok), p_vect_err)).reshape((nb_ok + 1, 3))
    d_vect = np.concatenate((np.tile(d_vect_ok, nb_ok), d_vect_err)).reshape((nb_ok + 1, 3))
    latitude = np.concatenate((latitude_ok, [latitude_err]))
    c_vect = np.concatenate((np.tile(p_vect_ok, nb_ok), c_vect_err)).reshape((nb_ok + 1, 3))

    pts = ellipsoid.point_at_latitude_vec(p_vect, d_vect, latitude, c_vect)

    # Error cases should produce nan
    assert np.all(np.isnan(pts[-1, :]))

    # Success cases should match the input latitude
    point_gp = ellipsoid.transform_vec(pts[:-1], ellipsoid.body_frame, None)
    assert np.allclose(point_gp[:, 0], latitude[:-1], rtol=0, atol=6.0e-15)


def test_point_at_latitude_issue1(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_latitude()"""

    init_orekit()

    position = np.array([-1988136.619268088, -2905373.394638188, 6231185.484365295])
    los = np.array([0.3489121277213534, 0.3447806500507106, -0.8714279261531437])
    close = np.array([-1709383.0948608494, -2630206.8820586684, 5535282.169189105])
    latitude = 1.0581058590215624

    s_vect = ellipsoid.point_at_latitude(position, los, latitude, close)
    point_gp = ellipsoid.transform_vec(s_vect, ellipsoid.body_frame, None)
    assert point_gp[0] == pytest.approx(latitude, abs=1.0e-15)


def test_point_at_altitude(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_altitude()"""

    init_orekit()

    p_vect = np.array([3220103.0, 69623.0, -6449822.0])
    d_vect = np.array([1.0, 2.0, 3.0])

    for altitude in np.arange(-500000, 800000.0, 100):
        point_gp = ellipsoid.transform_vec(
            ellipsoid.point_at_altitude(p_vect, d_vect, float(altitude)), ellipsoid.body_frame, None
        )

        assert point_gp[2] == pytest.approx(altitude, abs=1.0e-3)


def test_point_at_altitude_start_inside(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_altitude()"""

    init_orekit()

    p_vect = np.array([322010.30, 6962.30, -644982.20])
    d_vect = np.array([-1.0, -2.0, -3.0])

    for altitude in np.arange(-500000.0, 800000.0, 100):
        point_gp = ellipsoid.transform_vec(
            ellipsoid.point_at_altitude(p_vect, d_vect, float(altitude)), ellipsoid.body_frame, None
        )

        assert point_gp[2] == pytest.approx(altitude, abs=1.0e-3)


def test_point_at_altitude_error(ellipsoid):
    """Testing ExtendedEllipsoid.point_at_altitude()"""

    init_orekit()

    p_vect = np.array([3220103.0, 69623.0, -6449822.0])
    d_vect = np.array([1.0, 2.0, 3.0])
    altitude = -580000.0

    try:
        ellipsoid.point_at_altitude(p_vect, d_vect, altitude)
        pytest.fail("An error should have been triggered")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.LINE_OF_SIGHT_NEVER_CROSSES_ALTITUDE.value.format(altitude)


def test_convert_los(ellipsoid):
    """Testing ExtendedEllipsoid.convert_los()"""

    init_orekit()

    point_gp = np.array([[-0.2, 1.8, 2400.0]])
    point_p = ellipsoid.transform_vec(point_gp)
    los = np.array([[-1.0, -2.0, -3.0]])
    converted = ellipsoid.convert_los_from_point_vec(point_gp, los)
    line = Line(
        Vector3D(point_p[0].tolist()),
        Vector3D(compute_linear_combination_2(1.0, point_p[0], 1000.0, los[0]).tolist()),
        1.0e-10,
    )

    for delta in np.arange(0.1, 100.0, 0.1):
        shifted = np.array(
            [
                point_gp[0, 0] + float(delta) * converted[0, 0],
                point_gp[0, 1] + float(delta) * converted[0, 1],
                point_gp[0, 2] + float(delta) * converted[0, 2],
            ],
        )

        converted_2 = ellipsoid.convert_los_from_vector_vec(point_p, ellipsoid.transform_vec(shifted))
        assert distance(converted.T, converted_2.T) == pytest.approx(0.0, abs=3.0e-5 * get_norm(converted.T))
        assert line.distance(Vector3D(ellipsoid.transform_vec(shifted).tolist())) == pytest.approx(0.0, abs=8.0e-4)


def test_point_at_latitude_sar_vec(ellipsoid):
    """Test direct location vectorised for SAR"""

    pos_body = np.array(
        [
            [671337.06576085, -2401005.36995725, 6612027.16017191],
            [667195.62126813, -2422419.45435821, 6604647.07374154],
        ]
    )
    vel_body = np.array(
        [
            [-0.17950665, -0.93059144, -0.31902497],
            [-0.18021734, -0.92942658, -0.32200613],
        ]
    )

    range_dist = np.array(
        [
            880857.25658373,
            880857.25658373,
        ]
    )
    doppler_contribution = np.zeros(2, dtype="float64")
    altitudes = np.array([0.00012973077820577672, 29.99832155182921])
    is_right = True

    # Compute direct loc sar with vectorisation approach
    points_vec = ellipsoid.point_at_altitude_sar_vec(
        pos_body, vel_body, range_dist, is_right, doppler_contribution, altitudes
    )

    points_vec = points_vec[:, [1, 0, 2]]

    # Compute direct loc sar with point approach
    gnd = np.full((2, 3), np.nan, dtype="float64")
    for idx, (pos, vel, dist, alt) in enumerate(zip(pos_body, vel_body, range_dist, altitudes, strict=False)):
        points = ellipsoid.point_at_altitude_sar(
            pos,
            vel,
            dist,
            is_right,
            doppler_contribution[0],
            alt,
        )
        gnd[idx, :] = [points[1], points[0], points[2]]

    assert np.allclose(gnd, points_vec, rtol=0, atol=1e-8)


if __name__ == "__main__":

    # ExtendedEllipsoid().point_at_longitude() tests
    test_point_at_longitude(ellipsoid())
    test_point_at_longitude_error(ellipsoid())

    # ExtendedEllipsoid().point_at_latitude() tests
    test_point_at_latitude(ellipsoid())
    test_point_at_latitude_two_points_same_side(ellipsoid())
    test_point_at_latitude_two_points_opposite_side(ellipsoid())
    test_point_at_latitude_almost_equator(ellipsoid())
    test_point_at_latitude_error_quadratic_equation(ellipsoid())
    test_point_at_latitude_error_nappe(ellipsoid())
    test_point_at_latitude_error(ellipsoid())
    test_point_at_latitude_issue1(ellipsoid())

    # ExtendedEllipsoid().point_at_altitude() tests
    test_point_at_altitude_start_inside(ellipsoid())
    test_point_at_altitude_error(ellipsoid())
    test_point_at_altitude(ellipsoid())
    test_point_at_latitude_sar_vec(ellipsoid())
    # ExtendedEllipsoid().convert_los() test
    test_convert_los(ellipsoid())
