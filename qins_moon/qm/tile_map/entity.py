#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: entity.py
# @time: 3/12/2023 9:57 PM
import os
import pickle
from typing import List, Type

import numpy

from qins_moon.core.asset import AssetPackage, AssetManager
from qins_moon.core.director import EntityBase, RootEntityBase, RootEntityManager
from qins_moon.core.grid_map import GridMovement, GridStaticMoveController, GridNavigation, GridNavigationManager
from qins_moon.core.render.component import JoinedLayerSurfaceRenderComponent, JoinedSurfaceRuleBase, \
    AnimeRenderComponent, InfoRenderComponent
from qins_moon.core.render.render import SceneBase, SceneManager
from qins_moon.core.render.scene import TileMapSceneBase
from qins_moon.core.utils.data_structure import TableRowBase, NameIdTableStructure, LocIdTableStructure

from qins_moon.qm.tile_map.data_struction import IDataNodeInterface
from qins_moon.qm.tile_map.config import ConfigBase


class TerrainLayerData(TableRowBase):
    def __init__(self):
        super().__init__()
        self.layer = 0  # zindex
        self.terrainMap: numpy.ndarray | None = None
        self.dataTable: NameIdTableStructure | None = None
        self.entity: TerrainLayerEntity | None = None
        self.modelPrefix = ''


class TerrainLayerEntity(EntityBase):
    """
    1. 传入的terrain_map/permMap 和 table 等 在它的生命周期内具有持久性
    2. 必需有相同modelName 前缀 + '.'
    """
    def __init__(self, config, pkg, union_render, table: NameIdTableStructure, model_prefix, terrain_map, grid_nav=None,
                 layer=1):
        super().__init__()
        self.config: ConfigBase = config
        self.assetPackage: AssetPackage = pkg
        self.modelPrefix = model_prefix

        self.joinedLayerRender: JoinedLayerSurfaceRenderComponent = union_render

        joined_suf_rule_dict = {}
        for i1, i in table.idDict.items():
            tmp_d = JoinedSurfaceRuleBase()
            joined_suf_rule_dict[i1] = tmp_d
            tmp_d.id = i1
            tmp_d.rules = self.assetPackage.get_joined_surface_rule(self.modelPrefix+'.'+i.name)

        self.layer = layer
        self.permMap: numpy.ndarray = terrain_map
        self.joinedLayerRender.add_layer_surface(joined_suf_rule_dict, terrain_map, grid_nav, layer)

    def refresh_node(self, loc, v):
        terrain_map = self.permMap
        terrain_map[loc[1], loc[0]] = v
        self.joinedLayerRender.refresh_data(loc, v, self.layer, True)

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        height, width = terrain_map.shape

        for drt in directions:
            x_, y_ = drt[0] + loc[0], drt[1] + loc[1]
            if x_ < 0 or y_ < 0 or x_ >= width or y_ >= height:
                continue
            self.joinedLayerRender.refresh_data((x_, y_), terrain_map[y_, x_], self.layer, True)


class JoinedTerrainLayerEntity(EntityBase):
    def __init__(self, config, pkg, scene, map_size, terrain_layer_storage, grid_nav=None, zindex=(1, 1), interval=0,
                 layer_nu=1):
        super().__init__()
        self.config: ConfigBase = config
        self.assetPackage: AssetPackage = pkg
        self.worldScene: SceneBase = scene

        self.terrainLayerStorage: NameIdTableStructure[TerrainLayerData] = terrain_layer_storage

        self.joinedLayerRender = JoinedLayerSurfaceRenderComponent(self.config, map_size, interval, layer_nu)
        self.joinedLayerRender.zindex = zindex
        self.joinedLayerRender.set_scene(self.worldScene)

        for k, v in self.terrainLayerStorage.idDict.items():
            v.entity = TerrainLayerEntity(
                self.config, self.assetPackage, self.joinedLayerRender, v.dataTable, v.modelPrefix, v.terrainMap,
                grid_nav, v.layer
            )
            self.add_child(v.entity)

        self.joinedLayerRender.refresh_surface()

    def refresh_node(self, layer_key, loc, v):
        self.terrainLayerStorage[layer_key].entity.refresh_node(loc, v)


