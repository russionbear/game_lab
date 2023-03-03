#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :ui_state.py
# @Time      :21/02/2023
# @Author    :russionbear
# @Function  :function
# city info:
# military controller
# actions wait, attack

from typing import Dict

import numpy
import pygame

from qins_moon.core.director import UIStateManagerBase, IUIStateInterface, Director
from qins_moon.core.utils.math_tool import MathTool
from qins_moon.core.utils.detached_thread import DetachedThread
from qins_moon.core.ui_element import UserInterfaceManager
from qins_moon.qm.polity.config import Config
from qins_moon.qm.polity.entity import PolityRootEntity, TroopEntity
from qins_moon.qm.polity import ui_element


class PolityUIStateBase(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: PolityUIStateMngr = mngr


class PolityUIStateMngr(UIStateManagerBase[PolityUIStateBase]):
    STATE_HOME = 0x1
    STATE_ROAD_BUILD = 0x2
    STATE_CITY_TROOP_INFO = 0x3
    STATE_BUY = 0x4
    STATE_TROOP_MOVE = 0x5
    STATE_TROOP_ACTIONS = 0x6

    def __init__(self, root_entity):
        super().__init__()
        self.rootEntity: PolityRootEntity = root_entity

        self.homePolityUS = HomePolityUS(self)
        self.cityTroopInfoUS = CityTroopInfoPolityUS(self)
        self.buyTroopUS = BuyTroopPolityUS(self)
        self.troopMoveUS = TroopMovePolityUS(self)
        self.troopActionsUS = TroopActionsPolityUS(self)

        self[self.STATE_HOME] = self.homePolityUS
        self[self.STATE_CITY_TROOP_INFO] = self.cityTroopInfoUS
        self[self.STATE_BUY] = self.buyTroopUS
        self[self.STATE_TROOP_MOVE] = self.troopMoveUS
        self[self.STATE_TROOP_ACTIONS] = self.troopActionsUS

        self.currentUIState = self[self.STATE_HOME]

    def init_data(self):
        self.rootEntity.init_load_asset()
        self.rootEntity.init_map()
        self.rootEntity.init_register()

    def active(self):
        super().active()
        if self.rootEntity.assetPackage is None:
            self.init_data()


class HomePolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.homeUI: ui_element.HomePolicyUI | None = None
        self.modeData = ['view', 'opera']
        self.lastModeIndex = 0

    def active(self):
        self.homeUI = ui_element.HomePolicyUI(self.modeData, self.lastModeIndex)
        UserInterfaceManager().switch_user_interface(self.homeUI)

    def inactive(self):
        self.lastModeIndex = self.modeData.index(self.homeUI.modeBtn.selected_option)
        self.homeUI.kill()
        self.homeUI = None

    def event(self, e0):
        if hasattr(e0, 'pos'):
            if self.homeUI.modeBtn.get_relative_rect().collidepoint(*e0.pos):
                return

        if self.homeUI.modeBtn.selected_option == 'view':
            if e0.type == pygame.MOUSEBUTTONDOWN:
                dn = self.mngr.rootEntity.rootDataNode
                loc = self.mngr.rootEntity.worldScene.get_mouse_grid_loc()
                if loc not in dn.troopDict and loc not in dn.cityDict:
                    return
                self.mngr.cityTroopInfoUS.chosenGridLoc = loc
                self.mngr.switch_ui_state(PolityUIStateMngr.STATE_CITY_TROOP_INFO)

        elif self.homeUI.modeBtn.selected_option == 'opera':
            if e0.type == pygame.MOUSEBUTTONDOWN:
                dn = self.mngr.rootEntity.rootDataNode
                loc = self.mngr.rootEntity.worldScene.get_mouse_grid_loc()
                if loc not in dn.troopDict and loc in dn.cityDict:
                    self.mngr.buyTroopUS.chosenGridLoc = loc
                    self.mngr.switch_ui_state(PolityUIStateMngr.STATE_BUY)
                elif loc in dn.troopDict:
                    self.mngr.troopMoveUS.chosenGridLoc = loc
                    self.mngr.switch_ui_state(PolityUIStateMngr.STATE_TROOP_MOVE)


# ################################### operation #####################################

class CityTroopInfoPolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.cityTroopUI: ui_element.CityTroopInfoUI | None = None
        self.chosenGridLoc = None

    def show_view(self):
        if self.cityTroopUI:
            self.cityTroopUI.kill()
        if self.chosenGridLoc is None:
            return
        dn = self.mngr.rootEntity.rootDataNode
        if self.chosenGridLoc in dn.troopDict:
            troop_staffs = dn.troopDict[self.chosenGridLoc].staff
            troop_staffs = [f"{dn.personDict[i].name}-{dn.personDict[i].id}" for i in troop_staffs]
        else:
            troop_staffs = []

        self.cityTroopUI = ui_element.CityTroopInfoUI(troop_staffs)
        UserInterfaceManager().switch_user_interface(self.cityTroopUI)

        if self.chosenGridLoc in dn.cityDict:
            city_n = dn.cityDict[self.chosenGridLoc]
            flag_name = '中立' if city_n.flag == 0 else dn.groupDict[city_n.flag].name
            group_name = '中立' if city_n.belong == 0 else dn.groupDict[city_n.belong].name
            self.cityTroopUI.cityFlagLabel.set_text('flag:'+flag_name)
            self.cityTroopUI.cityBelongLabel.set_text("group:"+group_name)
            self.cityTroopUI.cityNameLabel.set_text("name:"+city_n.name)
            self.cityTroopUI.restFreezeBout.set_text("freeze:"+str(city_n.restFreezeBout))

            self.cityTroopUI.gdpLabel.set_text("gdp:"+str(city_n.gdp))
            self.cityTroopUI.restPayPerBout.set_text("restPay:"+str(city_n.restPayPerBout))
            self.cityTroopUI.wallArmor.set_text("wallArmor:"+str(city_n.wallArmor))

            self.cityTroopUI.navCityBtn.show()
            self.cityTroopUI.cityContainer.show()

        if self.chosenGridLoc in dn.troopDict:
            troop_n = dn.troopDict[self.chosenGridLoc]
            dt = dn.dataTable
            flag_name = '中立' if troop_n.flag == 0 else dn.groupDict[troop_n.flag].name
            group_name = '中立' if troop_n.belong == 0 else dn.groupDict[troop_n.belong].name
            self.cityTroopUI.troopFlagLabel.set_text('flag:'+flag_name)
            self.cityTroopUI.troopBelongLabel.set_text("group:"+group_name)
            self.cityTroopUI.troopNameLabel.set_text("name:"+troop_n.name)
            self.cityTroopUI.militaryForceListView.set_item_list([
                f"{dt.militaryTable[i.tableRowId].name}"
                f"-{i.currentBlood/dt.battlePropertyTable[dt.militaryTable[i.tableRowId].battleProperty].bloodValue}"
                f"-{i1}"
                for i1, i in enumerate(troop_n.militaryForce) if i.currentBlood != 0])
            self.cityTroopUI.movePropertyLabel.set_text('move:'+troop_n.moveProperty)
            self.cityTroopUI.viewPropertyLabel.set_text('view:'+troop_n.viewProperty)
            self.cityTroopUI.costPerBoutLabel.set_text('move:'+str(int(troop_n.costPerBout)))
            self.cityTroopUI.populationLabel.set_text(
                f'population:{int(troop_n.population)}/{int(dt.troopLevelTable[troop_n.tableRowId].population)}')

            self.cityTroopUI.navTroopBtn.show()
            self.cityTroopUI.troopContainer.show()
            self.cityTroopUI.cityContainer.hide()

        self.cityTroopUI.handleBack = self.handle_back
        self.cityTroopUI.handleLinkToPerson = self.handle_link_to_person

    def active(self):
        self.show_view()

    def inactive(self):
        if self.cityTroopUI:
            self.cityTroopUI.kill()
            self.cityTroopUI = None

    def event(self, e0):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            if self.cityTroopUI is None or self.cityTroopUI.window.get_relative_rect().collidepoint(*e0.pos):
                return
            grid_loc = self.mngr.rootEntity.worldScene.get_mouse_grid_loc()
            dn = self.mngr.rootEntity.rootDataNode
            if grid_loc not in dn.cityDict and grid_loc not in dn.troopDict:
                return

            if grid_loc in dn.cityDict:
                city_n = dn.cityDict[grid_loc]
                self.cityTroopUI.cityFlagLabel.set_text(dn.groupDict[city_n.flag].name)
                self.cityTroopUI.cityNameLabel.set_text(city_n.name)
                self.cityTroopUI.cityBelongLabel.set_text(dn.groupDict[city_n.belong].name)
                self.cityTroopUI.restFreezeBout.set_text(str(city_n.restPayPerBout))

                self.cityTroopUI.gdpLabel.set_text(str(city_n.gdp))
                self.cityTroopUI.restPayPerBout.set_text(str(city_n.restPayPerBout))
                self.cityTroopUI.wallArmor.set_text(str(city_n.wallArmor))
            else:
                self.cityTroopUI.navCityBtn.hide()

            if grid_loc in dn.troopDict:
                troop_n = dn.troopDict[grid_loc]
                self.cityTroopUI.troopFlagLabel.set_text(dn.groupDict[troop_n.flag].name)
            else:
                self.cityTroopUI.navTroopBtn.hide()

    def handle_back(self):
        self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)

    def handle_link_to_person(self, v):
        pass


class TroopMovePolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.chosenGridLoc = None
        self.moveArea: Dict[tuple, float] = {}
        self.costMap: numpy.ndarray | None = None

    def active(self):
        if self.chosenGridLoc is None:
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)
            return
        UserInterfaceManager().switch_user_interface(None)
        dn = self.mngr.rootEntity.rootDataNode
        troop_n = dn.troopDict[self.chosenGridLoc]
        if troop_n.isFrozen:
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)
            return
        self.moveArea, self.costMap = self.mngr.rootEntity.troopLayer.show_move_area(
            dn.troopDict[self.chosenGridLoc].id)
        if not self.moveArea:
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)
            return

    def inactive(self):
        self.mngr.rootEntity.troopLayer.coverLayer.clear()

    def event(self, e0):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            if e0.button == 3:
                self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)
            elif e0.button == 1:
                loc = self.mngr.rootEntity.worldScene.get_mouse_grid_loc()
                if loc not in self.moveArea:
                    self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)
                    return
                if loc in self.mngr.rootEntity.rootDataNode.troopDict:
                    return
                if self.mngr.rootEntity.rootDataNode.troopDict[self.chosenGridLoc].belong != self.mngr.rootEntity.userGroupId:
                    return
                self.mngr.troopActionsUS.chosenGridLoc = loc
                self.mngr.switch_ui_state(PolityUIStateMngr.STATE_TROOP_ACTIONS)


