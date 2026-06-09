# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:07:33 2025

@author: shenz
"""

import math


def estimate_cv_time(eh, el, v, cl):
    return (2 * abs(eh - el) * cl) / v


def estimate_eis_time(fh, fl, repeat):
    decades = math.log10(fh / fl)
    points = decades * 10
    return repeat * points * 0.5
