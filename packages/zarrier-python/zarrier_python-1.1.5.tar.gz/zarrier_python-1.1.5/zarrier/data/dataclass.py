from dataclasses import dataclass, asdict, astuple, fields, is_dataclass
from typing import Any, Dict, Tuple


class _Meta(type):
    def __new__(cls: Any, name: str, bases: Tuple[type], attrs: Dict[str, Any]):
        res = type.__new__(cls, name, bases, attrs)
        if name != "BaseDataClass":
            res = dataclass(res)
        return res


class BaseDataClass(metaclass=_Meta):
    """
    稍简化Python自带dataclasses用法
    """

    def asdict(self):
        return asdict(self)

    def astuple(self):
        return astuple(self)

    def fields(self):
        return fields(self)

    def is_dataclass(self):
        return is_dataclass(self)
