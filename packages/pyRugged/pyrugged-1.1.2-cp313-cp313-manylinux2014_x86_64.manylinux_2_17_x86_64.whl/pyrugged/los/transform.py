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

"""pyrugged Class DynamicTransform"""

from typing import Self

import numpy as np
from org.hipparchus.geometry.euclidean.threed import Rotation, Vector3D
from org.orekit.frames import Transform
from org.orekit.time import AbsoluteDate
from org.orekit.utils import AngularCoordinates, PVCoordinates
from scipy.spatial.transform import Rotation as R


def vector3d_to_array(vec: Vector3D) -> np.ndarray:
    """
    Utility function to convert Vectort3D to numpy
    :param vec: input 3D vector
    :return: numpy array of shape (3)
    """
    return np.array([vec.getX(), vec.getY(), vec.getZ()])


def rotation_to_array(rot: Rotation) -> np.array:
    """
    Utility function to convert Rotation to quaternion array [q1, q2, q3, q0] (using scalar last
    convention).
    :param rot: input rotation
    :return: quaternions as numpy array of shape (4)
    """
    return np.array([rot.getQ1(), rot.getQ2(), rot.getQ3(), rot.getQ0()])


def array_to_vector3d(arr: np.ndarray) -> Vector3D:
    """
    Utility function to convert a Numpy array of shape (3) to Vector3D
    :param arr: input array of shape (3)
    :return: output Vector3D
    """
    if arr is None:
        return Vector3D.ZERO
    assert arr.shape == (3,)
    return Vector3D(float(arr[0]), float(arr[1]), float(arr[2]))


def array_to_rotation(arr: np.ndarray) -> Rotation:
    """
    Utility function to convert a Numpy array of shape (4) to Rotation (quaternions following
    calar-last convention). Assume the quaternion are already normalized.
    :param arr: input array of shape (4)
    :return: output Rotation
    """
    if arr is None:
        return Rotation.IDENTITY
    assert arr.shape == (4,)
    return Rotation(float(arr[3]), float(arr[0]), float(arr[1]), float(arr[2]), False)


def transform_to_numpy(transforms: Transform | list[Transform], filter_identity: bool = True) -> list[np.ndarray]:
    """
    Export elements of a Transform list as a list of numpy arrays in the following order: translation,
    velocity, acceleration, rotation, rotation rate, rotation acceleration.
    :param transforms: transforms to export to numpy
    :param filter_identity: If some elements only contain identity elements, they are replaced by None.
    :return: list of transform elements as numpy arrays (each transform elements have been stacked)
    """
    if isinstance(transforms, Transform):
        transforms = [transforms]

    # read all Transforms
    all_parts = [[] for idx in range(6)]
    for item in transforms:
        elements = [
            vector3d_to_array(item.getTranslation()),
            vector3d_to_array(item.getVelocity()),
            vector3d_to_array(item.getAcceleration()),
            rotation_to_array(item.getRotation()),
            vector3d_to_array(item.getRotationRate()),
            vector3d_to_array(item.getRotationAcceleration()),
        ]
        for idx in range(6):
            all_parts[idx].append(elements[idx])

    # fuse all times together
    all_parts = [np.array(elem) for elem in all_parts]

    # remove identity
    if filter_identity:
        for idx in range(6):
            diff_to_identity = all_parts[idx]
            if idx == 3:
                # special case for rotation
                diff_to_identity = all_parts[idx] - np.array([[0.0, 0.0, 0.0, 1.0]])
            if np.all(diff_to_identity == 0.0):
                # all elements are identity => we can skip this term
                all_parts[idx] = None
    return all_parts


def get_corresponding_orekit_transform(elements: list[np.ndarray], sub_index: int = None) -> Transform:
    """
    Create an equivalement org.orekit.frames.Transform
    """
    # Build an equivalement Orekit Transform
    # WARNING: in org.orekit.frame.Transform uses the model: Y = Rotation( Translation(X) )
    filtered = []
    for item in elements:
        if sub_index is None:
            filtered.append(item)
        elif item is not None and len(item.shape) == 2:
            filtered.append(item[sub_index, :])
        else:
            filtered.append(item)
    date = AbsoluteDate.J2000_EPOCH
    pv_coord = PVCoordinates(
        array_to_vector3d(filtered[0]),
        array_to_vector3d(filtered[1]),
        array_to_vector3d(filtered[2]),
    )
    angular = AngularCoordinates(
        array_to_rotation(filtered[3]),
        array_to_vector3d(filtered[4]),
        array_to_vector3d(filtered[5]),
    )

    orekit_trans = Transform(date, pv_coord)
    orekit_rot = Transform(date, angular)
    return Transform(date, orekit_trans, orekit_rot)


