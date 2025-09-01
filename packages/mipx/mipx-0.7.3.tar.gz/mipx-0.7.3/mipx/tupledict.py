# -*- coding: utf-8 -*-
# @Time    : 2023/4/1 10:39
# @Author  : luyi
from abc import abstractmethod
from collections import UserDict
from typing import Dict, List, overload, Any, Tuple
from typing_extensions import TypeVar, TypeVarTuple, Generic, Unpack
import numpy as np
from .utilx import is_list_or_tuple, get_length


K = TypeVarTuple("K")
O = TypeVar("O")


class ITupledict(UserDict, Generic[O, Unpack[K]]):

    @overload
    def __setitem__(self, key: O, item: Any) -> None: ...

    @overload
    def __setitem__(self, key: Tuple[O, Unpack[K]], item: Any) -> None: ...

    def __setitem__(self, key, item: Any) -> None:
        super().__setitem__(key, item)

    @overload
    def __getitem__(self, key: O) -> Any: ...
    @overload
    def __getitem__(self, key: Tuple[O, Unpack[K]]) -> Any: ...
    def __getitem__(self, key) -> Any:
        return super().__getitem__(key)

    @abstractmethod
    def prod(self, coeff: Dict, *pattern) -> Any:
        """
        coeff为一个dict类型，指定待计算的元素的系数。coeff的key要与待计算的集合中的key能对应
        :param coeff:
        :param pattern:
        :return:
        """
        ...

    @abstractmethod
    def select(self, *pattern) -> List: ...

    @abstractmethod
    def sum(self, *pattern) -> Any:
        """
        快速求和
        """
        ...

    @abstractmethod
    def quicksum(self, *pattern) -> Any:
        """
        快速求和
        """
        ...

    @abstractmethod
    def quickselect(self, *pattern) -> List[Any]:
        """
        快速挑选符合模式的items
        """
        ...

    @abstractmethod
    def quickprod(self, coeff: Dict, *pattern) -> Any:
        """
        coeff为一个dict类型，指定待计算的元素的系数。coeff的key要与待计算的集合中的key能对应
        :param coeff:
        :param pattern:
        :return:
        """
        ...

    @abstractmethod
    def keyset(self, *pattern) -> List:
        """
        按pattern匹配的key集合
        keys = [(1,2,3,4), (2,3,4,5), (3,4,5,6)]
        '-': 表示排除，不参与返回
        '*': 表示任意值，参与返回
        '[]': 表示范围，参与返回
        '1': 表示具体值，参与返回
        keyset('-','*',[3,4],4) --> 返回 [(3,4,5)]
        :param pattern:
        :return:
        """
        ...

    @abstractmethod
    def key_pattern_set(self, *pattern) -> List:
        """
        按pattern匹配的key pattern集合
        keys = [(1,2,3,4), (2,3,4,5), (3,4,5,6)]
        '-': 表示排除，参与返回,返回"*"
        '*': 表示任意值，参与返回
        '[]': 表示范围，参与返回
        '1': 表示具体值，参与返回
        keyset('-','*',[3,4],4) --> 返回 [("*",3,4,5)]
        :param pattern:
        :return:
        """
        ...


class tupledict(ITupledict):
    """
    the keys are a tuplelist.
    """

    def __new__(cls, *args, **kwargs) -> ITupledict:
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        self._dim = None
        self._key_array = np.array([])
        self._key_ok = None
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if self._dim is None:
            self._dim = get_length(key)
        self._key_ok = None

        super().__setitem__(key, value)

    def prod(self, coeff: Dict, *pattern):  # type:ignore
        """
        coeff为一个dict类型，指定待计算的元素的系数。coeff的key要与待计算的集合中的key能对应
        :param coeff:
        :param pattern:
        :return:
        """
        keys = self._key_np_array(*pattern)
        if len(keys) == 0:
            return 0
        if keys.ndim == 1:
            return np.sum([self[key.item()] * coeff.get(key.item(), 0) for key in keys])
        return np.sum([self[tuple(key)] * coeff.get(tuple(key), 0) for key in keys])

    def _key_set_for_gurobi(self, *pattern):
        keys = self.keys()
        ava_key_array = np.array(list(keys))
        return tupledict._key_np_array_(ava_key_array, *pattern).tolist()

    @staticmethod
    def _key_np_array_(ava_key_array, *pattern):
        cols = []
        for i, pattern_item in enumerate(pattern):
            if pattern_item == "*":
                cols.append(i)
            elif pattern_item == "-":
                pass
            else:
                if isinstance(pattern_item, (str, int)):
                    pattern_item = [pattern_item]
                if is_list_or_tuple(pattern_item):
                    if ava_key_array.ndim == 2:
                        mask = np.isin(ava_key_array[:, i], pattern_item)
                    else:
                        mask = np.isin(ava_key_array, pattern_item)
                    ava_key_array = ava_key_array[mask]
                    cols.append(i)
                else:
                    raise ValueError(f"匹配模式{pattern_item}异常")
        if ava_key_array.ndim == 2:
            res = np.unique(ava_key_array[:, cols], axis=0)
            return res
        else:
            return np.unique(ava_key_array, axis=0)

    def _key_np_array(self, *pattern):
        if not self._key_ok:
            self._key_array = np.array(list(self.keys()))
            self._key_ok = True
        if self._key_array.size == 0:
            return np.array([])
        if (pattern_len := len(pattern)) == 0:
            return self._key_array
        assert (
            pattern_len == self._dim
        ), f"传入的pattern长度{pattern_len}与tupledict中的维度{self._dim}不匹配"
        ava_key_array = self._key_array
        return self._key_np_array_(ava_key_array, *pattern)

    def keyset(self, *pattern) -> List:
        return self._key_np_array(*pattern).tolist()

    def key_pattern_set(self, *pattern) -> List:
        key_set = self.keyset(*pattern)
        if len(pattern) == 1:
            return key_set
        row = len(key_set)
        for i, pattern_item in enumerate(pattern):
            if pattern_item == "-":
                for j in range(row):
                    key_set[j].insert(i, "*")
        return key_set

    def select(self, *pattern):
        keys = self._key_np_array(*pattern)
        if keys.ndim == 1:
            return [self[key.item()] for key in keys]
        return [self[tuple(key)] for key in keys]

    def sum(self, *pattern):  # type:ignore
        v = self.select(*pattern)
        if len(v) == 0:
            return 0
        return np.sum(v)

    def quickprod(self, coeff: Dict, *pattern):  # type:ignore
        return self.prod(coeff, *pattern)

    def quickselect(self, *pattern) -> List:
        """
        快速挑选符合模式的items
        """
        return self.select(*pattern)

    def quicksum(self, *pattern):  # type:ignore
        return self.sum(*pattern)
