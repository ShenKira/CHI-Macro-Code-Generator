import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from core.cp import CPExperiment
from core.cv import CVExperiment
from core.it import ITExperiment
from core.experiment import Experiment
from core.project import Project
from core.configured_experiment import MacroMappingError
from core.techniques.registry import TECHNIQUES, create_experiment
from utils.app_config import AppConfig, validate_config, application_dir

EXPECTED = {"CV", "LSV", "SCV", "TAFEL", "CA", "CC", "DPV", "NPV", "DNPV",
            "SWV", "ACV", "SHACV", "FTACV", "IT", "DPA", "DDPA", "TPA", "IPAD",
            "BE", "HMV", "SSF", "STEP", "EIS", "IMPT", "IMPE", "CP", "CPCR",
            "ISTEP", "PSA", "ECN", "OCPT"}
UNDOCUMENTED = {"FTACV", "DPA", "DDPA", "TPA", "IPAD"}


class ExperimentTests(unittest.TestCase):
    def test_catalogue_and_round_trip_every_technique(self):
        self.assertEqual(set(TECHNIQUES), EXPECTED)
        for code in EXPECTED:
            with self.subTest(code=code):
                exp = create_experiment(code)
                restored = Experiment.from_dict(json.loads(json.dumps(exp.to_dict())))
                self.assertEqual(restored.to_dict(), exp.to_dict())
                self.assertTrue(exp.definition.source.endswith(".htm"))

    def test_defaults_generate_only_documented_commands(self):
        reference = json.loads((Path(__file__).parent / "fixtures" / "macro_reference.json").read_text(encoding="utf-8"))
        for code in EXPECTED - UNDOCUMENTED:
            with self.subTest(code=code):
                commands = create_experiment(code).parameter_commands()
                self.assertIn(commands[0].split("=", 1)[1], reference["techniques"])
                for command in commands[1:]:
                    self.assertIn(command.split("=", 1)[0], reference["commands"])

    def test_undocumented_commands_never_silently_export(self):
        for code in UNDOCUMENTED:
            with self.subTest(code=code), self.assertRaises(MacroMappingError):
                create_experiment(code).to_macro("test")
        with self.assertRaises(MacroMappingError):
            create_experiment("IT", {"scales": 2}).to_macro("test")

    def test_explicit_custom_mapping_is_used_and_saved_values_are_not_ignored(self):
        exp = create_experiment("FTACV")
        # Synthetic mapping to exercise the extension path, not a claim about CHI syntax.
        mapping = {"FTACV": {"tech": "testft", "parameters": {
            p.key: "test" + p.key.replace("_", "") for p in exp.definition.parameters
            if p.command is None and not p.local}}}
        macro = exp.to_macro("test", mapping)
        self.assertIn("tech=testft", macro)
        self.assertIn("testtotalpoints=8192", macro)

    def test_cp_priority_zero_current_and_half_cycle_count(self):
        cp = CPExperiment(ic=0, ia=0, priority="time", pn="n", cl=3,
                          tc=10, ta=30, heht=3, leht=5)
        self.assertEqual(cp.estimate_time(), 63)
        self.assertIn("priot", cp.to_macro("test"))
        self.assertNotIn("prioe", cp.to_macro("test"))
        self.assertIn("ic=0.0", cp.to_macro("test"))
        self.assertEqual(CPExperiment(pn="p", cl=1, ta=30, tc=10, priority="time").estimate_time(), 30)
        self.assertIsNone(CPExperiment(ic=0, ia=0).estimate_time())

    def test_old_cp_json_and_it_cycles_remain_readable(self):
        old = dict(type="CP", ic=1e-4, ia=1e-4, eh=1, heht=0, el=0,
                   leht=0, tc=10, ta=30, pn="n", si=.0025, cl=2)
        cp = Experiment.from_dict(old)
        self.assertEqual(cp.priority, "potential")
        self.assertIn("prioe", cp.to_macro("test"))
        it = Experiment.from_dict(dict(type="IT", ei=1, si=.1, st=10, qt=0, sens=1e-5, cycles=3))
        self.assertEqual(it.repeat, 3)
        self.assertEqual(it.estimate_time(), 30)

    def test_cp_range_validation_and_scientific_notation(self):
        self.assertEqual(create_experiment("CP", {"ic": "1e-4"}).ic, 1e-4)
        for values in ({"ic": -.001}, {"ia": .3}, {"cl": 1.2}, {"cl": 0},
                       {"si": 0}, {"si": float("nan")}, {"tc": float("inf")},
                       {"pn": "invalid"}, {"priority": "invalid"}, {"eh": 0, "el": 1}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                create_experiment("CP", values)

    def test_existing_attribute_api_updates_generated_parameters(self):
        cp = CPExperiment(priority="time")
        cp.ic = 0
        self.assertIn("ic=0.0", cp.to_macro("test"))
        with self.assertRaises(ValueError):
            cp.ic = -.1
        self.assertEqual(cp.ic, 0)
        with self.assertRaises(ValueError):
            cp.eh = -1
        self.assertEqual(cp.eh, 1)

    def test_pulse_constraints_match_help_notes(self):
        for code in ("DPV", "NPV"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                create_experiment(code, {"pw": .1, "sw": .06, "prod": 1})
            with self.subTest(code=code), self.assertRaises(ValueError):
                create_experiment(code, {"pw": .6, "prod": 1})
        with self.assertRaises(ValueError):
            create_experiment("DPV", {"amp": 0})
        with self.assertRaises(ValueError):
            create_experiment("DNPV", {"sw": .009})

    def test_psa_and_ocpt_exact_parameter_commands(self):
        psa = create_experiment("PSA", {"depe": 1, "dept": 60, "i": 0, "ef": .1, "si": 1, "qt": 0})
        self.assertEqual(psa.parameter_commands(), ["tech=psa", "depe=1.0", "dept=60.0", "ef=0.1", "i=0.0", "si=1.0", "qt=0.0"])
        self.assertIsNone(psa.estimate_time())
        ocpt = create_experiment("OCPT", {"st": 3600, "si": 1})
        self.assertEqual(ocpt.estimate_time(), 3600)
        self.assertIn("si=1.0", ocpt.parameter_commands())

    def test_cv_sensitivity_and_half_cycle_duration(self):
        exp = CVExperiment(ei=0, eh=1, el=0, v=.1, cl=3)
        self.assertEqual(exp.estimate_time(), 30)
        cap = CVExperiment(ei=0, eh=1, v=.1, cl=2, sens=None, capacitance=1e-6)
        self.assertTrue(any(line.startswith("sens=") for line in cap.parameter_commands()))
        self.assertNotIn("autosens", cap.parameter_commands())
        with self.assertRaises(ValueError):
            create_experiment("CV", {"sens": "auto", "v": .1})
        self.assertIn("扫描速率", exp.summary())
        self.assertIn("扫描段数", exp.summary())
        automatic = CVExperiment(capacitance=1e-6)
        self.assertEqual(automatic.sens, "auto")

    def test_all_types_repetitions_and_reorder_have_unique_consistent_filenames(self):
        project = Project("test", "C:/data")
        for _ in range(2):
            for code in EXPECTED - UNDOCUMENTED:
                project.add_experiment(create_experiment(code, {"repeat": 2}))
        macro = project.to_macro()
        filenames = [line.split(":", 1)[1] for line in macro.splitlines() if line.startswith("save:")]
        self.assertEqual(len(filenames), len(set(filenames)))
        self.assertEqual(filenames, [name for exp in project.experiments for name in exp.get_filenames("test")])
        project.experiments.reverse()
        reversed_macro = project.to_macro()
        self.assertEqual(len([line for line in reversed_macro.splitlines() if line.startswith("run")]), len(filenames))
        restored = Project.from_dict(project.to_dict())
        self.assertEqual(restored.to_dict(), project.to_dict())

    def test_unknown_time_is_not_reported_as_zero_or_complete_total(self):
        project = Project("test", "C:/data")
        project.add_experiment(create_experiment("IT", {"st": 60}))
        project.add_experiment(create_experiment("PSA"))
        self.assertIsNone(project.total_time())
        self.assertEqual(project.time_info()[:2], (60, 1))


class ConfigTests(unittest.TestCase):
    def test_settings_persist_quick_order_and_parameters(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix=".tmp-") as root:
            config = AppConfig(Path(root) / "config" / "experiments.json")
            data = copy.deepcopy(config.data)
            data["quick_experiments"] = ["PSA", "OCPT", "CP"]
            config.save(data)
            config.remember(CPExperiment(ic=0, ia=0, priority="time"))
            restored = AppConfig(config.path)
            self.assertEqual(restored.quick_experiments, ["PSA", "OCPT", "CP"])
            self.assertEqual(restored.data["last_parameters"]["CP"]["priority"], "time")

    def test_bad_settings_remain_untouched(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix=".tmp-") as root:
            path = Path(root) / "experiments.json"
            path.write_text("broken-json", encoding="utf-8")
            config = AppConfig(path)
            self.assertIsNotNone(config.error)
            with self.assertRaises(ValueError):
                config.remember(CPExperiment())
            self.assertEqual(path.read_text(), "broken-json")

    def test_invalid_configuration_and_macro_injection_are_rejected(self):
        cases = [{"quick_experiments": ["CP", "CP"]}, {"quick_experiments": ["oops"]},
                 {"macro_overrides": {"CP": {"parameters": {"ic": "run"}}}},
                 {"macro_overrides": {"CP": {"parameters": {"ic": "ic\nrun"}}}},
                 {"macro_overrides": {"CP": {"parameters": {"nonexistent": "ic"}}}}]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_config(data)

    def test_nuitka_config_is_beside_executable_not_current_directory(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix=".tmp-") as root:
            exe = Path(root) / "dist" / "CHIMacroGenerator.exe"
            with patch("sys.argv", [str(exe)]):
                self.assertEqual(application_dir(compiled=True), exe.parent)
            source_root = Path(__file__).resolve().parents[1]
            self.assertEqual(application_dir(compiled=False), source_root)


if __name__ == "__main__":
    unittest.main()
