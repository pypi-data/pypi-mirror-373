from typing import Callable,Self
import numpy as np
import inspect
from ..function import analysis_params, auto_cast
import functools


def as_np(f: type | Callable) -> Self:
    """将class中函数中参数类型为np.ndarray的参数自动转为numpy的形式,也可用于单个函数"""
    if type(f) == type:
        for key in f.__dict__:
            attr = getattr(f, key)
            if callable(attr):
                setattr(f, key, as_np(attr))
        return f

    return auto_cast(f, {'np.ndarray': np.asarray})





