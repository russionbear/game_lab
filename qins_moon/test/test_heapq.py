#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :test_heapq.py
# @Time      :11/01/2023
# @Author    :russionbear
# @Function  :function

from heapq import heappop, heappush

pq1 = []
heappush(pq1, 5)
heappush(pq1, 10)
heappush(pq1, 1)
print(pq1)


class A:
    def __init__(self, z):
        self.zindex = z

    def __lt__(self, other):
        return self.zindex < other.id

    def __gt__(self, other):
        return self.zindex > other.id

    def __str__(self):
        return str(self.zindex)


pq = []
heappush(pq, A(5))
heappush(pq, A(10))
heappush(pq, A(1))
print([str(i) for i in pq])
