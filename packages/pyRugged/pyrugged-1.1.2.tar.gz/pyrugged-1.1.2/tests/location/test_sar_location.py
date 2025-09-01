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

"""Test of pyrugged Class SARLocation"""
import os
import time

import numpy as np
import pytest
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import CartesianDerivativesFilter

from pyrugged.bodies.body_rotating_frame_id import BodyRotatingFrameId
from pyrugged.bodies.ellipsoid_id import EllipsoidId
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.constant_elevation_algorithm import ConstantElevationAlgorithm
from pyrugged.intersection.duvenhage.duvenhage_algorithm import DuvenhageAlgorithm
from pyrugged.intersection.ignore_dem_algorithm import IgnoreDEMAlgorithm
from pyrugged.location.sar import SARLocation
from pyrugged.model.pyrugged_builder import PyRuggedBuilder
from pyrugged.sar_sensor.doppler_model import DopplerModel
from pyrugged.sar_sensor.range_from_pixel import RangeFromPixel, RangeGridCreation
from pyrugged.sar_sensor.sar_line_datation import SARLineDatation
from pyrugged.sar_sensor.sar_sensor import SARSensor
from pyrugged.utils.coordinates_reader import extract_pv_from_txt
from pyrugged.utils.math_utils import to_array_v  # pylint: disable=no-name-in-module
from pyrugged.utils.spacecraft_to_observed_body_sar import SpacecraftToObservedBodySAR


def setup_module():
    """
    setup : initVM and reset DUMP_VAR
    """

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None

    init_orekit()


# Direct Location #
# Sentinel SLC
def compute_sen1a_pix_location_slc(earth, pix_line):
    """
    Compute for 1 pixel [col, line] the location on ground with sentinel 1A SLC data
    s1a-s6-slc-vh-20230120t195127-20230120t195145-046872-059edc-001.xml
    """
    # Build sensor
    lines = [0, 734, 2202, 2936]
    pixels = [0, 884, 2652, 3536]
    antenna_pointing_right = True

    ranges = [
        [6.074426428179243e-03, 6.074426428179243e-03, 6.074426428179243e-03, 6.074426428179243e-03],
        [6.093267649205340e-03, 6.093267649205340e-03, 6.093267649205340e-03, 6.093267649205340e-03],
        [6.130950091257533e-03, 6.130950091257533e-03, 6.130950091257533e-03, 6.130950091257533e-03],
        [6.149791312283629e-03, 6.149791312283629e-03, 6.149791312283629e-03, 6.149791312283629e-03],
    ]
    time_conversion_to_range_needed = True
    range_pix_correspondance = RangeFromPixel(
        np.array(pixels), np.array(lines), np.array(ranges), time_conversion_to_range_needed
    )

    reference_date = AbsoluteDate("2023-01-20T19:51:27.266098", TimeScalesFactory.getUTC())
    corresponding_date_gap = [
        [
            0,
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.707341", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:28.589829", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:29.031073", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.266107", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.707350", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:28.589839", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:29.031083", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.266126", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.707369", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:28.589858", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:29.031102", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.266136", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.707379", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:28.589867", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:29.031111", TimeScalesFactory.getUTC())),
        ],
    ]

    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))
    doppler = DopplerModel()
    sensor = SARSensor("sar_sensor", sar_datation, range_pix_correspondance, doppler, antenna_pointing_right)

    # Image parameter retrieval
    ############
    # Date
    date = sensor.get_date(pix_line)[0]
    ############
    # Range
    d_range = sensor.get_range(np.array(pix_line))[0]
    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_pv_0_0.txt"
    )

    min_sensor_date = AbsoluteDate("2023-01-20T19:50:24.253712", TimeScalesFactory.getUTC())
    max_sensor_date = AbsoluteDate("2023-01-20T19:52:44.253712", TimeScalesFactory.getUTC())
    pv_list = extract_pv_from_txt(pv_txt_file_path)
    sc_to_body = SpacecraftToObservedBodySAR(
        earth.body_frame, min_sensor_date, max_sensor_date, 0.01, 5.0, pv_list, 8, CartesianDerivativesFilter.USE_PV
    )
    ############
    # Satellite PVT
    p_body = sc_to_body.get_sc_to_body(date)

    algorithm = ConstantElevationAlgorithm(0.0)
    point = algorithm.intersection_sar(
        earth,
        to_array_v(p_body.getCartesian().getPosition().toArray()),
        to_array_v(p_body.getCartesian().getVelocity().toArray()),
        d_range,
        sensor.is_antenna_pointing_right,
        sensor.get_doppler,
    )

    return point


def test_location_sen1a_slc(earth):
    """
    Test SARLocation class with sentinel 1A slc data
    s1a-s6-slc-vh-20230120t195127-20230120t195145-046872-059edc-001.xml
    """
    point = compute_sen1a_pix_location_slc(earth, [1768, 1468])
    assert point[0] * 180 / np.pi == pytest.approx(1.456805317082818e01, abs=1.0e-7)
    assert point[1] * 180 / np.pi == pytest.approx(-2.438902496287664e01, abs=1.0e-7)
    assert point[2] == pytest.approx(1.968163996934891e-05, abs=1.0e-4)


