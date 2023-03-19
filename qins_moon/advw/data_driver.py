#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_driver.py
# @time: 3/12/2023 11:41 AM
from typing import Any

from qins_moon.core.utils.data_structure import TableRowBase, NameIdTableStructure, LocIdsTableStructure, \
    LocIdTableStructure
from qins_moon.advw.data_node import AdvwDataNode

# event: web, local, trigger


class AdvwController:
    def __init__(self, dn, driver):
        self.rootDataNode: AdvwDataNode = dn
        self.dataDriver: AdvwDataDriver = driver
        self.dataDriver.controller = self

        self._actionHandleDict = {
            BoutEntHandler.__name__: self.bout_ent,
            ModifyBuildingFlagHandler.__name__: self.modify_building_flag,
            BuildMilitaryHandler.__name__: self.build_military,
            MilitaryActionHandler.__name__: self.military_action,
            # MoveMilitaryHandler.__name__: self.move_military,
            # MilitaryOccupyHandler.__name__: self.military_occupy,
            # MilitaryAttackHandler.__name__: self.military_attack,
            # MilitaryUnloadHandler.__name__: self.military_unload,
            # MilitaryActedHandler.__name__: self.military_acted,
            # MilitaryHiddenHandler.__name__: self.military_hidden,
            MilitaryKillHandler.__name__: self.military_kill,
            ModifyTerrainHandler.__name__: self.modify_terrain,
            ModifyPlayerValueHandler.__name__: self.modify_player_value,
            SetPlayerRltHandler.__name__: self.modify_player_value
        }
        self.isGameOver = False

    # 基础事件

    def bout_ent(self, d: 'BoutEntHandler'):
        flags = list(self.rootDataNode.playerDict.idDict.keys())
        old_flag = self.rootDataNode.currentPlayerId
        new_flag = flags[(flags.index(self.rootDataNode.currentPlayerId)+1) % len(flags)]
        self.rootDataNode.currentPlayerId = new_flag

        # change color
        for id_, v in self.rootDataNode.militaryDict.idDict.items():
            if v.flagId == old_flag:
                v.acted = False

        # money
        player = self.rootDataNode.playerDict[new_flag]
        player.money += sum([1 for v in self.rootDataNode.buildingDict.idDict.values() if v.flagId == new_flag]) * \
            self.rootDataNode.dataTable.generalTable.cityGdpPerBout

        # oil
        should_del = []
        for id_, v in self.rootDataNode.militaryDict.idDict.items():
            if v.flagId == new_flag:
                v.currentOil -= self.rootDataNode.dataTable.movePropertyTable[
                    self.rootDataNode.dataTable.militaryTable[v.tableRowId].moveProperty].costPer
                if v.currentOil <= 0:
                    should_del.append(v.id)
        for i in should_del:
            self.rootDataNode.del_military(self.rootDataNode.militaryDict[i].loc)

    def modify_building_flag(self, d: 'ModifyBuildingFlagHandler'):
        self.rootDataNode.buildingDict[d.loc].flagId = d.flag
        self.dataDriver.pub_building_change(d.loc)

    def build_military(self, d: 'BuildMilitaryHandler'):
        b = self.rootDataNode.buildingDict[d.loc]
        # if b.loc in self.rootDataNode.militaryDict:
        #     return
        player = self.rootDataNode.playerDict[b.flagId]
        cost = self.rootDataNode.dataTable.militaryTable[d.tableRowId].costBill
        player.money -= cost
        # print(d.check(self.rootDataNode), d.loc, d.__dict__)
        if d.check(self.rootDataNode) is not None:
            pass
        m = self.rootDataNode.make_military(d.tableRowId, d.loc, player.flagId)
        m.acted = True

    def military_action(self, d: "MilitaryActionHandler"):
        m = self.rootDataNode.militaryDict[d.militaryId]

        if d.road:
            self.rootDataNode.move_military(m.loc, d.road[-1])

        if d.occupy:
            b = self.rootDataNode.buildingDict[m.loc]
            if b.flagId == m.flagId:
                b.occupiedValue = 0
                return
            b.occupiedValue += m.currentBlo0d
            if b.occupiedValue >= self.rootDataNode.dataTable.generalTable.maxOccupyValue:
                b.occupiedValue = 0
                b.flagId = m.flagId

        if d.unloadIdLocDict:
            id_index_dict = {}
            rest_loadings: list = []
            for i1, i in enumerate(m.loadings):
                if i.id in id_index_dict:
                    id_index_dict[i.id] = i1
                else:
                    rest_loadings.append(i)
            for k, loc in d.unloadIdLocDict.items():
                n_m = m.loadings[id_index_dict[k]]
                n_m.id = self.rootDataNode.militaryDict.get_unique_id()
                n_m.loc = loc
                n_m.acted = True
                self.rootDataNode.militaryDict.add(n_m)
            m.loadings = rest_loadings

        if d.attackTargetId is not None:
            self.rootDataNode.count_attack_rlt(m.loc, self.rootDataNode.militaryDict[d.attackTargetId].loc)

        if d.hidden is not None:
            b = self.rootDataNode.buildingDict[m.loc]
            if b.flagId == m.flagId:
                b.occupiedValue = 0
                return
            b.occupiedValue += m.currentBlo0d
            if b.occupiedValue >= self.rootDataNode.dataTable.generalTable.maxOccupyValue:
                b.occupiedValue = 0
                b.flagId = m.flagId

        if d.acted:
            m.acted = True

    def military_kill(self, d: 'MilitaryKillHandler'):
        self.rootDataNode.del_military(d.militaryLoc)

    def modify_terrain(self, d: 'ModifyTerrainHandler'):
        for loc, v in d.terrainDict.items():
            self.rootDataNode.terrainMap[loc[1], loc[0]] = v
        for loc, v in d.trafficDict.items():
            self.rootDataNode.trafficMap[loc[1], loc[0]] = v
        for loc, v in d.decorationDict.items():
            self.rootDataNode.decorationMap[loc[1], loc[0]] = v

        for loc, fv in d.militaryDict.items():
            flag, table_id = fv
            m = self.rootDataNode.militaryDict[loc]
            if m is not None:
                self.rootDataNode.del_military(loc)
            if table_id == 0:
                return
            self.rootDataNode.make_military(table_id, loc, flag)

        for loc, fv in d.buildingDict.items():
            flag, table_id = fv
            m = self.rootDataNode.buildingDict[loc]
            if m is not None:
                del self.rootDataNode.buildingDict[loc]
            if table_id == 0:
                return
            self.rootDataNode.make_building(table_id, loc, flag)

    def modify_player_value(self, d: 'ModifyPlayerValueHandler'):
        player = self.rootDataNode.playerDict[d.flag]
        if d.money is not None:
            if d.money[0] == 0:
                player.money = d.money[1]
            else:
                player.money += d.money[0] * d.money[1]

        if d.blue is not None:
            if d.blue[0] == 0:
                player.hero.currentBlue = d.blue[1]
            else:
                player.hero.currentBlue += d.blue[0] * d.blue[1]

    def set_player_rlt(self, d: 'SetPlayerRltHandler'):
        if d.isOver:
            o_player = self.rootDataNode.playerDict[d.flag]
            should_del = []
            for v in self.rootDataNode.militaryDict.idDict.values():
                if v.flagId == o_player.flagId:
                    should_del.append(v.loc)
            for i in should_del:
                self.rootDataNode.del_military(i)

            for b in self.rootDataNode.buildingDict.idDict.values():
                if b.flagId == o_player.flagId:
                    b.flagId = d.toFlag
        else:
            for i in self.rootDataNode.playerDict.idDict.values():
                if i.flagId != d.flag:
                    i.isFailed = True

    # 复杂高级事件

    # def

    def handle_command(self, d):
        if self.isGameOver:
            return
        handle: Any = self._actionHandleDict[d.__class__.__name__]
        handle(d)


