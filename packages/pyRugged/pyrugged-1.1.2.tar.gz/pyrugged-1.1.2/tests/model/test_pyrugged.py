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

"""Test for pyrugged Class PyRugged"""

import json

# pylint: disable=too-many-locals, too-many-lines
import os
import time
from tempfile import NamedTemporaryFile

import numpy as np
import pytest
from org.hipparchus.geometry import Vector
from org.hipparchus.geometry.euclidean.threed import Rotation, RotationConvention, Vector3D
from org.orekit.frames import FramesFactory
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import AngularDerivativesFilter, CartesianDerivativesFilter, IERSConventions

from pyrugged.bodies.body_rotating_frame_id import BodyRotatingFrameId
from pyrugged.bodies.ellipsoid_id import EllipsoidId
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.ignore_dem_algorithm import IgnoreDEMAlgorithm
from pyrugged.intersection.intersection_algorithm import create_intersection_algorithm
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.line_sensor.linear_line_datation import LinearLineDatation
from pyrugged.location.optical import CorrectionsParams, OpticalLocation
from pyrugged.los.fixed_rotation import FixedRotation
from pyrugged.los.los_builder import LOSBuilder
from pyrugged.model.inertial_frame_id import InertialFrameId
from pyrugged.model.pyrugged_builder import PyRuggedBuilder
from pyrugged.utils.coordinates_reader import extract_pv_from_txt, extract_q_from_txt
from pyrugged.utils.math_utils import distance, to_array_v  # pylint: disable=no-name-in-module
from tests import helpers
from tests.raster.random_landscape_updater import RandomLandscapeUpdater


def setup_module():
    """
    setup : initVM and reset DUMP_VAR
    """

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None

    init_orekit()


def teardown_module():
    """
    teardown : reset DUMP_VAR
    """
    dump_manager.DUMP_VAR = None


def json_precision(number_str):
    return round(float(number_str), 12)


@pytest.mark.order(1)
def test_light_time_correction(earth):
    """Test light time correction and dumping functionality"""

    # Ground truth for dumped data
    ground_truth_dump_file = os.path.join(
        os.path.dirname(__file__), "../data/ref/errors/dump_light_time_correction.json"
    )
    with open(ground_truth_dump_file, "r", encoding="utf-8") as dfile_orig:
        data_ground_truth = json.load(dfile_orig, parse_float=json_precision)

    with NamedTemporaryFile(suffix=".json", delete=True) as dump_file:
        # Dump activation
        dump_manager.DUMP_VAR = dump_manager.DumpManager()
        dump_manager.DUMP_VAR.activate(dump_file.name)
        try:
            dimension = 400
            los = helpers.create_los_perfect_line(
                Vector3D.PLUS_K,
                Vector3D.PLUS_I,
                float(np.radians(10)),
                dimension,
            ).build()

            ref_date = AbsoluteDate("2012-01-07T11:21:15.000", TimeScalesFactory.getUTC())

            # one line sensor
            # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
            position = Vector3D(1.5, 0.0, -0.2)

            ref_line = dimension / 2
            line_rate = 1.0 / 1.5e-3
            # Linear datation model: at reference time we get line 200, and the rate is one line every 1.5ms
            line_datation = LinearLineDatation(
                ref_date,
                ref_line,
                line_rate,
            )

            suffix = "2012-01-07T11h21m13.700Z_2012-01-07T11h21m16.300Z"
            rugged = helpers.configure_rugged(los, line_datation, dimension, position, suffix, EllipsoidId.IERS2003)

            line_sensor = rugged.get_sensor("line")

            try:
                rugged.get_sensor("dummy")
                pytest.fail("An exception should have been thrown")

            except PyRuggedError as pre:
                assert str(pre) == PyRuggedMessages.UNKNOWN_SENSOR.value.format("dummy")

            assert rugged.get_sc_to_inertial(
                line_sensor.get_date(dimension / 2)
            ).getTranslation().getNorm() == pytest.approx(7176419.526, abs=1.0e-3)
            assert rugged.get_body_to_inertial(
                line_sensor.get_date(dimension / 2)
            ).getTranslation().getNorm() == pytest.approx(0.0, abs=1.0e-3)
            assert rugged.get_inertial_to_body(
                line_sensor.get_date(dimension / 2)
            ).getTranslation().getNorm() == pytest.approx(0.0, abs=1.0e-3)

            # create an optical location model with light time correction activated
            correction_params = CorrectionsParams(True, False, None)
            intersection_algorithm = create_intersection_algorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)
            location = OpticalLocation(rugged, intersection_algorithm, correction_params)
            gp_with_light_time_correction = location.direct_location_of_sensor_line(200)

            # create an optical location model without any correction
            location.corrections_params = CorrectionsParams(False, False, None)
            gp_without_light_time_correction = location.direct_location_of_sensor_line(200)

            for index, (gp_lon, gp_lat, gp_alt) in enumerate(gp_with_light_time_correction):
                gp_without_lon, gp_without_lat, gp_without_alt = gp_without_light_time_correction[index]

                p_with = earth.transform_vec(np.array([gp_lat, gp_lon, gp_alt]))
                p_without = earth.transform_vec(np.array([gp_without_lat, gp_without_lon, gp_without_alt]))
                assert distance(p_with, p_without) > 1.23
                assert distance(p_with, p_without) < 1.27

            # Check if dumped data is correct
            with open(dump_file.name, "r+", encoding="utf-8") as dfile:
                data = json.load(dfile, parse_float=json_precision)

            def assert_nested_approx(actual, expected):
                if isinstance(expected, dict):
                    assert isinstance(actual, dict), f"Expected dict, got {type(actual)}"
                    assert actual.keys() == expected.keys(), "Dictionaries have different keys"
                    for key in expected:
                        assert_nested_approx(actual[key], expected[key])
                elif isinstance(expected, (list, tuple)):
                    assert len(actual) == len(expected), "Sequences have different lengths"
                    for actu, expect in zip(actual, expected):
                        assert_nested_approx(actu, expect)
                elif isinstance(expected, float):
                    assert actual == pytest.approx(expected, abs=1.0e-9)
                else:
                    assert actual == expected

            assert_nested_approx(data, data_ground_truth)

            # Dump deactivation
            dump_manager.DUMP_VAR = None
        # pylint: disable=broad-except
        except BaseException as exc:  # noqa: B036
            # Dump deactivation
            dump_manager.DUMP_VAR = None
            pytest.fail(exc, pytrace=True)


def test_aberration_of_light_correction(earth):
    """Test aberration of light correction"""

    dimension = 400

    # orbit = helpers.create_orbit(Constants.EIGEN5C_EARTH_MU)

    crossing = AbsoluteDate("2012-01-07T11:46:35.000", TimeScalesFactory.getUTC())

    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    #  los: swath in the (YZ) plane, centered at +Z, ±10° aperture, 960 pixels
    position = Vector3D(1.5, 0.0, -0.2)
    los = helpers.create_los_perfect_line(
        Vector3D.PLUS_K,
        Vector3D.PLUS_I,
        float(np.radians(10.0)),
        dimension,
    ).build()

    # linear datation model: at reference time we get line 200, and the rate is one line every 1.5ms
    line_datation = LinearLineDatation(
        crossing,
        dimension / 2,
        1.0 / 1.5e-3,
    )
    suffix = "2012-01-07T11h46m33.700Z_2012-01-07T11h46m36.300Z"
    rugged = helpers.configure_rugged(los, line_datation, dimension, position, suffix)

    correction_params = CorrectionsParams(False, True, None)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)

    location = OpticalLocation(rugged, intersection_algorithm, correction_params)

    gp_with_aberration_of_light_correction = location.direct_location_of_sensor_line(200)

    location.corrections_params = CorrectionsParams(False, False, None)

    gp_without_aberration_of_light_correction = location.direct_location_of_sensor_line(200)

    for index, (lon_corr, lat_corr, alt_corr) in enumerate(gp_with_aberration_of_light_correction):
        lon, lat, alt = gp_without_aberration_of_light_correction[index]
        p_with = earth.transform_vec(np.array([lat_corr, lon_corr, alt_corr]))
        p_without = earth.transform_vec(np.array([lat, lon, alt]))
        assert distance(p_with, p_without) > 20.0
        assert distance(p_with, p_without) < 20.5


