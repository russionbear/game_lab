#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :data_node.py
# @Time      :07/01/2023
# @Author    :russionbear
# @Function  :function
import random
import time
from typing import Dict, List, Set, Tuple

import numpy
from qins_moon.core.utils.data_structure import LocIdTableStructure, NameIdTableStructure, LocIdsTableStructure, \
    LocationsIdTableStructure
from qins_moon.qm.polity.data_table import PolityDataTable


class GroupBase:
    def __init__(self):
        self.id = 0
        self.name = ""
        self.flag = 0
        self.belong = 0


class TeamNode(GroupBase):
    def __init__(self):
        super().__init__()
        # self.type: int = t

        self.loc = 0, 0
        self.staff = []
        self.storage = {}
        # self.header: int = 0
        # self.restStaff: List[int] = []
        # self.population = 0
        self.moveTarget = 0, 0


class BatMenNode(TeamNode):
    def __init__(self):
        super().__init__()
        self.currentMode = 0  # transport, spy, steal, attack, damage, defense
        self.transportProperty = 0, 0
        self.needStorage = {}


class CityNode(GroupBase):
    def __init__(self):
        super().__init__()
        self.locations = []
        self.maxBlockNu = 100
        self.tableRowId = 0

        # people
        self.population = 90
        self.popularSupport = 0.9
        self.talentCapacity = 0.5  # 人才相关
        self.baseFightingCapacity = 1  # 训练相关

        # 物资
        self.storageId = 0

        # 军事
        self.wallArmor = 1.2

        # 市场
        self.buildings: Dict[str, int] = {}  # provide(people per res), need()[过量自动清除];;good price
        self.needResource = set()  # 不包括extra
        self.extraNeedResource = set()
        self._lastExportResource: Dict[str, float | int] = {}
        # self.extraNeedResource: Dict[str, int] = {}
        # self.provideResource = {}

        self.tax = 0.1

        # 地下利润
        self.underTax = 0.1
        self.underTaxDistribution = {}

    def adjust_demand_supply(self, dt: PolityDataTable):
        self.needResource.clear()
        for k in self.buildings.keys():
            building_d = dt.buildingTable[k]
            for goods in building_d.provide:
                goods_d = dt.goodsTable[goods]
                for k1 in goods_d.madeFrom.keys():
                    self.needResource.add(k1)


class StorageNode(GroupBase):
    def __init__(self):
        super().__init__()
        self.goods = {}
        self.modifyTime = 0
        self.loc = 0, 0


class MilitaryNode:
    def __init__(self):
        self.tableRowId = 0
        self.militaryBlood = 1


class TroopNode(TeamNode):
    def __init__(self):
        super().__init__()
        self.innerTeams = []
        self.militaryForce = {}
        self.costPerTick: float = 0
        self.moveProperty = ""
        self.battleProperty = ""

        self.operaMoved = False
        self.operaHidden = False
        self.currentStatus = []

        self.needStorage = {}


class FerryNode(TeamNode):
    def __init__(self):
        super().__init__()
        self.loc = 0, 0
        self.tableRowId = 0
        self.maxCapacity = 100
        self.restCapacity = 0
        self.goods = {}

        self.stations = []
        self.currentStationIndex = 0


class PersonNode(GroupBase):
    def __init__(self):
        super().__init__()
        self.inArmy = False


"""
food, mine, 
"""


class GroupNode(GroupBase):
    def __init__(self):
        super().__init__()
        self.header = 0
        self.teams = []  # 亲兵
        self.subGroup: List[int] = []

        self.ferries: List[int] = []
        self.militaries: List[int] = []
        self.cities: List[int] = []
        self.storages = []


class RunTimeNode:
    def __init__(self):
        self.lockedPoints = set()


