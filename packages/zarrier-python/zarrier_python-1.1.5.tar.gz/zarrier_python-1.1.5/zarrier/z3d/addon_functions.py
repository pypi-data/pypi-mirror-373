from __future__ import annotations
import pyvista
from .function import Z3DFunction
import numpy as np
import typing
import open3d as o3d
from zarrier.math.base import svd_homogeneous, svd_non_homogeneous, rodrigues_rotation_between_vectors, rodrigues_rotate
from itertools import product
import os
import cv2

if typing.TYPE_CHECKING:
    from .mainwindow import _3DWidget
    from pyvista import Camera


# 计算视图矩阵
def get_view_matrix(camera: Camera):
    focal = np.array(camera.focal_point)
    pos = np.array(camera.position)
    up = np.array(camera.up)
    direction = (focal - pos) / np.linalg.norm(focal - pos)
    right = np.cross(direction, up)
    up = np.cross(right, direction)
    view_mat = np.eye(4)
    view_mat[:3, 0] = right
    view_mat[:3, 1] = up
    view_mat[:3, 2] = -direction
    view_mat[:3, 3] = -pos
    return view_mat


# 计算投影矩阵（透视投影）
def get_proj_matrix(camera: Camera, window_size=(800, 600)):
    fov = camera.view_angle
    aspect = window_size[0] / window_size[1]
    near, far = camera.clipping_range
    proj_mat = np.zeros((4, 4))
    proj_mat[0, 0] = 1 / (aspect * np.tan(np.radians(fov / 2)))
    proj_mat[1, 1] = 1 / np.tan(np.radians(fov / 2))
    proj_mat[2, 2] = -(far + near) / (far - near)
    proj_mat[2, 3] = -2 * far * near / (far - near)
    proj_mat[3, 2] = -1
    return proj_mat


def world_to_clip(points, view_mat, proj_mat):
    homogeneous = np.hstack([points, np.ones((len(points), 1))])
    clip_coords = (homogeneous @ view_mat.T) @ proj_mat.T
    return clip_coords


def is_in_frustum(points, camera, window_size=(800, 600)):
    view_mat = get_view_matrix(camera)
    proj_mat = get_proj_matrix(camera, window_size)
    clip_coords = world_to_clip(points, view_mat, proj_mat)

    # 归一化处理
    w = clip_coords[:, 3]
    valid = w > 0  # 排除背面点
    ndc = clip_coords[valid] / w[valid, None]

    # 视锥体边界检测
    mask_x = np.logical_and(ndc[:, 0] >= -1, ndc[:, 0] <= 1)
    mask_y = np.logical_and(ndc[:, 1] >= -1, ndc[:, 1] <= 1)
    mask_z = np.logical_and(ndc[:, 2] >= -1, ndc[:, 2] <= 1)
    combined_mask = mask_x & mask_y & mask_z

    # 返回全局索引
    global_mask = np.zeros(len(points), dtype=bool)
    global_mask[valid] = combined_mask
    return global_mask


def imread(path):
    """
    name: 读取2D图像
    help_inputs: 图像路径:str
    help_outputs: 2D图像
    help_detail: 读取2D图像
    inputs_type: file
    outputs_type: image
    """
    return [cv2.imread(path)]


def img_cut(img, x1, x2, y1, y2):
    """
    name: 裁剪图像
    help_inputs: img, x1, x2, y1, y2
    help_outputs: 2D图像
    help_detail: 裁剪
    inputs_type: image, none, none, none, none
    outputs_type: image
    """
    return [img[y1:y2, x1:x2]]


def pyvista_read(path: str):
    """
    name: 读取3D图像
    help_inputs: 图像路径:str
    help_outputs: 3D图像
    help_detail: 读取3D图像
    inputs_type: file
    outputs_type: point_cloud
    """

    path = path.replace('"', "")

    path_split: tuple[str, str] = os.path.splitext(path)
    prefix, suffix = path_split
    suffix = suffix.lower()

    if suffix == ".pcd":
        cloud = o3d.io.read_point_cloud(path)
        points = np.asarray(cloud.points)
        cloud = pyvista.PolyData(points)
        return [cloud]
    elif suffix == ".ply":
        return [pyvista.read(path)]
    elif suffix == ".npz":
        (points,) = np.load(path).values()
        cloud = pyvista.PolyData(points)
        return [cloud]


def clip_cloud_by_box(points, box_points):
    """
    返回裁剪后的点云
    box_points必须是add_box_widget返回的box.points
    满足以下方向边与中心
    o = box_points[0]
    ox = box_points[1] - o
    oy = box_points[3] - o
    oz = box_points[4] - o
    center = box_points[14]
    """
    o = box_points[0]
    ox = box_points[1] - o
    oy = box_points[3] - o
    oz = box_points[4] - o
    center = box_points[14]

    lx = np.linalg.norm(ox) / 2
    ly = np.linalg.norm(oy) / 2
    lz = np.linalg.norm(oz) / 2

    ex = ox / lx / 2
    ey = oy / ly / 2
    ez = oz / lz / 2

    _points = points - center
    R = np.column_stack([ex, ey, ez])
    # print(R)
    # 正常使用是
    # R.T @ _points.T
    # 再转置一次就是
    # _points @ R
    _points = _points @ R
    mask = (
        (_points[:, 0] >= -lx)
        & (_points[:, 0] <= lx)
        & (_points[:, 1] >= -ly)
        & (_points[:, 1] <= ly)
        & (_points[:, 2] >= -lz)
        & (_points[:, 2] <= lz)
    )
    __points = _points[mask]
    if __points.shape[0] == 0:
        return __points
    __points = __points @ R.T
    __points = __points + center
    return __points


