# SPDX-FileCopyrightText: 2022 GEOMAR Helmholtz Centre for Ocean Research Kiel
# SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

"""
themachinethatgoesping
**********************
Enable quantitative processing of multibeam and singlebeam echosounder systems
"""





# import the module functions into the current namespace
__modules_installed__ = []

# TODO: add warnings for installed packages with missing dependencies

try:
    from themachinethatgoesping import tools_cppy
    __modules_installed__.append(("tools_cppy", tools_cppy.__version__))
    from themachinethatgoesping import tools
    __modules_installed__.append(("tools", tools.__version__))
    from themachinethatgoesping import scripts
    __modules_installed__.append(("scripts", scripts.__version__))
except:
    pass

try:
    from themachinethatgoesping import algorithms
    __modules_installed__.append(("algorithms", algorithms.__version__))
except:
    pass

try:
    from themachinethatgoesping import navigation
    __modules_installed__.append(("navigation", navigation.__version__))
except:
    pass

try:
    from themachinethatgoesping import echosounders_cppy as echosounders
    __modules_installed__.append(("echosounders_cppy", echosounders_cppy.__version__))
    from themachinethatgoesping import echosounders
    __modules_installed__.append(("echosounders", echosounders.__version__))
except:
    pass

try:
    from themachinethatgoesping import pingprocessing_cppy
    __modules_installed__.append(("pingprocessing_cppy", pingprocessing_cppy.__version__))
    from themachinethatgoesping import pingprocessing
    __modules_installed__.append(("pingprocessing", pingprocessing.__version__))
except:
    pass

try:
    from themachinethatgoesping import gridding
    __modules_installed__.append(("gridding", gridding.__version__))
except:
    pass

# version
# TODO this does currently not give correct results in pydev_install.enabled() mode
# TODO this only updates the version the first time meson is executed
__version__ = "0.30.4"

# print versions


def version():
    width = 0
    for module_name, version in __modules_installed__:
        width = max(width, len(module_name))

    print("themachinethatgoesping")
    print("- {:14} {}".format("version:", __version__))
    print("\nmodules:")
    for module, version in __modules_installed__:
        print("- {:14} {}".format(module, version))


def modules():
    return version()
