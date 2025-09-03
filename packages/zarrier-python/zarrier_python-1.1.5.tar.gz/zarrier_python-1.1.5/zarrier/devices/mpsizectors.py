from __future__ import annotations
import numpy as np
import MPSizectorS as mp
import time

from typing import Literal

import logging
logger = logging.getLogger(__name__)


class MPSizectorSError(Exception): ...


class MPSizectorS:

    current_device: MPSizectorS | None = None

    def __init__(self, sensor) -> None:
        self.sensor = sensor

        logger.info("set hold state")
        sensor.SetHoldState(False)

        sensor.SetDataOutMode(mp.MPSizectorS_DataOutModeType.MPSizectorS_DataOutModeType_FloatPointCloud)
        sensor.SetHoldState(False)

    @classmethod
    def open(cls, index=0):
        sensor = mp.MPSizectorS_Factory.GetInstance(mp.MPSizectorS_LogMediaType.MPSizectorS_LogMediaType_Console, 2)
        sensor.UpdateDeviceList()
        device_count = sensor.GetDeviceCount()
        print(f"发现设备数量:{device_count}")

        if device_count == 0:
            raise MPSizectorSError("设备数量为0, 请检查设备连接情况")

        device_info = sensor.GetDeviceInfo(index)
        logger.info(device_info)
        rtv = sensor.Open(device_info)

        if not rtv:
            logger.info("打开设备失败")
        else:
            logger.info("打开设备成功, 等待设备就绪")

        while True:
            device_state = sensor.GetDeviceState()
            if (
                device_state == mp.MPSizectorS_DeviceStateType.MPSizectorS_DeviceStateType_Disconnected
                or device_state == mp.MPSizectorS_DeviceStateType.MPSizectorS_DeviceStateType_UnderInit
            ):
                time.sleep(0.5)
                logger.info("等待设备连接")
            else:
                logger.info("设备就绪")
                logger.info(device_state)
                break
        cls.current_device = MPSizectorS(sensor)
        return cls.current_device

    def close(self):
        sensor = self.sensor
        self.current_device = None
        sensor.Close()
        mp.MPSizectorS_Factory.DestructInstance(sensor)

    def snap(self):
        sensor = self.sensor
        dataFormat = mp.MPSizectorS_DataFormatType.MPSizectorS_DataFormatType_FloatPointCloud
        dataFrame = mp.MPSizectorS_DataFrameUndefinedStruct()
        ret = sensor.Snap(True, dataFormat, dataFrame, 1000)
        w = dataFrame.FrameInfo.DataInfo.XPixResolution
        h = dataFrame.FrameInfo.DataInfo.YPixResolution
        logger.info(f"完成snap:{ret}")
        if not ret:
            return None
        float3dFrame = mp.MPSizectorS_Utils.ConvertToFloat3DFrame(dataFrame)
        logger.info("data retrived")
        point_arrays = float3dFrame.GetData()
        res = point_arrays.copy()
        res = np.reshape(res, (h, w))
        logger.info("frame free")
        # mp.MPSizectorS_Utils.FreeDataFrame(dataFrame)
        return res

    def deconstruct_snap(self):
        """
        返回3个ndarray
        Gray, Mask, XYZ
        """

        res = self.snap()
        if res is None:
            return None, None, None
        gray = res["Gray"]
        mask = res["Mask"]
        xyz = np.stack([res["X"], res["Y"], res["Z"]], axis=2)
        return gray, mask, xyz

    @classmethod
    def load(cls, path=None, w=5328, h=3040, type: Literal["fix", "float"] = "float"):
        """直接读取mpdat文件，建议使用deconstruct_load"""
        dataFrame = mp.MPSizectorS_DataFrameUndefinedStruct()
        mp.MPSizectorS_Utils.Load(dataFrame, path, -100, 100)
        w = 5328
        h = 3040
        if type == "float":
            frame = mp.MPSizectorS_Utils.ConvertToFloat3DFrame(dataFrame)
        else:
            frame = mp.MPSizectorS_Utils.ConvertToFix3DFrame(dataFrame)
        logger.info("data retrived")
        point_arrays = frame.GetData()
        res = point_arrays.copy()
        res = np.reshape(res, (h, w))
        logger.info("frame free")
        mp.MPSizectorS_Utils.FreeDataFrame(dataFrame)
        return res

    @classmethod
    def deconstruct_load(cls, path, w=5328, h=3040, type: Literal["fix", "float"] = "float"):
        """
        返回3个ndarray
        Gray, Mask, XYZ
        """
        res = cls.load(path, w, h, type)
        gray = res["Gray"]
        mask = res["Mask"]
        xyz = np.stack([res["X"], res["Y"], res["Z"]], axis=2)
        return gray, mask, xyz
