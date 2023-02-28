#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :asset_editor.py
# @Time      :16/02/2023
# @Author    :russionbear
# @Function  :function

"""function
type.name.action
- 独立启动

edit: static tile, dynamic tile, sprite
1. load static tile asset from one image to type
2. export sprites/type to one image
3. load gif to action

1. make, list, delete type
2. make, list, delete name
3. set name type [static, dynamic, action]
4. make, list, delete, preview action

1. set action params global
2. set image size in worldScene, nav size(必须是连续 x*y 的区域), collide points
3. set interval
4. set per action filter
"""
import os.path

import pygame
import yaml

from qins_moon.core.asset import AssetManager, ConfigBase, AssetPackage
from qins_moon.core.director import Director, UIStateManagerBase, IUIStateInterface, RootEntityBase, RootEntityManager
from qins_moon.core.render.render import SceneManager, SceneBase
from qins_moon.core.ui_element import UserInterfaceBase, UserInterfaceManager, UIMenuBar
import pygame_gui
from pygame_gui import elements


EDITOR_ENV_ID = 'asset_editor'
CACHE_FILE_PATH = r'E:\workspace\game_lab\cache\asset_editor.yml'


# ui


class AssetEditorUI(UserInterfaceBase):
    def __init__(self):
        self.uiManager = None

        self.chooseFileDialog: pygame_gui.windows.UIFileDialog | None = None
        self.confirmDialog: pygame_gui.windows.UIConfirmationDialog | None = None

        # region ui elements
        self.loadButton: elements.UIDropDownMenu | None = None

        self.typeListBtn: elements.UIButton | None = None
        self.typeListView: elements.UISelectionList | None = None
        self.typeOperaBtn: elements.UIDropDownMenu | None = None

        self.nameListBtn: elements.UIButton | None = None
        self.nameListView: elements.UISelectionList | None = None
        self.nameOperaBtn: elements.UIDropDownMenu | None = None

        self.nameTypeBtn: elements.UIDropDownMenu | None = None

        self.actionListBtn: elements.UIButton | None = None
        self.actionListView: elements.UISelectionList | None = None
        self.actionOperaBtn: elements.UIDropDownMenu | None = None

        self.lazyButton: elements.UIDropDownMenu | None = None

        self.intervalInput: elements.UITextEntryLine | None = None
        self.playStopButton: elements.UIButton | None = None
        self.actionRegex: elements.UITextEntryLine | None = None

        self.legalSizeXInput: elements.UITextEntryLine | None = None
        self.legalSizeYInput: elements.UITextEntryLine | None = None

        self.anchorXInput: elements.UITextEntryLine | None = None
        self.anchorYInput: elements.UITextEntryLine | None = None

        self.showNavAreaBtn: elements.UIButton | None = None

        self.showCollideAreaBtn: elements.UIButton | None = None
        self.collideType: elements.UIDropDownMenu | None = None
        self.collideCircleRadiusInput: elements.UITextEntryLine | None = None
        self.collidePointClearBtn: elements.UIButton | None = None
        self.collidePointOkBtn: elements.UIButton | None = None

        self.infoLabel: elements.UILabel | None = None
        # endregion

        # region event handle
        self._handlePathPicked = None

        self.handleRefresh = None

        self.handleResourceLoad = None
        self.handleTypeModify = None
        self.handleNameModify = None
        self.handleActionModify = None

        self.handleDeleteType = None
        self.handleDeleteName = None
        self.handleDeleteAction = None

        self.handleParamToResource = None
        self.handleParamToType = None
        self.handleParamToName = None

        self.handlePlayStop = None
        self.handleShowCollide = None
        self.handleShowNav = None
        self.handleCollideClear = None
        self.handleCollideOk = None

        self.handleIntervalChange = None
        self.handleLegalSizeXChange = None
        self.handleLegalSizeYChange = None
        self.handleAnchorXChange = None
        self.handleAnchorYChange = None
        self.handleCollideRadiusChange = None

        self.handleActionRegexChange = None

        # self.handle

        # data
        # self.currentResourceId = None
        # self.currentTypeData = []
        # self.currentType = None
        # self.currentNameData = []
        # self.currentName = None
        # self.currentActionData = []
        # self.currentAction = None

        # endregion

    def resize(self, suf, ui_manager):
        ui_manager.set_locale('zh')
        self.uiManager = ui_manager

        # region top
        offset_x = 0
        self.loadButton = elements.UIDropDownMenu(
            ['resource', 'load', 'refresh'], 'resource', pygame.Rect(offset_x, 0, 100, 30), ui_manager)
        # self.loadButton = UIMenuBar(('title', ['111', '222']), pygame.Rect(0, 0, 100, 30), ui_manager)

        offset_x += 100
        self.typeListBtn = elements.UIButton(
            pygame.Rect(offset_x, 0, 100, 30), "type", ui_manager)
        self.typeListView = elements.UISelectionList(
            pygame.Rect(offset_x, 30, 150, 500), [], ui_manager, allow_double_clicks=True)
        self.typeListView.hide()
        self.typeOperaBtn = elements.UIDropDownMenu(
            ['opera', 'new', 'delete'], 'opera', pygame.Rect(offset_x+100, 0, 70, 30), ui_manager)

        offset_x += 200
        self.nameListBtn = elements.UIButton(
            pygame.Rect(offset_x, 0, 100, 30), "name", ui_manager)
        self.nameListView = elements.UISelectionList(
            pygame.Rect(offset_x, 30, 150, 500), [], ui_manager, allow_double_clicks=True)
        self.nameListView.hide()
        self.nameOperaBtn = elements.UIDropDownMenu(
            ['opera', 'new', 'delete'], 'opera', pygame.Rect(offset_x+100, 0, 70, 30), ui_manager)

        offset_x += 170
        self.nameTypeBtn = elements.UIDropDownMenu(
            ['static', 'dynamic', 'sprite'], 'static', pygame.Rect(offset_x, 0, 70, 30)
        )

        offset_x += 100
        self.actionListBtn = elements.UIButton(
            pygame.Rect(offset_x, 0, 100, 30), "action", ui_manager)
        self.actionListView = elements.UISelectionList(
            pygame.Rect(offset_x, 30, 150, 500), [], ui_manager, allow_double_clicks=True)
        self.actionListView.hide()
        self.actionOperaBtn = elements.UIDropDownMenu(
            ['opera', 'new', 'delete'], 'opera', pygame.Rect(offset_x+100, 0, 70, 30), ui_manager)

        offset_x += 200
        self.lazyButton = elements.UIDropDownMenu(
            ['layer', 'to resource', 'to type', 'to name'], 'layer', pygame.Rect(offset_x, 0, 70, 30), ui_manager
        )
        # endregion

        # left mid
        self.playStopButton = elements.UIButton(
            pygame.Rect(0, 300, 100, 30), 'play/stop', ui_manager
        )
        self.intervalInput = elements.UITextEntryLine(
            pygame.Rect(0, 330, 100, 30), ui_manager, initial_text='0.8'
        )
        self.actionRegex = elements.UITextEntryLine(
            pygame.Rect(0, 360, 100, 30), ui_manager, initial_text='.*'
        )

        # region right
        offset_y = 50  # ############# legalSize
        tmp_rect = pygame.Rect(0, offset_y, 100, 30)
        tmp_rect.right = -100
        tmp_label = elements.UILabel(
            tmp_rect, 'legalSize', ui_manager, anchors={'right': 'right'}
        )
        tmp_rect = pygame.Rect(0, offset_y, 50, 30)
        tmp_rect.right = -50
        self.legalSizeXInput = elements.UITextEntryLine(
            tmp_rect, ui_manager, initial_text='1', anchors={'right': 'right'}
        )
        tmp_rect = pygame.Rect(0, offset_y, 50, 30)
        tmp_rect.right = 0
        self.legalSizeYInput = elements.UITextEntryLine(
            tmp_rect, ui_manager, initial_text='1', anchors={'right': 'right'}
        )

        offset_y += 40  # ############# anchor
        tmp_rect = pygame.Rect(0, offset_y, 100, 30)
        tmp_rect.right = -100
        tmp_label = elements.UILabel(
            tmp_rect, 'anchor', ui_manager, anchors={'right': 'right'}
        )
        tmp_rect = pygame.Rect(0, offset_y, 50, 30)
        tmp_rect.right = -50
        self.anchorXInput = elements.UITextEntryLine(
            tmp_rect, ui_manager, initial_text='1', anchors={'right': 'right'}
        )
        tmp_rect = pygame.Rect(0, offset_y, 50, 30)
        tmp_rect.right = 0
        self.anchorYInput = elements.UITextEntryLine(
            tmp_rect, ui_manager, initial_text='1', anchors={'right': 'right'}
        )

        offset_y += 40  # ############# show
        tmp_rect = pygame.Rect(0, offset_y, 100, 30)
        tmp_rect.right = 0
        self.showNavAreaBtn = elements.UIButton(
            tmp_rect, 'show nav', ui_manager, anchors={'right': 'right'}
        )
        tmp_rect = pygame.Rect(0, offset_y, 100, 30)
        tmp_rect.right = -100
        self.showCollideAreaBtn = elements.UIButton(
            tmp_rect, 'show collide', ui_manager, anchors={'right': 'right'}
        )

        offset_y += 40  # ############# collide type | radius
        tmp_rect = pygame.Rect(0, offset_y, 100, 30)
        tmp_rect.right = -100
        self.collideType = elements.UIDropDownMenu(
            ['circle', 'polygon'], 'circle', tmp_rect, ui_manager, anchors={'right': 'right'}
        )
        tmp_rect = pygame.Rect(0, offset_y, 50, 30)
        tmp_rect.right = 0
        self.collideCircleRadiusInput = elements.UITextEntryLine(
            tmp_rect, ui_manager, initial_text='1', anchors={'right': 'right'}
        )

        offset_y += 40  # ############# point edit
        tmp_rect = pygame.Rect(0, offset_y, 100, 30)
        tmp_rect.right = -100
        self.collidePointClearBtn = elements.UIButton(
            tmp_rect, 'clear', ui_manager, anchors={'right': 'right'}
        )
        tmp_rect = pygame.Rect(0, offset_y, 100, 30)
        tmp_rect.right = 0
        self.collidePointOkBtn = elements.UIButton(
            tmp_rect, 'ok', ui_manager, anchors={'right': 'right'}
        )
        # endregion

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.typeListBtn:
                if self.typeListView.visible:
                    self.typeListView.hide()
                else:
                    self.typeListView.show()
                    # if self.handleTypeLoad is not None:
                    #     self.handleTypeLoad()
            elif e0.ui_element == self.nameListBtn:
                if self.nameListView.visible:
                    self.nameListView.hide()
                else:
                    self.nameListView.show()
                    # if self.handleNamesLoad is not None:
                    #     self.handleNamesLoad()
            elif e0.ui_element == self.actionListBtn:
                if self.actionListView.visible:
                    self.actionListView.hide()
                else:
                    self.actionListView.show()
                    # if self.handleActionLoad is not None:
                    #     self.handleActionLoad()

            elif e0.ui_element == self.playStopButton:
                pass
            elif e0.ui_element == self.showCollideAreaBtn:
                pass
            elif e0.ui_element == self.showNavAreaBtn:
                pass
            elif e0.ui_element == self.collidePointClearBtn:
                pass
            elif e0.ui_element == self.collidePointOkBtn:
                pass

        if e0.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if e0.ui_element == self.chooseFileDialog:
                if self._handlePathPicked is not None:
                    self._handlePathPicked(e0.text)
                    self._handlePathPicked = None

        elif e0.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if e0.ui_element == self.loadButton:
                if e0.text == 'load':
                    if self.chooseFileDialog is not None:
                        self.chooseFileDialog.kill()
                        self.chooseFileDialog = None
                    self.chooseFileDialog = pygame_gui.windows.UIFileDialog(
                        pygame.Rect(0, 0, 400, 400), self.uiManager, allow_picking_directories=True
                    )
                    self._handlePathPicked = self.handleResourceLoad
                elif e0.text == 'refresh':
                    if self.handleRefresh is not None:
                        self.handleRefresh()
                    # self.chooseFileDialog.on
                loadButton = elements.UIDropDownMenu(
                    self.loadButton.options_list, self.loadButton.options_list[0],
                    self.loadButton.relative_rect, self.uiManager, anchors=self.loadButton.anchors)
                self.loadButton.kill()
                self.loadButton = loadButton
            elif e0.ui_element == self.lazyButton:
                if e0.text == 'to resource':
                    if self.handleParamToResource is not None:
                        self.handleParamToResource()
                    elif self.handleParamToType is not None:
                        self.handleParamToType()
                    elif self.handleParamToName is not None:
                        self.handleParamToName()
                    # self.chooseFileDialog.on
                loadButton = elements.UIDropDownMenu(
                    self.lazyButton.options_list, self.lazyButton.options_list[0],
                    self.loadButton.relative_rect, self.uiManager, anchors=self.lazyButton.anchors)
                self.lazyButton.kill()
                self.lazyButton = loadButton

            elif e0.ui_element == self.typeOperaBtn:
                if e0.text == 'delete':
                    if self.handleDeleteType is not None:
                        self.handleDeleteType()
                    # self.chooseFileDialog.on
                loadButton = elements.UIDropDownMenu(
                    self.typeOperaBtn.options_list, self.typeOperaBtn.options_list[0],
                    self.typeOperaBtn.relative_rect, self.uiManager, anchors=self.typeOperaBtn.anchors)
                self.typeOperaBtn.kill()
                self.typeOperaBtn = loadButton
            elif e0.ui_element == self.nameOperaBtn:
                if e0.text == 'delete':
                    if self.handleDeleteType is not None:
                        self.handleDeleteType()
                    # self.chooseFileDialog.on
                loadButton = elements.UIDropDownMenu(
                    self.nameOperaBtn.options_list, self.nameOperaBtn.options_list[0],
                    self.nameOperaBtn.relative_rect, self.uiManager, anchors=self.nameOperaBtn.anchors)
                self.nameOperaBtn.kill()
                self.nameOperaBtn = loadButton
            elif e0.ui_element == self.actionOperaBtn:
                if e0.text == 'delete':
                    if self.handleDeleteType is not None:
                        self.handleDeleteType()
                    # self.chooseFileDialog.on
                loadButton = elements.UIDropDownMenu(
                    self.actionOperaBtn.options_list, self.actionOperaBtn.options_list[0],
                    self.actionOperaBtn.relative_rect, self.uiManager, anchors=self.actionOperaBtn.anchors)
                self.actionOperaBtn.kill()
                self.actionOperaBtn = loadButton

            elif e0.ui_element == self.collideType:
                pass

        elif e0.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if e0.ui_element == self.intervalInput:
                try:
                    v = float(self.intervalInput.get_text())
                    if self.handleIntervalChange is not None:
                        self.handleIntervalChange(v)
                except:
                    pass
            elif e0.ui_element == self.legalSizeXInput:
                try:
                    v = float(self.legalSizeXInput.get_text())
                    if self.legalSizeXInput is not None:
                        self.handleLegalSizeXChange(v)
                except:
                    pass
            elif e0.ui_element == self.legalSizeYInput:
                try:
                    v = float(self.legalSizeYInput.get_text())
                    if self.legalSizeYInput is not None:
                        self.handleLegalSizeXChange(v)
                except:
                    pass
            elif e0.ui_element == self.anchorXInput:
                try:
                    v = float(self.anchorXInput.get_text())
                    if self.handleAnchorXChange is not None:
                        self.handleAnchorYChange(v)
                except:
                    pass
            elif e0.ui_element == self.anchorYInput:
                try:
                    v = float(self.anchorYInput.get_text())
                    if self.handleAnchorYChange is not None:
                        self.handleAnchorYChange(v)
                except:
                    pass
            elif e0.ui_element == self.collideCircleRadiusInput:
                try:
                    v = float(self.collideCircleRadiusInput.get_text())
                    if self.handleCollideRadiusChange is not None:
                        self.handleCollideRadiusChange(v)
                except:
                    pass
            elif e0.ui_element == self.actionRegex:
                if self.handleActionRegexChange is not None:
                    self.handleActionRegexChange(self.actionRegex.get_text())

        elif e0.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if e0.element_ui == self.typeListView:
                if self.handleTypeModify is not None:
                    self.handleTypeModify(e0.text)
            elif e0.element_ui == self.nameListView:
                if self.handleNameModify is not None:
                    self.handleNameModify(e0.text)
            elif e0.element_ui == self.actionListView:
                if self.handleActionModify is not None:
                    self.handleActionModify(e0.text)