def test_flat_body_correction(earth):
    """Test flat body correction"""

    dimension = 200

    crossing = AbsoluteDate("2012-01-01T12:30:00.000", TimeScalesFactory.getUTC())

    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    #  los: swath in the (YZ) plane, centered at +Z, ±10° aperture, 960 pixels
    position = Vector3D(1.5, 0.0, -0.2)
    los = helpers.create_los_perfect_line(
        Rotation(Vector3D.PLUS_I, float(np.radians(50.0)), RotationConvention.VECTOR_OPERATOR).applyTo(Vector3D.PLUS_K),
        Vector3D.PLUS_I,
        float(np.radians(1.0)),
        dimension,
    ).build()

    # linear datation model: at reference time we get line 200, and the rate is one line every 1.5ms
    line_datation = LinearLineDatation(
        crossing,
        dimension / 2,
        1.0 / 1.5e-3,
    )
    suffix = "2012-01-01T12h29m58.850Z_2012-01-01T12h30m01.150Z"
    rugged = helpers.configure_rugged(los, line_datation, dimension, position, suffix)

    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.5, 1234, float(np.radians(1.0)), 257)
    correction_params = CorrectionsParams(True, True, None)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    location = OpticalLocation(rugged, intersection_algorithm, correction_params)

    gp_with_flat_body_correction = location.direct_location_of_sensor_line(100, "line")
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE_FLAT_BODY, updater, 8)
    location = OpticalLocation(rugged, intersection_algorithm, correction_params)

    gp_without_flat_body_correction = location.direct_location_of_sensor_line(100)

    distance_values = []
    for index, (lon_corr, lat_corr, alt_corr) in enumerate(gp_with_flat_body_correction):
        lon, lat, alt = gp_without_flat_body_correction[index]
        p_with = earth.transform_vec(np.array([lat_corr, lon_corr, alt_corr]))
        p_without = earth.transform_vec(np.array([lat, lon, alt]))
        distance_values.append(distance(p_with, p_without))

    assert min(distance_values) == pytest.approx(4.494, abs=1.0e-3)
    assert max(distance_values) == pytest.approx(74.546, abs=1.0e-3)
    assert np.mean(distance_values) == pytest.approx(10.608, abs=1.0e-3)


def configure_default_rugged():
    """
    Default configuration for rugged
    """
    dimension = 200

    crossing = AbsoluteDate("2012-01-01T12:30:00.000", TimeScalesFactory.getUTC())

    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    #  los: swath in the (YZ) plane, centered at +Z, ±10° aperture, 960 pixels
    position = Vector3D(1.5, 0.0, -0.2)
    los = helpers.create_los_perfect_line(
        Rotation(Vector3D.PLUS_I, float(np.radians(50.0)), RotationConvention.VECTOR_OPERATOR).applyTo(Vector3D.PLUS_K),
        Vector3D.PLUS_I,
        float(np.radians(1.0)),
        dimension,
    ).build()

    # linear datation model: at reference time we get line 200, and the rate is one line every 1.5ms
    line_datation = LinearLineDatation(
        crossing,
        dimension / 2,
        1.0 / 1.5e-3,
    )
    suffix = "2012-01-01T12h29m57.850Z_2012-01-01T12h30m02.150Z"
    rugged = helpers.configure_rugged(los, line_datation, dimension, position, suffix)

    line_sensor = rugged.get_sensor("line")
    return rugged, line_sensor


def test_location_los_single_point():
    """Test location of a single point"""
    rugged, line_sensor = configure_default_rugged()

    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.5, 1234, float(np.radians(1.0)), 257)
    correction_params = CorrectionsParams(True, True, None)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    location = OpticalLocation(rugged, intersection_algorithm, correction_params)

    gp_line = location.direct_location_of_sensor_line(100)

    for index, (gp_longitude, gp_latitude, gp_altitude) in enumerate(gp_line):
        longitude, latitude, altitude = location.direct_location_of_los(
            line_sensor.get_date(100), line_sensor.position, line_sensor.get_los(line_sensor.get_date(100), index)
        )
        assert latitude == pytest.approx(gp_latitude, abs=1.0e-10)
        assert longitude == pytest.approx(gp_longitude, abs=1.0e-10)
        assert altitude == pytest.approx(gp_altitude, abs=1.0e-8)


@pytest.mark.perf
def test_location_timing():
    """timing"""

    # pr = cProfile.Profile()
    # pr.enable()
    # profiler = Profile()

    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.5, 1234, float(np.radians(1.0)), 257)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    corrections_params = CorrectionsParams(False, False, None)
    perform_location_timing(intersection_algorithm, corrections_params)

    corrections_params = CorrectionsParams(True, True, None)
    perform_location_timing(intersection_algorithm, corrections_params)

    intersection_algorithm = create_intersection_algorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)

    corrections_params = CorrectionsParams(False, False, None)
    perform_location_timing(intersection_algorithm, corrections_params)

    corrections_params = CorrectionsParams(True, True, None)
    perform_location_timing(intersection_algorithm, corrections_params)

    intersection_algorithm = create_intersection_algorithm(
        AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID, constant_elevation=10.0
    )

    corrections_params = CorrectionsParams(False, False, None)
    perform_location_timing(intersection_algorithm, corrections_params)

    corrections_params = CorrectionsParams(True, True, None)
    perform_location_timing(intersection_algorithm, corrections_params)

    # pr.disable()
    # s = io.StringIO()
    # sortby = SortKey.TIME
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())


