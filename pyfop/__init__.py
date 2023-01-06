from pyfop.aspect import Aspect, Priority
from pyfop.execution import lazy, eager, lazy_no_cache, eager_no_cache, meta, Generator
from pyfop.utils import autoaspects, builder
from pyfop.cache import CacheScope
import sys


class Lazifier(object):
    def __enter__(self):
        self.mapper = dict()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for method in self.mapper.values():
            setattr(sys.modules[method.__module__], method.__name__, method)

    def __call__(self, *args, auto=True):
        for method in args:
            return self.lazify(method, auto)

    def lazify(self, method, auto=True, tobuilder=False):
        if method in self.mapper:
            raise Exception("Cannot lazify an already lazified method")
        ret = method
        if auto:
            ret = autoaspects(ret)
        ret = builder(ret) if tobuilder else lazy(ret)
        self.mapper[ret] = method
        setattr(sys.modules[method.__module__], method.__name__, ret)
        return ret


"""def lazify(method, members=True):
    if hasattr(method, "__dict__") and members:
        for attr, value in method.__dict__.items():
            if callable(value) and attr != "__new__" and attr != "__init__":
                setattr(method, attr, lazy(value))
    setattr(sys.modules[method.__module__], method.__name__, lazy(method))"""