# region handler
class HandlerBase(TableRowBase):
    def __init__(self):
        super().__init__()

    def check(self, dn: AdvwDataNode):
        pass


class BoutEntHandler(HandlerBase):
    pass


class ModifyBuildingFlagHandler(HandlerBase):
    def __init__(self):
        super().__init__()
        self.loc = 0
        self.flag = 0


class BuildMilitaryHandler(HandlerBase):
    def __init__(self):
        super().__init__()
        self.loc = 0, 0
        self.tableRowId = 0

    def check(self, dn: AdvwDataNode):
        if self.loc not in dn.buildingDict:
            return 'no building'
        b_d = dn.buildingDict[self.loc]
        if b_d.flagId != dn.currentPlayerId:
            return 'not flag ' + f"{b_d.flagId}-{dn.currentPlayerId}"
        if self.loc in dn.militaryDict:
            return 'military exited'
        # no enough money


class MilitaryActionHandler(HandlerBase):
    def __init__(self):
        super().__init__()
        self.militaryId = 0

        self.road = []

        self.occupy = False
        self.unloadIdLocDict = {}
        # self.unloadAll = False

        self.attackTargetId = None

        self.hidden = None
        self.acted = True
        self.encountered = False

    def check(self, dn: AdvwDataNode):
        m_d = dn.militaryDict[self.militaryId]
        if m_d is None:
            return 'no military'

        if m_d.flagId != dn.currentPlayerId:
            return 'flag error'
        if self.attackTargetId is not None:
            if self.attackTargetId not in dn.militaryDict:
                return 'no target military'


