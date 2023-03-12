#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :math_tool.py
# @Time      :18/01/2023
# @Author    :russionbear
# @Function  :function
from queue import PriorityQueue
from typing import List, Any, Dict

import numpy


"""
攻击距离：四边形
移动距离：八边形
"""


class MathTool:
    """
    tip:
      - 小数运算经常出现计算出错的情况，使用==之前应使用round处理;

    带权重的 cost_map: 最大值: 2**16, reference: -1:error, -2:不可停留， -3：运输车
    不带权重的 cost_map: -1 障碍物, 0可行走,
    """
    sqrt2 = 1.414

    @staticmethod
    def get_direction(v1, v2):
        __x = round(v2[0] - v1[0], 3)
        __y = round(v2[1] - v1[1], 3)
        if __x != 0:
            if __x > 0:
                __x = 1
            else:
                __x = -1
        if __y != 0:
            if __y > 0:
                __y = 1
            else:
                __y = -1
        return __x, __y

    # 带weight

    @staticmethod
    def short_road_by_astar(cost_map: numpy.ndarray, start_p, end_p):
        """
        目标点不可达将返回任意road
        start_p can't equal end_p
        :param cost_map: 最大值: 2**16, reference: -1:error, -2:不可停留， -3：运输车
        :param start_p: (x, y)
        :type start_p: Tuple[int,int]
        :param end_p: (x, y)
        :type end_p: Tuple[int,int]
        :return:
        """
        __max_v = 2 ** 16
        __sqrt2 = 2 ** 0.5
        rlt = []
        road_length = 0
        height, width = cost_map.shape
        directions = []
        # ### 以下代码为了实现: “假如end_p在start_p的北，那么方向更新为【北、东北|西北、东|西、东南|西南、南】，先东还是先西不重要”
        __directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        __offset = 0 if end_p[0] == start_p[0] else 1 if end_p[0] > start_p[0] else -1, 0 if end_p[1] == start_p[
            1] else 1 if end_p[1] > start_p[0] else -1

        for i1, i in enumerate(__directions):
            if i == __offset:
                directions.append(i)
                for j in range(1, 4):
                    directions.append(__directions[i1 - j])
                    directions.append(__directions[(i1 + j) % 8])
                directions.append(__directions[i1 - 4])

        frontier = PriorityQueue()
        frontier.put((0, start_p))
        came_from = dict()
        cost_so_far: Dict[Any, Any] = dict()
        came_from[start_p] = None
        cost_so_far[start_p] = 0
        __last_p = -1, 0

        while not frontier.empty():
            current = frontier.get()[1]

            __last_p = current

            if current == end_p:
                break

            for direction in directions:
                new_p = direction[0] + current[0], direction[1] + current[1]
                if new_p[0] < 0 or new_p[0] >= width or new_p[1] < 0 or new_p[1] >= height:
                    continue
                if cost_map[new_p[1], new_p[0]] >= __max_v:
                    continue
                new_cost = cost_so_far[current] + cost_map[new_p[1], new_p[0]] * (
                    1 if abs(direction[0]) + abs(direction[1]) != 2 else __sqrt2)
                if new_p not in cost_so_far or new_cost < cost_so_far[new_p]:
                    cost_so_far[new_p] = new_cost
                    # ((new_p[0] - end_p[0]) ** 2 + (new_p[1] - end_p[1]) ** 2) ** 0.5
                    offset = abs(end_p[0]-new_p[0]), abs(end_p[1]-new_p[1])
                    angle_cost = min(offset) * __sqrt2 + max(offset) - min(offset)
                    priority = new_cost + angle_cost
                    frontier.put((round(priority, 3), new_p))
                    came_from[new_p] = current

        if end_p not in came_from:
            __tmp_v = __last_p
        else:
            # return rlt, road_length
            __tmp_v = end_p
        if __tmp_v == start_p:  # 单位没有移动空间
            return rlt, road_length

        while True:
            road_length += cost_so_far[__tmp_v]

            rlt.append(__tmp_v)
            __tmp_v = came_from[__tmp_v]
            if __tmp_v == start_p:
                rlt.append(__tmp_v)
                break
        rlt.reverse()
        return rlt, road_length * 2 / len(rlt)

    @staticmethod
    def shortest_road_from_move_area(move_area, start_p, end_p):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        now_road: list = [end_p]

        while True:
            x_, y_ = now_road[0]
            now_oil = move_area[(x_, y_)]

            for drt in directions:
                new_x, new_y = drt[0] + x_, drt[1] + y_

                value = move_area.get((new_x, new_y), None)
                if value is None or value <= now_oil:
                    continue
                now_road.insert(0, (new_x, new_y))
                if (new_x, new_y) == start_p:
                    return now_road

    @staticmethod
    def count_move_area(cost_map: numpy.ndarray, start_p, oil):
        map_size = cost_map.shape
        map_size = map_size[1], map_size[0]
        rlt = {}
        directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        # directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        queue: List = [start_p]
        queue_value = {start_p: oil}
        __sqrt2 = 2 ** .5

        while queue:
            x_, y_ = queue.pop(0)
            now_oil = queue_value[(x_, y_)]
            del queue_value[(x_, y_)]

            rlt[(x_, y_)] = now_oil

            for drt in directions:
                new_x = x_ + drt[0]
                new_y = y_ + drt[1]

                if new_x < 0 or new_y < 0 or new_x >= map_size[0] or new_y >= map_size[1]:
                    continue

                rlt_target_oil = rlt.get((new_x, new_y), None)
                target_oil_cost = cost_map[new_y, new_x]
                if abs(drt[0]) + abs(drt[1]) > 1:
                    target_oil_cost *= __sqrt2

                target_q_oil = queue_value.get((new_x, new_y), None)
                new_oil = now_oil - target_oil_cost
                if rlt_target_oil is None and new_oil >= 0:
                    if target_q_oil is None:
                        queue.append((new_x, new_y))
                        queue_value[(new_x, new_y)] = new_oil
                    elif target_q_oil < new_oil:
                        queue_value[(new_x, new_y)] = new_oil

                elif rlt_target_oil is not None and new_oil > rlt_target_oil:
                    if target_q_oil is None:
                        queue.append((new_x, new_y))
                        queue_value[(new_x, new_y)] = new_oil
                    elif target_q_oil < new_oil:
                        queue_value[(new_x, new_y)] = new_oil

        return rlt

    @staticmethod
    def count_all_roads(move_area, start_p, end_p, cost_map, repeat=False):
        """
        比较消耗性能, 即使目标点短
        :param move_area:
        :param start_p:
        :param end_p:
        :param cost_map:
        :param repeat:
        :return:
        """
        oil = move_area[start_p]

        roads: List[list] = []

        directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        # directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        queue = [[end_p, oil]]
        __sqr2 = 2 ** .5

        while queue:
            now_road = queue.pop(0)
            # print('now ', now_road)
            if now_road[-1] < 0:
                continue
            x_, y_ = now_road[0]
            cost_oil = cost_map[y_, x_]

            for drt in directions:
                new_x, new_y = drt[0] + x_, drt[1] + y_

                if (new_x, new_y) not in move_area:
                    continue
                # value = move_area.get((new_x, new_y), None)
                # if value is None:
                #     continue

                if not repeat:
                    try:
                        now_road.index((new_x, new_y))
                        continue
                    except ValueError:
                        pass
                now_cost_oil = cost_oil
                if abs(drt[0]) + abs(drt[1]) > 1:
                    now_cost_oil *= __sqr2
                if now_road[-1] - now_cost_oil < 0:
                    continue

                new_road = now_road[:]
                new_road.insert(0, (new_x, new_y))
                new_road[-1] -= now_cost_oil

                if (new_x, new_y) == start_p:
                    roads.append(new_road[:-1])
                else:
                    queue.append(new_road)

        roads.sort(key=lambda a: len(a))
        return roads

    # @staticmethod
    # def count_all_roads(cost_map: numpy.ndarray, start_p, oil):
    #     map_size = cost_map.shape
    #     map_size = map_size[1], map_size[0]
    #     rlt = {}
    #     directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
    #     # directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    #     queue: List = [start_p]
    #     queue_value = {start_p: oil}
    #     __sqrt2 = 2 ** .5
    #     deep = 0
    #
    #     while queue:
    #         x_, y_ = queue.pop(0)
    #         now_oil = queue_value[(x_, y_)]
    #         del queue_value[(x_, y_)]
    #
    #         rlt[(x_, y_)] = now_oil
    #         deep += 1
    #
    #         for drt in directions:
    #             new_x = x_ + drt[0]
    #             new_y = y_ + drt[1]
    #
    #             if new_x < 0 or new_y < 0 or new_x >= map_size[0] or new_y >= map_size[1]:
    #                 continue
    #
    #             rlt_target_oil = rlt.get((new_x, new_y), None)
    #             target_oil_cost = cost_map[new_y, new_x]
    #             if abs(drt[0]) + abs(drt[1]) > 1:
    #                 target_oil_cost *= __sqrt2
    #
    #             target_q_oil = queue_value.get((new_x, new_y), None)
    #             new_oil = now_oil - target_oil_cost
    #             if rlt_target_oil is None and new_oil >= 0:
    #                 if target_q_oil is None:
    #                     queue.append((new_x, new_y))
    #                     queue_value[(new_x, new_y)] = new_oil
    #                 elif target_q_oil < new_oil:
    #                     queue_value[(new_x, new_y)] = new_oil
    #
    #             elif rlt_target_oil is not None and new_oil > rlt_target_oil:
    #                 if target_q_oil is None:
    #                     queue.append((new_x, new_y))
    #                     queue_value[(new_x, new_y)] = new_oil
    #                 elif target_q_oil < new_oil:
    #                     queue_value[(new_x, new_y)] = new_oil
    #
    #     return rlt

    @staticmethod
    def count_attack_area(width, height, start_p, min_dis, max_dis):
        target_area = set()
        for r in range(min_dis, max_dis+1):
            for x in range(0, max_dis+1):
                y = r - x
                handle_points = []
                if x == 0:
                    handle_points.extend([x, y, x, -y])
                elif y == 0:
                    handle_points.extend([x, y, -x, y])
                else:
                    handle_points.extend([x, y, -x, y, x, -y, -x, -y])
                for i in range(0, len(handle_points), 2):
                    now_x, now_y = handle_points[i] + start_p[0], handle_points[i+1] + start_p[1]
                    if now_x < 0 or now_y < 0 or now_x >= width or now_y >= height:
                        continue
                    target_area.add((now_x, now_y))

        return target_area

    @staticmethod
    def count_move_attack_area(width, height, move_area, min_dis, max_dis):
        rlt = set()
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        def get_border_points(arg_border_ps, arg_in_ps):
            _outer_points = set()
            for _loc in arg_border_ps:
                for _drt in directions:
                    x_1, y_1 = _loc[0] + _drt[0], _loc[1] + _drt[1]
                    if (x_1, y_1) in arg_border_ps or (x_1, y_1) in arg_in_ps:
                        continue
                    if x_1 < 0 or y_1 < 0 or x_1 >= width or y_1 >= height:
                        continue
                    _outer_points.add((x_1, y_1))
            return _outer_points

        border_points = set()
        outer_points = set()

        for loc in move_area.keys():
            for drt in directions:
                x_, y_ = loc[0] + drt[0], loc[1] + drt[1]
                if (x_, y_) in move_area:
                    continue
                if x_ < 0 or y_ < 0 or x_ >= width or y_ >= height:
                    continue
                outer_points.add((x_, y_))
                border_points.add(loc)

        if min_dis <= 1:
            rlt += outer_points

        for i in range(2, max_dis+1):
            tmp_points = get_border_points(outer_points, border_points)
            border_points = outer_points
            outer_points = tmp_points
            if min_dis <= i:
                rlt += tmp_points

        return rlt

    # 不带权重

    @staticmethod
    def short_road_by_astar_nw(cost_map, start_p, end_p, max_deep=1024, can_stop=None):
        """

        :param can_stop:
        :param cost_map: -1 can't move, others can
        :param start_p:
        :param end_p:
        :param max_deep:
        :return:
        """
        # __max_v = 2 ** 16
        print('short_road_by_astar_nw', max_deep, end=', ')
        __sqrt2 = 2 ** 0.5
        rlt = []
        road_length = 0
        height, width = cost_map.shape
        directions = []
        # ### 以下代码为了实现: “假如end_p在start_p的北，那么方向更新为【北、东北|西北、东|西、东南|西南、南】，先东还是先西不重要”
        __directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        __offset = 0 if end_p[0] == start_p[0] else 1 if end_p[0] > start_p[0] else -1, 0 if end_p[1] == start_p[
            1] else 1 if end_p[1] > start_p[0] else -1

        for i1, i in enumerate(__directions):
            if i == __offset:
                directions.append(i)
                for j in range(1, 4):
                    directions.append(__directions[i1 - j])
                    directions.append(__directions[(i1 + j) % 8])
                directions.append(__directions[i1 - 4])

        frontier = PriorityQueue()
        frontier.put((0, start_p))
        came_from = dict()
        cost_so_far: Dict[Any, Any] = dict()
        came_from[start_p] = None
        cost_so_far[start_p] = 0
        __last_p = -1, 0

        while not frontier.empty():
            current = frontier.get()[1]
            __last_p = current
            max_deep -= 1
            if max_deep == 0:
                if can_stop is None:
                    break
                max_deep = can_stop[1](can_stop[0])
                if max_deep == 0:
                    break

            if current == end_p:
                break

            for direction in directions:
                new_p = direction[0] + current[0], direction[1] + current[1]
                if new_p[0] < 0 or new_p[0] >= width or new_p[1] < 0 or new_p[1] >= height:
                    continue
                if cost_map[new_p[1], new_p[0]] == -1:
                    continue
                new_cost = cost_so_far[current] + 1 * (
                    1 if abs(direction[0]) + abs(direction[1]) != 2 else __sqrt2)
                if new_p not in cost_so_far or new_cost < cost_so_far[new_p]:
                    cost_so_far[new_p] = round(new_cost, 3)
                    # ((new_p[0] - end_p[0]) ** 2 + (new_p[1] - end_p[1]) ** 2) ** 0.5

                    offset = abs(end_p[0]-new_p[0]), abs(end_p[1]-new_p[1])
                    angle_cost = min(offset) * __sqrt2 + max(offset) - min(offset)
                    priority = new_cost + angle_cost
                    frontier.put((round(priority, 3), new_p))
                    came_from[new_p] = current

        if end_p not in came_from:
            __tmp_v = __last_p
        else:
            # return rlt, road_length
            __tmp_v = end_p
        if __tmp_v == start_p:  # 单位没有移动空间
            return rlt, road_length

        while True:
            road_length += cost_so_far[__tmp_v]

            rlt.append(__tmp_v)
            __tmp_v = came_from[__tmp_v]
            if __tmp_v == start_p:
                rlt.append(__tmp_v)
                break
        rlt.reverse()
        print(max_deep)
        return rlt, road_length * 2 / len(rlt)

    @staticmethod
    def short_road_by_direction_star_nw(cost_map: numpy.ndarray, start_p, end_p, max_deep=1024, can_stop=None):
        __directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        __direction_index = list(__directions)

        def normalize_vector(v):
            __distance = (v[0]**2+v[1]**2)**.5
            if __distance == 0:
                return 0, 0
            return v[0] / __distance, v[1] / __distance

        current_pos = start_p
        last_pos = current_pos
        height, width = cost_map.shape
        moved_road = {current_pos: None}
        rlt = []

        while True:
            if current_pos == end_p:
                rlt.append(current_pos)
                break
            rlt.append(current_pos)

            max_deep -= 1
            if max_deep == 0:
                if can_stop is None:
                    break
                max_deep = can_stop[1](can_stop[0])
                if max_deep == 0:
                    break

            _target = end_p[0] + (current_pos[0] - last_pos[0]), end_p[1] - (current_pos[1] - last_pos[1])
            __cd1 = normalize_vector((current_pos[0] - last_pos[0], current_pos[1] - last_pos[1]))
            __cd2 = normalize_vector((end_p[0] - current_pos[0], end_p[1] - current_pos[1]))
            __cd3 = round(__cd1[0] + __cd2[0]), round(__cd1[1] + __cd2[1])
            __cd3 = __cd3[0] if abs(__cd3[0]) <= 1 else __cd3[0]//2, __cd3[1] if abs(__cd3[1]) <= 1 else __cd3[1]//2
            if __cd3 == (0, 0):
                break
            current_drt_index = __direction_index.index(__cd3)

            for i in [0, 1, -1, 2, -2]:  # [0, 1, -1, 2, -2, 3, -3, 4]
                __c_drt = __directions[(current_drt_index+i+8) % 8]
                x_, y_ = current_pos[0] + __c_drt[0], current_pos[1] + __c_drt[1]

                if x_ < 0 or y_ < 0 or x_ >= width or y_ >= height or cost_map[y_, x_] == -1 or \
                        (x_, y_) in moved_road:
                    continue
                moved_road[(x_, y_)] = current_pos
                last_pos = current_pos
                current_pos = (x_, y_)
                if (2, 2) == (x_, y_):
                    pass
                break
            else:
                break

        return rlt

    @staticmethod
    def wavefront(cost_map: numpy.ndarray | Any, start_ps: dict, max_deep=1024, can_stop=None):
        print('wavefront', max_deep, end=', ')
        ladder_nu_dict = {}
        for k, v in start_ps.items():
            ladder_nu_dict[v] = ladder_nu_dict.get(v, 0)

        map_size = cost_map.shape
        map_size = map_size[1], map_size[0]
        directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        # directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        queue: List = list(start_ps.keys())
        queue_value = start_ps
        # __sqrt2 = 2 ** .5
        __sqrt2 = MathTool.sqrt2

        while queue:
            x_, y_ = queue.pop(0)
            now_oil = queue_value[(x_, y_)]
            del queue_value[(x_, y_)]
            ladder_nu_dict[now_oil] = ladder_nu_dict.get(now_oil, 0) + 1

            # print('old', (x_, y_), cost_map[y_, x_])
            cost_map[y_, x_] = round(now_oil, 3)
            # print(y_, x_, now_oil)

            max_deep -= 1
            if max_deep == 0:
                if can_stop is None:
                    break
                max_deep = can_stop[1](can_stop[0])
                if max_deep == 0:
                    break

            for drt in directions:
                new_x = x_ + drt[0]
                new_y = y_ + drt[1]

                if new_x < 0 or new_y < 0 or new_x >= map_size[0] or new_y >= map_size[1]:
                    continue
                target_oil = cost_map[new_y, new_x]
                if target_oil != 0:
                    continue

                if abs(drt[0]) + abs(drt[1]) > 1:
                    new_target_oil = now_oil + __sqrt2
                else:
                    new_target_oil = now_oil + 1

                cache_target_oil = queue_value.get((new_x, new_y), None)
                if cache_target_oil is None:
                    queue.append((new_x, new_y))
                    queue_value[(new_x, new_y)] = new_target_oil
                    # print((x_, y_), (new_x, new_y), now_oil, new_target_oil, cost_map[y_, x_], cost_map[new_y, new_x])
                elif cache_target_oil > new_target_oil:
                    queue_value[(new_x, new_y)] = new_target_oil

        print(max_deep)
        return cost_map, ladder_nu_dict

    @staticmethod
    def short_road_to_gff_by_astar(cost_map, flow_field, start_p, end_p, max_deep=1024, can_stop=None):
        # __max_v = 2 ** 16
        __sqrt2 = 2 ** 0.5
        rlt = []
        road_length = 0
        height, width = cost_map.shape
        directions = []
        # ### 以下代码为了实现: “假如end_p在start_p的北，那么方向更新为【北、东北|西北、东|西、东南|西南、南】，先东还是先西不重要”
        __directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        __offset = 0 if end_p[0] == start_p[0] else 1 if end_p[0] > start_p[0] else -1, 0 if end_p[1] == start_p[
            1] else 1 if end_p[1] > start_p[0] else -1

        for i1, i in enumerate(__directions):
            if i == __offset:
                directions.append(i)
                for j in range(1, 4):
                    directions.append(__directions[i1 - j])
                    directions.append(__directions[(i1 + j) % 8])
                directions.append(__directions[i1 - 4])

        frontier = PriorityQueue()
        frontier.put((0, start_p))
        came_from = dict()
        cost_so_far: Dict[Any, Any] = dict()
        came_from[start_p] = None
        cost_so_far[start_p] = 0
        __last_p = -1, 0

        while not frontier.empty():
            current = frontier.get()[1]

            __last_p = current
            if flow_field[current[1], current[0]] > 0:
                end_p = current
                break
            max_deep -= 1
            if max_deep == 0:
                if can_stop is None:
                    break
                max_deep = can_stop[1](can_stop[0])
                if max_deep == 0:
                    break

            # if current == end_p:
            #     break

            for direction in directions:
                new_p = direction[0] + current[0], direction[1] + current[1]
                if new_p[0] < 0 or new_p[0] >= width or new_p[1] < 0 or new_p[1] >= height:
                    continue
                if cost_map[new_p[1], new_p[0]] == -1:
                    continue
                new_cost = round(cost_so_far[current] + 1 * (
                    1 if abs(direction[0]) + abs(direction[1]) != 2 else __sqrt2))
                if new_p not in cost_so_far or new_cost < cost_so_far[new_p]:
                    cost_so_far[new_p] = new_cost
                    # ((new_p[0] - end_p[0]) ** 2 + (new_p[1] - end_p[1]) ** 2) ** 0.5
                    # priority = new_cost + \
                    #     min((new_p[0] - end_p[0]), (new_p[1] - end_p[1])) * __sqrt2 + \
                    #     abs((new_p[0] - end_p[0]) - (new_p[1] - end_p[1]))
                    # frontier.put((priority, new_p))
                    offset = abs(end_p[0]-new_p[0]), abs(end_p[1]-new_p[1])
                    angle_cost = min(offset) * __sqrt2 + max(offset) - min(offset)
                    priority = new_cost + angle_cost
                    frontier.put((round(priority, 3), new_p))
                    came_from[new_p] = current

        if end_p not in came_from:
            __tmp_v = __last_p
        else:
            return rlt, road_length
        __tmp_v = __last_p
        if __tmp_v == start_p:  # 单位没有移动空间
            return rlt, road_length

        while True:
            road_length += cost_so_far[__tmp_v]

            rlt.append(__tmp_v)
            __tmp_v = came_from[__tmp_v]
            if __tmp_v == start_p:
                rlt.append(__tmp_v)
                break
        rlt.reverse()
        return rlt, road_length * 2 / len(rlt)

    @staticmethod
    def short_road_to_gff_by_direction_star(cost_map, flow_field, start_p, end_p, max_deep=1024, can_stop=None):
        __directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        __direction_index = list(__directions)

        def normalize_vector(v):
            __distance = (v[0] ** 2 + v[1] ** 2) ** .5
            if __distance == 0:
                return 0, 0
            return v[0] / __distance, v[1] / __distance

        current_pos = start_p
        last_pos = current_pos
        height, width = cost_map.shape
        moved_road = {current_pos: None}
        rlt = []

        while True:
            if flow_field[current_pos[1], current_pos[0]] > 0:
                rlt.append(current_pos)
                break
            rlt.append(current_pos)

            max_deep -= 1
            if max_deep == 0:
                if can_stop is None:
                    break
                max_deep = can_stop[1](can_stop[0])
                if max_deep == 0:
                    break

            _target = end_p[0] + (current_pos[0] - last_pos[0]), end_p[1] - (current_pos[1] - last_pos[1])
            __cd1 = normalize_vector((current_pos[0] - last_pos[0], current_pos[1] - last_pos[1]))
            __cd2 = normalize_vector((end_p[0] - current_pos[0], end_p[1] - current_pos[1]))
            __cd3 = round(__cd1[0] + __cd2[0]), round(__cd1[1] + __cd2[1])
            __cd3 = __cd3[0] if abs(__cd3[0]) <= 1 else __cd3[0] // 2, __cd3[1] if abs(__cd3[1]) <= 1 else __cd3[1] // 2
            if __cd3 == (0, 0):
                break
            current_drt_index = __direction_index.index(__cd3)

            for i in [0, 1, -1, 2, -2]:  # [0, 1, -1, 2, -2, 3, -3, 4]
                __c_drt = __directions[(current_drt_index + i + 8) % 8]
                x_, y_ = current_pos[0] + __c_drt[0], current_pos[1] + __c_drt[1]

                if x_ < 0 or y_ < 0 or x_ >= width or y_ >= height or cost_map[y_, x_] == -1 or \
                        (x_, y_) in moved_road:
                    continue
                moved_road[(x_, y_)] = current_pos
                last_pos = current_pos
                current_pos = (x_, y_)
                if (2, 2) == (x_, y_):
                    pass
                break
            else:
                break

        return rlt


if __name__ == '__main__':
    __cost_map = numpy.zeros((16, 16), dtype=numpy.int_)
    for __i in range(16):
        __cost_map[3, __i] = -1
    print(MathTool.short_road_by_direction_star_nw(__cost_map, (0, 0), (0, 10)))
