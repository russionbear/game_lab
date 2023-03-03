#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :data_table.py
# @Time      :07/01/2023
# @Author    :russionbear
# @Function  :function
import json
from typing import Dict, Tuple, List

from qins_moon.core.utils.data_structure import TableRowBase, NameIdTableStructure


# terrain

class RowBase(TableRowBase):
    def refresh_property(self, dn: "PolityDataTable"):
        pass


class TerrainTerrainRow(RowBase):

    def __init__(self):
        super().__init__()
        self.modelName: str = ""
        self.engineTerrain: str = ""
        self.eyeTerrain: str = ""


class TrafficRow(RowBase):
    def __init__(self):
        super().__init__()
        self.modelName = ""
        self.engineTerrain: str = ""


class EngineTerrainRow(RowBase):
    def __init__(self):
        super().__init__()


class EyeTerrainRow(RowBase):
    def __init__(self):
        super().__init__()


class EngineRow(RowBase):
    def __init__(self):
        super().__init__()
        self.costDict: Dict[str, float] | str = {}
        self.speedDict: Dict[str, float] | str = {}

    def correct_property_type(self):
        super().correct_property_type()
        self.costDict = json.loads(self.costDict)
        self.speedDict = json.loads(self.speedDict)


class EyeRow(RowBase):
    def __init__(self):
        super().__init__()
        self.costDict: Dict[str, int] | str = {}

    def correct_property_type(self):
        super().correct_property_type()
        self.costDict = json.loads(self.costDict)


class TerrainAttackRow(RowBase):
    def __init__(self):
        super().__init__()
        self.value = 0.0


class TerrainDefenseRow(RowBase):
    def __init__(self):
        super().__init__()
        self.value = 0.0


class DecorationRow(RowBase):
    def __init__(self):
        super().__init__()
        self.modelName: str = ""


# unit in map, military


class MilitaryRow(RowBase):
    def __init__(self):
        super().__init__()
        self.population = 0
        self.costBill = 90
        self.costPerBout: float = 0

        self.moveProperty = ""
        self.battleProperty = ""
        self.viewProperty = ''
        self.modelName = ''


class ViewPropertyRow(RowBase):
    def __init__(self):
        super().__init__()
        self.eyeType = ''
        self.distance = 7


class MovePropertyRow(RowBase):
    def __init__(self):
        super().__init__()
        self.engineType = ''
        self.baseSpeed = 8
        self.maxOil = 90


class BattlePropertyRow(RowBase):
    def __init__(self):
        super().__init__()
        self.bloodType = ''
        self.bloodValue = 10

        self.attackType = ''
        self.attackInterval = 0.5
        self.attackValue = 0
        self.isRemoteAttack = False
        self.attackMaxDistance = 3
        self.attackMinDistance = 1

        self.maxViewDistance = 3
        self.viewType = ''


class TroopLevelRow(RowBase):
    def __init__(self):
        super().__init__()
        self.distribution: dict | str = ''

        self._moveProperty = ''
        self._viewProperty = ''
        self._battleProperty = ''
        self._population = 7
        self._costPerBout = 9
        self._costBill = 90

    # region property
    @property
    def move_property(self):
        return self.move_property

    @property
    def view_property(self):
        return self._viewProperty

    @property
    def battle_property(self):
        return self._battleProperty

    @property
    def population(self):
        return self._population

    @property
    def cost_per_bout(self):
        return self._costPerBout

    @property
    def cost_bill(self):
        return self._costBill
    # endregion

    def correct_property_type(self):
        super().correct_property_type()
        self.distribution = json.loads(self.distribution)

    def refresh_property(self, dt: "PolityDataTable"):
        self._population = 0
        self._costPerBout = 0
        self._costBill = 0

        military_rows = set()
        for k, v in self.distribution.items():
            tmp_row = dt.militaryTable[k]
            self._costPerBout += tmp_row.costPerBout * v
            self._population += tmp_row.population * v
            self._costBill += tmp_row.costBill
            military_rows.add(tmp_row)

        self._moveProperty = min(
            [dt.movePropertyTable[i.moveProperty] for i in military_rows],
            key=lambda arg: arg.baseSpeed).name
        self._viewProperty = max(
            [dt.viewPropertyTable[i.viewProperty] for i in military_rows],
            key=lambda arg: arg.distance).name


