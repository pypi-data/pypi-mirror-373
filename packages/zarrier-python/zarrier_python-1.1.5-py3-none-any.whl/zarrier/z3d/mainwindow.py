from __future__ import annotations
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import (
    QGroupBox,
    QDialog,
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QLabel,
)

from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPointF, QPoint
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap, QImage, QDragMoveEvent, QDragEnterEvent
from .function import Z3DFunction, Z3D_DATA_TYPE
from .addon_functions import addon_z3d_functions, clip_cloud_by_box
import sys
from .canvas import Canvas
import json
import cv2
from zarrier import zjoin, f
import os
from pyvistaqt import QtInteractor, BackgroundPlotter
import pyvista
from pyvista.plotting.plotter import BasePlotter
from typing import Any
import typing

"""
进一步安装PyQt5-stubs可以促进类型感知
pip install PyQt5-stubs
"""


class _QtInteractor(QtInteractor, QWidget, BasePlotter):
    """QtInteractor的类型感知有问题, 其父类是动态类型"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        return super().dragEnterEvent(event)

    def mouseMoveEvent(self, ev):
        # print(1, bool(Qt.RightButton & ev.buttons()))
        # print(2, bool(Qt.LeftButton & ev.buttons()))
        # print(3, bool(Qt.MidButton & ev.buttons()))
        c: pyvista.Camera = self.camera

        # def _(ts):
        #     if not isinstance(ts, typing.Iterable):
        #         ts = [ts]
        #     r = ''
        #     for t in ts:
        #         r += f"{round(t, 3)} "
        #     return r

        # msg = _(c.clipping_range) + _(c.direction) + _(c.distance) + _(c.focal_point) + _(c.position) + _(c.up) + _(c.parallel_scale)+_(c.roll)+_(c.view_angle)
        # print(msg)
        # self.parent().camera_position.setText(msg)
        return super().mouseMoveEvent(ev)


class _StepFrame(QFrame):

    sign_on_delete = pyqtSignal(str)
    sign_show_result = pyqtSignal(object, int)
    sign_show_function = pyqtSignal(object)

    def __init__(self, mark: str, func: Z3DFunction, default_input: str = ""):
        super().__init__()
        self.mark = mark
        self.func = func
        self.result = None
        self.list_item: _StepFrame | None = None
        self.setFixedSize(400, 100)
        self.setStyleSheet("_StepFrame{border: 1px solid #555;} QLabel{border: 1px solid #555;}")

        # 第一行
        mark_w = 40
        x = 0
        y = 0
        w = mark_w
        h = 100
        title = QLabel(mark, self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font: 22px;")
        title.setFixedSize(w, h)
        title.move(x, y)
        title.setStyleSheet("QLabel{border: 1px solid #555;}")

        x += mark_w
        w = 50
        h = 30
        label = QLabel("函数", self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(w, h)
        label.move(x, y)

        x += w
        w = 120

        label = QPushButton(self.func.name, self)
        label.setFixedSize(w, h)
        label.move(x, y)
        label.clicked.connect(self.show_function)

        x += w
        w = 60
        button = QPushButton("执行", self)
        button.setFixedSize(w, h)
        button.move(x, y)
        button.clicked.connect(f(self.call, True))

        x += w
        w = 80
        label = QLabel("缓存结果", self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(w, h)
        label.move(x, y)

        x += w
        w = 30
        check_box = QCheckBox(self)
        check_box.setFixedSize(w, h)
        check_box.move(x, y)
        self.cache_result_cb = check_box

        button = QPushButton("X", self)
        button.setFixedSize(h - 10, h - 10)
        button.move(self.width() - h + 5, 5)
        button.clicked.connect(self.on_delete)

        # 第二行
        x = mark_w
        y = 30
        h = 30

        if self.func.inputs_type == [Z3D_DATA_TYPE.FILE]:
            w = 100
            button = QPushButton("选择文件", self)
            button.setFixedSize(w, h)
            button.move(x, y)
            x += w
            w = 100
            input_line = QLineEdit(default_input, self)
            input_line.setFixedSize(self.width() - x, h)
            input_line.move(x, y)
            self.inputs = input_line

            def select_file():
                path, _ = QFileDialog.getOpenFileName(self)
                input_line.setText(path)

            button.clicked.connect(select_file)
        elif self.func.inputs_type == [Z3D_DATA_TYPE.WIDGET_3D]:
            w = 200
            label = QLabel("3D展示组件调整完成后可直接执行")
            label.move(x, y)
            self.inputs = None
        else:
            w = 50
            label = QLabel("输入", self)
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(w, h)
            label.move(x, y)
            x += w
            w = 100
            input_line = QLineEdit(default_input, self)
            input_line.setFixedSize(self.width() - x, h)
            input_line.move(x, y)
            self.inputs = input_line

        # 第三行
        x = mark_w
        y = 60
        h = 30

        row = QFrame(self)
        row.setMinimumHeight(h)
        row.move(x, y)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for i, type in enumerate(self.func.outputs_type):
            if type == Z3D_DATA_TYPE.IMAGE_2D or type == Z3D_DATA_TYPE.IMAGE_3D:
                button = QPushButton(f"查看图像{i}")
                layout.addWidget(button)
                button.clicked.connect(f(self.show_img, i))

        # if self.func.output_type == Z3DFunction.DATA_TYPE.IMAGE:
        #     button = QPushButton("查看图像", self)
        #     button.setFixedSize(w, h)
        #     button.move(x, y)
        #     button.clicked.connect(self.show_img)

    def select_func(self, *args):
        print(args)

    def on_delete(self):
        self.sign_on_delete.emit(self.mark)

    def get_params(self):
        if self.func.inputs_type == [Z3D_DATA_TYPE.WIDGET_3D]:
            return [Z3DMainWindow.current._3d_widget]

        # .TODO 暂时设计的是用空格分割的简化版, 特定场景不适用
        # 使用@代表取步骤值, @a.2表示取标识a的步骤的结果的第3个结果
        # 挺复杂，等待优化
        args = self.inputs.text().split(" ")
        params = []

        if self.func.inputs_type == [Z3D_DATA_TYPE.FILE]:
            params = [self.inputs.text()]
        elif self.func.inputs_type == []:
            params = []
        else:
            for arg in args:
                if arg.startswith("@"):
                    n = arg.index(".")
                    mark = arg[1:n]
                    result = Z3DMainWindow.current.mark2step[mark].call(force_calculate=False)
                    result_index = int(arg[n + 1 :])
                    params.append(result[result_index])
                else:
                    params.append(eval(arg))
        return params

    def call(self, force_calculate=True, *args):
        if not force_calculate and self.cache_result_cb.isChecked():
            return self.result

        if self.result is None:
            self.cache_result_cb.setChecked(True)

        params = self.get_params()
        self.result = self.func(*params)
        return self.result

    def show_img(self, i, *args):
        self.sign_show_result.emit(self, i)

    def show_function(self):
        self.sign_show_function.emit(self)


class _2DWidget(QFrame):

    def __init__(self, parent):
        super().__init__(parent)

        # self.setStyleSheet("background: #00e0e0; border: 1px solid #ccc;")

        self.canvas = Canvas(self)
        # self.canvas.zoomRequest.connect(self.zoomRequest)
        # self.canvas.setDrawingShapeToSquare(settings.get(SETTING_DRAW_SQUARE, False))

        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.scrollBars = {Qt.Vertical: scroll.verticalScrollBar(), Qt.Horizontal: scroll.horizontalScrollBar()}
        self.scrollArea = scroll
        self.canvas.scrollRequest.connect(self.scrollRequest)
        # self.canvas.newShape.connect(partial(self.newShape, False))
        # self.canvas.shapeMoved.connect(self.updateBoxlist)  # self.set_dirty
        # self.canvas.selectionChanged.connect(self.shapeSelectionChanged)
        # self.canvas.drawingPolygon.connect(self.toggleDrawingSensitive)

        tool_row = QFrame()
        tool_row.setFixedHeight(40)

        row_layout = QHBoxLayout(tool_row)
        row_layout.setAlignment(Qt.AlignCenter)
        row_layout.setContentsMargins(0, 0, 0, 0)

        self.label_position = QLabel("")
        self.label_position.setMinimumWidth(100)
        row_layout.addWidget(self.label_position)

        button = QPushButton("显示十字线")
        button.clicked.connect(self.show_cross)
        row_layout.addWidget(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll, stretch=1)
        layout.addWidget(tool_row, 0, Qt.AlignCenter)

    def load_image(self, cvimg: cv2.typing.MatLike):
        height, width = cvimg.shape[:2]
        if len(cvimg.shape) == 2:
            cvimg = cv2.cvtColor(cvimg, cv2.COLOR_GRAY2RGB)
        else:
            cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
        image = QImage(cvimg.data, width, height, width * 3, QImage.Format_RGB888)
        # self.status("Loaded %s" % os.path.basename(file_path))
        # self.image = image
        # self.cvimg = cvimg
        # self.file_mark = file_mark
        self.canvas.loadPixmap(QPixmap.fromImage(image))
        self.canvas.adjustSize()
        self.canvas.update()

    def scrollRequest(self, delta, orientation):
        units = -delta / (8 * 15)
        bar = self.scrollBars[orientation]
        v = bar.value() + bar.singleStep() * units
        bar.setValue(int(v))

    def show_cross(self):
        self.canvas.mode = not self.canvas.mode
        self.canvas.repaint()

    def show_position(self, x, y):
        self.label_position.setText(f"X:{x:.1f} Y:{y:.1f}")


class _3DWidget(QFrame):

    def __init__(self, parent):
        super().__init__(parent)

        # TODO. z3d
        # 这么写为了感知self.qt_interactor的类型
        # 等待高手优化
        # qti:_QtInteractor = QtInteractor(title="123123", parent=self)
        self.qt_interactor = _QtInteractor(title="123123", parent=self)
        # self.qt_interactor.add_axes()
        tool_row = QFrame()
        tool_row.setFixedHeight(40)

        row_layout = QHBoxLayout(tool_row)
        row_layout.setAlignment(Qt.AlignCenter)
        row_layout.setContentsMargins(0, 0, 0, 0)

        self.camera_position = QLabel("")
        self.camera_position.setMinimumWidth(100)
        row_layout.addWidget(self.camera_position)

        button = QPushButton("显示裁剪BOX")
        button.clicked.connect(self.show_cut_box)
        row_layout.addWidget(button)

        button = QPushButton("渲染裁剪部分")
        button.clicked.connect(self.render_cut)
        row_layout.addWidget(button)

        button = QPushButton("清空")
        button.clicked.connect(self.clear)
        row_layout.addWidget(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.addWidget(scroll, stretch=1)
        layout.addWidget(self.qt_interactor, stretch=1)
        layout.addWidget(tool_row, 0, Qt.AlignCenter)

        self.clip_box: pyvista.Actor = None
        self.clip_box_points = []

    def load_image(self, mesh: pyvista.PolyData):
        # height, width, depth = cvimg.shape

        # 提取 Z 坐标作为着色依据
        if "Z" not in mesh.array_names:
            z_values = mesh.points[:, 2]
            mesh["Z"] = z_values
        else:
            z_values = mesh["Z"]

        self.qt_interactor.add_mesh(mesh, scalars="Z", cmap="viridis", clim=[z_values.min(), z_values.max()])

        self.qt_interactor.add_axes()

        # self.qt_interactor.add_scalar_bar(
        #     title='Z Value',
        #     position_x=0.85,
        #     height=0.5,
        #     width=0.1
        # )

        # self.qt_interactor.add_mesh(mesh)

        # self.qt_interactor: Any = QtInteractor(title="", parent=self.page)
        # self.qt_interactor: QtInteractor | BasePlotter | QWidget
        # self.qt_interactor.setFixedSize(1300, 1300)
        # self.qt_interactor.move(0, 0)

    def scrollRequest(self, delta, orientation):
        units = -delta / (8 * 15)
        bar = self.scrollBars[orientation]
        v = bar.value() + bar.singleStep() * units
        bar.setValue(int(v))

    def show_cut_box(self):
        # self.qt_interactor.add_box_widget(self._on_cut)
        if self.clip_box is None:
            self.clip_box = self.qt_interactor.add_box_widget(callback=self.set_clip_box_points)
            # self.clip_box = self.qt_interactor.add_mesh_clip_box(self.qt_interactor._datasets[0], merge_points=False)
        else:
            self.qt_interactor.clear_box_widgets()
            self.clip_box = None

    def set_clip_box_points(self, box: pyvista.PolyData):
        self.clip_box_points = box.points

    def render_cut(self):
        mesh = self.qt_interactor._datasets[0]
        cliped_points = clip_cloud_by_box(mesh.points, self.clip_box_points)
        cloud = pyvista.PolyData(cliped_points)
        self.qt_interactor.add_mesh(cloud, "r", point_size=5)

    def _on_cut(self, *args):
        args

    def show_cross(self):
        self.canvas.mode = not self.canvas.mode
        self.canvas.repaint()

    def show_position(self, x, y):
        self.label_position.setText(f"X:{x:.1f} Y:{y:.1f}")

    def clear(self):
        self.qt_interactor.clear_actors()
        # self.qt_interactor.clear()


class Z3DMainWindow(QMainWindow):

    current: Z3DMainWindow

    _step_save_path = "./assets/z3d_config.json"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(1600, 900)
        self.setWindowTitle("Zarrier 3D")
        # self.setWindowIcon(QIcon("icon.png"))
        # win = QMainWindow()
        # win.show()

        self.mark2step: dict[str, _StepFrame] = {}

        cwidget = QWidget()
        self.setCentralWidget(cwidget)

        layout = QHBoxLayout(cwidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.init_left())
        layout.addWidget(self.init_middle())
        layout.addWidget(self.init_right(), stretch=1)

        # frame = self.init_left()
        # self.init_middle()
        # self.init_right()
        Z3DMainWindow.current = self

    def init_left(self):
        """函数集"""
        frame = QFrame()
        frame.setFixedWidth(150)
        frame.setStyleSheet("background: #ffe0e0; border: 1px solid #ccc;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("可用函数集")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font: 22px;")
        title.setFixedHeight(40)
        layout.addWidget(title)

        list_widget = QListWidget(frame)
        # list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(list_widget)
        self.list_widget_functions = list_widget
        return frame

    def init_middle(self):
        """步骤集"""
        frame = QFrame()
        frame.setFixedWidth(400)
        frame.setObjectName("middle_area")
        frame.setStyleSheet("#middle_area{background: #ffe000; border: 1px solid #ccc;}")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("处理路线图")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font: 22px;")
        title.setFixedHeight(40)
        layout.addWidget(title)

        button_row = QFrame()
        row_layout = QHBoxLayout(button_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button_row)

        button = QPushButton("增加步骤")
        button.setFixedHeight(40)
        button.clicked.connect(self.add_step)
        row_layout.addWidget(button)

        button = QPushButton("保存配置")
        button.setFixedHeight(40)
        button.clicked.connect(self.save_step)
        row_layout.addWidget(button)

        button = QPushButton("加载配置")
        button.setFixedHeight(40)
        button.clicked.connect(self.load_step)
        row_layout.addWidget(button)

        list_widget = QListWidget(frame)
        list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(list_widget)
        self.list_widget_steps = list_widget
        return frame

    def init_right(self):
        """图像展示"""

        frame = QFrame()
        frame.setObjectName("middle_area")
        frame.setStyleSheet("#middle_area{background: #ffe000; border: 1px solid #ccc;}")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("图像显示")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font: 22px;")
        title.setFixedHeight(40)
        layout.addWidget(title)

        display_area = QFrame(frame)
        # show_area.setStyleSheet("background: #ff0000; border: 1px solid #ccc;")
        display_area_layout = QVBoxLayout(display_area)

        layout.addWidget(display_area, stretch=1)

        self._2d_widget = _2DWidget(display_area)
        display_area_layout.addWidget(self._2d_widget, stretch=1)
        display_area_layout.setContentsMargins(0, 0, 0, 0)
        display_area_layout.setSpacing(0)

        self.display_area_layout = display_area_layout
        self._3d_widget = _3DWidget(display_area)
        return frame

    def add_functions(self, z3d_funs: list[Z3DFunction]):
        self.z3d_funs = z3d_funs
        self.name2func: dict[str, Z3DFunction] = {}
        # _StepFrame.functions = z3d_funs
        for zf in z3d_funs:
            self.name2func[zf.name] = zf
            self.list_widget_functions.addItem(zf.name)
        self.list_widget_functions.itemClicked.connect(self.show_function)

    def show_function(self, item: QListWidgetItem | _StepFrame):
        if isinstance(item, _StepFrame):
            zf = item.func
        else:
            i = self.list_widget_functions.currentIndex().row()
            zf = self.z3d_funs[i]

        dialog = QDialog()
        dialog.setMinimumWidth(300)
        dialog.setWindowTitle(f"函数 {zf.name} 的细节")

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("函数名:"))
        layout.addWidget(QLabel(zf.name))
        layout.addSpacing(20)
        layout.addWidget(QLabel("函数作用:"))
        layout.addWidget(QLabel(zf.help_detail))
        layout.addSpacing(20)
        layout.addWidget(QLabel("函数输入:"))
        layout.addWidget(QLabel(zf.help_inputs))
        layout.addSpacing(20)
        layout.addWidget(QLabel("函数输出:"))
        layout.addWidget(QLabel(zf.help_outputs))

        dialog.show()

        self.func_dialog = dialog

    def add_step(self):
        dia = QDialog(self)
        dia.setFixedSize(500, 200)
        dia.setWindowTitle("步骤创建")
        layout = QVBoxLayout(dia)

        row1 = QFrame(dia)
        row_layout = QHBoxLayout(row1)
        row_layout.addWidget(QLabel("请输入标识:"))
        input_mark = QLineEdit()
        row_layout.addWidget(input_mark)
        layout.addWidget(row1)

        row2 = QFrame(dia)
        row_layout = QHBoxLayout(row2)
        row_layout.addWidget(QLabel("请选择函数:"))
        func_cbox = QComboBox()
        for f in self.z3d_funs:
            func_cbox.addItem(f.name, f)
        row_layout.addWidget(func_cbox)
        layout.addWidget(row2)

        row3 = QFrame(dia)
        row_layout = QHBoxLayout(row3)
        button = QPushButton("确定")
        row_layout.addWidget(button)
        layout.addWidget(row3)

        def _add_step():
            mark = input_mark.text()
            if mark == "":
                QMessageBox.warning(self, "警告", "标识不能为空")
                return
            if mark in self.mark2step:
                QMessageBox.warning(self, "警告", f"已存在标识{mark}的步骤")
                return
            func = func_cbox.currentData()
            self._add_step(mark, func, "")
            dia.accept()

        button.clicked.connect(_add_step)
        dia.show()
        self.__add_step_dia = dia

    def _add_step(self, mark: str, func: Z3DFunction, input: str):
        if mark in self.mark2step:
            QMessageBox.warning(self, "警告", f"已存在标识{mark}的步骤")
            return

        step_frame = _StepFrame(mark, func, input)
        self.mark2step[mark] = step_frame
        step_frame.sign_on_delete.connect(self.remove_step)
        step_frame.sign_show_result.connect(self.show_result)
        step_frame.sign_show_function.connect(self.show_function)

        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(step_frame.width(), step_frame.height()))
        list_item.setData(Qt.UserRole, mark)
        self.list_widget_steps.addItem(list_item)
        self.list_widget_steps.setItemWidget(list_item, step_frame)
        step_frame.list_item = list_item

    def remove_step(self, mark):
        i = self.list_widget_steps.row(self.mark2step[mark].list_item)
        self.list_widget_steps.takeItem(i)
        del self.mark2step[mark]

    def show_result(self, step: _StepFrame, i: int):

        if step.result is None:
            QMessageBox.warning(self, "警告", f"步骤{step.mark}的结果为空, 请先执行")
            return

        # 首选需要切换widget
        current_widget = self.display_area_layout.itemAt(0).widget()
        if step.func.outputs_type[i] == Z3D_DATA_TYPE.IMAGE_2D:
            src = self._3d_widget
            tar = self._2d_widget
        elif step.func.outputs_type[i] == Z3D_DATA_TYPE.IMAGE_3D:
            src = self._2d_widget
            tar = self._3d_widget
        src.hide()
        tar.show()
        tar.load_image(step.result[i])
        if current_widget != tar:
            self.display_area_layout.replaceWidget(src, tar)

    def save_step(self):
        n = self.list_widget_steps.count()
        data = []
        for i in range(n):
            item = self.list_widget_steps.item(i)
            step = self.list_widget_steps.itemWidget(item)
            assert isinstance(step, _StepFrame)
            data.append([step.mark, step.func.name, step.inputs and step.inputs.text()])
        zjoin(self._step_save_path, 1, makedirs=True, is_dir=True)
        with open(self._step_save_path, "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load_step(self):
        with open(self._step_save_path, "r", encoding="utf8") as f:
            data = json.load(f)
        for mark, name, input in data:
            func = self.name2func[name]
            self._add_step(mark, func, input)

    def resizeEvent(self, event):
        # if self.canvas and not self.image.isNull() and self.zoomMode != self.MANUAL_ZOOM:
        #     self.adjustScale()
        super().resizeEvent(event)


def main(functions):
    app = QApplication(sys.argv)
    app.setApplicationName("Zarrier 3D")
    z3d = Z3DMainWindow()
    z3d.show()
    z3d.add_functions(addon_z3d_functions + functions)
    app.exec_()
