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

"""Test of pyrugged Class NormalizedGeodeticPoint"""


from pyrugged.bodies.normalized_geodetic_point import GeodeticPoint, NormalizedGeodeticPoint
from pyrugged.configuration.init_orekit import init_orekit

init_orekit(use_internal_data=False)


def test_normalized_geodetic_point_equals():
    """Basic tests"""
    normalized_point = NormalizedGeodeticPoint(1.0, 2.0, 3.0, 4.0)
    point = GeodeticPoint(1.0, 2.0, 3.0)
    assert normalized_point == NormalizedGeodeticPoint(1.0, 2.0, 3.0, 4.0)
    assert normalized_point == point
    assert normalized_point != NormalizedGeodeticPoint(0.0, 2.0, 3.0, 4.0)
    assert normalized_point != NormalizedGeodeticPoint(1.0, 0.0, 3.0, 4.0)
    assert normalized_point != NormalizedGeodeticPoint(1.0, 2.0, 0.0, 4.0)
    assert normalized_point != NormalizedGeodeticPoint(1.0, 2.0, 3.0, 10.0)
    assert point != NormalizedGeodeticPoint(1.0, 2.0, 3.0, 10.0)


if __name__ == "__main__":
    test_normalized_geodetic_point_equals()
