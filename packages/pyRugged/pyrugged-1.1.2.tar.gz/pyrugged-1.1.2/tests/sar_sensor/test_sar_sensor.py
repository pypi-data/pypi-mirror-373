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

"""pyrugged test Class for SARSensor"""

import numpy as np
import pytest
from org.orekit.time import AbsoluteDate, TimeScalesFactory

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.sar_sensor.doppler_model import DopplerModel
from pyrugged.sar_sensor.range_from_pixel import RangeFromPixel, RangeGridCreation
from pyrugged.sar_sensor.sar_line_datation import SARLineDatation
from pyrugged.sar_sensor.sar_sensor import SARSensor


def setup_module():
    """
    setup : initVM
    """

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None

    init_orekit()


def test_sar_sensor_radarsat():
    """sar sensor test"""

    # Range model
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
                pixel_size_slc, ground_range_or, 20577, pixel_time_incresing
            )
        ],
    ]
    range_model = RangeFromPixel(np.array([0, 20577]), np.array([0]), np.array(ranges))

    # Datation model
    reference_date = AbsoluteDate("2016-06-05T06:02:08.226323", TimeScalesFactory.getUTC())
    lines = [0, 27193]
    pixels = [0]

    corresponding_date_gap = [
        [0, reference_date.durationFrom(AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC()))]
    ]
    sar_datation_model = SARLineDatation(
        np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap)
    )

    # Doppler model
    doppler_model = DopplerModel()

    # SAR sensor
    sar_sensor = SARSensor("sar", sar_datation_model, range_model, doppler_model, True)

    assert pytest.approx(
        sar_sensor.get_range(np.array([1000, 0])), abs=1e-9
    ) == range_grid_construction.ground_range_to_slant_range_polynom_application(
        pixel_size_slc, ground_range_or, 1000, pixel_time_incresing
    )
    assert sar_sensor.get_date(np.array([0, 0]))[0].equals(reference_date)
    assert sar_sensor.is_antenna_pointing_right
    assert sar_sensor.get_doppler == 0
