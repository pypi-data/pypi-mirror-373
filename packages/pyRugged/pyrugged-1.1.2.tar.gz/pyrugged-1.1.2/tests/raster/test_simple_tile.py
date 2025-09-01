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

"""Test of pyrugged Class SimpleTile"""

# pylint: disable=arguments-out-of-order
import math

import numpy as np
import pytest

from pyrugged.bodies.geodesy import normalize_geodetic_point
from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.raster.location import Location
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.utils.math_utils import normalize_angle  # pylint: disable=no-name-in-module


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


def test_not_configured():
    """Test SimpleTile without configuration"""

    tile = SimpleTile()

    assert tile.minimum_latitude == pytest.approx(0, abs=1.0e-10)
    assert tile.minimum_longitude == pytest.approx(0, abs=1.0e-10)
    assert tile.latitude_step == pytest.approx(0, abs=1.0e-10)
    assert tile.longitude_step == pytest.approx(0, abs=1.0e-10)
    assert tile.latitude_rows == 0
    assert tile.longitude_columns == 0
    assert tile.min_elevation == pytest.approx(0, abs=1.0e-10)
    assert tile.max_elevation == pytest.approx(0, abs=1.0e-10)


def test_empty():
    """Test empty tile error"""

    try:
        tile = SimpleTile()
        tile.set_geometry(1.0, 2.0, 0.1, 0.2, 0, 200)
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.EMPTY_TILE.value.format(0, 200)

    try:
        tile = SimpleTile()
        tile.set_geometry(1.0, 2.0, 0.1, 0.2, 100, 0)
        pytest.fail("An exception should have been thrown")

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.EMPTY_TILE.value.format(100, 0)


def test_update():
    """Test SimpleTile update"""
    tile = SimpleTile()
    tile.set_geometry(np.radians(1.0), np.radians(2.0), np.radians(0.1), np.radians(0.2), 100, 200)
    for i in range(tile.latitude_rows):
        for j in range(tile.longitude_columns):
            tile.set_elevation(i, j, float(1000 * i + j))
    tile.tile_update_completed()

    assert tile.minimum_latitude == pytest.approx(np.radians(1.0), abs=1.0e-10)
    assert tile.minimum_longitude == pytest.approx(np.radians(2.0), abs=1.0e-10)
    assert tile.maximum_latitude == pytest.approx(np.radians(10.9), abs=1.0e-10)
    assert tile.maximum_longitude == pytest.approx(np.radians(41.8), abs=1.0e-10)
    assert tile.latitude_step == pytest.approx(np.radians(0.1), abs=1.0e-10)
    assert tile.longitude_step == pytest.approx(np.radians(0.2), abs=1.0e-10)
    assert tile.latitude_rows == 100
    assert tile.longitude_columns == 200
    assert tile.min_elevation == pytest.approx(0.0, abs=1.0e-10)
    assert tile.max_elevation == pytest.approx(99199.0, abs=1.0e-10)

    assert tile.get_location(np.radians(0.0), np.radians(1.0)) == Location.SOUTH_WEST
    assert tile.get_location(np.radians(6.0), np.radians(1.0)) == Location.WEST
    assert tile.get_location(np.radians(12.0), np.radians(1.0)) == Location.NORTH_WEST
    assert tile.get_location(np.radians(0.0), np.radians(22.0)) == Location.SOUTH
    assert tile.get_location(np.radians(6.0), np.radians(22.0)) == Location.HAS_INTERPOLATION_NEIGHBORS
    assert tile.get_location(np.radians(12.0), np.radians(22.0)) == Location.NORTH
    assert tile.get_location(np.radians(0.0), np.radians(43.0)) == Location.SOUTH_EAST
    assert tile.get_location(np.radians(6.0), np.radians(43.0)) == Location.EAST
    assert tile.get_location(np.radians(12.0), np.radians(43.0)) == Location.NORTH_EAST

    # check borders
    assert tile.get_location(tile.minimum_latitude, np.radians(22.0)) == Location.HAS_INTERPOLATION_NEIGHBORS
    assert tile.get_location(np.radians(6.0), tile.minimum_longitude) == Location.HAS_INTERPOLATION_NEIGHBORS
    assert tile.get_location(tile.maximum_latitude, np.radians(22.0)) == Location.HAS_INTERPOLATION_NEIGHBORS
    assert tile.get_location(np.radians(6.0), tile.maximum_longitude) == Location.HAS_INTERPOLATION_NEIGHBORS

    # gather all previous points
    latitudes = np.radians(np.array([0, 6, 12, 0, 6, 12, 0, 6, 12, 1, 6, 10.9, 6], dtype="float64"))
    longitudes = np.radians(np.array([1, 1, 1, 22, 22, 22, 43, 43, 43, 22, 2, 22, 41.8], dtype="float64"))
    # numeric fix for point #11 on the tile border
    latitudes[11] = tile.maximum_latitude

    ref_locations = np.array(
        [
            Location.SOUTH_WEST.value,
            Location.WEST.value,
            Location.NORTH_WEST.value,
            Location.SOUTH.value,
            Location.HAS_INTERPOLATION_NEIGHBORS.value,
            Location.NORTH.value,
            Location.SOUTH_EAST.value,
            Location.EAST.value,
            Location.NORTH_EAST.value,
            Location.HAS_INTERPOLATION_NEIGHBORS.value,
            Location.HAS_INTERPOLATION_NEIGHBORS.value,
            Location.HAS_INTERPOLATION_NEIGHBORS.value,
            Location.HAS_INTERPOLATION_NEIGHBORS.value,
        ],
        dtype="int16",
    )

    locations, ind_has_neighbors = tile.get_location_arr(latitudes, longitudes)
    assert np.all(locations == ref_locations)
    assert np.all(ind_has_neighbors == [4, 9, 10, 11, 12])

    for i in range(tile.latitude_rows):
        for j in range(tile.longitude_columns):
            assert tile.get_elevation_at_indices(i, j) == pytest.approx(1000 * i + j, abs=1.0e-10)


