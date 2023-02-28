#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :ui_state.py
# @Time      :21/02/2023
# @Author    :russionbear
# @Function  :function
import pygame
import pygame_gui.elements

from qins_moon.core.director import UIStateManagerBase, IUIStateInterface, Director, UIStateMngManager
from qins_moon.core.asset import AssetPackage, AssetManager
from qins_moon.core.render.render import SceneManager
from qins_moon.core.ui_element import UserInterfaceManager
from qins_moon.core.utils.data_table_loader import DataTableLoader
from qins_moon.qm.polity.ui_element import EditHomeUI, ProjectUI, LayerUI
from qins_moon.qm.polity.config import Config
from qins_moon.qm.polity.render import PolityScene
from qins_moon.qm.polity.data_node import PolityDataNode, PolityDataTable, CityNode
from qins_moon.qm.polity.entity import PolityRootEntity
from qins_moon.qm.polity import ui_element


class TileMapEditUIStateMngr(UIStateManagerBase[IUIStateInterface]):
    UI_HOME = 0x11
    UI_PRJ = 0x12
    UI_LAYER = 0x13

    UI_STATE_HOME = 0x1
    UI_STATE_PRJ = 0x2

    def __init__(self):
        super().__init__()
        self.uiStorage = {
            TileMapEditUIStateMngr.UI_HOME: EditHomeUI(),
            TileMapEditUIStateMngr.UI_PRJ: ProjectUI(),
            TileMapEditUIStateMngr.UI_LAYER: LayerUI()
        }

        self[self.UI_STATE_HOME] = EditHomeUIState(self)
        self[self.UI_STATE_PRJ] = ProjectUIState(self)
        self.currentUIState = self[self.UI_STATE_HOME]

        # self.worldScene = TileMapEditScene()
        # SceneManager()[SYSTEM_KEY] = self.worldScene

    def switch_ui(self, key):
        mngr = UserInterfaceManager()
        if mngr.currentUI is not None:
            mngr.currentUI.hide()
        new_ui = self.uiStorage.get(key, None)
        if new_ui is not None:
            new_ui.show()
        mngr.switch_user_interface(new_ui)


