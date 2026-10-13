"""Convenience wrapper around the common PSA form."""
from gui.experiment_dialog import ExperimentDialog


class PSADialog(ExperimentDialog):
    def __init__(self, parent=None, config=None, experiment=None):
        super().__init__("PSA", parent, config, experiment)
