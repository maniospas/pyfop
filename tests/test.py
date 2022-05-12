import pyfop as pfp
import pytest


def test_multi_arg():
    @pfp.lazy
    def increment(x, y):
        return x + y
    assert increment(1, 2).call() == 3


def test_simple_call():
    @pfp.lazy
    def increment(x):
        return x + 1
    assert increment(1).call() == 2
    assert increment(increment(1)).call() == 3


def test_aspect_nameless():
    @pfp.lazy
    def increment(x, inc=pfp.Aspect()):
        return x + inc
    assert increment(1).call(inc=2) == 3


def test_aspect_default():
    @pfp.lazy
    def increment(x, inc=pfp.Aspect(3)):
        return x + inc
    assert increment(1).call() == 4


def test_multi_call():
    @pfp.lazy
    def increment(x, inc=pfp.Aspect(1)):
        return x + inc
    assert increment(increment(1)).call(inc=2) == 5  # 1+2+2
    assert increment(increment(1, 4).call()).call(inc=2) == 7  # 1+4+2
    assert increment(increment(1), 3).call() == 7  # 1+3+3 (external scope overrides internal scope)
    assert increment(increment(1, 3)).call() == 7  # 1+3+3 (internal scope also overrides external scope)


def test_conflicting_declarations():
    @pfp.lazy
    def increment(x, inc=pfp.Aspect(1)):
        return x + inc
    with pytest.raises(Exception):
        increment(increment(1, 3), 2).call()
    with pytest.raises(Exception):
        print(increment(increment(1, 3), 2).call(inc=3))


def test_unused_imports():
    @pfp.lazy
    def increment(x, inc=pfp.Aspect(1)):
        return x + inc
    with pytest.raises(Exception):
        increment(increment(1), 2).call(inc=3)


def test_unused_imports():
    @pfp.lazy
    def increment(x, inc=pfp.Aspect(1)):
        return x + inc
    with pytest.raises(Exception):
        increment(increment(1)).call(incr=3)


def test_priority_comparison():
    @pfp.lazy
    def increment(x, inc=pfp.Aspect(7, priority=pfp.Priority.INCREASED)):
        return x + inc
    @pfp.lazy
    def increment2(x, inc=pfp.Aspect(11, priority=pfp.Priority.LOW)):
        return x + inc
    assert increment(increment2(0)).call() == 14
    assert increment2(increment(0)).call() == 14
    assert increment2(increment(0)).call(inc=2) == 4
    assert increment(increment(0)).call(inc=1) == 2


def test_scope_escaping():
    import numpy as np

    @pfp.lazy
    def dot(x, y):
        return np.sum(x*y)

    @pfp.lazy
    def KLdivergence(x, y, normalization=pfp.Aspect("L1")):
        if normalization != "L1":
            raise Exception("KLDivergence can only work with L1 normalization")
        return np.sum(x*np.log(x/y))

    @pfp.lazy
    def normalizer(x, normalization=pfp.Aspect("L2", priority=pfp.Priority.LOW)):
        if normalization == "L1":
            return x / np.sum(x)
        if normalization == "L2":
            return x / np.sqrt(np.sum(x*x))
        raise Exception("Invalid normalization type")

    def similarity(x, y, measure, **kwargs):
        return measure(normalizer(x, **kwargs), normalizer(y, **kwargs)).call()

    def similarity2(x, y, measure, **kwargs):
        result = measure(normalizer(x), normalizer(y))
        return result(**kwargs)

    x = np.array([1., 1., 1.])
    y = np.array([1., 1., 1.])
    assert similarity(x, y, KLdivergence) == 0
    assert similarity2(x, y, KLdivergence) == 0
    #print(similarity(x, y, dot, normalization="L2"))
    assert abs(similarity(x, y, dot) - 1) < 1.E-12
    assert abs(similarity2(x, y, dot) - 1) < 1.E-12
    assert abs(similarity(x, y, dot, normalization="L2") - 1) < 1.E-12
    assert abs(similarity2(x, y, dot, normalization="L2") - 1) < 1.E-12
    with pytest.raises(Exception):
        assert similarity(x, y, KLdivergence, normalization="L2") == 0
    with pytest.raises(Exception):
        assert similarity2(x, y, KLdivergence, normalization="L2") == 0


def test_intermediate_operations():
    @pfp.lazy
    def add(x, permutation=pfp.Aspect(1)):
        return x + permutation

    @pfp.lazy
    def mult(x, permutation=pfp.Aspect(2)):
        return x * permutation

    intermediate = add(1)
    ret = mult(intermediate)
    with pytest.raises(Exception):
        assert ret.call() == 6  # different defaults
    assert ret.call(permutation=3) == 12