class GroupAIRow(RowBase):
    def __init__(self):
        super().__init__()
        self.troopLevels: List[str] | str = ''
        self.billMakeNewTroop = 0  # 应大于所有的troop 类型
        self.minAttackTroopNu = 2
        self.maxAttackBouts = 9
        self.maxWaitActionBouts = 5
        self.attackViewDistance = 9

    def correct_property_type(self):
        super().correct_property_type()
        self.troopLevels = json.loads(self.troopLevels)


class CityLevelRow(RowBase):
    def __init__(self):
        super().__init__()
        self.canBuild: list | str = ''
        self.gdp = 90
        self.maxPayPerBout = 90
        self.wallArmor = 90
        self.areaSize: tuple | str = 0, 0

    def correct_property_type(self):
        super().correct_property_type()
        # self.areaSize = tuple(json.loads(self.areaSize))
        self.canBuild = json.loads(self.canBuild)
        self.areaSize = tuple(json.loads(self.areaSize))


class GeneralTable:
    def __init__(self):
        self.defaultResourcePackageId: Tuple[str, str] | str = "", ""
        self.cityModelName = ""
        self.cityTerrainTerrain = ''

        self.troopModelName = ""

        self.maxPopulationInTroop = 9000
        self.cityFreezeBouts = 5
        self.personCostPerBout = 90

        self.refreshMaxGovernTroopNuBouts = 9
        self.maxGovernTroopNu = 5

        self.conveyBoutsPerDistance = 0.1
        # self.maxSupplyDistance = 10
        self.costScaleWhenUnActed = 0.4
        self.maxSupplyTroopRate = 3

    def correct_property_type(self):
        self.defaultResourcePackageId = tuple(json.loads(self.defaultResourcePackageId))


class PolityDataTable:
    def __init__(self):
        self.dataTableId = "", "", ""

        # ##############
        self.namesListTable: Dict[str, List[str]] = {}
        self.generalTable: GeneralTable = GeneralTable()

        self.atkDefDictTable: Dict[str, Dict[str, float]] = {}
        self.terrainAttackTable = NameIdTableStructure[TerrainAttackRow](TerrainAttackRow())
        self.terrainDefenseTable = NameIdTableStructure[TerrainDefenseRow](TerrainDefenseRow())

        self.terrainTerrainTable = NameIdTableStructure[TerrainTerrainRow](TerrainTerrainRow())
        self.trafficTable = NameIdTableStructure[TrafficRow](TrafficRow())
        self.engineTerrainTable = NameIdTableStructure[EngineTerrainRow](EngineTerrainRow())
        self.eyeTerrainTable = NameIdTableStructure[EyeTerrainRow](EyeTerrainRow())
        self.engineTable = NameIdTableStructure[EngineRow](EngineRow())
        self.eyeTable = NameIdTableStructure[EyeRow](EyeRow())

        self.decorationTable = NameIdTableStructure[DecorationRow](DecorationRow())
        self.viewPropertyTable = NameIdTableStructure[ViewPropertyRow](ViewPropertyRow())
        self.battlePropertyTable = NameIdTableStructure[BattlePropertyRow](BattlePropertyRow())
        self.movePropertyTable = NameIdTableStructure[MovePropertyRow](MovePropertyRow())

        self.militaryTable = NameIdTableStructure[MilitaryRow](MilitaryRow())
        self.troopLevelTable = NameIdTableStructure[TroopLevelRow](TroopLevelRow())
        self.cityLevelTable = NameIdTableStructure[CityLevelRow](CityLevelRow())
        self.groupAITable = NameIdTableStructure[GroupAIRow](GroupAIRow())

        # adjust
        for v in self.__dict__.values():
            if isinstance(v, NameIdTableStructure) and isinstance(v.itemType, RowBase):
                for i in v.idDict.values():
                    i.refresh_property(self)
