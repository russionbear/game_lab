#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :config.py
# @Time      :22/02/2023
# @Author    :russionbear
# @Function  :function

from qins_moon.core.asset import ConfigBase


class Config(ConfigBase):
    def __init__(self):
        super().__init__()
        self.SYSTEM_KEY = 'POLITY'
        self.DATA_TABLE_ID = 'test', 'core', 'politics'
        self.ASSET_PACKAGE_ID = 'test', 'core', 'politics'
        self.MAP_ID = 'test'
        self.blockMapSize = 16, 16
