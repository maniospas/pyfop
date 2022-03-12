from pyfop.aspect import Aspect, Context, Priority
import pyfop.argparser as argparser


def _isfop(val):
    return isinstance(val, Aspect) or isinstance(val, PendingCall)


class PendingCall:
    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __call__(self, aspects=None, **kwargs):
        return self.call(aspects, **kwargs)

    def call(self, **kwargs):
        context = Context()
        context.extend(kwargs, Priority.HIGH)
        self._gather_aspects(context)
        ret = self._call(context)
        context.catch_unused()
        return ret

    def _gather_aspects(self, context):
        defaults = argparser.parse_defaults(self.method)
        kwargs = argparser.combine(defaults,
                                   argparser.parse_positional(self.method, self.args),
                                   self.kwargs)
        for arg, val in defaults.items():
            if isinstance(val, Aspect):
                val.name = arg
                context.add(arg, kwargs[arg], is_default=True)
                kwargs[arg] = val
        for val in kwargs.values():
            if isinstance(val, PendingCall):
                val._gather_aspects(context)

    def _call(self, context):
        kwargs = argparser.combine(argparser.parse_defaults(self.method),
                                   argparser.parse_positional(self.method, self.args),
                                   self.kwargs)
        for arg, val in kwargs.items():
            if isinstance(arg, Aspect):
                val.name = arg
        # print(self.method.__name__, kwargs)
        kwargs = {arg: val._call(context) if _isfop(val) else val for arg, val in kwargs.items()}
        return self.method(**kwargs)


def lazy(method):
    def wrapper(*args, **kwargs):
        return PendingCall(method, *args, **kwargs)
    wrapper.__name__ = method.__name__
    return wrapper


def eager(method):
    def wrapper(*args, **kwargs):
        return PendingCall(method, *args, **kwargs).call()
    wrapper.__name__ = method.__name__
    return wrapper
