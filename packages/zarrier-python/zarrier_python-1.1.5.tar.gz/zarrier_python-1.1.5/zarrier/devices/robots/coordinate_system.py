import numpy as np
from numpy.linalg import lstsq
from ...function import f, auto_cast
from sympy import symbols, Matrix, solve, sin, cos, Eq
import math

auto_np = f(auto_cast, type_cast={"np.ndarray": np.asarray})


@auto_np
def transformation(A: np.ndarray, B: np.ndarray):
    """
    solve A * X = B
    A: MxN
    B: MxL
    X: NxL
    return: X
    """
    T, residuals, rank, s = lstsq(A, B, rcond=None)
    return T


class Axis6Robot:
    """
    角度默认使用弧度
    """

    @classmethod
    def rotate_x(cls, t):
        return np.asarray([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])

    @classmethod
    def rotate_y(cls, t):
        return np.asarray([[np.cos(t), 0, np.sin(t)], [0, 1, 0], [-np.sin(t), 0, np.cos(t)]])

    @classmethod
    def rotate_z(cls, t):
        return np.asarray([[np.cos(t), -np.sin(t), 0], [np.sin(t), np.cos(t), 0], [0, 0, 1]])

    def __init__(
        self,
    ):
        self.angle_rotate_axis = []
        self.angle_factorial = []
        self.position_matrix = []

    def set_rotate_axiss(self, axiss=["z", "y", "y", "z", "y", "z"]):
        self.angle_rotate_axis = [getattr(self, "rotate_" + a) for a in axiss]

    def joor2coor(self, joor, rad=True):
        if not rad:
            joor = np.deg2rad(np.asarray(joor))
        rotates = []
        for j, rotate in zip(joor, self.angle_rotate_axis):
            rotates.append(rotate(j))
        factorials = []
        for r in rotates:
            if len(factorials > 0):
                factorials.append(r)
            else:
                factorials.append(r)

    def coor2joor(self, joor, rad=True):
        pass

    @classmethod
    def rotate_symbol_x(cls, a):
        return Matrix(
            [
                [1, 0, 0],
                [0, cos(a), -sin(a)],
                [0, sin(a), cos(a)],
            ]
        )

    @classmethod
    def rotate_symbol_y(cls, a):
        return Matrix(
            [
                [cos(a), 0, sin(a)],
                [0, 1, 0],
                [-sin(a), 0, cos(a)],
            ]
        )

    @classmethod
    def rotate_symbol_z(cls, a):
        return Matrix(
            [
                [cos(a), -sin(a), 0],
                [sin(a), cos(a), 0],
                [0, 0, 1],
            ]
        )

    @classmethod
    def solve_rxryrz_with_symbols(cls):
        """
        3x3正交矩阵相等只需要右上角3个元素相等，即可解出8个解
        """

        t12, t13, t23 = symbols("t12，t13 t23")
        rx, ry, rz = symbols("rx ry rz")
        m = cls.rotate_symbol_x(rx) * cls.rotate_symbol_y(ry) * cls.rotate_symbol_z(rz)
        res = solve([Eq(t12, m[0, 1]), Eq(t13, m[0, 2]), Eq(t23, m[1, 2])], rx, ry, rz)
        return res

    @classmethod
    def dim3_orthogonal_matrix_to_rxryrz(cls, m):
        """
        m: 3x3 np.ndarray
        使用cls.solve_rxryrz_with_symbols解出的符号解，然后直接带入验证，返回
        """
        t13 = m[0][2]
        t12 = m[0][1]
        t23 = m[1][2]
        pi = math.pi
        cos_t13 = math.sqrt(1 - t13**2)
        asin_t9 = math.asin(t23/cos_t13)
        asin_t1 = math.asin(t12/cos_t13)
        asin_t13 = math.asin(t13)
        solutions = [(pi - asin_t9, pi - asin_t13, pi - asin_t1,),
                    (pi - asin_t9, pi - asin_t13, asin_t1,),
                    (asin_t9 + pi, asin_t13, asin_t1 + pi,),
                    (asin_t9 + pi, asin_t13, -asin_t1,),
                    (-asin_t9, asin_t13, asin_t1 + pi,),
                    (-asin_t9, asin_t13, -asin_t1,),
                    (asin_t9, pi - asin_t13, pi - asin_t1,),
                    (asin_t9, pi - asin_t13, asin_t1,)]
        
        ok_solution = []
        for s in solutions:
            _m = cls.rotate_x(s[0]) @ cls.rotate_y(s[1]) @ cls.rotate_z(s[2])
            if np.max(np.abs(m-_m)) < 1e-5:
                ok_solution.append(s)
        return np.asarray(ok_solution)






