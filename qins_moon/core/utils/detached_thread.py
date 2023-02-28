#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :detached_thread.py
# @Time      :09/02/2023
# @Author    :russionbear
# @Function  :function

import threading
from queue import Queue
from typing import Dict, Tuple, Any, List
import time


class IDetachedThreadInterface:
    def __init__(self, max_size=8192):
        # {id: (kwargs, func, resultFunc)}
        self._taskDict: Dict[int, Tuple[dict, Any, Any]] = {}
        # [id, resultFunc, result]
        self._resultStorage: List[Tuple[int, Any, Any]] = []
        self.maxTaskQueueSize = max_size
        self._taskQueue = Queue(self.maxTaskQueueSize)
        self._currentStartId = 1  # 不能为0

        self._thread: threading.Thread | None = None
        self.defaultMaxDeep = 1024

    def start(self):
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def stop(self):
        self._taskDict.clear()
        self._taskQueue.put(0)

    def add_task(self, func_kwargs, func, handle_func):
        if self._taskQueue.full():
            return 0
        id_ = self._currentStartId + self._taskQueue.qsize()
        self._currentStartId += 1
        func_kwargs['max_deep'] = self.defaultMaxDeep
        func_kwargs['can_stop'] = id_, self._can_stop
        self._taskDict[id_] = func_kwargs, func, handle_func
        self._taskQueue.put(id_)
        return id_

    def remove_task(self, id_):
        if id_ in self._taskDict:
            del self._taskDict[id_]

    def run(self):
        while True:
            task_id = self._taskQueue.get()
            if task_id == 0:
                break
            task = self._taskDict.get(task_id, None)
            if task is None:
                continue
            start_time = time.time_ns()
            rlt = task[1](**task[0])
            cost_time = time.time_ns() - start_time
            print(f"{task[1]} cost {cost_time/10**9}")
            self._resultStorage.append((task_id, task[2], rlt))

    def _can_stop(self, key):
        return self.defaultMaxDeep if key in self._taskDict else 0

    def publish_result(self):
        l0 = len(self._resultStorage)
        l1 = self._resultStorage[:l0]
        self._resultStorage = self._resultStorage[l0:]
        for i in l1:
            if i[0] not in self._taskDict:
                continue
            del self._taskDict[i[0]]
            i[1](i[2])
        self._currentStartId += l0
        if self._currentStartId + len(self._taskDict) > self.maxTaskQueueSize:
            self._currentStartId = 1


class DetachedThread(IDetachedThreadInterface):
    _instance = None

    def __init__(self, max_size=8192):
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self
        super().__init__(max_size)

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)
