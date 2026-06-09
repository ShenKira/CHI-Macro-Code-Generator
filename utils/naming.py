# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:07:21 2025

@author: shenz
"""

from collections import defaultdict
from core.cv import CVExperiment


def assign_cv_indices(experiments):
    groups = defaultdict(list)

    for exp in experiments:
        if isinstance(exp, CVExperiment):
            groups[exp.signature()].append(exp)

    for group in groups.values():
        if len(group) == 1:
            group[0].index = None
        else:
            for i, exp in enumerate(group, start=1):
                exp.index = i
