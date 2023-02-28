#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :01_asset_load.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function

from qins_moon.core.utils.data_table_loader import DataTableLoader
from qins_moon.core.asset import AssetManager, ConfigBase
from data_table import Cv6DataTable
import pygame


TEST_ASSET_PACKAGE_ID = ('test', 'core', 'politics')
TEST_TABLE_ID = 'test', 'core', 'politics'


def load_table():
    config = ConfigBase()
    DataTableLoader.table_storage_path = config.TABLE_STORAGE_PATH
    DataTableLoader.load_data(*TEST_TABLE_ID, Cv6DataTable())


def load_asset_package():
    pygame.init()
    window = pygame.display.set_mode((800, 600))
    am = AssetManager()
    config = ConfigBase()
    am.init(config)
    pkg = am.load_resource(TEST_ASSET_PACKAGE_ID)
    print(pkg)


if __name__ == '__main__':
    load_asset_package()
    load_table()
    pass