# Sentinel GRD
def compute_location_sen1a_grd(earth, pix_line, alt):
    """
    SARLocation class compute location for 1 pixel (col, line) with sentinel 1A grd data
    s1a-s6-grd-vh-20230122t115524-20230122t115547-046896-059fb7-002
    """
    # Build sensor
    lines = [0, 1333, 3999, 5332]
    pixels = [0, 403, 1209, 1612]
    antenna_pointing_right = True

    ranges = [
        [6.087179789572389e-03, 6.087179789571471e-03, 6.087179789545996e-03, 6.087179789574176e-03],
        [6.105331060141939e-03, 6.105331901980906e-03, 6.105333405292106e-03, 6.105334174443712e-03],
        [6.141862979423282e-03, 6.141865488833737e-03, 6.141869969692967e-03, 6.141872262697154e-03],
        [6.160242253370319e-03, 6.160245588502567e-03, 6.160251543862904e-03, 6.160254591395568e-03],
    ]
    time_conversion_to_range_needed = True
    range_pix_correspondance = RangeFromPixel(
        np.array(pixels), np.array(lines), np.array(ranges), time_conversion_to_range_needed, "cubic_legacy"
    )

    reference_date = AbsoluteDate("2023-01-22T11:55:24.052832", TimeScalesFactory.getUTC())
    corresponding_date_gap = [
        [
            0,
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053751", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055590", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056510", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:24.052841", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053760", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055599", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056519", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:24.052859", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053778", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055617", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056537", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:24.052868", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053787", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055627", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056546", TimeScalesFactory.getUTC())),
        ],
    ]
    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))
    doppler = DopplerModel()
    sensor = SARSensor("sar_sensor", sar_datation, range_pix_correspondance, doppler, antenna_pointing_right)

    # Image parameter retrieval
    ############
    # Date
    date = sensor.get_date(pix_line)[0]
    ############
    # Range
    d_range = sensor.get_range(np.array(pix_line))[0]
    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_grd_pv_0_0.txt"
    )
    min_sensor_date = AbsoluteDate("2023-01-22T11:54:14.067377", TimeScalesFactory.getUTC())
    max_sensor_date = AbsoluteDate("2023-01-22T11:56:54.067377", TimeScalesFactory.getUTC())
    pv_list = extract_pv_from_txt(pv_txt_file_path)
    sc_to_body = SpacecraftToObservedBodySAR(
        earth.body_frame, min_sensor_date, max_sensor_date, 0.01, 5.0, pv_list, 8, CartesianDerivativesFilter.USE_PV
    )
    ############
    # Satellite PVT
    p_body = sc_to_body.get_sc_to_body(date)

    algorithm = ConstantElevationAlgorithm(alt)
    point = algorithm.intersection_sar(
        earth,
        to_array_v(p_body.getCartesian().getPosition().toArray()),
        to_array_v(p_body.getCartesian().getVelocity().toArray()),
        d_range,
        sensor.is_antenna_pointing_right,
        sensor.get_doppler,
    )
    return point


def test_location_sen1a_grd(earth):
    """
    Test sentinel 1A grd location
    """
    pix_line = [806, 2666]
    alt = 2.089855594234541e02
    point = compute_location_sen1a_grd(earth, pix_line, alt)
    assert point[0] * 180 / np.pi == pytest.approx(4.228123531821573e01, abs=3.0e-8)
    assert point[1] * 180 / np.pi == pytest.approx(-8.795354277157098e01, abs=3.0e-8)
    assert point[2] == pytest.approx(alt, abs=1e-3)


# RADARSAT SLC
def compute_location_for_pix_line_radarsat_slc(pix_line, algorithm, earth):
    """
    Compute intersection for 1 pixel coordinates [pix, line] for RADARSAT
    """
    # Datation model
    antenna_pointing_right = True
    reference_date = AbsoluteDate("2016-06-05T06:02:08.226323", TimeScalesFactory.getUTC())

    lines = [0.5, 27193.5]
    pixels = [0, 20576]
    corresponding_date_gap = [
        [0, -reference_date.durationFrom(AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC()))],
        [0, -reference_date.durationFrom(AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC()))],
    ]
    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))

    # Range model
    pixel_time_increasing = False
    sr_coefficient = np.array([9.738835958311997e05, 1.0, 0.0, 0.0, 0.0, 0.0])[::-1]
    total_pixel_number = 20577
    ground_range_or = 0.0
    pixel_size_slc = 1.33117902
    range_grid_construction = RangeGridCreation(total_pixel_number, sr_coefficient)
    ranges = [
        [
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 0, pixel_time_increasing
            ),
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 0, pixel_time_increasing
            ),
        ],
        [
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 20576, pixel_time_increasing
            ),
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 20576, pixel_time_increasing
            ),
        ],
    ]

    range_pix_correspondance = RangeFromPixel(np.array(pixels), np.array(lines), np.array(ranges))
    doppler = DopplerModel()
    sensor = SARSensor("sar_sensor", sar_datation, range_pix_correspondance, doppler, antenna_pointing_right)
    # Image parameter retrieval
    ############
    # Date
    date = sensor.get_date(pix_line)[0]
    ############
    # Range
    d_range = sensor.get_range(np.array(pix_line))[0]
    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_pv_0_1.txt"
    )
    min_sensor_date = AbsoluteDate("2016-06-05T06:02:08.226323", TimeScalesFactory.getUTC())
    max_sensor_date = AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC())

    pv_list = extract_pv_from_txt(pv_txt_file_path)
    sc_to_body = SpacecraftToObservedBodySAR(
        earth.body_frame, min_sensor_date, max_sensor_date, 0.01, 5.0, pv_list, 5, CartesianDerivativesFilter.USE_PV
    )
    ############
    # Satellite PVT
    p_body = sc_to_body.get_sc_to_body(date)

    point = algorithm.intersection_sar(
        earth,
        to_array_v(p_body.getCartesian().getPosition().toArray()),
        to_array_v(p_body.getCartesian().getVelocity().toArray()),
        d_range,
        sensor.is_antenna_pointing_right,
        sensor.get_doppler,
    )

    return point


