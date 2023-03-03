#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :component.py
# @Time      :07/02/2023
# @Author    :russionbear
# @Function  :function
from typing import List, Dict, Tuple, Any

import numpy
import pygame

from qins_moon.core.render.render import RenderBase
from qins_moon.core.interface.asset import IAssetPackageInterface, ISpriteAssetInterface, IConfigInterface, \
    IPencilInterface
from qins_moon.core.interface.grid_map import IGridNavigationInterface


class InfoRenderComponent(RenderBase):
    def __init__(self, unit_size, config: IConfigInterface,
                 asset_pkg, show_blood_bar=True, show_status=True):
        super().__init__()
        self.statusIconSize = config.STATUS_ICON_SIZE
        self.mapBlockSize = config.MAP_BLOCK_SIZE

        self._title = ""
        self._blood = 0.9
        self._status: List[str] = []
        self.showBloodBar = False
        self.showStatus = False

        self.assetPackage: IAssetPackageInterface | None = asset_pkg
        self.surface: pygame.Surface | None = None
        self.unitSize = unit_size

        self.showBloodBar = show_blood_bar
        self.showStatus = show_status
        self.set_unit_size(unit_size)

    def set_unit_size(self, size):
        self.unitSize = size
        self._render()

    def get_surface(self) -> pygame.Surface:
        return self.surface

    @property
    def blood(self):
        return self._blood

    @blood.setter
    def blood(self, value):
        self._blood = value
        if not self.showBloodBar:
            return
        self._render()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self._render()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if not self.showStatus:
            return
        self._status = value
        self._render()

    def _render(self):
        blood_bar_height = 5
        blood_bar_width = round(self.unitSize[0] * 1.2)

        pencil = self.assetPackage.get_pen()
        pencil.set_size(round(self.mapBlockSize[0] * 0.25))
        title_suf = self.assetPackage.get_pen().render(self._title).convert_alpha()
        title_rect = 0, 0, *title_suf.get_size()

        if self.showBloodBar:
            blood_rect = 0, 0, round(self.unitSize[0] * 1.2), 5
            blood_surface = pygame.Surface((blood_bar_width, blood_bar_height))
            pygame.draw.rect(blood_surface, '#000000',
                             pygame.Rect(0, 0, blood_surface.get_width(), blood_bar_height))
            pygame.draw.rect(blood_surface, (int(255 * (1 - self._blood)), int(255 * self._blood), 0),
                             pygame.Rect(0, 0, blood_surface.get_width() * self._blood, blood_bar_height))
        else:
            blood_rect = 0, 0, 0, 0
            blood_surface = None

        if self.showStatus:
            status_suf = pygame.Surface((self.statusIconSize[0] * len(self.status), self.statusIconSize[1])) \
                .convert_alpha()
            status_suf.fill((0, 0, 0, 0))
            for i1, i in enumerate(self.status):
                sp = self.assetPackage.get_sprite(i)
                status_suf.blit(pygame.transform.smoothscale(sp.images[0], self.statusIconSize),
                                (i1 * self.statusIconSize[0], 0))
            if status_suf.get_width() == 0:
                status_rect = 0, 0, 0, 0
            else:
                status_rect = 0, 0, *status_suf.get_size()
        else:
            status_suf = None
            status_rect = 0, 0, 0, 0

        suf_height = title_rect[-1] + blood_rect[-1] + status_rect[-1]
        suf_width = max(title_rect[-2], blood_rect[-2], status_rect[-2])

        if self.showBloodBar:
            extra_blood_height = blood_rect[-1] * 1.1
        else:
            extra_blood_height = 0

        extra_title_height = title_rect[-1] * 1.1

        suf_height += extra_blood_height
        if self.showStatus:
            suf_height += extra_title_height
        self.surface = pygame.Surface((suf_width, suf_height)).convert_alpha()
        self.surface.fill((0, 0, 0, 0))
        if self.showBloodBar:
            self.surface.blit(blood_surface, ((suf_width - blood_rect[-2]) // 2, suf_height - blood_rect[-1]))
        self.surface.blit(title_suf, ((suf_width - title_rect[-2]) // 2,
                          suf_height - blood_rect[-1] - extra_blood_height - title_rect[-1]))
        if self.showStatus:
            self.surface.blit(status_suf, ((suf_width-status_rect[-2])//2, 0))

        #  更新anchor
        if suf_width == 0:
            self.anchor = 0, 0
        else:
            self.anchor = 0, -(self.unitSize[1] + suf_height) / suf_width/2
            # print(self.anchor, 'info anchor', suf_width)
        # print('info anchor', self.anchor)


class AnimeRenderComponent(RenderBase):
    def __init__(self, model_name, asset_pkg: IAssetPackageInterface):
        super().__init__()
        self.modelName = model_name
        self._currentAction = ''

        self.assetPkg: IAssetPackageInterface = asset_pkg
        self._images: List[pygame.Surface] = []
        self.interval = 0
        self.__currentInterval = 0
        self.__currentImageIndex = 0
        self.action = ""
        self._speed = 1.0

        self._currentAnimeState = []
        self.__currentAnimeIndex = 0
        self._baseAnimeState = []
        self._isTmpAnimeStateFinished = True
        self._handleTmpAnimeStateFinished = None
        self.anchor = 0, 0

    def sub_tmp_anime_state_finished(self, v):
        self._handleTmpAnimeStateFinished = v

    def pub_tmp_anime_state_finished(self):
        self._isTmpAnimeStateFinished = True
        if self._handleTmpAnimeStateFinished:
            self._handleTmpAnimeStateFinished()

    @property
    def base_anime_state(self):
        return self._baseAnimeState

    @base_anime_state.setter
    def base_anime_state(self, value):
        self._baseAnimeState = value

    @property
    def anime_state(self):
        return self._currentAnimeState

    @anime_state.setter
    def anime_state(self, value):
        self._currentAnimeState = value
        self.__currentAnimeIndex = 0
        self._isTmpAnimeStateFinished = False

        if self.interval == 0:
            self.pub_tmp_anime_state_finished()

    @property
    def is_tmp_anime_finished(self):
        return self._isTmpAnimeStateFinished

    # ##############
    @property
    def speed(self):
        return self.speed

    @speed.setter
    def speed(self, value):
        self.speed = value

    @property
    def action(self):
        return self._currentAction

    @action.setter
    def action(self, value):
        self._currentAction = value
        sp = self.assetPkg.get_sprite(self.modelName, value)
        self.interval = sp.interval
        self.__currentImageIndex = 0
        self._images = [pygame.transform.smoothscale(i, sp.legalSize).convert_alpha() for i in sp.images]
        self.anchor = sp.anchor

    def get_surface(self) -> pygame.Surface:
        return self._images[self.__currentImageIndex]

    def update(self, delta_time):
        super().update(delta_time)
        if self.interval == 0:
            return
        self.__currentInterval += delta_time * self._speed
        if self.__currentInterval > self.interval:
            self.__currentInterval = 0
            if self.__currentImageIndex == len(self._images) - 1:
                self.__currentImageIndex = 0
                if self._currentAnimeState:  # anime state start
                    if self.__currentAnimeIndex == len(self._currentAnimeState) - 1:
                        self.__currentAnimeIndex = 0
                        if self._currentAnimeState != self._baseAnimeState:
                            self._currentAnimeState = self._baseAnimeState
                            self.pub_tmp_anime_state_finished()
                    else:
                        self.__currentAnimeIndex = (self.__currentAnimeIndex+1) % len(self._currentAnimeState)
                        self.action = self._currentAnimeState[self.__currentAnimeIndex]
            else:
                self.__currentImageIndex = (self.__currentInterval+1) % len(self._images)


class JoinedSurfaceRuleBase:
    """
    任何tile的值都不能等于0
    因为tile map的每个tile的id都是固定的，所以不设置mapperFunc
    """
    def __init__(self):
        self.id = 0
        #  [{方向: int(-2 相等, -1 不相等， 0 忽略, 其他相等)}]   ;; 不存在的邻居将被忽略
        self.rules: List[Tuple[Dict[tuple, int], ISpriteAssetInterface]] = []

    def get_sprite(self, loc, cost_map: numpy.ndarray):
        height, width = cost_map.shape
        center_v = self.id
        for rule, sp in self.rules:
            for k, v in rule.items():
                if v == 0:
                    continue
                x_, y_ = k[0] + loc[0], k[1] + loc[1]
                if x_ < 0 or y_ < 0 or x_ >= width or y_ >= height:
                    continue
                _v = cost_map[y_, x_]
                if _v == 0:
                    continue
                if v == -2:
                    v = center_v
                if v == -1 and _v == center_v:  # 不等于
                    break
                elif v != _v:
                    break
            else:
                return sp
        raise Exception("tile rule 有问题")


class JoinedSurfaceRenderComponent(RenderBase):
    """
    架上了layer.LayerMaskManager.refresh_area()
    没有重叠，一般用于刷新次数较少的东西，类似tile map
    """
    def __init__(self, config, joined_surf_rule_dict, terrain_map, grid_nav=None, layer=1, interval=0, layer_nu=1):
        super().__init__()
        self.config: IConfigInterface = config
        self.gridNav: IGridNavigationInterface = grid_nav
        self.layer = layer

        self.surfaces: List[pygame.Surface | None] = []
        self.interval: float = interval
        self._joinedSurfaceRuleDict: Dict[int, JoinedSurfaceRuleBase] = joined_surf_rule_dict
        self._cachedTerrainMap: numpy.ndarray = terrain_map.copy()
        self.__currentInterval = 0
        self.__currentSurfaceIndex = 0

        for nu in range(layer_nu):
            tmp_surface = pygame.Surface((
                self._cachedTerrainMap.shape[1] * config.MAP_BLOCK_SIZE[0],
                self._cachedTerrainMap.shape[0] * config.MAP_BLOCK_SIZE[1])
            ).convert_alpha()
            tmp_surface.fill((0, 0, 0, 0))
            self.surfaces.append(tmp_surface)

        for row_i, row in enumerate(self._cachedTerrainMap):
            for col_i, i in enumerate(row):
                if i == 0:
                    self._refresh_nav_layer((col_i, row_i), 0)
                    continue
                self._refresh_nav_layer((col_i, row_i), i)
        self._refresh_total_surface()
        self.anchor = .5, self.surfaces[0].get_height()/self.surfaces[0].get_width()/2

    def get_surface(self) -> pygame.Surface:
        return self.surfaces[self.__currentSurfaceIndex]

    def init_component(self, config, joined_surf_rule, terrain_map, grid_nav, interval=0, layer_nu=1):
        self._joinedSurfaceRuleDict = joined_surf_rule
        self._cachedTerrainMap = terrain_map.copy()
        self.interval = interval
        self.gridNav = grid_nav

        self.__currentSurfaceIndex = 0
        self.surfaces.clear()
        self.config = config
        config = self.config

        for nu in range(layer_nu):
            tmp_surface = pygame.Surface((
                self._cachedTerrainMap.shape[1] * config.MAP_BLOCK_SIZE[0],
                self._cachedTerrainMap.shape[0] * config.MAP_BLOCK_SIZE[1])
            ).convert_alpha()
            tmp_surface.fill((0, 0, 0, 0))
            self.surfaces.append(tmp_surface)

        for row_i, row in enumerate(self._cachedTerrainMap):
            for col_i, i in enumerate(row):
                if i == 0:
                    self._refresh_nav_layer((col_i, row_i), 0)
                    continue
                self._refresh_nav_layer((col_i, row_i), i)
        self._refresh_total_surface()

    def _refresh_surface(self, loc):
        config = self.config
        value = self._cachedTerrainMap[loc[1], loc[0]]
        if value == 0:
            sp = None
        else:
            sp = self._joinedSurfaceRuleDict[value].get_sprite(loc, self._cachedTerrainMap)
        for nu, tmp_surface in enumerate(self.surfaces):
            if sp is None:
                tmp_surface.fill((0, 0, 0, 0),
                                 pygame.Rect(loc[0] * config.MAP_BLOCK_SIZE[0], loc[1] * config.MAP_BLOCK_SIZE[1],
                                 *config.MAP_BLOCK_SIZE)
                                 )
            else:
                tmp_surface.blit(pygame.transform.smoothscale(sp.images[nu % len(sp.images)], sp.legalSize),
                                 (loc[0] * config.MAP_BLOCK_SIZE[0] + (config.MAP_BLOCK_SIZE[0] - sp.legalSize[0]) // 2,
                                  loc[1] * config.MAP_BLOCK_SIZE[1] + (config.MAP_BLOCK_SIZE[1] - sp.legalSize[1]) // 2)
                                 )

    def _refresh_total_surface(self):
        config = self.config
        for nu, tmp_surface in enumerate(self.surfaces):
            tmp_surface.fill((0, 0, 0, 0))
            for row_i, row in enumerate(self._cachedTerrainMap):
                for col_i, i in enumerate(row):
                    if i == 0:
                        continue
                    __sp = self._joinedSurfaceRuleDict[i].get_sprite((col_i, row_i), self._cachedTerrainMap)
                    tmp_surface.blit(
                        pygame.transform.smoothscale(__sp.images[nu % len(__sp.images)], __sp.legalSize),
                        (col_i * config.MAP_BLOCK_SIZE[0] + (config.MAP_BLOCK_SIZE[0] - __sp.legalSize[0]) // 2,
                         row_i * config.MAP_BLOCK_SIZE[1] + (config.MAP_BLOCK_SIZE[1] - __sp.legalSize[1]) // 2))

    def _refresh_nav_layer(self, loc, value):
        if self.gridNav:
            self.gridNav.refresh_node(loc, value, self.layer)

    def refresh_data(self, key, value, force=False):
        x, y = key
        his_value = self._cachedTerrainMap[y, x]
        if value == his_value and not force:
            return
        self._cachedTerrainMap[y, x] = value

        self._refresh_surface(key)
        self._refresh_nav_layer(key, value)

    def update(self, delta_time):
        if self.interval == 0:
            return
        self.__currentInterval += delta_time
        if self.__currentInterval >= self.interval:
            self.__currentInterval = 0
            self.__currentSurfaceIndex = (self.__currentSurfaceIndex + 1) % len(self.surfaces)


class JoinedLayerSurfaceRenderComponent(RenderBase):
    def __init__(self, config, map_size, interval=0, layer_nu=1):
        super().__init__()
        self.config: IConfigInterface = config
        self.interval = interval
        self.__currentInterval = 0
        self.__currentSurfaceIndex = 0
        self.layerNu = layer_nu
        self.joinedSurfaces: Dict[int, JoinedSurfaceRenderComponent] = {}
        self.surfaces: List[pygame.Surface] = []
        for nu in range(layer_nu):
            tmp_surface = pygame.Surface((
                map_size[0] * config.MAP_BLOCK_SIZE[0],
                map_size[1] * config.MAP_BLOCK_SIZE[1])
            ).convert_alpha()
            tmp_surface.fill((0, 0, 0, 0))
            self.surfaces.append(tmp_surface)

    def get_surface(self) -> pygame.Surface:
        return self.surfaces[self.__currentSurfaceIndex]

    def add_layer_surface(self, joined_surf_rule_dict, terrain_map, grid_nav=None, layer=1):
        tmp_r = JoinedSurfaceRenderComponent(
            self.config, joined_surf_rule_dict, terrain_map, grid_nav, layer, self.interval, self.layerNu)
        self.joinedSurfaces[layer] = tmp_r

        # sort
        tmp_joined_suf = {}
        for i in sorted(self.joinedSurfaces.keys()):
            tmp_joined_suf[i] = self.joinedSurfaces[i]
        self.joinedSurfaces = tmp_joined_suf

    def refresh_data(self, key, value, layer, force=False):
        self.joinedSurfaces[layer].refresh_data(key, value, force)
        self.refresh_surface(key)

    def refresh_surface(self, loc=None):
        if loc is None:
            for i in range(self.layerNu):
                for v in self.joinedSurfaces.values():
                    self.surfaces[i].blit(v.surfaces[i], (0, 0))
        else:
            rect = pygame.Rect(
                loc[0]*self.config.MAP_BLOCK_SIZE[0], loc[1]*self.config.MAP_BLOCK_SIZE[1],
                *self.config.MAP_BLOCK_SIZE)
            for i in range(self.layerNu):
                for v in self.joinedSurfaces.values():
                    self.surfaces[i].blit(v.surfaces[i].subsurface(rect), (rect.x, rect.y))

    def update(self, delta_time):
        if self.interval == 0:
            return
        self.__currentInterval += delta_time
        if self.__currentInterval >= self.interval:
            self.__currentInterval = 0
            self.__currentSurfaceIndex = (self.__currentSurfaceIndex + 1) % len(self.surfaces)


class CoverRenderComponent(RenderBase):
    """
    support:
    多条线段/多边形
    方形
    圆形/椭圆
    文字
    """
    TYPE_LINE = 0x1
    TYPE_RECT = 0x2
    TYPE_ARC = 0x3
    TYPE_TEXT = 0x4

    def __init__(self, suf_size, pencil, block_size=None):
        super().__init__()
        self.surface = pygame.Surface(suf_size).convert_alpha()
        self.surface.fill((0, 0, 0, 0))
        self.blockSize: tuple = block_size

        self.anchor = .5, self.surface.get_height()/2/self.surface.get_width()
        self.pencil: IPencilInterface = pencil

        self.lineStorage: Dict[Any, Tuple[Any, int, List[tuple]]] = {}
        self.rectStorage: Dict[Any, Tuple[Any, int, List[tuple]]] = {}
        # Tuple中[1]表示椭圆的区域(centerX, centerY, width, height), [2]为0表示填充, > 1>=表示线段粗细，
        # 第一个Tuple 椭圆或圆的局部 另一个表示全部
        self.arcStorage: Dict[Any, Tuple[Any, tuple, int, tuple] | Tuple[Any, tuple, int]] = {}
        self.textStorage: Dict[Any, Tuple[str, Any, list[tuple]]] = {}
        self.hidden = False
        self.showGridLine = False
        self.anchor = 0.5, suf_size[1] / suf_size[0] / 2

    def get_surface(self) -> pygame.Surface:
        if not self.hidden:
            return self.surface

    def _render(self):
        self.surface.fill((0, 0, 0, 0))
        for k, v in self.lineStorage.items():
            color, width, points = v
            for p_i in range(1, len(points)):
                s_p = v[p_i - 1]
                e_p = v[p_i]
                if self.blockSize:
                    s_p = s_p[0] * self.blockSize[0] + self.blockSize[0]//2, \
                        s_p[1] * self.blockSize[1] + self.blockSize[1]//2
                    e_p = e_p[0] * self.blockSize[0] + self.blockSize[0]//2, \
                        e_p[1] * self.blockSize[1] + self.blockSize[1]//2
                pygame.draw.line(self.surface, color, s_p, e_p, width)
        for k, v in self.rectStorage.items():
            color, width, blocks = v
            for block in blocks:
                s_p = block[:2]
                e_p = block[2:]
                if self.blockSize:
                    s_p = s_p[0] * self.blockSize[0], s_p[1] * self.blockSize[1]
                    e_p = e_p[0] * self.blockSize[0], e_p[1] * self.blockSize[1]
                s_p1 = min(s_p[0], e_p[0]), min(s_p[1], e_p[1])
                e_p1 = max(s_p[0], e_p[0]), max(s_p[1], e_p[1])
                size = e_p1[0]-s_p1[0], e_p1[1]-s_p1[1]
                pygame.draw.rect(self.surface, color, pygame.Rect(*s_p1, *size), width)
        for k, v in self.arcStorage.items():
            color, rect, width = v
            if self.blockSize:
                rect = pygame.Rect(
                    (rect[0]+1-rect[2])*self.blockSize[0]+self.blockSize[0]//2,
                    (rect[1]+1-rect[3])*self.blockSize[1]+self.blockSize[1]//2,
                    rect[2]*self.blockSize[0], rect[3]*self.blockSize[1]
                )
            else:
                rect = pygame.Rect(rect[0]-rect[2]//2, rect[1]-rect[3]//2, rect[2], rect[3])
            if len(v) > 3:
                pygame.draw.arc(self.surface, color, rect, v[3][0], v[3][1])
            else:
                pygame.draw.ellipse(self.surface, color, rect, width)
        for k, v in self.textStorage.items():
            text, color, points = v
            for point in points:
                tmp_suf = self.pencil.render(text, color)
                if self.blockSize:
                    if tmp_suf.get_width() > tmp_suf.get_height():
                        pygame.transform.smoothscale(
                            tmp_suf, self.blockSize[0], self.blockSize[0]/tmp_suf.get_width()*tmp_suf.get_height())
                    else:
                        pygame.transform.smoothscale(
                            tmp_suf, self.blockSize[1]/tmp_suf.get_height()*tmp_suf.get_width(), self.blockSize[1])

                    point = self.blockSize[0]*point[0]+self.blockSize[0]//2, \
                        self.blockSize[1]*point[1]+self.blockSize[1]//2

                pos = point[0] - tmp_suf.get_width()//2, point[1] - tmp_suf.get_height()//2
                self.surface.blit(tmp_suf, pos)

        if self.showGridLine:
            for y in range(self.surface.get_height()//self.blockSize[1]+1):
                pygame.draw.line(self.surface, (0, 255, 0), (0, y*self.blockSize[1]),
                                 (self.surface.get_width(), y*self.blockSize[1]))
            for x in range(self.surface.get_width()//self.blockSize[0]+1):
                pygame.draw.line(self.surface, (0, 255, 0), (x*self.blockSize[0], 0),
                                 (x*self.blockSize[0], self.surface.get_height()))

    def re_render(self):
        self._render()

    def clear(self):
        self.lineStorage.clear()
        self.rectStorage.clear()
        self.arcStorage.clear()
        self.textStorage.clear()
        self.re_render()

    def draw(self):
        pass
        super().draw()


class GridCoverRenderComponent(RenderBase):
    """
    support:
    多条线段/多边形
    方形
    圆形/椭圆
    文字
      - '-': 线段, value必须为list
      - '#': 单个线框, value必须为list
      - '1': 文字
      - others: 方块
    """

    def __init__(self, suf_size, map_block_size, pencil):
        super().__init__()
        self.mapBlockSize = map_block_size
        self.surface = pygame.Surface(suf_size).convert_alpha()
        self.surface.fill((0, 0, 0, 0))
        self._colorAreaDict: Dict[str, list | dict] = {}
        self.anchor = .5, self.surface.get_height()/2/self.surface.get_width()
        self.pencil: IPencilInterface = pencil

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def _render(self):
        self.surface.fill((0, 0, 0, 0))
        keys = list(self._colorAreaDict.keys())
        keys.sort()
        tmp_d = {}
        for i in keys:
            tmp_d[i] = self._colorAreaDict[i]
        self._colorAreaDict = tmp_d

        for k, v in self._colorAreaDict.items():
            color = v[0]
            if k.startswith('-'):
                for i in range(2, len(v)):
                    s_p = v[i-1]
                    e_p = v[i]
                    pygame.draw.line(
                        self.surface, color,
                        (s_p[0] * self.mapBlockSize[0] + self.mapBlockSize[0]//2,
                         s_p[1] * self.mapBlockSize[1] + self.mapBlockSize[1]//2),
                        (e_p[0] * self.mapBlockSize[0] + self.mapBlockSize[0]//2,
                         e_p[1] * self.mapBlockSize[1] + self.mapBlockSize[1]//2),
                        self.mapBlockSize[0]//10
                                     )
            elif k.startswith('#'):
                pygame.draw.rect(self.surface, color, pygame.Rect(v[1]), self.mapBlockSize[0]//10)
            elif k.startswith('1'):
                for i in v[1:]:
                    self.surface.blit(color, (i[0] * self.mapBlockSize[0], i[1] * self.mapBlockSize[1]))
            else:
                for i in v[1:]:
                    self.surface.fill(color, pygame.Rect(i[0] * self.mapBlockSize[0], i[1] * self.mapBlockSize[1],
                                                         *self.mapBlockSize))

    def clear(self):
        self._colorAreaDict.clear()
        self._render()

    def __getitem__(self, item):
        return self._colorAreaDict.get(item, None)

    def __delitem__(self, key):
        if key in self._colorAreaDict:
            del self._colorAreaDict[key]
            self._render()

    def __setitem__(self, key, value):
        self._colorAreaDict[key] = value
        if key.startswith('1'):
            suf = self.pencil.render(value[0])
            suf = pygame.transform.smoothscale(suf, self.mapBlockSize)
            value[0] = suf
        self._render()
