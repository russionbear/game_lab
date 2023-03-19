#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: parse_command.py
# @time: 3/14/2023 7:44 PM

import re
from typing import Any


def parse_command(s0, arg_names=None, defaults=None):
    """
    kw参数第一个字符不能为数字, 复杂的东西用双引号括起来, 里面可有有\", 只是  '\'  会被转成 \\
    没有详细的报错信息, 最多返回None
    :param defaults: Dict[str: str]
    :param arg_names: List[str]
    :param s0:
    :return:
    """
    str_locations = []
    kw_arg_locations = []
    world_locations = []

    for m in re.finditer(r'"(.*?[^\\])"', s0):
        str_locations.append((m.start() + 1, m.end() - 1))

    for m in re.finditer(r'-?\w+', s0):
        start_i, end_i = m.start(), m.end()
        s_vlue = m.group()
        for i in str_locations:
            if i[0] <= start_i <= i[1] or i[1] <= end_i <= i[1]:
                break
        else:
            if s_vlue[0] == '-' and (len(s_vlue) == 1 or re.match('\d', s_vlue[1]) is None):
                kw_arg_locations.append((m.start(), m.end()))
            else:
                world_locations.append((m.start(), m.end()))

    if not world_locations:
        world_locations = str_locations
    else:
        for i in str_locations:
            if i[1] < world_locations[0][0]:
                world_locations.insert(0, i)
            elif i[0] > world_locations[-1][1]:
                world_locations.append(i)
            else:
                for j in range(1, len(world_locations)):
                    if world_locations[j - 1][1] < i[0] < world_locations[j][0]:
                        world_locations.insert(j, i)
                        break

    cmd_name_loc = world_locations.pop(0)

    kw_start_index = 0
    if kw_arg_locations:
        kw_start_index = kw_arg_locations[0][0]

    kw_arg: Any = {}
    loc_arg = []
    if kw_start_index != 0:  # 有kw
        for i in range(len(kw_arg_locations) - 1):
            _h_l = kw_arg_locations[i]
            _finite = kw_arg_locations[i + 1][0]
            s_value = s0[_h_l[0]:_h_l[1]][1:]
            if s_value in kw_arg:
                tmp_l = kw_arg[s_value]
            else:
                tmp_l = []
                kw_arg[s_value] = tmp_l
            for j in world_locations:
                if j[1] < _h_l[0]:
                    continue
                if j[0] > _finite:
                    break
                tmp_l.append(s0[j[0]:j[1]])

        _h_l = kw_arg_locations[-1]
        tmp_l = []
        kw_arg[s0[_h_l[0]:_h_l[1]][1:]] = tmp_l
        for i in world_locations:
            if i[0] > kw_arg_locations[-1][0]:
                tmp_l.append(s0[i[0]:i[1]])

        for i in world_locations:
            if i[0] > kw_start_index:
                break
            loc_arg.append(s0[i[0]:i[1]])
    else:
        for i in world_locations:
            loc_arg.append(s0[i[0]:i[1]])

    # # 处理\
    # print(loc_arg)
    # print(kw_arg)
    # loc_arg = [i.replace(r'\\', '\\') for i in loc_arg]
    # kw_arg = {k: [i.replace(r'\\', '\\') for i in v] for k, v in kw_arg.items()}
    # print(loc_arg)
    # print(kw_arg)

    if arg_names is not None:
        rlt = {}
        for i1, i in enumerate(loc_arg):
            rlt[arg_names[i1]] = [i]
        for k, v in kw_arg.items():
            if k not in arg_names:
                continue
            rlt[k] = v
        if defaults is not None:
            for k, v in defaults.items():
                if k not in rlt:
                    rlt[k] = str(v)

        for i in arg_names:
            if i not in rlt:
                return None

    else:
        rlt = [i for i in loc_arg] + [v for v in kw_arg.values()]

    return s0[cmd_name_loc[0]:cmd_name_loc[1]], rlt


if __name__ == '__main__':
    __s0 = r'print'
    print('--s0', __s0)
    print(parse_command(__s0))
