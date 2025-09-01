# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.TypeMeta import PArray, PRelativeCoordinate, PBool, PFButton, PObjectArray, PVector2TF, PInt, PDict, PVector2WB
from Preset.Model import PartBaseMeta


@sunshine_class_meta
class CameraTrackPartMeta(PartBaseMeta):
    CLASS_NAME = "CameraTrackPart"
    PROPERTIES = {
        "preview": PBool(sort=6, text="预览路径", group='相机轨迹'),
        "play": PBool(sort=7, text="播放", group='相机轨迹'),
        "track": PArray(sort=8, text='轨迹', group='相机轨迹', childAttribute=PDict(
            sort=1, text='绑定事件', children={
                "offset": PRelativeCoordinate(sort=0, text="偏移"),
                "rotation": PVector2WB(sort=1, text="旋转", step=0.01, min=-3.14, max=3.14, precision=2),
                "clockwiseX": PBool(sort=2, text="Pitch顺向", default=True,  tips="用于调整绕俯仰角顺逆，一般不用改变"),
                "clockwiseY": PBool(sort=3, text="Yaw顺向", default=True, tips="用于调整绕偏航角顺逆，用于调整方向问题"),
                "time": PInt(sort=4, text="时间帧数", default=20),
                }
        ))}




from Preset.Model.PartBase import PartBase

class CameraTrackPart(PartBase):
    def __init__(self):
        # type: () -> 'None'
        """
        相机轨迹零件
        """
        self.track = None

    def PlayFromStart(self):
        # type: () -> 'None'
        """
        从头开始播放相机运动轨迹
        """
        pass

    def Pause(self):
        # type: () -> 'None'
        """
        暂停播放相机轨迹
        """
        pass

    def Continue(self):
        # type: () -> 'None'
        """
        继续播放相机轨迹
        """
        pass

    def Stop(self):
        # type: () -> 'None'
        """
        停止播放相机轨迹
        """
        pass

