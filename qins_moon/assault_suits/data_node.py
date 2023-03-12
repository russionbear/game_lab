#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_node.py
# @time: 3/10/2023 5:56 PM
import random

import numpy

from qins_moon.core.utils.data_structure import NameIdTableStructure, LocationsIdTableStructure, LocIdsTableStructure, \
    LocIdTableStructure
from qins_moon.core.director import TickEventLoop
from qins_moon.core.asset import ConfigBase

from qins_moon.assault_suits.data_table import AssaultSuitsDataTable


class LocationNodeBase:
    def __init__(self):
        self.id = 0
        self.name = 0
        self.loc = 0, 0


class TankNode(LocationNodeBase):
    def __init__(self):
        super().__init__()
        self.tableRowId = 0

        self.worldId = 0
        self.id = 0
        self.name = 0
        self.loc = 0, 0

        self.mainWeaponDevice = 0, 0, 0
        self.secondWeaponDevice = 0, 0, 0
        self.seWeaponDevice = 0, 0, 0
        self.cDevice = 0, 0
        self.classicDevice = 0, 0
        self.engineDevice = 0, 0

        self.restDevices = []
        self.tools = []

        self.restWeight = 0
        self.armor = 90


class PersonNode(LocationNodeBase):
    def __init__(self):
        super().__init__()
        self.tableRowId = 0

        self.worldId = 0
        self.id = 0
        self.name = 0
        self.loc = 0, 0

        self.level = 1
        self.experienceToNextLevel = 0

        self.weaponEquip = 0
        self.innerClothEquip = 0
        self.clothEquip = 0
        self.capEquip = 0
        self.shoeEquip = 0
        self.handEquip = 0

        self.tools = []

        self.currentBlood = 0
        self.currentMaxBlood = 0
        self.tankId = 0


class MessengerNode(LocationNodeBase):
    def __init__(self):
        super().__init__()
        self.isWander = False
        self.statement = ""
        self.tankTableRowId = 1
        self.tableRowId = 0


class MonsterNode(LocationNodeBase):
    def __init__(self):
        super().__init__()
        self.tableRowId = 0
        self.tankNode: TankNode | None = None
        self.personNode: PersonNode | None = None


class UnderGoodsNode(LocationNodeBase):
    def __init__(self):
        super().__init__()
        self.tableRowId = 0


class MonsterDistributionNode(LocationNodeBase):
    def __init__(self):
        super().__init__()
        self.tableRowId = ''


class WorldNodeBase:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.locations = []

        self.terrainMap: numpy.ndarray | None = None
        self.buildingMap: numpy.ndarray | None = None
        self.decorationMap: numpy.ndarray | None = None

        self.underGoodsDict = LocIdTableStructure[UnderGoodsNode]()

        self.monsterDistribution = LocIdTableStructure[MonsterDistributionNode]()
        self.tankSoftDict = LocIdsTableStructure[TankNode]()
        self.messengerDict = LocIdTableStructure[MessengerNode]()

        self.personSoftDict = LocIdsTableStructure[PersonNode]()


class RunTimeNode:
    def __init__(self):
        self.currentViewSystem = 0

        self.currentMoney = 0
        self.groupPersons = []
        self.currentAttackTargets = []  # 临时new
        self.currentStatement = ""
        self.currentDirection = 1, 0
        self.sellListId = 0

        self.wantedBeaten = set()


