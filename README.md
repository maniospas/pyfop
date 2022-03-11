# pyfop
A novel forward-oriented programming paradigm for Python.

**Dependencies:** None<br/>
**Developer:** Emmanouil (Manios) Krasanakis<br/>
**Contant:** maniospas@hotmail.com

## About
`pyfop` is a package that introduces the concept
of forward-oriented programming in Python. This
aims to simplify component-based development that
aims to share parameters across multiple components.

Contrary to typical programming paradigms, it makes
use of static variable annotations that can mark
them as aspects spanning multiple components and
whose values and whose values are automatically
retrieved, initialized and exchanged. Aspect
values persist through calls of methods annotated
with the package's wrapper *and* persist when
called methods return.

This way, only the components interested in respective
aspect variables handle their usage. This is achieved
with lazy execution.

# Problem Statement
To understand forward execution, let us create a 
simple setting in which we want to compare two
`numpy` vectors `x,y` under various measures,
let's say with the dot product and KL-divergence.
This can be easily achieved through the following
implementations: 

```python
import numpy as np

def dot(x, y):
    return np.sum(x*y)

def KLdivergence(x, y):
    return np.sum(x*np.log(x/y))
```

To spice things up, we also introduce the ability to 
perform normalization and bring everything together in 
one system that compare the vectors:

```python
def _normalizer(x, normalization):
    if normalization == "L1":
        return x / np.sum(x)
    if normalization == "L2":
        return x / np.sqrt(np.sum(x*x))
    if normalization is None:
        return x
    raise Exception("Invalid normalization type")

def compare(x, y, measure, normalization):
    normalized_x = _normalizer(x, normalization)
    normalized_y = _normalizer(y, normalization)
    return measure(normalized_x, normalized_y)
```

Easy, right? Surely, anybody can write expressions
like `compare(x, y, dot, normalization="L2")`, which
effectively computes the cosine similarity between
vectors.

If only the real world was that simple! The above
implementation is fine to use by oureselves but is
a nightmare to deploy into component-based systems.

First of all, you may have already noticed that I
do not include default parameter values. This is 
on purpose, since these could depend on the type
of measure used. For the dot product, L2 normalization
usually makes sense to compute the reputable cosine
similarity. However, for KL-diverence, which considers
similarities between probability distributions, 
it makes sense to have a L1 default value to make
both vector elements sum to one (and hence model
said distributions).

And this is only the beginning of our problems!

Let's say that we also want error checking in there,
for example to make sure that KL-divergence is
never computed with L2 normalization of base vectors.
There are several ways to achieve this. 

- Writing 
additional checks within the method `similarity` so
that errors are raised when some conditions are met.
This is ugly, does not scale well to complex systems
(imagine what happens if several components interact
with each other and we need to catch specific edge cases),
and non-comprehensible, since it separates error
checking from the code it refers to. A similar mechanism
can handle default value assignment. 

- Passing a normalization argument to *all* measure
method signatures. This includes useless arguments that
are completely ignored by some measures (e.g. by the 
dot product). This drastically increases code complexity
and reduces comprehensibility of produced code by
passing useless information back-and-forth. What's
worse, it can not even address the challenge of presenting
different default arguments tailored to the measures 
of choice.

- Create an object to hold potential parameters. This
does not help a lot - we just added complexity by offloading
the cost of writing complex method signature.

- Turn all measures into their own classes and implement
error checking and default setting methods. This is the 
most realistic option in terms of providing high-quality
code. However, not to mention that it is not very Python-ic,
it multiplies written lines of code by replacing each
method with 4 others (constructors, error checking, default
values, and the original implementations).

Ok, we found that some promising software engineering 
practices do not help a lot in writing simple 
comprehensible code. What's next?

# Quickstart
Let's see how `pyfop` addresses the above challenges. 
In fact, doing so is as easy as adding only a couple
of statements here and there. These are limited to
the `@pyfop.forward` method decorator,
`pyfop.Aspect` variable initialization available
for decorated methods and the `call()` method 
used to run decorated methods.

First, our decorators are easy to conceptualize:
they create wrappers for code methods
that wait until the `call()` method to run
(this method can also take more arguments
Decorated methods can be passed as arguments



```python
import pyfop as pfp
import numpy as np

def dot(x, y):
    return np.sum(x*y)

@pfp.forward
def KLdivergence(x, y, normalization=pfp.Aspect("L1")):
    if normalization == "L2":
        raise Exception("KLDivergence should not work on L1 normalization")
    return np.sum(x*np.log(x/y))

@pfp.forward
def normalizer(x, normalization=pfp.Aspect()):
    if normalization == "L1":
        return x / np.sum(x)
    if normalization == "L2":
        return x / np.sqrt(np.sum(x*x))
    if normalization is None:
        return x
    raise Exception("Invalid normalization type")

def similarity(x, y, measure, normalization=pfp.Aspect()):
    return measure(normalizer(x, normalization), normalizer(y, normalization)).call()


```