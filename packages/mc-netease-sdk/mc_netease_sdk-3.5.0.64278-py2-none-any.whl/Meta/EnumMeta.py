# -*- coding: utf-8 -*-
from typing import Dict, Any


class DefEnum(object):
	def __init__(self, name, valueDict):
		# type: (str, Dict[Any, str]) -> None
		"""
		使用此类定义需要的枚举类型数据。例如：
		DefEnum("MyEnum", {1: "a", 2: "b"})
		:param name: 枚举数据名称
		:param valueDict: 枚举数据，key会作为该选项的实际值，value会作为显示文本
		"""
		pass


