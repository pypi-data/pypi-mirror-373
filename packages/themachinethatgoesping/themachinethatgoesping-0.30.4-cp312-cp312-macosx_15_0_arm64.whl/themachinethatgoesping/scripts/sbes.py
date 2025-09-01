# SPDX-FileCopyrightText: 2022 Peter Urban, Sven Schorge, GEOMAR Helmholtz Centre for Ocean
# Research Kiel SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

from math import tan,radians
from copy import deepcopy

from themachinethatgoesping.scripts.oceanographic import knots_to_ms
from themachinethatgoesping.scripts.plot_tools import prepare_plt

## @package scipts
# Simple scripts for calculations with an sbes
#


## simple sbes calculation class
class SBES:

    ## The consructor
    # @param beamopening_angle: Beam opening of the sbes
    # @param x: x offset (positive along track)
    # @param z: z offset (positive downwards)
    def __init__(self, beamopening_angle,
                 x = 0,
                # y = 0,
                 z = 0):
        self.beamopening_angle = beamopening_angle
        self.x = x
        #self.y = y
        self.z = z

    ## Calculate the foot print at a certain depth
    #  @param depth: Depth in meeters
    #  @param beamopening_angle: Beam opening of the sbes
    def calc_footprint(self, depth: float, beamopening_angle: float = None) -> float:
        """

        :rtype: float
        """
        if beamopening_angle is None:
            beamopening_angle = self.beamopening_angle

        return depth*2*tan(radians(beamopening_angle/2))

    ## Calculate the necessary pingrate to reach overlap during the survey
    # @param speed: Speed of the vessel in knots
    # @param depth: Depth at which the pings should overlap
    # @return: pingrate in pings per second
    def calc_overlap_pingrate(self,speed : float,depth: float,beamopening_angle: float=None) -> float:

        footprint = self.calc_footprint(depth,beamopening_angle)

        return knots_to_ms(speed)/footprint

    @staticmethod
    def calc_pingdistance(speed,pingrate):
        return knots_to_ms(speed)/pingrate


    def calc_overlap_depth(self, delta_x):
        return (delta_x/2) / (tan(radians(self.beamopening_angle/2))) + self.z


    def calc_overlap_depth_for_pingrate(self,speed,pingrate):
        delta_x = self.calc_pingdistance(speed, pingrate)
        return self.calc_overlap_depth(delta_x)


    def get_beam_xmin(self, depth: float) -> float:
        y = -depth
        ymax = -self.z

        return -tan(radians(self.beamopening_angle / 2)) * (ymax - y) + self.x

    def get_beam_xmax(self, depth: float) -> float:
        y = -depth
        ymax = -self.z

        return tan(radians(self.beamopening_angle / 2)) * (ymax - y) + self.x

    def get_beam_limits(self,depth: float)-> tuple:

        xmin = self.get_beam_xmin(depth)
        xmax = self.get_beam_xmax(depth)

        return [xmin,self.x,xmax],[-depth,-self.z,-depth]

    def get_horizontal_line(self,depth: float) -> tuple:

        xmin = self.get_beam_xmin(depth)
        xmax = self.get_beam_xmax(depth)

        return [xmin,xmax],[-depth,-depth]


    def plot(self,depth,color,aspect = True,add_bottom = True,axes=None):

        if axes is None: axes = plt

        X, Y = self.get_beam_limits(depth)
        axes.plot(X,Y,color)

        plot_xmin = self.get_beam_xmin(depth)
        plot_xmax = self.get_beam_xmax(depth)
        plot_width = plot_xmax - plot_xmin
        if add_bottom:
            axes.plot([plot_xmin - 0.25 * plot_width, plot_xmax + 0.25 * plot_width], [-depth, -depth])

        return axes



    def plot_pingoverlap_at_pingrate(self,depth,speed,pingrate, color1 = 'r', color2 = 'b',
                                     print_vars = True,
                                     add_bottom = True,
                                     axes = None,
                                     make_figure = True):

        overlapdepth = self.calc_overlap_depth_for_pingrate(speed,pingrate)

        if axes is None:
            axes = plt
            if make_figure: self.make_figure("Beam: {}° pingoverlap at {} Hz | {} knots = overlapdepth {} m ".format(self.beamopening_angle,pingrate,speed,round(overlapdepth,2)))

        self.plot(depth,color1,add_bottom=False,axes=axes)

        x = knots_to_ms(speed)/pingrate
        overlap_sbes = deepcopy(self)
        overlap_sbes.x = x
        overlap_sbes.plot(depth,color2,add_bottom=False,axes=axes)

        X,Y = self.get_horizontal_line(overlapdepth)
        axes.plot(X,Y)

        plot_xmin = self.get_beam_xmin(depth)
        plot_xmax = overlap_sbes.get_beam_xmax(depth)
        plot_width = plot_xmax - plot_xmin
        if add_bottom:
            axes.plot([plot_xmin - 0.25 * plot_width, plot_xmax + 0.25 * plot_width], [-depth, -depth])

        if print_vars:
            print("Seafloor depth:",round(depth,2),"m")
            print("Ship speed:    ",round(speed,2),"knots")
            print("pingrate:      ",round(pingrate,2),"pings/second","\t|\t",round(1/pingrate,2),"seconds/ping")
            print("---")
            print("calculated ping distance:",round(overlap_sbes.x,2),"m")
            print("calculated overlap depth:",round(self.calc_overlap_depth_for_pingrate(speed,pingrate),2),"m")

    def plot_pingoverlap_at_overlapdepth(self, depth, speed, overlapdepth, color1 = 'r', color2 = 'b',
                                     print_vars = True,
                                     add_bottom = True,
                                     axes = None,
                                         make_figure = True):

        pingrate = self.calc_overlap_pingrate(speed,overlapdepth)

        if axes is None: axes = plt

        if make_figure: self.make_figure("Beam: {}° pingoverlap at {} m | {} knots = pingrate {} Hz".format(self.beamopening_angle,overlapdepth,speed,round(pingrate,2)))

        self.plot(depth, color1,add_bottom=False,axes=axes)


        x = knots_to_ms(speed) / pingrate
        overlap_sbes = deepcopy(self)
        overlap_sbes.x = x
        overlap_sbes.plot(depth, color2,add_bottom=False,axes=axes)

        X, Y = self.get_horizontal_line(self.calc_overlap_depth_for_pingrate(speed, pingrate))
        axes.plot(X, Y)

        plot_xmin = self.get_beam_xmin(depth)
        plot_xmax = overlap_sbes.get_beam_xmax(depth)
        plot_width = plot_xmax - plot_xmin
        if add_bottom:
            axes.plot([plot_xmin - 0.25 * plot_width, plot_xmax + 0.25 * plot_width], [-depth, -depth])

        if print_vars:
            print("Seafloor depth:", round(depth,2), "m")
            print("Ship speed:    ", round(speed,2), "knots")
            print("overlap depth: ", round(overlapdepth,2), "m")
            print("---")
            print("calculated ping distance:", round(overlap_sbes.x,2), "m")
            print("calculated pingrate:     ", round(pingrate,2), "pings/second", "\t|\t", round(1 / pingrate,2), "seconds/ping")



    plt_title = "SBES overlap"
    plt_xlabel = "Alongtrack (m)"
    plt_ylabel = "Depth (m)"
    plt_aspect = False
    plt_grid = True

    def make_figure(self, title=None, xlabel=None, ylabel=None, aspect=None, grid=None):
        if title is None: title = self.plt_title
        if xlabel is None: xlabel = self.plt_xlabel
        if ylabel is None: ylabel = self.plt_ylabel
        if aspect is None: aspect = self.plt_aspect
        if grid is None: grid = self.plt_grid

        fig = plt.figure(title)
        plt.clf()
        prepare_plt(plt, title, xlabel, ylabel, aspect=aspect,grid=grid)
        return fig

    @staticmethod
    def show():
        plt.show()




from matplotlib import pyplot as plt
if __name__ == "__main__":
    sbes = SBES(1)

    depth = 140
    overlapdepth = 120
    speed = 5
    pingrate = 1.2
    aspect = False

    plot_xmin = sbes.get_beam_xmin(depth)
    plot_xmax = sbes.get_beam_xmax(depth)
    plot_width = plot_xmax - plot_xmin

    print("\n---\nsbes1 - pingoverlap at pingrate\n---")
    #sbes.make_figure("sbes1 - pingoverlap at pingrate")
    sbes.plot_pingoverlap_at_pingrate(depth, speed, pingrate)
    plt.show()

    print("\n---\nsbes2 pingoverlap at overlapdept\n---")
    #sbes.make_figure("sbes2 pingoverlap at overlapdept")
    sbes.plot_pingoverlap_at_overlapdepth(depth, speed, overlapdepth)
    plt.show()
