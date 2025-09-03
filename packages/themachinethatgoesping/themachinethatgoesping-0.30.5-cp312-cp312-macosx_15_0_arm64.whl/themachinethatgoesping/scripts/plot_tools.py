# SPDX-FileCopyrightText: 2022 Peter Urban, Sven Schorge, GEOMAR Helmholtz Centre for Ocean
# Research Kiel SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

def prepare_plt(plt : object,
                title: str,
                xlabel: str,
                ylabel: str,
                aspect: bool = True,
                grid:   bool = True):
    # labes and scales
    plt.yscale('linear')
    plt.xscale('linear')
    plt.title(title)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    # plt.xlim(-depth, depth)

    plt.grid(grid)

    if aspect:
        axes = plt.gca()
        #axes.set_xlim([plot_xmin - 0.5 * plot_width, plot_xmax + 0.5 * plot_width])
        axes.set_aspect('equal', adjustable='box')
