#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :event_loop.py
# @Time      :13/02/2023
# @Author    :russionbear
# @Function  :function

from qins_moon.core.utils.event_loop import ITickEventLoopInterface


class TickEventLoop(ITickEventLoopInterface):
    _instance = None

    def __init__(self):
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self
        super().__init__()

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)
