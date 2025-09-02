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

"""pyrugged math functions"""

import sys
from typing import Tuple, Union

import numpy as np
from cython.cimports.libc import math

cimport numpy as np

import cython
from scipy import linalg
try:
    from org.hipparchus.geometry.euclidean.threed import Vector3D
    from org.orekit.frames import StaticTransform, Transform
except ModuleNotFoundError as emnfe:
    raise ImportError("Call pyrugged.configuration.init_orekit.init_orekit() first") from emnfe

np.import_array()

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def to_array(x, y, z) -> np.ndarray:
    return np.array([x, y, z], dtype=float)

def to_array_v(v) -> np.ndarray:
    return np.array(v, dtype=float)

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def dot(v1: np.ndarray, v2: np.ndarray) -> Union[cython.double, np.ndarray]:
    """
    Dot product between two vectors. The input vectors are expected to have 3D coordinates,
    with shape: (3, ...)
    """
    v1 = np.float128(v1)
    v2 = np.float128(v2)
    return np.asarray(v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2], dtype="float64")

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def dot_n(double[:, :] v1,double[:, :] v2) -> Union[cython.double, np.ndarray]:
    """
    Dot product between two vectors. The input vectors are expected to have 3D coordinates,
    with shape: (N, 3). This implementation will avoid a full copy of input vectors to float128.
    """
    cdef:
        Py_ssize_t idx
        long double v1_x, v1_y, v1_z, v2_x, v2_y, v2_z
        Py_ssize_t size = v1.shape[0]
        double[:] out_view

    assert v1.shape[0] == v2.shape[0]
    assert v1.shape[1] == 3, f"Last dimension is different from 3: {v1.shape[1]}"
    assert v2.shape[1] == 3, f"Last dimension is different from 3: {v2.shape[1]}"
    
    output = np.zeros((size,), dtype="float64")
    out_view = output
    
    for idx in range(size):
        v1_x = v1[idx, 0]
        v1_y = v1[idx, 1]
        v1_z = v1[idx, 2]
        
        v2_x = v2[idx, 0]
        v2_y = v2[idx, 1]
        v2_z = v2[idx, 2]
        
        out_view[idx] = v1_x*v2_x + v1_y*v2_y + v1_z*v2_z

    return output

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def cross(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    v1 = np.float128(v1)
    v2 = np.float128(v2)
    return np.array([v1[1] * v2[2] - v1[2] * v2[1],
                     v1[2] * v2[0] - v1[0] * v2[2],
                     v1[0] * v2[1] - v1[1] * v2[0]],
                    dtype=float)


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def cross_n(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    cdef:
        Py_ssize_t idx
        Py_ssize_t size = v1.shape[0]
        long double v1_x, v1_y, v1_z, v2_x, v2_y, v2_z
        double[:,:] out_view

    output = np.zeros((size, 3), dtype="float64")
    out_view = output

    for idx in range(size):
        v1_x = v1[idx, 0]
        v1_y = v1[idx, 1]
        v1_z = v1[idx, 2]
        
        v2_x = v2[idx, 0]
        v2_y = v2[idx, 1]
        v2_z = v2[idx, 2]
        
        out_view[idx,0] = v1_y * v2_z - v1_z * v2_y
        out_view[idx,1] = v1_z * v2_x - v1_x * v2_z
        out_view[idx,2] = v1_x * v2_y - v1_y * v2_x

    return output


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)
cdef cython.double normalize_angle_c(angle: cython.double, center: cython.double) noexcept:

    cdef double two_pi = 2.0 * math.pi
    return angle - two_pi * math.floor((angle + math.pi - center) / two_pi)


def normalize_angle(angle: cython.double, center: cython.double) -> cython.double:
    """
    Normalize an angle in a 2π-wide interval around a center value.
    This method has three main uses:

    * normalize an angle between 0 and 2π: a = normalize_angle(a, math.pi)
    * normalize an angle between -π and +π: a = normalize_angle(a, 0.0)
    * compute the angle between two defining angular positions: a = normalize_angle(end, start) - start

    Note that due to numerical accuracy and since pi; cannot be represented exactly, the result interval is
    closed, it cannot be half-closed as would be more satisfactory in a purely mathematical view.

    Parameters
    ----------
        angle: angle to normalize
        center: center of the desired 2&pi; interval for the result

    Returns
    -------
         a-2k*π with integer k so that center-π <= a-2k*π <= center+π
    """
    return normalize_angle_c(angle,center)


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def normalize_angle_vec(angle: np.ndarray, center: Union[float, np.ndarray]) -> np.ndarray:
    two_pi = 2.0 * np.pi
    return angle - two_pi * np.floor((angle + np.pi - center) / two_pi)

cdef cython.int get_exponent_c(double float_value) noexcept:
    """Get IEEE-754 exponent from non zero double-precision float number, assuming little endian"""

    cdef:
        cython.int exp
        unsigned char *buf = <unsigned char *>&float_value
        unsigned short raw_exp = (<unsigned short *>(buf+6))[0]
    
    raw_exp = (raw_exp >> 4) & 0x07ff
    exp = raw_exp - 1023
    return exp

def get_exponent(float_value: cython.double) -> cython.int:
    return get_exponent_c(float_value)


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def get_norm(v: np.ndarray) -> Union[cython.double, np.ndarray]:
    return np.sqrt(get_norm_sq(v))

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def get_norm_sq(v: np.ndarray) -> Union[cython.double, np.ndarray]:
    return dot(v, v)


def get_norm_n(v: np.ndarray) -> Union[cython.double, np.ndarray]:
    return np.sqrt(get_norm_sq_n(v))


def get_norm_sq_n(v: np.ndarray) -> Union[cython.double, np.ndarray]:
    return dot_n(v, v)


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def angle(v1: np.ndarray, v2: np.ndarray) -> cython.double:
    norm_product = get_norm(v1) * get_norm(v2)
    if norm_product == 0:
        raise RuntimeError

    dot_p = dot(v1, v2)
    threshold = norm_product * 0.9999
    if dot_p < -threshold or dot_p > threshold:
        v3 = cross(v1, v2)
        if dot_p >= 0:
            return math.asin(get_norm(v3) / norm_product)
        return math.pi - math.asin(get_norm(v3) / norm_product)

    return math.acos(dot_p / norm_product)

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def distance(v1: np.ndarray, v2:np.ndarray) -> Union[cython.double, np.ndarray]:
    v1 = np.float128(v1)
    v2 = np.float128(v2)
    dx = v2[0] - v1[0]
    dy = v2[1] - v1[1]
    dz = v2[2] - v1[2]
    return np.sqrt(dx * dx + dy * dy + dz * dz, dtype=float)

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def orthogonal(v: np.ndarray) -> np.ndarray:
    threshold = 0.6 * get_norm(v)
    if threshold == 0:
        raise RuntimeError

    if math.fabs(v[0]) <= threshold:
        inverse = 1. / math.sqrt(v[1] * v[1] + v[2] * v[2])
        return to_array(0, (inverse * v[2]), (-inverse * v[1]))
    elif math.fabs(v[1]) <= threshold:
        inverse = 1. / math.sqrt(v[0] * v[0] + v[2] * v[2])
        return to_array((-inverse * v[2]), 0, (inverse * v[0]))

    inverse = 1. / math.sqrt(v[0] * v[0] + v[1] * v[1])
    return to_array((inverse * v[1]), (-inverse * v[0]), 0)

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def compute_distance_in_meter_from_points(earth_radius: cython.double, gp_1: Tuple, gp_2: Tuple) -> cython.double:
    """Compute distance in meters between two geodetics coordinates.

    Parameters
    ----------
        earth_radius : earth radius
        gp_1 : first geodetic coordinates
        gp_2 : second geodetic coordinates

    Returns
    -------
        distance between geodetic points

    """

    p_1 = init_angle(gp_1[0], gp_1[1])
    p_2 = init_angle(gp_2[0], gp_1[1])

    return earth_radius * angle(p_1, p_2)

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def interpolate_func(t_val: cython.double,
                     tile_p: cython.double[:],
                     dx_p: cython.double,
                     dy_p: cython.double,
                     los: cython.double[:],
                     latitude_step: cython.double,
                     longitude_step: cython.double,
                     tolerance: cython.double,
                     ) -> np.ndarray:

    cdef double[3] p_res
    interpolate_func_c(t_val,
                     tile_p,
                     dx_p,
                     dy_p,
                     los,
                     latitude_step,
                     longitude_step,
                     tolerance, p_res)

    return np.asarray(p_res)


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)
cdef void interpolate_func_c(t_val: cython.double,
                             tile_p: cython.double[:],
                             dx_p: cython.double,
                             dy_p: cython.double,
                             los: cython.double[:],
                             latitude_step: cython.double,
                             longitude_step: cython.double,
                             tolerance: cython.double,
                             double* p_res) noexcept:

    if math.isinf(t_val):
        for i in range(3):
            p_res[i] = math.NAN

    cdef double d_x = dx_p + t_val * los[1] / longitude_step
    cdef double d_y = dy_p + t_val * los[0] / latitude_step

    if (
            d_x >= -tolerance
            and d_x <= 1 + tolerance
            and d_y >= -tolerance
            and d_y <= 1 + tolerance
    ):
        p_res[0] = tile_p[0] + t_val * los[0]
        p_res[1] = tile_p[1] + t_val * los[1]
        p_res[2] = tile_p[2] + t_val * los[2]
    else:
        p_res[0] = math.NAN
        p_res[1] = math.NAN
        p_res[2] = math.NAN


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)
def cell_intersection_func(dx_a: cython.double,
                           dx_b: cython.double,
                           dy_a: cython.double,
                           dy_b: cython.double,
                           dz_a: cython.double,
                           dz_b: cython.double,
                           los: cython.double[:],
                           tile_p: cython.double[:],
                           x_00: cython.double,
                           z_00: cython.double,
                           z_01: cython.double,
                           z_10: cython.double,
                           z_11: cython.double,
                           latitude_step: cython.double,
                           longitude_step: cython.double,
                           tolerance: cython.double
                           ) -> np.ndarray:

    cdef double[3] res
    epsilon = sys.float_info.epsilon
    cell_intersection_func_c(dx_a,
                                dx_b,
                                dy_a,
                                dy_b,
                                dz_a,
                                dz_b,
                                los,
                                tile_p,
                                x_00,
                                z_00,
                                z_01,
                                z_10,
                                z_11,
                                latitude_step,
                                longitude_step,
                                tolerance,
                                epsilon,
                                res
                                )

    if math.isnan(res[0]):
        return None
    else:
        return np.asarray(res)

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)
@cython.exceptval(check=False)
cdef void cell_intersection_func_c(dx_a: cython.double,
                           dx_b: cython.double,
                           dy_a: cython.double,
                           dy_b: cython.double,
                           dz_a: cython.double,
                           dz_b: cython.double,
                           los: cython.double[:],
                           tile_p: cython.double[:],
                           x_00: cython.double,
                           z_00: cython.double,
                           z_01: cython.double,
                           z_10: cython.double,
                           z_11: cython.double,
                           latitude_step: cython.double,
                           longitude_step: cython.double,
                           tolerance: cython.double,
                           epsilon: cython.double,
                           double *res) noexcept:

    cdef double[3] p_1
    cdef double[3] p_2
    d_y = dy_a - dy_b
    d_x = dx_a - dx_b
    dydx_a = d_y * dx_a
    dxdy_a = d_x * dy_a
    sumdtoda = dydx_a + dxdy_a
    u_val = d_x * d_y * (z_00 - z_10 - z_01 + z_11)
    v_val = (d_x + d_y - sumdtoda) * z_00 + (sumdtoda - d_x) * z_10 + (sumdtoda - d_y) * z_01 - sumdtoda * z_11
    w_val = (1 - dx_a) * ((1 - dy_a) * z_00 + dy_a * z_01) + dx_a * ((1 - dy_a) * z_10 + dy_a * z_11)
    # Subtract linear z_val from line_of_sight
    # z_DEM(t) - z_LOS(t) = a t² + b t + c
    a_val = u_val
    b_val = v_val + dz_a - dz_b
    c_val = w_val - dz_a
    # Solve the equation
    if math.fabs(a_val) <= epsilon * math.fabs(c_val):
        # The equation degenerates to a linear (or constant) equation

        if b_val == 0.0:
            if c_val == 0.0:
                # Quotient would return NaN
                t_1 = 0.0
            else:
                # Quotient would return inf
                t_1 = math.INFINITY
        else:
            t_1 = -c_val / b_val

        t_2 = math.INFINITY
        interpolate_func_c(float(t_1), tile_p, dx_a, dy_a, los, latitude_step, longitude_step, tolerance, p_1)
        interpolate_func_c(float(t_2), tile_p, dx_a, dy_a, los, latitude_step, longitude_step, tolerance, p_2)
        if math.isnan(p_1[0]):
            for i in range(3):
                res[i] = p_2[i]
        elif math.isnan(p_2[0]):
            for i in range(3):
                res[i] = p_1[i]
        elif t_1 <= t_2:
            for i in range(3):
                res[i] = p_1[i]
        else:
            for i in range(3):
                res[i] = p_2[i]
    else:
        # The equation is quadratic
        b_2 = b_val * b_val
        fac = 4 * a_val * c_val
        if b_2 < fac:
            # No intersection at all
            for i in range(3):
                res[i] = math.NAN
        else:
            s_val = math.sqrt(b_2 - fac)
            t_1 = (s_val - b_val) / (2 * a_val) if b_val < 0 else -2 * c_val / (b_val + s_val)
            if t_1 != 0:
                t_2 = c_val / (a_val * t_1)
            else:
                t_2 = math.INFINITY
            interpolate_func_c(float(t_1), tile_p, dx_a, dy_a, los, latitude_step, longitude_step, tolerance, p_1)
            interpolate_func_c(float(t_2), tile_p, dx_a, dy_a, los, latitude_step, longitude_step, tolerance, p_2)
            # Select the first point along line-of-sight
            if math.isnan(p_1[0]):
                for i in range(3):
                    res[i] = p_2[i]
            elif math.isnan(p_2[0]):
                for i in range(3):
                    res[i] = p_1[i]
            elif t_1 <= t_2:
                for i in range(3):
                    res[i] = p_1[i]
            else:
                for i in range(3):
                    res[i] = p_2[i]

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def cell_intersection_vec_func(dx_a: cython.double[:],
                               dx_b: cython.double[:],
                               dy_a: cython.double[:],
                               dy_b: cython.double[:],
                               dz_a: cython.double[:],
                               dz_b: cython.double[:],
                               los: np.ndarray,
                               tile_p: cython.double[:,:],
                               x_00: cython.double[:],
                               z_00: cython.double[:],
                               z_01: cython.double[:],
                               z_10: cython.double[:],
                               z_11: cython.double[:],
                               latitude_step: cython.double,
                               longitude_step: cython.double,
                               tolerance: cython.double
                               ) -> np.ndarray:

    length = dx_a.shape[0]
    epsilon = sys.float_info.epsilon
    res_out = np.empty((length, 3))
    cdef double[:, :] res = res_out
    cdef double[3] res_uni
    cdef double[:] los_single
    cdef double[:, :] los_vec
    
    if los.ndim == 1:
        los_single = los
        for i in range(length):
            cell_intersection_func_c(dx_a[i],
                                    dx_b[i],
                                    dy_a[i],
                                    dy_b[i],
                                    dz_a[i],
                                    dz_b[i],
                                    los_single,
                                    tile_p[i, :],
                                    x_00[i],
                                    z_00[i],
                                    z_01[i],
                                    z_10[i],
                                    z_11[i],
                                    latitude_step,
                                    longitude_step,
                                    tolerance,
                                    epsilon,
                                    &res[i, 0],
                                    )
    else:
        los_vec = los
        for i in range(length):
            cell_intersection_func_c(dx_a[i],
                                    dx_b[i],
                                    dy_a[i],
                                    dy_b[i],
                                    dz_a[i],
                                    dz_b[i],
                                    los_vec[i, :],
                                    tile_p[i, :],
                                    x_00[i],
                                    z_00[i],
                                    z_01[i],
                                    z_10[i],
                                    z_11[i],
                                    latitude_step,
                                    longitude_step,
                                    tolerance,
                                    epsilon,
                                    &res[i, 0],
                                    )

    return res_out

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.exceptval(check=False)
@cython.cdivision(True)
def transform_from_frame_cy(double[:,:] points,
                                 POL_EQU_ANGULAR_THRESHOLD: cython.double,
                                 _radius_2: cython.double,
                                 c_val: cython.double,
                                 a_val: cython.double,
                                 _e_2: cython.double,
                                 _g_val: cython.double,
                                 _ap_2: cython.double
                                 ) -> np.ndarray:

    cdef:
        Py_ssize_t length = points.shape[0]
        Py_ssize_t i = 0
        double[:,:] out_view
        double r2_val, r_val, z_val, lambda_val, osculating_radius, evolute_cusp_z, delta_r
        double phi, h_val, evolute_cusp_r, r_close, z_close, eps_h, abs_z, zc_val, sn_val, sn_2
        double cn_val, cn_2, an_2, an_val, bn_val, old_sn, old_cn, old_phi, old_h, an_3, c_sn_cn, cc_val
        cython.int exp
        double eps_phi = 1.0e-15
        double c_tf = a_val * _e_2  # 'c' param for Toshio Fukushima
    
    output = np.zeros((length, 3), dtype="float64")
    out_view = output

    for i in range(length):
        r2_val = points[i, 0] * points[i, 0] + points[i, 1] * points[i, 1]
        r_val = math.sqrt(r2_val)
        z_val = points[i, 2]
        lambda_val = math.atan2(points[i, 1], points[i, 0])
        if r_val <= POL_EQU_ANGULAR_THRESHOLD * math.fabs(z_val):
            # The point is almost on the polar axis, approximate the ellipsoid with
            # the osculating sphere whose center is at evolute cusp along polar axis
            osculating_radius = _radius_2 / c_val
            evolute_cusp_z = math.copysign(a_val * _e_2 / _g_val, -z_val)
            delta_z = z_val - evolute_cusp_z
    
            # We use π/2 - atan(r/Δz) instead of atan(Δz/r) for accuracy purposes, as r is much smaller than Δz
            phi = math.copysign(0.5 * math.pi - math.atan(r_val / math.fabs(delta_z)), delta_z)
            h_val = math.hypot(delta_z, r_val) - osculating_radius
    
        elif math.fabs(z_val) <= POL_EQU_ANGULAR_THRESHOLD * r_val:
            # The point is almost on the major axis
            osculating_radius = _ap_2 / a_val
            evolute_cusp_r = a_val * _e_2
            delta_r = r_val - evolute_cusp_r
    
            if delta_r >= 0:
                # The point is outside of the ellipse evolute, approximate the ellipse
                # with the osculating circle whose center is at evolute cusp along major axis
                phi = 0.0 if delta_r == 0 else math.atan(z_val / delta_r)
                h_val = math.hypot(delta_r, z_val) - osculating_radius
    
            else:
                # The point is on the part of the major axis within ellipse evolute
                # we can compute the closest ellipse point analytically, and it is NOT near the equator
                r_close = r_val / _e_2
                z_close = math.copysign(_g_val * math.sqrt(_radius_2 - r_close * r_close), z_val)
                phi = math.atan((z_close - z_val) / (r_close - r_val))
                h_val = -math.hypot(r_val - r_close, z_val - z_close)
    
        else:
            # Use Toshio Fukushima method, with several iterations
            eps_h = 1.0e-14 * max(a_val, math.sqrt(r2_val + z_val * z_val))
            
            abs_z = math.fabs(z_val)
            zc_val = _g_val * abs_z
    
            sn_val = abs_z
            sn_2 = sn_val * sn_val
            cn_val = _g_val * r_val
            cn_2 = cn_val * cn_val
            an_2 = cn_2 + sn_2
            an_val = math.sqrt(an_2)
            bn_val = 0
            phi = math.INFINITY
            h_val = -math.INFINITY
    
            # This usually converges in 2 iterations
            for _ in range(10):
                old_sn = sn_val
                old_cn = cn_val
                old_phi = phi
                old_h = h_val
                an_3 = an_2 * an_val
                c_sn_cn = c_tf * sn_val * cn_val
    
                bn_val = 1.5 * c_sn_cn * ((r_val * sn_val - zc_val * cn_val) * an_val - c_sn_cn)
                sn_val = (zc_val * an_3 + c_tf * sn_2 * sn_val) * an_3 - bn_val * sn_val
                cn_val = (r_val * an_3 - c_tf * cn_2 * cn_val) * an_3 - bn_val * cn_val
    
                if sn_val * old_sn < 0 or cn_val < 0:
                    # The Halley iteration went too far, we restrict it and iterate again
                    while sn_val * old_sn < 0 or cn_val < 0:
                        sn_val = (sn_val + old_sn) / 2
                        cn_val = (cn_val + old_cn) / 2
    
                else:
                    # Rescale components to avoid overflow when several iterations are used
                    exp = (get_exponent_c(sn_val) + get_exponent_c(cn_val)) / 2
                    sn_val = sn_val * math.pow(2, -exp)
                    cn_val = cn_val * math.pow(2, -exp)
    
                    sn_2 = sn_val * sn_val
                    cn_2 = cn_val * cn_val
                    an_2 = cn_2 + sn_2
                    an_val = math.sqrt(an_2)
    
                    cc_val = _g_val * cn_val
                    h_val = (r_val * cc_val + abs_z * sn_val - a_val * _g_val * an_val) / math.sqrt(an_2 - _e_2 * cn_2)
    
                    if math.fabs(old_h - h_val) < eps_h:
                        phi = math.copysign(math.atan(sn_val / cc_val), z_val)
                        if math.fabs(old_phi - phi) < eps_phi:
                            break
    
        out_view[i, 0] = phi
        out_view[i, 1] = lambda_val
        out_view[i, 2] = h_val

    return output

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def scalar_multiply(a: cython.double, v: np.ndarray) -> np.ndarray:
    r = a * v
    return r


