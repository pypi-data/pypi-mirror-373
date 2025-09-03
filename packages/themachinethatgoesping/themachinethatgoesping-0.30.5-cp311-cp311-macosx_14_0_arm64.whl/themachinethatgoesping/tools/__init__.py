# SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0


from . import timeconv as timeconv_ext# flake8: noqa

from themachinethatgoesping.tools_cppy import *  # flake8: noqa

# overwrite timeconv module using the loaded python extension
timeconv = timeconv_ext

__version__ = "@PROJECT_VERSION@"