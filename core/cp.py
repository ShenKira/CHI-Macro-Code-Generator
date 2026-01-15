# -*- coding: utf-8 -*-
"""
Created on 2026年1月10日

CP experiment implementation compatible with the Experiment base class.
"""

from core.experiment import Experiment
from utils.filename import format_number, format_scientific


class CPExperiment(Experiment):
    def __init__(self, ic: float, ia: float, eh: float, heht: float,
                 el: float, leht: float, tc: float = 10, ta: float = 10,
                 pn: str = 'n', si: float = 0.0025, cl: int = 1):
        super().__init__("CP")

        self.ic = ic
        self.ia = ia
        self.eh = eh
        self.heht = heht
        self.el = el
        self.leht = leht
        self.tc = tc
        self.ta = ta
        self.pn = pn
        self.si = si
        self.cl = cl

    def signature(self) -> tuple:
        return (
            self.ic, self.ia, self.eh, self.heht,
            self.el, self.leht, self.tc, self.ta,
            self.pn, self.si, self.cl,
        )

    def estimate_time(self) -> float:
        # A simple estimate: each segment contains cathodic+anodic periods
        # plus potential holds. This is a heuristic for UI time display.
        per_segment = self.tc + self.heht + self.ta + self.leht
        return per_segment * self.cl

    def summary(self) -> str:
        return (
            f"ic={self.ic:.3g} A | ia={self.ia:.3g} A | "
            f"eh={self.eh:.3g} V | cl={self.cl}"
        )

    def to_macro(self, project_name: str) -> str:
        # 电流值可能很小，用科学记数法格式化
        ic_str = f"{self.ic:.10e}".rstrip('0').rstrip('.')
        ia_str = f"{self.ia:.10e}".rstrip('0').rstrip('.')
        ic_fmt = format_scientific(ic_str)
        ia_fmt = format_scientific(ia_str)
        eh_fmt = format_number(self.eh)
        
        fname = f"{project_name}_CP_{ic_fmt}_{ia_fmt}_{eh_fmt}V"
        return f"""
tech=cp
ic={self.ic}
ia={self.ia}
eh={self.eh}
heht={self.heht}
el={self.el}
leht={self.leht}
tc={self.tc}
ta={self.ta}
pn={self.pn}
si={self.si}
cl={self.cl}
prioe
run
save:{fname}
tsave:{fname}
""".strip().strip()

    def get_filenames(self, project_name: str) -> list:
        # 电流值可能很小，用科学记数法格式化
        ic_str = f"{self.ic:.10e}".rstrip('0').rstrip('.')
        ia_str = f"{self.ia:.10e}".rstrip('0').rstrip('.')
        ic_fmt = format_scientific(ic_str)
        ia_fmt = format_scientific(ia_str)
        eh_fmt = format_number(self.eh)
        
        fname = f"{project_name}_CP_{ic_fmt}_{ia_fmt}_{eh_fmt}V"
        return [fname]