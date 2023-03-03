#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :grid_move_controller.py
# @Time      :07/02/2023
# @Author    :russionbear
# @Function  :function

import numpy

from qins_moon.core.interface.grid_map import IGridMoveControllerInterface, IGridMovementInterface, \
    IGridNavigationInterface
from qins_moon.core.utils.data_structure import JoinedNdarray, RegistryBase
from qins_moon.core.utils.math_tool import MathTool
from qins_moon.core.utils.detached_thread import DetachedThread


# # 静态路径
# 静态路径
# 静态路径+等待占有nextPoint
#
# ## 动态路径都要用nextPoint，这样可以处理避让和碰撞
# # 动态路径+短距离+单体
# 动态路径+短距离+简单地形/用户手动目标点
# 动态路径+短距离+复杂地形
# step 1: a*+max_deep+b*+flow_field
# ---------------------
# ## 长距离默认不考虑考虑敌方单位
# # 动态路径+长距离
# 多个target+高维地图+用户自定导航
#
# 额外参数：单位被卡住而退出群组寻路的时间
# 非静态路径 移动地图：-1障碍物，0 可行走


class GridStaticMoveController(IGridMoveControllerInterface):
    def __init__(self, movement, block_size):
        super().__init__(movement, block_size)
        self._gridRoad = []

    @property
    def is_road_finished(self):
        return not self._nextPoint and not self._gridRoad

    def set_task(self, road):
        self._gridRoad = road
        self._sleepTime = 0
        # 如果当前_nextPoint与road[0]像素距离差不大直接更新_nextPoint
        if road is not None:
            sec_p = road[0]
            s_p = self.movement.loc
            if ((s_p[0] - sec_p[0]) ** 2 + (s_p[1] - sec_p[1]) ** 2) ** .5 < self.blockSize[0]:
                self._set_next_grid_point(sec_p)

    def _pub_task_finished(self, **kwargs):
        super()._pub_task_finished(**kwargs)
        self._lastGridLoc = self._gridRoad

    def _update_road(self, delta_time):
        """
        调用事件 next Point 到达后, 包括正在 nextPoint is None 时
        :param delta_time:
        :return: 是否到达道路终点， 0 到达终点， 1 申请newNextPoint成功，2 申请失败， 3 移动中
        """
        moving_state = self._update_next_point(delta_time)
        if moving_state == 1:
            return 3
        elif moving_state == 0:
            if not self._gridRoad:
                self._pub_task_finished()
                return
        elif self._gridRoad:  # moving_state == 3
            while self._gridRoad:  # 剔除重复的移动点
                if self._gridRoad[0] == self._gridLoc:
                    self._gridRoad.pop(0)
                else:
                    break

        else:
            return

        road = self._gridRoad

        if self._alloc_next_point(road[0]):
            road.pop(0)
            return 1
        else:
            return 2

    def update(self, delta_time):
        if super().update(delta_time) is not None:
            return
        self._update_road(delta_time)


