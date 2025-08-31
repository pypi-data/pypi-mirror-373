from enum import Enum, EnumMeta


class NestedEnum(Enum):
    def __new__(cls, *args):
        obj = object.__new__(cls)
        value = None
        if len(args) == 1:
            value = args[0]

        if len(args) == 2:
            value = args[0]

        if value:
            obj._value_ = value

        return obj

    def __init__(self, items_or_value):
        if isinstance(items_or_value, EnumMeta):
            for enm in items_or_value:
                self.__setattr__(enm.name, enm)
