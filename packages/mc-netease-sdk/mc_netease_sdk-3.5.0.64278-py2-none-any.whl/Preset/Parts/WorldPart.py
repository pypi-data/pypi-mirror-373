# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.TypeMeta import PBool, PStr, PInt, PCustom, PVector3, PVector3TF, PEnum, PDict, PFloat, PArray, PVector2, PCoordinate
from Preset.Model import PartBaseMeta


@sunshine_class_meta
class WorldPartMeta(PartBaseMeta):
    def _cheatInfo(self):
        if self.cheat:
            return {'visible': True}
        else:
            return {'visible': False}

    def _stable_time(self):
        _property = {"editable": True, "sort": 6, "text": "固定时间", "default": 6000, "enumType": "StableTime", 'tip': '选择不开启昼夜更替时，时间停留在哪一刻。'}
        if self.cheatInfo:
            daylight_cycle = self.cheatInfo.get("daylight_cycle")
            if daylight_cycle:
                _property["editable"] = False
        return _property

    CLASS_NAME = "WorldPart"
    PROPERTIES = {
        'gameMode':
            PEnum(sort=6, text="游戏模式", enumType="GameType"),
        'difficulty':
            PEnum(sort=7, text="游戏难度", enumType="Difficulty"),
        'optionInfo':
            PDict(
                sort=9,
                text="世界选项",
                children={
                    'pvp': PBool(sort=0, text="开启玩家互相伤害", tip='是否允许玩家互相造成伤害。'),
                    'show_coordinates': PBool(sort=0, text="显示坐标", tip='是否在主界面左上角显示当前坐标位置。'),
                    'fire_spreads': PBool(sort=0, text="火焰蔓延", tip='若取消勾选，则阻止火在方块之间蔓延、摧毁方块、自己熄灭或被雨扑灭。'),
                    'tnt_explodes': PBool(sort=0, text="TNT爆炸", tip='TNT是否可被点燃。'),
                    'mob_loot': PBool(sort=0, text="生物战利品", tip='控制生物在死亡时是否掉落战利品。'),
                    'natural_regeneration': PBool(sort=0, text="自然生命恢复", tip='玩家饥饿条满时，是否会恢复生命值。'),
                    'tile_drops': PBool(sort=0, text="方块掉落", tip='方块被破坏时是否掉落方块物品。')
                },
            ),
        "cheat":
            PBool(sort=10, text="作弊模式", default=True, tip='若开启，玩家可使用命令，且可选择多种作弊选项。'),
        "cheatInfo":
            PDict(
                func=_cheatInfo,
                text="作弊选项",
                sort=11,
                children={
                    'daylight_cycle': PBool(sort=0, text="开启昼夜更替", default=True, tip='若取消勾选，则时间不会前进。'),
                    'stable_time': PEnum(func=_stable_time),
                    'keep_inventory': PBool(sort=2, text="保留物品栏", tip='玩家死亡时是否保留背包中的物品。'),
                    'mob_spawn': PBool(sort=3, text="生物生成", tip='是否自然生成生物。'),
                    'mob_griefing': PBool(sort=4, text="生物破坏", tip='是否允许生物破坏方块。'),
                    'entities_drop_loot': PBool(sort=5, text="实体掉落战利品", tip='控制矿车和盔甲架等物品在损坏后是否会掉落矿车和盔甲架。'),
                    'weather_cycle': PBool(sort=6, text="天气更替", tip='天气是否更替变化。'),
                    'command_blocks_enabled': PBool(sort=7, text="启用命令方块", tip='命令方块是否生效。'),
                    'random_tick_speed': PInt(sort=8, text="随机刻速度", min=1, tip='影响植物生长、树叶凋零、火焰蔓延等的速度。')
                },
            ),
        "spawn":
            PCoordinate(text="初始复活点", sort=12, visible=False),
        'storyline':
            PCustom(
                text="逻辑文件", sort=15, editAttribute="ETSWidget", default="", tip='可挂接通过逻辑编辑器制作的ets文件，可实现一些简单的逻辑。',
                pack="behavior", baseFolder=["storyline"], extension=".ets", withExtension=True, description="ets"
            )
    }


from Preset.Model.PartBase import PartBase

class WorldPart(PartBase):
    def __init__(self):
        # type: () -> 'None'
        """
        世界属性零件
        """
        self.gameMode = None
        self.difficulty = None
        self.cheat = None

