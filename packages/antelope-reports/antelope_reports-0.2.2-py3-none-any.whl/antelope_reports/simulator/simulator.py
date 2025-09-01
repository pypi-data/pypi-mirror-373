"""
Stochastic Simulator

This performs iterative scenario analysis using stochastic simulation.  Only total scores are accessible,
no aggregation or grouping is performed.

The simulator accepts one or more cases, and one or more simulation variants. Each variant is defined by
a set of parameters (fragments) whose exchange values vary according to a specification.  The variants can
either be "simple" (in which case the user specified the parameter values explicitly) or "stochastic" (in which
the parameter values are drawn from a distribution).
"""
from .parameter import LognormalParameter, UniformParameter, DirichletParameters
from collections import defaultdict
from math import floor, ceil
from pandas import DataFrame
from antelope_foreground.fragment_flows import frag_flow_lcia


class StochasticSimulator:
    def _scenario_spec(self, case):
        return tuple((*self._common_scenarios, *self._cases[case]))

    def _variant_spec(self, case, i):
        return tuple((*self._scenario_spec(case), i))

    def __init__(self, model, *common_scenarios):
        self._model = model

        self._common_scenarios = set()

        for c in common_scenarios:
            self.add_common_scenario(c)

        self._c = list()
        self._cases = defaultdict(set)
        self._v = list()
        self._variants = dict()
        self._simple = set()
        self._params = defaultdict(list)

        self._quantities = list()

        self._baselines = dict()  # case, quantity -> LciaResult
        self._results = dict()  # case, variant, quantity -> list of floats

    @property
    def cases(self):
        for c in self._c:
            yield c

    @property
    def variants(self):
        for v in self._v:
            yield v

    @property
    def quantities(self):
        for q in self._quantities:
            yield q

    def add_common_scenario(self, scenario):
        if isinstance(scenario, tuple):
            for sc in scenario:
                self._common_scenarios.add(sc)
        else:
            self._common_scenarios.add(scenario)

    def add_case(self, case, *case_params):
        if case not in self._c:
            self._c.append(case)
        for p in case_params:
            self._cases[case].add(p)

    def _check_match(self, variant, param):
        for p in self._params[variant]:
            if p.match(param):
                raise KeyError('Parameter %5.5s already specified' % param.uuid)

    def add_stochastic_variant(self, variant, key, n):
        """

        :param variant:
        :param key: a float value to index the observations
        :param n: the number of observations to conduct.
        :return:
        """
        if variant not in self._v:
            self._v.append(variant)
        self._variants[variant] = (key, n)

    def add_simple_variant(self, variant, key):
        if variant not in self._v:
            self._v.append(variant)
        self._simple.add(variant)
        self._variants[variant] = (key, 0)

    def add_uniform_parameter(self, variant, param, low, high):
        self._check_match(variant, param)
        self._params[variant].append(UniformParameter(param, low, high))

    def add_lognormal_parameter(self, variant, param, shape):
        self._check_match(variant, param)
        self._params[variant].append(LognormalParameter(param, shape))

    def add_dirichlet_parameters(self, variant, *fragments, scale=1.0, alpha=None):
        fs = list(fragments)
        for f in fs:
            self._check_match(variant, f)
        self._params[variant].append(DirichletParameters(*fs, scale=scale, alpha=alpha))

    def add_simple_parameter(self, variant, fragment, *values, mult=True, scenario=None):
        """
        In a simple variant, parameter values are specified directly by the modeler rather than from a stochastic
        process.  The number of "simulations" to run equals the maximum number of parameter values provided.
        :param variant:
        :param fragment:
        :param values:
        :param mult: whether the values are multiplicative or absolue
        :param scenario: for multiplicative params only, the scenario to use as baseline
        :return:
        """
        if variant not in self._simple:
            raise KeyError('Not a simple variant: %s' % variant)
        vals = list(values)
        key, n = self._variants[variant]
        if len(vals) > n:
            n = len(vals)
            self._variants[variant] = (key, n)
        if mult:
            if scenario is None:
                baseline = fragment.observed_ev
            else:
                baseline = fragment.exchange_value(scenario)
        else:
            baseline = 1.0

        for i, v in enumerate(vals):
            val = v * baseline
            fragment.observe(val, scenario=key+i)

    def observe_parameters(self, variant):
        key, n = self._variants[variant]
        for param in self._params[variant]:
            for i in range(n):
                param.observe(key+i)

    def run_baseline(self, quantity):
        if quantity not in self._quantities:
            self._quantities.append(quantity)
        for case in self.cases:
            sc = self._scenario_spec(case)
            r = self._model.fragment_lcia(quantity, scenario=sc)
            self._baselines[case, quantity] = r

    def run_variant(self, variant):
        for case in self.cases:
            self.run_case_variant(case, variant)

    def run_all(self):
        for variant in self.variants:
            self.run_variant(variant)

    def run_case_variant(self, case, variant):
        key, n = self._variants[variant]
        # reset scores
        for quantity in self.quantities:
            self._results[case, variant, quantity] = []

        # compute scores
        for i in range(n):
            ffs = self._model.traverse(scenario=self._variant_spec(case, key+i))
            for quantity in self.quantities:
                self._results[case, variant, quantity].append(frag_flow_lcia(ffs, quantity).total())
        print('%s {%s}: completed %d simulations' % (case, variant, n))

    def _5_95_ci(self, case, variant, quantity):
        r = self._results[case, variant, quantity]
        _ss = sorted(r)
        _ln = len(_ss)
        return _ss[int(floor(0.05*_ln))], _ss[int(ceil(0.95*_ln)) - 1]

    def baseline(self, case, quantity):
        return self._baselines[case, quantity]

    def result(self, case, variant, quantity):
        return self._results[case, variant, quantity]

    def output_row(self, case, variant, quantity):
        baseline = self._baselines[case, quantity].total()
        low_5, high_95 = self._5_95_ci(case, variant, quantity)
        return {
            'Case': case,
            'Variant': variant,
            'Quantity': quantity['ShortName'],
            'Indicator': quantity['Indicator'],
            'Unit': quantity.unit,
            'Baseline': baseline,
            'Low_5': low_5,
            'High_95': high_95
        }

    def output_table(self):
        return DataFrame((self.output_row(c, v, q) for c in self.cases for v in self.variants for q in self.quantities))
