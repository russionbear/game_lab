#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :grid_navigation.py
# @Time      :07/02/2023
# @Author    :russionbear
# @Function  :function
from typing import Dict, Tuple, List, Any

import numpy

from qins_moon.core.utils.data_structure import RegistryBase
from qins_moon.core.interface.grid_map import IGridNavigationInterface


class GridNavigation(IGridNavigationInterface):
    pass


class GridNavigationManager(RegistryBase[GridNavigation]):
    _instance = None

    def __init__(self):
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self
        super().__init__()

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)


class GridBigMapNavNodeInfo:
    def __init__(self):
        self.endpoints = 0, 0, 0, 0
        self.pointOnLine


class GridBigMapNavNodeStorage:
    def __init__(self, name, grid_nav, engine):
        self.storageName = name
        self.gridNavigation: IGridNavigationInterface = grid_nav
        self.moveEngine = engine
