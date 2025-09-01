# -*- coding: utf-8 -*-

from mod.client.ui.screenNode import ScreenNode
from Preset.Model.PresetBase import PresetBase

class UIPreset(PresetBase):
    def __init__(self):
        # type: () -> 'None'
        """
        UIPreset（界面预设）是一类绑定界面资源的预设。
        """
        self.uiNodeScreen = None
        self.uiNodeModulePath = None
        self.uiNodeModule = None
        self.uiName = None
        self.autoCreate = None
        self.isHud = None
        self.createUIMethod = None
        self.isBindParent = None
        self.bindParentOffset = None
        self.bindParentAutoScale = None
        self.showInEditor = None

    def SetUiActive(self, active):
        # type: (bool) -> 'None'
        """
        设置UI激活
        """
        pass

    def GetUiActive(self):
        # type: () -> 'bool'
        """
        获取当前UI是否激活
        """
        pass

    def SetUiVisible(self, visible):
        # type: (bool) -> 'None'
        """
        设置UI显隐
        """
        pass

    def GetUiVisible(self):
        # type: () -> 'bool'
        """
        获取当前UI是否显示
        """
        pass

    def GetScreenNode(self):
        # type: () -> 'ScreenNode'
        """
        获取当前ScreenNode实例
        """
        pass

