from pyfop.aspect import Aspect, Context, Priority
import pyfop.argparser as argparser
from functools import wraps
from pyfop.cache import cache


def _isfop(val):
    return isinstance(val, Aspect) or isinstance(val, PendingCall) or isinstance(val, Generator)


class Generator:
    def __init__(self, var):
        assert isinstance(var, PendingCall)
        self.method = var

    def _call(self, context):
        positional, unnamed = argparser.parse_positional(self.method.method, self.method.args)
        kwargs = argparser.combine(argparser.parse_defaults(self.method.method),
                                   positional,
                                   self.method.kwargs)
        for arg, val in kwargs.items():
            if isinstance(arg, Aspect):
                val.name = arg
        # print(self.method.__name__, kwargs)
        unnamed = [val._call(context) if _isfop(val) else val for val in unnamed]
        kwargs = {arg: val._call(context) if _isfop(val) else val for arg, val in kwargs.items()}
        return PendingCall(self.method.method, *unnamed, **kwargs, supercontext=context)

    def call(self, **kwargs):
        raise Exception("pyfop.Generator instances can only be passed to @lazy methods")

    def _gather_aspects(self, context):
        self.method._gather_aspects(context)


class PendingCall:
    def __init__(self, _pyfop_method, *args, supercontext=None, **kwargs):
        self.method = _pyfop_method
        self.args = args
        self.kwargs = kwargs
        self.inject_aspects_to_context = dict()
        self.supercontext = supercontext  # this is only to be set by the Generator class

    def __getattribute__(self, name):
        if name in ["method", "args", "kwargs", "supercontext", "inject_aspects_to_context"] or name in dir(PendingCall):
            return object.__getattribute__(self, name)

        def future_method(*args, fop_method_result, **kwargs):
            attr = getattr(fop_method_result, name)
            if callable(attr):
                return attr(*args, **kwargs)
            else:
                if args or kwargs:
                    raise Exception("Do not provide arguments when casting attributes.")
                return attr

        return lazy(future_method, fop_method_result=self)

    def __getitem__(self, item):
        return getitem(self, item)

    def __setitem__(self, key, value):
        return setitem(self, key, value)

    def __add__(self, other):
        return add(self, other)

    def __radd__(self, other):
        return add(other, self)

    def __mul__(self, other):
        return mul(self, other)

    def __rmul__(self, other):
        return mul(other, self)

    def __sub__(self, other):
        return sub(self, other)

    def __rsub__(self, other):
        return sub(other, self)

    def __abs__(self):
        return _abs(self)

    def __truediv__(self, other):
        return div(self, other)

    def __rdiv__(self, other):
        return div(self, other)

    def __pow__(self, other):
        return pow(self, other)

    def __eq__(self, other):
        return equals(self, other)

    def __gt__(self, other):
        return gt(self, other)

    def __lt__(self, other):
        return lt(self, other)

    def __ge__(self, other):
        return gt(self, other)

    def __le__(self, other):
        return lt(self, other)

    def __neg__(self):
        return neg(self)

    def __bool__(self):
        raise Exception("Python does not support boolean operation overriding to replace them with FOP")

    def __call__(self, **kwargs):
        return self.call(**kwargs)

    def role(self, context_role):
        return Aspect(self, role=context_role)

    def get_input_context(self, **kwargs):
        context = Context()
        context.extend(kwargs, Priority.HIGH)
        self._gather_aspects(context)
        return context

    def call(self, **kwargs):
        context = Context()
        context.extend(kwargs, Priority.HIGH)
        self._gather_aspects(context)
        ret = self._call(context)
        if isinstance(ret, PendingCall):
            ret._gather_aspects(context)
            ret = ret._call(context)
        if self.supercontext is None:  # TODO: this is a hack, find an actual fix
            context.catch_unused()
        return ret

    def aspects(self, **kwargs):
        if not kwargs:
            return self
        ret = PendingCall(self.method, *self.args, self.supercontext, **self.kwargs)
        for key, value in kwargs.items():
            ret.inject_aspects_to_context[key] = Aspect(value, priority=Priority.HIGH)
        for key, value in kwargs.items():
            if isinstance(value, PendingCall) and key not in self.kwargs:
                ret.inject_aspects_to_context = ret.inject_aspects_to_context | value.get_input_context().to_aspects()
        ret.supercontext = True
        return ret

    def _gather_aspects(self, context):
        defaults = argparser.parse_defaults(self.method)
        positional, unnamed = argparser.parse_positional(self.method, self.args)
        kwargs = argparser.combine(defaults, positional, self.kwargs)
        for arg, val in defaults.items():
            if isinstance(val, Aspect):
                val.name = arg
                if isinstance(kwargs[arg], Aspect):
                    kwargs[arg].name = arg
                context.add(val.extended_name(), kwargs[arg], is_default=True)
                kwargs[arg] = val
        for arg, val in kwargs.items():
            if isinstance(val, Aspect):
                val.name = arg
                if isinstance(kwargs[arg], Aspect):
                    kwargs[arg].name = arg
                context.add(val.extended_name(), kwargs[arg], is_default=True)
                kwargs[arg] = val
        for arg, val in self.inject_aspects_to_context.items():
            if isinstance(val, Aspect):
                val.name = arg
                context.add(val.extended_name(), val, is_default=False)
        for val in kwargs.values():
            if isinstance(val, PendingCall) or isinstance(val, Generator):
                val._gather_aspects(context)
        for val in self.inject_aspects_to_context.values():
            if isinstance(val, PendingCall) or isinstance(val, Generator):
                val._gather_aspects(context)

    def _call(self, context):
        positional, unnamed = argparser.parse_positional(self.method, self.args)
        kwargs = argparser.combine(argparser.parse_defaults(self.method),
                                   positional,
                                   self.kwargs)
        for arg, val in kwargs.items():
            if isinstance(val, Aspect):
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


def lazy_no_cache(method, *supplementary_args, **supplementary_kwargs):
    @wraps(method)
    def wrapper(*args, **kwargs):
        return PendingCall(method, *(supplementary_args+args), **(supplementary_kwargs | kwargs))
    return wrapper


def eager_no_cache(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        return PendingCall(method, *args, **kwargs).call()
    return wrapper


def eager(method):
    method = cache(method)

    @wraps(method)
    def wrapper(*args, **kwargs):
        return PendingCall(method, *args, **kwargs).call()
    return wrapper

"""
def _lazy_attribute_calls_to_attributes(x, y):
    if isinstance(x, PendingCall):
        x = x()
    if isinstance(y, PendingCall):
        y = y()
    return x, y
"""


@lazy
def neg(x):
    return -x


@lazy
def getitem(x, i):
    return x[i]


@lazy
def setitem(x, i, v):
    x[i] = v


@lazy
def add(x, y):
    return x + y


@lazy
def mul(x, y):
    return x * y


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
def equals(x, y):
    return x == y


@lazy
def gt(x, y):
    return x > y


@lazy
def lt(x, y):
    return x < y



@lazy
def ge(x, y):
    return x >= y


@lazy
def le(x, y):
    return x <= y


@lazy
def _abs(x):
    return abs(x)