class GridDynMoveController(IGridMoveControllerInterface):

    def __init__(self, movement, config, grid_nav, layer_and_value, engine, group_id):
        super().__init__(movement, config.MAP_BLOCK_SIZE)
        self.open_alloc_next_point(grid_nav, layer_and_value, engine)

        # about dynamic move
        self._nextGridTarget = None
        self._gridTargets = []
        self._flowField: GridFlowField | None = None  # 没有流场就不走
        self.__incompleteFlowField: GridFlowField | None = None  # 没有流场就不走
        self._firstFlowFieldRoad = []
        self._currentIndexOfFirstFlowFieldRoad = 0
        self.groupId = group_id

        # about wait time for search
        self._searchRoadTaskId = 0
        self.maxTickWaitRoadTask = config.MAX_TICK_WAIT_ROAD_TASK
        self._currentTickWaitRoadTask = 0

        # alloc next point blocked
        self.maxNextPointAllocCount = config.MAX_NEXT_POINT_ALLOC_COUNT
        self.blockedSleepTime = config.BLOCKED_SLEEP_TIME
        self._currentNextPointAllocCount = 0

    # 任务控制相关

    def clear_task(self):
        self._gridTargets = []
        self._clear_current_target()

    def set_task(self, targets):
        # if not targets or self._nextGridTarget is not None:
        self.clear_task()
        if targets:
            self._nextGridTarget = targets.pop(0)
            self._gridTargets = targets
            self._sleepTime = 0

    def append_task(self, targets):
        if self._nextGridTarget is None and not self._gridTargets:
            self.set_task(targets)
        else:
            self._gridTargets += targets

    # 寻路相关

    def search_road_function(self, max_deep, can_stop):
        """

        :param max_deep:
        :param can_stop:
        :return: None 没有道路， road
        """
        gff = self.__incompleteFlowField
        cost_map = self.gridNavigation.get_engine_move_map(self._moveEngine)
        if not gff.flowField.storage:
            tmp_road = MathTool.short_road_by_astar_nw(
                cost_map, self._gridLoc, self._nextGridTarget, max_deep, can_stop)[0]
        else:
            tmp_road = MathTool.short_road_to_gff_by_astar(
                cost_map, gff.flowField, self._gridLoc, self._nextGridTarget, max_deep, can_stop)[0]
        # 验货
        if len(tmp_road) < 2:
            return None
        if tmp_road[-1] != self._nextGridTarget:
            tmp_road = MathTool.short_road_by_direction_star_nw(
                cost_map, self._gridLoc, self._nextGridTarget, max_deep, can_stop)
        if len(tmp_road) < 2:
            return None

        return tmp_road

        # #
        # dn = self.dataNodeRoot
        # dt = dn.dataTable
        # tmp_d = dn.militaryDict[self.id]
        # if tmp_d is None:
        #     return
        # if target == self.grid_loc:
        #     tmp_road = [target, target]
        # else:
        #     tmp_road = MathTool.short_road_by_direction_star_nw(
        #         self.gridNavComponent.cost_map(self.navEngine),
        #         tmp_d.loc, target
        #     )
        #     if not tmp_road or tmp_road[-1] != target:
        #         return
        # # print('new road', tmp_road, self._gridLoc)
        # # 显示路线
        # # self.parent.coverLayer[f'-u-r{self.id}'] = [(255, 0, 0)] + tmp_road
        # self.gridRoadTask.road = tmp_road#

    def extend_flow_field_function(self, max_deep, can_stop):
        gff = self.__incompleteFlowField
        tmp_road = self._firstFlowFieldRoad
        gff.add_road(tmp_road, max_deep, can_stop)

    def handle_road_search_finished(self, rlt):
        if self._searchRoadTaskId == 0 or not self._nextGridTarget or rlt is None:
            # 这两条语句顺序不能换
            self._searchRoadTaskId = 0
            self._clear_current_target()
            return
        self._searchRoadTaskId = 0

        # 判断目标点是否被更改, 改了就更新flowField
        if rlt[-1] != self._nextGridTarget:
            self._clear_current_target()
            # self._gridTargets.insert(0, self._nextGridTarget)
            self._nextGridTarget = rlt[-1]
            self.__incompleteFlowField = GridFlowFieldStorage()[(*self._nextGridTarget, self.groupId, self._moveEngine)]

        self._firstFlowFieldRoad = rlt
        self._currentTickWaitRoadTask = 0
        self._currentIndexOfFirstFlowFieldRoad = 0
        self._searchRoadTaskId = DetachedThread().add_task(
            {}, self.extend_flow_field_function, self.handle_flow_field_extended)

    def handle_flow_field_extended(self, rlt):
        if self._searchRoadTaskId == 0 or not self._nextGridTarget:
            self._clear_current_target()
            self._searchRoadTaskId = 0
            return
        self._searchRoadTaskId = 0

        self._flowField = self.__incompleteFlowField
        # print(self._flowField.flowField.combine())
        self.__incompleteFlowField = None
        assert rlt is None

    def _pub_road_search(self):
        dt = DetachedThread()
        if self._searchRoadTaskId != 0:
            dt.remove_task(self._searchRoadTaskId)
        self._searchRoadTaskId = 0

        grid_loc = self._gridLoc
        gff = GridFlowFieldStorage()[(*self._nextGridTarget, self.groupId, self._moveEngine)]
        self.__incompleteFlowField = gff
        if gff.flowField[grid_loc[1], grid_loc[0]] > 0:
            self._flowField = gff
            return
        else:
            self._searchRoadTaskId = dt.add_task(
                {}, self.search_road_function,
                self.handle_road_search_finished)
        self._currentNextPointAllocCount = 0

    # 清除当前资源
    def _clear_current_target(self):
        # if self._gridTargets:
        #     self._nextGridTarget = self._gridTargets.pop(0)
        # else:
        self._nextGridTarget = None
        # self._sleepTime = -1

        self._firstFlowFieldRoad = []
        self._currentIndexOfFirstFlowFieldRoad = 0
        self._currentNextPointAllocCount = 0
        self._currentTickWaitRoadTask = 0

        if self.__incompleteFlowField is not None:
            del GridFlowFieldStorage()[self.__incompleteFlowField.componentKey]
            self.__incompleteFlowField = None

        if self._flowField is not None:
            del GridFlowFieldStorage()[self._flowField.componentKey]
            self._flowField = None

        if self._searchRoadTaskId != 0:
            DetachedThread().remove_task(self._searchRoadTaskId)
            self._searchRoadTaskId = 0

    # 申请nextPoint
    def _alloc_next_point_nb(self):
        ps = self._flowField.get_next_targets(self._gridLoc, self.forward)
        rlt = None
        for i in ps:
            __last_gird = self._lastGridLoc
            rlt = super()._alloc_next_point(i)
            if rlt is not None:
                if rlt == __last_gird:
                    self._currentNextPointAllocCount += 2
                else:
                    self._currentNextPointAllocCount = 0
                # print(self._currentNextPointAllocCount)
                break
        else:
            self._currentNextPointAllocCount += 1
            if self._currentNextPointAllocCount <= self.maxNextPointAllocCount:
                self._sleepTime = self.blockedSleepTime

        if self._currentNextPointAllocCount > self.maxNextPointAllocCount:
            self._clear_current_target()
            self._currentNextPointAllocCount = 0
        return rlt

    def update(self, delta_time):
        if super().update(delta_time) is not None:
            return
        self._update_flow_field(delta_time)

    def _update_flow_field(self, delta_time):
        moving_state = self._update_next_point(delta_time)
        if moving_state == 1:
            return 3
        if self._nextGridTarget is None:  # 获取目标点
            if self._gridTargets:
                self._nextGridTarget = self._gridTargets.pop(0)
            return
        elif self._nextGridTarget == self._gridLoc:
            self._clear_current_target()
            self._pub_task_finished()
            return

        if self._flowField is None:  # 流场出现之前
            if self._firstFlowFieldRoad:  # 临时道路
                next_p = self._firstFlowFieldRoad[self._currentIndexOfFirstFlowFieldRoad]
                if self._alloc_next_point(next_p) is not None:
                    self._currentIndexOfFirstFlowFieldRoad += 1
                    if self._currentIndexOfFirstFlowFieldRoad >= len(self._firstFlowFieldRoad):
                        self._clear_current_target()
            elif self._searchRoadTaskId == 0:  # 启动寻路
                self._pub_road_search()
            else:  # 等待寻路
                self._currentTickWaitRoadTask += 1
                if self._currentTickWaitRoadTask > self.maxTickWaitRoadTask:
                    self._clear_current_target()
            return

        self._alloc_next_point_nb()


