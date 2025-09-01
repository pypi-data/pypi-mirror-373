# -*- coding: utf-8 -*-

from Preset.Model.GameObject import GameObject
from typing import Tuple
from typing import Matrix
from Preset.Model.Transform import Transform

class Transform(GameObject):
    def __init__(self, pos=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        # type: (Tuple[float,float,float], Tuple[float,float,float], Tuple[float,float,float]) -> 'None'
        """
        坐标变换，包含位置、旋转和缩放
        """
        self.pos = None
        self.rotation = None
        self.scale = None

    def AddOffset(self, offset):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        给坐标变换位置增加偏移量
        """
        pass

    def AddRotation(self, rotation):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        给坐标变换旋转增加偏移量
        """
        pass

    def AddScale(self, scale):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        给坐标变换缩放增加偏移量
        """
        pass

    def AddTransform(self, transform):
        # type: (Transform) -> 'None'
        """
        给坐标变换增加偏移量
        """
        pass

    def GetMatrix(self):
        # type: () -> 'Matrix'
        """
        获取坐标变换矩阵
        """
        pass

