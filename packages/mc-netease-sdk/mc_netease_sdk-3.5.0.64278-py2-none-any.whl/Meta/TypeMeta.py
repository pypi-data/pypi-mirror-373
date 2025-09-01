# -*- coding: utf-8 -*-
from typing import Dict, Callable, Any, Optional, List


class ClassMeta(object):
	"""
	CLASS_NAME：对应的数据类名
	PROPERTIES：显示结构的Meta定义，如：PROPERTIES={"key1": PStr()}
	"""
	CLASS_NAME = ""
	PROPERTIES = {}


class TypeMeta(object):
	CLASS_NAME = ""  # type: str
	PROPERTIES = {}  # type: Dict[str, Any]


class PInt(TypeMeta):
	def __init__(self, sort=0, text="", default=0, editable=True, visible=True, func=None, tip="", group=None, min=None, max=None, step=1):
		# type: (int, str, int, bool, bool, Callable[[int], Dict[str, Any]], str, str, Optional[int], Optional[int], int) -> None
		"""
		int类型
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value!=0}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param min: 最小值
		:param max: 最大值
		:param step: 步进量
		"""
		pass


class PFloat(TypeMeta):
	def __init__(self, sort=0, text="", default=0.0, editable=True, visible=True, func=None, tip="", group=None, min=None, max=None, step=1.0, precision=2):
		# type: (int, str, float, bool, bool, Callable[[float], Dict[str, Any]], str, str, Optional[int], Optional[int], float, int) -> None
		"""
		float类型
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value>0}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param min: 最小值
		:param max: 最大值
		:param step: 步进量
		:param precision: 小数点后位数
		"""
		pass


class PBool(TypeMeta):
	def __init__(self, sort=0, text="", default=False, editable=True, visible=True, func=None, tip="", group=None):
		# type: (int, str, bool, bool, bool, Callable[[bool], Dict[str, Any]], str, str) -> None
		"""
		bool类型
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		"""
		pass


class PStr(TypeMeta):
	def __init__(self, sort=0, text="", default="", editable=True, visible=True, func=None, tip="", group=None, regex=None):
		# type: (int, str, str, bool, bool, Callable[[str], Dict[str, Any]], str, str, str) -> None
		"""
		str类型
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value!=""}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param regex: 内容需要符合的正则表达式
		"""
		pass


class PEnum(TypeMeta):
	def __init__(self, sort=0, text="", default=None, editable=True, visible=True, func=None, tip="", group=None, enumType="", searchable=False):
		# type: (int, str, Any, bool, bool, Callable[[Any], Dict[str, Any]], str, str, str) -> None
		"""
		下拉框式
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value is not None}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param enumType: 使用DefEnum定义的枚举类型数据名称，如DefEnum("MyEnum", {1: "a", 2: "b"})，这里就填"MyEnum"
		:param searchable: 是否使用快速搜索
		"""
		pass


class PVector2(TypeMeta):
	def __init__(self, sort=0, text="", default=None, editable=True, visible=True, func=None, tip="", group=None, min=None, max=None, step=1.0, precision=2):
		# type: (int, str, List[float], bool, bool, Callable[[float], Dict[str, Any]], str, str, Optional[int], Optional[int], float, int) -> None
		"""
		两个float的组合
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value is not None}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param min: 最小值
		:param max: 最大值
		:param step: 步进量，
		:param precision: 小数点后位数
		"""
		pass


class PVector2TF(TypeMeta):
	def __init__(self, sort=0, text="", default=None, editable=True, visible=True, func=None, tip="", group=None, min=None, max=None, step=1.0, precision=2):
		# type: (int, str, List[float], bool, bool, Callable[[float], Dict[str, Any]], str, str, Optional[int], Optional[int], float, int) -> None
		"""
		两个float的组合，这种样式会隐藏x,y的文本
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value is not None}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param min: 最小值
		:param max: 最大值
		:param step: 步进量
		:param precision: 小数点后位数
		"""
		pass


class PVector3(TypeMeta):
	def __init__(self, sort=0, text="", default=None, editable=True, visible=True, func=None, tip="", group=None, min=None, max=None, step=1.0, precision=2):
		# type: (int, str, List[float], bool, bool, Callable[[float], Dict[str, Any]], str, str, Optional[int], Optional[int], float, int) -> None
		"""
		三个float的组合
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value is not None}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param min: 最小值
		:param max: 最大值
		:param step: 步进量，
		:param precision: 小数点后位数
		"""
		pass

class PCoordinate(PVector3):
	pass

class PVector3TF(TypeMeta):
	def __init__(self, sort=0, text="", default=None, editable=True, visible=True, func=None, tip="", group=None, min=None, max=None, step=1.0, precision=2):
		# type: (int, str, List[float], bool, bool, Callable[[float], Dict[str, Any]], str, str, Optional[int], Optional[int], float, int) -> None
		"""
		三个float的组合。这种样式会隐藏x,y,z的文本
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value is not None}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param min: 最小值
		:param max: 最大值
		:param step: 步进量，
		:param precision: 小数点后位数
		"""
		pass


