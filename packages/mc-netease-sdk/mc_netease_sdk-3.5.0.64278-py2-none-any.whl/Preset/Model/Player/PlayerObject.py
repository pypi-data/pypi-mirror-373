# -*- coding: utf-8 -*-

from Preset.Model.Entity.EntityObject import EntityObject
from typing import Tuple

class PlayerObject(EntityObject):
    def __init__(self):
        # type: () -> 'None'
        """
        PlayerObject（玩家对象）是对玩家对象封装的基类，它为实体提供了面向对象的使用方式。
        """
        pass

    def GetPlayerId(self):
        # type: () -> 'str'
        """
        获取玩家预设的玩家ID
        """
        pass

    def IsLocalPlayer(self):
        # type: () -> 'bool'
        """
        判断当前玩家对象是否本地玩家
        """
        pass

    def IsSneaking(self):
        # type: () -> 'bool'
        """
        是否潜行
        """
        pass

    def GetHunger(self):
        # type: () -> 'float'
        """
        获取玩家饥饿度，展示在UI饥饿度进度条上，初始值为20，即每一个鸡腿代表2个饥饿度。 **饱和度(saturation)** ：玩家当前饱和度，初始值为5，最大值始终为玩家当前饥饿度(hunger)，该值直接影响玩家**饥饿度(hunger)**。<br>1）增加方法：吃食物。<br>2）减少方法：每触发一次**消耗事件**，该值减少1，如果该值不大于0，直接把玩家 **饥饿度(hunger)** 减少1。
        """
        pass

    def SetHunger(self, value):
        # type: (float) -> 'bool'
        """
        设置玩家饥饿度。
        """
        pass

    def SetStepHeight(self, stepHeight):
        # type: (float) -> 'bool'
        """
        设置玩家前进非跳跃状态下能上的最大台阶高度, 默认值为0.5625，1的话表示能上一个台阶
        """
        pass

    def GetStepHeight(self):
        # type: () -> 'float'
        """
        返回玩家前进非跳跃状态下能上的最大台阶高度
        """
        pass

    def ResetStepHeight(self):
        # type: () -> 'bool'
        """
        恢复引擎默认玩家前进非跳跃状态下能上的最大台阶高度
        """
        pass

    def GetExp(self, isPercent=True):
        # type: (bool) -> 'float'
        """
        获取玩家当前等级下的经验值
        """
        pass

    def AddExp(self, exp):
        # type: (int) -> 'bool'
        """
        增加玩家经验值
        """
        pass

    def GetTotalExp(self):
        # type: () -> 'int'
        """
        获取玩家的总经验值
        """
        pass

    def SetTotalExp(self, exp):
        # type: (int) -> 'bool'
        """
        设置玩家的总经验值
        """
        pass

    def IsFlying(self):
        # type: () -> 'bool'
        """
        获取玩家是否在飞行
        """
        pass

    def ChangeFlyState(self, isFly):
        # type: (bool) -> 'bool'
        """
        给予/取消飞行能力，并且进入飞行/非飞行状态
        """
        pass

    def GetLevel(self):
        # type: () -> 'int'
        """
        获取玩家等级
        """
        pass

    def AddLevel(self, level):
        # type: (int) -> 'bool'
        """
        修改玩家等级
        """
        pass

    def SetPrefixAndSuffixName(self, prefix, prefixColor, suffix, suffixColor):
        # type: (str, str, str, str) -> 'bool'
        """
        设置玩家前缀和后缀名字
        """
        pass

    def EnableKeepInventory(self, enable):
        # type: (bool) -> 'bool'
        """
        设置玩家死亡不掉落物品
        """
        pass

    def AddAnimation(self, animationKey, animationName):
        # type: (str, str) -> 'bool'
        """
        增加玩家渲染动画
        """
        pass

    def SetHealthLevel(self, healthLevel):
        # type: (int) -> 'bool'
        """
        设置玩家健康临界值，当饥饿值大于等于健康临界值时会自动恢复血量，开启饥饿值且开启自然恢复时有效.原版默认值为18
        """
        pass

    def SetStarveLevel(self, starveLevel):
        # type: (int) -> 'bool'
        """
        设置玩家饥饿临界值，当饥饿值小于饥饿临界值时会自动扣除血量，开启饥饿值且开启饥饿掉血时有效。原版默认值为1
        """
        pass

    def SetNaturalStarve(self, value):
        # type: (bool) -> 'bool'
        """
        设置是否开启玩家饥饿掉血，当饥饿值小于饥饿临界值时会自动扣除血量，开启饥饿值且开启饥饿掉血时有效.原版默认开启
        """
        pass

    def SetStarveTick(self, starveTick):
        # type: (int) -> 'bool'
        """
        设置玩家饥饿掉血速度，当饥饿值小于饥饿临界值时会自动扣除血量，开启饥饿值且开启饥饿掉血时有效
        """
        pass

    def SetNaturalRegen(self, value):
        # type: (bool) -> 'bool'
        """
        设置是否开启玩家自然恢复
        """
        pass

    def SetHealthTick(self, healthTick):
        # type: (int) -> 'bool'
        """
        设置玩家自然恢复速度
        """
        pass

    def SetMaxExhaustionValue(self, value):
        # type: (float) -> 'bool'
        """
        设置玩家最大消耗度(maxExhaustion)
        """
        pass

    def SetPickUpArea(self, area):
        # type: (Tuple[float,float,float]) -> 'bool'
        """
        设置玩家的拾取物品范围
        """
        pass

    def SetJumpable(self, isJumpable):
        # type: (bool) -> 'bool'
        """
        设置玩家是否可跳跃
        """
        pass

    def SetMovable(self, isMovable):
        # type: (bool) -> 'bool'
        """
        设置玩家是否可移动
        """
        pass

    def AddAnimationController(self, animationControllerKey, animationControllerName):
        # type: (str, str) -> 'bool'
        """
        增加玩家渲染动画控制器
        """
        pass

    def AddAnimationIntoState(self, animationControllerName, stateName, animationName, condition):
        # type: (str, str, str, str) -> 'bool'
        """
        在玩家的动画控制器中的状态添加动画
        """
        pass

    def AddGeometry(self, geometryKey, geometryName):
        # type: (str, str) -> 'bool'
        """
        增加玩家渲染几何体
        """
        pass

    def AddParticleEffect(self, effectKey, effectName):
        # type: (str, str) -> 'bool'
        """
        增加玩家特效资源
        """
        pass

    def AddRenderController(self, renderControllerName, condition):
        # type: (str, str) -> 'bool'
        """
        增加玩家渲染控制器
        """
        pass

    def AddRenderMaterial(self, materialKey, materialName):
        # type: (str, str) -> 'bool'
        """
        增加玩家渲染需要的材质
        """
        pass

    def AddSoundEffect(self, soundKey, soundName):
        # type: (str, str) -> 'bool'
        """
        增加玩家音效资源
        """
        pass

    def AddTexture(self, geometryKey, geometryName):
        # type: (str, str) -> 'bool'
        """
        增加玩家渲染贴图
        """
        pass

    def SetSkin(self, skin):
        # type: (str) -> 'bool'
        """
        更换原版自定义皮肤
        """
        pass

