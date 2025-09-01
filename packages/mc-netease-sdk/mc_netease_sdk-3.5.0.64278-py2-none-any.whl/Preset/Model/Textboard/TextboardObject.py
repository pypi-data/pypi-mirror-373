# -*- coding: utf-8 -*-

from Preset.Model.SdkInterface import SdkInterface
from typing import Tuple

class TextboardObject(SdkInterface):
    def __init__(self):
        # type: () -> 'None'
        """
        TextboardObject(文字面板对象)是对文字面板对象封装的基类，为文字面板提供了面向对象方法
        """
        self.textboardId = None

    def SetBindEntity(self, bindEntityId, offset, rot):
        # type: (str, Tuple[float,float,float], Tuple[float,float,float]) -> 'bool'
        """
        文字面板绑定实体对象
        """
        pass

    def SetPos(self, pos):
        # type: (Tuple[float,float,float]) -> 'bool'
        """
        修改文字面板预设位置
        """
        pass

    def SetRot(self, rot):
        # type: (Tuple[float,float,float]) -> 'bool'
        """
        修改旋转角度, 若设置了文本朝向相机，则旋转角度的修改不会生效
        """
        pass

    def SetScale(self, scale):
        # type: (Tuple[float,float]) -> 'bool'
        """
        内容整体缩放
        """
        pass

    def SetText(self, text):
        # type: (str) -> 'bool'
        """
        修改文字面板内容
        """
        pass

    def SetColor(self, textColor):
        # type: (Tuple[float,float,float,float]) -> 'bool'
        """
        修改字体颜色
        """
        pass

    def SetBackgroundColor(self, backgroundColor):
        # type: (Tuple[float,float,float,float]) -> 'bool'
        """
        修改背景颜色
        """
        pass

    def SetFaceCamera(self, faceCamera):
        # type: (bool) -> 'bool'
        """
        设置是否始终朝向相机
        """
        pass

    def SetBoardDepthTest(self, depthTest):
        # type: (bool) -> 'bool'
        """
        设置是否开启深度测试, 默认状态下是开启
        """
        pass