class AssaultSuitsDataNode(WorldNodeBase):
    def __init__(self):
        super().__init__()
        self.dataTable = AssaultSuitsDataTable()
        self.config: ConfigBase | None = None

        self.subWorldDict = LocationsIdTableStructure[WorldNodeBase]()
        self.bigWorldNode: WorldNodeBase | None = None

        self.tankDict = LocIdsTableStructure[TankNode]()
        self.personDict = LocIdsTableStructure[PersonNode]()

        self.runTimeNode = RunTimeNode()

    @staticmethod
    def make_data(map_size, dt, seed=100):
        width, height = map_size
        random.seed(seed)
        numpy.random.seed(seed)
        rlt = AssaultSuitsDataNode()
        rlt.dataTable = dt
        rlt.terrainMap = numpy.random.randint(1, 5, (height, width), numpy.int_)
        rlt.buildingMap = numpy.zeros((height, width), numpy.int_)
        rlt.decorationMap = numpy.zeros((height, width), numpy.int_)
        rlt.make_person(0, (0, 0), 1)
        return rlt

    @property
    def map_size(self):
        return tuple(reversed(self.terrainMap.shape))

    def make_person(self, world_id, loc, table_id):
        p = PersonNode()
        p.worldId = world_id
        p.id = self.personDict.get_unique_id()
        p.loc = loc
        p.tableRowId = table_id
        self.personDict.add(p)
        if world_id == 0:
            self.personSoftDict.add(p)
        else:
            self.subWorldDict[world_id].personSoftDict.add(p)
        return p

    def make_monster(self, loc, table_id):
        pass

    def make_monster_group(self, loc, table_id):
        pass

    def clear_monster(self):
        pass

    # about edit

    def make_under_goods(self, world_id, table_row_id, loc):
        ug = UnderGoodsNode()
        ug.tableRowId = table_row_id
        ug.loc = loc
        ug.name = str(ug.loc)
        if world_id == 0:
            ug.id = self.underGoodsDict.get_unique_id()
            self.underGoodsDict.add(ug)
        else:
            ug.id = self.subWorldDict[world_id].underGoodsDict.get_unique_id()
            self.subWorldDict[world_id].underGoodsDict.add(ug)
        return ug

    def make_messenger(self, world_id, table_row_id, loc):
        ug = MessengerNode()
        ug.tableRowId = table_row_id
        ug.loc = loc
        ug.name = str(ug.loc)
        ug.tankTableRowId = self.dataTable.messengerTable[table_row_id].tankTableRowId

        if world_id == 0:
            ug.id = self.messengerDict.get_unique_id()
            self.messengerDict.add(ug)
        else:
            ug.id = self.subWorldDict[world_id].messengerDict.get_unique_id()
            self.subWorldDict[world_id].messengerDict.add(ug)
        return ug

    def make_monster_distribution(self, world_id, table_row_id, loc):
        ug = MonsterDistributionNode()
        ug.tableRowId = table_row_id
        ug.loc = loc
        ug.name = str(ug.loc)
        if world_id == 0:
            ug.id = self.monsterDistribution.get_unique_id()
            self.monsterDistribution.add(ug)
        else:
            ug.id = self.subWorldDict[world_id].monsterDistribution.get_unique_id()
            self.subWorldDict[world_id].monsterDistribution.add(ug)
        return ug

    def make_tank(self, world_id, loc, table_id):
        ug = TankNode()
        ug.loc = loc
        ug.tableRowId = table_id
        ug.name = str(ug.loc)
        ug.id = self.tankDict.get_unique_id()
        self.tankDict.add(ug)
        if world_id == 0:
            self.tankSoftDict.add(ug)
        else:
            self.subWorldDict[world_id].tankSoftDict.add(ug)
        return ug


# controller
# view: world, attack, talk


# 行为文本格式化
class AssaultSuitsController:
    def __init__(self, dn):
        self.rootDataNode: AssaultSuitsDataNode = dn

    def modify_terrain(self,
                       terrain_dict, building_dict, decoration_dict, world_id_dict, under_goods_dict,
                       messenger_dict):
        pass

    # world system

    def transfer_group(self, loc):
        pass

    def move_group(self, direction):
        pass

    def to_detect(self):
        pass

    def use_goods(self, from_i, goods_order):
        pass

    def use_goods_by_name(self, name):
        pass

    def modify_armor(self, from_i, value_str):
        pass

    def modify_money(self, money_str):
        pass

    # region equipment

    def move_device(self, goods_order, from_i, to_i):
        pass

    def drop_device(self, goods_order, from_i):
        pass

    def equip_tank_device(self, goods_order, from_i):
        pass

    def move_tank_tool(self, tool_i, from_i, to_i):
        pass

    def move_equip(self, goods_order, from_i, to_i):
        pass

    def drop_equip(self, goods_order, from_i):
        pass

    def equip_person_equip(self, goods_order, from_i):
        pass

    def move_person_tool(self, tool_i, from_i, to_i):
        pass

    # endregion

    # attack system
    def to_attack(self, monster_group_id):
        pass

    def send_attack_actions(self, actions):
        pass

    # talk system
    def to_talk(self, statement_name):
        pass

    def to_statement(self, statement_name):
        pass

    # region buy system

    def to_buy(self, sell_list_id):
        pass

    def buy_goods(self, goods_order, to_i):
        pass

    def sell_tank_goods(self, goods_order, from_i):
        pass

    def sell_person_goods(self, goods_order, from_i):
        pass

    def exit_buy(self):
        pass
    # endregion


# trigger
# in/out area, after attack, fond goods, after talk, use tool, after sleep, timeout
#
# event
# about attack: after attack suc/fail
# about world:
#   modify map terrain, building, decoration, subWorld, messenger[action, statements], under goods
#   modify device/equip/tool, money, blood
#   modify partner
#   to world loc, to attack, to buy list
# about use tool:
#   scan, drink


class TriggerBase:
    def __init__(self, dn):
        self.id = 0
        self.name = 0
        self.rootDataNode: AssaultSuitsDataNode = dn


class MoveTrigger(TriggerBase):
    def __init__(self, dn):
        super().__init__(dn)


class TriggerManager:
    def __init__(self):
        pass


# if __name__ == '__main__':
#     _dn = AssaultSuitsDataNode.make_map(16, 16)
#     _ctrl = AssaultSuitsController(_dn)
