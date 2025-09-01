# -*- coding: utf-8 -*-
# @Time    : 2025/08/22 09:40:44
# @Author  : luyi
# @Desc    : 背包问题
from enum import Enum
from typing import List
from ortools.algorithms.python import knapsack_solver  # type: ignore


class SolverType(Enum):
    MultiBranchBound = 5
    """多维-分支定界:大项目"""
    SingleBruteForce = 0
    """暴力枚举法: < 30, <15 较佳"""
    Multi64Times = 1
    """< 64"""
    SingleDynamicProgramming = 2
    """动态规划法"""
    MultiCbcMip = 3
    """CBC"""
    MultiScipMip = 6
    """SCIP"""
    MultiSAT = 10
    """SAT"""
    SingleDivideAndConquer = 9
    """分治法"""


class KnapsackState(Enum):
    OPTIMAL = 1
    """最优解"""
    FEASIBLE = 2
    """可行解"""


class SimpleKnapsack:
    """
    简单背包问题,单个背包。
    输入: 物品价值列表, 物品重量列表(可以多维), 背包容量
    输出: 最大收益
    物品之间的关系无法考虑
    """

    def __init__(self, sover_id: SolverType, name: str = "") -> None:
        _solver_type = knapsack_solver.SolverType(sover_id.value)
        self.__solver = knapsack_solver.KnapsackSolver(_solver_type, name)
        self.__optimal_profit = None
        self._profits = []
        self._weights = []
        self._capacities = []

    def set_constrs(
        self, profits: List[int], weights: List[List[int]], capacities: List[int]
    ):
        self._profits = profits
        self._weights = weights
        self._capacities = capacities
        self.__solver.init(profits, weights, capacities)

    def set_time_limit(self, time_limit_seconds: int):
        self.__solver.set_time_limit(time_limit_seconds)

    def optimize(self) -> KnapsackState:
        self.__optimal_profit = self.__solver.solve()
        if self.__solver.is_solution_optimal():
            return KnapsackState.OPTIMAL
        else:
            return KnapsackState.FEASIBLE

    def optimal_profit(self):
        """返回最大收益"""
        assert self.__optimal_profit is not None, ""
        return self.__optimal_profit

    def get_chosed_item_ids(self) -> List[int]:
        """返回选择的物品id"""
        res = []
        for i in range(len(self._profits)):
            if self.__solver.best_solution_contains(i):
                res.append(i)
        return res

    def best_solution_contians(self, id: int) -> bool:
        """判断id是否在最优解中"""
        return self.__solver.best_solution_contains(id)
