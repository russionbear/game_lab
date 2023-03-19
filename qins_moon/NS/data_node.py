#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_node.py
# @time: 3/19/2023 10:16 AM

from typing import List

import numpy
import networkx

from qins_moon.core.asset import ConfigBase
from qins_moon.core.utils.data_structure import LocIdTableStructure, NameIdTableStructure
from qins_moon.advw.data_table import AdvwDataTable
from qins_moon.qm.tile_map.data_struction import IDataNodeInterface


# big node map
# city
# military
#  # city military


class LandNode:
    pass


class PersonNode:
    def __init__(self):
        self.id = 0
        self.name = ''


# people(amount, q), buildings(special),
class CityNode:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.loc = 0, 0
        self.flag = 0

        self.people = 10, 1.0
        self.income = 0
        self.canBuilding = []
        self.canProduce = []

        self.buildings = []
        self.tableRowId = 0


class TroopNode:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.loc = 0, 0
        self.flag = 0


class NSDataNode:
    def __init__(self):
        self.landGraph = networkx.Graph()