def init_angle(alpha: cython.double, delta: cython.double) -> np.ndarray:
    cos_alpha = math.cos(alpha)
    sin_alpha = math.sin(alpha)
    cos_delta = math.cos(delta)
    sin_delta = math.sin(delta)
    x = cos_alpha * cos_delta
    y = sin_alpha * cos_delta
    z = sin_delta
    return np.array([x, y, z])

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def find_fixed_pixel_func(fixed_direction: np.ndarray,
                          fixed_x: np.ndarray,
                          fixed_x_p1: np.ndarray,
                          high_los: np.ndarray,
                          low_index: cython.int) -> cython.double:

    fixed_z = cross(fixed_x, fixed_x_p1)
    fixed_y = cross(fixed_z, fixed_x)
    # Fix pixel
    pixel_width = math.atan2(dot(high_los, fixed_y), dot(high_los, fixed_x))
    alpha = math.atan2(dot(fixed_direction, fixed_y), dot(fixed_direction, fixed_x))
    fixed_pixel = low_index + alpha / pixel_width

    return fixed_pixel

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def find_fixed_line_func(high_los: np.ndarray,
                         line: cython.double,
                         low_los: np.ndarray,
                         target_direction: np.ndarray,
                         target_direction_derivative: np.ndarray):

    local_z = cross(low_los, high_los)
    local_z = local_z / get_norm(local_z)
    beta = math.acos(dot(target_direction, local_z))
    s_val = dot(target_direction_derivative, local_z)
    beta_der = -s_val / math.sqrt(1 - s_val * s_val)
    delta_l = (0.5 * math.pi - beta) / beta_der
    fixed_line = line + delta_l
    fixed_direction = compute_linear_combination_2(1.0, target_direction, delta_l, target_direction_derivative)
    fixed_direction = fixed_direction / get_norm(fixed_direction)

    return fixed_direction, fixed_line

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def matrix_solve(m_matrix: np.ndarray, v_vector: np.ndarray) -> np.ndarray:
    m_q, m_r = linalg.qr(m_matrix, mode="economic")
    m_qb = np.matmul(m_q.T, v_vector)
    v_x = linalg.solve(m_r, m_qb)
    return v_x

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def compute_svd(matrix):
    m_u, _, _ = linalg.svd(matrix, full_matrices=False)
    return m_u

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def normalized_dot(u_vector: np.ndarray, u_dot: np.ndarray) -> np.ndarray:
    """Compute the derivative of normalized vector.

    Parameters
    ----------
        u_vector : base vector
        u_dot : derivative of the base vector

    Returns
    -------
        result : vDot, where v = u / ||u||
    """

    n_val = get_norm(u_vector)
    return compute_linear_combination_2((1.0 / n_val), u_dot,
                                     (-dot(u_vector, u_dot) / (n_val * n_val * n_val)),
                                     u_vector)

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def compute_linear_combination_2(a1: cython.double, u1: np.ndarray,
                              a2: cython.double, u2: np.ndarray):
    r = np.float128(a1 * u1) + np.float128(a2 * u2)
    return np.array(r, dtype=float)


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def compute_low_prec_linear_combination_2(a1: cython.double, u1: np.ndarray,
                              a2: cython.double, u2: np.ndarray):
    r = a1 * u1 + a2 * u2
    return r


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def compute_linear_combination_3(a1: cython.double, u1: np.ndarray,
                              a2: cython.double, u2: np.ndarray,
                              a3: cython.double, u3: np.ndarray):
    r = np.float128(a1 * u1) + np.float128(a2 * u2) + np.float128(a3 * u3)
    return np.array(r, dtype=float)

