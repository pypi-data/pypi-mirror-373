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

"""Test for pyrugged tutorial"""
import numpy as np
import pytest
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.frames import FramesFactory
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import AngularDerivativesFilter, CartesianDerivativesFilter, IERSConventions

from pyrugged.bodies.body_rotating_frame_id import BodyRotatingFrameId
from pyrugged.bodies.ellipsoid_id import EllipsoidId
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.intersection_algorithm import create_intersection_algorithm
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.line_sensor.linear_line_datation import LinearLineDatation
from pyrugged.location.optical import OpticalLocation
from pyrugged.los.fixed_rotation import FixedRotation
from pyrugged.los.los_builder import LOSBuilder
from pyrugged.model.inertial_frame_id import InertialFrameId
from pyrugged.model.pyrugged_builder import PyRuggedBuilder
from tests import helpers


def build_test_sensor_and_location():
    """Set up a test line sensor and OpticalLocation instance for inverse/date location tests."""

    # Initialization
    init_orekit()

    # Line of sight
    raw_dirs = []
    for i in range(2000):
        raw_dirs.append(Vector3D(0.0, i * float(np.radians(20)) / 2000.0, 1.0))

    los_builder = LOSBuilder(raw_dirs)
    los_builder.add_ti_los_transform(FixedRotation("10-degrees-rotation", Vector3D.PLUS_I, float(np.radians(10))))

    line_of_sight = los_builder.build()

    # Datation model
    gps = TimeScalesFactory.getGPS()
    abs_date = AbsoluteDate("2009-12-11T16:59:30.0", gps)
    line_datation = LinearLineDatation(abs_date, 1.0, 20)

    # Line sensor
    line_sensor = LineSensor(
        "my-sensor",
        line_datation,
        Vector3D.ZERO,
        line_of_sight,
    )

    # Reference frames
    eme_2000 = FramesFactory.getEME2000()

    # We don't want to compute tiny tidal effects at millimeter level
    simple_eop = True

    itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, simple_eop)

    # Satellite attitude
    satellite_q_list = []

    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T16:58:42.592937", -0.340236, 0.333952, -0.844012, -0.245684
    )
    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T16:59:06.592937", -0.354773, 0.329336, -0.837871, -0.252281
    )
    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T16:59:30.592937", -0.369237, 0.324612, -0.831445, -0.258824
    )
    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T16:59:54.592937", -0.3836, 0.319792, -0.824743, -0.265299
    )
    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T17:00:18.592937", -0.397834, 0.314883, -0.817777, -0.271695
    )
    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T17:00:42.592937", -0.411912, 0.309895, -0.810561, -0.278001
    )
    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T17:01:06.592937", -0.42581, 0.304838, -0.803111, -0.284206
    )
    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T17:01:30.592937", -0.439505, 0.299722, -0.795442, -0.290301
    )
    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T17:01:54.592937", -0.452976, 0.294556, -0.787571, -0.296279
    )
    helpers.add_satellite_q(
        gps, satellite_q_list, "2009-12-11T17:02:18.592937", -0.466207, 0.28935, -0.779516, -0.302131
    )

    # Positions and velocities
    satellite_pv_list = []

    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T16:58:42.592937",
        -726361.466,
        -5411878.485,
        4637549.599,
        -2463.635,
        -4447.634,
        -5576.736,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T16:59:04.192937",
        -779538.267,
        -5506500.533,
        4515934.894,
        -2459.848,
        -4312.676,
        -5683.906,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T16:59:25.792937",
        -832615.368,
        -5598184.195,
        4392036.13,
        -2454.395,
        -4175.564,
        -5788.201,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T16:59:47.392937",
        -885556.748,
        -5686883.696,
        4265915.971,
        -2447.273,
        -4036.368,
        -5889.568,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T17:00:08.992937",
        -938326.32,
        -5772554.875,
        4137638.207,
        -2438.478,
        -3895.166,
        -5987.957,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T17:00:30.592937",
        -990887.942,
        -5855155.21,
        4007267.717,
        -2428.011,
        -3752.034,
        -6083.317,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T17:00:52.192937",
        -1043205.448,
        -5934643.836,
        3874870.441,
        -2415.868,
        -3607.05,
        -6175.6,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T17:01:13.792937",
        -1095242.669,
        -6010981.571,
        3740513.34,
        -2402.051,
        -3460.291,
        -6264.76,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T17:01:35.392937",
        -1146963.457,
        -6084130.93,
        3604264.372,
        -2386.561,
        -3311.835,
        -6350.751,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T17:01:56.992937",
        -1198331.706,
        -6154056.146,
        3466192.446,
        -2369.401,
        -3161.764,
        -6433.531,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        satellite_pv_list,
        "2009-12-11T17:02:18.592937",
        -1249311.381,
        -6220723.191,
        3326367.397,
        -2350.574,
        -3010.159,
        -6513.056,
    )

    # PyRugged initialization
    builder = PyRuggedBuilder()

    builder.set_ellipsoid(
        new_ellipsoid=None,
        ellipsoid_id=EllipsoidId.WGS84,
        body_rotating_frame_id=BodyRotatingFrameId.ITRF,
    )

    builder.set_time_span(abs_date, abs_date.shiftedBy(60.0), 0.01, 5 / line_sensor.get_rate(0))

    builder.set_trajectory(
        satellite_pv_list,
        4,
        CartesianDerivativesFilter.USE_P,
        satellite_q_list,
        4,
        AngularDerivativesFilter.USE_R,
        inertial_frame_id=InertialFrameId.EME2000,
    )

    builder.add_sensor(line_sensor)  # add_line_sensor

    rugged = builder.build()

    # Intersection initialization
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)

    location = OpticalLocation(rugged, intersection_algorithm)

    return line_sensor, location


