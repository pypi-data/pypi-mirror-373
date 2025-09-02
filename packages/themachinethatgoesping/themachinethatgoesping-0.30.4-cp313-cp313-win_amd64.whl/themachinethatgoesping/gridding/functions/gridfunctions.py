# SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
# SPDX-FileCopyrightText: 2022 GEOMAR Helmholtz Centre for Ocean Research Kiel
#
# SPDX-License-Identifier: MPL-2.0

"""
Helper functions for the gridder class, implemented using numba
"""

import math

import numpy as np
from numba import njit

from . import helperfunctions as hlp

# --- some useful functions ---


@njit
def get_minmax(sx: np.array, sy: np.array, sz: np.array) -> tuple:
    """returns the min/max value of three lists (same size).
    Sometimes faster than separate numpy functions because it only loops once.

    Parameters
    ----------
    sx : np.array
        1D array with x positions (same size)
    sy : np.array
        1D array with x positions (same size)
    sz : np.array
        1D array with x positions (same size)

    Returns
    -------
    tuple
        with (xmin,xmax,ymin,ymax,zmin,zmax)
    """

    assert len(sx) == len(sy) == len(sz), "expected length of all arrays to be the same"

    minx = np.nan
    maxx = np.nan
    miny = np.nan
    maxy = np.nan
    minz = np.nan
    maxz = np.nan

    for i in range(len(sx)):
        x = sx[i]
        y = sy[i]
        z = sz[i]

        if not x > minx:
            minx = x
        if not x < maxx:
            maxx = x
        if not y > miny:
            miny = y
        if not y < maxy:
            maxy = y
        if not z > minz:
            minz = z
        if not z < maxz:
            maxz = z

    return minx, maxx, miny, maxy, minz, maxz


# --- static helper functions for the gridder class (implemented using numba) ---
@njit
def get_index(val: float, grd_val_min: float, grd_res: float) -> int:
    return hlp.round_int((val - grd_val_min) / grd_res)


@njit
def get_index_fraction(val: float, grd_val_min: float, grd_res: float) -> float:
    return (val - grd_val_min) / grd_res


@njit
def get_value(index: float, grd_val_min: float, grd_res: float) -> float:
    return grd_val_min + grd_res * float(index)


@njit
def get_grd_value(value: float, grd_val_min: float, grd_res: float) -> float:
    return get_value(get_index(value, grd_val_min, grd_res), grd_val_min, grd_res)


@njit
def get_index_weights(fraction_index_x: float, fraction_index_y: float, fraction_index_z: float) -> tuple:
    """
    Return a vector with fraction and weights for the neighboring grid cells.
    """

    ifraction_x = fraction_index_x % 1
    ifraction_y = fraction_index_y % 1
    ifraction_z = fraction_index_z % 1

    fraction_x = 1 - ifraction_x
    fraction_y = 1 - ifraction_y
    fraction_z = 1 - ifraction_z

    ix1 = math.floor(fraction_index_x)
    ix2 = math.ceil(fraction_index_x)
    iy1 = math.floor(fraction_index_y)
    iy2 = math.ceil(fraction_index_y)
    iz1 = math.floor(fraction_index_z)
    iz2 = math.ceil(fraction_index_z)

    X = np.array([ix1, ix1, ix1, ix1, ix2, ix2, ix2, ix2])
    Y = np.array([iy1, iy1, iy2, iy2, iy1, iy1, iy2, iy2])
    Z = np.array([iz1, iz2, iz1, iz2, iz1, iz2, iz1, iz2])

    vx = 1 * fraction_x
    vxy = vx * fraction_y
    vxiy = vx * ifraction_y

    vix = 1 * ifraction_x
    vixy = vix * fraction_y
    vixiy = vix * ifraction_y

    WEIGHT = np.array(
        [
            vxy * fraction_z,
            vxy * ifraction_z,
            vxiy * fraction_z,
            vxiy * ifraction_z,
            vixy * fraction_z,
            vixy * ifraction_z,
            vixiy * fraction_z,
            vixiy * ifraction_z,
        ]
    )

    return X, Y, Z, WEIGHT


@njit()
def grd_weighted_mean(
    sx: np.array,
    sy: np.array,
    sz: np.array,
    sv: np.array,
    xmin: float,
    xres: float,
    nx: int,
    ymin: float,
    yres: float,
    ny: int,
    zmin: float,
    zres: float,
    nz: int,
    image_values: np.ndarray,
    image_weights: np.ndarray,
    skip_invalid: bool = True,
) -> tuple:

    for i in range(len(sx)):
        x = sx[i]
        y = sy[i]
        z = sz[i]
        v = sv[i]

        IX, IY, IZ, WEIGHT = get_index_weights(
            get_index_fraction(x, xmin, xres),
            get_index_fraction(y, ymin, yres),
            get_index_fraction(z, zmin, zres),
        )

        for i_ in range(len(IX)):
            ix = int(IX[i_])
            iy = int(IY[i_])
            iz = int(IZ[i_])
            w = WEIGHT[i_]

            if w == 0:
                continue

            if not skip_invalid:
                if ix < 0:
                    ix = 0
                if iy < 0:
                    iy = 0
                if iz < 0:
                    iz = 0

                if abs(ix) >= nx:
                    ix = nx - 1
                if abs(iy) >= ny:
                    iy = ny - 1
                if abs(iz) >= nz:
                    iz = nz - 1
            else:
                if ix < 0:
                    continue
                if iy < 0:
                    continue
                if iz < 0:
                    continue

                if abs(ix) >= nx:
                    continue
                if abs(iy) >= ny:
                    continue
                if abs(iz) >= nz:
                    continue

            # print(ix,iy,iz,v,w)
            # if v >= 0:
            if np.isfinite(v):
                image_values[ix][iy][iz] += v * w
                image_weights[ix][iy][iz] += w


@njit
def grd_block_mean(
    sx: np.array,
    sy: np.array,
    sz: np.array,
    sv: np.array,
    xmin: float,
    xres: float,
    nx: int,
    ymin: float,
    yres: float,
    ny: int,
    zmin: float,
    zres: float,
    nz: int,
    image_values: np.ndarray,
    image_weights: np.ndarray,
    skip_invalid: bool = True,
) -> tuple:

    for i in range(len(sx)):
        x = sx[i]
        y = sy[i]
        z = sz[i]
        v = sv[i]

        ix = get_index(x, xmin, xres)
        iy = get_index(y, ymin, yres)
        iz = get_index(z, zmin, zres)

        if not skip_invalid:
            if ix < 0:
                ix = 0
            if iy < 0:
                iy = 0
            if iz < 0:
                iz = 0

            if abs(ix) >= nx:
                ix = nx - 1
            if abs(iy) >= ny:
                iy = ny - 1
            if abs(iz) >= nz:
                iz = nz - 1
        else:
            if ix < 0:
                continue
            if iy < 0:
                continue
            if iz < 0:
                continue

            if abs(ix) >= nx:
                continue
            if abs(iy) >= ny:
                continue
            if abs(iz) >= nz:
                continue

        # if v >= 0:
        if np.isfinite(v):
            image_values[ix][iy][iz] += v
            image_weights[ix][iy][iz] += 1