class PolityDataNode:
    def __init__(self):
        # header
        self.dataTableId = "", ""
        self.resourcePackageId = "", ""
        self.dataTable: PolityDataTable | None = None

        # basic data
        self.terrainMap: numpy.ndarray = numpy.zeros((), numpy.uint8)
        self.trafficMap: numpy.ndarray = numpy.zeros((), numpy.uint8)
        self.resourceMap: numpy.ndarray = numpy.zeros((), numpy.int_)
        self.personDict = NameIdTableStructure[PersonNode]()
        self.cityDict = LocationsIdTableStructure[CityNode]()
        self.storageDict = LocIdsTableStructure[StorageNode]()
        self.teamDict = LocIdsTableStructure[TeamNode]()  # 间谍、小规模力量、团体
        self.ferryDict = LocIdsTableStructure[FerryNode]()
        self.troopDict = LocIdTableStructure[TroopNode]()

        # group data
        # self.buildingDict = LocIdTableStructure[BuildingNode]()
        self.groupDict = NameIdTableStructure[GroupNode]()
        self.topGroupEnemyShip: Set[Tuple[int, int]] = set()
        self.topGroups = []

        self.runtimeNode = RunTimeNode()

        self.interval = 1
        self.__currentInterval = 0

    @property
    def map_size(self):
        return tuple(reversed(self.terrainMap.shape))

    # ############# init map
    @staticmethod
    def make_data(map_size, dt: PolityDataTable, seed=None):
        if seed is not None:
            random.seed(seed)
            numpy.random.seed(seed)
        rlt = PolityDataNode()
        rlt.mapSize = map_size
        rlt.dataTableId = dt.dataTableId
        rlt.dataTable = dt
        rlt.terrainMap = numpy.random.randint(0, len(dt.terrainTerrainTable.idDict) - 1,
                                              (map_size[1], map_size[0]), numpy.uint8)
        for i, j in enumerate(sorted(dt.terrainTerrainTable.idDict.keys(), reverse=True)):
            rlt.terrainMap[rlt.terrainMap == len(dt.terrainTerrainTable.idDict) - 1 - i] = j

        # traffic
        rlt.trafficMap = numpy.random.randint(0, 2, (map_size[1], map_size[0]), numpy.uint8)
        rlt.trafficMap[0, 0] = 1
        rlt.trafficMap[1, 0] = 1

        # make cities
        city_loc = set()
        while len(city_loc) < map_size[0] * map_size[1] // 25:
            city_loc.add((random.randint(0, map_size[0]-1), random.randint(0, map_size[1]-1)))
        city_rows = [i.id for i in dt.cityLevelTable.idDict.values()]
        for i in city_loc:
            tmp_city = rlt.make_city(i, random.choice(city_rows))
            tmp_city.name = str(tmp_city.id)

        # make group & army &
        city_loc = list(city_loc)
        group_road_mark = False
        for i in range(2):
            group_1 = rlt.make_group(city_loc[i])
            rlt.topGroups.append(group_1.id)
            rlt.appoint_city(rlt.cityDict[city_loc[i]].id, group_1.id)
            if not group_road_mark:
                army_1 = rlt.make_troop(city_loc[i])
                army_1.name = str(army_1.id)
                rlt.appoint_troop(army_1.id, group_1.id)
                for j in [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]:
                    tmp_loc = city_loc[i][0] + j[0], city_loc[i][1] + j[1]
                    army_1 = rlt.make_troop(tmp_loc)
                    army_1.name = str(army_1.id)
                    rlt.appoint_troop(army_1.id, group_1.id)
                group_road_mark = True

        # top group
        group_ids = list(rlt.groupDict.idDict.keys())
        for y in range(len(group_ids)):
            for x in range(y+1, len(group_ids)):
                rlt.topGroupEnemyShip.add((min(group_ids[y], group_ids[x]), max(group_ids[y], group_ids[x])))

        # teams (wait for russionbear 's update)

        return rlt

    def get_name(self, t, s=None):
        if t in self.dataTable.namesListTable:
            q = self.dataTable.namesListTable[t]
            if len(q) != 0:
                return q[random.randint(0, len(q)-1)]
        if s is not None:
            while True:
                name = hex(random.randint(0x0000, 0xffff))
                if name in s:
                    continue
                return name
        return hex(random.randint(0x0000, 0xffff))

    # ############# city
    def make_city(self, loc, tbi):
        city = CityNode()
        city.id = self.cityDict.get_unique_id()
        city.tableRowId = tbi
        table = self.dataTable.cityLevelTable[tbi]
        city.maxBlockNu = table.maxBlockNu
        for y in range(table.areaSize[1]):
            for x in range(table.areaSize[0]):
                city.locations.append((y+loc[0], x+loc[1]))
        city.population = table.population
        city.baseFightingCapacity = table.baseFightingCapacity
        self.cityDict.add(city)
        city.storageId = self.make_storage(loc).id
        return city

    def del_city(self, id_):
        self.appoint_city(id_, 0)
        del self.cityDict[id_]

    def appoint_city(self, id_, t_id):
        city = self.cityDict[id_]
        if city.belong != 0:
            cities = self.groupDict[city.belong].cities
            if id_ in cities:
                cities.remove(id_)

        if t_id != 0:
            group = self.groupDict[t_id]
            cities = group.cities
            if id_ not in cities:
                cities.append(id_)
            city.flag = group.flag
        else:
            city.flag = 0

        city.belong = t_id

    def modify_building_nu(self, city_id, building, nu) -> bool:
        if nu < 0:
            nu = 0
        building_d = self.dataTable.buildingTable[building]
        city_n = self.cityDict[city_id]
        made_cost = building_d.madeFrom
        current_nu = city_n.buildings.get(building_d.name, 0)
        need_nu = nu - current_nu
        city_storage = self.storageDict[city_n.storageId].goods
        if need_nu <= 0:
            for k, v in made_cost:
                if k not in city_storage:
                    city_storage[k] = 0
                city_storage[k] += abs(need_nu) * v * 0.6
            city_n.buildings[building_d.name] = nu

            city_n.adjust_demand_supply(self.dataTable)
            return True
        else:
            for k, v in made_cost:
                if k not in city_storage:
                    return False
                if city_storage[k] < abs(need_nu) * v:
                    return False

            city_n.buildings[building_d.name] = nu
            for k, v in made_cost:
                city_storage[k] -= v
            city_n.adjust_demand_supply(self.dataTable)
            return True

    # ############# person

    def make_person(self, name=None):
        rlt = PersonNode()
        rlt.id = self.personDict.get_unique_id()
        if name is None:
            rlt.name = ('\\u'+str(rlt.id % 10000).ljust(4, '0')).encode('utf-8').decode('unicode_escape')
            # rlt.name = self.get_name('person', self.personDict.nameDict)
        else:
            rlt.name = name
        self.personDict.add(rlt)
        return rlt

    def del_person(self, id_):
        self.appoint_person(id_, 0)
        del self.personDict[id_]

    def rename_person(self, id_, new_name):
        self.personDict.rename(id_, new_name)

    def appoint_person(self, id_, t_id):
        person = self.personDict[id_]
        if person.belong != 0:
            if person.inArmy:
                staff = self.troopDict[person.belong].staff
            else:
                staff = self.teamDict[person.belong].staff
            if id_ in staff:
                staff.remove(id_)

        if t_id != 0:
            if person.inArmy:
                team = self.troopDict[t_id]
            else:
                team = self.teamDict[t_id]
            staff = team.staff
            if id_ not in staff:
                staff.append(id_)
            person.flag = team.flag
        else:
            person.flag = 0

        person.belong = t_id

    def make_storage(self, loc):
        storage = StorageNode()
        storage.modifyTime = time.time()
        storage.id = self.storageDict.get_unique_id()
        storage.loc = loc
        self.storageDict.add(storage)
        return storage

    # ############### team

    def make_team(self, loc, person=False):
        team = TeamNode()
        team.id = self.teamDict.get_unique_id()
        team.loc = loc
        self.teamDict.add(team)
        if person:
            p = self.make_person()
            self.appoint_person(p.id, team.id)
        return team

    def del_team(self, t):
        self.appoint_team(t, 0)
        team = self.teamDict[t]
        for i in team.staff:
            self.del_person(i)
        del self.teamDict[t]

    def appoint_team(self, id_, t_id):
        team = self.teamDict[id_]
        if team.belong != 0:
            staff = self.groupDict[team.belong].teams
            if id_ in staff:
                staff.remove(id_)

        if t_id != 0:
            group = self.groupDict[t_id]
            staff = group.teams
            if id_ not in staff:
                staff.append(id_)
            team.flag = team.flag
        else:
            team.flag = 0

        team.belong = t_id

    def move_team(self, id_, new_loc):
        self.teamDict.move_by_id(id_, new_loc)

    # ################# troop
    def make_troop(self, loc, person=False):
        team = TroopNode()
        team.id = self.troopDict.get_unique_id()
        team.loc = loc
        self.troopDict.add(team)
        if person:
            p = self.make_person()
            self.appoint_person(p.id, team.id)
        return team

    def del_troop(self, t):
        self.appoint_troop(t, 0)
        team = self.troopDict[t]
        for i in team.staff:
            self.del_person(i)
        del self.troopDict[t]

    def appoint_troop(self, id_, t_id):
        team = self.troopDict[id_]
        if team.belong != 0:
            staff = self.groupDict[team.belong].militaries
            if id_ in staff:
                staff.remove(id_)

        if t_id != 0:
            group = self.groupDict[t_id]
            staff = group.militaries
            if id_ not in staff:
                staff.append(id_)
            team.flag = team.flag
        else:
            team.flag = 0

        team.belong = t_id

    def move_troop(self, id_, new_loc):
        self.troopDict.move_by_id(id_, new_loc)

    # ################# ferry
    def make_ferry(self, loc):
        team = FerryNode()
        team.id = self.ferryDict.get_unique_id()
        team.loc = loc
        self.ferryDict.add(team)
        return team

    def del_ferry(self, t):
        self.appoint_troop(t, 0)
        team = self.troopDict[t]
        for i in team.staff:
            self.del_person(i)
        del self.troopDict[t]

    def appoint_ferry(self, id_, t_id):
        team = self.ferryDict[id_]
        if team.belong != 0:
            ferries = self.groupDict[team.belong].ferries
            if id_ in ferries:
                ferries.remove(id_)

        if t_id != 0:
            group = self.groupDict[t_id]
            ferries = group.ferries
            if id_ not in ferries:
                ferries.append(id_)
            team.flag = team.flag
        else:
            team.flag = 0

        team.belong = t_id

    def move_ferry(self, id_, new_loc):
        self.ferryDict.move_by_id(id_, new_loc)

    # ############ group
    def make_group(self, name=None):
        tmp_n = GroupNode()
        tmp_n.id = self.groupDict.get_unique_id()
        if name is None:
            # tmp_n.name = self.get_name('group', self.groupDict.nameDict)
            tmp_n.name = ('\\u'+str(tmp_n.id % 10000).ljust(4, '0')).encode('utf-8').decode('unicode_escape')
        else:
            tmp_n.name = name
        rlt = self.groupDict.add(tmp_n)
        if not rlt:
            raise Exception("")

        tmp_n.flagId = tmp_n.id
        return tmp_n

    def del_group(self, id_):
        group = self.groupDict[id_]
        self.del_team(group.header)
        for i in group.teams:
            self.del_team(i)
        for i in group.militaries:
            self.del_troop(i)
        for i in group.cities:
            self.appoint_city(i, 0)
        for i in group.subGroup:
            group2 = self.groupDict[i]
            group2.belong = 0
            group2.flag = group2.id

    def rename_group(self, id_, new_name):
        self.groupDict.rename(id_, new_name)

    def appoint_group(self, id_, belong):
        pass

    # ############# global use

    def is_enemy(self, f1, f2):
        if f1 == f2:
            return False
        key = f1, f2
        if f1 > f2:
            key = f2, f1
        return key in self.topGroupEnemyShip

    def get_group_flag(self, id_):
        if id_ == 0:
            return 0
        tmp_v = id_
        while True:
            tmp_v2 = self.groupDict[tmp_v].belong
            if tmp_v2 == 0:
                return tmp_v
            else:
                tmp_v = tmp_v2

    # update
    def update(self, delta_time):
        pass  #


# sub system
# traffic system