def test_inverse_location():
    """Test inverse_location with a known geodetic point."""

    line_sensor, location = build_test_sensor_and_location()

    latitude = np.array([float(np.radians(37.5849))])
    longitude = np.array([float(np.radians(-96.9492))])
    altitude = np.array([0.0])

    # Interval of lines where to search the point
    min_line = 0
    max_line = 100

    # Inverse location of a geodetic point
    line, pixel = location.inverse_location(
        min_line, max_line, latitude, longitude, altitude, sensor_name=line_sensor.name
    )

    assert line[0] == pytest.approx(np.float64(0.0358326202592814), abs=9e-8)
    assert pixel[0] == pytest.approx(np.float64(0.012435517984594963), abs=5e-7)


def test_date_location():
    """Test date_location with a known geodetic point."""

    line_sensor, location = build_test_sensor_and_location()

    latitude = np.array([float(np.radians(37.5849))])
    longitude = np.array([float(np.radians(-96.9492))])
    altitude = np.array([0.0])

    # Interval of lines where to search the point
    min_line = 0
    max_line = 100

    # Date location
    date_line = location.date_location(min_line, max_line, latitude, longitude, altitude, sensor_name=line_sensor.name)

    assert date_line[0].toString().startswith("2009-12-11T16:59:14.951")


def test_inverse_location_without_altitude():
    """Test inverse_location when no altitude is explicitly provided."""

    line_sensor, location = build_test_sensor_and_location()

    latitude = np.array([float(np.radians(37.5849))])
    longitude = np.array([float(np.radians(-96.9492))])

    # Interval of lines where to search the point
    min_line = 0
    max_line = 100

    # Inverse location and date location without altitude
    line_without_altitude, pixel_without_altitude = location.inverse_location(
        min_line, max_line, latitude, longitude, sensor_name=line_sensor.name
    )
    assert line_without_altitude[0] == pytest.approx(np.float64(0.0358326202592814), abs=9e-8)
    assert pixel_without_altitude[0] == pytest.approx(np.float64(0.012435517984594963), abs=5e-7)


def test_date_location_without_altitude():
    """Test date_location when no altitude is explicitly provided."""

    line_sensor, location = build_test_sensor_and_location()

    latitude = np.array([float(np.radians(37.5849))])
    longitude = np.array([float(np.radians(-96.9492))])

    # Interval of lines where to search the point
    min_line = 0
    max_line = 100

    # Date location
    date_line_without_altitude = location.date_location(
        min_line, max_line, latitude, longitude, sensor_name=line_sensor.name
    )

    assert date_line_without_altitude[0].toString().startswith("2009-12-11T16:59:14.951")
