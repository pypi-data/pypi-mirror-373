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
pyrugged MinMaxTreeTile class tests
"""
import math

import numpy as np

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.intersection.duvenhage.min_max_tree_tile import MinMaxTreeTile


def setup_module():
    """
    setup : initVM and reset DUMP_VAR
    """
    init_orekit(use_internal_data=False)

    # Ensuring DumpManager is deactivated
    dump_manager.DUMP_VAR = None


def teardown_module():
    """
    teardown : reset DUMP_VAR
    """
    dump_manager.DUMP_VAR = None


def create_test_tile(nb_rows: int, nb_cols: int):
    """
    create MinMaxTreeTile tiles for test
    """
    tile = MinMaxTreeTile()
    tile.set_geometry(1.0, 2.0, 0.1, 0.2, nb_rows, nb_cols)

    for i in range(nb_rows):
        for j in range(nb_cols):
            tile.set_elevation(i, j, i + 0.01 * j)

    tile.tile_update_completed()
    return tile


def create_ref_neighbors(row: int, column: int, nb_rows: int, nb_columns: int, stages: int):
    """
    create neighbors for tests' references
    """
    # poor man identification of neighbors cells merged together with specified cell
    # this identification is intentionally independent of the MinMaxTreeTile class,
    # for testing purposes
    r_min = row
    r_n = 1
    r_mask = -1
    c_min = column
    c_n = 1
    c_mask = -1

    merge_columns = True
    for _ in range(stages):
        if merge_columns:
            c_mask = c_mask << 1
            c_min = c_min & c_mask
            c_n = c_n * 2
        else:
            r_mask = r_mask << 1
            r_min = r_min & r_mask
            r_n = r_n * 2
        merge_columns = not merge_columns

    return r_min, min(r_min + r_n, nb_rows), c_min, min(c_min + c_n, nb_columns)


def create_ref_multiples(k_1: int, k_2: int, sub_tiles_size: int):
    """
    create crossings for tests' references
    """
    # poor man identification of rows/columns crossings
    # this identification is intentionally independent of the MinMaxTreeTile class,
    # for testing purposes

    # intentionally dumb way of counting multiples of n
    k_s = min(k_1, k_2)
    k_e = max(k_1, k_2) + 1
    count = 0

    for k in range(k_s, k_e):
        if k % sub_tiles_size == 0:
            count += 1

    multiples = [0] * count
    index = 0
    for k in range(k_s, k_e):
        if k % sub_tiles_size == 0:
            multiples[index] = k
            index += 1

    if k_1 > k_2:
        # revert the array
        multiples.reverse()

    return multiples


def test_size_tall():
    """
    Test tile creation
    """
    tile = create_test_tile(107, 19)

    assert tile.levels == 9

    assert np.allclose(tile.start, np.array([0, 7, 21, 49, 91, 172, 307, 577, 1117]))

    assert tile.is_column_merging(9) is True
    assert tile.is_column_merging(8) is False
    assert tile.is_column_merging(7) is True
    assert tile.is_column_merging(6) is False
    assert tile.is_column_merging(5) is True
    assert tile.is_column_merging(4) is False
    assert tile.is_column_merging(3) is True
    assert tile.is_column_merging(2) is False
    assert tile.is_column_merging(1) is True

    assert len(tile.min_tree) == 2187
    assert len(tile.max_tree) == 2187


def test_size_fat():
    """
    Test tile creation
    """
    tile = create_test_tile(4, 7)

    assert tile.levels == 4

    assert np.allclose(tile.start, np.array([0, 2, 6, 14]))

    assert tile.is_column_merging(4) is True
    assert tile.is_column_merging(3) is False
    assert tile.is_column_merging(2) is True
    assert tile.is_column_merging(1) is False

    assert len(tile.min_tree) == 30
    assert len(tile.max_tree) == 30


def test_single_pixel():
    """
    Test tile creation
    """
    tile = create_test_tile(1, 1)

    assert tile.levels == 0


def test_min_max():
    """
    Test get_min_elevation and get_max_elevation
    """

    def test_min_max_with_ref(i, j, nb_rows_tile, nb_columns_tile, level):
        # reference min and max
        neighbors = create_ref_neighbors(i, j, nb_rows_tile, nb_columns_tile, tile.levels - level)
        fm_min = math.inf
        fm_max = -math.inf

        for neighbors_i in range(neighbors[0], min(neighbors[1] + 1, nb_rows_tile)):
            for neighbors_j in range(neighbors[2], min(neighbors[3] + 1, nb_columns_tile)):
                cell_value = tile.get_elevation_at_indices(neighbors_i, neighbors_j)
                fm_min = min(fm_min, cell_value)
                fm_max = max(fm_max, cell_value)

        assert fm_min == tile.get_min_elevation(i, j, level)
        assert fm_max == tile.get_max_elevation(i, j, level)

    for nb_rows in range(1, 15):
        for nb_columns in range(1, 15):
            tile = create_test_tile(nb_rows, nb_columns)

            for level in range(tile.levels):
                for row in range(nb_rows):
                    for column in range(nb_columns):
                        test_min_max_with_ref(row, column, nb_rows, nb_columns, level)


def test_locate_min_max():
    """
    Test get_min_elevation and get_max_elevation
    """
    for nb_rows in range(1, 15):
        for nb_columns in range(1, 15):
            tile = MinMaxTreeTile()
            tile.set_geometry(1.0, 2.0, 0.1, 0.2, nb_rows, nb_columns)
            for i in range(nb_rows):
                for j in range(nb_columns):
                    elev = np.random.uniform(0, 1000)
                    tile.set_elevation(i, j, elev)
            tile.tile_update_completed()

            for i in range(tile.latitude_rows):
                for j in range(tile.longitude_columns):
                    for level in range(tile.levels):
                        located_min = tile.locate_min(i, j, level)
                        assert tile.get_min_elevation(i, j, level) == tile.get_elevation_at_indices(
                            located_min[0], located_min[1]
                        )

                        located_max = tile.locate_max(i, j, level)
                        assert tile.get_max_elevation(i, j, level) == tile.get_elevation_at_indices(
                            located_max[0], located_max[1]
                        )


def test_rugged_issue_189():
    """
    non reg to rugged issue 189
    """
    tile = MinMaxTreeTile()
    tile.set_geometry(1.0, 2.0, 0.1, 0.2, 2, 2)
    tile.set_elevation(0, 0, 1.0)
    tile.set_elevation(0, 1, 2.0)
    tile.set_elevation(1, 0, 3.0)
    tile.set_elevation(1, 1, 4.0)
    tile.tile_update_completed()

    assert 1.0 == tile.get_min_elevation(0, 0, 0)
    assert 3.0 == tile.get_min_elevation(1, 0, 0)
    assert 4.0 == tile.get_max_elevation(0, 0, 0)
    assert 4.0 == tile.get_max_elevation(1, 0, 0)


def test_merge_large():
    """
    Test get_merge_level method
    """
    tile = create_test_tile(1201, 1201)
    assert 21 == tile.levels
    assert 7 == tile.get_merge_level(703, 97, 765, 59)

    row_1 = np.array([703, 703, 703, 703])
    col_1 = np.array([97, 97, 97, 97])
    row_2 = np.array([765, 735, 655, 200])
    col_2 = np.array([59, 89, 110, 20])

    levels = tile.get_merge_level_vec(row_1, col_1, row_2, col_2)
    ref_levels = np.array([7, 7, 9, 1])

    assert np.all(levels == ref_levels)


def test_merge_level():
    """
    Test get_merge_level method
    """

    def test_merge_level_with_ref(row_1, col_1, row_2, col_2, nb_rows_tile, nb_columns_tile):
        level = tile.get_merge_level(row_1, col_1, row_2, col_2)

        if level > 0:
            neighbors1 = create_ref_neighbors(row_1, col_1, nb_rows_tile, nb_columns_tile, tile.levels - level)
            neighbors2 = create_ref_neighbors(row_2, col_2, nb_rows_tile, nb_columns_tile, tile.levels - level)

            for _ in range(len(neighbors1)):
                assert neighbors1 == neighbors2

        if level + 1 < tile.levels:
            neighbors1 = create_ref_neighbors(row_1, col_1, nb_rows_tile, nb_columns_tile, tile.levels - (level + 1))
            neighbors2 = create_ref_neighbors(row_2, col_2, nb_rows_tile, nb_columns_tile, tile.levels - (level + 1))

            for _ in range(len(neighbors1)):
                if neighbors1 == neighbors2:
                    tile.get_merge_level(row_1, col_1, row_2, col_2)

                assert neighbors1 != neighbors2

    for nb_rows in range(1, 15):
        for nb_columns in range(1, 15):

            tile = create_test_tile(nb_rows, nb_columns)

            for i_1 in range(nb_rows):
                for j_1 in range(nb_columns):
                    for i_2 in range(nb_rows):
                        for j_2 in range(nb_columns):
                            test_merge_level_with_ref(i_1, j_1, i_2, j_2, nb_rows, nb_columns)


def test_sub_tiles_limits():
    """
    Test get_boundary_rows and get_boundary_columns methods
    """
    for nb_rows in range(1, 15):
        for nb_columns in range(1, 15):
            tile = create_test_tile(nb_rows, nb_columns)

            for level in range(tile.levels):
                neighbors = create_ref_neighbors(0, 0, nb_rows, nb_columns, tile.levels - level)
                sub_tile_rows = neighbors[1] - neighbors[0]
                sub_tile_cols = neighbors[3] - neighbors[2]

                for i_1 in range(nb_rows):
                    for i_2 in range(nb_rows):
                        crossings = tile.get_crossed_boundary_rows(i_1, i_2, level)
                        ref = create_ref_multiples(i_1, i_2, sub_tile_rows)
                        assert ref == crossings

                for j_1 in range(nb_columns):
                    for j_2 in range(nb_columns):
                        crossings = tile.get_crossed_boundary_columns(j_1, j_2, level)
                        ref = create_ref_multiples(j_1, j_2, sub_tile_cols)
                        assert ref == crossings


# def test_for_coverage():
#     """
#     Test dump
#     """
#     ref_dump_path = os.path.join(os.path.dirname(__file__), "../../data/ref/intersection/dump_min_max_tree_tile.json")

#     with tempfile.TemporaryDirectory() as tmp_dir:
#         dump_path = os.path.join(tmp_dir, "dump.json")
#         tile = create_test_tile(1201, 1201, dump_file=dump_path)
#         tile.get_min_elevation(100, 100, 0)
#         tile.get_max_elevation(100, 100, 0)

#         # regenerate reference
#         # import shutil
#         # shutil.copyfile(dump_path, ref_dump_path)

#         with open(ref_dump_path, "r", encoding="utf-8") as ref_file:
#             data_ground_truth = json.load(ref_file)
#             with open(dump_path, "r", encoding="utf-8") as file:
#                 data = json.load(file)

#                 assert data == data_ground_truth