class GridFlowField:
    """
    关于大地图，这里的flow field 面积不能太大，一方面会占用内存，100张1000x1000流图 需要超过256M内存
    这种大图数量多的话也会影响性能
    当路径过长时应截断并更改目标点
    functions:
        - refresh the first road
        - refresh the second road
        - contains the loc of unit
    """
    # 该方案不适用于大规模的单位
    # def __init__(self, mem_nu, cost_map, road, radius):
    #     super().__init__()
    #     self._memeNu = mem_nu
    #     self.offset = 0, 0
    #     self.flowField: numpy.ndarray | None = None
    #
    #     height, width = cost_map.shape
    #     start_p = min(road[0][0], road[-1][0]), min(road[0][1], road[-1][1])
    #     end_p = max(road[0][0], road[-1][0]), max(road[0][1], road[-1][1])
    #     offset = end_p[0] - start_p[0], end_p[1] - start_p[1]
    #     size = offset[0] + 1 + radius, offset[1] + 1 + radius
    #     self.offset = start_p[0] - radius, start_p[1] - radius
    #     if start_p[0] < radius:
    #         size = size[0] - (radius - start_p[0]), size[1]
    #         self.offset = self.offset[0] + (radius - start_p[0]), self.offset[1]
    #     if start_p[1] < radius:
    #         size = size[0], size[1] - (radius - start_p[1])
    #         self.offset = self.offset[0], self.offset[1] + (radius - start_p[1])
    #     if end_p[0] + 1 + radius > width:
    #         size = size[0] - (end_p[0] + 1 + radius - width), size[1]
    #     if end_p[1] + 1 + radius > height:
    #         size = size[0], size[1] - (end_p[1] + 1 + radius - height)
    #
    #     print(size, self.offset)
    #     self.flowField = numpy.zeros((size[1], size[1]), dtype=numpy.int_)
    #     road = [(i[0] - self.offset[0], i[1] - self.offset[1]) for i in road]
    #     __sqrt = 2 ** .5
    #     # 第一阶段
    #     self.flowField[road[-1][1], road[-1][0]] = 1
    #     directions = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    #     for r in range(1, radius+1):
    #         # top
    #         for xp in range(-r, r):
    #             x_, y_ = road[-1][0] + xp, road[-1][1] - r
    #             if cost_map[y_, x_] != 1:
    #                 continue
    #             come_from = min(
    #                 filter(lambda arg: self.flowField[arg[1], arg[0]], [(x_-1, y_+1), (x_+1, y_+1), (x_, y_+1)]),
    #                 key=lambda arg: self.flowField[arg[1], arg[0]])
    #             if abs(come_from[0]-x_) + abs(come_from[1]-y_) > 1:
    #                 self.flowField[y_, x_] = self.flowField[come_from[1], come_from[0]] + __sqrt
    #             else:
    #                 self.flowField[y_, x_] = self.flowField[come_from[1], come_from[0]] + __sqrt
    #
    #         for drt_i in range(len(directions)):
    #             pass
    #         for drt in directions:
    #             x_, y_ = road[-1][0] + drt[0], road[-1][1] + drt[1]
    #             if x_ < 0 or y_ < 0 or x_ >= size[0] or y_ >= size[1]:
    #                 continue
    #             # self.flowField[]

    # 不要直接调用
    def __init__(self, component_key):
        """

        :param component_key: (locX, locY, groupId, engineId)
        """
        gff_storage = GridFlowFieldStorage()
        self.flowField: JoinedNdarray | None = None
        self._memeNu = 0
        self.componentKey = component_key

        self.costMap: numpy.ndarray = gff_storage.gridNav.get_engine_move_map(component_key[-1])
        self.flowField: JoinedNdarray = JoinedNdarray(
            (self.costMap.shape[1], self.costMap.shape[0]), gff_storage.areaSize)

    @property
    def target(self):
        return self.componentKey[:2]

    @property
    def mem_nu(self):
        return self._memeNu

    def add_road(self, road, max_deep, can_stop):
        areas = set()
        directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        area_size = GridFlowFieldStorage().areaSize

        # # 扩张流场，防止流场太小
        area_map_size = self.costMap.shape
        area_map_size = area_map_size[1] // area_size[0], area_map_size[0] // area_size[1]

        for i in road:
            ar = i[0] // area_size[0], i[1] // area_size[1]
            areas.add(ar)
            for drt in directions:
                x_, y_ = ar[0] - drt[0], ar[1] - drt[1]
                if x_ < 0 or y_ < 0 or x_ >= area_map_size[0] or y_ >= area_map_size[1]:
                    continue
                areas.add((x_, y_))

        # 从costMap中读取数据
        # print(areas)
        for i in areas:
            if i in self.flowField.storage:
                continue
            else:
                # print(range(i[1] * area_size[1], i[1] * area_size[1] + area_size[1]),
                #       [i[0] * area_size[0], i[0] * area_size[0] + area_size[0]])
                tmp = self.costMap[
                      range(i[1] * area_size[1], i[1] * area_size[1] + area_size[1]),
                      i[0] * area_size[0]: i[0] * area_size[0] + area_size[0]
                      ]
                # print(tmp.shape)

                self.flowField.add_block(i, tmp)

        # 寻找 start_ps
        start_ps = {}
        v1 = self.flowField[road[-1][1], road[-1][0]]
        if v1 == 0:
            start_ps[road[-1]] = 1
        else:
            v3 = self.flowField[road[0][1], road[0][0]]
            if v3 > 0:
                return
            _index = -2
            while True:
                v2 = self.flowField[road[_index][1], road[_index][0]]
                if v2 > 0:
                    _index -= 1
                    v1 = v2
                    continue
                start_ps[road[_index]] = v1
                break

        # # 更新start_ps
        # if start_ps is None:
        #     v1 = self.flowField[road[-1][1], road[-1][0]]
        #     v2 = self.flowField[road[-2][1], road[-2][0]]
        #     assert v1 > 0 and v2 == 0
        #     if abs(road[-1][0]-road[-2][0]) + abs(road[-1][1]-road[-2][1]) == 2:
        #         v1 += MathTool.sqrt2
        #     else:
        #         v1 += 1
        #     start_ps = {road[-2]: v1}

        # print(start_ps, 'start_ps')
        self.flowField, ladder_nu_dict = MathTool.wavefront(self.flowField, start_ps, max_deep, can_stop)

    # 不要直接调用
    def increment(self, value=1):
        """
        每次减/加一都必须删除/增加 仅一次它的引用，否则可能会有内存泄漏
        :param value:
        :return:
        """
        self._memeNu += value
        # if self._memeNu <= 0:
        #     del GridFlowFieldStorage()[self.componentKey]

    def in_center_area(self, loc):
        # loc = loc[0]-self.offset[0], loc[1]-self.offset[1]
        height, width = self.flowField.shape
        if loc[0] < 0 or loc[1] < 0 or loc[1] >= height or loc[0] > width:
            return False
        v = self.flowField[loc[1], loc[0]]
        return v <= GridFlowFieldStorage().areaSize[0]  # v <= self.center_area_mark()

    def get_next_targets(self, loc, last_forward):
        height, width = self.flowField.shape
        directions = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
        # loc = loc[0] - self.offset[0], loc[1] - self.offset[1]
        value = self.flowField[loc[1], loc[0]]
        rlt = []
        __sqrt = 1.41
        # final_target = self.target
        for drt in directions:
            x_, y_ = loc[0] + drt[0], loc[1] + drt[1]
            if x_ < 0 or y_ < 0 or x_ >= width or y_ >= height:
                continue
            tmp_v = self.flowField[y_, x_]
            if tmp_v <= 0:
                continue
            if tmp_v > value:
                continue

            rlt.append((tmp_v, (x_, y_)))
        rlt.sort(key=lambda arg: (arg[0], ((arg[1][0]-last_forward[0])**2+(arg[1][1]-last_forward[1])**2)**.5))
        # print(rlt, loc, last_forward)
        return [i[1] for i in rlt]

    def __contains__(self, item):
        # loc = item[0]-self.offset[0], item[1]-self.offset[1]
        loc = item
        height, width = self.flowField.shape
        if loc[0] < 0 or loc[1] < 0 or loc[1] >= height or loc[0] > width:
            return False
        return self.flowField[loc[1], loc[0]] > 0


class GridFlowFieldStorage(RegistryBase[GridFlowField]):
    """
    单例
    key的类型： Tuple[loc_x, loc_y, groupId, engine]
    """

    _instance = None

    def __init__(self):
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self
        super().__init__()

        # 长宽要相等
        self.areaSize = 4, 4
        self.gridNav: IGridNavigationInterface | None = None

    def init(self, area_size, grid_nav):
        self.areaSize = area_size
        self.gridNav = grid_nav

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)

    def __getitem__(self, item):
        tmp_obj = super().__getitem__(item)
        if tmp_obj is None:
            tmp_obj = GridFlowField(item)
            self._storage[item] = tmp_obj
        tmp_obj.increment()
        # print(tmp_obj.mem_nu)
        return tmp_obj

    def __delitem__(self, key):
        if key not in self._storage:
            return
        tmp_obj = self._storage[key]
        tmp_obj.increment(-1)
        if tmp_obj.mem_nu <= 0:
            super().__delitem__(key)

    def __setitem__(self, key, value):
        raise Exception("function dropped")
