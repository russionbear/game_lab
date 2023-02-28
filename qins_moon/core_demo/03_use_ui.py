#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :03_use_ui.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function
import pygame

from qins_moon.core.director import Director, UIStateManagerBase, IUIStateInterface
from qins_moon.core.ui_element import UserInterfaceBase, UserInterfaceManager
import pygame_gui
from pygame_gui import elements


class BeginGameUI(UserInterfaceBase):
    def __init__(self):
        self.beginBtn: elements.UIButton | None = None
        self.showOrHideBtn: elements.UIButton | None = None

    def resize(self, suf, ui_manager):
        self.beginBtn = elements.UIButton(pygame.Rect(0, 0, 100, 30), "begin", ui_manager, anchors={'center': 'center'})
        self.showOrHideBtn = elements.UIButton(pygame.Rect(0, 0, 100, 30), "show/hide", ui_manager,
                                               anchors={'centerx': 'centerx'})

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.beginBtn:
                print('hello')
            elif e0.ui_element == self.showOrHideBtn:
                if self.beginBtn.visible:
                    self.beginBtn.hide()
                else:
                    self.beginBtn.show()


class TestCoreUIStateMngr(UIStateManagerBase[IUIStateInterface]):
    UI_STATE_BEGIN = 0x1

    def __init__(self):
        super().__init__()
        self[self.UI_STATE_BEGIN] = BeginGameUIState()
        self.currentUIState = self[self.UI_STATE_BEGIN]

    def active(self):
        begin_game_ui = BeginGameUI()
        UserInterfaceManager().switch_user_interface(begin_game_ui)

    def inactive(self):
        UserInterfaceManager().switch_user_interface(None)


class BeginGameUIState(IUIStateInterface):
    pass


if __name__ == '__main__':
    __director = Director()
    __director.init('test', TestCoreUIStateMngr())
    __director.run()
