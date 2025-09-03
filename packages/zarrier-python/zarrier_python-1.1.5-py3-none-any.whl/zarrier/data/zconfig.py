from __future__ import annotations
from typing import Dict, List, Self, TypeVar

class _ZConfigMeta(type):
    
    def __new__(cls, name, bases, attrs) -> int:
        if name == 'ZConfig' and len(bases) == 0:
            return super().__new__(cls, name,bases,attrs)
        attrs['a123'] = 123
        return super().__new__(cls, name,bases,attrs) or bases[0]


class ZConfig(metaclass=_ZConfigMeta):
    """
    可继承式配置, 没错, 我被机器学习的多得批爆的参数烦死了
    """

    def __getattr__(self, key):
        """只有未定义的属性才会到__getattr__"""
        return None

    def get(self, key, default=None):
        return getattr(self, key) or default

    def copy(self):
        return self.__class__

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self,key,value):
        return setattr(self,key,value)

    def __contains__(self, key):
        return bool(getattr(self, key))

    def update(self, dic:Dict):
        for k,v in dic.items():
            setattr(self, k, v)

    def items(self):
        for k,v in self.__class__.__dict__.items():
            if k.startswith('__'):
                continue
            yield k,v

        for k,v in self.__dict__.items():
            if k.startswith('__'):
                continue
            yield k,v