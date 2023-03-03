#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :data_structure.py
# @Time      :02/01/2023
# @Author    :russionbear
import random
from bisect import bisect_left, bisect_right

import kdtree
import numpy
import pandas
from typing import Dict, TypeVar, Generic, Tuple, Type, List, Any, Set

AnyT = TypeVar("AnyT")


def get_unique_id(collection):
    while True:
        new_id = random.randint(100, 0xffff)
        if new_id in collection:
            continue
        return new_id


class NameIdTableStructure(Generic[AnyT]):
    def __init__(self, t: AnyT | None = None):
        self.itemType: Type[AnyT] | None = type(t) if t is not None else None
        self.idDict: Dict[int, AnyT] = {}
        self.nameDict: Dict[str, AnyT] = {}

    def rename(self, id_, name):
        tmp = self.idDict[id_]
        if tmp.name == name:
            return
        if name in self.nameDict:
            raise IndexError(f"rename: {tmp.name}->{name} exited")
        del self.nameDict[tmp.name]
        self.nameDict[name] = tmp

    def add(self, v: AnyT):
        if v.id in self.idDict or v.name in self.nameDict:
            raise Exception("NameIdTableStructure add error")
        self.idDict[v.id] = v
        self.nameDict[v.name] = v
        return True

    def get_unique_id(self) -> int:
        while True:
            new_id = random.randint(100, 0xffff)
            if new_id in self.idDict:
                continue
            return new_id

    def sort(self, key):
        tmp_d = sorted(self.idDict.items(), key=key)
        self.idDict.clear()
        for k, v in tmp_d:
            self.idDict[k] = v

    def __setitem__(self, key, value: AnyT):
        if value.id in self.idDict or value.name in self.nameDict:
            raise Exception("NameIdTableStructure add error")
        self.idDict[value.id] = value
        self.nameDict[value.name] = value

    def __getitem__(self, item) -> AnyT:

        if type(item) == int:
            return self.idDict.get(item, None)
        return self.nameDict.get(item, None)

    def __contains__(self, item):
        if type(item) == int:
            return item in self.idDict
        else:
            return item in self.nameDict

    def __delitem__(self, key):
        """

        :param key: 不为空
        :return:
        """
        if type(key) == int:
            tmp = self.idDict[key]
        elif type(key) == str:
            tmp = self.nameDict[key]
        else:
            for i in self.idDict.values():
                if i == key:
                    tmp = i
                    break
            else:
                return
        del self.idDict[tmp.id]
        del self.nameDict[tmp.name]


class LocIdTableStructure(Generic[AnyT]):
    def __init__(self, t: AnyT | None = None, open_kdtree=False):
        self.itemType: Type[AnyT] | None = type(t) if t is not None else None
        self.idDict: Dict[int, AnyT] = {}
        self.locDict: Dict[Tuple[int, int], AnyT] = {}
        self.kdTree: kdtree.KDNode | None = None if not open_kdtree else kdtree.create(dimensions=2)

    def add(self, v: AnyT):
        if v.id in self.idDict or v.loc in self.locDict:
            raise Exception("LocIdTableStructure add error")
            # return False
        self.idDict[v.id] = v
        self.locDict[v.loc] = v
        if self.kdTree:
            self.kdTree.add(v.loc)
        return True

    def move(self, o, n) -> bool:
        # print(o, n, self.locDict)
        if o == n:
            return True
        if n in self.locDict:
            return False
            # raise IndexError("already exit location")
        tmp = self.locDict[o]
        self.locDict[n] = tmp
        tmp.loc = n

        if self.kdTree:
            self.kdTree.add(n)

        del self.locDict[o]

        if self.kdTree:
            self.kdTree.remove(o)
        return True

    def move_by_id(self, id_, n) -> bool:
        if id_ not in self.idDict:
            raise IndexError("no such id")
        tmp = self.idDict[id_]
        return self.move(tmp.loc, n)

    def get_unique_id(self) -> int:
        while True:
            new_id = random.randint(100, 0xffff)
            if new_id in self.idDict:
                continue
            return new_id

    # def __setitem__(self, key, value: AnyT):
    #     if value.id in self.idDict or value.loc in self.locDict:
    #         raise Exception("LocIdTableStructure add error")
    #     self.idDict[value.id] = value
    #     self.locDict[value.loc] = value

    def __contains__(self, item):
        if type(item) == int:
            return item in self.idDict
        else:
            return item in self.locDict

    def __getitem__(self, item) -> AnyT:
        if type(item) == int:
            return self.idDict.get(item, None)
        return self.locDict.get(item, None)

    def __delitem__(self, key):
        """

        :param key: 不为空
        :return:
        """
        if type(key) == int:
            tmp = self.idDict[key]
        elif type(key) == tuple:
            tmp = self.locDict[key]
        else:
            for i in self.idDict.values():
                if i == key:
                    tmp = i
                    break
            else:
                return
        del self.idDict[tmp.id]
        del self.locDict[tmp.loc]
        if self.kdTree:
            self.kdTree.remove(tmp.loc)


