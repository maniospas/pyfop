import numpy as np


class Tautology:
    def __init__(self, **kwargs):
        pass

    def __call__(self, x):
        return x


class Normalize:
    def __init__(self, norm=2, **kwargs):
        self.norm = norm

    def __call__(self, x):
        return x / (np.sum(x**self.norm))**(1./self.norm)


class Dot:
    def __init__(self, **kwargs):
        pass

    def __call__(self, x, y):
        return np.sum(x*y)


class KLdivergence:
    def __init__(self, epsilon=np.finfo(float).eps, **kwargs):
        if kwargs.get("norm", 1) != 1:
            raise Exception("KLDivergence should not work on non-L1 normalizations")
        self.epsilon = epsilon

    def __call__(self, x, y):
        return np.sum(x*np.log(x/(y+self.epsilon)+self.epsilon))


class Similarity:
    def __init__(self, transform, measure, **kwargs):
        self.transform = transform
        self.measure = measure
        self.kwargs = kwargs

    def __call__(self, x, y):
        measure = self.measure(**self.kwargs)
        transform = self.transform(**self.kwargs)
        return measure(transform(x), transform(y))


x = np.array([1., 1., 1.])
y = np.array([1., 0., 1.])
print(Similarity(Normalize, KLdivergence, norm=1)(x, y))
