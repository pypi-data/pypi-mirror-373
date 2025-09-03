# SPDX-FileCopyrightText: 2022 Peter Urban, Sven Schorge, GEOMAR Helmholtz Centre for Ocean
# Research Kiel SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

from math import tan, radians, degrees, sin, asin, cos, pi, sqrt
import math
import numpy as np
from copy import deepcopy

from themachinethatgoesping.scripts.oceanographic import knots_to_ms
from themachinethatgoesping.scripts.sbes import SBES
from themachinethatgoesping.scripts.plot_tools import prepare_plt

# @package scipts
# Simple scripts for calculations with an sbes
#


## simple sbes calculation class
class MBES:

    ## The consructor
    # @param swathopening_angle: opening angle of the mbes swath
    # @param beamopening_angle_along:  alongtrack  opening angle of the mbes swath
    # @param beamopening_angle_across: acrosstrack opening angle of the mbes swath
    # @param x: x offset (positive along track)
    # @param y: y offset (positive starboard side)
    # @param z: z offset (positive downwards)
    def __init__(self,
                 swathopening_angle,
                 beamopening_angle_along,
                 beamopening_angle_across,
                 seafloor_alpha =0,
                 seafloor_beta = 0,
                 max_range_factor = 2,
                 x = 0,
                 y = 0,
                 z = 0):
        self.beamopening_angle_across  = beamopening_angle_across
        self.beamopening_angle_along  = beamopening_angle_along
        self.swathopening_angle = swathopening_angle
        self.x = x
        self.y = y
        self.z = z
        self.draw_delta_angle = 0.1

        self.max_range_factor = max_range_factor


        self.sbes = SBES(beamopening_angle_along,x,z)
        self.sbes.plt_title = "MBES Alongtrack overlap"

        #self.seafloor_depth = seafloor_depth
        self.seafloor_alpha = seafloor_alpha
        self.seafloor_beta  = seafloor_beta



    def get_seafloor_depth(self,depth,y = None,x = None):
        if x is None: x = self.x
        if y is None: y = self.y
        return depth - y* tan(radians(self.seafloor_alpha) - x*tan(radians(self.seafloor_beta)))

    def get_seafloor_y_distance(self,depth,beamangle):

        if math.fabs(self.seafloor_alpha) == 90: return np.nan
        if beamangle == 0: return 0

        # return max range y in case they are not intersecting
        if beamangle < 0 and self.seafloor_alpha > 0 and -beamangle > 90 - self.seafloor_alpha: return np.nan
        if beamangle > 0 and self.seafloor_alpha < 0 and  beamangle > 90 + self.seafloor_alpha: return np.nan
        #if beamangle > 0 and beamangle > -90 + self.seafloor_alpha: return self.max_range*sin(radians(beamangle))

        d = self.get_seafloor_depth(depth) - self.z #depth below transducer

        return d / (tan(radians(self.seafloor_alpha)) + 1 / (tan(radians(beamangle))))


    def get_minslant_range(self,depth):
        #if self.seafloor_alpha > self.swathopening_angle/2: return

        return (self.get_seafloor_depth(depth) - self.z) * cos(radians(self.seafloor_alpha))

    ## --- sbes functions ---
    ## Footprint along
    def calc_footprint_along(self, depth: float) -> float:
        return self.sbes.calc_footprint(depth)

    ## Footprint across
    def calc_footprint_across(self, depth: float) -> float:
        return self.sbes.calc_footprint(depth,
                                        beamopening_angle=self.beamopening_angle_across)

    ## swath width
    def calc_swathwidth(self, depth: float) -> float:
        return self.sbes.calc_footprint(depth,self.swathopening_angle)


    ## alongtrack overlap pingrate
    def calc_along_overlap_pingrate(self,speed : float,depth: float) -> float:
        return self.sbes.calc_overlap_pingrate(speed,depth)

    @staticmethod
    def calc_along_pingdistance(speed, pingrate):
        return SBES.calc_pingdistance(speed,pingrate)

    def calc_along_overlap_depth(self, delta_x):
        return self.sbes.calc_overlap_depth(delta_x)

    def calc_along_overlap_depth_for_pingrate(self, speed, pingrate):
        return self.sbes.calc_overlap_depth_for_pingrate(speed,pingrate)


    #--- MBES function ---

    def get_swath_ymin_z(self,depth : float) -> float:

        outer_beam_angle    = -self.swathopening_angle/2
        seafloor_y_position =  self.get_seafloor_y_distance(depth,outer_beam_angle) + self.y


        if seafloor_y_position and not math.isnan(seafloor_y_position):
            return seafloor_y_position, -self.get_seafloor_depth(depth,y=seafloor_y_position)
        else:
            max_range = depth*self.max_range_factor
            #if no intersection use max range
            return sin(radians(outer_beam_angle))*max_range + self.y,-cos(radians(outer_beam_angle))*max_range - self.z

    def get_swath_ymax_z(self, depth: float) -> float:
        outer_beam_angle    = self.swathopening_angle/2
        seafloor_y_position = self.get_seafloor_y_distance(depth,outer_beam_angle) + self.y


        if seafloor_y_position and not math.isnan(seafloor_y_position):
            return seafloor_y_position, -self.get_seafloor_depth(depth,y=seafloor_y_position)
        else:
            max_range = depth*self.max_range_factor
            #if no intersection use max range
            return sin(radians(outer_beam_angle))*max_range + self.y,-cos(radians(outer_beam_angle))*max_range - self.z

    ## return a vector with the limits of the outer swath
    # @param depth: Depth at which the pings should overlap
    def get_swath_limits(self,depth: float)-> tuple:

        ymin,z_ymin = self.get_swath_ymin_z(depth)
        ymax,z_ymax = self.get_swath_ymax_z(depth)


        return [ymin,self.y,ymax],[z_ymin,-self.z,z_ymax]

        ## return a vector with a horizontal line inside the swath
        # @param depth: Depth of line
    def get_horizontal_line(self, depth: float, extent = 0,ymin=None,ymax=None) -> tuple:
        if ymin is None: ymin,z_ymin =  self.get_swath_ymin_z(depth)
        else:                 z_ymin = -self.get_seafloor_depth(depth,y=ymin)

        if ymax is None: ymax,z_ymax =  self.get_swath_ymax_z(depth)
        else:                 z_ymax = -self.get_seafloor_depth(depth,y=ymax)

        ymin   -= cos(radians(self.seafloor_alpha)) * extent
        z_ymin -= sin(radians(self.seafloor_alpha)) * extent
        ymax   += cos(radians(self.seafloor_alpha)) * extent
        z_ymax += sin(radians(self.seafloor_alpha)) * extent

        return [ymin, ymax], [z_ymin,z_ymax]

    def get_sidelobe_circle(self, depth):
        # create side-lobe circles
        cl_x = []
        cl_y = []
        gamma = self.swathopening_angle * pi / 180.0
        #depth_under_transducer = -self.z + self.get_seafloor_depth(depth)
        minsant_range = self.get_minslant_range(depth)

        for g in np.linspace(-gamma / 2, gamma / 2, int(round(self.swathopening_angle / self.draw_delta_angle))):
            #x = -depth_under_transducer * sin(g) + self.y
            #y = -depth_under_transducer * cos(g) + -self.z
            x = -minsant_range * sin(g) + self.y
            y = -minsant_range * cos(g) + -self.z

            cl_x.append(x)
            cl_y.append(y)

        return cl_x, cl_y


    ## --- mbes functions ---

    def calc_minslant_bottom_distance(self,depth,y_distance):
        d = depth - self.z  #depth_below_transducer

        #check if it will exceed the maximum height
        beta = degrees(asin(y_distance/d))
        if beta > self.swathopening_angle/2:
            return np.nan
        #if not self.calc_minsland_visible_height(depth,y_distance ) >= 0:
        #    return np.nan

        try:
            minslant_bottom_distance = d - sqrt(d**2 - y_distance**2)

            return minslant_bottom_distance
        except:
            return np.nan

    def calc_minsland_visible_height(self,depth,y_distance,max_bottom_distance = None):
        try:
            d = depth - self.z  #depth_below_transducer
            minsland_visible_height = sqrt(d**2 - y_distance**2) - (y_distance/tan(radians(self.swathopening_angle/2)))

            if minsland_visible_height < 0: return np.nan

            if not max_bottom_distance:
                max_bottom_distance = d

            if minsland_visible_height + self.calc_minslant_bottom_distance(depth,y_distance) > max_bottom_distance:
                minsland_visible_height = max_bottom_distance - self.calc_minslant_bottom_distance(depth,y_distance)


            return minsland_visible_height
        except:
            return np.nan

    def calc_linespacing(self,depth,
                         max_minslant_bottom_distance,
                         min_minslant_visible_distance = None,
                         max_flare_height = None):
        d = depth - self.z  #depth_below_transducer
        linespacing = d

        if max_minslant_bottom_distance:
            linespacing_a = 2*sqrt(2*d*max_minslant_bottom_distance - max_minslant_bottom_distance**2)


        else:
            linespacing_a = None


        if min_minslant_visible_distance is None:
            min_minslant_visible_distance = max_minslant_bottom_distance

        if min_minslant_visible_distance:

            # angle where the pings overlap
            outer_beam_angle=self.swathopening_angle/2

            #use pen and paper
            tan_a = tan(radians(outer_beam_angle))
            k     = min_minslant_visible_distance
            a = 1+1/(tan_a**2)
            p = 2*k/tan_a
            q = k**2 - d**2

            p /= a
            q /= a

            linespacing_b = -(p/2) + sqrt((p/2)**2 - q)
            linespacing_b *=2



            try:
                if max_flare_height is not None and max_flare_height < d:

                    mmbd = max_flare_height - min_minslant_visible_distance
                    linespacing_c = 2 * sqrt(2 * d * mmbd - mmbd ** 2)

                    print("C", linespacing_c)
                    if linespacing_c < linespacing_b:
                        linespacing_b = linespacing_c
            except:
                pass

        else:
            linespacing_b = None

        if linespacing_a is not None:
            if linespacing_b is not None:
                if linespacing_b < linespacing_a:   linespacing = linespacing_b
                else:                               linespacing = linespacing_a
            else:
                linespacing = linespacing_a
        elif linespacing_b is not None:
            linespacing = linespacing_b



        return linespacing



    def plot_along(self,depth,color,add_bottom,axes=None):
        self.sbes.plot(depth,color,add_bottom,axes=axes)

    def plot_along_pingoverlap_at_pingrate(self, depth, speed, pingrate, color1='r', color2='b',
                                     print_vars=True,
                                           add_bottom = True,
                                                axes = None):
        self.sbes.plot_pingoverlap_at_pingrate(depth,speed,pingrate,color1,color2,
                                               print_vars,add_bottom,axes=axes)

    def plot_along_pingoverlap_at_overlapdepth(self, depth, speed, overlapdepth, color1='r', color2='b',
                                                print_vars=True,
                                                add_bottom = True,
                                                axes = None):
        self.sbes.plot_pingoverlap_at_overlapdepth(depth, speed, overlapdepth, color1, color2,
                                             print_vars,add_bottom,axes=axes)

    def plot_across_swathoverlap_at_linespacing(self,depth,linespacing,max_flare_height=None,
                                                        color1 = 'orange',color2 ='purple',
                                                        print_vars=True,
                                                        add_bottom=True,
                                                        axes = None,
                                                        make_figure=True,
                                                        limit_plot = True):
        if axes is None:
            axes = plt
            if make_figure: self.make_figure()

        self.plot(depth, color1,add_bottom=False,axes = axes,limit_plot=False)

        overlap_mbes = deepcopy(self)
        overlap_mbes.y = linespacing + self.y
        overlap_mbes.plot(depth, color2,add_bottom=False,axes = axes,limit_plot=False)

        #-- calculate --

        plot_xmin,_ = self.get_swath_ymin_z(depth)
        plot_xmax,_ = overlap_mbes.get_swath_ymax_z(depth)
        plot_width = plot_xmax - plot_xmin

        if add_bottom:
            X, Y = self.get_horizontal_line(depth, plot_width * 0.05, plot_xmin, plot_xmax)
            axes.plot(X, Y)
            # axes.plot([plot_xmin - 0.05 * plot_width, plot_xmax + 0.05 * plot_width], [-depth, -depth])

        if self.seafloor_alpha == 0:
            minslant_bottom_distance = self.calc_minslant_bottom_distance(depth, overlap_mbes.y / 2)
            minslant_visible_height = self.calc_minsland_visible_height(depth, overlap_mbes.y / 2, max_flare_height)

            minslant_o_x   = overlap_mbes.y / 2
            minslant_o_y_0 = -depth
            minslant_o_y_1 = minslant_o_y_0 + minslant_bottom_distance
            minslant_o_y_2 = minslant_o_y_1 + minslant_visible_height

            minslant_bottom_distance_color='red'
            minslant_visible_height_color='blue'

            axes.plot([minslant_o_x, minslant_o_x],[minslant_o_y_0, minslant_o_y_1],
                     minslant_bottom_distance_color)
            axes.plot([minslant_o_x, minslant_o_x],[minslant_o_y_1, minslant_o_y_2],
                     minslant_visible_height_color)




            if True: #add_bars
                axes.plot([minslant_o_x - plot_width * 0.01, minslant_o_x + plot_width * 0.01],
                         [minslant_o_y_2, minslant_o_y_2],
                         minslant_visible_height_color)

            if True: #add_bars
                axes.plot([minslant_o_x - plot_width * 0.01, minslant_o_x + plot_width * 0.01],
                         [minslant_o_y_1, minslant_o_y_1],
                         minslant_bottom_distance_color)
                axes.plot([minslant_o_x - plot_width * 0.01, minslant_o_x + plot_width * 0.01],
                         [minslant_o_y_0, minslant_o_y_0],
                         minslant_bottom_distance_color)

        if print_vars:
            print("Seafloor depth:", round(depth, 2), "m")
            print("Linespacing:   ", round(linespacing, 2), "m")
            if self.seafloor_alpha == 0:
                print("---")
                print("calculated minslant_bottom_distance", round(minslant_bottom_distance, 2), "m")
                print("calculated minslant_visible_height", round(minslant_visible_height, 2), "m")

        if limit_plot:
            ylimit_max = self.get_seafloor_depth(depth) *1.25
            l1 = self.get_seafloor_depth(depth,y=plot_xmin)
            l2 = self.get_seafloor_depth(depth,y=plot_xmax)
            if l1 > ylimit_max or l2 > ylimit_max or l1 < 0 or l2 < 0:
                axes = plt.gca()
                axes.set_xlim([-depth *2, depth*2])
                axes.set_ylim([-depth *1.25, 0])



    def plot_across_swathoverlap_at_max_bottom_distance(self,depth,max_minslant_bottom_distance,min_minslant_visible_height=None,max_flare_height=None,
                                                        color1 = 'orange',color2 ='purple',
                                                        print_vars=True,
                                                        add_bottom=True,
                                                        axes = None,
                                                        make_figure=True,
                                                        limit_plot = True):

        if axes is None:
            axes = plt
            if make_figure: self.make_figure()

        self.plot(depth, color1,add_bottom=False,axes=axes,limit_plot=False)

        linespacing = self.calc_linespacing(depth,max_minslant_bottom_distance,min_minslant_visible_height,max_flare_height)

        overlap_mbes = deepcopy(self)
        overlap_mbes.y = linespacing+self.y
        overlap_mbes.plot(depth, color2,add_bottom=False,axes=axes,limit_plot=False)

        #-- calculate --

        plot_xmin,_ = self.get_swath_ymin_z(depth)
        plot_xmax,_ = overlap_mbes.get_swath_ymax_z(depth)
        plot_width = plot_xmax - plot_xmin


        minslant_bottom_distance = self.calc_minslant_bottom_distance(depth, overlap_mbes.y / 2)
        minslant_visible_height = self.calc_minsland_visible_height(depth, overlap_mbes.y / 2, max_flare_height)

        minslant_o_x   = overlap_mbes.y / 2
        minslant_o_y_0 = -depth
        minslant_o_y_1 = minslant_o_y_0 + minslant_bottom_distance
        minslant_o_y_2 = minslant_o_y_1 + minslant_visible_height

        minslant_bottom_distance_color='red'
        minslant_visible_height_color='blue'

        plt.plot([minslant_o_x, minslant_o_x],[minslant_o_y_0, minslant_o_y_1],
                 minslant_bottom_distance_color)
        plt.plot([minslant_o_x, minslant_o_x],[minslant_o_y_1, minslant_o_y_2],
                 minslant_visible_height_color)




        if add_bottom:
            X,Y = self.get_horizontal_line(depth,plot_width*0.05,plot_xmin,plot_xmax)
            axes.plot(X,Y)

        if True: #add_bars
            axes.plot([minslant_o_x - plot_width * 0.01, minslant_o_x + plot_width * 0.01],
                     [minslant_o_y_2, minslant_o_y_2],
                     minslant_visible_height_color)

        if True: #add_bars
            axes.plot([minslant_o_x - plot_width * 0.01, minslant_o_x + plot_width * 0.01],
                     [minslant_o_y_1, minslant_o_y_1],
                     minslant_bottom_distance_color)
            axes.plot([minslant_o_x - plot_width * 0.01, minslant_o_x + plot_width * 0.01],
                     [minslant_o_y_0, minslant_o_y_0],
                     minslant_bottom_distance_color)

        if print_vars:
            print("Seafloor depth:", round(depth, 2), "m")
            print("max_minslant_bottom_distance:   ", round(max_minslant_bottom_distance, 2), "m")
            print("---")
            print("calculated Linespacing:   ", round(linespacing, 2), "m")
            print("calculated minslant_bottom_distance", round(minslant_bottom_distance, 2), "m")
            print("calculated minslant_visible_height", round(minslant_visible_height, 2), "m")


        if limit_plot:
            ylimit_max = self.get_seafloor_depth(depth) *1.25
            l1 = self.get_seafloor_depth(depth,y=plot_xmin)
            l2 = self.get_seafloor_depth(depth,y=plot_xmax)
            if l1 > ylimit_max or l2 > ylimit_max or l1 < 0 or l2 < 0:
                axes = plt.gca()
                axes.set_xlim([-depth *2, depth*2])
                axes.set_ylim([-depth *1.25, 0])


    def plot(self,depth,color,add_bottom=True,axes=None,limit_plot = True):

        line_dict = {}

        if axes is None: axes = plt

        X, Y = self.get_swath_limits(depth)
        clx, cly = self.get_sidelobe_circle(depth)
        axes.plot(X,Y,color)
        axes.plot(clx,cly,color)

        line_dict['mbes'] = [X,Y,color]
        line_dict['minslant'] = [clx,cly,color]

        plot_xmin,_ = self.get_swath_ymin_z(depth)
        plot_xmax,_ = self.get_swath_ymax_z(depth)
        plot_width = plot_xmax - plot_xmin
        if add_bottom:
            X,Y = self.get_horizontal_line(depth,plot_width*0.05)
            axes.plot(X,Y)
            line_dict['bottom'] = [X,Y,None]


        if limit_plot:
            ylimit_max = self.get_seafloor_depth(depth) *1.25
            l1 = self.get_seafloor_depth(depth,y=plot_xmin)
            l2 = self.get_seafloor_depth(depth,y=plot_xmax)
            if l1 > ylimit_max or l2 > ylimit_max or l1 < 0 or l2 < 0:
                axes = plt.gca()
                axes.set_xlim([-depth *2, depth*2])
                axes.set_ylim([-depth *1.25, 0])

        return line_dict


    plt_title="MBES overlap"
    plt_xlabel="Alongtrack (m)"
    plt_ylabel="Depth (m)"
    plt_aspect=True
    plt_grid=True

    def make_figure(self,title=None,xlabel=None,ylabel=None,aspect=None,grid=None):
        if title    is None: title  = self.plt_title
        if xlabel   is None: xlabel = self.plt_xlabel
        if ylabel   is None: ylabel = self.plt_ylabel
        if aspect   is None: aspect = self.plt_aspect
        if grid     is None: grid   = self.plt_grid

        fig = plt.figure(title)
        plt.clf()
        prepare_plt(plt, title, xlabel, ylabel, aspect=aspect,grid=grid)
        return fig

    @staticmethod
    def show():
        plt.show()




