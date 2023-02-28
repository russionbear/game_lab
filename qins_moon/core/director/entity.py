#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :entity.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function

from qins_moon.core.utils.data_structure import BisectList
from qins_moon.core.utils.data_structure import RegistryBase


class EntityBase:
    def __init__(self):
        # 　＃　这个id跟unity ecs 框架中的不同，可以随意设置
        #  # note：如果该id与其所有兄弟的id都相同且它有很多兄弟，那BisectList 就不快了，最好避免一下，给他赋个随机数什么的
        self.id = 0
        self._parent: 'EntityBase' | None = None
        self._children = BisectList[EntityBase](key=lambda a: a.id)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    # ############################ children
    def contains(self, e: 'EntityBase'):
        return e in self._children

    def add_child(self, *e: 'EntityBase'):
        """
        不要添加重复的 元素，否则会渲染两遍
        :param e:
        :return:
        """

        for i in e:
            if i.parent is not None:
                i.parent.remove_child(i)
            i.parent = self
            self._children.append(i)

    def remove_child(self, e: 'EntityBase'):
        self._children.remove(e)

    def find_child_by_id(self, id_):
        return self._children.find(id_)

    def update(self, delta_time):
        for i in self._children:
            i.update(delta_time)


class RootEntityBase(EntityBase):
    def event(self, e0):
        pass


class RootEntityManager(RegistryBase[RootEntityBase]):
    _instance = None

    def __init__(self):
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self
        super().__init__()
        self.currentRootEntity: RootEntityBase | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)

    def switch_root_entity(self, key):
        """

        :param key: 允许不存在的key，
        :return:
        """
        self.currentRootEntity = self[key]
