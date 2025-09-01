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

"""pyrugged test Class for RangeFromPixel"""

import numpy as np
import pytest

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.sar_sensor.range_from_pixel import RangeFromPixel, RangeGridCreation
from pyrugged.utils.constants import Constants

PIX_TO_TEST = 1000


def setup_module():
    """
    setup : initVM and reset DUMP_VAR
    """

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None

    init_orekit()


def test_slc_range_from_pixel():
    """SLC RADAR SAT"""
    pixel_time_incresing = False
    sr_coefficient = np.array([9.738835958311997e05, 1.0, 0.0, 0.0, 0.0, 0.0])[::-1]
    total_pixel_number = 20577
    ground_range_or = 0.0
    pixel_size_slc = 1.33117902
    range_grid_construction = RangeGridCreation(total_pixel_number, sr_coefficient)
    ranges = [
        [
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 0, pixel_time_incresing
            )
        ],
        [
            range_grid_construction.ground_range_to_slant_range_polynom_application(
                pixel_size_slc, ground_range_or, 20576, pixel_time_incresing
            )
        ],
    ]

    range_pix_correspondance = RangeFromPixel(np.array([0, 20576]), np.array([0]), np.array(ranges))
    assert pytest.approx(
        range_pix_correspondance.get_range(np.array([PIX_TO_TEST, 0])), abs=1e-9
    ) == range_grid_construction.ground_range_to_slant_range_polynom_application(
        pixel_size_slc, ground_range_or, PIX_TO_TEST, pixel_time_incresing
    )


def test_grd_range_from_pixel():
    """GRD RADAR SAT"""
    pixel_time_incresing = False
    gr_coefficient = [
        8.388989105455031e05,
        3.436893501000000e-01,
        5.992276886600000e-07,
        -2.470559360100000e-13,
        -1.110938369500000e-19,
        1.983900255700000e-25,
    ][::-1]
    total_pixel_number = 8205
    ground_range_or = 0.0
    pixel_size_slc = 1.25000000e01
    range_grid_construction = RangeGridCreation(total_pixel_number, gr_coefficient)

    ranges = []
    pixels = []
    for i in range(0, 20577, 200):
        ranges.append(
            [
                range_grid_construction.ground_range_to_slant_range_polynom_application(
                    pixel_size_slc, ground_range_or, i, pixel_time_incresing
                )
            ]
        )
        pixels.append(i)

    range_pix_correspondance = RangeFromPixel(np.array(pixels), np.array([0]), np.array(ranges))
    assert range_pix_correspondance.get_range(
        np.array([PIX_TO_TEST, 0])
    ) == range_grid_construction.ground_range_to_slant_range_polynom_application(
        pixel_size_slc, ground_range_or, PIX_TO_TEST, pixel_time_incresing
    )


def test_sentinel_range_from_pixel():
    """Sentinel grd"""
    lines = [0, 1333, 3999, 5332]
    pixels = [0, 403, 1209, 1612]

    ranges = [
        [6.087179789572389e-03, 6.087179789571471e-03, 6.087179789545996e-03, 6.087179789574176e-03],
        [6.105331060141939e-03, 6.105331901980906e-03, 6.105333405292106e-03, 6.105334174443712e-03],
        [6.141862979423282e-03, 6.141865488833737e-03, 6.141869969692967e-03, 6.123565228820869e-03],
        [6.160242253370319e-03, 6.160245588502567e-03, 6.141872262697154e-03, 6.160254591395568e-03],
    ]

    range_pix_correspondance = RangeFromPixel(np.array(pixels), np.array(lines), np.array(ranges), True)
    assert (
        pytest.approx(range_pix_correspondance.get_range(np.array([0, 2666])), abs=1e-3)
        == 6.087179789562094e-03 * Constants.SPEED_OF_LIGHT / 2
    )
    print(917901.7901225939)
    print(pytest.approx(range_pix_correspondance.get_range(np.array([806, 0]))))
    print(6.123559020109031e-03 * Constants.SPEED_OF_LIGHT / 2)
    assert (
        pytest.approx(range_pix_correspondance.get_range(np.array([806, 0])), abs=10)
        == 6.123559020109031e-03 * Constants.SPEED_OF_LIGHT / 2
    )


def test_sentinel_range_from_pixel_slc():
    """Sentinel slc"""
    lines = [0, 734, 2202, 2936]
    pixels = [0, 884, 2652, 3536]

    ranges = [
        [6.074426428179243e-03, 6.074426428179243e-03, 6.074426428179243e-03, 6.074426428179243e-03],
        [6.093267649205340e-03, 6.093267649205340e-03, 6.093267649205340e-03, 6.093267649205340e-03],
        [6.130950091257533e-03, 6.130950091257533e-03, 6.130950091257533e-03, 6.130950091257533e-03],
        [6.149791312283629e-03, 6.149791312283629e-03, 6.149791312283629e-03, 6.149791312283629e-03],
    ]

    range_pix_correspondance = RangeFromPixel(np.array(pixels), np.array(lines), np.array(ranges), True)
    assert (
        pytest.approx(range_pix_correspondance.get_range(np.array([0, 1468])), abs=1e-9)
        == 6.074426428179243e-03 * Constants.SPEED_OF_LIGHT / 2
    )
    assert (
        pytest.approx(range_pix_correspondance.get_range(np.array([1768, 0])), abs=1e-9)
        == 6.112108870231436e-03 * Constants.SPEED_OF_LIGHT / 2
    )