from matplotlib import pyplot as plt
if __name__ == "__main__":
    # mbes parameters
    mbes = MBES(120, 1, 2, z=5)

    depth = 50
    min_minslant_bottom_distance = (depth - 5) / 5
    min_minslant_7bottom_distance = None
    linespacing = depth
    linespacing = 40
    aspect = False
    max_bottom_distance = 20
    min_visible_height = 20
    max_flare_height = 80

    plot_xmin,_ = mbes.get_swath_ymin_z(depth)
    plot_xmax,_ = mbes.get_swath_ymax_z(depth)
    plot_width = plot_xmax - plot_xmin

    print("\n---\nmbes1 - plot_across_swathoverlap_at_linespacing\n---")
    #mbes.make_figure("mbes1 - plot_across_swathoverlap_at_linespacing")

    mbes.plot_across_swathoverlap_at_linespacing(depth, linespacing, max_flare_height)
    print()

    plt.show()




    print("\n---\nmbes2 - plot_across_swathoverlap_at_max_bottom_distance\n---")
    #mbes.make_figure("mbes2 - plot_across_swathoverlap_at_max_bottom_distance")


    mbes.plot_across_swathoverlap_at_max_bottom_distance(depth, max_bottom_distance, min_visible_height,
                                                         max_flare_height)
    print()

    sbes = SBES(7, x=-5, z=5)
    sbes.plot(depth, 'green')

    plt.show()


