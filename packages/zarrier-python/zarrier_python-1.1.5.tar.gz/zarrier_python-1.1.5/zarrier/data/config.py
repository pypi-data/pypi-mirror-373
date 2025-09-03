from typing import Dict


class ConfigStruct:

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
