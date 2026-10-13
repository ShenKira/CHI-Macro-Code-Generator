import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from core.techniques.registry import TECHNIQUES, create_experiment
from core.project import Project
from gui.experiment_dialog import ExperimentDialog
from gui.other_experiment_dialog import OtherExperimentDialog
from gui.settings_dialog import SettingsDialog
from gui.main_window import MainWindow
from gui.macro_dialog import MacroDialog
from utils.app_config import AppConfig


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix=".tmp-")
        self.config = AppConfig(Path(self.temp.name) / "experiments.json")

    def tearDown(self):
        self.app.processEvents()
        self.temp.cleanup()

    def test_every_form_includes_every_declared_parameter_and_accepts_defaults(self):
        for code, definition in TECHNIQUES.items():
            with self.subTest(code=code):
                dlg = ExperimentDialog(code, config=self.config)
                self.assertEqual(set(dlg.inputs), {p.key for p in definition.parameters})
                self.assertEqual(create_experiment(code, dlg.values()).exp_type, code)
                dlg.accept()
                self.assertEqual(dlg.experiment.exp_type, code)
                dlg.close()

    def test_cp_zero_current_time_priority_and_visible_validation(self):
        dlg = ExperimentDialog("CP", config=self.config)
        dlg.apply_values(dict(dlg.definition.presets[0][1]))
        self.assertEqual(create_experiment("CP", dlg.values()).estimate_time(), 3600)
        dlg.inputs["ic"].setText("0")
        dlg.inputs["ia"].setText("0")
        dlg.inputs["priority"].setCurrentIndex(dlg.inputs["priority"].findData("time"))
        self.assertIn("priot", dlg.preview.toPlainText())
        dlg.inputs["cl"].setText("1.5")
        with patch.object(QMessageBox, "warning") as warning:
            dlg.accept()
            warning.assert_called_once()
        self.assertIsNone(dlg.experiment)
        dlg.close()

    def test_quick_defaults_and_each_button_captures_its_own_type(self):
        window = MainWindow(config=self.config)
        self.assertEqual(list(window.quick_buttons), ["CV", "EIS", "CP", "IT", "PSA"])
        self.assertEqual(window.quick_tabs.tabText(0), "快捷添加")
        window.project_name.setText("test")
        window.folder_edit.setText("C:/data")
        with patch("gui.main_window.ExperimentDialog") as dialog:
            dialog.side_effect = lambda code, *_: SimpleNamespace(exec=lambda: 1, experiment=create_experiment(code))
            for button in window.quick_buttons.values():
                button.click()
        self.assertEqual([exp.exp_type for exp in window.project.experiments], list(window.quick_buttons))
        window.undo()
        self.assertEqual(len(window.project.experiments), 4)
        window.close()

    def test_quick_settings_save_and_rebuild_without_restart(self):
        dlg = SettingsDialog(self.config)
        for i in range(dlg.list.count()):
            item = dlg.list.item(i)
            item.setCheckState(Qt.Checked if item.data(Qt.UserRole) in ("PSA", "OCPT") else Qt.Unchecked)
        dlg.accept()
        window = MainWindow(config=self.config)
        self.assertEqual(list(window.quick_buttons), ["PSA", "OCPT"])
        self.assertIsNotNone(window.add_other_btn)
        window.close()
        dlg.close()

    def test_other_selector_searches_chinese_and_does_not_accept_hidden_results(self):
        dlg = OtherExperimentDialog()
        self.assertEqual(dlg.list.count(), 31)
        dlg.search.setText("开路电位")
        self.assertEqual(dlg.list.currentItem().data(Qt.UserRole), "OCPT")
        dlg.accept()
        self.assertEqual(dlg.selected_type, "OCPT")
        dlg = OtherExperimentDialog()
        dlg.search.setText("no matching technique")
        dlg.accept()
        self.assertIsNone(dlg.selected_type)
        dlg.close()

    def test_edit_and_reorder_keep_undo_and_numbering_correct(self):
        window = MainWindow(config=self.config)
        window.project = Project("test", "C:/data")
        window.project.add_experiment(create_experiment("CP", {"ic": 0, "ia": 0, "priority": "time"}))
        window.project.add_experiment(create_experiment("PSA"))
        replacement = create_experiment("CP", {"priority": "time", "tc": 30})
        with patch("gui.main_window.ExperimentDialog") as dialog:
            dialog.return_value = SimpleNamespace(exec=lambda: 1, experiment=replacement)
            window.edit_experiment(0)
        self.assertEqual(window.project.experiments[0].tc, 30)
        window.on_rows_reordered(0, 1)
        self.assertEqual(window.project.experiments[0].exp_type, "PSA")
        window.undo()
        self.assertEqual(window.project.experiments[0].exp_type, "CP")
        window.undo()
        self.assertEqual(window.project.experiments[0].tc, 10)
        window.close()

    def test_macro_preview_matches_project_and_unknown_duration_is_visible(self):
        project = Project("test", "C:/data")
        project.add_experiment(create_experiment("PSA"))
        dlg = MacroDialog(project)
        self.assertIn("i=0.0", dlg.text.toPlainText())
        self.assertIn("save:test_PSA_1", dlg.text.toPlainText())
        window = MainWindow(config=self.config)
        window.project = project
        window.refresh()
        self.assertIn("无法确定总耗时", window.time_label.text())
        window.close()
        dlg.close()


if __name__ == "__main__":
    unittest.main()
