# -*- coding: utf-8 -*-
"""
CP 参数对话框
"""

from PySide6.QtWidgets import (
    QDialog, QGridLayout, QLineEdit,
    QDialogButtonBox, QLabel
)
from core.cp import CPExperiment

LAST = {}


class CPDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加 CP")

        self.ic = QLineEdit(str(LAST.get("ic", "")))
        self.ia = QLineEdit(str(LAST.get("ia", "")))
        self.eh = QLineEdit(str(LAST.get("eh", "")))
        self.heht = QLineEdit(str(LAST.get("heht", "")))
        self.el = QLineEdit(str(LAST.get("el", "")))
        self.leht = QLineEdit(str(LAST.get("leht", "")))
        self.tc = QLineEdit(str(LAST.get("tc", 10)))
        self.ta = QLineEdit(str(LAST.get("ta", 10)))
        self.pn = QLineEdit(str(LAST.get("pn", "n")))
        self.si = QLineEdit(str(LAST.get("si", 0.0025)))
        self.cl = QLineEdit(str(LAST.get("cl", 1)))

        layout = QGridLayout(self)
        layout.addWidget(QLabel("阴极电流 (A)"), 0, 0)
        layout.addWidget(self.ic, 0, 1)
        layout.addWidget(QLabel("阳极电流 (A)"), 0, 2)
        layout.addWidget(self.ia, 0, 3)

        layout.addWidget(QLabel("高限电位 (V)"), 1, 0)
        layout.addWidget(self.eh, 1, 1)
        layout.addWidget(QLabel("高限电位保持时间 (s)"), 1, 2)
        layout.addWidget(self.heht, 1, 3)

        layout.addWidget(QLabel("低限电位 (V)"), 2, 0)
        layout.addWidget(self.el, 2, 1)
        layout.addWidget(QLabel("低限电位保持时间 (s)"), 2, 2)
        layout.addWidget(self.leht, 2, 3)

        layout.addWidget(QLabel("阴极时间 (s)"), 3, 0)
        layout.addWidget(self.tc, 3, 1)
        layout.addWidget(QLabel("阳极时间 (s)"), 3, 2)
        layout.addWidget(self.ta, 3, 3)

        layout.addWidget(QLabel("首步极性 (n/p)"), 4, 0)
        layout.addWidget(self.pn, 4, 1)
        layout.addWidget(QLabel("数据间隔 (s)"), 4, 2)
        layout.addWidget(self.si, 4, 3)

        layout.addWidget(QLabel("段数"), 5, 0)
        layout.addWidget(self.cl, 5, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons, 6, 0, 1, 4)

    def accept(self):
        try:
            ic = float(self.ic.text())
            ia = float(self.ia.text())
            eh = float(self.eh.text())
            heht = float(self.heht.text())
            el = float(self.el.text())
            leht = float(self.leht.text())
            tc = float(self.tc.text())
            ta = float(self.ta.text())
            pn = self.pn.text().strip() or 'n'
            si = float(self.si.text())
            cl = int(self.cl.text())
        except ValueError:
            return  # 简单地忽略，可改为消息提示

        self.result = CPExperiment(
            ic=ic,
            ia=ia,
            eh=eh,
            heht=heht,
            el=el,
            leht=leht,
            tc=tc,
            ta=ta,
            pn=pn,
            si=si,
            cl=cl,
        )

        LAST.update(dict(ic=ic, ia=ia, eh=eh, heht=heht, el=el, leht=leht,
                         tc=tc, ta=ta, pn=pn, si=si, cl=cl))
        super().accept()
