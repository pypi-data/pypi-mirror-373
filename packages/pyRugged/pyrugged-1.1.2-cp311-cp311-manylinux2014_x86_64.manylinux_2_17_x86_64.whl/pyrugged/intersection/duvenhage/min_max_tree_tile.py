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
Implementation of a pyrugged.raster.Tile with a min/max kd tree.

A n level min/max kd-tree contains sub-tiles merging individual cells
together from coarse-grained (at level 0) to fine-grained (at level n-1).
Level n-1, which is the deepest one, is computed from the raw cells by
merging adjacent cells pairs columns (i.e. cells at indices (i, 2j)
and (i, 2j+1) are merged together by computing and storing the minimum
and maximum in a sub-tile. Level n-1 therefore has the same number of rows
but half the number of columns of the raw tile, and its sub-tiles are
1 cell high and 2 cells wide. Level n-2 is computed from level n-1 by
merging sub-tiles rows. Level n-2 therefore has half the number of rows
and half the number of columns of the raw tile, and its sub-tiles are
2 cells high and 2 cells wide. Level n-3 is again computed by merging
columns, level n-4 merging rows and so on. As depth decreases, the number
of sub-tiles decreases and their size increase. Level 0 is reached when
there is only either one row or one column of large sub-tiles.

During the merging process, if at some stage there is an odd number of
rows or columns, then the last sub-tile at next level will not be computed
by merging two rows/columns from the current level, but instead computed by
simply copying the last single row/column. The process is therefore well
defined for any raw tile initial dimensions. A direct consequence is that
the dimension of the sub-tiles in the last row or column may be smaller than
the dimension of regular sub-tiles.

If we consider for example a tall 107 x 19 raw tile, the min/max kd-tree will
have 9 levels:

* level 8: Number of sub-tiles: 107 x 10, Regular sub-tiles dimension: 1 x 2
* level 7: Number of sub-tiles: 54 x 10, Regular sub-tiles dimension: 2 x 2
* level 6: Number of sub-tiles: 54 x 5, Regular sub-tiles dimension: 2 x 4
* level 5: Number of sub-tiles: 27 x 5, Regular sub-tiles dimension: 4 x 4
* level 4: Number of sub-tiles: 27 x 3, Regular sub-tiles dimension: 4 x 8
* level 3: Number of sub-tiles: 14 x 3, Regular sub-tiles dimension: 8 x 8
* level 2: Number of sub-tiles: 14 x 2, Regular sub-tiles dimension: 8 x 16
* level 1: Number of sub-tiles: 7 x 2, Regular sub-tiles dimension: 16 x 16
* level 0: Number of sub-tiles: 7 x 1, Regular sub-tiles dimension: 16 x 32
"""

import math
import sys
from enum import Enum
from typing import List

import numpy as np

from pyrugged.errors import dump_manager
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.utils.max_selector import MaxSelector
from pyrugged.utils.min_selector import MinSelector
from pyrugged.utils.selector import Selector


class MinMax(Enum):
    """min/max flags"""

    MIN = 0
    MAX = 1


class MinMaxTreeTile(SimpleTile):
    """
    pyrugged MinMaxTreeTile Class
    """

    def __init__(self):
        """
        MinMaxTreeTile constructor
        """
        super().__init__()
        self._raw = None
        self._min_tree = None
        self._max_tree = None
        self._start = None

    @property
    def raw(self) -> np.ndarray:
        """
        Get raw elevations

        Returns
        -------
            raw elevations as a list of floats
        """
        return self._raw

    @property
    def min_tree(self) -> np.ndarray:
        """
        Get min kd-tree

        Returns
        -------
            min kd-tree as a list of floats
        """
        return self._min_tree

    @property
    def max_tree(self) -> np.ndarray:
        """
        Get max kd-tree

        Returns
        -------
            max kd-tree as a list of floats
        """
        return self._max_tree

    @property
    def start(self) -> np.ndarray:
        """
        Get start indices of tree levels

        Returns
        -------
            max start indices as a list of int
        """
        return self._start

    @property
    def levels(self) -> int:
        """
        Get the number of kd-tree levels (not counting raw elevations).

        Returns
        -------
            number of kd-tree levels
        """
        return len(self.start)

    def set_levels(self, stage: int, stage_rows: int, stage_columns: int) -> int:
        """
        Recursive setting of tree levels.

        The following algorithms works for any array shape, even with
        rows or columns which are not powers of 2 or with one
        dimension much larger than the other. As an example, starting
        from a 107 ⨉ 19 array, we get the following 9 levels, for a
        total of 2187 elements in each tree:

         * level 0: Dimension: 7x1, start index: 0, end index: 6
         * level 1: Dimension: 7x2, start index: 7, end index: 20
         * level 2: Dimension: 14x2, start index: 21, end index: 48
         * level 3: Dimension: 14x3, start index: 49, end index: 90
         * level 4: Dimension: 27x3, start index: 91, end index: 171
         * level 5: Dimension: 27x5, start index: 172, end index: 306
         * level 6: Dimension: 54x5, start index: 307, end index: 576
         * level 7: Dimension: 54x10, start index: 577, end index: 1116
         * level 8: Dimension: 107x10, start index: 1117, end index: 2186

        Parameters
        ----------
            stage: number of merging stages
            stage_rows: number of rows at current stage
            stage_columns: number of columns at current stage

        Returns
        -------
            cumulative size from root to current level
        """
        if stage_rows == 1 or stage_columns == 1:
            # we have found root, stop recursion
            self._start = np.zeros(stage, dtype=int)

            if stage > 0:
                self._start[0] = 0
            return stage_columns * stage_rows

        if (stage % 2) == 0:
            # columns merging
            size = self.set_levels(stage + 1, stage_rows, (stage_columns + 1) // 2)
        else:
            # rows merging
            size = self.set_levels(stage + 1, (stage_rows + 1) // 2, stage_columns)

        if stage > 0:
            # store current level characteristics
            # we don't count the elements at stage 0 as they are not stored in the
            # min/max trees (they correspond to the raw elevation, without merging)
            self._start[len(self.start) - stage] = size
            size += stage_rows * stage_columns

        return size

    @classmethod
    def preprocess(
        cls, preprocessed: np.ndarray, elevations: np.ndarray, nb_rows: int, nb_cols: int, min_max_flag: MinMax
    ):
        """
        Preprocess recursive application of a function.

        At start, the min/max should be computed for each cell using the four corners values.

        Parameters
        ----------
            preprocessed: preprocessed array to fill up
            elevations: raw elevations te preprocess
            nb_rows: number of rows
            nb_cols: number of columns
            min_max_flag: calculate min or max ?
        """

        # If no cols or rows, do nothing
        if (nb_rows == 0) or (nb_cols == 0):
            preprocessed[:] = elevations

        # Calculate min
        if min_max_flag == MinMax.MIN:
            # We will pre-process ou data to replace nan values with big_float so min(v,nan) becomes min(v,big_float)
            nan_replacement = sys.float_info.max

            # Then we'll use the np.min function
            np_min_max_func = np.min

        # Do the opposite with max
        else:
            nan_replacement = sys.float_info.min
            np_min_max_func = np.max

        # Pre-processing
        nan_removed = np.nan_to_num(elevations, copy=True, nan=nan_replacement)

        # 1D -> 2D array
        in_array = nan_removed.reshape((nb_rows, nb_cols))

        # Use numpy to calculate min/max values for each 4 neighbor pixels.
        # Input arrays = elevation array minus 1 row and 1 col, shifted by 0/1 row/col.
        # Input shape is (4, nb_rows-1, nb_cols-1).
        # min/max is calculated for each 4 input pixels.
        # Output shape is (nb_rows-1, nb_cols-1).
        out_array = np_min_max_func(
            [in_array[:-1, :-1], in_array[1:, :-1], in_array[:-1, 1:], in_array[1:, 1:]], axis=0
        )

        # Calculate min/max values for each 2 neighbor row pixels of the last column.
        # Input shape is (2, nbrows-1, 1), output shape is (nbrows-1, 1)
        last_col = in_array[:, -1]
        last_col_min_max = np_min_max_func([last_col[:-1], last_col[1:]], axis=0)

        # Append last column min/max values to output
        out_array = np.hstack((out_array, last_col_min_max[:, np.newaxis]))

        # Idem for last row
        last_row = in_array[-1, :]
        last_row_min_max = np_min_max_func([last_row[:-1], last_row[1:]], axis=0)

        # Append the last row/col pixel to the last row min/max values
        # so this last row shape becomes (1, nbcols) and append it to output.
        last_row_min_max = np.append(last_row_min_max, in_array[-1, -1])
        out_array = np.vstack((out_array, last_row_min_max[np.newaxis, :]))

        # 2D -> 1D array
        out_array = out_array.reshape(-1)

        # Post-processing = put back the nan values, but only for float or double arrays
        # (nan does not exist in int arrays)
        if out_array.dtype.kind == "f":
            out_array[out_array == nan_replacement] = np.nan

        # Fill the array passed by the caller
        preprocessed[:] = out_array

    def is_column_merging(self, level: int) -> bool:
        """
        Check if the merging operation between level and level-1 is a column merging.

        Parameters
        ----------
            level: level to check

        Returns
        -------
            true if the merging operation between level and level-1 is a column merging, false if is a row merging
        """
        return (level % 2) == (len(self.start) % 2)

    def is_column_merging_vec(self, levels: np.ndarray) -> np.ndarray:
        """
        Check if the merging operation between level and level-1 is a column merging.

        Parameters
        ----------
            levels: levels to check

        Returns
        -------
            true if the merging operation between level and level-1 is a column merging, false if is a row merging
        """

        return (levels % 2) == (len(self.start) % 2)

    # pylint: disable=too-many-branches
    def apply_recursively(
        self,
        tree: np.ndarray,
        level: int,
        level_rows: int,
        level_columns: int,
        min_max_flag: MinMax,
        base: np.ndarray,
        first: int,
    ):
        """
        Recursive application of a function.

        Parameters
        ----------
            tree: tree to fill-up with the recursive applications
            level: current level
            level_rows: number of rows at current level
            level_columns: number of columns at current level
            min_max_flag: calculate min or max ?
            base: base array from which function arguments are drawn
            first: index of the first element to consider in base array
        """

        # If no cols or rows, do nothing
        if (level_rows == 0) or (level_columns == 0):
            return

        # Calculate min
        if min_max_flag == MinMax.MIN:
            # We will pre-process ou data to replace nan values with big_float so min(v,nan) becomes min(v,big_float)
            nan_replacement = sys.float_info.max

            # Then we'll use the np.min function
            np_min_max_func = np.min

        # Do the opposite with max
        else:
            nan_replacement = sys.float_info.min
            np_min_max_func = np.max

        start_level = self.start[level]
        pixels_base = level_rows * level_columns

        # List to numpy
        np_base = base[first : first + pixels_base].reshape((level_rows, level_columns))

        # Pre-processing
        np_base = np.nan_to_num(np_base, copy=False, nan=nan_replacement)

        # Post-processing
        def post_processing():
            # Post-processing = put back the nan values, but only for float or double arrays
            # (nan does not exist in int arrays)
            if out_array.dtype.kind == "f":
                out_array[out_array == nan_replacement] = np.nan

            # Copy results into the parent tree
            tree[start_level : start_level + pixels_tree] = out_array.reshape(-1)

        # Merge column pairs
        if self.is_column_merging(level + 1):
            next_columns = (level_columns + 1) // 2
            is_odd = (level_columns % 2) != 0
            if is_odd:
                j_end = next_columns - 1
            else:
                j_end = next_columns

            pixels_tree = level_rows * next_columns

            # For each row, use numpy to calculate min/max values for each group of 2 neighbor columns.
            # 1st input array = for each row, keep one of two columns starting from 0.
            # Don't keep the last column if odd.
            # 2nd input array = idem but start from 1.
            # Input shape is (2, nb_rows, level_columns // 2).
            # min/max is calculated for each 2 input pixels.
            # Output shape is (nb_rows, level_columns // 2).
            out_array = np_min_max_func(
                [
                    np_base[:, : j_end * 2 : 2],
                    np_base[:, 1 : j_end * 2 : 2],
                ],
                axis=0,
            )

            # If column count is odd, simply copy the last input column
            if is_odd:
                out_array = np.hstack((out_array, np_base[:, -1, np.newaxis]))

            # Post-processing = put back the nan values and copy results into the parent tree
            post_processing()

            # Recursive call
            if level > 0:
                self.apply_recursively(tree, level - 1, level_rows, next_columns, min_max_flag, tree, self.start[level])

        # Merge row pairs
        else:
            next_rows = (level_rows + 1) // 2
            is_odd = (level_rows % 2) != 0
            if is_odd:
                i_end = next_rows - 1
            else:
                i_end = next_rows

            pixels_tree = next_rows * level_columns

            # For each column, use numpy to calculate min/max values for each group of 2 neighbor rows.
            # 1st input array = for each column, keep one of two rows starting from 0.
            # Don't keep the last row if odd.
            # 2nd input array = idem but start from 1.
            # Input shape is (2, level_rows // 2, nb_cols).
            # min/max is calculated for each 2 input pixels.
            # Output shape is (level_rows // 2, nb_cols).
            out_array = np_min_max_func(
                [
                    np_base[: i_end * 2 : 2, :],
                    np_base[1 : i_end * 2 : 2, :],
                ],
                axis=0,
            )

            # If row count is odd, simply copy the last input row
            if is_odd:
                out_array = np.vstack((out_array, np_base[np.newaxis, -1, :]))

            # Post-processing = put back the nan values and copy results into the parent tree
            post_processing()

            # Recursive call
            if level > 0:
                self.apply_recursively(tree, level - 1, next_rows, level_columns, min_max_flag, tree, self.start[level])

    # pylint: enable=too-many-branches

    def process_updated_elevation(self, elevations_list: np.ndarray):
        """
        Override SimpleTile process_updated_elevation function
        """
        self._raw = elevations_list

        nb_rows = self.latitude_rows
        nb_cols = self.longitude_columns

        # set up the levels
        size = self.set_levels(0, nb_rows, nb_cols)
        self._min_tree = np.zeros(size)
        self._max_tree = np.zeros(size)

        # compute min/max trees
        if len(self.start) > 0:
            preprocessed = np.zeros_like(self.raw)

            self.preprocess(preprocessed, self._raw, nb_rows, nb_cols, MinMax.MIN)
            self.apply_recursively(self._min_tree, len(self.start) - 1, nb_rows, nb_cols, MinMax.MIN, preprocessed, 0)

            self.preprocess(preprocessed, self._raw, nb_rows, nb_cols, MinMax.MAX)
            self.apply_recursively(self._max_tree, len(self.start) - 1, nb_rows, nb_cols, MinMax.MAX, preprocessed, 0)

    def locate_min(self, i: int, j: int, level: int) -> List[int]:
        """
        Locate the cell at which min elevation is reached for a specified level.

        Min is computed with respect to the continuous interpolated elevation, which
        takes four neighboring cells into account. This implies that the cell at which
        min value is reached for some level is either within the sub-tile for this level,
        or in some case it may be one column outside to the East or one row outside to
        the North. See get_min_elevation() for a more complete explanation.

        Parameters
        ----------
            i: row index of the cell
            j: column index of the cell
            level: tree level of the sub-tile considered

        Returns
        -------
            row/column indices of the cell at which min elevation is reached
        """
        return self.locate_min_max(i, j, level, MinSelector(), self._min_tree)

    def locate_max(self, i: int, j: int, level: int) -> List[int]:
        """
        Locate the cell at which max elevation is reached for a specified level.

        Max is computed with respect to the continuous interpolated elevation, which
        takes four neighboring cells into account. This implies that the cell at which
        max value is reached for some level is either within the sub-tile for this level,
        or in some case it may be one column outside to the East or one row outside to
        the North. See get_max_elevation for a more complete explanation.

        Parameters
        ----------
            i: row index of the cell
            j: column index of the cell
            level: tree level of the sub-tile considered

        Returns
        -------
            row/column indices of the cell at which min elevation is reached
        """
        return self.locate_min_max(i, j, level, MaxSelector(), self._max_tree)

    def locate_min_max(self, i: int, j: int, level: int, selector: Selector, tree: List[float]) -> List[int]:
        """
        Locate the cell at which min/max elevation is reached for a specified level.

        Parameters
        ----------
            i: row index of the cell
            j: column index of the cell
            level: tree level of the sub-tile considered
            selector: min/max selector to use
            tree: min/max tree to use

        Returns
        -------
            row/column indices of the cell at which min/max elevation is reached
        """
        k = len(self.start) - level
        row_shift = k // 2
        col_shift = (k + 1) // 2
        level_i = i >> row_shift
        level_j = j >> col_shift
        level_c = 1 + ((self.longitude_columns - 1) >> col_shift)

        # track the cell ancestors from merged tree at specified level up to tree at level 1
        for lvl in range(level + 1, len(self.start)):
            if self.is_column_merging(lvl):
                col_shift -= 1
                level_c = 1 + ((self.longitude_columns - 1) >> col_shift)
                level_j = level_j << 1
                if level_j + 1 < level_c:
                    # the cell results from a regular merging of two columns
                    if selector.select_first(
                        tree[self.start[lvl] + level_i * level_c + level_j + 1],
                        tree[self.start[lvl] + level_i * level_c + level_j],
                    ):
                        level_j += 1
            else:
                row_shift -= 1
                level_r = 1 + ((self.latitude_rows - 1) >> row_shift)
                level_i = level_i << 1

                if level_i + 1 < level_r:
                    # the cell results from a regular merging of two rows
                    if selector.select_first(
                        tree[self.start[lvl] + (level_i + 1) * level_c + level_j],
                        tree[self.start[lvl] + level_i * level_c + level_j],
                    ):
                        level_i += 1

        # we are now at first merge level, which always results from a column merge
        # or pre-processed data, which themselves result from merging four cells
        # used in interpolation
        # this imply the ancestor of min/max at (col, row) is one of
        # (2col, row), (2col+1, row), (2col+2, row), (2col, row+1), (2col+1, row+1), (2col+2, row+1)

        selected_i = level_i
        selected_j = 2 * level_j
        selected_elevation = math.nan

        for col in range(2 * level_j, 2 * level_j + 3):
            if col < self.longitude_columns:
                for row in range(level_i, level_i + 2):
                    if row < self.latitude_rows:
                        elevation = self.raw[row * self.longitude_columns + col]
                        if selector.select_first(elevation, selected_elevation):
                            selected_i = row
                            selected_j = col
                            selected_elevation = elevation

        return [selected_i, selected_j]

    def get_min_elevation(self, i: int, j: int, level: int) -> float:
        """
        Get the minimum elevation at some level tree.

        Note that the min elevation is not computed
        only at cell center, but considering that it is interpolated
        considering also Eastwards and Northwards neighbors, and extends
        up to the center of these neighbors. As an example, lets consider
        four neighboring cells in some Digital Elevation Model:
        * j+1: 11; 10
        * j: 12; 11
        * j/i: i; i+1

        When we interpolate elevation at a point located slightly South-West
        to the center of the (i+1, j+1) cell, we use all four cells in the
        interpolation, and we will get a result very close to 10 if we start
        close to (i+1, j+1) cell center. As the min value for this interpolation
        is stored at (i, j) indices, this implies that get_min_elevation(i,
        j, l) must return 10 if l is chosen such that the sub-tile at
        tree level l includes cell (i,j) but not cell (i+1, j+1). In other words,
        interpolation implies sub-tile boundaries are overshoot by one column to
        the East and one row to the North when computing min.

        Parameters
        ----------
            i: row index of the cell
            j: column index of the cell
            level: tree level

        Returns
        -------
            minimum value that can be reached when interpolating elevation in the sub-tile
        """
        # compute indices in level merged array
        k = len(self.start) - level
        row_shift = k // 2
        col_shift = (k + 1) // 2
        level_i = i >> row_shift
        level_j = j >> col_shift
        level_c = 1 + ((self.longitude_columns - 1) >> col_shift)

        located_min = self.locate_min(i, j, level)
        index = located_min[0] * self.longitude_columns + located_min[1]

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_tile_cell(self, located_min[0], located_min[1], self.raw[index])
            if index + self.longitude_columns < len(self.raw):
                dump_manager.DUMP_VAR.dump_tile_cell(
                    self, located_min[0] + 1, located_min[1], self.raw[index + self.longitude_columns]
                )
            if index + 1 < len(self.raw):
                dump_manager.DUMP_VAR.dump_tile_cell(self, located_min[0], located_min[1] + 1, self.raw[index + 1])
            if index + self.longitude_columns + 1 < len(self.raw):
                dump_manager.DUMP_VAR.dump_tile_cell(
                    self, located_min[0] + 1, located_min[1] + 1, self.raw[index + self.longitude_columns + 1]
                )

        return self.min_tree[self.start[level] + level_i * level_c + level_j]

    def get_max_elevation(self, i: int, j: int, level: int) -> float:
        """
        Get the maximum elevation at some level tree.

        Note that the max elevation is not computed
        only at cell center, but considering that it is interpolated
        considering also Eastwards and Northwards neighbors, and extends
        up to the center of these neighbors. As an example, lets consider
        four neighboring cells in some Digital Elevation Model:
        * j+1: 11; 12
        * j: 10, 11
        * j/i: i; i+1

        When we interpolate elevation at a point located slightly South-West
        to the center of the (i+1, j+1) cell, we use all four cells in the
        interpolation, and we will get a result very close to 12 if we start
        close to (i+1, j+1) cell center. As the max value for this interpolation
        is stored at (i, j) indices, this implies that get_max_elevation(i,
        j, l) must return 12 if l is chosen such that the sub-tile at
        tree level l includes cell (i,j) but not cell (i+1, j+1). In other words,
        interpolation implies sub-tile boundaries are overshoot by one column to
        the East and one row to the North when computing max.

        Parameters
        ----------
            i: row index of the cell
            j: column index of the cell
            level: tree level

        Returns
        -------
            maximum value that can be reached when interpolating elevation
        """
        # compute indices in level merged array
        k = len(self.start) - level
        row_shift = k // 2
        col_shift = (k + 1) // 2
        level_i = i >> row_shift
        level_j = j >> col_shift
        level_c = 1 + ((self.longitude_columns - 1) >> col_shift)

        if dump_manager.DUMP_VAR is not None:
            located_max = self.locate_max(i, j, level)
            index = located_max[0] * self.longitude_columns + located_max[1]

            dump_manager.DUMP_VAR.dump_tile_cell(self, located_max[0], located_max[1], self.raw[index])
            if (index + self.longitude_columns) < len(self.raw):
                dump_manager.DUMP_VAR.dump_tile_cell(
                    self, located_max[0] + 1, located_max[1], self.raw[index + self.longitude_columns]
                )
            if (index + 1) < len(self.raw):
                dump_manager.DUMP_VAR.dump_tile_cell(self, located_max[0], located_max[1] + 1, self.raw[index + 1])
            if (index + self.longitude_columns + 1) < len(self.raw):
                dump_manager.DUMP_VAR.dump_tile_cell(
                    self, located_max[0] + 1, located_max[1] + 1, self.raw[index + self.longitude_columns] + 1
                )

        return self.max_tree[self.start[level] + level_i * level_c + level_j]

    def get_max_elevation_vec(self, i: np.ndarray, j: np.ndarray, levels: np.ndarray) -> np.ndarray:
        """
        Get the maximum elevations at some level trees.

        Note that the max elevation is not computed
        only at cell center, but considering that it is interpolated
        considering also Eastwards and Northwards neighbors, and extends
        up to the center of these neighbors. As an example, lets consider
        four neighboring cells in some Digital Elevation Model:
        * j+1: 11; 12
        * j: 10, 11
        * j/i: i; i+1

        When we interpolate elevation at a point located slightly South-West
        to the center of the (i+1, j+1) cell, we use all four cells in the
        interpolation, and we will get a result very close to 12 if we start
        close to (i+1, j+1) cell center. As the max value for this interpolation
        is stored at (i, j) indices, this implies that get_max_elevation(i,
        j, l) must return 12 if l is chosen such that the sub-tile at
        tree level l includes cell (i,j) but not cell (i+1, j+1). In other words,
        interpolation implies sub-tile boundaries are overshoot by one column to
        the East and one row to the North when computing max.

        Parameters
        ----------
            i: row indexes of the cell
            j: column indexes of the cell
            levels: tree levels

        Returns
        -------
            maximum values that can be reached when interpolating elevation
        """
        assert levels.shape == i.shape
        assert levels.shape == j.shape

        lvl_int = levels.astype("int64", copy=False)
        i_int = i.astype("int64", copy=False)
        j_int = j.astype("int64", copy=False)

        # compute indices in level merged array
        k = len(self.start) - lvl_int
        row_shift = k // 2
        col_shift = (k + 1) // 2
        level_i = i_int >> row_shift
        level_j = j_int >> col_shift
        level_c = 1 + ((self.longitude_columns - 1) >> col_shift)

        return self.max_tree[self.start[lvl_int] + level_i * level_c + level_j]

    def get_merge_level(self, i_1: int, j_1: int, i_2: int, j_2: int):
        """
        Get the deepest level at which two cells are merged in the same min/max sub-tile.

        Parameters
        ----------
            i_1: row index of first cell
            j_1: column index of first cell
            i_2: row index of second cell
            j_2: column index of second cell

        Returns
        -------
            deepest level at which two cells are merged in the same min/max sub-tile,
        or -1 if they are never merged in the same sub-tile
        """
        largest = -1

        for level in range(len(self.start)):
            # compute indices in level merged array
            k = len(self.start) - level
            row_shift = k // 2
            col_shift = (k + 1) // 2
            level_i_1 = i_1 >> row_shift
            level_j_1 = j_1 >> col_shift
            level_i_2 = i_2 >> row_shift
            level_j_2 = j_2 >> col_shift

            if level_i_1 != level_i_2 or level_j_1 != level_j_2:
                return largest

            largest = level

        return largest

    def get_merge_level_vec(self, i_1: np.ndarray, j_1: np.ndarray, i_2: np.ndarray, j_2: np.ndarray):
        """
        Get the deepest levels at which two cells are merged in the same min/max sub-tile.

        Parameters
        ----------
            i_1: row indexes of first cell
            j_1: column indexes of first cell
            i_2: row indexes of second cell
            j_2: column indexes of second cell

        Returns
        -------
            deepest level at which two cells are merged in the same min/max sub-tile,
        or -1 if they are never merged in the same sub-tile
        """

        largest = -np.ones(i_1.shape, dtype="int64")
        status = largest < 0
        ind_ok = np.where(status)[0]

        i_1_int = i_1.astype("int64", copy=False)
        j_1_int = j_1.astype("int64", copy=False)
        i_2_int = i_2.astype("int64", copy=False)
        j_2_int = j_2.astype("int64", copy=False)

        for level in range(len(self.start)):
            # compute indices in level merged array
            k = len(self.start) - level
            row_shift = k // 2
            col_shift = (k + 1) // 2
            level_i_1 = i_1_int[ind_ok] >> row_shift
            level_j_1 = j_1_int[ind_ok] >> col_shift
            level_i_2 = i_2_int[ind_ok] >> row_shift
            level_j_2 = j_2_int[ind_ok] >> col_shift

            # check points that are still merged at this level
            status[ind_ok] = (level_i_1 == level_i_2) * (level_j_1 == level_j_2)

            # update the set of points to search
            ind_ok = np.where(status)[0]
            if len(ind_ok) == 0:
                # stop here if all levels found
                break

            # update the current level for remaining points
            largest[ind_ok] = level

        return largest

    @staticmethod
    def build_crossings(begin: int, end: int, step: int, ascending: bool) -> List[int]:
        """
        Build crossings arrays.

        Parameters
        ----------
            begin: begin crossing index
            end: end crossing index (excluded, if equal to begin, the array is empty)
            step: crossing step
            ascending: if true, the crossings must be in ascending order

        Returns
        -------
            indices of rows or columns crossed at sub-tiles boundaries, in crossing order
        """
        if step > 0:
            step_sign = 1
        else:
            step_sign = -1

        fm_max = max(0, (end - begin + step - step_sign) // step)
        crossings = [0] * fm_max

        crossing = begin
        if ascending:
            for i, _ in enumerate(crossings):
                crossings[i] = crossing
                crossing += step
        else:
            for i, _ in enumerate(crossings):
                crossings[len(crossings) - 1 - i] = crossing
                crossing += step

        return crossings

    def get_crossed_boundary_rows(self, row1: int, row2: int, level: int) -> List[int]:
        """
        Get the index of sub-tiles start rows crossed.

        When going from one row to another row at some tree level,
        we cross sub-tiles boundaries. This method returns the index of these boundaries.

        Parameters
        ----------
            row1: starting row
            row2: ending row
            level: tree level

        Returns
        -------
            indices of rows crossed at sub-tiles boundaries, in crossing order, the endpoints are included
        (i.e. if row1 or row2 are boundary rows, they will be in returned array)
        """
        # number of rows in each sub-tile
        rows = 1 << ((len(self.start) - level) // 2)

        # build the crossings in ascending order
        fm_min = min(row1, row2)
        fm_max = max(row1, row2) + 1

        return self.build_crossings(fm_min + rows - 1 - ((fm_min + rows - 1) % rows), fm_max, rows, row1 <= row2)

    def get_crossed_boundary_rows_vec(self, row1: np.ndarray, row2: np.ndarray, level: np.ndarray) -> np.ndarray:
        """
        Get the indexes of sub-tiles start rows crossed.

        When going from one row to another row at some tree level,
        we cross sub-tiles boundaries. This method returns the index of these boundaries.

        Parameters
        ----------
            row1: starting rows
            row2: ending rows
            level: tree levels

        Returns
        -------
            indices of rows crossed at sub-tiles boundaries, in crossing order, the endpoints are included
        (i.e. if row1 or row2 are boundary rows, they will be in returned array)
        """
        crossed_res = np.zeros(row1.shape, dtype=object)
        for i in range(row1.size):
            crossed_res[i] = self.get_crossed_boundary_rows(int(row1[i]), int(row2[i]), int(level[i]))

        return crossed_res

    def get_crossed_boundary_columns(self, column1: int, column2: int, level: int):
        """
         Get the index of sub-tiles start columns crossed.

        When going from one column to another column at some tree level,
        we cross sub-tiles boundaries. This method returns the index of these boundaries.

        Parameters
        ----------
             column1: starting column
             column2: ending column (excluded)
             level: tree level

        Returns
        -------
            indices of columns crossed at sub-tiles boundaries, in crossing order, the endpoints are included
         (i.e. if column1 or column2 are boundary columns, they will be in returned array)
        """
        # number of columns in each sub-tile
        columns = 1 << ((len(self.start) + 1 - level) // 2)

        # build the crossings in ascending order
        fm_min = min(column1, column2)
        fm_max = max(column1, column2) + 1

        return self.build_crossings(
            fm_min + columns - 1 - ((fm_min + columns - 1) % columns), fm_max, columns, column1 <= column2
        )

    def get_crossed_boundary_columns_vec(self, column1: np.ndarray, column2: np.ndarray, level: np.ndarray):
        """
         Get the indexes of sub-tiles start columns crossed.

        When going from one column to another column at some tree level,
        we cross sub-tiles boundaries. This method returns the index of these boundaries.

        Parameters
        ----------
             column1: starting column
             column2: ending column (excluded)
             level: tree level

        Returns
        -------
            indices of columns crossed at sub-tiles boundaries, in crossing order, the endpoints are included
         (i.e. if column1 or column2 are boundary columns, they will be in returned array)
        """
        crossed_res = np.zeros(column1.shape, dtype=object)
        for i in range(column1.size):
            crossed_res[i] = self.get_crossed_boundary_columns(int(column1[i]), int(column2[i]), int(level[i]))

        return crossed_res
