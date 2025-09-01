# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.EnumMeta import DefEnum
from Meta.TypeMeta import PBool, PStr, PInt, PCustom, PVector3, PVector3TF, PEnum, PDict, PFloat, PArray, PVector2, PCoordinate
from Preset.Model import PartBaseMeta


@sunshine_class_meta
class PlayerBasicPartMeta(PartBaseMeta):
    CLASS_NAME = "PlayerBasicPart"
    PROPERTIES = {
        'attackDamage': PFloat(sort=1000, text='攻击力', group='基本属性', tip="玩家的最小攻击伤害为2，设置值小于2时可能不生效。"),
        'healthMax': PFloat(sort=1001, text='生命上限', group='基本属性', min=1),
        'disableHunger': PBool(sort=1002, text='是否锁定饥饿值', group='基本属性', tip='若勾选，则玩家的饥饿值不会变化'),
        'spawnPos': PCoordinate(sort=1003, text='玩家复活点', group='基本属性'),
        'nameDeeptest': PBool(sort=1004, text='名字是否透视', group='基本属性', tip='若勾选，则即使透过遮挡，也能够看到其他玩家的名字。'),
        'showName': PBool(sort=1005, text='是否在头顶显示名字', group='基本属性'),
        'storyline': PCustom(
            sort=1006, text='逻辑文件', group='基本属性', editAttribute='ETSWidget', tip='可挂接通过逻辑编辑器制作的ets文件，可实现一些简单的逻辑。',
            pack="behavior", baseFolder=["storyline"], extension=".ets", withExtension=True, description="ets"
        )
    }


from Preset.Model.PartBase import PartBase

class PlayerBasicPart(PartBase):
    def __init__(self):
        # type: () -> 'None'
        """
        玩家基础属性零件
        """
        self.attackDamage = None
        self.healthMax = None
        self.disableHunger = None
        self.spawnPos = None
        self.nameDeeptest = None
        self.showName = None

