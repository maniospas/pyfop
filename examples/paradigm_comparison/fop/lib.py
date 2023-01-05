from pyfop import lazy, autoaspects, Aspect, Priority
import numpy as np


@lazy
def tautology(x):
    return x


@lazy
def normalize(x, norm=Aspect(2, Priority.LOW)):
    return x / (np.sum(x**norm))**(1./norm)


@lazy
def dot(x, y):
    return np.sum(x*y)


@lazy
@autoaspects
def KL(x, y, norm=1, epsilon=np.finfo(float).eps):
    if norm != 1:
        raise Exception("KLDivergence should not work on non-L1 normalizations")
    return np.sum(x*np.log(x/(y+epsilon)+epsilon))
