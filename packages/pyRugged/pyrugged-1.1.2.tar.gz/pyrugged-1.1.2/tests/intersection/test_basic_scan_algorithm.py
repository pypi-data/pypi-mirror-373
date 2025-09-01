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
"""
basic scan algorithm test
"""

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.intersection.basic_scan_algorithm import BasicScanAlgorithm

from .algorithm_generic_tests import (
    generic_test_cliffs_of_moher,
    generic_test_mayon_volcano_on_sub_tile_corner,
    generic_test_mayon_volcano_within_pixel,
)


def setup_module():
    """
    setup : initVM
    """
    init_orekit(use_internal_data=False)


def test_mayon_volcano_within_pixel(mayon_volcano_context, earth):
    generic_test_mayon_volcano_within_pixel(BasicScanAlgorithm, mayon_volcano_context, earth)


def test_mayon_volcano_on_sub_tile_corner(mayon_volcano_context, earth):
    generic_test_mayon_volcano_on_sub_tile_corner(BasicScanAlgorithm, mayon_volcano_context, earth)


def test_cliffs_of_moher(cliffs_of_moher_context, earth):
    generic_test_cliffs_of_moher(BasicScanAlgorithm, cliffs_of_moher_context, earth)