class EditHomeUIState(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: TileMapEditUIStateMngr = mngr
        self.mngr.uiStorage[TileMapEditUIStateMngr.UI_HOME].handleToLayerButton = self.handle_show_sub_win
        self.mngr.uiStorage[TileMapEditUIStateMngr.UI_HOME].handleToProject = self.handle_to_project
        tmp_ui = self.mngr.uiStorage[TileMapEditUIStateMngr.UI_LAYER]
        tmp_ui.handleBack = self.handle_hide_sub_win
        tmp_ui.handleNew = self.handle_new_layer
        tmp_ui.handleDelete = self.handle_delete_layer
        tmp_ui.handleLayerChose = self.handle_layer_chose
        tmp_ui.handleSpriteChose = self.handle_sprite_chose
        tmp_ui.handleMouseIn = self.handle_mouse_in_layer
        tmp_ui.handleMouseOut = self.handle_mouse_out_layer

    def active(self):
        self.mngr.switch_ui(TileMapEditUIStateMngr.UI_HOME)

    def handle_to_project(self):
        self.mngr.switch_ui_state(TileMapEditUIStateMngr.UI_STATE_PRJ)

    def handle_show_sub_win(self):
        self.mngr.switch_ui(TileMapEditUIStateMngr.UI_LAYER)

    def handle_hide_sub_win(self):
        self.mngr.switch_ui(TileMapEditUIStateMngr.UI_HOME)

    def handle_delete_layer(self):
        pass

    def handle_new_layer(self):
        pass

    def handle_layer_chose(self, v):
        pass

    def handle_sprite_chose(self, v):
        pass

    def handle_mouse_in_layer(self):
        SceneManager()['SYSTEM_KEY'].camera.canScroll = False
        # self.mngr.worldScene.camera.canScroll = False

    def handle_mouse_out_layer(self):
        SceneManager()['SYSTEM_KEY'].camera.canScroll = True
        # self.mngr.worldScene.camera.canScroll = True


class ProjectUIState(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: TileMapEditUIStateMngr = mngr
        self.mngr.uiStorage[TileMapEditUIStateMngr.UI_PRJ].handleNew = self.handle_new
        self.mngr.uiStorage[TileMapEditUIStateMngr.UI_PRJ].handleBack = self.handle_back

    def active(self):
        self.mngr.switch_ui(TileMapEditUIStateMngr.UI_PRJ)

    def handle_back(self):
        print('back')
        self.mngr.switch_ui_state(TileMapEditUIStateMngr.UI_STATE_HOME)

    def handle_new(self):
        pass


class TestUIStateMngr(UIStateManagerBase[IUIStateInterface]):
    def __init__(self, config):
        super().__init__()
        self.config: Config = config
        self.rootEntity = PolityRootEntity(self.config, PolityRootEntity.make_map(self.config))

        self[1] = TroopInfoPolityUS(self)
        self.currentUIState = self[1]

    def init_data(self):
        self.rootEntity.init_load_asset()
        self.rootEntity.init_map()
        self.rootEntity.init_register()

    def active(self):
        super().active()
        if self.rootEntity.assetPackage is None:
            self.init_data()


class TestUIState(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: TestUIStateMngr = mngr


class PolityUIStateBase(IUIStateInterface):
    def __init__(self, mngr):
        self.mngr: PolityUIStateMngr = mngr


class PolityUIStateMngr(UIStateManagerBase[PolityUIStateBase]):
    STATE_HOME = 0x1
    STATE_ROAD_BUILD = 0x2
    STATE_FERRY = 0x3
    STATE_CITY = 0x4
    STATE_TROOP = 0x5
    STATE_TROOP_INFO = 0x6
    STATE_BATMEN = 0x7
    # STATE_BATMEN_CONVEY = 0x8

    def __init__(self, root_entity):
        super().__init__()
        self.rootEntity: PolityRootEntity = root_entity

        self[self.STATE_HOME] = HomePolityUS(self)
        self[self.STATE_ROAD_BUILD] = RoadBuildingPolityUS(self)
        self[self.STATE_FERRY] = FerryPolityUS(self)
        self[self.STATE_CITY] = CityInfoPolityUS(self)
        self[self.STATE_TROOP] = TroopMovePolityUS(self)
        self[self.STATE_TROOP_INFO] = TroopInfoPolityUS(self)
        self[self.STATE_BATMEN] = BatmenInfoPolityUS(self)

        # self.currentUIState = self[self.STATE_HOME]
        self.currentUIState = self[self.STATE_CITY]

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
        self.modeData = ['home', 'road', 'ferry', 'city', 'troop', 'troopInfo', 'batmen', 'batmenConvey']

    def active(self):
        self.homeUI = ui_element.HomePolicyUI(self.modeData)
        UserInterfaceManager().switch_user_interface(self.homeUI)
        self.homeUI.handleModeModify = self.handle_mode_change

    def inactive(self):
        self.homeUI.kill()

    def handle_mode_change(self, v):
        print(v)
        if v == 'home':
            return
        elif v == 'road':
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_ROAD_BUILD)
        elif v == 'ferry':
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_FERRY)
        elif v == 'city':
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_CITY)
        elif v == 'troop':
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_TROOP)
        elif v == 'troopInfo':
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_TROOP_INFO)
        elif v == 'batmen':
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_BATMEN)
        # elif v == 'batmenConvey':
        #     self.mngr.switch_ui_state(PolityUIStateMngr.STATE_BATMEN_CONVEY)


# ################################### operation #####################################

# troop


class TroopInfoPolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.troopInfoUI: ui_element.TroopInfoUI | None = None

    def active(self):
        self.troopInfoUI = ui_element.TroopInfoUI({'ff': 11})
        UserInterfaceManager().switch_user_interface(self.troopInfoUI)

    def inactive(self):
        self.troopInfoUI.kill()


class TroopMovePolityUS(PolityUIStateBase):
    pass


class TroopTaskPolityUS(PolityUIStateBase):
    pass


class TroopActionsPolityUS(PolityUIStateBase):
    pass


class TroopTargetPolityUS(PolityUIStateBase):
    pass


# city


class CityInfoPolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.cityInfoUI: ui_element.CityInfoPolicyUI | None = None
        self.currentCityNode: CityNode | None = None

    def show_city_info(self, city_d: CityNode):
        # last_loc = 0, 0
        if self.cityInfoUI is not None:
            last_loc = self.cityInfoUI.window.get_relative_rect()
            # last_loc = last_loc.x, last_loc.y
            self.cityInfoUI.kill()

        self.currentCityNode = city_d
        dn = self.mngr.rootEntity.rootDataNode
        city_table = dn.cityDict
        cities = [f"{v.name}-{k}" for k, v in dn.cityDict.idDict.items()]

        city_teams = {}  # 未过滤
        for loc in city_d.locations:
            _loc_teams = dn.teamDict[loc]
            if _loc_teams is None:
                continue
            for i in _loc_teams:
                target_name = f"-{i.moveTarget[0]}_{i.moveTarget[1]}"
                if i.moveTarget in city_table:
                    target_name = city_table[i.moveTarget].name+target_name
                city_teams[f"{i.name}-{i.id}"] = target_name

        print(city_teams)

        city_ferries = []
        for loc in city_d.locations:
            _loc_ferries = dn.ferryDict[loc]
            if _loc_ferries is None:
                continue
            for i in _loc_ferries:
                city_ferries.append(f"{i.name}-{i.id}")

        goods_price_dict = {}
        for k, v in dn.dataTable.goodsTable.nameDict.items():
            goods_price_dict[v] = v.price

        building_types = list(dn.dataTable.buildingTable.nameDict.keys())
        military_types = [k for k in dn.dataTable.militaryTable.nameDict.keys()]
        ferry_types = list(dn.dataTable.ferryTable.nameDict.keys())
        goods_types = list(dn.dataTable.goodsTable.nameDict.keys())

        city_buildings = [f"{k}-{v}" for k, v in city_d.buildings.items()]
        city_around_troops = []  # 未过滤
        __round_locations = set(city_d.locations)
        map_size = dn.map_size
        for i in city_d.locations:
            for drt in [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]:
                x_, y_ = drt[0] + i[0], drt[1]+i[1]
                if x_ < 0 or y_ < 0 or x_ >= map_size[0] or y_ >= map_size[1]:
                    continue
                __round_locations.add((x_, y_))
        for i in __round_locations:
            if i not in dn.troopDict:
                continue
            tmp_troop = dn.troopDict[i]
            city_around_troops.append(f"{tmp_troop.name}-{tmp_troop.id}")

        # general
        self.cityInfoUI = ui_element.CityInfoPolicyUI(military_types, cities, city_teams, building_types, ferry_types)
        UserInterfaceManager().switch_user_interface(self.cityInfoUI)
        self.cityInfoUI.populationLabel.set_text('population:'+str(city_d.population))
        self.cityInfoUI.popularSupportLabel.set_text('support:'+str(city_d.popularSupport))
        self.cityInfoUI.talentCapacityLabel.set_text('talent:'+str(city_d.talentCapacity))
        self.cityInfoUI.baseFightingCapacityLabel.set_text('fight:'+str(city_d.baseFightingCapacity))
        self.cityInfoUI.wallArmorLabel.set_text('wallArmor:'+str(city_d.wallArmor))

        # building
        self.cityInfoUI.maxBlockNuLabel.set_text(str(city_d.maxBlockNu))
        self.cityInfoUI.needResourceListView.set_item_list([k for k in city_d.needResource])
        # self.cityInfoUI.provideResourceListView.set_item_list(
        # [f"{k} x {v}" for k, v in city_d.provideResource.items()])
        self.cityInfoUI.buildingListView.set_item_list(city_buildings)

        # army
        self.cityInfoUI.destroyTroopListView.set_item_list(city_around_troops)

        # ferry
        self.cityInfoUI.ferryListView.set_item_list(city_ferries)
        self.cityInfoUI.storageListView.set_item_list(
            [f"{k}-{v}" for k, v in dn.storageDict[city_d.storageId].goods.items()])

        self.cityInfoUI.extraStorageListView.set_item_list([f"{i}-0" for i in goods_types])

        self.cityInfoUI.handleBack = self.handle_back
        self.cityInfoUI.handleModifyBuildingNu = self.handle_modify_building
        self.cityInfoUI.handleMakeArmy = self.handle_enlist_military
        self.cityInfoUI.handleDeleteTroop = self.handle_destroy_troop
        self.cityInfoUI.handleMakeFerry = self.handle_make_ferry
        self.cityInfoUI.handleDeleteFerry = self.handle_delete_ferry
        self.cityInfoUI.handleModifyExtra = self.handle_modify_extra
        self.cityInfoUI.handleModifyTeamTarget = self.handle_modify_team_target

    def active(self):
        pass

    def inactive(self):
        self.mngr.rootEntity.worldScene.canDrawCircle = True
        if self.cityInfoUI is not None:
            self.cityInfoUI.kill()

    def handle_back(self):
        self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)

    def event(self, e0):
        if e0.type == pygame.MOUSEBUTTONDOWN:
            if self.cityInfoUI is not None and self.cityInfoUI.window.get_relative_rect().collidepoint(*e0.pos):
                return
            grid_loc = self.mngr.rootEntity.worldScene.get_mouse_grid_loc()
            dn = self.mngr.rootEntity.rootDataNode
            if grid_loc not in dn.cityDict:
                return
            self.show_city_info(dn.cityDict[grid_loc])

    def handle_modify_building(self, t, v):
        if self.currentCityNode is None:
            return
        rlt = self.mngr.rootEntity.rootDataNode.modify_building_nu(self.currentCityNode.id, t, v)
        if rlt:
            self.show_city_info(self.currentCityNode)
            self.cityInfoUI.show_view(self.cityInfoUI.navBuildingBtn.text)
            # self.cityInfoUI.buildingListView.set_item_list(
            #     [f"{k}-{v}" for k, v in self.currentCityNode.buildings.items()])

    def handle_destroy_troop(self, v):
        pass

    def handle_enlist_military(self, force):
        pass

    def handle_delete_ferry(self, v):
        pass

    def handle_make_ferry(self, t):
        pass

    def handle_modify_extra(self, t, v):
        pass

    def handle_modify_team_target(self, t, v):
        pass