# pylint: disable=singleton-comparison
def perform_location_timing(intersection_algorithm, corrections_params):
    """Test  location timing"""

    t_0 = time.time()
    dimension = 2000
    nb_sensors = 3

    crossing = AbsoluteDate("2012-01-01T12:30:00.000", TimeScalesFactory.getUTC())

    sensors = []
    for index in range(nb_sensors):
        # one line sensor
        # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
        # los: swath in the (YZ) plane, looking roughly at 50° roll (sensor-dependent), 5.2" per pixel
        position = Vector3D(1.5, 0.0, -0.2)
        los = helpers.create_los_perfect_line(
            Rotation(
                Vector3D.PLUS_I, float(np.radians(50.0 - 0.001 * index)), RotationConvention.VECTOR_OPERATOR
            ).applyTo(Vector3D.PLUS_K),
            Vector3D.PLUS_I,
            float(np.radians((dimension / 2.0) * 5.2 / 3600.0)),
            dimension,
        ).build()

        # linear datation model: at reference time we get roughly middle line, and the rate is one line every 1.5ms
        line_datation = LinearLineDatation(
            crossing,
            index + dimension / 2,
            1.0 / 1.5e-3,
        )
        sensors.append(LineSensor(f'{"line-"}{index}', line_datation, to_array_v(position.toArray()), los))

    first_line = 0
    last_line = dimension
    min_date = sensors[0].get_date(first_line).shiftedBy(-1.0)
    max_date = sensors[-1].get_date(last_line).shiftedBy(1.0)

    pv_file_path = os.path.join(
        os.path.dirname(__file__),
        "../data/ref/api/testRuggedAPI_pv_2012-01-01T12h29m57.850Z_2012-01-01T12h30m02.150Z.txt",
    )
    q_file_path = os.path.join(
        os.path.dirname(__file__),
        "../data/ref/api/testRuggedAPI_q_2012-01-01T12h29m57.850Z_2012-01-01T12h30m02.150Z.txt",
    )

    pv_list = extract_pv_from_txt(pv_file_path)
    q_list = extract_q_from_txt(q_file_path)

    builder = PyRuggedBuilder()
    builder.set_ellipsoid(
        new_ellipsoid=None, ellipsoid_id=EllipsoidId.WGS84, body_rotating_frame_id=BodyRotatingFrameId.ITRF
    )
    builder.set_time_span(min_date, max_date, 0.001, 5.0)
    builder.set_trajectory(
        pv_list,
        8,
        CartesianDerivativesFilter.USE_PV,
        q_list,
        2,
        AngularDerivativesFilter.USE_R,
        inertial_frame_id=InertialFrameId.EME2000,
    )

    for line_sensor in sensors:
        builder.add_sensor(line_sensor)

    rugged = builder.build()

    location = OpticalLocation(rugged, intersection_algorithm, corrections_params)

    size = 500
    seed = 10
    lines = np.random.RandomState(seed).rand(size) * dimension  # pylint: disable=no-member
    pixels = np.random.RandomState(seed).rand(size) * dimension  # pylint: disable=no-member
    results_dir_loc = []
    t_1 = time.time()
    for line_sensor in sensors:
        lonlatalt = location.direct_location(lines, pixels, sensor_name=line_sensor.name)
        results_dir_loc.append(lonlatalt)
    t_2 = time.time()
    good_pixels = 0
    bad_pixels = 0
    for line_sensor in sensors:
        lon, lat, alt = results_dir_loc.pop(0)
        lines_inv, pixels_inv = location.inverse_location(
            first_line, last_line, lat, lon, alt, sensor_name=line_sensor.name
        )

        bad_pixel = np.sum(np.logical_or(np.array(lines_inv) == None, np.array(pixels_inv) == None))  # noqa: E711
        good_pixel = len(lines) - bad_pixel
        good_pixels += good_pixel
        bad_pixels += bad_pixel

    t_3 = time.time()
    assert bad_pixels == 0
    print("Corrections Params : ", corrections_params)
    print("Intersection Algorithm  : ", intersection_algorithm.algorithm_id)
    print("\n\n%5d, %d sensors:\n" % (size, nb_sensors))
    print("   Orekit initialization and DEM creation   : %5.1fs\n" % (t_1 - t_0))
    print(
        "   Direct location : %5.7fs (%.1f px/s, %.1f%% covered)\n"
        % (
            t_2 - t_1,
            (bad_pixels + good_pixels) / (t_2 - t_1),
            (100.0 * good_pixels) / (good_pixels + bad_pixels),
        )
    )
    print(
        "   Inverse location : %5.7fs (%.1f px/s, %.1f%% covered)\n"
        % (
            t_3 - t_2,
            (bad_pixels + good_pixels) / (t_3 - t_2),
            (100.0 * good_pixels) / (good_pixels + bad_pixels),
        )
    )


def test_location_multiple_points():
    """Test location of multiple points"""
    rugged, line_sensor = configure_default_rugged()
    dimension = 200
    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.5, 1234, float(np.radians(1.0)), 257)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    location = OpticalLocation(rugged, intersection_algorithm)

    nb_samples = 11
    lines_linspace = np.linspace(0, dimension, nb_samples)
    pixels_linspace = np.linspace(0, dimension, nb_samples)

    lines, pixels = np.meshgrid(lines_linspace, pixels_linspace)

    lines = lines.flatten()
    pixels = pixels.flatten()

    longitudes, latitudes, altitudes = location.direct_location(lines, pixels)

    assert len(longitudes) == nb_samples**2

    longitude, latitude, altitude = location.direct_location_of_los(
        line_sensor.get_date(100), line_sensor.position, line_sensor.get_los(line_sensor.get_date(100), 100)
    )
    assert latitude == pytest.approx(latitudes[60], abs=1.0e-8)
    assert longitude == pytest.approx(longitudes[60], abs=1.0e-8)
    assert altitude == pytest.approx(altitudes[60], abs=1.0e-2)


def test_location_single_point_no_corrections():
    """Test location of single point without corrections"""
    rugged, line_sensor = configure_default_rugged()

    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.5, 1234, float(np.radians(1.0)), 257)
    correction_params = CorrectionsParams(False, False, None)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    location = OpticalLocation(rugged, intersection_algorithm, correction_params)

    gp_line = location.direct_location_of_sensor_line(100)

    for index, (gp_longitude, gp_latitude, gp_altitude) in enumerate(gp_line):
        longitude, latitude, altitude = location.direct_location_of_los(
            line_sensor.get_date(100), line_sensor.position, line_sensor.get_los(line_sensor.get_date(100), index)
        )
        assert latitude == pytest.approx(gp_latitude, abs=1.0e-10)
        assert longitude == pytest.approx(gp_longitude, abs=1.0e-10)
        assert altitude == pytest.approx(gp_altitude, abs=1.0e-8)


def test_location_single_point_ellipsoid_no_corrections_10deg_rotation():
    """Test location single point ellipsoid no corrections"""

    dimension = 200

    # earth = test_utils.create_earth()
    # orbit = test_utils.create_orbit(Constants.EIGEN5C_EARTH_MU)

    crossing = AbsoluteDate("2012-01-01T12:30:00.000", TimeScalesFactory.getUTC())

    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    # los: swath in the (YZ) plane, looking at 50° roll, ±1° aperture
    position = Vector3D(1.5, 0.0, -0.2)
    losbuilder = helpers.create_los_perfect_line(
        Rotation(Vector3D.PLUS_I, float(np.radians(50.0)), RotationConvention.VECTOR_OPERATOR).applyTo(Vector3D.PLUS_K),
        Vector3D.PLUS_I,
        float(np.radians(1.0)),
        dimension,
    )
    losbuilder.add_los_transform(FixedRotation("10-degrees-rotation", Vector3D.PLUS_I, np.radians(10.0)))
    los = losbuilder.build()

    # linear datation model: at reference time we get line 100, and the rate is one line every 1.5ms
    line_datation = LinearLineDatation(crossing, dimension / 2, 1.0 / 1.5e-3)

    suffix = "2012-01-01T12h29m57.850Z_2012-01-01T12h30m02.150Z"
    rugged = helpers.configure_rugged(los, line_datation, dimension, position, suffix)

    line_sensor = rugged.get_sensor("line")
    correction_params = CorrectionsParams(False, False, None)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)

    location = OpticalLocation(rugged, intersection_algorithm, correction_params)

    gp_line = location.direct_location_of_sensor_line(100)
    assert gp_line[0][1] == pytest.approx(-0.41067609982495257, abs=2.0e-10)
    assert gp_line[0][0] == pytest.approx(2.3743204725736162, abs=1.0e-10)
    assert gp_line[0][2] == pytest.approx(0.0, abs=1.0e-6)
    assert gp_line[dimension - 1][1] == pytest.approx(-0.4162525611632697, abs=2.0e-10)
    assert gp_line[dimension - 1][0] == pytest.approx(2.3141448366516313, abs=1.0e-10)
    assert gp_line[dimension - 1][2] == pytest.approx(0.0, abs=1.0e-6)

    for index, (gp_longitude, gp_latitude, gp_altitude) in enumerate(gp_line):
        longitude, latitude, altitude = location.direct_location_of_los(
            line_sensor.get_date(100), line_sensor.position, line_sensor.get_los(line_sensor.get_date(100), index)
        )
        assert latitude == pytest.approx(gp_latitude, abs=1.0e-10)
        assert longitude == pytest.approx(gp_longitude, abs=1.0e-10)
        assert altitude == pytest.approx(gp_altitude, abs=1.0e-10)

    intersection_algorithm = create_intersection_algorithm(
        AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID, constant_elevation=0.0
    )

    location = OpticalLocation(rugged, intersection_algorithm, correction_params)

    gp_line_constant = location.direct_location_of_sensor_line(100)
    assert gp_line_constant[0][1] == pytest.approx(-0.41067609982495257, abs=2.0e-10)
    assert gp_line_constant[0][0] == pytest.approx(2.3743204725736162, abs=2.0e-10)
    assert gp_line_constant[0][2] == pytest.approx(0.0, abs=2.0e-4)
    assert gp_line_constant[dimension - 1][1] == pytest.approx(-0.4162525611632697, abs=2.0e-10)
    assert gp_line_constant[dimension - 1][0] == pytest.approx(2.3141448366516313, abs=1.0e-10)
    assert gp_line_constant[dimension - 1][2] == pytest.approx(0.0, abs=1.0e-6)


