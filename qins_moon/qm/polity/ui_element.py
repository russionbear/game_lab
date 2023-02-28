#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :ui_element.py
# @Time      :21/02/2023
# @Author    :russionbear
# @Function  :function
import re

import pygame
import pygame_gui
from pygame_gui import elements

from qins_moon.core.ui_element import UserInterfaceBase


class EditHomeUI(UserInterfaceBase):
    def __init__(self):
        self.fileButton: elements.UIButton | None = None
        self.layerButton: elements.UIButton | None = None
        self.handleToProject = None
        self.handleToLayerButton = None

    def resize(self, suf, ui_manager):
        self.kill()
        self.fileButton = elements.UIButton(pygame.Rect(0, 0, 100, 30), 'project', ui_manager)
        self.layerButton = elements.UIButton(pygame.Rect(100, 0, 100, 30), 'layer', ui_manager)

    def kill(self):
        if self.fileButton:
            self.fileButton.kill()
        if self.layerButton:
            self.layerButton.kill()

    def show(self):
        if not self.fileButton:
            return
        self.fileButton.show()
        self.layerButton.show()

    def hide(self):
        self.layerButton.hide()
        self.fileButton.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.fileButton:
                if self.handleToProject is not None:
                    self.handleToProject()
            elif e0.ui_element == self.layerButton:
                if self.handleToLayerButton is not None:
                    self.handleToLayerButton()


