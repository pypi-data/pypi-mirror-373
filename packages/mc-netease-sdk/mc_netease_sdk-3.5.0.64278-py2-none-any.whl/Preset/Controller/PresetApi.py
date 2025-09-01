# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase
clientPartApi = PartBase()
clientPartApi.isClient = True
serverPartApi = PartBase()
serverPartApi.isClient = False

from Preset.Model.PartBase import PartBase
from Preset.Model.TransformObject import TransformObject
from typing import Tuple
from Preset.Model.PresetBase import PresetBase
from typing import List
from Preset.Model.Block.BlockPreset import BlockPreset
from Preset.Model.Transform import Transform

def CreateTransform(pos=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    # type: (Tuple[float,float,float], Tuple[float,float,float], Tuple[float,float,float]) -> 'Transform'
    """
    构造变换对象
    """
    pass

def GetAllPresets(dimension=-1):
    # type: (int) -> 'List[PresetBase]'
    """
    获取所有预设
    """
    pass

def GetBlockPresetByPosition(x, y, z, dimension=-1):
    # type: (int, int, int, int) -> 'BlockPreset'
    """
    获取指定位置的第一个方块预设
    """
    pass

def GetGameObjectByEntityId(entityId):
    # type: (str) -> 'TransformObject'
    """
    获取指定实体ID的游戏对象
    """
    pass

def GetGameObjectById(id):
    # type: (int) -> 'TransformObject'
    """
    获取指定对象ID的游戏对象
    """
    pass

def GetGameObjectByTypeName(classType, name=None, dimension=-1):
    # type: (str, str, int) -> 'TransformObject'
    """
    获取指定类型和名称的第一个游戏对象
    """
    pass

def GetGameObjectsByTypeName(classType, name=None, dimension=-1):
    # type: (str, str, int) -> 'List[TransformObject]'
    """
    获取指定类型和名称的所有游戏对象
    """
    pass

def GetPartApi():
    # type: () -> 'PartBase'
    """
    获取零件API
    """
    pass

def GetPresetByName(name, dimension=-1):
    # type: (str, int) -> 'PresetBase'
    """
    获取指定名称的第一个预设
    """
    pass

def GetPresetByType(classType, dimension=-1):
    # type: (str, int) -> 'PresetBase'
    """
    获取指定维度的指定类型的第一个预设
    """
    pass

def GetPresetSize(presetId):
    # type: (str) -> 'Tuple[float,float,float]'
    """
    根据预设ID获取预设的包围盒大小
    """
    pass

def GetPresetsByName(name, dimension=-1):
    # type: (str, int) -> 'List[PresetBase]'
    """
    获取指定名称的所有预设
    """
    pass

def GetPresetsByType(classType, dimension=-1):
    # type: (str, int) -> 'List[PresetBase]'
    """
    获取指定维度的指定类型的所有预设
    """
    pass

def GetTickCount():
    # type: () -> 'int'
    """
    获取当前帧数
    """
    pass

def LoadPartByModulePath(modulePath):
    # type: (str) -> 'PartBase'
    """
    通过模块相对路径加载零件并实例化
    """
    pass

def LoadPartByType(partType):
    # type: (str) -> 'PartBase'
    """
    通过类名加载零件并实例化
    """
    pass

def SpawnPreset(presetId, transform, dimension=0, virtual=True):
    # type: (str, Transform, int, bool) -> 'PresetBase'
    """
    在指定维度的指定坐标变换处生成指定预设
    """
    pass

