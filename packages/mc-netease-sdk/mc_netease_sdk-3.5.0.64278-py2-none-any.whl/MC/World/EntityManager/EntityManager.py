# -*- coding: utf-8 -*-


class EntityManager(object):
    creatureEnumData = {}  # 原生生物和自定义生物
    extraCreatureEnumData = {}  # 自定义生物

    @staticmethod
    def getCreatureEnum():
        return EntityManager.creatureEnumData

    @staticmethod
    def getExtraCreatureEnum():
        return EntityManager.extraCreatureEnumData
