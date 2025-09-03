# -*- coding: utf-8 -*-
# @Time    : 2025/08/21 17:50:59
# @Author  : luyi
# @Desc    : 最低费用流

from enum import Enum
from typing import List, Union, Tuple
import numpy as _np
from numpy.typing import NDArray
from ortools.graph.python import min_cost_flow as _or_min_cost_flow  # type: ignore


class MinCostStatus(Enum):
    NOT_SOLVED = 0
    OPTIMAL = 1
    FEASIBLE = 2
    INFEASIBLE = 3
    UNBOUNDED = 4
    BAD_RESULT = 5
    BAD_COST_RANGE = 6
    BAD_CAPACITY_RANGE = 7


class SimpleMinCostFlow:
    (
        NOT_SOLVED,
        OPTIMAL,
        FEASIBLE,
        INFEASIBLE,
        UNBOUNDED,
        BAD_RESULT,
        BAD_COST_RANGE,
        BAD_CAPACITY_RANGE,
    ) = MinCostStatus

    def __init__(self) -> None:
        self.__mincost_flow = _or_min_cost_flow.SimpleMinCostFlow()
        self._is_optimize = False

    def add_arc_with_capacity_and_unit_cost(
        self, tail: int, head: int, capacity: int, unit_cost: int
    ) -> int:
        """
        添加弧
        :param tail: 起点
        :param head: 终点
        :param capacity: 容量
        :param unit_cost: 单位费用
        :return: 弧的编号
        """
        return self.__mincost_flow.add_arc_with_capacity_and_unit_cost(
            tail, head, capacity, unit_cost
        )

    def add_arcs_with_capacity_and_unit_cost(
        self,
        tails: Union[List[int], NDArray[_np.int32]],
        heads: Union[List[int], NDArray[_np.int32]],
        capacities: Union[List[int], NDArray[_np.int32]],
        unit_costs: Union[List[int], NDArray[_np.int32]],
    ) -> NDArray[_np.int32]:
        """
        添加弧
        :param tails: 起点列表
        :param heads: 终点列表
        :param capacities: 容量列表
        :param unit_costs: 费用列表
        :return: 弧的编号列表
        """
        return self.__mincost_flow.add_arcs_with_capacity_and_unit_cost(
            tails, heads, capacities, unit_costs
        )

    def set_node_supply(self, node: int, supply: int) -> None:
        """
        设置节点供应量
        :param node: 节点编号
        :param supply: 供应量
        """
        self.__mincost_flow.set_node_supply(node, supply)

    def set_nodes_supplies(
        self,
        nodes: Union[List[int], NDArray[_np.int32]],
        supplies: Union[List[int], NDArray[_np.int32]],
    ) -> None:
        """
        设置节点供应量
        :param nodes: 节点编号列表
        :param supplies: 供应量列表
        """
        self.__mincost_flow.set_nodes_supplies(nodes, supplies)

    def num_nodes(self) -> int:
        """
        获取节点数量
        :return: 节点数量
        """
        return self.__mincost_flow.num_nodes()

    def num_arcs(self) -> int:
        """
        获取弧数量
        :return: 弧数量
        """
        return self.__mincost_flow.num_arcs()

    def tail(self, arc: int) -> int:
        """
        获取弧的起点
        :param arc: 弧编号
        :return: 起点编号
        """
        return self.__mincost_flow.tail(arc)

    def head(self, arc: int) -> int:
        """
        获取弧的终点
        :param arc: 弧编号
        :return: 终点编号
        """
        return self.__mincost_flow.head(arc)

    def capacity(self, arc: int) -> int:
        """
        获取弧的容量
        :param arc: 弧编号
        :return: 容量
        """
        return self.__mincost_flow.capacity(arc)

    def unit_cost(self, arc: int) -> int:
        """
        获取弧的单位费用
        :param arc: 弧编号
        :return: 单位费用
        """
        return self.__mincost_flow.unit_cost(arc)

    def supply(self, node: int) -> int:
        """
        获取节点的供应量
        :param node: 节点编号
        :return: 供应量
        """
        return self.__mincost_flow.supply(node)

    def optimize(self) -> MinCostStatus:
        """
        最低费用流优化
        :return: 最低费用流
        """
        self._is_optimize = True
        status = self.__mincost_flow.solve()
        return MinCostStatus(status.value)

    def optimal_cost(self) -> int:
        assert self._is_optimize, "请先求解"
        return self.__mincost_flow.optimal_cost()

    def maximun_flow(self) -> int:
        assert self._is_optimize, "请先求解"
        return self.__mincost_flow.maximum_flow()

    def flow(self, arc: int) -> int:
        assert self._is_optimize, "请先求解"
        return self.__mincost_flow.flow(arc)

    def flows(self, arcs: Union[List[int], NDArray[_np.int32]]) -> NDArray[_np.int32]:
        assert self._is_optimize, "请先求解"
        return self.__mincost_flow.flows(arcs)

    def solve_max_flow_with_min_cost(self):
        self._is_optimize = True
        status = self.__mincost_flow.SolveMaxFlowWithMinCost()
        return MinCostStatus(status.value())
