from __future__ import annotations
from typing import List
from zarrier.math.utils import as_np
from zarrier import cached_property
import numpy as np
from .line import Segment,Line
import cv2
from zarrier.math.base import in_region


@as_np
class Polygon:

    def __init__(self, points:np.ndarray) -> None:
        self.points = np.asarray(points)

    @cached_property
    @property
    def sides(self):
        segs:List[Segment] = []
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            segs.append(Segment(p1, p2))
        return segs

    @classmethod
    def intersect(cls, poly1: Polygon, poly2: Polygon):
        """
        创建时: 运行时间2.1ms 
        第一次优化后: 运行时间0.7ms 
        """
        intersect_vertexs = []
        for s1 in poly1.sides:
            for s2 in poly2.sides:
                num,*points = s1.intersect(s2)
                intersect_vertexs += points[:num]

        for p in poly1.points:
            if poly2.contain_point(p):
                intersect_vertexs.append(p)

        for p in poly2.points:
            if poly1.contain_point(p):
                intersect_vertexs.append(p)

        res = cv2.convexHull(np.asarray(intersect_vertexs,dtype='float32'))
        return res

    def interset_line(self, tar: Segment | Line):
        res = []
        for s in self.sides:
            ins = s.intersect(tar)
            res += ins[1:ins[0]+1]
        return res

    def contain_point(self, point: np.ndarray, side_contain_allow=True):
        """ 
        判断内部包含点
        side_contain_allow = True 表示当边界包含点时依然返回True
        """
        contain = False

        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            if (point[1] - p1[1]) * (point[1] - p2[1]) > 0:
                continue
            if p1[0] < point[0] and p2[0] < point[0]:
                continue
            if p1[1] == p2[1]:
                if in_region(point[0],p1[0],p2[0]):
                    return side_contain_allow
                else:
                    contain = not contain
            else:
                x = Line.point2point(p1,p2).get_x(0)
                if x == point[0]:
                    return side_contain_allow
                elif x > point[0]:
                    contain = not contain
        return contain
    
    def min_cover_rect(self):
        """
        返回最小覆盖矩形的 中心xy，宽度高度，旋转角度
        注: 旋转角度可能出乎你的想象
        """
        return cv2.minAreaRect(self.points)
    
    def min_cover_rect_points(self,rotate_rect=None):
        """ 返回最小覆盖矩形的四个顶点坐标 """
        if rotate_rect is None:
            rotate_rect = self.min_cover_rect(self.points)
        return cv2.boxPoints(rotate_rect)

    @classmethod
    def iou(cls, poly1: Polygon, poly2: Polygon):

        inters = cls.intersect(poly1,poly2)
        union = cv2.convexHull(np.concatenate((poly1.points.astype('int32'),poly2.points.astype('int32'))))

        iarea = cv2.contourArea(inters)
        uarea = cv2.contourArea(union)
        return iarea/uarea