def compute_relative_and_absolute_err(
    coordinates,
    coord_ref,
    long_relative_err,
    long_absolute_err,
    lat_relative_err,
    lat_absolute_err,
    alt_relative_err,
    alt_absolute_err,
):
    """Compute relative and absolute errors, the difference is done in degrees (and not radian)"""
    long_absolute_err.append(np.abs(coordinates[1] * 180 / np.pi - coord_ref[0]))
    long_relative_err.append(np.abs(coordinates[1] * 180 / np.pi - coord_ref[0]) * 100 / coord_ref[0])
    lat_absolute_err.append(np.abs(coordinates[0] * 180 / np.pi - coord_ref[1]))
    lat_relative_err.append(np.abs(coordinates[0] * 180 / np.pi - coord_ref[1]) * 100 / coord_ref[1])
    alt_absolute_err.append(np.abs(coordinates[2] - coord_ref[2]))
    if coord_ref[2] != 0.0:
        alt_relative_err.append(np.abs(coordinates[2] - coord_ref[2]) * 100 / coord_ref[2])


def test_location_radarsat_slc(earth):
    """
    Test SARLocation class with RADARSAR SLC data product_SLC.xml (/data/ref/utils)
    Comparison with results obtained with EUCLIDIUM under product_SLC.xml (/data/ref/utils)
    """
    (
        latitude_absolute_error,
        latitude_relative_error,
        longitude_absolute_error,
        longitude_relative_error,
        altitude_absolute_error,
        altitude_relative_error,
    ) = ([], [], [], [], [], [])

    algorithm = ConstantElevationAlgorithm(0.0)
    # Coordinates [0, 0], altitude 0
    coord = [0, 0]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.811481804455971, 49.30134792982429, 0.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [0.5, 0.5], altitude 0
    coord = [0.5, 0.5]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.81149364308881, 49.3013378436149, 0.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [0, 27192], altitude 0
    coord = [0, 27192]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.688431593724418, 48.8394167651639, 0.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [0, 13596], altitude 0
    coord = [0, 13596]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.749812142121643, 49.07039300949105, 0.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [20575, 0], altitude 0
    coord = [20575, 0]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [2.406362259992629, 49.23256804613204, 0.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [10287, 0], altitude 0
    coord = [10287, 0]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [2.105221126414944, 49.26779200041256, 0.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [20575, 27192], altitude 0
    coord = [20575, 27192]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [2.277703907159967, 48.77068669686941, 0.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    algorithm = ConstantElevationAlgorithm(200.0)
    # Coordinates [0, 0], altitude 200
    coord = [0, 0]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.808220474281316, 49.30171250888474, 200.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [0.5, 0.5], altitude 200
    coord = [0.5, 0.5]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.808232307318574, 49.3017024237902, 200.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [0, 27192], altitude 200
    coord = [0, 27192]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.685201497733314, 48.83978116502965, 200.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [0, 13596], altitude 200
    coord = [0, 13596]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.746566526544757, 49.07075749323425, 200.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [20575, 0], altitude 200
    coord = [20575, 0]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [2.402819391623421, 49.23298375286658, 200.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [10287, 0], altitude 200
    coord = [10287, 0]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [2.101826280473405, 49.26818079175754, 200.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [20575, 27192], altitude 200
    coord = [20575, 27192]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [2.274194936111651, 48.77110189014451, 200.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    algorithm = ConstantElevationAlgorithm(500.0)
    # Coordinates [0, 0], altitude 500
    coord = [0, 0]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.803332937139676, 49.30225869209855, 500.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [0.5, 0.5], altitude 500
    coord = [0.5, 0.5]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.803344761799888, 49.3022486086731, 500.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [0, 27192], altitude 500
    coord = [0, 27192]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.680360770302073, 48.84032708270851, 500.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [0, 13596], altitude 500
    coord = [0, 13596]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [1.741702537187862, 49.07130353547852, 500.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [20575, 0], altitude 500
    coord = [20575, 0]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [2.397510420119956, 49.23360646545338, 500.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [10287, 0], altitude 500
    coord = [10287, 0]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [2.09673886174364, 49.26876322008526, 500.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )

    # Coordinates [20575, 27192], altitude 500
    coord = [20575, 27192]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    compute_relative_and_absolute_err(
        on_earth_coord,
        [2.268936760594826, 48.7717238369275, 500.0],
        longitude_relative_error,
        longitude_absolute_error,
        latitude_relative_error,
        latitude_absolute_error,
        altitude_relative_error,
        altitude_absolute_error,
    )
    assert np.array(longitude_absolute_error).max() < 2.19 * 10 ** (-7)
    assert np.array(longitude_absolute_error).min() > 7.96 * 10 ** (-10)

    assert np.array(latitude_absolute_error).max() < 6.74 * 10 ** (-8)
    assert np.array(latitude_absolute_error).min() > 2.26 * 10 ** (-8)

    assert np.array(altitude_absolute_error).max() < 2.72 * 10 ** (-5)
    assert np.array(altitude_absolute_error).min() > 1.25 * 10 ** (-5)


def sarlocation_class_direct_location_radarsat_slc(algorithm, line, col):
    """
    SARLocation class location for coordinantes [col, line] with specific algorithm (constant elevation or DEMignore)
    for SLC RADARSAT. Line and col must be arrays
    """
    # Datation model
    antenna_pointing_right = True
    reference_date = AbsoluteDate("2016-06-05T06:02:08.226323", TimeScalesFactory.getUTC())

    # For RADARSAT information given in product are given for pixel halves that is why for lines we use pixel halves.
    # This should not be done for pixels (columns) as pixel halves are already taken into account in the model, that is
    # why we do not take into account pixel halves for columns
    lines = [0.5, 27193.5]
    pixels = [0, 20576]
    corresponding_date_gap = [
        [0, -reference_date.durationFrom(AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC()))],
        [0, -reference_date.durationFrom(AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC()))],
    ]
    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))

    # Range model
    pixel_time_increasing = False
    sr_coefficient = np.array([9.738835958311997e05, 1.0, 0.0, 0.0, 0.0, 0.0])[::-1]
    total_pixel_number = 20577
    ground_range_or = 0.0
    pixel_size_slc = 1.33117902
    range_grid_construction = RangeGridCreation(total_pixel_number, sr_coefficient)
    ranges = [
        [
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 0, pixel_time_increasing
            ),
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 0, pixel_time_increasing
            ),
        ],
        [
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 20576, pixel_time_increasing
            ),
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 20576, pixel_time_increasing
            ),
        ],
    ]

    range_pix_correspondance = RangeFromPixel(np.array(pixels), np.array(lines), np.array(ranges))
    doppler = DopplerModel()
    sensor = SARSensor("sar_sensor", sar_datation, range_pix_correspondance, doppler, antenna_pointing_right)

    # Satellite position velocity
    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_pv_0_1.txt"
    )
    pv_list = extract_pv_from_txt(pv_txt_file_path)

    ############
    # Satellite PVT

    builder = PyRuggedBuilder()
    builder.set_ellipsoid(
        new_ellipsoid=None,
        ellipsoid_id=EllipsoidId.WGS84,
        body_rotating_frame_id=BodyRotatingFrameId.ITRF,
    )
    builder.set_time_span(
        AbsoluteDate("2016-06-05T06:02:08.226323", TimeScalesFactory.getUTC()),
        AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC()),
        0.01,
        5.0,
    )
    builder.set_trajectory(pv_list, 5, CartesianDerivativesFilter.USE_PV)
    builder.add_sensor(sensor)
    rugged = builder.build()
    sar_location = SARLocation(rugged, algorithm)

    return sar_location.direct_location(line, col, "sar_sensor")


