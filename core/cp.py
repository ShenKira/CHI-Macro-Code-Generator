"""CP adapter retaining the original constructor and flat JSON fields."""
from core.configured_experiment import ConfiguredExperiment


class CPExperiment(ConfiguredExperiment):
    def __init__(self, ic=1e-4, ia=1e-4, eh=1, heht=0, el=0, leht=0,
                 tc=10, ta=10, pn="n", si=.0025, cl=1,
                 priority="potential", aux=False, repeat=1):
        super().__init__("CP", dict(ic=ic, ia=ia, eh=eh, heht=heht, el=el, leht=leht,
                                    tc=tc, ta=ta, pn=pn, si=si, cl=cl,
                                    priority=priority, aux=aux, repeat=repeat))
