# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:09:21 2025

@author: shenz
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel,
    QFileDialog, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QShortcut, QKeySequence
from core.project import Project
from gui.cv_dialog import CVDialog
from gui.eis_dialog import EISDialog
from gui.macro_dialog import MacroDialog
from gui.cp_dialog import CPDialog
from utils.filename import validate_project_name
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QMenu


# ============================================================
#  UndoManager —— 基于快照的撤销栈
# ============================================================
class UndoManager:
    """保存 Project.to_dict() 快照，支持 Ctrl+Z 回退。"""
    MAX_STEPS = 50

    def __init__(self):
        self._stack: list[dict] = []

    def save(self, project: Project):
        """保存当前项目状态到撤销栈。"""
        if project is None:
            return
        snapshot = project.to_dict()
        # 去重：连续相同状态不重复保存
        if self._stack and self._stack[-1] == snapshot:
            return
        self._stack.append(snapshot)
        if len(self._stack) > self.MAX_STEPS:
            self._stack.pop(0)

    def undo(self) -> dict | None:
        """弹出最近一个快照。返回 None 表示无可撤销。"""
        if not self._stack:
            return None
        return self._stack.pop()

    @property
    def can_undo(self) -> bool:
        return len(self._stack) > 0


# ============================================================
#  DragTableWidget —— 拖拽排序，使用 InternalMove 指示器
#                       但完全由代码控制数据移动
# ============================================================
class DragTableWidget(QTableWidget):
    """支持鼠标拖拽排序的表格。

    关键设计：
    - 使用 InternalMove 模式以获得 Qt 原生的拖拽指示线
    - 重写 dropEvent，不调 super()，阻止 Qt 移动 QTableWidgetItem（避免数据丢失）
    - 设为 IgnoreAction 以阻止 startDrag 在返回后删除源行
    - 始终由外部通过 reordered 信号 + refresh() 来同步数据
    """
    reordered = Signal(int, int)  # source_row, target_row

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragDropOverwriteMode(False)   # 禁止覆盖模式
        self.setDropIndicatorShown(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def dropEvent(self, event):
        """完全接管 drop：计算出 source/target 后发信号，
           不让 Qt 执行任何 Item 移动。"""
        if event.source() != self:
            event.ignore()
            return

        source_row = self.currentRow()
        if source_row < 0:
            event.ignore()
            return

        # ---- 计算目标行 ----
        index = self.indexAt(event.position().toPoint())
        if index.isValid():
            target_row = index.row()
            # 使用 Qt 内部记录的指示器位置（AboveItem / BelowItem）
            if self.dropIndicatorPosition() == QAbstractItemView.BelowItem:
                target_row += 1
        else:
            target_row = self.rowCount()

        # 校正：若源行在目标之前，移除源行后目标索引需减一
        if source_row < target_row:
            adjusted = target_row - 1
        else:
            adjusted = target_row

        # 设为 IgnoreAction：阻止 Qt 在 startDrag 返回后因 MoveAction 而删除源行
        event.setDropAction(Qt.IgnoreAction)
        event.accept()

        # 仅在确实发生了移动时发出信号
        if adjusted != source_row and 0 <= adjusted < self.rowCount():
            self.reordered.emit(source_row, adjusted)


# ============================================================
#  MainWindow
# ============================================================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CHI Macro Generator")

        self.project = None
        self.undo_manager = UndoManager()

        # ---- 顶部：项目名 + 输出路径 ----
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

        # ---- 左侧：添加按钮 ----
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

        # ---- 中间：可拖拽表格 ----
        self.table = DragTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["序号", "类型", "参数摘要"])
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_menu)
        self.table.reordered.connect(self.on_rows_reordered)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        center = QHBoxLayout()
        center.addLayout(left)
        center.addWidget(self.table)

        # ---- 耗时标签 ----
        self.time_label = QLabel("预计耗时：00:00")

        # ---- 底栏三按钮：从文件读取 | 生成代码 | 保存实验 ----
        load_btn = QPushButton("从文件读取")
        load_btn.clicked.connect(self.load_from_file)

        gen_btn = QPushButton("生成代码")
        gen_btn.clicked.connect(self.generate_macro)

        save_btn = QPushButton("保存实验")
        save_btn.clicked.connect(self.save_to_file)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(load_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(gen_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addLayout(center)
        layout.addWidget(self.time_label)
        layout.addLayout(btn_layout)

        # ---- Ctrl+Z 撤销 ----
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self.undo)

    # ================================================================
    #  文件夹选择
    # ================================================================
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if folder:
            self.folder_edit.setText(folder)

    # ================================================================
    #  项目确保
    # ================================================================
    def ensure_project(self):
        if not self.project:
            self.project = Project(
                self.project_name.text(),
                self.folder_edit.text()
            )
        else:
            self.project.update(
                self.project_name.text(),
                self.folder_edit.text()
            )

    # ================================================================
    #  添加实验（操作前保存撤销快照）
    # ================================================================
    def add_cv(self):
        self.ensure_project()
        dlg = CVDialog(self)
        if dlg.exec():
            self._save_undo_state()
            self.project.add_experiment(dlg.result)
            self.refresh()

    def add_eis(self):
        self.ensure_project()
        dlg = EISDialog(self)
        if dlg.exec():
            self._save_undo_state()
            self.project.add_experiment(dlg.result)
            self.refresh()

    def add_cp(self):
        self.ensure_project()
        dlg = CPDialog(self)
        if dlg.exec():
            self._save_undo_state()
            self.project.add_experiment(dlg.result)
            self.refresh()

    def _save_undo_state(self):
        """保存快照到撤销管理器（在修改 project 之前调用）"""
        if self.project:
            self.undo_manager.save(self.project)

    # ================================================================
    #  表格刷新
    # ================================================================
    def refresh(self):
        if not self.project:
            self.table.setRowCount(0)
            return
        self.table.setRowCount(len(self.project.experiments))
        for i, exp in enumerate(self.project.experiments):
            idx_item = QTableWidgetItem(str(i + 1))
            self.table.setItem(i, 0, idx_item)
            self.table.setItem(i, 1, QTableWidgetItem(exp.exp_type))
            self.table.setItem(i, 2, QTableWidgetItem(exp.summary()))

        t = self.project.total_time()
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        self.time_label.setText(f"预计耗时：{h:02d}:{m:02d}")

    # ================================================================
    #  拖拽回调
    # ================================================================
    def on_rows_reordered(self, source_row: int, target_row: int):
        if not self.project:
            return
        exps = self.project.experiments
        if not (0 <= source_row < len(exps) and 0 <= target_row < len(exps)):
            return
        self._save_undo_state()
        exp = exps.pop(source_row)
        exps.insert(target_row, exp)
        self.refresh()

    # ================================================================
    #  生成宏
    # ================================================================
    def generate_macro(self):
        if not self.project or not self.project.experiments:
            return

        project_name = self.project_name.text().strip()

        if not validate_project_name(project_name):
            QMessageBox.warning(
                self,
                "项目名非法",
                "项目名不能包含 '.' 或 '/' 字符。\n\n请修改项目名后重试。"
            )
            return

        self.project.update(project_name, self.folder_edit.text())
        dlg = MacroDialog(self.project)
        dlg.exec()

    # ================================================================
    #  保存 / 加载 JSON
    # ================================================================
    def save_to_file(self):
        if not self.project or not self.project.experiments:
            QMessageBox.information(self, "无实验", "当前没有实验可以保存。")
            return

        self.project.update(self.project_name.text(), self.folder_edit.text())

        path, _ = QFileDialog.getSaveFileName(
            self, "保存实验配置", "", "JSON 文件 (*.json)"
        )
        if not path:
            return
        try:
            self.project.save_to_json(path)
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存文件：{e}")

    def load_from_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "读取实验配置", "", "JSON 文件 (*.json)"
        )
        if not path:
            return
        try:
            new_project = Project.load_from_json(path)
        except Exception as e:
            QMessageBox.critical(self, "读取失败", f"无法读取文件：{e}")
            return

        # 保存旧状态以便撤销
        self._save_undo_state()
        self.project = new_project
        self.project_name.setText(self.project.name)
        self.folder_edit.setText(self.project.folder)
        self.refresh()

    # ================================================================
    #  Ctrl+Z 撤销
    # ================================================================
    def undo(self):
        if not self.undo_manager.can_undo:
            return
        snapshot = self.undo_manager.undo()
        if snapshot is None:
            return
        self.project = Project.from_dict(snapshot)
        self.project_name.setText(self.project.name)
        self.folder_edit.setText(self.project.folder)
        self.refresh()

    # ================================================================
    #  右键菜单：删除
    # ================================================================
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

        self._save_undo_state()
        del self.project.experiments[row]
        self.refresh()