class LocIdsTableStructure(Generic[AnyT]):
    def __init__(self, t: AnyT | None = None, open_kdtree=False):
        self.itemType: Type[AnyT] | None = type(t) if t is not None else None
        self.idDict: Dict[int, AnyT] = {}
        self.locDict: Dict[Tuple[int, int], Set[AnyT]] = {}
        self.kdTree: kdtree.KDNode | None = None if not open_kdtree else kdtree.create(dimensions=2)

    def __in_loc(self, v):
        if v.loc not in self.locDict:
            s = set()
            self.locDict[v.loc] = s
            if self.kdTree:
                self.kdTree.add(v.loc)
        else:
            s = self.locDict[v.loc]
        s.add(v)

    def __out_loc(self, v):
        if v.loc not in self.locDict:
            return
        s = self.locDict[v.loc]
        s.remove(v)
        if not s:
            if self.kdTree:
                self.kdTree.remove(v.loc)
            del self.locDict[v.loc]

    def add(self, v: AnyT):
        if v.id in self.idDict:
            return False
        self.idDict[v.id] = v
        self.__in_loc(v)
        return True

    def move_by_id(self, id_, n):
        if id_ not in self.idDict:
            raise IndexError("no such id")

        tmp = self.idDict[id_]
        self.__out_loc(tmp)
        tmp.loc = n
        self.__in_loc(tmp)

    def get_unique_id(self) -> int:
        while True:
            new_id = random.randint(100, 0xffff)
            if new_id in self.idDict:
                continue
            return new_id

    def __setitem__(self, key, value: AnyT):
        if value.id in self.idDict:
            raise Exception("LocIdTableStructure add error")
        self.idDict[value.id] = value
        self.__in_loc(value)
        # self.locDict[value.loc] = value

    def __contains__(self, item):
        if type(item) == int:
            return item in self.idDict
        else:
            if item.loc not in self.locDict:
                return False
            return item in self.locDict[item.loc]

    def __getitem__(self, item) -> AnyT | Set[AnyT] | None:
        if type(item) == int:
            return self.idDict.get(item, None)
        return self.locDict.get(item, None)

    def __delitem__(self, key):
        """

        :param key: 不为空
        :return:
        """
        if type(key) == int:
            tmp = self.idDict[key]
        elif type(key) == tuple:
            if key not in self.locDict:
                return
            for i in self.locDict[key]:
                del self.idDict[i.id]
            del self.locDict[key]
            return
        else:
            for i in self.idDict.values():
                if i == key:
                    tmp = i
                    break
            else:
                return
        del self.idDict[tmp.id]
        self.__out_loc(tmp)


class LocationsIdTableStructure(Generic[AnyT]):
    def __init__(self, t: AnyT | None = None, open_kdtree=False):
        self.itemType: Type[AnyT] | None = type(t) if t is not None else None
        self.idDict: Dict[int, AnyT] = {}
        self.locDict: Dict[Tuple[int, int], AnyT] = {}
        self.kdTree: kdtree.KDNode | None = None if not open_kdtree else kdtree.create(dimensions=2)

    def __in_loc(self, v):
        for i in v.locations:
            if i in self.locDict:
                raise Exception('')
            self.locDict[i] = v
            if self.kdTree:
                self.kdTree.add(i)

    def __out_loc(self, v):
        for i in v.locations:
            del self.locDict[i]
            if self.kdTree:
                self.kdTree.remove(i)

    def add(self, v: AnyT):
        if v.id in self.idDict:
            return False
        self.__in_loc(v)
        self.idDict[v.id] = v
        return True

    def get_unique_id(self) -> int:
        while True:
            new_id = random.randint(100, 0xffff)
            if new_id in self.idDict:
                continue
            return new_id

    def __setitem__(self, key, value: AnyT):
        if value.id in self.idDict or value.loc in self.locDict:
            raise Exception("LocIdTableStructure add error")
        self.idDict[value.id] = value
        self.__in_loc(value)

    def __contains__(self, item):
        if type(item) == int:
            return item in self.idDict
        else:
            return item in self.locDict

    def __getitem__(self, item) -> AnyT:
        if type(item) == int:
            return self.idDict.get(item, None)
        return self.locDict.get(item, None)

    def __delitem__(self, key):
        """

        :param key: 不为空
        :return:
        """
        if type(key) == int:
            tmp = self.idDict[key]
        elif type(key) == tuple:
            tmp = self.locDict[key]
        else:
            for i in self.idDict.values():
                if i == key:
                    tmp = i
                    break
            else:
                return
        del self.idDict[tmp.id]
        self.__out_loc(tmp)


