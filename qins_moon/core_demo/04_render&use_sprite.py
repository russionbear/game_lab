#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :04_render&use_sprite.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function
import numpy
import pygame.draw

from qins_moon.core.asset import AssetManager, ConfigBase
from qins_moon.core.director import Director, IUIStateInterface, UIStateManagerBase
from qins_moon.core.render.render import RenderBase, SceneBase, SceneManager
from qins_moon.core.render.component import AnimeRenderComponent, InfoRenderComponent, JoinedSurfaceRenderComponent, \
    JoinedSurfaceRuleBase
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


def easy_render():
    __director = Director()

    class TileRender(RenderBase):
        def get_surface(self) -> pygame.Surface:
            suf = pygame.Surface((50, 50))
            suf.fill((255, 0, 0))
            return suf

    __scene = TestCoreScene()
    __tile = TileRender()
    __tile.loc = 100, 100
    __tile.set_scene(__scene)

    SceneManager()['test'] = __scene
    SceneManager().switch_scene('test')

    __director.init('test', TestCoreUIStateMngr())
    __director.run()


def info_and_anime_render_component():
    """
    只测试了一部分功能
    :return:
    """
    __director = Director()
    __director.init('test', TestCoreUIStateMngr())

    # 加载资源包
    am = AssetManager()
    config = ConfigBase()
    am.init(config)
    pkg = am.load_resource(TEST_ASSET_PACKAGE_ID)

    # 创建animation 实列
    test_mode = 'building.bridge'
    __animation = AnimeRenderComponent(test_mode, pkg)
    __animation.loc = 100, 100
    __animation2 = AnimeRenderComponent(test_mode, pkg)
    __animation2.loc = 100, 50

    # 创建info 实例
    __info = InfoRenderComponent(__animation.get_surface().get_size(), config, pkg)
    __info.loc = __animation.loc
    __info.blood = 1.0
    __info.title = "city"

    # 创建场景并添加render
    __scene = TestCoreScene()
    SceneManager()['test'] = __scene
    SceneManager().switch_scene('test')
    __animation.set_scene(__scene)
    __animation2.set_scene(__scene)
    __info.set_scene(__scene)

    __director.run()


def joined_surface_render_component():
    __director = Director()
    __director.init('test', TestCoreUIStateMngr())

    # 加载资源包
    am = AssetManager()
    config = ConfigBase()
    am.init(config)
    pkg = am.load_resource(TEST_ASSET_PACKAGE_ID)

    # # 加载数据表
    # config = ConfigBase()
    # DataTableLoader.table_storage_path = config.TABLE_STORAGE_PATH
    # DataTableLoader.load_data(*TEST_TABLE_ID, Cv6DataTable())

    # joined_surface
    terrain_map = numpy.ones((16, 16), dtype=numpy.int_)
    joined_suf_rule = JoinedSurfaceRuleBase()
    joined_suf_rule.rules = [({}, pkg.get_sprite(TEST_MODE))]
    joined_suf_rule.id = 1
    joined_suf = JoinedSurfaceRenderComponent(config, {1: joined_suf_rule}, terrain_map, interval=1.2, layer_nu=2)

    # 创建场景并添加render
    __scene = TestCoreScene()
    SceneManager()['test'] = __scene
    SceneManager().switch_scene('test')
    joined_suf.set_scene(__scene)

    __director.run()


if __name__ == '__main__':
    # easy_render()
    # info_and_anime_render_component()
    joined_surface_render_component()
    pass
