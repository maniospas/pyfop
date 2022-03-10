import pyfop as pfp
import numpy as np


@pfp.forward
def tautology(x):
    return x


@pfp.forward
def normalize(x, norm=pfp.Aspect(2)):
    return x / (np.sum(x**norm))**(1./norm)


@pfp.forward
def offset(x):
    return x+np.eps()


@pfp.forward
def dot(x, y):
    return np.sum(x*y)


@pfp.forward
def KLdivergence(x, y, norm=pfp.Aspect(1)):
    if norm != 1:
        raise Exception("KLDivergence should not work on L1 normalization")
    return np.sum(x*np.log(x/y))


class Similarity:
    def __init__(self, transform, measure, **kwargs):
        self.transform = transform
        self.measure = measure
        self.kwargs = kwargs

    def __call__(self, x, y):
        return self.measure(self.transform(x), self.transform(y)).call(**self.kwargs)


x = np.array([1., 1., 1.])
y = np.array([1., 1., 1.])

print(Similarity(normalize, dot, norm=2)(x, y))

