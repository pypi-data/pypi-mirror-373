# -*- coding: utf-8 -*-

from Preset.Model.SdkInterface import SdkInterface
from typing import Tuple

class EffectObject(SdkInterface):
    def __init__(self):
        # type: () -> 'None'
        """
        EffectObject（特效对象）是对特效对象封装的基类，它为特效提供了面向对象的使用方式。
        """
        self.effectId = None
        self.effectType = None

    def Play(self):
        # type: () -> 'None'
        """
        播放特效，仅客户端有效
        """
        pass

    def Stop(self):
        # type: () -> 'None'
        """
        停止播放特效，仅客户端有效
        """
        pass

    def BindToEntity(self, bindEntityId, offset=(0, 0, 0), rot=(0, 0, 0)):
        # type: (str, Tuple[float,float,float], Tuple[float,float,float]) -> 'bool'
        """
        绑定到实体
        """
        pass

    def BindToSkeleton(self, modelId, boneName, offset, rot):
        # type: (int, str, Tuple[float,float,float], Tuple[float,float,float]) -> 'bool'
        """
        绑定骨骼模型
        """
        pass

    def SetLoop(self, loop):
        # type: (bool) -> 'bool'
        """
        设置特效是否循环播放，默认为否，仅对序列帧有效
        """
        pass

    def SetDeepTest(self, deepTest):
        # type: (bool) -> 'bool'
        """
        设置序列帧是否透视，默认为否
        """
        pass

    def SetFaceCamera(self, face):
        # type: (bool) -> 'bool'
        """
        设置序列帧是否始终朝向摄像机，默认为是
        """
        pass

