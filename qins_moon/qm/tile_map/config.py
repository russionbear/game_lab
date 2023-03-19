#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: config.py
# @time: 3/13/2023 4:43 PM
import os

from qins_moon.core.asset import ConfigBase as _ConfigBase


class ConfigBase(_ConfigBase):
    """
    promise: nav_layer_id = (flag << 8) + engineId
    """
    def __init__(self, map_name=None):
        super().__init__()
        self.MAP_STORAGE_PATH = os.path.join(self.MAP_STORAGE_PATH, 'tile_map')
        self.ASSET_PACKAGE_ID = 'test', 'demo', 'advw'
        self.SYSTEM_KEY = 'tile_map'

        self.defaultInitMapSize = 16, 16
        self.defaultBlockSize = 50, 50
        self.mapName = 'tile_map' if map_name is None else map_name
