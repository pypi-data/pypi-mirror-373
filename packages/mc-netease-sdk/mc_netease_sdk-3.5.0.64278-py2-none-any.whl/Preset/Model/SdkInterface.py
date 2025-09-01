# -*- coding: utf-8 -*-

from mod.server.component.effectCompServer import EffectComponentServer
from mod.server.component.actorMotionCompServer import ActorMotionComponentServer
from mod.server.component.blockInfoCompServer import BlockInfoComponentServer
from mod.client.component.itemCompClient import ItemCompClient
from typing import Union
from Preset.Model.Effect.EffectPreset import EffectPreset
from mod.server.component.rotCompServer import RotComponentServer
from mod.server.component.blockCompServer import BlockCompServer
from mod.client.component.frameAniSkeletonBindComp import FrameAniSkeletonBindComp
from mod.server.component.scaleCompServer import ScaleComponentServer
from mod.server.component.gravityCompServer import GravityComponentServer
from mod.server.system.serverSystem import ServerSystem
from mod.server.component.itemCompServer import ItemCompServer
from mod.client.component.virtualWorldCompClient import VirtualWorldCompClient
from mod.client.system.clientSystem import ClientSystem
from typing import Tuple
from Preset.Model.Entity.EntityPreset import EntityPreset
from Preset.Model.UI.UIPreset import UIPreset
from mod.client.component.frameAniControlComp import FrameAniControlComp
from mod.client.component.actorMotionCompClient import ActorMotionComponentClient
from mod.client.component.skyRenderCompClient import SkyRenderCompClient
from mod.client.component.textBoardCompClient import TextBoardComponentClient
import mod.client.extraClientApi as extraClientApi
from mod.client.component.posCompClient import PosComponentClient
from mod.server.component.msgCompServer import MsgComponentServer
from mod.server.component.posCompServer import PosComponentServer
from mod.server.component.expCompServer import ExpComponentServer
from mod.server.component.flyCompServer import FlyComponentServer
from mod.server.component.nameCompServer import NameComponentServer
from mod.server.component.bulletAttributesCompServer import BulletAttributesComponentServer
from mod.server.component.dimensionCompServer import DimensionCompServer
from mod.client.component.blockUseEventWhiteListCompClient import BlockUseEventWhiteListComponentClient
from mod.server.component.mobSpawnCompServer import MobSpawnComponentServer
from mod.client.component.particleTransComp import ParticleTransComp
from mod.server.component.levelCompServer import LevelComponentServer
from mod.server.component.timeCompServer import TimeComponentServer
from mod.server.component.chestContainerCompServer import ChestContainerCompServer
from mod.server.blockEntityData import BlockEntityData
from mod.server.component.chunkSourceComp import ChunkSourceCompServer
from mod.client.component.postProcessControlComp import PostProcessComponent
from mod.client.component.auxValueCompClient import AuxValueComponentClient
from mod.server.component.tameCompServer import TameComponentServer
from mod.server.component.petCompServer import PetComponentServer
from mod.server.component.blockStateCompServer import BlockStateComponentServer
from mod.client.component.textNotifyCompClient import TextNotifyComponet
from mod.server.component.collisionBoxCompServer import CollisionBoxComponentServer
from mod.server.component.biomeCompServer import BiomeCompServer
from mod.client.component.particleSkeletonBindComp import ParticleSkeletonBindComp
from mod.server.component.modelCompServer import ModelComponentServer
from mod.common.utils.timer import CallLater
from mod.client.component.actorRenderCompClient import ActorRenderCompClient
from Preset.Model.Block.BlockPreset import BlockPreset
from mod.server.component.gameCompServer import GameComponentServer
from mod.client.component.frameAniTransComp import FrameAniTransComp
from mod.server.component.rideCompServer import RideCompServer
from mod.client.component.cameraCompClient import CameraComponentClient
from mod.client.component.attrCompClient import AttrCompClient
from mod.server.component.actorPushableCompServer import ActorPushableCompServer
from mod.client.component.recipeCompClient import RecipeCompClient
from mod.server.component.weatherCompServer import WeatherComponentServer
from mod.server.component.actorOwnerCompServer import ActorOwnerComponentServer
from mod.server.component.engineTypeCompServer import EngineTypeComponentServer
from mod.client.component.playerViewCompClient import PlayerViewCompClient
from mod.server.component.projectileCompServer import ProjectileComponentServer
from mod.server.component.attrCompServer import AttrCompServer
from mod.client.component.queryVariableCompClient import QueryVariableComponentClient
from mod.server.component.redStoneCompServer import RedStoneComponentServer
from mod.common.component.baseComponent import BaseComponent
from mod.server.component.itemBannedCompServer import ItemBannedCompServer
from mod.server.component.breathCompServer import BreathCompServer
from mod.server.component.controlAiCompServer import ControlAiCompServer
from mod.client.component.engineTypeCompClient import EngineTypeComponentClient
from mod.client.component.chunkSourceCompClient import ChunkSourceCompClient
from mod.client.component.healthCompClient import HealthComponentClient
from mod.client.component.audioCustomCompClient import AudioCustomComponentClient
from mod.client.component.particleEntityBindComp import ParticleEntityBindComp
from mod.client.component.blockInfoCompClient import BlockInfoComponentClient
from mod.client.component.rotCompClient import RotComponentClient
from mod.server.component.explosionCompServer import ExplosionComponentServer
from mod.server.component.persistenceCompServer import PersistenceCompServer
from mod.server.component.actionCompServer import ActionCompServer
from mod.server.component.portalCompServer import PortalComponentServer
from mod.server.component.commandCompServer import CommandCompServer
from mod.server.component.hurtCompServer import HurtCompServer
from mod.server.component.moveToCompServer import MoveToComponentServer
from mod.client.component.modelCompClient import ModelComponentClient
from mod.client.component.particleControlComp import ParticleControlComp
from typing import List
from mod.client.component.gameCompClient import GameComponentClient
from mod.server.component.recipeCompServer import RecipeCompServer
from mod.client.component.configCompClient import ConfigCompClient
from mod.client.component.nameCompClient import NameComponentClient
from mod.client.component.fogCompClient import FogCompClient
from mod.server.component.auxValueCompServer import AuxValueComponentServer
from typing import Any
import mod.common.minecraftEnum as minecraftEnum
from mod.client.component.brightnessCompClient import BrightnessCompClient
from mod.client.component.deviceCompClient import DeviceCompClient
from mod.server.component.entityEventCompServer import EntityEventComponentServer
from mod.server.component.playerCompServer import PlayerCompServer
from mod.server.component.blockEntityExDataCompServer import BlockEntityExDataCompServer
from mod.client.component.operationCompClient import OperationCompClient
from mod.client.component.modAttrCompClient import ModAttrComponentClient
from mod.server.component.featureCompServer import FeatureCompServer
from mod.server.component.modAttrCompServer import ModAttrComponentServer
from mod.server.component.exDataCompServer import ExDataCompServer
from Preset.Model.Player.PlayerPreset import PlayerPreset
from mod.client.component.playerAnimCompClient import PlayerAnimCompClient
from mod.server.component.blockUseEventWhiteListCompServer import BlockUseEventWhiteListComponentServer
import mod.server.extraServerApi as extraServerApi
from mod.server.component.actorLootCompServer import ActorLootComponentServer
from mod.client.component.frameAniEntityBindComp import FrameAniEntityBindComp

