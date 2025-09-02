# SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
# SPDX-FileCopyrightText: 2022 Peter Urban, GEOMAR Helmholtz Centre for Ocean Research Kiel
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np

from numba import njit

from .functions import gridfunctions as gf
from .forwardgridderlegacy import ForwardGridderLegacy
from .forwardgridderlegacynew import ForwardGridderLegacyNew
from themachinethatgoesping.algorithms.gridding import ForwardGridder3D

from collections.abc import MutableMapping

import warnings


@njit
def static_get_target_pos(image, min_val=np.nan):

    x_sum = 0
    y_sum = 0
    z_sum = 0
    x_weight = 0
    y_weight = 0
    z_weight = 0

    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            for z in range(image.shape[2]):
                if not np.isfinite(image[x][y][z]):
                    continue

                if image[x][y][z] < min_val:
                    continue

                x_sum += image[x][y][z] * x
                y_sum += image[x][y][z] * y
                z_sum += image[x][y][z] * z
                x_weight += image[x][y][z]
                y_weight += image[x][y][z]
                z_weight += image[x][y][z]

    return x_sum / x_weight, y_sum / y_weight, z_sum / z_weight


class EchoGrid:
    
    @classmethod
    def from_data(cls, res, sx, sy, sz, sv, blockmean=False):
        gridder = ForwardGridder3D.from_data(res, sx, sy, sz)
        if blockmean:
            image_sums, imagenumes = gridder.interpolate_block_mean(sx,sy,sz,sv)
        else:
            image_sums, imagenumes = gridder.interpolate_weighted_mean(sx,sy,sz,sv)
        return cls(image_sums, imagenumes, gridder)
    
    @classmethod
    def from_dataF(cls, res, sx, sy, sz, sv, blockmean=False):
        gridder = ForwardGridder3DF.from_data(res, sx, sy, sz)
        if blockmean:
            image_sums, imagenumes = gridder.interpolate_block_mean(sx,sy,sz,sv)
        else:
            image_sums, imagenumes = gridder.interpolate_weighted_mean(sx,sy,sz,sv)
        return cls(image_sums, imagenumes, gridder)
    
    @classmethod
    def from_data_legacy(cls, res, sx, sy, sz, sv, blockmean=False):
        gridder = ForwardGridderLegacy.from_data(res, sx, sy, sz)
        if blockmean:
            image_sums, imagenumes = gridder.interpolate_block_mean(sx,sy,sz,sv)
        else:
            image_sums, imagenumes = gridder.interpolate_weighted_mean(sx,sy,sz,sv)
        return cls(image_sums, imagenumes, gridder)
    
    @classmethod
    def from_data_legacy_new(cls, res, sx, sy, sz, sv, blockmean=False):
        gridder = ForwardGridderLegacyNew.from_data(res, sx, sy, sz)
        if blockmean:
            image_sums, imagenumes = gridder.interpolate_block_mean(sx,sy,sz,sv)
        else:
            image_sums, imagenumes = gridder.interpolate_weighted_mean(sx,sy,sz,sv)
        return cls(image_sums, imagenumes, gridder)
    
    def __init__(self, image_sums, image_nums, gridder):
        self.image_sums = image_sums.copy()
        self.image_nums = image_nums.copy()
        self.image_avg = np.empty(image_nums.shape, dtype=np.float64)
        self.image_avg.fill(np.nan)

        self.image_avg[image_nums > 0] = (
            image_sums[image_nums > 0] / image_nums[image_nums > 0]
        )

        self.gridder_type = type(gridder)
        # self.Gridder = gridder
        try:
            self.total_value = np.nansum(self.image_avg) * (
                gridder.get_xres() * gridder.get_yres() * gridder.get_zres()
            )

            self.ZDiff = gridder.get_extent_z()[1] - gridder.get_extent_z()[0]

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                self.total_value_layer = (
                    np.nansum(np.nanmean(self.image_avg, axis=2))
                    * gridder.get_xres()
                    * gridder.get_yres()
                    * self.ZDiff
                )

            self.extent_x = gridder.get_extent_x()
            self.extent_y = gridder.get_extent_y()
            self.extent_z = gridder.get_extent_z()
            self.res_x = gridder.get_xres()
            self.res_y = gridder.get_yres()
            self.res_z = gridder.get_zres()
            self.min_x = gridder.get_xmin()
            self.max_x = gridder.get_xmax()
            self.min_y = gridder.get_ymin()
            self.max_y = gridder.get_ymax()
            self.min_z = gridder.get_zmin()
            self.max_z = gridder.get_zmax()
        except:
            #for legacy gridder
            self.total_value = np.nansum(self.image_avg) * (
                gridder.xres * gridder.yres * gridder.zres
            )

            self.ZDiff = gridder.get_extent_z()[1] - gridder.get_extent_z()[0]

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                self.total_value_layer = (
                    np.nansum(np.nanmean(self.image_avg, axis=2))
                    * gridder.xres
                    * gridder.yres
                    * self.ZDiff
                )
                
            self.extent_x = gridder.get_extent_x()
            self.extent_y = gridder.get_extent_y()
            self.extent_z = gridder.get_extent_z()
            self.res_x = gridder.xres
            self.res_y = gridder.yres
            self.res_z = gridder.zres
            self.min_x = gridder.xmin
            self.max_x = gridder.xmax
            self.min_y = gridder.ymin
            self.max_y = gridder.ymax
            self.min_z = gridder.zmin
            self.max_z = gridder.zmax

    def get_target_pos(self, min_val=np.nan):
        xi, yi, zi = static_get_target_pos(self.image_avg, min_val)

        return (
            xi * self.res_x + self.min_x,
            yi * self.res_y + self.min_y,
            zi * self.res_z + self.min_z,
        )

    def get_total_value(self, min_val):
        if not np.isfinite(min_val):
            return self.total_value

        return np.nansum(self.image_avg[self.image_avg >= min_val]) * (
            self.res_x * self.res_y * self.res_z
        )

    def get_total_value_layer(self, min_val):
        if not np.isfinite(min_val):
            return self.total_value_layer

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            layerAvg = np.nanmean(self.image_avg, axis=2)

        return (
            np.nansum(layerAvg[layerAvg >= min_val])
            * self.res_x
            * self.res_y
            * self.ZDiff
        )

    def get_gridder(self):
        return self.gridder_type(
            self.res_x,
            self.res_y,
            self.res_z,
            self.min_x,
            self.max_x,
            self.min_y,
            self.max_y,
            self.min_z,
            self.max_z,
        )

    def cut_by_layer_size(self, layer_z, layer_size):
        gridder_old = self.get_gridder()

        min_z = gridder_old.get_z_grd_value(
            layer_z - (layer_size - gridder_old.get_zres()) / 2
        )
        max_z = gridder_old.get_z_grd_value(
            layer_z + (layer_size - gridder_old.get_zres()) / 2
        )
        
        return self.cut_by_layer_extent(min_z, max_z)

    def cut_by_layer_extent(self, min_z = None, max_z = None):
        gridder_old = self.get_gridder()
        
        if min_z is None:
            min_z = self.min_z
            
        if max_z is None:
            max_z = self.max_z
        
        gridder = self.gridder_type(
            self.res_x,
            self.res_y,
            self.res_z,
            self.min_x,
            self.max_x,
            self.min_y,
            self.max_y,
            min_z,
            max_z,
        )

        iz0 = gridder_old.get_z_index(min_z)
        iz1 = gridder_old.get_z_index(max_z)

        image_sums = self.image_sums[:, :, iz0: iz1 + 1]
        image_nums = self.image_nums[:, :, iz0: iz1 + 1]

        return EchoGrid(image_sums, image_nums, gridder)

    def get_depth_mean_image(self, layer_z, layer_size):

        gridder_old = self.get_gridder()

        min_z = gridder_old.get_z_grd_value(
            layer_z - (layer_size - gridder_old.zres) / 2
        )
        max_z = gridder_old.get_z_grd_value(
            layer_z + (layer_size - gridder_old.zres) / 2
        )

        gridder = self.gridder_type(
            self.res_x,
            self.res_y,
            self.res_z,
            self.min_x,
            self.max_x,
            self.min_y,
            self.max_y,
            min_z,
            max_z,
        )

        iz0 = gridder_old.get_z_index(min_z)
        iz1 = gridder_old.get_z_index(max_z)

        image_sums = self.image_sums[:, :, iz0: iz1 + 1]
        image_nums = self.image_nums[:, :, iz0: iz1 + 1]

        return image_sums, image_nums, gridder

    def get_grid_extent(self, axis='xyz'):
        extent = []
        for ax in axis:
            match ax:
                case 'x':
                    extent.extend(self.extent_x)
                case 'y':
                    extent.extend(self.extent_y)
                case 'z':
                    extent.extend(self.extent_z)
                case _:
                    raise ValueError(f"Invalid axis: {ax}. Use 'x', 'y', or 'z'.")
        return tuple(extent)

    def to_string(self, TrueValue, methodName=None, minMethodNameSize=None):

        if methodName is None:
            prefix = "total_value"
        else:
            prefix = "Bubbles Grid"
            if minMethodNameSize:
                prefix += "[{:MMMs}]".replace(
                    "MMM", str(int(minMethodNameSize))
                ).format(methodName)
            else:
                prefix += "[{}]".format(methodName)

        string = prefix + ": {:15.2f}  | {:5.2f} %".format(
            round(self.total_value, 2), round(100 * (self.total_value / TrueValue - 1), 2)
        )
        return string

    def print(self, methodName, minMethodNameSize, TrueValue):
        print(self.to_string(methodName, minMethodNameSize, TrueValue))

    def get_image(self, toDb=True, minDbVal=-50):

        image = self.image_avg.copy()
        image[self.image_nums == 0] = np.nan
        if toDb:
            image[image == 0] = 0.000000000000001
            image = 10 * np.log10(image)
            image[image < minDbVal] = minDbVal

        return image

    def plot(
        self,
        figure,
        targets_color=None,
        target_size=1,
        show_wci=True,
        show_echo=True,
        show_map=True,
        show_colorbar=True,
        toDb=True,
        minDbVal=-50,
        minDbReplace=None,
        xindex=None,
        yindex=None,
        zindex=None,
        zindeces=None,
        kwargs=None,
        colorbar_kwargs=None,
    ):

        figure.clear()

        nplots = sum([show_wci, show_echo, show_map])
        if kwargs is None:
            kwargs = {}
        if colorbar_kwargs is None:
            colorbar_kwargs = {}

        # gs = figure.add_gridspec(2, 2)
        #
        #
        # if nplots == 1:
        #     axes = [
        #         figure.add_subplot(gs[:, :])
        #     ]
        # elif nplots == 2:
        #     if show_wci:
        #         axes = [
        #             figure.add_subplot(gs[0, :]),
        #             figure.add_subplot(gs[1, :]),
        #         ]
        #     else:
        #         axes = [
        #             figure.add_subplot(gs[:, 0]),
        #             figure.add_subplot(gs[:, 1]),
        #         ]
        # elif nplots == 3:
        #     axes = [
        #         figure.add_subplot(gs[0, :]),
        #         figure.add_subplot(gs[1, 0]),
        #         figure.add_subplot(gs[1, 1])
        #     ]
        # else:
        #     axes = []
        if nplots == 1:
            axes = [figure.subplots(ncols=nplots)]
        else:
            axes = figure.subplots(ncols=nplots)

        axit = iter(axes)

        def get_nan_sum(imageLin, axis, divide=1):
            # image = np.nansum(imageLin,axis=axis)
            image = np.nanmean(imageLin, axis=axis)
            num = np.nansum(self.image_nums, axis=axis)

            if divide != 1:
                image /= divide

            image[num == 0] = np.nan

            if toDb:
                image[image == 0] = 0.000000000000001
                image = 10 * np.log10(image)
                if minDbReplace is not None:
                    image[image < minDbVal] = minDbReplace
                else:
                    image[image < minDbVal] = minDbVal

            return image

        if show_wci:
            ax = next(axit)

            if xindex is None:
                image = get_nan_sum(self.image_avg.copy(), axis=0)
            else:
                image = self.image_avg[xindex, :, :]
                if toDb:
                    image[image == 0] = 0.000000000000001
                    image = 10 * np.log10(image)
                    if minDbReplace is not None:
                        image[image < minDbVal] = minDbReplace
                    else:
                        image[image < minDbVal] = minDbVal

            mapable = ax.imshow(
                np.rot90(image),
                aspect="equal",
                extent=self.get_grid_extent('yz'),
                **kwargs
            )

            if show_colorbar:
                figure.colorbar(mapable, ax=ax, **colorbar_kwargs)

            if targets_color:
                for targets, color in targets_color:
                    ax.scatter(targets.y, targets.z, c=color, s=target_size)

        if show_echo:
            ax = next(axit)

            if yindex is None:
                image = get_nan_sum(self.image_avg.copy(), axis=1)
            else:
                image = self.image_avg[:, yindex, :]
                if toDb:
                    image[image == 0] = 0.000000000000001
                    image = 10 * np.log10(image)
                    if minDbReplace is not None:
                        image[image < minDbVal] = minDbReplace
                    else:
                        image[image < minDbVal] = minDbVal

            mapable = ax.imshow(
                np.rot90(image),
                aspect="equal",
                extent=self.get_grid_extent('xz'),
                **kwargs
            )
            if targets_color:
                for targets, color in targets_color:
                    ax.scatter(targets.x, targets.z, c=color, s=target_size)

            if show_colorbar:
                figure.colorbar(mapable, ax=ax, **colorbar_kwargs)

        if show_map:
            ax = next(axit)

            if zindex is None and zindeces is None:
                image = get_nan_sum(self.image_avg.copy(), axis=2)
            elif zindex is None and zindeces is not None:
                image = get_nan_sum(
                    self.image_avg[:, :, zindeces[0]: zindeces[1] + 1], axis=2
                )  # ,divide=abs(zindeces[1]-zindeces[0]))

            else:
                image = self.image_avg[:, :, zindex]
                if toDb:
                    image[image == 0] = 0.000000000000001
                    image = 10 * np.log10(image)
                    if minDbReplace is not None:
                        image[image < minDbVal] = minDbReplace
                    else:
                        image[image < minDbVal] = minDbVal

            mapable = ax.imshow(
                image,
                aspect="equal",
                extent=self.get_grid_extent('yx'),
                **kwargs
            )
            if targets_color:
                for targets, color in targets_color:
                    ax.scatter(targets.y, targets.x, c=color, s=target_size)

            if show_colorbar:
                figure.colorbar(mapable, ax=ax, **colorbar_kwargs)

        return figure, ax, image



if __name__ == "__main__":

    imN = np.ones((10, 10, 10))
    imS = np.ones((10, 10, 10))
    gridder = gf.GRIDDER(1, 1, 1, 0, 1, 0, 1, 0, 1)
    sc = EchoGrid(imN, imS, gridder)

    scd["test"] = sc
    scd["test2"] = imN, imS, gridder

    print(scd["test"].to_string(999, "peter", 10))
    print(scd["test2"].to_string(1010, "peter", 10))
    print(scd["test2"].to_string(1020, "peter"))
    print(
        scd["test2"].to_string(
            1030,
        )
    )

    print("---")
    scd.print(999)

    print("done")
