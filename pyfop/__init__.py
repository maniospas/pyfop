from pyfop.aspect import Aspect, Priority
from pyfop.execution import lazy, eager
from pyfop.utils import memoization, autoaspects
import sys


class Lazifier(object):
    def __enter__(self):
        self.mapper = dict()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for method in self.mapper.values():
            setattr(sys.modules[method.__module__], method.__name__, method)

    def lazify(self, method):
        if method in self.mapper:
            raise Exception("Cannot lazified an already lazified method")
        ret = lazy(method)
        self.mapper[ret] = method
        setattr(sys.modules[method.__module__], method.__name__, ret)
        return ret


"""def lazify(method, members=True):
    if hasattr(method, "__dict__") and members:
        for attr, value in method.__dict__.items():
            if callable(value) and attr != "__new__" and attr != "__init__":
                setattr(method, attr, lazy(value))
    setattr(sys.modules[method.__module__], method.__name__, lazy(method))"""
