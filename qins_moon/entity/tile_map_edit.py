#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: tile_map_edit.py
# @time: 3/13/2023 1:29 PM


import os
from typing import Dict
import pickle

import numpy
import pygame
import pygame_gui
from pygame_gui import elements

from qins_moon.core.asset import ConfigBase, AssetPackage, AssetManager
from qins_moon.core.director import EntityBase, RootEntityBase, RootEntityManager, IUIStateInterface, \
    UIStateManagerBase, Director
from qins_moon.core.grid_map import GridMovement, GridStaticMoveController
from qins_moon.core.render.component import JoinedLayerSurfaceRenderComponent, JoinedSurfaceRuleBase, \
    AnimeRenderComponent, InfoRenderComponent
from qins_moon.core.render.render import SceneBase, SceneManager, SceneCircleBase
from qins_moon.core.ui_element import UserInterfaceBase, UserInterfaceManager
from qins_moon.core.utils.data_structure import NameIdTableStructure, TableRowBase, LocIdTableStructure

from qins_moon.core.utils.data_table_loader import DataTableLoader
from qins_moon.advw.data_node import AdvwDataTable, AdvwDataNode


# config


class Config(ConfigBase):
    def __init__(self, map_name=None):
        super().__init__()
        self.ASSET_PACKAGE_ID = 'test', 'core', 'politics'
        self.DATA_TABLE_ID = 'test', 'advw', 'advw'
        self.SYSTEM_KEY = 'map_edit'

        self.defaultInitMapSize = 16, 16
        self.defaultBlockSize = 50, 50

        self.mapName = 'advw' if map_name is None else map_name


# world scene


