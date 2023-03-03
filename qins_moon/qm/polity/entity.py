#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :entity.py
# @Time      :21/02/2023
# @Author    :russionbear
# @Function  :function
import numpy

from qins_moon.core.asset import ConfigBase, AssetPackage, AssetManager
from qins_moon.core.director import EntityBase, RootEntityBase, RootEntityManager
from qins_moon.core.render.component import JoinedSurfaceRuleBase, JoinedSurfaceRenderComponent, InfoRenderComponent, \
    AnimeRenderComponent, JoinedLayerSurfaceRenderComponent, CoverRenderComponent
from qins_moon.core.render.render import SceneManager, SceneBase
from qins_moon.core.utils.data_structure import NameIdTableStructure
from qins_moon.core.utils.data_table_loader import DataTableLoader
from qins_moon.core.utils.math_tool import MathTool
from qins_moon.core.grid_map import GridMovement, GridNavigation, GridStaticMoveController, GridNavigationManager, \
    GridDynMoveController
from qins_moon.qm.polity.config import Config
from qins_moon.qm.polity.data_node import PolityDataNode, PolityDataTable
from qins_moon.qm.polity.render import PolityScene


# ################ tool
# surface layer: terrain、city、troop


class TerrainLayerEntityBase(EntityBase):
    """只有一个terrain类型的map"""

    def __init__(self, config, pkg, union_render, table: NameIdTableStructure, terrain_map, grid_nav=None, layer=1):
        super().__init__()
        self.config: ConfigBase = config
        self.assetPackage: AssetPackage = pkg

        self.joinedLayerRender: JoinedLayerSurfaceRenderComponent = union_render

        joined_suf_rule_dict = {}
        for i1, i in table.idDict.items():
            tmp_d = JoinedSurfaceRuleBase()
            joined_suf_rule_dict[i1] = tmp_d
            tmp_d.id = i1
            # tmp_d.rules = [({}, self.assetPackage.get_sprite(i.modelName))]
            tmp_d.rules = self.assetPackage.get_joined_surface_rule(i.modelName)

        self.joinedLayerRender.add_layer_surface(joined_suf_rule_dict, terrain_map, grid_nav, layer)


# ###################################################


class TerrainLayerEntity(TerrainLayerEntityBase):
    def __init__(self, config, pkg, union_render, table: NameIdTableStructure, data_node: PolityDataNode):
        self.layer = 1
        super().__init__(config, pkg, union_render, table, data_node.terrainMap,
                         GridNavigationManager()[config.SYSTEM_KEY], self.layer)
        self.rootDataNode: PolityDataNode = data_node
        # # self.joinedSurfaceComponent = JoinedSurfaceRenderComponent(
        # #     config, joined_suf_rule_dict, terrain_map)
        # # self.joinedSurfaceComponent.set_scene(scene)
        # # self.joinedSurfaceComponent.zindex = 1, 1
        #
        # # grid nav
        # grid_nav = GridNavigationManager()[config.SYSTEM_KEY]
        # for y in range(terrain_map.shape[0]):
        #     for x in range(terrain_map.shape[1]):
        #         grid_nav.refresh_node((x, y), terrain_map[y, x], 1)

    def refresh_node(self, loc, v):
        self.rootDataNode.terrainMap[loc[1], loc[0]] = v
        self.joinedLayerRender.refresh_data(loc, v, self.layer, True)

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        width, height = self.rootDataNode.map_size
        terrain_map = self.rootDataNode.terrainMap
        for drt in directions:
            x_, y_ = drt[0]+loc[0], drt[1]+loc[1]
            if x_ < 0 or y_ < 0 or x_ >= width or y_ >= height:
                continue
            self.joinedLayerRender.refresh_data((x_, y_), terrain_map[y_, x_], self.layer, True)


class TrafficLayerEntity(TerrainLayerEntityBase):
    def __init__(self, config, pkg, union_render, table: NameIdTableStructure, data_node: PolityDataNode):
        self.layer = 2
        super().__init__(config, pkg, union_render, table, data_node.trafficMap,
                         GridNavigationManager()[config.SYSTEM_KEY], self.layer)
        self.rootDataNode: PolityDataNode = data_node

    def refresh_node(self, loc, v):
        self.rootDataNode.trafficMap[loc[1], loc[0]] = v
        self.joinedLayerRender.refresh_data(loc, v, self.layer, True)

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        width, height = self.rootDataNode.map_size
        terrain_map = self.rootDataNode.trafficMap
        for drt in directions:
            x_, y_ = drt[0]+loc[0], drt[1]+loc[1]
            if x_ < 0 or y_ < 0 or x_ >= width or y_ >= height:
                continue
            self.joinedLayerRender.refresh_data((x_, y_), terrain_map[y_, x_], self.layer, True)


