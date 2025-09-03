# SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

import importlib
from pkgutil import extend_path as __extend_path__

# c++ module
from themachinethatgoesping.echosounders_cppy import *  # flake8: noqa

# python only modules
from . index_functions import get_index_paths # flake8: noqa
from .evaluate.evaluate_ping_features import evaluate_ping_features_can_be_called # flake8: noqa

__version__ = "@PROJECT_VERSION@"