#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_ai.py
# @time: 3/13/2023 9:11 PM
import random
from typing import Dict

# building: random build
# attack: choose unit -> choose target -> move and attack


from qins_moon.advw.data_node import AdvwDataNode
from qins_moon.core.director import EntityBase
from qins_moon.core.grid_map import GridNavigation
from qins_moon.core.utils.math_tool import MathTool
from qins_moon.core.utils.data_structure import TableRowBase, NameIdTableStructure
from qins_moon.advw.data_driver import AdvwDataDriver
from qins_moon.advw import data_driver as _data_driver


class AdvwDataAIModelEntity(EntityBase):
    def __init__(self):
        super().__init__()

    def init_data(self):
        pass

    def get_buy_plain(self):
        pass

    def get_next_unit_action(self):
        pass

    def update(self, delta):
        pass


class AdvwEasyAIModelEntity(AdvwDataAIModelEntity):
    """
    都是陆军
    """
    def __init__(self, flag_id, data_driver, grid_nav):
        super().__init__()
        self.flagId = flag_id
        self.dataDriver: AdvwDataDriver = data_driver
        self.gridNav: GridNavigation = grid_nav

        self.unitIds = set()
        self.buildingIds = set()

        self.enemyUnitIds = set()
        self.enemyBuildings = set()

        self.lastUnitTargetDict: Dict[int, tuple] = {}
        self._buildingPlain = {}

    def init_data(self):
        dn = self.dataDriver.controller.rootDataNode
        self.unitIds.clear()
        for k, v in dn.militaryDict.idDict.items():
            if v.flagId == self.flagId:
                self.unitIds.add(v.id)
            else:
                self.enemyUnitIds.add(v.id)

        self.buildingIds.clear()
        for v in dn.buildingDict.idDict.values():
            if v.flagId == self.flagId:
                self.buildingIds.add(v.id)
            else:
                self.enemyBuildings.add(v.id)

        # print(list(self.unitIds))
        should_del = []
        for k, v in self.lastUnitTargetDict.items():
            if k not in self.unitIds:
                should_del.append(k)
            elif dn.buildingDict[v].flagId == self.flagId:
                should_del.append(k)
        for i in should_del:
            del self.lastUnitTargetDict[i]

    def get_next_unit_action(self):
        """
        全攻击性单位、全近战
        :return:
        """
        dn = self.dataDriver.controller.rootDataNode
        dt = dn.dataTable
        should_del = set()
        action = None
        for id_ in self.unitIds:
            m = dn.militaryDict[id_]
            if m is None:
                continue

            m_t = dt.militaryTable[m.tableRowId]
            move_t = dt.movePropertyTable[m_t.moveProperty]
            if move_t.baseSpeed > m.currentOil:
                rest_oil = m.currentOil
            else:
                rest_oil = move_t.baseSpeed
            move_area = MathTool.count_move_area(
                self.gridNav.get_engine_move_map((self.flagId << 8)+dt.engineTable[move_t.engineType].id),
                m.loc, rest_oil
            )

            atk_target_loc = None
            atk_move_target = None
            for loc in move_area:
                if loc not in dn.militaryDict:
                    continue
                target_m = dn.militaryDict[loc]
                if target_m.flagId == self.flagId:
                    continue
                # 能攻击它吗， 默认能
                #
                for drt in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    n_x, n_y = drt[0] + target_m.loc[0], drt[1] + target_m.loc[1]
                    if (n_x, n_y) in move_area and (n_x, n_y) not in dn.militaryDict:
                        atk_target_loc = target_m.loc
                        atk_move_target = n_x, n_y
                        break
                else:
                    continue

                break

            if atk_target_loc is not None:
                b_h = _data_driver.MilitaryActionHandler()
                b_h.militaryId = m.id
                b_h.acted = True
                b_h.road = MathTool.shortest_road_from_move_area(move_area, m.loc, atk_move_target)
                b_h.attackTargetId = dn.militaryDict[atk_target_loc].id
                action = b_h
                should_del.add(m.id)
                break

            # find nearst target
            nearst_loc = None
            for enemy in self.enemyUnitIds:
                if enemy not in dn.militaryDict:
                    continue
                enemy_m = dn.militaryDict[enemy]
                if enemy_m.flagId == self.flagId:
                    continue
                if nearst_loc is None:
                    nearst_loc = enemy_m.loc
                elif abs(m.loc[0]-enemy_m.loc[0]) + abs(m.loc[1]-enemy_m.loc[1]) < \
                        abs(m.loc[0]-nearst_loc[0]) + abs(m.loc[1]-nearst_loc[1]):
                    nearst_loc = enemy_m.loc
            if nearst_loc is None:
                break
            a_road = MathTool.short_road_by_astar(
                self.gridNav.get_engine_move_map((self.flagId << 8)+dt.engineTable[move_t.engineType].id),
                m.loc, nearst_loc)
            # if not a_road[0]:
            #     continue

            # mov_road = []
            for i1, i in enumerate(reversed(a_road[0])):
                if i in move_area:
                    mov_road = a_road[0][:-i1]
                    break
            else:
                continue

            # print('nearst target', nearst_loc)
            b_h = _data_driver.MilitaryActionHandler()
            b_h.militaryId = m.id
            b_h.acted = True
            b_h.road = mov_road
            action = b_h
            should_del.add(m.id)
            break

        for i in should_del:
            self.unitIds.remove(i)
        return action

    def get_buy_plain(self):
        """
        没有bout end
        :return:
        """
        actions = []

        dn = self.dataDriver.controller.rootDataNode
        dt = dn.dataTable
        for id_ in self.buildingIds:
            money = dn.playerDict[self.flagId].money
            b = dn.buildingDict[id_]
            if b.loc in dn.militaryDict:
                continue
            can_build = dt.buildingTable[b.tableRowId].canBuilding
            if not can_build:
                continue

            b_u = random.choice(can_build)
            u_t = dt.militaryTable[b_u]
            if u_t.costBill > money:
                continue

            event = _data_driver.BuildMilitaryHandler()
            event.loc = b.loc
            event.tableRowId = u_t.id
            actions.append(event)
        # actions.append(_data_driver.BoutEntHandler())
        return actions

    def get_buy_plain2(self):
        if self._buildingPlain is None:
            self._buildingPlain = {}
            dn = self.dataDriver.controller.rootDataNode
            dt = dn.dataTable
            for id_ in self.buildingIds:
                money = dn.playerDict[self.flagId].money
                b = dn.buildingDict[id_]
                if b.loc in dn.militaryDict:
                    continue
                can_build = dt.buildingTable[b.tableRowId].canBuilding
                if not can_build:
                    continue

                b_u = random.choice(can_build)
                u_t = dt.militaryTable[b_u]
                if u_t.costBill > money:
                    continue

                self._buildingPlain[b.loc] = u_t.id

        if not self._buildingPlain:
            return None
        else:
            k = list(self._buildingPlain.keys())[0]
            event = _data_driver.BuildMilitaryHandler()
            event.loc = k
            event.tableRowId = self._buildingPlain[k]
            del self._buildingPlain[k]
            return event


class AdvwAIModelMngr(NameIdTableStructure):
    pass