class CityEntity(EntityBase):
    def __init__(self, id_, scene, data_node, pkg, config):
        super().__init__()
        self.scene: SceneBase = scene
        self.id = id_
        self.dataNodeRoot: PolityDataNode = data_node
        self.animeComponent = AnimeRenderComponent(self.dataNodeRoot.dataTable.generalTable.cityModelName, pkg)
        self.animeComponent.action = ''
        self.infoComponent: InfoRenderComponent = InfoRenderComponent(
            self.animeComponent.get_surface().get_size(), config, pkg, False)
        tmp_d = self.dataNodeRoot.cityDict[id_]
        loc = sum([i[0] for i in tmp_d.locations])/len(tmp_d.locations), \
            sum([i[1] for i in tmp_d.locations])/len(tmp_d.locations)
        loc = config.MAP_BLOCK_SIZE[0] * loc[0] + config.MAP_BLOCK_SIZE[0] // 2, \
            config.MAP_BLOCK_SIZE[1] * loc[1] + config.MAP_BLOCK_SIZE[1] // 2
        self.infoComponent.set_location(loc)
        self.animeComponent.set_location(loc)
        self.infoComponent.zindex = 2, 2
        self.animeComponent.zindex = 2, 1
        self.infoComponent.set_scene(self.scene)
        self.animeComponent.set_scene(self.scene)
        self.infoComponent.title = tmp_d.name

    def refresh_info(self):
        tmp_d = self.dataNodeRoot.cityDict[self.id]
        self.infoComponent.title = tmp_d.name


class GridCityLayerEntity(EntityBase):
    def __init__(self, scene, data_node, pkg, config):
        super().__init__()
        self.worldScene: SceneBase = scene
        self.rootDataNode: PolityDataNode = data_node
        self.assetPackage: AssetPackage = pkg
        self.config: Config = config

        grid_nav = GridNavigationManager()[config.SYSTEM_KEY]
        for k, v in self.rootDataNode.cityDict.idDict.items():
            tmp_e = CityEntity(k, self.worldScene, self.rootDataNode, self.assetPackage, self.config)
            self.add_child(tmp_e)
            for l1 in v.locations:
                grid_nav.refresh_node(l1, k, 2)


