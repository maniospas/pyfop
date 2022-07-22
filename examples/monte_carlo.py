from pyfop import lazy, lazy_no_cache, autoaspects, Aspect, Priority
import numpy as np


@lazy_no_cache
class Uniform:
    @autoaspects
    def __init__(self, a=0, b=1, seed=None):
        self.a = a
        self.b = b
        self.rng = np.random.default_rng(seed)

    def random(self):
        return self.rng.random() * (self.b - self.a) + self.a


@lazy
@autoaspects
def integrate(f, distribution=Uniform(), samples=100000):
    return sum(f(distribution.random()) for _ in range(samples))/samples


pi = 4*integrate(lambda x: (1-x**2)**0.5)
print(pi(samples=5000000))

@lazy
def gamma(n, integrate=integrate, seed=Aspect(0, Priority.INCREASED), b=Aspect(100, Priority.HIGH)):
    gamma1 = integrate(lambda t: t*np.exp(-t))
    gamman = integrate(lambda t: t**(n-1)*np.exp(-t)) / gamma1
    return gamman


print(gamma(0.5)(samples=5000000, seed=1))
