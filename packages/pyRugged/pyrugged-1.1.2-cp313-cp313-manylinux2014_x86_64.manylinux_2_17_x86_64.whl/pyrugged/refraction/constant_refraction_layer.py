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

"""pyrugged Class ConstantRefractionLayer"""


class ConstantRefractionLayer:
    """Class that represents a constant refraction layer to be used with MultiLayerModel."""

    def __init__(self, lowest_altitude: float, refractive_index: float):
        """Builds a new instance.

        Parameters
        ----------
            lowest_altitude : lowest altitude of the layer (m)
            refractive_index : refractive index of the layer
        """

        self.lowest_altitude = lowest_altitude
        self.refractive_index = refractive_index

    def get_lowest_altitude(self) -> float:
        """Get lowest altitude of the layer (m)"""

        return self.lowest_altitude

    def get_refractive_index(self) -> float:
        """Get refractive index of the layer"""

        return self.refractive_index
