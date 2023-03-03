#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :ui_element.py
# @Time      :21/02/2023
# @Author    :russionbear
# @Function  :function
import re
from typing import List, Dict, Tuple

import pygame
import pygame_gui
from pygame_gui import elements

from qins_moon.core.ui_element import UserInterfaceBase


class HomePolicyUI(UserInterfaceBase):
    def __init__(self, modes, index):
        super().__init__()
        self.modeBtn: elements.UIDropDownMenu | None = None
        self.handleModeModify = None
        self.modeData = modes
        self.initModeDataIndex = index

    def resize(self, suf, ui_manager):
        self.modeBtn = elements.UIDropDownMenu(
            self.modeData, self.modeData[self.initModeDataIndex], pygame.Rect(0, 0, 100, 30), ui_manager
        )

    def set_mode(self, v):
        o_btn = self.modeBtn
        self.modeBtn = elements.UIDropDownMenu(
            self.modeData, v, self.modeBtn.get_relative_rect(), o_btn.ui_manager
        )
        o_btn.kill()
        if self.handleModeModify is not None:
            self.handleModeModify(v)

    def show(self):
        self.modeBtn.show()

    def hide(self):
        self.modeBtn.hide()

    def kill(self):
        if self.modeBtn is not None:
            self.modeBtn.kill()

    def event(self, e0):
        if e0.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if self.handleModeModify is not None:
                self.handleModeModify(e0.text)
        elif e0.type == pygame.KEYDOWN:
            if e0.key == pygame.K_TAB:
                # print(e0)
                options = self.modeBtn.options_list
                selected_o = self.modeBtn.selected_option
                index = options.index(selected_o)
                if e0.mod & pygame.KMOD_SHIFT:
                    index -= 1
                else:
                    index += 1
                self.modeBtn = elements.UIDropDownMenu(
                    options, options[(index + len(options)) % len(options)], self.modeBtn.get_relative_rect(),
                    self.modeBtn.ui_manager, self.modeBtn.ui_container
                )


