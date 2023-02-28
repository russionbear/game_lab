#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :data_table.py
# @Time      :07/01/2023
# @Author    :russionbear
# @Function  :function
import json
from typing import Dict, Tuple, List

from qins_moon.core.utils.data_structure import TableRowBase as RowBase, NameIdTableStructure


class TerrainTerrainRow(RowBase):

    def __init__(self):
        super().__init__()
        self.modelName: str = ""
        self.engineTerrain: str = ""
        self.eyeTerrain: str = ""


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


class MilitaryRow(RowBase):
    def __init__(self):
        super().__init__()
        # self.costPopulation = 0
        self.costMoney = 0
        self.maintainMoney: float = 0
        self.moveProperty = ""
        self.battleProperty = ""
        self.modelName = ''


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


class BuildingRow(RowBase):
    def __init__(self):
        super().__init__()
        self.maxPopulation = 1000
        self.populationGrowth = 0.001
        self.moneyRate = 0.0008
        # self.maxMoney = 1
        self.upgradeCost: list | str = ''
        self.modelName = ''
        self.terrainTerrain = ''
        self.provideUnits: list | str | None = None
        self.talentRate = 0

    def correct_property_type(self):
        super().correct_property_type()
        self.upgradeCost = json.loads(self.upgradeCost)
        if len(self.provideUnits) == 0:
            self.provideUnits = None
        else:
            self.provideUnits = json.loads(self.provideUnits)


class UnitBufRow(RowBase):
    def __init__(self):
        super().__init__()
        self.kind = ""
        self.type = ''
        self.value = 0


class GeneralTable:
    def __init__(self):
        self.minEnlistPopulationRate = 0.7
        self.minMoneyPopulationRate = 0.8
        self.defaultResourcePackageId: Tuple[str, str] | str = "", ""
        self.cityModelName = ""
        self.cityTerrainTerrain = ''
        self.militaryModelName = ""
        self.militaryTerrainTerrain = ''
        self.militaryMaxNumber = 40*1000
        self.militaryMaxFightNumber = 40*1000 * .5

    def correct_property_type(self):
        self.defaultResourcePackageId = tuple(json.loads(self.defaultResourcePackageId))


class Cv6DataTable:
    def __init__(self):
        self.dataTableId = "", "", ""

        # ##############
        self.namesListTable: Dict[str, List[str]] = {}
        self.generalTable: GeneralTable = GeneralTable()

        self.atkDefDictTable: Dict[str, Dict[str, float]] = {}
        self.terrainAttackTable = NameIdTableStructure[TerrainAttackRow](TerrainAttackRow())
        self.terrainDefenseTable = NameIdTableStructure[TerrainDefenseRow](TerrainDefenseRow())

        self.terrainTerrainTable = NameIdTableStructure[TerrainTerrainRow](TerrainTerrainRow())
        self.engineTerrainTable = NameIdTableStructure[EngineTerrainRow](EngineTerrainRow())
        self.eyeTerrainTable = NameIdTableStructure[EyeTerrainRow](EyeTerrainRow())
        self.engineTable = NameIdTableStructure[EngineRow](EngineRow())
        self.eyeTable = NameIdTableStructure[EyeRow](EyeRow())

        self.decorationTable = NameIdTableStructure[DecorationRow](DecorationRow())
        self.battlePropertyTable = NameIdTableStructure[BattlePropertyRow](BattlePropertyRow())
        self.movePropertyTable = NameIdTableStructure[MovePropertyRow](MovePropertyRow())

        self.buildingTable = NameIdTableStructure[BuildingRow](BuildingRow())
        self.militaryTable = NameIdTableStructure[MilitaryRow](MilitaryRow())
        self.unitBufTable = NameIdTableStructure[UnitBufRow](UnitBufRow)
