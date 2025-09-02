# SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
# SPDX-FileCopyrightText: 2022 Peter Urban, GEOMAR Helmholtz Centre for Ocean Research Kiel
#
# SPDX-License-Identifier: MPL-2.0

# disable pylint warnings for too many arguments
# pylint: disable=too-many-arguments

"""
Simple gridder class that can create quantitative 3D images from x,z,y,val from some custom data.
"""

import numpy as np
from numpy.typing import ArrayLike

from .functions import gridfunctions as grdf


class ForwardGridderLegacy:
    """Simple class to generate 3D grids (images) and interpolate xyz data onto a grid using simple forward mapping algorithms.
    (e.g. block mean, weighted mean interpolation)
    """

    @classmethod
    def from_data(cls, res: float, sx: ArrayLike, sy: ArrayLike, sz: ArrayLike):
        """Create gridder with resolution "res"
        xmin,xmax,ymin,ymax,zmin,zmax are determined to exactly contain the given data vectors (sx,sy,sz)

        Parameters
        ----------
        res : float
            x,y and z resolution of the grid
        sx : ArrayLike
            array with x data
        sy : ArrayLike
            array with y data
        sz : ArrayLike
            array with z data

        Returns
        -------
        ForwardGridder
            ForwardGridder object
        """
        return cls.from_res(
            res, *grdf.get_minmax(np.array(sx), np.array(sy), np.array(sz))
        )

    # -- factory methods --
    @classmethod
    def from_res(
        cls,
        res: float,
        min_x: float,
        max_x: float,
        min_y: float,
        max_y: float,
        min_z: float,
        max_z: float,
    ):
        """Create gridder setting xres,yres and zres to "res"

        Parameters
        ----------
        res : float
            x,y and z resolution of the grid
        min_x : float
            smallest x value that must be contained within the grid
        max_x : float
            largest x value that must be contained within the grid
        min_y : float
            smallest y value that must be contained within the grid
        max_y : float
            smallest y value that must be contained within the grid
        min_z : float
            smallest z value that must be contained within the grid
        max_z : float
            smallest z value that must be contained within the grid

        Returns
        -------
        ForwardGridder
            ForwardGridder object
        """
        return cls(res, res, res, min_x, max_x, min_y, max_y, min_z, max_z)

    def __init__(
        self,
        xres: float,
        yres: float,
        zres: float,
        min_x: float,
        max_x: float,
        min_y: float,
        max_y: float,
        min_z: float,
        max_z: float,
        xbase: float = 0.0,
        ybase: float = 0.0,
        zbase: float = 0.0,
    ):
        """Initialize forward gridder class using grid parameters.

        Parameters
        ----------
        xres : float
            x resolution of the grid
        yres : float
            y resolution of the grid
        zres : float
            z resolution of the grid
        min_x : float
            smallest x value that must be contained within the grid
        max_x : float
            largest x value that must be contained within the grid
        min_y : float
            smallest y value that must be contained within the grid
        max_y : float
            largest y value that must be contained within the grid
        min_z : float
            smallest z value that must be contained within the grid
        max_z : float
            largest z value that must be contained within the grid
        xbase : float, optional
            x base position of the grid, by default 0.0
        ybase : float, optional
            y base position of the grid, by default 0.0
        zbase : float, optional
            z base position of the grid, by default 0.0
        """

        # initialize values that need no computation
        self.xres = xres
        self.yres = yres
        self.zres = zres
        self.xbase = xbase
        self.ybase = ybase
        self.zbase = zbase

        # compute center values of the grid cells that contain min_x, _y, _z and max_x, _y, _z
        self.xmin = grdf.get_grd_value(min_x, xbase, xres)
        self.xmax = grdf.get_grd_value(max_x, xbase, xres)
        self.ymin = grdf.get_grd_value(min_y, ybase, yres)
        self.ymax = grdf.get_grd_value(max_y, ybase, yres)
        self.zmin = grdf.get_grd_value(min_z, zbase, zres)
        self.zmax = grdf.get_grd_value(max_z, zbase, zres)

        # compute the number of elements from (including) min_x, _y, _z to max_x, _y, _z
        self.nx = int((self.xmax - self.xmin) / self.xres) + 1
        self.ny = int((self.ymax - self.ymin) / self.yres) + 1
        self.nz = int((self.zmax - self.zmin) / self.zres) + 1

        # compute x,y,z borders (extend of the outest grid cells)
        self.border_xmin = self.xmin - self.xres / 2.0
        self.border_xmax = self.xmax + self.xres / 2.0
        self.border_ymin = self.ymin - self.yres / 2.0
        self.border_ymax = self.ymax + self.yres / 2.0
        self.border_zmin = self.zmin - self.zres / 2.0
        self.border_zmax = self.zmax + self.zres / 2.0

    def get_empty_grd_images(self) -> tuple:
        """create empty num and sum grid images

        Returns
        -------
        (image_values, image_weights):
            image_values: summed value for each grid position
            image_weights: weights for each grid position
        """
        image_values = np.zeros((self.nx, self.ny, self.nz)).astype(np.float64)
        image_weights = np.zeros((self.nx, self.ny, self.nz)).astype(np.float64)

        return image_values, image_weights

    def interpolate_block_mean(
        self,
        sx: ArrayLike,
        sy: ArrayLike,
        sz: ArrayLike,
        s_val: ArrayLike,
        image_values: np.ndarray = None,
        image_weights: np.ndarray = None,
        skip_invalid: bool = True,
    ) -> tuple:
        """interpolate 3D points onto 3d images using block mean interpolation

        Parameters
        ----------
        sx : ArrayLike
            x values
        sy : ArrayLike
            y values
        sz : ArrayLike
            z values
        s_val : ArrayLike
            amplitudes / volume backscattering coefficients
        image_values : np.ndarray, optional
            Image with values. If None a new image will be created. Dimensions must fit the internal nx,ny,nz
        image_weights : np.ndarray, optional
            Image with weights. If None a new image will be created. Dimensions must fit the internal nx,ny,nz
        skip_invalid : bool, optional
            skip values that exceed border_xmin, _xmax, _ymin, _ymax, _zmin, _zmax. Otherwise throw exception by default True

        Returns
        -------
        tuple
            image_values, image_weights
        """

        if image_values is None or image_weights is None:
            image_weights, image_values = self.get_empty_grd_images()
        else:
            assert image_values.shape == (
                self.nx,
                self.ny,
                self.nz,
            ), "ERROR: image_values dimensions do not fit ForwardGridder dimensions!"
            assert image_weights.shape == (
                self.nx,
                self.ny,
                self.nz,
            ), "ERROR: image_weight dimensions do not fit ForwardGridder dimensions!"

        grdf.grd_block_mean(
            np.array(sx),
            np.array(sy),
            np.array(sz),
            np.array(s_val),
            *self._get_min_and_offset(),
            image_values=image_values,
            image_weights=image_weights,
            skip_invalid=skip_invalid
        )
        return image_values, image_weights

    def interpolate_weighted_mean(
        self,
        sx: ArrayLike,
        sy: ArrayLike,
        sz: ArrayLike,
        s_val: ArrayLike,
        image_values: np.ndarray = None,
        image_weights: np.ndarray = None,
        skip_invalid: bool = True,
    ):
        """interpolate 3D points onto 3d images using weighted mean interpolation

        Parameters
        ----------
        sx : ArrayLike
            x values
        sy : ArrayLike
            y values
        sz : ArrayLike
            z values
        s_val : ArrayLike
            amplitudes / volume backscattering coefficients
        image_values : np.ndarray, optional
            Image with values. If None a new image will be created. Dimensions must fit the internal nx,ny,nz
        image_weights : np.ndarray, optional
            Image with weights. If None a new image will be created. Dimensions must fit the internal nx,ny,nz
        skip_invalid : bool, optional
            skip values that exceed border_xmin, _xmax, _ymin, _ymax, _zmin, _zmax. Otherwise throw exception by default True

        Returns
        -------
        tuple
            image_values, image_weights
        """

        if image_values is None or image_weights is None:
            image_weights, image_values = self.get_empty_grd_images()
        else:
            assert image_values.shape == (
                self.nx,
                self.ny,
                self.nz,
            ), "ERROR: image_values dimensions do not fit ForwardGridder dimensions!"
            assert image_weights.shape == (
                self.nx,
                self.ny,
                self.nz,
            ), "ERROR: image_weight dimensions do not fit ForwardGridder dimensions!"

        grdf.grd_weighted_mean(
            np.array(sx),
            np.array(sy),
            np.array(sz),
            np.array(s_val),
            *self._get_min_and_offset(),
            image_values=image_values,
            image_weights=image_weights,
            skip_invalid=skip_invalid
        )
        return image_values, image_weights

    @staticmethod
    def get_minmax(sx: ArrayLike, sy: ArrayLike, sz: ArrayLike) -> tuple:
        """returns the min/max value of three lists (same size).
        Sometimes faster than separate numpy functions because it only loops once.

        Parameters
        ----------
        sx : ArrayLike
            1D array with x positions (same size)
        sy : ArrayLike
            1D array with x positions (same size)
        sz : ArrayLike
            1D array with x positions (same size)

        Returns
        -------
        tuple
            with (xmin,xmax,ymin,ymax,zmin,zmax)
        """
        return grdf.get_minmax(np.array(sx), np.array(sy), np.array(sz))

    def get_x_index(self, x: float) -> int:
        """get the x index of the grid cell that physically contains "x"

        Parameters
        ----------
        x : float

        Returns
        -------
        x_index : int
        """
        return grdf.get_index(x, self.xmin, self.xres)

    def get_y_index(self, y: float) -> int:
        """get the y index of the grid cell that physically contains "x"

        Parameters
        ----------
        y : float

        Returns
        -------
        y_index : int
        """
        return grdf.get_index(y, self.ymin, self.yres)

    def get_z_index(self, z: float) -> int:
        """get the y index of the grid cell that physically contains "z"

        Parameters
        ----------
        z : float

        Returns
        -------
        z_index : int
        """
        return grdf.get_index(z, self.zmin, self.zres)

    def get_x_index_fraction(self, x: float) -> float:
        """get the fractional x index of "x" within the 3D grid image

        Parameters
        ----------
        x : float

        Returns
        -------
        x_index : float
        """
        return grdf.get_index_fraction(x, self.xmin, self.xres)

    def get_y_index_fraction(self, y: float) -> float:
        """get the fractional y index of "y" within the 3D grid image

        Parameters
        ----------
        y : float

        Returns
        -------
        y_index : float
        """
        return grdf.get_index_fraction(y, self.xmin, self.xres)

    def get_z_index_fraction(self, z: float) -> float:
        """get the fractional z index of "z" within the 3D grid image

        Parameters
        ----------
        z : float

        Returns
        -------
        z_index : float
        """
        return grdf.get_index_fraction(z, self.xmin, self.xres)

    def get_x_value(self, x_index: float) -> float:
        """return the x value of the grid cell of index x_index

        Parameters
        ----------
        x_index : int

        Returns
        -------
        x : float
        """
        return grdf.get_value(x_index, self.xmin, self.xres)

    def get_y_value(self, y_index: int) -> float:
        """return the y value of the grid cell of index y_index

        Parameters
        ----------
        y_index : int

        Returns
        -------
        y : float
        """
        return grdf.get_value(y_index, self.ymin, self.yres)

    def get_z_value(self, z_index: int) -> float:
        """return the z value of the grid cell of index z_index

        Parameters
        ----------
        z_index : int

        Returns
        -------
        z : float
        """
        return grdf.get_value(z_index, self.zmin, self.zres)

    def get_x_grd_value(self, x: float) -> float:
        """return the x value of the grid cell that contains x

        Parameters
        ----------
        x : float

        Returns
        -------
        x_value of grid cell : float
        """
        return grdf.get_grd_value(x, self.xmin, self.xres)

    def get_y_grd_value(self, y: float) -> float:
        """return the y value of the grid cell that contains y

        Parameters
        ----------
        y : float

        Returns
        -------
        y_value of grid cell : float
        """
        return grdf.get_grd_value(y, self.ymin, self.yres)

    def get_z_grd_value(self, z: float) -> float:
        """return the z value of the grid cell that contains z

        Parameters
        ----------
        z : float

        Returns
        -------
        z_value of grid cell : float
        """
        return grdf.get_grd_value(z, self.zmin, self.zres)

    def get_extent_x(self) -> list:
        """return x extend (useful for plotting)"""
        return [self.border_xmin, self.border_xmax]

    def get_extent_y(self) -> list:
        """return y extend (useful for plotting)"""
        return [self.border_ymin, self.border_ymax]

    def get_extent_z(self) -> list:
        """return z extend (useful for plotting)"""
        return [self.border_zmin, self.border_zmax]
    
    def get_extent(self, axis: str = 'xyz') -> list:
        """return x,y,z extend (useful for plotting)"""
        extent = []
        for ax in axis:
            match ax:
                case 'x':
                    extent.extend(self.get_extent_x())
                case 'y':
                    extent.extend(self.get_extent_y())
                case 'z':
                    extent.extend(self.get_extent_z())
                case _:
                    raise ValueError(f"Invalid axis {ax}. Only 'x', 'y' and 'z' are allowed.")
        return tuple(extent)

    def get_x_coordinates(self) -> list:
        """return valid x grid coordinates as list"""
        coordinates = []
        for i in range(self.nx):
            coordinates.append(self.get_x_value(i))

        return coordinates

    def get_y_coordinates(self) -> list:
        """return valid y grid coordinates as list"""
        coordinates = []
        for i in range(self.ny):
            coordinates.append(self.get_y_value(i))

        return coordinates

    def get_z_coordinates(self) -> list:
        """return valid z grid coordinates as list"""
        coordinates = []
        for i in range(self.nz):
            coordinates.append(self.get_z_value(i))

        return coordinates

    # --- private helper functions ---
    def _get_min_and_offset(self):
        return (
            self.xmin,
            self.xres,
            self.nx,
            self.ymin,
            self.yres,
            self.ny,
            self.zmin,
            self.zres,
            self.nz,
        )
