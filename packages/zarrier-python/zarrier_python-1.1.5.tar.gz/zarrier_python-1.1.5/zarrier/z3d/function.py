from __future__ import annotations
from typing import Callable, Literal, List
from enum import Enum
import cv2
import pyvista
import numpy as np
import open3d as o3d
import os


class Z3D_DATA_TYPE:

    NONE = ["none"]
    FILE = ["file"]
    IMAGE_2D = ["image", "image_2d"]
    IMAGE_3D = ["point_cloud", "cloud", "image_3d"]
    WIDGET_2D = ["w2d"]
    WIDGET_3D = ["w3d"]

    @classmethod
    def from_mark(cls, mark):
        for k, v in Z3D_DATA_TYPE.__dict__.items():
            if k.startswith("__"):
                continue
            if not isinstance(v, list):
                continue
            if mark in v:
                return v

    @classmethod
    def from_mark_str(cls, mark_str: str):
        if mark_str == "":
            return []
        marks = mark_str.replace(" ", "").split(",")
        return [cls.from_mark(mark) for mark in marks]


class Z3DFunction:

    def __init__(
        self,
        func: Callable,
        name: str = "",
        help_inputs: str = "",
        help_outputs: str = "",
        help_detail: str = "",
        inputs_type: list[Z3D_DATA_TYPE] = [],
        outputs_type: list[Z3D_DATA_TYPE] = [],
    ):
        self.name = name
        self.func = func
        self.help_inputs = help_inputs
        self.help_outputs = help_outputs
        self.help_detail = help_detail
        self.inputs_type = inputs_type
        self.outputs_type = outputs_type

    def __call__(self, *args, **kwds):
        return self.func(*args, **kwds)

    @classmethod
    def parse(cls, fun: Callable) -> Z3DFunction:
        """
        通过fun的注释进行解构, 例如

        def imread(path):
            /"/"/"
            name: 读取2D图像
            help_inputs: 图像路径:str
            help_outputs: 2D图像
            help_detail: 读取2D图像
            input_type: file
            output_type: image
            /"/"/"
            return [cv2.imread(path)]

        """

        params: dict[str, str | list] = {"name": "", "help_inputs": "", "help_outputs": "", "help_detail": ""}
        assert isinstance(fun.__doc__, str)
        for line in fun.__doc__.split("\n"):
            if ":" not in line:
                continue
            n = line.index(":")
            key = line[:n].strip().lower()
            value = line[n + 1 :].strip()
            if key in params:
                params[key] = value
            if key == "inputs_type" or key == "outputs_type":
                params[key] = Z3D_DATA_TYPE.from_mark_str(value.lower())

        return Z3DFunction(fun, **params)
