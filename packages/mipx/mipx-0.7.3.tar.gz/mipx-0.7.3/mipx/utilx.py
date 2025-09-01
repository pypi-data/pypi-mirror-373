# -*- coding: utf-8 -*-
# @Time    : 2023/4/2 15:17
# @Author  : luyi
import inspect
from typing import Tuple, Optional, Any
from math import ceil, floor
from .constants import Vtype

INFINITY = 1000000000000


def get_update_lub(lb, ub: Any, vtype: Vtype):
    if lb is None:
        lb = 0
    if ub is None:
        ub = INFINITY
    if vtype == Vtype.INTEGER:
        lb = ceil(lb)
        ub = floor(ub)

    if vtype == Vtype.BINARY:
        if ub >= 1:
            ub = 1
        else:
            ub = 0
        if lb <= 0:
            lb = 0
        else:
            lb = 1
    if lb > ub:
        raise Exception("变量lb > ub")
    return lb, ub


def get_length(arg) -> int:
    if is_list_or_tuple(arg):
        return len(arg)
    return 1


def is_list_or_tuple(items) -> bool:
    """
    是否是list或tupe类型
    """
    return isinstance(items, (list, tuple))


def is_real(expr):
    return isinstance(expr, (int, float)) and not isinstance(expr, (complex,))


def is_generator(obj):
    return inspect.isgeneratorfunction(obj) or inspect.isgenerator(obj)


def get_combinations(lst):
    """
    对于一个由若干个子列表组成的列表，返回其中所有元素的组合方式
    例如，对于输入 [[1,2],[3,4]] ，调用 get_combinations() 函数会返回 [[1, 3], [1, 4], [2, 3], [2, 4]]，
    对于更复杂的列表，例如 [[1, 2], [3], [4, 5, 6]] ，调用 get_combinations() 函数会返回
    [[1, 3, 4], [1, 3, 5], [1, 3, 6], [2, 3, 4], [2, 3, 5], [2, 3, 6]]，
    也就是每个子列表中的元素都和其它子列表中的所有元素进行了组合。
    :param lst: 由若干个子列表组成的列表
    :return: 所有元素的组合方式，以列表形式返回
    """
    if not isinstance(lst, list):
        lst = [lst]
    if len(lst) == 1:
        return lst[0]
    else:
        combinations = []
        sub_combinations = get_combinations(lst[1:])
        if not isinstance(sub_combinations, list):
            sub_combinations = [sub_combinations]
        elems = lst[0]
        if not isinstance(elems, list):
            elems = [elems]
        for elem in elems:
            for sub_elem in sub_combinations:
                com = ()
                if is_list_or_tuple(elem):
                    elem = tuple(elem)
                else:
                    elem = tuple([elem])
                if is_list_or_tuple(sub_elem):
                    sub_elem = tuple(sub_elem)
                else:
                    sub_elem = tuple([sub_elem])
                com += elem + sub_elem
                combinations.append(com)
        return combinations


def tuple_fuzzy_match(tuple_value1, tuple_value2) -> bool:
    if not is_list_or_tuple(tuple_value1) and not is_list_or_tuple(tuple_value2):
        tuple_value1 = [tuple_value1]
        tuple_value2 = [tuple_value2]
    if len(tuple_value1) != len(tuple_value2):
        raise ValueError("元组大小不匹配")
    for i, v in enumerate(tuple_value1):
        if v == "*" or tuple_value2[i] == "*":
            continue
        if v != tuple_value2[i]:
            return False
    return True


def tuple_fuzz_match_list(
    tuple_value1, tuple_value_list
) -> Tuple[bool, Optional[tuple]]:
    """
    模糊匹配
    :param tuple_value1:
    :param tuple_value_list:
    :return:
    """
    for v in tuple_value_list:
        if tuple_fuzzy_match(tuple_value1, v):
            return True, v
    return False, None


def check_bool_var(*args):
    """检测若不是ool变量，则抛出异常"""
    for arg in args:
        if is_list_or_tuple(arg) or is_generator(arg):
            for ar in arg:
                if not is_bool_var(ar):
                    raise RuntimeError(f"{ar.VarName} is not a binary variable.")
        else:
            if not is_bool_var(arg):
                raise RuntimeError(f"{arg.VarName} is not a binary variable.")


def is_bool_var(var) -> bool:
    """是否是bool变量"""
    try:
        if not (var.UB == 1 and var.LB == 0):
            return False
        return True
    except Exception as _:
        return True


def pre_condition(condition: bool, msg: str):
    if not condition:
        raise Exception(msg)


if __name__ == "__main__":
    print(get_combinations([[(2, 8), (2, 3)], [(1, 2), (2, 3)]]))