def sarlocation_class_direct_location_sen1a_grd(algorithm, line, col):
    """
    SARLocation class compute location for 1 pixel (col, line) with sentinel 1A grd data
    s1a-s6-grd-vh-20230122t115524-20230122t115547-046896-059fb7-002
    """
    # Build sensor
    lines = [0, 1333, 3999, 5332]
    pixels = [0, 403, 1209, 1612]
    antenna_pointing_right = True

    ranges = [
        [6.087179789572389e-03, 6.087179789571471e-03, 6.087179789545996e-03, 6.087179789574176e-03],
        [6.105331060141939e-03, 6.105331901980906e-03, 6.105333405292106e-03, 6.105334174443712e-03],
        [6.141862979423282e-03, 6.141865488833737e-03, 6.141869969692967e-03, 6.141872262697154e-03],
        [6.160242253370319e-03, 6.160245588502567e-03, 6.160251543862904e-03, 6.160254591395568e-03],
    ]

    time_conversion_to_range_needed = True
    range_pix_correspondance = RangeFromPixel(
        np.array(pixels), np.array(lines), np.array(ranges), time_conversion_to_range_needed, "cubic"
    )

    reference_date = AbsoluteDate("2023-01-22T11:55:24.052832", TimeScalesFactory.getUTC())
    corresponding_date_gap = [
        [
            0,
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053751", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055590", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056510", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:24.052841", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053760", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055599", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056519", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:24.052859", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053778", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055617", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056537", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:24.052868", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053787", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055627", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056546", TimeScalesFactory.getUTC())),
        ],
    ]

    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))
    doppler = DopplerModel()
    sensor = SARSensor("sar_sensor", sar_datation, range_pix_correspondance, doppler, antenna_pointing_right)

    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_grd_pv_0_0.txt"
    )
    pv_list = extract_pv_from_txt(pv_txt_file_path)

    ############
    # Satellite PVT

    builder = PyRuggedBuilder()
    builder.set_ellipsoid(
        new_ellipsoid=None,
        ellipsoid_id=EllipsoidId.WGS84,
        body_rotating_frame_id=BodyRotatingFrameId.ITRF,
    )
    builder.set_time_span(
        AbsoluteDate("2023-01-22T11:54:14.067377", TimeScalesFactory.getUTC()),
        AbsoluteDate("2023-01-22T11:56:54.067377", TimeScalesFactory.getUTC()),
        0.01,
        5.0,
    )
    builder.set_trajectory(pv_list, 5, CartesianDerivativesFilter.USE_PV)
    builder.add_sensor(sensor)
    rugged = builder.build()
    sar_location = SARLocation(rugged, algorithm)

    return sar_location.direct_location(line, col, "sar_sensor")


