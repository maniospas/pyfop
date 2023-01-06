from functools import update_wrapper

_all_objects = list()  # keeping objects in memory prevents ids from being reused
_hashers = list()


class CacheScope(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        cleanup()


def cleanup():
    for hasher in _hashers:
        hasher.clear_hashed()
    _all_objects.clear()


def obj2id(obj):
    _all_objects.append(obj)
    return str(id(obj))


def _idfier(*args, **kwargs):
    return "[" +",".join(obj2id(arg) for arg in args) + "]" + "{" + ",".join(v + ":" + obj2id(kwarg) for v, kwarg in kwargs.items()) + "}"


class MethodHasher:
    def __init__(self, method):
        self._method = method
        self._stored = dict()
        _hashers.append(self)
        # update_wrapper(self, method)  # TODO: this throws an exception

    def clear_hashed(self):
        self._stored = dict()

    def __call__(self, *args, **kwargs):
        desc = _idfier(*args, **kwargs)
        if desc in self._stored:
            return self._stored[desc]
        value = self._method(*args, **kwargs)
        self._stored[desc] = value
        return value


def cache(method):
    return MethodHasher(method)
