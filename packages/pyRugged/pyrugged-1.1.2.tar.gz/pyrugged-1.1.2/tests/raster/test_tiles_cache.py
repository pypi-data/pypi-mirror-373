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

"""Test of pyrugged Class TilesCache"""

import numpy as np
import pytest
from org.hipparchus.random import Well19937a

from pyrugged.configuration.init_orekit import init_orekit
from pyrugged.raster.simple_tile import SimpleTile
from pyrugged.raster.tiles_cache import TilesCache
from tests.raster.cached_elevation_updater import CachedElevationUpdater
from tests.raster.checked_pattern_elevation_updater import CheckedPatternElevationUpdater

init_orekit(use_internal_data=False)


def test_single_tile():
    """Test TilesCache with on tile"""

    cache = TilesCache(SimpleTile, CheckedPatternElevationUpdater(float(np.radians(3.0)), 11, 10.0, 20.0), 1000)
    tile = cache.get_tile(float(np.radians(-23.2)), float(np.radians(137.5)))

    assert cache.tiles_count == 1
    assert np.degrees(tile.minimum_latitude) == pytest.approx(-24.0, abs=1.0e-10)
    assert np.degrees(tile.minimum_longitude) == pytest.approx(135.0, abs=1.0e-10)
    assert np.degrees(tile.latitude_step) == pytest.approx(0.3, abs=1.0e-10)
    assert np.degrees(tile.longitude_step) == pytest.approx(0.3, abs=1.0e-10)
    assert tile.min_elevation == pytest.approx(10.0, abs=1.0e-10)
    assert tile.max_elevation == pytest.approx(20.0, abs=1.0e-10)


def test_eviction():
    """Test eviction of tiles from TilesCache"""

    cache = TilesCache(SimpleTile, CheckedPatternElevationUpdater(float(np.radians(1.0)), 11, 10.0, 20.0), 12)

    # Fill up the 12 tiles we can keep in cache
    for i in range(4):
        for j in range(3):
            cache.get_tile(float(np.radians(0.5 + j)), float(np.radians(0.5 + i)))

    assert cache.tiles_count == 12

    # Keep using the same tiles for a while
    generator = Well19937a(1234)
    for _index in range(10000):
        lat = 3.0 * generator.nextDouble()
        lon = 4.0 * generator.nextDouble()
        cache.get_tile(float(np.radians(lat)), float(np.radians(lon)))

    assert cache.tiles_count == 12

    # Ensure the (0.0, 0.0) tile is the least recently used one
    for i in range(4):
        for j in range(3):
            cache.get_tile(float(np.radians(0.5 + j)), float(np.radians(0.5 + i)))

    # Ask for one point outside of the covered area, to evict the (0.0, 0.0) tile
    cache.get_tile(float(np.radians(20.5)), float(np.radians(30.5)))
    assert cache.tiles_count == 12
    assert cache.is_tile_in_cache(float(np.radians(0.5)), float(np.radians(0.5))) is None

    # Ask again for one point in the evicted tile which must be reallocated
    cache.get_tile(float(np.radians(0.5)), float(np.radians(0.5)))
    assert cache.tiles_count == 12
    assert cache.is_tile_in_cache(float(np.radians(0.5)), float(np.radians(0.5))) is not None

    # The 13th allocated tile should still be there
    assert cache.tiles_count == 12
    assert cache.is_tile_in_cache(float(np.radians(20.5)), float(np.radians(30.5))) is not None

    # evict all the tiles, going to a completely different zone
    for i in range(4):
        for j in range(3):
            cache.get_tile(float(np.radians(40.5 + i)), float(np.radians(90.5 + j)))

    assert cache.tiles_count == 12
    for i in range(4):
        for j in range(3):
            assert cache.is_tile_in_cache(float(np.radians(0.5 + j)), float(np.radians(0.5 + i))) is None


