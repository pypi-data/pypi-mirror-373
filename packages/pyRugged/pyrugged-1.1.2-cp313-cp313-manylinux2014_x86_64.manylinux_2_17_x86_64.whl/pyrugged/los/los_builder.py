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

""" pyrugged Class LOSBuilder
"""

from typing import List, Union

import numpy as np
from org.hipparchus.geometry.euclidean.threed import FieldVector3D, Vector3D
from org.orekit.time import AbsoluteDate

from pyrugged.los.fixed_rotation import FixedRotation
from pyrugged.los.fixed_z_homothety import FixedZHomothety
from pyrugged.los.polynomial_rotation import PolynomialRotation
from pyrugged.los.sinusoidal_rotation import SinusoidalRotation
from pyrugged.utils.derivative_generator import DerivativeGenerator
from pyrugged.utils.math_utils import get_norm, to_array_v  # pylint: disable=no-name-in-module
from pyrugged.utils.parameter_driver import ParameterDriver


class TransformAdapter:
    """Adapter from time-independent transform to time-dependent transform."""

    def __init__(self, transform: Union[FixedZHomothety, FixedRotation]):
        """Builds a new instance.

        Parameters
        ----------
            transform : underlying time-independent transform
        """

        self.transform = transform

    # pylint: disable="unused-argument"
    def transform_los(self, i: int, los: np.ndarray, date: AbsoluteDate) -> Union[np.ndarray, FieldVector3D]:
        """Transform a line-of-sight.

        Parameters
        ----------
            i : LOS pixel index
            los : line-of-sight to transform
            date : current date

        Returns
        -------
            result : transformed line-of-sight
        """
        return self.transform.transform_los(i, los)

    # pylint: disable="unused-argument"
    def transform_los_arr(self, i: int, los: np.ndarray, date: AbsoluteDate) -> Union[np.ndarray, FieldVector3D]:
        """Transform a series of line-of-sight.

        Parameters
        ----------
        i : LOS pixel index
        los : line-of-sight to transform
        date : current date

        Returns
        -------
        result : transformed line-of-sight
        """
        return self.transform.transform_los_arr(i, los)

    # pylint: disable="unused-argument"
    def transform_los_derivatives(
        self, i: int, los: np.ndarray, date: AbsoluteDate, generator: DerivativeGenerator
    ) -> Union[np.ndarray, FieldVector3D]:
        """Transform a line-of-sight's' derivatives.

        Used for LOS calibration purposes. It allows to compute
        the Jacobian matrix of the LOS with respect to the parameters, which
        are typically polynomials coefficients representing rotation angles.
        These polynomials can be used for example to model thermo-elastic effects.

        Parameters
        ----------
            i : LOS pixel index
            los : line-of-sight to transform
            date : current date
            generator : generator to use for building Derivative instances

        Returns
        -------
            result : line of sight, and its first partial derivatives with respect to the parameters
        """

        return self.transform.transform_los_derivatives(i, los, generator)

    def get_parameters_drivers(self) -> List[ParameterDriver]:
        """Get parameters drivers."""

        return self.transform.get_parameters_drivers()


class TransformsSequenceLOS:
    """Implement time-independent LOS by recomputing directions by applying all transforms each time."""

    def __init__(self, raw: List[np.ndarray], transforms: List[PolynomialRotation]):
        """Builds a new instance.

        Parameters
        ----------
            raw : raw directions
            transforms : transforms to apply
        """

        # Copy the lists, to ensure immutability of the built object,
        # in case addTransform is called again after build
        # or the raw LOS list is changed by caller
        self.raw = []
        for _, value in enumerate(raw):
            if value is not None:
                if isinstance(value, Vector3D):
                    self.raw.append(to_array_v(value.toArray()))
                else:
                    self.raw.append(value)
            else:
                self.raw.append(None)

        self.transforms = transforms

    def get_nb_pixels(self) -> int:
        """Get the number of pixels."""

        return len(self.raw)

    def get_los(self, index: int, date: AbsoluteDate) -> np.ndarray:
        """Get the line of sight for a given date.

        Parameters
        ----------
            index : LOS pixel index
            date : current date

        Returns
        -------
            result : line of sight
        """

        los = self.raw[index]
        for transform in self.transforms:
            los = transform.transform_los(index, los, date)

        return los/get_norm(los)

    def get_los_arr(self, pixels: List[int], dates: List[AbsoluteDate]) -> np.ndarray:
        """Get the lines of sight for given dates.

        Parameters
        ----------
            pixels : LOS pixel indexes
            dates : current dates

        Returns
        -------
            result : lines of sight
        """

        # los = []
        # for _, pixel in enumerate(pixels):
        #     los.append(self.raw[pixel])

        los = np.array(np.array(self.raw)[pixels]).T
        for transform in self.transforms:
            los = transform.transform_los_arr(pixels, los, dates)

        los = los.T
        norm = np.linalg.norm(los, axis=1)

        # res = []
        # for i in range(len(pixels)):
        #     res.append(los[i, :] / norm[i])

        res = los / norm[:, np.newaxis]
        return res

    def get_los_derivatives(self, index: int, date: AbsoluteDate, generator: DerivativeGenerator):
        """Get the line of sight and its partial derivatives for a given date.

        This method is used for LOS calibration purposes. It allows to compute
        the Jacobian matrix of the LOS with respect to the estimated parameters, which
        are typically polynomials coefficients representing rotation angles.
        These polynomials can be used for example to model thermo-elastic effects.

        Note that in order for the partial derivatives to be properly set up, the
        ParameterDriver.selected(arg)
        method must have been set to True for the various parameters returned
        by get_parameters_drivers() that should be estimated.

        Parameters
        ----------
            index : LOS pixel index
            date : current date
            generator : generator to use for building Derivative instances

        Returns
        -------
            result : line of sight, and its partial derivatives with respect to parameters
        """
        # todo: add test for this function when derivative generator are available

        # # The raw line of sights are considered to be constant
        # los = FieldVector3D(
        #     generator.constant(self.raw[index].getX()),
        #     generator.constant(self.raw[index].getY()),
        #     generator.constant(self.raw[index].getZ()),
        # )
        #
        # # Apply the transforms, which depend on parameters and hence may introduce non-zero derivatives
        # for transform in self.transforms:
        #     los = transform.transform_los_derivatives(index, los, date, generator)
        #
        # return los.normalize()

    def get_parameters_drivers(self) -> List[ParameterDriver]:
        """Get the drivers for LOS parameters."""

        drivers = []
        for transform in self.transforms:
            drivers += transform.get_parameters_drivers()

        return drivers


