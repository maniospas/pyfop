import inspect


def signature(obj):
    if hasattr(obj, "_method"):
        obj = obj._method
    return inspect.signature(obj)


def parse_defaults(method):
    return {arg: v.default for arg, v in signature(method).parameters.items()
            if not hasattr(v.default, "__name__") or v.default.__name__ != '_empty'}


def parse_positional(method, args):
    ret = dict()
    method_args = list(signature(method).parameters)
    method_args_pos = 0
    unnamed = list()
    for val in args:
        if method_args[method_args_pos] == "args":
            unnamed.append(val)
        else:
            ret[method_args[method_args_pos]] = val
            method_args_pos += 1
    return ret, unnamed
    #return {arg: val for arg, val in zip(list(signature(method).parameters)[:len(args)], args)}


def combine(*kwarg_list):
    ret = dict()
    for kwargs in kwarg_list:
        for arg, val in kwargs.items():
            ret[arg] = val
    return ret