def test_location_with_pyrugged():
    """
    SARLocation class location test for Constant Elevation and DEM ignore
    Computation compared to EUCLIDIUM (CNES) direct location at different altitudes for RADARSAT SLC stored in
    locdirecte_out_RS2_OPER_SAR_UW_SLC_20160605T060208_N49-036_E002-045_0000(1).txt in tests/data/sar_sensor
    """
    # Constant elevation algorithm
    algorithm = ConstantElevationAlgorithm(0.0)
    assert sarlocation_class_direct_location_radarsat_slc(algorithm, [0], [0])[0][0] * 180.0 / np.pi == pytest.approx(
        1.811481804455971, abs=1.0e-6
    )
    assert sarlocation_class_direct_location_radarsat_slc(algorithm, [0], [0])[1][0] * 180.0 / np.pi == pytest.approx(
        49.30134792982429, abs=1.0e-7
    )
    assert sarlocation_class_direct_location_radarsat_slc(algorithm, [0], [0])[2][0] == pytest.approx(0.0, abs=2.0e-5)

    # Several pixels
    algorithm = ConstantElevationAlgorithm(200)
    lon, lat, alt = sarlocation_class_direct_location_radarsat_slc(algorithm, [0.5, 27192, 0], [0.5, 0, 10287])
    lon = np.array(lon) * 180.0 / np.pi
    lat = np.array(lat) * 180.0 / np.pi
    assert lon[0] == pytest.approx(1.808232307318574, abs=1.0e-6)
    assert lon[1] == pytest.approx(1.685201497733314, abs=1.0e-6)
    assert lon[2] == pytest.approx(2.101826280473405, abs=1.0e-6)
    assert lat[0] == pytest.approx(49.3017024237902, abs=1.0e-6)
    assert lat[1] == pytest.approx(48.83978116502965, abs=1.0e-6)
    assert lat[2] == pytest.approx(49.26818079175754, abs=1.0e-6)
    assert alt[0] == pytest.approx(200, abs=1e-4)

    # Ignore DEM algorithm
    algorithm = IgnoreDEMAlgorithm()
    assert sarlocation_class_direct_location_radarsat_slc(algorithm, [0], [0])[0][0] * 180 / np.pi == pytest.approx(
        1.811481804455971, abs=1.0e-6
    )
    assert sarlocation_class_direct_location_radarsat_slc(algorithm, [0], [0])[1][0] * 180 / np.pi == pytest.approx(
        49.30134792982429, abs=1.0e-7
    )
    assert sarlocation_class_direct_location_radarsat_slc(algorithm, [0], [0])[2][0] == pytest.approx(0.0, abs=2.0e-5)


def test_location_duration_1000_coord():
    """
    SARLocation duration for RADARSAT and Sentinel1
    """
    algorithm = ConstantElevationAlgorithm(0.0)

    # For RADARSAT slc (sentinel slc should be similar)
    start = time.time()
    sarlocation_class_direct_location_radarsat_slc(algorithm, np.linspace(0, 0, 1001), np.linspace(0, 1000, 1001))
    end = time.time()
    point_per_sec_direct_loc = (end - start) / 1001.0
    assert point_per_sec_direct_loc < 0.005

    # For Sentinel 1 GRD (with cubique interpolation)
    start = time.time()
    sarlocation_class_direct_location_sen1a_grd(algorithm, np.linspace(0, 0, 1001), np.linspace(0, 1000, 1001))
    end = time.time()
    point_per_sec_direct_loc = (end - start) / 1001.0
    assert point_per_sec_direct_loc < 0.01


def test_duvenhage_exception(mayon_volcano_context):
    """
    SARLocation class location test for raising exception if not using Constant Elevation or DEM ignore
    """
    updater = mayon_volcano_context["updater"]
    algorithm = DuvenhageAlgorithm(updater, 8, False)
    try:
        sarlocation_class_direct_location_radarsat_slc(algorithm, [0], [0])
        pytest.fail("An error should have been triggered")
    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.SAR_LOCATION_ALGORITH_ALLOWED.value