class TroopTaskPolityUS(PolityUIStateBase):
    pass


class TroopActionsPolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.chosenGridLoc = None
        self.troopActionUI: ui_element.TroopActionUI | None = None
        self.roads = []
        self.currentRoadIndex = 0
        self.attackTargets = []
        pass

    def active(self):
        DetachedThread().add_task({}, self.count_roads, self.handle_road_counted)
        dn = self.mngr.rootEntity.rootDataNode
        map_size = dn.map_size
        # troop_n = dn.troopDict[self.chosenGridLoc]
        self.attackTargets.clear()
        user_flag = dn.groupDict[self.mngr.rootEntity.userGroupId].flag
        for drt in [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]:
            x_, y_ = self.chosenGridLoc[0] + drt[0], self.chosenGridLoc[1] + drt[1]
            if x_ < 0 or y_ < 0 or x_ >= map_size[0] or y_ >= map_size[1]:
                continue
            if (x_, y_) not in dn.troopDict:
                continue
            if dn.is_enemy(user_flag, dn.troopDict[(x_, y_)].flag):
                self.attackTargets.append((x_, y_))

        actions = ['wait']
        if self.attackTargets:
            actions.append('attack')
        self.troopActionUI = ui_element.TroopActionUI(actions)
        UserInterfaceManager().switch_user_interface(self.troopActionUI)
        self.troopActionUI.handleBack = self.handle_back
        self.troopActionUI.handleClick = self.handle_action
        self.troopActionUI.rightMenu.disable()

        block_size = self.mngr.rootEntity.config.MAP_BLOCK_SIZE
        mouse_loc = block_size[0] * (self.chosenGridLoc[0]+.5), block_size[1] * (self.chosenGridLoc[1]*.5)
        world_scene_loc = self.mngr.rootEntity.worldScene.loc
        world_scene_size = self.mngr.rootEntity.worldScene.get_surface().get_size()
        world_scene_loc = world_scene_loc[0] - world_scene_size[0]//2, world_scene_loc[1] - world_scene_size[1]//2
        mouse_loc = mouse_loc[0] + world_scene_loc[0], mouse_loc[1] + world_scene_loc[1]
        screen_size = pygame.display.get_window_size()
        rm_size = self.troopActionUI.window.get_relative_rect().size
        # print(mouse_loc)
        # print(self.chosenGridLoc)
        if mouse_loc[0] > screen_size[0]/2:
            rm_loc = mouse_loc[0] - rm_size[0] / 2 - block_size[0]/2, mouse_loc[1]
        else:
            rm_loc = mouse_loc[0] + rm_size[0] / 2 + block_size[0]/2, mouse_loc[1]
        if rm_loc[0] - rm_size[0]//2 < 0:
            rm_loc = rm_size[0]//2, rm_loc[1]
        if rm_loc[1] - rm_size[1]//2 < 0:
            rm_loc = rm_loc[0], rm_size[1]//2
        if rm_loc[0] + rm_size[0]//2 > screen_size[0]:
            rm_loc = screen_size[0]-rm_size[0]//2, rm_loc[1]
        if rm_loc[1] + rm_size[1]//2 > screen_size[1]:
            rm_loc = rm_loc[0], screen_size[1] - rm_size[1]//2
        # print(rm_loc)
        self.troopActionUI.window.set_relative_position(rm_loc)

    def inactive(self):
        if self.troopActionUI:
            self.troopActionUI.kill()
            self.troopActionUI = None
        self.mngr.rootEntity.troopLayer.coverLayer.clear()

    def count_roads(self, **kwargs):
        self.roads.clear()
        return MathTool.count_all_roads(
            self.mngr.troopMoveUS.moveArea, self.mngr.troopMoveUS.chosenGridLoc,
            self.chosenGridLoc, self.mngr.troopMoveUS.costMap)

    def handle_road_counted(self, rlt):
        self.troopActionUI.rightMenu.enable()
        if self.troopActionUI is None or not rlt:
            return
        self.roads = rlt
        self.currentRoadIndex = 0
        self.mngr.rootEntity.troopLayer.show_road(self.roads[self.currentRoadIndex])

    def event(self, e0):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            if e0.button == 4:
                self.currentRoadIndex = (self.currentRoadIndex+1) % len(self.roads)
            elif e0.button == 5:
                self.currentRoadIndex = (self.currentRoadIndex+1+len(self.roads)) % len(self.roads)
            else:
                if e0.button == 3:
                    self.handle_back()
                return
            self.mngr.rootEntity.troopLayer.show_road(self.roads[self.currentRoadIndex])

    def handle_action(self, v):
        if not self.roads:
            return
        if v == 'wait':
            dn = self.mngr.rootEntity.rootDataNode
            # print(self.roads)
            road = self.roads[self.currentRoadIndex]
            troop_n = dn.troopDict[self.mngr.troopMoveUS.chosenGridLoc]
            troop_e: TroopEntity = self.mngr.rootEntity.troopLayer.find_child_by_id(troop_n.id)
            troop_e.gridMoveController.set_task(road)
            troop_e.currentTask = 'wait'
            dn.move_troop(troop_e.id, self.chosenGridLoc)
            troop_n.operaActed = True
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)
            return
        elif v == 'attack':
            print('attack')

    def handle_back(self):
        self.mngr.switch_ui_state(PolityUIStateMngr.STATE_TROOP_MOVE)


