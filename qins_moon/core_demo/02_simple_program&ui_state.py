#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :02_simple_program&ui_state.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function

from qins_moon.core.director import Director, UIStateManagerBase, IUIStateInterface
import pygame
import random


class UIStateBase(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: TestCoreUIStateMngr = mngr


class TestCoreUIStateMngr(UIStateManagerBase):
    UI_STATE_HOME = 0x1
    UI_STATE_UNIT_CMD = 0x2

    def __init__(self):
        super().__init__()
        self[self.UI_STATE_HOME] = HomeUIState(self)
        self[self.UI_STATE_UNIT_CMD] = UnitCmdUIState(self)
        self.currentUIState = self[self.UI_STATE_HOME]
        self.chosenUnitId = 0


class HomeUIState(UIStateBase):
    def event(self, e0):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            unit_id = random.randint(100, 10000)
            self.mngr.chosenUnitId = unit_id
            print(f"单位{unit_id}被你选中")
            self.mngr.switch_ui_state(TestCoreUIStateMngr.UI_STATE_UNIT_CMD)


class UnitCmdUIState(UIStateBase):
    def event(self, e0):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            print(f"你对单位{self.mngr.chosenUnitId}发布了命令")


if __name__ == '__main__':
    __director = Director()
    __director.init('test', TestCoreUIStateMngr())
    __director.run()
