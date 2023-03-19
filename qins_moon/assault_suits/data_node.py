#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_node.py
# @time: 3/10/2023 5:56 PM
import random
from typing import List, Dict

import numpy

from qins_moon.core.utils.data_structure import NameIdTableStructure, LocationsIdTableStructure, LocIdsTableStructure, \
    LocIdTableStructure, TableRowBase
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

        self.monsterDistribution = LocIdTableStructure[MonsterDistributionNode](open_kdtree=True)
        self.tankSoftDict = LocIdsTableStructure[TankNode]()
        self.messengerDict = LocIdTableStructure[MessengerNode]()

        self.personSoftDict = LocIdsTableStructure[PersonNode]()

    @property
    def map_size(self):
        return tuple(reversed(self.terrainMap.shape))


class RunTimeNode:
    def __init__(self):
        self.currentViewSystem = 0

        self.currentMoney = 0
        self.groupPersons: List[PersonNode] = []
        self.currentAttackTargets: List[MonsterNode] = []  # 临时new
        self.currentStatement: str | None = None
        self.currentDirection = 1, 0
        self.sellListId = 0

        self.wantedBeaten = set()


class AssaultSuitsDataNode:
    def __init__(self):
        self.dataTable = AssaultSuitsDataTable()
        self.config: ConfigBase | None = None

        self.subWorldDict = LocationsIdTableStructure[WorldNodeBase]()

        self.bigWorldNode: WorldNodeBase | None = None
        self.currentWorldNode: WorldNodeBase | None = None

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

        wn = WorldNodeBase()
        wn.id = 0
        wn.terrainMap = numpy.random.randint(1, 5, (height, width), numpy.int_)
        wn.buildingMap = numpy.zeros((height, width), numpy.int_)
        wn.decorationMap = numpy.zeros((height, width), numpy.int_)
        rlt.bigWorldNode = wn
        rlt.subWorldDict.add(wn)
        rlt.currentWorldNode = wn

        rlt.make_person(0, (0, 0), 1)
        return rlt

    def modify_current_world(self, world_id):
        self.currentWorldNode = self.subWorldDict[world_id]

    def make_person(self, world_id, loc, table_id):
        p = PersonNode()
        p.worldId = world_id
        p.id = self.personDict.get_unique_id()
        p.loc = loc
        p.tableRowId = table_id
        self.personDict.add(p)
        # if world_id == 0:
        #     self.personSoftDict.add(p)
        # else:
        self.subWorldDict[world_id].personSoftDict.add(p)
        self.runTimeNode.groupPersons.append(p)
        return p

    def del_person(self, world_id, id_):
        del self.personDict[id_]
        del self.subWorldDict[world_id].personSoftDict[id_]
        p = self.personDict[id_]
        self.runTimeNode.groupPersons.remove(p)

    def move_person(self, id_, world_id, loc):
        self.personDict.move_by_id(id_, loc)
        p = self.personDict[id_]
        del self.subWorldDict[p.worldId].personSoftDict[p.loc]
        p.loc = loc
        self.subWorldDict[world_id].personSoftDict.add(p)
        p.worldId = world_id

    # region monster
    def make_monster(self, loc, table_id):
        pass

    def make_monster_group(self, loc, table_id):
        pass

    def clear_monster(self):
        self.runTimeNode.currentAttackTargets.clear()

    # endregion

    # region about edit

    def make_under_goods(self, world_id, table_row_id, loc):
        ug = UnderGoodsNode()
        ug.tableRowId = table_row_id
        ug.loc = loc
        ug.name = str(ug.loc)
        # if world_id == 0:
        #     ug.id = self.underGoodsDict.get_unique_id()
        #     self.underGoodsDict.add(ug)
        # else:
        ug.id = self.subWorldDict[world_id].underGoodsDict.get_unique_id()
        self.subWorldDict[world_id].underGoodsDict.add(ug)
        return ug

    def make_messenger(self, world_id, table_row_id, loc):
        ug = MessengerNode()
        ug.tableRowId = table_row_id
        ug.loc = loc
        ug.name = str(ug.loc)
        ug.tankTableRowId = self.dataTable.messengerTable[table_row_id].tankTableRowId

        # if world_id == 0:
        #     ug.id = self.messengerDict.get_unique_id()
        #     self.messengerDict.add(ug)
        # else:
        ug.id = self.subWorldDict[world_id].messengerDict.get_unique_id()
        self.subWorldDict[world_id].messengerDict.add(ug)
        return ug

    def make_monster_distribution(self, world_id, table_row_id, loc):
        ug = MonsterDistributionNode()
        ug.tableRowId = table_row_id
        ug.loc = loc
        ug.name = str(ug.loc)
        # if world_id == 0:
        #     ug.id = self.monsterDistribution.get_unique_id()
        #     self.monsterDistribution.add(ug)
        # else:
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
        # if world_id == 0:
        #     self.tankSoftDict.add(ug)
        # else:
        self.subWorldDict[world_id].tankSoftDict.add(ug)
        return ug

    def del_under_goods(self, world_id, id_):
        del self.subWorldDict[world_id].underGoodsDict[id_]

    def del_messenger(self, world_id, id_):
        del self.subWorldDict[world_id].messengerDict[id_]

    def del_monster_distribution(self, world_id, id_):
        del self.subWorldDict[world_id].monsterDistribution[id_]

    def del_tank(self, world_id, id_):
        del self.tankDict[id_]
        del self.subWorldDict[world_id].tankSoftDict[id_]

    def move_under_goods(self, world_id, id_, n_loc):
        self.subWorldDict[world_id].underGoodsDict.move_by_id(id_, n_loc)

    def move_messenger(self, world_id, id_, n_loc):
        self.subWorldDict[world_id].messengerDict.move_by_id(id_, n_loc)

    def move_monster_distribution(self, world_id, id_, n_loc):
        self.subWorldDict[world_id].monsterDistribution.move_by_id(id_, n_loc)

    def move_tank(self, id_, world_id, loc):
        self.tankDict.move_by_id(id_, loc)
        p = self.tankDict[id_]
        del self.subWorldDict[p.worldId].tankSoftDict[p.loc]
        p.loc = loc
        self.subWorldDict[world_id].tankSoftDict.add(p)
        p.worldId = world_id
    # endregion