def check_out_of_bound(i, j, tile):
    """Test coordinates out of tile error"""

    try:
        tile.set_elevation(i, j, 1000.0)

    except PyRuggedError as pre:
        assert str(pre) == PyRuggedMessages.OUT_OF_TILE_INDICES.value.format(
            i, j, tile.latitude_rows - 1, tile.longitude_columns - 1
        )


def test_out_of_bounds_indices():
    """Test coordinates out of tile error"""

    tile = SimpleTile()
    tile.set_geometry(1.0, 2.0, 0.1, 0.2, 100, 200)
    tile.set_elevation(50, 100, 1000.0)
    tile.tile_update_completed()

    check_out_of_bound(-1, 100, tile)
    check_out_of_bound(100, 100, tile)
    check_out_of_bound(50, -1, tile)
    check_out_of_bound(50, 200, tile)


def test_index_shift():
    """Test indexes shift"""

    tile = SimpleTile()
    tile.set_geometry(1.0, 2.0, 0.1, 0.2, 100, 200)
    tile.set_elevation(50, 100, 1000.0)
    tile.tile_update_completed()

    # Indices correspond to cells centers
    lat_center_column_50 = tile.get_latitude_at_index(50)
    lat_center_column_51 = tile.get_latitude_at_index(51)
    lon_center_row_23 = tile.get_longitude_at_index(23)
    lon_center_row_24 = tile.get_longitude_at_index(24)

    # get_latitude_index shit indices 1/2 cell so that
    # the specified latitude is always between index and index + 1
    # So despite lat_west_column_51 is very close to column 51 center,
    # get_latitude_index should return 50
    lat_west_column_51 = 0.001 * lat_center_column_50 + 0.999 * lat_center_column_51
    retrieved_lat_index = tile.get_floor_latitude_index(lat_west_column_51)
    assert retrieved_lat_index == 50
    assert tile.get_latitude_at_index(retrieved_lat_index) < lat_west_column_51
    assert lat_west_column_51 < tile.get_latitude_at_index(retrieved_lat_index + 1)

    # get_longitude_index shift indices 1/2 cell, so that
    # the specified longitude is always between index and index+1
    # So despite lon_south_row_24 is very close to row 24 center,
    # get_longitude_index should return 23
    lon_south_row_24 = 0.001 * lon_center_row_23 + 0.999 * lon_center_row_24
    retrieved_lon_index = tile.get_floor_longitude_index(lon_south_row_24)
    assert retrieved_lon_index == 23
    assert tile.get_longitude_at_index(retrieved_lon_index) < lon_south_row_24
    assert lon_south_row_24 < tile.get_longitude_at_index(retrieved_lon_index + 1)