# Inverse Location #
# RADARSAT SLC
def compute_inverse_location_radarsat(points, number_line, algorithm):
    """
    SARLocation class inverse location of [lat, long, alt] for RADARSAT (product_SLC.xml) data
    """

    # For RADARSAT information given in product are given for pixel halves that is why for lines we use pixel halves.
    # This should not be done for pixels (columns) as pixel halves are already taken into account in the model, that is
    # why we do not take into account pixel halves for columns
    lines = [0.5, 27193.5]
    pixels = [0, 20576]

    # SAR datation model
    reference_date = AbsoluteDate("2016-06-05T06:02:08.226323", TimeScalesFactory.getUTC())
    corresponding_date_gap = [
        0,
        -reference_date.durationFrom(AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC())),
    ]
    # For inverse location pixels dimension should match corresponding_date_gap. Moreover, lines dimensions must also
    # match corresponding_date_gap dimension as we use scipy.griddata to retrieve pixel column and row.
    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))

    # SAR range model
    pixel_time_increasing = False
    sr_coefficient = np.array([9.738835958311997e05, 1.0, 0.0, 0.0, 0.0, 0.0])[::-1]
    total_pixel_number = 20577
    ground_range_or = 0.0
    pixel_size_slc = 1.33117902
    range_grid_construction = RangeGridCreation(total_pixel_number, sr_coefficient)
    ranges = [
        range_grid_construction.ground_range_to_slant_range_polynom_application(
            pixel_size_slc, ground_range_or, 0, pixel_time_increasing
        ),
        range_grid_construction.ground_range_to_slant_range_polynom_application(
            pixel_size_slc, ground_range_or, 20576, pixel_time_increasing
        ),
    ]
    # For inverse location pixels dimension should match corresponding_date_gap. Moreover, lines dimensions must also
    # match corresponding_date_gap dimension as we use scipy.griddata to retrieve pixel column and row.
    range_pix_correspondance = RangeFromPixel(np.array(pixels), np.array(lines), np.array(ranges))
    doppler = DopplerModel()
    sensor = SARSensor("sar_sensor", sar_datation, range_pix_correspondance, doppler, antenna_pointing_right=True)

    # Satellite position velocity
    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_pv_0_1.txt"
    )
    pv_list = extract_pv_from_txt(pv_txt_file_path)

    ############
    # Pyrugged building
    builder = PyRuggedBuilder()

    builder.set_ellipsoid(
        new_ellipsoid=None,
        ellipsoid_id=EllipsoidId.WGS84,
        body_rotating_frame_id=BodyRotatingFrameId.ITRF,
    )

    builder.set_time_span(
        AbsoluteDate("2016-06-05T06:02:08.226323", TimeScalesFactory.getUTC()),
        AbsoluteDate("2016-06-05T06:02:16.208620", TimeScalesFactory.getUTC()),
        0.01,
        5.0,
    )

    builder.set_trajectory(pv_list, 5, CartesianDerivativesFilter.USE_PV)

    builder.add_sensor(sensor)

    rugged = builder.build()
    sar_location = SARLocation(rugged, algorithm)

    latitudes, longis, alts = [], [], []
    for point in points:
        latitudes.append(point[0])
        longis.append(point[1])
        alts.append(point[2])

    return sar_location.inverse_location(
        AbsoluteDate("2016-06-05T06:02:08.226323", TimeScalesFactory.getUTC()),
        AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC()),
        np.array(latitudes),
        np.array(longis),
        np.array(alts),
        "sar_sensor",
        number_line,
    )


def test_inverse_location_radarsat():
    """
    SARLocation class inverse location test for several points, altitudes for RADARSAT
    """

    algorithm = ConstantElevationAlgorithm(0.0)
    point_0_0 = np.array([49.30134792982429 * np.pi / 180.0, 1.811481804455971 * np.pi / 180.0, 0.0])
    assert compute_inverse_location_radarsat([point_0_0], None, algorithm)[0] == pytest.approx(0.0, abs=1e-2)
    assert compute_inverse_location_radarsat([point_0_0], None, algorithm)[1] == 0.5
    point_10287_0 = np.array([49.26779200041256 * np.pi / 180.0, 2.105221126414944 * np.pi / 180.0, 0.0])
    assert compute_inverse_location_radarsat([point_10287_0], None, algorithm)[0] == pytest.approx(10287.0, abs=1e-2)
    assert compute_inverse_location_radarsat([point_10287_0], None, algorithm)[1] == 0.5

    algorithm = ConstantElevationAlgorithm(500.0)
    point_0_27192 = np.array([48.84032708270851 * np.pi / 180.0, 1.680360770302073 * np.pi / 180.0, 500.0])
    assert compute_inverse_location_radarsat([point_0_27192], None, algorithm)[0] == pytest.approx(0.0, abs=1e-2)
    assert compute_inverse_location_radarsat([point_0_27192], None, algorithm)[1] == pytest.approx(27192, abs=2e-1)
    point_20575_27192 = np.array([48.7717238369275 * np.pi / 180.0, 2.268936760594826 * np.pi / 180.0, 500.0])
    assert round(compute_inverse_location_radarsat([point_20575_27192], 27193, algorithm)[0][0]) == 20575
    assert compute_inverse_location_radarsat([point_20575_27192], 27193, algorithm)[1] == pytest.approx(27192, abs=2e-1)


