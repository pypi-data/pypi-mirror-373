# -*- coding: utf-8 -*-
# @Time    : 2025/08/22 14:50:17
# @Author  : luyi
# @Desc    : 车辆路径相关的算法
from typing import List, Union
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class Vrp:
    def __init__(
        self,
        num_node: int,
        num_vehicles: int,
        start_nodes: Union[List[int], int],
        end_nodes: Union[List[int], int],
    ) -> None:
        if not isinstance(start_nodes, list):
            start_nodes = [start_nodes]
        if not isinstance(end_nodes, list):
            end_nodes = [end_nodes]
        manager = pywrapcp.RoutingIndexManager(
            num_node, num_vehicles, start_nodes, end_nodes
        )
        self._router = pywrapcp.RoutingModel(manager)
        a = pywrapcp.DefaultRoutingSearchParameters()

        pass

    @property
    def Params(self):
        pass

    def optimize(self):
        pass