def compute_linear_combination_2_arr(a1: np.ndarray, u1: Union[list, np.ndarray],
                                     a2: np.ndarray, u2: Union[list, np.ndarray]) \
    -> np.ndarray:
    """Compute linear combination a1 * u1 + a2 * u2 in high precision.

     Parameters
     ----------
         a1 : coefficients
         u1 : list of vectors
         a2 : coefficients
         u2 : list of vectors

     Returns
     -------
         linear combination

     """
    a1 = a1.astype(np.float128)
    a2 = a2.astype(np.float128)
    u1 = u1.astype(np.float128)
    u2 = u2.astype(np.float128)
    
    res = (u1 * a1[:, np.newaxis] + u2 * a2[:, np.newaxis]).astype(float)

    # res = list()
    # for i in range(np.size(a1)):
    #     v1 = np.float128(a1[i]) * np.float128(u1[i])
    #     v2 = np.float128(a2[i]) * np.float128(u2[i])
    #     r = v1 + v2
    #     res.append(np.array(r, dtype=float))
    return res

def compute_low_prec_linear_combination_2_arr(a1: np.ndarray, u1: Union[list, np.ndarray],
                                     a2: np.ndarray, u2: Union[list, np.ndarray]) \
    -> np.ndarray:
    """Compute linear combination a1 * u1 + a2 * u2 in low precision.

     Parameters
     ----------
         a1 : coefficients
         u1 : list of vectors
         a2 : coefficients
         u2 : list of vectors

     Returns
     -------
         linear combination

     """
    res = u1 * a1[:, np.newaxis] + u2 * a2[:, np.newaxis]
    # res = list()
    # for i in range(np.size(a1)):
    #     r = a1[i] * u1[i] + a2[i] * u2[i]
    #     res.append(r)
    return res

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def rotate(q: np.ndarray, los: np.ndarray) -> np.ndarray:
    s = q[1] * los[0] + q[2] * los[1] + q[3] * los[2]
    return np.array([2 * (q[0] * (los[0] * q[0] - (q[2] * los[2] - q[3] * los[1])) + s * q[1]) - los[0],
                     2 * (q[0] * (los[1] * q[0] - (q[3] * los[0] - q[1] * los[2])) + s * q[2]) - los[1],
                     2 * (q[0] * (los[2] * q[0] - (q[1] * los[1] - q[2] * los[0])) + s * q[3]) - los[2]])
    # s = np.sum(q[1:] * los)
    # return 2. * (q[0] * (los * q[0] - (np.roll(q[1:], -1) * np.roll(los, 1) -
    #                                              np.roll(q[1:], -2) * np.roll(los, -1)))
    #              + s * q[1:]) - los





