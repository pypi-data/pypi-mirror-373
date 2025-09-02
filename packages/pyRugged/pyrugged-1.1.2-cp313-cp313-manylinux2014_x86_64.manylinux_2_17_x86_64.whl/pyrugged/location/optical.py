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
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""optical location"""

import math
from typing import List, NamedTuple, Tuple, Union

# pylint: disable=too-many-locals, too-many-lines, too-many-public-methods, too-many-arguments, too-many-function-args
import numpy as np
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.frames import StaticTransform, Transform
from org.orekit.time import AbsoluteDate
from org.orekit.utils import PVCoordinates

from pyrugged.bodies.extended_ellipsoid import ExtendedEllipsoid
from pyrugged.errors import dump_manager
from pyrugged.errors.pyrugged_exception import PyRuggedError, PyRuggedInternalError
from pyrugged.errors.pyrugged_messages import PyRuggedMessages
from pyrugged.intersection.algorithm_id import AlgorithmId
from pyrugged.intersection.basic_scan_algorithm import BasicScanAlgorithm
from pyrugged.intersection.constant_elevation_algorithm import ConstantElevationAlgorithm
from pyrugged.intersection.duvenhage.duvenhage_algorithm import DuvenhageAlgorithm
from pyrugged.intersection.ignore_dem_algorithm import IgnoreDEMAlgorithm
from pyrugged.line_sensor.line_sensor import LineSensor
from pyrugged.line_sensor.sensor_mean_plane_crossing import SensorMeanPlaneCrossing
from pyrugged.line_sensor.sensor_pixel_crossing import SensorPixelCrossing
from pyrugged.los.transform import DynamicTransform, get_corresponding_orekit_transform, transform_to_numpy
from pyrugged.model.pyrugged import PyRugged
from pyrugged.refraction.atmospheric_refraction import AtmosphericRefraction
from pyrugged.utils.constants import Constants
from pyrugged.utils.math_utils import (  # pylint: disable=no-name-in-module
    compute_linear_combination_2,
    compute_linear_combination_2_arr,
    distance,
    dot,
    dot_n,
    find_fixed_line_func,
    find_fixed_pixel_func,
    get_norm_sq,
    get_norm_sq_n,
    to_array,
    to_array_v,
)
from pyrugged.utils.spacecraft_to_observed_body import SpacecraftToObservedBody


class CorrectionsParams(NamedTuple):
    """
    Correction parameters name tuple definition
    """

    light_time: bool
    aberration_light: bool
    atmospheric_refraction: AtmosphericRefraction


DEFAULT_CORRECTIONS_PARAMS = CorrectionsParams(False, False, None)


class OpticalLocation:
    """Optical Localisation functions."""

    # Accuracy to use in the first stage of inverse location.
    # This accuracy is only used to locate the point within one
    # pixel, hence there is no point in choosing a too small value here.
    COARSE_INVERSE_LOCATION_ACCURACY = 0.01

    # Maximum number of evaluations for crossing algorithms.
    MAX_EVAL = 50

    # Threshold for pixel convergence in fixed point method
    # (for inverse location with atmospheric refraction correction).
    PIXEL_CV_THRESHOLD = 1.0e-4

    # Threshold for line convergence in fixed point method
    # (for inverse location with atmospheric refraction correction).
    LINE_CV_THRESHOLD = 1.0e-4

    def __init__(
        self,
        rugged: PyRugged,
        algorithm: Union[BasicScanAlgorithm, ConstantElevationAlgorithm, IgnoreDEMAlgorithm, DuvenhageAlgorithm],
        corrections_params: CorrectionsParams = DEFAULT_CORRECTIONS_PARAMS,
    ):
        """Builds a new instance.

        By default, the instance performs both light time correction (which refers to ground point motion with
        respect to inertial frame) and aberration of light correction (which refers to spacecraft proper velocity).
        Explicit calls to set_light_time_correction and set_aberration_of_light_correction
        can be made after construction if these phenomena should not be corrected.

        Parameters
        ----------
            rugged : Pyrugged instance
            algorithm : algorithm to use for Digital Elevation Model intersection
            correction_params : corrections parameters (activation status and parameters including the aberration light
                 correction,the light time correction, and with atmospheric correction.
                A CorrectionsParams named tuple has to be instantiate and given as argument.
                >>> from pyrugged.location.optical import CorrectionsParams
                >>> correction_params = CorrectionsParams(False, False, None)
                or
                >>> correction_params = CorrectionsParams(False, False, MultiLayerModel(pyrugged_builder.ellipsoid))
                individual fields are accessed with the following command lines:
                >>> correction_params.aberration_light
                >>> correction_params.light_time
                >>> correction_params.atmospheric_refraction
        """

        # Orbit/attitude to body converter
        self._rugged = rugged

        # Intersection algorithm
        self._algorithm = algorithm

        # finders (mean plane crossing for inverse location)
        self._finders = {}

        # correction parameters
        self._corrections_params = corrections_params

    @property
    def rugged(self) -> PyRugged:
        """Get rugged instance."""

        return self._rugged

    @property
    def ellipsoid(self) -> ExtendedEllipsoid:
        """Get the observed body ellipsoid."""

        return self.rugged.ellipsoid

    @property
    def algorithm(
        self,
    ) -> Union[BasicScanAlgorithm, ConstantElevationAlgorithm, IgnoreDEMAlgorithm, DuvenhageAlgorithm]:
        """Get the DEM intersection algorithm."""

        return self._algorithm

    @algorithm.setter
    def algorithm(
        self, algorithm=Union[BasicScanAlgorithm, ConstantElevationAlgorithm, IgnoreDEMAlgorithm, DuvenhageAlgorithm]
    ):
        """Set the DEM intersection algorithm."""

        self._algorithm = algorithm

    @property
    def algorithm_id(self) -> AlgorithmId:
        """Get the DEM intersection algorithm identifier."""

        return self.algorithm.algorithm_id

    @property
    def light_time_correction(self) -> bool:
        """Get flag for light time correction."""

        return self._corrections_params.light_time

    @property
    def corrections_params(self) -> CorrectionsParams:
        """Get corections params."""

        return self._corrections_params

    @corrections_params.setter
    def corrections_params(self, corrections_params: CorrectionsParams):
        """Set corrections params."""

        self._corrections_params = corrections_params

    @property
    def aberration_of_light_correction(self) -> bool:
        """Get flag for aberration of light correction."""

        return self._corrections_params.aberration_light

    @property
    def atmospheric_refraction(self) -> AtmosphericRefraction:
        """Get the atmospheric refraction model."""

        return self._corrections_params.atmospheric_refraction

    def direct_location_of_sensor_line(
        self, line_number: float, sensor_name: str = None, alt: float = None
    ) -> List[Tuple]:
        """Direct location of a sensor line.

        Parameters
        ----------
            sensor_name : name of the line sensor, if None default line sensor is used
            line_number : number of the line to localize on ground
            alt : altitude at wich the intersection occurs

        Returns
        -------
            result : ground position of all pixels of the specified sensor line
        """

        sensor = self.rugged.get_sensor(sensor_name)
        sensor_name = sensor.name
        sensor_position = sensor.position
        date = sensor.get_date(line_number)

        # Compute the transform for the date
        # from spacecraft to inertial
        sc_to_inert = self.rugged.sc_to_body.get_sc_to_inertial(date)
        # from inertial to body
        inert_to_body = self.rugged.sc_to_body.get_inertial_to_body(date)

        # Compute spacecraft velocity in inertial frame
        spacecraft_velocity = sc_to_inert.transformPVCoordinates(PVCoordinates.ZERO).getVelocity()
        # Compute sensor position in inertial frame
        # TBN : for simplicity, due to the size of sensor, we consider each pixel to be at sensor position
        p_inert = StaticTransform.cast_(sc_to_inert).transformPosition(Vector3D(sensor_position.tolist()))

        # Compute location of each pixel
        gp_list = [None] * sensor.nb_pixels
        dates = [date] * sensor.nb_pixels
        los = sensor.get_los_arr(dates, list(range(sensor.nb_pixels)))

        for index, _ in enumerate(gp_list):
            if dump_manager.DUMP_VAR is not None:
                dump_manager.DUMP_VAR.dump_direct_location(
                    date,
                    sensor_position,
                    los[index],
                    self.light_time_correction,
                    self.aberration_of_light_correction,
                    self.atmospheric_refraction is not None,
                )

            # Compute the line of sight in inertial frame (without correction)
            obs_l_inert = StaticTransform.cast_(sc_to_inert).transformVector(Vector3D(los[index].tolist()))

            result = self.direct_location_inert(inert_to_body, spacecraft_velocity, p_inert, obs_l_inert, alt)

            if dump_manager.DUMP_VAR is not None:
                dump_manager.DUMP_VAR.dump_direct_location_result(result)

            gp_list[index] = result

        return gp_list

    def direct_location(self, lines: List, pixels: List, altitudes: List = None, sensor_name=None) -> Tuple:
        """Direct location lines and pixels.

        Parameters
        ----------
            sensor_name : the sensor name
            lines : list of lines index
            pixels : list of pixels index
            altitudes : altitudes at wich the intersection occurs
        Returns
        -------
            longitudes, latitudes, altitudes : ground position of intersection point with ground,
                which can be None if errors
        """

        line_sensor = self.rugged.get_sensor(sensor_name)
        position = line_sensor.position

        # for i in range(len(lines)):  # noqa: B905
        #     point_lon, point_lat, point_alt = self.direct_location_of_los(dates[i], position, pixels_los[i])
        #     longitudes.append(point_lon)
        #     latitudes.append(point_lat)
        #     altitudes.append(point_alt)

        if altitudes is not None:
            if isinstance(altitudes, (list, np.ndarray)):
                altitudes = np.array(altitudes)
            else:
                altitudes = np.array([altitudes])

            if 1 < np.size(altitudes) < min(np.size(pixels), np.size(lines)):
                raise RuntimeError("len(altitudes) must be at least equals to min(len(pixels),len(lines))")
            if np.size(altitudes) > max(np.size(pixels), np.size(lines)):
                raise RuntimeError("len(altitudes) must not exceed max(len(pixels),len(lines))")

        if len(pixels) > 1:
            dates = line_sensor.get_date(np.array(lines))
            pixels_los = line_sensor.get_interpolated_los_arr(dates, pixels)
            longitudes, latitudes, altitudes = self.direct_location_of_los_vec(
                dates, position, np.array(pixels_los), altitudes
            )

            return longitudes, latitudes, altitudes

        # else:  # one point to locate
        longitudes_res = []
        latitudes_res = []
        altitudes_res = []
        dates = line_sensor.get_date(float(lines[0]))
        pixels_los = line_sensor.get_interpolated_los_arr(dates, pixels)
        if altitudes is not None:
            point_lon, point_lat, point_alt = self.direct_location_of_los(dates, position, pixels_los[0], altitudes[0])
        else:
            point_lon, point_lat, point_alt = self.direct_location_of_los(dates, position, pixels_los[0])

        longitudes_res.append(point_lon)
        latitudes_res.append(point_lat)
        altitudes_res.append(point_alt)

        return longitudes_res, latitudes_res, altitudes_res

    def direct_location_of_los(
        self, date: AbsoluteDate, sensor_position: np.ndarray, los: np.ndarray, altitude: float = None
    ) -> Tuple:
        """Direct location of a single line-of-sight.

        Parameters
        ----------
            date : date of the location
            sensor_position : sensor position in spacecraft frame. For simplicity, due to the size of sensor,
                we consider each pixel to be at sensor position
            los : normalized line-of-sight in spacecraft frame
            altitude : altitude at wich the intersection occurs
        Returns
        -------
            result : ground position (longitude, latitude, altitude)
                of intersection point between specified los and ground (Tuple of None if error)
        """

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_direct_location(
                date,
                sensor_position,
                los,
                self.light_time_correction,
                self.aberration_of_light_correction,
                self.atmospheric_refraction is not None,
            )

        # Compute the transforms for the date
        # from spacecraft to inertial
        sc_to_inert = self.rugged.sc_to_body.get_sc_to_inertial(date)
        # from inertial to body
        inert_to_body = self.rugged.sc_to_body.get_inertial_to_body(date)

        # Compute spacecraft velocity in inertial frame
        spacecraft_velocity = sc_to_inert.transformPVCoordinates(PVCoordinates.ZERO).getVelocity()
        # Compute sensor position in inertial frame
        # TBN : for simplicity, due to the size of sensor, we consider each pixel to be at sensor position
        p_inert = StaticTransform.cast_(sc_to_inert).transformPosition(Vector3D(sensor_position.tolist()))

        # Compute the line-of-sight in inertial frame (without correction)
        obs_l_inert = StaticTransform.cast_(sc_to_inert).transformVector(Vector3D(los.tolist()))

        result = self.direct_location_inert(inert_to_body, spacecraft_velocity, p_inert, obs_l_inert, altitude)

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_direct_location_result(result)

        return result

    def direct_location_of_los_vec(
        self,
        dates: List[AbsoluteDate],
        sensor_position: np.ndarray,
        los: np.ndarray,
        altitudes: np.ndarray = None,
    ) -> Tuple:
        """Direct location of all line-of-sights.

        Parameters
        ----------
            dates : dates of the locations
            sensor_position : sensor position in spacecraft frame. For simplicity, due to the size of sensor,
                we consider each pixel to be at sensor position
            los : normalized line-of-sights in spacecraft frame
            altitudes : altitudes at wich the intersection occurs
        Returns
        -------
            result : ground positions (longitude, latitude, altitude)
                of intersection points between specified los and ground (Tuple of None if error)
        """

        if dump_manager.DUMP_VAR is not None:
            for index, date in enumerate(dates):
                dump_manager.DUMP_VAR.dump_direct_location(
                    date,
                    sensor_position,
                    los[index],
                    self.light_time_correction,
                    self.aberration_of_light_correction,
                    self.atmospheric_refraction is not None,
                )

        # Compute the transforms for the date
        # from spacecraft to inertial
        sc_to_inert = self.rugged.sc_to_body.get_sc_to_inertial(dates)
        # from inertial to body
        inert_to_body = self.rugged.sc_to_body.get_inertial_to_body(dates)

        # Compute spacecraft velocity in inertial frame
        spacecraft_velocity = [
            sc_to_inert_i.transformPVCoordinates(PVCoordinates.ZERO).getVelocity() for sc_to_inert_i in sc_to_inert
        ]
        # Compute sensor position in inertial frame
        # TBN : for simplicity, due to the size of sensor, we consider each pixel to be at sensor position
        p_inert = [
            StaticTransform.cast_(sc_to_inert_i).transformPosition(Vector3D(sensor_position.tolist()))
            for sc_to_inert_i in sc_to_inert
        ]

        # Compute the line-of-sight in inertial frame (without correction)
        obs_l_inert = [
            StaticTransform.cast_(sc_to_inert_i).transformVector(Vector3D(los[index].tolist()))
            for index, sc_to_inert_i in enumerate(sc_to_inert)
        ]

        result = self.direct_location_inert_vec(inert_to_body, spacecraft_velocity, p_inert, obs_l_inert, altitudes)

        if dump_manager.DUMP_VAR is not None:
            for res in result:
                dump_manager.DUMP_VAR.dump_direct_location_result(res)

        return result

    def direct_location_inert(
        self,
        inert_to_body: Transform,
        spacecraft_velocity: Vector3D,
        pos_inert: Vector3D,
        los_inert: Vector3D,
        altitude: float = None,
    ) -> Tuple:
        """Direct location with effect correction in inertial frame.

        Parameters
        ----------
            inert_to_body : inertial to body transform
            spacecraft_velocity : spacecraft velocity vector
            pos_inert : spacecraft position in inertial frame
            los_inert : los vector in inertial frame
            altitude : altitudes at wich the intersection occurs
        Returns
        -------
            result : ground position (longitude, latitude, altitude)
                of intersection point between specified los and ground
        """

        # from inertial to body
        shifted_inert_to_body = inert_to_body

        if self.aberration_of_light_correction:
            # Apply aberration of light correction on LOS
            los_inert = Vector3D(self.apply_aberration_of_light_correction(los_inert, spacecraft_velocity).tolist())

        # Compute ground location of specified pixel according to light time correction flag
        if self.light_time_correction:
            # Compute DEM intersection with light time correction
            # TBN: for simplicity, due to the size of sensor, we consider each pixel to be at sensor position

            shifted_inert_to_body = self.apply_light_time_correction(inert_to_body, pos_inert, los_inert, altitude)

        # Compute DEM intersection without light time correction
        p_body = StaticTransform.cast_(shifted_inert_to_body).transformPosition(pos_inert)
        l_body = StaticTransform.cast_(shifted_inert_to_body).transformVector(los_inert)
        p_bodyp = to_array(p_body.getX(), p_body.getY(), p_body.getZ())
        l_bodyp = to_array(l_body.getX(), l_body.getY(), l_body.getZ())

        if self.algorithm.__class__.__name__ == "ConstantElevationAlgorithm":
            raw_point_gp = self.algorithm.intersection(self.ellipsoid, p_bodyp, l_bodyp, altitude)
        else:
            raw_point_gp = self.algorithm.intersection(self.ellipsoid, p_bodyp, l_bodyp)

        point_gp = self.algorithm.refine_intersection(
            self.ellipsoid,
            p_bodyp,
            l_bodyp,
            raw_point_gp,
        )

        # Compute ground location of specified pixel according to atmospheric refraction correction flag
        result = point_gp

        # Compute the ground location with atmospheric correction if asked for
        if self.atmospheric_refraction is not None and self.atmospheric_refraction.must_be_computed:
            result = self.atmospheric_refraction.apply_correction(p_bodyp, l_bodyp, point_gp, self.algorithm)

        return result[1], result[0], result[2]

    def direct_location_inert_vec(
        self,
        inert_to_body: List[Transform],
        spacecraft_velocity: List[Vector3D],
        pos_inert: List[Vector3D],
        los_inert: List[Vector3D],
        altitudes: np.ndarray = None,
    ) -> Tuple:
        """Direct location with effect correction in inertial frame.

        Parameters
        ----------
            inert_to_body : inertial to body transform
            spacecraft_velocity : spacecraft velocity vector
            pos_inert : spacecraft position in inertial frame
            los_inert : los vector in inertial frame
            altitudes : altitudes at wich the intersection occurs
        Returns
        -------
            result : ground position (longitude, latitude, altitude)
                of intersection point between specified los and ground
        """

        # Convert inputs to Numpy array
        los_inert = np.array([to_array_v(item.toArray()) for item in los_inert])
        pos_inert = np.array([to_array_v(item.toArray()) for item in pos_inert])
        spacecraft_velocity = np.array([to_array_v(item.toArray()) for item in spacecraft_velocity])

        output = self.direct_location_inert_npy(
            inert_to_body,
            spacecraft_velocity,
            pos_inert,
            los_inert,
            altitudes=altitudes,
        )

        longitude = output[:, 1]
        latitude = output[:, 0]
        altitude = output[:, 2]

        return longitude, latitude, altitude

    def direct_location_inert_npy(
        self,
        inert_to_body: List[Transform],
        spacecraft_velocity: np.ndarray,
        pos_inert: np.ndarray,
        los_inert: np.ndarray,
        altitudes: np.ndarray = None,
    ) -> np.ndarray:
        """Direct location with effect correction in inertial frame.

        Parameters
        ----------
            inert_to_body : inertial to body transform
            spacecraft_velocity : spacecraft velocity vector, shape (N, 3)
            pos_inert : spacecraft position in inertial frame, shape (N, 3)
            los_inert : los vector in inertial frame, shape (N, 3)
            altitudes : altitudes at wich the intersection occurs
        Returns
        -------
            result : array of ground position of intersection point between specified los and ground,
                shape (N, 3) with order (latitude, longitude, altitude).
        """

        # build DynamicTransform
        all_parts = transform_to_numpy(inert_to_body)
        transforms = DynamicTransform(
            translation=all_parts[0],
            velocity=all_parts[1],
            acceleration=all_parts[2],
            rotation=all_parts[3],
            rotation_rate=all_parts[4],
            rotation_acceleration=all_parts[5],
        )

        return self.direct_location_inert_fast(
            inert_to_body=transforms,
            spacecraft_velocity=spacecraft_velocity,
            pos_inert=pos_inert,
            los_inert=los_inert,
            altitudes=altitudes,
        )

    def direct_location_inert_fast(
        self,
        inert_to_body: DynamicTransform,
        spacecraft_velocity: np.ndarray,
        pos_inert: np.ndarray,
        los_inert: np.ndarray,
        altitudes: np.ndarray = None,
    ) -> np.ndarray:
        """Direct location with effect correction in inertial frame.

        Parameters
        ----------
            inert_to_body : inertial to body transform
            spacecraft_velocity : spacecraft velocity vector, shape (N, 3)
            pos_inert : spacecraft position in inertial frame, shape (N, 3)
            los_inert : los vector in inertial frame, shape (N, 3)
            altitudes : altitudes at wich the intersection occurs
        Returns
        -------
            result : array of ground position of intersection point between specified los and ground,
                shape (N, 3) with order (latitude, longitude, altitude).
        """
        # TODO : check sizes

        # from inertial to body
        shifted_inert_to_body = inert_to_body

        if self.aberration_of_light_correction:
            # Apply aberration of light correction on LOS
            los_inert = self.apply_aberration_of_light_correction_npy(los_inert, spacecraft_velocity)

        # Compute ground location of specified pixel according to light time correction flag
        if self.light_time_correction:
            # Compute DEM intersection with light time correction
            # TBN: for simplicity, due to the size of sensor, we consider each pixel to be at sensor position
            shifted_inert_to_body = self.apply_light_time_correction_npy(inert_to_body, pos_inert, los_inert, altitudes)

        # Compute DEM intersection without light time correction
        p_body = shifted_inert_to_body.transform_position(pos_inert)
        l_body = shifted_inert_to_body.transform_direction(los_inert)

        # compute intersection with ellipsoid
        gp0 = self.ellipsoid.point_on_ground_vec(p_body, l_body, 0.0)

        # Only compute points that intersect the ellipsoid
        ind_not_nan = np.where(~np.isnan(gp0[:, 0]))[0]

        result = np.zeros_like(p_body) + np.nan

        if self.algorithm.__class__.__name__ == "ConstantElevationAlgorithm":  # and altitudes is not None:
            raw_point_gp = self.algorithm.intersection_vec(
                self.ellipsoid, p_body[ind_not_nan], l_body[ind_not_nan], altitudes
            )
        else:
            raw_point_gp = self.algorithm.intersection_vec(self.ellipsoid, p_body[ind_not_nan], l_body[ind_not_nan])

        point_gp = self.algorithm.refine_intersection_vec(
            self.ellipsoid, p_body[ind_not_nan], l_body[ind_not_nan], raw_point_gp
        )

        # Compute ground location of specified pixel according to atmospheric refraction correction flag
        result[ind_not_nan, :] = point_gp

        # Compute the ground location with atmospheric correction if asked for
        if self.atmospheric_refraction is not None and self.atmospheric_refraction.must_be_computed:
            for index, point_gp_i in enumerate(point_gp):
                result[ind_not_nan][index] = self.atmospheric_refraction.apply_correction(
                    p_body[ind_not_nan][index], l_body[ind_not_nan][index], np.array(point_gp_i), self.algorithm
                )

        return result

    def date_location(
        self,
        min_line: int,
        max_line: int,
        latitude: np.ndarray,
        longitude: np.ndarray,
        altitude: np.ndarray = None,
        sensor_name: str = None,
    ) -> AbsoluteDate:
        """Find the date at which sensor sees a ground point.

        Note that for each sensor name, the min_line and max_line settings are cached, because they induce costly
        frames computation. So these settings should not be tuned very finely and changed at each call, but should
        rather be a few thousand lines wide and refreshed only when needed.

        TODO If for example an
        inverse location is roughly estimated to occur near line 53764 (for example
        using pyrugged.utils.RoughVisibilityEstimator, min_line
        and {@code maxLine} could be set for example to 50000 and 60000, which would
        be OK also if next line inverse location is expected to occur near line 53780,
        and next one ... The setting could be changed for example to 55000 and 65000 when
        an inverse location is expected to occur after 55750. Of course, these values
        are only an example and should be adjusted depending on mission needs.

        Parameters
        ----------
            sensor_name : name of the line sensor
            min_line : minimum line number
            max_line : maximum line number
            point : point to localize
            latitude : ground point latitude (rad)
            longitude : ground point longitude (rad)
            altitude : explicit altitude for location (m) (if  not specified use algorithm altitude)

        Returns
        -------
            result : date at which ground point is seen by line sensor
        """

        if altitude is None:
            altitude = self.algorithm.get_elevation(latitude, longitude)

        sensor = self.rugged.get_sensor(sensor_name)
        sensor_name = sensor.name
        plane_crossing = self.get_plane_crossing(sensor_name, min_line, max_line)

        # Find approximately the sensor line at which ground point crosses sensor mean plane
        target = self.ellipsoid.transform((latitude, longitude, altitude))
        crossing_result = plane_crossing.find(target[0], target[1], target[2])

        dates = []
        for _, crossing_result_i in enumerate(crossing_result):
            if crossing_result_i is None:
                # Target is out of search interval
                dates.append(None)
            else:
                dates.append(sensor.get_date(crossing_result_i.line))

        return dates

    def inverse_location(
        self,
        min_line: int,
        max_line: int,
        latitudes: np.ndarray,
        longitudes: np.ndarray,
        altitudes: np.ndarray = None,
        sensor_name: str = None,
    ) -> Tuple:
        """Inverse location of a ground point.

        TODO
        Note that for each sensor name, the min_line and max_line settings are cached, because they induce
        costly frames computation. So these settings should not be tuned very finely and changed at each call,
        but should rather be a few thousand lines wide and refreshed only when needed. If for example an
        inverse location is roughly estimated to occur near line 53764 (for example
        using pyrugged.utils.RoughVisibilityEstimator, min_line and max_line could be set for example to 50000 and
        60000, which would be OK also if next line inverse location is expected to occur near line 53780,
        and next one ... The setting could be changed for example to 55000 and 65000 when
        an inverse location is expected to occur after 55750. Of course, these values
        are only an example and should be adjusted depending on mission needs.

        Parameters
        ----------
            sensor_name : name of the line sensor
            min_line : minimum line number
            max_line : maximum line number
            latitudes : array of ground points latitudes (rad), [lat_point1, lat_point2, .., lat_pointn]
            longitudes : array list of ground point longitude (rad), , [lon_point1, lon_point2, .., lon_pointn]
            altitudes : explicit array of altitudes for location (m) (if  not specified use algorithm altitude)

        Returns
        -------
            result : (lines, pixels), i.e. sensors pixel seeing point, or (None, None)
            if point cannot be seen between the prescribed line numbers
        """

        lines = []
        pixels = []
        index = 0

        if altitudes is None:
            altitudes = self.algorithm.get_elevation(latitudes, longitudes)

        sensor = self.rugged.get_sensor(sensor_name)
        sensor_name = sensor.name

        plane_crossing = self.get_plane_crossing(sensor_name, min_line, max_line)
        point_coord = (latitudes, longitudes, altitudes)

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_inverse_location(
                sensor,
                point_coord,
                self.ellipsoid,
                min_line,
                max_line,
                self.light_time_correction,
                self.aberration_of_light_correction,
                self.atmospheric_refraction is not None,
            )

        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_sensor_mean_plane(plane_crossing)

        if self.atmospheric_refraction is None or not self.atmospheric_refraction.must_be_computed:
            # Compute inverse location WITHOUT atmospheric refraction
            lines, pixels = self.find_sensor_pixel_without_atmosphere(
                latitudes, longitudes, altitudes, sensor, plane_crossing
            )
        else:
            for latitude, longitude, altitude in zip(latitudes, longitudes, altitudes):  # noqa: B905
                if altitudes is None:
                    altitude = self.algorithm.get_elevation(latitude, longitude)

                point = np.array([latitude, longitude, altitude])

                # Compute inverse location WITH atmospheric refraction
                line, pixel = self.find_sensor_pixel_with_atmosphere(point, sensor, min_line, max_line)

                lines.append(line)
                pixels.append(pixel)
                index = index + 1

        return lines, pixels

    def apply_aberration_of_light_correction(self, obs_l_inert: Vector3D, spacecraft_velocity: Vector3D) -> np.ndarray:
        """Apply aberration of light correction (for direct location).

        Parameters
        ----------
            obs_l_inert : line of sight in inertial frame
            spacecraft_velocity : spacecraft velocity in inertial frame

        Returns
        -------
            l_inert : line of sight with aberration of light correction
        """

        obs_l_inert_arr = to_array_v(obs_l_inert.toArray())
        spacecraft_velocity_arr = to_array_v(spacecraft_velocity.toArray())
        a_val = get_norm_sq(obs_l_inert_arr)
        b_val = -dot(obs_l_inert_arr, spacecraft_velocity_arr)
        c_val = get_norm_sq(spacecraft_velocity_arr) - Constants.SPEED_OF_LIGHT * Constants.SPEED_OF_LIGHT

        # a > 0 and c < 0
        s_val = math.sqrt(b_val * b_val - a_val * c_val)

        # Only the k > 0 are kept as solutions (the solutions: -(s+b)/a  and c/(s-b) are useless)
        k_val = -c_val / (s_val + b_val) if b_val > 0 else (s_val - b_val) / a_val

        l_inert = compute_linear_combination_2(
            k_val / Constants.SPEED_OF_LIGHT, obs_l_inert_arr, -1.0 / Constants.SPEED_OF_LIGHT, spacecraft_velocity_arr
        )

        return l_inert

    def apply_aberration_of_light_correction_vec(
        self, obs_l_inert: List[Vector3D], spacecraft_velocity: List[Vector3D]
    ) -> List[Vector3D]:
        """Apply aberration of light correction (for direct location).

        Parameters
        ----------
            obs_l_inert : line of sight in inertial frame as list
            spacecraft_velocity : spacecraft velocity in inertial frame as list

        Returns
        -------
            l_inert : line of sight with aberration of light correction as list
        """

        obs_l_inert = np.array([to_array_v(item.toArray()) for item in obs_l_inert])
        spacecraft_velocity = np.array([to_array_v(item.toArray()) for item in spacecraft_velocity])

        output = self.apply_aberration_of_light_correction_npy(obs_l_inert, spacecraft_velocity)

        return [Vector3D(item.tolist()) for item in output]

    def apply_aberration_of_light_correction_npy(
        self, obs_l_inert: np.ndarray, spacecraft_velocity: np.ndarray
    ) -> np.ndarray:
        """Apply aberration of light correction (for direct location).

        Parameters
        ----------
            obs_l_inert : line of sight in inertial frame, shape (N, 3)
            spacecraft_velocity : spacecraft velocity in inertial frame, shape (N, 3)

        Returns
        -------
            l_inert : line of sight with aberration of light correction, shape (N, 3)
        """

        a_val = get_norm_sq_n(obs_l_inert)
        b_val = -dot_n(obs_l_inert, spacecraft_velocity)
        c_val = get_norm_sq_n(spacecraft_velocity) - Constants.SPEED_OF_LIGHT * Constants.SPEED_OF_LIGHT

        # a > 0 and c < 0
        s_val = np.sqrt(b_val * b_val - a_val * c_val)

        # Only the k > 0 are kept as solutions (the solutions: -(s+b)/a  and c/(s-b) are useless)
        k_val = np.where(b_val > 0, -c_val / (s_val + b_val), (s_val - b_val) / a_val)

        l_inert = compute_linear_combination_2_arr(
            k_val / Constants.SPEED_OF_LIGHT,
            obs_l_inert,
            -np.ones_like(k_val) / Constants.SPEED_OF_LIGHT,
            spacecraft_velocity,
        )

        return l_inert

    def apply_light_time_correction(
        self,
        inert_to_body: Transform,
        p_inert: Vector3D,
        l_inert: Vector3D,
        altitude: float = None,
    ) -> np.ndarray:
        """Compute the DEM intersection with light time correction.

        Parameters
        ----------
            inert_to_body : transform for the date from inertial to body
            p_inert : sensor position in inertial frame
            l_inert : line of sight in inertial frame (with light time correction if asked for)
            altitude : altitude at wich the intersection occurs

        Returns
        -------
            result : geodetic point with light time correction
        """

        # Transform LOS in spacecraft frame to observed body
        s_l = StaticTransform.cast_(inert_to_body).transformVector(l_inert)
        s_p = StaticTransform.cast_(inert_to_body).transformPosition(p_inert)

        s_lp = to_array(s_l.getX(), s_l.getY(), s_l.getZ())
        s_pp = to_array(s_p.getX(), s_p.getY(), s_p.getZ())

        # Compute point intersecting ground (= the ellipsoid) along the pixel LOS
        e_p1 = self.ellipsoid.transform_vec(self.ellipsoid.point_on_ground(s_pp, s_lp, 0.0))
        # Compute light time time correction (vs the ellipsoid) (s)
        delta_t1 = distance(e_p1, s_pp) / Constants.SPEED_OF_LIGHT
        # Apply shift due to light time correction (vs the ellipsoid)
        shifted_1 = inert_to_body.shiftedBy(float(-delta_t1))
        # Search the intersection of LOS (taking into account the light time correction if asked for) with DEM
        s_tp = StaticTransform.cast_(shifted_1).transformPosition(p_inert)
        s_tv = StaticTransform.cast_(shifted_1).transformVector(l_inert)
        s_tpp = to_array(s_tp.getX(), s_tp.getY(), s_tp.getZ())
        s_tvp = to_array(s_tv.getX(), s_tv.getY(), s_tv.getZ())

        if self.algorithm.__class__.__name__ == "ConstantElevationAlgorithm":  # and altitudes is not None:
            gp_1 = self.algorithm.intersection(self.ellipsoid, s_tpp, s_tvp, altitude)
        else:
            gp_1 = self.algorithm.intersection(self.ellipsoid, s_tpp, s_tvp)

        # Convert the geodetic point (intersection of LOS with DEM) in cartesian coordinates
        e_p2 = self.ellipsoid.transform_vec(gp_1)
        # Compute the light time correction (vs DEM) (s)
        delta_t2 = distance(e_p2, s_pp) / Constants.SPEED_OF_LIGHT

        # Apply shift due to light time correction (vs DEM)
        return inert_to_body.shiftedBy(float(-delta_t2))

    def apply_light_time_correction_vec(
        self,
        inert_to_body: List[Transform],
        p_inert: List[Vector3D],
        l_inert: List[Vector3D],
        altitudes: np.ndarray = None,
    ) -> List[Transform]:
        """Compute the DEM intersection with light time correction.

        Parameters
        ----------
            inert_to_body : transform for the date from inertial to body
            p_inert : sensor position in inertial frame
            l_inert : line of sight in inertial frame (with light time correction if asked for)
            altitudes : altitudes at wich the intersection occurs

        Returns
        -------
            result : geodetic point with light time correction
        """

        p_inert = np.array([to_array_v(item.toArray()) for item in p_inert])
        l_inert = np.array([to_array_v(item.toArray()) for item in l_inert])

        # build DynamicTransform
        all_parts = transform_to_numpy(inert_to_body)
        transforms = DynamicTransform(
            translation=all_parts[0],
            velocity=all_parts[1],
            acceleration=all_parts[2],
            rotation=all_parts[3],
            rotation_rate=all_parts[4],
            rotation_acceleration=all_parts[5],
        )

        shifted_transforms = self.apply_light_time_correction_npy(transforms, p_inert, l_inert, altitudes=altitudes)

        # convert to List[Transform]
        shifted_elements = [
            shifted_transforms.translation,
            shifted_transforms.velocity,
            shifted_transforms.acceleration,
            shifted_transforms.rotation,
            shifted_transforms.rotation_rate,
            shifted_transforms.rotation_acceleration,
        ]
        return [
            get_corresponding_orekit_transform(shifted_elements, sub_index=idx)
            for idx in range(len(shifted_transforms))
        ]

    def apply_light_time_correction_npy(
        self,
        inert_to_body: DynamicTransform,
        p_inert: np.ndarray,
        l_inert: np.ndarray,
        altitudes: np.ndarray = None,
    ) -> DynamicTransform:
        """Compute the DEM intersection with light time correction.

        Parameters
        ----------
            inert_to_body : transform for the date from inertial to body
            p_inert : sensor position in inertial frame
            l_inert : line of sight in inertial frame (with light time correction if asked for)
            altitudes : altitudes at wich the intersection occurs

        Returns
        -------
            result : geodetic point with light time correction
        """

        # Transform LOS in spacecraft frame to observed body
        s_p = inert_to_body.transform_position(p_inert)
        s_l = inert_to_body.transform_direction(l_inert)

        # Compute point intersecting ground (= the ellipsoid) along the pixel LOS
        e_p1 = self.ellipsoid.transform_vec(self.ellipsoid.point_on_ground_vec(s_p, s_l, 0.0))
        # Compute light time time correction (vs the ellipsoid) (s)
        delta_t1 = distance(e_p1.T, s_p.T) / Constants.SPEED_OF_LIGHT
        # Apply shift due to light time correction (vs the ellipsoid)
        shifted_1 = inert_to_body.shifted(-delta_t1)
        # Search the intersection of LOS (taking into account the light time correction if asked for) with DEM
        s_tp = shifted_1.transform_position(p_inert)
        s_tv = shifted_1.transform_direction(l_inert)

        if self.algorithm.__class__.__name__ == "ConstantElevationAlgorithm":  # and altitudes is not None:
            gp_1 = self.algorithm.intersection_vec(self.ellipsoid, s_tp, s_tv, altitudes)
        else:
            gp_1 = self.algorithm.intersection_vec(self.ellipsoid, s_tp, s_tv)

        # Convert the geodetic points (intersection of LOS with DEM) in cartesian coordinates
        e_p2 = self.ellipsoid.transform_vec(gp_1)
        # Compute the light time correction (vs DEM) (s)
        delta_t2 = distance(e_p2.T, s_p.T) / Constants.SPEED_OF_LIGHT

        # Apply shift due to light time correction (vs DEM)
        return inert_to_body.shifted(-delta_t2)

    def find_sensor_pixel_without_atmosphere(
        self,
        latitudes: np.ndarray,
        longitudes: np.ndarray,
        altitudes: np.ndarray,
        sensor: LineSensor,
        plane_crossing: SensorMeanPlaneCrossing,
    ) -> Tuple:
        """Find the sensor pixel WITHOUT atmospheric refraction correction.

        Parameters
        ----------
            latitudes : array of ground points latitudes (rad), [lat_point1, lat_point2, .., lat_pointn]
            longitudes : array list of ground point longitude (rad), , [lon_point1, lon_point2, .., lon_pointn]
            altitudes : explicit array of altitudes for location (m) (if  not specified use algorithm altitude)
            sensor : the line sensor
            plane_crossing : the sensor mean plane crossing

        Returns
        -------
            result : the sensor pixel crossing (line,pixel) or (None,None) if cannot be found
        """

        # Find approximately the sensor line at which ground point crosses sensor mean plane
        if len(latitudes) > 1:
            target = self.ellipsoid.transform_vec(np.array([latitudes, longitudes, altitudes]).T).T
        else:
            if isinstance(altitudes[0], np.ndarray):
                target = self.ellipsoid.transform_vec(np.array([latitudes[0], longitudes[0], altitudes[0][0]]))
            else:
                target = self.ellipsoid.transform_vec(np.array([latitudes[0], longitudes[0], altitudes[0]]))

        crossing_results = plane_crossing.find(target[0], target[1], target[2])
        lines = []
        pixels = []
        for crossing_result in crossing_results:
            if crossing_result is None:
                # Target is out of search interval
                lines.append(None)
                pixels.append(None)
            else:
                date = crossing_result.date
                target_direction = crossing_result.target_direction
                target_direction_derivative = crossing_result.target_direction_derivative
                line = crossing_result.line

                # Find approximately the pixel along this sensor line
                pixel_crossing = SensorPixelCrossing(
                    sensor,
                    plane_crossing.mean_plane_normal,
                    target_direction,
                    self.MAX_EVAL,
                    self.COARSE_INVERSE_LOCATION_ACCURACY,
                )

                coarse_pixel = pixel_crossing.locate_pixel(date)

                if math.isnan(coarse_pixel):
                    lines.append(None)
                    pixels.append(None)
                else:
                    # Fix line by considering the closest pixel exact position and line-of-sight
                    # (this pixel might point towards a direction slightly above or below the mean sensor plane)
                    low_index = int(max(0, min(sensor.nb_pixels - 2, math.floor(coarse_pixel))))
                    low_los = sensor.get_los(date, low_index)
                    high_los = sensor.get_los(date, low_index + 1)
                    fixed_direction, fixed_line = find_fixed_line_func(
                        high_los, line, low_los, target_direction, target_direction_derivative
                    )

                    # Fix neighbouring pixels
                    fixed_date = sensor.get_date(float(fixed_line))
                    fixed_x = sensor.get_los(fixed_date, low_index)
                    fixed_x_p1 = sensor.get_los(fixed_date, low_index + 1)

                    fixed_pixel = find_fixed_pixel_func(fixed_direction, fixed_x, fixed_x_p1, high_los, low_index)
                    lines.append(fixed_line)
                    pixels.append(fixed_pixel)

                    if dump_manager.DUMP_VAR is not None:
                        dump_manager.DUMP_VAR.dump_inverse_location_result((fixed_line, fixed_pixel))

        return lines, pixels

    def find_sensor_pixel_with_atmosphere(
        self, point: np.ndarray, sensor: LineSensor, min_line: int, max_line: int
    ) -> Tuple:
        """Find the sensor pixel WITH atmospheric refraction correction.

        Parameters
        ----------
            point : geodetic point to localize
            sensor : the line sensor
            min_line : minimum line number where the search will be performed
            max_line : maximum line number where the search wille be performed

        Returns
        -------
            sensor_pixel_with_atmosphere : the sensor pixel crossing (line,pixel) or (None,None) if cannot be found
        """

        # TBN : there is no direct way to compute the inverse location.
        # The method is based on an interpolation grid associated with the fixed point method

        sensor_name = sensor.name

        # Compute a correction grid (at sensor level)
        # ===========================================

        # Need to be computed only once for a given sensor (with the same min_line and max_line)

        if (
            self.atmospheric_refraction.bif_pixel is None
            or self.atmospheric_refraction.bif_line is None
            or not self.atmospheric_refraction.is_same_context(sensor_name, min_line, max_line)
        ):
            # Definition of a regular grid (at sensor level)
            self.atmospheric_refraction.configure_correction_grid(sensor, min_line, max_line)

            # Get the grid nodes
            nb_pixel_grid = self.atmospheric_refraction.get_computation_parameters().nb_pixel_grid
            nb_line_grid = self.atmospheric_refraction.get_computation_parameters().nb_line_grid
            pixel_grid = self.atmospheric_refraction.get_computation_parameters().u_grid
            line_grid = self.atmospheric_refraction.get_computation_parameters().v_grid

            # Computation, for the sensor grid, of the direct location WITH atmospheric refraction
            # (full computation)
            self.atmospheric_refraction.reactivate_computation()
            geodetic_grid_with_atmosphere = self.compute_direct_loc_on_grid_with_atmosphere(
                pixel_grid, line_grid, sensor
            )
            # pixel_grid and line_grid are the nodes where the direct loc is computed WITH atmosphere

            # Computation of the inverse location WITHOUT atmospheric refraction for the grid nodes
            self.atmospheric_refraction.deactivate_computation()
            sensor_pixel_grid_inverse_without = self.compute_inverse_loc_on_grid_without_atmosphere(
                geodetic_grid_with_atmosphere, nb_pixel_grid, nb_line_grid, sensor, min_line, max_line
            )

            self.atmospheric_refraction.reactivate_computation()

            # Compute the grid correction functions (for pixel and line)
            self.atmospheric_refraction.compute_grid_correction_functions(sensor_pixel_grid_inverse_without)

        # Fixed point method
        # ==================

        # Initialization
        # --------------

        # Deactivate the dump because no need to keep intermediate computations of inverse loc (can be regenerate)
        if dump_manager.DUMP_VAR is not None:
            was_suspended = dump_manager.DUMP_VAR.suspend()

        # Compute the sensor pixel on the desired ground point WITHOUT atmosphere
        self.atmospheric_refraction.deactivate_computation()
        sp_0 = self.inverse_location(min_line, max_line, [point[0]], [point[1]], [point[2]], sensor_name)
        sp_0 = (sp_0[0][0], sp_0[1][0])
        self.atmospheric_refraction.reactivate_computation()

        # Reactivate the dump
        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.resume(was_suspended)

        if sp_0 == (None, None):
            # In order for the dump to end nicely
            if dump_manager.DUMP_VAR is not None:
                dump_manager.DUMP_VAR.end_nicely()

            # Impossible to find the point in the given min line and max line (without atmosphere)
            raise PyRuggedError(PyRuggedMessages.INVALID_RANGE_FOR_LINES.value, min_line, max_line, "")

        # Set up the starting point of the fixed point method
        pixel_0 = sp_0[1]
        line_0 = sp_0[0]

        # Needed data for the dump
        sensor.dump_rate(line_0)

        # Apply fixed point method until convergence in pixel and line
        # ------------------------------------------------------------

        # Compute the first (pixel, line) value:
        # Initial sensor pixel value + correction due to atmosphere at this same sensor pixel
        corr_pixel_previous = pixel_0 + self.atmospheric_refraction.bif_pixel.value(np.array([pixel_0, line_0]))
        corr_line_previous = line_0 + self.atmospheric_refraction.bif_line.value(np.array([pixel_0, line_0]))

        # TODO dumping values
        # value_pixel = self.atmospheric_refraction.bif_pixel.value(np.array([pixel_0, line_0]))
        # value_line = self.atmospheric_refraction.bif_line.value(np.array([pixel_0, line_0]))

        # log_file = open("log_line_pixel.txt", "a")
        # text_to_dump = f'{"interpolation pixel0  "}{pixel_0}{"  line0  "}{line_0}
        # {"  bif_pixel.value(pixel_0, line_0)  "}{value_pixel}{"  bif_line.value(pixel0, line0)  "}{value_line}\n'
        # print(text_to_dump, file=log_file)
        # log_file.write(text_to_dump)
        # log_file.close()

        delta_corr_pixel = float("inf")
        delta_corr_line = float("-inf")

        while delta_corr_pixel > self.PIXEL_CV_THRESHOLD and delta_corr_line > self.LINE_CV_THRESHOLD:
            # Compute the current (pixel, line) value =
            # Initial sensor pixel value + correction due to atmosphere on the previous sensor pixel
            corr_pixel_current = pixel_0 + self.atmospheric_refraction.bif_pixel.value(
                np.array([corr_pixel_previous, corr_line_previous])
            )
            corr_line_current = line_0 + self.atmospheric_refraction.bif_line.value(
                np.array([corr_pixel_previous, corr_line_previous])
            )

            # Compute the delta in pixel and line to check the convergence
            delta_corr_pixel = float(np.abs(corr_pixel_current - corr_pixel_previous))
            delta_corr_line = float(np.abs(corr_line_current - corr_line_previous))

            # Store the (pixel, line) for next loop
            corr_pixel_previous = corr_pixel_current
            corr_line_previous = corr_pixel_current

        # The sensor pixel is found !
        sensor_pixel_with_atmosphere = (corr_line_previous, corr_pixel_previous)

        # Dump the found sensor pixel
        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.dump_inverse_location_result(sensor_pixel_with_atmosphere)

        return sensor_pixel_with_atmosphere

    def compute_inverse_loc_on_grid_without_atmosphere(
        self,
        ground_grid_with_atmosphere: List[List[float]],
        nb_pixel_grid: int,
        nb_line_grid: int,
        sensor: LineSensor,
        min_line: int,
        max_line: int,
    ) -> np.array:
        """Compute the inverse location WITHOUT atmospheric refraction for the geodetic points
        associated to the sensor grid nodes.

        Parameters
        ----------
            ground_grid_with_atmosphere : ground grid found for sensor grid nodes with atmosphere
            nb_pixel_grid : size of the pixel grid
            nb_line_grid : size of the line grid
            sensor : the line sensor
            min_line : minimum line number where the search will be performed
            max_line : maximum line number where the search will be performed

        Returns
        -------
            sensor_pixel_grid : the sensor pixel grid computed without atmosphere
        """

        # Deactivate the dump because no need to keep intermediate computations of inverse loc (can be regenerate)
        if dump_manager.DUMP_VAR is not None:
            was_suspended = dump_manager.DUMP_VAR.suspend()

        sensor_pixel_grid = [[0 for i in range(nb_line_grid)] for j in range(nb_pixel_grid)]
        sensor_name = sensor.name

        for u_index in range(nb_pixel_grid):
            for v_index in range(nb_line_grid):
                # Check if the geodetic point exists
                if ground_grid_with_atmosphere[u_index][v_index] != (None, None):
                    ground_point = ground_grid_with_atmosphere[u_index][v_index]
                    current_lat = ground_point[1]  # latitude
                    current_lon = ground_point[0]  # longitude

                    try:
                        # Compute the inverse location for the current node
                        lines, pixels = self.inverse_location(
                            min_line,
                            max_line,
                            np.array([current_lat]),
                            np.array([current_lon]),
                            sensor_name=sensor_name,
                        )
                        sensor_pixel_grid[u_index][v_index] = (lines[0], pixels[0])

                    except PyRuggedError as pre:
                        # This should never happen
                        # In order for the dump to end nicely
                        if dump_manager.DUMP_VAR is not None:
                            dump_manager.DUMP_VAR.end_nicely()

                        raise PyRuggedInternalError from pre

                    # Check if the pixel is inside the sensor (with a margin)
                    # OR if the inverse location was impossible (null result)
                    if not self.pixel_is_inside(sensor_pixel_grid[u_index][v_index], sensor):
                        # In order for the dump to end nicely
                        if dump_manager.DUMP_VAR is not None:
                            dump_manager.DUMP_VAR.end_nicely()
                        # Impossible to find the point in the given min line
                        if sensor_pixel_grid[u_index][v_index] == (None, None):
                            raise PyRuggedError(
                                PyRuggedMessages.SENSOR_PIXEL_NOT_FOUND_IN_RANGE_LINES.value, min_line, max_line
                            )

                        invloc_margin = self.atmospheric_refraction.atmospheric_params.invloc_margin
                        raise PyRuggedError(
                            PyRuggedMessages.SENSOR_PIXEL_NOT_FOUND_IN_PIXELS_LINE.value,
                            sensor_pixel_grid[u_index][v_index][1],
                            -invloc_margin,
                            invloc_margin + sensor.nb_pixels - 1,
                            invloc_margin,
                        )

                else:
                    # ground_grid[u_index, v_index] == None:
                    # impossible to compute inverse loc because ground point not defined
                    sensor_pixel_grid[u_index][v_index] = (None, None)

        # Reactivate the dump
        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.resume(was_suspended)

        # The sensor grid computed WITHOUT atmospheric refraction correction
        return sensor_pixel_grid

    def pixel_is_inside(self, pixel: Tuple, sensor: LineSensor) -> bool:
        """Check if pixel is inside the sensor with a margin.

        Parameters
        ----------
            pixel : pixel to check (may be (None,None) if not found)
            sensor : the line sensor

        Returns
        -------
            result : true if the pixel is inside the sensor
        """

        if pixel != (None, None):
            # Get inverse loc margin
            if self.atmospheric_refraction is None:
                invloc_margin = 0

            else:
                invloc_margin = self.atmospheric_refraction.atmospheric_params.invloc_margin

            return pixel[1] >= -invloc_margin and pixel[1] < invloc_margin + sensor.nb_pixels - 1

        return False

    def compute_direct_loc_on_grid_with_atmosphere(
        self, pixel_grid: List[float], line_grid: List[float], sensor: LineSensor
    ) -> List[List[float]]:
        """Computation, for the sensor pixels grid, of the direct location WITH atmospheric refraction.
        (full computation)

        Parameters
        ----------
            pixel_grid : the pixel grid
            line_grid : the line grid
            sensor : the line sensor

        Returns
        -------
            result : the ground grid computed with atmosphere
        """

        # Deactivate the dump because no need to keep intermediate computations of direct loc (can be regenerate)
        if dump_manager.DUMP_VAR is not None:
            was_suspended = dump_manager.DUMP_VAR.suspend()

        nb_pixel_grid = len(pixel_grid)
        nb_line_grid = len(line_grid)
        ground_grid_with_atmosphere = [[0 for i in range(nb_line_grid)] for j in range(nb_pixel_grid)]
        sensor_position = sensor.position

        dates = [sensor.get_date(line) for line in line_grid]

        for u_index in range(nb_pixel_grid):
            pixel_number = [pixel_grid[u_index] for v_index in range(nb_line_grid)]
            los = sensor.get_interpolated_los_arr(dates, pixel_number)
            for v_index in range(nb_line_grid):
                date = dates[v_index]
                los_i = los[v_index]

                try:
                    # Compute the direct location for the current node
                    ground_grid_with_atmosphere[u_index][v_index] = self.direct_location_of_los(
                        date, sensor_position, los_i
                    )

                except PyRuggedError as pre:
                    # In order for the dump to end nicely
                    if dump_manager.DUMP_VAR is not None:
                        dump_manager.DUMP_VAR.end_nicely()

                    raise PyRuggedInternalError from pre

        # Reactivate the dump
        if dump_manager.DUMP_VAR is not None:
            dump_manager.DUMP_VAR.resume(was_suspended)

        # The ground grid computed WITH atmospheric refraction correction
        return ground_grid_with_atmosphere

    def distance_between_los(
        self,
        sensor_a: LineSensor,
        date_a: AbsoluteDate,
        pixel_a: float,
        sc_to_body_a: SpacecraftToObservedBody,
        sensor_b: LineSensor,
        date_b: AbsoluteDate,
        pixel_b: float,
    ) -> List[float]:
        """Compute distances between two line sensors.

        Parameters
        ----------
            sensor_a : line sensor A
            date_a : current date for sensor A
            pixel_a : pixel index for sensor A
            sc_to_body_a : spacecraft to body transform for sensor A
            sensor_b : line sensor B
            date_b : current date for sensor B
            pixel_b : pixel index for sensor B

        Returns
        -------
            distances : distances computed between LOS and to the ground
        """

        # Compute the approximate transform between spacecraft and observed body
        # from PyRugged instance A
        sc_to_inert_a = sc_to_body_a.get_sc_to_inertial(date_a)
        inert_to_body_a = sc_to_body_a.get_inertial_to_body(date_a)
        transform_sc_to_body_a = Transform(date_a, sc_to_inert_a, inert_to_body_a)

        # from (current) PyRugged instance B
        sc_to_inert_b = self.rugged.sc_to_body.get_sc_to_inertial(date_b)
        inert_to_body_b = self.rugged.sc_to_body.get_inertial_to_body(date_b)
        transform_sc_to_body_b = Transform(date_b, sc_to_inert_b, inert_to_body_b)

        # Get sensors LOS into local frame
        v_a_local = sensor_a.get_los(date_a, pixel_a)  # v_a : line of sight's vector A
        v_b_local = sensor_b.get_los(date_b, pixel_b)  # v_b : line of sight's vector B

        # Position of sensors into local frame
        s_a_local = sensor_a.position  # s_a : sensor_a 's position
        s_b_local = sensor_b.position  # s_b : sensor_b 's position

        # Get sensors position and LOS into body frame
        s_a = StaticTransform.cast_(transform_sc_to_body_a).transformPosition(Vector3D(s_a_local.tolist()))
        v_a = StaticTransform.cast_(transform_sc_to_body_a).transformVector(Vector3D(v_a_local.tolist()))
        s_b = StaticTransform.cast_(transform_sc_to_body_b).transformPosition(Vector3D(s_b_local.tolist()))
        v_b = StaticTransform.cast_(transform_sc_to_body_b).transformPosition(Vector3D(v_b_local.tolist()))

        # Compute distance
        v_base = s_b.subtract(s_a)
        sv_a = v_base.dotProduct(v_a)
        sv_b = v_base.dotProduct(v_b)

        va_vb = v_a.dotProduct(v_b)

        # Compute lambda_b = (sv_a * v_a.v_b - sv_b) / (1 - (v_a.v_b)²)
        lambda_b = (sv_a * va_vb - sv_b) / (1 - va_vb * va_vb)

        # Compute lambda_a = sv_a + lambda_b * v_a.v_b
        lambda_a = sv_a + lambda_b * va_vb

        # Compute vector m_a = s_a + lambda_a * v_a
        m_a = s_a.add(v_a.scalarMultiply(lambda_a))
        # Compute vector m_b = s_b + lambda_b * v_b
        m_b = s_b.add(v_b.scalarMultiply(lambda_b))

        # Compute m_a -> m_b for which distance between LOS is minimum
        v_distance_min = m_b.subtrat(m_a)

        # Compute vector from mid point of vector m_a -> m_b to the ground (corresponds to minimum elevation)
        mid_point = (m_b.add(m_a)).scalarMultiply(0.5)

        # Get the euclidean norms to compute the minimum distances: between LOS and to the ground
        distances = [v_distance_min.getNorm(), mid_point.getNorm()]

        return distances

    # def distance_between_los_derivatives(
    #     self,
    #     sensor_a: LineSensor,
    #     date_a: AbsoluteDate,
    #     pixel_a: float,
    #     sc_to_body_a: SpacecraftToObservedBody,
    #     sensor_b: LineSensor,
    #     date_b: AbsoluteDate,
    #     pixel_b: float,
    #     generator: DerivativeGenerator
    # ) -> :
    #     """Compute distances between two line sensors with derivatives.

    #     Parameters
    #     ----------
    #         sensor_a : pyrugged.line_sensor.line_sensor.LineSensor
    #             Line sensor A
    #         date_a : orekit.time.AbsoluteDate
    #             Current date for sensor A
    #         pixel_a : float
    #             Pixel index for sensor A
    #         sc_to_body_a : pyrugged.utils.spacecraft_to_observed_body.SpacecraftToObservedBody
    #             Spacecraft to body transform for sensor A
    #         sensor_b : pyrugged.line_sensor.line_sensor.LineSensor
    #             Line sensor B
    #         date_b : orekit.time.AbsoluteDate
    #             Current date for sensor B
    #         pixel_b : float
    #             Pixel index for sensor B
    #         generator : TODO
    #             Generator to use for building DerivativeStructure instances

    #     Returns
    #     -------
    #         ret : TODO
    #             Distances computed, with derivatives, between LOS and to the ground

    #     """

    #     # Compute the approximate transforms between spacecraft and observed body
    #     # from PyRugged instance A
    #     sc_to_inert_a = sc_to_body_a.get_sc_to_inertial(date_a)
    #     inert_to_body_a = sc_to_body_a.get_inertial_to_body(date_a)
    #     transform_sc_to_body_a = Transform(date_a, sc_to_inert_a, inert_to_body_a)

    #     # from (current) PyRugged instance B
    #     sc_to_inert_b = self.sc_to_body.get_sc_to_inertial(date_b)
    #     inert_to_body_b = self.sc_to_body.get_inertial_to_body(date_b)
    #     transform_sc_to_body_b = Transform(date_b, sc_to_inert_b, inert_to_body_b)

    #     # Get sensors LOS into local frame
    #     v_a_local = sensor_a.get_los_derivatives(date_a, pixel_a, generator)
    #     v_b_local = sensor_b.get_los_derivatives(date_b, pixel_b, generator)

    #     # Get sensors LOS into body frame
    #     v_a = StaticTransform.cast_(transform_sc_to_body_a).transformVector(v_a_local)
    #     v_b = StaticTransform.cast_(transform_sc_to_body_b).transformVector(v_b_local)

    #     # Position of sensors into local frame
    #     s_atmp = sensor_a.get_position()
    #     s_btmp = sensor_b.get_position()

    #     scale_factor = FieldVector3D.dotProduct(
    #                                   Vector.cast_(v_a).normalize(),
    #                                   Vector.cast_(v_a).normalize()
    #                                  )  # v_a.v_a = 1

    #     # Build a vector from the position and a scale factor (equals to 1).
    #     # The vector built will be scaleFactor * sAtmp for example.
    #     s_a_local = FieldVector3D(scale_factor, s_atmp)
    #     s_b_local = FieldVector3D(scale_factor, s_btmp)

    #     # Get sensors position into body frame
    #     s_a = StaticTransform.cast_(transform_sc_to_body_a).transformPosition(s_a_local)  # s_a : sensor A 's position
    #     s_b = StaticTransform.cast_(transform_sc_to_body_b).transformPosition(s_b_local)  # s_b : sensor B 's position

    #     # Compute distance
    #     v_base = s_b.subtract(s_a)  # s_b - s_a
    #     sv_a = FieldVector3D.dotProduct(v_base, v_a)  # sv_a = (s_b - s_a).v_a
    #     sv_b = FieldVector3D.dotProduct(v_base, v_b)  # sv_b = (s_b - s_a).v_b

    #     va_vb = FieldVector3D.dotProduct(v_a, v_b)  # v_a.v_b

    #     # Compute lambda_b = (sv_a * v_a.v_b - sv_b) / (1 - (v_a.v_b)²)
    #     lambda_b = (sv_a.multiply(va_vb).subtract(sv_b)).divide(va_vb.multiply(va_vb).subtract(1).negate())

    #     # Compute lambda_a = sv_a + lambda_b * v_a.v_b
    #     lambda_a = va_vb.multiply(lambda_b).add(sv_a)

    #     # Compute vector m_a
    #     m_a = s_a.add(v_a.scalarMultiply(lambda_a))  # m_a = s_a + lambda_a * v_a
    #     m_b = s_b.add(v_b.scalarMultiply(lambda_b))  # m_b = s_b + lambda_b * v_b

    #     # Compute vector m_a -> m_b for which distance between LOS is minimum
    #     v_distance_min = m_b.subtract(m_a)

    #     # Compute vector from mid point of vector m_a -> m_B to the ground (corresponds to minimum elevation)
    #     mid_point = (m_b.add(m_a)).scalarMultiply(0.5)

    #     # Get the euclidean norms to compute the minimum distances:
    #     # between LOS
    #     d_min = v_distance_min.getNorm()
    #     # to the ground
    #     d_central_body = mid_point.getNorm()

    #     ret = MathArrays.buildArray(d_min.getField(), 2)
    #     ret[0] = d_min
    #     ret[1] = d_central_body

    #     return ret

    def get_plane_crossing(self, sensor_name: str, min_line: int, max_line: int) -> SensorMeanPlaneCrossing:
        """Get the mean plane crossing finder for a sensor.

        Parameters
        ----------
            sensor_name : name of the line sensor
            min_line : minimum line number
            max_line : maximum line number

        Returns
        -------
            plane_crossing : mean plane crossing finder
        """

        if sensor_name not in self._finders:
            self._finders[sensor_name] = None

        sensor = self.rugged.get_sensor(sensor_name)
        sensor_name = sensor.name
        plane_crossing = self._finders[sensor_name]

        if plane_crossing is None or plane_crossing.min_line != min_line or plane_crossing.max_line != max_line:
            # Create a new finder for the specified sensor and range
            plane_crossing = SensorMeanPlaneCrossing(
                sensor,
                self.rugged.sc_to_body,
                min_line,
                max_line,
                self.light_time_correction,
                self.aberration_of_light_correction,
                self.MAX_EVAL,
                self.COARSE_INVERSE_LOCATION_ACCURACY,
            )

            # Store the finder, in order to reuse it
            # (and save some computation done in its constructor)
            self.set_plane_crossing(plane_crossing)

        return plane_crossing

    def set_plane_crossing(self, plane_crossing: SensorMeanPlaneCrossing):
        """Set the mean plane crossing finder for a sensor.

        Parameters
        ----------
            plane_crossing : plane crossing finder

        """

        self._finders[plane_crossing.sensor.name] = plane_crossing

    # def inverse_location_derivatives(
    #     self,
    #     sensor_name: str,
    #     point: np.ndarray,
    #     min_line: int,
    #     max_line: int,
    #     generator:
    #     ):
    #     """Inverse location of a point with derivatives.

    #     Parameters
    #     ----------
    #         sensor_name : string
    #             Name of the line sensor
    #         point : orekit.bodies.GeodeticPoint
    #             Point to localize
    #         min_line : int
    #             Minimum line number
    #         max_line : int
    #             Maximum line number
    #         generator : TODO
    #             Generator to use for building Derivative instances

    #     Returns
    #     -------
    #         ret :
    #             Sensor pixel seeing point with derivatives,
    #             or null if point cannot be seen between the prescribed line numbers

    #     """

    #     sensor = self.get_line_sensor(sensor_name)
    #     plane_crossing = self.get_plane_crossing(sensor_name, min_line, max_line)

    #     # Find approximately the sensor line at which ground point crosses sensor mean plane
    #     target = self.ellipsoid.transform_vec(point)
    #     crossing_result = plane_crossing.find(target)
    #     if crossing_result is None:
    #         # Target is out of search interval
    #         return None

    #     # Find approximately the pixel along this sensor line
    #     pixel_crossing = SensorPixelCrossing(
    #         sensor,
    #         plane_crossing.get_mean_plane_normal(),
    #         crossing_result.get_target_direction(),
    #         self.MAX_EVAL,
    #         self.COARSE_INVERSE_LOCATION_ACCURACY,
    #     )

    #     coarse_pixel = pixel_crossing.locate_pixel(crossing_result.get_date())
    #     if math.isnan(coarse_pixel):
    #         # Target is out of search interval
    #         return None

    #     # Fix line by considering the closest pixel exact position and line-of-sight
    #     # (this pixel might point towards a direction slightly above or below the mean sensor plane)
    #     low_index = max(0, min(sensor.get_nb_pixels() - 2, float(np.floor(coarse_pixel))))
    #     low_los = sensor.get_los_derivatives(crossing_result.get_date(), low_index, generator)
    #     high_los = sensor.get_los_derivatives(crossing_result.get_date(), low_index + 1, generator)
    #     local_z = FieldVector3D.crossProduct(low_los, high_los).normalize()
    #     beta = FieldVector3D.dotProduct(crossing_result.get_target_direction(), local_z).acos()
    #     s_var = FieldVector3D.dotProduct(crossing_result.get_target_direction_derivative(), local_z)
    #     minus_beta_der = s_var.divide(s_var.multiply(s_var).subtract(1).negate().sqrt())
    #     delta_l = beta.subtract(0.5 * float(np.pi)).divide(minus_beta_der)
    #     fixed_line = delta_l.add(crossing_result.get_line())
    #     fixed_direction = FieldVector3D(
    #         delta_l.getField().getOne(),
    #         crossing_result.get_target_direction(),
    #         delta_l,
    #         crossing_result.get_target_direction_derivative(),
    #     ).normalize()

    #     # Fix neighbouring pixels
    #     fixed_date = sensor.get_date(fixed_line.getValue())
    #     fixed_x = sensor.get_los_derivatives(fixed_date, low_index, generator)
    #     fixed_z = FieldVector3D.crossProduct(
    # fixed_x,
    # sensor.get_los_derivatives(fixed_date, low_index + 1, generator))
    #     fixed_y = FieldVector3D.crossProduct(fixed_z, fixed_x)

    #     # Fix pixel
    #     h_y = FieldVector3D.dotProduct(high_los, fixed_y)
    #     h_x = FieldVector3D.dotProduct(high_los, fixed_x)
    #     pixel_width = h_y.atan2(h_x)
    #     f_y = FieldVector3D.dotProduct(fixed_direction, fixed_y)
    #     f_x = FieldVector3D.dotProduct(fixed_direction, fixed_x)
    #     alpha = f_y.atan2(f_x)
    #     fixed_pixel = alpha.divide(pixel_width).add(low_index)

    #     ret = MathArrays.buildArray(fixed_pixel.getField(), 2)
    #     ret[0] = fixed_line
    #     ret[1] = fixed_pixel

    #     return ret