def test_location_single_point_ellipsoid_no_corrections():
    """Test location single point ellipsoid no corrections"""
    rugged, line_sensor = configure_default_rugged()
    dimension = 200
    correction_params = CorrectionsParams(False, False, None)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)

    location = OpticalLocation(rugged, intersection_algorithm, correction_params)

    gp_line = location.direct_location_of_sensor_line(100)
    assert gp_line[0][1] == pytest.approx(-0.39474270849103016, abs=2.0e-09)
    assert gp_line[0][0] == pytest.approx(2.4992200319175386, abs=1.0e-10)
    assert gp_line[0][2] == pytest.approx(0.0, abs=1.0e-6)
    assert gp_line[dimension - 1][1] == pytest.approx(-0.39712879399305245, abs=2.0e-10)
    assert gp_line[dimension - 1][0] == pytest.approx(2.4831039080253965, abs=6.0e-11)
    assert gp_line[dimension - 1][2] == pytest.approx(0.0, abs=1.0e-6)

    for index, (gp_longitude, gp_latitude, gp_altitude) in enumerate(gp_line):
        longitude, latitude, altitude = location.direct_location_of_los(
            line_sensor.get_date(100), line_sensor.position, line_sensor.get_los(line_sensor.get_date(100), index)
        )
        assert latitude == pytest.approx(gp_latitude, abs=1.0e-10)
        assert longitude == pytest.approx(gp_longitude, abs=1.0e-10)
        assert altitude == pytest.approx(gp_altitude, abs=1.0e-10)

    intersection_algorithm = create_intersection_algorithm(
        AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID, constant_elevation=0.0
    )

    location.algorithm = intersection_algorithm

    gp_line_constant = location.direct_location_of_sensor_line(100)
    assert gp_line_constant[0][1] == pytest.approx(-0.39474270849103016, abs=2.0e-10)
    assert gp_line_constant[0][0] == pytest.approx(2.4992200319175386, abs=1.0e-10)
    assert gp_line_constant[0][2] == pytest.approx(0.0, abs=1.0e-5)
    assert gp_line_constant[dimension - 1][1] == pytest.approx(-0.39712879399305245, abs=2.0e-10)
    assert gp_line_constant[dimension - 1][0] == pytest.approx(2.4831039080253965, abs=6.0e-11)
    assert gp_line_constant[dimension - 1][2] == pytest.approx(0.0, abs=1.0e-5)


def test_basic_scan(earth):
    """Test of exhaustive basic scan algorithm,
    and comparison with Duvenhage algorithm
    """

    rugged, _ = configure_default_rugged()

    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.5, 1234, float(np.radians(1.0)), 257)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    location = OpticalLocation(rugged, intersection_algorithm)

    gp_duvenhage = location.direct_location_of_sensor_line(100)
    intersection_algorithm = create_intersection_algorithm(
        AlgorithmId.BASIC_SLOW_EXHAUSTIVE_SCAN_FOR_TESTS_ONLY, updater, 8
    )

    location.algorithm = intersection_algorithm
    gp_basic_scan = location.direct_location_of_sensor_line(100)

    data = [None] * len(gp_duvenhage)
    for index, (lon_duv, lat_duv, alt_duv) in enumerate(gp_duvenhage):
        lon_basic, lat_basic, alt_basic = gp_basic_scan[index]
        p_duvenhage = earth.transform_vec(np.array([lat_duv, lon_duv, alt_duv]))
        p_basic_scan = earth.transform_vec(np.array([lat_basic, lon_basic, alt_basic]))
        data[index] = distance(p_duvenhage, p_basic_scan)

    assert np.percentile(data, 99) == pytest.approx(0.0, abs=5.1e-4)


def test_inverse_location():
    """Test inverse location"""

    check_inverse_location(2000, False, False, 4.0e-7, 5.0e-6)
    check_inverse_location(2000, False, True, 1.0e-5, 2.0e-7)
    check_inverse_location(2000, True, False, 4.0e-7, 4.0e-7)
    check_inverse_location(2000, True, True, 2.0e-5, 3.0e-7)


def test_date_location():
    """Test date location"""

    check_date_location(200, False, False, 7.0e-7)
    check_date_location(200, False, True, 2.0e-5)
    check_date_location(200, True, False, 8.0e-7)
    check_date_location(200, True, True, 3.0e-6)


def test_line_datation():
    """Test line datation"""

    check_line_datation(2000, 7.0e-7)
    check_line_datation(10000, 8.0e-7)