def test_direct_inverse_location_radarsat(earth):
    """
    SARLocation class direct followed by inverse location test for several points for RADARSAT
    """
    algorithm = ConstantElevationAlgorithm(0.0)
    coord = [0.5, 0.5]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    pix_line = compute_inverse_location_radarsat([on_earth_coord], 27193, algorithm)
    assert pix_line[0] == pytest.approx(0.5, abs=1e-9)
    assert pix_line[1] == pytest.approx(0.5, abs=1e-9)

    algorithm = ConstantElevationAlgorithm(0.0)
    coord = [11567, 156.5]
    on_earth_coord = compute_location_for_pix_line_radarsat_slc(coord, algorithm, earth)
    pix_line = compute_inverse_location_radarsat([on_earth_coord], 27193, algorithm)
    assert pix_line[0] == pytest.approx(11567, abs=1e-8)
    assert pix_line[1] == pytest.approx(156.5, abs=3e-2)


# Sentinel SLC
def compute_inverse_location_sentinel(points, number_line, algorithm):
    """
    SARLocation class inverse location of [lat, long, alt] for Sentinel SLC data
    s1a-s6-slc-vh-20230120t195127-20230120t195145-046872-059edc-001.xml
    """

    # Build sensor
    lines = [0, 734, 2202]
    pixels = [0, 884, 2652]
    antenna_pointing_right = True

    ranges = [6.074426428179243e-03, 6.093267649205340e-03, 6.130950091257533e-03]

    time_conversion_to_range_needed = True
    range_pix_correspondance = RangeFromPixel(
        np.array(pixels), np.array(lines), np.array(ranges), time_conversion_to_range_needed
    )

    reference_date = AbsoluteDate("2023-01-20T19:51:27.266098", TimeScalesFactory.getUTC())
    corresponding_date_gap = [
        [
            0,
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.707341", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:28.589829", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.266107", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.707350", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:28.589839", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.266126", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.707369", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:28.589858", TimeScalesFactory.getUTC())),
        ],
    ]

    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))
    doppler = DopplerModel()
    sensor = SARSensor("sar_sensor", sar_datation, range_pix_correspondance, doppler, antenna_pointing_right)

    # Satellite position velocity
    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_pv_0_0_extend.txt"
    )
    pv_list = extract_pv_from_txt(pv_txt_file_path)

    ############
    # Pyrugged building
    builder = PyRuggedBuilder()

    builder.set_ellipsoid(
        new_ellipsoid=None,
        ellipsoid_id=EllipsoidId.WGS84,
        body_rotating_frame_id=BodyRotatingFrameId.ITRF,
    )

    builder.set_time_span(
        AbsoluteDate("2023-01-20T19:50:24.253712", TimeScalesFactory.getUTC()),
        AbsoluteDate("2023-01-20T19:52:44.253712", TimeScalesFactory.getUTC()),
        0.01,
        5.0,
    )

    builder.set_trajectory(pv_list, 8, CartesianDerivativesFilter.USE_PV)
    builder.add_sensor(sensor)
    rugged = builder.build()
    sar_location = SARLocation(rugged, algorithm)

    latitudes, longis, alts = [], [], []
    for point in points:
        latitudes.append(point[0])
        longis.append(point[1])
        alts.append(point[2])

    return sar_location.inverse_location(
        AbsoluteDate("2023-01-20T19:50:24.253712", TimeScalesFactory.getUTC()),
        AbsoluteDate("2023-01-20T19:52:44.253712", TimeScalesFactory.getUTC()),
        np.array(latitudes),
        np.array(longis),
        np.array(alts),
        "sar_sensor",
        number_line,
    )


def test_inverse_location_sentinel():
    """
    SARLocation class inverse location test for several points, altitudes for Sentinel SLC
    """
    algorithm = ConstantElevationAlgorithm(0.0)
    point_0_0 = np.array([1.456805317082818e01 * np.pi / 180.0, -2.438902496287664e01 * np.pi / 180.0, 0.0])
    assert compute_inverse_location_sentinel([point_0_0], 31079, algorithm)[0] == pytest.approx(1768.0, abs=1e-2)
    assert compute_inverse_location_sentinel([point_0_0], 31079, algorithm)[1] == pytest.approx(1468.0, abs=3e-1)


def test_direct_inverse_location_sentinel_slc(earth):
    """
    SARLocation class direct followed by inverse location test for several points for Sentinel SLC
    """
    algorithm = ConstantElevationAlgorithm(0.0)
    point = compute_sen1a_pix_location_slc(earth, [1768, 1468])
    assert compute_inverse_location_sentinel([point], 40000, algorithm)[0] == pytest.approx(1768.0, abs=1e-5)
    assert compute_inverse_location_sentinel([point], 40000, algorithm)[1] == pytest.approx(1468.0, abs=3e-1)

    point = compute_sen1a_pix_location_slc(earth, [0.5, 1500.5])
    assert compute_inverse_location_sentinel([point], 40000, algorithm)[0] == pytest.approx(0.5, abs=1e-5)
    assert compute_inverse_location_sentinel([point], 40000, algorithm)[1] == pytest.approx(1500.5, abs=3e-1)


