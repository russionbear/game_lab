#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :render.py
# @Time      :07/02/2023
# @Author    :russionbear
# @Function  :function
import pygame

from qins_moon.core.utils.data_structure import BisectList


class IRenderInterface:
    def __init__(self):
        self._scene: ISceneInterface | None = None

        #  # zindex 只表示在它父节点中的层级 并非 world scene 中的节点
        #  # 层级相同则看y坐标，再看x坐标(看起来更规律)
        self.zindex: tuple = 0,

        self.loc = 0, 0
        self.tags = {}
        self.anchor = .5, .5

    def set_location(self, loc):
        self.loc = loc

    @property
    def render_order(self):
        return *self.zindex, self.loc[1], self.loc[0]

    def set_scene(self, scene):
        """
        可能会改变id
        :param scene:
        :return:
        """
        old_scene = self._scene
        if old_scene != scene:
            self._scene = scene
            if old_scene is not None:
                old_scene.remove_child(self)

            if scene is not None:
                self._scene.add_child(self)

    def get_surface(self) -> pygame.Surface:
        pass

    # ############################ tick
    def update(self, delta_time):
        pass

    def draw(self):
        suf = self.get_surface()

        if suf is not None:
            size = suf.get_size()
            anchor = size[0] * self.anchor[0], size[0] * self.anchor[1]
            loc = self.loc[0] + anchor[0] - size[0]//2, self.loc[1] + anchor[1] - size[1]//2
            self._scene.get_surface().blit(suf, loc)


class ISceneInterface:
    """
    同时具有相机的功能
    """
    def __init__(self):
        self._blitWindow: pygame.Surface | None = None
        self._children = BisectList[IRenderInterface](key=lambda a: a.render_order)
        self.loc = 0, 0
        self.scale = 1
        # self.mousePosWhenLastScale = pygame.display.get_surface().get_rect().center

    def set_blit_window(self, w):
        self._blitWindow = w

    def get_blit_window(self):
        return self._blitWindow

    def set_location(self, loc):
        self.loc = loc

    def get_surface(self) -> pygame.Surface:
        """
        如果返回值为None，则这是个空节点
        :return:
        """
        pass

    # ############################ children
    def contains(self, e: 'IRenderInterface'):
        return e in self._children

    def add_child(self, *e: 'IRenderInterface'):
        """
        不要添加重复的 元素，否则会渲染两遍
        :param e:
        :return:
        """

        for i in e:
            i.set_scene(self)
            self._children.append(i)

    def remove_child(self, e: 'IRenderInterface'):
        e.set_scene(None)
        self._children.remove(e)

    # ############################ tick
    def update(self, delta_time):
        self._children.sort()
        for v in self._children:
            v.update(delta_time)

    def draw(self):
        suf = self.get_surface()
        suf.fill((0, 0, 0, 0))
        for v in self._children:
            v.draw()

        if self.scale != 1:
            suf = pygame.transform.smoothscale(suf, (suf.get_width()*self.scale, suf.get_height()*self.scale))

        size = suf.get_size()
        loc = self.loc[0] - size[0] // 2, self.loc[1] - size[1] // 2
        # if self.scale != 1:
        #     screes_center = pygame.display.get_surface().get_rect().center
        #     loc = screes_center[0] + (loc[0]-screes_center[0])*self.scale, \
        #         screes_center[1] + (loc[1]-screes_center[1])*self.scale
        #     suf = pygame.transform.smoothscale(suf, (suf.get_width()*self.scale, suf.get_height()*self.scale))
        self._blitWindow.blit(suf, loc)

    def get_mouse_loc_in_scene(self):
        mouse_pos = pygame.mouse.get_pos()
        offset = self.get_render_offset()
        rlt = mouse_pos[0] - offset[0], mouse_pos[1] - offset[1]

        return rlt

    def get_render_offset(self):
        suf = self.get_surface()
        size = (suf.get_width()*self.scale, suf.get_height()*self.scale)
        loc = self.loc[0] - size[0] // 2, self.loc[1] - size[1] // 2
        return loc

    # def get_prim_render_offset(self):
    #     size = self.get_surface().get_size()
    #     loc = self.loc[0] - size[0] // 2, self.loc[1] - size[1] // 2
    #     return loc
    #
    # def get_screen_render_pos(self, pos):
    #     offset = self.loc
    #     o = self.get_render_offset()
    #
    #     return (pos[0]-offset[0]) / self.scale + offset[0] - o[0], (pos[1]-offset[1]) / self.scale + offset[1] - o[1]

    def event(self, e0: pygame.event.Event):
        pass
