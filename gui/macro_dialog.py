# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 12:10:19 2025

@author: shenz
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit,
    QPushButton, QFileDialog
)


class MacroDialog(QDialog):
    def __init__(self, project):
        super().__init__()
        self.setWindowTitle("生成的 Macro")

        self.text = QTextEdit()
        self.text.setPlainText(project.to_macro())
        self.text.setReadOnly(True)

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
