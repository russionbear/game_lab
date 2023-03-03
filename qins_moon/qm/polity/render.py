#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :render.py
# @Time      :22/02/2023
# @Author    :russionbear
# @Function  :function
import pygame

from qins_moon.core.render.render import SceneBase, SceneCircleBase


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


class PolityScene(SceneBase):
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
        return int(loc[0]//self.blockSize[0]), int(loc[1]//self.blockSize[1])

    def event(self, e0: pygame.event.Event):
        super().event(e0)
        if self.canDrawCircle:
            self.circle.event(e0)

    def draw(self):
        suf = self.get_surface()
        suf.fill((0, 0, 0, 0))
        for v in self._children:
            v.draw()

        size = suf.get_size()
        loc = self.loc[0] - size[0] // 2, self.loc[1] - size[1] // 2
        if self.scale != 1:
            screes_center = pygame.display.get_surface().get_rect().center
            loc = screes_center[0] + (loc[0]-screes_center[0])*self.scale, \
                screes_center[1] + (loc[1]-screes_center[1])*self.scale
            suf = pygame.transform.smoothscale(suf, (suf.get_width()*self.scale, suf.get_height()*self.scale))

        self.circle.draw()
        self._blitWindow.blit(suf, loc)
