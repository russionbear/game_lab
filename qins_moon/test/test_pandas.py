#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: test_pandas.py
# @time: 3/11/2023 4:26 PM

import pandas

# import pandas as pd
#
# file_path = r'E:\workspace\game_lab\qins_moon\res\tables\test\as\as.xlsx'
# df = pd.read_excel(file_path, sheet_name="Terrain", header=None)  # sheet_name不指定时默认返回全表数据
#
# # 打印表数据，如果数据太多，会略去中间部分
# print(df)
#
# l0 = [[i for i in range(10)] for j in range(10)]
# l0.insert(0, [])
# l0.insert(0, [])
# l0.insert(0, [])
# new_df = pd.DataFrame(l0)
# print(new_df)

import pandas as pd


with pd.ExcelWriter('excel1.xlsx') as writer:
    df1 = pd.DataFrame([[1]])
    df2 = pd.DataFrame([1, 2, 3, 4])
    df1.to_excel(writer, sheet_name='Sheet1', index=False)
    df2.to_excel(writer, sheet_name='Sheet2', index=False)