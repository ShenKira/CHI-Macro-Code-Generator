# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:06:19 2025

@author: shenz
"""

from core.experiment import Experiment
from utils.time_estimate import estimate_eis_time


class EISExperiment(Experiment):
    def __init__(
        self,
        fh: float = 1e6,
        fl: float = 0.01,
        amp: float = 0.005,
        qt: float = 2.0,
        repeat: int = 1,
    ):
        super().__init__("EIS")

        self.fh = fh
        self.fl = fl
        self.amp = amp
        self.qt = qt
        self.repeat = repeat

        self.start_index = None  # Project 分配

    def signature(self) -> tuple:
        return (self.fh, self.fl, self.amp, self.qt)

    def estimate_time(self) -> float:
        return estimate_eis_time(self.fh, self.fl, self.repeat)

    def to_macro(self, project_name: str) -> str:
        blocks = ["""
tech:imp
eio
fh:{fh}
fl:{fl}
amp:{amp}
qt:{qt}
""".format(
            fh=self.fh,
            fl=self.fl,
            amp=self.amp,
            qt=self.qt
        ).strip()]

        for i in range(self.repeat):
            idx = self.start_index + i
            fname = f"{project_name}_EIS_{idx}"
            blocks.append(f"""
run
save={fname}
tsave={fname}
""".strip())

        return "\n".join(blocks)
    def summary(self) -> str:
        return (
            f"{self.fh:.1e} Hz → {self.fl:.1e} Hz | "
            f"amp={self.amp} V | x{self.repeat}"
        )
