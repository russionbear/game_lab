#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: cmd_spectator.py
# @time: 3/12/2023 9:28 PM
from queue import Queue
from typing import Any

import numpy
import pygame

from qins_moon.advw import data_node as m_data_node
from qins_moon.advw.data_node import AdvwDataNode, PlayerNode
from qins_moon.advw.data_table import AdvwDataTable
from qins_moon.advw import data_driver as _data_driver
from qins_moon.core.utils.data_structure import NameIdTableStructure
from qins_moon.core.utils.data_table_loader import DataTableLoader
from qins_moon.core.utils.parse_command import parse_command
from qins_moon.core.grid_map.grid_navigation import GridNavigation, GridNavigationManager
from qins_moon.qm.tile_map.config import ConfigBase
from qins_moon.qm.tile_map.entity import TileMapRootEntity, UnitLayerData, TerrainLayerData, JoinedTerrainLayerEntity, \
    JoinedUnitLayerEntity, UnitEntityBase, UnitLayerEntityBase
from qins_moon.qm.tile_map.ui_state import TileMapUIStateMngr, TileMapEditUS, run_tile_map, TileMapCmdSpectatorUS, \
    TileMapUIStateBase
from qins_moon.advw.data_ai import AdvwEasyAIModelEntity


class Config(ConfigBase):
    def __init__(self, map_name=None):
        super().__init__(map_name)

        self.ASSET_PACKAGE_ID = 'test', 'demo', 'advw'
        self.DATA_TABLE_ID = 'test', 'advw', 'advw'
        self.SYSTEM_KEY = 'runtime'

        self.defaultInitMapSize = 16, 16
        self.defaultBlockSize = 50, 50
        self.flagIdColorDict = {
            1: 'red', 2: 'blue', 3: 'green', 4: 'yellow', 5: 'aliceBlue',
            6: 'coral', 7: 'hotPink', 8: 'linen', 0: 'none'
        }


# region custom unit entity


class BuildingEntity(UnitEntityBase):

    def refresh_info(self):
        super().refresh_info()
        config: Config | Any = self.config
        self.infoComponent.showBloodBar = False
        self.infoComponent.title = ' '
        self.animationComponent.base_anime_state = [config.flagIdColorDict[self.permData.flagId]]


class MilitaryEntity(UnitEntityBase):
    def refresh_info(self):
        super().refresh_info()
        config: Config | Any = self.config
        self.infoComponent.title = '*' if not self.permData.acted else ' '
        self.infoComponent.blood = self.permData.currentBlood / self.permData.maxBlood
        self.animationComponent.base_anime_state = [config.flagIdColorDict[self.permData.flagId]]


class BuildingLayerEntity(UnitLayerEntityBase):
    def make_child_entity(self, perm_key):
        tmp_d: m_data_node.BuildingNode = self.permDataDict[perm_key]
        tmp_e = BuildingEntity(tmp_d.id, self.worldScene, tmp_d, self.assetPackage, self.config, self.gridNav,
                               self.renderZIndex, self.layer, self.tableRowModelNameDict[tmp_d.tableRowId])
        self.add_child(tmp_e)
        return tmp_e


class MilitaryLayerEntity(UnitLayerEntityBase):
    def make_child_entity(self, perm_key):
        tmp_d: m_data_node.MilitaryNode = self.permDataDict[perm_key]
        tmp_e = MilitaryEntity(tmp_d.id, self.worldScene, tmp_d, self.assetPackage, self.config, self.gridNav,
                               self.renderZIndex, self.layer, self.tableRowModelNameDict[tmp_d.tableRowId])
        self.add_child(tmp_e)
        return tmp_e


# endregion


