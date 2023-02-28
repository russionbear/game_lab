#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :05_entity_system&grid_move.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function

import pygame.draw

from qins_moon.core.asset import AssetManager, ConfigBase
from qins_moon.core.director import Director, IUIStateInterface, UIStateManagerBase, EntityBase, RootEntityBase, \
    RootEntityManager
from qins_moon.core.render.render import SceneBase, SceneManager
from qins_moon.core.render.component import AnimeRenderComponent, InfoRenderComponent
from qins_moon.core.grid_map.grid_movement import GridMovement


TEST_ASSET_PACKAGE_ID = ('test', 'core', 'politics')
TEST_TABLE_ID = 'test', 'core', 'politics'
TEST_MODE = 'building.bridge'

# scene


class TestCoreScene(SceneBase):
    def __init__(self):
        super().__init__()
        self.surface = pygame.Surface((800, 600)).convert_alpha()

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


# about entity
class UnitEntity(EntityBase):
    def __init__(self, mode_name, pkg, config, scene):
        super().__init__()
        self.animationComponent = AnimeRenderComponent(mode_name, pkg)
        self.infoComponent = InfoRenderComponent(self.animationComponent.get_surface().get_size(),
                                                 config, pkg)
        self.animationComponent.set_scene(scene)
        self.infoComponent.set_scene(scene)

        self.movement = GridMovement((0, 0), 300)

    def update(self, delta_time):
        self.infoComponent.update(delta_time)
        self.animationComponent.update(delta_time)
        self.movement.update(delta_time)
        loc = self.movement.loc
        self.infoComponent.loc = loc
        self.animationComponent.loc = loc


class RootEntity(RootEntityBase):
    def __init__(self, config, asset_pkg, scene):
        super().__init__()
        self.config = config
        self.worldScene = scene
        self.assetPackage = asset_pkg

        unit = UnitEntity(TEST_MODE, asset_pkg, config, scene)
        unit.id = 100
        self.unit = unit
        self.add_child(unit)

    def update(self, delta_time):
        loc = self.unit.movement.loc
        mouse_loc = pygame.mouse.get_pos()
        self.unit.movement.direction = mouse_loc[0] - loc[0], mouse_loc[1] - loc[1]
        super().update(delta_time)
        # print('hi')


if __name__ == '__main__':
    __director = Director()
    __director.init('test', TestCoreUIStateMngr())

    # 加载资源包
    __am = AssetManager()
    __config = ConfigBase()
    __am.init(__config)
    __pkg = __am.load_resource(TEST_ASSET_PACKAGE_ID)

    # 创建场景
    __scene = TestCoreScene()
    SceneManager()['test'] = __scene
    SceneManager().switch_scene('test')

    # root entity
    root_entity = RootEntity(__config, __pkg, __scene)
    RootEntityManager()['test'] = root_entity
    RootEntityManager().switch_root_entity('test')

    __director.run()
