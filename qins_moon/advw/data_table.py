#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_table.py
# @time: 3/12/2023 11:41 AM

import json
from typing import Dict, Tuple, List

from qins_moon.core.utils.data_structure import TableRowBase, NameIdTableStructure


# terrain

class RowBase(TableRowBase):
    def refresh_property(self, dn: "AdvwDataTable"):
        pass


class TerrainTerrainRow(RowBase):
    def __init__(self):
        super().__init__()
        self.engineTerrain: str = ""
        self.eyeTerrain: str = ""


class TrafficRow(RowBase):
    def __init__(self):
        super().__init__()
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


class DecorationRow(RowBase):
    def __init__(self):
        super().__init__()


# unit in map, military


class MilitaryRow(RowBase):
    def __init__(self):
        super().__init__()
        self.costBill = 90
        # self.costPerBout: float = 0

        self.moveProperty = ""
        self.battleProperty = ""
        self.viewProperty = ''
        self.loadMask = 0
        self.beLoadMask = 0
        self.canHidden = False
        self.canBeatBack = False

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
        self.baseSpeed = 8  # max cost oil
        self.maxOil = 90
        # self.maxCostOil = 4
        self.costPer = 0


class BattlePropertyRow(RowBase):
    def __init__(self):
        super().__init__()
        self.bloodType = ''
        self.bloodValue = 10

        self.attackType = ''
        self.attackValue = 0
        self.isRemoteAttack = False
        self.attackMaxDistance = 3
        self.attackMinDistance = 1
        self.maxBullet = 10


class HeroRow(RowBase):
    def __init__(self):
        super().__init__()
        self.midBlueValue = 5
        self.midBlueName = ''
        self.maxBlueValue = 10
        self.maxBlueName = ''
        self.militaryEffect: list | str = ''


class BuildingRow(RowBase):
    def __init__(self):
        super().__init__()
        self.canBuilding: list | str = []
        self.modelName = ''

    def correct_property_type(self):
        super().correct_property_type()
        self.canBuilding = json.loads(self.canBuilding)


class GeneralTable:
    def __init__(self):
        self.defaultResourcePackageId: Tuple[str, str] | str = "", ""
        self.maxOccupyValue = 20
        self.cityGdpPerBout = 1000

    def correct_property_type(self):
        self.defaultResourcePackageId = tuple(json.loads(self.defaultResourcePackageId))


class AdvwDataTable:
    def __init__(self):
        self.dataTableId = "", "", ""

        # ##############
        self.namesListTable: Dict[str, List[str]] = {}
        self.generalTable: GeneralTable = GeneralTable()

        self.atkDefDictTable: Dict[str, Dict[str, float]] = {}
        self.terrainAttackDictTable: Dict[str, Dict[str, float]] = {}
        self.terrainDefenseDictTable: Dict[str, Dict[str, float]] = {}

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
        self.heroTable = NameIdTableStructure[HeroRow](HeroRow())
        self.buildingTable = NameIdTableStructure[BuildingRow](BuildingRow())

        # adjust
        for v in self.__dict__.values():
            if isinstance(v, NameIdTableStructure) and isinstance(v.itemType, RowBase):
                for i in v.idDict.values():
                    i.refresh_property(self)