class TerrainLayerEntity(JoinedTerrainLayerEntity):
    def __init__(self, dn, config, pkg, scene, map_size, grid_nav=None, zindex=(1, 1), interval=0,
                 layer_nu=1):
        self.rootDataNode: AdvwDataNode = dn
        # region make some data
        terrain_layer_storage = NameIdTableStructure[TerrainLayerData]()
        tmp_d = TerrainLayerData()
        tmp_d.id = 1
        tmp_d.name = 'terrain'
        tmp_d.layer = 1
        tmp_d.terrainMap = self.rootDataNode.terrainMap
        tmp_d.dataTable = self.rootDataNode.dataTable.terrainTerrainTable
        tmp_d.modelPrefix = 'terrain'
        terrain_layer_storage.add(tmp_d)

        tmp_d = TerrainLayerData()
        tmp_d.id = 2
        tmp_d.name = 'traffic'
        tmp_d.layer = 2
        tmp_d.terrainMap = self.rootDataNode.trafficMap
        tmp_d.dataTable = self.rootDataNode.dataTable.trafficTable
        tmp_d.modelPrefix = 'traffic'
        terrain_layer_storage.add(tmp_d)

        tmp_d = TerrainLayerData()
        tmp_d.id = 3
        tmp_d.name = 'decoration'
        tmp_d.layer = 3
        tmp_d.terrainMap = self.rootDataNode.decorationMap
        tmp_d.dataTable = self.rootDataNode.dataTable.decorationTable
        tmp_d.modelPrefix = 'decoration'
        terrain_layer_storage.add(tmp_d)
        # endregion
        super().__init__(config, pkg, scene, map_size, terrain_layer_storage, grid_nav, zindex, interval, layer_nu)


class UnitLayerEntity(JoinedUnitLayerEntity):
    def __init__(self, dn, config, pkg, scene, grid_nav=None):
        self.rootDataNode: AdvwDataNode = dn

        # region unit layer storage
        unit_layer_storage = NameIdTableStructure[UnitLayerData]()
        tmp_d = UnitLayerData()
        tmp_d.id = 4
        tmp_d.name = 'building'
        tmp_d.layer = 4
        tmp_d.zIndex = 4
        tmp_d.unitDict = dn.buildingDict
        tmp_d.dataTable = dn.dataTable.buildingTable
        tmp_d.tableModelDict = {v.id: v.modelName for k, v in dn.dataTable.buildingTable.idDict.items()}
        tmp_d.modelPrefix = 'building'
        unit_layer_storage.add(tmp_d)

        tmp_d = UnitLayerData()
        tmp_d.id = 5
        tmp_d.name = 'military'
        tmp_d.layer = 5
        tmp_d.zIndex = 5
        tmp_d.unitDict = dn.militaryDict
        tmp_d.dataTable = dn.dataTable.militaryTable
        tmp_d.tableModelDict = {v.id: v.modelName for k, v in dn.dataTable.militaryTable.idDict.items()}
        tmp_d.modelPrefix = 'military'
        unit_layer_storage.add(tmp_d)
        # endregion

        super().__init__(config, pkg, scene, unit_layer_storage, grid_nav)

    def make_layer_entity(self, v: UnitLayerData):
        if v.name == 'building':
            tmp_e = BuildingLayerEntity(self.worldScene, self.assetPackage, self.config, self.gridNav,
                                        v.unitDict.idDict, 4, 4, v.tableModelDict)
            v.entity = tmp_e
            tmp_e.id = v.id
            tmp_e.sub_unit_action_finished(self._pub_unit_action_finished)
            self.add_child(tmp_e)
        elif v.name == 'military':
            tmp_e = MilitaryLayerEntity(self.worldScene, self.assetPackage, self.config, self.gridNav,
                                        v.unitDict.idDict, 5, 5, v.tableModelDict)
            tmp_e.id = v.id
            v.entity = tmp_e
            tmp_e.sub_unit_action_finished(self._pub_unit_action_finished)
            self.add_child(tmp_e)
        else:
            raise Exception()


