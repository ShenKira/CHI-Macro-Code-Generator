"""CV adapter retaining legacy fields and capacitance-based sensitivity."""
from core.configured_experiment import ConfiguredExperiment
_UNSET = object()


class CVExperiment(ConfiguredExperiment):
    def __init__(self, ei=0, eh=1, v=.1, cl=2, capacitance=None, sens=_UNSET,
                 el=0, ef=0, **parameters):
        if sens is _UNSET:
            sens = None if capacitance is not None else 1e-5
        values = dict(ei=ei, eh=eh, el=el, ef=ef, v=v, cl=cl,
                      capacitance=capacitance, sens="auto" if sens is None else sens)
        values.update(parameters)
        super().__init__("CV", values)