# class CityInfoPolicyUI(UserInterfaceBase):
#     def __init__(self):
#         # # region ui
#         # self.window: elements.UIWindow | None = None
#         # self.peopleContainer: elements.UIScrollingContainer | None = None
#         # self.buildingsContainer: elements.UIScrollingContainer | None = None
#         # self.armyContainer: elements.UIScrollingContainer | None = None
#         # self.ferryContainer: elements.UIScrollingContainer | None = None
#         # # self.storageContainer: elements.UIScrollingContainer | None = None
#         #
#         # self.navPeopleBtn: elements.UIButton | None = None
#         # self.navBuildingBtn: elements.UIButton | None = None
#         # self.navArmyBtn: elements.UIButton | None = None
#         # self.navFerryBtn: elements.UIButton | None = None
#         #
#         # # people & general
#         # self.populationLabel: elements.UILabel | None = None
#         # self.popularSupportLabel: elements.UILabel | None = None
#         # self.talentCapacityLabel: elements.UILabel | None = None
#         # self.baseFightingCapacityLabel: elements.UILabel | None = None
#         # self.wallArmorLabel: elements.UILabel | None = None
#         #
#         # # buildings
#         # self.needResourceListView: elements.UISelectionList | None = None
#         # # self.provideResourceListView: elements.UISelectionList | None = None
#         #
#         # self.maxBlockNuLabel: elements.UILabel | None = None
#         # self.buildingListView: elements.UISelectionList | None = None
#         # self.buildingTypeBtn: elements.UIDropDownMenu | None = None
#         # self.buildingInputBtn: elements.UITextEntryLine | None = None
#         # self.buildingSureBtn: elements.UIButton | None = None
#         #
#         # # 己方army
#         # self.enlistMilitaryListView: elements.UISelectionList | None = None
#         # self.enlistMilitarySureBtn: elements.UIButton | None = None
#         # self.enlistMilitaryInputBtn: elements.UITextEntryLine | None = None
#         # self.enlistMilitaryCostLabel: elements.UILabel | None = None
#         #
#         # self.destroyTroopListView: elements.UISelectionList | None = None
#         # self.destroyTroopSureBtn: elements.UIButton | None = None
#         #
#         # # 己方 仓库中的ferry
#         # self.ferryListView: elements.UISelectionList | None = None
#         # self.ferryMakeTypeBtn: elements.UIDropDownMenu | None = None
#         # self.ferryMakeSureBtn: elements.UIButton | None = None
#         # self.ferryDeleteBtn: elements.UIButton | None = None
#         #
#         # self.storageListView: elements.UISelectionList | None = None
#         # self.extraStorageListView: elements.UISelectionList | None = None
#         # self.extraInputBtn: elements.UITextEntryLine | None = None
#         #
#         # self._teamItems = []
#         # self.teamContainer: elements.UIScrollingContainer | None = None
#         # # endregion
#         #
#         # # data
#         # self.militaryForceDict = {k: 0 for k in military_types}
#         # # self.militaryPriceDict: dict = military_price_dict
#         # self.extraStorageDict: dict = {k: 0 for k in military_types}
#         # self.allTargetCities: list = all_cities
#         # self.uiManager = None
#         # self.localInnerTeamTargets = team_targets
#         # self.buildingTyeData = building_types
#         # self.ferryTypeData = ferry_types
#         #
#         # # event and cached var
#         #
#         # self.handleModifyBuildingNu = None
#         #
#         # self.choseMilitaryType = None
#         # self.handleMakeArmy = None
#         #
#         # self.choseTroop = None
#         # self.handleDeleteTroop = None
#         #
#         # self.handleMakeFerry = None
#         #
#         # self.choseFerry = None
#         # self.handleDeleteFerry = None
#         #
#         # self.choseExtraGood = None
#         # self.handleModifyExtra = None
#         #
#         # self.handleModifyTeamTarget = None
#
#         self.window: elements.UIWindow | None = None
#         self.flagLabel: elements.UIWindow | None = None
#         self.nameLabel: elements.UIWindow | None = None
#         self.belongLabel: elements.UIWindow | None = None
#         self.restFreezeBout: elements.UILabel | None = None
#
#         self.gdpLabel: elements.UILabel | None = None
#         self.restPayPerBout: elements.UILabel | None = None
#         self.wallArmor: elements.UILabel | None = None
#
#         self.handleBack = None
#
#     def resize(self, suf, ui_manager):
#         self.window = elements.UIWindow(
#             pygame.Rect(0, 0, 600, 400), ui_manager
#         )
#         self.flagLabel = elements.UILabel(
#             pygame.Rect(0, 0, 150, 30), 'flag', ui_manager, container=self.window
#         )
#         self.nameLabel = elements.UILabel(
#             pygame.Rect(150, 0, 150, 30), 'name', ui_manager, container=self.window
#         )
#         self.belongLabel = elements.UILabel(
#             pygame.Rect(300, 0, 150, 30), 'group', ui_manager, container=self.window
#         )
#         self.restFreezeBout = elements.UILabel(
#             pygame.Rect(450, 0, 150, 30), 'freeze', ui_manager, container=self.window
#         )
#
#         self.gdpLabel = elements.UILabel(
#             pygame.Rect(0, 30, 150, 30), 'gdp', ui_manager, container=self.window
#         )
#         self.restPayPerBout = elements.UILabel(
#             pygame.Rect(150, 0, 150, 30), 'restPay', ui_manager, container=self.window
#         )
#         self.wallArmor = elements.UILabel(
#             pygame.Rect(0, 60, 150, 30), 'wallArmor', ui_manager, container=self.window
#         )
#         self.window.on_close_window_button_pressed = self.handle_close
#
#     def show(self):
#         self.window.show()
#
#     def handle_close(self):
#         self.hide()
#         if self.handleBack is not None:
#             self.handleBack()
#
#     def hide(self):
#         self.window.hide()
#
#
# class TroopInfoUI(UserInterfaceBase):
#     def __init__(self, staffs):
#         self.window: elements.UIWindow | None = None
#
#         self.flagLabel: elements.UILabel | None = None
#         self.nameLabel: elements.UILabel | None = None
#         self.belongLabel: elements.UILabel | None = None
#         self.headerPersonBtn: elements.UIDropDownMenu | None = None
#
#         self.militaryForceListView: elements.UISelectionList | None = None
#         self.staffListView: elements.UISelectionList | None = None
#
#         self.costPerBoutLabel: elements.UILabel | None = None
#         self.movePropertyLabel: elements.UILabel | None = None
#         self.battlePropertyLabel: elements.UILabel | None = None
#         self.viewPropertyLabel: elements.UILabel | None = None
#
#         self.populationLabel: elements.UILabel | None = None
#
#         self.staffData = staffs
#
#         self.handleLinkToPerson = None
#         self.handleBack = None
#
#     def resize(self, suf, ui_manager):
#         self.window = elements.UIWindow(
#             pygame.Rect(0, 0, 600, 400), ui_manager
#         )
#         self.flagLabel = elements.UILabel(
#             pygame.Rect(0, 0, 150, 30), 'flag', ui_manager, container=self.window
#         )
#         self.nameLabel = elements.UILabel(
#             pygame.Rect(150, 0, 150, 30), 'name', ui_manager, container=self.window
#         )
#         self.belongLabel = elements.UILabel(
#             pygame.Rect(300, 0, 150, 30), 'belong', ui_manager, container=self.window
#         )
#         self.headerPersonBtn = elements.UIDropDownMenu(
#             self.staffData, self.staffData[0], pygame.Rect(450, 0, 150, 30), ui_manager, container=self.window
#         )
#
#         self.militaryForceListView = elements.UISelectionList(
#             pygame.Rect(0, 30, 300, 200), [], ui_manager, container=self.window
#         )
#
#         self.costPerBoutLabel = elements.UILabel(
#             pygame.Rect(200, 30, 150, 30), 'cost', ui_manager, container=self.window
#         )
#         self.populationLabel = elements.UILabel(
#             pygame.Rect(200, 60, 150, 30), 'population', ui_manager, container=self.window
#         )
#         self.movePropertyLabel = elements.UILabel(
#             pygame.Rect(200, 90, 150, 30), 'move', ui_manager, container=self.window
#         )
#         self.battlePropertyLabel = elements.UILabel(
#             pygame.Rect(200, 120, 150, 30), 'battle', ui_manager, container=self.window
#         )
#         self.viewPropertyLabel = elements.UILabel(
#             pygame.Rect(200, 150, 150, 30), 'view', ui_manager, container=self.window
#         )
#
#         self.staffListView = elements.UISelectionList(
#             pygame.Rect(350, 30, 200, 300), self.staffData, ui_manager, container=self.window
#         )
#         self.window.on_close_window_button_pressed = self.handle_close
#
#     def show(self):
#         self.window.show()
#
#     def hide(self):
#         self.window.hide()
#
#     def event(self, e0):
#         if e0.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
#             if e0.ui_element == self.staffListView:
#                 if self.handleLinkToPerson is not None:
#                     self.handleLinkToPerson(e0.text)
#
#     def handle_close(self):
#         self.hide()
#         if self.handleBack is not None:
#             self.handleBack()


