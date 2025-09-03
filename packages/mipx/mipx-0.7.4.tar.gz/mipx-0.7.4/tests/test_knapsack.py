# -*- coding: utf-8 -*-
# @Time    : 2025/08/22 14:12:29
# @Author  : luyi
# @Desc    : 测试背包问题
from mipx.knapsack import SimpleKnapsack, SolverType


def test_knapsack():
    sk = SimpleKnapsack(SolverType.MultiSAT)
    values = [
        # fmt:off
      360, 83, 59, 130, 431, 67, 230, 52, 93, 125, 670, 892, 600, 38, 48, 147,
      78, 256, 63, 17, 120, 164, 432, 35, 92, 110, 22, 42, 50, 323, 514, 28,
      87, 73, 78, 15, 26, 78, 210, 36, 85, 189, 274, 43, 33, 10, 19, 389, 276,
      312
        # fmt:on
    ]
    weights = [
        # fmt: off
      [7, 0, 30, 22, 80, 94, 11, 81, 70, 64, 59, 18, 0, 36, 3, 8, 15, 42, 9, 0,
       42, 47, 52, 32, 26, 48, 55, 6, 29, 84, 2, 4, 18, 56, 7, 29, 93, 44, 71,
       3, 86, 66, 31, 65, 0, 79, 20, 65, 52, 13],
        # fmt: on
    ]
    capacities = [850]
    sk.set_constrs(values, weights, capacities)
    status = sk.optimize()
    print(sk.optimal_profit())
    print(status)
    print(sk.get_chosed_item_ids())


if __name__ == "__main__":
    test_knapsack()