def test_interpolation():
    """Test SimpleTile.interpolate_elevation()"""

    tile = SimpleTile()
    tile.set_geometry(np.deg2rad(0.0), np.deg2rad(0.0), np.deg2rad(1.0), np.deg2rad(1.0), 50, 50)
    tile.set_elevation(20, 14, 91.0)
    tile.set_elevation(20, 15, 210.0)
    tile.set_elevation(21, 14, 162.0)
    tile.set_elevation(21, 15, 95.0)
    tile.tile_update_completed()

    assert tile.interpolate_elevation(np.deg2rad(20.0), np.deg2rad(14.5)) == pytest.approx(150.5, abs=1.0e-10)
    assert tile.interpolate_elevation(np.deg2rad(21.0 - 1.0e-14), np.deg2rad(14.5)) == pytest.approx(128.5, abs=1.0e-10)
    assert math.isnan(tile.interpolate_elevation(np.deg2rad(21.0 + 1.0e-14), np.deg2rad(14.5)))
    assert tile.interpolate_elevation(np.deg2rad(20.2), np.deg2rad(14.5)) == pytest.approx(146.1, abs=1.0e-10)


def test_interpolation_within_tolerance():
    """Test SimpleTile.interpolate_elevation()"""

    tile = SimpleTile()
    tile.set_geometry(np.deg2rad(0.0), np.deg2rad(0.0), np.deg2rad(1.0), np.deg2rad(1.0), 2, 2)
    tile.set_elevation(0, 0, 91.0)
    tile.set_elevation(0, 1, 210.0)
    tile.set_elevation(1, 0, 162.0)
    tile.set_elevation(1, 1, 95.0)
    tile.tile_update_completed()

    # The following points are 1/16 cell out of tile
    assert tile.interpolate_elevation(np.deg2rad(-0.0625), np.deg2rad(0.5)) == pytest.approx(151.875, abs=1.0e-10)
    assert tile.interpolate_elevation(np.deg2rad(1.0625), np.deg2rad(0.5)) == pytest.approx(127.125, abs=1.0e-10)
    assert tile.interpolate_elevation(np.deg2rad(0.5), np.deg2rad(-0.0625)) == pytest.approx(124.875, abs=1.0e-10)
    assert tile.interpolate_elevation(np.deg2rad(0.5), np.deg2rad(1.0625)) == pytest.approx(154.125, abs=1.0e-10)


def test_interpolation_out_of_tolerance():
    """Test coordinates out of tile error"""

    tile = SimpleTile()
    tile.set_geometry(np.deg2rad(0.0), np.deg2rad(0.0), np.deg2rad(1.0), np.deg2rad(1.0), 2, 2)
    tile.set_elevation(0, 0, 91.0)
    tile.set_elevation(0, 1, 210.0)
    tile.set_elevation(1, 0, 162.0)
    tile.set_elevation(1, 1, 95.0)
    tile.tile_update_completed()

    # The following point are 3/16 cell out of tile
    outside_points = np.array(
        [
            [np.deg2rad(-0.1875), np.deg2rad(0.5)],
            [np.deg2rad(1.1875), np.deg2rad(0.5)],
            [np.deg2rad(0.5), np.deg2rad(-0.1875)],
            [np.deg2rad(0.5), np.deg2rad(1.1875)],
        ],
    )
    for point in outside_points:
        with pytest.raises(PyRuggedError, match=r".*no data at latitude .* and longitude .*"):
            tile.interpolate_elevation(point[0], point[1])

    points_batch = np.concatenate([outside_points, [[np.deg2rad(0.5), np.deg2rad(0.5)]]])
    elev = tile.interpolate_elevation_arr(points_batch[:, 0], points_batch[:, 1])
    assert np.all(np.isnan(elev[0:4]))
    assert ~np.isnan(elev[4])


def check_in_line(gp_a, gp_b, gp_i):
    """Check line"""

    t_val = (gp_i[2] - gp_a[2]) / (gp_b[2] - gp_a[2])

    assert gp_a[0] * (1 - t_val) + gp_b[0] * t_val == pytest.approx(gp_i[0], abs=1.0e-10)
    assert normalize_angle(gp_a[1] * (1 - t_val) + gp_b[1] * t_val, gp_i[1]) == pytest.approx(gp_i[1], abs=1.0e-10)


def check_on_tile(tile, gp_i):
    """Check if geodetic point is on the tile"""

    assert tile.interpolate_elevation(gp_i[0], gp_i[1]) == pytest.approx(gp_i[2], abs=1.0e-10)


