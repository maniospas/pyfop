import inspect


def parse_defaults(method):
    return {arg: v.default for arg, v in inspect.signature(method).parameters.items()
            if not hasattr(v.default, "__name__") or v.default.__name__ != '_empty'}


def parse_positional(method, args):
    ret = dict()
    method_args = list(inspect.signature(method).parameters)
    method_args_pos = 0
    unnamed = list()
    for val in args:
        if method_args[method_args_pos] == "args":
            unnamed.append(val)
        else:
            ret[method_args[method_args_pos]] = val
            method_args_pos += 1
    return ret, unnamed
    #return {arg: val for arg, val in zip(list(inspect.signature(method).parameters)[:len(args)], args)}


def combine(*kwarg_list):
    ret = dict()
    for kwargs in kwarg_list:
        for arg, val in kwargs.items():
            ret[arg] = val
    return ret