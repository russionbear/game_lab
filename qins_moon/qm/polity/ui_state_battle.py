#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :ui_state_battle.py
# @Time      :23/02/2023
# @Author    :russionbear
# @Function  :function

"""
# info: city, unit, terrain, group
# storage info
# team command: appoint team, make/del team, appoint staff, ...storage
# batmen team command:
    damage building/people/storage,
    attack team/army,
    steal storage/people,
    spy storage/team/group/army/buildings
    split/combine army/team,
# unit team command: show move/attack area, choose action/road, choose target | set unit perm action
    attack, defence, spy,
# city team command: build building/unit, enlist unit/talent, team command,
# ferry team command: make/del team, appoint staff, set road, building road
################################################
random: flood, fire, collapsed mine; robber, rebel, union
ai...
"""

from typing import List, Any

import pygame.event

from qins_moon.core.render.render import SceneManager
from qins_moon.core.ui_element import UserInterfaceManager
from qins_moon.core.director.ui_state import IUIStateInterface, UIStateManagerBase, UIStateMngManager
from qins_moon.core.director import Director
from config import Config
from entity import PolityRootEntity


class BattleUIStates:

    home = 0x1
    status = 0x2
    moveArea = 0x3
    chooseMenu = 0x4
    attackTarget = 0x5
    buyUnit = 0x6
    groupCmd = 0x11


class BattleUIStateManager(UIStateManagerBase):
    def __init__(self, root_entity):
        super().__init__()
        self.rootEntity: PolityRootEntity = root_entity

        self.homeState = HomeUIState(self)
        self.groupStateState = GroupStateState(self)
        self.moveAreaState = MoveAreaUIState(self)
        self.chooseMenuState = ChooseMenuUIState(self)
        self.attackTargetState = AttackTargetUIState(self)
        self.stateComponentDict = {
            BattleUIStates.home: self.homeState,
            BattleUIStates.status: self.groupStateState,
            BattleUIStates.moveArea: self.moveAreaState,
            BattleUIStates.chooseMenu: self.chooseMenuState,
            BattleUIStates.attackTarget: self.attackTargetState
        }
        self.currentState = BattleUIStates.home

    def active(self):
        super().active()
        RootEntityManager.switch_root_entity(self.componentKey)
        SceneManager.switch_scene(self.componentKey)
        UserInterfaceManager.switch(self.ui)

    def switch_state(self, state):
        if self.currentState == state:
            return
        if self.currentState != BattleUIStates.home:
            self.stateComponentDict[self.currentState].inactive()
        self.currentState = state
        self.stateComponentDict[self.currentState].active()

    def event(self, e0: pygame.event.Event):
        if self.currentState == BattleUIStates.home:
            self.homeState.event(e0)
        else:
            self.stateComponentDict[self.currentState].event(e0)


class BattleUIStateBase(UIStateBase):
    def __init__(self, mng):
        self.mng: BattleUIStateManager = mng

    def event(self, e0: pygame.event.Event):
        pass

    def active(self):
        pass

    def inactive(self):
        pass


