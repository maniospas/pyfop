# pyfop
Implements 
[forward-oriented programming](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4180025)
in Python. This shares configuration arguments across multiple components
and determines their values *after* the main business logic.

![build](https://github.com/maniospas/pyfop/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/maniospas/pyfop/branch/main/graph/badge.svg?token=MCsMLyteqD)](https://codecov.io/gh/maniospas/pyfop)
[![Downloads](https://static.pepy.tech/personalized-badge/pyfop?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/pyfop)

**Dependencies:** None<br/>
**Developer:** Emmanouil (Manios) Krasanakis<br/>
**Contant:** maniospas@hotmail.com


## Features
:alembic: Adapt arguments to usage context<br>
:surfer: Argument sharing between methods<br>
:rocket: Speed up development<br>
:hammer_and_wrench: Easy adoption with decorators

## Quickstart
Enable lazy execution and automatically set arguments with defaults as aspects:
```python
@lazy
@autoaspects
def affine(x, scale=1, offset=0):
    return x*scale + offset
```
Produce results with normal python code:
```python
GM = (affine(2)*affine(8))**0.5
```
Declare aspect argument values to be shared with all method calls:
```python
print(GM(scale=3))  # 12
```

## Advanced features
Lazy methods calling lazy methods:
```python
@lazy
@autoaspects
def gm(x, y, affine=affine):
    return (affine(x)*affine(y))**0.5

GM = gm(2, 8)
print(GM(scale=3))  # 12
```

Show context, for example to understand which aspects can be controlled:
```python
print(GM.get_input_context(scale=3))
# context:
#	- scale:
#		 value: 3,
#		 priority: Priority.HIGH
#		 shares: 1
#	- offset:
#		 value: 1,
#		 priority: Priority.INCREASED
#		 shares: 4
```

Aspects are shared with all methods conttibuting to the result:
```python
@lazy
@autoaspects
def square(x, scale=1):
    return scale*x*x

print(affine(2)(scale=2))  # 4
print((affine(2)+square(1))(scale=2))  # 5
```

Manually declare priority-based aspects to resolve conflicting defaults:
```python
@lazy
def logpp(x, offset=Aspect(1, Priority.INCREASED)):
    import math
    return math.log(x+offset)/math.log(2)

result = affine(2)+log(3)
print(result(scale=2))  # 5+2=7
```