def test_inverse_loc_near_line_end():
    """Test inverse location near line end"""

    offset = Vector3D.ZERO
    gps = TimeScalesFactory.getGPS()
    eme2000 = FramesFactory.getEME2000()
    itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

    pv_list = []
    q_list = []

    helpers.add_satellite_q(gps, q_list, "2009-12-11T16:58:42.592937", -0.340236, 0.333952, -0.844012, -0.245684)
    helpers.add_satellite_q(gps, q_list, "2009-12-11T16:59:06.592937", -0.354773, 0.329336, -0.837871, -0.252281)
    helpers.add_satellite_q(gps, q_list, "2009-12-11T16:59:30.592937", -0.369237, 0.324612, -0.831445, -0.258824)
    helpers.add_satellite_q(gps, q_list, "2009-12-11T16:59:54.592937", -0.3836, 0.319792, -0.824743, -0.265299)
    helpers.add_satellite_q(gps, q_list, "2009-12-11T17:00:18.592937", -0.397834, 0.314883, -0.817777, -0.271695)
    helpers.add_satellite_q(gps, q_list, "2009-12-11T17:00:42.592937", -0.411912, 0.309895, -0.810561, -0.278001)
    helpers.add_satellite_q(gps, q_list, "2009-12-11T17:01:06.592937", -0.42581, 0.304838, -0.803111, -0.284206)
    helpers.add_satellite_q(gps, q_list, "2009-12-11T17:01:30.592937", -0.439505, 0.299722, -0.795442, -0.290301)
    helpers.add_satellite_q(gps, q_list, "2009-12-11T17:01:54.592937", -0.452976, 0.294556, -0.787571, -0.296279)
    helpers.add_satellite_q(gps, q_list, "2009-12-11T17:02:18.592937", -0.466207, 0.28935, -0.779516, -0.302131)

    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T16:58:42.592937",
        -726361.466,
        -5411878.485,
        4637549.599,
        -2068.995,
        -4500.601,
        -5576.736,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T16:59:04.192937",
        -779538.267,
        -5506500.533,
        4515934.894,
        -2058.308,
        -4369.521,
        -5683.906,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T16:59:25.792937",
        -832615.368,
        -5598184.195,
        4392036.13,
        -2046.169,
        -4236.279,
        -5788.201,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T16:59:47.392937",
        -885556.748,
        -5686883.696,
        4265915.971,
        -2032.579,
        -4100.944,
        -5889.568,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T17:00:08.992937",
        -938326.32,
        -5772554.875,
        4137638.207,
        -2017.537,
        -3963.59,
        -5987.957,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T17:00:30.592937",
        -990887.942,
        -5855155.21,
        4007267.717,
        -2001.046,
        -3824.291,
        -6083.317,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T17:00:52.192937",
        -1043205.448,
        -5934643.836,
        3874870.441,
        -1983.107,
        -3683.122,
        -6175.6,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T17:01:13.792937",
        -1095242.669,
        -6010981.571,
        3740513.34,
        -1963.723,
        -3540.157,
        -6264.76,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T17:01:35.392937",
        -1146963.457,
        -6084130.93,
        3604264.372,
        -1942.899,
        -3395.473,
        -6350.751,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T17:01:56.992937",
        -1198331.706,
        -6154056.146,
        3466192.446,
        -1920.64,
        -3249.148,
        -6433.531,
    )
    helpers.add_satellite_pv(
        gps,
        eme2000,
        itrf,
        pv_list,
        "2009-12-11T17:02:18.592937",
        -1249311.381,
        -6220723.191,
        3326367.397,
        -1896.952,
        -3101.26,
        -6513.056,
    )

    builder = PyRuggedBuilder()
    builder.set_ellipsoid(
        new_ellipsoid=None, ellipsoid_id=EllipsoidId.WGS84, body_rotating_frame_id=BodyRotatingFrameId.ITRF
    )
    builder.set_time_span(pv_list[0].getDate(), pv_list[-1].getDate(), 0.001, 5.0)
    builder.set_trajectory(
        pv_list,
        8,
        CartesianDerivativesFilter.USE_PV,
        q_list,
        8,
        AngularDerivativesFilter.USE_R,
        inertial_frame_id=InertialFrameId.EME2000,
    )

    line_of_sight = []

    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181530, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181518, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181505, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181492, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181480, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181467, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181455, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181442, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181430, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181417, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181405, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.181392, 1.0)).normalize()))

    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149762, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149749, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149737, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149724, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149712, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149699, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149686, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149674, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149661, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149649, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149636, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149624, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149611, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149599, 1.0)).normalize()))
    line_of_sight.append(Vector3D.cast_(Vector.cast_(Vector3D(-0.011204, 0.149586, 1.0)).normalize()))

    abs_date = AbsoluteDate("2009-12-11T16:58:51.593", gps)
    line_datation = LinearLineDatation(abs_date, 1.0, 638.5696040868454)
    line_sensor = LineSensor("perfect-line", line_datation, offset, LOSBuilder(line_of_sight).build())

    builder.add_sensor(line_sensor)

    rugged = builder.build()

    corrections_params = CorrectionsParams(True, True, None)
    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.5, 1234, float(np.radians(1.0)), 257)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    location = OpticalLocation(rugged, intersection_algorithm, corrections_params)

    point_1 = np.array([0.7053784581520293, -1.7354535645320581, 691.856741468848])
    sensor_pixel_1 = location.inverse_location(1, 131328, [point_1[0]], [point_1[1]], [point_1[2]])
    assert sensor_pixel_1[0][0] == pytest.approx(2.291809, abs=1.0e-5)
    assert sensor_pixel_1[1][0] == pytest.approx(1.582062, abs=1.0e-5)

    point_2 = np.array([0.704463899881073, -1.7303503789334154, 648.9200602492216])
    sensor_pixel_2 = location.inverse_location(1, 131328, [point_2[0]], [point_2[1]], [point_2[2]])
    assert sensor_pixel_2[0][0] == pytest.approx(2.281645, abs=1.0e-5)
    assert sensor_pixel_2[1][0] == pytest.approx(27.024577, abs=1.0e-5)

    point_3 = np.array([0.7009593480939814, -1.7314283804521957, 588.3075485689468])
    sensor_pixel_3 = location.inverse_location(1, 131328, [point_3[0]], [point_3[1]], [point_3[2]])
    assert sensor_pixel_3[0][0] == pytest.approx(2305.52854, abs=1.0e-5)
    assert sensor_pixel_3[1][0] == pytest.approx(26.673220, abs=1.0e-5)

    point_4 = np.array([0.7018731669637096, -1.73651769725183, 611.2759403696498])
    sensor_pixel_4 = location.inverse_location(1, 131328, [point_4[0]], [point_4[1]], [point_4[2]])
    assert sensor_pixel_4[0][0] == pytest.approx(2305.539102, abs=1.0e-5)
    assert sensor_pixel_4[1][0] == pytest.approx(1.028736, abs=1.0e-5)


