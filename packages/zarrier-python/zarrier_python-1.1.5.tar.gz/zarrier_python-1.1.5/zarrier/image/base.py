import cv2
import numpy as np
from PIL import Image
import os
from shapely import Polygon


def _crop_rect(img: cv2.typing.MatLike, points, angle):
    h, w, _ = img.shape
    center = (w / 2, h / 2)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    rect = cv2.RotatedRect(center, (w, h), angle)
    newimg_points = cv2.boundingRect(rect.points())
    new_size = newimg_points[2:]
    m[:, 2] -= newimg_points[:2]
    new_img = cv2.warpAffine(img, m, new_size)
    new_points = np.round(points @ m[:, :2].T + m[:, 2]).astype("int32")
    x0, y0 = new_points.min(axis=0)
    x1, y1 = new_points.max(axis=0)
    res = new_img[y0 : y1 + 1, x0 : x1 + 1]
    return res


def crop_rect(img: cv2.typing.MatLike, points):
    "无序裁剪"

    rotated = cv2.minAreaRect(points)
    angle = rotated[2]

    # 有些矩形长度方向是竖着的，需要扶正
    if abs(angle - 90) < 15:
        angle = rotated[2] - 90

    return _crop_rect(img, points, angle)


def points_to_same_order(base_points, points):
    """
    返回points中距base_points最近的点的数组
    """

    ps1 = np.asarray(base_points).copy()
    ps2 = np.asarray(points).copy()

    res = []
    for p in ps1:
        ds = ps2 - p
        ds = np.sum(ds**2, axis=1)
        i = np.argmin(ds)
        res.append(ps2[i])
        ps2 = np.delete(ps2, i, axis=0)

    return np.asarray(res)


def points_to_same_order_base(base_points, points):
    """
    返回points中距base_points最近的点的数组
    """
    res = []
    for bp in base_points:
        ds = np.sum((points - bp) ** 2, axis=1)
        res.append(points[np.argmin(ds)])
    return np.asarray(res)


def crop_ordered_rect(img: cv2.typing.MatLike, points):
    "有序裁剪, 将points的第1个点到第2个点的边作为裁剪后矩形的上边"

    vec = points[1] - points[0]
    angle = np.arctan2(*vec[::-1]) * 180 / np.pi
    return _crop_rect(img, points, angle), angle


def rotate_90x(img, angle):
    "顺时针旋转0,90,180,270"
    angle = int(angle)
    angle = angle % 360
    if angle == 0:
        return img
    if angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    if angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)


def generate_gif_from_dir(dir, tar_path, duration=200, loop=0, tar_size=None):
    """
    duration=200 表示每帧之间的延迟时间为200毫秒
    loop=0 表示无限循环
    """
    images = []
    files = os.listdir(dir)
    for file in files:
        img = Image.open(os.path.join(dir, file))
        if tar_size is not None:
            img = img.resize(tar_size)
        images.append(img)
        print(f"已读取完成 {len(images)} / {len(files)}， 读取 {file}")

    print("正在组合成gif")
    images[0].save(tar_path, save_all=True, append_images=images[1:], duration=duration, loop=loop)
    print(f"成功生成:{tar_path}")


def compute_iou(polygon_a, polygon_b):
    """交的面积除以并的面积"""

    if not isinstance(polygon_a, Polygon):
        polygon_a = Polygon(np.asarray(polygon_a).reshape((4, 2)))
    if not isinstance(polygon_b, Polygon):
        polygon_b = Polygon(np.asarray(polygon_b).reshape((4, 2)))

    if not polygon_a.is_simple:
        print("不是简单曲线")
        return 0

    if not polygon_b.is_simple:
        print("不是简单曲线")
        return 0
    # 计算两个多边形的交集
    intersection = polygon_a.intersection(polygon_b)
    # 计算两个多边形的并集
    union = polygon_a.union(polygon_b)
    # 计算交并比
    iou = intersection.area / union.area
    return iou


def compute_ioa(polygon_a, polygon_b):
    """交的面积除以a的面积"""

    if not isinstance(polygon_a, Polygon):
        polygon_a = Polygon(np.asarray(polygon_a).reshape((4, 2)))
    if not isinstance(polygon_b, Polygon):
        polygon_b = Polygon(np.asarray(polygon_b).reshape((4, 2)))

    if not polygon_a.is_simple:
        print("不是简单曲线")
        return 0

    if not polygon_b.is_simple:
        print("不是简单曲线")
        return 0

    # 计算两个多边形的交集
    intersection = polygon_a.intersection(polygon_b)

    # 计算交并比
    iou = intersection.area / polygon_a.area
    return iou