class CityTroopInfoUI(UserInterfaceBase):
    def __init__(self, troop_staffs):
        super().__init__()
        self.window: elements.UIWindow | None = None
        self.navCityBtn: elements.UIButton | None = None
        self.navTroopBtn: elements.UIButton | None = None
        self.troopContainer: elements.UIScrollingContainer | None = None
        self.cityContainer: elements.UIScrollingContainer | None = None

        self.cityFlagLabel: elements.UILabel | None = None
        self.cityNameLabel: elements.UILabel | None = None
        self.cityBelongLabel: elements.UILabel | None = None
        self.restFreezeBout: elements.UILabel | None = None

        self.gdpLabel: elements.UILabel | None = None
        self.restPayPerBout: elements.UILabel | None = None
        self.wallArmor: elements.UILabel | None = None

        self.troopFlagLabel: elements.UILabel | None = None
        self.troopNameLabel: elements.UILabel | None = None
        self.troopBelongLabel: elements.UILabel | None = None
        self.troopHeaderPersonBtn: elements.UIDropDownMenu | None = None

        self.militaryForceListView: elements.UISelectionList | None = None
        self.staffListView: elements.UISelectionList | None = None

        self.costPerBoutLabel: elements.UILabel | None = None
        self.movePropertyLabel: elements.UILabel | None = None
        self.battlePropertyLabel: elements.UILabel | None = None
        self.viewPropertyLabel: elements.UILabel | None = None

        self.populationLabel: elements.UILabel | None = None

        self.troopStaffData = troop_staffs

        self.handleLinkToPerson = None
        self.handleBack = None

    def resize(self, suf, ui_manager):
        self.window = elements.UIWindow(
            pygame.Rect(0, 0, 600, 430)
        )
        self.cityContainer = elements.UIScrollingContainer(
            pygame.Rect(0, 30, 600, 400), ui_manager, container=self.window
        )
        self.troopContainer = elements.UIScrollingContainer(
            pygame.Rect(0, 30, 600, 400), ui_manager, container=self.window
        )
        self.navCityBtn = elements.UIButton(
            pygame.Rect(0, 0, 100, 30), 'city', ui_manager, container=self.window
        )
        self.navTroopBtn = elements.UIButton(
            pygame.Rect(100, 0, 100, 30), 'troop', ui_manager, container=self.window
        )

        # region city
        self.cityFlagLabel = elements.UILabel(
            pygame.Rect(0, 0, 150, 30), 'flag', ui_manager, container=self.cityContainer
        )
        self.cityNameLabel = elements.UILabel(
            pygame.Rect(150, 0, 150, 30), 'name', ui_manager, container=self.cityContainer
        )
        self.cityBelongLabel = elements.UILabel(
            pygame.Rect(300, 0, 150, 30), 'group', ui_manager, container=self.cityContainer
        )
        self.restFreezeBout = elements.UILabel(
            pygame.Rect(450, 0, 150, 30), 'freeze', ui_manager, container=self.cityContainer
        )

        self.gdpLabel = elements.UILabel(
            pygame.Rect(0, 30, 150, 30), 'gdp', ui_manager, container=self.cityContainer
        )
        self.restPayPerBout = elements.UILabel(
            pygame.Rect(150, 30, 150, 30), 'restPay', ui_manager, container=self.cityContainer
        )
        self.wallArmor = elements.UILabel(
            pygame.Rect(0, 60, 150, 30), 'wallArmor', ui_manager, container=self.cityContainer
        )
        # endregion

        # region troop
        self.troopFlagLabel = elements.UILabel(
            pygame.Rect(0, 0, 150, 30), 'flag', ui_manager, container=self.troopContainer
        )
        self.troopNameLabel = elements.UILabel(
            pygame.Rect(150, 0, 150, 30), 'name', ui_manager, container=self.troopContainer
        )
        self.troopBelongLabel = elements.UILabel(
            pygame.Rect(300, 0, 150, 30), 'belong', ui_manager, container=self.troopContainer
        )
        self.troopHeaderPersonBtn = elements.UIDropDownMenu(
            self.troopStaffData if self.troopStaffData else [''],
            '' if not self.troopStaffData else self.troopStaffData[0],
            pygame.Rect(450, 0, 100, 30), ui_manager, container=self.troopContainer
        )

        self.militaryForceListView = elements.UISelectionList(
            pygame.Rect(0, 30, 200, 300), [], ui_manager, container=self.troopContainer
        )

        self.costPerBoutLabel = elements.UILabel(
            pygame.Rect(200, 30, 150, 30), 'cost', ui_manager, container=self.troopContainer
        )
        self.populationLabel = elements.UILabel(
            pygame.Rect(200, 60, 150, 30), 'population', ui_manager, container=self.troopContainer
        )
        self.movePropertyLabel = elements.UILabel(
            pygame.Rect(200, 90, 150, 30), 'move', ui_manager, container=self.troopContainer
        )
        self.battlePropertyLabel = elements.UILabel(
            pygame.Rect(200, 120, 150, 30), 'battle', ui_manager, container=self.troopContainer
        )
        self.viewPropertyLabel = elements.UILabel(
            pygame.Rect(200, 150, 150, 30), 'view', ui_manager, container=self.troopContainer
        )

        self.staffListView = elements.UISelectionList(
            pygame.Rect(350, 30, 200, 300), self.troopStaffData, ui_manager, container=self.troopContainer
        )
        # endregion

        self.window.on_close_window_button_pressed = self.handle_close

        self.navCityBtn.hide()
        self.navTroopBtn.hide()
        self.troopContainer.hide()
        self.cityContainer.hide()

    def handle_close(self):
        self.hide()
        if self.handleBack is not None:
            self.handleBack()

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.navCityBtn:
                self.cityContainer.show()
                self.troopContainer.hide()
            elif e0.ui_element == self.navTroopBtn:
                self.cityContainer.hide()
                self.troopContainer.show()
        elif e0.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if e0.ui_element == self.staffListView:
                if self.handleLinkToPerson is not None:
                    self.handleLinkToPerson(e0.text)


