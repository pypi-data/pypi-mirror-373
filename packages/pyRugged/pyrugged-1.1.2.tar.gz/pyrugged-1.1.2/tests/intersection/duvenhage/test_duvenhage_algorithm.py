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
pyrugged DuvenhageAlgorithm class tests
"""
import json
import os
import pickle
import re
import tempfile

import numpy as np
import pytest

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.duvenhage.duvenhage_algorithm import DuvenhageAlgorithm
from pyrugged.intersection.duvenhage.min_max_tree_tile import MinMaxTreeTile
from pyrugged.raster.simple_tile import SimpleTile

from ...raster.cached_elevation_updater import CachedElevationUpdater
from ...raster.checked_pattern_elevation_updater import CheckedPatternElevationUpdater
from ..algorithm_generic_tests import check_intersection

# pylint: disable=no-member
init_orekit(use_internal_data=False)


def test_algorithm_id(mayon_volcano_context):
    """
    Test algorithm id
    """
    updater = mayon_volcano_context["updater"]

    algorithm = DuvenhageAlgorithm(updater, 8, False)
    assert algorithm.algorithm_id == AlgorithmId.DUVENHAGE

    algorithm = DuvenhageAlgorithm(updater, 8, True)
    assert algorithm.algorithm_id == AlgorithmId.DUVENHAGE_FLAT_BODY


def test_numerical_issue_at_tile_exit(mayon_volcano_context, earth):
    """
    test numerical issue at tile exit
    """
    updater = mayon_volcano_context["updater"]
    duvenhage_algo = DuvenhageAlgorithm(updater, 8, False)

    position = np.array([[-3787079.6453602533, 5856784.405679551, 1655869.0582939098]])
    los = np.array([[0.5127552821932051, -0.8254313129088879, -0.2361041470463311]])

    intersection = duvenhage_algo.refine_intersection_vec(
        earth, position, los, duvenhage_algo.intersection_vec(earth, position, los)
    )
    check_intersection(position[0], los[0], intersection[0], updater, earth)


def test_crossing_before_line_segment_start(mayon_volcano_context, earth):
    """
    test crossing before line segment start
    """
    updater = mayon_volcano_context["updater"]
    duvenhage_algo = DuvenhageAlgorithm(updater, 8, False)

    position = np.array([[-3787079.6453602533, 5856784.405679551, 1655869.0582939098]])
    los = np.array([[0.42804005978915904, -0.8670291034054828, -0.2550338037664377]])

    intersection = duvenhage_algo.refine_intersection_vec(
        earth, position, los, duvenhage_algo.intersection_vec(earth, position, los)
    )

    check_intersection(position[0], los[0], intersection[0], updater, earth)


def test_wrong_position_misses_ground(mayon_volcano_context, earth):
    """
    Test line of sight does not reach ground exception
    """
    updater = mayon_volcano_context["updater"]
    duvenhage_algo = DuvenhageAlgorithm(updater, 8, False)
    position = np.array([[7.551889113912788e9, -3.173692685491814e10, 1.5727517321541348e9]])
    los = np.array([[0.010401349221417867, -0.17836068905951286, 0.9839101973923178]])
    with pytest.raises(PyRuggedError) as pre:
        duvenhage_algo.intersection_vec(earth, position, los)
    assert PyRuggedMessages.LINE_OF_SIGHT_DOES_NOT_REACH_GROUND.value == str(pre.value)


def test_inconsistent_tile_updater(earth):
    """
    Test tile updater exception
    """

    # pylint: disable="too-few-public-methods"
    class TileUpdater:
        """
        Fake tile updater
        """

        def update_tile(self, latitude, longitude, tile: SimpleTile):
            """
            update tile method
            """
            dim = 1201
            size = float(np.radians(1.0))
            step = size / (dim - 1)

            # this geometry is incorrect:
            # the specified latitude/longitude belong to rows/columns [1, dim-1]
            # and not [0, dim-2].
            tile.set_geometry(
                size * float(np.floor(latitude / size)) - 0.5 * step,
                size * float(np.floor(longitude / size)) - 0.5 * step,
                step,
                step,
                dim,
                dim,
            )

            for i in range(dim):
                for j in range(dim):
                    if (i + j) % 2 == 0:
                        tile.set_elevation(i, j, -7.0)
                    else:
                        tile.set_elevation(i, j, 224)

    updater = TileUpdater()
    duvenhage_algo = DuvenhageAlgorithm(updater, 8, False)

    with pytest.raises(PyRuggedError) as pre:
        duvenhage_algo.intersection_vec(
            earth,
            np.array([[-3010311.9672771087, 5307094.8081077365, 1852867.7919871407]]),
            np.array([[0.3953329359154183, -0.8654901360032332, -0.30763402650162286]]),
        )

    error_latlon = re.findall("-?\\d+\\.\\d+", str(pre.value))
    original_error_msg = PyRuggedMessages.TILE_WITHOUT_REQUIRED_NEIGHBORS_SELECTED.value
    assert original_error_msg.format(error_latlon[0], error_latlon[1]) == str(pre.value)


def test_pure_east_west_los(earth):
    """
    Test pure east west los and dump of algorithm id
    """
    updater = CheckedPatternElevationUpdater(float(np.radians(1.0)), 1201, 41.0, 1563.0)
    ref_dump_path = os.path.join(os.path.dirname(__file__), "../../data/ref/intersection/dump_duvenhage.json")

    position = np.array([-3041185.154503948, 6486750.132281409, -32335.022880173332])
    los = np.array([0.5660218606298548, -0.8233939240951769, 0.040517885584811814])

    with tempfile.TemporaryDirectory() as tmp_dir:
        dump_path = os.path.join(tmp_dir, "dump.json")
        duvenhage_algo = DuvenhageAlgorithm(updater, 8, False, dump_file=dump_path)

        ground_point_single = duvenhage_algo.intersection(earth, position, los)

        ground_point = duvenhage_algo.intersection_vec(earth, position[np.newaxis, ...], los[np.newaxis, ...])

        # regenerate reference
        # import shutil
        # shutil.copyfile(dump_path, ref_dump_path)

        with open(ref_dump_path, "r", encoding="utf-8") as ref_file:
            data_ground_truth = json.load(ref_file)
            with open(dump_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                assert data == data_ground_truth

    assert -2.7188743318528344e-6 == pytest.approx(ground_point_single[0], abs=1.0e-10)
    assert 1.9888210365497252 == pytest.approx(ground_point_single[1], abs=1.0e-10)
    assert 1164.3556908842102 == pytest.approx(ground_point_single[2], abs=1.0e-2)

    # check intersection_vec is giving the same results
    assert -2.7188743318528344e-6 == pytest.approx(ground_point[0, 0], abs=1.0e-10)
    assert 1.9888210365497252 == pytest.approx(ground_point[0, 1], abs=1.0e-10)
    assert 1164.3556908842102 == pytest.approx(ground_point[0, 2], abs=1.0e-2)


def test_parallel_los(earth):
    """
    Test parallel los
    """
    size = 0.125
    n_val = 129
    elevation_1 = 0.0
    elevation_2 = 100.0

    updater = CheckedPatternElevationUpdater(size, n_val, elevation_1, elevation_2)
    north_tile = MinMaxTreeTile()
    updater.update_tile((3 * size) / 2, (3 * size) / 2, north_tile)
    south_tile = MinMaxTreeTile()
    updater.update_tile((-3 * size) / 2, (3 * size) / 2, south_tile)
    duvenhage_algo = DuvenhageAlgorithm(updater, 8, False)

    # line of sight in the South West corner
    exit_point = duvenhage_algo.find_exit_vec(
        [north_tile],
        [np.array([0])],
        earth,
        np.array([[6278799.86896170100, 788574.17965500170, 796074.70414069280]]),
        np.array([[0.09416282233912959, 0.01183204230132312, -0.99548649697728680]]),
    )
    assert north_tile.minimum_longitude - 0.0625 * north_tile.longitude_step == pytest.approx(
        exit_point[0, 1], abs=1.0e-6
    )

    # line of sight in the West column
    exit_point = duvenhage_algo.find_exit_vec(
        [north_tile],
        [np.array([0])],
        earth,
        np.array([[6278799.868961701, 788574.17965500171, 796074.7041406928]]),
        np.array([[0.09231669916268806, 0.011600067441452849, -0.9956621241621375]]),
    )
    assert north_tile.minimum_longitude - 0.0625 * north_tile.longitude_step == pytest.approx(
        exit_point[0, 1], abs=1.0e-6
    )

    # line of sight in the North-West corner
    exit_point = duvenhage_algo.find_exit_vec(
        [north_tile],
        [np.array([0])],
        earth,
        np.array([[6133039.79342824500, 770267.71434489540, 1568158.38266382620]]),
        np.array([[-0.52028845147300570, -0.06537691642830394, -0.85148446025875800]]),
    )
    assert north_tile.minimum_longitude - 0.0625 * north_tile.longitude_step == pytest.approx(
        exit_point[0, 1], abs=1.0e-6
    )

    # line of sight in the North-East corner
    exit_point = duvenhage_algo.find_exit_vec(
        [north_tile],
        [np.array([0])],
        earth,
        np.array([[5988968.17708294100, 1529624.01701343130, 1568158.38266382620]]),
        np.array([[-0.93877408645552440, -0.23970837882807683, -0.24747344851359457]]),
    )
    assert north_tile.maximum_longitude + 0.0625 * north_tile.longitude_step == pytest.approx(
        exit_point[0, 1], abs=1.0e-6
    )

    # line of sight in the East column
    exit_point = duvenhage_algo.find_exit_vec(
        [north_tile],
        [np.array([0])],
        earth,
        np.array([[6106093.15406747100, 1559538.54861392200, 979886.66862965740]]),
        np.array([[-0.18115090486319424, -0.04625542007869719, 0.98236693031707310]]),
    )
    assert north_tile.maximum_longitude + 0.0625 * north_tile.longitude_step == pytest.approx(
        exit_point[0, 1], abs=1.0e-6
    )

    # line of sight in the South-East corner
    exit_point = duvenhage_algo.find_exit_vec(
        [north_tile],
        [np.array([0])],
        earth,
        np.array([[6131304.19368509600, 1565977.62301751650, 796074.70414069280]]),
        np.array([[0.09195297594530785, 0.02347944953986664, -0.99548649697728530]]),
    )
    assert north_tile.maximum_longitude + 0.0625 * north_tile.longitude_step == pytest.approx(
        exit_point[0, 1], abs=1.0e-6
    )

    # line of sight in the South row
    exit_point = duvenhage_algo.find_exit_vec(
        [north_tile],
        [np.array([0])],
        earth,
        np.array([[6251729.731998736, 984354.4963428857, 789526.5774750853]]),
        np.array([[-0.15561499277355603, 0.9878177838164719, 0.0]]),
    )
    assert north_tile.minimum_latitude - 0.0625 * north_tile.latitude_step == pytest.approx(
        exit_point[0, 0], abs=1.0e-6
    )

    # line of sight in the North row
    exit_point = duvenhage_algo.find_exit_vec(
        [south_tile],
        [np.array([0])],
        earth,
        np.array([[6251729.731998736, 984354.4963428857, -789526.5774750853]]),
        np.array([[-0.15561499277355603, 0.9878177838164719, 0.0]]),
    )
    assert south_tile.maximum_latitude + 0.0625 * south_tile.latitude_step == pytest.approx(
        exit_point[0, 0], abs=1.0e-6
    )


@pytest.fixture(name="cached_updater", scope="module")
def setup_cached_tile_updater():
    """
    Setup a tile updater based on cached tiles
    """

    ref_data_path = os.path.join(os.path.dirname(__file__), "../../data/ref/intersection/crossing_tile")

    tiles = []
    for index in range(10):
        with open(os.path.join(ref_data_path, f"tile_{index}.bin"), "rb") as fhd:
            data = fhd.read()
            tiles.append(pickle.loads(data))

    return CachedElevationUpdater(tiles)


def test_intersection_vec_changing_tile(earth, cached_updater):
    """
    Test case from a bug : intersection_vec() was not able to explore adjacent tile when los exits
    current tile at the side.
    """

    ref_data_path = os.path.join(os.path.dirname(__file__), "../../data/ref/intersection/crossing_tile")

    duvenhage_algo = DuvenhageAlgorithm(cached_updater, 8, False)

    # This LOS starts on one tile and goes to the neighbor.
    p_body = np.load(os.path.join(ref_data_path, "msi_bug_positions.npy"))
    l_body = np.load(os.path.join(ref_data_path, "msi_bug_los.npy"))
    gnd = duvenhage_algo.intersection_vec(earth, p_body, l_body)
    assert np.all(~np.isnan(gnd))

    # This set of points requires 9~10 tiles but the cache is limited to 8 tiles
    p_body = np.load(os.path.join(ref_data_path, "b05d01_p_body.npy"))
    l_body = np.load(os.path.join(ref_data_path, "b05d01_l_body.npy"))
    gnd = duvenhage_algo.intersection_vec(earth, p_body, l_body)
    assert np.all(~np.isnan(gnd))
