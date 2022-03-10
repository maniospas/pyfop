import inspect


def isfop(arg):
    return isinstance(arg, Aspect) or isinstance(arg, PendingCall)


def argname(arg, val):
    if isinstance(val, Aspect):
        return val.name
    return arg


def isequal(val1, val2):
    if isfop(val1) or isfop(val2):
        return True
    return val1 == val2


class Aspect:
    def __init__(self, value=None):
        self.name = None  # TODO: enable named aspects
        self.value = value

    def call(self, aspects):
        if self.name in aspects.kwargs and aspects.kwargs[self.name] != self:
            return aspects.kwargs[self.name]
        return self.value


class Aspects:
    def __init__(self, inherit=None, kwargs=None):
        self.kwargs = dict() if inherit is None else dict(inherit.kwargs)
        self.inherit = inherit
        if kwargs is not None:
            self.kwargs = self.kwargs | kwargs

    def put(self, arg, val, _pyfop_update_aspects=True):
        if isinstance(val, Aspect):
            if not _pyfop_update_aspects:
                return
            print('Default value for',val.name,'is',val.call(self))
            val = val.call(self)
        self.kwargs[arg] = val
        if self.inherit is not None:
            self.inherit.put(arg, val)

    def __call__(self, method, *args, _pyfop_update_aspects=True, **kwargs):
        for arg, v in inspect.signature(method).parameters.items():
            val = v.default
            if hasattr(val, "__name__") and val.__name__ == '_empty':
                continue
            if isinstance(val, Aspect) and val.name is None:
                val.name = arg
            self.put(argname(arg, val), val, _pyfop_update_aspects)
        for arg, val in zip(list(inspect.signature(method).parameters)[:len(args)], args):
            self.put(argname(arg, val), val, _pyfop_update_aspects)
        for arg, val in kwargs.items():
            self.put(argname(arg, val), val, _pyfop_update_aspects)
        ret = {kwarg: self.kwargs[kwarg] if not isinstance(kwarg, Aspect) else self.kwargs[kwarg.name]
                for kwarg in inspect.signature(method).parameters
                if kwarg in self.kwargs}
        #print(ret)
        return ret


class PendingCall:
    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        self.call(*args, **kwargs)

    def call(self, aspects=None, **kwargs):
        if aspects is None:
            aspects = Aspects(kwargs=kwargs)
        kwargs = aspects(self.method, *self.args, **self.kwargs)
        kwargs = {argname(kw, arg): arg.call(Aspects(aspects)) if isfop(arg) else arg for kw, arg in kwargs.items()}
        kwargs = aspects(self.method, **kwargs, _pyfop_update_aspects=False)  # parse again to account for the outcome of children calls
        kwargs = {argname(kw, arg): arg.call(aspects) if isinstance(arg, Aspect) else arg for kw, arg in kwargs.items()}
        return self.method(**kwargs)


def forward(method):
    def wrapper(*args, **kwargs):
        return PendingCall(method, *args, **kwargs)
    wrapper.__name__ = method.__name__
    return wrapper