class TroopActionUI(UserInterfaceBase):
    def __init__(self, actions):
        super().__init__()
        self.window: elements.UIWindow | None = None
        self.rightMenu: elements.UISelectionList | None = None
        self.actionData = actions
        self.handleClick = None
        self.handleBack = None

    def resize(self, suf, ui_manager):
        self.window = elements.UIWindow(
            pygame.Rect(0, 0, 100, len(self.actionData) * 25), ui_manager
        )
        self.rightMenu = elements.UISelectionList(
            pygame.Rect(0, 0, 100, len(self.actionData) * 25), self.actionData,
            ui_manager, container=self.window
        )
        self.window.on_close_window_button_pressed = self.handle_close

    def event(self, e0):
        if e0.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if e0.ui_element == self.rightMenu:
                if self.handleClick is not None:
                    self.handleClick(e0.text)

    def handle_close(self):
        self.hide()
        if self.handleBack is not None:
            self.handleBack()


class TroopSupplyUI(UserInterfaceBase):
    def __init__(self, military_price_dict=None, military_nu=None):
        """
        choose one from two
        :param military_price_dict:
        :param military_nu:
        """
        super().__init__()
        self.window: elements.UIWindow | None = None
        self.militaryPriceListView: elements.UISelectionList | None = None
        self.militaryNuListView: elements.UISelectionList | None = None
        self.inputBtn: elements.UITextEntryLine | None = None
        self.sureBtn: elements.UIButton | None = None

        self.militaryPriceData = military_price_dict
        self.militaryNuData = military_nu

        self.handleBack = None
        self.handleSure = None

    def resize(self, suf, ui_manager):
        self.window = elements.UIWindow(
            pygame.Rect(0, 0, 600, 400), ui_manager
        )
        if self.militaryPriceData is not None:
            self.militaryPriceListView = elements.UISelectionList(
                pygame.Rect(0, 0, 200, 300), [f"{k}-{v}-0" for k, v in self.militaryPriceData.items()],
                ui_manager, container=self.window
            )
        else:
            self.militaryNuListView = elements.UISelectionList(
                pygame.Rect(0, 0, 200, 300), [f"{k}-{v}" for k, v in self.militaryNuData.items()],
                ui_manager, container=self.window
            )
        self.inputBtn = elements.UITextEntryLine(
            pygame.Rect(200, 0, 100, 30), ui_manager, container=self.window
        )
        self.sureBtn = elements.UIButton(
            pygame.Rect(200, 30, 100, 30), 'sure', ui_manager, container=self.window
        )
        self.window.on_close_window_button_pressed = self.handle_close

    def handle_close(self):
        self.hide()
        if self.handleBack is not None:
            self.handleBack()


