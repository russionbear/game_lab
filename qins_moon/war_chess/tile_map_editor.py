#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :tile_map_editor.py
# @Time      :20/02/2023
# @Author    :russionbear
# @Function  :function

"""
# home: file, layer
# map new、save、close、
# no undo
# layer new(type layerName, sheetName zindex), close, choose
"""
from typing import Dict, List, Any

import numpy
import pygame.draw
import pygame_gui
from pygame_gui import elements

from qins_moon.core.asset import AssetManager, ConfigBase, SpriteAsset, AssetPackage
from qins_moon.core.director import Director, IUIStateInterface, UIStateManagerBase, EntityBase, RootEntityBase
from qins_moon.core.render.render import RenderBase, SceneBase, SceneManager, SceneCircleBase
from qins_moon.core.render.component import AnimeRenderComponent, InfoRenderComponent, JoinedSurfaceRenderComponent, \
    JoinedSurfaceRuleBase
from qins_moon.core.ui_element import UserInterfaceBase, UserInterfaceManager
from qins_moon.core.utils.data_table_loader import DataTableLoader
from qins_moon.core_demo.data_table import Cv6DataTable


SYSTEM_KEY = 'tileMapEditor'
ASSET_PACKAGE_ID = ('test', 'core', 'politics')
TABLE_ID = 'test', 'core', 'politics'
MAP_NAME = "test"

TEST_MODE = 'building.bridge'


# data struction


class TileMapLayerData:
    TYPE_GRID_BASE = 0x1
    TYPE_GRID_TERRAIN = 0x2
    TYPE_GRID_SPRITE = 0x3
    TYPE_COLLIDE = 0x4

    def __init__(self):
        self.layerName = ""
        self.sheetName = ''
        self.zindex = 0
        self.type = TileMapLayerData.TYPE_GRID_BASE
        self.data: numpy.ndarray | Dict[tuple, int] | None = None


class TileMapObj:
    def __init__(self):
        self.mapSize = 0, 0
        self.dataTableId = "", "", ""
        self.assetPackageId = None
        self.layerData: List[TileMapLayerData] = []


# scene


class TileMapEditScene(SceneBase):
    def __init__(self):
        super().__init__()
        self.surface = pygame.Surface((800, 600)).convert_alpha()
        self.camera.handle_resize()
        self.circle = SceneCircleBase(self)

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def event(self, e0: pygame.event.Event):
        super().event(e0)
        self.circle.event(e0)

    def draw(self):
        super().draw()
        self.circle.draw()


# entity


class EmptySprite(EntityBase):
    def __init__(self, scene, model_name, asset):
        super().__init__()
        self.animation = AnimeRenderComponent(model_name, asset)
        self.animation.set_scene(scene)


class TileMapLayerEntity(EntityBase):
    def __init__(self, config, layer_data, pkg):
        super().__init__()
        self.config: ConfigBase = config
        self.assetPackage: AssetPackage = pkg
        self.worldScene: SceneBase = SceneManager()[SYSTEM_KEY]

        self.layerData: TileMapLayerData = layer_data
        self.joinedRender: JoinedSurfaceRenderComponent | None = None
        self.spriteDict: Dict[tuple, EmptySprite] = {}
        if self.layerData.type in [TileMapLayerData.TYPE_GRID_BASE, TileMapLayerData.TYPE_GRID_TERRAIN]:
            joined_suf_rule_dict = {}
            for i1, i in [(1, 'terrain.plain-desert'), (2, 'terrain.mountain-desert')]:
                tmp_d = JoinedSurfaceRuleBase()
                joined_suf_rule_dict[i1] = tmp_d
                tmp_d.id = i1
                tmp_d.rules = [({}, pkg.get_sprite(i))]
            self.joinedRender = JoinedSurfaceRenderComponent(config, joined_suf_rule_dict, self.layerData.data)
            self.joinedRender.set_scene(self.worldScene)
        elif self.layerData.type == TileMapLayerData.TYPE_GRID_SPRITE:
            for k, v in self.layerData.data.items():
                tmp_e = EmptySprite(self.worldScene,)


