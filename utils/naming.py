# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:07:21 2025

@author: shenz
"""

from collections import defaultdict
from core.cv import CVExperiment
from core.it import ITExperiment


def assign_cv_indices(experiments):
    """为 CV 和 IT 实验中 signature 相同的实验分配去重序号。

    单次出现：index = None（文件名不加后缀）
    多次出现：index = 1, 2, 3...（文件名追加 _1, _2, _3）
    """
    groups = defaultdict(list)

    for exp in experiments:
        if isinstance(exp, (CVExperiment, ITExperiment)):
            groups[exp.signature()].append(exp)

    for group in groups.values():
        if len(group) == 1:
            group[0].index = None
        else:
            for i, exp in enumerate(group, start=1):
                exp.index = i
