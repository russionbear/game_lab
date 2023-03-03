#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :data_node.py
# @Time      :07/01/2023
# @Author    :russionbear
# @Function  :function
import random
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


class CityNode(GroupBase):
    def __init__(self):
        super().__init__()
        self.locations = []
        # self.maxBlockNu = 100
        self.tableRowId = 0

        self.gdp = 90
        self.restFreezeBout = 0
        self.restPayPerBout = 0
        self.wallArmor = 1.2

    def update(self, dn: 'PolityDataNode'):
        if self.restFreezeBout != 0:
            self.restFreezeBout -= 1
            return


class MilitaryNode:
    def __init__(self):
        self.tableRowId = 0
        self.currentBlood = 1


class TroopNode(GroupBase):
    def __init__(self):
        super().__init__()
        self.tableRowId = 0

        self.loc = 0, 0
        self.staff: List[int] = []
        self.militaryForce: List[MilitaryNode] = []

        self.costPerBout: float = 0
        self.isFrozen = False

        self.population = 0
        self.moveProperty = ""
        self.viewProperty = ''

        # about ai
        self.moveTarget = -1, 0
        # self.attackTargetAndWeight = 0, 0, 0

        self.operaActed = False
        self.operaHidden = False

    def refresh_property(self, dt: 'PolityDataTable'):
        self.population = 0
        self.costPerBout = 0
        military_rows = set()
        for i in self.militaryForce:
            if i.currentBlood <= 0:
                continue
            tmp_row = dt.militaryTable[i.tableRowId]
            self.population += i.currentBlood / dt.battlePropertyTable[tmp_row.battleProperty].\
                bloodValue * tmp_row.population
            self.costPerBout += i.currentBlood / dt.battlePropertyTable[tmp_row.battleProperty].\
                bloodValue * tmp_row.costPerBout
            military_rows.add(tmp_row)

        self.moveProperty = min(
            [dt.movePropertyTable[i.moveProperty] for i in military_rows],
            key=lambda arg: arg.baseSpeed).name
        self.viewProperty = max(
            [dt.viewPropertyTable[i.viewProperty] for i in military_rows],
            key=lambda arg: arg.distance).name


class PersonNode(GroupBase):
    def __init__(self):
        super().__init__()


