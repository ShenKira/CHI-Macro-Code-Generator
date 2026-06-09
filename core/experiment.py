# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:06:36 2025

@author: shenz
"""

from abc import ABC, abstractmethod


class Experiment(ABC):
    def __init__(self, exp_type: str):
        self.exp_type = exp_type

    @abstractmethod
    def to_macro(self, project_name: str) -> str:
        """生成 CHI Macro 代码"""
        pass

    @abstractmethod
    def estimate_time(self) -> float:
        """估算实验耗时（秒）"""
        pass

    @abstractmethod
    def signature(self) -> tuple:
        """用于判断实验是否"参数完全相同" """
        pass

    @abstractmethod
    def get_filenames(self, project_name: str) -> list:
        """返回该实验在保存数据时使用的文件名（可能有多个），不包含父目录。
        例: ['proj_CV_0.5V_0.01V/s_1']
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """序列化为字典，用于 JSON 保存"""
        pass

    @staticmethod
    def from_dict(data: dict) -> "Experiment":
        """从字典反序列化。根据 type 字段分发到对应子类。"""
        exp_type = data.get("type", "")
        if exp_type == "CV":
            from core.cv import CVExperiment
            return CVExperiment(**{k: v for k, v in data.items() if k != "type"})
        elif exp_type == "EIS":
            from core.eis import EISExperiment
            return EISExperiment(**{k: v for k, v in data.items() if k != "type"})
        elif exp_type == "CP":
            from core.cp import CPExperiment
            return CPExperiment(**{k: v for k, v in data.items() if k != "type"})
        else:
            raise ValueError(f"Unknown experiment type: {exp_type}")
