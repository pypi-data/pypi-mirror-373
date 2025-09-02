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

"""pyrugged Class PyRuggedMessages"""

import enum


class PyRuggedMessages(enum.Enum):
    """Error Messages for PyRuggedError Class"""

    INTERNAL_ERROR = "internal error, please notify development team by creating an issue at {0}"
    OUT_OF_TILE_INDICES = "no data at indices [{0}, {1}], tile only covers from [0, 0] to [{2}, {3}] (inclusive)"
    OUT_OF_TILE_ANGLES = (
        "no data at latitude {0} and longitude {1}, tile covers only latitudes {2} to {3} and longitudes {4} to {5}"
    )
    NO_DEM_DATA = "no Digital Elevation Model data at latitude {0} and longitude {1}"
    TILE_WITHOUT_REQUIRED_NEIGHBORS_SELECTED = (
        "the tile selected for latitude {0} and longitude {1} does not contain required point neighborhood"
    )
    OUT_OF_TIME_RANGE = "date {0} is out of time span [{1}, {2}] (UTC)"
    UNINITIALIZED_CONTEXT = "general context has not been initialized (missing call to {0})"
    INTERSECTION_ALGORITHM_ERROR = "Algorithm Id error {0}"
    EMPTY_TILE = "tile is empty: {0} ⨉ {1}"
    UNKNOWN_SENSOR = "unknown sensor {0}"
    NO_INERTIAL_FRAME_FOR_SAR_SENSOR = "No transform from or to inertial frame available for SAR because not needed"
    DEFAULT_SENSOR = "can't use default sensor"
    LINE_OF_SIGHT_DOES_NOT_REACH_GROUND = "line-of-sight does not reach ground"
    LINE_OF_SIGHT_NEVER_CROSSES_LATITUDE = "line-of-sight never crosses latitude {0}"
    LINE_OF_SIGHT_NEVER_CROSSES_LONGITUDE = "line-of-sight never crosses longitude {0}"
    LINE_OF_SIGHT_NEVER_CROSSES_ALTITUDE = "line-of-sight never crosses altitude {0}"
    SAR_AIMING_CIRCLE_NEVER_CROSSES_LATITUDE = "SAR aiming circle never crosses latitude {0}"
    SAR_AIMING_CIRCLE_NEVER_CROSSES_LONGITUDE = "SAR aiming circle never crosses longitude {0}"
    SAR_AIMING_CIRCLE_NEVER_CROSSES_ALTITUDE = "SAR aiming circle never crosses altitude {0}"
    SAR_LOCATION_ALGORITH_ALLOWED = "For SAR location, ConstantElevationAlgorithm or DEMIgnoreAlgorithm must be used"
    SAR_NOT_ENOUGH_PIXEL_LINE_VALUES_FOR_CUBIC_INTERP = (
        "Not enough pixels, lines and range values for cubic interpolation, 4 lines and 4 pixels at least needed"
    )
    DEM_ENTRY_POINT_IS_BEHIND_SPACECRAFT = "line-of-sight enters the Digital Elevation Model behind spacecraft!"
    FRAMES_MISMATCH_WITH_INTERPOLATOR_DUMP = "frame {0} does not match frame {1} from interpolator dump"
    NOT_INTERPOLATOR_DUMP_DATA = "data is not an interpolator dump"
    DEBUG_DUMP_ALREADY_ACTIVE = "debug dump is already active for this thread"
    DEBUG_DUMP_ACTIVATION_ERROR = "unable to active debug dump with file {0}: {1}"
    DEBUG_DUMP_NOT_ACTIVE = "debug dump is not active for this thread"
    CANNOT_PARSE_LINE = "cannot parse line {0}, file {1}: {2}"
    LIGHT_TIME_CORRECTION_REDEFINED = "light time correction redefined, line {0}, file {1}: {2}"
    ABERRATION_OF_LIGHT_CORRECTION_REDEFINED = "aberration of light correction redefined, line {0}, file {1}: {2}"
    ATMOSPHERIC_REFRACTION_REDEFINED = "atmospheric refraction correction redefined, line {0}, file {1}: {2}"
    TILE_ALREADY_DEFINED = "tile {0} already defined, line {1}, file {2}: {3}"
    UNKNOWN_TILE = "unknown tile {0}, line {1}, file {2}: {3}"
    NO_PARAMETERS_SELECTED = "no parameters have been selected for estimation"
    NO_REFERENCE_MAPPINGS = "no reference mappings for parameters estimation"
    DUPLICATED_PARAMETER_NAME = "a different parameter with name {0} already exists"
    INVALID_RUGGED_NAME = "invalid rugged name"
    UNSUPPORTED_REFINING_CONTEXT = "refining using {0} rugged instance is not handled"
    NO_LAYER_DATA = "no atmospheric layer data at altitude {0} (lowest altitude: {1})"
    INVALID_STEP = "step {0} is not valid : {1}"
    INVALID_RANGE_FOR_LINES = "range between min line {0} and max line {1} is invalid {2}"
    SENSOR_PIXEL_NOT_FOUND_IN_RANGE_LINES = (
        "impossible to find sensor pixel in given range lines (with atmospheric refraction) between lines {0} and {1}"
    )
    SENSOR_PIXEL_NOT_FOUND_IN_PIXELS_LINE = (
        "impossible to find sensor pixel: pixel {0:.2f} outside interval "
        "[ {1} , {2} [ (with atmospheric refraction margin = {3})"
    )
    TRANSFORM_FROM_FRAME_NOT_ALLOWED = "transform_from_frame is only allowed with Geodetic point argument"
