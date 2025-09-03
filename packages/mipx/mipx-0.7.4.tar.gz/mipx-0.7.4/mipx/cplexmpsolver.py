# -*- coding: utf-8 -*-
# @Time    : 2023/4/12 9:12
# @Author  : luyi
"""
约束规划
"""

from collections import defaultdict
from typing import Any, Optional, Union, List, Tuple
from typing_extensions import override
from .constants import Vtype, ObjType, OptimizationStatus, CmpType
from .interface_ import IVar, IModel
from .utilx import (
    INFINITY,
    is_bool_var,
)

from .variable_cplex import CPlexVar
from docplex.mp.model import Model
from docplex.mp.sdetails import SolveDetails
from docplex.mp.solution import SolveSolution
from docplex.mp.model_reader import ModelReader

Real = Union[float, int]


class CplexMpSolver(IModel):

    def __init__(self, name=""):
        super().__init__("CPLEX", name)
        self.__model = Model(self.name)
        self.__line_expr_object = defaultdict(list)
        self.__expr_simple_object = None

    @override
    def Sum(self, expr_array) -> "IVar":  # type: ignore
        return self.__model.sum(expr_array)  # type: ignore

    @override
    def setHint(self, start: List[Tuple[IVar, Real]]):
        warmstart = self.__model.new_solution()
        for var, value in start:
            warmstart.add_var_value(var, value)
        self.__model.add_mip_start(warmstart)

    @override
    def setTimeLimit(self, time_limit_seconds: int):
        self.__model.set_time_limit(time_limit_seconds)

    @override
    def wall_time(self) -> int:
        solver_details: SolveDetails = self.__model.solve_details  # type: ignore
        return solver_details.time * 1000

    @override
    def iterations(self) -> Real:
        solver_details: SolveDetails = self.__model.solve_details  # type: ignore
        return solver_details.nb_iterations

    @override
    def nodes(self) -> Real:
        solver_details: SolveDetails = self.__model.solve_details  # type: ignore
        return solver_details.nb_nodes_processed

    @override
    def addVar(
        self,
        lb: Real = 0.0,
        ub: Real = INFINITY,
        vtype: Vtype = Vtype.CONTINUOUS,
        name: str = "",
    ) -> IVar:
        """
            Add a decision variable to a model.
        :param lb: Lower bound for new variable.
        :param ub: Upper bound for new variable.
        :param vtype: variable type for new variable(Vtype.CONTINUOUS, Vtype.BINARY, Vtype.INTEGER).
        :param name: Name for new variable.
        :return: variable.
        """

        if vtype == Vtype.CONTINUOUS:
            var1: CPlexVar = self.__model.continuous_var(
                lb=lb, ub=ub, name=name
            )  # type: ignore
        elif vtype == Vtype.INTEGER:
            var1 = self.__model.integer_var(lb=lb, ub=ub, name=name)  # type: ignore
        else:
            var1 = self.__model.binary_var(name=name)  # type: ignore
        var1._solver = self  # type: ignore
        return var1

    @override
    def addVars(
        self,
        *indices,
        lb: Real = 0.0,
        ub: Real = INFINITY,
        vtype: Vtype = Vtype.CONTINUOUS,
        name: str = "",
    ):
        return super().addVars(*indices, lb=lb, ub=ub, vtype=vtype, name=name)

    @override
    def getVars(self) -> List[IVar]:
        raise RuntimeError("not implemented")

    @override
    def getVar(self, i) -> IVar:
        return self.__model.get_var_by_index(i)  # type: ignore

    @override
    def addConstr(self, lin_expr):
        self.__model.add_constraint_(lin_expr)

    @override
    def addConstrs(self, lin_exprs):
        # 检查下是否可以迭代。
        self.__model.add_constraints_(lin_exprs)

    @override
    def setObjective(self, expr):
        self.__expr_simple_object = expr

    @override
    def setObjectiveN(
        self, expr, index: int, priority=None, weight: float = 1, name: str = ""
    ):
        """

        :param expr:
        :param index:
        :param priority:
        :param weight:
        :param name:
        :return:
        """
        self._flag_objective_n = True
        self.__line_expr_object["exprs"].append(expr)
        self.__line_expr_object["priority"].append(priority)
        self.__line_expr_object["weight"].append(weight)

    @override
    def addGenConstrAnd(self, resvar, varList: List[IVar]):
        """
        和 addGenConstrAnd(y, [x1,x2])
        :param resvar:
        :param varList:
        :return:
        """

        self.addConstr(resvar == self.__model.logical_and(*varList))

    @override
    def addGenConstrOr(self, resvar: IVar, varList: List[IVar]):
        self.addConstr(resvar == self.__model.logical_or(*varList))

    @override
    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar]):
        super().addGenConstrXOr(resvar, varList)

    @override
    def addGenConstrPWL(
        self,
        var_x: IVar,
        var_y: IVar,
        x_range: List,
        y_range: List,
        cmp_type: Union[List[CmpType], CmpType],
        M,
    ):

        super().addGenConstrPWL(var_x, var_y, x_range, y_range, M=M, cmp_type=cmp_type)

    @override
    def addGenConstrIndicator(
        self,
        binvar: IVar,
        binval: bool,
        lhs: IVar,
        sense: CmpType,
        rhs: float,
        M: float,
    ):
        """
        若 binvar 为binval ,则 lhs 与 rhs 之间有sense 的关系

        :param binvar: 0-1变量
        :param binval: bool 常量
        :param lhs:  左侧变量
        :param sense: 等号，大于等于，小于等于
        :param rhs: 右侧常量
        :param M: 大M
        :return:
        """
        super().addGenConstrIndicator(binvar, binval, lhs, sense, rhs, M)

    @override
    def addIndicator(self, binvar: IVar, binval: bool, constr):
        self.__model.add_indicator(binvar, constr, binval)

    @override
    def addGenConstrAbs(self, resvar, var_abs: IVar, M):
        self.addConstr(self.__model.abs(var_abs) == resvar)

    @override
    def addGenConstrMultiply(self, z: IVar, l: Tuple[IVar, IVar]):
        """x * y = z"""
        super().addGenConstrMultiply(z, l)
        x = l[0]
        y = l[1]
        if not is_bool_var(x) and not is_bool_var(y):
            raise RuntimeError("At least one binary variable is required.")
        if is_bool_var(y):
            x, y = y, x
        M = y.UB
        self.addConstr(z <= y)
        self.addConstr(z <= x * M)
        self.addConstr(z >= y + (x - 1) * M)

    @override
    def addRange(
        self, expr, min_value: Union[float, int], max_value: Union[float, int]
    ):
        self.__model.add_range(min_value, expr, max_value)

    @override
    def calc_lbub_and_expr(self, constr) -> Tuple[Real, Real, Any]:
        expr = constr.left_expr - constr.right_expr
        sign = constr.cplex_code  # 'L' (≤), 'G' (≥), 'E' (=)
        lb = -self.INFINITY
        ub = self.INFINITY
        if sign == "L":
            ub = 0
        elif sign == "G":
            lb = 0
        elif sign == "E":
            lb = 0
            ub = 0
        return lb, ub, expr

    @override
    def addConstrOr(
        self,
        constrs: List,
        ok_num: int = 1,
        cmp_type: CmpType = CmpType.EQUAL,
        M=None,
    ):
        """
        约束的满足情况

        :param constr: 所有的约束
        :param ok_num: 需要满足的个数，具体则根据cmpType
        :param cmpType: CmpType.LESS_EQUAL CmpType.EQUAL,CmpType.GREATER_EQUAL
        :return:
        """
        constr_num = len(constrs)
        x = []
        for i in range(constr_num):
            x.append(self.addVar(vtype=Vtype.BINARY))
            constr = constrs[i]
            lb, ub, expr = self.calc_lbub_and_expr(constr)
            tempM = self.INFINITY
            if M is not None:
                tempM = M
            if lb > -self.INFINITY:  # 若大于
                self.addConstr(expr + tempM * (1 - x[i]) >= lb)
            if ub < self.INFINITY:
                self.addConstr(expr - tempM * (1 - x[i]) <= ub)

        if cmp_type == CmpType.EQUAL:
            self.addConstr(self.Sum(x) == ok_num)
        elif cmp_type == CmpType.GREATER_EQUAL:
            self.addConstr(self.Sum(x) >= ok_num)
        elif cmp_type == CmpType.LESS_EQUAL:
            self.addConstr(self.Sum(x) <= ok_num)  # type: ignore
        else:
            raise Exception("error value of cmpType")

    @override
    def numVars(self, vtype: Optional[Vtype] = None) -> int:
        if vtype is None:
            return self.__model.number_of_variables
        elif vtype == Vtype.CONTINUOUS:
            return self.__model.number_of_continuous_variables
        elif vtype == Vtype.INTEGER:
            return self.__model.number_of_integer_variables
        else:
            return self.__model.number_of_binary_variables

    @override
    def numConstraints(self) -> int:
        return self.__model.number_of_constraints

    @override
    def write(self, filename: str, obfuscated=False):
        filename = filename.lower()
        if filename.endswith(".lp"):
            self.__model.export_as_lp(filename)
        elif filename.endswith(".mps"):
            self.__model.export_as_mps(filename)
        elif filename.endswith(".proto"):
            raise TypeError(".proto 导出异常，待修复")

    @override
    def read(self, path: str):
        self.clear()
        m = ModelReader.read_model(path)
        self.__line_expr_object = defaultdict(list)
        self.__expr_simple_object = None
        self.__model = m

    @property
    @override
    def ObjVal(self) -> Real:
        return sum(self.__model.multi_objective_values)

    @property
    def has_cplex_env(self):
        return self.__model.environment.has_cplex

    @override
    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        if self._params.TimeLimit:
            self.setTimeLimit(self._params.TimeLimit)
        if self._params.MIPGap:
            self.__model.parameters.mip.tolerances.mipgap = self._params.MIPGap  # type: ignore
        if self._params.Precision:
            self.__model.float_precision = self._params.Precision
        if self._flag_objective_n:
            self.__model.set_multi_objective(
                "min" if obj_type is ObjType.MINIMIZE else "max",
                self.__line_expr_object["exprs"],
                self.__line_expr_object["priority"],
                self.__line_expr_object["weight"],
            )
        else:
            self.__model.set_objective(
                "min" if obj_type is ObjType.MINIMIZE else "max",
                self.__expr_simple_object,
            )
        status: SolveSolution = self.__model.solve(
            log_output=self._params.EnableOutput
        )  # type: ignore

        if status:
            if status.is_feasible_solution or status.is_valid_solution:
                result = OptimizationStatus.OPTIMAL
            else:
                result = OptimizationStatus.FEASIBLE
        else:
            result = OptimizationStatus.ERROR
        return result

    @override
    def clear(self):
        self.__model.clear()

    @override
    def close(self):
        self.__model.end()

    # 独有。

    @override
    def addNoOverlap(self, interval_vars, M):
        """
        相邻不重复。

        :param interval_vars:
        :return:
        """
        raise RuntimeError("not implemented")

    @override
    def newIntervalVar(self, start, size, end):
        raise RuntimeError("not implemented")

    @override
    def valueExpression(self, expression):
        return expression.solution_value

    @override
    def setNumThreads(self, num_theads: int):
        self.__model.context.cplex_parameters.threads = num_theads
