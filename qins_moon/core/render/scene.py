#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: scene.py
# @time: 3/13/2023 1:34 PM
import pygame

from qins_moon.core.render.render import SceneBase, SceneCircleBase


class TileMapSceneBase(SceneBase):
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
        return int(loc[0] // (self.blockSize[0] * self.scale)), int(loc[1] // (self.blockSize[1] * self.scale))

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
        super().draw()
        self.circle.draw()