class TroopEntity(EntityBase):
    TASK_WAIT = 0x1
    TASK_ATTACK = 0x2

    def __init__(self, id_, scene, data_node, pkg, config):
        super().__init__()
        self.rootDataNode: PolityDataNode = data_node
        self.config: Config = config
        self.gridNav = GridNavigationManager()[config.SYSTEM_KEY]
        self.id = id_
        model_name = self.rootDataNode.dataTable.generalTable.troopModelName
        tmp_d = self.rootDataNode.troopDict[id_]
        self.animationComponent = AnimeRenderComponent(model_name, pkg)
        self.infoComponent = InfoRenderComponent(self.animationComponent.get_surface().get_size(),
                                                 config, pkg)
        self.animationComponent.set_scene(scene)
        self.infoComponent.set_scene(scene)
        self.animationComponent.zindex = 3, 1
        self.infoComponent.zindex = 3, 2
        self.infoComponent.title = tmp_d.name

        loc = tmp_d.loc
        loc = self.config.MAP_BLOCK_SIZE[0] * loc[0] + self.config.MAP_BLOCK_SIZE[0]//2, \
            self.config.MAP_BLOCK_SIZE[1]*loc[1] + self.config.MAP_BLOCK_SIZE[1]//2
        # print(loc)
        self.movement = GridMovement(loc, 100)
        self.gridMoveController = GridStaticMoveController(self.movement, config.MAP_BLOCK_SIZE)
        self.gridMoveController.sub_task_finished(self.handle_road_finished)
        self.gridMoveController.sub_next_point_allocated(self.handle_next_point_allocated)
        self.animationComponent.sub_tmp_anime_state_finished(self.handle_anime_state_finished)

        self.currentTask = 'wait'
        self.currentTaskParam = {}

    def refresh_info(self):
        tmp_d = self.rootDataNode.troopDict[self.id]
        self.infoComponent.title = tmp_d.name
        loc = tmp_d.loc
        loc = self.config.MAP_BLOCK_SIZE[0] * loc[0] + self.config.MAP_BLOCK_SIZE[0]//2, \
            self.config.MAP_BLOCK_SIZE[1]*loc[1] + self.config.MAP_BLOCK_SIZE[1]//2
        # print(loc)
        self.movement = GridMovement(loc, 100)

    def update(self, delta_time):
        self.gridMoveController.update(delta_time)
        self.infoComponent.update(delta_time)
        self.animationComponent.update(delta_time)
        self.movement.update(delta_time)
        loc = self.movement.loc
        self.infoComponent.loc = loc
        self.animationComponent.loc = loc

    def handle_road_finished(self, **kwargs):
        # o_loc = self.rootDataNode.troopDict[self.id].loc
        # n_loc = self.gridMoveController.grid_loc()
        # self.gridNav.refresh_node(o_loc, 0, 3)
        # self.gridNav.refresh_node(n_loc, self.id, 3)
        if self.currentTask == 'wait':
            self.animationComponent.anime_state = 'wait'
        else:
            self.animationComponent.anime_state = 'attack'

    def handle_anime_state_finished(self):
        self.handle_task_finished()

    def handle_task_finished(self):
        self.parent.refresh_node(self.id)
        if self.currentTask == 'attack':
            self.parent.refresh_node(self.currentTaskParam['targetId'])

    def handle_next_point_allocated(self, o_p, n_p):
        pass


class GridTroopLayerEntity(EntityBase):
    def __init__(self, scene, data_node, pkg, config):
        super().__init__()
        self.worldScene: SceneBase = scene
        self.rootDataNode: PolityDataNode = data_node
        self.assetPackage: AssetPackage = pkg
        self.config: Config = config
        self.gridNav = GridNavigationManager()[config.SYSTEM_KEY]
        self.layer = 3

        self.gridNav = GridNavigationManager()[config.SYSTEM_KEY]
        for k, v in self.rootDataNode.troopDict.idDict.items():
            tmp_e = TroopEntity(k, self.worldScene, self.rootDataNode, self.assetPackage, self.config)
            self.add_child(tmp_e)
            self.gridNav.refresh_node(v.loc, k, self.layer)

        self.coverLayer = CoverRenderComponent(self.worldScene.get_surface().get_size(),
                                               self.assetPackage.get_pen(), config.MAP_BLOCK_SIZE)
        self.coverLayer.set_scene(self.worldScene)
        self.coverLayer.zindex = 3, 0

    def refresh_node(self, id_):
        child = self.find_child_by_id(id_)
        troop_dict = self.rootDataNode.troopDict
        if id_ in troop_dict and child is None:
            tmp_d = troop_dict[id_]
            tmp_e = TroopEntity(id_, self.worldScene, self.rootDataNode, self.assetPackage, self.config)
            self.add_child(tmp_e)
            self.gridNav.refresh_node(tmp_d.loc, id_, self.layer)
        elif id_ not in troop_dict and child is not None:
            self.remove_child(child)
        elif id_ in troop_dict:
            child.refresh_info()

    def show_move_area(self, id_):
        dt = self.rootDataNode.dataTable
        troop_n = self.rootDataNode.troopDict[id_]
        move_property = dt.movePropertyTable[troop_n.moveProperty]
        cost_map = self.gridNav.get_engine_move_map(dt.engineTable[move_property.engineType].id)
        move_area = MathTool.count_move_area(
            cost_map,
            troop_n.loc, move_property.baseSpeed
        )

        self.coverLayer.rectStorage['move_area'] = (0, 200, 60, 200), 0, \
            [(i[0], i[1],
              (i[0]+1), (i[1]+1))
             for i in move_area.keys()]
        self.coverLayer.re_render()
        return move_area, cost_map

    def show_road(self, road):
        self.coverLayer.clear()
        self.coverLayer.rectStorage['move_area'] = (0, 200, 60, 200), 0, \
            [(i[0], i[1],
              (i[0] + 1), (i[1] + 1))
             for i in road]
        self.coverLayer.re_render()


