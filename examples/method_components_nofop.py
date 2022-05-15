import numpy as np


def tautology(x):
    return x


def normalize(x, norm=2):
    return x / (np.sum(x**norm))**(1./norm)


def dot(x, y):
    return np.sum(x*y)


def KLdivergence(x, y, epsilon=np.finfo(float).eps):
    return np.sum(x*np.log(x/(y+epsilon)+epsilon))


class Similarity:
    def __init__(self, transform, measure, **kwargs):
        self.transform = transform
        self.measure = measure
        self.kwargs = kwargs

    def __call__(self, x, y):
        if self.transform == normalize and self.measure == KLdivergence:
            norm = self.kwargs.get("norm", 1)
            if norm != 1:
                raise Exception("KLDivergence should not work on non-L1 normalizations")
            x = self.transform(x, norm=norm)
            y = self.transform(y, norm=norm)
        elif self.transform == normalize:
            norm = self.kwargs.get("norm", 2)
            x = self.transform(x, norm=norm)
            y = self.transform(y, norm=norm)
        else:
            x = self.transform(x)
            y = self.transform(y)
        if self.measure == KLdivergence and "epsilon" in self.kwargs:
            return self.measure(x, y, epsilon=self.epsilon)
        return self.measure(x, y)


x = np.array([1., 1., 1.])
y = np.array([1., 0., 1.])
print(Similarity(normalize, KLdivergence, norm=1)(x, y))
