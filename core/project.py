# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:06:36 2025

@author: shenz
"""

from core.experiment import Experiment
from core.configured_experiment import MacroMappingError
from utils.filename import validate_project_name
from datetime import datetime
import json
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
        counters = {}
        for exp in self.experiments:
            exp.start_index = counters.get(exp.exp_type, 1)
            counters[exp.exp_type] = exp.start_index + exp.repeat

    def time_info(self) -> tuple[float, int, bool]:
        durations = [exp.estimate_time() for exp in self.experiments]
        return (sum(t for t in durations if t is not None),
                sum(t is None for t in durations),
                any(exp.time_is_upper_bound for exp in self.experiments))

    def total_time(self) -> float | None:
        known, unknown, _ = self.time_info()
        return None if unknown else known
    
    def update(self, name: str, folder: str):
        """更新项目名和路径"""
        self.name = name
        self.folder = folder

    def macro_issues(self, macro_overrides=None) -> list[str]:
        issues = []
        for i, exp in enumerate(self.experiments, 1):
            try:
                exp.parameter_commands(macro_overrides)
            except ValueError as exc:
                issues.append(f"第 {i} 项 {exp.exp_type}：{exc}")
        return issues

    def to_macro(self, macro_overrides=None) -> str:
        if not validate_project_name(self.name):
            raise ValueError("项目名为空或包含文件名／宏命令不允许的字符。")
        if not self.folder or any(c in self.folder for c in "\r\n#;"):
            raise ValueError("输出目录为空或包含宏命令不允许的字符。")
        issues = self.macro_issues(macro_overrides)
        if issues:
            raise MacroMappingError("\n".join(issues))
        self._reindex()
        now = datetime.now().strftime("%Y/%m/%d  %H:%M")

        header = [
            f"# Generated On {now}",
            f"# Powered By ModularTagShen",   # ← 你的昵称
            f"folder:{self.folder}",
        ]

        blocks = header[:]
        for exp in self.experiments:
            blocks.append(exp.to_macro(self.name, macro_overrides))

        return "\n\n".join(blocks)

    def to_dict(self) -> dict:
        """序列化整个项目为字典"""
        return {
            "schema_version": 2,
            "project_name": self.name,
            "folder": self.folder,
            "experiments": [exp.to_dict() for exp in self.experiments],
        }

    def save_to_json(self, path: str):
        """保存项目到 JSON 文件"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def from_dict(data: dict) -> "Project":
        """从字典恢复项目（不依赖文件）"""
        proj = Project(data["project_name"], data["folder"])
        for exp_data in data.get("experiments", []):
            exp = Experiment.from_dict(exp_data)
            proj.experiments.append(exp)
        proj._reindex()
        return proj

    @staticmethod
    def load_from_json(path: str) -> "Project":
        """从 JSON 文件加载项目"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Project.from_dict(data)

    def get_save_paths(self) -> list:
        """返回将由宏保存的所有目标文件的绝对路径列表。"""
        # 确保索引已分配（EIS start_index, CV index 等）
        self._reindex()

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
