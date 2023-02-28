#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :asset.py
# @Time      :07/02/2023
# @Author    :russionbear
# @Function  :function
import os.path
from typing import Dict, List, Tuple
import pygame

# ##############################
# 定义了asset 的存放、加载格式
# file struction: author/name/[bgm | sound | entity | particle] / [\d].png, meta.json
# entity type: sprite, sprites + collide
# 暂不允许collideRange
# #############################


class IConfigInterface:
    def __init__(self):

        # ########## 路径相关
        self.TABLE_STORAGE_PATH = r'E:\workspace\game_lab\qins_moon\res\tables'
        self.RESOURCE_ROOT_PATH = r'E:\workspace\game_lab\qins_moon\res\resource'

        # ######### 显示相关
        self.MAP_BLOCK_SIZE = 50, 50
        self.COLLIDE_BLOCK_SIZE = 5, 5
        self.STATUS_ICON_SIZE = 15, 15
        self.DEFAULT_FONT_SIZE = 30

        # # #######  地图默认配置相关
        # self.DEFAULT_RESOURCE_PACKAGE = 'standard', 'standard', 'politics'

        # 用户默认控制参数相关
        self.MOUSE_SPEED = 10.0

        # 游戏内参数帧数
        self.FPS = 60
        self.MAX_NEXT_POINT_ALLOC_COUNT = 10
        self.BLOCKED_SLEEP_TIME = .4
        self.MAX_TICK_WAIT_ROAD_TASK = 6


class ISpriteAssetInterface:
    def __init__(self):

        self.isTerrain = False

        self.imageRegex = '.*'

        self.anchor = 0, 0
        self.images: List[pygame.Surface] = []
        self.interval: float = 0.0

        self.legalSize: Tuple[float, float] | Tuple[int, int] = 0, 0
        # #### 第一个元素为float，则表示circle形状，tuple类型表示距离中心点的偏移量
        # ###所有值范围 0~1,真实值为：值 * width
        self.shapePoints: List[float | Tuple[float, float]] = []
        self.navBlockSize: tuple = 0, 0


class IPencilInterface:
    def __init__(self, file_path, default_font_size):
        self.filePath: str = file_path
        self.pen: pygame.font.Font = pygame.font.Font(self.filePath, default_font_size)
        self.cacheStorage: Dict[int, pygame.font.Font] = {}

    def set_size(self, size):
        if size not in self.cacheStorage:
            self.cacheStorage[size] = pygame.font.Font(self.filePath, size)
        self.pen = self.cacheStorage[size]

    def render(self, text, color=(0, 0, 0), ant=True, bg=None) -> pygame.Surface:
        return self.pen.render(text, ant, color, bg)


class IAssetPackageInterface:
    def __init__(self):
        self.packageId = "", ""

        self.pencil: IPencilInterface | None = None
        self.backgroundMusics = {}
        self.sound: Dict[str, pygame.mixer.Sound] = {}
        self.sprite: Dict[str, ISpriteAssetInterface] = {}
        self.theme: Dict[str, str] = {}

    def get_pen(self):
        # if self.pencil is None:
        #     return AssetManager.get_instance()[DEFAULT_RESOURCE_PACKAGE].get_pen()
        return self.pencil

    def get_bgm(self, v):
        return self.backgroundMusics.get(v, None)

    def get_sound(self, v):
        return self.sound.get(v, None)

    def get_sprite(self, v, action=''):
        # if action != '':
        #     v = '.' + action
        # if v not in self.sprite:
        #     print(f'error kye {v}, {action}')
        #     return AssetManager.get_instance()[DEFAULT_RESOURCE_PACKAGE].get_sprite('error')
        return self.sprite[os.path.join(v, action)]

    def release(self):
        pass
