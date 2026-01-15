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
import os



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

    def get_save_paths(self) -> list:
        """返回将由宏保存的所有目标文件的绝对路径列表。"""
        # 确保索引已分配（EIS start_index, CV index 等）
        try:
            self._reindex()
        except Exception:
            pass

        paths = []
        for exp in self.experiments:
            # 每个实验应实现 get_filenames(project_name)
            if not hasattr(exp, "get_filenames"):
                continue
            fnames = exp.get_filenames(self.name)
            for fname in fnames:
                # fname 可能使用 '/' 作为子目录分隔符，按平台转换并生成绝对路径
                parts = fname.split("/")
                full = os.path.abspath(os.path.normpath(os.path.join(self.folder, *parts)))
                paths.append(full)
        return paths
