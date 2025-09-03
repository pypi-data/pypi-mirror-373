from __future__ import annotations
import numpy as np
from zarrier.math.utils import as_np
from zarrier import cached_property
from zarrier.math.base import in_region


@as_np
class Line:

    PARALLEL = 1
    COINCIDE = 2
    CROSS = 4

    def __init__(self, A, B, C) -> None:
        """"""
        self.A = A
        self.B = B
        self.C = C
        self.ABC = np.asarray((A, B, C))

    @cached_property
    @property
    def deg(self):
        """返回倾斜角,角度"""
        return np.rad2deg(self.rad)

    @cached_property
    @property
    def rad(self):
        """返回倾斜角,弧度"""
        return np.arctan2(self.A, -self.B)

    def intersect(self, line: Line):
        return Line.line_intersect(self,line)

    def get_y(self, x):
        return -(self.A * x + self.C) / self.B

    def get_x(self, y):
        return -(self.B * y + self.C) / self.A

    def contain_point(self, point: np.ndarray):
        match = np.sum(np.append(point, 1) * self.ABC)
        return match == 0

    @classmethod
    def point2point(cls, p1: np.ndarray, p2: np.ndarray):
        """
        AX + BY + C = 0
        return A, B, C
        """
        k = p2 - p1
        if k[0] == 0:
            if k[1] == 0:
                raise Exception("过两点求直线中,两点重合")
            return Line(1, 0, -p1[0])
        k = k[1] / k[0]
        return Line(k, -1, p1[1] - k * p1[0])

    @classmethod
    def point2line(cls, point, line: Line = None):
        """点到直线距离"""
        d = abs(np.sum(np.append(point, 1) * line.ABC))
        f = np.sqrt(np.sum(line.ABC[:2] ** 2))
        return d / f

    @classmethod
    def line_intersect(cls, line1: Line, line2: Line, need_check=True):
        """
        A1 x + B1 y + C1= 0
        A2 x + B2 y + C2= 0
        """
        if need_check:
            if cls.line_parallel(line1, line2) != cls.CROSS:
                return None

        delta = line1.A * line2.B - line1.B * line2.A
        x = (line2.C * line1.B - line1.C * line2.B) / delta
        y = (line1.C * line2.A - line2.C * line1.A) / delta
        return np.asarray([x, y])

    @classmethod
    def line_parallel(cls, line1: Line, line2: Line):
        """检查两直线 交叉、平行、重合"""
        delta = line1.A * line2.B == line1.B * line2.A

        if not delta:
            return cls.CROSS

        if (
            line2.C * line1.B == line1.C * line2.B
            and line1.C * line2.A == line2.C * line1.A
        ):
            return cls.COINCIDE
        return cls.PARALLEL

class Segment:

    def __init__(self, p1: np.ndarray, p2: np.ndarray):
        p1 = np.asarray(p1)
        p2 = np.asarray(p2)
        if (p2[0] < p1[0]) or (p2[0] == p1[0] and p2[1] < p1[1]):
            p1, p2 = p2, p1
        self.p1, self.p2 = p1, p2
        self.min_x = p1[0]
        self.max_x = p2[0]
        if p1[1] < p2[1]:
            self.min_y = p1[1]
            self.max_y = p2[1]
        else:
            self.min_y = p2[1]
            self.max_y = p1[1]
        self.ps = [self.p1, self.p2]

    @cached_property
    @property
    def line(self) -> Line:
        return Line.point2point(self.p1, self.p2)

    def contain_point(self, p: np.ndarray):
        if not self.line.contain_point(p):
            return False
        p1, p2 = self.ps
        if p1[0] == p2[0]:
            return min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])
        else:
            return min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0])

    def intersect_segment(self, seg: Segment):
        """
        线段交集
        线段使用2个点表示 seg[0] = p0, seg[1] = p1
        当线段部分重合时:
            返回重合部分两个端点 2, np.ndarray, np.ndarray
        交叉时：
            返回交叉点 1, np.ndarray, None
        无交点时：
            返回 0, None, None
        """
        seg1 = seg
        seg2 = self

        if seg1.min_x > seg2.max_x or seg1.max_x < seg2.min_x:
            return 0, None, None

        if seg1.min_y > seg2.max_y or seg1.max_y < seg2.min_y:
            return 0, None, None

        line1 = seg1.line
        line2 = seg2.line
        para = Line.line_parallel(line1, line2)
        if para == Line.COINCIDE:
            if line1.B == 0:
                y1 =  max(seg1.min_y,seg2.min_y)
                y2 =  min(seg1.max_y,seg2.max_y)
                if y1 > y2:
                    return 0, None, None
                else:
                    x = self.min_x
                    return 2, np.asarray([x, y1]), np.asarray([x, y2])
            else:
                x1 =  max(seg1.min_x,seg2.min_x)
                x2 =  min(seg1.max_x,seg2.max_x)
                if x1>x2:
                    return 0, None, None
                else:
                    y1 = line1.get_y(x1)
                    y2 = line1.get_y(x2)
                    return 2, np.asarray([x1, y1]), np.asarray([x2, y2])
        elif para == Line.CROSS:
            p = Line.line_intersect(line1, line2, need_check=False)
            x, y = p
            cross = (
                    in_region(x, seg1.p1[0], seg1.p2[0])
                and in_region(x, seg2.p1[0], seg2.p2[0])
                and in_region(y, seg1.p1[1], seg1.p2[1])
                and in_region(y, seg2.p1[1], seg2.p2[1])
            )
            return (1, p, None) if cross else (0, None, None)
        else:
            return 0, None, None

    def intersect_line(self,line:Line):
        """
        线段交集
        线段使用2个点表示 seg[0] = p0, seg[1] = p1
        当线段部分重合时:
            返回重合部分两个端点 2, np.ndarray, np.ndarray
        交叉时：
            返回交叉点 1, np.ndarray, None
        无交点时：
            返回 0, None, None
        """

        para = Line.line_parallel(self.line, line)
        if para == Line.COINCIDE:
            return 2, self.p1, self.p2
        elif para == Line.CROSS:
            p = Line.line_intersect(self.line, line)
            x, y = p
            cross = (
                    in_region(x, self.p1[0], self.p2[0])
                and in_region(y, self.p1[1], self.p2[1])
            )
            return (1, p, None) if cross else (0, None, None)
        else:
            return 0, None, None

    def intersect(self, tar):
        if isinstance(tar, Segment):
            return self.intersect_segment(tar)
        elif isinstance(tar, Line):
            return self.intersect_line(tar)
        else:
            raise Exception("目标必须是线段或直线")