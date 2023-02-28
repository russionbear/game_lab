#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :navigation_mesh_2d.py
# @Time      :11/02/2023
# @Author    :russionbear
# @Function  :function
from queue import PriorityQueue

import kdtree

import numpy
from typing import Dict, Tuple, List, Any

import pygame


class NavigationMesh2D:
    def __init__(self):
        self.worldSize = 0, 0
        self.obstacles = []

        self.points = []
        self.lines = []
        self.angels = []

        self.pointToLineDict = {}
        self.lineToAngleDict = {}
        self.lineToLineIdDict = {}
        self.pointToAngleDict = {}
        self.midpointToAngleDict = {}
        self.kdTree: kdtree.KDNode | None = None

    def init(self, world_size, obstacles: List[List[Tuple]]):
        """
        不支持"多边形切成三角形中的嵌套"， 太复杂了懒得实现
        :param world_size:
        :param obstacles: 障碍物之间不能重叠，最好留一点点空隙, 障碍物也不能与边界重叠
        :return:
        """
        # print(world_size, obstacles)
        self.worldSize = world_size
        self.obstacles = obstacles

        outer_points = [(0, 0), (0, world_size[1]), world_size, (world_size[0], 0)]
        assert not NavigationMesh2D.is_clockwise(outer_points)
        outer_lines = [(outer_points[i - 1], outer_points[i]) for i in range(len(outer_points))]
        all_inner_lines = []
        for i in obstacles:
            all_inner_lines += [(i[j-1], i[j]) for j in range(len(i))]
        for inner_points in obstacles:
            if not NavigationMesh2D.is_clockwise(inner_points):
                inner_points = inner_points[::-1]
            # inner_lines = [(inner_points[i - 1], inner_points[i]) for i in range(len(inner_points))]
            # # print(inner_lines, outer_lines)
            join_line, outer_index, inner_index = NavigationMesh2D.find_obstacle_line(outer_points, inner_points, all_inner_lines)
            new_points = inner_points[inner_index:] + inner_points[:inner_index]
            new_points.append(new_points[0])

            outer_points = outer_points[:outer_index + 1] + new_points + outer_points[outer_index:]
            outer_lines = [(outer_points[i - 1], outer_points[i]) for i in range(len(outer_points))]
            # print(new_points, outer_points)
            # print('111')
        self.points = outer_points
        self.lines = outer_lines
        # print(outer_points)
        if NavigationMesh2D.is_clockwise(outer_points):
            outer_points = outer_points[::-1]
        else:
            outer_points = outer_points[:]
        # print(outer_points)
        assert not NavigationMesh2D.is_clockwise(outer_points)

        deep = 0
        while outer_points:
            angle = NavigationMesh2D.get_ear(outer_points)
            if angle is not None:
                self.lines.append((angle[0], angle[2]))
                self.angels.append(angle)
                # print(outer_points, self.lines[-1], angle[1])
                deep = 0
            else:
                deep += 1
                outer_points.append(outer_points.pop(0))
                if deep > len(outer_points):
                    break
                print(outer_points)
                print('angle is None', not NavigationMesh2D.is_clockwise(outer_points))

        tmp_lines = []
        for i in self.angels:
            for j in range(3):
                t0 = i[j-1], i[j]
                if t0[0] > t0[1]:
                    t0 = t0[1], t0[0]
                tmp_lines.append(t0)

        self.lines = list(set(tmp_lines))
        for i1, i in enumerate(self.lines):
            self.lineToLineIdDict[i1] = i
            for j in i:
                l0 = self.pointToLineDict.get(j, None)
                if l0 is None:
                    l0 = set()
                    self.pointToLineDict[j] = l0
                l0.add(i1)

        for i1, i in enumerate(self.angels):
            center_pos = sum([j[0] for j in i]) / len(i), sum([j[1] for j in i]) / len(i)
            self.midpointToAngleDict[center_pos] = i1
            for j in i:
                l0 = self.pointToAngleDict.get(j, None)
                if l0 is None:
                    l0 = set()
                    self.pointToAngleDict[j] = l0
                l0.add(i1)
            for j in range(3):
                current_line = i[j-1], i[j]
                if current_line[0] > current_line[1]:
                    current_line = current_line[1], current_line[0]
                l0 = self.lineToAngleDict.get(current_line, None)
                if l0 is None:
                    l0 = set()
                    self.lineToAngleDict[current_line] = l0
                l0.add(i1)

        self.kdTree = kdtree.create(list(self.midpointToAngleDict.keys()))

    def get_triangle(self, pos):
        """
        该点需要为与可行走区域内
        :param pos:
        :return:
        """
        nb = self.kdTree.search_nn(pos)  # 肯定不为None
        angle_id = self.midpointToAngleDict[nb[0].data]
        angle = self.angels[angle_id]
        current_line = pos, nb[0].data
        for i in range(3):
            a_line = angle[i-1], angle[i]
            if NavigationMesh2D.is_lines_cross(current_line, a_line) > 1:
                if a_line[0] > a_line[1]:
                    a_line = a_line[1], a_line[0]
                angles = self.lineToAngleDict[a_line]
                if len(angles) == 1:
                    return None
                else:
                    for j in angles:
                        if j == angle_id:
                            continue
                        return j
        else:
            return angle_id

    @staticmethod
    def distance_dot_to_line(point, line):
        A = line[1][1] - line[0][1]
        B = line[0][0] - line[1][0]
        C = (line[0][1] - line[1][1]) * line[0][0] + \
            (line[1][0] - line[0][0]) * line[0][1]
        # 根据点到直线的距离公式计算距离
        distance = numpy.abs(A * point[0] + B * point[1] + C) / (numpy.sqrt(A ** 2 + B ** 2))
        return distance

    @staticmethod
    def get_line_length(p1, p2):
        return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**.5

    @staticmethod
    def is_lines_cross(line1, line2):
        """
        0 无交点（1端点相交）
        2 相交
        端点相交或者在同一条直线上都返回False
        cross(a-d,c-d)*cross(b-d,c-d)>0||cross(c-b,a-b)*cross(d-b,a-b)>0) return true;
        :param line1:
        :param line2:
        :return:
        """
        v1 = numpy.cross((line1[0][1] - line2[1][1], line1[0][0] - line2[1][0]),
                         (line2[0][1] - line2[1][1], line2[0][0] - line2[1][0])) * \
             numpy.cross((line1[1][1] - line2[1][1], line1[1][0] - line2[1][0]),
                         (line2[0][1] - line2[1][1], line2[0][0] - line2[1][0]))
        # print(v1, 'v1')
        if v1 > 0:
            return 0
        v2 = numpy.cross((line1[0][1] - line1[1][1], line1[0][0] - line1[1][0]),
                         (line2[0][1] - line1[1][1], line2[0][0] - line1[1][0])) * \
             numpy.cross((line1[0][1] - line1[1][1], line1[0][0] - line1[1][0]),
                         (line2[1][1] - line1[1][1], line2[1][0] - line1[1][0]))
        # print(v2, 'v2')
        if v2 > 0:
            return 0
        if v1 == v2 == 0:
            return 1
        return 2

    @staticmethod
    def find_obstacle_line(outer_points, inner_points, all_inner_lines):
        # print(outer_points, 'p')
        outer_lines = [(outer_points[i - 1], outer_points[i]) for i in range(len(outer_points))]
        # inner_lines = [(inner_points[i - 1], inner_points[i]) for i in range(len(inner_points))]
        for inner_index, inner_point in enumerate(inner_points):
            for outer_index, outer_point in enumerate(outer_points):
                current_line = outer_point, inner_point
                should_pass = False
                for inner_line in all_inner_lines:
                    if NavigationMesh2D.is_lines_cross(current_line, inner_line) > 1:
                        should_pass = True
                        break
                if should_pass:
                    continue
                for outer_line in outer_lines:
                    if NavigationMesh2D.is_lines_cross(current_line, outer_line) > 1:
                        should_pass = True
                        break
                if not should_pass:
                    return current_line, outer_index, inner_index

    @staticmethod
    def is_convex(a, b, c):
        # only convex if traversing anti-clockwise!
        a = tuple(reversed(a))
        b = tuple(reversed(b))
        c = tuple(reversed(c))
        cross_p = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if cross_p >= 0:
            return True
        return False

    @staticmethod
    def in_triangle(a, b, c, p):

        a = tuple(reversed(a))
        b = tuple(reversed(b))
        c = tuple(reversed(c))
        p = tuple(reversed(p))
        L = [0, 0, 0]
        eps = 0.0000001
        # calculate barycentric coefficients for point p
        # eps is needed as error correction since for very small distances denom->0
        L[0] = ((b[1] - c[1]) * (p[0] - c[0]) + (c[0] - b[0]) * (p[1] - c[1])) / \
               (((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])) + eps)
        L[1] = ((c[1] - a[1]) * (p[0] - c[0]) + (a[0] - c[0]) * (p[1] - c[1])) / \
               (((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])) + eps)
        L[2] = 1 - L[0] - L[1]
        # check if p lies in triangle (a, b, c)
        for x in L:
            if x > 1 or x < 0:
                return False
        return True

    @staticmethod
    def dot_in_line(dot, ep1, ep2):
        k, b = NavigationMesh2D.dot_mode_equation(ep1, ep2)
        if min(ep1[1], ep2[1]) <= (dot[0]*k+b) <= max(ep1[1], ep2[1]):
            return True
        return False

    @staticmethod
    def is_clockwise(poly):
        poly = [tuple(reversed(i)) for i in poly]
        # initialize sum with last element
        sum_ = (poly[0][0] - poly[len(poly) - 1][0]) * (poly[0][1] + poly[len(poly) - 1][1])
        # iterate over all other elements (0 to n-1)
        for i in range(len(poly) - 1):
            sum_ += (poly[i + 1][0] - poly[i][0]) * (poly[i + 1][1] + poly[i][1])
        if sum_ > 0:
            return True
        return False

    @staticmethod
    def get_ear(poly):
        size = len(poly)
        if size < 3:
            poly.clear()
        if size == 3:
            tri = tuple(poly)
            poly.clear()
            return tri
        for i in range(size):
            p1 = poly[i - 1]
            p2 = poly[i]
            p3 = poly[(i + 1) % size]
            # if p1 in point_to_obstacle_dict and p3 in point_to_obstacle_dict and\
            #         point_to_obstacle_dict[p1] == point_to_obstacle_dict[p3]:
            #     continue

            if NavigationMesh2D.is_convex(p1, p2, p3):
                for x in poly:
                    if x in (p1, p2, p3):
                        continue
                    if NavigationMesh2D.in_triangle(p1, p2, p3, x):
                        break
                else:
                    del poly[i % size]
                    return p1, p2, p3

    @staticmethod
    def dot_mode_equation(p1, p2):
        if (p2[0] - p1[0]) == 0:
            k = 1
            print('/zero', p1, p2)
        else:
            k = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = p2[1] - k * p2[0]
        return k, b

    @staticmethod
    def dot_from_cross_lines(line1, line2):
        k1, b1 = NavigationMesh2D.dot_mode_equation(*line1)
        k2, b2 = NavigationMesh2D.dot_mode_equation(*line2)
        if k1 == k2:
            if NavigationMesh2D.get_line_length(line1[0], line2[1]) < NavigationMesh2D.get_line_length(line1[1], line2[1]):
                return line1[0]
            return line1[1]
        x = (b2-b1) / (k1-k2)
        y = k1 * x + b1
        return x, y

    @staticmethod
    def is_side_in_triangle_small(side, triangle, unit_r):
        side = min(side), max(side)
        s1 = triangle[0], triangle[1]
        s2 = triangle[1], triangle[2]
        s3 = triangle[2], triangle[-1]
        s1 = min(s1), max(s1)
        s2 = min(s2), max(s2)
        s3 = min(s3), max(s3)
        max_s = max([s1, s2, s3], key=lambda arg: NavigationMesh2D.get_line_length(*arg))
        max_s = min(max_s), max(max_s)
        if max_s == side:
            return False
        if max_s[0] == side[0] or max_s[0] == side[1]:
            same_p = max_s[0]
        else:
            same_p = max_s[1]
        if side[0] == same_p:
            diff_p = side[1]
        else:
            diff_p = side[0]
        return NavigationMesh2D.distance_dot_to_line(diff_p, max_s) < unit_r

    def short_road_by_a_star(self, start_p, end_p, unit_r):
        __sqrt2 = 2 ** 0.5
        rlt = []
        road_length = 0
        start_i = self.get_triangle(start_p)
        end_i = self.get_triangle(end_p)
        # print('start_p', self.angels[start_i])
        if start_i is None or end_i is None:
            return rlt, road_length
        if start_i == end_i:
            # rlt.append(start_p)
            # # rlt.append(end_p)
            # road_length = NavigationMesh2D.get_line_length(start_p, end_p)
            return rlt, road_length

        frontier = PriorityQueue()
        came_from = dict()
        cost_so_far: Dict[Any, Any] = dict()
        # came_from[start_i] = None
        # cost_so_far[start_i] = 0
        __last_line = None
        __first_points = self.angels[start_i]
        for i in range(3):
            current_line = __first_points[i-1], __first_points[i]
            if current_line[0] > current_line[1]:
                current_line = current_line[1], current_line[0]
            # line_id = self.lineToLineIdDict[current_line]
            angle_ids = self.lineToAngleDict[current_line]
            if len(angle_ids) == 1:  # 防止撞墙
                continue
            new_angle_id = -1
            for j in angle_ids:
                if j == start_i:
                    continue
                new_angle_id = j
                break

            line_length = NavigationMesh2D.get_line_length(*current_line)
            if line_length < unit_r * 2 + 1:
                continue

            line_center_p = (current_line[0][0] + current_line[1][0])/2, (current_line[0][1] + current_line[1][1])/2
            came_from[current_line] = None
            cost_so_far[current_line] = NavigationMesh2D.get_line_length(start_p, line_center_p)
            pre_distance = NavigationMesh2D.get_line_length(end_p, line_center_p)
            frontier.put(
                (cost_so_far[current_line]+pre_distance, cost_so_far[current_line], new_angle_id, current_line)
            )

        while not frontier.empty():
            current_cost, angle_id, current_line = frontier.get()[1:]
            # print('out', current_line)
            if current_line == ((2, 1), (3, 0)):
                pass
            if current_cost < cost_so_far[current_line]:  # ### 全局改进，改进！！！！！
                # print("passed")
                continue

            __last_line = current_line
            current_line_center_p = (current_line[0][0] + current_line[1][0]) / 2, (
                    current_line[0][1] + current_line[1][1]) / 2
            if angle_id == end_i:
                road_length += NavigationMesh2D.get_line_length(end_p, current_line_center_p)
                break
            print(angle_id, end_i)
            current_angle = self.angels[angle_id]

            if NavigationMesh2D.is_side_in_triangle_small(current_line, current_angle, unit_r):
                continue

            for i in range(3):
                new_line = current_angle[i-1], current_angle[i]

                line_length = NavigationMesh2D.get_line_length(*new_line)
                if line_length < unit_r * 2 + 1:
                    continue
                if new_line[0] > new_line[1]:
                    new_line = new_line[1], new_line[0]
                    if new_line == current_line:
                        continue

                angle_ids = self.lineToAngleDict[new_line]
                if len(angle_ids) == 1:  # 防止撞墙
                    continue
                new_angle_id = 65536
                for j in angle_ids:
                    if j == angle_id:
                        continue
                    new_angle_id = j
                    break

                new_line_center_p = (new_line[0][0] + new_line[1][0]) / 2, (
                    new_line[0][1] + new_line[1][1]) / 2
                cost = NavigationMesh2D.get_line_length(new_line_center_p, current_line_center_p)
                new_cost = cost + current_cost
                if new_line not in cost_so_far or new_cost < cost_so_far[new_line]:
                    cost_so_far[new_line] = new_cost
                    pre_cost = NavigationMesh2D.get_line_length(new_line_center_p, end_p)
                    frontier.put((new_cost+pre_cost, new_cost, new_angle_id, new_line))
                    # print('in', (new_cost+pre_cost, new_cost, new_angle_id, new_line))
                    came_from[new_line] = current_line

        __tmp_v = __last_line
        while True:
            road_length += cost_so_far[__tmp_v]

            rlt.append(__tmp_v)
            __tmp_v = came_from[__tmp_v]
            if __tmp_v is None:
                break
        rlt.reverse()
        return rlt, road_length * 2 / len(rlt)

    def short_road(self, start_p, end_p, unit_r):
        tmp_road = self.short_road_by_a_star(start_p, end_p, unit_r)
        # return [((i[0][0]+i[1][0])/2, (i[0][1]+i[1][1])/2) for i in tmp_road[0]] + [end_p]
        # print('tmp_road', tmp_road[0][:])
        return NavigationMesh2D.smooth_road(start_p, end_p, tmp_road[0], unit_r)

    @staticmethod
    def check_angles_by_dot(near_line, far_line, dot):
        """

        :param near_line:
        :param far_line:
        :param dot:
        :return: new point or side
        """
        far_center_p = (far_line[0][0] + far_line[1][0]) / 2, \
                       (far_line[0][1] + far_line[1][1]) / 2
        f_l1 = dot, far_line[0]
        f_l2 = dot, far_line[1]

        bl1 = NavigationMesh2D.is_lines_cross(f_l1, near_line)
        bl2 = NavigationMesh2D.is_lines_cross(f_l2, near_line)
        if bl2 <= 1 and bl1 <= 1:
            blc_points = dot, far_line[0], far_line[1]
            if NavigationMesh2D.is_clockwise(blc_points):
                blc_points = blc_points[0], blc_points[2], blc_points[1]
            near_center_p = (near_line[0][0] + near_line[1][0]) / 2, (near_line[0][1] + near_line[1][1]) / 2
            blc = NavigationMesh2D.in_triangle(
                *blc_points, near_center_p)
            if not blc:  # 没有交点
                n_l1 = dot, near_line[0]
                n_l2 = dot, near_line[1]
                l1_d = NavigationMesh2D.distance_dot_to_line(far_center_p, n_l1)
                l2_d = NavigationMesh2D.distance_dot_to_line(far_center_p, n_l2)
                if l1_d < l2_d:
                    dot = n_l1[1]
                else:
                    dot = n_l2[1]
                return dot
            else:  # 包含
                n_p_1 = NavigationMesh2D.dot_from_cross_lines(far_line, (dot, near_line[0]))
                n_p_2 = NavigationMesh2D.dot_from_cross_lines(far_line, (dot, near_line[1]))
                return min(n_p_1, n_p_2), max(n_p_1, n_p_2)

        elif bl1 <= 1 or bl2 <= 1:  # 部分相交
            n_p_1, n_p_2 = (f_l1[1], f_l2[1]) if bl1 <= 1 else (f_l2[1], f_l1[1])  # 外点，内点
            if n_p_1 not in near_line:
                chose_n_p = near_line[0]
                blc_points = f_l1[1], dot, f_l2[1]
                if NavigationMesh2D.is_clockwise(blc_points):
                    blc_points = blc_points[0], blc_points[2], blc_points[1]
                if not NavigationMesh2D.in_triangle(*blc_points, near_line[0]):
                    chose_n_p = near_line[1]
                n_p_1 = NavigationMesh2D.dot_from_cross_lines(far_line, (dot, chose_n_p))

            return min(n_p_1, n_p_2), max(n_p_1, n_p_2)
        else:  # 两个交点
            n_p_1 = NavigationMesh2D.dot_from_cross_lines(near_line, (dot, far_line[0]))
            n_p_2 = NavigationMesh2D.dot_from_cross_lines(near_line, (dot, far_line[1]))

            return min(n_p_1, n_p_2), max(n_p_1, n_p_2)

    @staticmethod
    def smooth_road(start_p, end_p, lines, unit_r):
        if not lines:
            return [start_p, end_p]

        lines = lines[::-1]

        if NavigationMesh2D.dot_in_line(end_p, *lines[0]):
            lines.pop(0)
            if not lines:
                return [start_p, end_p]

        # print('lines', lines)
        checked_lines = {i: i for i in lines}
        line_index = 1
        last_p = end_p
        last_l = None
        rlt_ps = [last_p]
        rlt_ls = []

        while line_index < len(lines):
            if rlt_ps[-1] != last_p:
                rlt_ps.append(last_p)
                rlt_ls.append(last_l)
            far_line = checked_lines[lines[line_index]]
            near_line = checked_lines[lines[line_index-1]]

            check_rlt = NavigationMesh2D.check_angles_by_dot(near_line, far_line, last_p)
            if type(check_rlt[0]) != tuple:
                line_index += 1
                last_p = check_rlt
                last_l = near_line
            else:
                lines.pop(line_index - 1)

            # far_center_p = (far_line[0][0] + far_line[1][0]) / 2, \
            #     (far_line[0][1] + far_line[1][1]) / 2
            # f_l1 = last_p, far_line[0]
            # f_l2 = last_p, far_line[1]
            #
            # bl1 = NavigationMesh2D.is_lines_cross(f_l1, near_line)
            # bl2 = NavigationMesh2D.is_lines_cross(f_l2, near_line)
            # deep += 1
            # if bl2 <= 1 and bl1 <= 1:
            #     blc_points = last_p, far_line[0], far_line[1]
            #     if NavigationMesh2D.is_clockwise(blc_points):
            #         blc_points = blc_points[0], blc_points[2], blc_points[1]
            #     near_center_p = (near_line[0][0]+near_line[1][0])/2, (near_line[0][1]+near_line[1][1])/2
            #     blc = NavigationMesh2D.in_triangle(
            #         *blc_points, near_center_p)
            #     if not blc:  # 没有交点
            #         n_l1 = last_p, near_line[0]
            #         n_l2 = last_p, near_line[1]
            #         l1_d = NavigationMesh2D.distance_dot_to_line(far_center_p, n_l1)
            #         l2_d = NavigationMesh2D.distance_dot_to_line(far_center_p, n_l2)
            #         if l1_d < l2_d:
            #             last_p = n_l1[1]
            #         else:
            #             last_p = n_l2[1]
            #         last_l = near_line
            #         # print('88', last_l, last_p)
            #         line_index += 1
            #     else:  # 包含
            #         n_p_1 = NavigationMesh2D.dot_from_cross_lines(far_line, (last_p, near_line[0]))
            #         n_p_2 = NavigationMesh2D.dot_from_cross_lines(far_line, (last_p, near_line[1]))
            #         checked_lines[lines[line_index]] = min(n_p_1, n_p_2), max(n_p_1, n_p_2)
            #         # del checked_lines[lines[line_index - 1]]
            #         lines.pop(line_index-1)
            #
            # elif bl1 <= 1 or bl2 <= 1:  # 部分相交
            #     n_p_1, n_p_2 = (f_l1[1], f_l2[1]) if bl1 <= 1 else (f_l2[1], f_l1[1])  # 外点，内点
            #     if n_p_1 not in near_line:
            #         chose_n_p = near_line[0]
            #         blc_points = f_l1[1], last_p, f_l2[1]
            #         if NavigationMesh2D.is_clockwise(blc_points):
            #             blc_points = blc_points[0], blc_points[2], blc_points[1]
            #         if not NavigationMesh2D.in_triangle(*blc_points, near_line[0]):
            #             chose_n_p = near_line[1]
            #         n_p_1 = NavigationMesh2D.dot_from_cross_lines(far_line, (last_p, chose_n_p))
            #
            #     checked_lines[lines[line_index]] = min(n_p_1, n_p_2), max(n_p_1, n_p_2)
            #     # del checked_lines[lines[line_index - 1]]
            #     lines.pop(line_index - 1)
            #
            # else:  # 两个交点
            #     n_p_1 = NavigationMesh2D.dot_from_cross_lines(near_line, (last_p, far_line[0]))
            #     n_p_2 = NavigationMesh2D.dot_from_cross_lines(near_line, (last_p, far_line[1]))
            #
            #     checked_lines[lines[line_index]] = min(n_p_1, n_p_2), max(n_p_1, n_p_2)
            #     # del checked_lines[lines[line_index - 1]]
            #     lines.pop(line_index - 1)

        # 收尾处
        e_line = rlt_ps[-1], start_p
        d_line = checked_lines[lines[-1]]
        if NavigationMesh2D.is_lines_cross(e_line, d_line):
            print('cross')
            rlt_ps.append(NavigationMesh2D.dot_from_cross_lines(e_line, d_line))
        else:
            print('not cross')
            # if last_l is None:
            #     pass
            rlt_ls.append((d_line[0], NavigationMesh2D.dot_from_cross_lines(e_line, d_line)))
            if NavigationMesh2D.distance_dot_to_line(d_line[0], e_line) < \
                    NavigationMesh2D.distance_dot_to_line(d_line[1], e_line):
                rlt_ps.append(d_line[0])
            else:
                rlt_ps.append(d_line[1])
        rlt_ps.append(start_p)

        # 平滑处理
        # print('smooth', rlt_ls, rlt_ps)
        new_pos = []
        # print('l1', rlt_ps, checked_lines, lines, [i if i not in checked_lines else checked_lines[i] for i in lines])
        for line, point in zip(rlt_ls, rlt_ps[1:-1]):
            s_p_1 = line[0]
            s_p_2 = line[1]
            if abs(line[0][0] - point[0]) + abs(line[0][1] - point[1]) > \
                    abs(line[1][0] - point[0]) + abs(line[1][1] - point[1]):
                s_p_1 = line[1]
                s_p_2 = line[0]
            k, b = NavigationMesh2D.dot_mode_equation(*line)
            o_x = unit_r / ((k**2+1)**.5)
            if abs(s_p_1[0] - o_x-s_p_2[0]) < abs(s_p_1[0] + o_x-s_p_2[0]):
                x = s_p_1[0] - o_x
            else:
                x = s_p_1[0] + o_x
            y = x * k + b
            new_pos.append((x, y))

        new_pos.reverse()
        # print(new_pos)

        return new_pos + [end_p]


