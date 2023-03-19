#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_node.py
# @time: 3/12/2023 11:41 AM
import random
from typing import List

import numpy

from qins_moon.core.asset import ConfigBase
from qins_moon.core.utils.data_structure import LocIdTableStructure, NameIdTableStructure
from qins_moon.advw.data_table import AdvwDataTable
from qins_moon.qm.tile_map.data_struction import IDataNodeInterface


class BuildingNode:
    def __init__(self):
        self.id = 0
        self.loc = 0, 0
        self.name = ''
        self.tableRowId = 0
        self.flagId = 0

        self.occupiedValue = 0


class MilitaryNode:
    def __init__(self):
        self.id = 0
        self.loc = 0, 0
        self.name = ''
        self.tableRowId = 0
        self.flagId = 0

        self.currentBlood = 0
        self.maxBlood = 10
        self.currentOil = 10
        self.currentBullet = 10
        self.isHidden = False
        self.acted = False

        self.heroId = 0
        self.loadings: List['MilitaryNode'] = []


class HeroNode:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.tableRowId = 0
        self.currentBlue = 0
        self.flagId = 0


class PlayerNode:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.flagId = 0

        self.isFailed = False
        self.isComputer = False
        self.currentBout = 0

        self.hero: HeroNode | None = None
        self.money = 100000


class AdvwDataNode(IDataNodeInterface):
    def __init__(self):
        self.dataTable: AdvwDataTable | None = None
        self.config: ConfigBase | None = None

        self.terrainMap: numpy.ndarray | None = None
        self.trafficMap: numpy.ndarray | None = None
        self.decorationMap: numpy.ndarray | None = None

        self.buildingDict = LocIdTableStructure[BuildingNode]()
        self.militaryDict = LocIdTableStructure[MilitaryNode]()
        self.playerDict = NameIdTableStructure[PlayerNode]()

        self.currentPlayerId = 0
        self.currentWeather = ''

    def map_size(self):
        return tuple(reversed(self.terrainMap.shape))

    @staticmethod
    def make_data(map_size, dt, seed=100):
        width, height = map_size
        random.seed(seed)
        numpy.random.seed(seed)
        rlt = AdvwDataNode()
        rlt.dataTable = dt
        rlt.terrainMap = numpy.random.randint(1, 5, (height, width), numpy.int_)
        rlt.trafficMap = numpy.zeros((height, width), numpy.int_)
        rlt.decorationMap = numpy.zeros((height, width), numpy.int_)

        # red_player = PlayerNode()
        # red_player.id = red_player.flagId = 1
        # red_player.name = 'red'
        # rlt.playerDict.add(red_player)
        # blue_player = PlayerNode()
        # blue_player.id = blue_player.flagId = 2
        # blue_player.name = 'blue'
        # rlt.playerDict.add(blue_player)

        # print(rlt.make_military(1, (5, 4), 1).id)

        return rlt

    def make_building(self, table_id, loc, flag):
        b = BuildingNode()
        b.id = self.buildingDict.get_unique_id()
        b.tableRowId = table_id
        b.flagId = flag
        b.loc = loc
        b.name = str(b.loc)
        self.buildingDict.add(b)
        return b

    def make_military(self, table_id, loc, flag):
        b = MilitaryNode()
        b.id = self.militaryDict.get_unique_id()
        b.tableRowId = table_id
        b.flagId = flag
        b.loc = loc
        b.name = str(b.loc)
        b_t = self.dataTable.militaryTable[table_id]
        b_t_battle = self.dataTable.battlePropertyTable[b_t.battleProperty]
        b_t_move = self.dataTable.movePropertyTable[b_t.moveProperty]
        b.currentBlood = b_t_battle.bloodValue
        b.currentOil = b_t_move.maxOil
        b.currentBullet = b_t_battle.maxBullet
        self.militaryDict.add(b)
        return b

    def del_building(self, loc):
        del self.buildingDict[loc]

    def del_military(self, loc):
        del self.militaryDict[loc]

    def move_military(self, o_loc, n_loc):
        o_m = self.militaryDict[o_loc]
        n_m = self.militaryDict[n_loc]
        if n_m is not None:
            n_m.loadings.append(o_m)
            del self.militaryDict[o_loc]
        else:
            self.militaryDict.move_by_id(o_m.id, n_loc)

    def count_attack_rlt(self, a_loc, d_loc):
        a_m = self.militaryDict[a_loc]
        d_m = self.militaryDict[d_loc]
        distance = abs(a_loc[0]-d_loc[0]) + abs(a_loc[1]-d_loc[1])

        if a_m.currentBullet == 0:
            return
        dt = self.dataTable
        a_table = dt.militaryTable[a_m.tableRowId]
        d_table = dt.militaryTable[d_m.tableRowId]
        a_battle = dt.battlePropertyTable[a_table.battleProperty]
        d_battle = dt.battlePropertyTable[d_table.battleProperty]

        a_terrain = dt.terrainTerrainTable[int(self.terrainMap[a_loc[1], a_loc[0]])].name
        d_terrain = dt.terrainTerrainTable[int(self.terrainMap[d_loc[1], d_loc[0]])].name

        a_value = dt.atkDefDictTable[a_battle.attackType][d_battle.bloodType] * \
            dt.terrainAttackDictTable[a_terrain][a_battle.attackType] * \
            dt.terrainDefenseDictTable[d_terrain][d_battle.bloodType] * \
            a_m.currentBlood / 10 * a_battle.attackValue
        if a_value <= 0:  # 无法攻击
            return

        a_m.currentBullet -= 1

        d_m.currentBlood -= a_value
        if d_m.currentBlood <= 0:
            self.del_military(d_loc)
            return
        if not d_table.canBeatBack or d_m.currentBullet == 0 or distance > 1:  # 无法反击
            return
        b_value = dt.atkDefDictTable[d_battle.attackType][a_battle.bloodType] * \
            dt.terrainDefenseDictTable[a_terrain][a_battle.attackType] * \
            dt.terrainAttackDictTable[d_terrain][d_battle.bloodType] * \
            d_m.currentBlood / 10 * d_battle.attackValue

        if b_value <= 0:
            return
        d_m.currentBullet -= 1
        a_m.currentBlood -= b_value
        if a_m.currentBlood <= 0:
            self.del_military(a_loc)

    def make_player(self, flag, name, hero_table_id):
        p = PlayerNode()
        p.id = flag
        p.flagId = flag
        p.name = name
        p.hero = HeroNode()
        p.hero.flagId = flag
        p.hero.tableRowId = hero_table_id
        self.playerDict.add(p)
        return p