class SpectatorRootEntity(TileMapRootEntity):
    """
    不支持多个行动并行
    内置ai
    一帧内只建造一个但闻，嗯，还能改进
    """

    def __init__(self, config):
        self.rootDataNode: AdvwDataNode | Any = None
        super().__init__(config)
        self.config: Config = config
        self.dataDriver: _data_driver.AdvwDataDriver = _data_driver.AdvwDataDriver()

        self._preHandleEvents = Queue(128)
        self._handledEvents = Queue(128)
        self._handleActionFinished = None
        # self.openActionChain = True  # 尽量不要在init之后改变它
        self._isInActionChain = False

    def init_map(self):
        self.dataDriver.controller = _data_driver.AdvwController(self.rootDataNode, self.dataDriver)
        self.dataDriver.sub_trigger_event(self._handle_local_event_handled)
        self.dataDriver.sub_local_event(self._handle_local_event_handled)
        super().init_map()

    def make_nav_data(self):
        self.gridNavComponent = GridNavigation(self.rootDataNode.map_size(), [1, 2, 3, 4, 5])
        GridNavigationManager()[self.config.SYSTEM_KEY] = self.gridNavComponent
        dn = self.rootDataNode
        for group in dn.playerDict.idDict.keys():
            for engine in dn.dataTable.engineTable.idDict.keys():
                self.gridNavComponent.add_engine_mapper(
                    (group << 8)+engine,
                    [(1, lambda arg: 1), (2, lambda arg: 1), (3, lambda arg: 1),
                     (5, lambda arg: 0 if dn.militaryDict[arg].flagId == group else 999)],
                    numpy.float_)  # init 引擎移动层

    def make_map(self):
        config = self.config
        DataTableLoader.table_storage_path = config.TABLE_STORAGE_PATH
        data_table = DataTableLoader.load_data(*config.DATA_TABLE_ID, AdvwDataTable())
        data_node = AdvwDataNode.make_data(config.defaultInitMapSize, data_table, 100)
        data_node.config = config
        return data_node

    def save_map(self):
        flag_id_color_dict = self.config.flagIdColorDict
        flags = set()
        for v in self.rootDataNode.buildingDict.idDict.values():
            flags.add(v.flagId)
        for v in self.rootDataNode.militaryDict.idDict.values():
            flags.add(v.flagId)

        if 0 in flags:
            flags.remove(0)
        self.rootDataNode.playerDict.clear()
        for i in flags:
            tmp_player = PlayerNode()
            tmp_player.id = i
            tmp_player.flagId = i
            tmp_player.name = flag_id_color_dict[i]
            self.rootDataNode.playerDict.add(tmp_player)
        self.rootDataNode.currentPlayerId = list(flags)[0]

        super().save_map()

    # def load_map(self):
    #     self.rootDataNode = self.make_map()

    def make_terrain_layer(self):
        self.terrainLayer = TerrainLayerEntity(
            self.rootDataNode, self.config, self.assetPackage, self.worldScene, self.rootDataNode.map_size(),
            self.gridNavComponent)
        self.add_child(self.terrainLayer)

    def make_unit_layer(self):
        self.unitLayer = UnitLayerEntity(
            self.rootDataNode, self.config, self.assetPackage, self.worldScene, self.gridNavComponent)
        self.add_child(self.unitLayer)
        self.unitLayer.sub_unit_action_finished(self._pub_action_finished)

    def put_local_event(self, e):
        check_info = e.check(self.rootDataNode)
        if check_info is None:
            try:
                self._preHandleEvents.put(e)
            except:
                print(e.__dict__)

        else:
            print('not in', check_info, e.__dict__)

    def _handle_local_event_handled(self, d):
        cls_name = d.__class__.__name__
        dn = self.rootDataNode
        if cls_name == _data_driver.ModifyTerrainHandler.__name__:
            d: _data_driver.ModifyTerrainHandler = d
            for k, v in d.terrainDict.items():
                self.terrainLayer.refresh_node('terrain', k, v)
            for k, v in d.trafficDict.items():
                self.terrainLayer.refresh_node('traffic', k, v)
            for k, v in d.decorationDict.items():
                self.terrainLayer.refresh_node('decoration', k, v)
            for k, v in d.buildingDict.items():
                self.unitLayer.refresh_node('building', dn.buildingDict[k].id)
            for k, v in d.militaryDict.items():
                self.unitLayer.refresh_node('military', dn.militaryDict[k].id)

            self._handledEvents.put(d)
            self._pub_action_finished()

        elif cls_name == _data_driver.BoutEntHandler.__name__:
            for v in dn.militaryDict.idDict.values():
                self.unitLayer.refresh_node('military', v.id)

            self._handledEvents.put(d)
            self._pub_action_finished()

        elif cls_name == _data_driver.BuildMilitaryHandler.__name__:
            self.unitLayer.refresh_node('military', dn.militaryDict[d.loc].id)

            self._handledEvents.put(d)
            self._pub_action_finished()

        elif cls_name == _data_driver.MilitaryActionHandler.__name__:
            m_e: MilitaryEntity = self.unitLayer.unitLayerStorage['military'] \
                .entity.find_child_by_id(d.militaryId)
            # if m_e is None:
            #     self._pub_action_finished()
            #     return
            actions = []
            if d.road:
                actions.append(d.road)
            actions.append(['wait'])
            m_e.actionController.set_actions(actions)
            if d.attackTargetId is not None:
                m_e.unitIdShouldRefreshAfterAction.append(d.attackTargetId)
            self._handledEvents.put(d)

    def _pub_action_finished(self, *args, **kwargs):
        # print('hi', args, kwargs)
        # if args[0] == 1:
        #     raise Exception("")
        event = self._handledEvents.get()
        # print('root entity', event.__dict__)
        if self._handleActionFinished:
            self._handleActionFinished(event)

        # if 'u_id' in kwargs:
        #     u_e = self.unitLayer.unitLayerStorage[kwargs['l_id']].entity.find_child_by_id(kwargs['u_id'])
        #     for i in u_e.unitIdShouldRefresh:
        #         self.unitLayer.refresh_node('military', i)
        #     u_e.unitIdShouldRefresh.clear()

        # if 'atk_tar' in kwargs:
        #     self.unitLayer.refresh_node('military', self.rootDataNode.militaryDict[kwargs['atk_tar']].id)

        self._isInActionChain = False
        # if not self.openActionChain:
        #     return
        # if self._currentIgnoreRenderDeep < self.actionIgnoreRenderMaxDeep:
        #     return

    def sub_action_finished(self, v):
        self._handleActionFinished = v

    def update(self, delta_time):
        if not self._preHandleEvents.empty():
            dd = self.dataDriver
            if not self._isInActionChain:
                self._isInActionChain = True
                dd.put_local_event(self._preHandleEvents.get())
        super().update(delta_time)


