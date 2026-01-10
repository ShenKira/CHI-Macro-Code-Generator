# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:06:36 2025

@author: shenz
"""

from utils.naming import assign_cv_indices
from core.cv import CVExperiment
from core.eis import EISExperiment
from core.cp import CPExperiment  
from datetime import datetime



class Project:
    def __init__(self, name: str, folder: str):
        self.name = name
        self.folder = folder
        self.experiments: list = []

    def add_experiment(self, exp):
        self.experiments.append(exp)
        self._reindex()

    def _reindex(self):
        assign_cv_indices(self.experiments)

        eis_counter = 1
        for exp in self.experiments:
            if isinstance(exp, EISExperiment):
                exp.start_index = eis_counter
                eis_counter += exp.repeat

    def total_time(self) -> float:
        return sum(exp.estimate_time() for exp in self.experiments)
    
    def update(self, name: str, folder: str):
        """更新项目名和路径"""
        self.name = name
        self.folder = folder

    def to_macro(self) -> str:
        now = datetime.now().strftime("%Y/%m/%d  %H:%M")
    
        header = [
            f"# Generated On {now}",
            f"# Powered By ModularTagShen",   # ← 你的昵称
            f"folder:{self.folder}",
        ]
    
        blocks = header[:]
        for exp in self.experiments:
            blocks.append(exp.to_macro(self.name))
    
        return "\n\n".join(blocks)
