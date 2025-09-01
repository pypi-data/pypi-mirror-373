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

"""Test of pyrugged Class LineSensor"""


import json
import os
from tempfile import NamedTemporaryFile

import numpy as np
import pytest
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.time import AbsoluteDate, TimeScalesFactory

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.line_sensor.line_sensor import LinearLineDatation, LineSensor
from tests.helpers import create_los_perfect_line


def setup_module():
    """
    setup : initVM
    """

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None

    init_orekit()


def teardown_module():
    """
    teardown : reset DUMP_VAR
    """
    dump_manager.DUMP_VAR = None


def test_line_sensor():
    """line sensor test"""

    ground_truth_dump_file = os.path.join(os.path.dirname(__file__), "../data/ref/errors/line_sensor_dump.json")
    with open(ground_truth_dump_file, "r", encoding="utf-8") as dfile_orig:
        data_ground_truth = json.load(dfile_orig)

    with NamedTemporaryFile(suffix=".json", delete=True) as dump_file:

        # Dump activation
        dump_manager.DUMP_VAR = dump_manager.DumpManager()

        dump_manager.DUMP_VAR.activate(dump_file.name)

        dimension = 400

        crossing = AbsoluteDate("2012-01-07T11:21:15.000", TimeScalesFactory.getUTC())

        # one line sensor
        # position: 1.5m in front (+X) and 20 cm above (-Z) of the S/C center of mass
        # los: swath in the (YZ) plane, centered at +Z, ±10° aperture, 960 pixels
        position = Vector3D(1.5, 0.0, -0.2)
        los = create_los_perfect_line(
            Vector3D.PLUS_K,
            Vector3D.PLUS_I,
            float(np.radians(10.0)),
            dimension,
        ).build()

        rate = 1.0 / 1.5e-3
        # Linear datation model: at reference time we get line 200, and the rate is one line every 1.5ms
        line_datation = LinearLineDatation(
            crossing,
            dimension / 2,
            rate,
        )

        line_sensor = LineSensor(
            "line",
            line_datation,
            position,
            los,
        )

        assert line_sensor.get_date(100.0).durationFrom(
            AbsoluteDate("2012-01-07T11:21:14.850", TimeScalesFactory.getUTC())
        ) == pytest.approx(0, abs=1e-15)
        assert line_sensor.datation_model.reference_line == 200
        assert line_sensor.get_line(crossing) == 200.0
        assert Vector3D(line_sensor.get_los(crossing, 0).tolist()).equals(
            Vector3D(0.0, 0.17364817766693033, 0.9848077530122081)
        )
        assert line_sensor.get_rate() == rate

        # Check if dumped data is correct
        with open(dump_file.name, "r", encoding="utf-8") as dfile:
            data = json.load(dfile)

        assert data == data_ground_truth