class SpectatorUIStateMngr(TileMapUIStateMngr):
    STATE_HOME = 0x1
    STATE_CMD_SPECTATOR = 0x2
    STATE_AI = 0x3

    def __init__(self, root_e):
        super().__init__(root_e)
        self.rootEntity: SpectatorRootEntity | Any = self.rootEntity
        self.mapEditUS = MapEditUI(self)
        self.cmdSpectatorUS = CmdSpectatorUS(self)
        self.easyAIModelUS = EasyAIModelUS(self)
        self[self.STATE_HOME] = self.mapEditUS
        self[self.STATE_CMD_SPECTATOR] = self.cmdSpectatorUS
        self[self.STATE_AI] = self.easyAIModelUS

        self.currentUIState = self[self.STATE_CMD_SPECTATOR]


class MapEditUI(TileMapEditUS):
    def handle_make_unit(self, loc, v) -> Any:
        dn: AdvwDataNode | Any = self.mngr.rootEntity.rootDataNode
        if self.homeUI.layerButton.selected_option == 'building':
            return dn.make_building(v, loc, int(self.homeUI.flagButton.selected_option))
        elif self.homeUI.layerButton.selected_option == 'military':
            return dn.make_military(v, loc, int(self.homeUI.flagButton.selected_option))

    def event(self, e0):
        super().event(e0)
        if e0.type == pygame.KEYDOWN:
            if e0.key == pygame.K_F2:
                self.mngr.switch_ui_state(SpectatorUIStateMngr.STATE_CMD_SPECTATOR)


