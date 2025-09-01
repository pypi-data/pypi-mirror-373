# -*- coding: utf-8 -*-

ClassTypeDict = {}

def registerGenericClass(genericType):
	def wrapper(cls):
		classType = genericType or cls.__class__.__name__
		ClassTypeDict[classType] = cls
		return cls

	return wrapper



from typing import Union
from Preset.Model.GameObject import GameObject

class GameObject():
    def __init__(self):
        # type: () -> 'None'
        """
        GameObject（游戏对象）是所有预设对象的基类，即API文档中Preset API - 预设对象下的所有类都继承自GameObject。
        """
        self.id = None
        self.classType = None
        self.isClient = None

    def LoadFile(self, path):
        # type: (str) -> 'str'
        """
        加载指定路径的非python脚本文件内容，如配置文件
        """
        pass

    def fromDict(self, data):
        # type: (dict) -> 'Union[GameObject,dict]'
        """
        将字典根据classType字段转换为对应类型的对象，该类型必须使用@registerGenericClass装饰
        """
        pass

