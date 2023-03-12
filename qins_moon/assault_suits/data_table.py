#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_table.py
# @time: 3/10/2023 5:56 PM
import json
from typing import Dict

from qins_moon.core.utils.data_structure import TableRowBase, NameIdTableStructure
from qins_moon.core.utils.data_table_loader import DataTableMaker

# geo


class TerrainRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.worldType = ''
        self.canTankPass = True
        self.canPersonPass = True


class BuildingRow(TerrainRow):
    def __init__(self):
        super().__init__()
        self.canTankPass = True
        self.canPersonPass = True


class DecorationRow(TableRowBase):
    pass


# goods

class SellListRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.tankDevices: list | str = []
        self.tankTools: list | str = []
        self.personEquips: list | str = []
        self.personTools: list | str = []

    def correct_property_type(self):
        super().correct_property_type()
        self.tankDevices = json.loads(self.tankDevices)
        self.tankTools = json.loads(self.tankTools)
        self.personEquips = json.loads(self.personEquips)
        self.personTools = json.loads(self.personTools)


class UnderGoodsRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.tankDevices: list | str = []
        self.tankTools: list | str = []
        self.personEquips: list | str = []
        self.personTools: list | str = []

    def correct_property_type(self):
        super().correct_property_type()
        self.tankDevices = json.loads(self.tankDevices)
        self.tankTools = json.loads(self.tankTools)
        self.personEquips = json.loads(self.personEquips)
        self.personTools = json.loads(self.personTools)


# tool


class TankDeviceRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.price = 0
        self.deviceType = ''  # cDevice, engine, weapon, secondWeapon, seWeapon
        self.deviceWeight = 0

        self.defenseValue = 0
        self.defenseTypes: list | str = []

        self.engineLoadWeight = 0

        self.weaponAttackType = ''
        self.weaponAttackValue = ''
        self.weaponMaxBulletNu = 0
        self.canDrop = True
        self.canMove = True

    def correct_property_type(self):
        super().correct_property_type()
        self.defenseTypes = json.loads(self.defenseTypes)


class TankToolRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.price = 0
        self.dsc = ''
        self.toolWeight = 0
        self.canDrop = True
        self.canMove = True


class PersonEquipRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.price = 0
        self.equipType = ''  # weapon, tap, cloth, innerCloth, shoe, hand

        self.defenseValue = 0
        self.defenseTypes: list | str = []
        self.weaponAttackType = ''
        self.weaponAttackValue = ''
        self.canDrop = True
        self.canMove = True

    def correct_property_type(self):
        super().correct_property_type()
        self.defenseTypes = json.loads(self.defenseTypes)


class PersonToolRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.price = 0
        self.toolType = ""  # blood, weapon, other

        self.bloodValue = 90

        self.weaponType = ''
        self.weaponValue = ''

        self.otherFunctions: list | str = []
        self.canDrop = True
        self.canMove = True

    def correct_property_type(self):
        super().correct_property_type()
        self.otherFunctions = json.loads(self.otherFunctions)


# classic


class TankClassicRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.weight = 90

        self.defenseTypes: list | str = []
        self.defenseValue = 0

        self.mainWeaponHoleNu = 1
        self.secondWeaponHoleNu = 1
        self.seWeaponHoleNu = 1

    def correct_property_type(self):
        super().correct_property_type()
        self.defenseTypes = json.loads(self.defenseTypes)


class PersonClassicRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.profession = ''  # hunter, machinist

        self.basicAttackValue = ''
        self.basicDefenseValue = ''
        self.basicMaxBloodValue = 0


# monster


class WildTankRow(TankToolRow):
    def __init__(self):
        super().__init__()

        self.mainWeaponDevice = 0, 0, 0
        self.secondWeaponDevice = 0, 0, 0
        self.seWeaponDevice = 0, 0, 0
        self.cDevice = 0, 0
        self.classicDevice = 0, 0
        self.engineDevice = 0, 0
        self.armor = 90
        self.tankTools: list | str = []

        self.canBeOccupy = False

    def correct_property_type(self):
        super().correct_property_type()
        self.tankTools = json.loads(self.tankTools)


class MessengerRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.isWander = False
        self.statement = ""
        self.tankTableRowId = 1


class MonsterRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.isTank = False

        # person
        self.weaponEquip = 0
        self.innerClothEquip = 0
        self.clothEquip = 0
        self.capEquip = 0
        self.shoeEquip = 0
        self.handEquip = 0
        self.personTools: list | str = []

        # tank
        self.mainWeaponDevice = 0, 0, 0
        self.secondWeaponDevice = 0, 0, 0
        self.seWeaponDevice = 0, 0, 0
        self.cDevice = 0, 0
        self.classicDevice = 0, 0
        self.engineDevice = 0, 0
        self.armor = 90
        self.tankTools: list | str = []

        # drop
        self.dropPersonTools: dict | str = {}
        self.dropPersonEquip: dict | str = {}
        self.dropTankTools: dict | str = {}
        self.dropTankEquip: dict | str = {}
        self.dropExperience = 0
        self.dropMoney = 0

    def correct_property_type(self):
        super().correct_property_type()
        self.personTools = json.loads(self.personTools)
        self.tankTools = json.loads(self.tankTools)
        self.dropPersonEquip = json.loads(self.dropPersonEquip)
        self.dropPersonTools = json.loads(self.dropPersonTools)
        self.dropTankTools = json.loads(self.dropTankTools)
        self.dropTankEquip = json.loads(self.dropTankEquip)


class MonsterGroupRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.persons: list | str = []
        self.tanks: list | str = []
        self.carryCondition: dict | str = {}  # {Person index: Tank index}
        self.isWanted = False

    def correct_property_type(self):
        super().correct_property_type()
        self.persons = json.loads(self.persons)
        self.tanks = json.loads(self.tanks)
        self.carryCondition = json.loads(self.carryCondition)


# statement

class TalkStatementRow(TableRowBase):
    def __init__(self):
        super().__init__()
        self.statements: list | str = ''
        self.chooseItems: Dict[str, str] | str = {}  # 选项以及对应的下一个statement， {}就默认id+1, ""默认推出

    def correct_property_type(self):
        super().correct_property_type()
        self.statements = json.loads(self.statements)
        self.chooseItems = json.loads(self.chooseItems)


class GeneralTable:
    def __init__(self):
        self.underGoodsEditModelName = ""
        self.monsterModelName = ""
        self.tankEditModelName = ""
        self.messengerEditModelName = ""


class AssaultSuitsDataTable:
    def __init__(self):
        self.generalTable = GeneralTable()

        self.terrainTable = NameIdTableStructure[TerrainRow](TerrainRow())
        self.buildingTable = NameIdTableStructure[BuildingRow](BuildingRow())
        self.decorationTable = NameIdTableStructure[DecorationRow](DecorationRow())
        self.sellListTable = NameIdTableStructure[SellListRow](SellListRow())
        self.underGoodsTable = NameIdTableStructure[UnderGoodsRow](UnderGoodsRow())
        self.tankDeviceTable = NameIdTableStructure[TankDeviceRow](TankDeviceRow())
        self.tankToolTable = NameIdTableStructure[TankToolRow](TankToolRow())
        self.personEquipTable = NameIdTableStructure[PersonEquipRow](PersonEquipRow())
        self.personToolTable = NameIdTableStructure[PersonToolRow](PersonToolRow())
        self.tankClassicTable = NameIdTableStructure[TankClassicRow](TankClassicRow())
        self.personClassicTable = NameIdTableStructure[PersonClassicRow](PersonClassicRow())
        self.wildTankTable = NameIdTableStructure[WildTankRow](WildTankRow())
        self.messengerTable = NameIdTableStructure[MessengerRow](MessengerRow())
        self.monsterTable = NameIdTableStructure[MonsterRow](MonsterRow())
        self.monsterGroupTable = NameIdTableStructure[MonsterGroupRow](MonsterGroupRow())
        self.talkStatementTable = NameIdTableStructure[TalkStatementRow](TalkStatementRow())


# if __name__ == '__main__':
#     DataTableMaker.make_table(AssaultSuitsDataTable(), r'E:\workspace\game_lab\qins_moon\res\tables\test\as\ttt')
