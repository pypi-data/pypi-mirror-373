# -*- coding: utf-8 -*-

from Preset.Model.PresetBase import PresetBase
from Preset.Model.Effect.EffectObject import EffectObject

class EffectPreset(PresetBase, EffectObject):
    def __init__(self):
        # type: () -> 'None'
        """
        EffectPreset（特效预设）是一类绑定特效资源的预设。
        """
        self.resource = None
        self.effectType = None
        self.effectId = None
        self.auto = None

    def GetResource(self):
        # type: () -> 'str'
        """
        获取绑定的json资源
        """
        pass

    def SetResource(self, resource):
        # type: (str) -> 'None'
        """
        设置绑定的json资源
        """
        pass

