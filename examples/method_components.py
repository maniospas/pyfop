from pyfop import lazy, Aspect, Priority
import numpy as np


@lazy
def tautology(x):
    return x


@lazy
def normalize(x, norm=Aspect(2, Priority.LOW)):
    return x / (np.sum(x**norm))**(1./norm)


@lazy
def offset(x):
    return x+np.eps()


@lazy
def dot(x, y):
    return np.sum(x*y)


@lazy
def KLdivergence(x, y, norm=Aspect(1), epsilon=Aspect(np.finfo(float).eps)):
    if norm != 1:
        raise Exception("KLDivergence should not work on non-L1 normalizations")
    return np.sum(x*np.log(x/(y+epsilon)+epsilon))


class Similarity:
    def __init__(self, transform, measure, **kwargs):
        self.transform = transform
        self.measure = measure
        self.kwargs = kwargs

    def __call__(self, x, y):
        return self.measure(self.transform(x), self.transform(y)).call(**self.kwargs)


x = np.array([1., 1., 1.])
#y = np.array([1., 1., 1.])
y = np.array([1., 0., 1.])
print(Similarity(normalize, KLdivergence, norm=1, epsilon=Aspect())(x, y))
