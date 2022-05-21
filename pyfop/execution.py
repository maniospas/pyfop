from pyfop.aspect import Aspect, Context, Priority
import pyfop.argparser as argparser
from functools import wraps
from pyfop.cache import cache


def _isfop(val):
    return isinstance(val, Aspect) or isinstance(val, PendingCall)


class PendingCall:
    def __init__(self, _pyfop_method, *args, **kwargs):
        self.method = _pyfop_method
        self.args = args
        self.kwargs = kwargs

    def __getattribute__(self, name):
        if name in ["method", "args", "kwargs"] or name in dir(PendingCall):
            return object.__getattribute__(self, name)

        def future_method(*args, fop_method_result, **kwargs):
            return getattr(fop_method_result, name)(*args, **kwargs)

        return lazy(future_method, fop_method_result=self)

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


def lazy(method, *supplementary_args, **supplementary_kwargs):
    method = cache(method)
    @wraps(method)
    def wrapper(*args, **kwargs):
        return PendingCall(method, *(supplementary_args+args), **(supplementary_kwargs | kwargs))
    return wrapper


def eager(method):
    method = cache(method)
    @wraps(method)
    def wrapper(*args, **kwargs):
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
