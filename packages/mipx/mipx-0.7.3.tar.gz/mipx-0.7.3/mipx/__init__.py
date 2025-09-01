# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 22:18
# @Author  : luyi
from .constants import *
from .model import Model
from .cpmodel import CpModel
from .tupledict import tupledict
from .func import debugVar, success, name_str
from .variable import Var, IntervalVar
from ._version import __version__
from .types import TupleDict
from . import maxflow, mincost, knapsack


succ = success
nameStr = name_str
BINARY = Vtype.BINARY
CONTINUOUS = Vtype.CONTINUOUS
INTEGER = Vtype.INTEGER
MINIMIZE, MAXIMIZE = ObjType
LESS_EQUAL, EQUAL, GREATER_EQUAL = CmpType
# 最优解和可行解
OPTIMAL, FEASIBLE = OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE
name = "mipx"