@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)
def convert_los_from_point_func(p_3d_0: cython.double,
                                    p_3d_1: cython.double,
                                    p_3d_2: cython.double,
                                    _a_2: cython.double,
                                    _b_2: cython.double) -> (double, double):

    cdef double r_val
    cdef double rho

    # Local radius of curvature in the East-West direction (parallel)
    r_val = math.hypot(p_3d_0, p_3d_1)
    # Local radius of curvature in the North-South direction (meridian)
    b2r = _b_2 * r_val
    b4r2 = b2r * b2r
    a2z = _a_2 * p_3d_2
    a4z2 = a2z * a2z
    q_val = a4z2 + b4r2
    rho = q_val * math.sqrt(q_val) / (_b_2 * a4z2 + _a_2 * b4r2)

    return r_val, rho



@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)
def convert_los_from_point_vec_func(p_3d_0: cython.double[:],
                                    p_3d_1: cython.double[:],
                                    p_3d_2: cython.double[:],
                                    _a_2: cython.double,
                                    _b_2: cython.double) -> (np.ndarray, np.ndarray):

    cdef int length = p_3d_0.shape[0]
    r_val_out = np.empty(length)
    cdef double[:] r_val = r_val_out
    rho_out = np.empty(length)
    cdef double[:] rho = rho_out

    for i in range(length):
        # Local radius of curvature in the East-West direction (parallel)
        r_val[i] = math.hypot(p_3d_0[i], p_3d_1[i])
        # Local radius of curvature in the North-South direction (meridian)
        b2r = _b_2 * r_val[i]
        b4r2 = b2r * b2r
        a2z = _a_2 * p_3d_2[i]
        a4z2 = a2z * a2z
        q_val = a4z2 + b4r2
        rho[i] = q_val * math.sqrt(q_val) / (_b_2 * a4z2 + _a_2 * b4r2)

    return r_val_out, rho_out



