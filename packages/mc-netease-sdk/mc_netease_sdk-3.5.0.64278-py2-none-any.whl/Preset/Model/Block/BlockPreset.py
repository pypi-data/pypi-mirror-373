# -*- coding: utf-8 -*-

from Preset.Model.PresetBase import PresetBase

class BlockPreset(PresetBase):
    def __init__(self):
        # type: () -> 'None'
        """
        BlockPreset（方块预设）是一类绑定方块的预设。由于MC的方块数量巨大，将方块预设与MC的原生方块绑定，尤其是地图中常见的原生方块可能对性能造成重大影响。
        """
        self.engineTypeStr = None
        self.blockId = None
        self.auxValue = None

    def GetEngineTypeStr(self):
        # type: () -> 'str'
        """
        获取方块预设的方块类型ID
        """
        pass

