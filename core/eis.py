"""EIS adapter compatible with older saved projects."""
from core.configured_experiment import ConfiguredExperiment


class EISExperiment(ConfiguredExperiment):
    def __init__(self, fh=1e6, fl=.01, amp=.005, qt=2, repeat=1, **parameters):
        values = dict(fh=fh, fl=fl, amp=amp, qt=qt, repeat=repeat)
        values.update(parameters)
        super().__init__("EIS", values)