# road


class RoadBuildingPolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.roadUI: ui_element.RoadPolicyUI | None = None
        self.trafficTable = self.mngr.rootEntity.rootDataNode.dataTable.trafficTable
        self.CLEAR_KEY = 'clear'
        self.currentKey = self.CLEAR_KEY
        self.isToolBarHidden = False

    def active(self):
        self.roadUI = ui_element.RoadPolicyUI(self.CLEAR_KEY)
        UserInterfaceManager().switch_user_interface(self.roadUI)
        names = list(self.trafficTable.nameDict.keys())
        names.append(self.CLEAR_KEY)
        self.roadUI.roadTypeBtn.remove_options(self.roadUI.roadTypeBtn.options_list)
        self.roadUI.roadTypeBtn.add_options(names)
        self.roadUI.handleModify = self.handle_modify_key
        self.isToolBarHidden = False
        self.roadUI.show()

    def inactive(self):
        self.roadUI.kill()

    def handle_modify_key(self, v):
        self.currentKey = v

    def event(self, e0):
        if e0.type == pygame.KEYDOWN:
            if e0.key == pygame.K_TAB:
                if self.isToolBarHidden:
                    self.roadUI.show()
                else:
                    self.roadUI.hide()
                self.isToolBarHidden = not self.isToolBarHidden
            elif e0.key == pygame.K_ESCAPE:
                self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)
        elif e0.type == pygame.MOUSEBUTTONUP and not self.isToolBarHidden and e0.button == 1:
            area = self.mngr.rootEntity.worldScene.circle.get_current_circle_area()
            if area is None:
                return

            block_size = self.mngr.rootEntity.config.MAP_BLOCK_SIZE
            area = area[0]//block_size[0], area[1]//block_size[1], area[2]//block_size[0], area[3]//block_size[1]
            dn = self.mngr.rootEntity.rootDataNode
            map_size = dn.map_size
            if area[0] < 0:
                area = 0, *area[1:]
            if area[0] >= map_size[0]:
                area = map_size[0]-1, *area[1:]
            if area[1] < 0:
                area = area[0], 0, *area[2:]
            if area[1] >= map_size[1]:
                area = area[0], map_size[1]-1, *area[2:]

            key = 0 if self.currentKey == self.CLEAR_KEY else self.trafficTable[self.currentKey].id
            traffic_map_entity = self.mngr.rootEntity.trafficLayer
            for y in range(area[1], area[3]+1):
                for x in range(area[0], area[2]+1):
                    traffic_map_entity.refresh_node((x, y), key)


