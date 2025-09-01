import warnings
import gurobipy as gp
from typing import Any, Generator, List, Optional, Tuple, Union

from mipx.constants import CmpType, ObjType, OptimizationStatus, Vtype
from mipx.interface_ import IModel, ITupledict, IVar
from typing_extensions import override

from mipx.tupledict import tupledict
from mipx.utilx import INFINITY, is_bool_var


Real = Union[float, int]

gp.tupledict.quicksum = gp.tupledict.sum  # type: ignore
gp.tupledict.quickprod = gp.tupledict.prod  # type: ignore
gp.tupledict.quickselect = gp.tupledict.select  # type: ignore
gp.tupledict.keyset = tupledict._key_set_for_gurobi  # type: ignore
gp.tupledict.key_pattern_set = tupledict.key_pattern_set  # type: ignore


class GurobiSolver(IModel):
    def __init__(self, name=""):
        super().__init__("CPLEX", name)
        self.__model = gp.Model(name)

    @override
    def Sum(self, expr_array):
        return gp.quicksum(expr_array)

    @override
    def setHint(self, start: List[Tuple[IVar, Real]]):
        pass

    @override
    def setTimeLimit(self, time_limit_seconds: int):
        self.__model.Params.TimeLimit = time_limit_seconds

    @override
    def wall_time(self) -> float:
        return self.__model.Runtime * 1000

    @override
    def iterations(self) -> Real:
        raise NotImplementedError()

    @override
    def nodes(self) -> Real:
        raise NotImplementedError()

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
        gvtype = gp.GRB.CONTINUOUS
        if vtype == Vtype.BINARY:
            gvtype = gp.GRB.BINARY
        elif vtype == Vtype.INTEGER:
            gvtype = gp.GRB.INTEGER
        var = self.__model.addVar(lb=lb, ub=ub, vtype=gvtype, name=name)
        return var  # type: ignore

    @override
    def addVars(
        self,
        *indices,
        lb: Real = 0.0,
        ub: Real = INFINITY,
        vtype: Vtype = Vtype.CONTINUOUS,
        name: str = "",
    ) -> ITupledict:
        gvtype = gp.GRB.CONTINUOUS
        if vtype == Vtype.BINARY:
            gvtype = gp.GRB.BINARY
        elif vtype == Vtype.INTEGER:
            gvtype = gp.GRB.INTEGER
        tu_dict = self.__model.addVars(*indices, lb=lb, ub=ub, name=name, vtype=gvtype)
        return tu_dict  # type: ignore

    @override
    def getVars(self) -> List[IVar]:
        return self.__model.getVars()  # type: ignore

    @override
    def getVar(self, i) -> IVar:  # type: ignore
        self.__model.getVarByName(i)

    @override
    def addConstr(self, lin_expr):
        self.__model.addConstr(lin_expr)

    @override
    def addConstrs(self, lin_exprs: Union[List, Generator, Tuple]):
        if isinstance(lin_exprs, Generator):
            self.__model.addConstrs(lin_exprs)
        else:
            self.__model.addConstrs(constr for constr in lin_exprs)

    @override
    def setObjective(self, expr):
        self.__model.setObjective(expr)

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
        self.__model.setObjectiveN(expr, index, priority, weight, name=name)

    @override
    def addGenConstrAnd(self, resvar, varList: List[IVar]):
        """
        和 addGenConstrAnd(y, [x1,x2])
        :param resvar:
        :param varList:
        :return:
        """
        self.__model.addGenConstrAnd(resvar, varList)  # type: ignore

    @override
    def addGenConstrOr(self, resvar: IVar, varList: List[IVar]):
        self.__model.addGenConstrOr(resvar, varList)  # type: ignore

    @override
    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar]):
        super().addGenConstrXOr(resvar, varList)

    @override
    def addGenConstrPWL(
        self,
        var_x: IVar,
        var_y: IVar,
        x_range: List[float],
        y_range: List,
        cmp_type,
        M,
    ):
        super().addGenConstrPWL(var_x, var_y, x_range, y_range, cmp_type=cmp_type, M=M)

    @override
    def addGenConstrIndicator(
        self, binvar: IVar, binval: bool, lhs: IVar, sense: CmpType, rhs: float, M=None
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
        g_sense = gp.GRB.LESS_EQUAL
        if sense == CmpType.GREATER_EQUAL:
            g_sense = gp.GRB.GREATER_EQUAL
        elif sense == CmpType.LESS_EQUAL:
            g_sense = gp.GRB.LESS_EQUAL
        self.__model.addGenConstrIndicator(binvar, binval, lhs, g_sense, rhs)  # type: ignore

    @override
    def addIndicator(self, binvar: IVar, binval: bool, constr):
        raise NotImplementedError()

    @override
    def addGenConstrAbs(self, resvar, var_abs: IVar, M):
        if isinstance(var_abs, gp.Var):
            self.__model.addGenConstrAbs(resvar, var_abs)  # type: ignore
        else:
            temp = self.addVar()
            self.addConstr(temp == var_abs)
            self.addGenConstrAbs(resvar, temp, M)

    @override
    def addGenConstrMultiply(self, z: IVar, l: Tuple[IVar, IVar]):
        """x * y = z"""
        warnings.warn("gurobi使用下该方法<addConstrMultiply>可能会影响性能")
        self.__model.update()
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
        self.__model.addRange(expr, min_value, max_value)

    @override
    def calc_lbub_and_expr(self, constr) -> Tuple[Real, Real, Any]:
        raise NotImplementedError()

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
            return self.__model.NumVars
        elif vtype == Vtype.CONTINUOUS:
            return self.__model.NumVars - self.__model.NumIntVars
        elif vtype == Vtype.INTEGER:
            return self.__model.NumIntVars - self.__model.NumBinVars
        else:
            return self.__model.NumBinVars

    @override
    def numConstraints(self) -> int:
        return self.__model.NumConstrs

    @override
    def write(self, filename: str, obfuscated=False):
        self.__model.write(filename)

    @override
    def read(self, path: str):
        self.__model.read(path)

    @property
    @override
    def ObjVal(self) -> Real:
        return self.__model.ObjVal

    @override
    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        if self._params.TimeLimit:
            self.setTimeLimit(self._params.TimeLimit)
        if self._params.MIPGap:
            self.__model.Params.MIPGap = self._params.MIPGap
        if self._params.Precision:
            pass
        if self._params.EnableOutput:
            self.__model.setParam("OutputFlag", 1)
        else:
            self.__model.setParam("OutputFlag", 0)
        self.__model.ModelSense = (
            gp.GRB.MAXIMIZE if obj_type == ObjType.MAXIMIZE else gp.GRB.MINIMIZE
        )
        self.__model.optimize()
        status = self.__model.Status
        if status == gp.GRB.OPTIMAL:
            result = OptimizationStatus.OPTIMAL
        elif status == gp.GRB.INFEASIBLE:
            result = OptimizationStatus.INFEASIBLE
        elif status == gp.GRB.UNBOUNDED:
            result = OptimizationStatus.UNBOUNDED
        elif status == gp.GRB.CUTOFF:
            result = OptimizationStatus.CUTOFF
        elif status == gp.GRB.LOADED:
            result = OptimizationStatus.LOADED
        elif status == gp.GRB.TIME_LIMIT:
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
        if isinstance(expression, Real):
            return expression
        if isinstance(expression, gp.Var):
            return expression.X
        return expression.getValue()

    @override
    def setNumThreads(self, num_theads: int):
        self.__model.setParam("Threads", num_theads)
