#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :nav_mesh2d.py
# @Time      :15/02/2023
# @Author    :russionbear
# @Function  :function

import ctypes
DLL_PATH = r"E:\workspace\c++\NavMesh2D\cmake-build-debug\NavMesh2D.dll"
CACHE_FILE = r'E:\workspace\game_lab\cache\nav_mesh2d.obj'


class SampleConfiguration(ctypes.Structure):
    _fields_ = [('m_cellSize', ctypes.c_float),
                ('m_cellHeight', ctypes.c_float),
                ('m_agentHeight', ctypes.c_float),
                ('m_agentRadius', ctypes.c_float),
                ('m_regionMinSize', ctypes.c_float),
                ('m_regionMergeSize', ctypes.c_float),
                ('m_edgeMaxLen', ctypes.c_float),
                ('m_edgeMaxError', ctypes.c_float),
                ('m_vertsPerPoly', ctypes.c_float)
                ]


class NavMesh2d:
    def __init__(self):
        self.dll = None
        self.sample = None
        self.defaultConfiguration = SampleConfiguration()
        self.defaultConfiguration.m_cellSize = 1
        self.defaultConfiguration.m_cellHeight = 1
        self.defaultConfiguration.m_agentHeight = 1
        self.defaultConfiguration.m_agentRadius = .5
        self.defaultConfiguration.m_regionMinSize = .3
        self.defaultConfiguration.m_regionMergeSize = 5
        self.defaultConfiguration.m_edgeMaxLen = 5
        self.defaultConfiguration.m_edgeMaxError = 2
        self.defaultConfiguration.m_vertsPerPoly = 16
        self.sampleType = ctypes.POINTER(ctypes.c_void_p)

    def init(self, world_size, obstacles: list):
        self.dll = ctypes.cdll.LoadLibrary(DLL_PATH)
        self.dll.getSample.restype = self.sampleType

        self.sample = self.dll.getSample()
        # self.dll.loadSample.restype = self.sampleType
        # self.dll.loadSample.argtypes = (ctypes.c_wchar_p, SampleConfiguration)
        vs = [(0, 0, 0), (0, 0, world_size[1]), (world_size[0], 0, world_size[1]), (world_size[0], 0, 0)]
        fs = [(1, 2, 3, 4)]
        it = 5
        for obstacle in obstacles:
            size = len(obstacle)
            for v in obstacle:
                vs.append((v[0], 0, v[1]))
            for v in obstacle:
                vs.append((v[0], 10, v[1]))
            for v in range(size):
                f = (it+(v-1) % size, it+(v-1) % size + size, it+v, it+v+size)
                fs.append(f)
                fs.append(tuple(reversed(f)))

            it += size * 2
        s0 = ''
        for i in vs:
            s0 += f'v {i[0]} {i[1]} {i[2]}\n'
        for i in fs:
            s0 += f'f {i[0]} {i[1]} {i[2]} {i[3]}\n'
        with open(CACHE_FILE, 'w') as f:
            f.write(s0)
        self.dll.loadSample(self.sample, CACHE_FILE, self.defaultConfiguration)

    def short_road(self, start_p, end_p):
        f_t = ctypes.c_float * 3
        s_p = f_t()
        e_p = f_t()

        s_p[0] = start_p[0]
        s_p[1] = 0
        s_p[2] = start_p[1]
        e_p[0] = end_p[0]
        e_p[1] = 0
        e_p[2] = end_p[1]

        road_len = ctypes.pointer(ctypes.c_int(0))
        t_road = ctypes.c_float * (256 * 3)
        road = t_road()

        self.dll.findPath.argtypes = self.sampleType, ctypes.c_float * 3, ctypes.c_float * 3, \
            ctypes.POINTER(ctypes.c_int), ctypes.c_float * (256 * 3)

        self.dll.findPath(self.sample, s_p, e_p, road_len, road)

        road = [road[i] for i in range(6)]
        print(road_len[0], road, self.sample)

    def test(self):
        t_f = ctypes.c_float * 120
        self.dll.testFindPath.restype = ctypes.c_int
        self.dll.testFindPath.argtypes = self.sampleType, t_f
        d = t_f()
        length = self.dll.testFindPath(self.sample, d)
        print(length, d)
        for i in range(length*3):
            print(d[i])


if __name__ == '__main__':
    __nav = NavMesh2d()
    __nav.init((100, 200), [[(50, 50), (75, 50), (75, 75), (50, 75)]])
    __nav.test()
    exit()
    print('====')
    __nav.short_road((20, 20), (80, 150))
