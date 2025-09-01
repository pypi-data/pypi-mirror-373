#!/usr/bin/env python
# coding: utf8
#
# Copyright 2024 CS GROUP
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

"""Test of math utils routines"""

import numpy as np

# pylint: disable=no-name-in-module
import pyrugged.utils.math_utils as mu


def test_dot_functions():
    """
    Unit test for functions dot and dot_n (working with float128)
    """

    # 1D case
    vec1 = np.array([1.1, 2.2, 10 / 3])
    vec2 = np.array([4.4, 5.5, 6.6])

    out = mu.dot(vec1, vec2)
    out_n = mu.dot_n(vec1[np.newaxis, :], vec2[np.newaxis, :])
    ref = np.dot(vec1, vec2)
    assert np.allclose(out, ref, rtol=0, atol=1e-11)
    assert np.allclose(out_n, [ref], rtol=0, atol=1e-11)

    # 2D case
    vec1 = np.array(
        [
            [1.1, 2.2, 10 / 3],
            [1.2, 2.3, 10 / 3 + 0.1],
            [1.3, 2.4, 10 / 3 + 0.2],
            [1.4, 2.5, 10 / 3 + 0.3],
        ]
    )
    vec2 = np.array(
        [
            [4.4, 5.5, 6.6],
            [4.5, 5.6, 6.7],
            [4.6, 5.7, 6.8],
            [4.7, 5.8, 6.9],
        ]
    )

    out = mu.dot(vec1.T, vec2.T)
    out_n = mu.dot_n(vec1, vec2)
    ref = np.sum(vec1 * vec2, axis=1)
    assert np.allclose(out, ref, rtol=0, atol=1e-11)
    assert np.allclose(out_n, [ref], rtol=0, atol=1e-11)
