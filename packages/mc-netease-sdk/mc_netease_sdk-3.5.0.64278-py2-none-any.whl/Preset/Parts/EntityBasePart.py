# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.EnumMeta import DefEnum
from Meta.TypeMeta import PBool, PStr, PInt, PCustom, PVector3, PVector3TF, PEnum, PDict, PFloat, PArray, PVector2
from MC.World.EntityManager import EntityManager
from Preset.Parts.UseConfigPartBase import UseConfigPartBaseMeta


@sunshine_class_meta
class EntityBasePartMeta(UseConfigPartBaseMeta):
    CLASS_NAME = "EntityBasePart"
    PROPERTIES = {
        "engineType": PCustom(sort=101, group="实体", text="实体类型", editAttribute="MCEnum", customFunc=lambda _: EntityManager.getCreatureEnum()),
    }



class EntityBasePart(UseConfigPartBase):
    def __init__(self):
        # type: () -> 'None'
        """
        实体零件
        """
        self.engineType = None
        self.autoCreate = None
        self.persistence = None

    def CreateVirtualEntity(self):
        # type: () -> 'str'
        """
        手动创建关联实体，如果已创建会直接返回
        """
        pass

    def DestroyVirtualEntity(self):
        # type: () -> 'None'
        """
        移除已创建的关联实体，引擎退出时会默认调用
        """
        pass

