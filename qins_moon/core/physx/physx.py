#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :physx.py
# @Time      :10/02/2023
# @Author    :russionbear
# @Function  :function

from qins_moon.core.interface.physx import IRigidBodyInterface, IPhysXInterface, IStaticBodyInterface


class StaticBodyBase(IStaticBodyInterface):
    pass


class RigidBodyBase(IRigidBodyInterface):
    def __init__(self, id_, base_speed, radius, loc, category):
        super().__init__(id_, base_speed, radius, loc, category)
        self._nextTarget = None

    def set_target(self, target):
        nav = PhysX().navigationMesh2D
        points = nav.short_road(self.loc, target, self.shape.radius)
        # print(points)
        self.set_next_points(points)


class PhysX(IPhysXInterface):
    _instance = None

    def __init__(self):
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self
        super().__init__()

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)