class MilitaryKillHandler(HandlerBase):
    def __init__(self):
        super().__init__()
        self.militaryLoc = 0

    def check(self, dn: AdvwDataNode):
        if self.militaryLoc not in dn.militaryDict:
            return 'military not exited'
        elif dn.militaryDict[self.militaryLoc].flagId != dn.currentPlayerId:
            return 'error flag'


class ModifyTerrainHandler(HandlerBase):
    def __init__(self):
        super().__init__()
        self.terrainDict = {}
        self.trafficDict = {}
        self.decorationDict = {}
        self.militaryDict = {}
        self.buildingDict = {}


class ModifyPlayerValueHandler(HandlerBase):
    def __init__(self):
        super().__init__()
        self.flag = 0
        self.money = (0, 0)
        self.blue = 0, 0


class SetPlayerRltHandler(HandlerBase):
    def __init__(self):
        super().__init__()
        self.flag = 0
        self.isOver = False
        self.toFlag = 0


# endregion


# region trigger
class TriggerBase(TableRowBase):
    def __init__(self):
        super().__init__()
        self.eventType = 0
        self.eventKey = 0


class InOutAreaTrigger(TriggerBase):
    def __init__(self):
        super().__init__()
        self.loc = 0, 0
        self.isIn = False


class MilitaryKilledTrigger(TriggerBase):
    def __init__(self):
        super().__init__()
        self.id = 0


class BuildingChangeTrigger(TriggerBase):
    def __init__(self):
        super().__init__()
        self.loc = 0, 0


class BoutAtTrigger(TriggerBase):
    def __init__(self):
        super().__init__()
        self.bout = 90
# endregion


