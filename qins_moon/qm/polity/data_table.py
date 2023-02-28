#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :data_table.py
# @Time      :07/01/2023
# @Author    :russionbear
# @Function  :function
import json
from typing import Dict, Tuple, List

from qins_moon.core.utils.data_structure import TableRowBase as RowBase, NameIdTableStructure


# terrain


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
        # self.costPopulation = 0
        self.madeFrom: dict | str = {}
        self.costPerTick: float = 0
        # self.moveProperty = ""
        self.battleProperty = ""
        self.modelName = ''
        self.engineType = ''
        self.baseSpeed = 10

    def correct_property_type(self):
        super().correct_property_type()
        self.madeFrom = json.loads(self.madeFrom)


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


# enemy or building


class GoodsRow(RowBase):
    def __init__(self):
        super().__init__()
        self.weight = 1.0
        self.price = 1.0
        # self.costLabour = 1.0
        self.madeFrom: str | dict = {}
        self.modelName = ''

    def correct_property_type(self):
        super().correct_property_type()
        self.madeFrom = json.loads(self.madeFrom)


class BuildingRow(RowBase):
    def __init__(self):
        super().__init__()
        self.provide: dict | str = ''
        # self.need: dict | str = ''

        self.madeFrom: dict | str = {}
        self.modelName = ''
        self.costPerTick = 0.1

        self.isSingleBuilding = False
        self.bufWallArmor = -1.1  # 0表示没影响
        self.talentCapacity = 1.1
        self.tax = 0.2
        self.underTax = 0.1

    def correct_property_type(self):
        super().correct_property_type()
        self.provide = set(json.loads(self.provide))
        # self.need = json.loads(self.need)
        self.madeFrom = json.loads(self.madeFrom)


class FerryRow(RowBase):
    def __init__(self):
        super().__init__()
        self.madeFrom: dict | str = {}
        self.costMoneyPerTick = 0.1
        # self.canLoad: set | str = ''
        self.moveProperty = ''
        self.modelName = ''

    def correct_property_type(self):
        super().correct_property_type()
        # self.canLoad = set(json.loads(self.canLoad))
        self.madeFrom = json.loads(self.madeFrom)


class CityLevelRow(RowBase):
    def __init__(self):
        super().__init__()
        self.maxBlockNu = 0
        self.areaSize: tuple | str = 1, 1
        self.population = 0
        self.baseFightingCapacity = 1

    def correct_property_type(self):
        super().correct_property_type()
        self.areaSize = tuple(json.loads(self.areaSize))


class GeneralTable:
    def __init__(self):
        # self.minEnlistPopulationRate = 0.7
        # self.minMoneyPopulationRate = 0.8
        self.defaultResourcePackageId: Tuple[str, str] | str = "", ""
        self.cityModelName = ""
        self.cityTerrainTerrain = ''
        # self.militaryModelName = ""
        # self.militaryTerrainTerrain = ''
        # self.militaryMaxNumber = 40*1000
        # self.militaryMaxFightNumber = 40*1000 * .5
        self.troopModelName = ""
        self.teamModelName = ''
        self.ferryModelName = ''
        self.goldGoods = ''

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
        self.battlePropertyTable = NameIdTableStructure[BattlePropertyRow](BattlePropertyRow())
        self.movePropertyTable = NameIdTableStructure[MovePropertyRow](MovePropertyRow())

        self.militaryTable = NameIdTableStructure[MilitaryRow](MilitaryRow())
        self.goodsTable = NameIdTableStructure[GoodsRow](GoodsRow())
        self.buildingTable = NameIdTableStructure[BuildingRow](BuildingRow())
        self.cityLevelTable = NameIdTableStructure[CityLevelRow](CityLevelRow())
        self.ferryTable = NameIdTableStructure[FerryRow](FerryRow())
