#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :director.py
# @Time      :07/01/2023
# @Author    :russionbear
# @Function  :程序入口类，协调管理ui模块(UserInterfaceManager), 实体模块(RootEntity), 算法模块
import pygame

from qins_moon.core.ui_element import UserInterfaceManager
from qins_moon.core.render.render import SceneManager
from qins_moon.core.director.entity import RootEntityManager
from qins_moon.core.director.ui_state import UIStateMngManager
from qins_moon.core.director.event_loop import TickEventLoop
from qins_moon.core.utils.detached_thread import DetachedThread
from qins_moon.core.physx import PhysX


class Director:
    """
    全局唯一
    """
    _instance = None

    def __init__(self):
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self

        #
        self.surface: pygame.Surface | None = None
        self.isRunning = True
        self.clock = pygame.time.Clock()
        self.fps = 60

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)

    def init(self, begin_ui_state_key, begin_ui_state, size=(1000, 800)):
        pygame.init()
        self.isRunning = True
        self.surface = pygame.display.set_mode(size, flags=pygame.RESIZABLE)
        UserInterfaceManager().resize(self.surface)
        SceneManager().set_blit_window(self.surface)
        ui_mng = UIStateMngManager()
        ui_mng[begin_ui_state_key] = begin_ui_state
        ui_mng.switch_ui_state_mngr(begin_ui_state_key)
        DetachedThread().start()

    def run(self):
        self.clock = pygame.time.Clock()

        scene_mng = SceneManager()
        root_entity_center = RootEntityManager()
        ui_state_center = UIStateMngManager()
        ui_ele_mng = UserInterfaceManager()
        detached_thread = DetachedThread()
        phys = PhysX()
        event_loop = TickEventLoop()
        try:
            while self.isRunning:
                world_scene = scene_mng.current_scene
                root_entity = root_entity_center.currentRootEntity
                ui_state = ui_state_center.currentUiStateMngr

                time_delta = self.clock.tick(self.fps) / 1000.0

                # event
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.isRunning = False

                    ui_ele_mng.event(event)
                    ui_state.event(event)
                    if root_entity:
                        root_entity.event(event)
                    if world_scene:
                        world_scene.event(event)

                # update
                ui_ele_mng.update(time_delta)
                if root_entity:
                    root_entity.update(time_delta)
                if world_scene:
                    world_scene.update(time_delta)

                # 物理系统更新
                phys.update(time_delta)

                # 独立线程发布计算结果
                detached_thread.publish_result()

                # 事件循环
                event_loop.update(time_delta)

                # draw
                self.surface.fill((0, 0, 0, 0))
                if world_scene:
                    world_scene.draw()
                ui_ele_mng.draw()

                pygame.display.set_caption(str(1/time_delta))

                pygame.display.update()
        finally:
            DetachedThread().stop()
            pass
