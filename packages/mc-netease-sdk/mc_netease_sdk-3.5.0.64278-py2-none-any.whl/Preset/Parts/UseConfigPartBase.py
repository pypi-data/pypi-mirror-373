# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Preset.Model import PartBaseMeta
from Preset.Model.PartBase import PartBase


class UseConfigPartBase(PartBase):
    pass


@sunshine_class_meta
class UseConfigPartBaseMeta(PartBaseMeta):
    CLASS_NAME = "UseConfigPartBase"
    PROPERTIES = {
    }
