#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :collide_points_tool.py
# @Time      :20/02/2023
# @Author    :russionbear
# @Function  :function

import numpy
import pygame.draw

from qins_moon.core.asset import AssetManager, ConfigBase
from qins_moon.core.director import Director, IUIStateInterface, UIStateManagerBase
from qins_moon.core.render.render import RenderBase, SceneBase, SceneManager
from qins_moon.core.render.component import AnimeRenderComponent, InfoRenderComponent, JoinedSurfaceRenderComponent, \
    JoinedSurfaceRuleBase, CoverRenderComponent
from qins_moon.core.utils.data_table_loader import DataTableLoader
from qins_moon.core_demo.data_table import Cv6DataTable


TEST_ASSET_PACKAGE_ID = ('test', 'core', 'politics')
TEST_TABLE_ID = 'test', 'core', 'politics'

TEST_MODE = 'building.bridge'
# scene


class TestCoreScene(SceneBase):
    def __init__(self):
        super().__init__()
        self.surface = pygame.Surface((800, 600)).convert_alpha()
        self.camera.handle_resize()

    def get_surface(self) -> pygame.Surface:
        return self.surface


# about ui_state


class TestCoreUIStateMngr(UIStateManagerBase[IUIStateInterface]):
    UI_STATE_BEGIN = 0x1

    def __init__(self):
        super().__init__()
        self[self.UI_STATE_BEGIN] = BeginGameUIState()
        self.currentUIState = self[self.UI_STATE_BEGIN]


class BeginGameUIState(IUIStateInterface):
    def active(self):
        pass


def easy_render(path, action):
    __director = Director()
    __director.init('test', TestCoreUIStateMngr())

    class TileRender(RenderBase):
        def get_surface(self) -> pygame.Surface:
            suf = pygame.Surface((50, 50))
            suf.fill((255, 0, 0))
            return suf

    am = AssetManager()
    config = ConfigBase()
    am.init(config)
    pkg = am.load_resource(TEST_ASSET_PACKAGE_ID)

    __grid_layer = CoverRenderComponent((800, 600), pkg.get_pen(), config.MAP_BLOCK_SIZE)
    __grid_layer.showGridLine = True
    __grid_layer.re_render()

    __scene = TestCoreScene()

    __tile = TileRender()
    __tile.loc = 100, 100
    __tile.set_scene(__scene)
    __grid_layer.set_scene(__scene)

    SceneManager()['test'] = __scene
    SceneManager().switch_scene('test')

    __director.run()


if __name__ == '__main__':
    easy_render('', '')
