from __future__ import annotations
from typing import Dict, Generic, TypeVar


class DictClass:

    def __getattr__(self, key):
        """只有未定义的属性才会到__getattr__"""
        return None

    def get(self, key, default=None):
        return getattr(self, key) or default

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, key):
        return bool(getattr(self, key))

    def update(self, dic: Dict):
        for k, v in dic.items():
            setattr(self, k, v)

    def items(self):
        for k, v in self.__class__.__dict__.items():
            if k.startswith("__"):
                continue
            yield k, v

        for k, v in self.__dict__.items():
            if k.startswith("__"):
                continue
            yield k, v


class ClassDict:

    def __init__(self, d: Dict):
        self._dict = d

    def get(self, *args):
        return self._dict.get(*args)

    def __getitem__(self, key):
        return self._dict.get(key, None)

    def __setitem__(self, *args):
        return self._dict.__setitem__(*args)

    def __getattr__(self, key):
        if key == "_dict":
            return super(ClassDict, self).__getattribute__("_dict")
        else:
            return self._dict.get(key, None)

    def __setattr__(self, key, value):
        if key == "_dict":
            super(ClassDict, self).__setattr__(key, value)
        else:
            self._dict["key"] = value

    def __contains__(self, key):
        return bool(getattr(self, key))


def merge_dict_recursively(d1: Dict, d2: Dict) -> Dict:
    """递归合并字典"""
    res = {}
    for k, v in d1.items():
        if k in d2:
            if isinstance(v, dict):
                res[k] = merge_dict_recursively(v, d2[k])
            else:
                res[k] = d2[k]
        else:
            res[k] = v
    for k, v in d2.items():
        if k not in d1:
            res[k] = v
    return res


KT = TypeVar("KT")
VT = TypeVar("VT")
T1 = TypeVar("T1")
T2 = TypeVar("T2")


class BiDict(dict[KT, VT]):
    """简易版双向字典"""

    _inverse_dict: Dict[VT, KT]

    @classmethod
    def from_dict(cls, d: Dict[T1, T2]) -> BiDict[T1, T2]:
        res = cls(**d)
        res._inverse_dict = {v: k for k, v in d.items()}
        return res

    def __setitem__(self, key, value):
        if (key in self) or (value in self._inverse_dict):
            raise KeyError(f"{key} or {value} already exists")
        super().__setitem__(key, value)
        self._inverse_dict[value] = key

    def __delitem__(self, key):
        value = self[key]
        super().__delitem__(key)
        del self._inverse_dict[value]

    def get_key(self, value, default=None):
        return self._inverse_dict.get(value, default)


class QueryField:
    ...


class QueryClass(Generic[T1]):
    """
    每个实例将是一个查询器
    例子:
        class Person:

            name: str = QueryField
            age: int = QueryField
            high: float = QueryField

            def __init__(self, name, age, high):
                self.name = name
                self.age = age
                self.high = high

        qc = QueryClass[Person]()
        qc.add(Person("z1", 20, 183))
        qc.add(Person("z2", 22, 163))
        p = qc.query('age', 20)
        qc.delete('age', 20)

    """

    def __init__(self):
        self.__inited = False
        self.dicts = {}

    def init(self):
        if self.__inited:
            return
        if not hasattr(self, "__orig_class__") or len(self.__orig_class__.__args__) != 1:
            raise TypeError("请使用[]指定QueryClass数据类型, 例如 QueryClass[YourClass]()")

        self.type = self.__orig_class__.__args__[0]

        for k, v in self.type.__dict__.items():
            if v == QueryField:
                self.dicts[k] = {}

        self.__inited = True

    def add(self, obj: T1):
        self.init()
        for k, d in self.dicts.items():
            d[getattr(obj, k)] = obj

    def delete(self, obj: T1):
        self.init()
        for k, d in self.dicts.items():
            del d[getattr(obj, k)]

    def delete_by_key(self, key, value):
        self.delete(self.dicts[key][value])

    def query(self, key, value) -> T1:
        self.init()
        return self.dicts[key][value]

    