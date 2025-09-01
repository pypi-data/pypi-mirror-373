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

"""pyrugged Class Dump"""


import json
import math

import numpy as np
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.frames import FactoryManagedFrame
from org.orekit.time import TimeScalesFactory

from pyrugged.errors.pyrugged_exception import PyRuggedError, PyRuggedInternalError
from pyrugged.utils.math_utils import angle  # pylint: disable=no-name-in-module


class DumpedTileData:
    """Local class for handling already dumped tile data."""

    def __init__(self, name, tile, dump_file):
        """Builds a new instance.

        Parameters
        ----------
            name : name of the tile
            tile : tile associated with this dump
            dump_file : file to dumped data
        """

        self._name = name
        self._tile = tile
        self._elevations = {}

        self._dump_file = dump_file

        with open(self._dump_file, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)
            if "DEM Tile" not in data.keys():
                data["DEM Tile"] = []

            tile_dict = {
                "name": name,
                "lat min": tile.minimum_latitude,
                "lat step": tile.latitude_step,
                "lat rows": tile.latitude_rows,
                "lon min": tile.minimum_longitude,
                "lon step": tile.longitude_step,
                "lon cols": tile.longitude_columns,
            }

            data["DEM Tile"].append(tile_dict)
            dfile.seek(0)
            json.dump(data, dfile, indent=4)
            dfile.truncate()

    @property
    def tile(self):
        """Get Tile attribute."""

        return self._tile

    def set_elevation(self, latitude_index, longitude_index, elevation):
        """Set an elevation.

        Parameters
        ----------
            latitude_index : latitude index of the cell
            longitude_index : longitude index of the cell
            elevation : elevation of the cell
        """

        key = latitude_index * self._tile.longitude_columns + longitude_index
        if key not in self._elevations:
            self._elevations[key] = elevation

            with open(self._dump_file, "r+", encoding="utf-8") as dfile:
                data = json.load(dfile)
                if "DEM Cell" not in data.keys():
                    data["DEM Cell"] = {}
                if self._name not in data["DEM Cell"].keys():
                    data["DEM Cell"][self._name] = []

                cell_dict = {
                    "lat index": latitude_index,
                    "lon index": longitude_index,
                    "elevation": elevation,
                }
                data["DEM Cell"][self._name].append(cell_dict)
                dfile.seek(0)
                json.dump(data, dfile, indent=4)
                dfile.truncate()


