# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:07:03 2025

@author: shenz
"""

import math

AVAILABLE_SENS = [
    1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2
]


def auto_sensitivity(capacitance: float, v: float) -> float:
    """
    capacitance: F，在 0.1 V/s 下测得
    """
    scale = math.log10(0.1 / v)
    c_eff = capacitance * (2 ** scale)

    i_max = c_eff * v
    required = 1.5 * i_max

    for sens in AVAILABLE_SENS:
        if 10 * sens >= required:
            return sens

    return AVAILABLE_SENS[-1]


def sens_to_str(sens: float) -> str:
    """
    将 0.001 → '1e-3'
    """
    if sens == 0:
        return "0"
    exponent = int(round(math.log10(sens)))
    return f"1e{exponent}"
