# -*- coding: utf-8 -*-
# @Time    : 2023/4/12 9:12
# @Author  : luyi
"""
约束规划
"""

from typing import Optional, Union, List, Tuple
from typing_extensions import override

from ortools.sat.python import cp_model
from ortools.util.python.sorted_interval_list import Domain

from .constants import Vtype, ObjType, OptimizationStatus, CmpType
from .interface_ import IVar, ICpModel
from .utilx import (
    is_list_or_tuple,
    is_generator,
    is_bool_var,
    INFINITY,
)
from .variable import CpVar


Real = Union[float, int]


class CpModelSolver(ICpModel):

    def __init__(self, name=""):
        super().__init__("CP")
        self._name = name
        self.__model = cp_model.CpModel()
        self.__solver: cp_model.CpSolver = cp_model.CpSolver()
        self.__line_expr_object = None
        self.__all_vars = []
        self.__all_constr = []

    @override
    def Sum(self, expr_array):
        return cp_model.LinearExpr.Sum(expr_array)

    @override
    def setHint(self, start: List[Tuple[IVar, Real]]):
        for var, num in start:
            self.__model.AddHint(var, num)  # type: ignore

    @override
    def setTimeLimit(self, time_limit_seconds: int):
        self.__solver.parameters.max_time_in_seconds = int(time_limit_seconds)

    @override
    def wall_time(self) -> int:
        return int(self.__solver.WallTime()) * 1000

    @override
    def iterations(self) -> Real:
        return 0

    @override
    def nodes(self) -> Real:
        return self.__solver.NumBranches()

    @override
    def addVar(
        self,
        lb: int = 0,
        ub: int = INFINITY,
        vtype: Vtype = Vtype.BINARY,
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
        tempModel = self.__model._CpModel__model  # type: ignore
        var1: Optional[CpVar] = None
        if vtype == Vtype.CONTINUOUS or vtype == Vtype.INTEGER:
            var1 = CpVar(tempModel, Domain(lb, ub), False, name, self)
        elif vtype == Vtype.BINARY:
            var1 = CpVar(tempModel, Domain(lb, ub), True, name, self)
        self.__all_vars.append(var1)
        return var1

    @override
    def addVars(
        self,
        *indices,
        lb: int = 0,
        ub: int = INFINITY,
        vtype: Vtype = Vtype.INTEGER,
        name: str = "",
    ):
        return super().addVars(*indices, lb=lb, ub=ub, vtype=vtype, name=name)

    @override
    def getVars(self) -> List[IVar]:
        return self.__all_vars

    @override
    def getVar(self, i) -> IVar:
        return self.__all_vars[i]

    @override
    def addConstr(self, lin_expr):
        self.__all_constr.append(lin_expr)
        self.__model.Add(lin_expr)

    @override
    def addConstrs(self, lin_exprs):
        # 检查下是否可以迭代。
        if not is_list_or_tuple(lin_exprs) and not is_generator(lin_exprs):
            raise RuntimeError("constraint conditions are not a set or list")
        for i, lin_expr in enumerate(lin_exprs):
            self.addConstr(lin_expr)

    @override
    def setObjective(self, expr):
        self.__model.Minimize(expr)
        self.__line_expr_object = expr

    @override
    def setObjectiveN(
        self, expr, index: int, priority: int = 0, weight: float = 1, name: str = ""
    ):
        """

        :param expr:
        :param index:
        :param priority:
        :param weight:
        :param name:
        :return:
        """
        if self.__line_expr_object is None:
            self.__line_expr_object = expr * weight
            return
        self.__line_expr_object = self.__line_expr_object + expr * weight

    @override
    def addGenConstrAnd(self, resvar, varList: List[IVar]):
        """
        和 addGenConstrAnd(y, [x1,x2])
        :param resvar:
        :param varList:
        :return:
        """
        super().addGenConstrAnd(resvar, varList)

    @override
    def addGenConstrOr(self, resvar: IVar, varList: List[IVar]):
        super().addGenConstrOr(resvar, varList)

    @override
    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar]):
        super().addGenConstrXOr(resvar, varList)

    @override
    def addGenConstrPWL(
        self, var_x: IVar, var_y: IVar, x_range: List[float], y_range: List, cmp_type, M
    ):
        super().addGenConstrPWL(var_x, var_y, x_range, y_range, cmp_type=cmp_type, M=M)

    def calc_ava_m(self, expr):
        constr = expr == 0
        m = 0
        for i, var in enumerate(constr.vars):
            m += max(abs(var.LB), abs(var.UB)) * abs(constr.coeffs[i])
        m += abs(constr.offset)
        m += 1
        if m > self.INFINITY:
            m = self.INFINITY
        return m

    @override
    def addGenConstrIndicator(
        self,
        binvar: IVar,
        binval: bool,
        lhs: IVar,
        sense: CmpType,
        rhs: int,
        M,
    ):
        if M == self.INFINITY:
            M = self.calc_ava_m(lhs - rhs)
        super().addGenConstrIndicator(binvar, binval, lhs, sense, rhs, M)

    @override
    def addIndicator(self, binvar: IVar, binval: bool, constr):
        raise RuntimeError("not implemented")

    @override
    def addGenConstrAbs(self, resvar, var_abs: IVar, M=None):
        self.__model.AddAbsEquality(resvar, var_abs)  # type: ignore

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
        self.__model.AddLinearConstraint(expr, min_value, max_value)  # type: ignore

    @override
    def calc_lbub_and_expr(self, constr):
        try:
            expr = constr.Expression()  # type: ignore
            lb, ub = constr.Bounds()  # type: ignore
            return lb, ub, expr
        except:
            pass
        try:
            lb, ub = constr.bounds()
            expr = constr.expression()
            return lb, ub, expr
        except:
            pass
        try:
            bounds: Domain = constr.bounds
            expr = self.sum([constr.coeffs[i] * constr.vars[i] for i in constr.coeffs])
            return bounds.min(), bounds.max(), expr
        except:
            pass

        raise RuntimeError("mipx异常")

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
        tempM = 100000000
        if M is not None:
            tempM = M
        x = []
        for i in range(constr_num):
            x.append(self.addVar(vtype=Vtype.BINARY))
            constr = constrs[i]
            lb, ub, expr = self.calc_lbub_and_expr(constr)
            if lb > -INFINITY:  # 若大于
                self.addConstr(expr + tempM * (1 - x[i]) >= lb)
            if ub < INFINITY:
                self.addConstr(expr - tempM * (1 - x[i]) <= ub)
        if cmp_type == CmpType.EQUAL:
            self.addConstr(self.Sum(x) == ok_num)
        elif cmp_type == CmpType.GREATER_EQUAL:
            self.addConstr(self.Sum(x) >= ok_num)
        elif cmp_type == CmpType.LESS_EQUAL:
            self.addConstr(self.Sum(x) <= ok_num)
        else:
            raise Exception("error value of cmpType")

    @override
    def numVars(self, vtype: Optional[Vtype] = None) -> int:
        if vtype is Vtype.CONTINUOUS:
            return 0
        return len(self.__all_vars)

    @override
    def numConstraints(self) -> int:
        return len(self.__all_constr)

    @override
    def write(self, filename: str, obfuscated=False):
        self.__model.ExportToFile(filename)

    @override
    def read(self, path: str):
        raise RuntimeError("not implemented")

    @property
    @override
    def ObjVal(self) -> Real:
        return self.__solver.ObjectiveValue()

    @override
    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        solver = self.__solver
        self._set_objective(obj_type)
        self._set_params()
        status = solver.Solve(self.__model)
        if status == cp_model.OPTIMAL:
            result = OptimizationStatus.OPTIMAL
        elif status == cp_model.INFEASIBLE:
            result = OptimizationStatus.INFEASIBLE
        elif status == cp_model.UNKNOWN:
            result = OptimizationStatus.UNBOUNDED
        elif status == cp_model.FEASIBLE:
            result = OptimizationStatus.FEASIBLE
        else:
            result = OptimizationStatus.ERROR
        return result

    @override
    def clear(self):
        self.__line_expr_object = None
        self.__all_vars.clear()
        self.__all_constr.clear()
        self._flag_objective = False
        self._flag_objective_n = False
        self.__model.ClearObjective()
        self.__model.ClearHints()
        self.__model.ClearAssumptions()

    @override
    def close(self):
        self.clear()
        self.__solver = None  # type: ignore

    def _set_objective(self, obj_type: ObjType):
        if self.__line_expr_object is not None:
            if obj_type == ObjType.MINIMIZE:
                self.__model.Minimize(self.__line_expr_object)
            else:
                self.__model.Maximize(self.__line_expr_object)

    def _set_params(self):
        if self._params.TimeLimit:
            self.setTimeLimit(self._params.TimeLimit)
        if self._params.EnableOutput:
            self.__solver.parameters.log_search_progress = True
        if self._params.MIPGap:
            self.__solver.parameters.absolute_gap_limit = self._params.MIPGap

    @override
    def addNoOverlap(self, interval_vars, M):
        """
        相邻不重复。

        :param interval_vars:
        :return:
        """
        self.__model.AddNoOverlap(interval_vars)

    @override
    def newIntervalVar(self, start, size, end):
        if type(start) == type(0.1):
            start = int(start)
        if type(end) == type(0.1):
            end = int(end)
        if type(size) == type(0.1):
            size = int(size)
        return self.__model.NewIntervalVar(start, size, end, "")

    @override
    def valueExpression(self, expression):
        return self.__solver.Value(expression)

    @override
    def setNumThreads(self, num_theads: int):
        self.__solver.parameters.num_workers = num_theads

    # 独有。其他方法待添加

    @override
    def addCpGenConstrMin(self, target: IVar, varList: List[IVar]):
        self.__model.add_min_equality(target, varList)  # type: ignore

    @override
    def addCpGenConstrMax(self, target: IVar, varList: List[IVar]):
        """
        最小值约束
        """
        self.__model.add_max_equality(target, varList)  # type: ignore

    @override
    def addCpGenConstrDivision(self, target, num, denom):
        """Adds `target == num // denom` (integer division rounded towards 0)."""
        self.__model.add_division_equality(target, num, denom)

    @override
    def addCpGenConstrModulo(self, target, num, denom):
        """Adds `target = expr % mod`."""
        self.__model.add_modulo_equality(target, num, denom)

    @override
    def addCpGenConstrMultiplication(
        self,
        target,
        *expressions,
    ):
        """Adds `target == expressions[0] * .. * expressions[n]`."""
        self.__model.add_multiplication_equality(target, *expressions)

    @override
    def addCpElement(self, index, variables, target):
        self.__model.add_element(index, variables, target)

    @override
    def addCpCircuit(self, arcs):
        self.__model.add_circuit(arcs)

    @override
    def addCpAllowedAssignments(self, variables, tuples_list):
        self.__model.add_allowed_assignments(variables, tuples_list)

    @override
    def addCpForbiddenAssignments(self, variables, tuples_list):
        self.__model.add_forbidden_assignments(variables, tuples_list)

    @override
    def addCpInverse(self, variables, inverse_variables):
        self.__model.add_inverse(variables, inverse_variables)

    @override
    def addCpMapDomain(self, var, bool_var_array, offset):
        self.__model.add_map_domain(var, bool_var_array, offset)

    @override
    def addCpImplication(self, a, b):
        self.__model.add_implication(a, b)

    @override
    def addCpBoolTrueOr(self, literals):
        self.__model.add_bool_or(literals)

    @override
    def addCpAtLeastOneIsTrue(self, literals):
        self.__model.add_at_least_one(literals)

    @override
    def addCpAtMostOneIsTrue(self, literals):
        self.__model.add_at_most_one(literals)

    @override
    def addCpExactlyNumIsTrue(self, literals, num: int = 1):
        if num == 1:
            self.__model.AddExactlyOne(literals)
        else:
            self.addConstr(self.Sum(literals) == num)

    @override
    def addCpBoolTrueAnd(self, literals):
        self.__model.add_bool_and(literals)
