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

"""pyrugged Class ParameterDriver"""


import sys

import numpy as np
from org.orekit.time import AbsoluteDate

from pyrugged.utils.parameter_observer import ParameterObserver


class ParameterDriver:
    """Class allowing to drive the value of a parameter.

    This class is typically used as a bridge between an estimation
    algorithm (typically orbit determination or optimizer) and an
    internal parameter in a physical model that needs to be tuned,
    or a bridge between a finite differences algorithm and an
    internal parameter in a physical model that needs to be slightly
    offset. The physical model will expose to the algorithm a
    set of instances of this class so the algorithm can call the
    set_value(double) method to update the
    parameter value. Each time the value is set, the physical model
    will be notified as it will register a ParameterObserver
    for this purpose.

    This design has two major goals. First, it allows an external
    algorithm to drive internal parameters almost anonymously, as it only
    needs to get a list of instances of this class, without knowing
    what they really drive. Second, it allows the physical model to
    not expose directly setters methods for its parameters. In order
    to be able to modify the parameter value, the algorithm
    must retrieve a parameter driver.

    """

    def __init__(self, name: str, reference_value: float, scale: float, min_value: float, max_value: float):
        """Builds a new instance."""

        if float(np.abs(scale)) <= sys.float_info.min:
            raise ValueError("Too small 'scale' parameter.")

        self._name = name
        self._reference_value = reference_value
        self._scale = scale
        self._min_value = min_value
        self._max_value = max_value
        self._reference_date = None
        self._value = reference_value
        self._selected = False
        self._observers = []

    def add_observer(self, observer: ParameterObserver):
        """Add an observer for this driver.

        The observer ParameterObserver.value_changed(float, ParameterDriver)
        method is called once automatically when the
        observer is added, and then called at each value change.

        Parameters
        ----------
            observer : observer to add
        """

        observer.value_changed(self._value)
        self._observers.append(observer)

    # def remove_observer(self, observer: ParameterObserver):
    #     """Remove an observer.

    #     Parameters
    #     ----------
    #         observer : observer to remove
    #     """

    #     self.observers.remove(observer)

    # def replace_observer(self, old_observer: ParameterObserver, new_observer: ParameterObserver):
    #     """Replace an observer.

    #     Parameters
    #     ----------
    #         old_observer : observer to replace
    #         new_observer : new observer to use
    #     """

    #     for index, _ in enumerate(self.observers):
    #         if self.observers[index] == old_observer:
    #             self.observers[index] = new_observer

    # @property
    # def observers(self) -> List[ParameterObserver]:
    #     """Get the observers for this driver."""

    #     return self._observers

    @property
    def name(self) -> str:
        """Get name parameter."""

        return self._name

    @name.setter
    def name(self, name: str):
        """Set name parameter."""

        # previous_name = self._name
        self._name = name
        # for observer in self._observers:
        #     observer.name_changed(previous_name)

    @property
    def reference_value(self) -> float:
        """Get reference value parameter."""

        return self._reference_value

    @reference_value.setter
    def reference_value(self, reference_value: float):
        """Set reference value parameter."""

        # previous_reference_value = self._reference_value
        self._reference_value = reference_value
        # for observer in self._observers:
        #     observer.reference_value_changed(previous_reference_value)

    @property
    def min_value(self) -> float:
        """Get min value parameter."""

        return self._min_value

    @min_value.setter
    def min_value(self, min_value: float):
        """Set min value parameter."""

        # previous_min_value = self._min_value
        self._min_value = min_value
        # for observer in self._observers:
        #     observer.min_value_changed(previous_min_value)

    @property
    def max_value(self) -> float:
        """Get max value parameter."""

        return self._max_value

    @max_value.setter
    def max_value(self, max_value: float):
        """Set max value parameter."""

        # previous_max_value = self._max_value
        self._max_value = max_value
        # for observer in self._observers:
        #     observer.max_value_changed(previous_max_value)

    @property
    def scale(self) -> float:
        """Get scale parameter."""

        return self._scale

    @scale.setter
    def scale(self, scale: float):
        """Set scale parameter."""

        # previous_scale = self._scale
        self._scale = scale
        # for observer in self._observers:
        #     observer.scale_changed(previous_scale)

    @property
    def normalized_value(self) -> float:
        """Get normalized value.

        The normalized value is a non-dimensional value
        suitable for use as part of a vector in an optimization
        process. It is computed as (current - reference) / scale.

        """

        return (self._value - self._reference_value) / self._scale

    @normalized_value.setter
    def normalized_value(self, normalized: float):
        """Set normalized value.

        The normalized value is a non-dimensional value
        suitable for use as part of a vector in an optimization
        process. It is computed as (current - reference) / scale.

        Parameters
        ----------
            normalized : normalized value
        """

        self._value = self._reference_value + self._scale * normalized

    @property
    def reference_date(self) -> AbsoluteDate:
        """Get reference date parameter."""

        return self._reference_date

    @reference_date.setter
    def reference_date(self, reference_date: AbsoluteDate):
        """Set reference date parameter."""

        # previous_reference_date = self._reference_date
        self._reference_date = reference_date
        # for observer in self._observers:
        #     observer.reference_date_changed(previous_reference_date)

    @property
    def value(self) -> float:
        """Get value parameter."""

        return self._value

    @value.setter
    def value(self, value: float):
        """Set value parameter."""

        previous_value = self._value
        self._value = value
        for observer in self._observers:
            observer.value_changed(previous_value)

    @property
    def selected(self) -> bool:
        """Get selected parameter."""

        return self._selected

    @selected.setter
    def selected(self, selected: bool):
        """Configure a parameter selection status.

        Selection is used for estimated parameters in orbit determination,
        or to compute the Jacobian matrix in partial derivatives computation.
        """

        # previous_selection = self._selected
        self._selected = selected
        # for observer in self._observers:
        #     observer.selection_changed(previous_selection)

    def to_string(self) -> str:
        """Get a text representation of the parameter."""

        return f'{self._name}{" = "}{self._value}'
