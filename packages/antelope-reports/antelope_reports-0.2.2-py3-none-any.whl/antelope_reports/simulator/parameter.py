from .randomizer import UniformRandomizer, LognormalRandomizer, DirichletRandomizer


class SimulationParameter:
    frag = None
    rand = None
    mean = 1.0

    def observe(self, n):
        self.frag.observe(self.rand.value(self.mean), scenario=n)

    def match(self, frag):
        return frag == self.frag


class UniformParameter(SimulationParameter):
    def __init__(self, fragment, low, high, scenario=None):
        """

        :param fragment: The fragment to be observed
        :param low: multiplicative lower bound for the uniform distribution
        :param high: multiplicative upper bound for the uniform distribution
        :param scenario: baseline scenario for observation
        """
        self.frag = fragment
        if scenario is None:
            self.mean = fragment.observed_ev
        else:
            self.mean = fragment.exchange_value(scenario)
        self.rand = UniformRandomizer(low, high)


class LognormalParameter(SimulationParameter):
    def __init__(self, fragment, shape, scenario=None):
        """

        :param fragment: The fragment to be observed
        :param shape: dimensionless shape parameter
        :param scenario: baseline scenario for observation
        """
        self.frag = fragment
        if scenario is None:
            self.mean = fragment.observed_ev
        else:
            self.mean = fragment.exchange_value(scenario)
        self.rand = LognormalRandomizer(shape)


class DirichletParameters:
    def __init__(self, *fragments, scale=1.0, alpha=None, scenario=None):
        """
        Implement a dirichlet distribution across the specified fragments
        :param fragments:
        :param scale: [1.0] Parameters will sum to this value
        :param alpha: [None] default: use uniform distribution parameters (e.g. [1, 1, 1]).
          Specify a single float to construct a distribution based on the fragments' exchange values, so that the
          parameters sum to alpha (e.g. 3)
          Specify a list or tuple of length equal to # of fragments to specify alpha explicitly.
        :param scenario: background scenario, used only when dynamically calculating alpha parameters
        """
        self.fragments = list(fragments)
        self.scale = scale
        if alpha is None:
            self.params = tuple([1] * len(self.fragments))
        else:
            if isinstance(alpha, list) or isinstance(alpha, tuple):
                if len(alpha) == len(self.fragments):
                    self.params = tuple(alpha)
                else:
                    raise ValueError('Bad alpha specification %s' % alpha)
            else:
                try:
                    a = float(alpha)
                    if scenario is None:
                        evs = [f.observed_ev for f in self.fragments]
                    else:
                        evs = [f.exchange_value(scenario) for f in self.fragments]
                    mul = a / sum(evs)
                    self.params = tuple(mul * ev for ev in evs)
                except TypeError:
                    raise ValueError('Bad alpha specification %s' % alpha)
        self.rand = DirichletRandomizer(*self.params)

    def observe(self, n):
        ds = self.rand.value(self.scale)
        for i, f in enumerate(self.fragments):
            f.observe(ds[i], scenario=n)

    def match(self, frag):
        return any(f == frag for f in self.fragments)
