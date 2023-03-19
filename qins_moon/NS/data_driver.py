#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: data_driver.py
# @time: 3/19/2023 10:16 AM
from qins_moon.NS.data_node import NSDataNode


class NSController:
    def __init__(self, dn):
        self.rootDataNode: NSDataNode = dn
