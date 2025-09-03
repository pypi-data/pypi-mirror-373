# SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
# SPDX-FileCopyrightText: 2022 GEOMAR Helmholtz Centre for Ocean Research Kiel
#
# SPDX-License-Identifier: MPL-2.0

"""
Simple helper functions
"""

# ------------------- Imports -------------------
import math

from numba import njit

# ---------- precompute constants ---------
M_PI = math.pi
M_PI_2 = math.pi / 2
M_2_PI = 2 * math.pi
M_PI_180 = math.pi / 180

MIN_DB_VALUE: float = -50.0

# ------------------- Functions -------------------
# Use this instead of the python internal


@njit
def round_int(val: float) -> int:
    # Helper function: rounds float to int using decimal rounding
    # instead of pythons bankers rounding

    return int(math.copysign(math.floor(math.fabs(val) + 0.5), val))


# Some testing
if __name__ == "__main__":
    print("Nothing to do")
