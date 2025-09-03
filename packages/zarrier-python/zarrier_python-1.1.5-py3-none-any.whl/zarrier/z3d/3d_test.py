import pyvista
import numpy as np
import debugpy
import pyvista.plotting

points = np.random.random((1500000, 3))

plt = pyvista.Plotter()
cloud = pyvista.PolyData(points)

plt.add_mesh(cloud)
# plt.add_mesh_clip_box(cloud)

clip = False
i = 0

actor = None

def call_back(box: pyvista.PolyData):
    global clip, plt, i, actor
    debugpy.debug_this_thread()
    o = box.points[0]
    ox = box.points[1] - o
    oy = box.points[3] - o
    oz = box.points[4] - o
    center = box.points[14]

    lx = np.linalg.norm(ox) / 2 
    ly = np.linalg.norm(oy) / 2 
    lz = np.linalg.norm(oz) / 2

    print(center, lx, ly, lz)

    ex = ox / lx / 2
    ey = oy / ly / 2
    ez = oz / lz / 2

    x0, y0, z0 = center

    # _points = points
    _points = points - center
    R = np.column_stack([ex, ey, ez])
    print(R)
    # 正常使用是
    # R.T @ _points.T
    # 再转置一次就是
    # _points @ R
    _points = _points @ R
    mask = (
        (_points[:, 0] >=-lx) & (_points[:, 0] <=lx) &
        (_points[:, 1] >=-ly) & (_points[:, 1] <=ly) &
        (_points[:, 2] >=-lz) & (_points[:, 2] <=lz)
    )
    # mask = (
    #     (_points[:, 0] >= x0-lx) & (_points[:, 0] <= x0+lx) &
    #     (_points[:, 1] >= y0-ly) & (_points[:, 1] <= y0+ly) &
    #     (_points[:, 2] >= z0-lz) & (_points[:, 2] <= z0+lz)
    # )
    
    # plt.clear_actors()
    __points =  _points[mask]

    if actor is not None:
        plt.remove_actor(actor)
    if __points.shape[0] == 0:
        return
    __points = __points @ R.T
    __points = __points + center
    cloud = pyvista.PolyData(__points)
    # actor:pyvista.plotting.actor.Actor = plt.add_mesh(cloud, color='red')
    actor = plt.add_mesh(cloud, color='red')

    # plt.add_axes()
    # plt.show()


plt.add_box_widget(callback=call_back)
plt.add_axes()
plt.show()
