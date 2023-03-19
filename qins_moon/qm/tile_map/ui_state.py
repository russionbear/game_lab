#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: ui_state.py
# @time: 3/13/2023 5:00 PM
from typing import Any, Type

import pygame

from qins_moon.core.director import IUIStateInterface, UIStateManagerBase, Director
from qins_moon.core.ui_element import UserInterfaceManager
from qins_moon.qm.tile_map.entity import TileMapRootEntity
from qins_moon.qm.tile_map.ui_element import TileMapEditUI, TileMapCmdSpectatorUI


class TileMapUIStateBase(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: TileMapUIStateMngr = mngr


class TileMapUIStateMngr(UIStateManagerBase[TileMapUIStateBase]):

    def __init__(self, root_entity):
        super().__init__()
        self.rootEntity: TileMapRootEntity = root_entity

    def init_data(self):
        self.rootEntity.load_asset()
        self.rootEntity.load_map()
        self.rootEntity.init_map()
        self.rootEntity.register_map()

    def active(self):
        if self.rootEntity.assetPackage is None:
            self.init_data()

        super().active()


class TileMapEditUS(TileMapUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.homeUI: TileMapEditUI | None = None

        self.layerItemData = {}

        self.lastModeIndex = 0

    def active(self):
        for k, v in self.mngr.rootEntity.terrainLayer.terrainLayerStorage.idDict.items():
            self.layerItemData[v.name] = list(v.dataTable.nameDict.keys())
        for k, v in self.mngr.rootEntity.unitLayer.unitLayerStorage.idDict.items():
            self.layerItemData[v.name] = list(v.dataTable.nameDict.keys())

        self.homeUI = TileMapEditUI(self.layerItemData)
        UserInterfaceManager().switch_user_interface(self.homeUI)
        self.homeUI.handleVisibleChange = self.handle_layer_visible

    def inactive(self):
        if self.homeUI:
            self.homeUI.kill()
            self.homeUI = None
        UserInterfaceManager().switch_user_interface(None)

    def handle_layer_visible(self, layer_name):
        if layer_name in self.mngr.rootEntity.unitLayer.unitLayerStorage:
            v = self.mngr.rootEntity.unitLayer.unitLayerStorage[layer_name]
            rl = v.entity
        else:
            return

        if rl.isHidden:
            rl.show_render()
        else:
            rl.hide_render()

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
                dn.map_size())

            t_name = self.homeUI.layerButton.selected_option
            v_name = self.homeUI.layerItemButton.selected_option
            if t_name == '':
                return
            if t_name in self.mngr.rootEntity.terrainLayer.terrainLayerStorage:
                v2 = self.mngr.rootEntity.terrainLayer.terrainLayerStorage[t_name]
                if e0.button == 3:
                    v = 0
                else:
                    v = v2.dataTable[v_name].id
                    # v = dn.dataTable.terrainTable[v_name].id
                for x in range(circle_area[0], circle_area[2]+1):
                    for y in range(circle_area[1], circle_area[3]+1):
                        v2.terrainMap[y, x] = v
                        v2.entity.refresh_node((x, y), v)

            elif t_name in self.mngr.rootEntity.unitLayer.unitLayerStorage:
                v2 = self.mngr.rootEntity.unitLayer.unitLayerStorage[t_name]
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

                            tmp_d = self.handle_make_unit((x, y), v)
                            if tmp_d is None:
                                continue
                            # tmp_d = v2.newUnitFunc(loc=(x, y), table_id=v, **v2.newUnitKwargs)

                        v2.entity.refresh_node(tmp_d.id)

        elif e0.type == pygame.KEYDOWN and e0.key == pygame.K_s and e0.mod & pygame.KMOD_CTRL:
            self.mngr.rootEntity.save_map()

    # overwrite
    def handle_make_unit(self, loc, v) -> Any:
        pass


class TileMapCmdSpectatorUS(TileMapUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.cmdSpectatorUI: TileMapCmdSpectatorUI | None = None

    def active(self):
        self.cmdSpectatorUI = TileMapCmdSpectatorUI()
        UserInterfaceManager().switch_user_interface(self.cmdSpectatorUI)
        self.cmdSpectatorUI.handleInput = self.handle_input
        # self.cmdSpectatorUI.infoBox.get_focus_set()

    def inactive(self):
        if self.cmdSpectatorUI:
            self.cmdSpectatorUI.kill()
            self.cmdSpectatorUI = None
        UserInterfaceManager().switch_user_interface(None)

    def handle_input(self, text):
        pass

    def event(self, e0):
        if e0.type == pygame.MOUSEMOTION:
            if self.cmdSpectatorUI.infoBox.get_relative_rect().collidepoint(e0.pos):
                self.mngr.rootEntity.worldScene.camera.canScroll = False
            else:
                self.mngr.rootEntity.worldScene.camera.canScroll = True


def run_tile_map(config, entity_type: Type[TileMapRootEntity], us_mngr_type: Type[TileMapUIStateMngr]):
    director = Director()
    root_entity = entity_type(config)
    director.init(
        config.SYSTEM_KEY,
        us_mngr_type(root_entity)
    )
    director.run()