def test_exact_end():
    """Test tiles parameters in TilesCache"""

    cache = TilesCache(SimpleTile, CheckedPatternElevationUpdater(0.125, 9, 10.0, 20.0), 12)

    regular_tile = cache.get_tile(0.2, 0.6)
    assert cache.tiles_count == 1
    assert regular_tile.minimum_latitude == pytest.approx(0.125, abs=1.0e-10)
    assert regular_tile.minimum_longitude == pytest.approx(0.5, abs=1.0e-10)
    assert regular_tile.latitude_step == pytest.approx(0.015625, abs=1.0e-10)
    assert regular_tile.longitude_step == pytest.approx(0.015625, abs=1.0e-10)
    assert regular_tile.min_elevation == pytest.approx(10.0, abs=1.0e-10)
    assert regular_tile.max_elevation == pytest.approx(20.0, abs=1.0e-10)

    tile_at_end = cache.get_tile(0.234375, 0.609375)
    assert cache.tiles_count == 1
    assert tile_at_end.minimum_latitude == pytest.approx(0.125, abs=1.0e-10)
    assert tile_at_end.minimum_longitude == pytest.approx(0.5, abs=1.0e-10)
    assert tile_at_end.latitude_step == pytest.approx(0.015625, abs=1.0e-10)
    assert tile_at_end.longitude_step == pytest.approx(0.015625, abs=1.0e-10)
    assert tile_at_end.min_elevation == pytest.approx(10.0, abs=1.0e-10)
    assert tile_at_end.max_elevation == pytest.approx(20.0, abs=1.0e-10)


def test_non_contiguous_fill():
    """Test TilesCache filling"""

    cache = TilesCache(SimpleTile, CheckedPatternElevationUpdater(np.radians(1.0), 11, 10.0, 20.0), 16)

    cache.get_tile(float(np.radians(1.5)), float(np.radians(0.5)))
    cache.get_tile(float(np.radians(3.5)), float(np.radians(2.5)))
    cache.get_tile(float(np.radians(2.5)), float(np.radians(3.5)))
    cache.get_tile(float(np.radians(3.5)), float(np.radians(3.5)))
    cache.get_tile(float(np.radians(1.5)), float(np.radians(3.5)))
    cache.get_tile(float(np.radians(1.5)), float(np.radians(1.5)))
    cache.get_tile(float(np.radians(3.5)), float(np.radians(1.5)))
    cache.get_tile(float(np.radians(2.5)), float(np.radians(1.5)))
    cache.get_tile(float(np.radians(0.5)), float(np.radians(3.5)))
    cache.get_tile(float(np.radians(1.5)), float(np.radians(2.5)))
    cache.get_tile(float(np.radians(2.5)), float(np.radians(2.5)))
    cache.get_tile(float(np.radians(0.5)), float(np.radians(2.5)))
    cache.get_tile(float(np.radians(3.5)), float(np.radians(0.5)))
    cache.get_tile(float(np.radians(0.5)), float(np.radians(1.5)))
    cache.get_tile(float(np.radians(2.5)), float(np.radians(0.5)))
    cache.get_tile(float(np.radians(0.5)), float(np.radians(0.5)))
    assert cache.tiles_count == 16

    # Keep using the same tiles for a while
    generator = Well19937a(1234)
    for _index in range(10000):
        lat = 3.0 * generator.nextDouble()
        lon = 4.0 * generator.nextDouble()
        cache.get_tile(float(np.radians(lat)), float(np.radians(lon)))

    assert cache.tiles_count == 16

    cache.get_tile(float(np.radians(-30.5)), float(np.radians(2.5)))

    assert cache.tiles_count == 16
    assert cache.is_tile_in_cache(float(np.radians(-30.5)), float(np.radians(2.5))) is not None


def test_overlapping_tiles():
    """Test TilesCache with 2 overlapping tiles"""
    tile_a = SimpleTile()
    tile_a.set_geometry(0.0, 0.0, 0.1, 0.1, 11, 11)
    tile_a.set_elevation_block(np.ones((11, 11)))

    # second tile has half overlap with previous one
    tile_b = SimpleTile()
    tile_b.set_geometry(0.0, 0.5, 0.1, 0.1, 11, 11)
    tile_b.set_elevation_block(np.ones((11, 11)))

    cache = TilesCache(SimpleTile, CachedElevationUpdater([tile_a, tile_b]), 3)

    # fill the cache
    lattitudes = np.array([0.4, 0.5, 0.6])
    longitudes = np.array([0.3, 0.7, 1.2])
    cache.get_tiles(lattitudes, longitudes)

    # check that overlapped point only appear once in indexes
    tiles, indexes = cache.get_tiles(lattitudes, longitudes)

    assert len(tiles) == 2
    assert len(indexes) == 2
    assert tiles[1].minimum_longitude == tile_a.minimum_longitude
    assert tiles[0].minimum_longitude == tile_b.minimum_longitude
    assert np.all(indexes[1] == [0])
    assert np.all(indexes[0] == [1, 2])
