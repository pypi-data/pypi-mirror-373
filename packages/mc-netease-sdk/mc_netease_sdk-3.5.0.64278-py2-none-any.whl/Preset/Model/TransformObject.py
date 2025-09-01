# -*- coding: utf-8 -*-

from typing import Matrix
from typing import Tuple
from Preset.Model.GameObject import GameObject
from typing import List
from Preset.Model.Transform import Transform
import Preset.Controller.PresetManager as PresetManager
from Preset.Model.TransformObject import TransformObject
from Preset.Model.PresetBase import PresetBase

class TransformObject(GameObject):
    def __init__(self):
        # type: () -> 'None'
        """
        TransformObject（变换对象）是拥有变换属性的GameObject（游戏对象）的基类，他们在游戏世界中有着确切的位置等信息。
        """
        self.name = None
        self.transform = None
        self.dimension = None
        self.isBroken = None
        self.isRemoved = None

    def GetDimension(self):
        # type: () -> 'int'
        """
        获取所在的维度
        """
        pass

    def SetDimension(self, dimension, pos=None):
        # type: (int, Tuple[int,int,int]) -> 'bool'
        """
        设置所在的维度
        """
        pass

    def GetChildTransformObjects(self, recursive=False):
        # type: (bool) -> 'List[TransformObject]'
        """
        获取子TransformObject列表
        """
        pass

    def GetTransformObjects(self, recursive=False):
        # type: (bool) -> 'List[TransformObject]'
        """
        获取TransformObject列表，包含自身
        """
        pass

    def GetChildGameObjects(self, recursive=False):
        # type: (bool) -> 'List[GameObject]'
        """
        获取子GameObject列表
        """
        pass

    def GetGameObjects(self, recursive=False):
        # type: (bool) -> 'List[GameObject]'
        """
        获取GameObject列表，包含自身
        """
        pass

    def GetGameObjectById(self, id):
        # type: (int) -> 'GameObject'
        """
        根据ID获取GameObject
        """
        pass

    def GetGameObjectByEntityId(self, entityId):
        # type: (str) -> 'GameObject'
        """
        根据实体ID获取GameObject
        """
        pass

    def GetId(self):
        # type: () -> 'str'
        """
        获取当前预设的ID
        """
        pass

    def GetEntityId(self):
        # type: () -> 'str'
        """
        获取当前预设的实体ID
        """
        pass

    def GetDisplayName(self):
        # type: () -> 'str'
        """
        获取当前预设的显示名称
        """
        pass

    def GetDisplayPath(self):
        # type: () -> 'str'
        """
        获取当前预设到根节点的显示路径
        """
        pass

    def GetLocalTransform(self):
        # type: () -> 'Transform'
        """
        获取当前预设的局部坐标变换
        """
        pass

    def SetLocalTransform(self, transform):
        # type: (Transform) -> 'None'
        """
        设置当前预设的局部坐标变换
        """
        pass

    def GetLocalPosition(self):
        # type: () -> 'Tuple[float,float,float]'
        """
        获取当前预设的局部坐标位置
        """
        pass

    def SetLocalPosition(self, pos):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        设置当前预设的局部坐标位置
        """
        pass

    def GetLocalRotation(self):
        # type: () -> 'Tuple[float,float,float]'
        """
        获取当前预设的局部坐标旋转
        """
        pass

    def SetLocalRotation(self, rotation):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        设置当前预设的局部坐标旋转
        """
        pass

    def GetLocalScale(self):
        # type: () -> 'Tuple[float,float,float]'
        """
        获取当前预设的局部坐标缩放
        """
        pass

    def SetLocalScale(self, scale):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        设置当前预设的局部坐标缩放
        """
        pass

    def GetWorldTransform(self):
        # type: () -> 'Transform'
        """
        获取当前预设的世界坐标变换
        """
        pass

    def GetWorldMatrix(self):
        # type: () -> 'Matrix'
        """
        获取世界坐标变换矩阵
        """
        pass

    def GetLocalMatrix(self):
        # type: () -> 'Matrix'
        """
        获取局部坐标变换矩阵
        """
        pass

    def SetWorldTransform(self, transform):
        # type: (Transform) -> 'None'
        """
        设置当前预设的世界坐标变换
        """
        pass

    def GetWorldPosition(self):
        # type: () -> 'Tuple[float,float,float]'
        """
        获取当前预设的世界坐标位置
        """
        pass

    def SetWorldPosition(self, pos):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        设置当前预设的世界坐标位置
        """
        pass

    def GetWorldRotation(self):
        # type: () -> 'Tuple[float,float,float]'
        """
        获取当前预设的世界坐标旋转
        """
        pass

    def SetWorldRotation(self, rotation):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        设置当前预设的世界坐标旋转
        """
        pass

    def GetWorldScale(self):
        # type: () -> 'Tuple[float,float,float]'
        """
        获取当前预设的世界坐标缩放
        """
        pass

    def SetWorldScale(self, scale):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        设置当前预设的世界坐标缩放
        """
        pass

    def AddLocalOffset(self, offset):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        给局部坐标变换位置增加偏移量
        """
        pass

    def AddWorldOffset(self, offset):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        给世界坐标变换位置增加偏移量
        """
        pass

    def AddLocalRotation(self, rotation):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        给局部坐标变换旋转增加偏移量
        """
        pass

    def AddWorldRotation(self, rotation):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        给世界坐标变换旋转增加偏移量
        """
        pass

    def AddLocalScale(self, scale):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        给局部坐标变换缩放增加偏移量
        """
        pass

    def AddWorldScale(self, scale):
        # type: (Tuple[float,float,float]) -> 'None'
        """
        给世界坐标变换缩放增加偏移量
        """
        pass

    def AddLocalTransform(self, transform):
        # type: (Transform) -> 'None'
        """
        给局部坐标变换增加偏移量
        """
        pass

    def AddWorldTransform(self, transform):
        # type: (Transform) -> 'None'
        """
        给世界坐标变换增加偏移量
        """
        pass

    def GetRootParent(self):
        # type: () -> 'PresetBase'
        """
        获取当前预设所在的根预设
        """
        pass

    def GetParent(self):
        # type: () -> 'PresetBase'
        """
        获取当前预设的父预设
        """
        pass

    def SetParent(self, parent):
        # type: (PresetBase) -> 'None'
        """
        设置当前预设的父预设
        """
        pass

    def GetManager(self):
        # type: () -> 'PresetManager'
        """
        获取当前预设所在的预设管理器
        """
        pass

    def Unload(self):
        # type: () -> 'None'
        """
        卸载当前预设
        """
        pass

    def Destroy(self):
        # type: () -> 'None'
        """
        销毁当前预设
        """
        pass

