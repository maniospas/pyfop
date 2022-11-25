from enum import Enum


class Priority(Enum):
    IGNORE = -1
    LOW = 0
    NORMAL = 1
    INCREASED = 2
    HIGH = 3
    CRITICAL = 4


class Aspect:
    def __init__(self, default=None, priority=None, role=None):
        if isinstance(default, Aspect):
            if priority is None:
                priority = default.priority
            if role is None:
                role = self.context_role
            default = default.default
        self.name = None
        self.default = default
        if priority is None:
            priority = Priority.IGNORE if default is None else Priority.NORMAL
        self.priority = priority
        self.context_role = role

    def alias(self, name):
        self.name = name
        return self

    def extended_name(self):
        ret = self.name
        if self.context_role is not None:
            ret += "@" + self.context_role
        return ret

    def _call(self, context):
        ret = context.get(self.name)
        if ret.__class__.__name__ == 'PendingCall':
            ret = ret._call(context)
        return ret


def _name(arg, val):
    return val.extended_name() if isinstance(val, Aspect) else arg


def _value(arg, val):
    return val.default if isinstance(val, Aspect) else val


def _priority(val, default=Priority.HIGH):
    return val.priority if isinstance(val, Aspect) else default


class Context:
    def __init__(self):
        self.values = dict()
        self.priorities = dict()
        self.usages = dict()

    def to_aspects(self):
        ret = dict()
        for arg in self.values:
            aspect = Aspect(self.values[arg], self.priorities[arg])
            aspect.name = arg
            ret[arg] = aspect
        return ret

    def add(self, arg, val, default_priority=Priority.HIGH, is_default=False):
        arg = _name(arg, val)
        #if arg is None and isinstance(val, Aspect): # TODO: enable to remove some redundant execution.py code
        #    val.name = arg
        priority_diff = self.priorities.get(arg, Priority.LOW).value - _priority(val, default_priority).value
        if priority_diff <= 0:
            if priority_diff == 0 and arg in self.values and id(self.values[arg]) != id(_value(arg, val)):
                raise Exception("Conflicting values with the same priority ("
                                +str(self.priorities.get(arg, Priority.LOW))+") for argument: "+str(arg)+" (consider assigning different roles)")
            #print(arg, _value(arg, val), _priority(val, default_priority))
            if arg in self.usages and self.usages[arg] == 0 and not is_default:
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
                raise Exception("Unused argument: "+arg+" (no aspect with such name)")
        pass

    def __iter__(self):
        for item in self.values:
            yield item, self.values[item], self.priorities[item], self.usages[item]

    def __contains__(self, item):
        return item in self.values

    def __getitem__(self, item):
        return self.values[item]

    def __str__(self):
        ret = "context:"
        for item, value, priority, usage in self.__iter__():
            ret += f"\n\t- {item}:\n\t\t value: {value(**{arg: self.values[arg] for arg in value.get_input_context().values.keys()}) if value.__class__.__name__=='PendingCall' else value},\n\t\t priority: {priority}\n\t\t usage: {usage}"
        return ret
