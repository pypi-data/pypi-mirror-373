# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.EnumMeta import DefEnum
from Meta.TypeMeta import PInt, PCustom, PEnum
from Preset.Model import PartBaseMeta


@sunshine_class_meta
class PortalPartMeta(PartBaseMeta):
    CLASS_NAME = "PortalPart"
    PROPERTIES = {
        "portalGateType": PEnum(sort=101, text="类型", enumType="PortalGateTypeEnum", default=0, tip='单向传送门：在任意维度均可激活该传送门，不会在传送后在目标维度生成返回的传送门。\n双向传送门：只能在后面配置的“传送门方块”和“反向传送门方块”中的维度被激活。会自动在传送后的维度生成对应的反向传送门。'),
        "portalGateShape": PEnum(sort=102, text="形状", enumType="PortalGateShapeEnum", default=0, tip='目前只能选择立式方框。\n立式方框：类似下界传送门的形状，垂直于地面的矩形边框。'),
        "portalGateWidth": PInt(sort=103, text="宽", min=4, tip='传送门的总体宽度，单位为格子。'),
        "portalGateHeight": PInt(sort=104, text="高", min=5, tip='传送门的总体高度，单位为格子。'),
        "gate": PCustom(sort=105, text="边框方块", editAttribute="MCBlockNameWithAux", tip='传送门边框的方块类型。'),
        "portal": PCustom(sort=106, text="传送门方块", editAttribute="MCEnum", tip='传送门被激活时，方框内填充的传送门方块，需先在配置中添加好传送门方块。'),
        "reverse": PCustom(sort=107, text="反向传送门方块", func=lambda obj: {'visible': bool(obj.portalGateType)}, editAttribute="MCEnum", customFunc=_propertyPortal, tip='传送门被激活时，方框内填充的传送门方块类型。具体被“传送门方块”还是“反向传送门方块”填充，由当前传送门所在的维度决定。'),
        "key": PCustom(
            sort=108, text="激活物品",
            editAttribute='MCItems',
            default=('minecraft:diamond_sword', 0),
            withNamespace=True,
            tip='对传送门边框使用激活物品，即可激活传送门。注意如果是双向传送门，在传送门方块维度之外的维度无法被激活。'
        )
    }

    @staticmethod
    def registerEnum():
        DefEnum(
            "PortalGateShapeEnum", {
                0: "立式方块"
            }
        )
        DefEnum(
            "PortalGateTypeEnum", {
                0: "单向传送门",
                1: "双向传送门"
            }
        )

from Preset.Model.PartBase import PartBase

class PortalPart(PartBase):
    def __init__(self):
        # type: () -> 'None'
        """
        传送门零件
        """
        self.portalGateType = None
        self.portalGateShape = None
        self.portalGateWidth = None
        self.portalGateHeight = None

