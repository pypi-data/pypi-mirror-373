from __future__ import annotations
from typing import List, Tuple, Any,Callable,Dict
import cv2
import numpy as np
from zarrier.math.geometry.plane.line import Line, Segment
from zarrier.math.geometry.plane.polygon import Polygon


class CLine:

    def __init__(self, line: Line, index, horizon) -> None:
        self.line = line
        self.index = index

        self.horizon = horizon
        
        self.axis = 'x'
        
        if horizon:
            self.intercept = -line.C / line.B
        else:
            self.intercept = -line.C / line.A

        self.score = -1
        self.order = -1

class Calibration:

    def __init__(self, img: cv2.typing.MatLike) -> None:
        self.origin_img = img
        self.display_img = img.copy()

        if len(img.shape) == 3:
            self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            self.gray = img.copy()
        self.current_img = self.gray.copy()

        h,w = img.shape[:2]
        self.box = Polygon([(0, 0), (0, h), (w, h), (w, 0)])
        self.lines: List[CLine] = []
        self.saved_lines: List[CLine] = {}

    def clarity(self):
        img = self.current_img
        h, w = img.shape
        d = np.sum(np.abs(img[1:, :] - img[:-1, :]))
        d += np.sum(np.abs(img[:, 1:] - img[:, :-1]))
        res = d / h / w
        self.msg(f"目前清晰度为 {res:.03f}")
        return res

    def rec_lines(self,canny_th1=50, canny_th2=50, hough_dr=1, hough_dt=0.002, hough_th=300):
        edges = cv2.Canny(self.gray, canny_th1, canny_th2, apertureSize=3)
        hlines = cv2.HoughLines(edges, hough_dr, hough_dt, hough_th)
        self.lines = []
        for i, ((r, t),) in enumerate(hlines):
            a = np.cos(t)
            b = np.sin(t)
            c = -r
            line = Line(a, b, c)
            horizon = bool(abs(line.deg) < 45 or abs(180 - abs(line.deg)) < 45)
            cline = CLine(line, i, horizon)
            self.lines.append(cline)

        return self.lines

    def modify_lines(self, clines: List[CLine]):
        horizon_lines:Dict[bool,List[CLine]] = {False:[], True:[]}
        for cline in clines:
            horizon_lines[cline.horizon].append(cline)
        from sklearn.cluster import KMeans, DBSCAN
        res:Dict[bool,Dict[int, CLine]] = {}
        for horizon in [False,True]:
            _clines = horizon_lines[horizon]
            if horizon:
                ds = np.asarray([ -c.line.C / c.line.B for c in _clines]).reshape(-1, 1)
            else:
                ds = np.asarray([ -c.line.C / c.line.A for c in _clines]).reshape(-1, 1)
            db = DBSCAN(min_samples=1, eps=100)
            db.fit(ds)

            label_lines:Dict[int, List[CLine]] = {}

            for i,label in enumerate(db.labels_):
                lines = label_lines.setdefault(label,[])
                lines.append(_clines[i])

            choosed_lines:Dict[int, CLine] = {}
            for i, clines in label_lines.items():

                print(f"当前bunch label = {i}")
                for cl in clines:
                    cl.score = self.line_score(cl)
                    print((cl.index, cl.score))

                cline = max(clines, key = lambda cl : cl.score)

                choosed_lines[i] = cline

            res[horizon] = choosed_lines
        return res

    def line_score(self, cline:CLine, width = 2, r = 50):
        line = cline.line
        delta = 0
        n = 0
        h, w = self.current_img.shape[:2]
        if cline.horizon:
            for x in range(0, w, width * 2):
                y = int(line.get_y(x))
                if y - r <= 0 or y + r >= h:
                    continue
                delta += np.sum(np.abs(self.current_img[y : y + r, x - width : x + width] - self.current_img[y - r : y, x - width : x + width]))
                n += 2*r
        else:
            for y in range(0, h, width * 2):
                x = int(line.get_x(y))
                if x - r <= 0 or x + r >= w:
                    continue
                delta += np.sum(np.abs(self.current_img[y - width : y + width, x : x + r] - self.current_img[y - width : y + width, x - r : x]))
                n += 2*r
        s = delta / n
        print(f" {line.A:.04f}, {line.B:.04f}, {line.C:.04f} total {n:05d} score = {s:.04f}")
        return s

    def draw_line(self, cline: CLine):
        ps = self.box.interset_line(cline.line)
        if len(ps) > 1:
            cv2.line(self.display_img, ps[0].astype("int"), ps[1].astype("int"), (0, 255, 255), 3)
            # if edge.horizon:
            p = ps[0].astype("int")
            if p[0] >= self.display_img.shape[1] - 10:
                p = ps[1].astype("int")
                p[1] += 100
            color = (255 * cline.horizon, 0, 255 - 255 * cline.horizon)
            cv2.putText(self.display_img, f"{cline.index}", p, cv2.FONT_HERSHEY_SIMPLEX, 4, color, thickness=10)

    def tune_line(self, cline: CLine, callback:Callable=None):
        self.current_img = self.current_img.astype("int32")

        current_cline = cline
        current_score = self.line_score(cline)
        need_continue = True

        mda = 0.1
        mdc = 10

        while need_continue:
            need_continue = False
            line  = current_cline.line
            
            for da in [-mda, mda, 0]:
                if need_continue:
                    break
                for dc in [0, -mdc, mdc]:
                    if da == 0 and dc == 0:
                        continue
                    a = line.A + da * cline.horizon
                    b = line.B + da*(1-cline.horizon)
                    c = line.C + dc
                    test_cline = CLine(Line(a,b,c), cline.index, cline.horizon)
                    score = self.line_score(test_cline)
                    if score > current_score:
                        current_cline = test_cline
                        current_score = score
                        need_continue = True
                        break
            
            if not need_continue:
                if mda > 0.0001:
                    mda /= 2
                    need_continue = True
                elif mdc > 0.5:
                    mdc /= 2
                    need_continue = True
            
            callback and callback(current_cline)

        print(f"微调完成")
        return current_cline



