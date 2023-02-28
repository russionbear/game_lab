#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :rvo2.py
# @Time      :16/01/2023
# @Author    :russionbear
# @Function  :function

import ctypes
from typing import List, Tuple

DLL_PATH = r'E:\workspace\c++\make_dll\cmake-build-debug\RVO.dll'


class Vector2(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float)]


class AgentNodeStruct(ctypes.Structure):
    _fields_ = [("neighbor_dist", ctypes.c_float),
                ("max_neighbors", ctypes.c_int),
                ("time_horizon", ctypes.c_float),
                ("time_horizon_obst", ctypes.c_float),
                ("radius", ctypes.c_float),
                ("max_speed", ctypes.c_float),
                ("global_", Vector2),
                ("velocity", Vector2),
                ("position", Vector2),
                ("id_", ctypes.c_int),
                ("category", ctypes.c_uint32),
                ("category_mask", ctypes.c_uint32)]


class RVO2:
    """
    每次跟新都要重构agent和obstacle
    """
    def __init__(self):
        self.dll = None
        self.sim = None
        self.simType = ctypes.POINTER(ctypes.c_void_p)

    def init(self):
        self.dll = ctypes.cdll.LoadLibrary(DLL_PATH)
        self.dll.get_sim.restype = self.simType
        self.sim = self.dll.get_sim()

    def update(self, delta_time):
        self.dll.set_delta_time(self.sim, ctypes.c_float(delta_time))
        self.dll.do_step(self.sim)

    def building_agent(self, l0: List[AgentNodeStruct]):
        array_type = AgentNodeStruct * len(l0)
        arg_arr = array_type()
        for i in range(len(l0)):
            arg_arr[i] = l0[0]
        self.dll.building_agent(self.sim, arg_arr)

    def building_obstacle(self, l0: List[Tuple[List[Tuple[float, float]], int, int]]):
        self.dll.clear_obstacles(self.sim)
        for i0 in l0:
            i = i0[0]
            tmp_type = (len(i) * 2 + 1) * ctypes.c_float
            tmp_value = tmp_type()
            tmp_value[0] = len(i)
            for j, v in enumerate(i):
                tmp_value[j*2+1] = v[0]
                tmp_value[j*2+2] = v[1]

            self.dll.add_obstacle(self.sim, tmp_value, ctypes.c_uint32(i0[1]), ctypes.c_uint32(i0[2]))
        self.dll.process_obstacles(self.sim)

    def set_agent_data(self, id_: int, data: AgentNodeStruct):
        self.dll.set_agent_data(self.sim, id_, ctypes.byref(data))

    def set_agents_position(self, positions: List[Tuple[float, float]]):
        tmp_type = (len(positions) * 2 + 1) * ctypes.c_float
        tmp_value = tmp_type()
        tmp_value[0] = len(positions)
        for i, v in enumerate(positions):
            tmp_value[i*2+1] = v[0]
            tmp_value[i*2+2] = v[1]
        self.dll.set_agents_position(self.sim, tmp_value)

    def set_agents_global(self, goals: List[Tuple[float, float]]):
        tmp_type = (len(goals) * 2 + 1) * ctypes.c_float
        tmp_value = tmp_type()
        tmp_value[0] = len(goals)
        for i, v in enumerate(goals):
            tmp_value[i*2+1] = v[0]
            tmp_value[i*2+2] = v[1]
        self.dll.set_agents_global(self.sim, tmp_value)

    def get_result(self):
        result_length = self.dll.get_result_len(self.sim)
        rlt = []
        if result_length == 0:
            return rlt
        result_type = ctypes.c_float * result_length
        tmp_rlt = result_type()
        self.dll.get_result(self.sim, tmp_rlt)
        for i in range(result_length//2):
            rlt.append((tmp_rlt[i*2], tmp_rlt[i*2+1]))
        return rlt

    def test(self):
        l0 = []
        for i in range(2):
            ans = AgentNodeStruct()
            ans.id_ = i
            l0.append(ans)
        self.building_agent(l0)
        # self.dll.get_result(self.sim, List[Tuple[float, float]])


if __name__ == '__main__':

    __storage = RVO2()
    __storage.init()
    __storage.building_obstacle([([(5, 0), (6, 0), (6, 3), (5, 3)], 1, 0)])

    agents = []
    tmp_agent = AgentNodeStruct()
    tmp_agent.max_neighbors = 10
    tmp_agent.neighbor_dist = 75
    tmp_agent.time_horizon = 5.0
    tmp_agent.time_horizon_obst = 5.0
    tmp_agent.radius = 25
    tmp_agent.max_speed = 100
    tmp_agent.global_ = Vector2(0, 0)
    tmp_agent.position = Vector2(100, 100)
    tmp_agent.id_ = 100
    tmp_agent.category = 1
    tmp_agent.category_mask = 1
    agents.append(tmp_agent)
    __storage.building_agent(agents)
    __positions = [(i.position.x, i.position.y) for i in agents]
    __goals = [(i.global_.x, i.global_.y) for i in agents]
    import pygame
    clock = pygame.time.Clock()
    windows = pygame.display.set_mode((1000, 800))
    __is_run = True
    while __is_run:
        __delta_time = clock.tick(60) / 1000
        print('positions', __positions, __goals)
        __storage.set_agents_position(__positions)
        __storage.set_agents_global(__goals)
        __storage.update(__delta_time)
        __result = __storage.get_result()
        print(__result, 'result')
        __positions = [(__result[i][0]*__delta_time*100+__positions[i][0], __result[i][1]*__delta_time*100+__positions[i][1])
                       for i in range(len(__result))]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                __is_run = False

        windows.fill((0, 0, 0))

        pygame.draw.rect(windows, 'red', pygame.Rect(500, 0, 100, 300))
        pygame.draw.circle(windows, 'green', (1000, 300), 5)
        pygame.draw.circle(windows, 'blue', (__positions[0][0], __positions[0][1]), 100)

        pygame.display.update()
