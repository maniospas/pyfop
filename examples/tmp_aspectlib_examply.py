import aspectlib


def amean(x, y):
    return (x + y)/2


def gmean(x, y):
    return (x * y)**0.5


@aspectlib.Aspect
def test(x, y):
    m = max(abs(x), abs(y))
    x /= x
    y /= y
    yield aspectlib.Return((yield aspectlib.Proceed(x, y)) * m)


for method in list(globals().values()):
    if hasattr(method, "__name__") and method.__name__.endswith("mean"):
        aspectlib.weave(method, test)

print(amean(1.E308, 1.E308))
print(gmean(1.E200, 2.E200))
