# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 22:04
# @Author  : luyi
from typing import Any, List, Optional, Union, Tuple, Dict
from typing_extensions import override
from ortools.linear_solver import pywraplp
from ortools.linear_solver.python.linear_solver_natural_api import Constant

try:
    from ortools.linear_solver.linear_solver_natural_api import OFFSET_KEY  # type: ignore
except Exception as e:
    from ortools.linear_solver.python.linear_solver_natural_api import OFFSET_KEY
from .constants import Vtype, ObjType, OptimizationStatus, CmpType
from .interface_ import IModel, IVar
from .utilx import (
    is_list_or_tuple,
    is_generator,
    is_bool_var,
    INFINITY,
)
from .variable import IntervalVar


Real = Union[float, int]


class LinearConstraint(pywraplp.LinearConstraint):
    """
    线性约束

    Args:
        pywraplp (_type_): 线性
    """

    def __init__(self, expr, lb, ub):
        self.__expr = expr
        self.__lb = lb
        self.__ub = ub
        super().__init__(expr, lb, ub)

    def lbAndUb(self) -> Tuple[float, float]:
        coeffs = self.__expr.GetCoeffs()
        constant = coeffs.pop(OFFSET_KEY, 0.0)
        lb = -INFINITY
        ub = INFINITY
        if self.__lb > -INFINITY:
            lb = self.__lb - constant
        if self.__ub < INFINITY:
            ub = self.__ub - constant
        return lb, ub

    def linear_expr(self) -> pywraplp.LinearExpr:
        return self.__expr


