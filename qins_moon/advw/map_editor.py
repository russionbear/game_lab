#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: map_editor.py
# @time: 3/13/2023 6:31 PM
# easy version
from queue import Queue
from typing import Any

from qins_moon.advw.data_node import AdvwDataNode, PlayerNode
from qins_moon.advw.data_table import AdvwDataTable
from qins_moon.advw import data_driver as _data_driver
from qins_moon.core.utils.data_structure import NameIdTableStructure
from qins_moon.core.utils.data_table_loader import DataTableLoader
from qins_moon.qm.tile_map.config import ConfigBase
from qins_moon.qm.tile_map.entity import TileMapRootEntity, UnitLayerData, TerrainLayerData, JoinedTerrainLayerEntity, \
    JoinedUnitLayerEntity
from qins_moon.qm.tile_map.ui_state import TileMapUIStateMngr, TileMapEditUS, run_tile_map


class Config(ConfigBase):
    def __init__(self, map_name=None):
        super().__init__(map_name)

        self.ASSET_PACKAGE_ID = 'test', 'core', 'politics'
        self.DATA_TABLE_ID = 'test', 'advw', 'advw'
        self.SYSTEM_KEY = 'runtime'

        self.defaultInitMapSize = 16, 16
        self.defaultBlockSize = 50, 50


class TerrainLayerEntity(JoinedTerrainLayerEntity):
    def __init__(self, dn, config, pkg, scene, map_size, grid_nav=None, zindex=(1, 1), interval=0,
                 layer_nu=1):
        self.rootDataNode: AdvwDataNode = dn
        # region make some data
        terrain_layer_storage = NameIdTableStructure[TerrainLayerData]()
        tmp_d = TerrainLayerData()
        tmp_d.id = 1
        tmp_d.name = 'terrain'
        tmp_d.layer = 1
        tmp_d.terrainMap = self.rootDataNode.terrainMap
        tmp_d.dataTable = self.rootDataNode.dataTable.terrainTerrainTable
        tmp_d.modelPrefix = 'terrain'
        terrain_layer_storage.add(tmp_d)

        tmp_d = TerrainLayerData()
        tmp_d.id = 2
        tmp_d.name = 'traffic'
        tmp_d.layer = 2
        tmp_d.terrainMap = self.rootDataNode.trafficMap
        tmp_d.dataTable = self.rootDataNode.dataTable.trafficTable
        tmp_d.modelPrefix = 'traffic'
        terrain_layer_storage.add(tmp_d)

        tmp_d = TerrainLayerData()
        tmp_d.id = 3
        tmp_d.name = 'decoration'
        tmp_d.layer = 3
        tmp_d.terrainMap = self.rootDataNode.decorationMap
        tmp_d.dataTable = self.rootDataNode.dataTable.decorationTable
        tmp_d.modelPrefix = 'decoration'
        terrain_layer_storage.add(tmp_d)
        # endregion
        super().__init__(config, pkg, scene, map_size, terrain_layer_storage, grid_nav, zindex, interval, layer_nu)


class UnitLayerEntity(JoinedUnitLayerEntity):
    def __init__(self, dn, config, pkg, scene, grid_nav=None):
        self.rootDataNode: AdvwDataNode = dn

        # region unit layer storage
        unit_layer_storage = NameIdTableStructure[UnitLayerData]()
        tmp_d = UnitLayerData()
        tmp_d.id = 4
        tmp_d.name = 'building'
        tmp_d.layer = 4
        tmp_d.zIndex = 4
        tmp_d.unitDict = dn.buildingDict
        tmp_d.dataTable = dn.dataTable.buildingTable
        tmp_d.tableModelDict = {v.id: v.modelName for k, v in dn.dataTable.buildingTable.idDict.items()}
        tmp_d.modelPrefix = 'building'
        unit_layer_storage.add(tmp_d)

        tmp_d = UnitLayerData()
        tmp_d.id = 5
        tmp_d.name = 'military'
        tmp_d.layer = 5
        tmp_d.zIndex = 5
        tmp_d.unitDict = dn.militaryDict
        tmp_d.dataTable = dn.dataTable.militaryTable
        tmp_d.tableModelDict = {v.id: v.modelName for k, v in dn.dataTable.militaryTable.idDict.items()}
        tmp_d.modelPrefix = 'military'
        unit_layer_storage.add(tmp_d)
        # endregion

        super().__init__(config, pkg, scene, unit_layer_storage, grid_nav)


class MapEditRootEntity(TileMapRootEntity):

    def __init__(self, config):
        super().__init__(config)
        self.config: Config = config
        self.rootDataNode: AdvwDataNode | Any = self.rootDataNode

    def make_map(self):
        config = self.config
        DataTableLoader.table_storage_path = config.TABLE_STORAGE_PATH
        data_table = DataTableLoader.load_data(*config.DATA_TABLE_ID, AdvwDataTable())
        data_node = AdvwDataNode.make_data(config.defaultInitMapSize, data_table, 100)
        data_node.config = config
        return data_node

    def make_terrain_layer(self):
        self.terrainLayer = TerrainLayerEntity(
            self.rootDataNode, self.config, self.assetPackage, self.worldScene, self.rootDataNode.map_size(),
            self.gridNavComponent)
        self.add_child(self.terrainLayer)

    def make_unit_layer(self):
        self.unitLayer = UnitLayerEntity(
            self.rootDataNode, self.config, self.assetPackage, self.worldScene, self.gridNavComponent)
        self.add_child(self.unitLayer)

    def save_map(self):
        flag_id_color_dict = {
            1: 'red', 2: 'blue', 3: 'green', 4: 'yellow', 5: 'aliceBlue',
            6: 'coral', 7: 'hotPink', 8: 'linen'
        }
        flags = set()
        for v in self.rootDataNode.buildingDict.idDict.values():
            flags.add(v.flagId)
        for v in self.rootDataNode.militaryDict.idDict.values():
            flags.add(v.flagId)

        self.rootDataNode.playerDict.clear()
        for i in flags:
            tmp_player = PlayerNode()
            tmp_player.id = i
            tmp_player.name = flag_id_color_dict[i]
            self.rootDataNode.playerDict.add(tmp_player)
        self.rootDataNode.currentPlayerId = list(flags)[0]
        super().save_map()


class MapEditUIStateMngr(TileMapUIStateMngr):
    STATE_HOME = 0x1

    def __init__(self, root_e):
        super().__init__(root_e)
        self.mapEditUS = MapEditUI(self)
        self[self.STATE_HOME] = self.mapEditUS

        self.currentUIState = self[self.STATE_HOME]


class MapEditUI(TileMapEditUS):
    def handle_make_unit(self, loc, v) -> Any:
        dn: AdvwDataNode | Any = self.mngr.rootEntity.rootDataNode
        if self.homeUI.layerButton.selected_option == 'building':
            return dn.make_building(v, loc, int(self.homeUI.flagButton.selected_option))
        elif self.homeUI.layerButton.selected_option == 'military':
            return dn.make_military(v, loc, int(self.homeUI.flagButton.selected_option))


if __name__ == '__main__':
    __config = Config()
    run_tile_map(__config, MapEditRootEntity, MapEditUIStateMngr)