class TroopTargetPolityUS(PolityUIStateBase):
    pass


class BuyTroopPolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.chosenGridLoc = None
        self.buyTroopUI: ui_element.BuyTroopUI | None = None

    def active(self):
        if self.chosenGridLoc is None:
            self.handle_back()
            return
        dn = self.mngr.rootEntity.rootDataNode
        city_n = dn.cityDict[self.chosenGridLoc]
        distributions = {v: (dn.dataTable.troopLevelTable[v].distribution, dn.dataTable.troopLevelTable[v].cost_bill)
                         for v in dn.dataTable.groupAITable[
                             dn.groupDict[city_n.belong].groupAIId].troopLevels}
        self.buyTroopUI = ui_element.BuyTroopUI(distributions)
        UserInterfaceManager().switch_user_interface(self.buyTroopUI)
        self.buyTroopUI.groupBillLabel.set_text('bill:'+str(dn.groupDict[city_n.belong].bill))
        self.buyTroopUI.handleBack = self.handle_back
        self.buyTroopUI.handleSure = self.handle_sure

    def inactive(self):
        if self.buyTroopUI:
            self.buyTroopUI.kill()
            self.buyTroopUI = None

    def handle_sure(self):
        dn = self.mngr.rootEntity.rootDataNode
        group_n = dn.groupDict[dn.cityDict[self.chosenGridLoc].belong]
        troop_d = dn.dataTable.troopLevelTable[self.buyTroopUI.groupAiTypeBtn.selected_option]
        cost_bill = troop_d.cost_bill
        if cost_bill > group_n.bill:
            return
        troop_n = dn.make_troop(self.chosenGridLoc, troop_d.id)
        dn.appoint_troop(troop_n.id, group_n.id)
        self.mngr.rootEntity.troopLayer.refresh_node(troop_n.id)
        self.handle_back()

    def handle_back(self):
        self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)