#  ui state


class AssetEditorUIStateMngr(UIStateManagerBase[IUIStateInterface]):
    UI_STATE_BEGIN = 0x1

    def __init__(self):
        super().__init__()
        self.ui = AssetEditorUI()

        self[self.UI_STATE_BEGIN] = AssetEditorUIState(self.ui)
        self.currentUIState = self[self.UI_STATE_BEGIN]

    def active(self):
        begin_game_ui = AssetEditorUI()
        UserInterfaceManager().switch_user_interface(begin_game_ui)

    def inactive(self):
        UserInterfaceManager().switch_user_interface(None)


class AssetEditorUIState(IUIStateInterface):
    def __init__(self, ui):
        self.ui: AssetEditorUI = ui
        self.config: ConfigBase | None = None
        self.assetPackage: AssetPackage | None = None

        self.currentResourceId = None
        self.currentResourcePath = None
        # self.currentTypeData = {}
        self.currentType = None
        # self.currentNameData = []
        self.currentName = None
        self.isCurrentNameSprite = False
        # self.currentActionData = []
        self.currentAction = None

    def active(self):
        self.config = ConfigBase()
        am = AssetManager()
        am.init(self.config)
        self.assetPackage = am.load_resource(('test', "core", "politics"))

    def inactive(self):
        del AssetManager()[self.assetPackage.packageId]

    def handle_resource_load(self, p):
        if not os.path.isdir(p):
            return
        tmp_p = p
        p, t = os.path.split(p)
        p, name = os.path.split(p)
        p, type_ = os.path.split(p)
        self.currentResourceId = type_, name, t
        self.currentResourcePath = tmp_p
        if self.assetPackage is not None:
            del AssetManager()[self.assetPackage.packageId]
        self.assetPackage = AssetManager().load_resource(self.currentResourceId, True)
        self.handle_type_load()

    def handle_type_modify(self, v):
        pass

    def handle_name_modify(self, v):
        pass

    def handle_action_modify(self, v):
        pass

    def handle_name_type_change(self, v):
        pass

    # def handle_type_load(self):
    #     if self.currentResourceId is None:
    #         return
    #     self.currentTypeData.clear()
    #     for i in os.listdir(self.currentResourcePath):
    #         if not os.path.isdir(os.path.join(self.currentResourcePath, i)):
    #             continue
    #         _i = i.index('.')
    #         if _i == -1:
    #             continue
    #         t, name = i[:_i], i[_i:]
    #         if t == '' or name == '':
    #             continue
    #         if t not in self.currentTypeData:
    #             self.currentTypeData[t] = [name]
    #         else:
    #             self.currentTypeData[t].append(name)
    #
    #     self.ui.typeListView.set_item_list(list(self.currentTypeData.keys()))
    #
    # def handle_name_load(self):
    #     if self.currentType is None:
    #         return
    #     self.currentNameData = self.currentTypeData[self.currentType]
    #     self.ui.nameListView.set_item_list(self.currentNameData)
    #
    # def handle_action_load(self):
    #     if self.currentName is None:
    #         return
    #     if self.isCurrentNameSprite:
    #         self.ui.actionOperaBtn.show()
    #         self.ui.actionListView.show()
    #         self.ui.actionRegex.show()
    #         self.ui.actionListBtn.show()
    #     else:
    #         self.ui.actionOperaBtn.hide()
    #         self.ui.actionListView.hide()
    #         self.ui.actionRegex.hide()
    #         self.ui.actionListBtn.hide()
    #     # self.currentActionData

    def handle_delete_type(self):
        pass

    def handle_delete_name(self):
        pass

    def handle_delete_action(self):
        pass

    def handle_param_to_resource(self):
        pass

    def handle_param_to_type(self):
        pass

    def handle_param_to_name(self):
        pass

    def handle_play_stop(self):
        pass

    def handle_show_collide(self):
        pass

    def handle_show_nav(self):
        pass

    def handle_collide_clear(self):
        pass

    def handle_collide_ok(self):
        pass

    def handle_interval_change(self, v):
        pass

    def handle_legal_size_x_change(self, v):
        pass

    def handle_legal_size_y_change(self, v):
        pass

    def handle_anchor_x_change(self, v):
        pass

    def handle_anchor_y_change(self, v):
        pass

    def handle_collide_radius_change(self, v):
        pass

    def handle_action_regex_change(self, v):
        pass


# scene


class AssetEditorScene(SceneBase):
    def __init__(self):
        super().__init__()
        self.surface = pygame.Surface((1000, 750)).convert_alpha()

    def get_surface(self) -> pygame.Surface:
        return self.surface


# entity


class AssetEditorRootEntity(RootEntityBase):
    def __init__(self, config, pkg, scene):
        super().__init__()
        self.config: ConfigBase = config
        self.assetPackage: AssetPackage = pkg
        self.worldScene: SceneBase = scene

    def release(self):
        pass


if __name__ == '__main__':
    __director = Director()
    __director.init(EDITOR_ENV_ID, AssetEditorUIStateMngr(), (1000, 750))

    # 创建场景
    __scene = AssetEditorScene()
    SceneManager()[EDITOR_ENV_ID] = __scene
    SceneManager().switch_scene(EDITOR_ENV_ID)

    __director.run()
