# -*- coding: utf-8 -*-
from typing import Type


def sunshine_class_meta(cls):
	# type: (Type) -> Type
	"""
	使用此装饰器装饰Meta类，
	例如：
	@sunshine_class_meta
	class MyMeta(ClassMeta):
		pass
	"""
	return cls