class CollideLayerEntity(EntityBase):
    pass


class PolityRootEntity(RootEntityBase):
    def __init__(self, config, dt, user_group_id):
        super().__init__()

        self.config: Config = config
        self.rootDataNode: PolityDataNode = dt
        self.assetPackage: AssetPackage | None = None
        self.worldScene: PolityScene | None = None

        self.joinedLayerRender: JoinedLayerSurfaceRenderComponent | None = None

        self.terrainLayer: TerrainLayerEntity | None = None
        self.trafficLayer: TrafficLayerEntity | None = None
        self.cityLayer: GridCityLayerEntity | None = None
        self.troopLayer: GridTroopLayerEntity | None = None
        self.userGroupId = user_group_id
        self.currentGroupId = user_group_id

    def init_load_asset(self):
        asset_mngr = AssetManager()
        asset_mngr.init(self.config)
        asset_pkg = AssetManager().load_resource(self.config.ASSET_PACKAGE_ID)
        self.assetPackage = asset_pkg

    def init_map(self):
        # user_flag = 100
        map_size = self.rootDataNode.map_size

        # grid nav
        grid_nav = GridNavigation(map_size, [1, 2, 3])
        GridNavigationManager()[self.config.SYSTEM_KEY] = grid_nav
        dn = self.rootDataNode
        troop_dict = dn.troopDict
        terrain_table = dn.dataTable.terrainTerrainTable
        terrain_engine_table = dn.dataTable.engineTerrainTable

        user_flag = dn.groupDict[self.userGroupId].flag
        for k, v in dn.dataTable.engineTable.idDict.items():
            terrain_cost_dict = {
                v1.id: v.costDict[terrain_engine_table[v1.engineTerrain].name] for v1 in terrain_table.idDict.values()}
            grid_nav.add_engine_mapper(k, [
                (1, lambda arg: terrain_cost_dict[arg]),
                (3, lambda arg: 9999 if dn.is_enemy(user_flag, troop_dict[int(arg)].flag) else 0)
            ], numpy.float_)

        # world scene
        self.worldScene = PolityScene((map_size[0] * self.config.MAP_BLOCK_SIZE[0],
                                       map_size[1] * self.config.MAP_BLOCK_SIZE[1]), self.config.MAP_BLOCK_SIZE)
        self.joinedLayerRender = JoinedLayerSurfaceRenderComponent(self.config, map_size)
        self.joinedLayerRender.zindex = 1, 1
        self.joinedLayerRender.set_scene(self.worldScene)

        # layer
        self.terrainLayer = TerrainLayerEntity(
            self.config, self.assetPackage, self.joinedLayerRender,
            self.rootDataNode.dataTable.terrainTerrainTable, self.rootDataNode)
        self.trafficLayer = TrafficLayerEntity(
            self.config, self.assetPackage, self.joinedLayerRender, self.rootDataNode.dataTable.trafficTable,
            self.rootDataNode
        )
        self.joinedLayerRender.refresh_surface()

        self.cityLayer = GridCityLayerEntity(self.worldScene, self.rootDataNode, self.assetPackage, self.config)
        self.troopLayer = GridTroopLayerEntity(self.worldScene, self.rootDataNode, self.assetPackage, self.config)
        self.add_child(self.terrainLayer)
        self.add_child(self.trafficLayer)
        self.add_child(self.cityLayer)
        self.add_child(self.troopLayer)

    def init_register(self):
        SceneManager()[self.config.SYSTEM_KEY] = self.worldScene
        SceneManager().switch_scene(self.config.SYSTEM_KEY)
        RootEntityManager()[self.config.SYSTEM_KEY] = self
        RootEntityManager().switch_root_entity(self.config.SYSTEM_KEY)

    @staticmethod
    def make_map(config: Config):
        DataTableLoader.table_storage_path = config.TABLE_STORAGE_PATH
        data_table = DataTableLoader.load_data(*config.DATA_TABLE_ID, PolityDataTable())
        data_node = PolityDataNode.make_data(config.blockMapSize, data_table, 100)
        data_node.resourcePackageId = config.ASSET_PACKAGE_ID
        return data_node
