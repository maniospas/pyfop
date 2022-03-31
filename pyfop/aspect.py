from enum import Enum


class Priority(Enum):
    IGNORE = -1
    LOW = 0
    NORMAL = 1
    INCREASED = 2
    HIGH = 3
    CRITICAL = 4


class Aspect:
    def __init__(self, default=None, priority=None):
        self.name = None
        self.default = default
        if priority is None:
            priority = Priority.IGNORE if default is None else Priority.NORMAL
        self.priority = priority

    def alias(self, name):
        self.name = name
        return self

    def _call(self, context):
        return context.get(self.name)


def _name(arg, val):
    return val.name if isinstance(val, Aspect) else arg


def _value(arg, val):
    return val.default if isinstance(val, Aspect) else val


def _priority(val, default=Priority.HIGH):
    return val.priority if isinstance(val, Aspect) else default


class Context:
    def __init__(self):
        self.values = dict()
        self.priorities = dict()
        self.usages = dict()

    def add(self, arg, val, default_priority=Priority.HIGH, is_default=False):
        arg = _name(arg, val)
        #if arg is None and isinstance(val, Aspect): # TODO: enable to remove some redundant execution.py code
        #    val.name = arg
        priority_diff = self.priorities.get(arg, Priority.LOW).value - _priority(val, default_priority).value
        if priority_diff <= 0:
            if priority_diff == 0 and arg in self.values and self.values[arg] != _value(arg, val):
                raise Exception("Conflicting values with the same priority ("
                                +str(self.priorities.get(arg, Priority.LOW))+") for argument: "+arg)
            #print(arg, _value(arg, val), _priority(val, default_priority))
            if arg in self.usages and self.usages[arg] == 0:
                raise Exception("Unused argument: "+arg)
            self.values[arg] = _value(arg, val)
            self.priorities[arg] = _priority(val, default_priority)
            self.usages[arg] = 1 if is_default else 0

    def extend(self, kwargs, default_priority=Priority.HIGH, is_default=False):
        for arg, val in kwargs.items():
            self.add(arg, val, default_priority, is_default)

    def get(self, arg):
        self.usages[arg] = self.usages.get(arg, 0) + 1
        return self.values.get(arg, None)

    def catch_unused(self):
        for arg, usage in self.usages.items():
            if usage == 0:
                raise Exception("Unused argument: "+arg)
        pass