# ferry


class FerryPolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.ferriesUI: ui_element.FerriesPolityUI | None = None
        self.ferryInfoCmdUI: ui_element.FerryInfoCmdPolityUI | None = None

    def active(self):
        self.ferriesUI = ui_element.FerriesPolityUI()
        self.ferryInfoCmdUI = ui_element.FerryInfoCmdPolityUI()
        # self.ferryInfoCmdUI.hide()
        UserInterfaceManager().switch_user_interface(self.ferryInfoCmdUI)
        self.ferryInfoCmdUI.handleBack = self.handle_back

    def inactive(self):
        self.ferriesUI.kill()
        self.ferryInfoCmdUI.kill()

    def event(self, e0):
        if e0.type == pygame.KEYDOWN and e0.key == pygame.K_ESCAPE:
            self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)

    def handle_back(self):
        self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)


# batmen


class BatmenInfoPolityUS(PolityUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.teamsUI: ui_element.TeamsUI | None = None
        self.teamInfoUI: ui_element.TeamInfoUI | None = None
        self.teamConveyUI: ui_element.TeamConveyUI | None = None

    def active(self):
        self.teamsUI = ui_element.TeamsUI(['111', '222', '333'])
        self.teamInfoUI = ui_element.TeamInfoUI()
        self.teamConveyUI = ui_element.TeamConveyUI()

        UserInterfaceManager().switch_user_interface(self.teamsUI)
        self.teamInfoUI.handleBack = self.handle_back
        self.teamConveyUI.handleBack = self.handle_back

    def inactive(self):
        self.teamsUI.kill()
        self.teamInfoUI.kill()

    def handle_back(self):
        self.mngr.switch_ui_state(PolityUIStateMngr.STATE_HOME)

    def event(self, e0):
        if e0.type == pygame.KEYDOWN and e0.key == pygame.K_ESCAPE:
            self.handle_back()


# class BatmenActionsPolityUS(PolityUIStateBase):
#     pass
#
#
# class BatmenMovePolityUS(PolityUIStateBase):
#     pass


# ################################### statistics #####################################


if __name__ == '__main__':
    __director = Director()
    __config = Config()
    __director.init(
        __config.SYSTEM_KEY,
        PolityUIStateMngr(
            PolityRootEntity(__config, PolityRootEntity.make_map(__config))
        )
    )
    __director.run()