def z3d_clip_cloud_by_box(w3d: _3DWidget):
    """
    name: box裁剪点云
    help_inputs: 需要打开3D展示界面, 并且使用box圈好使用部分
    help_outputs: 3D图像
    help_detail: 获取当前box内3D点云
    inputs_type: w3d
    outputs_type: point_cloud
    """
    mesh = w3d.qt_interactor._datasets[0]
    points = mesh.points
    _points = clip_cloud_by_box(points, w3d.clip_box_points)
    cloud = pyvista.PolyData(_points)
    return [cloud]


def random_point_cloud(n: int):
    """
    name: 随机3D点云
    help_inputs: 点数量
    help_outputs: 3D图像
    help_detail: 生成随机3D点云
    inputs_type: none
    outputs_type: point_cloud
    """
    points = np.random.random((n, 3))
    cloud = pyvista.PolyData(points)
    return [cloud]


def remove_outlier(mesh: pyvista.PolyData, nb_neighbors=50, std_ratio=2.0):
    """
    name: 离群点去除
    help_inputs: 点云, 邻域点数阈值(建议20-100), 标准差倍数(值越小过滤越严格)
    help_outputs: 点云
    help_detail: 离群点去除
    inputs_type: none, none, none
    outputs_type: point_cloud
    """

    points = mesh.points
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # 执行滤波
    inlier_cloud, ind = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    points = np.asarray(inlier_cloud.points)
    return [pyvista.PolyData(points)]


def down_sample(mesh: pyvista.PolyData, max_sample=13000):
    """
    name: 点云降采样
    help_inputs: 点云, 最大采样点数
    help_outputs: 点云
    help_detail: 将点云降采样
    inputs_type: none, none
    outputs_type: point_cloud
    """
    points = mesh.points
    step = int(np.ceil(points.shape[0] / max_sample))
    return [pyvista.PolyData(points[::step])]


def plane_norm_to_z(mesh: pyvista.PolyData, rotate_z=20, show_plane=0):
    """
    name: 点云拨正
    help_inputs: 点云, 旋转角度, 显示平面
    help_outputs: 点云
    help_detail: 将点云拟合的平面的法线旋转至Z轴, 并绕Z轴旋转某个角度
    inputs_type: none, none
    outputs_type: point_cloud
    """

    points = mesh.points
    points = points - np.average(points, axis=0)

    x, y, z = points.T
    a, b, c, d = svd_homogeneous([x, y, z, np.ones_like(x)])

    print(f"平面方程: {a:.4f}x + {b:.4f}y + {c:.4f}z + {d:.4f} = 0")

    normal = [a, b, c]

    z_axis = (0, 0, 1.0)
    z_axis = z_axis / np.linalg.norm(z_axis)

    normal = normal / np.linalg.norm(normal)
    if np.dot(normal, z_axis) < 0:
        normal = -normal  # 确保法向量朝向一致

    _points = rodrigues_rotation_between_vectors(normal, z_axis, points)

    # 绕z轴旋转
    _points = rodrigues_rotate((0, 0, 0), (0, 0, 1), np.deg2rad(rotate_z), _points)

    if show_plane:
        x, y, _z = _points.T
        fit_z = -d * np.ones(x.shape)
        plane_points = np.stack([x, y, fit_z], axis=1)
        points = np.concatenate([_points, plane_points])
    else:
        points = _points

    return [pyvista.PolyData(points)]


def fit_poly_surface(mesh: pyvista.PolyData, degree=2, show_delta=0):
    """
    name: 点云拟合
    help_inputs: 点云, 次数, 0显示拟合曲面/1颜色显示拟合结果差
    help_outputs: 点云
    help_detail: 将点云拟合为某个次数的曲面
    inputs_type: none, none, none
    outputs_type: point_cloud
    """

    points = mesh.points
    points = points - np.average(points, axis=0)

    x, y, z = points.T

    # 生成多项式项的组合：i + j ≤ degree
    terms = []
    for i, j in product(range(degree + 1), repeat=2):
        if i + j <= degree:
            terms.append((i, j))

    # 构造设计矩阵
    A = []
    for i, j in terms:
        col = (x**i) * (y**j)
        A.append(col)

    coeffs = svd_non_homogeneous(A, z)

    fit_z = np.zeros_like(z)
    for term_value, c in zip(A, coeffs):
        fit_z += c * term_value

    if not show_delta:
        _points = np.stack([x, y, fit_z], axis=1)
        return [pyvista.PolyData(_points)]
    else:
        mesh = mesh.copy()
        mesh["Z"] = z - fit_z
        return [mesh]


addon_z3d_functions = [
    Z3DFunction.parse(imread),
    Z3DFunction.parse(img_cut),
    Z3DFunction.parse(pyvista_read),
    Z3DFunction.parse(down_sample),
    Z3DFunction.parse(z3d_clip_cloud_by_box),
    Z3DFunction.parse(random_point_cloud),
    Z3DFunction.parse(remove_outlier),
    Z3DFunction.parse(plane_norm_to_z),
    Z3DFunction.parse(fit_poly_surface),
]
