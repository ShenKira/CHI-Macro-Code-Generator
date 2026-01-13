# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:05:58 2025

@author: shenz
"""

from core.experiment import Experiment
from utils.sensitivity import auto_sensitivity
from utils.time_estimate import estimate_cv_time
from utils.sensitivity import sens_to_str

class CVExperiment(Experiment):
    def __init__(
        self,
        ei: float,
        eh: float,
        v: float,
        cl: int,
        capacitance: float | None = None,
        sens: float | None = None,
        el: float = 0.0,
        ef: float = 0.0,
    ):
        super().__init__("CV")

        self.ei = ei
        self.eh = eh
        self.el = el
        self.ef = ef
        self.v = v
        self.cl = cl
        self.capacitance = capacitance

        # 自动灵敏度
        if sens is None and capacitance is not None:
            self.sens = auto_sensitivity(capacitance, v)
            self.sens_source = "auto"
        else:
            self.sens = sens
            self.sens_source = "manual"

        self.index = None  # 由 Project 分配

    def signature(self) -> tuple:
        return (
            self.ei,
            self.eh,
            self.el,
            self.ef,
            self.v,
            self.cl,
            self.sens,
        )

    def estimate_time(self) -> float:
        return estimate_cv_time(self.eh, self.el, self.v, self.cl)

    def to_macro(self, project_name: str) -> str:
        fname = f"{project_name}_CV_{self.eh}V_{self.v}V/s"
        if self.index is not None:
            fname += f"_{self.index}"

        return f"""
tech=cv
ei={self.ei}
eh={self.eh}
el={self.el}
ef={self.ef}

v={self.v}
cl={self.cl}
sens={sens_to_str(self.sens)}
run
save:{fname}
tsave:{fname}
""".strip()
