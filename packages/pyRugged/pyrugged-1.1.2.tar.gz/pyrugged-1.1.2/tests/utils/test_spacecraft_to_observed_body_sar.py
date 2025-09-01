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

"""Test of pyrugged Class SpacecraftToObservedBody"""

# pylint: disable=redefined-outer-name

import os

import pytest
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.utils import CartesianDerivativesFilter

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.utils.coordinates_reader import extract_pv_from_txt
from pyrugged.utils.spacecraft_to_observed_body_sar import SpacecraftToObservedBodySAR


def setup_module():
    """
    setup : initVM and reset DUMP_VAR
    """

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None

    init_orekit()


# pylint: disable=unused-variable
def do_test_out_of_time_range(earth, pv_txt_file_path):
    """Test out of time range"""

    min_sensor_date = AbsoluteDate("2023-01-19T19:50:24.253712", TimeScalesFactory.getUTC())
    max_sensor_date = AbsoluteDate("2023-01-20T19:52:44.253712", TimeScalesFactory.getUTC())

    pv_list = extract_pv_from_txt(pv_txt_file_path)

    try:
        sc_to_body = SpacecraftToObservedBodySAR(  # noqa:F841
            earth.body_frame, min_sensor_date, max_sensor_date, 0.01, 5.0, pv_list, 8, CartesianDerivativesFilter.USE_PV
        )

        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.OUT_OF_TIME_RANGE.value.format(
            min_sensor_date,
            pv_list[0].getDate(),
            pv_list[-1].getDate(),
        )


def test_transform_position(earth):
    """Test position transformation for Sentinel 1A data SLC /data/sar_sensor/
    s1a-s6-slc-vh-20230120t195127-20230120t195145-046872-059edc-001.xml"""

    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_pv_0_0.txt"
    )

    min_sensor_date = AbsoluteDate("2023-01-20T19:50:24.253712", TimeScalesFactory.getUTC())
    max_sensor_date = AbsoluteDate("2023-01-20T19:52:44.253712", TimeScalesFactory.getUTC())

    pv_list = extract_pv_from_txt(pv_txt_file_path)

    sc_to_body = SpacecraftToObservedBodySAR(
        earth.body_frame, min_sensor_date, max_sensor_date, 0.01, 5.0, pv_list, 8, CartesianDerivativesFilter.USE_PV
    )

    mid_sensor_date = AbsoluteDate("2023-01-20T19:50:34.253711", TimeScalesFactory.getUTC())

    # From spacecraft to body
    p_body = sc_to_body.get_sc_to_body(mid_sensor_date)

    assert p_body.getCartesian().getPosition().getX() == pytest.approx(6.102189834224000e06, abs=1.0e-2)
    assert p_body.getCartesian().getPosition().getY() == pytest.approx(-3.353503913740000e06, abs=1.0e-3)
    assert p_body.getCartesian().getPosition().getZ() == pytest.approx(1.256277618069000e06, abs=1.0e-1)


def test_sc_to_body_out_of_time_range_1(earth):
    """Test bad configuration"""

    pv_txt_file_path = os.path.join(
        os.path.dirname(__file__), "../data/ref/utils/testSpacecraftToObservedBodySAR_pv_0_0.txt"
    )

    do_test_out_of_time_range(earth, pv_txt_file_path)