# dyn
# provide action: finite state


class UnitEntityBase(EntityBase):

    def __init__(self, id_, scene, perm_data, pkg, config, grid_nav=None, z_index=1, layer=1, model_name=''):
        super().__init__()
        self.config: ConfigBase = config
        self.permData = perm_data
        self.layer = layer

        self.id = id_

        self.animationComponent = AnimeRenderComponent(model_name, pkg)
        self.infoComponent = InfoRenderComponent(self.animationComponent.get_surface().get_size(),
                                                 config, pkg)
        self.animationComponent.set_scene(scene)
        self.infoComponent.set_scene(scene)
        self.animationComponent.zindex = z_index, 1
        self.infoComponent.zindex = z_index, 2
        self.infoComponent.title = " "

        loc = 0, 0
        loc = self.config.MAP_BLOCK_SIZE[0] * loc[0] + self.config.MAP_BLOCK_SIZE[0] // 2, \
            self.config.MAP_BLOCK_SIZE[1] * loc[1] + self.config.MAP_BLOCK_SIZE[1] // 2

        self.movement = GridMovement(loc, 300)
        self.gridNav: GridNavigation = grid_nav
        self.gridMoveController = GridStaticMoveController(self.movement, config.MAP_BLOCK_SIZE)
        self.actionController = UnitActionControllerComponent(self.animationComponent, self.gridMoveController)
        self.actionController.sub_action_finished(self._handle_action_finished)
        self.unitIdShouldRefreshAfterAction = []
        self.refresh_info()

    def refresh_info(self):
        self.infoComponent.title = self.permData.name
        grid_loc = self.permData.loc
        loc = self.config.MAP_BLOCK_SIZE[0] * grid_loc[0] + self.config.MAP_BLOCK_SIZE[0] // 2, \
            self.config.MAP_BLOCK_SIZE[1] * grid_loc[1] + self.config.MAP_BLOCK_SIZE[1] // 2
        self.movement.loc = loc

    def update(self, delta_time):
        self.gridMoveController.update(delta_time)
        self.infoComponent.update(delta_time)
        self.animationComponent.update(delta_time)
        self.movement.update(delta_time)
        loc = self.movement.loc
        self.infoComponent.loc = loc
        self.animationComponent.loc = loc

    def _handle_action_finished(self, index):
        # print('index', index)
        if index + 1 == len(self.actionController.actions):
            self.refresh_info()
            for i in self.unitIdShouldRefreshAfterAction:
                self.parent.refresh_node(i)
            self.parent.pub_unit_action_finished(self.id)

    def pop_render(self):
        self.animationComponent.set_scene(None)
        self.infoComponent.set_scene(None)

    def insert_render(self):
        self.animationComponent.set_scene(self.parent.worldScene)
        self.infoComponent.set_scene(self.parent.worldScene)


class UnitActionControllerComponent:
    """
    actions: List[list(road) | str(anime)] + refresh_info
    """
    def __init__(self, anime_cmp, grid_ctrl):
        self.animationComponent: AnimeRenderComponent = anime_cmp
        self.gridMoveController: GridStaticMoveController = grid_ctrl

        self.actions: List[List[str] | list] = []
        self.currentActionIndex = 0

        self.gridMoveController.sub_task_finished(self.handle_road_finished)
        self.gridMoveController.sub_next_point_allocated(self.handle_next_point_allocated)
        self.animationComponent.sub_tmp_anime_state_finished(self.handle_anime_state_finished)

        self._actionFinishedHandler = None

    def sub_action_finished(self, v):
        self._actionFinishedHandler = v

    def _pub_action_finished(self, index):
        # print(self._actionFinishedHandler, index)
        if self._actionFinishedHandler is not None:
            self._actionFinishedHandler(index)

    def set_actions(self, actions):
        if not actions:
            return
        self.actions = actions
        self.currentActionIndex = -1

        self._next_action()

    def _next_action(self):
        self.currentActionIndex += 1
        if self.currentActionIndex >= len(self.actions):
            # self.actions.clear()
            return
        current_action = self.actions[self.currentActionIndex]
        if type(current_action[0]) == str:
            self.animationComponent.anime_state = current_action
        else:
            self.gridMoveController.set_task(current_action)

    def handle_next_point_allocated(self, o_p, n_p):
        pass

    def handle_road_finished(self, **kwargs):
        self._pub_action_finished(self.currentActionIndex)
        self._next_action()

    def handle_anime_state_finished(self):
        self._pub_action_finished(self.currentActionIndex)
        self._next_action()


