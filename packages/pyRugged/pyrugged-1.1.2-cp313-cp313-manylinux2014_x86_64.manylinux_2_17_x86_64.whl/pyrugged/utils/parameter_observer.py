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

"""pyrugged Class ParameterObserver"""

from abc import abstractmethod

# from org.orekit.time import AbsoluteDate


class ParameterObserver:
    """Tool for observing parameters changes."""

    @abstractmethod
    def value_changed(self, previous_value):
        """Notify that a parameter value has been changed.

        Parameters
        ----------
            previous_value : float
                Previous value
        """

    def reference_date_changed(self, previous_reference_date):
        """Notify that a parameter reference date has been changed."""

        # nothing by default

    def name_changed(self, previous_name):
        """Notify that a parameter name has been changed."""

        # nothing by default

    def selection_changed(self, previous_selection):
        """Notify that a parameter selection has been changed."""

        # nothing by default

    def reference_value_changed(self, previous_reference_value):
        """Notify that a parameter reference value has been changed."""

        # nothing by default

    def min_value_changed(self, previous_min_value):
        """Notify that a parameter minimum value has been changed."""

        # nothing by default

    def max_value_changed(self, previous_max_value):
        """Notify that a parameter maximum value has been changed."""

        # nothing by default

    def scale_changed(self, previous_scale):
        """Notify that a parameter scale has been changed."""

        # nothing by default
