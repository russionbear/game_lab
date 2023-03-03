#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :grid_map.py
# @Time      :07/02/2023
# @Author    :russionbear
# @Function  :function
from typing import Dict, Tuple, List, Any
import numpy


class IGridMovementInterface:
    """
    都是像素坐标
    """
    def __init__(self, loc, base_speed):
        super().__init__()
        self._loc: tuple = loc

        self._speedBuf: Dict[str, float] = {}
        self._baseSpeed = base_speed
        self._speedAfterBuf = base_speed
        self._direction = 0, 0

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

    @property
    def loc(self):
        return self._loc

    @loc.setter
    def loc(self, value):
        self._loc = value

    def update(self, delta_time):
        direction = self.direction
        if direction == (0, 0):
            return
        self._loc = self._loc[0] + direction[0] * self._speedAfterBuf * delta_time, \
            self._loc[1] + direction[1] * self._speedAfterBuf * delta_time


class IGridNavigationInterface:
    """
    此grid nav component 定义的世界不允许任意物体穿透, 即同图层不允许覆盖;
    """

    def __init__(self, size, layers):
        self._size = size
        # ####### _geoMap 必须再init里初始化，之后不可setter操作该属性
        self._layerMapDict: Dict[int, numpy.ndarray] = {i: numpy.zeros((size[1], size[0])) for i in layers}
        # ########################### engineId, (nd, [(layer, value mapper: function)])
        self._engineMapper: Dict[str, Tuple[numpy.ndarray, List[Tuple[int, Any]]]] = {}

    def size(self) -> tuple:
        return self._size

    def get_layer_map(self, layer) -> numpy.ndarray:
        return self._layerMapDict[layer]

    def add_engine_mapper(self, name, mapper, t=numpy.int_):
        """
        相同的name会覆盖
        :param t:
        :param name:
        :param mapper:
        :return:
        """
        self._engineMapper[name] = (numpy.zeros(tuple(reversed(self.size())), t), mapper)

    def get_engine_move_map(self, engine) -> numpy.ndarray:
        return self._engineMapper[engine][0]

    def refresh_node(self, loc, value, layer=1):
        self._layerMapDict[layer][loc[1], loc[0]] = value
        # self._geoMap[loc[1], loc[0]] = value
        for k, v in self._engineMapper.items():
            # v[0][loc[1], loc[0]] = v[1][value]
            for (l, m) in v[1]:
                tmp_v = self._layerMapDict[l][loc[1], loc[0]]
                if tmp_v == 0:
                    continue
                tmp_v2 = m(tmp_v)
                if tmp_v2 == 0:
                    continue
                v[0][loc[1], loc[0]] = tmp_v2


