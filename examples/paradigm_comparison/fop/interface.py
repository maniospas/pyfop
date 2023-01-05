class Similarity:
    def __init__(self, transform, measure, **kwargs):
        self.transform = transform
        self.measure = measure
        self.kwargs = kwargs

    def __call__(self, x, y):
        return self.measure(self.transform(x), self.transform(y)).call(**self.kwargs)