@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)
def transform_from_point_optim(latitudes: np.ndarray,
                        longitudes: np.ndarray,
                        h_vals: np.ndarray,
                        a_val: float,
                        _e_2:float,
                        _g_2:float) -> np.ndarray:
    """
    Transform a surface-relative point to a Cartesian point.

    Parameters
    ----------
        latitudes : surface-relative point latitudes [lat_point1, lat_point2, ..., lat_pointn],
        longitudes : surface-relative points longitudes [longi_point1, longi_point2, ..., longi_pointn]
        warning must be same length as latitudes
        h_vals : surface-relative point altitudes [alt_pix1, alt_pix2, ..., alt_pixn]
        warning must be same length as latitudes

    Returns
    -------
        result : points cartesian coordinates at the same location (but as a cartesian points)
        [x_point1, x_point2,..., x_pointn], [y_point1, y_point2, ..., y_pointn], [z_point1, z_point2, ..., z_pointn]
    """

    len = latitudes.shape[0]
    res_0 = np.empty(len)
    res_1 = np.empty(len)
    res_2 = np.empty(len)

    cdef:
        double[:] latitudes_view = latitudes
        double[:] longitudes_view = longitudes
        double[:] h_vals_view = h_vals
        double[:] res_0_view = res_0
        double[:] res_1_view = res_1
        double[:] res_2_view = res_2
        double sin_lat
        double n_val
        double r_val

    for i in range(len):

        sin_lat = math.sin(latitudes_view[i])
        n_val = a_val / math.sqrt(1.0 - _e_2 * sin_lat * sin_lat)
        r_val = (n_val + h_vals_view[i]) * math.cos(latitudes_view[i])

        res_0_view[i] = r_val * math.cos(longitudes_view[i])
        res_1_view[i] = r_val * math.sin(longitudes_view[i])
        res_2_view[i] = (_g_2 * n_val + h_vals_view[i]) * sin_lat

    return np.array([res_0,res_1,res_2])

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)
@cython.exceptval(check=False)
def normalize_geodetic_point_optim(geodetic_point: np.ndarray, central_longitude: Union[np.ndarray, float] = None) \
        -> np.ndarray:
    """Normalize geodetic point longitude and latitude.

    Returns
    -------
        geodetic_point : point with normalized longitude and latitude
    """

    cdef double pi_2 = math.pi/2.0
    cdef double [:,:] geodetic_point_view
    cdef size_t len = geodetic_point.shape[0]
    cdef double [:] lat_view
    cdef double [:] lon_view
    cdef double [:] lon_longitude_view
    cdef double [:, :] out_view
    cdef size_t len_ll
    cdef int i
    cdef double lon_d, lat_d


    if central_longitude is not None:
        if isinstance(central_longitude,float):
            lon_longitude = np.array([central_longitude])
            len_ll = 1
        else:
            lon_longitude = central_longitude #is an array
            len_ll = np.shape(central_longitude)[0]
    else:
        lon_longitude = np.array([0.])
        len_ll = 1


    if geodetic_point.ndim == 2:

        geodetic_point_view = geodetic_point
        lat = np.empty(len)
        lon = np.empty(len)
        lat_view = lat
        lon_view = lon
        lon_longitude_view = lon_longitude


        for i in range(len):
            lat_view[i] = normalize_angle_c(geodetic_point_view[i, 0], pi_2)

            if lat_view[i]>pi_2:
                lat_view[i] = math.pi - lat_view[i]
                lon_view[i] = normalize_angle_c(geodetic_point_view[i, 1] + math.pi, lon_longitude_view[<int>math.fmod(i,len_ll)])
            else:
                lon_view[i] = normalize_angle_c(geodetic_point_view[i, 1], lon_longitude_view[<int>math.fmod(i,len_ll)])

        return np.array([lat, lon, geodetic_point[:, 2]]).T

    elif isinstance(central_longitude,np.ndarray):
        lat_d = normalize_angle_c(<double>geodetic_point[0], pi_2)
        lon_d = normalize_angle_c(<double>geodetic_point[1], 0.0)
        
        output = np.empty((len_ll, 3), dtype="float64")
        output[:, 0] = lat_d
        output[:, 1] = lon_d
        output[:, 2] = geodetic_point[2]
        out_view = output
        lon_longitude_view = lon_longitude
        
        if lat_d > pi_2:
            for i in range(len_ll):
                out_view[i, 0] = math.pi - lat_d
                out_view[i, 1] = normalize_angle_c(lon_d + math.pi, lon_longitude_view[i])
        else:
            for i in range(len_ll):
                out_view[i, 1] = normalize_angle_c(lon_d, lon_longitude_view[i])

        return output
    else:

        lat_d = normalize_angle_c(<double>geodetic_point[0], pi_2)
        lon_d = normalize_angle_c(<double>geodetic_point[1], 0.0)

        if lat_d > pi_2:
            # Latitude is beyond the pole -> add 180 to longitude

            lat_d = math.pi - lat_d
            lon_d = normalize_angle_c(<double>geodetic_point[1] + math.pi, 0.0)

        if central_longitude is not None:
            lon_d = normalize_angle_c(lon_d, <double>central_longitude)

        return np.array([lat_d, lon_d, <double>geodetic_point[2]])

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def transform_position_arr(transforms: List[Transform], double[:, :] positions) -> np.ndarray:
    """
    Apply a list of StaticTransforms on 3D positions
    
    :param transforms: List of transforms (will be cast to StaticTransform), of size N
    :param positions: array of input positions, shape (N, 3)
    :return: transformed positions, shape (N, 3)
    """
    
    cdef:
        Py_ssize_t idx
        Py_ssize_t size = positions.shape[0]
        double[:, :] out_view

    assert positions.shape[1] == 3, f"Last dimension is different from 3: {positions.shape[1]}"
    
    output = np.zeros((size, 3), dtype="float64")
    out_view = output
    
    for idx in range(size):
        static_transfo = StaticTransform.cast_(transforms[idx])

        pos_in = Vector3D(float(positions[idx, 0]), float(positions[idx, 1]), float(positions[idx, 2]))
        pos_out = static_transfo.transformPosition(pos_in)
        
        out_view[idx, 0] = pos_out.getX()
        out_view[idx, 1] = pos_out.getY()
        out_view[idx, 2] = pos_out.getZ()
    
    return output

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def transform_direction_arr(transforms: List[Transform], directions: np.ndarray) -> np.ndarray:
    """
    Apply a list of StaticTransforms on 3D directions
    
    :param transforms: List of transforms (will be cast to StaticTransform), of size N
    :param directions: array of input directions, shape (N, 3)
    :return: transformed directions, shape (N, 3)
    """
    
    cdef:
        Py_ssize_t idx
        Py_ssize_t size = directions.shape[0]
        double[:, :] out_view

    assert directions.shape[1] == 3, f"Last dimension is different from 3: {directions.shape[1]}"
    
    output = np.zeros((size, 3), dtype="float64")
    out_view = output
    
    for idx in range(size):
        static_transfo = StaticTransform.cast_(transforms[idx])

        vec_in = Vector3D(float(directions[idx, 0]), float(directions[idx, 1]), float(directions[idx, 2]))
        vec_out = static_transfo.transformVector(vec_in)
        
        out_view[idx, 0] = vec_out.getX()
        out_view[idx, 1] = vec_out.getY()
        out_view[idx, 2] = vec_out.getZ()
    
    return output
