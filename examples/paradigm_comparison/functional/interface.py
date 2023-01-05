from .lib import normalize, KL


class Similarity:
    def __init__(self, transform, measure, **kwargs):
        self.transform = transform
        self.measure = measure
        self.kwargs = kwargs

    def __call__(self, x, y):
        if self.transform == normalize and self.measure == KL:
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
        if self.measure == KL and "epsilon" in self.kwargs:
            return self.measure(x, y, epsilon=self.kwargs["epsilon"])
        return self.measure(x, y)
