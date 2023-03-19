#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_driver.py
# @time: 3/12/2023 11:09 AM


from typing import Dict

from qins_moon.assault_suits.data_node import AssaultSuitsDataNode
from qins_moon.core.utils.data_structure import TableRowBase, NameIdTableStructure, LocIdsTableStructure


# controller
# view: world, attack, talk


# 行为文本格式化

class AssaultSuitsController:
    def __init__(self, dn):
        self.rootDataNode: AssaultSuitsDataNode = dn

    def modify_terrain(self, world_id,
                       terrain_dict, building_dict, decoration_dict, under_goods_dict,
                       monster_dict, tank_dict,
                       messenger_dict):
        wn = self.rootDataNode.subWorldDict[world_id]
        for loc, v in terrain_dict.items():
            wn.terrainMap[loc[1], loc[0]] = v
        for loc, v in building_dict.items():
            wn.buildingMap[loc[1], loc[0]] = v
        for loc, v in decoration_dict.items():
            wn.decorationMap[loc[1], loc[0]] = v

        for loc, v in under_goods_dict.items():
            if loc in wn.underGoodsDict[loc]:
                del wn.underGoodsDict[loc]
            if v != 0:
                self.rootDataNode.make_under_goods(world_id, v, loc)

        for loc, v in messenger_dict.items():
            if loc in wn.messengerDict[loc]:
                del wn.messengerDict[loc]
            if v != 0:
                self.rootDataNode.make_messenger(world_id, v, loc)

        for loc, v in monster_dict.items():
            if loc in wn.monsterDistribution[loc]:
                del wn.monsterDistribution[loc]
            if v != 0:
                self.rootDataNode.make_monster_distribution(world_id, v, loc)

        for loc, v in tank_dict.items():
            if loc in wn.tankSoftDict[loc]:
                tanks = list(wn.tankSoftDict[loc])
                for i in tanks:
                    self.rootDataNode.del_tank(world_id, i.id)
            if v != 0:
                self.rootDataNode.make_tank(world_id, v, loc)

    # world system

    def transfer_group(self, world_id, loc):
        self.rootDataNode.currentWorldNode = self.rootDataNode.subWorldDict[world_id]
        for i in self.rootDataNode.runTimeNode.groupPersons:
            if i.tankId != 0:
                self.rootDataNode.move_tank(i.tankId, world_id, loc)
            self.rootDataNode.move_person(i.id, world_id, loc)

    def move_group(self, direction):
        rt = self.rootDataNode.runTimeNode
        rt.currentDirection = direction
        for i in rt.groupPersons:
            if i.tankId != 0:
                has_tank = True
                break
        else:
            has_tank = False
        locations = [i.loc for i in rt.groupPersons]

        new_loc = locations[0][0] + direction[0], locations[0][1] + direction[1]
        if new_loc in self.rootDataNode.currentWorldNode.messengerDict:
            return False
        b_v = self.rootDataNode.currentWorldNode.buildingMap[new_loc[1], new_loc[0]]
        if b_v != 0:
            building_d = self.rootDataNode.dataTable.buildingTable[b_v]
            if not building_d.canPersonPass:
                return
            if has_tank and not building_d.canTankPass:
                return False

        t_v = self.rootDataNode.currentWorldNode.terrainMap[new_loc[1], new_loc[0]]
        if t_v != 0:
            terrain_d = self.rootDataNode.dataTable.terrainTable[t_v]
            if not terrain_d.canPersonPass:
                return
            if has_tank and not terrain_d.canTankPass:
                return False

        locations.insert(0, new_loc)
        for i1, i in enumerate(rt.groupPersons):
            if i.tankId != 0:
                self.rootDataNode.move_tank(i.tankId, self.rootDataNode.currentWorldNode.id, locations[i1])
            self.rootDataNode.move_person(i.id, self.rootDataNode.currentWorldNode.id, locations[i1])

        return True

    def to_detect(self):
        loc = self.rootDataNode.runTimeNode.groupPersons[0].loc
        if loc in self.rootDataNode.currentWorldNode.underGoodsDict:
            return self.rootDataNode.currentWorldNode.underGoodsDict[loc]
        return None

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

    def handle_event(self, d):
        pass


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

''
# event


class HandlerBase(TableRowBase):
    pass


class ModifyTerrainHandler(HandlerBase):
    def __init__(self):
        super().__init__()
        self.terrainDict: Dict[tuple, int] | str = ''
        self.buildingDict: Dict[tuple, int] | str = ''
        self.decorationDict: Dict[tuple, int] | str = ''
        self.underGoodsDict: Dict[tuple, int] | str = ''
        self.monsterDict: Dict[tuple, int] | str = ''
        self.tankDict: Dict[tuple, int] | str = ''
        self.messengerDict: Dict[tuple, int] | str = ''


class TransferGroupHandler(TableRowBase):
    def __init__(self):
        super().__init__()
        self.worldId = 0
        self.loc = 0, 0


class MoveGroupHandler(TableRowBase):
    def __init__(self):
        super().__init__()
        self.direction = 0, 0


class UseGoodsHandler(TableRowBase):
    def __init__(self):
        super().__init__()
        self.fromI = 0
        self.goodsOrder = 0


class UseGoodsByNameHandler(TableRowBase):
    def __init__(self):
        super().__init__()
        self.name = '90'


# trigger


class TriggerBase(TableRowBase):
    def __init__(self):
        super().__init__()
        self.eventType = 0
        self.eventKey = 0


class InOutAreaTrigger(TriggerBase):
    def __init__(self):
        super().__init__()
        self.loc = 0, 0
        self.isIn = 0


class DriverManager:
    def __init__(self, ctrl):
        self.controller: AssaultSuitsController = ctrl
        # event
        self.moveGroupEventTable = NameIdTableStructure[MoveGroupHandler]()
        self.transferGroupEventTable = NameIdTableStructure[TransferGroupHandler]()

        # trigger
        self.inOutAreaTriggerTable = LocIdsTableStructure[InOutAreaTrigger]()

    def pub_in_area(self, loc):
        triggers = self.inOutAreaTriggerTable[loc]
        if triggers is None:
            return
        for i in triggers:
            if i.isIn:
                self.handle_event(i.eventType, i.eventKey)

    def pub_out_area(self, loc):
        triggers = self.inOutAreaTriggerTable[loc]
        if triggers is None:
            return
        for i in triggers:
            if not i.isIn:
                self.handle_event(i.eventType, i.eventKey)

    def handle_event(self, t, key):
        if TransferGroupHandler.__name__.startswith(t):
            e = self.transferGroupEventTable[key]
            self.controller.transfer_group(e.worldId, e.loc)
        elif MoveGroupHandler.__name__.startswith(t):
            e = self.moveGroupEventTable[key]
            self.controller.move_group(e.direction)
        else:
            return
        print(t, e.__dict__)