class IGridMoveControllerInterface:
    def __init__(self, movement, block_size):
        self.movement: IGridMovementInterface = movement
        self.blockSize = block_size
        self._nextPoint = None
        self._gridLoc = 0, 0
        self._lastGridLoc = 0, 0

        # alloc next point
        self.gridNavigation: IGridNavigationInterface | None = None
        self._unitLayerAndValue = 0, 0
        self._moveEngine = 0

        # #  #  下面的两个方法可能会更新road，realize it when call them
        # self._allocNextPointEvent = None
        self._taskFinishedEvent = None
        self._nextPointAllocatedEvent = None  # o_d, n_d

        self._sleepTime = 0  # -1表示无任务, 0通过, > 0 等待

    def open_alloc_next_point(self, grid_nav, layer_and_value, engine):
        self.gridNavigation = grid_nav
        self._unitLayerAndValue = layer_and_value
        self._moveEngine = engine

    # 关于事件

    def sub_next_point_allocated(self, v):
        self._nextPointAllocatedEvent = v

    def sub_task_finished(self, v):
        """
        订阅任务完成，
        :param v: void (*) (**kwargs)
        :return:
        """
        self._taskFinishedEvent = v

    def _alloc_next_point(self, p, **kwargs):
        # """
        #
        # :param p: 可以为数组，但 _allocNextPointEvent为None时只会看第一个值
        # :return: 取反合格的第一个值，没有则返回None
        # """
        #
        # if not self._allocNextPointEvent:
        #     if type(p) == list:
        #         p = p[0]
        #     self._set_next_grid_point(p)
        #     return p
        #
        # if type(p) == list:
        #     for i in p:
        #         if self._allocNextPointEvent(i, **kwargs):
        #             self._set_next_grid_point(i)
        #             return i
        # else:
        #     if self._allocNextPointEvent(p, **kwargs):
        #         self._set_next_grid_point(p)
        #         return p
        if p == self._gridLoc:
            return p
        old_grid_loc = self._gridLoc
        if self.gridNavigation:
            layer_map = self.gridNavigation.get_layer_map(self._unitLayerAndValue[0])
            if layer_map[p[1], p[0]] != 0:
                return None
            loc = self._gridLoc
            layer_map[loc[1], loc[0]] = 0
            layer_map[p[1], p[0]] = self._unitLayerAndValue[1]
            # print(loc, 'to', p, self._unitLayerAndValue[1], layer_map[p[1], [0]])
        self._set_next_grid_point(p)
        if self._nextPointAllocatedEvent is not None:
            self._nextPointAllocatedEvent(old_grid_loc, p)
        return p

    def _pub_task_finished(self, **kwargs):
        self._sleepTime = -1
        if self._taskFinishedEvent is not None:
            self._taskFinishedEvent(**kwargs)

    # sleep

    def sleep(self, t):
        """
        由外部调用，而非self或super
        :param t:
        :return:
        """
        self._sleepTime = t

    # 关于基础属性

    @property
    def forward(self):
        return self._gridLoc[0] - self._lastGridLoc[0], self._gridLoc[1] - self._lastGridLoc[1]

    @property
    def last_grid_loc(self):
        return self._lastGridLoc

    def next_grid_point(self):
        return self._nextPoint[0] // self.blockSize[0], self._nextPoint[1] // self.blockSize[1]

    def _set_next_grid_point(self, value):
        """
        value is not None => 自动更新_lastGridLoc 和 _gridLoc
        :param value:
        :return:
        """
        if value is not None:
            self._lastGridLoc = self._gridLoc
            self._gridLoc = value
            value = value[0] * self.blockSize[0] + self.blockSize[0]//2, \
                value[1] * self.blockSize[1] + self.blockSize[1]//2
        self._nextPoint = value

    def grid_loc(self):
        return self._gridLoc

    def set_grid_loc(self, value):
        """
        由外部调用，强制更改坐标并中断所有任务
        :param value:
        :return:
        """
        # self._set_next_grid_point(value)
        self._lastGridLoc = value
        self._gridLoc = value
        self.movement.loc = value[0] * self.blockSize[0] + self.blockSize[0]//2, \
            value[1] * self.blockSize[1] + self.blockSize[1]//2

    # 移动更新

    def _update_next_point(self, delta_time) -> int:
        """

        :param delta_time:
        :return: is next point arrived, 0 arrived, 1 moving, 2, no next point
        """
        next_p = self._nextPoint
        if next_p is None:
            return 2

        loc = self.movement.loc
        offset = next_p[0] - loc[0], next_p[1] - loc[1]

        distance = (offset[0] ** 2 + offset[1] ** 2) ** .5
        if distance <= self.movement.speed * delta_time:  # 到达 nextPoint
            # n剑客，不可分割
            self._set_next_grid_point(None)
            self.movement.direction = 0, 0
            self.movement.loc = next_p
            return 0
        else:
            self.movement.direction = offset
            return 1

    def update(self, delta_time):
        if self._sleepTime < 0:
            return False
        elif self._sleepTime > 0:
            self._sleepTime -= delta_time
            if self._sleepTime < 0:
                self._sleepTime = 0
            return False