def test_inverse_loc():
    """Test inverse location"""

    offset = Vector3D.ZERO
    gps = TimeScalesFactory.getGPS()
    eme_2000 = FramesFactory.getEME2000()
    itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

    satellite_q_list = []
    pv_list = []

    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:27", -0.327993, -0.715194, -0.56313, 0.252592)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:29", -0.328628, -0.71494, -0.562769, 0.25329)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:31", -0.329263, -0.714685, -0.562407, 0.253988)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:33", -0.329898, -0.714429, -0.562044, 0.254685)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:35", -0.330532, -0.714173, -0.561681, 0.255383)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:37", -0.331166, -0.713915, -0.561318, 0.256079)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:39", -0.3318, -0.713657, -0.560954, 0.256776)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:41", -0.332434, -0.713397, -0.560589, 0.257472)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:43", -0.333067, -0.713137, -0.560224, 0.258168)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:16:45", -0.333699, -0.712876, -0.559859, 0.258864)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:18:17", -0.36244, -0.699935, -0.542511, 0.290533)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:27", -0.401688, -0.678574, -0.516285, 0.334116)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:29", -0.402278, -0.678218, -0.515866, 0.334776)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:31", -0.402868, -0.677861, -0.515447, 0.335435)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:33", -0.403457, -0.677503, -0.515028, 0.336093)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:35", -0.404046, -0.677144, -0.514608, 0.336752)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:37", -0.404634, -0.676785, -0.514187, 0.337409)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:39", -0.405222, -0.676424, -0.513767, 0.338067)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:41", -0.40581, -0.676063, -0.513345, 0.338724)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:43", -0.406397, -0.675701, -0.512924, 0.339381)
    helpers.add_satellite_q(gps, satellite_q_list, "2013-07-07T17:20:45", -0.406983, -0.675338, -0.512502, 0.340038)

    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:16:27.857531",
        -379110.393,
        -5386317.278,
        4708158.61,
        -1802.078,
        -4690.847,
        -5512.223,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:16:36.857531",
        -398874.476,
        -5428039.968,
        4658344.906,
        -1801.326,
        -4636.91,
        -5557.915,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:16:45.857531",
        -418657.992,
        -5469262.453,
        4608122.145,
        -1800.345,
        -4582.57,
        -5603.119,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:16:54.857531",
        -438458.554,
        -5509981.109,
        4557494.737,
        -1799.136,
        -4527.831,
        -5647.831,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:17:03.857531",
        -458273.771,
        -5550192.355,
        4506467.128,
        -1797.697,
        -4472.698,
        -5692.046,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:17:12.857531",
        -478101.244,
        -5589892.661,
        4455043.798,
        -1796.029,
        -4417.176,
        -5735.762,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:17:21.857531",
        -497938.57,
        -5629078.543,
        4403229.263,
        -1794.131,
        -4361.271,
        -5778.975,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:17:30.857531",
        -517783.34,
        -5667746.565,
        4351028.073,
        -1792.003,
        -4304.987,
        -5821.679,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:17:39.857531",
        -537633.139,
        -5705893.34,
        4298444.812,
        -1789.644,
        -4248.329,
        -5863.873,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:17:48.857531",
        -557485.549,
        -5743515.53,
        4245484.097,
        -1787.055,
        -4191.304,
        -5905.552,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:17:57.857531",
        -577338.146,
        -5780609.846,
        4192150.579,
        -1784.234,
        -4133.916,
        -5946.712,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:18:06.857531",
        -597188.502,
        -5817173.047,
        4138448.941,
        -1781.183,
        -4076.171,
        -5987.35,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:18:15.857531",
        -617034.185,
        -5853201.943,
        4084383.899,
        -1777.899,
        -4018.073,
        -6027.462,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:18:24.857531",
        -636872.759,
        -5888693.393,
        4029960.2,
        -1774.385,
        -3959.629,
        -6067.045,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:18:33.857531",
        -656701.786,
        -5923644.307,
        3975182.623,
        -1770.638,
        -3900.844,
        -6106.095,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:18:42.857531",
        -676518.822,
        -5958051.645,
        3920055.979,
        -1766.659,
        -3841.723,
        -6144.609,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:18:51.857531",
        -696321.424,
        -5991912.417,
        3864585.108,
        -1762.449,
        -3782.271,
        -6182.583,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:19:00.857531",
        -716107.143,
        -6025223.686,
        3808774.881,
        -1758.006,
        -3722.495,
        -6220.015,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:19:09.857531",
        -735873.528,
        -6057982.563,
        3752630.2,
        -1753.332,
        -3662.399,
        -6256.9,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:19:18.857531",
        -755618.129,
        -6090186.214,
        3696155.993,
        -1748.425,
        -3601.99,
        -6293.236,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:19:27.857531",
        -775338.49,
        -6121831.854,
        3639357.221,
        -1743.286,
        -3541.272,
        -6329.019,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:19:36.857531",
        -795032.157,
        -6152916.751,
        3582238.87,
        -1737.915,
        -3480.252,
        -6364.246,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:19:45.857531",
        -814696.672,
        -6183438.226,
        3524805.957,
        -1732.313,
        -3418.935,
        -6398.915,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:19:54.857531",
        -834329.579,
        -6213393.652,
        3467063.525,
        -1726.478,
        -3357.327,
        -6433.022,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:20:03.857531",
        -853928.418,
        -6242780.453,
        3409016.644,
        -1720.412,
        -3295.433,
        -6466.563,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:20:12.857531",
        -873490.732,
        -6271596.108,
        3350670.411,
        -1714.114,
        -3233.259,
        -6499.537,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:20:21.857531",
        -893014.061,
        -6299838.148,
        3292029.951,
        -1707.585,
        -3170.811,
        -6531.941,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:20:30.857531",
        -912495.948,
        -6327504.159,
        3233100.411,
        -1700.825,
        -3108.095,
        -6563.77,
    )
    helpers.add_satellite_pv(
        gps,
        eme_2000,
        itrf,
        pv_list,
        "2013-07-07T17:20:39.857531",
        -931933.933,
        -6354591.778,
        3173886.968,
        -1693.833,
        -3045.116,
        -6595.024,
    )

    line_of_sight = []
    line_of_sight.append(Vector3D(0.0046536264, -0.1851800945, 1.0))
    line_of_sight.append(Vector3D(0.0000001251, -0.0002815246, 1.0))
    line_of_sight.append(Vector3D(0.0046694108, 0.1853863933, 1.0))

    abs_date = AbsoluteDate("2013-07-07T17:16:36.857", gps)
    line_datation = LinearLineDatation(abs_date, 0.03125, 19.95565693384045)
    line_sensor = LineSensor("QUICK_LOOK", line_datation, offset, LOSBuilder(line_of_sight).build())

    rugged_builder = PyRuggedBuilder()
    rugged_builder.set_ellipsoid(
        new_ellipsoid=None, ellipsoid_id=EllipsoidId.WGS84, body_rotating_frame_id=BodyRotatingFrameId.ITRF
    )
    rugged_builder.set_time_span(pv_list[0].getDate(), pv_list[-1].getDate(), 0.1, 10.0)
    rugged_builder.set_trajectory(
        pv_list,
        6,
        CartesianDerivativesFilter.USE_P,
        satellite_q_list,
        8,
        AngularDerivativesFilter.USE_R,
        inertial_frame_id=InertialFrameId.EME2000,
    )
    rugged_builder.add_sensor(line_sensor)

    rugged = rugged_builder.build()

    intersection_algorithm = create_intersection_algorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)
    location = OpticalLocation(rugged, intersection_algorithm)

    temp = location.direct_location_of_sensor_line(-250)
    min_lon, min_lat, _ = temp[0]

    temp = location.direct_location_of_sensor_line(350)
    max_lon, max_lat, _ = temp[-1]

    lat = (min_lat + max_lat) / 2.0
    lon = (min_lon + max_lon) / 2.0
    alt = 0.0
    sensor_pixel = location.inverse_location(-250, 350, np.array([lat]), np.array([lon]), np.array([alt]))

    assert sensor_pixel[0][0] is not None

    assert not location.pixel_is_inside((-100, -100), line_sensor)
    assert not location.pixel_is_inside((-100, 100), line_sensor)
    assert not location.pixel_is_inside((100, -100), line_sensor)
    assert not location.pixel_is_inside((100, 100), line_sensor)
    assert location.pixel_is_inside((0.2, 0.3), line_sensor)


def test_inverse_loc_curved_line():
    """Test inverse location with curved line"""
    # orbit = helpers.create_orbit(Constants.EIGEN5C_EARTH_MU)

    crossing = AbsoluteDate("2012-01-01T12:30:00.000", TimeScalesFactory.getUTC())
    dimension = 200
    first_line = 0
    last_line = dimension
    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    # los: swath in the (YZ) plane, looking at nadir, 5.2" per pixel, 3" sagitta
    position = Vector3D(1.5, 0.0, -0.2)
    los = helpers.create_los_curved_line(
        Vector3D.PLUS_K,
        Vector3D.PLUS_I,
        float(np.radians((dimension / 2.0) * 5.2 / 3600.0)),
        float(np.radians(3.0 / 3600.0)),
        dimension,
    )

    # linear datation model: at reference time we get the middle line, and the rate is one line every 1.5ms
    line_datation = LinearLineDatation(crossing, dimension / 2, 1.0 / 1.5e-3)
    suffix = "2012-01-01T12h29m57.850Z_2012-01-01T12h30m02.150Z"
    rugged = helpers.configure_rugged(los, line_datation, dimension, position, suffix)

    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.5, 1234, float(np.radians(1.0)), 257)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    location = OpticalLocation(rugged, intersection_algorithm)

    line_number = 97
    gp_list = location.direct_location_of_sensor_line(line_number)
    gp_list = np.array(gp_list)

    # for index, (gp_longitude, gp_latitude, gp_altitude) in enumerate(gp_list):
    line_num, pixel_num = location.inverse_location(first_line, last_line, gp_list[:, 1], gp_list[:, 0], gp_list[:, 2])

    np.testing.assert_allclose(line_num, line_number * np.ones(dimension), rtol=0, atol=5e-4)
    np.testing.assert_allclose(pixel_num, np.arange(dimension), rtol=0, atol=5e-4)


