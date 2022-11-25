# pyfop
A novel forward-oriented programming paradigm for Python.

![build](https://github.com/maniospas/pyfop/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/maniospas/pyfop/branch/main/graph/badge.svg?token=MCsMLyteqD)](https://codecov.io/gh/maniospas/pyfop)
[![Downloads](https://static.pepy.tech/personalized-badge/pyfop?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/pyfop)

**Dependencies:** None<br/>
**Developer:** Emmanouil (Manios) Krasanakis<br/>
**Contant:** maniospas@hotmail.com

# :brain: About
`pyfop` is a package that introduces the concept
of forward-oriented programming in Python. This
aims to simplify development by
sharing parameters across multiple components
and defining those *after* main business logic.

# :fire: Features
* Simplified code that focuses on business logic.
* Value sharing between arguments.
* Non-intrusive API (minimal changes to source code).
* Priority-based conflict resolution.
* Scoped method modification.
* Cached optimization.
* Lazy calls with internal eager calls.

# :zap: Quickstart
Overall, there are three steps to using the library:
1. wrapping some components with a lazy execution decorator
2. assigning some arguments of these components as aspects
3. calling components

To see these in action,
let us create a system where we transform (e.g. normalize) 
`numpy` arrays and then compare them with known data mining
measures. We will make this system modular by allowing
combination of various transformation and comparison components.

First, we define a couple of single-input
array transformations `tautology` and `normalize`, 
as well as two pairwise array comparisons
`dot` and `KLdivergence`. In addition to array inputs,
some of these methods also make use of optional
parameter values, such as `norm` to indicate
the type of normalization and `epsilon` to offset
division with or logarithms of zero.

We make arguments share-able by name between
objects by wrapping their default values with the
`@pyfop.Aspect` class. For example, if `normalize`
and `KLdivergence` are used together in the same
call, their `norm` argument would obtain the same value.
This value is either determined through the priority 
defaults (the package would throw an
error if the same priorities tried to set different
values with the same priorities)
and can be customized during calls.

To parse aspects as values, we also need to set up our
methods for lazy execution required by the package.
This is achieved by adding a `@pyfop.lazy` decorator.


```python
import pyfop as pfp
import numpy as np

@pfp.lazy
def tautology(x):
    return x

@pfp.lazy
def normalize(x, norm=pfp.Aspect(2)):
    return x / (np.sum(x**norm))**(1./norm)

@pfp.lazy
def dot(x, y):
    return np.sum(x*y)

@pfp.lazy
def KLdivergence(x, y, 
                 norm=pfp.Aspect(1, priority=pfp.Priority.INCREASED), 
                 epsilon=pfp.Aspect(np.finfo(float).eps)):
    if norm != 1:
        raise Exception("KLDivergence should not work on non-L1 normalizations")
    return np.sum(-x*np.log(x/(y+epsilon)+epsilon))
```

We finally bring together various normalization and comparison
strategies in the following class. This stores lazy execution
methods as well as any additional keyword arguments `kwargs`
to be used for aspect values. Then, when comparing arrays,
it runs the lazy execution with these arguments. 

```python
class Comparator :
    def __init__(self, transform, measure, **kwargs):
        self.transform = transform
        self.measure = measure
        self.kwargs = kwargs

    def __call__(self, x, y):
        transformed_x = self.transform(x)
        transformed_y = self.transform(y)
        return self.measure(transformed_x, transformed_y).call(**self.kwargs)
```

For example, we can write the following expression to
compute the cosine similarity between two arrays. 

```python
x = np.array([1., 1., 1.])
y = np.array([1., 1., 1.])
print(Comparator(normalize, dot, norm=2)(x, y))
```

If we did not provide a `norm` argument to the constructor
to be eventually passed to lazy execution, the first
default value would be inferred (in this case, `norm=2` 
based on the default of normalization). 

This default can change depending on what is being executed.
For example, the following code automatically infers `norm=1`
based on priority conflict resolution.

```python
print(Comparator(normalize, KLdivergence, epsilon=0)(x, y))
```

`pyfop` makes error checking trivial; we just needed to add
the normalization aspect to KLdivergence and check for the
shared value. For example, adding a `norm=2` argument to the
previous command will throw an error. There is no need for
conditional checks at other parts of the code.

As a final remark, lazy execution employs caching to prevent
leaks in large programs that reuse the same methods. This
keeps references to all method input arguments that prevent
the garbage collector from destroying objcets no longer in
memory. Leaks can be
avoided by generating cache scope contexts, in which lazy evaluations
are not recomputed for the same arguments, but which will allow the 
garbage collector to run upon exit. For example, the previous
call could run in a cache scope per:

```python
from pyfop import CacheScope

with CacheScope():
    print(Comparator(normalize, KLdivergence, epsilon=0)(x, y))
```


# :hammer_and_wrench: Functionalities
Making a method lazily execute can be achieved with the `@pyfop.lazy` decorator.
Aspect variables are assigned as `pfp.Aspect` variables. These can have a 
default value. Aspect values can change after lazy methods are first called.

```python
import pyfop as pfp

@pfp.lazy
def increase(x, inc=pfp.Aspect(1)):
    return x + inc

y = increase(2)
assert y.call() == 3
assert y.call(inc=2) == 4
```

For minimal intrusiveness, a `@pyfop.aytoaspects` is provided
can turn all default arguments into aspects. In the above snippet,
the method definition could change to the one bellow. 
Note that lazy decorators should remain the topmost ones.

```python
@pfp.lazy
@pfp.autoaspects
def increase(x, inc=1):
    return x + inc
```

Caching (also known as memoization) 
is automatically supported to prevent lazy calls from re-running
for the exact same inputs. It is based on object identifiers,
but it prevents the garbage collector from running on past
method inputs. To clear the garbage collector after operations,
these can run withing a cached scope, which is available in the form
of the context. This can be achieved per the following code:


```python
import pyfop as pfp

@pfp.eager
@pfp.autoaspects
def zeros(length=10):
    return [0] * length

with pfp.CacheScope():
    id1 = id(zeros(10))
    assert id1 == id(zeros(10))

assert id1 != id(zeros(10))
```

In the above example, the `@pyfop.eager` decorator defines
immediately runnable methods that support lazy execution arguments.
Calling methods decorated this way is equivalent 
to calling lazy executions without arguments. 
All aspects should obtain values at least once,
either via defaults or through normal pythonic argument parsing.

```python
import pyfop as pfp

@pfp.lazy
def add(x, permutation=pfp.Aspect()):
    return x + permutation

@pfp.eager
def mult(x, permutation=pfp.Aspect()):
    return x * permutation

assert mult(add(1, 3)) == 12
assert mult(add(1), 3) == 12
```

As a final remark on caching, you can also use the
decorator `@pyfop.lazy_no_cache` to prevent caching
for specific functions.

