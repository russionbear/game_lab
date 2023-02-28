#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :physx.py
# @Time      :10/02/2023
# @Author    :russionbear
# @Function  :function

from typing import Dict, Tuple, List
import pymunk

from qins_moon.core.utils.navigation_mesh_2d import NavigationMesh2D
from qins_moon.core.utils.rvo2 import RVO2, AgentNodeStruct, Vector2


class IStaticBodyInterface:
    def __init__(self, id_, points, loc, category: tuple):
        self.shapePoints: list = points
        body = pymunk.Body(10, 10, pymunk.Body.STATIC)
        body.position = loc
        shape = pymunk.Poly(body, self.shapePoints)  # [(i[0]+loc[0], i[1]+loc[1]) for i in self.shapePoints]
        shape.filter = pymunk.ShapeFilter(categories=category[0], mask=category[1])
        self.shape: pymunk.Poly = shape
        self.id: int = id_

    def release(self):
        pass


"""
参数，同意速度与帧速度一样
"""


class IRigidBodyInterface:
    """
    都是像素坐标
    """
    def __init__(self, id_, base_speed, radius, loc, category: tuple):
        super().__init__()
        self.id: int = id_

        self._speedBuf: Dict[str, float] = {}
        self._baseSpeed = base_speed
        self._speedAfterBuf = base_speed
        self._direction = 0, 0

        body = pymunk.Body(10, 1)
        shape = pymunk.Circle(body, radius)
        shape.filter = pymunk.ShapeFilter(categories=category[0], mask=category[1])
        body.position = loc
        self.shape: pymunk.Circle = shape
        # self.shape.filter.category
        self._nextPoint = 500, 500
        self.nextPoints = []

    def set_base_speed(self, v):
        self._baseSpeed = v
        self.__refresh_speed_after_buf()

    def add_speed_buf(self, k, v):
        self._speedBuf[k] = v
        self.__refresh_speed_after_buf()

    def remove_speed_buf(self, k):
        if k in self._speedBuf:
            del self._speedBuf
        self.__refresh_speed_after_buf()

    def __refresh_speed_after_buf(self):
        self._speedAfterBuf = self._baseSpeed
        for v in self._speedBuf.values():
            self._speedAfterBuf *= v
            self.direction = self.direction
        self.__refresh_velocity()

    # 自动更新nextPoint
    def __refresh_velocity(self):
        direction = self.direction
        velocity = 0, 0
        if self._nextPoint is not None:
            velocity = direction[0] * self._speedAfterBuf, direction[1] * self._speedAfterBuf
            loc = self.shape.body.position
            target = self._nextPoint

            distance = ((loc.x-target[0])**2 + (loc.y-target[1])**2)**.5
            std_dis = self.shape.radius + 10 if self.nextPoints else 2
            if distance < std_dis:
                if self.nextPoints:
                    self._nextPoint = self.nextPoints.pop(0)
                else:
                    self._nextPoint = None
                    velocity = 0, 0
        self.shape.body.velocity = velocity

    def set_next_points(self, points, append=False):
        if points:
            if self._nextPoint is None:
                self._nextPoint = points.pop(0)
            elif not append:
                self._nextPoint = points.pop(0)
            if not append:
                self.nextPoints = points
            else:
                self.nextPoints += points
        else:  # stop
            self._nextPoint = None
            self.nextPoints = []

    @property
    def speed(self):
        return self._speedAfterBuf

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        """
        自动归一化
        :param value:
        :return:
        """
        n_ = (value[0] ** 2 + value[1] ** 2) ** .5
        if n_ == 0:
            n = 0
        else:
            n = 1 / n_
        value = n * value[0], n * value[1]
        self._direction = value
        self.__refresh_velocity()

    @property
    def loc(self):
        return self.shape.body.position

    @loc.setter
    def loc(self, value):
        self.shape.body.position = value

    @property
    def next_point(self):
        return self._nextPoint

    def release(self):
        pass