class GroupNode(GroupBase):
    def __init__(self):
        super().__init__()
        self.groupAIId = 0

        self.headerTroopId = 0
        self.maxGovernTroopNu = 5  # 定期刷新
        self.bill = 0
        self.subGroup: List[int] = []

        self.troops: List[int] = []
        self.cities: List[int] = []

        self.attackTarget = -1, 0
        self.nextActionBouts = 0

    def update_bout(self, dn: 'PolityDataNode'):
        general_t = dn.dataTable.generalTable

        # gdp
        for i in self.cities:
            city_n = dn.cityDict[i]
            city_d = dn.dataTable.cityLevelTable[city_n.tableRowId]
            city_n.restPayPerBout = city_d.maxPayPerBout
            if city_n.restFreezeBout > 0:
                city_n.restFreezeBout -= 1
                continue
            self.bill += city_n.gdp

        # maintain cost
        for i in self.troops:
            troop_n = dn.troopDict[i]
            if troop_n.operaActed:
                if troop_n.costPerBout > self.bill:
                    troop_n.operaActed = True
                    troop_n.isFrozen = True
                    continue
                self.bill -= troop_n.costPerBout
                troop_n.operaActed = False
                troop_n.isFrozen = False
            else:
                if troop_n.costPerBout * general_t.costScaleWhenUnActed > self.bill:
                    troop_n.operaActed = True
                    troop_n.isFrozen = True
                    continue
                self.bill -= troop_n.costPerBout * general_t.costScaleWhenUnActed
                troop_n.operaActed = False
                troop_n.isFrozen = False

        # supply
        for i in self.troops:
            if self.bill <= 0:
                break
            troop_n = dn.troopDict[i]
            if troop_n.isFrozen:
                continue
            country_id = dn.countryMap[troop_n.loc[1], troop_n.loc[0]]
            if country_id == 0:
                continue
            if dn.cityDict[country_id].belong == self.id:
                for military in troop_n.militaryForce:
                    military_d = dn.dataTable.militaryTable[military.tableRowId]
                    battle_d = dn.dataTable.battlePropertyTable[military_d.battleProperty]
                    need_nu = battle_d.bloodValue - military.currentBlood
                    if need_nu <= 0:
                        continue
                    if need_nu > battle_d.bloodValue * general_t.maxSupplyTroopRate:
                        need_nu = battle_d.bloodValue * general_t.maxSupplyTroopRate
                    cost_bill = military_d.costBill * need_nu
                    if self.bill < cost_bill:
                        self.bill = 0
                        supply_nu = self.bill / military_d.costBill
                    else:
                        self.bill -= cost_bill
                        supply_nu = cost_bill / military_d.costBill
                    military.currentBlood += supply_nu
                troop_n.refresh_property(dn.dataTable)

        # # ai
        # action: 发育、攻城
        group_ai = dn.dataTable.groupAITable[self.groupAIId]
        map_size = dn.map_size
        # enlist troop
        if self.bill >= group_ai.billMakeNewTroop and general_t.maxGovernTroopNu > len(self.troops):
            # chose location
            loc = random.choice(self.cities).locations[0]
            for drt in [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]:
                x_, y_ = drt[0] + loc[0], drt[1] + loc[1]
                if x_ < 0 or y_ < 0 or x_ >= map_size[0] or y_ >= map_size[1]:
                    continue
                if (x_, y_) in dn.troopDict:
                    continue
                loc = x_, y_
                break
            else:
                loc = None
            # enlist
            if loc is not None:
                # total_cost = 0
                troop_n = dn.make_troop(loc, random.choice(group_ai.troopLevels))
                dn.appoint_troop(troop_n.id, self.id)
                self.bill -= dn.dataTable.troopLevelTable[troop_n.tableRowId].cost_bill
                # military_distribution = dn.dataTable.troopLevelTable[random.choice(group_ai.troopLevels)].distribution
                # for k, v in military_distribution.items():
                #     military_d = dn.dataTable.militaryTable[k]
                #     total_cost += military_d.costBill * v
                #     for j in range(v):
                #         tmp_military = MilitaryNode()
                #         tmp_military.tableRowId = military_d.id
                #         tmp_military.currentBlood = dn.dataTable.battlePropertyTable[military_d.battleProperty]\
                #             .bloodValue
                #         troop_n.militaryForce.append(tmp_military)
                # troop_n.refresh_property(dn.dataTable)
                # self.bill -= total_cost

        # begin attack
        if self.attackTarget[0] < 0:
            if group_ai.minAttackTroopNu <= len(self.troops):
                # find target
                target_locations = []
                for k, v in dn.cityDict.idDict.items():
                    if dn.is_enemy(self.flag, v.flag):
                        target_locations.append(v.locations[0])

                self.attackTarget = random.choice(target_locations)
                self.nextActionBouts = group_ai.maxAttackBouts
                for i in self.troops:
                    troop_n = dn.troopDict[i]
                    troop_n.moveTarget = self.attackTarget
            else:
                pass  # 继续发育

        else:
            self.nextActionBouts -= 1
            # 取消行动
            if self.nextActionBouts <= 0:
                self.attackTarget = -1, 0
                self.nextActionBouts = group_ai.maxWaitActionBouts
                for i in self.troops:
                    troop_n = dn.troopDict[i]
                    troop_n.moveTarget = dn.cityDict[random.choice(self.cities)].locations[0]


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
        self.countryMap: numpy.ndarray = numpy.zeros((), numpy.uint8)

        self.resourceMap: numpy.ndarray = numpy.zeros((), numpy.int_)
        self.personDict = NameIdTableStructure[PersonNode]()
        self.cityDict = LocationsIdTableStructure[CityNode]()

        self.troopDict = LocIdTableStructure[TroopNode](open_kdtree=True)
        self.peopleInConvey: Dict[int, Tuple[int, int, int, int]] = {}

        # group data
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
        for i in range(len(city_loc)):
            group_1 = rlt.make_group(str(city_loc[i]))
            group_1.flag = group_1.id
            print(group_1.id, city_loc[i])
            group_1.bill = 9000
            rlt.topGroups.append(group_1.id)
            rlt.appoint_city(rlt.cityDict[city_loc[i]].id, group_1.id)

            if random.randint(0, 5) > 3:
                army_1 = rlt.make_troop(city_loc[i], random.choice(
                    rlt.dataTable.groupAITable[group_1.groupAIId].troopLevels))
                army_1.name = str(army_1.id)
                rlt.appoint_troop(army_1.id, group_1.id)

        # top group
        group_ids = list(rlt.groupDict.idDict.keys())
        for y in range(len(group_ids)):
            for x in range(y+1, len(group_ids)):
                rlt.topGroupEnemyShip.add((min(group_ids[y], group_ids[x]), max(group_ids[y], group_ids[x])))

        # # make city troop
        # for i in range(len(city_loc)):
        #     group_1 = rlt.make_group(city_loc[i])
        #     rlt.topGroups.append(group_1.id)
        #     rlt.appoint_city(rlt.cityDict[city_loc[i]].id, group_1.id)
        #
        #     army_1 = rlt.make_troop(city_loc[i])
        #     army_1.name = str(army_1.id)
        #     rlt.appoint_troop(army_1.id, group_1.id)

        # country map
        rlt.countryMap = numpy.random.randint(0, 2, (map_size[1], map_size[0]), numpy.int_)

        # resource
        rlt.resourceMap = numpy.random.randint(0, 2, (map_size[1], map_size[0]), numpy.int_)

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
        for y in range(table.areaSize[1]):
            for x in range(table.areaSize[0]):
                city.locations.append((y+loc[0], x+loc[1]))
        self.cityDict.add(city)
        # city.storageId = self.make_storage(loc).id
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
            staff = self.troopDict[person.belong].staff
            if id_ in staff:
                staff.remove(id_)

        if t_id != 0:
            team = self.troopDict[t_id]
            staff = team.staff
            if id_ not in staff:
                staff.append(id_)
            person.flag = team.flag
        else:
            person.flag = 0

        person.belong = t_id

    # ################# troop
    def make_troop(self, loc, level_id, person=False):
        troop = TroopNode()
        troop.tableRowId = level_id
        troop.id = self.troopDict.get_unique_id()
        troop.loc = loc
        self.troopDict.add(troop)
        if person:
            p = self.make_person()
            self.appoint_person(p.id, troop.id)

        distributions = self.dataTable.troopLevelTable[level_id].distribution
        for k, v in distributions.items():
            for i in range(v):
                tmp_military = MilitaryNode()
                tmp_military.tableRowId = self.dataTable.militaryTable[k].id
                tmp_military.currentBlood = self.dataTable.battlePropertyTable[
                    self.dataTable.militaryTable[k].battleProperty].bloodValue
                troop.militaryForce.append(tmp_military)
        troop.refresh_property(self.dataTable)
        return troop

    def del_troop(self, t):
        self.appoint_troop(t, 0)
        team = self.troopDict[t]
        for i in team.staff:
            self.del_person(i)
        del self.troopDict[t]

    def appoint_troop(self, id_, t_id):
        team = self.troopDict[id_]
        if team.belong != 0:
            staff = self.groupDict[team.belong].troops
            if id_ in staff:
                staff.remove(id_)

        if t_id != 0:
            group = self.groupDict[t_id]
            staff = group.troops
            if id_ not in staff:
                staff.append(id_)
            team.flag = team.flag
        else:
            team.flag = 0

        team.belong = t_id

    def move_troop(self, id_, new_loc):
        self.troopDict.move_by_id(id_, new_loc)

    # ############ group
    def make_group(self, name=None, group_ai_id=None):
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
        if group_ai_id is None:
            tmp_n.groupAIId = random.choice(list(self.dataTable.groupAITable.idDict.keys()))
        else:
            tmp_n.groupAIId = group_ai_id
        return tmp_n

    def del_group(self, id_):
        group = self.groupDict[id_]
        for i in group.troops:
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
    def update_bout(self):
        for v in self.groupDict.idDict.values():
            v.update_bout(self)

    def count_troop_fight_rlt(self, atk_id, def_id):
        pass


# sub system
# traffic system