def los(gp_a, gp_b):
    """This is a crude conversion into geodetic space
    intended only for the purposes of these tests
    it considers the geodetic space is perfectly Cartesian
    in the East, North, Zenith frame

    """

    return np.array([gp_b[0] - gp_a[0], gp_b[1] - gp_a[1], gp_b[2] - gp_a[2]])


def test_cell_intersection():
    """Test SimpleTile.cell_intersection()"""

    tile = SimpleTile()
    tile.set_geometry(0.0, 0.0, 0.025, 0.025, 50, 50)
    tile.set_elevation(20, 14, 91.0)
    tile.set_elevation(20, 15, 210.0)
    tile.set_elevation(21, 14, 162.0)
    tile.set_elevation(21, 15, 95.0)
    tile.tile_update_completed()

    gp_a = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(20) + 0.1 * tile.latitude_step,
                tile.get_longitude_at_index(14) + 0.2 * tile.longitude_step,
                300.0,
            ]
        ),
        tile.get_longitude_at_index(14),
    )

    gp_b = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(20) + 0.7 * tile.latitude_step,
                tile.get_longitude_at_index(14) + 0.9 * tile.longitude_step,
                10.0,
            ]
        ),
        tile.get_longitude_at_index(14),
    )

    gp_iab = tile.cell_intersection(gp_a, los(gp_a, gp_b), 20, 14)
    check_in_line(gp_a, gp_b, gp_iab)
    check_on_tile(tile, gp_iab)

    gp_iba = tile.cell_intersection(gp_b, los(gp_b, gp_a), 20, 14)
    check_in_line(gp_a, gp_b, gp_iba)
    check_on_tile(tile, gp_iba)

    assert gp_iab[0] == pytest.approx(gp_iba[0], abs=1.0e-10)
    assert gp_iab[1] == pytest.approx(gp_iba[1], abs=1.0e-10)
    assert gp_iab[2] == pytest.approx(gp_iba[2], abs=1.0e-10)


def test_cell_intersection_2_pi_wrapping():
    """Test SimpleTile.cell_intersection()"""

    tile = SimpleTile()
    tile.set_geometry(0.0, 0.0, 0.025, 0.025, 50, 50)
    tile.set_elevation(20, 14, 91.0)
    tile.set_elevation(20, 15, 210.0)
    tile.set_elevation(21, 14, 162.0)
    tile.set_elevation(21, 15, 95.0)
    tile.tile_update_completed()

    gp_a = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(20) + 0.1 * tile.latitude_step,
                tile.get_longitude_at_index(14) + 0.2 * tile.longitude_step,
                300.0,
            ]
        ),
        4 * float(np.pi),
    )

    gp_b = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(20) + 0.7 * tile.latitude_step,
                tile.get_longitude_at_index(14) + 0.9 * tile.longitude_step,
                10.0,
            ]
        ),
        4 * float(np.pi),
    )

    gp_iab = tile.cell_intersection(gp_a, los(gp_a, gp_b), 20, 14)
    check_in_line(gp_a, gp_b, gp_iab)
    check_on_tile(tile, gp_iab)

    gp_iba = tile.cell_intersection(gp_b, los(gp_b, gp_a), 20, 14)
    check_in_line(gp_a, gp_b, gp_iab)
    check_on_tile(tile, gp_iba)

    assert gp_iab[0] == pytest.approx(gp_iba[0], abs=1.0e-10)
    assert gp_iab[1] == pytest.approx(gp_iba[1], abs=1.0e-10)
    assert gp_iab[2] == pytest.approx(gp_iba[2], abs=1.0e-10)


