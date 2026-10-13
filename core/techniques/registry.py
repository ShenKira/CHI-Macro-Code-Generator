"""Explicit imports, never filesystem scanning or importlib plugins."""
from core.techniques.voltammetry import TECHNIQUES as VOLTAMMETRY
from core.techniques.amperometry import TECHNIQUES as AMPEROMETRY
from core.techniques.impedance import TECHNIQUES as IMPEDANCE
from core.techniques.potentiometry import TECHNIQUES as POTENTIOMETRY

_ALL = (*VOLTAMMETRY, *AMPEROMETRY, *IMPEDANCE, *POTENTIOMETRY)
TECHNIQUES = {item.code: item for item in _ALL}
ALIASES = {"IMP": "EIS", "I-T": "IT", "CPCS": "ISTEP"}
DEFAULT_QUICK = ("CV", "EIS", "CP", "IT", "PSA")


def canonical_type(code):
    code = str(code).upper()
    return ALIASES.get(code, code)


def get_technique(code):
    code = canonical_type(code)
    try:
        return TECHNIQUES[code]
    except KeyError:
        raise ValueError(f"未知试验类型：{code}") from None


def create_experiment(code, values=None):
    # All imports below are static and discoverable by Nuitka.
    from core.cp import CPExperiment
    from core.cv import CVExperiment
    from core.eis import EISExperiment
    from core.it import ITExperiment
    from core.configured_experiment import ConfiguredExperiment
    code = canonical_type(code)
    values = dict(values or {})
    factory = {"CP": CPExperiment, "CV": CVExperiment, "EIS": EISExperiment, "IT": ITExperiment}
    if code in factory:
        return factory[code](**values)
    return ConfiguredExperiment(code, values)