# Sentinel GRD
def compute_inverse_location_sentinel_grd(points, number_line, algorithm):
    """
    SARLocation class inverse location of [lat, long, alt] for Sentinel GRD data
    s1a-s6-grd-vh-20230122t115524-20230122t115547-046896-059fb7-002.xml
    """

    # Build sensor
    lines = [0, 1333, 3999, 5332]
    pixels = [0, 403, 1209, 1612]
    antenna_pointing_right = True

    ranges = [6.087179789572389e-03, 6.105331060141939e-03, 6.141862979423282e-03, 6.160242253370319e-03]

    time_conversion_to_range_needed = True
    range_pix_correspondance = RangeFromPixel(
        np.array(pixels), np.array(lines), np.array(ranges), time_conversion_to_range_needed, "cubic"
    )

    reference_date = AbsoluteDate("2023-01-22T11:55:24.052832", TimeScalesFactory.getUTC())
    corresponding_date_gap = [
        [
            0,
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053751", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055590", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056510", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:24.052841", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053760", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055599", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056519", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:24.052859", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053778", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055617", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056537", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:24.052868", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053787", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055627", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:32.056546", TimeScalesFactory.getUTC())),
        ],
    ]

    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))
    doppler = DopplerModel()
    sensor = SARSensor("sar_sensor", sar_datation, range_pix_correspondance, doppler, antenna_pointing_right)

    # Satellite position velocity
    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_grd_pv_0_0.txt"
    )
    pv_list = extract_pv_from_txt(pv_txt_file_path)

    ############
    # Pyrugged building
    builder = PyRuggedBuilder()

    builder.set_ellipsoid(
        new_ellipsoid=None,
        ellipsoid_id=EllipsoidId.WGS84,
        body_rotating_frame_id=BodyRotatingFrameId.ITRF,
    )

    builder.set_time_span(
        AbsoluteDate("2023-01-22T11:54:14.067377", TimeScalesFactory.getUTC()),
        AbsoluteDate("2023-01-22T11:56:54.067377", TimeScalesFactory.getUTC()),
        0.01,
        5.0,
    )

    builder.set_trajectory(pv_list, 9, CartesianDerivativesFilter.USE_PV)
    builder.add_sensor(sensor)
    rugged = builder.build()
    sar_location = SARLocation(rugged, algorithm)

    latitudes, longis, alts = [], [], []
    for point in points:
        latitudes.append(point[0])
        longis.append(point[1])
        alts.append(point[2])

    return sar_location.inverse_location(
        AbsoluteDate("2023-01-22T11:55:24.052832", TimeScalesFactory.getUTC()),
        AbsoluteDate("2023-01-22T11:55:47.705301", TimeScalesFactory.getUTC()),
        latitudes,
        longis,
        alts,
        "sar_sensor",
        number_line,
    )


def test_inverse_location_sentinel_grd():
    """
    SARLocation class inverse location test for Sentinel GRD
    """
    algorithm = ConstantElevationAlgorithm(208.0)
    point_806_2666 = np.array([4.228123531821573e01 * np.pi / 180.0, -8.795354277157098e01 * np.pi / 180.0, 208])
    assert compute_inverse_location_sentinel_grd([point_806_2666], 20000, algorithm)[0] == pytest.approx(806.0, abs=0.2)
    assert compute_inverse_location_sentinel_grd([point_806_2666], 20000, algorithm)[1] == pytest.approx(
        2666.0, abs=0.3
    )


def test_directe_inverse_location_sentinel_grd(earth):
    """
    SARLocation class Test for direct followed by inverse location test for Sentinel GRD data
    """
    alt = 2.089855594234541e02
    algorithm = ConstantElevationAlgorithm(alt)
    point = compute_location_sen1a_grd(earth, [806, 2666], alt)
    point2 = compute_location_sen1a_grd(earth, [0.5, 1832], alt)
    points = compute_inverse_location_sentinel_grd([point, point2], 20000, algorithm)
    assert points[0][0] == pytest.approx(806.0, abs=8e-2)
    assert points[0][1] == pytest.approx(0.5, abs=1e-3)
    assert points[1][0] == pytest.approx(2666.0, abs=5e-2)
    assert points[1][1] == pytest.approx(1832.0, abs=0.1)


def test_inv_location_duration_1000_coord():
    """
    SARLocation class location test for Constant Elevation and DEM ignore
    """
    algorithm = ConstantElevationAlgorithm(0.0)
    nb_col = 100
    nb_line = 10
    points = []
    for i in range(nb_col):
        for j in range(nb_line):
            points.append(
                np.array(
                    [
                        (49.30134792982429 + (i * 0.1)) * np.pi / 180.0,
                        (1.811481804455971 + (j * 0.1)) * np.pi / 180.0,
                        0.0,
                    ],
                )
            )

    start = time.time()
    compute_inverse_location_radarsat(points, 27193, algorithm)
    end = time.time()
    point_per_sec_inv_loc = (end - start) / (nb_line * nb_col)
    assert point_per_sec_inv_loc < 3e-2

    nb_col = 100
    nb_line = 10
    points = []
    for i in range(nb_col):
        for j in range(nb_line):
            points.append(
                np.array(
                    [
                        (1.456805317082818e01 + (i * 0.1)) * np.pi / 180.0,
                        (-2.438902496287664e01 + (j * 0.1)) * np.pi / 180.0,
                        0.0,
                    ],
                )
            )
    start = time.time()
    compute_inverse_location_sentinel(points, 31079, algorithm)
    end = time.time()
    point_per_sec_inv_loc = (end - start) / (nb_line * nb_col)
    assert point_per_sec_inv_loc < 3e-2