class CmdSpectatorUS(TileMapCmdSpectatorUS):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.mngr: SpectatorUIStateMngr = mngr
        self.openLoopAI = False

    def active(self):
        super().active()
        self.mngr.rootEntity.sub_action_finished(self._handle_action_finished)

    def handle_input(self, text):
        if text == '':
            return
        self.cmdSpectatorUI.messageData.append(text)
        self.cmdSpectatorUI.re_render_message()
        dn: AdvwDataNode | Any = self.mngr.rootEntity.rootDataNode
        cmd_info = parse_command(text)

        rlt_info = ''
        if cmd_info[0] == 'build':  # build 5_4 table_row_id
            loc = int(cmd_info[1][0].split('_')[0]), int(cmd_info[1][0].split('_')[1])
            table_row_id = int(cmd_info[1][1])
            if loc not in dn.buildingDict:
                return
            if table_row_id == 0:
                b_h = _data_driver.MilitaryKillHandler()
                b_h.militaryLoc = loc
            else:
                b_h = _data_driver.BuildMilitaryHandler()
                b_h.loc = loc
                b_h.tableRowId = table_row_id
            self.mngr.rootEntity.put_local_event(b_h)

        elif cmd_info[0] == 'players':
            rlt_info = str(list(dn.playerDict.idDict.keys()))

        elif cmd_info[0] == 'units':
            print('units')
            for i in dn.militaryDict.idDict.values():
                print(i.__dict__)

        elif cmd_info[0] == 'move':
            b_h = _data_driver.MilitaryActionHandler()
            b_h_o_loc = cmd_info[1][0]
            b_h_n_loc = cmd_info[1][1]
            b_h_o_loc = int(b_h_o_loc.split('_')[0]), int(b_h_o_loc.split('_')[1])
            b_h_n_loc = int(b_h_n_loc.split('_')[0]), int(b_h_n_loc.split('_')[1])
            if b_h_o_loc not in dn.militaryDict:
                return
            b_h.militaryId = dn.militaryDict[b_h_o_loc].id
            b_h.road = [b_h_o_loc, b_h_n_loc]
            self.mngr.rootEntity.put_local_event(b_h)

        elif cmd_info[0] == 'atk':
            b_h = _data_driver.MilitaryActionHandler()
            b_h_o_loc = cmd_info[1][0]
            b_h_n_loc = cmd_info[1][1]
            b_h_o_loc = int(b_h_o_loc.split('_')[0]), int(b_h_o_loc.split('_')[1])
            b_h_n_loc = int(b_h_n_loc.split('_')[0]), int(b_h_n_loc.split('_')[1])
            # loc = int(cmd_info[1][0].split('_')[0]), int(cmd_info[1][0].split('_')[1])
            # tar_loc = int(cmd_info[1][1].split('_')[0]), int(cmd_info[1][1].split('_')[1])
            b_h.attackTargetId = dn.militaryDict[b_h_n_loc].id
            b_h.loc = b_h_o_loc
            b_h.militaryId = dn.militaryDict[b_h.loc].id
            self.mngr.rootEntity.put_local_event(b_h)

        elif cmd_info[0] == 'bout_end':
            # print(dn.currentPlayerId)
            self.mngr.rootEntity.put_local_event(_data_driver.BoutEntHandler())
            # print(dn.currentPlayerId)

        elif cmd_info[0] == 'enemy':
            rlt_info = str({i.name: i.money for i in dn.playerDict.idDict.values()})

        elif cmd_info[0] == 'm_b_flag':
            b_h = _data_driver.ModifyBuildingFlagHandler()
            b_h_o_loc = cmd_info[1][0]
            b_h_o_loc = int(b_h_o_loc.split('_')[0]), int(b_h_o_loc.split('_')[1])
            if b_h_o_loc not in dn.buildingDict:
                return
            b_h.flag = dn.playerDict[cmd_info[1][1]].flagId
            b_h.loc = b_h_o_loc
            self.mngr.rootEntity.put_local_event(b_h)

        elif cmd_info[0] == 'mouse':
            rlt_info = str(self.mngr.rootEntity.worldScene.get_mouse_grid_loc())

        elif cmd_info[0] == 'to_ai':
            self.mngr.switch_ui_state(SpectatorUIStateMngr.STATE_AI)

        elif cmd_info[0] == 'load_dt':
            DataTableLoader.table_storage_path = self.mngr.rootEntity.config.TABLE_STORAGE_PATH
            self.mngr.rootEntity.rootDataNode.dataTable = DataTableLoader.load_data(
                *self.mngr.rootEntity.config.DATA_TABLE_ID, AdvwDataTable())

        # except (IndexError, ValueError):
        #     return

        if rlt_info != '':
            self.cmdSpectatorUI.messageData.append(rlt_info)
            self.cmdSpectatorUI.re_render_message()

    def event(self, e0):
        super().event(e0)
        if e0.type == pygame.KEYDOWN:
            if e0.key == pygame.K_F1:
                self.mngr.switch_ui_state(SpectatorUIStateMngr.STATE_HOME)
            elif e0.key == pygame.K_i:
                if e0.mod & pygame.KMOD_CTRL:
                    self.openLoopAI = not self.openLoopAI

    def _handle_action_finished(self, e0):
        print(e0.__dict__)
        if self.openLoopAI:
            if self.mngr.easyAIModelUS.easyAIModel is None or \
                    self.mngr.easyAIModelUS.easyAIModel.flagId != self.mngr.rootEntity.rootDataNode.currentPlayerId:
                self.mngr.switch_ui_state(SpectatorUIStateMngr.STATE_AI)