class ProjectUI(UserInterfaceBase):
    def __init__(self):
        self.panel: elements.UIPanel | None = None
        self.nameInput: elements.UITextEntryLine | None = None
        self.pkgButton: elements.UIDropDownMenu | None = None
        self.tableButton: elements.UIDropDownMenu | None = None

        self.sizeXButton: elements.UIDropDownMenu | None = None
        self.sizeYButton: elements.UIDropDownMenu | None = None
        self.newButton: elements.UIButton | None = None

        self.backButton: elements.UIButton | None = None

        self.handleBack = None
        self.handleNew = None

    def resize(self, suf, ui_manager):
        if self.panel:
            self.kill()
        self.panel = elements.UIPanel(pygame.Rect(0, 0, 400, 300), manager=ui_manager, anchors={'center': "center"})
        tmp_rect = pygame.Rect(0, 0, 100, 30)
        tmp_rect.bottom = -30
        self.backButton = elements.UIButton(
            tmp_rect, 'back', ui_manager, container=self.panel, anchors={'centerx': 'centerx', 'bottom': 'bottom'})

        self.nameInput = elements.UITextEntryLine(
            pygame.Rect(0, 0, 200, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.pkgButton = elements.UIDropDownMenu(
            [''], '', pygame.Rect(0, 40, 200, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.tableButton = elements.UIDropDownMenu(
            [''], '', pygame.Rect(0, 80, 200, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.sizeXButton = elements.UIDropDownMenu(
            [str(2**i) for i in range(4, 14)], str(2**4), pygame.Rect(-50, 120, 100, 30), ui_manager,
            container=self.panel, anchors={'centerx': 'centerx'}
        )
        self.sizeYButton = elements.UIDropDownMenu(
            [str(2**i) for i in range(4, 14)], str(2**4), pygame.Rect(50, 120, 100, 30), ui_manager,
            container=self.panel, anchors={'centerx': 'centerx'}
        )
        self.newButton = elements.UIButton(
            pygame.Rect(0, 160, 100, 30), 'new', ui_manager, container=self.panel, anchors={'centerx': 'centerx'})

    def show(self):
        if not self.panel:
            return
        self.panel.show()

    def hide(self):
        self.panel.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.backButton:
                if self.handleBack is not None:
                    self.handleBack()
            elif e0.ui_element == self.handleNew:
                if self.handleNew is not None:
                    self.handleNew()


class LayerUI(UserInterfaceBase):
    def __init__(self):
        self.panel: elements.UIWindow | None = None
        self.spriteListView: elements.UISelectionList | None = None

        self.layerView: elements.UISelectionList | None = None
        self.layerNameInput: elements.UITextEntryLine | None = None
        self.layerSheetNameBtn: elements.UIDropDownMenu | None = None
        self.typeButton: elements.UIDropDownMenu | None = None
        self.zindexInput: elements.UITextEntryLine | None = None
        self.newButton: elements.UIButton | None = None

        self.deleteButton: elements.UIButton | None = None

        self.handleBack = None
        self.handleDelete = None
        self.handleNew = None
        self.handleLayerChose = None
        self.handleSpriteChose = None
        self.handleMouseIn = None
        self.handleMouseOut = None

    def resize(self, suf, ui_manager):
        if self.panel:
            self.kill()
        width = 220
        offset_y = 0
        self.panel = elements.UIWindow(pygame.Rect(10, 10, width, 500), manager=ui_manager)
        self.panel.on_close_window_button_pressed = self.handle_close
        self.layerView = elements.UISelectionList(
            pygame.Rect(offset_y, 0, width-10, 190), [], ui_manager, container=self.panel,
            anchors={'centerx': 'centerx'}
        )
        offset_y += 200
        self.layerSheetNameBtn = elements.UIDropDownMenu(
            [''], '', pygame.Rect(-60, offset_y, 60, 30), ui_manager, container=self.panel,
            anchors={'centerx': 'centerx'})
        self.zindexInput = elements.UITextEntryLine(
            pygame.Rect(0, offset_y, 60, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.typeButton = elements.UIDropDownMenu(
            [''], '', pygame.Rect(60, offset_y, 60, 30), ui_manager, container=self.panel,
            anchors={'centerx': 'centerx'})

        offset_y += 30
        self.layerNameInput = elements.UITextEntryLine(
            pygame.Rect(-60, offset_y, 60, 30), ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.newButton = elements.UIButton(
            pygame.Rect(0, offset_y, 60, 30), 'new', ui_manager, container=self.panel, anchors={'centerx': 'centerx'})
        self.deleteButton = elements.UIButton(
            pygame.Rect(60, offset_y, 60, 30), 'delete', ui_manager, container=self.panel,
            anchors={'centerx': 'centerx'})

        offset_y += 30
        self.spriteListView = elements.UISelectionList(
            pygame.Rect(0, offset_y, width, 190), [], ui_manager, container=self.panel, anchors={'centerx': 'centerx'}
        )

    def show(self):
        if not self.panel:
            return
        self.panel.show()

    def hide(self):
        self.panel.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            # print(e0)
            if self.panel.is_focused:
                if self.handleMouseIn:
                    self.handleMouseIn()
            else:
                if self.handleMouseOut:
                    self.handleMouseOut()

            if e0.ui_element == self.deleteButton:
                if self.handleDelete is not None:
                    self.handleDelete()
            elif e0.ui_element == self.newButton:
                if self.handleNew is not None:
                    self.handleNew()
            # elif e0.ui_element == self.panel.close_window_button:
            #     if self.handleBack is not None:
            #         self.handleBack()
        elif e0.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if e0.ui_element == self.layerView:
                if self.handleLayerChose is not None:
                    self.handleLayerChose(e0.text)
            elif e0.ui_element == self.spriteListView:
                if self.handleSpriteChose is not None:
                    self.handleSpriteChose(e0.text)

    def handle_close(self):
        if self.handleBack is not None:
            self.handleBack()
        self.panel.hide()


# class PolicyUIMngr()


class HomePolicyUI(UserInterfaceBase):
    def __init__(self, modes):
        self.modeBtn: elements.UIDropDownMenu | None = None
        self.handleModeModify = None
        self.modeData = modes

    def resize(self, suf, ui_manager):
        self.modeBtn = elements.UIDropDownMenu(
            self.modeData, self.modeData[0], pygame.Rect(0, 0, 100, 30), ui_manager
        )

    def show(self):
        self.modeBtn.show()

    def hide(self):
        self.modeBtn.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if self.handleModeModify is not None:
                self.handleModeModify(e0.text)


class RoadPolicyUI(UserInterfaceBase):
    def __init__(self, clear_key='clear'):
        self.roadTypeBtn: elements.UIDropDownMenu | None = None
        self.handleModify = None
        self.clearKey = clear_key

    def show(self):
        self.roadTypeBtn.show()

    def hide(self):
        self.roadTypeBtn.hide()

    def resize(self, suf, ui_manager):
        self.roadTypeBtn = elements.UIDropDownMenu(
            [self.clearKey], self.clearKey, pygame.Rect(10, 10, 100, 30), ui_manager)

    def event(self, e0):
        if e0.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if e0.ui_element == self.roadTypeBtn:
                if self.handleModify is not None:
                    self.handleModify(e0.text)


class CityInfoPolicyUI(UserInterfaceBase):
    def __init__(self, all_cities, military_types, team_targets, building_types, ferry_types):
        # region ui
        self.window: elements.UIWindow | None = None
        self.peopleContainer: elements.UIScrollingContainer | None = None
        self.buildingsContainer: elements.UIScrollingContainer | None = None
        self.armyContainer: elements.UIScrollingContainer | None = None
        self.ferryContainer: elements.UIScrollingContainer | None = None
        # self.storageContainer: elements.UIScrollingContainer | None = None

        self.navPeopleBtn: elements.UIButton | None = None
        self.navBuildingBtn: elements.UIButton | None = None
        self.navArmyBtn: elements.UIButton | None = None
        self.navFerryBtn: elements.UIButton | None = None

        # people & general
        self.populationLabel: elements.UILabel | None = None
        self.popularSupportLabel: elements.UILabel | None = None
        self.talentCapacityLabel: elements.UILabel | None = None
        self.baseFightingCapacityLabel: elements.UILabel | None = None
        self.wallArmorLabel: elements.UILabel | None = None

        # buildings
        self.needResourceListView: elements.UISelectionList | None = None
        # self.provideResourceListView: elements.UISelectionList | None = None

        self.maxBlockNuLabel: elements.UILabel | None = None
        self.buildingListView: elements.UISelectionList | None = None
        self.buildingTypeBtn: elements.UIDropDownMenu | None = None
        self.buildingInputBtn: elements.UITextEntryLine | None = None
        self.buildingSureBtn: elements.UIButton | None = None

        # 己方army
        self.enlistMilitaryListView: elements.UISelectionList | None = None
        self.enlistMilitarySureBtn: elements.UIButton | None = None
        self.enlistMilitaryInputBtn: elements.UITextEntryLine | None = None
        self.enlistMilitaryCostLabel: elements.UILabel | None = None

        self.destroyTroopListView: elements.UISelectionList | None = None
        self.destroyTroopSureBtn: elements.UIButton | None = None

        # 己方 仓库中的ferry
        self.ferryListView: elements.UISelectionList | None = None
        self.ferryMakeTypeBtn: elements.UIDropDownMenu | None = None
        self.ferryMakeSureBtn: elements.UIButton | None = None
        self.ferryDeleteBtn: elements.UIButton | None = None

        self.storageListView: elements.UISelectionList | None = None
        self.extraStorageListView: elements.UISelectionList | None = None
        self.extraInputBtn: elements.UITextEntryLine | None = None

        self._teamItems = []
        self.teamContainer: elements.UIScrollingContainer | None = None
        # endregion

        # data
        self.militaryForceDict = {k: 0 for k in military_types}
        # self.militaryPriceDict: dict = military_price_dict
        self.extraStorageDict: dict = {k: 0 for k in military_types}
        self.allTargetCities: list = all_cities
        self.uiManager = None
        self.localInnerTeamTargets = team_targets
        self.buildingTyeData = building_types
        self.ferryTypeData = ferry_types

        # event and cached var

        self.handleModifyBuildingNu = None

        self.choseMilitaryType = None
        self.handleMakeArmy = None

        self.choseTroop = None
        self.handleDeleteTroop = None

        self.handleMakeFerry = None

        self.choseFerry = None
        self.handleDeleteFerry = None

        self.choseExtraGood = None
        self.handleModifyExtra = None

        self.handleModifyTeamTarget = None

        self.handleBack = None

    def resize(self, suf, ui_manager):
        c_size = (600, 800)
        self.uiManager = ui_manager

        # region nav
        self.window = elements.UIWindow(pygame.Rect(0, 0, c_size[0]+30, c_size[1]+30), ui_manager)
        self.window.on_close_window_button_pressed = self.handle_close

        self.navPeopleBtn = elements.UIButton(
            pygame.Rect(0, 0, 100, 30), 'general', ui_manager, self.window)
        self.navBuildingBtn = elements.UIButton(
            pygame.Rect(100, 0, 100, 30), 'building', ui_manager, self.window)
        self.navArmyBtn = elements.UIButton(
            pygame.Rect(200, 0, 100, 30), 'army', ui_manager, self.window)
        self.navFerryBtn = elements.UIButton(
            pygame.Rect(300, 0, 100, 30), 'ferry', ui_manager, self.window)
        self.peopleContainer = elements.UIScrollingContainer(
            pygame.Rect(0, 30, *c_size), ui_manager, container=self.window)
        self.buildingsContainer = elements.UIScrollingContainer(
            pygame.Rect(0, 30, *c_size), ui_manager, container=self.window)
        self.armyContainer = elements.UIScrollingContainer(
            pygame.Rect(0, 30, *c_size), ui_manager, container=self.window)
        self.ferryContainer = elements.UIScrollingContainer(
            pygame.Rect(0, 30, *c_size), ui_manager, container=self.window)
        # endregion

        # region general
        self.populationLabel = elements.UILabel(
            pygame.Rect(0, 0, 150, 30), '100', ui_manager, container=self.peopleContainer)
        self.popularSupportLabel = elements.UILabel(
            pygame.Rect(150, 0, 150, 30), '100', ui_manager, container=self.peopleContainer)
        self.talentCapacityLabel = elements.UILabel(
            pygame.Rect(300, 0, 150, 30), '100', ui_manager, container=self.peopleContainer)
        self.baseFightingCapacityLabel = elements.UILabel(
            pygame.Rect(450, 0, 150, 30), '100', ui_manager, container=self.peopleContainer)

        self.wallArmorLabel = elements.UILabel(
            pygame.Rect(0, 30, 150, 30), '100', ui_manager, container=self.peopleContainer)
        # endregion

        # region building
        self.needResourceListView = elements.UISelectionList(
            pygame.Rect(0, 0, 300, 300), [], ui_manager, container=self.buildingsContainer
        )
        # self.provideResourceListView = elements.UISelectionList(
        #     pygame.Rect(300, 0, 300, 300), [], ui_manager, container=self.buildingsContainer
        # )

        self.maxBlockNuLabel = elements.UILabel(
            pygame.Rect(0, 300, 100, 30), '90', ui_manager, self.buildingsContainer
        )
        self.buildingInputBtn = elements.UITextEntryLine(
            pygame.Rect(100, 300, 100, 30), ui_manager, container=self.buildingsContainer
        )
        self.buildingTypeBtn = elements.UIDropDownMenu(
            self.buildingTyeData, self.buildingTyeData[0], pygame.Rect(200, 300, 100, 30), ui_manager,
            self.buildingsContainer
        )
        self.buildingSureBtn = elements.UIButton(
            pygame.Rect(300, 300, 100, 30), 'yes', ui_manager, container=self.buildingsContainer
        )
        self.buildingListView = elements.UISelectionList(
            pygame.Rect(100, 330, 400, 300), [], ui_manager, container=self.buildingsContainer
        )
        # endregion

        # region army
        self.destroyTroopListView = elements.UISelectionList(
            pygame.Rect(0, 0, 300, 300), [], ui_manager, container=self.armyContainer
        )
        self.destroyTroopSureBtn = elements.UIButton(
            pygame.Rect(300, 0, 100, 30), 'yes', ui_manager, container=self.armyContainer
        )
        self.enlistMilitaryListView = elements.UISelectionList(
            pygame.Rect(0, 330, 300, 300), [f"{k}-{v}" for k, v in self.militaryForceDict.items()],
            ui_manager, container=self.armyContainer
        )
        self.enlistMilitaryInputBtn = elements.UITextEntryLine(
            pygame.Rect(100, 300, 150, 30), ui_manager, container=self.armyContainer
        )
        self.enlistMilitarySureBtn = elements.UIButton(
            pygame.Rect(250, 300, 100, 30), 'enlist', ui_manager, container=self.armyContainer
        )
        # endregion

        # region ferry
        self.ferryListView = elements.UISelectionList(
            pygame.Rect(0, 30, 300, 300), [], ui_manager, container=self.ferryContainer
        )
        self.ferryDeleteBtn = elements.UIButton(
            pygame.Rect(0, 0, 100, 30), 'drop', ui_manager, container=self.ferryContainer
        )
        self.ferryMakeTypeBtn = elements.UIDropDownMenu(
            self.ferryTypeData, self.ferryTypeData[0], pygame.Rect(100, 0, 100, 30), ui_manager,
            container=self.ferryContainer
        )
        self.ferryMakeSureBtn = elements.UIButton(
            pygame.Rect(200, 0, 100, 30), 'make', ui_manager, container=self.ferryContainer
        )

        self.storageListView = elements.UISelectionList(
            pygame.Rect(0, 330, 300, 300), [], ui_manager, container=self.ferryContainer
        )
        self.extraInputBtn = elements.UITextEntryLine(
            pygame.Rect(300, 0, 100, 30), ui_manager, container=self.ferryContainer
        )
        # self.extraSureBtn = elements.UIButton(
        #     pygame.Rect(400, 0, 100, 30), 'save', ui_manager, container=self.ferryContainer
        # )
        self.extraStorageListView = elements.UISelectionList(
            pygame.Rect(300, 30, 300, 300), [f"{k}-{v}" for k, v in self.extraStorageDict.items()],
            ui_manager, container=self.ferryContainer
        )

        self.teamContainer = elements.UIScrollingContainer(
            pygame.Rect(300, 330, 300, 300), ui_manager, container=self.ferryContainer
        )
        self.set_ferry_teams(self.localInnerTeamTargets)
        # endregion

        self.buildingsContainer.hide()
        self.armyContainer.hide()
        self.ferryContainer.hide()

    def set_ferry_teams(self, team_targets):
        for i in self._teamItems:
            i.kill()
        self._teamItems.clear()
        i1 = 0
        for k, v in team_targets.items():
            tmp_label = elements.UILabel(
                pygame.Rect(0, i1*30, 100, 30), k, self.uiManager, container=self.teamContainer
            )
            tmp_btn = elements.UIDropDownMenu(
                self.allTargetCities+[''], v, pygame.Rect(100, i1*30, 100, 30),
                self.uiManager, container=self.teamContainer
            )
            self._teamItems.append(tmp_label)
            self._teamItems.append(tmp_btn)
            i1 += 1

    def show(self):
        self.window.show()

    def show_view(self, t):
        if t == self.navPeopleBtn.text:
            self.peopleContainer.show()
            self.buildingsContainer.hide()
            self.armyContainer.hide()
            self.ferryContainer.hide()
        elif t == self.navBuildingBtn.text:
            self.peopleContainer.hide()
            self.buildingsContainer.show()
            self.armyContainer.hide()
            self.ferryContainer.hide()
        elif t == self.navArmyBtn.text:
            self.peopleContainer.hide()
            self.buildingsContainer.hide()
            self.armyContainer.show()
            self.ferryContainer.hide()
        elif t == self.navFerryBtn.text:
            self.peopleContainer.hide()
            self.buildingsContainer.hide()
            self.armyContainer.hide()
            self.ferryContainer.show()

    def handle_close(self):
        self.hide()
        if self.handleBack is not None:
            self.handleBack()

    def hide(self):
        self.window.hide()

    def kill(self):
        super().kill()
        for i in self._teamItems:
            i.kill()
        self._teamItems.clear()

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element in [self.navFerryBtn, self.navBuildingBtn, self.navArmyBtn, self.navFerryBtn]:
                self.show_view(e0.ui_element.text)
            # if e0.ui_element == self.navPeopleBtn:
            #     self.peopleContainer.show()
            #     self.buildingsContainer.hide()
            #     self.armyContainer.hide()
            #     self.ferryContainer.hide()
            # elif e0.ui_element == self.navBuildingBtn:
            #     self.peopleContainer.hide()
            #     self.buildingsContainer.show()
            #     self.armyContainer.hide()
            #     self.ferryContainer.hide()
            # elif e0.ui_element == self.navArmyBtn:
            #     self.peopleContainer.hide()
            #     self.buildingsContainer.hide()
            #     self.armyContainer.show()
            #     self.ferryContainer.hide()
            # elif e0.ui_element == self.navFerryBtn:
            #     self.peopleContainer.hide()
            #     self.buildingsContainer.hide()
            #     self.armyContainer.hide()
            #     self.ferryContainer.show()

            elif e0.ui_element == self.buildingSureBtn:
                if self.handleModifyBuildingNu is not None:
                    nu = self.buildingInputBtn.get_text()
                    try:
                        nu = int(nu)
                    except ValueError:
                        return
                    self.handleModifyBuildingNu(self.buildingTypeBtn.selected_option, nu)
            elif e0.ui_element == self.enlistMilitarySureBtn:
                if self.handleMakeArmy is not None and sum(self.militaryForceDict.values()) > 0:
                    self.handleMakeArmy(self.militaryForceDict)
            elif e0.ui_element == self.destroyTroopSureBtn:
                if self.choseTroop is not None and self.handleDeleteTroop is not None:
                    self.handleDeleteTroop(self.choseTroop)

            elif e0.ui_element == self.ferryMakeSureBtn:
                if self.handleMakeFerry is not None:
                    self.handleMakeFerry(self.ferryMakeTypeBtn.selected_option)
            elif e0.ui_element == self.ferryDeleteBtn:
                if self.choseFerry is not None and self.handleDeleteFerry is not None:
                    self.handleDeleteFerry(self.choseFerry)

        elif e0.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if e0.ui_element == self.ferryListView:
                index = e0.text.rindex('-') + 1
                id_ = int(e0.text[index:])
                self.choseFerry = id_
            elif e0.ui_element == self.destroyTroopListView:
                index = e0.text.rindex('-') + 1
                id_ = int(e0.text[index:])
                self.choseTroop = id_
            elif e0.ui_element == self.enlistMilitaryListView:
                index = e0.text.rindex('-') + 1
                id_ = int(e0.text[index:])
                self.choseMilitaryType = id_
            elif e0.ui_element == self.buildingListView:
                index = e0.text.rindex('-') + 1
                id_ = int(e0.text[index:])
                self.buildingInputBtn.set_text(str(id_))

        elif e0.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if e0.ui_element == self.enlistMilitaryInputBtn:
                if self.choseMilitaryType is None:
                    return
                try:
                    nu = int(e0.text)
                except ValueError:
                    return
                old_v = f"{self.choseMilitaryType}-{self.militaryForceDict[self.choseMilitaryType]}"
                self.militaryForceDict[self.choseMilitaryType] = nu
                new_v = f"{self.choseMilitaryType}-{self.militaryForceDict[self.choseMilitaryType]}"
                self.enlistMilitaryListView.remove_items([old_v])
                self.enlistMilitaryListView.add_items([new_v])
                # cost = 0
                # for k, v in self.militaryForceDict.items():
                #     cost += v * self.militaryPriceDict[k]
                # self.enlistMilitaryCostLabel.set_text(str(cost))
            if e0.ui_element == self.extraInputBtn:
                if self.choseExtraGood is None:
                    return
                v = e0.text
                try:
                    v = int(v)
                except ValueError:
                    return
                if self.handleModifyExtra is not None:
                    self.handleModifyExtra(self.choseExtraGood, v)

        elif e0.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if e0.ui_element == self.buildingTypeBtn:
                for i in self.buildingListView.item_list:
                    if re.match(f'^{e0.text}-\d+$', i['text']) is not None:
                        index = i['text'].rindex('-') + 1
                        id_ = int(i['text'][index:])
                        self.buildingInputBtn.set_text(str(id_))
                        break

                else:
                    self.buildingInputBtn.set_text('0')
            else:
                length = len(self._teamItems) // 2
                for i in range(length):
                    if self._teamItems[i * 2 + 1] == e0.ui_element:
                        if self.handleModifyTeamTarget is not None:
                            self.handleModifyTeamTarget(self._teamItems[i * 2].text, e0.text)
                        break


class FerriesPolityUI(UserInterfaceBase):
    def __init__(self):
        self.listView: elements.UISelectionList | None = None
        self.handleClick = None

    def resize(self, suf, ui_manager):
        self.listView = elements.UISelectionList(pygame.Rect(0, 0, 100, 300), [], ui_manager)

    def show(self):
        self.listView.show()

    def hide(self):
        self.listView.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if e0.ui_element == self.listView:
                if self.handleClick is not None:
                    self.handleClick(e0.text)


class FerryInfoCmdPolityUI(UserInterfaceBase):
    def __init__(self):
        self.container: elements.UIWindow | None = None
        self.belongLabel: elements.UILabel | None = None
        self.flagLabel: elements.UILabel | None = None
        self.nameLabel: elements.UILabel | None = None

        self.roadListView: elements.UISelectionList | None = None
        self.newStationBtn: elements.UIButton | None = None
        self.deleteStationBtn: elements.UIButton | None = None
        self.setRoadModeBtn: elements.UIButton | None = None

        self._showInfoBtn: elements.UILabel | None = None
        self.storageListView: elements.UISelectionList | None = None
        self.teamListView: elements.UISelectionList | None = None

        self.MINI_MODE = 500, 330
        self.NORMAL_MODE = 600, 700

        self.choseStation = None
        self.choseTeam = None

        self.handleNewStation = None
        self.handleDelStation = None
        self.handleModifyMode = None
        self.handleLinkToTeam = None
        self.handleBack = None

    def show(self):
        self.container.show()

    def hide(self):
        if self.container:
            self.container.hide()

    def handle_close(self):
        self.hide()
        if self.handleBack is not None:
            self.handleBack()

    def add_new_station(self, v):
        l0 = self.roadListView.item_list[:]
        if self.choseStation is None:
            l0.append(v)
        else:
            index = l0.index(self.choseStation)
            l0.insert(index+1, v)
        self.roadListView.set_item_list(l0)

    def resize(self, suf, ui_manager):
        self.container = elements.UIWindow(
            pygame.Rect(0, 0, *self.MINI_MODE)
        )
        self.container.on_close_window_button_pressed = self.handle_close
        self.flagLabel = elements.UILabel(
            pygame.Rect(0, 0, 100, 30), 'flag', ui_manager, container=self.container
        )
        self.nameLabel = elements.UILabel(
            pygame.Rect(100, 0, 100, 30), 'name', ui_manager, container=self.container
        )
        self.belongLabel = elements.UILabel(
            pygame.Rect(200, 0, 100, 30), 'belong', ui_manager, container=self.container
        )
        self._showInfoBtn = elements.UIButton(
            pygame.Rect(300, 0, 100, 30), 'more', ui_manager, container=self.container
        )

        self.roadListView = elements.UISelectionList(
            pygame.Rect(0, 30, 300, 300), [], ui_manager, container=self.container
        )
        self.newStationBtn = elements.UIButton(
            pygame.Rect(300, 30, 100, 30), 'new', ui_manager, container=self.container
        )
        self.deleteStationBtn = elements.UIButton(
            pygame.Rect(300, 60, 100, 30), 'del', ui_manager, container=self.container
        )
        self.setRoadModeBtn = elements.UIButton(
            pygame.Rect(300, 90, 100, 30), 'loop', ui_manager, container=self.container
        )

        self.storageListView = elements.UISelectionList(
            pygame.Rect(0, 330, 300, 300), [], ui_manager, container=self.container
        )
        self.teamListView = elements.UISelectionList(
            pygame.Rect(300, 330, 300, 300), [], ui_manager, container=self.container
        )

    def event(self, e0):
        if e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.newStationBtn:
                if self.handleNewStation is not None:
                    self.handleNewStation()
            elif e0.ui_element == self.deleteStationBtn:
                if self.handleDelStation is not None:
                    self.handleDelStation()
            elif e0.ui_element == self.setRoadModeBtn:
                if self.handleModifyMode is not None:
                    self.handleModifyMode()
            elif e0.ui_element == self._showInfoBtn:
                if self.container.get_relative_rect().size == self.MINI_MODE:
                    self.container.set_dimensions(self.NORMAL_MODE)
                else:
                    self.container.set_dimensions(self.MINI_MODE)
        elif e0.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if e0.ui_element == self.roadListView:
                self.choseStation = e0.text

        elif e0.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if e0.ui_element == self.teamListView:
                if self.handleLinkToTeam is not None:
                    self.handleLinkToTeam(e0.text)


class TroopInfoUI(UserInterfaceBase):
    def __init__(self, type_need):
        self.container: elements.UIWindow | None = None
        self.militaryForceListView: elements.UISelectionList | None = None
        self.costPerTickLabel: elements.UILabel | None = None
        self.movePropertyLabel: elements.UILabel | None = None
        self.battlePropertyLabel: elements.UILabel | None = None

        self.flagLabel: elements.UILabel | None = None
        self.nameLabel: elements.UILabel | None = None
        self.belongLabel: elements.UILabel | None = None

        self.staffListView: elements.UISelectionList | None = None
        self.enlistTalentBtn: elements.UIButton | None = None

        # self.setTroopModelBtn: elements.UIButton | None = None
        self._showMoreBtn: elements.UIButton | None = None

        # self.supplyFromBtn: elements.UIButton | None = None
        # self.supplyToBtn: elements.UIButton | None = None

        # self.actionContainer: elements.UIScrollingContainer | None = None
        # self._actionItems = []
        self.typeNeedListView: elements.UISelectionList | None = None
        self.typeNeedInputBtn: elements.UIButton | None = None

        self.uiManager = None
        # self.actionCostDict: dict = action_cost_dict

        self.MINI_VIEW_SIZE = 800, 390
        self.NORMAL_VIEW_SIZE = 800, 700
        self.typeNeedDict = type_need

        self.handleLinkToStaff = None
        self.handleEnlistTalent = None
        # self.handleModifyMode = None
        # self.handleModifyFromCity = None
        # self.handleModifyToCity = None
        # self.handleActionModify = None
        self.choseTypeNeed = None
        self.handleTypeNeedModify = None

    def resize(self, suf, ui_manager):
        self.container = elements.UIWindow(
            pygame.Rect(0, 0, *self.MINI_VIEW_SIZE), ui_manager
        )
        self.militaryForceListView = elements.UISelectionList(
            pygame.Rect(300, 0, 300, 300), [], ui_manager, container=self.container
        )

        self.flagLabel = elements.UILabel(
            pygame.Rect(0, 0, 100, 30), 'flag', ui_manager, container=self.container
        )
        self.nameLabel = elements.UILabel(
            pygame.Rect(100, 0, 100, 30), 'name', ui_manager, container=self.container
        )
        self.belongLabel = elements.UILabel(
            pygame.Rect(200, 0, 100, 30), 'belong', ui_manager, container=self.container
        )

        self.costPerTickLabel = elements.UILabel(
            pygame.Rect(0, 30, 100, 30), '', ui_manager, container=self.container
        )
        self.movePropertyLabel = elements.UILabel(
            pygame.Rect(100, 30, 100, 30), '', ui_manager, container=self.container
        )
        self.battlePropertyLabel = elements.UILabel(
            pygame.Rect(200, 30, 100, 30), '', ui_manager, container=self.container
        )

        # self.setTroopModelBtn = elements.UIButton(
        #     pygame.Rect(0, 60, 100, 30), 'loop', ui_manager, container=self.container
        # )
        self.enlistTalentBtn = elements.UIButton(
            pygame.Rect(100, 60, 100, 30), '', ui_manager, container=self.container
        )
        self._showMoreBtn = elements.UIButton(
            pygame.Rect(200, 60, 100, 30), 'more', ui_manager, container=self.container
        )

        self.staffListView = elements.UISelectionList(
            pygame.Rect(0, 90, 300, 210), [], ui_manager, container=self.container
        )

        # self.supplyFromBtn = elements.UIDropDownMenu(
        #     [''], '', pygame.Rect(0, 300, 100, 30), ui_manager, container=self.container
        # )
        # self.supplyToBtn = elements.UIDropDownMenu(
        #     [''], '', pygame.Rect(100, 300, 100, 30), ui_manager, container=self.container
        # )
        #
        # self.actionContainer = elements.UIScrollingContainer(
        #     pygame.Rect(0, 330, 300, 300), ui_manager, container=self.container
        # )
        # self.set_actions(self.actionCostDict)
        self.typeNeedListView = elements.UISelectionList(
            pygame.Rect(0, 330, 300, 300), list(self.typeNeedDict.keys()), ui_manager, container=self.container
        )
        self.typeNeedInputBtn = elements.UITextEntryLine(
            pygame.Rect(0, 300, 100, 30), ui_manager, container=self.container
        )

    # def set_actions(self, action_cost_dict):
    #     for i in self._actionItems:
    #         i.kill()
    #     self._actionItems.clear()
    #
    #     i1 = 0
    #     for k, v in action_cost_dict.items():
    #         tmp_btn = elements.UIButton(
    #             pygame.Rect(0, i1*30, 100, 30), f"{k}-{v}", self.uiManager, container=self.actionContainer
    #         )
    #         self._actionItems.append(tmp_btn)
    #         i1 += 1

    # def kill(self):
    #     super().kill()
    #     # self.set_actions({})

    def show(self):
        self.container.show()

    def hide(self):
        self.container.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if e0.ui_element == self.staffListView:
                if self.handleLinkToStaff is not None:
                    self.handleLinkToStaff(e0.text)
        elif e0.type == pygame_gui.UI_BUTTON_PRESSED:
            if e0.ui_element == self.enlistTalentBtn:
                if self.handleEnlistTalent is not None:
                    self.handleEnlistTalent()
            # elif e0.ui_element == self.setTroopModelBtn:
            #     if self.handleModifyMode is not None:
            #         self.handleModifyMode()
            elif e0.ui_element == self._showMoreBtn:
                if self.container.get_relative_rect().size == self.MINI_VIEW_SIZE:
                    self.container.set_dimensions(self.NORMAL_VIEW_SIZE)
                else:
                    self.container.set_dimensions(self.MINI_VIEW_SIZE)
            # else:
            #     for i in self._actionItems:
            #         if i == e0.ui_element:
            #             if self.handleActionModify is not None:
            #                 self.handleActionModify(i.text)
            #             break
        elif e0.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            # if e0.ui_element == self.supplyFromBtn:
            #     if self.handleModifyFromCity is not None:
            #         self.handleModifyFromCity(e0.text)
            # elif e0.ui_element == self.supplyToBtn:
            #     if self.handleModifyToCity is not None:
            #         self.handleModifyToCity(e0.text)
            pass
        elif e0.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if e0.ui_element == self.typeNeedListView:
                self.choseTypeNeed = e0.text
                self.typeNeedInputBtn.set_text(str(self.typeNeedDict[e0.text]))

        elif e0.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if e0.ui_element == self.typeNeedListView:
                if self.choseTypeNeed is None:
                    return
                if self.handleTypeNeedModify is not None:
                    try:
                        nu = int(e0.text)
                    except ValueError:
                        return
                    self.handleTypeNeedModify(self.choseTypeNeed, nu)


class TroopActionUI(UserInterfaceBase):
    def __init__(self, actions):
        self.rightMenu: elements.UISelectionList | None = None
        self.actionData = actions
        self.handleClick = None

    def resize(self, suf, ui_manager):
        self.rightMenu = elements.UISelectionList(
            pygame.Rect(0, 0, 100, len(self.actionData)*25), self.actionData, ui_manager
        )

    def show(self):
        self.rightMenu.show()

    def hide(self):
        self.rightMenu.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if e0.ui_element == self.rightMenu:
                if self.handleClick is not None:
                    self.handleClick(e0.text)


class TeamsUI(UserInterfaceBase):
    def __init__(self, teams):
        self.rightMenu: elements.UISelectionList | None = None
        self.teamData = teams
        self.handleClick = None

    def resize(self, suf, ui_manager):
        self.rightMenu = elements.UISelectionList(
            pygame.Rect(0, 0, 100, len(self.teamData) * 25), self.teamData, ui_manager
        )

    def show(self):
        self.rightMenu.show()

    def hide(self):
        self.rightMenu.hide()

    def event(self, e0):
        if e0.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if e0.ui_element == self.rightMenu:
                if self.handleClick is not None:
                    self.handleClick(e0.text)


class TeamInfoUI(UserInterfaceBase):
    def __init__(self):
        self.container: elements.UIWindow | None = None

        self.flagLabel: elements.UILabel | None = None
        self.nameLabel: elements.UILabel | None = None
        self.belongLabel: elements.UILabel | None = None

        self.costPerTickLabel: elements.UILabel | None = None
        self.movePropertyLabel: elements.UILabel | None = None
        self.battlePropertyLabel: elements.UILabel | None = None

        self.staffListView: elements.UISelectionList | None = None
        self.enlistTalentBtn: elements.UIButton | None = None
        self.setTroopModelBtn: elements.UIButton | None = None

        self._showMoreBtn: elements.UIButton | None = None

        self.typeNeedListView: elements.UISelectionList | None = None
        self.typeNeedInputBtn: elements.UIButton | None = None

        self.conveyBtn: elements.UIButton | None = None
        self.supplyFromBtn: elements.UIButton | None = None
        self.supplyToBtn: elements.UIButton | None = None

        self.attackTargetBtn: elements.UIDropDownMenu | None = None

        self.stealTypeBtn: elements.UIDropDownMenu | None = None
        self.stealType2Btn: elements.UIDropDownMenu | None = None
        self.stealType3Btn: elements.UIDropDownMenu | None = None

        self.damageTypeBtn: elements.UIDropDownMenu | None = None
        self.damageType2Btn: elements.UIDropDownMenu | None = None
        self.damageType3Btn: elements.UIDropDownMenu | None = None

        self.setHeaderBtn: elements.UIDropDownMenu | None = None
        self.setGroupBtn: elements.UIDropDownMenu | None = None
        self.sureBtn: elements.UIButton | None = None

        # event
        self.handleModifyMode = None
        self.handleModifyFromCity = None
        self.handleModifyToCity = None
        self.handleBack = None


class TeamConveyUI(UserInterfaceBase):
    def __init__(self):
        self.container: elements.UIWindow | None = None
        self.targetLocBtn: elements.UIDropDownMenu | None = None
        self.targetBtn: elements.UIDropDownMenu | None = None

        self.staffListView: elements.UISelectionList | None = None
        self.storageListView: elements.UISelectionList | None = None
        self.storageInputBtn: elements.UITextEntryLine | None = None
        self.storageMaxInputLabel: elements.UILabel | None = None

        # event
        self.handleBack = None