class DumpedSensorData:
    """Local class for handling already dumped sensor data."""

    def __init__(self, sensor, dump_file):
        """Builds a new instance."""

        self.dump_name = sensor.name
        self.sensor = sensor
        self.los_map = {}
        self.datation = []
        self.rates = []

        self.mean_plane = None
        self.dump_file = dump_file

        with open(self.dump_file, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)
            data["sensor"] = {
                "sensor name": sensor.name,
                "nb pixels": sensor.nb_pixels,
                "position": [sensor.position[0], sensor.position[1], sensor.position[2]],
            }
            dfile.seek(0)
            json.dump(data, dfile, indent=4)
            dfile.truncate()

    def get_dump_name(self):
        """Get dump name attribute."""

        return self.dump_name

    def get_sensor(self):
        """Get sensor attribute."""

        return self.sensor

    def set_mean_plane(self, mean_plane):
        """Set the mean plane finder.

        Parameters
        ----------
            mean_plane : mean plane finder
        """

        if self.mean_plane is None:
            self.mean_plane = mean_plane
            # nb_results = len(mean_plane.cached_results)
            nb_results = sum(result is not None for result in mean_plane.cached_results)

            with open(self.dump_file, "r+", encoding="utf-8") as dfile:
                data = json.load(dfile)
                data["sensor mean plane"] = {
                    "sensor name": self.dump_name,
                    "min line": mean_plane.min_line,
                    "max line": mean_plane.max_line,
                    "max eval": mean_plane.max_eval,
                    "accuracy": mean_plane.accuracy,
                    "normal": [
                        mean_plane.mean_plane_normal.getX(),
                        mean_plane.mean_plane_normal.getY(),
                        mean_plane.mean_plane_normal.getZ(),
                    ],
                    "cached results": nb_results,
                }
                dfile.seek(0)
                json.dump(data, dfile, indent=4)
                dfile.truncate()

            for result in mean_plane.cached_results:
                if result is not None:
                    try:

                        with open(self.dump_file, "r+", encoding="utf-8") as dfile:
                            data = json.load(dfile)
                            data["mean plane cached result"] = {
                                "line number": result.line,
                                "date": self.convert_date(result.getDate()),
                                "target": [
                                    result.target.getX(),
                                    result.target.getY(),
                                    result.target.getZ(),
                                ],
                                "target direction": [
                                    result.target_direction.getX(),
                                    result.target_direction.getY(),
                                    result.target_direction.getZ(),
                                ],
                                "target direction derivative": [
                                    result.target_direction_derivative.getX(),
                                    result.target_direction_derivative.getY(),
                                    result.target_direction_derivative.getZ(),
                                ],
                            }
                            dfile.seek(0)
                            json.dump(data, dfile, indent=4)
                            dfile.truncate()

                    except PyRuggedError as pre:
                        raise PyRuggedInternalError from pre

            # Ensure the transforms for mid date are dumped
            mid_date = self.mean_plane.sensor.get_date(0.5 * (self.mean_plane.min_line + self.mean_plane.max_line))
            self.mean_plane.sc_to_body.get_body_to_inertial(mid_date)
            self.mean_plane.sc_to_body.get_sc_to_inertial(mid_date)

    def set_los(self, date, pixel_number, los):
        """Set a los direction.

        Parameters
        ----------
            date : date
            pixel_number : number of the pixel
            los : line-of-sight direction
        """

        if pixel_number not in self.los_map:
            self.los_map[pixel_number] = []

        pairs_list = self.los_map[pixel_number]

        for already_dumped in pairs_list:
            if math.fabs(date.durationFrom(already_dumped[0])) < 1.0e-12 and angle(los, already_dumped[1]) < 1.0e-12:
                return

        pairs_list.append([date, los])
        with open(self.dump_file, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)
            data["sensor LOS"] = {
                "sensor name": self.dump_name,
                "date": self.convert_date(date),
                "pixel number": pixel_number,
                "los": [los[0], los[1], los[2]],
            }
            dfile.seek(0)
            json.dump(data, dfile, indent=4)
            dfile.truncate()

    def set_datation(self, line_number, date):
        """Set a datation pair.

        Parameters
        ----------
            line_number : line number
            date : date
        """

        for already_dumped in self.datation:
            if (
                math.fabs(date.durationFrom(already_dumped[1])) < 1.0e-12
                and math.fabs(line_number - already_dumped[0]) < 1.0e-12
            ):
                return

        with open(self.dump_file, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)
            data["sensor datation"] = {
                "sensor name": self.dump_name,
                "line number": line_number,
                "date": self.convert_date(date),
            }
            dfile.seek(0)
            json.dump(data, dfile, indent=4)
            dfile.truncate()

    def set_rate(self, line_number, rate):
        """Set a rate.

        Parameters
        ----------
            line_number : line number
            rate : lines rate
        """

        for already_dumped in self.rates:
            if math.fabs(rate - already_dumped[1]) < 1.0e-12 and math.fabs(line_number - already_dumped[0]) < 1.0e-12:
                return

        self.rates.append([line_number, rate])
        with open(self.dump_file, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)
            data["sensor rate"] = {"sensor name": self.dump_name, "line number": line_number, "rate": rate}
            dfile.seek(0)
            json.dump(data, dfile, indent=4)
            dfile.truncate()

    def convert_date(self, date):
        """Convert a date to string with high accuracy.

        Parameters
        ----------
            date : computation date

        Returns
        -------
            result : converted date
        """

        date_components = date.getComponents(TimeScalesFactory.getUTC())
        return (
            f'{date_components.getDate().getYear()}{"-"}'
            f'{date_components.getDate().getMonth()}{"-"}'
            f'{date_components.getDate().getDay()}{"T"}'
            f'{date_components.getTime().getHour()}{":"}'
            f'{date_components.getTime().getMinute()}{":"}'
            f'{date_components.getTime().getSecond()}{"Z"}'
        )