class UnitLayerEntityBase(EntityBase):
    """
    permData 必须有属性tableRowId
    """
    def __init__(self, scene, pkg, config, grid_nav, id_data_dict, z_index, layer, table_model_dict):
        super().__init__()
        self.worldScene: SceneBase = scene
        self.assetPackage: AssetPackage = pkg
        self.config: ConfigBase = config
        self.gridNav: GridNavigation = grid_nav

        self.renderZIndex = z_index
        self.layer = layer
        self.tableRowModelNameDict = table_model_dict
        self.permDataDict = id_data_dict

        for k, v in id_data_dict.items():
            self.make_child_entity(k)

        self.isHidden = False
        self._handleUnitActionFinished = None

    def make_child_entity(self, perm_key):
        tmp_e = UnitEntityBase(perm_key, self.worldScene, self.permDataDict[perm_key], self.assetPackage, self.config,
                               self.gridNav, self.renderZIndex, self.layer,
                               self.tableRowModelNameDict[self.permDataDict[perm_key].tableRowId])
        self.add_child(tmp_e)
        # tmp_e.actionController.sub_action_finished(self.pub_unit_action_finished)
        return tmp_e

    def refresh_node(self, id_):
        data_dict = self.permDataDict
        child: UnitEntityBase = self.find_child_by_id(id_)
        troop_dict = data_dict
        if id_ in troop_dict and child is None:

            tmp_e = self.make_child_entity(id_)
            if self.isHidden:
                tmp_e.pop_render()
            self.add_child(tmp_e)
        elif id_ not in troop_dict and child is not None:
            self.remove_child(child)
            child.pop_render()

        elif id_ in troop_dict:
            child.refresh_info()

    def show_render(self):
        self.isHidden = False
        for i in self._children.list():
            i: UnitEntityBase = i
            i.insert_render()

    def hide_render(self):
        self.isHidden = True
        for i in self._children.list():
            i: UnitEntityBase = i
            i.pop_render()

    def sub_unit_action_finished(self, v):
        self._handleUnitActionFinished = v

    def pub_unit_action_finished(self, id_):
        """
        don't call it directly
        :param id_:
        :return:
        """
        if self._handleUnitActionFinished is not None:
            self._handleUnitActionFinished(u_id=id_, l_id=self.id)


class UnitLayerData(TableRowBase):
    def __init__(self):
        super().__init__()
        self.layer = 0
        self.zIndex = 0
        self.unitDict: LocIdTableStructure[UnitEntityBase] | None = None
        self.entity: UnitLayerEntityBase | None = None
        self.dataTable: NameIdTableStructure | None = None
        self.tableModelDict = {}


class JoinedUnitLayerEntity(EntityBase):
    def __init__(self, config, pkg, scene, unit_layer_storage, grid_nav=None):
        super().__init__()
        self.config: ConfigBase = config
        self.assetPackage: AssetPackage = pkg
        self.worldScene: SceneBase = scene
        self.gridNav: GridNavigation = grid_nav

        self.unitLayerStorage: NameIdTableStructure[UnitLayerData] = unit_layer_storage

        for k, v in self.unitLayerStorage.idDict.items():
            self.make_layer_entity(v)

        self._handleUnitActionFinished = None

    def make_layer_entity(self, v: UnitLayerData):
        v.entity = UnitLayerEntityBase(
            self.worldScene, self.assetPackage, self.config, self.gridNav, v.unitDict.idDict,
            v.zIndex, v.layer, v.tableModelDict)
        v.entity.id = v.id
        self.add_child(v.entity)

    def refresh_node(self, key, id_):
        self.unitLayerStorage[key].entity.refresh_node(id_)

    def _pub_unit_action_finished(self, u_id, l_id):
        if self._handleUnitActionFinished is not None:
            self._handleUnitActionFinished(u_id, self.unitLayerStorage[l_id].name)

    def sub_unit_action_finished(self, v):
        self._handleUnitActionFinished = v

