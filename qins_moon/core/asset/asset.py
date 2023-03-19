#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :asset.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function

import json
import math
import os
import re
import yaml
from typing import Dict, Tuple, List

import pygame

from qins_moon.core.interface.asset import IConfigInterface, IAssetPackageInterface, ISpriteAssetInterface, \
    IPencilInterface


class ConfigBase(IConfigInterface):
    pass


class SpriteAsset(ISpriteAssetInterface):
    """
    config file
    anchor,
    image_re,
    interval,
    legalSize,
    shapePoints,
    navBlockSize,
    isTerrain
    """

    @staticmethod  # dropped
    def load_sprite(path, config: IConfigInterface):
        rlt = ISpriteAssetInterface()

        # 获取所有图片，名称如下正则表达式
        for i in sorted(os.listdir(path)):
            if re.match('^\d\.png$', i) is None:
                continue
            rlt.images.append(pygame.image.load(os.path.join(path, i)).convert_alpha())

        # 获取资源信息
        meta_info = {}
        if os.path.exists(os.path.join(path, 'meta.json')):
            with open(os.path.join(path, 'meta.json'), 'r', encoding='utf-8') as f:
                meta_info = json.load(f)
        else:
            with open(os.path.join(path, 'meta.json'), 'w', encoding='utf-8') as f:
                json.dump({}, f)
        rlt.anchor = meta_info.get("anchor", (.0, .0))
        rlt.interval = meta_info.get("interval", 1.2 if len(rlt.images) > 1 else 0)
        rlt.legalSize = meta_info.get("legalSize", (1, 1))
        rlt.legalSize = rlt.legalSize[0] * config.MAP_BLOCK_SIZE[0], rlt.legalSize[1] * config.MAP_BLOCK_SIZE[1]
        # rlt.shapePoints = meta_info.get('shapePoints', [.5])

        return rlt

    @staticmethod
    def load_sprites(path, config: IConfigInterface):
        sprites = {}
        all_images = {}
        for i in sorted(os.listdir(path)):
            if re.match('^.*\.png$', i) is None:
                continue
            _i = i.rindex('.')
            all_images[i[:_i]] = pygame.image.load(os.path.join(path, i))
            # all_images.append(pygame.image.load(os.path.join(path, i)).convert_alpha())

        if os.path.exists(os.path.join(path, 'meta.yml')):
            with open(os.path.join(path, 'meta.yml'), 'r', encoding='utf-8') as f:
                meta_info = yaml.load(f, yaml.Loader)
                if '' not in meta_info:
                    meta_info[''] = {}
        else:
            with open(os.path.join(path, 'meta.yml'), 'w', encoding='utf-8') as f:
                meta_info = {'': {}}
                # yaml.dump(meta_info, f)
        if 'global' in meta_info:
            global_set = meta_info['global']
            del meta_info['global']
        else:
            global_set = None
        for k, action_info in meta_info.items():
            if global_set:
                action_info = global_set

            sprite = SpriteAsset()
            sprite.imageRegex = action_info.get('imageRegex', '.*')
            sprite.isTerrain = action_info.get('isTerrain', False)

            for k1, v in all_images.items():
                if re.match(sprite.imageRegex, k1):
                    if sprite.isTerrain:
                        sprite.images.append(v)
                    else:
                        sprite.images.append(v.convert_alpha())

            sprite.anchor = tuple(action_info.get("anchor", (.0, .0)))
            sprite.interval = action_info.get("interval", 1.2 if len(sprite.images) > 1 else 0)
            sprite.legalSize = action_info.get("legalSize", (1, 1))
            sprite.legalSize = sprite.legalSize[0] * config.MAP_BLOCK_SIZE[0], \
                               sprite.legalSize[1] * config.MAP_BLOCK_SIZE[1]
            if 'navBlockSize' not in action_info:
                sprite.navBlockSize = math.ceil(sprite.legalSize[0] / config.MAP_BLOCK_SIZE[0]), \
                    math.ceil(sprite.legalSize[1] / config.MAP_BLOCK_SIZE[1])
            else:
                sprite.navBlockSize = tuple(action_info['navBlockSize'])

            if 'shapePoints' not in action_info:
                if sprite.isTerrain:
                    sprite.shapePoints = [
                        (-sprite.legalSize[0], -sprite.legalSize[1]),
                        (-sprite.legalSize[0], sprite.legalSize[1]),
                        (sprite.legalSize[0], sprite.legalSize[1]),
                        (sprite.legalSize[0], -sprite.legalSize[1])
                    ]
                else:
                    sprite.shapePoints = [max(sprite.legalSize) // 2]
            else:
                sprite.shapePoints = action_info['shapePoints']

            sprites[k] = sprite

        return sprites


class Pencil(IPencilInterface):
    pass


class AssetPackage(IAssetPackageInterface):
    def __init__(self):
        super().__init__()

        # #  [{方向: int(-2 相等, -1 不相等， 0 忽略, 其他相等)}]   ;; 不存在的邻居将被忽略
        self.modelJoinedSurfaceRule: Dict[str, List[Tuple[Dict[tuple, int], SpriteAsset | str]]] = {}

    @staticmethod
    def load_resource(config: IConfigInterface, key):
        path = os.path.join(config.RESOURCE_ROOT_PATH, *key)
        rlt = AssetPackage()
        rlt.packageId = key

        for i in os.listdir(path):
            if re.match(r'^.*\.ttf$', i, re.IGNORECASE) is not None:
                rlt.pencil = IPencilInterface(os.path.join(path, i), config.DEFAULT_FONT_SIZE)
                break

        for i in os.listdir(os.path.join(path, 'bgm')):
            rlt.backgroundMusics['.'.join(i.split('.')[:-1])] = i

        for i in os.listdir(os.path.join(path, 'sound')):
            rlt.sound['.'.join(i.split('.')[:-1])] = pygame.mixer.Sound(os.path.join(path, 'sound', i))

        for i in os.listdir(os.path.join(path, 'sprite')):
            if not os.path.isdir(os.path.join(path, 'sprite', i)):
                continue
            # rlt.sprite[i] = SpriteAsset.load_sprite(os.path.join(path, 'sprite', i), config)
            ss = SpriteAsset.load_sprites(os.path.join(path, 'sprite', i), config)
            name = os.path.split(i)[1]
            for k, v in ss.items():
                rlt.sprite[os.path.join(name, k)] = v

        for i in os.listdir(os.path.join(path, 'theme')):
            if i.endswith('.json'):
                rlt.theme['.'.join(i.split('.')[:-1])] = os.path.join(path, 'theme', i)

        with open(os.path.join(path, 'sprite', 'joined_surface_rule.json'), 'r') as f:
            # joined_surface_rule.json = yaml.load(f, yaml.Loader)
            joined_surface_rule = json.load(f)
            # print(joined_surface_rule.json)
            # exit()
            if joined_surface_rule is None:
                joined_surface_rule = {}
            for k, v in joined_surface_rule.items():
                n_l = [({(int(k1.split('_')[0]), int(k1.split('_')[1])): v1 for k1, v1 in rule.items()},
                        rlt.get_sprite(k, s0))
                       for rule, s0 in v]
                rlt.modelJoinedSurfaceRule[k] = n_l

        return rlt

    def get_joined_surface_rule(self, model_name):
        if model_name not in self.modelJoinedSurfaceRule:
            return [({}, self.get_sprite(model_name))]
        return self.modelJoinedSurfaceRule[model_name]


class AssetManager:
    _instance = None

    def __init__(self):
        if self.__class__._instance is not None:
            return

        self.__class__._instance = self
        self._storage: Dict[tuple, IAssetPackageInterface] = {}
        self.config: IConfigInterface | None = None

    def init(self, config):
        self.config = config

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)

    def load_resource(self, key, reload=False):
        if self[key] is not None and not reload:
            return
        rlt = AssetPackage.load_resource(self.config, key)
        self._storage[key] = rlt
        return rlt

    def __getitem__(self, item: Tuple[str, str, str]):
        return self._storage.get(item, None)

    def __contains__(self, item):
        return item in self._storage

    def __delitem__(self, key: Tuple[str, str, str]):
        _tmp = self[key]
        if _tmp is None:
            return
        _tmp.release()
        del self._storage[key]