class TileMapEditRootEntity(RootEntityBase):
    pass


# ui


class HomeUI(UserInterfaceBase):
    def __init__(self):
        self.fileButton: elements.UIButton | None = None
        self.layerButton: elements.UIButton | None = None
        self.handleToProject = None
        self.handleToLayerButton = None

    def resize(self, suf, ui_manager):
        self.kill()
        self.fileButton = elements.UIButton(pygame.Rect(0, 0, 100, 30), 'project', ui_manager)
        self.layerButton = elements.UIButton(pygame.Rect(100, 0, 100, 30), 'layer', ui_manager)

    def kill(self):
        if self.fileButton:
            self.fileButton.kill()
        if self.layerButton:
            self.layerButton.kill()

    def show(self):
        if not self.fileButton:
            return
        self.fileButton.show()
        self.layerButton.show()

    def hide(self):
        self.layerButton.hide()
        self.fileButton.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.fileButton:
                if self.handleToProject is not None:
                    self.handleToProject()
            elif e0.ui_element == self.layerButton:
                if self.handleToLayerButton is not None:
                    self.handleToLayerButton()


class ProjectUI(UserInterfaceBase):
    def __init__(self):
        self.panel: elements.UIPanel | None = None
        self.nameInput: elements.UITextEntryLine | None = None
        self.pkgButton: elements.UIDropDownMenu | None = None
        self.tableButton: elements.UIDropDownMenu | None = None

        self.sizeXButton: elements.UIDropDownMenu | None = None
        self.sizeYButton: elements.UIDropDownMenu | None = None
        self.newButton: elements.UIButton | None = None

        self.backButton: elements.UIButton | None = None

        self.handleBack = None
        self.handleNew = None

    def resize(self, suf, ui_manager):
        if self.panel:
            self.kill()
        self.panel = elements.UIPanel(pygame.Rect(0, 0, 400, 300), manager=ui_manager, anchors={'center': "center"})
        tmp_rect = pygame.Rect(0, 0, 100, 30)
        tmp_rect.bottom = -30
        self.backButton = elements.UIButton(
            tmp_rect, 'back', ui_manager, container=self.panel, anchors={'centerx': 'centerx', 'bottom': 'bottom'})

        self.nameInput = elements.UITextEntryLine(
            pygame.Rect(0, 0, 200, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.pkgButton = elements.UIDropDownMenu(
            [''], '', pygame.Rect(0, 40, 200, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.tableButton = elements.UIDropDownMenu(
            [''], '', pygame.Rect(0, 80, 200, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.sizeXButton = elements.UIDropDownMenu(
            [str(2**i) for i in range(4, 14)], str(2**4), pygame.Rect(-50, 120, 100, 30), ui_manager,
            container=self.panel, anchors={'centerx': 'centerx'}
        )
        self.sizeYButton = elements.UIDropDownMenu(
            [str(2**i) for i in range(4, 14)], str(2**4), pygame.Rect(50, 120, 100, 30), ui_manager,
            container=self.panel, anchors={'centerx': 'centerx'}
        )
        self.newButton = elements.UIButton(
            pygame.Rect(0, 160, 100, 30), 'new', ui_manager, container=self.panel, anchors={'centerx': 'centerx'})

    def show(self):
        if not self.panel:
            return
        self.panel.show()

    def hide(self):
        self.panel.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.backButton:
                if self.handleBack is not None:
                    self.handleBack()
            elif e0.ui_element == self.handleNew:
                if self.handleNew is not None:
                    self.handleNew()


class LayerUI(UserInterfaceBase):
    def __init__(self):
        self.panel: elements.UIWindow | None = None
        self.spriteListView: elements.UISelectionList | None = None

        self.layerView: elements.UISelectionList | None = None
        self.layerNameInput: elements.UITextEntryLine | None = None
        self.layerSheetNameBtn: elements.UIDropDownMenu | None = None
        self.typeButton: elements.UIDropDownMenu | None = None
        self.zindexInput: elements.UITextEntryLine | None = None
        self.newButton: elements.UIButton | None = None

        self.deleteButton: elements.UIButton | None = None

        self.handleBack = None
        self.handleDelete = None
        self.handleNew = None
        self.handleLayerChose = None
        self.handleSpriteChose = None
        self.handleMouseIn = None
        self.handleMouseOut = None

    def resize(self, suf, ui_manager):
        if self.panel:
            self.kill()
        width = 220
        offset_y = 0
        self.panel = elements.UIWindow(pygame.Rect(10, 10, width, 500), manager=ui_manager)
        self.panel.on_close_window_button_pressed = self.handle_close
        self.layerView = elements.UISelectionList(
            pygame.Rect(offset_y, 0, width-10, 190), [], ui_manager, container=self.panel,
            anchors={'centerx': 'centerx'}
        )
        offset_y += 200
        self.layerSheetNameBtn = elements.UIDropDownMenu(
            [''], '', pygame.Rect(-60, offset_y, 60, 30), ui_manager, container=self.panel,
            anchors={'centerx': 'centerx'})
        self.zindexInput = elements.UITextEntryLine(
            pygame.Rect(0, offset_y, 60, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.typeButton = elements.UIDropDownMenu(
            [''], '', pygame.Rect(60, offset_y, 60, 30), ui_manager, container=self.panel,
            anchors={'centerx': 'centerx'})

        offset_y += 30
        self.layerNameInput = elements.UITextEntryLine(
            pygame.Rect(-60, offset_y, 60, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.newButton = elements.UIButton(
            pygame.Rect(0, offset_y, 60, 30), 'new', ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.deleteButton = elements.UIButton(
            pygame.Rect(60, offset_y, 60, 30), 'delete', ui_manager, container=self.panel,
            anchors={'centerx': 'centerx'})

        offset_y += 30
        self.spriteListView = elements.UISelectionList(
            pygame.Rect(0, offset_y, width, 190), [], ui_manager, container=self.panel, anchors={'centerx': 'centerx'}
        )

    def show(self):
        if not self.panel:
            return
        self.panel.show()

    def hide(self):
        self.panel.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            # print(e0)
            if self.panel.is_focused:
                if self.handleMouseIn:
                    self.handleMouseIn()
            else:
                if self.handleMouseOut:
                    self.handleMouseOut()

            if e0.ui_element == self.deleteButton:
                if self.handleDelete is not None:
                    self.handleDelete()
            elif e0.ui_element == self.newButton:
                if self.handleNew is not None:
                    self.handleNew()
            # elif e0.ui_element == self.panel.close_window_button:
            #     if self.handleBack is not None:
            #         self.handleBack()
        elif e0.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if e0.ui_element == self.layerView:
                if self.handleLayerChose is not None:
                    self.handleLayerChose(e0.text)
            elif e0.ui_element == self.spriteListView:
                if self.handleSpriteChose is not None:
                    self.handleSpriteChose(e0.text)

    def handle_close(self):
        if self.handleBack is not None:
            self.handleBack()
        self.panel.hide()


# about ui_state


class TileMapEditUIStateMngr(UIStateManagerBase[IUIStateInterface]):
    UI_HOME = 0x11
    UI_PRJ = 0x12
    UI_LAYER = 0x13

    UI_STATE_HOME = 0x1
    UI_STATE_PRJ = 0x2

    def __init__(self):
        super().__init__()
        self.uiStorage = {
            TileMapEditUIStateMngr.UI_HOME: HomeUI(),
            TileMapEditUIStateMngr.UI_PRJ: ProjectUI(),
            TileMapEditUIStateMngr.UI_LAYER: LayerUI()
        }

        self[self.UI_STATE_HOME] = HomeUIState(self)
        self[self.UI_STATE_PRJ] = ProjectUIState(self)
        self.currentUIState = self[self.UI_STATE_HOME]

        # self.worldScene = TileMapEditScene()
        # SceneManager()[SYSTEM_KEY] = self.worldScene

    def switch_ui(self, key):
        mngr = UserInterfaceManager()
        if mngr.currentUI is not None:
            mngr.currentUI.hide()
        new_ui = self.uiStorage.get(key, None)
        if new_ui is not None:
            new_ui.show()
        mngr.switch_user_interface(new_ui)


class HomeUIState(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: TileMapEditUIStateMngr = mngr
        self.mngr.uiStorage[TileMapEditUIStateMngr.UI_HOME].handleToLayerButton = self.handle_show_sub_win
        self.mngr.uiStorage[TileMapEditUIStateMngr.UI_HOME].handleToProject = self.handle_to_project
        tmp_ui = self.mngr.uiStorage[TileMapEditUIStateMngr.UI_LAYER]
        tmp_ui.handleBack = self.handle_hide_sub_win
        tmp_ui.handleNew = self.handle_new_layer
        tmp_ui.handleDelete = self.handle_delete_layer
        tmp_ui.handleLayerChose = self.handle_layer_chose
        tmp_ui.handleSpriteChose = self.handle_sprite_chose
        tmp_ui.handleMouseIn = self.handle_mouse_in_layer
        tmp_ui.handleMouseOut = self.handle_mouse_out_layer

    def active(self):
        self.mngr.switch_ui(TileMapEditUIStateMngr.UI_HOME)

    def handle_to_project(self):
        self.mngr.switch_ui_state(TileMapEditUIStateMngr.UI_STATE_PRJ)

    def handle_show_sub_win(self):
        self.mngr.switch_ui(TileMapEditUIStateMngr.UI_LAYER)

    def handle_hide_sub_win(self):
        self.mngr.switch_ui(TileMapEditUIStateMngr.UI_HOME)

    def handle_delete_layer(self):
        pass

    def handle_new_layer(self):
        pass

    def handle_layer_chose(self, v):
        pass

    def handle_sprite_chose(self, v):
        pass

    def handle_mouse_in_layer(self):
        SceneManager()[SYSTEM_KEY].camera.canScroll = False
        # self.mngr.worldScene.camera.canScroll = False

    def handle_mouse_out_layer(self):
        SceneManager()[SYSTEM_KEY].camera.canScroll = True
        # self.mngr.worldScene.camera.canScroll = True


class ProjectUIState(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: TileMapEditUIStateMngr = mngr
        self.mngr.uiStorage[TileMapEditUIStateMngr.UI_PRJ].handleNew = self.handle_new
        self.mngr.uiStorage[TileMapEditUIStateMngr.UI_PRJ].handleBack = self.handle_back

    def active(self):
        self.mngr.switch_ui(TileMapEditUIStateMngr.UI_PRJ)

    def handle_back(self):
        print('back')
        self.mngr.switch_ui_state(TileMapEditUIStateMngr.UI_STATE_HOME)

    def handle_new(self):
        pass


def joined_surface_render_component():
    __director = Director()
    __director.init('test', TileMapEditUIStateMngr())

    # 加载资源包
    am = AssetManager()
    config = ConfigBase()
    am.init(config)
    pkg = am.load_resource(ASSET_PACKAGE_ID)

    # # 加载数据表
    # config = ConfigBase()
    # DataTableLoader.table_storage_path = config.TABLE_STORAGE_PATH
    # DataTableLoader.load_data(*TEST_TABLE_ID, Cv6DataTable())

    # joined_surface
    terrain_map = numpy.ones((16, 16), dtype=numpy.int_)
    joined_suf_rule = JoinedSurfaceRuleBase()
    joined_suf_rule.rules = [({}, pkg.get_sprite(TEST_MODE))]
    joined_suf_rule.id = 1
    joined_suf = JoinedSurfaceRenderComponent(config, {1: joined_suf_rule}, terrain_map, interval=1.2, layer_nu=2)

    # 创建场景并添加render
    __scene = TileMapEditScene()
    SceneManager()[SYSTEM_KEY] = __scene
    SceneManager().switch_scene(SYSTEM_KEY)
    joined_suf.set_scene(__scene)

    __director.run()


if __name__ == '__main__':
    # easy_render()
    # info_and_anime_render_component()
    joined_surface_render_component()
    pass