class TileMapEditScene(SceneBase):
    def __init__(self, size, block_size):
        super().__init__()
        self.blockSize = block_size
        self.surface = pygame.Surface(size).convert_alpha()
        self.camera.handle_resize()
        self.circle = SceneCircleBase(self)
        self.canDrawCircle = True

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def get_mouse_grid_loc(self):
        loc = self.get_mouse_loc_in_scene()
        return int(loc[0]//(self.blockSize[0]*self.scale)), int(loc[1]//(self.blockSize[1]*self.scale))

    def get_current_legal_circle_grid_area(self, map_size):
        block_size = self.blockSize[0] * self.scale, self.blockSize[1] * self.scale
        circle_area = self.circle.get_scene_circle_grid_area(block_size)

        if circle_area[0] < 0:
            circle_area = 0, *circle_area[1:]
        if circle_area[1] < 0:
            circle_area = circle_area[0], 0, *circle_area[2:]
        if circle_area[2] > map_size[0]:
            circle_area = *circle_area[:2], map_size[0], circle_area[-1]
        if circle_area[3] > map_size[1]:
            circle_area = *circle_area[:3], circle_area[-1]

        circle_area = int(circle_area[0]), int(circle_area[1]), int(circle_area[2]), int(circle_area[3])
        return circle_area

    def event(self, e0: pygame.event.Event):
        super().event(e0)
        if self.canDrawCircle:
            self.circle.event(e0)

    def draw(self):
        # suf = self.get_surface()
        # suf.fill((0, 0, 0, 0))
        # for v in self._children:
        #     v.draw()
        #
        # if self.scale != 1:
        #     suf = pygame.transform.smoothscale(suf, (suf.get_width()*self.scale, suf.get_height()*self.scale))
        #
        # size = suf.get_size()
        # loc = self.loc[0] - size[0] // 2, self.loc[1] - size[1] // 2
        # self._blitWindow.blit(suf, loc)
        super().draw()
        self.circle.draw()


# entity
''
# base layer


class TerrainLayerEntityBase(EntityBase):
    """只有一个terrain类型的map"""

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
            # tmp_d.rules = [({}, self.assetPackage.get_sprite(i.modelName))]
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


# dyn layer


class DynUnitEntityBase(EntityBase):

    def __init__(self, id_, scene, perm_data, pkg, config, z_index=1, model_name=''):
        super().__init__()
        self.config: Config = config
        self.permData = perm_data

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
        # print(loc)
        self.movement = GridMovement(loc, 100)
        self.gridMoveController = GridStaticMoveController(self.movement, config.MAP_BLOCK_SIZE)
        self.gridMoveController.sub_task_finished(self.handle_road_finished)
        self.gridMoveController.sub_next_point_allocated(self.handle_next_point_allocated)
        self.animationComponent.sub_tmp_anime_state_finished(self.handle_anime_state_finished)
        self.refresh_info()

        self.currentTask = 'wait'
        self.currentTaskParam = {}

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

    def handle_road_finished(self, **kwargs):
        # o_loc = self.rootDataNode.troopDict[self.id].loc
        # n_loc = self.gridMoveController.grid_loc()
        # self.gridNav.refresh_node(o_loc, 0, 3)
        # self.gridNav.refresh_node(n_loc, self.id, 3)
        if self.currentTask == 'wait':
            self.animationComponent.anime_state = 'wait'
        else:
            self.animationComponent.anime_state = 'attack'

    def handle_anime_state_finished(self):
        self.handle_task_finished()

    def handle_task_finished(self):
        self.parent.refresh_node(self.id)
        if self.currentTask == 'attack':
            self.parent.refresh_node(self.currentTaskParam['targetId'])

    def handle_next_point_allocated(self, o_p, n_p):
        pass


# # dyn layer


class GridDynLayerEntityBase(EntityBase):
    def __init__(self, scene, pkg, config, nav_layer, id_data_dict, z_index, table_model_dict):
        super().__init__()
        self.worldScene: SceneBase = scene
        self.assetPackage: AssetPackage = pkg
        self.config: Config = config
        self.navLayer = nav_layer

        self.renderZIndex = z_index
        self.tableRowModelNameDict = table_model_dict
        self.permDataDict = id_data_dict

        for k, v in id_data_dict.items():
            tmp_e = DynUnitEntityBase(k, self.worldScene, v,  self.assetPackage, self.config,
                                      self.renderZIndex, self.tableRowModelNameDict[v.tableRowId])
            self.add_child(tmp_e)

        self.isHidden = False

    def refresh_node(self, id_):
        data_dict = self.permDataDict
        child: DynUnitEntityBase = self.find_child_by_id(id_)
        troop_dict = data_dict
        if id_ in troop_dict and child is None:
            tmp_e = DynUnitEntityBase(id_, self.worldScene, self.permDataDict[id_],
                                      self.assetPackage, self.config,
                                      self.renderZIndex, self.tableRowModelNameDict[self.permDataDict[id_].tableRowId])
            if self.isHidden:
                tmp_e.animationComponent.set_scene(None)
                tmp_e.animationComponent.set_scene(None)
            self.add_child(tmp_e)
        elif id_ not in troop_dict and child is not None:
            self.remove_child(child)
            # ########## 释放资源
            child.animationComponent.set_scene(None)
            child.infoComponent.set_scene(None)

        elif id_ in troop_dict:
            child.refresh_info()

    def show_render(self):
        self.isHidden = False
        for i in self._children.list():
            i: DynUnitEntityBase = i
            i.animationComponent.set_scene(self.worldScene)
            i.infoComponent.set_scene(self.worldScene)

    def hide_render(self):
        self.isHidden = True
        for i in self._children.list():
            i: DynUnitEntityBase = i
            i.animationComponent.set_scene(None)
            i.infoComponent.set_scene(None)


# root entity


class TerrainLayerNode(TableRowBase):
    def __init__(self):
        super().__init__()
        self.layer = 0  # zindex
        self.terrainMap: numpy.ndarray | None = None
        self.dataTable: NameIdTableStructure | None = None
        self.entity: TerrainLayerEntityBase | None = None
        self.modelPrefix = ''


class DynLayerNode(TableRowBase):
    def __init__(self):
        super().__init__()
        self.layer = 0
        self.zIndex = 0
        self.unitDict: LocIdTableStructure[DynUnitEntityBase] | None = None
        self.entity: GridDynLayerEntityBase | None = None
        self.dataTable: NameIdTableStructure | None = None
        self.tableModelDict = {}
        self.newUnitFunc = None
        self.newUnitKwargs = {}


class MapEditRootEntity(RootEntityBase):
    def __init__(self, config, dt):
        super().__init__()

        self.config: Config = config
        self.rootDataNode: AdvwDataNode = dt
        self.assetPackage: AssetPackage | None = None
        self.worldScene: TileMapEditScene | None = None

        self.joinedLayerRender: JoinedLayerSurfaceRenderComponent | None = None

        self.terrainLayerStorage = NameIdTableStructure[TerrainLayerNode]()
        self.dynLayerStorage = NameIdTableStructure[DynLayerNode]()

    def init_load_asset(self):
        asset_mngr = AssetManager()
        asset_mngr.init(self.config)
        asset_pkg = AssetManager().load_resource(self.config.ASSET_PACKAGE_ID)
        self.assetPackage = asset_pkg

    def init_map(self):
        # user_flag = 10
        map_size = self.rootDataNode.map_size

        # world scene
        self.worldScene = TileMapEditScene((map_size[0] * self.config.MAP_BLOCK_SIZE[0],
                                            map_size[1] * self.config.MAP_BLOCK_SIZE[1]), self.config.MAP_BLOCK_SIZE)
        self.joinedLayerRender = JoinedLayerSurfaceRenderComponent(self.config, map_size)
        self.joinedLayerRender.zindex = 1, 1
        self.joinedLayerRender.set_scene(self.worldScene)

        # region init some data
        tmp_d = TerrainLayerNode()
        tmp_d.id = 1
        tmp_d.name = 'terrain'
        tmp_d.layer = 1
        tmp_d.terrainMap = self.rootDataNode.terrainMap
        tmp_d.dataTable = self.rootDataNode.dataTable.terrainTerrainTable
        tmp_d.modelPrefix = 'terrain'
        self.terrainLayerStorage.add(tmp_d)

        tmp_d = TerrainLayerNode()
        tmp_d.id = 2
        tmp_d.name = 'traffic'
        tmp_d.layer = 2
        tmp_d.terrainMap = self.rootDataNode.trafficMap
        tmp_d.dataTable = self.rootDataNode.dataTable.trafficTable
        tmp_d.modelPrefix = 'traffic'
        self.terrainLayerStorage.add(tmp_d)

        tmp_d = TerrainLayerNode()
        tmp_d.id = 3
        tmp_d.name = 'decoration'
        tmp_d.layer = 3
        tmp_d.terrainMap = self.rootDataNode.decorationMap
        tmp_d.dataTable = self.rootDataNode.dataTable.decorationTable
        tmp_d.modelPrefix = 'decoration'
        self.terrainLayerStorage.add(tmp_d)

        tmp_d = DynLayerNode()
        tmp_d.id = 4
        tmp_d.name = 'building'
        tmp_d.layer = 4
        tmp_d.zIndex = 4
        tmp_d.unitDict = self.rootDataNode.buildingDict
        tmp_d.dataTable = self.rootDataNode.dataTable.buildingTable
        tmp_d.tableModelDict = {v.id: v.modelName for k, v in self.rootDataNode.dataTable.buildingTable.idDict.items()}
        tmp_d.modelPrefix = 'building'
        tmp_d.newUnitFunc = self.rootDataNode.make_building
        tmp_d.newUnitKwargs = {'flag': 0}
        self.dynLayerStorage.add(tmp_d)

        tmp_d = DynLayerNode()
        tmp_d.id = 5
        tmp_d.name = 'military'
        tmp_d.layer = 5
        tmp_d.zIndex = 5
        tmp_d.unitDict = self.rootDataNode.militaryDict
        tmp_d.dataTable = self.rootDataNode.dataTable.militaryTable
        tmp_d.tableModelDict = {v.id: v.modelName for k, v in self.rootDataNode.dataTable.militaryTable.idDict.items()}
        tmp_d.modelPrefix = 'military'
        tmp_d.newUnitFunc = self.rootDataNode.make_military
        tmp_d.newUnitKwargs = {'flag': 0}
        self.dynLayerStorage.add(tmp_d)
        # endregion

        # layer
        for k, v in self.terrainLayerStorage.idDict.items():
            v.entity = TerrainLayerEntityBase(
                self.config, self.assetPackage, self.joinedLayerRender, v.dataTable, v.modelPrefix, v.terrainMap,
                layer=v.layer
            )
            self.add_child(v.entity)

        self.joinedLayerRender.refresh_surface()

        for k, v in self.dynLayerStorage.idDict.items():
            v.entity = GridDynLayerEntityBase(
                self.worldScene, self.assetPackage, self.config, v.layer, v.unitDict.idDict,
                v.zIndex, v.tableModelDict)
            self.add_child(v.entity)

    def init_register(self):
        SceneManager()[self.config.SYSTEM_KEY] = self.worldScene
        SceneManager().switch_scene(self.config.SYSTEM_KEY)
        RootEntityManager()[self.config.SYSTEM_KEY] = self
        RootEntityManager().switch_root_entity(self.config.SYSTEM_KEY)

    @staticmethod
    def make_map(config: Config):
        """
        不要直接调用
        :param config:
        :return:
        """
        DataTableLoader.table_storage_path = config.TABLE_STORAGE_PATH
        data_table = DataTableLoader.load_data(*config.DATA_TABLE_ID, AdvwDataTable())
        data_node = AdvwDataNode.make_data(config.defaultInitMapSize, data_table, 100)
        data_node.config = config
        return data_node

    @staticmethod
    def load_map(config: Config):
        if not os.path.exists(os.path.join(config.MAP_STORAGE_PATH, config.mapName)):
            data_node = MapEditRootEntity.make_map(config)
            with open(os.path.join(config.MAP_STORAGE_PATH, config.mapName), 'wb') as f:
                pickle.dump(data_node, f)

        with open(os.path.join(config.MAP_STORAGE_PATH, config.mapName), 'rb') as f:
            data_node = pickle.load(f)

        return data_node

    def handle_layer_visible(self, layer_name):
        pass

    def handle_modify_terrain(self, area, layer_name, v: str):
        pass


# ui element


class MapEditUI(UserInterfaceBase):
    def __init__(self, layer_data, maps=None):
        super().__init__()
        self.maps = maps if maps is not None else []
        self.layerItemData: Dict[str, list] = layer_data

        self.layerButton: elements.UIDropDownMenu | None = None
        self.layerItemButton: elements.UIDropDownMenu | None = None
        self.visibleListView: elements.UISelectionList | None = None
        self.mapListView: elements.UIDropDownMenu | None = None

        self.mouseLocaPanel: elements.UIPanel | None = None
        self.mouseLocLabel: elements.UILabel | None = None

        self.handleVisibleChange = None

    def show(self):
        self.layerButton.show()
        self.layerItemButton.show()
        self.visibleListView.show()

    def hide(self):
        if self.layerButton is None:
            return
        self.layerButton.hide()
        self.layerItemButton.hide()
        self.visibleListView.hide()

    def resize(self, suf, ui_manager):
        self.kill()
        current_type = list(self.layerItemData.keys())[0]
        current_items = self.layerItemData[current_type]
        if not current_items:
            current_items = ['']
        self.visibleListView = elements.UISelectionList(
            pygame.Rect(0, 0, 150, 100), list(self.layerItemData.keys()), ui_manager
        )
        self.layerButton = elements.UIDropDownMenu(
            list(self.layerItemData.keys()), current_type, pygame.Rect(300, 0, 100, 30), ui_manager
        )
        self.layerItemButton = elements.UIDropDownMenu(
            current_items, current_items[0], pygame.Rect(400, 0, 150, 30),
            ui_manager
        )
        self.mapListView = elements.UIDropDownMenu(
            self.maps+[''], '', pygame.Rect(600, 0, 100, 30), ui_manager
        )
        rect = pygame.Rect(0, 0, 100, 30)
        rect.bottom = 0
        rect.left = 0
        self.mouseLocaPanel = elements.UIPanel(rect, manager=ui_manager, anchors={'left': 'left', 'bottom': 'bottom'})
        self.mouseLocLabel = elements.UILabel(pygame.Rect(0, 0, 100, 30), '0 0', ui_manager,
                                              container=self.mouseLocaPanel, anchors={'center': 'center'})

    def event(self, e0):
        if e0.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if e0.ui_element == self.visibleListView:
                if self.handleVisibleChange is not None:
                    self.handleVisibleChange(e0.text)
        elif e0.type == pygame.KEYDOWN and e0.key == pygame.K_TAB:
            if self.layerButton.visible:
                self.hide()
            else:
                self.show()
        elif e0.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if e0.ui_element == self.layerButton:
                old_btn = self.layerItemButton
                current_items = self.layerItemData[self.layerButton.selected_option]
                if not current_items:
                    current_items = ['']

                self.layerItemButton = elements.UIDropDownMenu(
                    current_items, current_items[0], old_btn.relative_rect, old_btn.ui_manager
                )
                old_btn.kill()


# ui state


class MapEditUIStateBase(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: MapEditUIStateMngr = mngr


class MapEditUIStateMngr(UIStateManagerBase[MapEditUIStateBase]):
    STATE_HOME = 0x1

    def __init__(self, root_entity):
        super().__init__()
        self.rootEntity: MapEditRootEntity = root_entity

        self.homePolityUS = HomePolityUS(self)

        self[self.STATE_HOME] = self.homePolityUS

        self.currentUIState = self[self.STATE_HOME]

    def init_data(self):
        self.rootEntity.init_load_asset()
        self.rootEntity.init_map()
        self.rootEntity.init_register()

    def active(self):
        if self.rootEntity.assetPackage is None:
            self.init_data()

        super().active()


class HomePolityUS(MapEditUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.homeUI: MapEditUI | None = None

        self.layerItemData = {}

        self.lastModeIndex = 0

    def active(self):
        for k, v in self.mngr.rootEntity.terrainLayerStorage.idDict.items():
            self.layerItemData[v.name] = list(v.dataTable.nameDict.keys())
        for k, v in self.mngr.rootEntity.dynLayerStorage.idDict.items():
            self.layerItemData[v.name] = list(v.dataTable.nameDict.keys())

        self.homeUI = MapEditUI(self.layerItemData)
        UserInterfaceManager().switch_user_interface(self.homeUI)
        self.homeUI.handleVisibleChange = self.handle_layer_visible

    def inactive(self):
        self.homeUI.kill()
        self.homeUI = None

    def handle_layer_visible(self, layer_name):
        if layer_name in self.mngr.rootEntity.dynLayerStorage:
            v = self.mngr.rootEntity.dynLayerStorage[layer_name]
            rl = v.entity
        else:
            return

        if rl.isHidden:
            rl.show_render()
        else:
            rl.hide_render()

    def handle_load_map(self, map_name):
        pass

    def event(self, e0):
        if e0.type == pygame.MOUSEMOTION:
            mouse_grid = self.mngr.rootEntity.worldScene.get_mouse_grid_loc()
            self.homeUI.mouseLocLabel.set_text(f'{mouse_grid[0]} {mouse_grid[1]}', text_kwargs={'color': 'red'})

        elif e0.type == pygame.MOUSEBUTTONUP:
            mouse_grid = self.mngr.rootEntity.worldScene.get_mouse_grid_loc()
            self.homeUI.mouseLocLabel.set_text(f'{mouse_grid[0]} {mouse_grid[1]}')
            if self.homeUI.layerButton.visible or abs(e0.button-2) != 1:
                return
            dn = self.mngr.rootEntity.rootDataNode
            circle_area = self.mngr.rootEntity.worldScene.get_current_legal_circle_grid_area(
                dn.map_size)

            t_name = self.homeUI.layerButton.selected_option
            v_name = self.homeUI.layerItemButton.selected_option
            if t_name == '':
                return
            if t_name in self.mngr.rootEntity.terrainLayerStorage:
                v2 = self.mngr.rootEntity.terrainLayerStorage[t_name]
                if e0.button == 3:
                    v = 0
                else:
                    v = v2.dataTable[v_name].id
                    # v = dn.dataTable.terrainTable[v_name].id
                for x in range(circle_area[0], circle_area[2]+1):
                    for y in range(circle_area[1], circle_area[3]+1):
                        v2.terrainMap[y, x] = v
                        v2.entity.refresh_node((x, y), v)

            elif t_name in self.mngr.rootEntity.dynLayerStorage:
                v2 = self.mngr.rootEntity.dynLayerStorage[t_name]
                if e0.button == 3:
                    v = 0
                else:
                    v = v2.dataTable[v_name].id
                for x in range(circle_area[0], circle_area[2] + 1):
                    for y in range(circle_area[1], circle_area[3] + 1):
                        tmp_d = v2.unitDict[(x, y)]
                        if v == 0:
                            if tmp_d is None:
                                continue
                            else:
                                del v2.unitDict[(x, y)]
                        else:
                            if tmp_d is not None:
                                del v2.unitDict[(x, y)]
                                v2.entity.refresh_node(tmp_d.id)
                            tmp_d = v2.newUnitFunc(loc=(x, y), table_id=v, **v2.newUnitKwargs)

                        v2.entity.refresh_node(tmp_d.id)

        elif e0.type == pygame.KEYDOWN and e0.key == pygame.K_s and e0.mod & pygame.KMOD_CTRL:
            with open(os.path.join(self.mngr.rootEntity.config.MAP_STORAGE_PATH, self.mngr.rootEntity.config.mapName),
                      'wb') as f:  # 打开文件
                pickle.dump(self.mngr.rootEntity.rootDataNode, f)


# 重写: ConfigBase, MapEditRootEntity (load_map, make_map, init_map)


if __name__ == '__main__':
    __config = Config()

    # from qins_moon.core.utils.data_table_loader import DataTableLoader, DataTableMaker
    # DataTableMaker.make_table(AdvwDataTable(),
    # os.path.join(r'E:\workspace\game_lab\qins_moon\res\tables\test\advw\advw.xlsx'))
    # exit()
    __director = Director()
    __dn = MapEditRootEntity.load_map(__config)
    __config: Config = __dn.config
    __director.init(
        __config.SYSTEM_KEY,
        MapEditUIStateMngr(
            MapEditRootEntity(__config, __dn)
        )
    )
    __director.run()
