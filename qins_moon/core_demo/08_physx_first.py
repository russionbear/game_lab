#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :08_physx_first.py
# @Time      :12/02/2023
# @Author    :russionbear
# @Function  :function
import numpy
import pygame.draw

from qins_moon.core.asset import AssetManager, ConfigBase
from qins_moon.core.director import Director, IUIStateInterface, UIStateManagerBase, EntityBase, RootEntityBase, \
    RootEntityManager
from qins_moon.core.render.render import SceneBase, SceneManager, RenderBase
from qins_moon.core.render.component import AnimeRenderComponent, InfoRenderComponent
from qins_moon.core.grid_map.grid_movement import GridMovement
from qins_moon.core.physx import PhysX, RigidBodyBase, StaticBodyBase
from qins_moon.core.utils.navigation_mesh_2d import NavigationMesh2D


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


class CoverRender(RenderBase):
    def __init__(self, world_size):
        super().__init__()
        self.suf = pygame.Surface(world_size).convert_alpha()
        self.zindex = 10, 1
        self.anchor = .5, self.suf.get_height()/self.suf.get_width()/2
        self.suf.fill((0, 0, 0, 0))
        self.lastLines = []
        self.lastRoad = []

    def get_surface(self) -> pygame.Surface:
        return self.suf

    def show_lines(self, lines):
        self.lastLines = lines
        self._render()

    def show_road(self, road):
        self.lastRoad = road
        self._render()

    def _render(self):
        self.suf.fill((0, 0, 0, 0))
        for line in self.lastLines:
            pygame.draw.line(
                self.suf, (255, 0, 0), line[0], line[1])

        if self.lastRoad:
            for line_i in range(1, len(self.lastRoad)):
                # print(self.lastRoad, line_i)
                line = self.lastRoad[line_i-1], self.lastRoad[line_i]
                # print(line, 'line')
                pygame.draw.line(
                    self.suf, (0, 255, 0), line[0], line[1])


class BuildingRender(RenderBase):
    def __init__(self):
        super().__init__()
        self.suf = pygame.Surface((50, 50))
        self.suf.fill((255, 0, 0))
        self.zindex = 2, 1
        self.anchor = 0, 0

    def get_surface(self) -> pygame.Surface:
        return self.suf


class BuildingEntity(EntityBase):
    def __init__(self, id_, loc, size, scene):
        super().__init__()
        self.id = id_
        size = size/2
        self.staticBody = StaticBodyBase(id_, [(-size, -size), (size, -size), (size, size), (-size, size)], loc, (1, 1))
        PhysX().add_static(self.staticBody)
        self.buildingRender = BuildingRender()
        self.buildingRender.loc = loc
        self.buildingRender.suf = pygame.Surface((size*2, size*2)).convert_alpha()
        self.buildingRender.suf.fill((255, 0, 0, 100))
        self.buildingRender.set_scene(scene)
        # print(self.buildingRender.loc, self.buildingRender.anchor)


class BuildingLayerEntity(EntityBase):
    def __init__(self, scene):
        super().__init__()
        # 16, 12
        self.buildings = [(1, 1), (2, 2)]
        for i1, i in enumerate(self.buildings):
            tmp_e = BuildingEntity(i1, (i[0]*50+25, i[1]*50+25), 40, scene)
            self.add_child(tmp_e)


# about entity
class UnitEntity(EntityBase):
    def __init__(self, mode_name, pkg, config, scene):
        super().__init__()
        self.animationComponent = AnimeRenderComponent(mode_name, pkg)
        self.infoComponent = InfoRenderComponent(self.animationComponent.get_surface().get_size(),
                                                 config, pkg)
        self.animationComponent.set_scene(scene)
        self.infoComponent.set_scene(scene)
        self.animationComponent.zindex = 1, 1
        self.infoComponent.zindex = 1, 2

        # self.movement = GridMovement((0, 0), 300)
        self.rigidbody = RigidBodyBase(100, 100, 25, (100, 100), (1, 1))
        PhysX().add_dynamic(self.rigidbody)

    def update(self, delta_time):
        self.infoComponent.update(delta_time)
        self.animationComponent.update(delta_time)
        loc = self.rigidbody.loc
        self.infoComponent.loc = loc
        self.animationComponent.loc = loc
        # print('loc', loc, 'anchor', self.infoComponent.anchor, self.animationComponent.anchor)


class RootEntity(RootEntityBase):
    def __init__(self, config, asset_pkg, scene):
        super().__init__()
        self.config = config
        self.worldScene = scene
        self.assetPackage = asset_pkg

        PhysX().init((800, 600), [(1, 1)])
        unit = UnitEntity(TEST_MODE, asset_pkg, config, scene)
        unit.id = 100

        self.unit = unit
        self.add_child(unit)
        # self.unit2 = self.lastLoc
        self.buildingLayer = BuildingLayerEntity(scene)
        self.coverLayer = CoverRender((800, 600))
        self.coverLayer.set_scene(self.worldScene)

    def event(self, e0):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            if e0.button == 1:
                mouse_loc = pygame.mouse.get_pos()
                # self.unit.rigidbody._nextPoint = mouse_loc
                # current_loc = self.unit.rigidbody.loc
                # current_loc = current_loc.x, current_loc.y
                # print(PhysX().navigationMesh2D.get_triangle(mouse_loc), 'angleId')
                self.unit.rigidbody.set_target(mouse_loc)
                # print(PhysX().navigationMesh2D.short_road(current_loc, mouse_loc, self.unit.rigidbody.shape.radius))
                self.coverLayer.show_road([tuple(self.unit.rigidbody.next_point)] + self.unit.rigidbody.nextPoints)
            elif e0.button == 3:
                print(PhysX().navigationMesh2D.angels)
                self.coverLayer.show_lines(PhysX().navigationMesh2D.lines)


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
