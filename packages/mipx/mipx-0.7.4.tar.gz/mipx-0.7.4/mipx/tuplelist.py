# -*- coding: utf-8 -*-
# @Time    : 2023/4/1 10:41
# @Author  : luyi
from collections import UserList
from typing import List, Iterable
from warnings import warn

from .interface_ import ITuplelist
from .utilx import get_length, is_list_or_tuple


class tuplelist(ITuplelist):
    """
    For example:
      > l = tuplelist([(1, 2), (1, 3), (2, 3), (2, 4)])
      > print(l.select('*', '*'))
      [(1, 2), (1, 3), (2, 3), (2, 4)]
      > print(l.select('*', 3))
      [(1, 3), (2, 3)]
      > print(l.select(1, '*'))
      [(1, 2), (1, 3)]
    """

    def append(self, item):
        # 检查是否重复。若重复则不添加。
        if isinstance(item, UserList) or type(item) == type(
            []
        ):  # 由于特殊性，不进行过多的扩展。
            raise ValueError("append传入参数不能为集合")
        if item in self.data:
            return
        # 检查维度
        if self.dim is None:
            self.dim = get_length(item)
        else:
            if self.dim != get_length(item):
                raise ValueError("传入的数据维度不一致。")
        super().append(item)

    def extend(self, other: Iterable[any]):  # type: ignore
        # 检查是否重复。
        if isinstance(other, UserList):
            datas = other.data
        else:
            datas = other
        for item in datas:
            self.append(item)

    def __init__(self, seq=None):
        seq = self._duplicate(seq)
        if len(seq) == 0:
            self.dim = None
            super().__init__([])
        else:
            self.dim = get_length(seq[0])
            super().__init__(seq)

    def _get_dim(self):
        if self.dim is None:
            if len(self) == 0:
                self.dim = 0
                return self.dim
            self.dim = get_length(self[0])
        return self.dim

    def quickselect(self, *pattern) -> List:
        dim = len(pattern)
        if dim == 0:
            return list(self)  # type: ignore
        if len(self) == 0:
            return []
        li = []
        if self._get_dim() == 1:
            for key in self:
                p = pattern[0]
                if p == "*" or p == key:
                    li.append(key)
            return li
        for key in self:
            ok = True
            # 判定key是否可以迭代
            for i, k in enumerate(key):
                p = pattern[i]
                if p == "*":
                    continue
                if p != k:
                    ok = False
                    break
            if ok:
                li.append(key)
        return li

    def select(self, *args) -> List:
        warn(f"call to deprecated function,use quickselect function")
        values = [*args]
        if len(self.data) == 0:
            return []
        if len(values) == 0:  # 全选
            return self.data
        if self.dim is None:
            self.dim = len(values)
        if self.dim != len(values):
            raise ValueError("传入的数据个数异常")
        _dim_ok_index = []
        _list_num_range = [i for i in range(len(self.data))]
        # 为了减少其他方法如pop,remove 等操作。将计算的操作放入该位置。
        # 会存在重复计算的问题。
        _keys = []
        for i in range(self.dim):
            temp = []
            for tu in self.data:
                _dim = get_length(tu)
                # 检查传入的参数维度是否一致
                if _dim != self.dim:
                    raise ValueError("传入的数据维度不一致。")
                if is_list_or_tuple(tu):
                    temp.append(tu[i])
                else:
                    temp.append(tu)
            _keys.append(temp)

        for i, key in enumerate(values):
            if key == "*":
                _dim_ok_index.append(_list_num_range)
                continue
            if isinstance(key, (float, int, str)):
                key = [key]
            _dim_ok_index.append([j for j, x in enumerate(_keys[i]) if x in key])
        flag = []
        for i, item in enumerate(_dim_ok_index):
            if i == 0:
                flag = item
                continue
            flag = list(set(flag).intersection(set(item)))
        return [key for i, key in enumerate(self.data) if i in flag]

    @staticmethod
    def _duplicate(initList):
        data = []
        if initList is not None:
            if type(initList) == type(data):
                data[:] = initList
            elif isinstance(initList, UserList):
                data[:] = initList.data[:]
            else:
                data = list(initList)
        l = [key for key in data]
        dim = None  # 检查传入的数据是否都是同一纬度的。
        for i, key in enumerate(l):
            if isinstance(key, list):
                t_key = tuple(key)
                l[i] = t_key
            _dim = get_length(key)
            if dim is None:
                dim = _dim
            else:
                if dim != _dim:
                    raise ValueError("传入的数据维度不一致。")
        return list(set(l))
