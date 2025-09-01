# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.TypeMeta import PBool, PStr, PInt, PCustom, PVector3, PVector3TF, PEnum, PDict, PFloat, PArray, PVector2, PGameObjectArea
from Preset.Model import PartBaseMeta


def _getSupportType():
    return {1: '仅客户端支持', 2: '仅服务端支持', 3: '双端支持'}


@sunshine_class_meta
class TriggerPartMeta(PartBaseMeta):
    CLASS_NAME = "TriggerPart"
    PROPERTIES = {
        "area": PGameObjectArea(
            sort=1002,
            text="区域", tip='trigger零件所造的区域。',
            children={
                'min': PVector3(sort=0, text="顶点1"),
                'max': PVector3(sort=1, text="顶点2"),
                'dimensionId': PInt(sort=2, text="维度")
            },
        ),
        "isTriggerEnter": PBool(
            sort=1003,
            group="监听",
            text="是否监听实体进入",
            tip="若监听实体进入，则实体进入时会触发OnTriggerEntityEnter事件",
        ),
        "isTriggerExit": PBool(
            sort=1004,
            group="监听",
            text="是否监听实体离开",
            tip="若监听实体离开，则实体离开时会触发OnTriggerEntityExit事件",
        ),

        "isTriggerStay": PBool(
            sort=1005,
            group="监听",
            text="是否监听实体停留",
            tip="若监听实体停留，当则当区域内存在实体时，每次检测会触发OnTriggerEntityStay事件",
        ),
        "intervalTick": PInt(
            sort=1006,
            group="监听",
            text="监听间隔（单位：帧）",
            tip="每隔一定帧数，进行一次检测",
        ),
        "support": PEnum(
            text='支持端',
            group="监听",
            sort=1007,
            func=lambda obj: {'enumData': _getSupportType()},
            tip='选择支持的端，选择合适的端有助于提升性能'),
    }


from Preset.Model.PartBase import PartBase

class TriggerPart(PartBase):
    def __init__(self):
        # type: () -> 'None'
        """
        触发器零件，当实体进入时触发OnTriggerEntityEnter，当实体退出时触发OnTriggerEntityExit，当实体停留时触发OnTriggerEntityStay
        """
        self.isTriggerEnter = None
        self.isTriggerExit = None
        self.isTriggerStay = None
        self.support = None

    def GetEntitiesInTrigger(self):
        # type: () -> 'None'
        """
        获取当前在触发器区域的实体列表
        """
        pass