# class CustomParameterObserver(ParameterObserver): # TODO

#     def value_changed(previous_value, driver):
#         transformed = [None] * len(self.raw)


# pylint: disable="too-few-public-methods"
class FixedLOS(TransformsSequenceLOS):
    """Implement time-independent LOS by computing directions only when parameters are changed."""

    def __init__(self, raw: List[np.ndarray], transforms: List[PolynomialRotation]):
        """Builds a new instance.

        Parameters
        ----------
            raw : raw directions
            transforms : transforms to apply (must be time-independent)
        """

        super().__init__(raw, transforms)
        self.transformed = [None] * len(self.raw)

        # resetting_observer = CustomParameterObserver() TODO
        # for driver in self.get_parameters_drivers():
        #     driver.add_observer(resetting_observer)

    def get_los(self, index: int, date: AbsoluteDate) -> np.ndarray:
        """Get the line of sight for a given date.

        Parameters
        ----------
            index : LOS pixel index
            date : current date

        Returns
        -------
            result : line of sight
        """

        # TODO : how to check if los has to be recomputed
        # if self.transformed[index] is None:
        # Recompute the transformed los direction only if needed
        res = super().get_los(index, date)
        try:
            self.transformed[index] = res
        except IndexError:
            self.transformed.append(res)
            return res
        return self.transformed[index]

    def get_los_arr(self, pixels: List[int], dates: List[AbsoluteDate]) -> np.ndarray:
        """Get the line of sight for a given date.

        Parameters
        ----------
            pixels : LOS pixel indexes
            dates : current dates

        Returns
        -------
            result : line of sight
        """

        # TODO : how to check if los has to be recomputed
        # if self.transformed[index] is None:
        # Recompute the transformed los direction only if needed
        res = super().get_los_arr(pixels, dates)
        self.transformed = []
        self.transformed.append(res)

        return res

    def get_los_derivatives(self, index: int, date: AbsoluteDate, generator: DerivativeGenerator):
        """Get the line of sight and its partial derivatives for a given date.

        This method is used for LOS calibration purposes. It allows to compute
        the Jacobian matrix of the LOS with respect to the estimated parameters, which
        are typically polynomials coefficients representing rotation angles.
        These polynomials can be used for example to model thermo-elastic effects.

        Note that in order for the partial derivatives to be properly set up, the
        ParameterDriver.selected(arg)
        method must have been set to True for the various parameters returned
        by get_parameters_drivers() that should be estimated.

        Parameters
        ----------
            index : LOS pixel index
            date : current date
            generator : generator to use for building Derivative instances

        Returns
        -------
            result : line of sight, and its partial derivatives with respect to parameters
        """
        raise NotImplementedError("This method is not implemented in the TransformsSequenceLOS class")


class LOSBuilder:
    """Builder for lines-of-sight list.

    This builder aims at creating lines-of-sight directions which are
    the result of several transforms applied to an initial list of raw
    directions. It therefore allows to take into account the optical
    path due to mirrors and the alignments of sensors frames with respect
    to a spacecraft.

    """

    def __init__(self, raw_los: List[np.ndarray]):
        """Builds a new instance.

        Parameters
        ----------
            raw_los : raw fixed lines-of-sight
        """

        self.raw_los = [np.array(item.toArray())
                        if ((item is not None) and isinstance(item, Vector3D))
                        else item for item in raw_los]
        self.transforms = []
        self.time_independent = True

    def add_ti_los_transform(self, transform: Union[FixedZHomothety, FixedRotation]):
        """Add a transform to be applied after the already registered transforms.

        Parameters
        ----------
            transform : transform to be applied to the lines-of-sight
        """

        self.transforms.append(TransformAdapter(transform))

    def add_los_transform(self, transform: Union[PolynomialRotation, SinusoidalRotation]):
        """Add a transform to be applied after the already registered transforms.

        Parameters
        ----------
            transform : transform to be applied to the lines-of-sight
        """

        self.transforms.append(transform)
        self.time_independent = False

    def build(self) -> Union[FixedLOS, TransformsSequenceLOS]:
        """Build a lines-of-sight provider.

        Returns
        -------
            res : lines-of-sight provider
        """

        if self.time_independent:
            # Fast implementation for time-independent lines-of-sight
            res = FixedLOS(self.raw_los, self.transforms)

        else:
            # Regular implementation, for time-dependent lines-of-sight
            res = TransformsSequenceLOS(self.raw_los, self.transforms)

        return res
