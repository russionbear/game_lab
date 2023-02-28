#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :ui_home.py
# @Time      :07/01/2023
# @Author    :russionbear
# @Function  :function
import pygame

from qins_moon.dropped.core.ui import UserInterfaceManager
from dropped.example.politics.ui import MakeRandomMapView


if __name__ == "__main__":
    pygame.init()

    pygame.display.set_caption('Quick Start')
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    __ui_mng = UserInterfaceManager.get_instance()
    __ui_mng.resize(window_surface)
    __ui_mng.switch(MakeRandomMapView())

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            __ui_mng.event(event)

        __ui_mng.update(time_delta)

        window_surface.blit(background, (0, 0))
        __ui_mng.draw()

        pygame.display.update()
