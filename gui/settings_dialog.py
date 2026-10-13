"""Quick-add selection and editable, validated macro command overrides."""
import copy
import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QListWidget, QListWidgetItem, QPushButton, QDialogButtonBox,
    QPlainTextEdit, QLabel, QMessageBox, QLineEdit)
from PySide6.QtCore import Qt
from core.techniques.registry import TECHNIQUES


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("试验设置")
        self.resize(720, 650)
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        page = QWidget()
        quick_layout = QVBoxLayout(page)
        explanation = QLabel("勾选快捷添加的试验；列表顺序即按钮顺序。未勾选的试验仍可从“添加其他试验”选择。")
        explanation.setWordWrap(True)
        quick_layout.addWidget(explanation)
        self.list = QListWidget()
        ordered = list(config.quick_experiments) + [code for code in TECHNIQUES if code not in config.quick_experiments]
        for code in ordered:
            item = QListWidgetItem(f"{code} — {TECHNIQUES[code].name}")
            item.setData(Qt.UserRole, code)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if code in config.quick_experiments else Qt.Unchecked)
            self.list.addItem(item)
        quick_layout.addWidget(self.list)
        moves = QHBoxLayout()
        for text, delta in (("上移", -1), ("下移", 1)):
            button = QPushButton(text)
            button.clicked.connect(lambda _, d=delta: self.move_item(d))
            moves.addWidget(button)
        quick_layout.addLayout(moves)
        self.tabs.addTab(page, "快捷添加")
        mapping_page = QWidget()
        mapping_layout = QVBoxLayout(mapping_page)
        info = QLabel("CHM 未给出命令的参数不会被猜测或忽略。这里可补充已在 CHI 软件中确认的映射："
                      "每种试验包含 tech 技术名与 parameters 参数名映射。开关参数需为每个选项提供独立命令。"
                      "具体格式见 docs/TECHNIQUE_MAPPING.md。")
        info.setWordWrap(True)
        mapping_layout.addWidget(info)
        self.mapping = QPlainTextEdit(json.dumps(config.macro_overrides, ensure_ascii=False, indent=2))
        mapping_layout.addWidget(self.mapping)
        self.tabs.addTab(mapping_page, "宏命令映射")
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("设置文件"))
        path_edit = QLineEdit(str(config.path))
        path_edit.setReadOnly(True)
        path_edit.setToolTip(str(config.path))
        path_row.addWidget(path_edit, 1)
        layout.addLayout(path_row)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("保存设置")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def move_item(self, delta):
        row = self.list.currentRow()
        if row < 0 or not 0 <= row + delta < self.list.count():
            return
        item = self.list.takeItem(row)
        self.list.insertItem(row + delta, item)
        self.list.setCurrentRow(row + delta)

    def accept(self):
        data = copy.deepcopy(self.config.data)
        data["quick_experiments"] = [self.list.item(i).data(Qt.UserRole)
                                    for i in range(self.list.count())
                                    if self.list.item(i).checkState() == Qt.Checked]
        try:
            data["macro_overrides"] = json.loads(self.mapping.toPlainText())
            self.config.save(data)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "设置未保存", str(exc))
            return
        super().accept()
