from zarrier.z3d.function import Z3DFunction
from zarrier.devices.mpsizectors import MPSizectorS
import cv2
import numpy as np
import pyvista
from zarrier.math.base import svd_homogeneous, svd_non_homogeneous, rodrigues_rotation_between_vectors, rodrigues_rotate
from itertools import product


def mpsize_cloud():
    """
    name: 读取3D相机点云
    help_inputs: 无
    help_outputs: 2D图像, 3D图像, [gray, mask, xyz]
    help_detail: 读取3D图像
    inputs_type:
    outputs_type: image, point_cloud, none
    """
    mp = MPSizectorS.current_device
    if mp is None:
        mp = MPSizectorS.open()
    gray, mask, xyz = mp.deconstruct_snap()

    if gray is None:
        return None

    points = xyz[mask == 0]
    cloud = pyvista.PolyData(points)
    return [gray, cloud, [gray, mask, xyz]]


def clip_mpzise_cloud(mpsize_cloud, x0, y0, x1, y1):
    """
    name: 裁剪mp点云
    help_inputs: mp点云[gray, mask, xyz], x0, y0, x1, y1
    help_outputs: 2D图像, 3D图像, [gray, mask, xyz]
    help_detail: 裁剪mp点云
    inputs_type: none, none, none, none, none
    outputs_type: image, point_cloud, none
    """
    _gray, _mask, _xyz = mpsize_cloud

    gray = _gray[y0:y1, x0:x1]
    mask = _mask[y0:y1, x0:x1]
    xyz = _xyz[y0:y1, x0:x1]

    points = xyz[mask == 0]
    cloud = pyvista.PolyData(points)
    return [gray, cloud, [gray, mask, xyz]]


def mp_down_sample(mpsize_cloud, max_sample=13000):
    """
    name: mp点云降采样
    help_inputs: mp点云, 最大采样点数
    help_outputs: 点云
    help_detail: 将mp点云降采样
    inputs_type: none, none
    outputs_type: point_cloud
    """
    _gray, _mask, _xyz = mpsize_cloud
    h, w = _gray.shape
    step = int(np.ceil(np.sqrt(h * w / max_sample)))
    sim_mask = _mask[::step, ::step]
    sim_xyz = _xyz[::step, ::step]
    points = sim_xyz[sim_mask == 0]
    return [pyvista.PolyData(points)]


def mp_plane_norm_to_z(mpsize_cloud, fit_cloud: pyvista.PolyData, rotate_z=20, show_plane=0):
    """
    name: mp点云拨正
    help_inputs: mp点云, 拟合点云, 旋转角度, 显示平面
    help_outputs: 点云, mp点云
    help_detail: 将点云拟合的平面的法线旋转至Z轴, 并绕Z轴旋转某个角度
    inputs_type: none, none
    outputs_type: point_cloud, none
    """

    _gray, _mask, _xyz = mpsize_cloud

    points = fit_cloud.points

    center = np.average(points, axis=0)
    points = points - center
    _xyz = _xyz - center

    x, y, z = points.T
    a, b, c, d = svd_homogeneous([x, y, z, np.ones_like(x)])

    print(f"平面方程: {a:.4f}x + {b:.4f}y + {c:.4f}z + {d:.4f} = 0")

    z_axis = np.asarray((0, 0, 1))
    z_axis = z_axis / np.linalg.norm(z_axis)

    normal = np.asarray((a, b, c))
    normal = normal / np.linalg.norm(normal)
    if np.dot(normal, z_axis) < 0:
        normal = -normal  # 确保法向量朝向一致

    _xyz = rodrigues_rotation_between_vectors(normal, z_axis, _xyz)

    # 绕z轴旋转
    # _xyz = rodrigues_rotate((0, 0, 0), (0, 0, 1), np.deg2rad(rotate_z), _xyz)

    if show_plane:
        points = _xyz[_mask == 0]
        x, y, _z = points.T
        fit_z = -d * np.ones(x.shape)
        plane_points = np.stack([x, y, fit_z], axis=1)
        points = np.concatenate([points, plane_points])
    else:
        points = _xyz[_mask == 0]
    return [pyvista.PolyData(points), [_gray, _mask, _xyz]]


def mp_fit_poly_surface(mesh: pyvista.PolyData, fit_cloud: pyvista.PolyData, degree=2, show_delta=0):
    """
    name: mp点云拟合
    help_inputs: 计算点云, 拟合点云, 次数, 是否显示差
    help_outputs: 点云
    help_detail: 将拟合点云拟合为某个次数的曲面，再用计算点云进行计算
    inputs_type: none, none, none, none
    outputs_type: point_cloud
    """

    points = fit_cloud.points
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
        if i == 0 and j == 0:
            col = np.ones_like(x)  # 常数项
        else:
            col = (x**i) * (y**j)
        A.append(col)

    coeffs = svd_non_homogeneous(A, z)

    points = mesh.points
    points = points - np.average(points, axis=0)
    x, y, z = points.T
    fit_z = np.zeros_like(z)
    for (i, j), c in zip(terms, coeffs):
        if i == 0 and j == 0:
            fit_z += c
        else:
            fit_z += c * (x**i) * (y**j)

    if not show_delta:
        _points = np.stack([x, y, fit_z], axis=1)
        return [pyvista.PolyData(_points)]
    else:
        mesh = mesh.copy()
        mesh["Z"] = z - fit_z
        return [mesh]


mp_functions = [
    Z3DFunction.parse(mpsize_cloud),
    Z3DFunction.parse(clip_mpzise_cloud),
    Z3DFunction.parse(mp_down_sample),
    Z3DFunction.parse(mp_plane_norm_to_z),
    Z3DFunction.parse(mp_fit_poly_surface),
]