class SdkInterface():
    def __init__(self):
        # type: () -> 'None'
        """
        SdkInterface是对SDK接口封装的基类。
        """
        self.entityId = None
        self.isClient = None

    def GetEntityId(self):
        # type: () -> 'Union[str,int]'
        """
        获取对象实体ID
        """
        pass

    def ToPlayerPreset(self):
        # type: () -> 'PlayerPreset'
        """
        强制类型转换为玩家预设
        """
        pass

    def ToEntityPreset(self):
        # type: () -> 'EntityPreset'
        """
        强制类型转换为实体预设
        """
        pass

    def ToEffectPreset(self):
        # type: () -> 'EffectPreset'
        """
        强制类型转换为特效预设
        """
        pass

    def ToBlockPreset(self):
        # type: () -> 'BlockPreset'
        """
        强制类型转换为方块预设
        """
        pass

    def ToUIPreset(self):
        # type: () -> 'UIPreset'
        """
        强制类型转换为UI预设
        """
        pass

    def GetServerSystem(self):
        # type: () -> 'ServerSystem'
        """
        返回当前对象可使用的服务端system
        """
        pass

    def GetClientSystem(self):
        # type: () -> 'ClientSystem'
        """
        返回当前对象可使用的客户端system
        """
        pass

    def GetSystem(self):
        # type: () -> 'Union[ClientSystem,ServerSystem]'
        """
        返回当前对象可使用的system
        """
        pass

    def GetApi(self):
        # type: () -> 'Union[extraClientApi,extraServerApi]'
        """
        返回当前对象可使用的SDK API模块
        """
        pass

    def GetLevelId(self):
        # type: () -> 'str'
        """
        获取当前对象所在的level_id
        """
        pass

    def CreateComponent(self, entityId, nameSpace, name):
        # type: (Union[str,int], str, str) -> 'BaseComponent'
        """
        给实体创建组件
        """
        pass

    def GetMinecraftEnum(self):
        # type: () -> 'minecraftEnum'
        """
        用于获取枚举值文档中的枚举值
        """
        pass

    def DestroyEntity(self, entityId=None):
        # type: (str) -> 'bool'
        """
        销毁实体
        """
        pass

    def CreateActionComponent(self, entityId):
        # type: (Union[str,int]) -> 'ActionCompServer'
        """
        创建action组件
        """
        pass

    def SetEntityAttackTarget(self, entityId, targetId):
        # type: (Union[str,int], str) -> 'bool'
        """
        设置仇恨目标
        """
        pass

    def ResetEntityAttackTarget(self, entityId):
        # type: (Union[str,int]) -> 'bool'
        """
        清除仇恨目标
        """
        pass

    def GetEntityAttackTarget(self, entityId):
        # type: (Union[str,int]) -> 'str'
        """
        获取仇恨目标
        """
        pass

    def SetMobKnockback(self, entityId, xd=0.1, zd=0.1, power=1.0, height=1.0, heightCap=1.0):
        # type: (Union[str,int], float, float, float, float, float) -> 'None'
        """
        设置击退的初始速度，需要考虑阻力的影响
        """
        pass

    def CreateActorLootComponent(self, entityId):
        # type: (Union[str,int]) -> 'ActorLootComponentServer'
        """
        创建actorLoot组件
        """
        pass

    def SpawnLootTable(self, pos, identifier, playerKillerId=None, damageCauseEntityId=None):
        # type: (Tuple[int,int,int], str, str, str) -> 'bool'
        """
        使用生物类型模拟一次随机掉落，生成的物品与json定义的概率有关
        """
        pass

    def SpawnLootTableWithActor(self, pos, entityId, playerKillerId=None, damageCauseEntityId=None):
        # type: (Tuple[int,int,int], str, str, str) -> 'bool'
        """
        使用生物实例模拟一次随机掉落，生成的物品与json定义的概率有关
        """
        pass

    def CreateActorMotionComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[ActorMotionComponentServer,ActorMotionComponentClient]'
        """
        创建actorMotion组件
        """
        pass

    def GetDirFromRot(self, rot):
        # type: (Tuple[float,float]) -> 'Tuple[float,float,float]'
        """
        通过旋转角度获取朝向
        """
        pass

    def SetEntityMotion(self, entityId, motion):
        # type: (Union[str,int], Tuple[float,float,float]) -> 'bool'
        """
        设置生物的瞬时移动方向向量，服务端只能对非玩家使用，客户端只能对本地玩家使用
        """
        pass

    def GetEntityMotion(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[int,int,int]'
        """
        获取生物（含玩家）的瞬时移动方向向量
        """
        pass

    def GetInputVector(self):
        # type: () -> 'Tuple[float,float]'
        """
        获取本地玩家方向键（移动轮盘）的输入
        """
        pass

    def LockInputVector(self, inputVector):
        # type: (Tuple[float,float]) -> 'bool'
        """
        锁定本地玩家方向键（移动轮盘）的输入，可使本地玩家持续向指定方向前行，且不会再受玩家输入影响
        """
        pass

    def UnlockInputVector(self):
        # type: () -> 'bool'
        """
        解锁本地玩家方向键（移动轮盘）的输入
        """
        pass

    def CreateActorOwnerComponent(self, entityId):
        # type: (Union[str,int]) -> 'ActorOwnerComponentServer'
        """
        创建actorOwner组件
        """
        pass

    def SetEntityOwner(self, entityId, ownerId):
        # type: (Union[str,int], str) -> 'bool'
        """
        设置实体的属主
        """
        pass

    def GetEntityOwner(self, entityId):
        # type: (Union[str,int]) -> 'str'
        """
        获取实体的属主
        """
        pass

    def CreateActorPushableComponent(self, entityId):
        # type: (Union[str,int]) -> 'ActorPushableCompServer'
        """
        创建actorPushable组件
        """
        pass

    def SetActorPushable(self, entityId, isPushable):
        # type: (Union[str,int], int) -> 'bool'
        """
        设置实体是否可推动
        """
        pass

    def CreateAttrComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[AttrCompServer,AttrCompClient]'
        """
        创建attr组件
        """
        pass

    def IsEntityOnFire(self, entityId):
        # type: (Union[str,int]) -> 'bool'
        """
        获取实体是否着火
        """
        pass

    def SetEntityOnFire(self, entityId, seconds, burn_damage=1):
        # type: (Union[str,int], int, int) -> 'bool'
        """
        设置实体着火
        """
        pass

    def GetEntityAttrValue(self, entityId, attrType):
        # type: (Union[str,int], int) -> 'float'
        """
        获取属性值，包括生命值，饥饿度，移速
        """
        pass

    def GetEntityAttrMaxValue(self, entityId, attrType):
        # type: (Union[str,int], int) -> 'float'
        """
        获取属性最大值，包括生命值，饥饿度，移速
        """
        pass

    def SetEntityAttrValue(self, entityId, attrType, value):
        # type: (Union[str,int], int, float) -> 'bool'
        """
        设置属性值，包括生命值，饥饿度，移速
        """
        pass

    def SetEntityAttrMaxValue(self, entityId, attrType, value):
        # type: (Union[str,int], int, float) -> 'bool'
        """
        设置属性最大值，包括生命值，饥饿度，移速
        """
        pass

    def SetPlayerStepHeight(self, playerId, stepHeight):
        # type: (Union[str,int], float) -> 'bool'
        """
        设置玩家前进非跳跃状态下能上的最大台阶高度, 默认值为0.5625，1的话表示能上一个台阶
        """
        pass

    def GetPlayerStepHeight(self, playerId):
        # type: (Union[str,int]) -> 'float'
        """
        返回玩家前进非跳跃状态下能上的最大台阶高度
        """
        pass

    def ResetPlayerStepHeight(self, playerId):
        # type: (Union[str,int]) -> 'bool'
        """
        恢复引擎默认玩家前进非跳跃状态下能上的最大台阶高度
        """
        pass

    def IsEntityInLava(self, entityId):
        # type: (Union[str,int]) -> 'bool'
        """
        实体是否在岩浆中
        """
        pass

    def IsEntityOnGround(self, entityId):
        # type: (Union[str,int]) -> 'bool'
        """
        实体是否触地
        """
        pass

    def CreateAuxValueComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[AuxValueComponentServer,AuxValueComponentClient]'
        """
        创建auxValue组件
        """
        pass

    def GetEntityAuxValue(self, entityId):
        # type: (Union[str,int]) -> 'int'
        """
        获取射出的弓箭或投掷出的药水的附加值
        """
        pass

    def CreateBiomeComponent(self, entityId):
        # type: (Union[str,int]) -> 'BiomeCompServer'
        """
        创建biome组件
        """
        pass

    def GetBiomeName(self, pos, dimId=-1):
        # type: (Tuple[int,int,int], int) -> 'str'
        """
        获取某一位置所属的生物群系信息
        """
        pass

    def CreateBlockComponent(self, entityId):
        # type: (Union[str,int]) -> 'BlockCompServer'
        """
        创建block组件
        """
        pass

    def RegisterBlockPatterns(self, pattern, defines, result_actor_name):
        # type: (List[str], dict, str) -> 'bool'
        """
        注册特殊方块组合
        """
        pass

    def CreateMicroBlockResStr(self, identifier, start, end, colorMap=None, isMerge=False, icon=''):
        # type: (str, Tuple[int,int,int], Tuple[int,int,int], dict, bool, str) -> 'str'
        """
        生成微缩方块资源Json字符串
        """
        pass

    def CreateBlockEntityData(self, entityId):
        # type: (Union[str,int]) -> 'BlockEntityExDataCompServer'
        """
        创建blockEntityData组件
        """
        pass

    def GetCustomBlockEntityData(self, dimension, pos):
        # type: (int, Tuple[int,int,int]) -> 'Union[BlockEntityData,None]'
        """
        用于获取可操作某个自定义方块实体数据的对象，操作方式与dict类似
        """
        pass

    def CreateBlockInfoComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[BlockInfoComponentServer,BlockInfoComponentClient]'
        """
        创建blockInfo组件
        """
        pass

    def GetBlock(self, pos, dimensionId=0):
        # type: (Tuple[int,int,int], int) -> 'dict'
        """
        获取某一位置的block
        """
        pass

    def SetBlock(self, pos, blockDict, oldBlockHandling=0, dimensionId=0):
        # type: (Tuple[int,int,int], dict, int, int) -> 'bool'
        """
        设置某一位置的方块
        """
        pass

    def GetTopBlockHeight(self, pos, dimension=0):
        # type: (Tuple[int,int], int) -> 'Union[int,None]'
        """
        获取当前维度某一位置最高的非空气方块的高度
        """
        pass

    def GetBlockDestroyTime(self, blockName, itemName=None):
        # type: (str, str) -> 'float'
        """
        获取使用物品破坏方块需要的时间
        """
        pass

    def GetBlockEntityData(self, dimension, pos):
        # type: (int, Tuple[int,int,int]) -> 'Union[dict,None]'
        """
        用于获取方块（包括自定义方块）的数据，数据只读不可写
        """
        pass

    def CreateBlockStateComponent(self, entityId):
        # type: (Union[str,int]) -> 'BlockStateComponentServer'
        """
        创建blockState组件
        """
        pass

    def GetBlockStates(self, pos, dimensionId=0):
        # type: (Tuple[float,float,float], int) -> 'dict'
        """
        获取<a href="../../../../mcguide/20-玩法开发/10-基本概念/1-我的世界基础概念.html#物品信息字典#方块状态">方块状态</a>
        """
        pass

    def SetBlockStates(self, pos, data, dimensionId=0):
        # type: (Tuple[float,float,float], dict, int) -> 'bool'
        """
        设置<a href="../../../../mcguide/20-玩法开发/10-基本概念/1-我的世界基础概念.html#物品信息字典#方块状态">方块状态</a>
        """
        pass

    def GetBlockAuxValueFromStates(self, blockName, states):
        # type: (str, dict) -> 'int'
        """
        根据方块名称和<a href="../../../../mcguide/20-玩法开发/10-基本概念/1-我的世界基础概念.html#物品信息字典#方块状态">方块状态</a>获取方块附加值AuxValue
        """
        pass

    def GetBlockStatesFromAuxValue(self, blockName, auxValue):
        # type: (str, int) -> 'dict'
        """
        根据方块名称和方块附加值AuxValue获取<a href="../../../../mcguide/20-玩法开发/10-基本概念/1-我的世界基础概念.html#物品信息字典#方块状态">方块状态</a>
        """
        pass

    def CreateBlockUseEventWhiteList(self, entityId):
        # type: (Union[str,int]) -> 'Union[BlockUseEventWhiteListComponentServer,BlockUseEventWhiteListComponentClient]'
        """
        创建blockUseEventWhiteList组件
        """
        pass

    def AddBlockItemListenForUseEvent(self, blockName):
        # type: (str) -> 'bool'
        """
        增加blockName方块对ServerBlockUseEvent事件的脚本层监听
        """
        pass

    def RemoveBlockItemListenForUseEvent(self, blockName):
        # type: (str) -> 'bool'
        """
        移除blockName方块对ServerBlockUseEvent事件的脚本层监听
        """
        pass

    def ClearAllListenForBlockUseEventItems(self):
        # type: () -> 'bool'
        """
        清空所有已添加方块对ServerBlockUseEvent事件的脚本层监听
        """
        pass

    def CreateBreathComponent(self, entityId):
        # type: (Union[str,int]) -> 'BreathCompServer'
        """
        创建breath组件
        """
        pass

    def GetUnitBubbleAirSupply(self):
        # type: () -> 'int'
        """
        单位气泡数对应的氧气储备值
        """
        pass

    def GetEntityCurrentAirSupply(self, entityId):
        # type: (Union[str,int]) -> 'int'
        """
        生物当前氧气储备值
        """
        pass

    def GetEntityMaxAirSupply(self, entityId):
        # type: (Union[str,int]) -> 'int'
        """
        获取生物最大氧气储备值
        """
        pass

    def SetEntityCurrentAirSupply(self, entityId, data):
        # type: (Union[str,int], int) -> 'bool'
        """
        设置生物氧气储备值
        """
        pass

    def SetEntityMaxAirSupply(self, entityId, data):
        # type: (Union[str,int], int) -> 'bool'
        """
        设置生物最大氧气储备值
        """
        pass

    def IsEntityConsumingAirSupply(self, entityId):
        # type: (Union[str,int]) -> 'bool'
        """
        获取生物当前是否在消耗氧气
        """
        pass

    def SetEntityRecoverTotalAirSupplyTime(self, entityId, timeSec):
        # type: (Union[str,int], float) -> 'bool'
        """
        设置恢复最大氧气量的时间，单位秒
        """
        pass

    def CreateBulletAttributesComponent(self, entityId):
        # type: (Union[str,int]) -> 'BulletAttributesComponentServer'
        """
        创建bulletAttributes组件
        """
        pass

    def GetEntitySourceId(self, entityId):
        # type: (Union[str,int]) -> 'str'
        """
        获取抛射物发射者实体id
        """
        pass

    def CreateChestBlockComponent(self, entityId):
        # type: (Union[str,int]) -> 'ChestContainerCompServer'
        """
        创建chestBlock组件
        """
        pass

    def GetChestBoxSize(self, pos, dimensionId=0):
        # type: (Tuple[int,int,int], int) -> 'int'
        """
        获取箱子容量大小
        """
        pass

    def SetChestBoxItemNum(self, pos, slotPos, num, dimensionId=0):
        # type: (Tuple[int,int,int], int, int, int) -> 'bool'
        """
        设置箱子槽位物品数目
        """
        pass

    def SetChestBoxItemExchange(self, playerId, pos, slotPos1, slotPos2):
        # type: (str, Tuple[int,int,int], int, int) -> 'bool'
        """
        交换箱子里物品的槽位
        """
        pass

    def CreateChunkSourceComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[ChunkSourceCompServer,ChunkSourceCompClient]'
        """
        创建chunkSource组件
        """
        pass

    def SetAddArea(self, key, dimensionId, minPos, maxPos):
        # type: (str, int, Tuple[int,int,int], Tuple[int,int,int]) -> 'bool'
        """
        设置区块的常加载
        """
        pass

    def DeleteArea(self, key):
        # type: (str) -> 'bool'
        """
        删除一个常加载区域
        """
        pass

    def DeleteAllArea(self):
        # type: () -> 'int'
        """
        删除所有常加载区域
        """
        pass

    def GetAllAreaKeys(self):
        # type: () -> 'List[str]'
        """
        获取所有常加载区域名称列表
        """
        pass

    def CheckChunkState(self, dimension, pos):
        # type: (int, Tuple[int,int,int]) -> 'bool'
        """
        判断指定位置的chunk是否加载完成
        """
        pass

    def GetLoadedChunks(self, dimension):
        # type: (int) -> 'Union[None,List[Tuple[int,int]]]'
        """
        获取指定维度当前已经加载完毕的全部区块的坐标列表
        """
        pass

    def GetChunkEntities(self, dimension, pos):
        # type: (int, Tuple[int,int,int]) -> 'Union[None,List[str]]'
        """
        获取指定位置的区块中，全部的实体和玩家的ID列表
        """
        pass

    def GetChunkMobNum(self, dimension, chunkPos):
        # type: (int, Tuple[int,int]) -> 'int'
        """
        获取某区块中的生物数量（不包括玩家，但包括盔甲架）
        """
        pass

    def IsChunkGenerated(self, dimension, chunkPos):
        # type: (int, Tuple[int,int]) -> 'bool'
        """
        获取某个区块是否生成过。
        """
        pass

    def CreateCollisionBoxComponent(self, entityId):
        # type: (Union[str,int]) -> 'CollisionBoxComponentServer'
        """
        创建collisionBox组件
        """
        pass

    def SetEntityCollisionBoxSize(self, entityId, size):
        # type: (Union[str,int], Tuple[float,float]) -> 'bool'
        """
        设置实体的包围盒
        """
        pass

    def GetEntityCollisionBoxSize(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[float,float]'
        """
        获取实体的包围盒
        """
        pass

    def CreateCommandComponent(self, entityId):
        # type: (Union[str,int]) -> 'CommandCompServer'
        """
        创建command组件
        """
        pass

    def SetCommand(self, cmdStr, entityId=None, showOutput=False):
        # type: (str, str, bool) -> 'bool'
        """
        使用游戏内指令
        """
        pass

    def GetCommandPermissionLevel(self):
        # type: () -> 'int'
        """
        返回设定使用/op命令时OP的权限等级（对应server.properties中的op-permission-level配置）
        """
        pass

    def SetCommandPermissionLevel(self, opLevel):
        # type: (int) -> 'bool'
        """
        设置当玩家使用/op命令时OP的权限等级（对应server.properties中的op-permission-level配置）
        """
        pass

    def GetDefaultPlayerPermissionLevel(self):
        # type: () -> 'int'
        """
        返回新玩家加入时的权限身份（对应server.properties中的default-player-permission-level配置）
        """
        pass

    def SetDefaultPlayerPermissionLevel(self, opLevel):
        # type: (int) -> 'bool'
        """
        设置新玩家加入时的权限身份（对应server.properties中的default-player-permission-level配置）
        """
        pass

    def CreateControlAiComponent(self, entityId):
        # type: (Union[str,int]) -> 'ControlAiCompServer'
        """
        创建controlAi组件
        """
        pass

    def SetEntityBlockControlAi(self, entityId, isBlock):
        # type: (Union[str,int], bool) -> 'bool'
        """
        设置屏蔽生物原生AI
        """
        pass

    def CreateDimensionComponent(self, entityId):
        # type: (Union[str,int]) -> 'DimensionCompServer'
        """
        创建dimension组件
        """
        pass

    def GetEntityDimensionId(self, entityId):
        # type: (Union[str,int]) -> 'int'
        """
        获取实体所在维度
        """
        pass

    def ChangeEntityDimension(self, entityId, dimensionId, pos=None):
        # type: (Union[str,int], int, Tuple[int,int,int]) -> 'bool'
        """
        传送玩家以外的实体
        """
        pass

    def ChangePlayerDimension(self, playerId, dimensionId, pos):
        # type: (Union[str,int], int, Tuple[int,int,int]) -> 'bool'
        """
        传送玩家
        """
        pass

    def MirrorDimension(self, fromId, toId):
        # type: (int, int) -> 'bool'
        """
        复制不同dimension的地形
        """
        pass

    def CreateDimension(self, dimensionId):
        # type: (int) -> 'bool'
        """
        创建新的dimension
        """
        pass

    def RegisterEntityAOIEvent(self, dimension, name, aabb, ignoredEntities, entityType=1):
        # type: (int, str, Tuple[float,float,float,float,float,float], List[str], int) -> 'bool'
        """
        注册感应区域，有实体进入时和离开时会有消息通知
        """
        pass

    def UnRegisterEntityAOIEvent(self, dimension, name):
        # type: (int, str) -> 'bool'
        """
        反注册感应区域
        """
        pass

    def SetUseLocalTime(self, dimension, value):
        # type: (int, bool) -> 'bool'
        """
        让某个维度拥有自己的局部时间规则，开启后该维度可以拥有与其他维度不同的时间与是否昼夜更替的规则
        """
        pass

    def GetUseLocalTime(self, dimension):
        # type: (int) -> 'bool'
        """
        获取某个维度是否设置了使用局部时间规则
        """
        pass

    def SetLocalTime(self, dimension, time):
        # type: (int, int) -> 'bool'
        """
        设置使用局部时间规则维度的时间
        """
        pass

    def SetLocalTimeOfDay(self, dimension, timeOfDay):
        # type: (int, int) -> 'bool'
        """
        设置使用局部时间规则维度在一天内所在的时间
        """
        pass

    def GetLocalTime(self, dimension):
        # type: (int) -> 'int'
        """
        获取维度的时间
        """
        pass

    def SetLocalDoDayNightCycle(self, dimension, value):
        # type: (int, bool) -> 'bool'
        """
        设置使用局部时间规则的维度是否打开昼夜更替
        """
        pass

    def GetLocalDoDayNightCycle(self, dimension):
        # type: (int) -> 'bool'
        """
        获取维度是否打开昼夜更替
        """
        pass

    def CreateEffectComponent(self, entityId):
        # type: (Union[str,int]) -> 'EffectComponentServer'
        """
        创建effect组件
        """
        pass

    def RemoveEffectFromEntity(self, entityId, effectName):
        # type: (Union[str,int], str) -> 'bool'
        """
        为实体删除指定状态效果
        """
        pass

    def AddEffectToEntity(self, entityId, effectName, duration, amplifier, showParticles):
        # type: (Union[str,int], str, int, int, bool) -> 'bool'
        """
        为实体添加指定状态效果，如果添加的状态已存在则有以下集中情况：1、等级大于已存在则更新状态等级及持续时间；2、状态等级相等且剩余时间duration大于已存在则刷新剩余时间；3、等级小于已存在则不做修改；4、粒子效果以新的为准
        """
        pass

    def GetEntityEffects(self, entityId):
        # type: (Union[str,int]) -> 'List[dict]'
        """
        获取实体当前所有状态效果
        """
        pass

    def CreateEngineTypeComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[EngineTypeComponentServer,EngineTypeComponentClient]'
        """
        创建engineType组件
        """
        pass

    def GetEntityEngineTypeStr(self, entityId):
        # type: (Union[str,int]) -> 'str'
        """
        获取实体的类型名称
        """
        pass

    def GetEntityEngineType(self):
        # type: () -> 'int'
        """
        获取实体类型
        """
        pass

    def CreateEntityEventComponent(self, entityId):
        # type: (Union[str,int]) -> 'EntityEventComponentServer'
        """
        创建entityEvent组件
        """
        pass

    def TriggerEntityCustomEvent(self, entityId, eventName):
        # type: (str, str) -> 'bool'
        """
        触发生物自定义事件
        """
        pass

    def CreateExtraDataComponent(self, entityId=None):
        # type: (Union[str,int]) -> 'ExDataCompServer'
        """
        创建extraData组件
        """
        pass

    def GetExtraData(self, key, entityId=None):
        # type: (str, Union[str,int]) -> 'Any'
        """
        获取实体的自定义数据或者世界的自定义数据，某个键所对应的值。获取实体数据传入对应实体id
        """
        pass

    def SaveExtraData(self, entityId=None):
        # type: (Union[str,int]) -> 'bool'
        """
        用于保存实体的自定义数据或者世界的自定义数据
        """
        pass

    def SetExtraData(self, key, value, entityId=None, autoSave=True):
        # type: (str, Any, Union[str,int], bool) -> 'bool'
        """
        用于设置实体的自定义数据或者世界的自定义数据，数据以键值对的形式保存。设置实体数据时使用对应实体id创建组件，设置世界数据时使用levelId创建组件
        """
        pass

    def CleanExtraData(self, key, entityId=None):
        # type: (str, Union[str,int]) -> 'bool'
        """
        清除实体的自定义数据或者世界的自定义数据，清除实体数据时使用对应实体id创建组件，清除世界数据时使用levelId创建组件
        """
        pass

    def GetWholeExtraData(self, entityId=None):
        # type: (Union[str,int]) -> 'Union[dict,None]'
        """
        获取完整的实体的自定义数据或者世界的自定义数据，获取实体数据时使用对应实体id创建组件，获取世界数据时使用levelId创建组件
        """
        pass

    def CreateExpComponent(self, entityId):
        # type: (Union[str,int]) -> 'ExpComponentServer'
        """
        创建exp组件
        """
        pass

    def GetPlayerExp(self, playerId, isPercent=True):
        # type: (Union[str,int], bool) -> 'float'
        """
        获取玩家当前等级下的经验值
        """
        pass

    def AddPlayerExp(self, playerId, exp):
        # type: (Union[str,int], int) -> 'bool'
        """
        增加玩家经验值
        """
        pass

    def GetPlayerTotalExp(self, playerId):
        # type: (Union[str,int]) -> 'int'
        """
        获取玩家的总经验值
        """
        pass

    def SetPlayerTotalExp(self, playerId, exp):
        # type: (Union[str,int], int) -> 'bool'
        """
        设置玩家的总经验值
        """
        pass

    def GetOrbExperience(self, entityId):
        # type: (Union[str,int]) -> 'int'
        """
        获取经验球的经验
        """
        pass

    def SetOrbExperience(self, entityId, exp):
        # type: (Union[str,int], int) -> 'bool'
        """
        设置经验球经验
        """
        pass

    def CreateExperienceOrb(self, playerId, exp, position, isSpecial):
        # type: (int, int, Tuple[float,float,float], bool) -> 'bool'
        """
        创建专属经验球
        """
        pass

    def CreateExplosionComponent(self, entityId):
        # type: (Union[str,int]) -> 'ExplosionComponentServer'
        """
        创建explosion组件
        """
        pass

    def CreateExplosion(self, pos, radius, fire, breaks, sourceId, playerId):
        # type: (Tuple[float,float,float], int, bool, bool, str, str) -> 'bool'
        """
        用于生成爆炸
        """
        pass

    def CreateFeatureComponent(self, entityId):
        # type: (Union[str,int]) -> 'FeatureCompServer'
        """
        创建feature组件
        """
        pass

    def AddNeteaseFeatureWhiteList(self, structureName):
        # type: (str) -> 'bool'
        """
        添加结构对PlaceNeteaseStructureFeatureEvent事件的脚本层监听
        """
        pass

    def RemoveNeteaseFeatureWhiteList(self, structureName):
        # type: (str) -> 'bool'
        """
        移除structureName对PlaceNeteaseStructureFeatureEvent事件的脚本层监听
        """
        pass

    def ClearAllNeteaseFeatureWhiteList(self):
        # type: () -> 'bool'
        """
        清空所有已添加Netease Structure Feature对PlaceNeteaseStructureFeatureEvent事件的脚本层监听
        """
        pass

    def LocateStructureFeature(self, featureType, dimensionId, pos, useNewChunksOnly=False):
        # type: (int, int, Tuple[int,int,int], bool) -> 'Union[Tuple[float,float],None]'
        """
        与/locate指令相似，用于定位原版的部分结构，如海底神殿、末地城等。
        """
        pass

    def LocateNeteaseFeatureRule(self, ruleName, dimensionId, pos, mustBeInNewChunk=False):
        # type: (str, int, Tuple[int,int,int], bool) -> 'Union[Tuple[float,float,float],None]'
        """
        与/locate指令相似，用于定位<a href="../../../../mcguide/20-玩法开发/15-自定义游戏内容/4-自定义维度/4-自定义特征.html#特征规则（feature-rules）">网易自定义特征规则</a>
        """
        pass

    def CreateFlyComponent(self, playerId):
        # type: (Union[str,int]) -> 'FlyComponentServer'
        """
        创建fly组件
        """
        pass

    def IsPlayerFlying(self, playerId):
        # type: (Union[str,int]) -> 'bool'
        """
        获取玩家是否在飞行
        """
        pass

    def ChangePlayerFlyState(self, playerId, isFly):
        # type: (Union[str,int], bool) -> 'bool'
        """
        给予/取消飞行能力，并且进入飞行/非飞行状态
        """
        pass

    def CreateGameComponent(self):
        # type: () -> 'Union[GameComponentServer,GameComponentClient]'
        """
        创建game组件
        """
        pass

    def AddBlockProtectField(self, dimensionId, startPos, endPos):
        # type: (int, Tuple[int,int,int], Tuple[int,int,int]) -> 'int'
        """
        设置一个方块无法被玩家/实体破坏的区域
        """
        pass

    def RemoveBlockProtectField(self, field):
        # type: (int) -> 'bool'
        """
        取消一个方块无法被玩家/实体破坏的区域
        """
        pass

    def CleanBlockProtectField(self):
        # type: () -> 'bool'
        """
        取消全部已设置的方块无法被玩家/实体破坏的区域
        """
        pass

    def KillEntity(self, entityId):
        # type: (str) -> 'bool'
        """
        杀死某个Entity
        """
        pass

    def CreateEngineEntityByTypeStr(self, engineTypeStr, pos, rot, dimensionId=0, isNpc=False):
        # type: (str, Tuple[float,float,float], Tuple[float,float], int, bool) -> 'Union[str,None]'
        """
        创建指定identifier的实体
        """
        pass

    def PlaceStructure(self, pos, structureName, dimensionId=-1, rotation=0):
        # type: (Tuple[float,float,float], str, int, int) -> 'bool'
        """
        放置结构
        """
        pass

    def AddTimer(self, delay, func, *args, **kwargs):
        # type: (float, function, Any, Any) -> 'CallLater'
        """
        添加定时器，非重复
        """
        pass

    def AddRepeatedTimer(self, delay, func, *args, **kwargs):
        # type: (float, function, Any, Any) -> 'CallLater'
        """
        添加服务端触发的定时器，重复执行
        """
        pass

    def CancelTimer(self, timer):
        # type: (CallLater) -> 'None'
        """
        取消定时器
        """
        pass

    def GetEntitiesInArea(self, startPos, endPos, dimensionId=0):
        # type: (Tuple[int,int,int], Tuple[int,int,int], int) -> 'List[str]'
        """
        获取区域内的entity列表
        """
        pass

    def GetEntitiesAround(self, entityId, radius, filters):
        # type: (str, int, dict) -> 'List[str]'
        """
        获取区域内的entity列表
        """
        pass

    def ShowHealthBar(self, show):
        # type: (bool) -> 'bool'
        """
        设置是否显示血条
        """
        pass

    def SetNameDeeptest(self, deeptest):
        # type: (bool) -> 'bool'
        """
        设置名字是否透视
        """
        pass

    def GetScreenSize(self):
        # type: () -> 'Tuple[float,float]'
        """
        获取游戏分辨率
        """
        pass

    def SetRenderLocalPlayer(self, render):
        # type: (bool) -> 'bool'
        """
        设置本地玩家是否渲染
        """
        pass

    def AddPickBlacklist(self, entityId):
        # type: (str) -> 'bool'
        """
        添加使用camera组件（例如GetChosen接口、PickFacing接口）选取实体时的黑名单，即该实体不会被选取到
        """
        pass

    def ClearPickBlacklist(self):
        # type: () -> 'bool'
        """
        清除使用camera组件（例如GetChosen接口、PickFacing接口）选取实体的黑名单
        """
        pass

    def CheckWordsValid(self, words):
        # type: (str) -> 'bool'
        """
        检查语句是否合法，即不包含敏感词
        """
        pass

    def CheckNameValid(self, name):
        # type: (str) -> 'bool'
        """
        检查昵称是否合法，即不包含敏感词
        """
        pass

    def GetScreenViewInfo(self):
        # type: () -> 'Tuple[float,float,float,float]'
        """
        获取游戏视角信息。分辨率为1313，618时，画布是376，250的2倍，所以viewport得到的是1313 + (2-(1313%2))，y值类似，可参考<a href="../../../mcguide/18-界面与交互/1-界面编辑器使用说明.html#《我的世界》界面适配方法">《我的世界》界面适配方法</a>
        """
        pass

    def SimulateTouchWithMouse(self, touch):
        # type: (bool) -> 'bool'
        """
        模拟使用鼠标控制UI（PC F11快捷键）
        """
        pass

    def GetCurrentDimension(self):
        # type: () -> 'int'
        """
        获取客户端当前维度
        """
        pass

    def GetChinese(self, langStr):
        # type: (str) -> 'str'
        """
        获取langStr对应的中文，可参考PC开发包中\handheld\localization\handheld\data\resource_packs\vanilla\texts\zh_CN.lang
        """
        pass

    def SetDisableHunger(self, isDisable):
        # type: (bool) -> 'bool'
        """
        设置是否屏蔽饥饿度
        """
        pass

    def SetOneTipMessage(self, playerId, message):
        # type: (str, str) -> 'bool'
        """
        在具体某个玩家的物品栏上方弹出tip类型通知，位置位于popup类型通知上方，此功能更建议在客户端使用game组件的对应接口SetTipMessage
        """
        pass

    def SetPopupNotice(self, message, subtitle):
        # type: (str, str) -> 'bool'
        """
        在物品栏上方弹出popup类型通知，位置位于tip类型消息下方，服务端调用是针对全体玩家，客户端调用只影响本地玩家
        """
        pass

    def SetTipMessage(self, message):
        # type: (str) -> 'bool'
        """
        在物品栏上方弹出tip类型通知，位置位于popup类型通知上方，服务端调用是针对全体玩家，客户端调用只影响本地玩家
        """
        pass

    def SetNotifyMsg(self, msg, color='\xc2\xa7f'):
        # type: (str, str) -> 'bool'
        """
        设置消息通知
        """
        pass

    def GetPlayerGameType(self, playerId):
        # type: (str) -> 'int'
        """
        获取指定玩家的游戏模式
        """
        pass

    def HasEntity(self, entityId):
        # type: (str) -> 'int'
        """
        判断 entity 是否存在
        """
        pass

    def IsEntityAlive(self, entityId):
        # type: (str) -> 'bool'
        """
        判断生物实体是否存活或非生物实体是否存在
        """
        pass

    def CreateGravityComponent(self, entityId):
        # type: (Union[str,int]) -> 'GravityComponentServer'
        """
        创建gravity组件
        """
        pass

    def GetEntityGravity(self, entityId):
        # type: (Union[str,int]) -> 'float'
        """
        获取实体的重力因子，当生物重力因子为0时则应用世界的重力因子
        """
        pass

    def SetEntityGravity(self, entityId, gravity):
        # type: (Union[str,int], float) -> 'bool'
        """
        设置实体的重力因子，当生物重力因子为0时则应用世界的重力因子
        """
        pass

    def CreateHurtComponent(self, entityId):
        # type: (Union[str,int]) -> 'HurtCompServer'
        """
        创建hurt组件
        """
        pass

    def SetHurtByEntity(self, entityId, attackerId, damage, byPassArmor, knocked=True):
        # type: (Union[str,int], str, float, bool, bool) -> 'bool'
        """
        对实体造成伤害
        """
        pass

    def SetHurtByEntityNew(self, entityId, damage, cause, attackerId=None, childAttackerId=None, knocked=True):
        # type: (Union[str,int], float, str, str, str, bool) -> 'bool'
        """
        对实体造成伤害
        """
        pass

    def SetEntityImmuneDamage(self, entityId, immune):
        # type: (Union[str,int], bool) -> 'bool'
        """
        设置实体是否免疫伤害（该属性存档）
        """
        pass

    def CreateItemBannedComponent(self, entityId):
        # type: (Union[str,int]) -> 'ItemBannedCompServer'
        """
        创建itembanned组件
        """
        pass

    def AddBannedItem(self, itemName):
        # type: (str) -> 'bool'
        """
        增加禁用物品
        """
        pass

    def GetBannedItemList(self):
        # type: () -> 'Union[List[str],None]'
        """
        获取禁用物品列表
        """
        pass

    def RemoveBannedItem(self, itemName):
        # type: (str) -> 'bool'
        """
        移除禁用物品
        """
        pass

    def ClearBannedItems(self):
        # type: () -> 'bool'
        """
        清空禁用物品
        """
        pass

    def CreateItemComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[ItemCompServer,ItemCompClient]'
        """
        创建item组件
        """
        pass

    def GetItemBasicInfo(self, itemName, auxValue=0, isEnchanted=False):
        # type: (str, int, bool) -> 'dict'
        """
        获取物品的基础信息
        """
        pass

    def GetLocalPlayerId(self):
        # type: () -> 'str'
        """
        获取本地玩家的id
        """
        pass

    def ClearPlayerOffHand(self, playerId):
        # type: (str) -> 'bool'
        """
        清除玩家左手物品
        """
        pass

    def GetPlayerItem(self, playerId, posType, slotPos=0, getUserData=False):
        # type: (str, int, int, bool) -> 'dict'
        """
        获取玩家物品，支持获取背包，盔甲栏，副手以及主手物品
        """
        pass

    def ChangePlayerItemTipsAndExtraId(self, playerId, posType, slotPos=0, customTips='', extraId=''):
        # type: (str, int, int, str, str) -> 'bool'
        """
        修改玩家物品的自定义tips和自定义标识符
        """
        pass

    def AddEnchantToInvItem(self, playerId, slotPos, enchantType, level):
        # type: (str, int, int, int) -> 'bool'
        """
        给物品栏的物品添加附魔信息
        """
        pass

    def GetInvItemEnchantData(self, playerId, slotPos):
        # type: (str, int) -> 'List[Tuple[int,int]]'
        """
        获取物品栏的物品附魔信息
        """
        pass

    def GetOffhandItem(self, playerId, getUserData=False):
        # type: (str, bool) -> 'dict'
        """
        获取左手物品的信息
        """
        pass

    def SetInvItemNum(self, playerId, slotPos, num):
        # type: (str, int, int) -> 'bool'
        """
        设置玩家背包物品数目
        """
        pass

    def SpawnItemToPlayerInv(self, itemDict, playerId, slotPos=-1):
        # type: (dict, str, int) -> 'bool'
        """
        生成物品到玩家背包
        """
        pass

    def SpawnItemToPlayerCarried(self, itemDict, playerId):
        # type: (dict, str) -> 'bool'
        """
        生成物品到玩家右手
        """
        pass

    def GetCarriedItem(self, getUserData=False):
        # type: (bool) -> 'dict'
        """
        获取右手物品的信息
        """
        pass

    def GetSlotId(self):
        # type: () -> 'int'
        """
        获取当前手持的快捷栏的槽id
        """
        pass

    def GetItemFormattedHoverText(self, itemName, auxValue=0, showCategory=False, userData=None):
        # type: (str, int, bool, dict) -> 'str'
        """
        获取物品的格式化hover文本，如：§f灾厄旗帜§r
        """
        pass

    def GetItemHoverName(self, itemName, auxValue=0, userData=None):
        # type: (str, int, dict) -> 'str'
        """
        获取物品的hover名称，如：灾厄旗帜§r
        """
        pass

    def GetItemEffectName(self, itemName, auxValue=0, userData=None):
        # type: (str, int, dict) -> 'str'
        """
        获取物品的状态描述，如：§7保护 0§r
        """
        pass

    def GetUserDataInEvent(self, eventName):
        # type: (str) -> 'bool'
        """
        使物品相关客户端事件的<a href="../../../mcguide/20-玩法开发/10-基本概念/1-我的世界基础概念.html#物品信息字典#物品信息字典">物品信息字典</a>参数带有userData。在mod初始化时调用即可
        """
        pass

    def ChangeItemTexture(self, identifier, texturePath):
        # type: (str, str) -> 'bool'
        """
        替换物品的贴图，修改后所有用到该贴图的物品都会被改变，后续创建的此类物品也会被改变。会同时修改物品在UI界面上的显示，手持时候的显示与场景掉落的显示。
        """
        pass

    def CreateLvComponent(self, playerId):
        # type: (Union[str,int]) -> 'LevelComponentServer'
        """
        创建lv组件
        """
        pass

    def GetPlayerLevel(self, playerId):
        # type: (Union[str,int]) -> 'int'
        """
        获取玩家等级
        """
        pass

    def AddPlayerLevel(self, playerId, level):
        # type: (Union[str,int], int) -> 'bool'
        """
        修改玩家等级
        """
        pass

    def CreateMobSpawnComponent(self, entityId):
        # type: (Union[str,int]) -> 'MobSpawnComponentServer'
        """
        创建mobSpawn组件
        """
        pass

    def SpawnCustomModule(self, biomeType, change, entityType, probability, minCount, maxCount, environment, minBrightness=-1, maxBrightness=-1, minHeight=-1, maxHeight=-1):
        # type: (int, int, int, int, int, int, int, int, int, int, int) -> 'bool'
        """
        设置自定义刷怪
        """
        pass

    def CreateModAttrComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[ModAttrComponentServer,ModAttrComponentClient]'
        """
        创建modAttr组件
        """
        pass

    def SetEntityModAttr(self, paramName, paramValue, needRestore, autoSave=False):
        # type: (str, Any, bool, bool) -> 'None'
        """
        设置属性值
        """
        pass

    def GetEntityModAttr(self, entityId, paramName, defaultValue=None):
        # type: (Union[str,int], str, Any) -> 'Any'
        """
        获取属性值
        """
        pass

    def RegisterEntityModAttrUpdateFunc(self, entityId, paramName, func):
        # type: (Union[str,int], str, function) -> 'None'
        """
        注册属性值变换时的回调函数，当属性变化时会调用该函数
        """
        pass

    def UnRegisterEntityModAttrUpdateFunc(self, entityId, paramName, func):
        # type: (Union[str,int], str, function) -> 'None'
        """
        反注册属性值变换时的回调函数
        """
        pass

    def CreateModelComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[ModelComponentServer,ModelComponentClient]'
        """
        创建model组件
        """
        pass

    def SetEntityOpacity(self, entityId, opacity):
        # type: (Union[str,int], float) -> 'None'
        """
        设置生物模型的透明度
        """
        pass

    def PlayEntityAnim(self, entityId, aniName, isLoop):
        # type: (Union[str,int], str, bool) -> 'bool'
        """
        播放骨骼动画
        """
        pass

    def GetEntityModelId(self, entityId):
        # type: (Union[str,int]) -> 'int'
        """
        获取骨骼模型的Id，主要用于特效绑定骨骼模型
        """
        pass

    def SetEntityModel(self, entityId, modelName):
        # type: (Union[str,int], str) -> 'bool'
        """
        设置骨骼模型
        """
        pass

    def ResetEntityModel(self, entityId):
        # type: (Union[str,int]) -> 'bool'
        """
        恢复实体为原版模型
        """
        pass

    def BindModelToEntity(self, entityId, boneName, modelName, offset=(0, 0, 0), rot=(0, 0, 0)):
        # type: (Union[str,int], str, str, Tuple[float,float,float], Tuple[float,float,float]) -> 'int'
        """
        实体替换骨骼模型后，再往上挂接其他骨骼模型。
        """
        pass

    def UnBindModelToEntity(self, entityId, modelId):
        # type: (Union[str,int], int) -> 'bool'
        """
        取消实体上挂接的某个骨骼模型。取消挂接后，这个modelId的模型便会销毁，无法再使用，如果是临时隐藏可以使用HideModel
        """
        pass

    def CreateMoveToComponent(self, entityId):
        # type: (Union[str,int]) -> 'MoveToComponentServer'
        """
        创建moveTo组件
        """
        pass

    def SetEntityMoveSetting(self, entityId, pos, speed, maxIteration, callback=None):
        # type: (Union[str,int], Tuple[float,float,float], float, int, function) -> 'None'
        """
        寻路组件
        """
        pass

    def CreateMsgComponent(self, entityId):
        # type: (Union[str,int]) -> 'MsgComponentServer'
        """
        创建msg组件
        """
        pass

    def SendMsg(self, name, msg):
        # type: (str, str) -> 'bool'
        """
        模拟玩家给所有人发送聊天栏消息
        """
        pass

    def SendMsgToPlayer(self, fromEntityId, toEntityId, msg):
        # type: (str, str, str) -> 'None'
        """
        模拟玩家给另一个玩家发送聊天栏消息
        """
        pass

    def NotifyOneMessage(self, playerId, msg, color='\xc2\xa7f'):
        # type: (str, str, str) -> 'None'
        """
        给指定玩家发送聊天框消息
        """
        pass

    def CreateNameComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[NameComponentServer,NameComponentClient]'
        """
        创建name组件
        """
        pass

    def GetEntityName(self, entityId):
        # type: (Union[str,int]) -> 'str'
        """
        获取生物的自定义名称，即使用命名牌或者SetName接口设置的名称
        """
        pass

    def SetEntityName(self, entityId, name):
        # type: (Union[str,int], str) -> 'bool'
        """
        用于设置生物的自定义名称，跟原版命名牌作用相同，玩家和新版流浪商人暂不支持
        """
        pass

    def SetPlayerPrefixAndSuffixName(self, playerId, prefix, prefixColor, suffix, suffixColor):
        # type: (Union[str,int], str, str, str, str) -> 'bool'
        """
        设置玩家前缀和后缀名字
        """
        pass

    def SetEntityShowName(self, entityId, show):
        # type: (Union[str,int], bool) -> 'bool'
        """
        设置生物名字是否按照默认游戏逻辑显示
        """
        pass

    def SetEntityAlwaysShowName(self, entityId, show):
        # type: (Union[str,int], bool) -> 'bool'
        """
        设置生物名字是否一直显示，瞄准点不指向生物时也能显示
        """
        pass

    def CreatePersistenceComponent(self, entityId):
        # type: (Union[str,int]) -> 'PersistenceCompServer'
        """
        创建persistence组件
        """
        pass

    def SetEntityPersistence(self, entityId, isPersistent):
        # type: (Union[str,int], bool) -> 'None'
        """
        设置实体是否存盘
        """
        pass

    def CreatePetComponent(self, entityId):
        # type: (Union[str,int]) -> 'PetComponentServer'
        """
        创建pet组件
        """
        pass

    def DisablePet(self):
        # type: () -> 'bool'
        """
        关闭官方伙伴功能，单人游戏以及本地联机不支持该接口
        """
        pass

    def EnablePet(self):
        # type: () -> 'bool'
        """
        启用官方伙伴功能，单人游戏以及本地联机不支持该接口
        """
        pass

    def CreatePlayerComponent(self, entityId):
        # type: (Union[str,int]) -> 'PlayerCompServer'
        """
        创建player组件
        """
        pass

    def EnablePlayerKeepInventory(self, playerId, enable):
        # type: (Union[str,int], bool) -> 'bool'
        """
        设置玩家死亡不掉落物品
        """
        pass

    def IsPlayerSneaking(self, playerId):
        # type: (Union[str,int]) -> 'bool'
        """
        是否潜行
        """
        pass

    def GetPlayerHunger(self, playerId):
        # type: (Union[str,int]) -> 'float'
        """
        获取玩家饥饿度，展示在UI饥饿度进度条上，初始值为20，即每一个鸡腿代表2个饥饿度。 **饱和度(saturation)** ：玩家当前饱和度，初始值为5，最大值始终为玩家当前饥饿度(hunger)，该值直接影响玩家**饥饿度(hunger)**。<br>1）增加方法：吃食物。<br>2）减少方法：每触发一次**消耗事件**，该值减少1，如果该值不大于0，直接把玩家 **饥饿度(hunger)** 减少1。
        """
        pass

    def SetPlayerHunger(self, playerId, value):
        # type: (Union[str,int], float) -> 'bool'
        """
        设置玩家饥饿度。
        """
        pass

    def CreatePortalComponent(self, entityId):
        # type: (Union[str,int]) -> 'PortalComponentServer'
        """
        创建portal组件
        """
        pass

    def CreatePosComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[PosComponentServer,PosComponentClient]'
        """
        创建pos组件
        """
        pass

    def GetEntityPos(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[float,float,float]'
        """
        获取实体位置
        """
        pass

    def GetEntityFootPos(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[float,float,float]'
        """
        获取实体脚所在的位置
        """
        pass

    def SetEntityPos(self, entityId, pos):
        # type: (Union[str,int], Tuple[int,int,int]) -> 'bool'
        """
        设置实体位置
        """
        pass

    def SetEntityFootPos(self, entityId, pos):
        # type: (Union[str,int], Tuple[float,float,float]) -> 'bool'
        """
        设置实体脚底所在的位置
        """
        pass

    def CreateProjectileComponent(self, entityId):
        # type: (Union[str,int]) -> 'ProjectileComponentServer'
        """
        创建projectile组件
        """
        pass

    def CreateProjectileEntity(self, spawnerId, entityIdentifier, param=None):
        # type: (str, str, dict) -> 'str'
        """
        创建抛射物（直接发射）
        """
        pass

    def CreateRecipeComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[RecipeCompServer,RecipeCompClient]'
        """
        创建recipe组件
        """
        pass

    def GetRecipeResult(self, recipeId):
        # type: (str) -> 'List[dict]'
        """
        根据配方id获取配方结果。仅支持合成配方
        """
        pass

    def GetRecipesByResult(self, resultIdentifier, tag, aux=0, maxResultNum=-1):
        # type: (str, str, int, int) -> 'List[dict]'
        """
        通过输出物品查询配方所需要的输入材料
        """
        pass

    def GetRecipesByInput(self, inputIdentifier, tag, aux=0, maxResultNum=-1):
        # type: (str, str, int, int) -> 'List[dict]'
        """
        通过输入物品查询配方
        """
        pass

    def CreateRedStoneComponent(self, entityId):
        # type: (Union[str,int]) -> 'RedStoneComponentServer'
        """
        创建redStone组件
        """
        pass

    def CreateRideComponent(self, entityId):
        # type: (Union[str,int]) -> 'RideCompServer'
        """
        创建ride组件
        """
        pass

    def CreateRotComponent(self, entityId):
        # type: (Union[str,int]) -> 'Union[RotComponentServer,RotComponentClient]'
        """
        创建rot组件
        """
        pass

    def GetEntityRot(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[float,float]'
        """
        获取实体角度
        """
        pass

    def SetEntityRot(self, entityId, rot):
        # type: (Union[str,int], Tuple[float,float]) -> 'bool'
        """
        设置实体的头的角度
        """
        pass

    def SetEntityLookAtPos(self, entityId, targetPos, minTime, maxTime, reject):
        # type: (Union[str,int], Tuple[float,float,float], float, float, bool) -> 'bool'
        """
        设置非玩家的实体看向某个位置
        """
        pass

    def GetBodyRot(self, entityId):
        # type: (Union[str,int]) -> 'float'
        """
        获取实体的身体的角度
        """
        pass

    def LockLocalPlayerRot(self, lock):
        # type: (bool) -> 'bool'
        """
        在分离摄像机时，锁定本地玩家的头部角度
        """
        pass

    def SetPlayerLookAtPos(self, targetPos, pitchStep, yawStep, blockInput=True):
        # type: (Tuple[float,float,float], float, float, bool) -> 'bool'
        """
        设置本地玩家看向某个位置
        """
        pass

    def CreateScaleComponent(self, entityId):
        # type: (Union[str,int]) -> 'ScaleComponentServer'
        """
        创建scale组件
        """
        pass

    def CreateTameComponent(self, entityId):
        # type: (Union[str,int]) -> 'TameComponentServer'
        """
        创建tame组件
        """
        pass

    def CreateTimeComponent(self, entityId):
        # type: (Union[str,int]) -> 'TimeComponentServer'
        """
        创建time组件
        """
        pass

    def GetTime(self):
        # type: () -> 'int'
        """
        获取当前世界时间
        """
        pass

    def CreateWeatherComponent(self, entityId):
        # type: (Union[str,int]) -> 'WeatherComponentServer'
        """
        创建weather组件
        """
        pass

    def CreateActorCollidableComponent(self, entityId):
        # type: (Union[str,int]) -> 'ActorCollidableCompClient'
        """
        创建actorCollidable组件
        """
        pass

    def CreateActorRenderComponent(self, entityId):
        # type: (Union[str,int]) -> 'ActorRenderCompClient'
        """
        创建actorRender组件
        """
        pass

    def CreateCustomAudioComponent(self, entityId):
        # type: (Union[str,int]) -> 'AudioCustomComponentClient'
        """
        创建customAudio组件
        """
        pass

    def CreateBrightnessComponent(self, entityId):
        # type: (Union[str,int]) -> 'BrightnessCompClient'
        """
        创建brightness组件
        """
        pass

    def SetEntityBrightness(self, entityId, brightness):
        # type: (Union[str,int], float) -> 'bool'
        """
        设置实体的亮度
        """
        pass

    def CreateCameraComponent(self, entityId):
        # type: (Union[str,int]) -> 'CameraComponentClient'
        """
        创建camera组件
        """
        pass

    def PickFacing(self):
        # type: () -> 'dict'
        """
        获取准星选中的实体或者方块
        """
        pass

    def CreateFogComponent(self, entityId):
        # type: (Union[str,int]) -> 'FogCompClient'
        """
        创建fog组件
        """
        pass

    def CreateFrameAniControlComponent(self, frameEntityId):
        # type: (Union[str,int]) -> 'FrameAniControlComp'
        """
        创建frameAniControl组件
        """
        pass

    def SetFrameAniLoop(self, frameEntityId, loop):
        # type: (Union[str,int], bool) -> 'bool'
        """
        设置序列帧是否循环播放，默认为否
        """
        pass

    def SetFrameAniFaceCamera(self, frameEntityId, face):
        # type: (Union[str,int], bool) -> 'bool'
        """
        设置序列帧是否始终朝向摄像机，默认为是
        """
        pass

    def SetFrameAniDeepTest(self, frameEntityId, deepTest):
        # type: (Union[str,int], bool) -> 'bool'
        """
        设置序列帧是否透视，默认为否
        """
        pass

    def CreateFrameAniEntityBindComponent(self, entityId):
        # type: (Union[str,int]) -> 'FrameAniEntityBindComp'
        """
        创建frameAniEntityBind组件
        """
        pass

    def BindFrameAniToEntity(self, frameEntityId, bindEntityId, offset, rot):
        # type: (int, str, Tuple[float,float,float], Tuple[float,float,float]) -> 'bool'
        """
        绑定entity
        """
        pass

    def CreateFrameAniSkeletonBindComponent(self, entityId):
        # type: (Union[str,int]) -> 'FrameAniSkeletonBindComp'
        """
        创建frameAniSkeletonBind组件
        """
        pass

    def BindFrameAniToSkeleton(self, frameEntityId, modelId, boneName, offset, rot):
        # type: (int, int, str, Tuple[float,float,float], Tuple[float,float,float]) -> 'bool'
        """
        绑定骨骼模型
        """
        pass

    def CreateFrameAniTransComponent(self, entityId):
        # type: (Union[str,int]) -> 'FrameAniTransComp'
        """
        创建frameAniTrans组件
        """
        pass

    def GetFrameAniPos(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[float,float,float]'
        """
        获取序列帧位置
        """
        pass

    def GetFrameAniRot(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[float,float]'
        """
        获取序列帧的角度
        """
        pass

    def GetFrameAniScale(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[float,float,float]'
        """
        获取序列帧的缩放
        """
        pass

    def SetFrameAniPos(self, entityId, pos):
        # type: (Union[str,int], Tuple[int,int,int]) -> 'bool'
        """
        设置序列帧位置
        """
        pass

    def SetFrameAniRot(self, entityId, rot):
        # type: (Union[str,int], Tuple[float,float]) -> 'bool'
        """
        设置特效的角度
        """
        pass

    def SetFrameAniScale(self, entityId, scale):
        # type: (Union[str,int], Tuple[float,float,float]) -> 'bool'
        """
        设置序列帧的缩放
        """
        pass

    def CreateHealthComponent(self, entityId):
        # type: (Union[str,int]) -> 'HealthComponentClient'
        """
        创建health组件
        """
        pass

    def ShowEntityHealth(self, entityId, show):
        # type: (Union[str,int], bool) -> 'None'
        """
        设置某个entity是否显示血条，默认为显示
        """
        pass

    def CreateOperationComponent(self, entityId):
        # type: (Union[str,int]) -> 'OperationCompClient'
        """
        创建operation组件
        """
        pass

    def SetCanAll(self, flag):
        # type: (bool) -> 'bool'
        """
        同时设置SetCanMove，SetCanJump，SetCanAttack，SetCanWalkMode，SetCanPerspective，SetCanPause，SetCanChat，SetCanScreenShot，SetCanOpenInv，SetCanDrag，SetCanInair
        """
        pass

    def CreateDeviceComponent(self, entityId):
        # type: (Union[str,int]) -> 'DeviceCompClient'
        """
        创建device组件
        """
        pass

    def CreateParticleControlComponent(self, entityId):
        # type: (Union[str,int]) -> 'ParticleControlComp'
        """
        创建particleControl组件
        """
        pass

    def CreateParticleEntityBindComponent(self, entityId):
        # type: (Union[str,int]) -> 'ParticleEntityBindComp'
        """
        创建particleEntityBind组件
        """
        pass

    def BindParticleToEntity(self, particleId, bindEntityId, offset, rot, correction=False):
        # type: (int, str, Tuple[float,float,float], Tuple[float,float,float], bool) -> 'bool'
        """
        粒子特效绑定entity
        """
        pass

    def CreateParticleSkeletonBindComponent(self, entityId):
        # type: (Union[str,int]) -> 'ParticleSkeletonBindComp'
        """
        创建particleSkeletonBind组件
        """
        pass

    def BindParticleToSkeleton(self, particleId, modelId, boneName, offset, rot):
        # type: (int, int, str, Tuple[float,float,float], Tuple[float,float,float]) -> 'bool'
        """
        绑定粒子特效到骨骼模型
        """
        pass

    def CreateParticleTransComponent(self, entityId):
        # type: (Union[str,int]) -> 'ParticleTransComp'
        """
        创建particleTrans组件
        """
        pass

    def GetParticlePos(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[float,float,float]'
        """
        获取特效位置
        """
        pass

    def GetParticleRot(self, entityId):
        # type: (Union[str,int]) -> 'Tuple[float,float]'
        """
        获取特效角度
        """
        pass

    def SetParticlePos(self, entityId, pos):
        # type: (Union[str,int], Tuple[int,int,int]) -> 'bool'
        """
        设置特效位置
        """
        pass

    def SetParticleRot(self, entityId, rot):
        # type: (Union[str,int], Tuple[float,float]) -> 'bool'
        """
        设置特效的角度
        """
        pass

    def CreatePlayerViewComponent(self, playerId):
        # type: (Union[str,int]) -> 'PlayerViewCompClient'
        """
        创建playerView组件
        """
        pass

    def GetPlayerPerspective(self, playerId):
        # type: (Union[str,int]) -> 'int'
        """
        获取当前的视角模式
        """
        pass

    def SetPlayerPerspective(self, playerId, persp):
        # type: (Union[str,int], int) -> 'bool'
        """
        设置视角模式
        """
        pass

    def LockPlayerPerspective(self, playerId, persp):
        # type: (Union[str,int], int) -> 'bool'
        """
        锁定玩家的视角模式
        """
        pass

    def CreateQueryVariableComponent(self, entityId):
        # type: (Union[str,int]) -> 'QueryVariableComponentClient'
        """
        创建queryVariable组件
        """
        pass

    def CreateSkyRenderComponent(self, entityId):
        # type: (Union[str,int]) -> 'SkyRenderCompClient'
        """
        创建skyRender组件
        """
        pass

    def CreateTextBoardComponent(self, entityId):
        # type: (Union[str,int]) -> 'TextBoardComponentClient'
        """
        创建textBoard组件
        """
        pass

    def CreateTextNotifyClientComponent(self, entityId):
        # type: (Union[str,int]) -> 'TextNotifyComponet'
        """
        创建textNotifyClient组件
        """
        pass

    def CreateConfigClientComponent(self, levelId):
        # type: (str) -> 'ConfigCompClient'
        """
        创建config组件
        """
        pass

    def CreateVirtualWorldComponent(self, levelId):
        # type: (str) -> 'VirtualWorldCompClient'
        """
        创建virtualWorld组件实例组件
        """
        pass

    def CreatePlayerAnimComponent(self, playerId):
        # type: (str) -> 'PlayerAnimCompClient'
        """
        创建玩家动画组件
        """
        pass

    def CreatePostProcessComponent(self):
        # type: () -> 'PostProcessComponent'
        """
        创建PostProcess组件
        """
        pass

