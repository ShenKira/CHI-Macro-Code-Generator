"""Compatibility wrapper around the common parameter form."""
from gui.experiment_dialog import ExperimentDialog


class ITDialog(ExperimentDialog):
    def __init__(self, parent=None, config=None, experiment=None):
        super().__init__("IT", parent, config, experiment)
