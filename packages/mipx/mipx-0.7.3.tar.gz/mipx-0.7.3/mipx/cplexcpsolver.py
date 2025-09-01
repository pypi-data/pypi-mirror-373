# -*- coding: utf-8 -*-
# @Time    : 2023/4/12 9:12
# @Author  : luyi
"""
约束规划
"""

from typing import Any, Optional, Sequence, Union, List, Dict, Tuple
from typing_extensions import override

from docplex.cp.config import CpoParameters
from docplex.cp.model import CpoModel, Type_Int
from docplex.cp.expression import (
    CpoExpr,
    CpoFunctionCall,
    Type_Float,
)
from .variable_cplex import CPlexCpoVar
from .constants import Vtype, ObjType, OptimizationStatus, CmpType
from .interface_ import IVar, ICpModel
from .utilx import (
    INFINITY,
    is_bool_var,
)


Real = Union[float, int]


class CplexCpSolver(ICpModel):
    """
    约束规划CPLEX 未实现

    :param _type_ IModel: _description_
    """

    def __init__(self, name=""):
        super().__init__("CPLEX_CP")
        self._name = name
        self.__model = CpoModel(self._name)
        self._solver = None
        self.__line_expr_object = None

    def _get_execfile_path(self) -> str:
        import os

        cplex_studio_dir = os.getenv("CPLEX_STUDIO_CPOPTIMIZER_DIR")
        if cplex_studio_dir:
            from pathlib import Path

            cpoptimizer_path = Path(cplex_studio_dir)
            if cpoptimizer_path.exists():
                return str(cplex_studio_dir)
            else:
                raise RuntimeError(
                    f"环境变量[CPLEX_STUDIO_CPOPTIMIZER_DIR={cplex_studio_dir}]指定的目录不存在"
                )
        else:
            raise RuntimeError(
                "请设置环境变量[CPLEX_STUDIO_CPOPTIMIZER_DIR]或者设置model.Params.CpoptimizerPath"
            )

    @override
    def Sum(self, expr_array):
        return sum(expr_array)

    @override
    def setHint(self, start: List[Tuple[IVar, Real]]):
        pass

    @override
    def setTimeLimit(self, time_limit_seconds: int):
        self._params.TimeLimit = time_limit_seconds

    @override
    def wall_time(self) -> int:
        solver_details: SolveDetails = self.__model.solve_details  # type: ignore
        return solver_details.time

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
        vtype: Vtype = Vtype.INTEGER,
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
        if lb is None:
            lb = 0
        if vtype == Vtype.CONTINUOUS or vtype == Vtype.INTEGER:
            var1 = CPlexCpoVar(True, self, lb, ub, name)
        else:
            var1 = CPlexCpoVar(False, self, lb, ub, name)
        return var1

    @override
    def addVars(
        self,
        *indices,
        lb: Real = 0.0,
        ub: Real = INFINITY,
        vtype: Vtype = Vtype.INTEGER,
        name: str = "",
    ):

        return super().addVars(*indices, lb=lb, ub=ub, vtype=vtype, name=name)

    @override
    def getVars(self) -> List[IVar]:
        return self.__model.get_all_variables()  # type: ignore

    @override
    def getVar(self, i) -> IVar:
        raise RuntimeError("not implemented")

    @override
    def addConstr(self, lin_expr):
        self.__model.add_constraint(lin_expr)

    @override
    def addConstrs(self, lin_exprs):
        # 检查下是否可以迭代。
        self.__model.add(lin_exprs)

    @override
    def setObjective(self, expr):
        self.__line_expr_object = expr

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
        self,
        var_x: IVar,
        var_y: IVar,
        x_range: List,
        y_range: List,
        cmp_type,
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
        rhs: int,
        M,
    ):
        super().addGenConstrIndicator(binvar, binval, lhs, sense, rhs, M)

    @override
    def addIndicator(self, binvar: IVar, binval: bool, constr):
        raise RuntimeError("not implemented")

    @override
    def addGenConstrAbs(self, resvar, var_abs: IVar):  # type: ignore
        self.addConstr(self.__model.abs(var_abs) == resvar)  # type: ignore

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
        super().addRange(expr, min_value, max_value)

    @override
    def calc_lbub_and_expr(self, constr) -> Tuple[Real, Real, Any]: ...
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
            tempM = 100000000
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
        return len(self.__model.get_all_variables())

    @override
    def numConstraints(self) -> int:
        return len(self.__model.expr_list)

    @override
    def write(self, filename: str, obfuscated=False):
        raise NotImplementedError()

    @override
    def read(self, path: str):  # type: ignore
        raise NotImplementedError()

    @property
    @override
    def ObjVal(self) -> Real:
        res = self._solver.get_objective_values()  # type: ignore
        if res:
            return res[0]  # type: ignore
        return 0

    @override
    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        params = CpoParameters()
        if self._params.TimeLimit:
            params.TimeLimit = self._params.TimeLimit
        self.__model.set_parameters(params)
        if self.__line_expr_object is not None:
            if obj_type == ObjType.MINIMIZE:
                self.__model.minimize(self.__line_expr_object)
            else:
                self.__model.maximize(self.__line_expr_object)
        trace_log = True if self._params.EnableOutput else False
        if self._params.CpoptimizerPath is None:
            cplex_file = self._get_execfile_path()
            self._params.CpoptimizerPath = cplex_file
        sol = self.__model.solve(
            execfile=self._params.CpoptimizerPath, trace_log=trace_log
        )
        if sol:  # type: ignore
            self._solver = sol
            return OptimizationStatus.OPTIMAL
        else:
            return OptimizationStatus.ERROR

    @override
    def clear(self):
        self.__model = CpoModel(self._name)
        self._solver = None
        self.__line_expr_object = None

    @override
    def close(self):
        raise NotImplementedError()

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
    def valueExpression(self, expression: CpoExpr) -> Real:  # type: ignore
        assert self._solver is not None, "执行optimize后才能进行值评价"
        if expression.is_type(Type_Int) or expression.is_type(Type_Float):
            return expression.value  # type: ignore
        if expression.is_variable():
            try:
                return self._solver[expression]  # type:ignore
            except KeyError:
                print(f"warning:变量{expression}未使用")
            # 此时应该是这个变量没有使用,直接去最小值
            return expression.lb  # type:ignore
        # 此时是表达式
        assert isinstance(
            expression, CpoFunctionCall
        ), f"参数`expression`必须是CpoFunctionCall,传入的是:{expression}"
        assert (
            len(expression.children) == 2
        ), f"CpoFunctionCall下的`expression.children`的长度必须等于2"
        left = expression.children[0]
        right = expression.children[1]
        op = expression.operation
        left_value = self.valueExpression(left)
        right_value = self.valueExpression(right)
        value = 0
        if op.get_cpo_name() == "plus":
            value = left_value + right_value
        elif op.get_cpo_name() == "times":
            value = left_value * right_value
        elif op.get_cpo_name() == "minus":
            value = left_value - right_value
        else:
            raise ValueError(f"暂不支持的操作符{op.get_cpo_name()}")
        return value

    @override
    def setNumThreads(self, num_theads: int):
        raise RuntimeError("not implemented")

    @override
    def addCpElement(
        self,
        index: Union[IVar, int],
        variables: Sequence[Union[IVar, int]],
        target: Union[IVar, int],
    ): ...

    @override
    def addCpCircuit(self, arcs): ...

    @override
    def addCpAllowedAssignments(self, variables, tuples_list): ...

    @override
    def addCpForbiddenAssignments(self, variables, tuples_list): ...

    @override
    def addCpInverse(self, variables, inverse_variables): ...

    @override
    def addCpMapDomain(self, var, bool_var_array, offset): ...

    @override
    def addCpImplication(self, a, b): ...

    @override
    def addCpBoolTrueOr(self, literals): ...

    @override
    def addCpAtLeastOneIsTrue(self, literals): ...

    @override
    def addCpAtMostOneIsTrue(self, literals): ...

    @override
    def addCpExactlyNumIsTrue(self, literals, num: int = 1): ...

    @override
    def addCpBoolTrueAnd(self, literals): ...

    @override
    def addCpGenConstrMax(self, target: IVar, varList: List[IVar]):
        """
        最大值约束
        """
        ...

    @override
    def addCpGenConstrMin(self, target: IVar, varList: List[IVar]):
        """
        最小值约束
        """
        ...

    @override
    def addCpGenConstrDivision(self, target, num, denom):
        """Adds `target == num // denom` (integer division rounded towards 0)."""
        ...

    @override
    def addCpGenConstrModulo(self, target, num, denom):
        """Adds `target = expr % mod`."""
        ...

    @override
    def addCpGenConstrMultiplication(
        self,
        target,
        *expressions,
    ): ...