class CommonModelSolver(IModel):
    """
    模型
    """

    def __init__(self, solver_id="SCIP", name=""):
        super().__init__(solver_id, name)
        self._name = name
        self.__solver: pywraplp.Solver = pywraplp.Solver.CreateSolver(solver_id)
        self._objective_n_list = []
        self._flag_objective = False
        self._num_inter_vars = 0
        self._num_binary_vars = 0
        self._num_coutinuous_vars = 0

    @override
    def Sum(self, expr_array) -> float:
        result = pywraplp.SumArray(expr_array)
        return result  # type: ignore

    @override
    def setHint(self, start: List[Tuple[IVar, Real]]):
        _vars = []
        _values = []
        for var, value in start:
            _vars.append(var)
            _values.append(value)
        self.__solver.SetHint(_vars, _values)

    @override
    def setTimeLimit(self, time_limit_seconds):
        self.__solver.set_time_limit(time_limit_seconds * 1000)

    @override
    def wall_time(self) -> int:
        """
        求解所花费的时间 milliseconds
        :return:
        """
        return self.__solver.wall_time()

    @override
    def iterations(self) -> int:
        """迭代次数"""
        return self.__solver.iterations()

    @override
    def nodes(self) -> int:
        return self.__solver.nodes()

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
        :param name: Name for new variable.write
        :return: variable.
        """
        var: Optional[IVar] = None
        if vtype == Vtype.CONTINUOUS:
            self._num_coutinuous_vars += 1
            var = self.__solver.NumVar(lb, ub, name)
        elif vtype == Vtype.INTEGER:
            self._num_inter_vars += 1
            var = self.__solver.IntVar(lb, ub, name)
        elif vtype == Vtype.BINARY:
            self._num_binary_vars += 1
            var = self.__solver.IntVar(lb, ub, name)
        var.v_type = vtype  # type: ignore
        var._solver = self  # type: ignore
        return var  # type: ignore

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
        """
        Retrieve a list of all variables in the model.
        :return: All variables in the model.
        """
        return self.__solver.variables()

    @override
    def getVar(self, i) -> IVar:
        """
        获得第i个变量
        :param i:
        :return:
        """
        return self.__solver.variable(i)

    @override
    def addConstr(self, lin_expr):
        self.__solver.Add(lin_expr)

    @override
    def addConstrs(self, lin_exprs, name=""):
        if not is_list_or_tuple(lin_exprs) and not is_generator(lin_exprs):
            raise RuntimeError("constraint conditions are not a set or list")
        for i, lin_expr in enumerate(lin_exprs):
            self.addConstr(lin_expr)

    @override
    def setObjective(self, expr):
        """
        Set the model objective equal to a linear expression
        :param expr:New objective expression
        :param obj_type:Optimization sense (Sense.MINIMIZE for minimization, Sense.MAXIMIZE for maximization)
        """
        self._objective_n_list.append(expr)

    def _set_objective_sense(self, obj_type: ObjType):
        if obj_type == ObjType.MINIMIZE:
            self.__solver.Objective().SetMinimization()
        else:
            self.__solver.Objective().SetMaximization()

    @override
    def setObjectiveN(
        self, expr, index: int, priority: int = 0, weight: float = 1, name: str = ""
    ):
        """
        多目标优化，优化最小值
        :param name:
        :param expr: 表达式
        :param index: 目标函数对应的序号 (默认 0，1，2，…), 以 index=0 作为目标函数的值, 其余值需要另外设置参数
        :param priority:分层序列法多目标决策优先级(整数值), 值越大优先级越高,# 未实现。
        :param weight: 线性加权多目标决策权重(在优先级相同时发挥作用)
        """
        self._objective_n_list.append(expr * weight)

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
        """
        或
        :param resvar:
        :param varList:
        :return:
        """
        super().addGenConstrOr(resvar, varList)

    @override
    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar]):
        """
        异或
        :param resvar:
        :param varList:
        :return:
        """
        super().addGenConstrXOr(resvar, varList)

    @override
    def addGenConstrPWL(
        self,
        var_x,
        var_y,
        x_range,
        y_range,
        cmp_type,
        M=None,
    ):
        """
        设置分段约束
        :param var_y: f(x)
        :param var_x:指定变量的目标函数是分段线性
        :param x:  定义分段线性变量的点的范围边界(非减序列)
        :param y:定义分段线性变量的范围所对应的目标函数的值
        :return:
        """
        super().addGenConstrPWL(var_x, var_y, x_range, y_range, M=M, cmp_type=cmp_type)

    def calc_ava_m(self, expr):
        m = 0
        for var, value in expr.GetCoeffs().items():
            if var is OFFSET_KEY:
                m += abs(value)
            else:
                m += max(abs(var.LB), abs(var.UB)) * abs(value)
        m = m + 1
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
        if M == self.INFINITY:
            M = self.calc_ava_m(lhs - rhs)
        super().addGenConstrIndicator(binvar, binval, lhs, sense, rhs, M)

    @override
    def addIndicator(self, binvar: IVar, binval: bool, constr):
        raise RuntimeError("not implemented")

    @override
    def addGenConstrAbs(self, resvar, var_abs: IVar, M=None):  # type: ignore
        x = self.addVars(2, name="")
        _M = 10000000
        if M is not None:
            _M = M
        self.addConstr(var_abs == x[0] - x[1])
        self.addConstr(resvar == x[0] + x[1])
        y = self.addVar(vtype=Vtype.BINARY)
        # x[0] * x[1]==0 的约束
        self.addConstr(x[0] <= y * _M)
        self.addConstr(x[1] <= (1 - y) * _M)

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
        M = self.calc_ava_m(x + y)
        # M = y.UB
        self.addConstr(z <= y)
        self.addConstr(z <= x * M)
        self.addConstr(z >= y + (x - 1) * M)

    @override
    def addRange(
        self, expr, min_value: Union[float, int], max_value: Union[float, int]
    ):
        """
        添加范围约束
        :param
        expr:
        :param
        min_value:
        :param
        max_value:
        :param
        :return:
        """
        super().addRange(expr, min_value, max_value)

    @override
    def calc_lbub_and_expr(self, constr) -> Tuple[Real, Real, Any]:
        tempConstr = _change_to_linear_constraint(constr)
        lb, ub = tempConstr.lbAndUb()
        expr = tempConstr.linear_expr()
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
            tempM = 0
            if M is not None:
                tempM = M
            lb, ub, expr = self.calc_lbub_and_expr(constrs[i])
            if lb > -INFINITY:  # 若大于
                if M is None:
                    tempM = (abs(lb) + 1) * 10
                self.addConstr(expr + tempM * (1 - x[i]) >= lb)
            if ub < INFINITY:
                if M is None:
                    tempM = (abs(ub) + 1) * 10
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
        """
        当前的变量的个数
        :return:
        """
        if vtype is Vtype.CONTINUOUS:
            return self._num_coutinuous_vars
        elif vtype is Vtype.INTEGER:
            return self._num_inter_vars
        elif vtype is Vtype.BINARY:
            return self._num_binary_vars
        else:
            return self.__solver.NumVariables()

    @override
    def numConstraints(self) -> int:
        """
        当前的约束的个数
        :return:
        """
        return self.__solver.NumConstraints()

    @override
    def write(self, filename: str, obfuscated=False):
        """
        写入到文件
        :param filename:文件名，支持后缀 .lp .mps .proto
        :param obfuscated:
        :return:
        """
        filename = filename.lower()
        content = ""
        if filename.endswith(".lp"):
            content = self.__solver.ExportModelAsLpFormat(False)
        elif filename.endswith(".mps"):
            content = self.__solver.ExportModelAsMpsFormat(True, obfuscated)
        elif filename.endswith(".proto"):
            raise TypeError(".proto 导出异常，待修复")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    @override
    def read(self, path: str):
        raise RuntimeError("not implemented")

    @property
    @override
    def ObjVal(self):
        return self.__solver.Objective().Value()

    def _set_params(self):
        if self._params.TimeLimit:
            self.setTimeLimit(self._params.TimeLimit)
            # 是否允许输出运算信息，包括gap等
        if self._params.EnableOutput:
            self.__solver.EnableOutput()

    @override
    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        self._set_params()
        # GAP 设置。
        params = pywraplp.MPSolverParameters()
        # 配置参数
        if self._params.MIPGap:
            params.SetDoubleParam(params.RELATIVE_MIP_GAP, self._params.MIPGap)
        if self._params.Precision:
            params.SetDoubleParam(params.PRIMAL_TOLERANCE, self._params.Precision)
        if obj_type == ObjType.MINIMIZE:
            self.__solver.Minimize(self.Sum(self._objective_n_list))
        else:
            self.__solver.Maximize(self.Sum(self._objective_n_list))
        status = self.__solver.Solve(params)

        if status == pywraplp.Solver.OPTIMAL:
            result = OptimizationStatus.OPTIMAL
        elif status == pywraplp.Solver.INFEASIBLE:
            result = OptimizationStatus.INFEASIBLE
        elif status == pywraplp.Solver.UNBOUNDED:
            result = OptimizationStatus.UNBOUNDED
        elif status == pywraplp.Solver.FEASIBLE:
            result = OptimizationStatus.FEASIBLE
        elif status == pywraplp.Solver.NOT_SOLVED:
            result = OptimizationStatus.NO_SOLUTION_FOUND
        else:
            result = OptimizationStatus.ERROR
        return result

    @override
    def clear(self):
        self.__solver.Clear()
        self._objective_n_list = []
        self._flag_objective = False
        self._num_inter_vars = 0
        self._num_binary_vars = 0
        self._num_coutinuous_vars = 0

    @override
    def close(self):
        self.clear()
        self.__solver = None  # type: ignore

    @override
    def valueExpression(self, expression):
        return expression.solution_value()
        # value = 0
        # coeffs = expression.GetCoeffs()
        # for key, coeff in coeffs.items():
        #     if key is OFFSET_KEY:
        #         value += coeffs.get(key)
        #     else:
        #         var: IVar = key
        #         x = var.X
        #         value += coeff * x
        # return value

    @override
    def newIntervalVar(self, start, size, end) -> IntervalVar:
        self.addConstr(start + size == end)
        return IntervalVar(start, size, end)

    @override
    def addNoOverlap(self, interval_vars: List[IntervalVar], M: int):
        # m = INFINITY if M is None else M
        if M is None:
            m = 0
            for var in interval_vars:
                m = max(m, self.calc_ava_m(var.start))
                m = max(m, self.calc_ava_m(var.end))
            m *= 2
            M = m
        for i, var_i in enumerate(interval_vars):
            for j, var_j in enumerate(interval_vars):
                if i == j:
                    continue
                t = self.addVar(vtype=Vtype.BINARY)
                self.addConstr(var_i.start >= var_j.end - (1 - t) * m)
                self.addConstr(var_j.start >= var_i.end - t * m)

    @override
    def setNumThreads(self, num_theads: int):
        self.__solver.SetNumThreads(num_theads)


def _change_to_linear_constraint(
    constraint: pywraplp.LinearConstraint,
) -> LinearConstraint:
    expr = constraint._LinearConstraint__expr  # type: ignore
    ub = constraint._LinearConstraint__ub  # type: ignore
    lb = constraint._LinearConstraint__lb  # type: ignore
    return LinearConstraint(expr, lb, ub)