# road


# class RoadBuildingPolityUS(PolityUIStateBase):
#     def __init__(self, mngr):
#         super().__init__(mngr)
#         self.roadUI: ui_element.RoadPolicyUI | None = None
#         self.trafficTable = self.mngr.rootEntity.rootDataNode.dataTable.trafficTable
#         self.CLEAR_KEY = 'clear'
#         self.currentKey = self.CLEAR_KEY
#         self.isToolBarHidden = False
#
#     def active(self):
#         self.roadUI = ui_element.RoadPolicyUI(self.CLEAR_KEY)
#         UserInterfaceManager().switch_user_interface(self.roadUI)
#         names = list(self.trafficTable.nameDict.keys())
#         names.append(self.CLEAR_KEY)
#         self.roadUI.roadTypeBtn.remove_options(self.roadUI.roadTypeBtn.options_list)
#         self.roadUI.roadTypeBtn.add_options(names)
#         self.roadUI.handleModify = self.handle_modify_key
#         self.isToolBarHidden = False
#         self.roadUI.show()
#
#     def inactive(self):
#         self.roadUI.kill()
#
#     def handle_modify_key(self, v):
#         self.currentKey = v
#
#     def event(self, e0):
#         if e0.type == pygame.KEYDOWN:
#             if e0.key == pygame.K_TAB:
#                 if self.isToolBarHidden:
#                     self.roadUI.show()
#                 else:
#                     self.roadUI.hide()
#                 self.isToolBarHidden = not self.isToolBarHidden
#             elif e0.key == pygame.K_ESCAPE:
#                 self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)
#         elif e0.type == pygame.MOUSEBUTTONUP and not self.isToolBarHidden and e0.button == 1:
#             area = self.mngr.rootEntity.worldScene.circle.get_current_circle_area()
#             if area is None:
#                 return
#
#             block_size = self.mngr.rootEntity.config.MAP_BLOCK_SIZE
#             area = area[0]//block_size[0], area[1]//block_size[1], area[2]//block_size[0], area[3]//block_size[1]
#             dn = self.mngr.rootEntity.rootDataNode
#             map_size = dn.map_size
#             if area[0] < 0:
#                 area = 0, *area[1:]
#             if area[0] >= map_size[0]:
#                 area = map_size[0]-1, *area[1:]
#             if area[1] < 0:
#                 area = area[0], 0, *area[2:]
#             if area[1] >= map_size[1]:
#                 area = area[0], map_size[1]-1, *area[2:]
#
#             key = 0 if self.currentKey == self.CLEAR_KEY else self.trafficTable[self.currentKey].id
#             traffic_map_entity = self.mngr.rootEntity.trafficLayer
#             for y in range(area[1], area[3]+1):
#                 for x in range(area[0], area[2]+1):
#                     traffic_map_entity.refresh_node((x, y), key)
#


# ################################### statistics #####################################


if __name__ == '__main__':
    __director = Director()
    __config = Config()
    __director.init(
        __config.SYSTEM_KEY,
        PolityUIStateMngr(
            PolityRootEntity(__config, PolityRootEntity.make_map(__config), 26020)
        )
    )
    __director.run()