def check_inverse_location(
    dimension, light_time_correction, aberration_of_light_correction, max_line_error, max_pixel_error
):
    """Check inverse location"""
    # orbit = helpers.create_orbit(Constants.EIGEN5C_EARTH_MU)

    crossing = AbsoluteDate("2012-01-01T12:30:00.000", TimeScalesFactory.getUTC())

    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    # los: swath in the (YZ) plane, looking at nadir, 5.2" per pixel, 3" sagitta
    position = Vector3D(1.5, 0.0, -0.2)
    los = helpers.create_los_perfect_line(
        Rotation(Vector3D.PLUS_I, float(np.radians(5.0)), RotationConvention.VECTOR_OPERATOR).applyTo(Vector3D.PLUS_K),
        Vector3D.PLUS_I,
        float(np.radians((dimension / 2.0) * 5.2 / 3600.0)),
        dimension,
    ).build()

    # linear datation model: at reference time we get the middle line, and the rate is one line every 1.5ms
    line_datation = LinearLineDatation(crossing, dimension / 2, 1.0 / 1.5e-3)
    suffix = "2012-01-01T12h29m56.500Z_2012-01-01T12h30m03.500Z"
    rugged = helpers.configure_rugged(los, line_datation, dimension, position, suffix)

    corrections_params = CorrectionsParams(light_time_correction, aberration_of_light_correction, None)
    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.3, 1234, float(np.radians(1.0)), 257)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    location = OpticalLocation(rugged, intersection_algorithm, corrections_params)

    reference_line = 0.87654 * dimension
    gp_list = location.direct_location_of_sensor_line(reference_line)

    p_val = 0
    latitudes = []
    longitudes = []
    while p_val < len(gp_list) - 1:
        i = int(np.floor(p_val))
        d_val = p_val - i

        current_lon, current_lat, _ = gp_list[i]
        next_lon, next_lat, _ = gp_list[i + 1]
        latitudes.append((1.0 - d_val) * current_lat + d_val * next_lat)
        longitudes.append((1.0 - d_val) * current_lon + d_val * next_lon)
        p_val += 1.0

    (line_num, pixel_num) = location.inverse_location(
        0,
        dimension,
        np.array(latitudes),
        np.array(longitudes),
    )

    while p_val < len(gp_list) - 1:
        i = int(np.floor(p_val))
        assert line_num[i] == pytest.approx(reference_line, abs=max_line_error)
        assert pixel_num[i] == pytest.approx(p_val, abs=max_pixel_error)
        p_val += 1.0

        p_val += 1.0

    # Point out of line (20 pixels before first pixel)
    assert location.inverse_location(
        0,
        dimension,
        np.array([21.0 * gp_list[0][1] - 20.0 * gp_list[1][1]]),
        np.array([21.0 * gp_list[0][0] - 20.0 * gp_list[1][0]]),
    ) == ([None], [None])

    # Point out of line (20 pixels after last pixel)
    assert location.inverse_location(
        0,
        dimension,
        np.array([-20.0 * gp_list[-2][1] + 21.0 * gp_list[-1][1]]),
        np.array([-20.0 * gp_list[-2][0] + 21.0 * gp_list[-1][0]]),
    ) == ([None], [None])

    # Point out of line (20 pixels before first line)
    gp_0 = location.direct_location_of_sensor_line(0)
    gp_1 = location.direct_location_of_sensor_line(1)
    assert location.inverse_location(
        0,
        dimension,
        np.array([21.0 * gp_0[dimension // 2][1] - 20.0 * gp_1[dimension // 2][1]]),
        np.array([21.0 * gp_0[dimension // 2][0] - 20.0 * gp_1[dimension // 2][0]]),
    ) == ([None], [None])

    # Point out of line (20 lines after last line)
    gp_2 = location.direct_location_of_sensor_line(dimension - 2)
    gp_3 = location.direct_location_of_sensor_line(dimension - 1)
    assert location.inverse_location(
        0,
        dimension,
        np.array([-20 * gp_2[dimension // 2][1] + 21 * gp_3[dimension // 2][1]]),
        np.array([-20 * gp_2[dimension // 2][0] + 21 * gp_3[dimension // 2][0]]),
    ) == ([None], [None])


def check_date_location(dimension, light_time_correction, aberration_of_light_correction, max_date_error):
    """Check of date location"""
    # orbit = helpers.create_orbit(Constants.EIGEN5C_EARTH_MU)

    crossing = AbsoluteDate("2012-01-01T12:30:00.000", TimeScalesFactory.getUTC())

    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    # los: swath in the (YZ) plane, looking at nadir, 5.2" per pixel, 3" sagitta
    position = Vector3D(1.5, 0.0, -0.2)
    los = helpers.create_los_perfect_line(
        Rotation(Vector3D.PLUS_I, float(np.radians(50.0)), RotationConvention.VECTOR_OPERATOR).applyTo(Vector3D.PLUS_K),
        Vector3D.PLUS_I,
        float(np.radians((dimension / 2.0) * 5.2 / 3600.0)),
        dimension,
    ).build()

    # linear datation model: at reference time we get the middle line, and the rate is one line every 1.5ms
    line_datation = LinearLineDatation(crossing, dimension / 2, 1.0 / 1.5e-3)
    suffix = "2012-01-01T12h29m57.850Z_2012-01-01T12h30m02.150Z"
    rugged = helpers.configure_rugged(los, line_datation, dimension, position, suffix)

    line_sensor = rugged.get_sensor("line")

    corrections_params = CorrectionsParams(light_time_correction, aberration_of_light_correction, None)
    updater = RandomLandscapeUpdater(0.0, 9000.0, 0.5, 1234, float(np.radians(1.0)), 257)
    intersection_algorithm = create_intersection_algorithm(AlgorithmId.DUVENHAGE, updater, 8)

    location = OpticalLocation(rugged, intersection_algorithm, corrections_params)

    reference_line = 0.87654 * dimension
    gp_list = location.direct_location_of_sensor_line(reference_line)

    p_val = 0.0
    latitudes = []
    longitudes = []
    while p_val < len(gp_list) - 1:
        i = int(np.floor(p_val))
        d_val = p_val - i

        current_lon, current_lat, _ = gp_list[i]
        next_lon, next_lat, _ = gp_list[i + 1]
        latitudes.append(float((1 - d_val) * current_lat + d_val * next_lat))
        longitudes.append(float((1 - d_val) * current_lon + d_val * next_lon))
        p_val += 1.0

    date = location.date_location(
        0,
        dimension,
        np.array(latitudes),
        np.array(longitudes),
    )

    while p_val < len(gp_list) - 1:
        i = int(np.floor(p_val))
        assert date[i].durationFrom(line_sensor.get_date(reference_line)) == pytest.approx(0.0, abs=max_date_error)
        p_val += 1.0

    # point out of line (20 lines before first line)
    gp_0 = location.direct_location_of_sensor_line(0)
    gp_1 = location.direct_location_of_sensor_line(1)

    assert location.date_location(
        0,
        dimension,
        np.array([21 * gp_0[dimension // 2][1] - 20 * gp_1[dimension // 2][1]]),
        np.array([21 * gp_0[dimension // 2][0] - 20 * gp_1[dimension // 2][0]]),
    ) == [None]

    # point out of line (20 lines after lats line)
    gp_2 = location.direct_location_of_sensor_line(dimension - 2)
    gp_3 = location.direct_location_of_sensor_line(dimension - 1)

    assert location.date_location(
        0,
        dimension,
        np.array([-20 * gp_2[dimension // 2][1] + 21 * gp_3[dimension // 2][1]]),
        np.array([-20 * gp_2[dimension // 2][0] + 21 * gp_3[dimension // 2][0]]),
    ) == [None]


def check_line_datation(dimension, max_line_error):
    """Check of line datation"""

    crossing = AbsoluteDate("2012-01-01T12:30:00.000", TimeScalesFactory.getUTC())

    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    # los: swath in the (YZ) plane, looking at 50° roll, 2.6" per pixel
    position = Vector3D(1.5, 0.0, -0.2)
    los = helpers.create_los_perfect_line(
        Rotation(Vector3D.PLUS_I, float(np.radians(50.0)), RotationConvention.VECTOR_OPERATOR).applyTo(Vector3D.PLUS_K),
        Vector3D.PLUS_I,
        float(np.radians(dimension * 2.6 / 3600.0)),
        dimension,
    ).build()
    # In fact the pixel size = 5.2" as we construct the LOS with the full line (dimension) instead of dimension/2

    # linear datation model: at reference time we get the middle line, and the rate is one line every 1.5ms
    line_datation = LinearLineDatation(crossing, dimension / 2, 1.0 / 1.5e-3)
    first_line = 0
    last_line = dimension
    line_sensor = LineSensor("line", line_datation, position, los)
    min_date = line_sensor.get_date(first_line).shiftedBy(-1.0)
    max_date = line_sensor.get_date(last_line).shiftedBy(1.0)

    # Recompute the lines from the date with the appropriate shift of date
    recomputed_first_line = line_sensor.get_line(min_date.shiftedBy(1.0))
    recomputed_last_line = line_sensor.get_line(max_date.shiftedBy(-1.0))

    assert recomputed_first_line == pytest.approx(first_line, abs=max_line_error)
    assert recomputed_last_line == pytest.approx(last_line, abs=max_line_error)


def test_for_coverage():
    """Test for coverage"""
    dimension = 400

    # orbit = helpers.create_orbit(Constants.EIGEN5C_EARTH_MU)

    crossing = AbsoluteDate("2012-01-07T11:21:15.000", TimeScalesFactory.getUTC())

    # one line sensor
    # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
    # los: swath in the (YZ) plane, centered at +Z, ±10° aperture, 960 pixels
    position = Vector3D(1.5, 0.0, -0.2)
    los = helpers.create_los_perfect_line(
        Vector3D.PLUS_K,
        Vector3D.PLUS_I,
        float(np.radians(10.0)),
        dimension,
    ).build()

    # linear datation model: at reference time we get line 200, and the rate is one line every 1.5ms
    line_datation = LinearLineDatation(crossing, dimension / 2, 1.0 / 1.5e-3)
    suffix = "2012-01-07T11h21m13.700Z_2012-01-07T11h21m16.300Z"
    rugged = helpers.configure_rugged(los, line_datation, dimension, position, suffix, EllipsoidId.IERS2003)

    line_sensor = rugged.get_sensor("line")
    first_line = 0
    last_line = dimension
    # Check builder
    assert rugged is not None
    sensor_name = None
    assert line_sensor == rugged.get_sensor(sensor_name)

    try:
        line_sensor = LineSensor("line2", line_datation, position, los)
        rugged.add_sensor(line_sensor)
        rugged.get_sensor()
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.DEFAULT_SENSOR.value

    # Check a date in the range of min_date - max_date
    middle_date = line_sensor.get_date((first_line + last_line) / 2)

    intersection_algorithm = create_intersection_algorithm(AlgorithmId.IGNORE_DEM_USE_ELLIPSOID)

    location = OpticalLocation(rugged, intersection_algorithm)

    assert rugged.is_in_range(middle_date)

    # Get the algorithm
    assert isinstance(location.algorithm, IgnoreDEMAlgorithm)

    # Get the algorithm identifier
    assert location.algorithm_id == AlgorithmId.IGNORE_DEM_USE_ELLIPSOID

    # Change the min and max line in inverse location
    # to update the SensorMeanPlaneCrossing when the planeCrossing is not null
    min_line = first_line
    max_line = last_line
    line = (first_line + last_line) / 2.0
    pixel = int(dimension / 2)
    date = line_sensor.get_date(line)
    pixel_los = line_sensor.get_los(date, pixel)
    point_lon, point_lat, point_alt = location.direct_location_of_los(date, np.array(position.toArray()), pixel_los)

    sp_line_num, sp_pixel_num = location.inverse_location(
        min_line, max_line, np.array([point_lat]), np.array([point_lon]), np.array([point_alt]), "line"
    )

    min_line_new = min_line + 10
    max_line_new = max_line - 10
    sp_change_line_num, sp_change_pixel_num = location.inverse_location(
        min_line_new, max_line_new, np.array([point_lat]), np.array([point_lon]), np.array([point_alt]), "line"
    )

    assert sp_change_pixel_num[0] == pytest.approx(sp_pixel_num[0], abs=1.0e-9)
    assert sp_change_line_num[0] == pytest.approx(sp_line_num[0], abs=1.0e-9)

    line = 312
    pixel = 161
    date = line_sensor.get_date(line)
    pixel_los = line_sensor.get_los(date, pixel)
    point_lon1, point_lat1, point_alt1 = location.direct_location_of_los(date, np.array(position.toArray()), pixel_los)
    sp_line_num, sp_pixel_num = location.inverse_location(
        min_line,
        max_line,
        np.array([point_lat, point_lat1]),
        np.array([point_lon, point_lon1]),
        np.array([point_alt, point_alt1]),
        "line",
    )

    min_line_new = min_line + 10
    max_line_new = max_line - 10
    sp_change_line_num, sp_change_pixel_num = location.inverse_location(
        min_line_new,
        max_line_new,
        np.array([point_lat, point_lat1]),
        np.array([point_lon, point_lon1]),
        np.array([point_alt, point_alt1]),
        "line",
    )

    assert sp_change_pixel_num[0] == pytest.approx(sp_pixel_num[0], abs=1.0e-9)
    assert sp_change_line_num[0] == pytest.approx(sp_line_num[0], abs=1.0e-9)
    assert sp_change_pixel_num[1] == pytest.approx(sp_pixel_num[1], abs=1.0e-9)
    assert sp_change_line_num[1] == pytest.approx(sp_line_num[1], abs=1.0e-9)


def test_location_multiple_points_altitudes():
    """Test location of multiple points"""

    rugged, _ = configure_default_rugged()

    intersection_algorithm = create_intersection_algorithm(
        AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID, constant_elevation=0.0
    )
    location = OpticalLocation(rugged, intersection_algorithm)

    dimension = 200
    nb_samples = 11
    lines_linspace = np.linspace(0, dimension, nb_samples)
    pixels_linspace = np.linspace(0, dimension, nb_samples)
    altitudes_linspace = [0.0, 1.32, 5.2, 15.6, 32.1, 25.3, 45.8, 80, 99.999, 142.0, 500.2]  # len = 11

    longitudes, latitudes, altitudes = location.direct_location(
        lines_linspace, pixels_linspace, altitudes=altitudes_linspace
    )

    longitudes2 = [None] * nb_samples
    latitudes2 = [None] * nb_samples
    altitudes2 = [None] * nb_samples

    for i, alt in enumerate(altitudes):
        print(alt)
        inters_algo = create_intersection_algorithm(
            AlgorithmId.CONSTANT_ELEVATION_OVER_ELLIPSOID, constant_elevation=alt
        )
        location2 = OpticalLocation(rugged, inters_algo)
        lon, lat, alt = location2.direct_location(
            [lines_linspace[i]], [pixels_linspace[i]], altitudes=altitudes_linspace[i]
        )
        longitudes2[i], latitudes2[i], altitudes2[i] = lon[0], lat[0], alt[0]

    print("longitudes[:4]", longitudes[:4])
    print("longitudes2[:4]", longitudes2[:4])

    # dates = line_sensor.get_date(np.array(lines_linspace))
    # pixels_los = line_sensor.get_interpolated_los_arr(dates, pixels_linspace)
    # longitudes2, latitudes2, altitudes2 = location.direct_location_of_los_vec(
    #     dates, line_sensor.position, np.array(pixels_los), altitudes_linspace
    # )

    print(np.amax(abs(np.array(latitudes) - np.array(latitudes2))))
    print(np.amax(abs(np.array(longitudes) - np.array(longitudes2))))
    print(np.amax(abs(np.array(altitudes) - np.array(altitudes2))))

    assert latitudes2 == pytest.approx(latitudes, abs=1.0e-12)
    assert longitudes2 == pytest.approx(longitudes, abs=1.0e-12)
    assert altitudes2 == pytest.approx(altitudes, abs=1.0e-5)