class Dump:
    """Dump data class."""

    def __init__(self, dump_file):
        """Builds new instance.

        Parameters
        ----------
            dump_file : pathlib.Path(<user_dump_file_path>).open("a")
                Dump file (text file)
        """

        self.dump_file = dump_file
        self.tiles = []
        self.sensors = []
        self.algorithm_dumped = False
        self.ellipsoid_dumped = False
        self.transforms_dumped = None

        self.dump_header()

    def dump_header(self):
        """Dump header."""

        with open(self.dump_file, "w", encoding="utf-8") as dfile:
            json.dump(
                {
                    "header": f'{"PyRugged library dump file"}',
                    "units": f'{"All units are SI units (m, m/s, rad, ...)"}',
                },
                dfile,
                indent=4,
            )

    def dump_tile_cell(self, tile, latitude_index, longitude_index, elevation):
        """Dump some context data.

        Parameters
        ----------
            tile : tile to which the cell belongs
            latitude_index : latitude index of the cell
            longitude_index : longitude index of the cell
            elevation : elevation of the cell
        """
        self.get_tile_data(tile).set_elevation(latitude_index, longitude_index, elevation)

    def dump_algorithm(self, algorithm_id, specific=None):
        """Dump algorithm data.

        Parameters
        ----------
            algorithm_id : Algorithm Identifier
            specific : algorithm specific extra data
        """

        if not self.algorithm_dumped:
            if specific is None:
                with open(self.dump_file, "r+", encoding="utf-8") as dfile:
                    data = json.load(dfile)
                    data["algorithm"] = str(algorithm_id)
                    dfile.seek(0)
                    json.dump(data, dfile, indent=4)
                    dfile.truncate()

            else:
                with open(self.dump_file, "r+", encoding="utf-8") as dfile:
                    data = json.load(dfile)
                    data["algorithm"] = {"name": str(algorithm_id), "elevation": specific}
                    dfile.seek(0)
                    json.dump(data, dfile, indent=4)
                    dfile.truncate()

            self.algorithm_dumped = True

    def dump_ellipsoid(self, ellipsoid):
        """Dump ellipsoid data.

        Parameters
        ----------
            ellipsoid : ellipsoid to dump
        """

        if not self.ellipsoid_dumped:
            with open(self.dump_file, "r+", encoding="utf-8") as dfile:
                data = json.load(dfile)
                data["ellipsoid"] = {
                    "ae": ellipsoid.a_val,
                    "f": ellipsoid.flattening,
                    "frame": str(ellipsoid.body_frame),
                }
                dfile.seek(0)
                json.dump(data, dfile, indent=4)
                dfile.truncate()

            self.ellipsoid_dumped = True

    def dump_direct_location(
        self,
        date,
        sensor_position,
        los,
        light_time_correction,
        aberration_of_light_correction,
        refraction_correction,
    ):
        """Dump a direct location computation.

        Parameters
        ----------
            date : date of the location
            sensor_position : sensor position in spacecraft frame
            los : normalized line-of-sight in spacecraft frame
            light_time_correction : flag for light time correction
            aberration_of_light_correction : flag for aberration of light correction
            refraction_correction : flag for refraction correction
        """

        if isinstance(los, Vector3D):
            los = np.array(los.toArray())

        with open(self.dump_file, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)

            if "Direct location" not in data.keys():
                data["Direct location"] = []

            data["Direct location"].append(
                {
                    "date": self.convert_date(date),
                    "position": [sensor_position[0], sensor_position[1], sensor_position[2]],
                    "los": [los[0], los[1], los[2]],
                    "light_time": light_time_correction,
                    "aberration": aberration_of_light_correction,
                    "refraction": refraction_correction,
                }
            )
            dfile.seek(0)
            json.dump(data, dfile, indent=4)
            dfile.truncate()

    def dump_direct_location_result(self, dir_loc):
        """Dump a direct location result.

        Parameters
        ----------
            dir_loc : resulting geodetic point
        """

        if dir_loc is not None:
            direct_location_result = {
                "latitude": dir_loc[1],
                "longitude": dir_loc[0],
                "elevation": dir_loc[2],
            }

        else:
            direct_location_result = None

        with open(self.dump_file, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)

            if "Direct location result" not in data.keys():
                data["Direct location result"] = []

            data["Direct location result"].append(direct_location_result)
            dfile.seek(0)
            json.dump(data, dfile, indent=4)
            dfile.truncate()

    def dump_inverse_location(
        self,
        sensor,
        point,
        min_line,
        max_line,
        light_time_correction,
        aberration_of_light_correction,
        refraction_correction,
    ):
        """Dump an inverse location computation.

        Parameters
        ----------
            sensor : sensor
            point : point to localize
            min_line : minimum line number
            max_line : maximum line number
            light_time_correction : flag for light time correction
            aberration_of_light_correction : flag for aberration of light correction
            refraction_correction : flag for refraction correction
        """

        sensor_data = self.get_sensor_data(sensor)

        with open(self.dump_file, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)

            if "Inverse location" not in data.keys():
                data["Inverse location"] = []

            data["Inverse location"].append(
                {
                    "sensor name": sensor_data.get_dump_name(),
                    "latitude": point[0],
                    "longitude": point[1],
                    "elevation": point[2],
                    "min_line": min_line,
                    "max_line": max_line,
                    "light time": light_time_correction,
                    "aberration": aberration_of_light_correction,
                    "refraction": refraction_correction,
                }
            )
            dfile.seek(0)
            json.dump(data, dfile, indent=4)
            dfile.truncate()

    def dump_inverse_location_result(self, pixel):
        """Dump an inverse location result.

        Parameters
        ----------
            pixel : resulting sensor pixel
        """

        if pixel is not None:
            inverse_location_result = {"line number": pixel[0], "pixel number": pixel[1]}

        else:
            inverse_location_result = None

        with open(self.dump_file, "r+", encoding="utf-8") as dfile:
            data = json.load(dfile)

            if "Inverse location result" not in data.keys():
                data["Inverse location result"] = []

            data["Inverse location result"].append(inverse_location_result)
            dfile.seek(0)
            json.dump(data, dfile, indent=4)
            dfile.truncate()

    def dump_transform(
        self,
        sc_to_body,
        index,
        body_to_inertial,
        sc_to_inertial,
    ):
        """Dump an observation transform.

        Parameters
        ----------
            sc_to_body : provider for observation
            index : index of the transform
            body_to_inertial : transform from body frame to inertial frame
            sc_to_inertial : transfrom from spacecraft frame to inertial frame
        """

        if self.transforms_dumped is None:
            min_date = sc_to_body.min_date
            max_date = sc_to_body.max_date
            t_step = sc_to_body.t_step
            tolerance = sc_to_body.overshoot_tolerance
            n_val = int(math.ceil(max_date.durationFrom(min_date) / t_step))

            with open(self.dump_file, "r+", encoding="utf-8") as dfile:
                data = json.load(dfile)
                data["span"] = {
                    "min date": self.convert_date(min_date),
                    "max date": self.convert_date(max_date),
                    "t_step": t_step,
                    "tolerance": tolerance,
                    "inertial frame": self.get_key_or_name(sc_to_body.inertial_frame),
                }
                dfile.seek(0)
                json.dump(data, dfile, indent=4)
                dfile.truncate()

            self.transforms_dumped = [False] * n_val

        if not self.transforms_dumped[index]:
            body_rotation = self.convert_rotation(
                body_to_inertial.getRotation(),
                body_to_inertial.getRotationRate(),
                body_to_inertial.getRotationAcceleration(),
            )
            spacecraft_translation = self.convert_translation(
                sc_to_inertial.getTranslation(), sc_to_inertial.getVelocity(), sc_to_inertial.getAcceleration()
            )
            spacecraft_rotation = self.convert_rotation(
                sc_to_inertial.getRotation(), sc_to_inertial.getRotationRate(), sc_to_inertial.getRotationAcceleration()
            )

            with open(self.dump_file, "r+", encoding="utf-8") as dfile:
                data = json.load(dfile)
                data["transform"] = {
                    "index": index,
                    "body": body_rotation,
                    "spacecraft": [spacecraft_translation, spacecraft_rotation],
                }
                dfile.seek(0)
                json.dump(data, dfile, indent=4)
                dfile.truncate()

            self.transforms_dumped[index] = True

    def dump_sensor_mean_plane(self, mean_plane):
        """Dump a sensor mean plane.

        Parameters
        ----------
            mean_plane : mean plane associated with sensor
        """

        self.get_sensor_data(mean_plane.sensor).set_mean_plane(mean_plane)

    def dump_sensor_los(self, sensor, date, i: int, los):
        """Dump a sensor LOS.

        Parameters
        ----------
            sensor : sensor
            date : date
            i : pixel index
            los : pixel normalized line-of-sight
        """

        self.get_sensor_data(sensor).set_los(date, i, los)

    def dump_sensor_datation(self, sensor, line_number: float, date):
        """Dump a sensor datation.

        Parameters
        ----------
            sensor : sensor
            line_number : line Number
            date : date
        """

        self.get_sensor_data(sensor).set_datation(line_number, date)

    def dump_sensor_rate(self, sensor, line_number: float, rate: float):
        """Dump a sensor rate.

        Parameters
        ----------
            sensor : sensor
            line_number : line Number
            rate : rate
        """

        self.get_sensor_data(sensor).set_rate(line_number, rate)

    def get_key_or_name(self, frame):
        """Get a frame key or name.

        Parameters
        ----------
            frame : frame to convert

        Returns
        -------
            res : frame key or frame name

        """

        if isinstance(frame, FactoryManagedFrame):
            res = frame.getFactoryKey().toString()
        else:
            res = frame.getName()

        return res

    def get_tile_data(self, tile) -> DumpedTileData:
        """Get tile data.

        Parameters
        ----------
            tile : tile to which the cell belongs

        Returns
        -------
            result : index of the tile
        """

        for dumped_tile_data in self.tiles:
            if tile == dumped_tile_data.tile:
                return dumped_tile_data

        dumped_tile_data = DumpedTileData(f'{"t"}{len(self.tiles)}', tile, self.dump_file)
        self.tiles.append(dumped_tile_data)

        dumped_tile_data.set_elevation(
            tile.min_elevation_latitude_index,
            tile.min_elevation_longitude_index,
            tile.min_elevation,
        )
        dumped_tile_data.set_elevation(
            tile.max_elevation_latitude_index,
            tile.max_elevation_longitude_index,
            tile.max_elevation,
        )

        return dumped_tile_data

    def get_sensor_data(self, sensor):
        """Get sensor data.

        Parameters
        ----------
            sensor : sensor

        Returns
        -------
            result : dumped sensor data
        """

        for dumped_sensor_data in self.sensors:
            if sensor == dumped_sensor_data.get_sensor():
                return dumped_sensor_data

        dumped_sensor_data = DumpedSensorData(sensor, self.dump_file)
        self.sensors.append(dumped_sensor_data)

        return dumped_sensor_data

    def convert_date(self, date):
        """Convert a date to string with high accuracy.

        Parameters
        ----------
            date : computation date

        Returns
        -------
            result : converted date
        """

        date_components = date.getComponents(TimeScalesFactory.getUTC())
        return (
            f'{date_components.getDate().getYear()}{"-"}'
            f'{date_components.getDate().getMonth()}{"-"}'
            f'{date_components.getDate().getDay()}{"T"}'
            f'{date_components.getTime().getHour()}{":"}'
            f'{date_components.getTime().getMinute()}{":"}'
            f'{date_components.getTime().getSecond()}{"Z"}'
        )

    def convert_translation(self, translation, velocity, acceleration):
        """Convert a translation to string.

        Parameters
        ----------
            translation : translation vector
            velocity : linear velocity
            acceleration : linear acceleration

        Returns
        -------
            result : converted rotation
        """

        return {
            "translation": {
                "position": [translation.getX(), translation.getY(), translation.getZ()],
                "velocity": [velocity.getX(), velocity.getY(), velocity.getZ()],
                "acceleration": [acceleration.getX(), acceleration.getY(), acceleration.getZ()],
            }
        }

    def convert_rotation(self, rotation, rate, acceleration):
        """Convert a rotation to string.

        Parameters
        ----------
            rotation : rotation
            rate : rate of the rotation
            acceleration : angular acceleration

        Returns
        -------
            result : converted rotation
        """

        return {
            "rotation": {
                "rotation": [rotation.getQ0(), rotation.getQ1(), rotation.getQ2(), rotation.getQ3()],
                "rate": [rate.getX(), rate.getY(), rate.getZ()],
                "acceleration": [acceleration.getX(), acceleration.getY(), acceleration.getZ()],
            }
        }