class ConveyPersonUI(UserInterfaceBase):
    def __init__(self, troops):
        super().__init__()
        self.window: elements.UIWindow | None = None
        self.filterGroupsBtn: elements.UIDropDownMenu | None = None
        self.personListView: elements.UISelectionList | None = None
        self.currentGroupLabel: elements.UIDropDownMenu | None = None
        self.targetGroupBtn: elements.UIDropDownMenu | None = None

        self.troopsData = troops

        self.handleBack = None
        self.handleTargetGroupChose = None

    def resize(self, suf, ui_manager):
        self.window = elements.UIWindow(
            pygame.Rect(0, 0, 300, 400), ui_manager
        )
        self.filterGroupsBtn = elements.UIDropDownMenu(
            self.troopsData + [''], '', pygame.Rect(0, 0, 100, 30), ui_manager, container=self.window
        )
        self.personListView = elements.UISelectionList(
            pygame.Rect(0, 0, 200, 300), [], ui_manager, container=self.window
        )
        self.currentGroupLabel = elements.UILabel(
            pygame.Rect(200, 30, 100, 30), 'group', ui_manager, container=self.window
        )

        self.targetGroupBtn = elements.UIDropDownMenu(
            self.troopsData, self.troopsData[0], pygame.Rect(200, 60, 100, 30), ui_manager, container=self.window
        )
        self.window.on_close_window_button_pressed = self.handle_close

    def show(self):
        self.window.show()

    def hide(self):
        self.window.hide()

    def handle_close(self):
        self.hide()
        if self.handleBack is not None:
            self.handleBack()

    def event(self, e0):
        pass


