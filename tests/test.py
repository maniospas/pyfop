import pyfop as pfp
import pytest


def test_multi_arg():
    @pfp.forward
    def increment(x, y):
        return x + y
    assert increment(1, 2).call() == 3


def test_simple_call():
    @pfp.forward
    def increment(x):
        return x + 1
    assert increment(1).call() == 2
    assert increment(increment(1)).call() == 3


def test_aspect_nameless():
    @pfp.forward
    def increment(x, inc=pfp.Aspect()):
        return x + inc
    assert increment(1).call(inc=2) == 3


def test_aspect_default():
    @pfp.forward
    def increment(x, inc=pfp.Aspect(3)):
        return x + inc
    assert increment(1).call() == 4


def test_multi_call():
    @pfp.forward
    def increment(x, inc=pfp.Aspect(1)):
        return x + inc
    #assert increment(increment(1)).call(inc=2) == 5  # 1+2+2
    #assert increment(increment(1, 2), 3).call(inc=2) == 6  # 1+2+3
    #assert increment(increment(1, 2), 3).call() == 6  # 1+2+3
    #assert increment(increment(1), 3).call() == 7  # 1+3+3 (external scope overrides internal scope)
    assert increment(increment(1, 3)).call() == 7  # 1+3+3 (internal scope also overrides external scope)


def test_scope_escaping():
    import numpy as np

    @pfp.forward
    def dot(x, y):
        return np.sum(x*y)

    @pfp.forward
    def KLdivergence(x, y, normalization=pfp.Aspect("L1")):
        if normalization != "L1":
            raise Exception("KLDivergence can only work with L1 normalization")
        return np.sum(x*np.log(x/y))

    @pfp.forward
    def normalizer(x, normalization=pfp.Aspect()):
        if normalization == "L1":
            return x / np.sum(x)
        if normalization == "L2":
            return x / np.sqrt(np.sum(x*x))
        raise Exception("Invalid normalization type")

    def similarity(x, y, measure, normalization=pfp.Aspect()):
        return measure(normalizer(x, normalization), normalizer(y, normalization)).call()

    x = np.array([1., 1., 1.])
    y = np.array([1., 1., 1.])
    assert similarity(x, y, KLdivergence) == 0
    print(similarity(x, y, dot, normalization="L2"))
    #assert similarity(x, y, dot, normalization="L2") == 1
    with pytest.raises(Exception):
        assert similarity(x, y, KLdivergence, normalization="L2") == 0



def test_intermediate_operations():
    @pfp.forward
    def add(x, permutation=pfp.Aspect(1)):
        return x + permutation

    @pfp.forward
    def mult(x, permutation=pfp.Aspect(2)):
        return x * permutation

    intermediate = add(1)
    ret = mult(intermediate)
    assert ret.call() == 4
    assert ret.run(permutation=2) == 6


def test_class_initialization():
    @pfp.forward
    class Tester:
        def __init__(self, x, scale=pfp.Aspect()):
            self.x = x
            self.scale = scale

        def apply(self):
            self.x /= self.scale
            return self

    test_obj = Tester(2)
    print(test_obj.apply().apply().run(scale=2.))
