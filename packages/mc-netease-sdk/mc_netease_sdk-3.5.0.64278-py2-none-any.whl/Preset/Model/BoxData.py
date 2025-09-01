# -*- coding: utf-8 -*-

from Preset.Model.TransformObject import TransformObject

class BoxData(TransformObject):
    def __init__(self, filePath=None):
        # type: (str) -> 'None'
        """
        BoxData（素材数据）与素材类似，可以挂接在预设下使用。BoxData在编辑器中不会实际生成，可以重叠放置。
        """
        self.filePath = None

