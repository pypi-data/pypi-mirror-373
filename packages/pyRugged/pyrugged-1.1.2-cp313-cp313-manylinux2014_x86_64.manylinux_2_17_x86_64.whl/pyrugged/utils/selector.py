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

"""pyrugged Class Selector"""


class Selector:
    """Class for selecting one value among two."""

    def __init__(self):
        """Builds a new instance."""

    def select_first(self, v_1: float, v_2: float) -> bool:
        """Check if first value should be selected.

        Parameters
        ----------
            v_1 : first value
            v_2 : second value

        Returns
        -------
            result : true if v_1 should be selected
        """

    def select(self, v_1: float, v_2: float) -> float:
        """Select a value.

        Parameters
        ----------
            v_1 : first value
            v_2 : second value

        Returns
        -------
            result : selected value, v_1 or v_2
        """

        return v_1 if self.select_first(v_1, v_2) else v_2