class IPhysXInterface:
    def __init__(self):
        self.wordSize = 0, 0
        self.physxSpace: pymunk.Space | None = None
        self.physxTranslation: pymunk.Transform | None = None
        self.staticBodyDict: Dict[int, IStaticBodyInterface] = {}
        self.dynamicBodyDict: Dict[int, IRigidBodyInterface] = {}

        self.shapeFilterDict = {}
        self.navigationMesh2D: NavigationMesh2D | None = None
        self.rvo2System: RVO2 = RVO2()
        self.shouldRebuildStatic = True
        self.shouldRebuildDynamic = False
        self.isOpen = False

    def init(self, world_size, shape_filters):
        self.wordSize = world_size
        self.physxSpace = pymunk.Space()
        self.physxTranslation = pymunk.Transform()
        self.navigationMesh2D = NavigationMesh2D()
        self.shapeFilterDict = {bytes(i[0]): bytes(i[1]) for i in shape_filters}
        # ### init border
        border_radius = 100
        self.physxSpace.add(*[
            pymunk.Poly(self.physxSpace.static_body,
                        [(-border_radius, -border_radius), (world_size[0]+border_radius, -border_radius),
                         (border_radius+world_size[0], 0), (-border_radius, 0)]),
            pymunk.Poly(self.physxSpace.static_body,
                        [(-border_radius, world_size[1]), (world_size[0]+border_radius, world_size[1]),
                         (border_radius+world_size[0], world_size[1]+border_radius),
                         (-border_radius, world_size[1]+border_radius)]),
            pymunk.Poly(self.physxSpace.static_body,
                        [(-border_radius, 0), (0, 0), (0, world_size[1]), (-border_radius, world_size[1])]),
            pymunk.Poly(self.physxSpace.static_body,
                        [(world_size[0], 0), (world_size[0]+border_radius, 0),
                         (border_radius + world_size[0], world_size[1]),
                         (world_size[0], world_size[1])])
            # pymunk.Segment(self.physxSpace.static_body, (-border_radius, -border_radius),
            #                (-border_radius,
            #                 world_size[1] + border_radius), border_radius),
            # pymunk.Segment(self.physxSpace.static_body, (-border_radius, -border_radius),
            #                (world_size[0] + border_radius,
            #                 -border_radius), border_radius),
            # pymunk.Segment(self.physxSpace.static_body,
            #                (world_size[0] + border_radius,
            #                 -border_radius),
            #                (world_size[0] + border_radius,
            #                 world_size[1] + border_radius), border_radius),
            # pymunk.Segment(self.physxSpace.static_body, (-border_radius,
            #                                              world_size[1] + border_radius),
            #                (world_size[0] + border_radius,
            #                 world_size[1] + border_radius), border_radius)
        ])
        self.rvo2System.init()
        self.isOpen = True

    def add_static(self, v: IStaticBodyInterface):
        assert v.id not in self.staticBodyDict
        self.staticBodyDict[v.id] = v
        self.physxSpace.add(v.shape, v.shape.body)
        self.shouldRebuildStatic = True

    def remove_static(self, v: IStaticBodyInterface):
        del self.staticBodyDict[v.id]
        self.physxSpace.remove(v.shape, v.shape.body)
        self.shouldRebuildStatic = True

    def add_dynamic(self, v: IRigidBodyInterface):
        assert v.id not in self.dynamicBodyDict
        self.dynamicBodyDict[v.id] = v
        self.physxSpace.add(v.shape, v.shape.body)
        self.shouldRebuildDynamic = True

    def remove_dynamic(self, v: IRigidBodyInterface):
        del self.dynamicBodyDict[v.id]
        self.physxSpace.remove(v.shape, v.shape.body)
        self.shouldRebuildDynamic = True

    def rebuild(self):
        if not self.shouldRebuildStatic and not self.shouldRebuildDynamic:
            return
        if self.shouldRebuildStatic:
            self.navigationMesh2D = NavigationMesh2D()
            self.navigationMesh2D.init(
                world_size=self.wordSize, obstacles=[
                    [(j[0]+i.shape.body.position.x, j[1]++i.shape.body.position.y) for j in i.shapePoints]
                    for i in self.staticBodyDict.values()])

            self.rvo2System.building_obstacle(
                [([(j[0]+i.shape.body.position.x, j[1]++i.shape.body.position.y) for j in i.shapePoints],
                  i.shape.filter.categories, i.shape.filter.mask) for i in self.staticBodyDict.values()])
            # print('build', [([(j[0]+i.shape.body.position.x, j[1]++i.shape.body.position.y) for j in i.shapePoints],
            #       i.shape.filter.categories, i.shape.filter.mask) for i in self.staticBodyDict.values()])

        if self.shouldRebuildDynamic:
            agent_data = []
            for v in self.dynamicBodyDict.values():
                tmp_agent = AgentNodeStruct()
                tmp_agent.max_neighbors = 10
                tmp_agent.neighbor_dist = v.shape.radius * 3
                tmp_agent.time_horizon = 5.0
                tmp_agent.time_horizon_obst = 5.0
                tmp_agent.radius = v.shape.radius
                tmp_agent.max_speed = v.speed
                goal = v.next_point
                if goal is None:
                    goal = v.loc
                tmp_agent.global_ = Vector2(x=goal[0], y=goal[1])
                position = v.shape.body.position
                tmp_agent.position = Vector2(x=position.x, y=position.y)
                tmp_agent.id_ = v.id
                tmp_agent.category = v.shape.filter.categories
                tmp_agent.category_mask = v.shape.filter.mask
                agent_data.append(tmp_agent)
            self.rvo2System.building_agent(agent_data)
        self.shouldRebuildStatic = False
        self.shouldRebuildDynamic = False

    # 放到后面调用
    def update(self, delta_time):
        if not self.isOpen:
            return
        self.rebuild()
        positions = [tuple(i.loc) for i in self.dynamicBodyDict.values()]
        goals = [tuple(i.next_point) if i.next_point is not None else tuple(i.loc)
                 for i in self.dynamicBodyDict.values()]
        # print(positions, goals)
        self.rvo2System.set_agents_position(positions)
        self.rvo2System.set_agents_global(goals)
        # print('h2', goals)
        self.rvo2System.update(delta_time)
        result = self.rvo2System.get_result()
        # print('h4', result)
        for v1, v in enumerate(self.dynamicBodyDict.values()):
            if v.next_point is not None:
                v.direction = result[v1]
        self.physxSpace.step(delta_time)
