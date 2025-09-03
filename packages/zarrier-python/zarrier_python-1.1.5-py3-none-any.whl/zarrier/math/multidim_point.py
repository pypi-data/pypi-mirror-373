from typing import List
import numpy as np
import math


class MultidimPointWatcher:
    """接收空间点集后，生成矩形膨胀闭包，可以判断接下来的点是否在该闭包中"""

    DTYPE_ABS = "absolute"
    DTYPE_REL = "relative"

    def __init__(
        self,
        points: np.ndarray = None,
        bounds: np.ndarray = None,
        dim=None,
        max_delta=[10000000],
        min_delta=[0.000001],
        block_nums=[10],
        dilation=[0.5],
        dilation_type=[DTYPE_REL],
    ) -> None:
        self.points = points
        self.bounds: List[List] = bounds
        self.dim = dim
        if self.points is not None and self.dim is None:
            self.dim = self.points[0].size
        self.max_delta = max_delta + [max_delta[-1]] * self.dim
        self.min_delta = min_delta + [min_delta[-1]] * self.dim
        self.block_nums = block_nums + [block_nums[-1]] * self.dim
        self.dilation = dilation + [dilation[-1]] * self.dim
        self.dilation_type = dilation_type + [dilation_type[-1]] * self.dim

    def generate_bounds(self):
        self.bounds = [[] for i in range(self.dim)]
        self._cut_one_dim(self.points)

    def check_in(self,point):
        pairs = self.bounds[0]
        for i in range(self.dim):
            x = point[i]
            which = self.in_which(pairs,x)
            if which < 0:
                return False
            if self.dim == i+1:
                return True
            start, end = map(int,pairs[which][2:])
            pairs = self.bounds[i+1][start:end]
            
    def in_which(self,pairs,x):
        if x < pairs[0][0]:
            return -1
        if x >= pairs[-1][1]:
            return -1
        left = 0
        right = len(pairs) - 1
        while right >= left:
            middle = int((left+right)/2)
            pair = pairs[middle]
            if x < pair[0]:
                right = middle - 1
                continue
            if x >= pair[1]:
                left = middle + 1
                continue
            return middle
        return -1

    def _cut_one_dim(self, points: np.ndarray, dim=0):
        x = points[:, 0]
        x0, x1 = x.min(), x.max()

        if x1 - x0 < self.min_delta[dim]:
            m = (x1+x0)/2
            pairs = [[m-self.min_delta[dim]/2,m+self.min_delta[dim]/2]]
        else:
            pairs = []
            if points.shape[0] > 1:
                n = self.block_nums[dim]
            else:
                n = 1
            step = min(max((x1 - x0) / n, self.min_delta[dim]), self.max_delta[dim])
            n = math.ceil((x1-x0) / step)
            for i in range(n):
                pairs.append([x0 + i * step, x0 + (i + 1) * step])

        if self.dilation_type[dim] == self.DTYPE_ABS:
            pairs[0][0] -= self.dilation[dim]
            pairs[-1][1] += self.dilation[dim]
        else:
            pairs[0][0] -= self.dilation[dim] * step
            pairs[-1][1] += self.dilation[dim] * step
        
        points = points[np.argsort(x)]
        pointss = []
        subset = []
        pair_index = 0
        start, end = pairs[0]
        for p in points:
            while p[0] >= end:
                pair_index += 1
                start, end = pairs[pair_index]
                pointss.append(subset)
                subset = []
            subset.append(p)
        pointss.append(subset)
        slim_pairs = []
        start_index = len(self.bounds[dim])
        for pair, points in zip(pairs, pointss):
            if len(points) == 0:
                continue
            slim_pairs.append(pair)
            if points[0].size > 1:
                start, end = self._cut_one_dim(np.asarray(points)[:, 1:], dim + 1)
                self.bounds[dim].append((*pair, start, end))
            else:
                self.bounds[dim].append((*pair, None, None))
        return start_index , len(self.bounds[dim])
