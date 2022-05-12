import uuid
from functools import update_wrapper
from pyfop.argparser import parse_defaults
from pyfop.aspect import Aspect, Priority
from inspect import signature, Parameter
from makefun import wraps, add_signature_parameters, remove_signature_parameters


def obj2id(obj):
    if isinstance(obj, object):
        try:
            if not hasattr(obj, "_pyfop_uuid"):
                obj._pyfop_uuid = uuid.uuid1()
            return str(obj._pyfop_uuid)
        except AttributeError:
            pass
    return str(hash(obj))


def _idfier(*args, **kwargs):
    return "[" +",".join(obj2id(arg) for arg in args) + "]" + "{" + ",".join(v + ":" + obj2id(kwarg) for v, kwarg in kwargs.items()) + "}"


class MethodHasher:
    def __init__(self, method):
        self._method = method
        self._stored = dict()
        update_wrapper(self, method)

    def clear_hashed(self):
        self._stored = dict()

    def __call__(self, *args, **kwargs):
        desc = _idfier(*args, **kwargs)
        if desc in self._stored:
            return self._stored[desc]
        value = self._method(*args, **kwargs)
        self._stored[desc] = value
        return value


def memoization(method):
    return MethodHasher(method)


def autoaspects(method):
    params = signature(method)
    new_params = list()
    for value in params.parameters.values():
        if hasattr(value.default, "__name__") and value.default.__name__ == '_empty':
            new_params.append(Parameter(value.name, value.kind, default=value.default))
        else:
            new_params.append(Parameter(value.name, value.kind,
                              default=Aspect(value.default, Priority.NORMAL) if not isinstance(value.default, Aspect) else value.default))

    @wraps(method, new_sig=params.replace(parameters=new_params))
    def wrapper(*args, **kwargs):
        return method(*args, **kwargs)
    return wrapper
