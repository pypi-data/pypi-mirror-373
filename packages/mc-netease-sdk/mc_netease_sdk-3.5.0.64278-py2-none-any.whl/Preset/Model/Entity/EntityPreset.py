# -*- coding: utf-8 -*-

from Preset.Model.PresetBase import PresetBase
from Preset.Model.Entity.EntityObject import EntityObject

class EntityPreset(PresetBase, EntityObject):
    def __init__(self):
        # type: () -> 'None'
        """
        EntityPreset（实体预设）是一类特殊的预设，实体预设通常会绑定MC的某类实体，实体预设实例与MC的某一个实体绑定，因此可以使用实体预设来进行一些实体相关的逻辑的编程。如果玩家同时启用了多个AddOn，且这些AddOn中均包含与同一种MC原版实体绑定的实体预设，那么只会加载第一个这种实体预设。
        """
        self.engineTypeStr = None
        self.entityId = None
        self.updateTransformInterval = None

