# -*- coding: utf-8 -*-
# @Time    : 2023/4/7 8:07
# @Author  : luyi
"""
变量
"""
from docplex.mp.dvar import Var as DVar
from docplex.cp.model import CpoIntVar
from docplex.cp.expression import _build_int_var_domain
from docplex.mp.kpi import DecisionKPI
from mipx.interface_ import IVar


class CPlexVar(DVar, IVar):

    # def Not(self) -> "IVar":
    #     return self.logical_not()

    # def setUb(self, ub):
    #     self.set_ub(ub)

    # def setLb(self, lb):
    #     self.set_lb(lb)

    # def setBounds(self, lb, ub):
    #     self.setLb(lb)
    #     self.setUb(ub)

    # def setValue(self, value):
    #     self.setBounds(value, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def X(self):
        return self.solution_value

    # @property
    # def VarIndex(self):
    #     return self.index

    @property
    def VarName(self) -> str:
        return self.get_name()  # type: ignore

    @property
    def LB(self):  # type: ignore
        return self.lb

    @property
    def UB(self):  # type: ignore
        return self.ub


DVar.X = CPlexVar.X  # type: ignore
DVar.VarName = CPlexVar.VarName  # type: ignore
# DVar.VarIndex = CPlexVar.VarIndex  # type: ignore
DVar.LB = CPlexVar.LB  # type: ignore
DVar.UB = CPlexVar.UB  # type: ignore
# DVar.setValue = CPlexVar.setValue  # type: ignore
# DVar.setLb = CPlexVar.setLb  # type: ignore
# DVar.setUb = CPlexVar.setUb  # type: ignore
# DVar.setBounds = CPlexVar.setBounds  # type: ignore
# DVar.Not = CPlexVar.Not  # type: ignore

DecisionKPI.X = CPlexVar.X  # type: ignore


class CPlexCpoVar(CpoIntVar, IVar):
    def __init__(
        self,
        is_integer_var: bool,
        solver,
        min=None,
        max=None,
        name=None,
        domain=None,
    ):
        if is_integer_var:
            super().__init__(_build_int_var_domain(min, max, domain), name)
        else:
            super().__init__((0, 1), name)
        self._solver = solver

    # def Not(self) -> "IVar":
    #     raise RuntimeError("NotImplemented")

    # def setUb(self, ub):
    #     raise RuntimeError("NotImplemented")

    # def setLb(self, lb):
    #     raise RuntimeError("NotImplemented")

    # def setBounds(self, lb, ub):
    #     raise RuntimeError("NotImplemented")

    # def setValue(self, value):
    #     raise RuntimeError("NotImplemented")

    @property
    def X(self):
        return self._solver.valueExpression(self)

    # @property
    # def VarIndex(self):
    #     raise RuntimeError("NotImplemented")

    @property
    def VarName(self) -> str:
        return self.get_name()

    @property
    def LB(self):
        return self.lb

    @property
    def UB(self):
        return self.ub
