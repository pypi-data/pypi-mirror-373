# -*- coding: utf-8 -*-
# @Time    : 2025/08/21 16:00:09
# @Author  : yi
# @Desc    : 最大流

from enum import Enum
from typing import List, Union, Tuple
import numpy as _np
from numpy.typing import NDArray
from ortools.graph.python import max_flow as _or_max_flow  # type: ignore


class MaxFlowStatus(Enum):
    OPTIMAL = 0
    POSSIBLE_OVERFLOW = 1
    BAD_INPUT = 2
    BAD_RESULT = 3


class SimpleMaxFlow:
    """最大流"""

    OPTIMAL, POSSIBLE_OVERFLOW, BAD_INPUT, BAD_RESULT = MaxFlowStatus

    def __init__(self) -> None:
        self.__max_flow = _or_max_flow.SimpleMaxFlow()
        self._is_optimize = False

    def add_arcs_with_capacity(
        self,
        tails: Union[List[int], NDArray[_np.int32]],
        heads: Union[List[int], NDArray[_np.int32]],
        capacities: Union[List[int], NDArray[_np.int32]],
    ) -> NDArray[_np.int32]:
        """
        添加有容量的弧
        :param tails: 起始节点列表
        :param heads: 终止节点列表
        :param capacities: 容量列表
        :return: 弧索引列表
        """
        return self.__max_flow.add_arcs_with_capacity(tails, heads, capacities)

    def add_arc_with_capacity(self, tail: int, head: int, capacity: int) -> int:
        """
        添加单条有容量的弧
        :param tail: 起始节点
        :param head: 终止节点
        :param capacity: 容量
        :return: 弧索引
        """
        return self.__max_flow.add_arc_with_capacity(tail, head, capacity)

    def optimize(self, source: int, sink: int) -> MaxFlowStatus:
        """
        求解最大流
        :param source: 源节点索引
        :param sink: 汇节点索引
        :return: 求解状态常量
        """
        status = self.__max_flow.solve(source, sink)
        self._is_optimize = True
        return MaxFlowStatus(status.value)

    def num_nodes(self):
        """
        获取节点数量
        :return: 节点数量
        """
        return self.__max_flow.num_nodes()

    def num_arcs(self):
        """
        获取弧数量
        :return: 弧数量
        """
        return self.__max_flow.num_arcs()

    def tail(self, arc: int) -> int:
        """
        获取起始节点
        :return: 起始节点
        """
        return self.__max_flow.tail(arc)

    def head(self, arc: int) -> int:
        """
        获取终止节点
        :return: 终止节点
        """
        return self.__max_flow.head(arc)

    def capacity(self, arc: int) -> int:
        """
        获取容量
        :return: 容量
        """
        return self.__max_flow.capacity(arc)

    def flow(self, arc: int) -> int:
        """
        求解成功后才可以使用
        获取流
        :return: 流
        """
        assert self._is_optimize, "请先求解最大流"
        return self.__max_flow.flow(arc)

    def flows(self, arcs: Union[List[int], NDArray[_np.int32]]) -> NDArray[_np.int32]:
        """
        求解成功后才可以使用
        获取流列表
        :return: 流列表
        """
        assert self._is_optimize, "请先求解最大流"
        return self.__max_flow.flows(arcs)

    def get_source_side_min_cut(self) -> NDArray[_np.int32]:
        """
        求解成功后才可以使用
        获取源侧最小割集
        :return: 源侧最小割集
        """
        assert self._is_optimize, "请先求解最大流"
        return self.__max_flow.get_source_side_min_cut()

    def get_sink_side_min_cut(self) -> NDArray[_np.int32]:
        """
        求解成功后才可以使用
        获取汇侧最小割集
        :return: 汇侧最小割集
        """
        assert self._is_optimize, "请先求解最大流"
        return self.__max_flow.get_sink_side_min_cut()

    def optimal_flow(self) -> int:
        """
        获取最大流
        :return: 最大流
        """
        assert self._is_optimize, "请先求解最大流"
        return self.__max_flow.optimal_flow()

    def get_solution(self) -> List[Tuple[int, int, int]]:
        li = []
        for i in range(self.num_arcs()):
            tail = self.tail(i)
            head = self.head(i)
            flow = self.flow(i)
            if flow > 0:
                li.append((tail, head, flow))
        return li
