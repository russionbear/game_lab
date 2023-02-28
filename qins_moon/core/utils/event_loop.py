#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :event_loop.py
# @Time      :13/02/2023
# @Author    :russionbear
# @Function  :function
from typing import Dict


class ITickEventLoopInterface:
    """
    类型: 直接分发，event和update结束后分发,
    mask: &1 is once, &10 direct rev
    以下两个规范可以带来性能上的提升
    一个函数是否只能监听一种类型的事件, 是
    是否支持对象销毁时撤销所有sub, 否
    sub成千上万类型的事件是不灵活的
    """

    def __init__(self):
        self._directOnceSubStorage: Dict[tuple, set] = {}
        self._directPermSubStorage: Dict[tuple, set] = {}
        self._endTickOnceSubStorage: Dict[tuple, set] = {}
        self._endTickPermSubStorage: Dict[tuple, set] = {}

        self._eventStorage = []

    def reset(self):
        self._directOnceSubStorage.clear()
        self._directPermSubStorage.clear()
        self._endTickOnceSubStorage.clear()
        self._endTickPermSubStorage.clear()
        self._eventStorage.clear()

    def publish(self, t, **kwargs):
        self._eventStorage.append((t, kwargs))
        # direct, once
        once_subs = self._directOnceSubStorage.get(t, None)
        if once_subs is not None:
            for sub in once_subs:
                sub(**kwargs)
            once_subs.clear()

        # direct, perm
        prem_subs = self._directPermSubStorage.get(t, None)
        if prem_subs is not None:
            for sub in prem_subs:
                sub(**kwargs)

    def subscribe(self, t, func, once=False, direct=False):
        if once:
            if direct:
                if t not in self._directOnceSubStorage:
                    self._directOnceSubStorage[t] = set()
                self._directOnceSubStorage[t].add(func)
            else:
                if t not in self._endTickOnceSubStorage:
                    self._endTickOnceSubStorage[t] = set()
                self._endTickOnceSubStorage[t].add(func)
        else:
            if direct:
                if t not in self._directPermSubStorage:
                    self._directPermSubStorage[t] = set()
                self._directPermSubStorage[t].add(func)
            else:
                if t not in self._endTickPermSubStorage:
                    self._endTickPermSubStorage[t] = set()
                self._endTickPermSubStorage[t].add(func)

    def unsubscribe(self, t, func):
        if func in self._directPermSubStorage:
            self._directPermSubStorage[t].remove(func)
        if func in self._directOnceSubStorage:
            self._directOnceSubStorage[t].remove(func)
        if func in self._endTickPermSubStorage:
            self._endTickPermSubStorage[t].remove(func)
        if func in self._endTickOnceSubStorage:
            self._endTickOnceSubStorage[t].remove(func)

    def update(self, delta_time):
        for t, kwargs in self._eventStorage:
            # tick, once
            once_subs = self._endTickOnceSubStorage.get(t, None)
            if once_subs is not None:
                for sub in once_subs:
                    sub(**kwargs)
                once_subs.clear()

            # tick, perm
            prem_subs = self._endTickPermSubStorage.get(t, None)
            if prem_subs is not None:
                for sub in prem_subs:
                    sub(**kwargs)
        self._eventStorage.clear()


if __name__ == '__main__':
    func1 = ITickEventLoopInterface().subscribe
    func2 = ITickEventLoopInterface().subscribe
    print(func1)
    print(hash(func1), hash(func2))
    print(hash(ITickEventLoopInterface().subscribe))
