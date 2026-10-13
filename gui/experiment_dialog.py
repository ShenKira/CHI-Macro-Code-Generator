"""A single metadata-driven form for every supported technique."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QWidget, QScrollArea, QTabWidget, QLineEdit, QComboBox, QCheckBox,
    QDialogButtonBox, QLabel, QPlainTextEdit, QMessageBox, QPushButton)
from core.techniques.registry import get_technique, create_experiment
from utils.app_config import AppConfig


class ExperimentDialog(QDialog):
    def __init__(self, exp_type, parent=None, config=None, experiment=None):
        super().__init__(parent)
        self.definition = get_technique(exp_type)
        self.config = config if config is not None else AppConfig()
        self.experiment = None
        self.editing = experiment is not None
        self.setWindowTitle(f"{'编辑' if self.editing else '添加'} {self.definition.code} — {self.definition.name}")
        self.resize(750, 640)
        values = (experiment.parameters if experiment else
                  self.config.data["last_parameters"].get(self.definition.code, {}))
        self.inputs = {}
        self.enablers = {}
        layout = QVBoxLayout(self)
        note = self.definition.note
        if self.definition.tech is None:
            note += "\n当前文档没有技术宏名称；参数配置可以保存，缺少映射时暂不能导出宏。"
        if note:
            label = QLabel(note)
            label.setWordWrap(True)
            layout.addWidget(label)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        page = QWidget()
        form = QFormLayout(page)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        for field in self.definition.parameters:
            value = values.get(field.key, field.default)
            if field.kind == "choice":
                widget = QComboBox()
                for stored, label, _ in field.choices:
                    widget.addItem(label, stored)
                selected = widget.findData(value)
                if selected >= 0:
                    widget.setCurrentIndex(selected)
                widget.currentIndexChanged.connect(self.update_preview)
            else:
                fallback = field.minimum if field.minimum is not None else 0
                widget = QLineEdit(str(value if value is not None else fallback))
                widget.setPlaceholderText("支持科学计数法，例如 1e-4")
                widget.textChanged.connect(self.update_preview)
            widget.setObjectName(field.key)
            limits = ""
            if field.minimum is not None:
                limits = f"范围：{field.minimum:g} – {field.maximum:g}。"
            widget.setToolTip(limits + field.help)
            self.inputs[field.key] = widget
            if field.optional:
                container = QWidget()
                row = QHBoxLayout(container)
                row.setContentsMargins(0, 0, 0, 0)
                check = QCheckBox("设置")
                check.setChecked(value is not None)
                check.setToolTip("未勾选时不生成该参数命令，沿用 CHI 软件现有设置。")
                widget.setEnabled(value is not None)
                check.toggled.connect(widget.setEnabled)
                check.toggled.connect(self.update_preview)
                row.addWidget(check)
                row.addWidget(widget, 1)
                self.enablers[field.key] = check
                form.addRow(field.label, container)
            else:
                form.addRow(field.label, widget)
            # Compatibility with the old dialogs' public field widgets.
            setattr(self, field.key, widget)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        self.tabs.addTab(scroll, "参数")
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.tabs.addTab(self.preview, "宏命令预览")
        source = QLabel(f"参数来源：chi660e.chm / {self.definition.source}")
        source.setWordWrap(True)
        layout.addWidget(source)
        reset = QPushButton("恢复默认参数")
        reset.clicked.connect(self.reset_defaults)
        presets_row = QHBoxLayout()
        presets_row.addWidget(reset)
        for title, parameters in self.definition.presets:
            preset = QPushButton(title)
            preset.setToolTip("应用此观察配置前，需先给电容预充电；此配置不会自行充到 1 V。")
            preset.clicked.connect(lambda _, values=parameters: self.apply_values(values))
            presets_row.addWidget(preset)
        layout.addLayout(presets_row)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("保存修改" if self.editing else "添加试验")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.update_preview()

    def values(self):
        result = {}
        for field in self.definition.parameters:
            if field.optional and not self.enablers[field.key].isChecked():
                result[field.key] = None
            elif field.kind == "choice":
                result[field.key] = self.inputs[field.key].currentData()
            else:
                result[field.key] = self.inputs[field.key].text().strip()
        return result

    def update_preview(self, *_):
        if not hasattr(self, "preview"):
            return
        try:
            exp = create_experiment(self.definition.code, self.values())
            text = "\n".join(exp.parameter_commands(self.config.macro_overrides))
            self.preview.setPlainText(text + "\nrun\n# 保存文件名由项目自动分配")
        except ValueError as exc:
            self.preview.setPlainText(f"暂不能生成宏：\n{exc}\n\n参数仍可保存到项目。")

    def reset_defaults(self):
        self.apply_values({field.key: field.default for field in self.definition.parameters})

    def apply_values(self, values):
        for field in self.definition.parameters:
            if field.key not in values:
                continue
            value = values[field.key]
            widget = self.inputs[field.key]
            if field.optional:
                self.enablers[field.key].setChecked(value is not None)
            if field.kind == "choice":
                widget.setCurrentIndex(max(widget.findData(value), 0))
            else:
                widget.setText(str(value if value is not None else field.minimum or 0))
        self.update_preview()

    def accept(self):
        try:
            self.experiment = create_experiment(self.definition.code, self.values())
        except (TypeError, ValueError) as exc:
            QMessageBox.warning(self, "参数有误", str(exc))
            return
        try:
            self.config.remember(self.experiment)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "参数记忆未保存", f"试验参数已接受，但无法保存到设置文件：\n{exc}")
        # Retain the original dialog API used by existing callers.
        self.result = self.experiment
        super().accept()
