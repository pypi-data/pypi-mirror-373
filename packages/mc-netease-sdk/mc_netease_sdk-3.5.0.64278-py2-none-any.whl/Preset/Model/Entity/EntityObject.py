# -*- coding: utf-8 -*-

from Preset.Model.SdkInterface import SdkInterface
from typing import List
from typing import Any
from typing import Tuple

class EntityObject(SdkInterface):
    def __init__(self):
        # type: () -> 'None'
        """
        EntityObject（实体对象）是对实体对象封装的基类，它为实体提供了面向对象的使用方式。
        """
        pass

    def GetPos(self):
        # type: () -> 'Tuple[float,float,float]'
        """
        获取实体位置
        """
        pass

    def GetFootPos(self):
        # type: () -> 'Tuple[float,float,float]'
        """
        获取实体脚所在的位置
        """
        pass

    def SetPos(self, pos):
        # type: (Tuple[int,int,int]) -> 'bool'
        """
        设置实体位置
        """
        pass

    def SetFootPos(self, pos):
        # type: (Tuple[float,float,float]) -> 'bool'
        """
        设置实体脚底所在的位置
        """
        pass

    def GetRot(self):
        # type: () -> 'Tuple[float,float]'
        """
        获取实体角度
        """
        pass

    def SetRot(self, rot):
        # type: (Tuple[float,float]) -> 'bool'
        """
        设置实体的头的角度
        """
        pass

    def GetEngineTypeStr(self):
        # type: () -> 'str'
        """
        获取实体的类型名称
        """
        pass

    def GetEngineType(self):
        # type: () -> 'int'
        """
        获取实体类型
        """
        pass

    def GetModelId(self):
        # type: () -> 'int'
        """
        获取骨骼模型的Id，主要用于特效绑定骨骼模型
        """
        pass

    def PlayAnim(self, aniName, isLoop):
        # type: (str, bool) -> 'bool'
        """
        播放骨骼动画
        """
        pass

    def SetAnimSpeed(self, aniName, speed):
        # type: (str, float) -> 'bool'
        """
        设置某个骨骼动画的播放速度
        """
        pass

    def GetAnimLength(self, aniName):
        # type: (str) -> 'float'
        """
        获取某个骨骼动画的长度，单位为秒
        """
        pass

    def SetBrightness(self, brightness):
        # type: (float) -> 'bool'
        """
        设置实体的亮度
        """
        pass

    def SetOpacity(self, opacity):
        # type: (float) -> 'None'
        """
        设置生物模型的透明度
        """
        pass

    def GetHealth(self):
        # type: () -> 'float'
        """
        获取实体预设的生命值
        """
        pass

    def SetHealth(self, hp):
        # type: (float) -> 'None'
        """
        设置实体预设的生命值
        """
        pass

    def GetMaxHealth(self):
        # type: () -> 'float'
        """
        获取实体预设的最大生命值
        """
        pass

    def SetMaxHealth(self, hp):
        # type: (float) -> 'None'
        """
        设置实体预设的最大生命值
        """
        pass

    def GetSpeed(self):
        # type: () -> 'float'
        """
        获取实体预设的速度
        """
        pass

    def SetSpeed(self, speed):
        # type: (float) -> 'None'
        """
        设置实体预设的速度
        """
        pass

    def GetMaxSpeed(self):
        # type: () -> 'float'
        """
        获取实体预设的最大速度
        """
        pass

    def SetMaxSpeed(self, speed):
        # type: (float) -> 'None'
        """
        设置实体预设的最大速度
        """
        pass

    def GetDamage(self):
        # type: () -> 'float'
        """
        获取实体预设的伤害
        """
        pass

    def SetDamage(self, hp):
        # type: (float) -> 'None'
        """
        设置实体预设的伤害
        """
        pass

    def GetMaxDamage(self):
        # type: () -> 'float'
        """
        获取实体预设的最大伤害
        """
        pass

    def SetMaxDamage(self, damage):
        # type: (float) -> 'None'
        """
        设置实体预设的最大伤害
        """
        pass

    def ShowHealth(self, show):
        # type: (bool) -> 'None'
        """
        设置是否显示血条，默认为显示
        """
        pass

    def SetAttackTarget(self, targetId):
        # type: (str) -> 'bool'
        """
        设置仇恨目标
        """
        pass

    def ResetAttackTarget(self):
        # type: () -> 'bool'
        """
        清除仇恨目标
        """
        pass

    def GetAttackTarget(self):
        # type: () -> 'str'
        """
        获取仇恨目标
        """
        pass

    def SetKnockback(self, xd=0.1, zd=0.1, power=1.0, height=1.0, heightCap=1.0):
        # type: (float, float, float, float, float) -> 'None'
        """
        设置击退的初始速度，需要考虑阻力的影响
        """
        pass

    def SetOwner(self, ownerId):
        # type: (str) -> 'bool'
        """
        设置实体的属主
        """
        pass

    def GetOwner(self):
        # type: () -> 'str'
        """
        获取实体的属主
        """
        pass

    def IsOnFire(self):
        # type: () -> 'bool'
        """
        获取实体是否着火
        """
        pass

    def SetOnFire(self, seconds, burn_damage=1):
        # type: (int, int) -> 'bool'
        """
        设置实体着火
        """
        pass

    def GetAttrValue(self, attrType):
        # type: (int) -> 'float'
        """
        获取属性值，包括生命值，饥饿度，移速
        """
        pass

    def GetAttrMaxValue(self, attrType):
        # type: (int) -> 'float'
        """
        获取属性最大值，包括生命值，饥饿度，移速
        """
        pass

    def SetAttrValue(self, attrType, value):
        # type: (int, float) -> 'bool'
        """
        设置属性值，包括生命值，饥饿度，移速
        """
        pass

    def SetAttrMaxValue(self, attrType, value):
        # type: (int, float) -> 'bool'
        """
        设置属性最大值，包括生命值，饥饿度，移速
        """
        pass

    def IsInLava(self):
        # type: () -> 'bool'
        """
        实体是否在岩浆中
        """
        pass

    def IsOnGround(self):
        # type: () -> 'bool'
        """
        实体是否触地
        """
        pass

    def GetAuxValue(self):
        # type: () -> 'int'
        """
        获取射出的弓箭或投掷出的药水的附加值
        """
        pass

    def GetCurrentAirSupply(self):
        # type: () -> 'int'
        """
        生物当前氧气储备值
        """
        pass

    def GetMaxAirSupply(self):
        # type: () -> 'int'
        """
        获取生物最大氧气储备值
        """
        pass

    def SetCurrentAirSupply(self, data):
        # type: (int) -> 'bool'
        """
        设置生物氧气储备值
        """
        pass

    def SetMaxAirSupply(self, data):
        # type: (int) -> 'bool'
        """
        设置生物最大氧气储备值
        """
        pass

    def IsConsumingAirSupply(self):
        # type: () -> 'bool'
        """
        获取生物当前是否在消耗氧气
        """
        pass

    def SetRecoverTotalAirSupplyTime(self, timeSec):
        # type: (float) -> 'bool'
        """
        设置恢复最大氧气量的时间，单位秒
        """
        pass

    def GetSourceId(self):
        # type: () -> 'str'
        """
        获取抛射物发射者实体id
        """
        pass

    def SetCollisionBoxSize(self, size):
        # type: (Tuple[float,float]) -> 'bool'
        """
        设置实体的包围盒
        """
        pass

    def GetCollisionBoxSize(self):
        # type: () -> 'Tuple[float,float]'
        """
        获取实体的包围盒
        """
        pass

    def SetBlockControlAi(self, isBlock):
        # type: (bool) -> 'bool'
        """
        设置屏蔽生物原生AI
        """
        pass

    def GetDimensionId(self):
        # type: () -> 'int'
        """
        获取实体所在维度
        """
        pass

    def ChangeDimension(self, dimensionId, pos=None):
        # type: (int, Tuple[int,int,int]) -> 'bool'
        """
        传送实体
        """
        pass

    def RemoveEffect(self, effectName):
        # type: (str) -> 'bool'
        """
        为实体删除指定状态效果
        """
        pass

    def AddEffect(self, effectName, duration, amplifier, showParticles):
        # type: (str, int, int, bool) -> 'bool'
        """
        为实体添加指定状态效果，如果添加的状态已存在则有以下集中情况：1、等级大于已存在则更新状态等级及持续时间；2、状态等级相等且剩余时间duration大于已存在则刷新剩余时间；3、等级小于已存在则不做修改；4、粒子效果以新的为准
        """
        pass

    def GetEffects(self):
        # type: () -> 'List[dict]'
        """
        获取实体当前所有状态效果
        """
        pass

    def TriggerCustomEvent(self, entityId, eventName):
        # type: (str, str) -> 'bool'
        """
        触发生物自定义事件
        """
        pass

    def IsAlive(self):
        # type: () -> 'bool'
        """
        判断生物实体是否存活或非生物实体是否存在
        """
        pass

    def GetGravity(self):
        # type: () -> 'float'
        """
        获取实体的重力因子，当生物重力因子为0时则应用世界的重力因子
        """
        pass

    def SetGravity(self, gravity):
        # type: (float) -> 'bool'
        """
        设置实体的重力因子，当生物重力因子为0时则应用世界的重力因子
        """
        pass

    def SetHurt(self, damage, cause, attackerId=None, childAttackerId=None, knocked=True):
        # type: (float, str, str, str, bool) -> 'bool'
        """
        对实体造成伤害
        """
        pass

    def SetImmuneDamage(self, immune):
        # type: (bool) -> 'bool'
        """
        设置实体是否免疫伤害（该属性存档）
        """
        pass

    def SetModAttr(self, paramName, paramValue, needRestore=False):
        # type: (str, Any, bool) -> 'None'
        """
        设置属性值
        """
        pass

    def GetModAttr(self, paramName, defaultValue=None):
        # type: (str, Any) -> 'Any'
        """
        获取属性值
        """
        pass

    def RegisterModAttrUpdateFunc(self, paramName, func):
        # type: (str, function) -> 'None'
        """
        注册属性值变换时的回调函数，当属性变化时会调用该函数
        """
        pass

    def UnRegisterModAttrUpdateFunc(self, paramName, func):
        # type: (str, function) -> 'None'
        """
        反注册属性值变换时的回调函数
        """
        pass

    def GetName(self):
        # type: () -> 'str'
        """
        获取生物的自定义名称，即使用命名牌或者SetName接口设置的名称
        """
        pass

    def SetName(self, name):
        # type: (str) -> 'bool'
        """
        用于设置生物的自定义名称，跟原版命名牌作用相同，玩家和新版流浪商人暂不支持
        """
        pass

    def SetShowName(self, show):
        # type: (bool) -> 'bool'
        """
        设置生物名字是否按照默认游戏逻辑显示
        """
        pass

    def SetAlwaysShowName(self, show):
        # type: (bool) -> 'bool'
        """
        设置生物名字是否一直显示，瞄准点不指向生物时也能显示
        """
        pass

    def SetPersistence(self, isPersistent):
        # type: (bool) -> 'None'
        """
        设置实体是否存盘
        """
        pass

    def SetMotion(self, motion):
        # type: (Tuple[float,float,float]) -> 'bool'
        """
        设置生物的瞬时移动方向向量，服务端只能对非玩家使用，客户端只能对本地玩家使用
        """
        pass

    def GetMotion(self):
        # type: () -> 'Tuple[int,int,int]'
        """
        获取生物（含玩家）的瞬时移动方向向量
        """
        pass

    def SetItem(self, posType, itemDict, slotPos):
        # type: (int, dict, int) -> 'bool'
        """
        设置生物物品
        """
        pass

    def SetCanOtherPlayerRide(self, canRide):
        # type: (bool) -> 'bool'
        """
        设置其他玩家是否有权限骑乘
        """
        pass

    def SetControl(self, isControl):
        # type: (bool) -> 'bool'
        """
        设置该生物无需装备鞍就可以控制行走跳跃
        """
        pass

    def SetRidePos(self, pos):
        # type: (Tuple[float,float,float]) -> 'bool'
        """
        设置生物骑乘位置
        """
        pass

    def SetNotRender(self, notRender):
        # type: (bool) -> 'bool'
        """
        设置是否关闭实体渲染
        """
        pass

    def SetCollidable(self, isCollidable):
        # type: (bool) -> 'bool'
        """
        设置实体是否可碰撞
        """
        pass

    def SetHealthColor(self, front, back):
        # type: (Tuple[float,float,float,float], Tuple[float,float,float,float]) -> 'None'
        """
        设置血条的颜色及背景色, 必须用game组件设置ShowHealthBar时才能显示血条！！
        """
        pass

    def AddAnimation(self, animationKey, animationName):
        # type: (str, str) -> 'bool'
        """
        增加生物渲染动画
        """
        pass

    def AddAnimationController(self, animationControllerKey, animationControllerName):
        # type: (str, str) -> 'bool'
        """
        增加生物渲染动画控制器
        """
        pass

    def AddScriptAnimate(self, animateName, condition='', autoReplace=False):
        # type: (str, str, bool) -> 'bool'
        """
        在生物的客户端实体定义（minecraft:client_entity）json中的scripts/animate节点添加动画/动画控制器
        """
        pass

    def AddParticleEffect(self, effectKey, effectName):
        # type: (str, str) -> 'bool'
        """
        增加生物特效资源
        """
        pass

    def AddRenderController(self, renderControllerName, condition):
        # type: (str, str) -> 'bool'
        """
        增加生物渲染控制器
        """
        pass

    def AddRenderMaterial(self, materialKey, materialName):
        # type: (str, str) -> 'bool'
        """
        增加生物渲染需要的材质,调用该接口后需要调用RebuildActorRender才会生效
        """
        pass

    def AddSoundEffect(self, soundKey, soundName):
        # type: (str, str) -> 'bool'
        """
        增加生物音效资源
        """
        pass

    def SetPushable(self, isPushable):
        # type: (bool) -> 'bool'
        """
        设置实体是否可推动
        """
        pass

    def SetModel(self, modelName):
        # type: (str) -> 'bool'
        """
        设置骨骼模型
        """
        pass

    def GetLavaSpeed(self):
        # type: () -> 'float'
        """
        获取实体预设岩浆里的移速
        """
        pass

    def SetLavaSpeed(self, value):
        # type: (float) -> 'None'
        """
        设置实体预设岩浆里的移速
        """
        pass

    def GetMaxLavaSpeed(self):
        # type: () -> 'float'
        """
        获取实体预设岩浆里的最大移速
        """
        pass

    def SetMaxLavaSpeed(self, value):
        # type: (float) -> 'None'
        """
        设置实体预设岩浆里的最大移速
        """
        pass