def test_cell_intersection_2_solutions():
    """Test SimpleTile.cell_intersection()"""

    tile = SimpleTile()
    tile.set_geometry(0.0, 0.0, 0.025, 0.025, 50, 50)
    tile.set_elevation(20, 14, 91.0)
    tile.set_elevation(20, 15, 210.0)
    tile.set_elevation(21, 14, 162.0)
    tile.set_elevation(21, 15, 95.0)
    tile.tile_update_completed()

    # The line from gpA to gpB should traverse the DEM twice within the tile
    # we use the points in the two different orders to retrieve both solutions
    gp_a = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(20) + 0.1 * tile.latitude_step,
                tile.get_longitude_at_index(14) + 0.2 * tile.longitude_step,
                120.0,
            ]
        ),
        tile.get_longitude_at_index(14),
    )

    gp_b = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(20) + 0.7 * tile.latitude_step,
                tile.get_longitude_at_index(14) + 0.9 * tile.longitude_step,
                130.0,
            ]
        ),
        tile.get_longitude_at_index(14),
    )

    # The line from gpA to gpB should traverse the DEM twice within the tile
    # we use the points in the two different orders to retrieve both solutions
    gp_iab = tile.cell_intersection(gp_a, los(gp_a, gp_b), 20, 14)
    check_in_line(gp_a, gp_b, gp_iab)
    check_on_tile(tile, gp_iab)

    gp_iba = tile.cell_intersection(gp_b, los(gp_b, gp_a), 20, 14)
    check_in_line(gp_a, gp_b, gp_iba)
    check_on_tile(tile, gp_iba)

    # The two solutions are different
    assert gp_iab[2] == pytest.approx(120.231, abs=1.0e-3)
    assert gp_iba[2] == pytest.approx(130.081, abs=1.0e-3)


def test_cell_intersection_no_solutions():
    """Test SimpleTile.cell_intersection()"""

    tile = SimpleTile()
    tile.set_geometry(0.0, 0.0, 0.025, 0.025, 50, 50)
    tile.set_elevation(20, 14, 91.0)
    tile.set_elevation(20, 15, 210.0)
    tile.set_elevation(21, 14, 162.0)
    tile.set_elevation(21, 15, 95.0)
    tile.tile_update_completed()

    gp_a = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(20) + 0.1 * tile.latitude_step,
                tile.get_longitude_at_index(14) + 0.2 * tile.longitude_step,
                180.0,
            ]
        ),
        tile.get_longitude_at_index(14),
    )

    gp_b = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(20) + 0.7 * tile.latitude_step,
                tile.get_longitude_at_index(14) + 0.9 * tile.longitude_step,
                190.0,
            ]
        ),
        tile.get_longitude_at_index(14),
    )

    assert tile.cell_intersection(gp_a, los(gp_a, gp_b), 20, 14) is None


def test_cell_intersection_linear_only():
    """Test SimpleTile.cell_intersection()"""

    tile = SimpleTile()
    tile.set_geometry(0.0, 0.0, 0.025, 0.025, 50, 50)
    tile.set_elevation(0, 0, 30.0)
    tile.set_elevation(0, 1, 30.0)
    tile.set_elevation(1, 0, 40.0)
    tile.set_elevation(1, 1, 40.0)
    tile.tile_update_completed()

    gp_a = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(0) + 0.25 * tile.latitude_step,
                tile.get_longitude_at_index(0) + 0.50 * tile.longitude_step,
                50.0,
            ]
        ),
        tile.get_longitude_at_index(0),
    )

    gp_b = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(0) + 0.75 * tile.latitude_step,
                tile.get_longitude_at_index(0) + 0.50 * tile.longitude_step,
                20.0,
            ]
        ),
        tile.get_longitude_at_index(0),
    )

    gp_iab = tile.cell_intersection(gp_a, los(gp_a, gp_b), 0, 0)
    check_in_line(gp_a, gp_b, gp_iab)
    check_on_tile(tile, gp_iab)

    gp_iba = tile.cell_intersection(gp_b, los(gp_b, gp_a), 0, 0)
    check_in_line(gp_a, gp_b, gp_iba)
    check_on_tile(tile, gp_iba)

    assert gp_iab[0] == pytest.approx(gp_iba[0], abs=1.0e-10)
    assert gp_iab[1] == pytest.approx(gp_iba[1], abs=1.0e-10)
    assert gp_iab[2] == pytest.approx(gp_iba[2], abs=1.0e-10)


def test_cell_intersection_linear_intersection_outside():
    """Test SimpleTile.cell_intersection()"""

    tile = SimpleTile()
    tile.set_geometry(0.0, 0.0, 0.025, 0.025, 50, 50)
    tile.set_elevation(0, 0, 30.0)
    tile.set_elevation(0, 1, 30.0)
    tile.set_elevation(1, 0, 40.0)
    tile.set_elevation(1, 1, 40.0)
    tile.tile_update_completed()

    gp_a = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(0) + 0.25 * tile.latitude_step,
                tile.get_longitude_at_index(0) + 0.50 * tile.longitude_step,
                45.0,
            ]
        ),
        tile.get_longitude_at_index(0),
    )

    gp_b = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(0) + 0.75 * tile.latitude_step,
                tile.get_longitude_at_index(0) + 0.50 * tile.longitude_step,
                55.0,
            ]
        ),
        tile.get_longitude_at_index(0),
    )

    assert tile.cell_intersection(gp_a, los(gp_a, gp_b), 0, 0) is None


