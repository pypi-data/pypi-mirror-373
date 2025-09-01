from scipy import stats
from numpy.random import default_rng
from math import exp, sqrt

import logging


class Randomizer:
    """
    An abstract class, meant to generate unit-scaled random numbers to be multiplied by static means to generate
    distributions.
    """
    _engine = None

    @property
    def engine(self):
        return self._engine

    @property
    def rv(self):
        return self.engine.rvs()

    def value(self, scale):
        return scale * self.rv


class UniformRandomizer(Randomizer):

    def __init__(self, low, high):
        """
        The stats.uniform distribution is specified as a "low" and a "width"

        :param low:
        :param high:
        """
        if low >= high:
            raise ValueError('Invalid bounds %g -> %g' % (low, high))
        if low > 1.0 or high < 1.0:
            logging.warning('1.0 is not in bounds for this uniform randomizer')

        self.params = (low, high)
        self._engine = stats.uniform(low, high - low)


class LognormalRandomizer(Randomizer):

    def __init__(self, shape):
        """
        :param shape: the shape parameter for the lognormal distribution. This is dimensionless and should not depend
        on the mean.  The coefficient of variation is derived rom the shape parameter.

        """
        self.params = (shape,)
        self._engine = stats.lognorm(shape)

    @property
    def cv(self):
        """
        The coefficient of variation for the underlying uniform distribution
        """
        shape = self.params[0]
        return sqrt(exp(shape ** 2) - 1)


class DirichletRandomizer(Randomizer):
    """
    A Dirichlet distribution is a way of picking points across a simplex (that sum to a constant value).
    It returns a vector of random values equal to the number of input parameters.  Those parameters should
    be given weights relative to each other to bias the result, and relative to 1 to increase the concentration
    around the mean.  e.g. in the default parameterization of [1, 1, 1], all points in the simplex will be equally
    likely and they will all be centered around 1/3.  In a parameterization of [8, 1, 1], the first value will
    be in the vicinity of 0.8 the size of the others, but they will still be somewhat uniformly concentrated.
    Whereas in a parameterization of [0.8, 0.1, 0.1] the first value will be in the vicinity of 0.8, but the values
    will be biased toward the edges.
    """
    def __init__(self, *params):
        self.params = list(params)
        if len(self.params) < 2:
            logging.warning("Trivial Dirichlet distribution (N=%d(" % len(self.params))
        self._engine = default_rng()

    @property
    def rv(self):
        return self.engine.dirichlet(self.params)

    def value(self, scale):
        return [scale * k for k in self.rv]
