import typing


class Pair:
    def __init__(self, v) -> None:
        self.name: str
        self.value = v
        self.type = type(v)
        self.parent: str

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Pair) and self.name == value.name and self.parent == value.parent


class _ClassMeta(type):

    def __new__(cls, name, bases, attrs: typing.Dict[str, typing.Any]):
        basenames = [b.__name__ for b in bases]

        if "AllNamedAttrClass" in basenames:
            for k, v in attrs.items():
                if k.startswith("__"):
                    continue
                if isinstance(v, Pair):
                    v = v.value
                v = Pair(v)
                v.name = k
                v.parent = name
                attrs[k] = v
        elif "NamedAttrClass" in basenames:
            for k, v in attrs.items():
                if k.startswith("__"):
                    continue
                if isinstance(v, Pair):
                    v.name = k
        elif name not in ["AllNamedAttrClass", "NamedAttrClass"]:
            raise Exception("别乱继承")
        return type.__new__(cls, name, bases, attrs)


class NamedAttrClass(metaclass=_ClassMeta): ...


class AllNamedAttrClass(metaclass=_ClassMeta): ...
