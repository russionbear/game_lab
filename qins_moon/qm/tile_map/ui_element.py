#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: ui_element.py
# @time: 3/12/2023 10:16 PM
from typing import Dict, List

import pygame
import pygame_gui
from pygame_gui import elements

from qins_moon.core.ui_element import UserInterfaceBase


class TileMapEditUI(UserInterfaceBase):
    def __init__(self, layer_data, maps=None):
        super().__init__()
        self.maps = maps if maps is not None else []
        self.layerItemData: Dict[str, list] = layer_data

        self.layerButton: elements.UIDropDownMenu | None = None
        self.layerItemButton: elements.UIDropDownMenu | None = None
        self.flagButton: elements.UIDropDownMenu | None = None
        self.visibleListView: elements.UISelectionList | None = None
        self.mapListView: elements.UIDropDownMenu | None = None

        self.mouseLocaPanel: elements.UIPanel | None = None
        self.mouseLocLabel: elements.UILabel | None = None

        self.handleVisibleChange = None

    def show(self):
        self.layerButton.show()
        self.layerItemButton.show()
        self.visibleListView.show()
        self.flagButton.show()

    def hide(self):
        if self.layerButton is None:
            return
        self.layerButton.hide()
        self.layerItemButton.hide()
        self.visibleListView.hide()
        self.flagButton.hide()

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
        self.flagButton = elements.UIDropDownMenu(
            [str(i) for i in range(1, 5)], '1', pygame.Rect(550, 0, 50, 30),
            ui_manager
        )
        self.mapListView = elements.UIDropDownMenu(
            self.maps+[''], '', pygame.Rect(700, 0, 100, 30), ui_manager
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


class TileMapCmdSpectatorUI(UserInterfaceBase):
    def __init__(self):
        super().__init__()
        self.infoBox: elements.UITextBox | None = None

        self.window: elements.UITextEntryLine | None = None
        self.messageData: List[str] = []
        self.maxMessageQueueLength = 20
        # self.
        self.handleInput = None

    def show(self):
        self.window.show()
        self.infoBox.show()

    def hide(self):
        self.window.hide()
        self.infoBox.hide()

    def resize(self, suf, ui_manager):
        rect = pygame.Rect(0, 0, 500, 30)
        rect.bottom = -50
        self.window = elements.UITextEntryLine(
            rect, ui_manager, anchors={'centerx': 'centerx', 'bottom': 'bottom'}
        )
        self.infoBox = elements.UITextBox('', pygame.Rect(0, 0, 300, 200), ui_manager)
        self.re_render_message()

    def re_render_message(self):
        if len(self.messageData) > self.maxMessageQueueLength:
            self.messageData = self.messageData[-self.maxMessageQueueLength:]
        self.infoBox.set_text('\n'.join(self.messageData))

    def event(self, e0):
        if e0.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if e0.ui_element == self.window:
                if self.handleInput is not None:
                    self.handleInput(e0.text)
                self.window.set_text('')