def test_unused():
    @pfp.lazy
    def add(x, permutation=pfp.Aspect(1, pfp.Priority.IGNORE)):
        return x + permutation

    @pfp.lazy
    def mult(x, permutation=pfp.Aspect(2, pfp.Priority.CRITICAL)):
        return x * permutation

    intermediate = add(1)
    ret = mult(intermediate)
    assert ret.call() == 6
    with pytest.raises(Exception):
        assert ret.call(permutation=3) == 6


def test_class_initialization():
    @pfp.lazy
    class Tester:
        def __init__(self, x, scale=pfp.Aspect()):
            self.x = x
            self.scale = scale

        def apply(self):
            self.x /= self.scale
            return self

    test_obj = Tester(2)
    assert test_obj.call(scale=2.).apply().apply().x == 0.5


def test_eager():
    @pfp.lazy
    def add(x, permutation=pfp.Aspect(1)):
        return x + permutation

    @pfp.eager
    def mult(x, permutation=pfp.Aspect(2)):
        return x * permutation

    intermediate = add(1, 3)
    with pytest.raises(Exception):
        mult(intermediate, 4)  # different values for permutation aspect
    assert mult(intermediate) == 12


def test_eager_custom():
    @pfp.lazy
    def add(x, permutation=pfp.Aspect()):
        return x + permutation

    @pfp.eager
    def mult(x, permutation=pfp.Aspect()):
        return x * permutation

    assert mult(add(1, 3)) == 12
    assert mult(add(1), 3) == 12


def test_lazifier():
    import numpy as np

    x = np.array([[1., 1., 1.], [2., 2., 2.]])
    y = np.array([[1., 1., 1.], [2., 2., 2.]])

    desired = np.sum(x, axis=0) + np.mean(y, axis=0)

    with pfp.Lazifier() as lazifier:
        lazifier.lazify(np.sum)
        lazifier.lazify(np.mean)
        r1 = np.sum(x, axis=pfp.Aspect())
        r2 = np.mean(y, axis=pfp.Aspect())
    assert str((r1 + r2).call(axis=0)) == str(desired)
    assert np.sum(x) == 9


def test_immutability_operations():
    @pfp.lazy
    @pfp.memoization
    def increment(x, inc=pfp.Aspect(7, priority=pfp.Priority.INCREASED)):
        return x + inc

    @pfp.lazy
    def increment2(x, inc=pfp.Aspect(11, priority=pfp.Priority.LOW)):
        return x + inc

    assert increment(increment2(0)).call() == 14
    assert increment2(increment(0)).call() == 14
    assert increment2(increment(0)).call(inc=2) == 4
    assert increment(increment(0)).call(inc=1) == 2


def test_immutability_persistent():

    @pfp.lazy
    @pfp.autoaspects
    def increment(x, inc=7):
        return x + inc

    @pfp.lazy
    def increment2(x, inc=pfp.Aspect(11, priority=pfp.Priority.LOW)):
        return x + inc

    assert increment(increment2(0)).call() == 14
    assert increment2(increment(0)).call() == 14
    assert increment2(increment(0)).call(inc=2) == 4
    assert increment(increment(0)).call(inc=1) == 2

    """
    
    
    @pfp.lazy
    @pfp.immutable
    def value2list(value=pfp.Aspect(7)):
        return [value]

    @pfp.lazy
    def value2list_nonimmutable(value=pfp.Aspect(7)):
        return [value]

    assert id(value2list().call()) == id(value2list().call())
    assert id(value2list(2).call()) == id(value2list(2).call())
    assert id(value2list().call(value=2)) == id(value2list().call(value=2))
    assert id(value2list(3).call()) != id(value2list(2).call())
    assert id(value2list_nonimmutable(2).call()) != id(value2list_nonimmutable(2).call())
    """

def test_autoaspects():
    @pfp.lazy
    class Tester:
        @pfp.autoaspects
        def __init__(self, x, scale=1):
            self.x = x
            self.scale = scale

        def apply(self):
            self.x /= self.scale
            return self

    test_obj = Tester(2)
    assert test_obj.call(scale=2.).apply().apply().x == 0.5


def test_eager_autoaspect_memoization():
    @pfp.eager
    @pfp.memoization
    @pfp.autoaspects
    def zeros(length=10):
        return [0] * length

    assert id(zeros(9)) != id(zeros(10))
    assert id(zeros(10)) == id(zeros(10))