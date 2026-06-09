# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:09:46 2025

@author: shenz
"""

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QComboBox
)
from core.cv import CVExperiment

LAST = {}


class CVDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加 CV")

        self.ei = QLineEdit(str(LAST.get("ei", "")))
        self.eh = QLineEdit(str(LAST.get("eh", "")))
        self.v = QLineEdit(str(LAST.get("v", "")))
        self.cl = QLineEdit(str(LAST.get("cl", "")))
        self.cap = QLineEdit(str(LAST.get("cap", "")))

        self.sens = QComboBox()
        self.sens.addItems(["自动", "1e-7", "1e-6", "1e-5", "1e-4", "1e-3", "1e-2"])
        self.sens_manually_set = False

        self.sens.currentIndexChanged.connect(self._on_sens_changed)
        
        self.cap.textChanged.connect(self._on_cap_changed)


        form = QFormLayout(self)
        form.addRow("初始电位", self.ei)
        form.addRow("高电位上限", self.eh)
        form.addRow("扫速 (V/s)", self.v)
        form.addRow("循环次数", self.cl)
        form.addRow("电容 (uF)", self.cap)
        form.addRow("灵敏度", self.sens)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

    def _parse_capacitance(self):
        text = self.cap.text().strip()
        if not text:
            return None
        try:
            return float(text) * 1e-6  # μF → F
        except ValueError:
            return "INVALID"
        
    def _on_sens_changed(self):
        if self.sens.currentText() != "自动":
            self.sens_manually_set = True
            
    def _on_cap_changed(self):
        if self.sens_manually_set:
            return
    
        cap = self._parse_capacitance()
        if cap in (None, "INVALID"):
            return
    
        try:
            v = float(self.v.text())
        except ValueError:
            return
    
        sens = self._auto_sens(cap, v)
        if sens is None:
            return
    
        text = f"{sens:.0e}"
        index = self.sens.findText(text)
        if index >= 0:
            self.sens.setCurrentIndex(index)
    
    def _auto_sens(self, cap_f: float, v: float) -> float:
        # 电容在不同扫速下的经验修正
        cap_eff = cap_f * (0.1 / v) ** 0.301  # log10(2)/log10(10)
    
        i_max = cap_eff * v
        i_need = i_max * 1.5
    
        for s in [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]:
            if i_need <= 10 * s:
                return s
        return 1e-2



    def accept(self):
        try:
            ei = float(self.ei.text())
            eh = float(self.eh.text())
            v = float(self.v.text())
            cl = int(self.cl.text())
        except ValueError:
            return  # 可加 QMessageBox
    
        cap = self._parse_capacitance()
        if cap == "INVALID":
            return
    
        sens = None
        if self.sens.currentText() != "自动":
            sens = float(self.sens.currentText())
    
        if cap is None and sens is None:
            return  # 必须二选一
    
        self.result = CVExperiment(
            ei=ei,
            eh=eh,
            v=v,
            cl=cl,
            capacitance=cap,
            sens=sens,
        )
    
        LAST.update(dict(ei=ei, eh=eh, v=v, cl=cl, cap=self.cap.text()))
        super().accept()
