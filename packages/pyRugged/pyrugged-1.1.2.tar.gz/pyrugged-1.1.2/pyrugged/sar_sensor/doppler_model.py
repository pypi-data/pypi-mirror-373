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

"""pyrugged Class DopplerModel"""


class DopplerModel:
    """Doppler model for SAR sensor, only Zero Doppler available, general Doppler model still to be developed."""

    def __init__(self, doppler_contribution: float = 0.0):
        """Builds a new instance.

        Parameters
        ----------
            doppler_contribution : doppler contribution
        """

        self._doppler_contribution = doppler_contribution

    @property
    def get_doppler(self) -> float:
        """Get the doppler model of the sensor, only Zero Doppler available,
        general Doppler model still to be developed."""

        return self.zero_doppler

    @property
    def zero_doppler(self) -> float:
        """Get the zero doppler model of the sensor."""

        self._doppler_contribution = 0.0
        return self._doppler_contribution