class PVector4(TypeMeta):
	def __init__(self, sort=0, text="", default=None, editable=True, visible=True, func=None, tip="", group=None, min=None, max=None, step=1.0, precision=2):
		# type: (int, str, List[float], bool, bool, Callable[[float], Dict[str, Any]], str, str, Optional[int], Optional[int], float, int) -> None
		"""
		四个float的组合
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value is not None}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param min: 最小值
		:param max: 最大值
		:param step: 步进量，
		:param precision: 小数点后位数
		"""
		pass


class PColor(TypeMeta):
	def __init__(self, sort=0, text="", default=None, editable=True, visible=True, func=None, tip="", group=None, format=""):
		# type: (int, str, str, bool, bool, Callable[[float], Dict[str, Any]], str, str, str) -> None
		"""
		颜色选取器
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value is not None}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param format: 颜色格式。format取默认值""时，会使用默认格式[r, g, b]如：[244, 37, 18]，仅额外支持format="#RRGGBB"，此时，实际值形如："#A6B7C8"
		"""
		pass


class PArray(TypeMeta):
	def __init__(self, sort=0, text="", default=[], editable=True, visible=True, func=None, tip="", group=None, childAttribute=None, maxSize=9999):
		# type: (int, str, List[Any], bool, bool, Callable[[float], Dict[str, Any]], str, str, TypeMeta, int) -> None
		"""
		数组类型
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": len(value) > 0}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param childAttribute: 子元素的Meta定义，如：childAttribute=PStr()
		:param maxSize: 最大长度
		"""
		pass


class PFixArray(TypeMeta):
	def __init__(self, sort=0, text="", default=[], editable=True, visible=True, func=None, tip="", group=None, childAttribute=None, size=1):
		# type: (int, str, List[Any], bool, bool, Callable[[float], Dict[str, Any]], str, str, TypeMeta, int) -> None
		"""
		数组类型，只支持固定长度的数组
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"editable": value[0]!=0}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param childAttribute: 子元素的Meta定义，如：childAttribute=PStr()
		:param size: 固定长度值
		"""
		pass


class PDict(TypeMeta):
	def __init__(self, sort=0, text="", default={}, editable=True, visible=True, func=None, tip="", group=None, children=None, addable=False, removable=False):
		# type: (int, str, Dict[str, Any], bool, bool, Callable[[float], Dict[str, Any]], str, str, Dict[str, TypeMeta], bool, bool) -> None
		"""
		字典类型
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": len(value) > 0}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param children: 子元素的Meta定义，如：children={"key1": PStr(), "key2": PInt()}
		:param addable: 允许动态增加子元素，该子元素的key需要存在于此Meta定义中。
		:param removable: 允许动态删除已存在的子元素，
		"""
		pass


class PCustom(TypeMeta):
	def __init__(self, sort=0, text="", default=None, editable=True, visible=True, func=None, tip="", group=None, editAttribute="", extend=None, **kwargs):
		# type: (int, str, Any, bool, bool, Callable[[float], Dict[str, Any]], str, str, str, Callable[[Any], Dict[str, Any]], Any) -> None
		"""
		自定义类型
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value is not None}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param editAttribute: 自定义UI控件的名称
		:param extend: 当editAttribute为MCEnum动态枚举时，动态扩展枚举的方法，返回值为扩展枚举的字典，key为值，value为下拉菜单显示内容
		:param kwargs: 自定义UI控件所需要的额外参数
		"""


class PObjectArray(TypeMeta):
	def __init__(self, sort=0, text="", default=None, editable=True, visible=True, func=None, tip="", group=None, itemCreator=""):
		# type: (int, str, Any, bool, bool, Callable[[float], Dict[str, Any]], str, str, PropertyListObject) -> None
		"""
		自定义类型
		:param sort: 排列顺序
		:param text: 标题文本
		:param default: 默认值
		:param editable: 是否可编辑
		:param visible: 是否可见
		:param func: 更新时自动调用的函数，可用于动态更新参数。如：func=lambda value: {"visible": value is not None}，其中value为实际值、
		:param tip: 提示文字，鼠标悬浮时显示
		:param group: 分组名名称，属性面板将按此名称进行分组。注意：仅支持第一级结点分组。
		:param itemCreator: 继承于PropertyListObject的自定义类
		"""

class PGameObjectArea(PDict):
	"""
	区域选定组件
	children字段必须为：
		{
			'min': PVector3(sort=0, text="顶点1"),
			'max': PVector3(sort=1, text="顶点2"),
			'dimensionId': PInt(sort=2, text="维度")
		}
	"""
	pass