class DynamicTransform:
    """
    DynamicTransform class, can be time shifted
    """

    def __init__(
        self,
        translation: np.ndarray | None = None,
        velocity: np.ndarray | None = None,
        acceleration: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        rotation_rate: np.ndarray | None = None,
        rotation_acceleration: np.ndarray | None = None,
    ):
        self.translation = translation
        self.velocity = velocity
        self.acceleration = acceleration
        self.rotation = rotation
        self.rotation_rate = rotation_rate
        self.rotation_acceleration = rotation_acceleration

    def __len__(self) -> int:
        """
        Length operator
        """
        size = 0
        if self.translation is not None:
            size = max(size, self.translation.size // 3)
        if self.velocity is not None:
            size = max(size, self.velocity.size // 3)
        if self.acceleration is not None:
            size = max(size, self.acceleration.size // 3)
        if self.rotation is not None:
            size = max(size, self.rotation.size // 4)
        if self.rotation_rate is not None:
            size = max(size, self.rotation_rate.size // 3)
        if self.rotation_acceleration is not None:
            size = max(size, self.rotation_acceleration.size // 3)
        return size

    @staticmethod
    def _make_2d(arr: np.ndarray):
        """
        Return an array that is always 2D. A new axis is added at the begining if the input is 1D
        :param arr: input array
        :return: output 2D array
        """
        if len(arr.shape) == 1:
            return arr[np.newaxis, :]
        return arr

    def shifted(self, delay) -> Self:
        """
        Shift the current transform by a time offset
        :param delay: time offset to apply
        :return: Shifted transform
        """
        size = len(self)
        if isinstance(delay, list):
            delay = np.array(delay, dtype="float64")
        if isinstance(delay, np.ndarray) and len(delay.shape) == 1:
            delay = delay[:, np.newaxis]

        # Cartesian part
        next_translation = np.zeros((size, 3), dtype="float64")
        next_velocity = np.zeros((size, 3), dtype="float64")
        next_acceleration = None
        if self.translation is not None:
            next_translation += self._make_2d(self.translation)
        if self.velocity is not None:
            next_translation += delay * self._make_2d(self.velocity)
            next_velocity += self._make_2d(self.velocity)
        if self.acceleration is not None:
            next_translation += 0.5 * delay * delay * self._make_2d(self.acceleration)
            next_velocity += delay * self._make_2d(self.acceleration)
            next_acceleration = self._make_2d(self.acceleration)

        # Angular part
        next_rotation = R.identity(num=size)
        next_rotation_rate = np.zeros((size, 3), dtype="float64")
        next_rotation_acc = None
        if self.rotation is not None:
            next_rotation = R.from_quat(self.rotation)
        rate_contrib = R.identity(num=size)
        rate = np.zeros((1,))
        if self.rotation_rate is not None:
            rate = np.linalg.norm(self._make_2d(self.rotation_rate), axis=1, keepdims=True)
        if any(rate != 0.0):
            rate_contrib = R.from_rotvec(self._make_2d(self.rotation_rate) * delay)
            next_rotation = next_rotation * rate_contrib
            next_rotation_rate += self._make_2d(self.rotation_rate)

        acc = np.zeros((1,))
        if self.rotation_acceleration is not None:
            acc = np.linalg.norm(self._make_2d(self.rotation_acceleration), axis=1, keepdims=True)
        if any(acc != 0.0):
            quadratic_contrib = R.from_rotvec(self._make_2d(self.rotation_acceleration) * 0.5 * delay * delay)
            # ~ next_rotation = quadratic_contrib * next_rotation
            next_rotation = next_rotation * quadratic_contrib
            # compute next_rotation_rate with quadratic contribution
            r_omega = quadratic_contrib.apply(next_rotation_rate, inverse=True)
            next_rotation_rate = self._make_2d(self.rotation_acceleration) * delay + r_omega
            # compute next_rotation acceleration with quadratic contribution
            next_rotation_acc = self._make_2d(self.rotation_acceleration) - np.cross(
                self._make_2d(self.rotation_acceleration) * delay, r_omega
            )

        return DynamicTransform(
            translation=next_translation,
            velocity=next_velocity,
            acceleration=next_acceleration,
            rotation=next_rotation.as_quat(),
            rotation_rate=next_rotation_rate,
            rotation_acceleration=next_rotation_acc,
        )

    def transform_position(self, position: np.ndarray) -> np.ndarray:
        """
        Apply this transform to a position
        """
        output = position
        if self.translation is not None:
            output = position + self.translation
        if self.rotation is not None:
            rot = R.from_quat(self.rotation)
            temp = rot.apply(output, inverse=True)
            output = temp
        return output

    def transform_direction(self, direction: np.ndarray) -> np.ndarray:
        """
        Apply this transform to a direction
        """
        output = direction
        if self.rotation is not None:
            rot = R.from_quat(self.rotation)
            temp = rot.apply(output, inverse=True)
            output = temp
        return output