def test_cell_intersction_linear_no_intersection():
    """Test SimpleTile.cell_intersection()"""

    tile = SimpleTile()
    tile.set_geometry(0.0, 0.0, 0.025, 0.025, 50, 50)
    tile.set_elevation(0, 0, 30.0)
    tile.set_elevation(0, 1, 30.0)
    tile.set_elevation(1, 0, 40.0)
    tile.set_elevation(1, 1, 40.0)
    tile.tile_update_completed()

    gp_a = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(0) + 0.25 * tile.latitude_step,
                tile.get_longitude_at_index(0) + 0.50 * tile.longitude_step,
                45.0,
            ]
        ),
        tile.get_longitude_at_index(0),
    )

    gp_b = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(0) + 0.75 * tile.latitude_step,
                tile.get_longitude_at_index(0) + 0.50 * tile.longitude_step,
                50.0,
            ]
        ),
        tile.get_longitude_at_index(0),
    )

    assert tile.cell_intersection(gp_a, los(gp_a, gp_b), 0, 0) is None


def test_cell_intersection_constant_0():
    """Test SimpleTile.cell_intersection()"""

    tile = SimpleTile()
    tile.set_geometry(0.0, 0.0, 0.025, 0.025, 50, 50)
    tile.set_elevation(0, 0, 30.0)
    tile.set_elevation(0, 1, 30.0)
    tile.set_elevation(1, 0, 40.0)
    tile.set_elevation(1, 1, 40.0)
    tile.tile_update_completed()

    gp_a = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(0) + 0.25 * tile.latitude_step,
                tile.get_longitude_at_index(0) + 0.50 * tile.longitude_step,
                32.5,
            ]
        ),
        tile.get_longitude_at_index(0),
    )

    gp_b = normalize_geodetic_point(
        np.array(
            [
                tile.get_latitude_at_index(0) + 0.75 * tile.latitude_step,
                tile.get_longitude_at_index(0) + 0.50 * tile.longitude_step,
                37.5,
            ]
        ),
        tile.get_longitude_at_index(0),
    )

    gp_iab = tile.cell_intersection(gp_a, los(gp_a, gp_b), 0, 0)
    check_in_line(gp_a, gp_b, gp_iab)
    check_on_tile(tile, gp_iab)

    gp_iba = tile.cell_intersection(gp_b, los(gp_b, gp_a), 0, 0)
    check_in_line(gp_a, gp_b, gp_iba)
    check_on_tile(tile, gp_iba)

    assert gp_iab[0] == pytest.approx(gp_a[0], abs=1.0e-10)
    assert gp_iab[1] == pytest.approx(gp_a[1], abs=1.0e-10)
    assert gp_iab[2] == pytest.approx(gp_a[2], abs=1.0e-10)
    assert gp_iba[0] == pytest.approx(gp_b[0], abs=1.0e-10)
    assert gp_iba[1] == pytest.approx(gp_b[1], abs=1.0e-10)
    assert gp_iba[2] == pytest.approx(gp_b[2], abs=1.0e-10)


def test_normalize_geodetic_point():
    """
    Unit test to check behaviors of normalize_geodetic_point
    """
    gp_in = np.radians([15, -120, 0])

    # scalar version
    gp_a = normalize_geodetic_point(gp_in, np.radians(100))
    assert gp_a[1] == pytest.approx(np.radians(240), abs=1.0e-10)

    # vectorized versions
    gp_b = normalize_geodetic_point(np.array([gp_in, gp_in]), np.radians(100))
    assert gp_b.shape == (2, 3)
    assert gp_b[0, 1] == pytest.approx(np.radians(240), abs=1.0e-10)

    gp_c = normalize_geodetic_point(np.array([gp_in, gp_in]), np.radians([100, 100]))
    assert gp_c.shape == (2, 3)
    assert gp_c[0, 1] == pytest.approx(np.radians(240), abs=1.0e-10)

    gp_d = normalize_geodetic_point(gp_in, np.radians([100, 100]))
    assert gp_d.shape == (2, 3)
    assert gp_d[0, 1] == pytest.approx(np.radians(240), abs=1.0e-10)
