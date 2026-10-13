"""I-t adapter accepting the original cycles field."""
from core.configured_experiment import ConfiguredExperiment


class ITExperiment(ConfiguredExperiment):
    def __init__(self, ei=1, si=.1, st=60, qt=0, sens=1e-5, cycles=1, **parameters):
        values = dict(ei=ei, si=si, st=st, qt=qt, sens=sens,
                      repeat=parameters.pop("repeat", cycles))
        values.update(parameters)
        super().__init__("IT", values)

    @property
    def cycles(self):
        return self.repeat
