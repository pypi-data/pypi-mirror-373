from __future__ import annotations
from typing import Callable, Iterable, List, TYPE_CHECKING, Dict
from multiprocessing import Pool
from tqdm import tqdm
import time
import functools
import inspect
import copy
import threading
import traceback
import logging

logger = logging.getLogger(__name__)


def f(func: Callable, *args, **kw):
    @functools.wraps(func)
    def wrap(*a, **w):
        return func(*args, *a, **kw, **w)

    return wrap


def recursive_update(src: Dict, tar: Dict):
    """字典递归赋值,将src赋值给tar"""

    for k, v in src.items():
        if k in tar and isinstance(tar[k], dict) and isinstance(src[k], dict):
            recursive_update(v, tar[k])
        else:
            tar[k] = v


def wait_for(func: Callable, value=True, delta=0.1):
    """反复运行, 直到func返回值为value"""
    while not (func() == value):
        time.sleep(delta)


def _catch_func(arg):
    func, dumps, *ds = arg
    try:
        if dumps:
            return func(*ds)
        else:
            return func(ds)
    except Exception as e:
        logger.error(e.args)
        logger.error(traceback.format_exc())


def run_in_multiprocess(func: Callable, datas: Iterable, multi=10, total=None, need_process_bar=True, dumps=True, test=False):
    """
    func作用于datas的每个元素的返回值存入列表返回,保序。
    保序,保序,保序

    func中尽量不要使用datas以外的变量。

    注 多进程，榨干CPU。
    """
    _datas = [(func, dumps, *data) for data in datas]
    if total is None:
        total = len(_datas)

    if test:
        return [_catch_func(_data) for _data in tqdm(_datas, total=total)]
    else:
        p = Pool(multi)
        iter = p.imap(_catch_func, _datas)
        if need_process_bar:
            return list(tqdm(iter, total=total))
        else:
            return list(tqdm(iter))


def analysis_params(f: Callable):
    params = inspect.signature(f).parameters
    keys = list(params.keys())
    return [params[k] for k in keys]


_type_cast = {int: int, str: str, float: float, bool: bool}


def auto_cast(func: Callable, type_cast={}):
    """
    传入的函数参数自动进行类型转换或任意转换
    type_cast : {k,v}  k为类型注解, v为函数
    当参数注解类型类型为k时, 自动调用v作用于该参数
    """
    new_type_cast = {}
    for k, v in _type_cast.items():
        new_type_cast[k.__name__] = v
    for k, v in type_cast.items():
        new_type_cast[str(k)] = v

    params = inspect.signature(func).parameters

    # @functools.wraps(func)
    def wrap(*args, **kws):
        new_args = []
        new_kws = {}
        _params = list(params.values()) + [None] * len(args)
        for param, arg in zip(_params, args):
            if param is not None:
                ann = param.annotation
                if isinstance(ann, type):
                    ann = ann.__name__
                if ann in new_type_cast:
                    arg = new_type_cast[ann](arg)
            new_args.append(arg)

        for k, v in kws.items():
            new_kws[k] = v
            if k not in params:
                continue
            if params[k].annotation in new_type_cast:
                v = new_type_cast[params[k].annotation](v)
                new_kws[k] = v
        return func(*new_args, **new_kws)

    return wrap


class ZTodo:
    """
    自动执行队列
    """

    todos: List[ZTodo] = []
    loop_thread: threading.Thread = None

    @classmethod
    def loop(cls):
        def _loop():
            while True:
                time.sleep(0.03)
                if len(cls.todos) == 0:
                    continue
                todo = cls.todos.pop(0)
                todo.do()

        cls.loop_thread = threading.Thread(target=_loop)
        cls.loop_thread.start()

    def __init__(self, todo_name, f, *args, **kws) -> None:
        self.name = todo_name
        self.f = f
        self.args = args
        self.kws = kws
        self.todos.append(self)

    def do(self):
        try:
            time0 = time.time()
            self.f(*self.args, **self.kws)
            logger.info(f"完成计划任务{self.name}, 用时:{time.time()-time0}秒, 剩余任务数{len(self.todos)}")
        except Exception:
            logger.error(traceback.format_exc())


def cached_property(p: property):
    """
    用于仅计算一次的计算属性，自动缓存.

    class A:

        @cached_property
        @property
        def b(self):
            print(123)
            return 1

    a = A()
    print(a.b)
    print(a.b)
    a = A()
    print(a.b)

    打印结果:
    123
    1
    1
    123
    1

    """

    @functools.wraps(p.fget)
    def attr(self):
        key = f"_cached_{p.fget.__name__}"
        if not hasattr(self, key):
            setattr(self, key, p.fget(self))
        return getattr(self, key)

    return p.getter(attr)


if TYPE_CHECKING:

    def cached_property(p: property):
        return p.fget()
