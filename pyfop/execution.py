from pyfop.aspect import Aspect, Context, Priority
import pyfop.argparser as argparser
from functools import wraps


def _isfop(val):
    return isinstance(val, Aspect) or isinstance(val, PendingCall)


class PendingCall:
    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs
        #if hasattr(method, "__dict__"):
        #    for attribute, value in method.__dict__.items():
        #        if callable(value) and attribute != "__init__" and attribute != "__new__":
        #            self.__dict__[attribute] = lazy(value)
        #        else:
        #            self.__dict__[attribute] = value

    def __add__(self, other):
        return add(self, other)

    def __sub__(self, other):
        return sub(self, other)

    def __abs__(self):
        return _abs(self)

    def __div__(self, other):
        return div(self, other)

    def __rdiv__(self, other):
        return div(self, other)

    def __pow__(self, other):
        return pow(self, other)

    def __call__(self, **kwargs):
        return self.call(**kwargs)

    def call(self, **kwargs):
        context = Context()
        context.extend(kwargs, Priority.HIGH)
        self._gather_aspects(context)
        ret = self._call(context)
        if isinstance(ret, PendingCall):
            ret._gather_aspects(context)
            ret = ret._call(context)
        context.catch_unused()
        return ret

    def _gather_aspects(self, context):
        defaults = argparser.parse_defaults(self.method)
        positional, unnamed = argparser.parse_positional(self.method, self.args)
        kwargs = argparser.combine(defaults, positional, self.kwargs)
        for arg, val in defaults.items():
            if isinstance(val, Aspect):
                val.name = arg
                context.add(arg, kwargs[arg], is_default=True)
                kwargs[arg] = val
        for arg, val in kwargs.items():
            if isinstance(val, Aspect):
                val.name = arg
                context.add(arg, kwargs[arg], is_default=True)
                kwargs[arg] = val
        for val in kwargs.values():
            if isinstance(val, PendingCall):
                val._gather_aspects(context)

    def _call(self, context):
        positional, unnamed = argparser.parse_positional(self.method, self.args)
        kwargs = argparser.combine(argparser.parse_defaults(self.method),
                                   positional,
                                   self.kwargs)
        for arg, val in kwargs.items():
            if isinstance(arg, Aspect):
                val.name = arg
        # print(self.method.__name__, kwargs)
        unnamed = [val._call(context) if _isfop(val) else val for val in unnamed]
        kwargs = {arg: val._call(context) if _isfop(val) else val for arg, val in kwargs.items()}
        return self.method(*unnamed, **kwargs)


def lazy(method):
    def wrapper(*args, **kwargs):
        wraps(method)
        return PendingCall(method, *args, **kwargs)
    return wrapper


def eager(method):
    def wrapper(*args, **kwargs):
        wraps(method)
        return PendingCall(method, *args, **kwargs).call()
    return wrapper


@lazy
def add(x, y):
    return x + y


@lazy
def div(x, y):
    return x / y


@lazy
def pow(x, y):
    return x ** y


@lazy
def sub(x, y):
    return x - y


@lazy
def _abs(x):
    return abs(x)
