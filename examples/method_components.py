import pyfop as pfp
import numpy as np


@pfp.lazy
def tautology(x):
    return x


@pfp.lazy
def normalize(x, norm=pfp.Aspect(2)):
    return x / (np.sum(x**norm))**(1./norm)


@pfp.lazy
def offset(x):
    return x+np.eps()


@pfp.lazy
def dot(x, y):
    return np.sum(x*y)


@pfp.lazy
def KLdivergence(x, y, norm=pfp.Aspect(1), epsilon=pfp.Aspect(np.finfo(float).eps)):
    if norm != 1:
        raise Exception("KLDivergence should not work on non-L1 normalizations")
    return np.sum(-x*np.log(x/(y+epsilon)+epsilon))


class Similarity:
    def __init__(self, transform, measure, **kwargs):
        self.transform = transform
        self.measure = measure
        self.kwargs = kwargs

    def __call__(self, x, y):
        return self.measure(self.transform(x), self.transform(y)).call(**self.kwargs)


x = np.array([1., 1., 1.])
y = np.array([1., 1., 1.])

print(Similarity(normalize, KLdivergence, norm=1, epsilon=0)(x, y))
