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


def test_input_context_detection():
    @pfp.lazy
    def increment(x, inc=pfp.Aspect(3)):
        return x + inc

    @pfp.lazy
    def scale(x, slope=pfp.Aspect(2)):
        return x*slope

    assert 'inc' in increment(scale(1)).get_input_context()
    assert 'slope' in increment(scale(1)).get_input_context()
    assert 'unknown' not in increment(scale(1)).get_input_context()
    assert increment(scale(1)).get_input_context(slope=4)['slope'] == 4
    assert "value: 2" in str(increment(scale(1)).get_input_context())
    assert "value: 3" in str(increment(scale(1)).get_input_context(slope=5))
    assert "value: 5" in str(increment(scale(1)).get_input_context(slope=5))


def test_aspect_default_operations():
    @pfp.lazy
    def strange(x, inc=pfp.Aspect(3)):
        return x+inc

    y1 = abs((strange(1)*2 + 1) / 3-6) == 3
    assert y1.call()
    with pytest.raises(Exception):
        assert (not y1).call(inc=2)  # assert error check for not converting to bool


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
        return np.sum(x * y)

    @pfp.lazy
    def KLdivergence(x, y, normalization=pfp.Aspect("L1")):
        if normalization != "L1":
            raise Exception("KLDivergence can only work with L1 normalization")
        return np.sum(x * np.log(x / y))

    @pfp.lazy
    def normalizer(x, normalization=pfp.Aspect("L2", priority=pfp.Priority.LOW)):
        if normalization == "L1":
            return x / np.sum(x)
        if normalization == "L2":
            return x / np.sqrt(np.sum(x * x))
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
    # print(similarity(x, y, dot, normalization="L2"))
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
    #with pytest.raises(Exception):  # TODO: fix this
    #    assert ret.call(permutation=3) == 6


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
        r1 = np.sum(x)
        r2 = np.mean(y)
    assert str((r1 + r2).call(axis=0)) == str(desired)
    assert np.sum(x) == 9


def test_immutability_operations():
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


def test_lazy_lists():
    @pfp.lazy
    @pfp.autoaspects
    def zeros(length=10, default=0):
        return [default] * length
    assert zeros()[0](default=1) == 1


def test_eager_autoaspect_cache():
    @pfp.eager
    @pfp.autoaspects
    def zeros(length=10):
        return [0] * length

    assert id(zeros(9)) != id(zeros(10))
    assert id(zeros(10)) == id(zeros(10))


def test_eager_no_cache():
    @pfp.eager_no_cache
    @pfp.autoaspects
    def zeros(length=10):
        return [0] * length

    assert id(zeros(9)) != id(zeros(10))
    assert id(zeros(10)) != id(zeros(10))


def test_lazy_no_cache():
    @pfp.lazy_no_cache
    @pfp.autoaspects
    def zeros(length=10):
        return [0] * length
    assert id(zeros()(length=9)) != id(zeros()(length=10))
    assert id(zeros()(length=10)) != id(zeros()(length=10))


def test_cache_scope():
    @pfp.eager
    @pfp.autoaspects
    def zeros(length=10):
        return [0] * length

    with pfp.CacheScope():
        id1 = id(zeros(10))
        assert id1 == id(zeros(10))

    assert id1 != id(zeros(10))


def test_lazy_defaults():
    @pfp.lazy
    class Convergence:
        @pfp.autoaspects
        def __init__(self, iters=10):
            self.iter = 0
            self.iters = iters

        def converged(self, value):
            self.iter += 1
            return self.iter == self.iters

    @pfp.lazy
    @pfp.autoaspects
    def exp(value, convergence=Convergence()):
        ret = value
        while not convergence.converged(value):
            ret *= value
        return ret

    @pfp.lazy
    def default_base():
        return 2

    assert exp(2).call(iters=4) == 16
    assert exp(default_base()).call(iters=4) == 16
    assert exp(2, convergence=Convergence(5)).call() == 32
    with pytest.raises(Exception):
        assert exp(2, convergence=Convergence(5)).call(iters=6) == 64  # conflicting values
    assert exp(2, convergence=Convergence()).call(iters=6) == 64


def test_autoaspects_placement():
    @pfp.lazy
    @pfp.autoaspects
    class Convergence:
        def __init__(self, iters=10):
            self.iter = 0
            self.iters = iters

        def converged(self, value):
            self.iter += 1
            return self.iter == self.iters

    convergence = Convergence(3).call()
    assert convergence.converged(None) is False
    assert convergence.converged(None) is False
    assert convergence.converged(None) is True
