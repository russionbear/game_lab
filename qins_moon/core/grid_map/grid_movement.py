#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :grid_movement.py
# @Time      :07/02/2023
# @Author    :russionbear
# @Function  :function
from typing import Dict

from qins_moon.core.interface.grid_map import IGridMovementInterface, IGridNavigationInterface


class GridMovement(IGridMovementInterface):
    """

    """

    def __init__(self, loc, base_speed):
        super().__init__(loc, base_speed)
        self.gridNavComponent: IGridNavigationInterface | None = None
        self._speedDict: Dict[int, float] = {}
        self._mapBlockSize = 0, 0
        self.loc = loc
        self._lastTerrainId = 0
        self._engineId = 0

    def open_terrain_affect_speed(self, speed_dict: dict, engine, grid_nav, block_size):
        self.gridNavComponent: IGridNavigationInterface = grid_nav
        self._speedDict: Dict[int, float] = speed_dict
        self._engineId = engine
        self._speedDict = speed_dict
        self._mapBlockSize = block_size

    def close_terrain_affect_speed(self):
        self.gridNavComponent = None

    def update(self, delta_time):
        # 更新terrain对速度的影响
        if self.gridNavComponent is not None:
            x, y = self._loc[0] // self._mapBlockSize[0], self.loc[1] // self._mapBlockSize[1]
            x, y = int(x), int(y)
            cost_map = self.gridNavComponent.get_engine_move_map(self._engineId)
            current_terrain = cost_map[y, x]
            if current_terrain != self._lastTerrainId:
                self.add_speed_buf('terrain', self._speedDict.get(current_terrain, 1))
                self._lastTerrainId = current_terrain
        super().update(delta_time)
