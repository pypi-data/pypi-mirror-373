# -*- coding: utf-8 -*-
# @Time    : 2023/4/7 8:07
# @Author  : luyi
"""
变量
"""
from ortools.linear_solver.pywraplp import Variable
from ortools.sat.python.cp_model import IntVar, CpSolver
from ortools.util.python.sorted_interval_list import Domain
from .interface_ import *


class IntervalVar:
    def __init__(self, start, size, end) -> None:
        self.start = start
        self.size = size
        self.end = end


class Var(Variable, IVar):

    # def Not(self) -> "IVar":
    #     if self.v_type == Vtype.BINARY or self.v_type == Vtype.INTEGER:
    #         z = self._solver.IntVar(  # type: ignore
    #             lb=0, ub=1, name=f"{self.VarName}.Not"
    #         )  # type: ignore
    #         self._solver.Add(z + self == 1)  # type: ignore
    #         return z
    #     else:
    #         raise RuntimeError("Only for binary variable .")  # type: ignore

    # def setUb(self, ub):
    #     self.SetUb(ub)

    # def setLb(self, lb):
    #     self.SetLb(lb)

    # def setBounds(self, lb, ub):
    #     self.SetBounds(lb, ub)

    # def setValue(self, value):
    #     self.SetBounds(value, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.v_type = None

    @property
    def X(self):
        return self.solution_value()

    # @property
    # def VarIndex(self):
    #     return self.index()

    @property
    def VarName(self) -> str:
        return self.name()

    @property
    def LB(self):
        return self.lb()

    @property
    def UB(self):
        return self.ub()


Variable.X = Var.X  # type: ignore
Variable.VarName = Var.VarName  # type: ignore
# Variable.VarIndex = Var.VarIndex  # type: ignore
Variable.LB = Var.LB  # type: ignore
Variable.UB = Var.UB  # type: ignore
# Variable.setValue = Var.setValue  # type: ignore
# Variable.setLb = Var.setLb  # type: ignore
# Variable.setUb = Var.setUb  # type: ignore
# Variable.setBounds = Var.setBounds  # type: ignore
# Variable.Not = Var.Not  # type: ignore


class CpVar(IntVar, IVar):
    def __init__(self, model, domain, is_bool: bool, name, solver):
        self._solver: CpSolver = solver
        self.__domain: Domain = domain
        try:
            super().__init__(model, domain, is_bool, name)  # type: ignore
        except:
            super().__init__(model, domain, name)  # type: ignore

    # def Not(self):  # type: ignore
    #     y = super().Not()
    #     y.VarName = f"{self.VarName}.not"  # type: ignore
    #     y.X = lambda: self._solver.valueExpression(y)  # type: ignore
    #     return y

    # def setValue(self, value):
    #     raise Exception("not impl")

    # def setUb(self, ub):
    #     raise Exception("not impl")

    # def setLb(self, lb):
    #     raise Exception("not impl")

    # def setBounds(self, lb, ub):
    #     raise Exception("not impl")

    @property
    def X(self):
        return self._solver.valueExpression(self)  # type: ignore

    # @property
    # def VarIndex(self):
    #     return self.Index()

    @property
    def VarName(self):
        return self.Name()

    @property
    def LB(self):
        try:
            return self.__domain.Min()  # type: ignore
        except:
            return self.__domain.min()

    @property
    def UB(self):
        try:
            return self.__domain.Max()  # type: ignore
        except:
            return self.__domain.max()