class AdvwDataDriver:
    def __init__(self):
        self.controller: AdvwController | None = None
        # event
        self.boutEndEventTable = NameIdTableStructure[BoutEntHandler](BoutEntHandler())
        self.modifyBuildingFlagEventTable = NameIdTableStructure[ModifyBuildingFlagHandler](ModifyBuildingFlagHandler())
        self.buildingMilitaryEventTable = NameIdTableStructure[BuildMilitaryHandler](BuildMilitaryHandler())
        self.militaryActionEventTable = NameIdTableStructure[MilitaryActionHandler](MilitaryKillHandler())
        # self.moveMilitaryEventTable = NameIdTableStructure[MoveMilitaryHandler](MoveMilitaryHandler())
        # self.militaryOccupyEventTable = NameIdTableStructure[MilitaryOccupyHandler](MilitaryOccupyHandler())
        # self.militaryAttackEventTable = NameIdTableStructure[MilitaryAttackHandler](MilitaryAttackHandler())
        # self.militaryUnloadEventTable = NameIdTableStructure[MilitaryUnloadHandler](MilitaryUnloadHandler())
        # self.militaryActedEventTable = NameIdTableStructure[MilitaryActedHandler](MilitaryActedHandler())
        # self.militaryHiddenEventTable = NameIdTableStructure[MilitaryHiddenHandler](MilitaryHiddenHandler())
        self.militaryKilledEventTable = NameIdTableStructure[MilitaryKillHandler](MilitaryKillHandler())
        self.modifyTerrainEventTable = NameIdTableStructure[ModifyTerrainHandler](ModifyTerrainHandler())
        self.modifyPlayerValueEventTable = NameIdTableStructure[ModifyPlayerValueHandler](ModifyPlayerValueHandler())
        self.setPlayerRltEventTable = NameIdTableStructure[SetPlayerRltHandler](SetPlayerRltHandler())

        self._typeEventDict = {
            BoutEntHandler.__name__: self.boutEndEventTable,
            ModifyBuildingFlagHandler.__name__: self.modifyBuildingFlagEventTable,
            BuildMilitaryHandler.__name__: self.buildingMilitaryEventTable,
            MilitaryActionHandler.__name__: self.militaryActionEventTable,
            # MoveMilitaryHandler.__name__: self.moveMilitaryEventTable,
            # MilitaryOccupyHandler.__name__: self.militaryOccupyEventTable,
            # MilitaryAttackHandler.__name__: self.militaryAttackEventTable,
            # MilitaryUnloadHandler.__name__: self.militaryUnloadEventTable,
            # MilitaryActedHandler.__name__: self.militaryActedEventTable,
            # MilitaryHiddenHandler.__name__: self.militaryHiddenEventTable,
            MilitaryKillHandler.__name__: self.militaryKilledEventTable,
            ModifyTerrainHandler.__name__: self.modifyTerrainEventTable,
            ModifyPlayerValueHandler.__name__: self.modifyPlayerValueEventTable,
            SetPlayerRltHandler.__name__: self.setPlayerRltEventTable
        }

        # trigger
        self.inOutAreaTriggerTable = LocIdsTableStructure[InOutAreaTrigger](InOutAreaTrigger())
        self.militaryKilledTriggerTable = NameIdTableStructure[MilitaryKilledTrigger](MilitaryKilledTrigger())
        self.buildingChangeTriggerTable = LocIdsTableStructure[BuildingChangeTrigger](BuildingChangeTrigger())
        self.boutAtTriggerTable = LocIdsTableStructure[BoutAtTrigger](BoutAtTrigger())

        self._handleLocalEventRRev = None  # (key, e)
        self._handleTriggerEventRev = None

        self._lastEvent = None
        self._currentTriggerDeep = 0
        self.maxTriggerDeep = 50

    def pub_int_out_area(self, old_loc, loc, is_in):
        pass

    def pub_military_killed(self, id_):
        pass

    def pub_building_change(self, loc):
        pass

    def pub_bout_at(self, bout):
        bout = (bout, bout)
        if bout in self.boutAtTriggerTable:
            for i in self.boutAtTriggerTable[bout]:
                self._handle_event(i.eventType, i.eventKey)

    def _handle_event(self, t=None, key=None, e=None):
        """
        原子操作
        当心循环调用
        :param t:
        :param key:
        :param e:
        :return:
        """
        if e is None:
            if t not in self._typeEventDict:
                return
            e = self._typeEventDict[t](key)
            # if e is None:
            #     return
        else:
            t = e.__class__.__name__

        if self._lastEvent is not None:
            if self._currentTriggerDeep > 0:
                self._pub_trigger_event(e)
            else:
                self._pub_local_event(e)
        self._lastEvent = e

        self._currentTriggerDeep += 1

        if self._currentTriggerDeep > self.maxTriggerDeep:
            raise Exception('最大递归调用错误')
        self.controller.handle_command(e)

        self._currentTriggerDeep -= 1

        if self._lastEvent is not None:
            if self._currentTriggerDeep > 0:
                self._pub_trigger_event(e)
            else:
                self._pub_local_event(e)
        self._lastEvent = None

    def put_local_event(self, e):
        self._handle_event(e=e)

    def sub_trigger_event(self, v):
        self._handleTriggerEventRev = v

    def sub_local_event(self, v):
        self._handleLocalEventRRev = v

    def _pub_trigger_event(self, e):
        if self._handleTriggerEventRev is not None:
            self._handleTriggerEventRev(e)

    def _pub_local_event(self, e):
        if self._handleLocalEventRRev is not None:
            self._handleLocalEventRRev(e)