if __name__ == '__main__':
    __line1 = ((0, 0), (1, 1))
    __line2 = ((1, 1), (2, 1))
    # print(NavigationMesh2D.is_clockwise([(3, 3), (3, 0), (1, 1)]))
    # print(NavigationMesh2D.in_triangle((3, 3), (1, 1), (0, 3), (.5, 2.5)))
    # print(NavigationMesh2D.is_lines_cross(__line1, __line2))
    # print(NavigationMesh2D.get_ear([(0, 0), (1, 1), (2, 1)]))
    print(NavigationMesh2D.is_convex((2, 1), (2, 2), (1, 2)))
    __outer_points = [(0, 0), (3, 0), (3, 3), (0, 3)]
    __inner_points = [(1, 1), (1, 2), (2, 2), (2, 1)]
    __nav = NavigationMesh2D()
    __nav.init((3, 3), [__inner_points])

    _tmp_road = __nav.short_road_by_a_star((0, 0.1), (3, 3), .1)
    _tmp_road2 = NavigationMesh2D.smooth_road((0, 0.1), (3, 3), _tmp_road[0], .1)

    # print('road', _tmp_road, _tmp_road2)
    pygame.init()
    window = pygame.display.set_mode((800, 600))
    __clock = pygame.time.Clock()
    while True:
        __clock.tick(30)
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                exit()
        for _j in __nav.angels:
            for _i in [(_j[i1-1], _j[i1]) for i1 in range(len(_j))]:
                pygame.draw.line(window, (255, 0, 0), (_i[0][0]*100, _i[0][1]*100), (_i[1][0]*100, _i[1][1]*100))

        for _j in range(1, len(_tmp_road[0])):
            _j1 = _tmp_road[0][_j-1]
            _j2 = _tmp_road[0][_j]
            _j1 = (_j1[0][0] + _j1[1][0]) / 2 * 100, (_j1[0][1] + _j1[1][1]) / 2 * 100
            _j2 = (_j2[0][0] + _j2[1][0]) / 2 * 100, (_j2[0][1] + _j2[1][1]) / 2 * 100
            pygame.draw.line(window, (0, 255, 0), _j1, _j2)

        for _j in range(1, len(_tmp_road2)):
            pygame.draw.line(
                window, (0, 0, 255),
                (_tmp_road2[_j-1][0]*100, _tmp_road2[_j-1][1]*100),
                (_tmp_road2[_j][0]*100, _tmp_road2[_j][1]*100))

        pygame.display.update()
