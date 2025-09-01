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

"""Test of pyrugged Class SARLineDatation"""

import numpy as np
from org.orekit.time import AbsoluteDate, TimeScalesFactory

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.sar_sensor.sar_line_datation import SARLineDatation


def setup_module():
    """
    setup : initVM and reset DUMP_VAR
    """

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None

    init_orekit()


def test_date_from_row_radarsat():
    """SLC RADAR SAT on product_SLC.xml"""

    reference_date = AbsoluteDate("2016-06-05T06:02:08.226323", TimeScalesFactory.getUTC())

    lines = [0, 27193]
    pixels = [0]
    corresponding_date_gap = [
        [0, reference_date.durationFrom(AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC()))]
    ]
    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))

    assert reference_date.shiftedBy(
        reference_date.durationFrom(AbsoluteDate("2016-06-05T06:02:16.108620", TimeScalesFactory.getUTC()))
        / 27193
        * 1000
    ).isCloseTo(sar_datation.get_date(np.array([0, 1000]))[0], 0.000001)


def test_date_from_row_pixel_sentinel_gr():
    """SLC RADAR SAT on product_SLC.xml"""
    reference_date = AbsoluteDate("2023-01-22T11:55:24.052832", TimeScalesFactory.getUTC())
    lines = [0, 1333, 3999]
    pixels = [0, 403]

    corresponding_date_gap = [
        [
            0,
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053751", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055590", TimeScalesFactory.getUTC())),
        ],
        [
            -reference_date.durationFrom(AbsoluteDate("2023-01-20T19:51:27.266107", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:26.053760", TimeScalesFactory.getUTC())),
            -reference_date.durationFrom(AbsoluteDate("2023-01-22T11:55:30.055599", TimeScalesFactory.getUTC())),
        ],
    ]

    sar_datation = SARLineDatation(np.array(pixels), np.array(lines), reference_date, np.array(corresponding_date_gap))
    assert sar_datation.get_date([0, 2666])[0].isCloseTo(
        AbsoluteDate("2023-01-22T11:55:28.054670", TimeScalesFactory.getUTC()), 0.000001
    )
    assert sar_datation.get_date([806, 2666])[0].isCloseTo(
        AbsoluteDate("2023-01-22T11:55:28.054688", TimeScalesFactory.getUTC()), 0.000001
    )
