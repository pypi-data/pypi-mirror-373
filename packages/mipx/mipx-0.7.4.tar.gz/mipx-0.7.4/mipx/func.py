# -*- coding: utf-8 -*-
# @Time    : 2023/4/28 23:54
# @Author  : luyi

from collections import UserDict
from .constants import OptimizationStatus
from .utilx import is_list_or_tuple


def debugVar(vars, no_zero=False):
    """
    调试var的方法

    :param _type_ vars: 可以是变量的集合或者单个变量
    :param bool no_zero: 不输出<=0的值, defaults to True
    """
    is_list = False
    if isinstance(vars, UserDict) or isinstance(vars, dict):
        vars = vars.values()
        is_list = True
    if is_list_or_tuple(vars):
        is_list = True
    if is_list:
        for var in vars:
            if no_zero:
                if var.X <= 0.01:
                    continue
            print(f"{var.VarName}:{var.X}")
    else:
        print(f"{vars.VarName}:{vars.X}")  # type:ignore


def success(statue: OptimizationStatus):
    """
    判断是否求解成功

    :param statue: 求解状态
    :return: 是否成功
    """
    return statue in [OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE]


def name_str(base_name, *key) -> str:
    """
    名称组合
    """
    if base_name == "":
        return ""
    re_name = key
    if is_list_or_tuple(key):
        re_name = ",".join(str(x) for x in key)
    return f"{base_name}[{re_name}]"
