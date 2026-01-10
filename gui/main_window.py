# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:09:21 2025

@author: shenz
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel,
    QFileDialog, QTableWidget, QTableWidgetItem
)
from core.project import Project
from gui.cv_dialog import CVDialog
from gui.eis_dialog import EISDialog
from gui.macro_dialog import MacroDialog
from gui.cp_dialog import CPDialog
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt

import math


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CHI Macro Generator")

        self.project = None

        self.project_name = QLineEdit()
        self.folder_edit = QLineEdit()
        browse_btn = QPushButton("浏览…")
        browse_btn.clicked.connect(self.select_folder)

        top = QHBoxLayout()
        top.addWidget(QLabel("项目名"))
        top.addWidget(self.project_name)
        top.addWidget(QLabel("输出路径"))
        top.addWidget(self.folder_edit)
        top.addWidget(browse_btn)

        self.add_cv_btn = QPushButton("添加 CV")
        self.add_eis_btn = QPushButton("添加 EIS")
        self.add_cp_btn = QPushButton("添加 CP")
        self.add_cv_btn.clicked.connect(self.add_cv)
        self.add_eis_btn.clicked.connect(self.add_eis)
        self.add_cp_btn.clicked.connect(self.add_cp)

        left = QVBoxLayout()
        left.addWidget(self.add_cv_btn)
        left.addWidget(self.add_eis_btn)
        left.addWidget(self.add_cp_btn)
        left.addStretch()

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["序号", "类型", "参数摘要"])
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_menu)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 序号
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 类型
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # 参数摘要


        center = QHBoxLayout()
        center.addLayout(left)
        center.addWidget(self.table)

        self.time_label = QLabel("预计耗时：00:00")

        gen_btn = QPushButton("生成代码")
        gen_btn.clicked.connect(self.generate_macro)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addLayout(center)
        layout.addWidget(self.time_label)
        layout.addWidget(gen_btn)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self.folder_edit.setText(folder)

    def ensure_project(self):
        if not self.project:
            self.project = Project(
                self.project_name.text(),
                self.folder_edit.text()
            )
        else:
            # 更新现有项目的名称和路径
            self.project.update(
                self.project_name.text(),
                self.folder_edit.text()
            )

    def add_cv(self):
        self.ensure_project()
        dlg = CVDialog(self)
        if dlg.exec():
            self.project.add_experiment(dlg.result)
            self.refresh()

    def add_eis(self):
        self.ensure_project()
        dlg = EISDialog(self)
        if dlg.exec():
            self.project.add_experiment(dlg.result)
            self.refresh()

    def add_cp(self):
        self.ensure_project()
        dlg = CPDialog(self)
        if dlg.exec():
            self.project.add_experiment(dlg.result)
            self.refresh()

    def refresh(self):
        self.table.setRowCount(len(self.project.experiments))
        for i, exp in enumerate(self.project.experiments):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(exp.exp_type))
            if exp.exp_type == "CV":
                summary = f"{exp.eh:.2g} V | {exp.v:.3g} V/s | cl={exp.cl} | sens={exp.sens:.1e}"
            else:
                summary = exp.summary()
            self.table.setItem(i, 2, QTableWidgetItem(summary))


        t = self.project.total_time()
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        self.time_label.setText(f"预计耗时：{h:02d}:{m:02d}")

    def generate_macro(self):
        if not self.project:
            return
        # 生成前更新项目的最新信息
        self.project.update(
            self.project_name.text(),
            self.folder_edit.text()
        )
        dlg = MacroDialog(self.project)
        dlg.exec()
        
        
    def show_table_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
    
        menu = QMenu(self)
        delete_action = menu.addAction("删除该实验")
    
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == delete_action:
            self.delete_experiment(row)
            
    def delete_experiment(self, row):
        if not self.project:
            return
        if row < 0 or row >= len(self.project.experiments):
            return
    
        del self.project.experiments[row]
        self.refresh()


