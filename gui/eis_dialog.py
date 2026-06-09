# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:10:08 2025

@author: shenz
"""

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox
)
from core.eis import EISExperiment


class EISDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加 EIS")

        self.fh = QLineEdit("1e6")
        self.fl = QLineEdit("0.01")
        self.amp = QLineEdit("0.005")
        self.qt = QLineEdit("2")
        self.rep = QLineEdit("3")

        form = QFormLayout(self)
        form.addRow("最高频率", self.fh)
        form.addRow("最低频率", self.fl)
        form.addRow("幅度", self.amp)
        form.addRow("静息时间", self.qt)
        form.addRow("重复次数", self.rep)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

    def accept(self):
        self.result = EISExperiment(
            int(float(self.fh.text())),
            float(self.fl.text()),
            float(self.amp.text()),
            float(self.qt.text()),
            int(self.rep.text()),
        )
        super().accept()