#


class TileMapRootEntity(RootEntityBase):
    """
    默认调用顺序: load_map | load_asset -> init_map -> register_map -> unload_map -> unload_asset
    """
    def __init__(self, config):
        super().__init__()
        self.config: ConfigBase = config
        self.assetPackage: AssetPackage | None = None
        self.worldScene: TileMapSceneBase | None = None

        self.gridNavComponent: GridNavigation | None = None

        self.terrainLayer: JoinedTerrainLayerEntity | None = None
        self.unitLayer: JoinedUnitLayerEntity | None = None
        self.rootDataNode: IDataNodeInterface | None = None

    def load_asset(self):
        asset_mngr = AssetManager()
        asset_mngr.init(self.config)
        asset_pkg = AssetManager().load_resource(self.config.ASSET_PACKAGE_ID)
        self.assetPackage = asset_pkg

    def make_map(self):
        """
        不要直接调用
        :return:
        """
        pass

    def save_map(self):
        with open(os.path.join(self.config.MAP_STORAGE_PATH, self.config.mapName),
                  'wb') as f:  # 打开文件
            pickle.dump(self.rootDataNode, f)

    def load_map(self):
        config = self.config
        if not os.path.exists(os.path.join(config.MAP_STORAGE_PATH, config.mapName)):
            data_node = self.make_map()
            with open(os.path.join(config.MAP_STORAGE_PATH, config.mapName), 'wb') as f:
                pickle.dump(data_node, f)

        with open(os.path.join(config.MAP_STORAGE_PATH, config.mapName), 'rb') as f:
            data_node = pickle.load(f)

        self.rootDataNode = data_node

    # region init map
    def init_map(self):
        self.make_world_scene()
        self.make_nav_data()
        self.make_terrain_layer()
        self.make_unit_layer()

    def make_world_scene(self):
        map_size = self.rootDataNode.map_size()
        # world scene
        self.worldScene = TileMapSceneBase(
            (map_size[0] * self.config.MAP_BLOCK_SIZE[0],
             map_size[1] * self.config.MAP_BLOCK_SIZE[1]), self.config.MAP_BLOCK_SIZE)

    def make_nav_data(self):
        pass

    def make_terrain_layer(self):
        # print(self.config.__dict__)
        # print(self.rootDataNode.map_size())
        map_size = self.rootDataNode.map_size()
        self.terrainLayer = JoinedTerrainLayerEntity(
            self.config, self.assetPackage, self.worldScene, map_size,
            self.gridNavComponent)
        self.add_child(self.terrainLayer)

    def make_unit_layer(self):
        self.unitLayer = JoinedUnitLayerEntity(
            self.config, self.assetPackage, self.worldScene, self.gridNavComponent
        )
        self.add_child(self.unitLayer)

    # endregion

    def register_map(self):
        SceneManager()[self.config.SYSTEM_KEY] = self.worldScene
        SceneManager().switch_scene(self.config.SYSTEM_KEY)
        RootEntityManager()[self.config.SYSTEM_KEY] = self
        RootEntityManager().switch_root_entity(self.config.SYSTEM_KEY)

    def unload_map(self):
        SceneManager().switch_scene(None)
        del SceneManager()[self.config.SYSTEM_KEY]
        self._children.clear()
        del RootEntityManager()[self.config.SYSTEM_KEY]
        RootEntityManager().switch_root_entity(None)
        if self.gridNavComponent is not None:
            del GridNavigationManager()[self.config.SYSTEM_KEY]

    def unload_asset(self):
        del AssetManager()[self.assetPackage.packageId]
