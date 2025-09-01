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

"""pyrugged test module for Dump and Dumpmanager"""

# pylint: disable=consider-using-with
import json
import os
from tempfile import NamedTemporaryFile

from org.orekit.frames import FramesFactory

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager


def setup_module():
    """
    setup : initVM and reset DUMP_VAR
    """
    init_orekit(use_internal_data=False)

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None


def teardown_module():
    """
    teardown : reset DUMP_VAR
    """
    dump_manager.DUMP_VAR = None


def test_dump_ellipsoid():
    """Test dumpManager class to dump ellipsoid"""
    gt_file = os.path.join(os.path.dirname(__file__), "../data/ref/errors/dump_ellips.json")
    with open(gt_file, "r", encoding="utf-8") as dfile_orig:
        data_ground_truth = json.load(dfile_orig)

    with NamedTemporaryFile(suffix=".json") as dump_file:
        dump_tool = dump_manager.DumpManager()
        dump_tool.activate(dump_file.name)
        ellipsoid = ExtendedEllipsoid(1.0, 2.0, FramesFactory.getEME2000())
        dump_tool.dump_ellipsoid(ellipsoid)
        with open(dump_file.name, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)
        assert data == data_ground_truth


if __name__ == "__main__":
    test_dump_ellipsoid()
