#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :test_numpy.py
# @Time      :07/01/2023
# @Author    :russionbear
# @Function  :function

if __name__ == "__main__":
    import numpy as np
    import collections

    random_data = np.random.randint(1, 7, 10000)
    random_data.mean()  # 均值
    random_data.std()  # 标准差
    print(collections.Counter(random_data))
