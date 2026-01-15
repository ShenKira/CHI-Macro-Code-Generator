# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:10:19 2025

@author: shenz
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit,
    QPushButton, QFileDialog, QMessageBox
)
import os


class MacroDialog(QDialog):
    def __init__(self, project):
        super().__init__()
        self.setWindowTitle("生成的 Macro")

        self.text = QTextEdit()
        self.text.setPlainText(project.to_macro())
        self.text.setReadOnly(True)

        # 在展示宏之前，检查所有将被保存的数据文件路径长度是否可能超出 Windows 限制
        try:
            paths = project.get_save_paths()
        except Exception:
            paths = []

        if paths:
            MAX_PATH = 260
            long = [p for p in paths if len(p) >= MAX_PATH]
            if long:
                sample = "\n".join(long[:10])
                more = f"\n...另外还有 {len(long)-10} 项" if len(long) > 10 else ""
                QMessageBox.warning(
                    self,
                    "路径过长",
                    "警告：以下保存路径长度可能超过 Windows 限制（260 字符）：\n\n" + sample + more
                )

        save_btn = QPushButton("保存为 TXT")
        save_btn.clicked.connect(self.save)

        layout = QVBoxLayout(self)
        layout.addWidget(save_btn)
        layout.addWidget(self.text)

    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存宏文件", "", "*.txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.toPlainText())
