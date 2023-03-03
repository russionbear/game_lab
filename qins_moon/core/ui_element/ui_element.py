#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :ui_element.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function
from typing import List, Tuple, Any

import pygame
import pygame_gui
from pygame_gui import elements

from qins_moon.core.interface.ui_element import IUIInterface


class UserInterfaceBase(IUIInterface):
    def __init__(self):
        self.window: pygame_gui.core.UIElement | None = None

    def show(self):
        if self.window is not None:
            self.window.show()

    def hide(self):
        if self.window is not None:
            self.window.hide()

    def resize(self, suf, ui_manager):
        """
        初始化函数
        :param suf:
        :param ui_manager:
        :return:
        """
        pass

    def event(self, e0):
        pass

    def kill(self):
        for v in self.__dict__.values():
            if isinstance(v, pygame_gui.core.UIElement):
                v.kill()

    @staticmethod
    def set_vertical_layout(self: 'UserInterfaceBase', total_size):
        """
        element 不能设置anchor
        :param self:
        :param total_size:
        :return:
        """
        keys: List[pygame_gui.core.UIElement] = []
        for i in self.__dict__.keys():
            if i == "attributeCrossLine":
                break
            if self.__dict__[i] is None:
                continue
            keys.append(self.__dict__[i])
        heights = [i.get_relative_rect().height for i in keys]
        n = total_size[1] / sum(heights)
        for i1, i in enumerate(keys):
            i.set_relative_position((
                (total_size[0]-i.get_relative_rect().width)//2,
                (i.get_relative_rect().height*n-i.get_relative_rect().height)//2 + sum(heights[:i1]) * n
            ))


class UserInterfaceManager:
    _instance = None

    def __init__(self):
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self

        #
        self.blitWindow: pygame.Surface | None = None
        self.uiManager: pygame_gui.UIManager | None = None
        self.currentUI: IUIInterface | None = None
        self.language = 'zh'

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)

    def switch_user_interface(self, ui: 'IUIInterface | None'):
        self.currentUI = ui
        if self.currentUI is not None:
            self.currentUI.resize(self.blitWindow, self.uiManager)

    def clear(self):
        self.currentUI = None

    def resize(self, suf: pygame.Surface):
        self.blitWindow = suf
        self.uiManager = pygame_gui.UIManager(suf.get_size(), starting_language=self.language)
        if self.currentUI is not None:
            self.currentUI.resize(suf, self.uiManager)

    def update(self, delta_time):
        self.uiManager.update(delta_time)

    def draw(self):
        if self.currentUI:
            self.uiManager.draw_ui(self.blitWindow)

    def event(self, e0):
        self.uiManager.process_events(e0)
        if self.currentUI is not None:
            self.currentUI.event(e0)


class UIMenuBar:
    def __init__(self, data, rect: pygame.Rect, ui_manager, anchor=None):
        self.data: Tuple[str, list] = data
        self.uiManager = ui_manager
        self.titleButton = elements.UIButton(rect, self.data[0], ui_manager, anchors=anchor)
        # self.titleButton.cli
        # rect.move(0, )
        self.listView = elements.UISelectionList(
            pygame.Rect(rect.x, rect.height, rect.width, rect.height*len(data[1])*0.8), data[1], ui_manager,
            anchors={'top': self.titleButton}
        )
        self.listView.hide()

    def _handle_title_click(self):
        if self.listView.visible:
            self.listView.hide()
        else:
            self.listView.show()
            self.listView.on_locale_changed = lambda arg: print(arg)
            # self.listView.set

    def _handle_item_click(self):
        pass