class BisectList(Generic[AnyT]):
    def __init__(self, key=None):
        self._list: List[AnyT] = []
        self._key = key
        self.set_key(key)

    def set_key(self, key):
        if key is None:
            self._key = lambda a: a
        else:
            self._key = key

    def sort(self):
        self._list.sort(key=self._key)

    def find(self, v2):
        """
        根据值来查找对象
        :param v2:
        :return:
        """
        l0 = list(map(self._key, self._list))
        index = bisect_left(l0, v2)
        if l0[index] != v2:
            # if index == -1 or index >= len(l0):
            return None
        return self._list[index]

    def index_of(self, value):
        l0 = list(map(self._key, self._list))
        index = -1
        v2 = self._key(value)
        for i1, i in enumerate(self._list[bisect_left(l0, v2):]):
            if self._key(i) != v2:
                break
            if i != value:
                continue
            index = i1
            break
        return index

    def __contains__(self, item):
        return self.index_of(item) != -1

    def remove(self, e):
        index = self.index_of(e)
        if index != -1:
            self._list.pop(index)

    def append(self, e):
        self._list.insert(bisect_right(list(map(self._key, self._list)), self._key(e)), e)

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def list(self):
        """
        不要更改返回数组里面的值
        :return:
        """
        return self._list


class TableRowBase:
    def __init__(self):
        self.id: int = 0
        self.name: str = ""
        self.callName: str = ""

    def correct_property_type(self):
        for k, v in self.__dict__.items():
            if pandas.isna(v):
                self.__setattr__(k, None)


class RegistryBase(Generic[AnyT]):
    def __init__(self):
        self._storage: Dict[Any, AnyT] = {}

    def __getitem__(self, item):
        return self._storage.get(item, None)

    def __contains__(self, item):
        return item in self._storage

    def __delitem__(self, key):
        if key in self._storage:
            del self._storage[key]

    def __setitem__(self, key, value):
        if key in self._storage:
            raise Exception(f'{key} already exited')
        self._storage[key] = value


class JoinedNdarray:
    """
    像ndarray地方法都用ndarray规则，否则 x, y
    """

    def __init__(self, map_size, block_size):
        self.mapSize = map_size
        self.blockMapSize = map_size[0] // block_size[0], map_size[1] // block_size[1]
        self.blockSize = block_size
        self.storage: Dict[Tuple[int, int], numpy.ndarray] = {}

    def add_block(self, key, value):
        self.storage[key] = value

    def combine(self):
        rlt = numpy.zeros((self.mapSize[1], self.mapSize[0]), dtype=numpy.float_)
        for k, v in self.storage.items():
            rlt[
            k[1] * self.blockSize[1]: k[1] * self.blockSize[1] + self.blockSize[1],
            k[0] * self.blockSize[0]: k[0] * self.blockSize[0] + self.blockSize[0]
            ] = v
        return rlt

    @property
    def shape(self):
        return self.mapSize[1], self.mapSize[0]

    @property
    def nbytes(self):
        return len(self.storage) * list(self.storage.values())[0].nbytes

    def __getitem__(self, item):
        block_size = self.blockSize
        loc = item[0] // block_size[1], item[1] // block_size[0]
        nd_arr = self.storage.get((loc[1], loc[0]), None)
        if nd_arr is None:
            return -1
        loc1 = item[0] % block_size[1], item[1] % block_size[0]
        return nd_arr[loc1]

    def __setitem__(self, key, value):
        block_size = self.blockSize
        loc = key[0] // block_size[1], key[1] // block_size[0]
        nd_arr = self.storage.get((loc[1], loc[0]), None)
        loc1 = key[0] % block_size[1], key[1] % block_size[0]
        nd_arr[loc1] = value
