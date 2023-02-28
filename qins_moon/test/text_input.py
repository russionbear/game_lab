#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :text_input.py
# @Time      :07/01/2023
# @Author    :russionbear
# @Function  :function
import random
# if __name__ == "__main__":
#     run_code = 0
import time

import numpy


class A:
    def __init__(self):
        self.a = 0

    def b(self):
        pass

    @classmethod
    def b1(cls):
        pass

    @staticmethod
    def b2():
        pass


for j in range(5):
    # b = {i:i for i in range(10000)}

    start = time.time_ns()
    for i in range(10**8):
        pass

    print((time.time_ns()-start)/10**9)


"""
数学运算 pass * 1.05
创建/调用变量 pass * 1.5

list[]      pass * 2
obj.property pass * 2.33
dict[] pass * 2.33
dict.get pass * 2.5
set.add pass * 2.5

创建list pass * 1.5
创建dict pass * 1.6
创建set  pass * 4
创建对象  pass * 7

staticmethod.func() pass * 4
obj.func() pass * 4
class.func() pass * 5

random.randint pass * 24

创建1000 个 (1000, 1000) numpy.ndarray  2s
创建10 个 (10000, 10000) numpy.ndarray  1s
numpy.ndarray[shape: (10000, 10000)] fill 0.037

"""
