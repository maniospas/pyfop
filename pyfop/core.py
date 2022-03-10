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
        value = aspects.kwargs[self.name] if self.name in aspects.kwargs and aspects.kwargs[self.name] != self else self.value
        if self.name not in aspects.evaluated_aspects:
            aspects.evaluated_aspects[self.name] = value
        if value != aspects.evaluated_aspects[self.name]:
            raise Exception("Aspect "+self.name+" was initialized with different values")
        return value


class Aspects:
    def __init__(self, inherit=None, kwargs=None):
        self.kwargs = dict() if inherit is None else dict(inherit.kwargs)
        self.inherit = inherit
        self.evaluated_aspects = dict()
        if kwargs is not None:
            self.kwargs = self.kwargs | kwargs

    def put(self, arg, val):
        if isinstance(val, Aspect) and arg in self.kwargs:
            return
        self.kwargs[arg] = val
        if self.inherit is not None:
            self.inherit.put(arg, val)

    def full_kwargs(self, method, *args,  **kwargs):
        for arg, v in inspect.signature(method).parameters.items():
            val = v.default
            if hasattr(val, "__name__") and val.__name__ == '_empty':
                continue
            if isinstance(val, Aspect) and val.name is None:
                val.name = arg
            self.put(argname(arg, val), val)
        for arg, val in zip(list(inspect.signature(method).parameters)[:len(args)], args):
            self.put(argname(arg, val), val)
        for arg, val in kwargs.items():
            self.put(argname(arg, val), val)
        ret = {kwarg: self.kwargs[kwarg] if not isinstance(kwarg, Aspect) else self.kwargs[kwarg.name]
                for kwarg in inspect.signature(method).parameters
                if kwarg in self.kwargs}
        return ret


class PendingCall:
    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        self.call(*args, **kwargs)

    def call(self, aspects=None, **kwargs):
        aspects = Aspects(aspects)
        for kw, val in (dict(zip(list(inspect.signature(self.method).parameters)[:len(self.args)], self.args)) | self.kwargs).items():
            if kw in kwargs and val != kwargs[kw]:
                raise Exception("Argument "+kw+" was initialized with different values")
        original_kwargs = aspects.full_kwargs(self.method, *self.args, **(self.kwargs | kwargs))
        evaluated_kwargs = {argname(kw, arg): arg.call(aspects) if isfop(arg) else arg for kw, arg in original_kwargs.items()}
        for kw, val in original_kwargs.items():
            if isinstance(val, Aspect):
                evaluated_kwargs[kw] = val.call(aspects)
        print(original_kwargs, aspects.kwargs, evaluated_kwargs)
        #kwargs = aspects.full_kwargs(self.method, **kwargs)  # parse again to account for the outcome of children calls
        #kwargs = {argname(kw, arg): arg.call(aspects) if isinstance(arg, Aspect) else arg for kw, arg in kwargs.items()}
        return self.method(**evaluated_kwargs)


def forward(method):
    def wrapper(*args, **kwargs):
        return PendingCall(method, *args, **kwargs)
    wrapper.__name__ = method.__name__
    return wrapper
