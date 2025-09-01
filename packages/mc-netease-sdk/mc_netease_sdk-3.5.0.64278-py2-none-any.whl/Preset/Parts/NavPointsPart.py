# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.TypeMeta import PArray, PRelativeCoordinate, PBool, PDict, PFloat
from Preset.Model import PartBaseMeta


@sunshine_class_meta
class NavPointsPartMeta(PartBaseMeta):
    CLASS_NAME = "NavPointsPart"
    PROPERTIES = {
        "preview": PBool(sort=6, text="预览路径", group='巡逻路径'),
        'patrolsPath': PArray(sort=7, text="路径", group='巡逻路径', childAttribute=PDict(
            sort=1, text='路径点', children={
                "point": PRelativeCoordinate(text="位置", tip="如果和前一点的距离大于 50, 巡逻可能失败"),
                "radius": PFloat(text="随机半径", default=0, min=0),
            }))
    }


from Preset.Model.PartBase import PartBase
from typing import List
from typing import Tuple

class NavPointsPart(PartBase):
    def __init__(self):
        # type: () -> 'None'
        """
        导航路径零件, 在编辑器内可以选定一系列相对于该零件的坐标点，当零件运行时可以获得这些坐标点的世界坐标列表
        """
        self.patrolsPath = None

    def GetNavigationPoints(self):
        # type: () -> 'List[Tuple[float,float,float]]'
        """
        获得路径点的世界坐标列表
        """
        pass

    def GetNavigationRadius(self):
        # type: () -> 'List[float]'
        """
        获得路径点的随机半径列表
        """
        pass

