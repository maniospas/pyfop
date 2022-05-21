from pyfop.execution import PendingCall
from pyfop.aspect import Aspect, Priority
from inspect import signature, Parameter
from makefun import wraps, add_signature_parameters, remove_signature_parameters


def autoaspects(method):
    if isinstance(method, type):
        return type(method.__name__, (method,), {"__init__": autoaspects(method.__init__)})

    params = signature(method)
    new_params = list()
    for value in params.parameters.values():
        if hasattr(value.default, "__name__") and value.default.__name__ == '_empty':
            new_params.append(Parameter(value.name, value.kind, default=value.default))
        else:
            new_params.append(Parameter(value.name, value.kind,
                              default=Aspect(value.default, Priority.NORMAL)
                              if not isinstance(value.default, Aspect) and not isinstance(value.default, PendingCall)
                              else value.default))

    @wraps(method, new_sig=params.replace(parameters=new_params))
    def wrapper(*args, **kwargs):
        return method(*args, **kwargs)
    return wrapper
