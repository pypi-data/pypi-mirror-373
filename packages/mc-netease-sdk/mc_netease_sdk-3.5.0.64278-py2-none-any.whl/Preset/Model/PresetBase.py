# -*- coding: utf-8 -*-

from Preset.Model.PartBase import PartBase
from typing import Tuple
from Preset.Model.GameObject import GameObject
from typing import List
from Preset.Model.SdkInterface import SdkInterface
from Preset.Model.BoxData import BoxData
from Preset.Model.TransformObject import TransformObject
from Preset.Model.PresetBase import PresetBase

class PresetBase(SdkInterface, TransformObject):
    def __init__(self):
        # type: () -> 'None'
        """
        PresetBase（预设基类）是所有预设的基类。预设是一类可以被直接放置在场景中的TransformObject（变换对象），并且预设下可以挂接其他TransformObject，可以通过这种方式对游戏逻辑进行简单的封装。在编辑器中放置预设时，会生成预设的虚拟实例，在游戏中生成预设，会生成实例。
        """
        self.presetId = None
        self.preLoad = None
        self.forceLoad = None
        self.childPresetInstances = None
        self.childPartInstances = None
        self.dimension = None
        self.isAlive = None

    def GetIsAlive(self):
        # type: () -> 'bool'
        """
        获取预设的存活状态
        """
        pass

    def GetGameObjectById(self, id):
        # type: (int) -> 'GameObject'
        """
        获取当前预设节点底下指定ID的游戏对象
        """
        pass

    def GetGameObjectByEntityId(self, entityId):
        # type: (str) -> 'GameObject'
        """
        获取当前预设节点底下指定实体ID的游戏对象
        """
        pass

    def GetChildPresets(self):
        # type: () -> 'List[PresetBase]'
        """
        获取当前预设的所有子预设
        """
        pass

    def GetChildPresetsByName(self, name, recursive=True):
        # type: (str, bool) -> 'List[PresetBase]'
        """
        获取指定名称的所有子预设
        """
        pass

    def GetChildPresetsByType(self, classType, recursive=True):
        # type: (str, bool) -> 'List[PresetBase]'
        """
        获取指定类型的所有子预设
        """
        pass

    def GetChildObjectByTypeName(self, classType, name=None):
        # type: (str, str) -> 'TransformObject'
        """
        获取指定实体ID的游戏对象
        """
        pass

    def GetChildObjectsByTypeName(self, classType, name=None):
        # type: (str, str) -> 'TransformObject'
        """
        获取指定实体ID的游戏对象
        """
        pass

    def SetBlockProtect(self, protect):
        # type: (bool) -> 'None'
        """
        设置预设内的所有素材区域的方块保护状态
        """
        pass

    def Replicate(self, pos):
        # type: (Tuple[float,float,float]) -> 'PresetBase'
        """
        在指定位置坐标下复制当前预设
        """
        pass

    def RemoveChild(self, child):
        # type: (TransformObject) -> 'None'
        """
        移除指定的子节点对象
        """
        pass

    def AddBoxData(self, boxData):
        # type: (BoxData) -> 'None'
        """
        添加指定的素材数据
        """
        pass

    def RemoveBoxData(self, boxData):
        # type: (BoxData) -> 'None'
        """
        移除指定的素材数据
        """
        pass

    def AddPreset(self, preset):
        # type: (PresetBase) -> 'None'
        """
        添加指定预设作为子预设
        """
        pass

    def RemovePreset(self, preset):
        # type: (PresetBase) -> 'None'
        """
        移除指定的子预设
        """
        pass

    def AddPart(self, part):
        # type: (PartBase) -> 'None'
        """
        添加指定零件作为子零件
        """
        pass

    def RemovePart(self, part):
        # type: (PartBase) -> 'None'
        """
        移除指定的子零件
        """
        pass

    def GetPartsByName(self, name):
        # type: (str) -> 'List[PartBase]'
        """
        获取指定名称的所有子零件
        """
        pass

    def GetPartByName(self, name):
        # type: (str) -> 'PartBase'
        """
        获取指定名称的第一个子零件
        """
        pass

    def GetPartsByType(self, type):
        # type: (str) -> 'List[PartBase]'
        """
        获取指定类型的所有子零件
        """
        pass

    def GetPartByType(self, type):
        # type: (str) -> 'PartBase'
        """
        获取指定类型的第一个子零件
        """
        pass

    def RemovePartsByType(self, type):
        # type: (str) -> 'None'
        """
        移除指定类型的所有子零件
        """
        pass

