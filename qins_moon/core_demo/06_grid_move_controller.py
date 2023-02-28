#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :06_grid_move_controller.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function

import pygame.draw
import numpy
from qins_moon.core.asset import AssetManager, ConfigBase, AssetPackage
from qins_moon.core.director import Director, IUIStateInterface, UIStateManagerBase, EntityBase, RootEntityBase, \
    RootEntityManager
from qins_moon.core.render.render import SceneBase, SceneManager
from qins_moon.core.render.component import AnimeRenderComponent, InfoRenderComponent, JoinedSurfaceRenderComponent, \
    JoinedSurfaceRuleBase, GridCoverRenderComponent
from qins_moon.core.grid_map import GridMovement, GridNavigation, GridNavigationManager, GridDynMoveController, \
    GridStaticMoveController, GridFlowFieldStorage


TEST_ASSET_PACKAGE_ID = ('test', 'core', 'politics')
TEST_TABLE_ID = 'test', 'core', 'politics'
TEST_MODE = 'unit.tank'
TEST_MAP_SIZE = 16, 16
TEST_GROUP_ENGINE = 1, 1
TEST_IS_GROUP_PATHFINDING = True  # 测试群组寻路

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
class TerrainLayerEntity(EntityBase):
    def __init__(self, config, pkg, scene):
        super().__init__()
        self.config: ConfigBase = config
        self.assetPackage: AssetPackage = pkg

        if not TEST_IS_GROUP_PATHFINDING:
            # 一.单个单位寻路地图构建
            numpy.random.seed(100)
            terrain_map = numpy.random.randint(0, 5, (16, 16), numpy.int_)
            terrain_map[terrain_map > 1] = 1
            terrain_map[terrain_map == 0] = 2
            terrain_map[0, 0] = 1
            # 模拟寻路出错
            # # 情况一
            # terrain_map[1, 0] = 2
            # # 情况二
            # terrain_map[2, 0] = 2
            # terrain_map[2, 1] = 2
        else:
            # 二.群组寻路地图构建
            numpy.random.seed(100)
            terrain_map = numpy.random.randint(0, 5, (16, 16), numpy.int_)
            terrain_map[terrain_map > 1] = 1
            terrain_map[terrain_map == 0] = 2
            terrain_map[0: 3, 0: 3] = 1

        joined_suf_rule_dict = {}
        for i1, i in [(1, 'terrain.plain-desert'), (2, 'terrain.mountain-desert')]:
            tmp_d = JoinedSurfaceRuleBase()
            joined_suf_rule_dict[i1] = tmp_d
            tmp_d.id = i1
            tmp_d.rules = [({}, self.assetPackage.get_sprite(i))]

        self.joinedSurfaceComponent = JoinedSurfaceRenderComponent(
            config, joined_suf_rule_dict, terrain_map, GridNavigationManager()['test'], 1)
        self.joinedSurfaceComponent.set_scene(scene)
        self.joinedSurfaceComponent.zindex = 1, 1


class UnitEntity(EntityBase):
    def __init__(self, mode_name, pkg, config, scene):
        super().__init__()
        self.animationComponent = AnimeRenderComponent(mode_name, pkg)
        self.infoComponent = InfoRenderComponent(self.animationComponent.get_surface().get_size(),
                                                 config, pkg)
        self.animationComponent.set_scene(scene)
        self.infoComponent.set_scene(scene)
        self.animationComponent.zindex = 2, 1
        self.infoComponent.zindex = 2, 2

        self.movement = GridMovement((0, 0), 100)
        # ####### 以下两个选一个
        # 静态寻路
        # self.gridMoveController = GridStaticMoveController(self.movement, config.MAP_BLOCK_SIZE)
        # self.gridMoveController.set_task([(i, i) for i in range(6)])
        # 动态寻路
        self.gridMoveController = GridDynMoveController(
            self.movement, config, GridNavigationManager()['test'],
            (2, 10), (TEST_GROUP_ENGINE[0] << 8)+TEST_GROUP_ENGINE[1], TEST_GROUP_ENGINE[0])

    def update(self, delta_time):
        self.gridMoveController.update(delta_time)
        self.infoComponent.update(delta_time)
        self.animationComponent.update(delta_time)
        self.movement.update(delta_time)
        loc = self.movement.loc
        self.infoComponent.loc = loc
        self.animationComponent.loc = loc

    def handle_alloc_next_point(self, loc, last_forward):
        pass

    def handle_road_search(self, target):
        pass

    def handle_task_finish(self):
        pass


class RootEntity(RootEntityBase):
    def __init__(self, config, asset_pkg, scene):
        super().__init__()
        self.config = config
        self.worldScene = scene
        self.assetPackage = asset_pkg

        # init grid_nav
        grid_nav = GridNavigation(TEST_MAP_SIZE, [1, 2])  # 地形层、单位层
        GridNavigationManager()['test'] = grid_nav
        grid_nav.add_engine_mapper(
            (TEST_GROUP_ENGINE[0] << 8)+TEST_GROUP_ENGINE[1],
            [(1, lambda arg: 0 if arg == 1 else -1)], numpy.float_)  # init 引擎移动层
        GridFlowFieldStorage().init((4, 4), grid_nav)

        # init terrain map
        self.terrainMap = TerrainLayerEntity(self.config, self.assetPackage, self.worldScene)

        self.units = []
        for i in range(9 if TEST_IS_GROUP_PATHFINDING else 1):
            unit = UnitEntity(TEST_MODE, asset_pkg, config, scene)
            unit.id = i + 100
            unit.gridMoveController.set_grid_loc((i % 3, i // 3))
            grid_nav.refresh_node((i % 3, i // 3), 10, 2)
            self.add_child(unit)
            self.units.append(unit)

    def event(self, e0):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            target = e0.pos
            target = target[0] // self.config.MAP_BLOCK_SIZE[0], target[1] // self.config.MAP_BLOCK_SIZE[1]
            for i in self.units:
                i.gridMoveController.set_task([target])
            for i in self.units[1:]:
                i.gridMoveController.sleep(0.2)


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

    #
    __director.fps = __config.FPS

    __director.run()
