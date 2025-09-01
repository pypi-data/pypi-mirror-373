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
Intersection algorithm module generic tests
"""
import numpy as np
import pytest
from org.hipparchus.geometry.euclidean.threed import Line, Vector3D
from org.orekit.frames import StaticTransform, Transform

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.intersection.duvenhage.min_max_tree_tile import MinMaxTreeTile
from pyrugged.utils.math_utils import distance, to_array_v  # pylint: disable=no-name-in-module


def setup_module():
    """
    setup : initVM
    """
    init_orekit(use_internal_data=False)


def check_intersection(position, los, intersection, updater, ellipsoid):
    """
    Checks intersection.
    """

    # Check the point is on the line
    line = Line(
        Vector3D(position.tolist()), Vector3D(1.0, Vector3D(position.tolist()), 1e6, Vector3D(los.tolist())), 1.0e-12
    )
    assert line.distance(Vector3D(ellipsoid.transform_vec(intersection).tolist())) == pytest.approx(0.0, abs=3.0e-9)

    # check the point is on the Digital Elevation Model
    tile = MinMaxTreeTile()
    updater.update_tile(intersection[0], intersection[1], tile)
    assert tile.interpolate_elevation(intersection[0], intersection[1]) == pytest.approx(intersection[2], abs=2.0e-9)


def generic_test_mayon_volcano_on_sub_tile_corner(algo_to_test, context, ellipsoid):
    """
    Generic test for Mayon Volcano on sub tile corner
    """

    state = context["state"]
    updater = context["updater"]

    # Test point approximately 1.6km North-North-West and 800 meters below volcano summit
    # Note that this test point is EXACTLY at a cell corner, and even at corners of
    # middle level (12 and above) sub-tiles
    latitude = float(np.radians(13.27))
    longitude = float(np.radians(123.68))
    tile = MinMaxTreeTile()
    updater.update_tile(latitude, longitude, tile)
    altitude = tile.interpolate_elevation(latitude, longitude)
    ground_gp = np.array([latitude, longitude, altitude])
    ground_p = ellipsoid.transform_vec(ground_gp)

    algorithm = algo_to_test(updater, 8)

    # Preliminary check : the point has been chosen in the spacecraft (YZ) plane
    earth_to_spacecraft = Transform(
        state.getDate(),
        ellipsoid.body_frame.getTransformTo(state.getFrame(), state.getDate()),
        state.toTransform(),
    )

    point_in_spacecraft_frame = StaticTransform.cast_(earth_to_spacecraft).transformPosition(
        Vector3D(ground_p.tolist())
    )
    assert point_in_spacecraft_frame.getX() == pytest.approx(0.000, abs=1.0e-3)
    assert point_in_spacecraft_frame.getY() == pytest.approx(-87754.914, abs=1.0e-3)
    assert point_in_spacecraft_frame.getZ() == pytest.approx(790330.254, abs=1.0e-3)

    # Test direct location
    position = to_array_v(state.getPVCoordinates(ellipsoid.body_frame).getPosition().toArray())
    los = ground_p - position
    close_guess = algorithm.intersection(ellipsoid, position, los)
    result = algorithm.refine_intersection(ellipsoid, position, los, close_guess)
    check_intersection(position, los, result, updater, ellipsoid)
    assert distance(ground_p, ellipsoid.transform_vec(result)) == pytest.approx(0.0, abs=2.0e-9)


def generic_test_mayon_volcano_within_pixel(algo_to_test, context, ellipsoid):
    """
    Generic test for Mayon Volcano within pixel
    """

    state = context["state"]
    updater = context["updater"]

    latitude = float(np.radians(13.2696))
    longitude = float(np.radians(123.6803))
    tile = MinMaxTreeTile()
    updater.update_tile(latitude, longitude, tile)
    altitude = tile.interpolate_elevation(latitude, longitude)
    ground_gp = np.array([latitude, longitude, altitude])
    ground_p = ellipsoid.transform_vec(ground_gp)

    algorithm = algo_to_test(updater, 8)

    # Test direct location
    position = to_array_v(state.getPVCoordinates(ellipsoid.body_frame).getPosition().toArray())
    los = ground_p - position
    close_guess = algorithm.intersection(ellipsoid, position, los)
    result = algorithm.refine_intersection(ellipsoid, position, los, close_guess)

    check_intersection(position, los, result, updater, ellipsoid)
    assert distance(ground_p, ellipsoid.transform_vec(result)) == pytest.approx(0.0, abs=2.0e-9)


def generic_test_cliffs_of_moher(algo_to_test, context, ellipsoid):
    """
    Generic test for Cliffs of Moher
    """

    state = context["state"]
    updater = context["updater"]

    # Test point on top the cliffs, roughly 15m East of edge (inland)
    latitude = float(np.radians(52.98045))
    longitude = float(np.radians(-9.421826199814143))
    tile = MinMaxTreeTile()
    updater.update_tile(latitude, longitude, tile)
    altitude = tile.interpolate_elevation(latitude, longitude)
    ground_gp = np.array([latitude, longitude, altitude])
    ground_p = ellipsoid.transform_vec(ground_gp)

    algorithm = algo_to_test(updater, 8)

    assert algorithm.get_elevation(np.array([latitude]), np.array([longitude - 2.0e-5]))[0] == pytest.approx(
        0.0, abs=1.0e-6
    )
    assert algorithm.get_elevation(np.array([latitude]), np.array([longitude + 2.0e-5]))[0] == pytest.approx(
        120.0, abs=1.0e-6
    )

    # Preliminary check : the point has been chosen in the spacecraft (YZ) plane
    earth_to_spacecraft = Transform(
        state.getDate(),
        ellipsoid.body_frame.getTransformTo(state.getFrame(), state.getDate()),
        state.toTransform(),
    )

    point_in_spacecraft_frame = StaticTransform.cast_(earth_to_spacecraft).transformPosition(
        Vector3D(ground_p.tolist())
    )
    assert point_in_spacecraft_frame.getX() == pytest.approx(0.0, abs=1.0e-3)
    assert point_in_spacecraft_frame.getY() == pytest.approx(66702.419, abs=1.0e-3)
    assert point_in_spacecraft_frame.getZ() == pytest.approx(796873.178, abs=1.0e-3)

    position = to_array_v(state.getPVCoordinates(ellipsoid.body_frame).getPosition().toArray())
    los = ground_p - position
    close_guess = algorithm.intersection(ellipsoid, position, los)
    result = algorithm.refine_intersection(ellipsoid, position, los, close_guess)

    check_intersection(position, los, result, updater, ellipsoid)
    assert distance(ground_p, ellipsoid.transform_vec(result)) == pytest.approx(0.0, abs=2.0e-9)