class EasyAIModelUS(TileMapUIStateBase):
    def __init__(self, mngr):
        super().__init__(mngr)
        self.mngr: SpectatorUIStateMngr = mngr
        self.easyAIModel: AdvwEasyAIModelEntity | None = None

    def active(self):
        self.mngr.rootEntity.sub_action_finished(self._handle_action_finished)
        self._handle_action_finished()

    def inactive(self):
        self.mngr.rootEntity.sub_action_finished(None)
        self.easyAIModel = None

    def _handle_action_finished(self, e0=None):
        if e0 is not None and e0.__class__ == _data_driver.BuildMilitaryHandler:
            return

        if self.easyAIModel is None:
            self.easyAIModel = AdvwEasyAIModelEntity(
                self.mngr.rootEntity.rootDataNode.currentPlayerId, self.mngr.rootEntity.dataDriver,
                self.mngr.rootEntity.gridNavComponent)
            self.easyAIModel.init_data()

        unit_action = self.easyAIModel.get_next_unit_action()
        if unit_action is None:
            buy_actions = self.easyAIModel.get_buy_plain()
            for i in buy_actions:
                if i.check(self.mngr.rootEntity.rootDataNode) is not None:
                    continue
                self.mngr.rootEntity.put_local_event(i)

            self.easyAIModel = None
            self.mngr.rootEntity.put_local_event(_data_driver.BoutEntHandler())
        else:
            self.mngr.rootEntity.put_local_event(unit_action)

    def event(self, e0):
        if e0.type == pygame.KEYDOWN:
            if e0.key == pygame.K_ESCAPE:
                self.mngr.switch_ui_state(SpectatorUIStateMngr.STATE_CMD_SPECTATOR)


if __name__ == '__main__':
    __config = Config()
    run_tile_map(__config, SpectatorRootEntity, SpectatorUIStateMngr)
