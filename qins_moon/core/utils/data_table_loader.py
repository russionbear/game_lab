#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :data_table_loader.py
# @Time      :15/01/2023
# @Author    :russionbear
# @Function  :function
import os
import re
from typing import Type

import pandas

from qins_moon.core.utils.data_structure import TableRowBase, NameIdTableStructure


# #####################################
# data table 相关
# #####################################


class DataTableLoader:
    """
    数据表规范：
    1. 表名: 手写字母大写，峰驼法命名， 对应的存放表数据的变量名为表名（手写字母变为小写）+"Table"

    2. 表类型:
        (1) table（一行一个类），
        (2) dict(类型为Dict[str(行键), Dict[str, str|float|int|bool])，
        (3) general，存放全局变量, 一行一个字段，前两列不会读取
        (4) names: 一列为一种类型的名称
    3. 任何表前两行用来描述表的信息，之后的两行空(不会读取)、类型为names、table的表可以用这两行来描述列名对应的信息

    4. 依据提供变量的属性名称来提取数据表中的值，对应的值不存在将会报错，多余的值不会读取

    """

    table_storage_path = ''

    @staticmethod
    def scan_tables() -> list[tuple[str, str]]:
        rlt = []
        for i in os.listdir(DataTableLoader.table_storage_path):
            if not os.path.isdir(i):
                continue
            for j in os.listdir(os.path.join(DataTableLoader.table_storage_path, i)):
                if os.path.isdir(os.path.join(DataTableLoader.table_storage_path, i, j)):
                    continue
                rlt.append((i, j))
        return rlt

    @staticmethod
    def load_data(table_author, data_table_name, t, root_table):
        """

        :param t:
        :param data_table_name:
        :param table_author:
        :param root_table:该对象中应包含属性author,name
        :return:
        """
        root_table.dataTableId = table_author, data_table_name, t

        for table_name in root_table.__dict__.keys():
            if re.match(r'^.*Table$', table_name) is None:
                continue
            try:
                table = pandas.read_excel(
                    os.path.join(DataTableLoader.table_storage_path, table_author, data_table_name, t + '.xlsx'),
                    table_name[0].upper() + table_name[1:-5], header=None)
            except ValueError:
                print(f"{table_name} ignored")
                continue
            table_info = {}
            for k, v in zip(table.loc[0, :], table.loc[1, :]):
                if pandas.isna(k):
                    continue
                table_info[k] = v
            try:
                table.columns = table.loc[4, :]
            except KeyError:
                print(f"{table_name} ignored")
                continue
            table.drop(range(5), inplace=True)

            print(f"now table {table_name}")
            if table_info.get('tableType', None) == "dict":
                root_table.__setattr__(table_name, DataTableLoader.load_dict_from_df(table))
            elif table_info.get('tableType', None) == "names":
                root_table.__setattr__(table_name, DataTableLoader.load_names_from_df(table))
            elif table_info.get('tableType', None) == "general":
                DataTableLoader.load_general_from_df(table, root_table.__getattribute__(table_name))
            else:
                DataTableLoader.load_table_from_df(table, root_table.__getattribute__(table_name).itemType,
                                                   root_table.__getattribute__(table_name))
                # if 'model_prefix' in type(rlt.__getattribute__(table_name)).__dict__:
                #     setattr(type(rlt.__getattribute__(table_name)), 'model_prefix',
                #             table_info.get('model_prefix', None))
        return root_table

    @staticmethod
    def load_dict_from_df(table: pandas.DataFrame):
        rlt = {}
        keys = list(table.keys())
        for row_name, row in table.iterrows():
            tmp = {}
            for k in keys[1:]:
                tmp[k] = row[k]
            rlt[row[0]] = tmp
        return rlt

    @staticmethod
    def load_names_from_df(table: pandas.DataFrame):
        """
        返回值中，每列的名称都不重复
        :param table:
        :return:
        """
        rlt = {}
        for k, v in table.items():
            tmp = set()
            for item in v:
                tmp.add(item)
            rlt[k] = list(tmp)
        return rlt

    @staticmethod
    def load_table_from_df(table: pandas.DataFrame, cls: Type[TableRowBase], rlt: NameIdTableStructure):
        for row_name, row in table.iterrows():
            tmp = cls()
            for k in tmp.__dict__.keys():
                if k not in table.keys():
                    raise IndexError(f"{k} not in {list(table.keys())}")
                tmp.__setattr__(k, row[k])
            if pandas.isna(tmp.id) or pandas.isna(tmp.name):
                continue
            if not rlt.add(tmp):
                raise IndexError(f'exited id {tmp.id}')
            tmp.correct_property_type()

    @staticmethod
    def load_general_from_df(table: pandas.DataFrame, rlt):
        keys = list(table.keys())
        tmp = {}
        for row_name, row in table.iterrows():
            # print(row[keys[2]])
            if pandas.isna(keys[2]):
                continue
            if pandas.isna(row[keys[2]]):
                continue
            tmp[row[keys[2]]] = row[keys[3]]
        for k in rlt.__dict__.keys():
            if k not in tmp:
                raise IndexError(f'{k} not exited {tmp}')
            rlt.__setattr__(k, tmp[k])
