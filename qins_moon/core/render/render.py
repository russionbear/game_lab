#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :render.py
# @Time      :16/01/2023
# @Author    :russionbear
# @Function  :function
import pygame

from qins_moon.core.interface.render import IRenderInterface, ISceneInterface
from qins_moon.core.utils.data_structure import RegistryBase


class RenderBase(IRenderInterface):
    pass


class SceneBase(ISceneInterface):
    def __init__(self):
        super().__init__()
        self.camera = SceneCameraBase(self)

    def event(self, e0: pygame.event.Event):
        self.camera.event(e0)

    def update(self, delta_time):
        super().update(delta_time)
        self.camera.update(delta_time)


class SceneCameraBase:
    def __init__(self, scene):
        self._scene: SceneBase = scene
        self._moveDirection = 0, 0
        self._trackTarget = 0
        self._speed = 500
        self._moveArea = 0, 0, 0, 0
        self.canScroll = True

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def track_target(self):
        return self._trackTarget

    @track_target.setter
    def track_target(self, value):
        pass

    def handle_resize(self):
        window_size = pygame.display.get_window_size()
        scene_size = self._scene.get_surface().get_size()
        scene_size = scene_size[0] * self._scene.scale, scene_size[1] * self._scene.scale
        self._moveArea = (scene_size[0] - window_size[0]) / 2, (scene_size[1] - window_size[1]) / 2
        if self._moveArea[0] < 0:
            self._moveArea = 0, self._moveArea[1]
        if self._moveArea[1] < 0:
            self._moveArea = self._moveArea[0], 0
        center_loc = window_size
        center_loc = center_loc[0] / 2, center_loc[1] / 2
        self._moveArea = center_loc[0] - self._moveArea[0], center_loc[1] - self._moveArea[1], \
            center_loc[0] + self._moveArea[0], center_loc[1] + self._moveArea[1]
        self._scene.set_location(self.handle_new_loc(self._scene.loc))

    def handle_new_loc(self, loc):
        if loc[0] < self._moveArea[0]:
            loc = self._moveArea[0], loc[1]
        elif loc[0] > self._moveArea[2]:
            loc = self._moveArea[2], loc[1]

        if loc[1] < self._moveArea[1]:
            loc = loc[0], self._moveArea[1]
        elif loc[1] > self._moveArea[3]:
            loc = loc[0], self._moveArea[3]
        return loc

    def update(self, delta_time):
        if self._moveDirection == (0, 0):
            return
        old_loc = self._scene.loc
        speed2 = self._speed * delta_time
        new_loc = old_loc[0] + self._moveDirection[0] * speed2, old_loc[1] + self._moveDirection[1] * speed2
        self._scene.set_location(self.handle_new_loc(new_loc))
        # print(self._scene.loc, self._moveDirection, new_loc, self._moveArea)

    def event(self, e0: pygame.event.Event):
        if e0.type == pygame.MOUSEMOTION:
            pass
        elif e0.type == pygame.WINDOWRESIZED:
            self.handle_resize()
        elif e0.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            left = int(keys[pygame.K_LEFT])
            up = int(keys[pygame.K_UP])
            down = int(keys[pygame.K_DOWN])
            right = int(keys[pygame.K_RIGHT])
            if min(left, right, up, down) != max(left, right, up, down):
                self._moveDirection = left - right, up - down
        elif e0.type == pygame.KEYUP:
            keys = pygame.key.get_pressed()
            left = int(keys[pygame.K_LEFT])
            up = int(keys[pygame.K_UP])
            down = int(keys[pygame.K_DOWN])
            right = int(keys[pygame.K_RIGHT])
            if left == right == up == down == 0:
                self._moveDirection = 0, 0

        elif e0.type == pygame.MOUSEWHEEL and self.canScroll:
            # self._scene.mousePosWhenLastScale = pygame.mouse.get_pos()
            if e0.y > 0:
                self._scene.scale = round((self._scene.scale + 0.1), 3)
            else:
                self._scene.scale = round((self._scene.scale - 0.1), 3)
                if self._scene.scale < 0.1:
                    self._scene.scale = 0.1
            self.handle_resize()


class SceneCircleBase:
    def __init__(self, scene):
        self.scene: SceneBase = scene
        self.p = None
        self.currentCircleArea = None
        self.lastCircleArea = None  # beginX, beginY, endX, endY

    def get_current_circle_area(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.p is not None:
            start = min(self.p[0], mouse_pos[0]), min(self.p[1], mouse_pos[1])
            end = max(self.p[0], mouse_pos[0]), max(self.p[1], mouse_pos[1])
            return *start, *end
        return *mouse_pos, *mouse_pos

    def event(self, e0: pygame.event.Event):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            self.p = e0.pos
        elif e0.type == pygame.MOUSEBUTTONUP:
            self.p = None
            self.lastCircleArea = self.currentCircleArea
            self.currentCircleArea = None
        elif e0.type == pygame.MOUSEMOTION:
            if self.p is not None:
                start = min(self.p[0], e0.pos[0]), min(self.p[1], e0.pos[1])
                end = max(self.p[0], e0.pos[0]), max(self.p[1], e0.pos[1])
                self.currentCircleArea = *start, *end

    def draw(self):
        if self.currentCircleArea is not None:
            # print(self.currentCircleArea, '90')
            pygame.draw.rect(self.scene.get_surface(), 'green',
                             pygame.Rect(*self.currentCircleArea[:2],
                                         self.currentCircleArea[2] - self.currentCircleArea[0],
                                         self.currentCircleArea[3] - self.currentCircleArea[1]), 3)


class SceneManager(RegistryBase[SceneBase]):
    """
    单列模式
    """
    _instance = None

    def __init__(self):
        """
        在这里唯一一次写入_instance
        """
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self
        super().__init__()

        self._currentSceneKey: str | None = None
        self._blitWindow: pygame.Surface | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)

    def set_blit_window(self, window):
        self._blitWindow = window
        scene = self.current_scene
        if scene is not None:
            scene.set_blit_window(self._blitWindow)

    @property
    def current_scene(self) -> SceneBase:
        return self._storage.get(self._currentSceneKey, None)

    def switch_scene(self, key):
        self._currentSceneKey = key
        scene = self.current_scene
        if scene is not None:
            scene.set_blit_window(self._blitWindow)
            scene.loc = scene.get_surface().get_width() // 2, scene.get_surface().get_height() // 2

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        value.set_blit_window(self._blitWindow)
