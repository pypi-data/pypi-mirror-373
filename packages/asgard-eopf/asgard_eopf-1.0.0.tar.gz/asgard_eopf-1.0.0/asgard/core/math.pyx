#!/usr/bin/env python
# coding: utf8
#
# Copyright 2023 CS GROUP
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
Module for mathematic routines
"""

import math
from typing import Tuple

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

cimport cython
from libc.math cimport acos, cos, sin, sqrt

TWO_PI = 2.0 * np.pi

RADIANS_SCALING_FACTORS = {
    "arcsecond": np.pi / 180 / 3600,
    "arcseconds": np.pi / 180 / 3600,
    "arcminute": np.pi / 180 / 60,
    "arcminutes": np.pi / 180 / 60,
    "degree": np.pi / 180,
    "degrees": np.pi / 180,
    "degrees_north": np.pi / 180,
    "degrees_east": np.pi / 180,
    "radians": 1.0,
    "mrad": 1.0 / 1000.0,
    "milliradian": 1.0 / 1000.0,
}

cdef double quat_norm(double* quat):
    """
    Compute quaternion norm
    """
    return sqrt(quat[0]*quat[0] + quat[1]*quat[1] + quat[2]*quat[2] + quat[3]*quat[3])

def slerp_n(positions: np.ndarray, table: np.ndarray) -> np.ndarray:
    """
    Quaternion SLERP interpolation. For each input position, a SLERP interpolation is computed
    from the table between the two consecutive rows around the input position. Examples:

        - position = 2.4  => quat = SLERP( 0.4, table[2], table[3] )
        - position = -0.2 => quat = SLERP( -0.2, table[0], table[1] )

    :param positions: positions to interpolate in the quaternion table (first axis), 1D array-like
    :param table: quaternion table, 2D array-like, expected shape is (n, 4)
    :return: interpolated quaternions
    """

    nb_pos = len(positions)
    nb_quat = len(table)
    assert nb_quat > 1
    ipos = np.floor(positions).clip(0, nb_quat - 2)
    # frac = positions - ipos
    # output = np.zeros((nb_pos, 4), dtype="float64")
    # for idx in range(nb_pos):
    #     output[idx, :] = slerp(frac[idx], table[int(ipos[idx])], table[int(ipos[idx]) + 1])
    frac = positions - ipos
    quat1 = table[ipos.astype(int)]
    quat2 = table[ipos.astype(int) + 1]
    output = slerp_vec(frac, quat1, quat2)

    return output


def slerp(frac: float, quat1, quat2) -> np.ndarray:
    """
    Quaternion SLERP interpolation between 2 quaternions

    :param frac: fraction to interpolate between quat1 and quat2
    :param quat1: first quaternion (size 4)
    :param quat2: second quaternion (size 4)
    :return: interpolated quaternion
    """

    costheta0 = np.dot(quat1, quat2)
    if costheta0 > 0.9995:
        quat = (1 - frac) * quat1 + frac * quat2
    else:
        quat3 = quat2 - costheta0 * quat1
        quat3 /= np.linalg.norm(quat3)
        theta = frac * math.acos(costheta0)
        quat = math.cos(theta) * quat1 + math.sin(theta) * quat3
    quat /= np.linalg.norm(quat)

    return quat


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
@cython.cdivision(True)
def slerp_vec(frac: np.ndarray, quat1, quat2) -> np.ndarray:
    """
    Quaternion SLERP interpolation between 2 quaternions

    :param frac: (np.double) fractions to interpolate between quat1 and quat2 (size N)
    :param quat1: (np.double) first quaternions, size (N,4)
    :param quat2: (np.double) second quaternions, size (N,4)
    :return: interpolated quaternions, size (N,4)
    """
    
    cdef:
        double[:] fr_view = frac
        double[:,:] q1_view = quat1
        double[:,:] q2_view = quat2
        Py_ssize_t size = frac.shape[0]
        Py_ssize_t x = 0
        double[4] tmp_quat
        double costheta0
        double theta
        double cos_theta
        double sin_theta
        double inv_norm

    assert quat1.shape == (size, 4)
    assert quat2.shape == (size, 4)

    quat = np.zeros_like(quat1)
    cdef double [:,:] out_view = quat
    
    for x in range(size):
        costheta0 = q1_view[x,0]*q2_view[x,0]+q1_view[x,1]*q2_view[x,1]+q1_view[x,2]*q2_view[x,2]+q1_view[x,3]*q2_view[x,3]
        if costheta0 > 0.9995:
            out_view[x, 0] = (1-fr_view[x])*q1_view[x,0] + fr_view[x] * q2_view[x,0]
            out_view[x, 1] = (1-fr_view[x])*q1_view[x,1] + fr_view[x] * q2_view[x,1]
            out_view[x, 2] = (1-fr_view[x])*q1_view[x,2] + fr_view[x] * q2_view[x,2]
            out_view[x, 3] = (1-fr_view[x])*q1_view[x,3] + fr_view[x] * q2_view[x,3]
        else:
            tmp_quat[0] = q2_view[x,0] - costheta0 * q1_view[x,0]
            tmp_quat[1] = q2_view[x,1] - costheta0 * q1_view[x,1]
            tmp_quat[2] = q2_view[x,2] - costheta0 * q1_view[x,2]
            tmp_quat[3] = q2_view[x,3] - costheta0 * q1_view[x,3]
            
            inv_norm = 1.0 / quat_norm(tmp_quat)
            theta = fr_view[x] * acos(costheta0)
            cos_theta = cos(theta)
            sin_theta = sin(theta)

            out_view[x, 0] = cos_theta * q1_view[x,0] + sin_theta * inv_norm * tmp_quat[0]
            out_view[x, 1] = cos_theta * q1_view[x,1] + sin_theta * inv_norm * tmp_quat[1]
            out_view[x, 2] = cos_theta * q1_view[x,2] + sin_theta * inv_norm * tmp_quat[2]
            out_view[x, 3] = cos_theta * q1_view[x,3] + sin_theta * inv_norm * tmp_quat[3]
        
        inv_norm = 1.0 / quat_norm(&out_view[x, 0])
        out_view[x, 0] *= inv_norm
        out_view[x, 1] *= inv_norm
        out_view[x, 2] *= inv_norm
        out_view[x, 3] *= inv_norm
    
    return quat


def quat_to_matrix(quat) -> np.ndarray:
    """
    Convert quaternion to rotation matrix

    :param quat: quaternion (a, b, c, d) with d the real part
    :return: 3x3 rotation matrix
    """

    # pylint: disable=invalid-name
    a = quat[0]
    b = quat[1]
    c = quat[2]
    d = quat[3]
    mat = np.array(
        [
            [
                a * a - b * b - c * c + d * d,
                2 * (a * b + c * d),
                2 * (a * c - b * d),
            ],
            [
                2 * (a * b - c * d),
                -a * a + b * b - c * c + d * d,
                2 * (b * c + a * d),
            ],
            [
                2 * (a * c + b * d),
                2 * (b * c - a * d),
                -a * a - b * b + c * c + d * d,
            ],
        ]
    )
    return mat


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def collapse_siblings(arr: np.ndarray) -> np.ndarray:
    """
    Create a copy of input array (1D) where consecutive identical values are collapsed
    
    :param arr: input 1D array of "float64" type
    :return: output collapsed array
    """
    
    cdef:
        double[:] arr_view = arr
        Py_ssize_t size = arr.shape[0]
        Py_ssize_t x = 0
        Py_ssize_t y = 0
        double prev = arr_view[0] + 1.0
    
    output = np.zeros_like(arr)
    cdef double[:] out_view = output
    
    for x in range(size):
        if arr_view[x] != prev:
            out_view[y] = arr_view[x]
            y+=1
            prev = arr_view[x]
    
    out_view = None
    return np.resize(output, (y,))


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def expand_siblings(arr: np.ndarray, input_collection) -> list:
    """
    Repeat the element in the input collection when siblings are present in the input array.
    
    :param arr: Input array (1D) containing siblings
    :param input_collection: Input collection to expand
    :return: Output collection expanded
    """
    
    cdef:
        double[:] arr_view = arr
        Py_ssize_t size = arr.shape[0]
        Py_ssize_t x = 0
        Py_ssize_t y = 0
        double prev = arr_view[0] + 1.0
    
    output = []
    current_item = None
    for x in range(size):
        if arr_view[x] != prev:
            current_item = input_collection[y]
            y+=1
            prev = arr_view[x]
        output.append(current_item)
    
    return output

def flatten_array(data: np.ndarray, last_dim: int | None = None) -> np.ndarray:
    """
    Reshape an array to flatten it as much as possible. If last_dim is specified, the output shape
    will be (x, last_dim). A check will be made so that the last
    dimension matches on the input array.

    Otherwise, a 1D array is output.

    :param data: input array
    :param last_dim: Freeze last dimension to a given value
    :return: reshaped array
    """
    arr = np.asarray(data)
    if last_dim is not None:
        assert arr.shape[-1] == last_dim
        nb_elem = 1
        for size in arr.shape[:-1]:
            nb_elem *= size
        return arr.reshape((nb_elem, last_dim))
    # default case
    nb_elem = arr.size
    return arr.reshape((nb_elem))


def restore_array(arr: np.ndarray, shape, last_dim: int | None = None) -> np.ndarray:
    """
    Reshape an array to match the input shape. If last_dim is specified, the new shape is
    ('shape', last_dim).

    :param arr: Array to reshape
    :param shape: Target shape
    :param last_dim: Last dimension to append (optional)
    :return: reshaped array
    """
    target_shape = list(shape)
    if last_dim is not None:
        assert arr.shape[-1] == last_dim
        target_shape.append(last_dim)
    elif len(target_shape) == 0:
        return arr
    return arr.reshape(target_shape)


def is_sorted(x: np.ndarray) -> np.bool_:
    """
    O(N) helper function that returns whether a :class:`numpy.ndarray` is sorted.
    """
    return np.all(np.diff(x) >= 0)


def vector3d_to_list(v3d) -> list[float]:
    """
    Converts a :class:`org.hipparchus.geometry.euclidean.threed.Vector3D` into an array.
    """
    return [v3d.getX(), v3d.getY(), v3d.getZ()]


def numerical_jacobian(direct_mapping: callable, coords: np.ndarray, epsilon: int = 1) -> np.ndarray:
    """
    The numerical_jacobian function computes the numerical approximation
    of the Jacobian of a given function f.
    The function uses finite differences to compute the Jacobian,
    which means it approximates the derivatives by taking the difference
    between the function's outputs for slightly perturbed inputs (by one).
    The function returns an np.ndarray of shape:

        (x.shape[0], x.shape[1], x.shape[1])

    where the third dimension represents the Jacobian matrix at each input
    point.
    The jacobian array is initialized to a zero array of the required shape,
    then it's iteratively populated by computing the finite differences.

    For each input point x[i, :], the function computes two perturbed input
    points x_plus_epsilon and x_minus_epsilon by adding and subtracting epsilon
    to/from the j-th component of x[i, :], respectively
    [according to the symmetric difference quotient
    (https://en.wikipedia.org/wiki/Symmetric_derivative) which is known
    to be more numerically stable than the ordinary finite difference formula].

    Then, the function evaluates f at both perturbed input points and computes
    the finite differences, which are used to estimate the partial derivative with
    respect to the j-th component of x[i, :].

    Finally, the estimates are stored in the jacobian array.

    :param callable direct_mapping: a function to compute the Jacobian of.
    :param np.ndarray coords:       an np.ndarray of input points for which to compute the Jacobian.
    :param int, optional epsilon: an integer representing the size of the perturbation applied to the input points (as
                                    the input points are integers). Defaults to 1.
    :return: The Jacobian array
    """

    assert len(coords.shape) == 2

    # prepare deltas for shifted coordinate with symmetric difference: x-epsilon, x+epsilon
    deltas = []
    for j in range(coords.shape[1]):
        delta = np.zeros((coords.shape[1],), dtype=coords.dtype)
        delta[j] = epsilon
        deltas.append(-delta)
        deltas.append(delta)

    # compute coordinates to explore
    shifted_coords = np.stack([coords + delta for delta in deltas], axis=1)
    shifted_flat = shifted_coords.reshape((coords.shape[0] * 2 * coords.shape[1], coords.shape[1]))

    # compute function values on shifted coords
    values_flat = direct_mapping(shifted_flat)

    values = values_flat.reshape((coords.shape[0], coords.shape[1], 2, coords.shape[1]))

    jacobian = np.zeros((coords.shape[0], coords.shape[1], coords.shape[1]))
    for j in range(coords.shape[1]):
        jacobian[:, :, j] = (values[:, j, 1, :] - values[:, j, 0, :]) / (2 * epsilon)

    return jacobian


class CoordinatePredictor:
    """
    Coordinates predictors class
    """

    def __init__(self, img_coords_flatten: np.ndarray, xy_coords: np.ndarray):
        self.poly = PolynomialFeatures(degree=2)
        self.model_col = LinearRegression()
        self.model_lig = LinearRegression()

        self.poly.fit(xy_coords)
        in_features = self.poly.transform(xy_coords)
        self.model_col.fit(in_features, img_coords_flatten[:, 0])
        self.model_lig.fit(in_features, img_coords_flatten[:, 1])

    def predict(self, xy_ground_coords: np.ndarray) -> np.ndarray:
        """computes the matrix positions estimates given ground coordinates"""
        in_features = self.poly.transform(xy_ground_coords)
        col_0 = self.model_col.predict(in_features)
        lig_0 = self.model_lig.predict(in_features)
        return np.stack((col_0, lig_0), axis=-1)

    def transform(self):
        raise NotImplementedError


def rotation_matrix(angle, axis: str) -> np.ndarray:
    """
    Compute a 3x3 rotation matrix of a given angle around the given axis

    :param angle: rotation angle (in radians), both scalar and array types should be supported
    :param axis: Rotation axis ("x"/"y"/"z")
    :return: 3x3 rotation matrix (when angle is scalar). If angle is an (D1, ..., DN) array, the
             output dimensions are (D1, ..., DN, 3, 3)
    """
    axis_list = ["x", "y", "z"]
    assert axis.lower() in axis_list
    # get index of rotation axis: eg. "x" -> 0, "y" -> 1, "z" -> 2
    start_pos = axis_list.index(axis.lower())

    cos_a = np.cos(angle)
    sin_a = np.sin(angle)

    if np.isscalar(angle):
        output = np.zeros((3, 3), dtype="float64")
    else:
        output = np.zeros(list(cos_a.shape) + [3, 3], dtype="float64")

    # set the one
    output[..., start_pos, start_pos] = 1.0

    # set the cosine terms
    output[..., (start_pos + 1) % 3, (start_pos + 1) % 3] = cos_a
    output[..., (start_pos + 2) % 3, (start_pos + 2) % 3] = cos_a

    # set the sinus terms
    output[..., (start_pos + 1) % 3, (start_pos + 2) % 3] = -sin_a
    output[..., (start_pos + 2) % 3, (start_pos + 1) % 3] = sin_a

    return output


def extend_circular_lut(positions, values, start=0, end=360) -> Tuple[np.ndarray, np.ndarray]:
    """
    Wrap a lookup table so that the range [start, end] is full covered, also ensuring that the LUT
    values at start and end are equal.

    :param positions: input X coordinates of the LUT, 1D, assumed to be sorted increasingly.
    :param values: output Y values of the LUT
    :param int start: minimum X coordinate to cover
    :param int end: maximum X coordinate to cover
    :return: tuple with extended positions and values
    """
    size = len(positions)
    assert size >= 2
    assert size == len(values)

    assert start < end

    parts_positions = []
    parts_values = []

    # check value at "start"
    if start < positions[0]:
        # first value computed from linear extrapolation
        first_val = values[0] + (start - positions[0]) * (values[1] - values[0]) / (positions[1] - positions[0])
        parts_positions.append([start])
        parts_values.append([first_val])
    else:
        # first value interpolated
        if isinstance(values, np.ndarray) and len(values.shape) > 1:
            # handle N-D interpolation
            idx_positions = list(range(size))
            pos_start = np.interp(start, positions, idx_positions)
            idx_start = int(pos_start)
            frac_start = pos_start - idx_start
            first_val = (1.0 - frac_start) * values[idx_start] + frac_start * values[idx_start + 1]
        else:
            # 1D interpolation
            first_val = np.interp(start, positions, values)

    # center
    parts_positions.append(positions)
    parts_values.append(values)

    # check end
    if positions[-1] < end:
        # use first value
        parts_positions.append([end])
        parts_values.append([first_val])

    if len(parts_positions) == 1:
        # no extension needed
        next_positions = positions
        next_values = values
    else:
        next_positions = np.concatenate(parts_positions)
        next_values = np.concatenate(parts_values)

    return next_positions, next_values


def antimeridian_crossing(point1, point2) -> Tuple[float, float]:
    """
    Compute the antimeridian crossing between two [lon, lat] points. Coordinates are expected in
    the longitude range [-180.0, +180.0]

    :param point1: first point
    :param point2: second point
    :return: the crossing (longitude, lattitude)
    """
    if point1[0] > point2[0]:
        east = point1
        west = [point2[0] + 360.0, point2[1]]
        cross_lon = 180.0
    else:
        east = point2
        west = [point1[0] + 360.0, point1[1]]
        cross_lon = -180.0

    # TODO: check if one of the coordinate is 180.0 or -180.0

    # General case
    cross_lat = (east[1] * (west[0] - 180.0) + west[1] * (180.0 - east[0])) / (west[0] - east[0])

    return cross_lon, cross_lat


def spherical_triangle_height(side_a, side_b, side_c) -> float:
    """
    Compute the height "AX" based at side "a" in a spherical triangle defined from the 3 side angles.

    :param side_a: angle of side a of the triangle (in rad)
    :param side_b: angle of side b of the triangle (in rad)
    :param side_c: angle of side c of the triangle (in rad)
    :return: tuple with triangle height "AX" based at side "a" and angle of side "BX" (in radians)
    """

    sin_c = np.sin(side_c)
    cos_c = np.cos(side_c)
    sin_a = np.sin(side_a)
    cos_a = np.cos(side_a)
    cos_b = np.cos(side_b)
    surf_angle = np.arccos((cos_b - cos_a * cos_c) / (sin_a * sin_c))
    if np.isnan(surf_angle):
        surf_angle = 0.0

    ax_angle = np.arcsin(np.sin(surf_angle) * sin_c)
    cos_h = np.cos(ax_angle)
    bx_angle = np.arccos(cos_c / cos_h)

    return ax_angle, bx_angle


def angular_distance(view_1: np.ndarray, view_2: np.ndarray) -> np.ndarray:
    """
    Compute the angle between two cartesian vectors.

    :param np.ndarray view_1: 2D Array of first vectors in cartesian, shape (N,3)
    :param np.ndarray view_2: 2D Array of second vectors in cartesian, shape (N,3)
    :return: 1D Array of angles (in deg), shape (N,)
    """

    unit_view_1 = view_1 / np.linalg.norm(view_1, axis=1, keepdims=True)
    unit_view_2 = view_2 / np.linalg.norm(view_2, axis=1, keepdims=True)

    return np.rad2deg(np.arccos(np.clip(np.sum(unit_view_1 * unit_view_2, axis=1), -1, 1)))


def reorder_euler_angles(angles: np.ndarray, euler_order: str) -> np.ndarray:
    """
    Re-order rotation angles to match the given order

    :param angles: Array of rotation angles (axes in the order X, Y, Z)
    :param euler_order: Sequence of rotation axes (default is "XYZ")
    """

    if euler_order == "XYZ":
        # Nothing to do
        return angles

    assert euler_order in ["YZX", "ZXY", "YXZ", "XZY", "ZYX"], f"Euler order not recogniszed: {euler_order}"

    mapper = {"X": 0, "Y": 1, "Z": 2}

    output = np.zeros(angles.shape, dtype="float64")
    for idx in range(3):
        output[..., idx] = angles[..., mapper[euler_order[idx]]]

    return output

def apply_rotation_on_vector(vec: np.ndarray, axe: np.ndarray, angle: float) -> np.ndarray:
    """
    Apply rotation on a vector via Rodrigues formula in 3D

    :param Vector we want to rotate: np.ndarray
    :param Axe around wich we want to rotate: np.ndarray
    :param Angle of the rotation (in rad): float
    :return: Rotated vector: : np.ndarray
    """
    return vec * np.cos(angle) + np.cross(axe, vec) * np.sin(angle) + axe * np.dot(axe, vec) * (1 - np.cos(angle))


def get_roll_pitch_yaw_EF_axes(position: np.ndarray, velocity: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns normalised Earth Fixed axes
    position/velocity of shape (3,) or (3,1)

    :param position of the spacecraft: np.ndarray
    :param velocity of the spacecraft: np.ndarray

    :return: roll/pitch/yaw axes: tuple(np.ndarray,np.ndarray,np.ndarray)
    """
    # Rotation axes start time (normalised)
    roll_axes_norm = velocity / np.linalg.norm(velocity)  # roll = vel

    pitch_axes_norm = np.cross(roll_axes_norm, position)  # pitch = roll^pos
    pitch_axes_norm = pitch_axes_norm / np.linalg.norm(pitch_axes_norm)

    yaw_axes_norm = np.cross(velocity, pitch_axes_norm)  # yaw = vel^pitch
    yaw_axes_norm = yaw_axes_norm / np.linalg.norm(yaw_axes_norm)

    return roll_axes_norm, pitch_axes_norm, yaw_axes_norm