class HomeUIState(BattleUIStateBase):
    def __init__(self, mng):
        super().__init__(mng)
        self.mng.ui.homeState.handleStatus = self.handle_status
        self.mng.ui.homeState.handleExit = self.handle_exit
        self.mng.ui.homeState.handleSave = self.handle_save

        self.clickedBuilding = None
        self.clickedMilitary = None
        self.lastClickedGridArea = 0, 0
        # self.lastLeftCircleArea = 0, 0, 0, 0
        self._leftMouseCircleArea = None
        self.leftMouseCircledUnits = []

    def active(self):
        self.mng.clickedBuilding = None
        self.mng.clickedMilitary = None
        self.mng.ui.switch_view(BattleUIViewType.home)

    @staticmethod
    def get_grid_loc():
        current_scene = SceneManager.current_scene
        size = current_scene.get_surface().get_size()
        scene_loc = current_scene.loc
        mouse_loc = pygame.mouse.get_pos()

        # print("loc", (scene_loc[0] - size[0] // 2, scene_loc[1] - size[1] // 2))

        mouse_loc = mouse_loc[0] + scene_loc[0] - size[0] // 2, mouse_loc[1] + scene_loc[1] - size[1] // 2
        mouse_loc = mouse_loc[0] // Config.MAP_BLOCK_SIZE[0], mouse_loc[1] // Config.MAP_BLOCK_SIZE[1]
        # print(HomeUIState.grid_loc_to_pos(mouse_loc), mouse_loc, pygame.mouse.get_pos())
        return mouse_loc

    @staticmethod
    def scene_pos():
        current_scene = SceneManager.current_scene
        scene_loc = current_scene.loc
        size = current_scene.get_surface().get_size()
        return scene_loc[0] - size[0] // 2, scene_loc[1] - size[1] // 2

    @staticmethod
    def grid_loc_to_pos(loc):
        current_scene = SceneManager.current_scene
        scene_loc = current_scene.loc
        size = current_scene.get_surface().get_size()
        mouse_pos = loc[0] * Config.MAP_BLOCK_SIZE[0], loc[1] * Config.MAP_BLOCK_SIZE[1]
        pos = mouse_pos[0] - (scene_loc[0] - size[0] // 2), mouse_pos[1] - (scene_loc[1] - size[1] // 2)
        return pos

    def event(self, e0: pygame.event.Event):
        # 这个 if-else 用于更新lastClickedArea
        # # 同时更新左键框选
        if e0.type == pygame.MOUSEMOTION:
            if self._leftMouseCircleArea is not None:
                left_mouse_area = *self._leftMouseCircleArea[:2], *e0.pos
                left_mouse_area = min(left_mouse_area[0], left_mouse_area[2]), \
                    min(left_mouse_area[1], left_mouse_area[3]), \
                    max(left_mouse_area[0], left_mouse_area[2]), \
                    max(left_mouse_area[1], left_mouse_area[3])
                left_mouse_area = *left_mouse_area[:2], \
                    left_mouse_area[2] - left_mouse_area[0], left_mouse_area[3] - left_mouse_area[1]
                self.mng.rootEntity.militaryLayer.coverLayer['#selection'] = [(0, 255, 0), left_mouse_area]
        elif e0.type == pygame.MOUSEBUTTONDOWN:
            if e0.button == 1:
                mouse_loc = HomeUIState.get_grid_loc()
                self.lastClickedGridArea = mouse_loc
                self._leftMouseCircleArea = *e0.pos, 1, 1
        elif e0.type == pygame.MOUSEBUTTONUP:
            if e0.button == 1:
                mouse_loc = HomeUIState.get_grid_loc()
                last_click_area = *self.lastClickedGridArea, *mouse_loc
                self.lastClickedGridArea = min(last_click_area[0], last_click_area[2]), \
                    min(last_click_area[1], last_click_area[3]), \
                    max(last_click_area[0], last_click_area[2]), \
                    max(last_click_area[1], last_click_area[3])
                # self.lastLeftCircleArea = self._leftMouseCircleArea
                self._leftMouseCircleArea = None
                del self.mng.rootEntity.militaryLayer.coverLayer['#selection']

        # 状态切换逻辑
        if e0.type == pygame.MOUSEBUTTONUP and e0.button == 1:
            # 框选单位逻辑
            self.leftMouseCircledUnits.clear()
            player_mngr = self.mng.rootEntity.playerCtrlManager
            dn = self.mng.rootEntity.dataNodeRoot
            military_d = dn.militaryDict
            lock_points = self.mng.rootEntity.dataNodeRoot.runtimeNode.lockedPoints
            # 第一种遍历方式
            # for y in range(self.lastClickedArea[1], self.lastClickedArea[3]+1):
            #     for x in range(self.lastClickedArea[0], self.lastClickedArea[2]+1):
            #         if (x, y) in lock_points:
            #             continue
            #         tmp_d = military_d.get((x, y), None)
            #         if tmp_d is None:
            #             continue
            #         tmp_p = player_mngr[tmp_d.belong]
            #         if tmp_p is None:
            #             continue
            #         if tmp_p.isLocalPlayer:
            #             self.leftMouseCircledUnits.append((x, y))
            # 第二中遍历方式
            filter_rect = *HomeUIState.grid_loc_to_pos(self.lastClickedGridArea[:2]), \
                *HomeUIState.grid_loc_to_pos(self.lastClickedGridArea[2:])
            scene_pos = HomeUIState.scene_pos()
            # print(filter_rect, scene_pos)
            filter_rect = pygame.Rect(
                filter_rect[0]-scene_pos[0],
                filter_rect[1]-scene_pos[1],
                filter_rect[2]-filter_rect[0]+Config.MAP_BLOCK_SIZE[0],
                filter_rect[3]-filter_rect[1]+Config.MAP_BLOCK_SIZE[1])
            # print(filter_rect)
            for i in self.mng.rootEntity.militaryLayer.find_children_by_rect(filter_rect):
                tmp_d = military_d[i]
                tmp_p = player_mngr[tmp_d.belong]
                if tmp_p is None:
                    continue
                if tmp_d.loc in lock_points:
                    continue
                if tmp_p.isLocalPlayer:
                    self.leftMouseCircledUnits.append(tmp_d.id)

            # print(self.leftMouseCircledUnits)
            # 写入数据、跳转
            self.clickedBuilding = None
            self.clickedMilitary = None

            if len(self.leftMouseCircledUnits) > 1:
                self.mng.switch_state(BattleUIStates.groupCmd)
                return
            elif self.leftMouseCircledUnits:
                self.clickedMilitary = self.leftMouseCircledUnits[0]
                self.mng.switch_state(BattleUIStates.moveArea)
            elif self.lastClickedGridArea[2:] in self.mng.rootEntity.dataNodeRoot.buildingMap:
                self.clickedBuilding = self.lastClickedGridArea[2:]
                self.mng.switch_state(BattleUIStates.buyUnit)
            # # 单击逻辑
            # mouse_loc = self.lastClickedArea[2:]
            # if mouse_loc in self.mng.rootEntity.dataNodeRoot.runtimeNode.lockedPoints:
            #     return
            # if mouse_loc in self.mng.rootEntity.dataNodeRoot.militaryDict:
            #     self.clickedBuilding = None
            #     self.clickedMilitary = mouse_loc
            #     self.mng.switch_state(BattleUIStates.moveArea)
            # elif mouse_loc in self.mng.rootEntity.dataNodeRoot.buildingDict:
            #     self.clickedBuilding = mouse_loc
            #     self.clickedMilitary = None
            #     self.mng.switch_state(BattleUIStates.buyUnit)

    def handle_save(self):
        pass

    def handle_exit(self):
        pass

    def handle_status(self):
        self.mng.switch_state(BattleUIStates.status)


class GroupStateState(BattleUIStateBase):
    def __init__(self, mng):
        super().__init__(mng)
        self.mng.ui.statusView.handleHide = self.handle_close

    def handle_close(self):
        self.mng.switch_state(BattleUIStates.home)

    def active(self):
        self.mng.ui.switch_view(BattleUIViewType.status)
        self.mng.ui.statusView.set_text(f"""<h1>12</h1>""")


class MoveAreaUIState(BattleUIStateBase):
    def __init__(self, mng):
        super().__init__(mng)
        self.moveArea = {}
        self.clickedLocation = 0, 0
        self.engineId = None

    def active(self):
        dn = self.mng.rootEntity.dataNodeRoot
        unit_d = dn.militaryDict[self.mng.homeState.clickedMilitary]
        unit_move_p = dn.dataTable.movePropertyTable[dn.dataTable.militaryTable[unit_d.tableRowId].moveProperty]
        self.engineId = dn.dataTable.engineTable[unit_move_p.engineType].id

        self.moveArea = self.mng.rootEntity.gridController.count_move_area(
            unit_d.loc, self.engineId, unit_move_p.baseSpeed)
        # print(self.moveArea)

        self.mng.rootEntity.militaryLayer.coverLayer['moveArea']: List[Any] = \
            [(200, 100, 0, 100)] + list(self.moveArea.keys())

    def event(self, e0: pygame.event.Event):
        if e0.type == pygame.MOUSEBUTTONDOWN and e0.button == 1:

            # dn = self.mng.rootEntity.dataNodeRoot
            # dt = dn.dataTable
            # tmp_d = dn.militaryDict[self.mng.homeState.clickedMilitary]
            # tmp_target = HomeUIState.get_grid_loc()
            # tmp_road = self.mng.rootEntity.gridController.find_road(
            #     dt.movePropertyTable[dt.militaryTable[tmp_d.tableRowId].moveProperty].id,
            #     tmp_d.loc, tmp_target
            # )[0]
            # tmp_e = self.mng.rootEntity.militaryLayer.find_child_by_id(tmp_d.id)
            # tmp_e.set_task(MilitaryEntity.TASK_WAIT, tmp_road)
            # print(tmp_road)
            # self.mng.rootEntity.militaryLayer.coverLayer[f'-u-r{tmp_d.id}'] = [(255, 0, 0)] + tmp_road
            # return  # for debug group move
            self.clickedLocation = HomeUIState.get_grid_loc()
            if self.clickedLocation not in self.moveArea:
                print('home')
                self.mng.switch_state(BattleUIStates.home)
                self.mng.rootEntity.militaryLayer.coverLayer.clear()
            else:
                print('right m')
                self.mng.switch_state(BattleUIStates.chooseMenu)


class ChooseMenuUIState(BattleUIStateBase):
    def __init__(self, mng):
        super().__init__(mng)
        self.allRoads = []
        self.currentRoadIndex = 0
        self.mng.ui.chooseMenu.handleClick = self.handle_btn_click
        self.attackArea = None
        self.attackTargets = []

    def active(self):
        self.mng.ui.switch_view(BattleUIViewType.chooseMenu)
        #  计算、显示移动范围
        start_p = self.mng.rootEntity.dataNodeRoot.militaryDict[self.mng.homeState.clickedMilitary].loc
        end_p = self.mng.moveAreaState.clickedLocation
        if start_p == end_p:
            self.allRoads = [[start_p]]
        else:
            self.allRoads = self.mng.rootEntity.gridController.find_roads(
                self.mng.moveAreaState.moveArea, self.mng.moveAreaState.engineId,
                start_p, end_p
            )
        # print(self.allRoads)
        # print(self.allRoads)
        cover_layer = self.mng.rootEntity.militaryLayer.coverLayer
        cover_layer.clear()
        cover_layer['-road']: List[Any] = [(200, 100, 0, 100)] + self.allRoads[0]
        self.currentRoadIndex = 0
        #  设置菜单内容
        right_menu = {'wait': 'wait', 'back': 'back'}
        #  1.计算攻击距离
        dn = self.mng.rootEntity.dataNodeRoot
        tmp_nd = dn.militaryDict[start_p]
        tmp_dt = dn.dataTable
        tmp_td = tmp_dt.militaryTable[tmp_nd.tableRowId]
        if tmp_td.battleProperty != "":
            battle_property = tmp_dt.battlePropertyTable[tmp_td.battleProperty]
            self.attackArea = self.mng.rootEntity.gridController.count_attack_area(
                battle_property.attackMinDistance, battle_property.attackMaxDistance, start_p
            )
            military_nodes = dn.militaryDict
            self.attackTargets.clear()
            for i in self.attackArea:
                tmp_military = military_nodes.locDict.get(i, None)
                if tmp_military is None:
                    continue
                if dn.is_enemy(tmp_military.flagId, tmp_nd.flagId):
                    self.attackTargets.append(i)
            if self.attackTargets:
                right_menu['attack'] = 'attack'

        self.mng.ui.chooseMenu.set_buttons(right_menu)
        #  设置菜单位置
        p1 = HomeUIState.grid_loc_to_pos(start_p)
        p2 = HomeUIState.grid_loc_to_pos(end_p)
        center_p = pygame.display.get_window_size()
        center_p = center_p[0]//2, center_p[1]//2
        if ((center_p[0]-p1[0])**2+(center_p[1]-p1[1])**2)**.5 > ((center_p[0]-p2[0])**2+(center_p[1]-p2[1])**2)**.5:
            self.mng.ui.chooseMenu.set_pos(pygame.Rect(*p2, *Config.MAP_BLOCK_SIZE))
        else:
            self.mng.ui.chooseMenu.set_pos(pygame.Rect(*p1, *Config.MAP_BLOCK_SIZE))
        self.mng.ui.chooseMenu.show()

    def inactive(self):
        self.mng.rootEntity.militaryLayer.coverLayer.clear()
        self.mng.ui.chooseMenu.hide()

    def event(self, e0: pygame.event.Event):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            cover_layer = self.mng.rootEntity.militaryLayer.coverLayer
            if e0.button == 4:
                self.currentRoadIndex = (self.currentRoadIndex+1) % len(self.allRoads)
                cover_layer['-road']: List[Any] = [(200, 100, 0, 100)] + self.allRoads[self.currentRoadIndex]
            elif e0.button == 5:
                self.currentRoadIndex = (self.currentRoadIndex-1+len(self.allRoads)) % len(self.allRoads)
                cover_layer['-road']: List[Any] = [(200, 100, 0, 100)] + self.allRoads[self.currentRoadIndex]
            # elif e0.button == 1:
            #     mouse_loc = HomeUIState.get_grid_loc()
            #     if mouse_loc not in self.allRoads[self.currentRoadIndex]:
            #         self.mng.switch_state(BattleUIStates.moveArea)
        elif e0.type == pygame.KEYDOWN:
            if e0.key == pygame.K_ESCAPE:
                self.mng.switch_state(BattleUIStates.moveArea)

    def handle_btn_click(self, key):
        if key == 'back':
            self.mng.switch_state(BattleUIStates.moveArea)
        elif key == 'wait':
            tmp_d = self.mng.rootEntity.dataNodeRoot.militaryDict[self.allRoads[0][0]]
            tmp_e = self.mng.rootEntity.militaryLayer.find_child_by_id(tmp_d.id)
            # tmp_e.set_task(MilitaryEntity.TASK_WAIT, self.allRoads[self.currentRoadIndex])
            tmp_e.set_task(MilitaryEntity.TASK_WAIT, self.allRoads[self.currentRoadIndex][-1])
            self.mng.switch_state(BattleUIStates.home)
        elif key == 'attack':
            self.mng.switch_state(BattleUIStates.attackTarget)


class AttackTargetUIState(BattleUIStateBase):
    def __init__(self, mng):
        super().__init__(mng)

    def active(self):
        self.mng.ui.switch_view(BattleUIViewType.home)
        cover_layer = self.mng.rootEntity.militaryLayer.coverLayer
        cover_layer.clear()
        # print("target", self.mng.chooseMenuState.attackTargets)
        cover_layer['target']: List[Any] = [(200, 100, 0, 100)] + self.mng.chooseMenuState.attackTargets