class BuyTroopUI(UserInterfaceBase):
    def __init__(self, distributions):
        super().__init__()
        self.window: elements.UIWindow | None = None
        self.groupAiTypeBtn: elements.UIDropDownMenu | None = None
        self.militaryListView: elements.UISelectionList | None = None
        self.troopPriceLabel: elements.UILabel | None = None
        self.groupBillLabel: elements.UILabel | None = None
        self.sureBtn: elements.UIButton | None = None
        self.groupAiData: Dict[str, Tuple[dict, int]] = distributions

        self.handleSure = None
        self.handleBack = None

    def resize(self, suf, ui_manager):
        self.window = elements.UIWindow(
            pygame.Rect(0, 0, 600, 600), ui_manager, 'buy troop'
        )
        current_key = list(self.groupAiData.keys())[0]
        self.groupAiTypeBtn = elements.UIDropDownMenu(
            list(self.groupAiData.keys()), current_key, pygame.Rect(0, 0, 100, 30),
            ui_manager, container=self.window
        )
        self.troopPriceLabel = elements.UILabel(
            pygame.Rect(100, 0, 100, 30), str(self.groupAiData[current_key][1]), ui_manager, container=self.window
        )
        self.groupBillLabel = elements.UILabel(
            pygame.Rect(200, 0, 100, 30), 'bill', ui_manager, container=self.window
        )

        self.militaryListView = elements.UISelectionList(
            pygame.Rect(0, 30, 400, 400), [f"{k}-{v}" for k, v in self.groupAiData[current_key][0].items()],
            ui_manager, container=self.window
        )
        self.sureBtn = elements.UIButton(
            pygame.Rect(0, 500, 100, 30), 'sure', ui_manager, container=self.window
        )
        self.window.on_close_window_button_pressed = self.handle_close

    def handle_close(self):
        self.hide()
        if self.handleBack is not None:
            self.handleBack()

    def event(self, e0):
        if e0.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if e0.ui_element == self.groupAiTypeBtn:
                self.militaryListView.set_item_list([f"{k}-{v}" for k, v in self.groupAiData[e0.text][0].items()])
                self.troopPriceLabel.set_text("price:" + str(self.groupAiData[e0.text][1]))
        elif e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.sureBtn:
                if self.handleSure is not None:
                    self.handleSure()
