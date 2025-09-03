from __future__ import annotations
import os
import inspect


def zdir(path, upper=1):
    """返回路径的n集父文件夹"""
    res = path
    for i in range(upper):
        res = os.path.dirname(res)
    return res


def rjoin(*args, is_dir=False, makedirs=False):
    """从工作目录开始拼接路径"""
    return zjoin(os.getcwd(), *args, is_dir=is_dir, makedirs=makedirs)


def zjoin(origin_path: str, upper: int | str, *args, is_dir=False, makedirs=False, need_norm=True):
    """
    zjoin('/b/c/d', 1, 'e', 'f') = '/b/c/e/f'
    zjoin('/b/c/d', 0, 'e', 'f') = '/b/c/d/e/f'
    zjoin('/b/c/d', 'e', 'f') = '/b/c/d/e/f'
    """
    if isinstance(upper, str):
        res = origin_path
        res = os.path.join(res, upper, *args)
    else:
        res = zdir(origin_path, upper)
        res = os.path.join(res, *args)
    if makedirs:
        os.makedirs(zdir(res, 1 - is_dir), exist_ok=True)
    if need_norm:
        res = os.path.normpath(res)
    return res


def xjoin(origin_path: int | str, upper: int | str = None, *args, is_dir=False, makedirs=False):
    """
    注意，编译后使用会出错

    仅传入1个参数时，从调用该函数的文件的文件夹拼接
        if __file__ = '/a/b.py'
        xjoin('c.jpg') = '/a/c.jpg'

    origin_path为绝对路径时，返回路径的upper集父文件夹后拼接
        xjoin('/b/c/d', 2, 'e', 'f') = '/b/e/f'
        xjoin('/b/c/d.py', 2, 'e', 'f') = '/b/e/f'

    origin_path为相对路径时，相当于从__file__的父文件夹开始拼接
        if __file__ = '/a/b.py'
        xjoin(__file__, 1, 'c','d.png') = '/a/c/d.png'
        xjoin('c','d.png') = '/a/c/d.png'

    origin_path为数字时, __file__作为第一个参数加入传入
        if __file__ = '/a/b.py'
        xjoin(__file__, 1, 'c','d.png') = '/a/c/d.png'
        xjoin(1, 'c','d.png') = '/a/c/d.png'
    """

    dirs = []
    lastfile = os.path.abspath(inspect.stack()[1].filename)
    if upper is None:
        return xjoin(lastfile, 1, origin_path)
    if isinstance(origin_path, int):
        dirs = [upper]
        upper = origin_path
        origin_path = lastfile
    elif not os.path.isabs(origin_path):
        dirs = [origin_path, upper]
        origin_path = lastfile
        upper = 1
    elif isinstance(upper, str):
        dirs = [upper]
        upper = 0
    res = zdir(origin_path, upper)
    res = os.path.join(res, *dirs, *args)
    if makedirs:
        os.makedirs(zdir(res, 1 - is_dir), exist_ok=True)
    return res


def zwalk(*args):
    """
    返回待扫描dir，与目录下的直接文件列表、直接文件夹列表
    args[0]为绝对路径或从工作目录开始的相对路径
    """
    if os.path.isabs(args[0]):
        dir = zjoin(*args)
    else:
        dir = rjoin(*args)
    return next(os.walk(dir))
