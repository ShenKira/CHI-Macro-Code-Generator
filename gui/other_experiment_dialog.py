"""Searchable selection of all technique definitions."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QListWidget,
                               QListWidgetItem, QDialogButtonBox, QLabel)
from PySide6.QtCore import Qt
from core.techniques.registry import TECHNIQUES


class OtherExperimentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加其他试验")
        self.resize(640, 600)
        self.selected_type = None
        layout = QVBoxLayout(self)
        explanation = QLabel("选择试验类型；可按缩写或中文名称搜索。")
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        self.search = QLineEdit()
        self.search.setPlaceholderText("例如 OCPT、计时电流、阻抗")
        self.search.textChanged.connect(self.filter_items)
        layout.addWidget(self.search)
        self.list = QListWidget()
        for code, definition in TECHNIQUES.items():
            suffix = "（需补充宏映射）" if definition.tech is None else ""
            item = QListWidgetItem(f"{code} — {definition.name}{suffix}")
            item.setData(Qt.UserRole, code)
            self.list.addItem(item)
        self.list.itemDoubleClicked.connect(lambda _: self.accept())
        layout.addWidget(self.list)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText("设置参数")
        self.buttons.button(QDialogButtonBox.Cancel).setText("取消")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.list.setCurrentRow(0)
        self.list.currentItemChanged.connect(self.update_accept)

    def update_accept(self, *_):
        item = self.list.currentItem()
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(item is not None and not item.isHidden())

    def filter_items(self, query):
        visible = []
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(query.casefold() not in item.text().casefold())
            if not item.isHidden():
                visible.append(item)
        self.list.setCurrentItem(visible[0] if visible else None)
        self.update_accept()

    def accept(self):
        item = self.list.currentItem()
        if item is None or item.isHidden():
            return
        self.selected_type = item.data(Qt.UserRole)
        super().accept()
