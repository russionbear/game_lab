#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :unit_loop.py
# @Time      :02/02/2023
# @Author    :russionbear
# @Function  :function
import numpy


class UnitLoop:
    def __init__(self, loop_map: numpy.ndarray, units_loc, coastlines):
        """

        :param loop_map: 0 sea can't move, < 16 land can move, > 2**16 can't move, others unit can't move
        :param units_loc:
        """
        self.unitLoopMap = loop_map.copy()
        # self.unitLoopMap[self.unitLoopMap > 16] =
        height, width = loop_map.shape
        # directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        # for i in units_loc:
        #     count = 0
        #     for drt in directions:
        #         x_, y_ = i[0] + drt[0], i[1] + drt[1]
        #         if x_ < 0 or y_ < 0 or x_ >= width or y_ >= height:
        #             count += 1
        #             continue
        #         v = loop_map[y_, x_]
        #         if v < 0


if __name__ == "__main__":
    run_code = 0
