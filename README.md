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
aims to simplify component-based development by
sharing parameters across multiple components.

Contrary to typical programming paradigms,
static annotations are used to mark variables
as aspects spanning multiple components whose 
values are automatically retrieved, initialized 
and exchanged.

# :fire: Features
* Simplified code that considers only main data flows.
* Value sharing between arguments.
* Non-intrusive API (minimal changes to code).
* Priority-based conflict resolution.
* Scoped method modification.

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
array transformation methods `tautology` and `normalize`, 
as well as two pairwise array comparison methods
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
previous command will throw an error.

