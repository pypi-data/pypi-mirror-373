# -*- coding: utf-8 -*-
# @Time    : 2023/4/28 15:33
# @Author  : luyi
# 定义接口。统一类型。
from abc import ABCMeta, abstractmethod
from collections import UserList
from itertools import groupby
from typing import (
    Any,
    List,
    Literal,
    Optional,
    Union,
    Generator,
    Tuple,
)


from .tupledict import ITupledict, tupledict
from .func import name_str
from .utilx import INFINITY, check_bool_var, get_combinations, is_list_or_tuple
from .constants import Vtype, ObjType, CmpType, OptimizationStatus, Params

Real = Union[float, int]


class IVar:
    def __init__(self):
        # 变量类型
        self.v_type = None
        self._solver = None

    @property
    def X(self) -> Real: ...

    # @property
    # def VarIndex(self) -> Real: ...

    @property
    def VarName(self) -> str: ...

    @property
    def LB(self) -> Real: ...

    @property
    def UB(self) -> Real: ...

    # def setValue(self, value: Real): ...

    # def setUb(self, ub: Real): ...

    # def setLb(self, lb: Real): ...

    # def Not(self) -> "IVar":
    #     """
    #     返回一个相反的变量，仅用于0,1变量。
    #     :return:
    #     """
    #     ...

    # def setBounds(self, lb, ub): ...

    def __add__(self, expr) -> Any: ...

    def __radd__(self, cst) -> Any: ...

    def __sub__(self, expr) -> Any: ...

    def __rsub__(self, cst) -> Any: ...

    def __mul__(self, other) -> Any: ...

    def __rmul__(self, other) -> Any: ...

    def __ge__(self, other) -> Any: ...

    def __le__(self, other) -> Any: ...


class ITuplelist(UserList):
    @abstractmethod
    def select(self, *args) -> List: ...


class IModel(metaclass=ABCMeta):
    def __init__(
        self,
        solver_id: Literal[
            "SCIP",
            "CBC",
            "CP",
            "SAT",
            "CLP",
            "CPLEX",
            "CPLEX_CP",
            "GLOP",
            "BOP",
            "GLPK",
            "GUROBI",
        ],
        name,
    ):
        self._params: Params = Params()
        self.solver_id = solver_id
        self._name = name
        self._allkpis = {}
        self._multi_object_expr = []
        self._flag_objective_n = None

    @property
    def Params(self) -> Params:
        return self._params

    @property
    def INFINITY(self) -> Real:
        return INFINITY

    @property
    def name(self) -> str:
        return self._name

    @property
    def WallTime(self) -> float:
        return self.wall_time()

    def addKpi(self, kpi_arg, name: str):
        if name in self._allkpis:
            raise Exception(f"KPI名称 {name} 重复")
        self._allkpis[name] = kpi_arg

    def reportKpis(self):
        """
        输出所有KPI
        :return:
        """
        print("===========all kpis=============")
        for name, kpi_arg in self._allkpis.items():
            value = self.valueExpression(kpi_arg)
            print(f"{name} = {value}")
        print("================================")

    def kpiByName(self, name: str):
        """根据名称获取KPI"""
        kpi = self._allkpis.get(name)
        if kpi is None:
            raise Exception(f"KPI名称 {name} 不存在")
        return kpi

    def kpiValueByName(self, name: str):
        """根据名称获取KPI的值"""
        kpi = self.kpiByName(name)
        return self.valueExpression(kpi)

    def removeKpi(self, name: str):
        """
        移除KPI
        :param name:
        :return:
        """
        if name not in self._allkpis:
            raise Exception(f"KPI名称 {name} 不存在")
        del self._allkpis[name]

    def clearKpis(self):
        """
        清除所有KPI
        :return:
        """
        self._allkpis.clear()

    @property
    def numOfKpis(self):
        return len(self._allkpis)

    def statistics(self):
        """
        统计模型信息
        :return:
        """
        print("statistics：\n========")
        print(f"numConstraints：{self.numConstraints()}")
        print(f"numVars：{self.numVars()}")
        print(
            f"numVars of int：{self.numVars(Vtype.INTEGER)+self.numVars(Vtype.BINARY)}"
        )
        print("========")

    def reportMultiObjValue(self):
        """
        展示多目标优化的目标值
        """
        print("========MultiObjValue===========")
        for expr, weight, name in self._multi_object_expr:
            value = self.valueExpression(expr)
            print(f"{name} : {round(value*weight, 2)}")
        print("================================")

    # -----------------------抽象方法-------------------------------
    @abstractmethod
    def calc_lbub_and_expr(self, constr) -> Tuple[Real, Real, Any]:
        """
        将线性约束分解为变量下界，变量上界，表达式。

        :param constr: 线性约束
        """
        ...

    @abstractmethod
    def Sum(self, expr_array) -> Any: ...

    def sum(self, expr_array):
        return self.Sum(expr_array)

    @abstractmethod
    def setHint(self, start: List[Tuple[IVar, Real]]): ...
    @abstractmethod
    def setTimeLimit(self, time_limit_seconds: int):
        """
        设置程序最大运行时间
        :param time_limit_seconds: 秒
        """
        ...

    @abstractmethod
    def wall_time(self) -> Real:
        """
        求解所花费的时间
        :return: 求解所花费的时间，单位毫秒
        """
        ...

    @abstractmethod
    def iterations(self) -> Real:
        """

        :return: 算法迭代的次数
        """
        ...

    @abstractmethod
    def nodes(self) -> Real:
        """

        :return: 节点数
        """
        ...

    @abstractmethod
    def addVar(
        self,
        lb,
        ub,
        vtype: Vtype,
        name: str = "",
    ) -> IVar:
        """
        创建变量
        :param lb: 变量下界
        :param ub: 变量上界
        :param vtype: 变量类型： Vtype.CONTINUOUS（连续）,Vtype.BINARY(0-1变量), Vtype.BINARY（整数变量）
        :param name:变量名
        :return:变量实体
        """
        ...

    @abstractmethod
    def addVars(
        self,
        *indices,
        lb,
        ub,
        vtype: Vtype,
        name: str = "",
    ) -> ITupledict:
        """
        创建多维变量
        :param indices:多维的参数，如addVars(1,2),addVars(mList,nList),addVars([1,2,3],[3,4,5])等。
        :param lb:变量下界
        :param ub:变量上界
        :param vtype:变量类型： Vtype.CONTINUOUS（连续）,Vtype.BINARY(0-1变量), Vtype.BINARY（整数变量）
        :param name:变量名
        :return:tupledict类型
        """
        li = []
        for ind in indices:
            if isinstance(ind, int):
                ind = [i for i in range(ind)]
            elif is_list_or_tuple(ind):
                pass
            elif isinstance(ind, str):
                ind = [ind]
            else:
                raise ValueError("error input")
            li.append(ind)
        all_keys_tuple = get_combinations(li)
        tu_dict = tupledict(
            [
                [key, self.addVar(lb, ub, vtype, name_str(name, key))]
                for key in all_keys_tuple
            ]
        )
        return tu_dict  # type: ignore

    @abstractmethod
    def getVars(self) -> List[IVar]:
        """
        获取所有的变量对象
        :return:
        """
        ...

    @abstractmethod
    def getVar(self, i) -> IVar:
        """
        获取第i个变量
        :param i:
        :return:
        """
        ...

    @abstractmethod
    def addConstr(self, lin_expr):
        """
        向模型添加约束条件，
        :param lin_expr:线性约束表达式
        :param name: 约束名称
        :return:
        """
        ...

    @abstractmethod
    def addConstrs(self, lin_exprs: Union[List, Generator, Tuple]):
        """
        向模型添加多个约束条件，
        :param lin_exprs: 线性约束表达式集合 可以为列表或者元组。
        :param name:名称
        :return:
        """
        ...

    @abstractmethod
    def setObjective(self, expr):
        """
        设置模型的单一目标
        :param expr: 目标表达式
        优化方向。ObjType.MINIMIZE（最小值），ObjType.MAXIMIZE(最大值)
        :return:
        """
        self._multi_object_expr.clear()
        self._multi_object_expr.append((expr, 1, "单一目标"))
        if self._flag_objective_n is None:
            self._flag_objective_n = False
        else:
            if self._flag_objective_n:
                raise Exception("单一目标和多目标不能同时设置")
            else:
                raise Exception("单一目标设置多次,请检查")

    @abstractmethod
    def setObjectiveN(
        self, expr, index: int, priority: int = 0, weight: float = 1, name: str = ""
    ):
        """
        多目标优化，优化最小值
        :param expr: 表达式
        :param index: 目标函数对应的序号 (默认 0，1，2，…), 以 index=0 作为目标函数的值, 其余值需要另外设置参数
        :param priority: 分层序列法多目标决策优先级(整数值), 值越大优先级越高【未实现】
        :param weight: 线性加权多目标决策权重(在优先级相同时发挥作用)
        :param name: 名称
        :return:
        """
        if self._flag_objective_n is False:
            raise Exception("单一目标和多目标不能同时设置")
        else:
            self._flag_objective_n = True
        self._multi_object_expr.append((expr, weight, name))

    @abstractmethod
    def addGenConstrAnd(self, resvar, varList: List[IVar]):
        """
        and 运算。
        addGenConstrAnd(y, [x1, x2]) 表示y = max(x1,x2)。 所有变量均为0-1变量
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        check_bool_var(resvar, varList)
        for var in varList:
            self.addConstr(resvar <= var)
        self.addConstr(resvar >= self.Sum(varList) - len(varList) + 1)

    @abstractmethod
    def addGenConstrOr(self, resvar: IVar, varList: List[IVar]):
        """
        或运算
        addGenConstrOr(y, [x1, x2]) 表示y = min(x1,x2)。 所有变量均为0-1变量
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        check_bool_var(resvar, varList)
        for var in varList:
            self.addConstr(resvar >= var)
        self.addConstr(resvar <= self.Sum(varList))

    @abstractmethod
    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar]):
        """
        异或运算
        addGenConstrXOr(y, [x1, x2])。 所有变量均为0-1变量
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        if len(varList) != 2:
            raise ValueError("length of vars must be 2")
        check_bool_var(resvar, varList)
        self.addConstr(resvar >= varList[0] - varList[1])
        self.addConstr(resvar >= varList[1] - varList[0])
        self.addConstr(resvar <= varList[0] + varList[1])
        self.addConstr(resvar <= 2 - varList[0] - varList[1])

    @abstractmethod
    def addGenConstrPWL(
        self,
        var_x: IVar,
        var_y: IVar,
        x_range: List[float],
        y_range: List,
        cmp_type: Union[List[CmpType], CmpType],
        M,
    ):
        """
        设置分段约束
        :param var_y: f(x)
        :param var_x:指定变量的目标函数是分段线性
        :param x:  定义分段线性目标函数的点的横坐标值(非减序列)
        :param y:定义分段线性目标函数的点的纵坐标值
        :return:
        """
        if M is None:
            M = self.INFINITY
        if isinstance(cmp_type, list):
            assert len(cmp_type) == len(y_range), "分段函数设置异常"
        else:
            cmp_type = [cmp_type] * len(y_range)
        assert len(x_range) == len(y_range) - 1, "分段函数设置异常"
        # name = f"{var_x.VarName}_{var_y.VarName}"
        z = self.addVars(len(y_range), vtype=Vtype.BINARY, lb=0, ub=1)
        self.addConstr(z.quicksum() == 1)
        self.addConstr(
            var_x
            <= z.quickprod(
                {i: x_range[i] if i < len(z) - 1 else M for i in range(len(z))}, "*"
            )
        )
        self.addConstr(
            var_x
            >= z.quickprod(
                {i: x_range[i - 1] if i > 0 else -M for i in range(len(z))}, "*"
            )
        )

        for i in range(len(y_range)):
            cmp = cmp_type[i]
            if cmp == CmpType.EQUAL:
                self.addConstr(var_y <= y_range[i] + (1 - z[i]) * M)
                self.addConstr(var_y >= y_range[i] - (1 - z[i]) * M)
            elif cmp == CmpType.LESS_EQUAL:
                self.addConstr(var_y <= y_range[i] + (1 - z[i]) * M)
            else:
                self.addConstr(var_y >= y_range[i] - (1 - z[i]) * M)

    @abstractmethod
    def addGenConstrIndicator(
        self,
        binvar: IVar,
        binval: bool,
        lhs: IVar,
        sense: CmpType,
        rhs,
        M,
    ):
        """
        若 binvar 为binval ,则 lhs 与 rhs 之间有sense 的关系
        若M不指定,则程序会给与默认。但仍推荐给出M。程序自动给出的可能会存在问题。
        :param binvar: 0-1变量
        :param binval: bool 常量
        :param lhs:  左侧变量
        :param sense: 等号，大于等于，小于等于
        :param rhs: 右侧常量
        :param M: 大M
        :return:
        """
        if binval is True:
            z = 1 - binvar
        else:
            z = binvar
        if sense == CmpType.GREATER_EQUAL:
            self.addConstr(lhs + M * z >= rhs)
        elif sense == CmpType.EQUAL:
            self.addConstr(lhs + M * z >= rhs)
            self.addConstr(lhs - M * z <= rhs)
        else:
            self.addConstr(lhs - M * z <= rhs)

    @abstractmethod
    def addIndicator(self, binvar: IVar, binval: bool, constr):
        """
        若 binvar 为binval ,则 lhs 与 rhs 之间有sense 的关系
        若M不指定，则程序会给与默认。但仍推荐给出M。程序自动给出的可能会存在问题。
        :param binvar: 0-1变量
        :param binval: bool 常量
        :param lhs:  左侧变量
        :param sense: 等号，大于等于，小于等于
        :param rhs: 右侧常量
        :param M: 大M
        :return:
        """
        ...

    @abstractmethod
    def addGenConstrAbs(self, resvar: any, var_abs: IVar, M):  # type: ignore
        """
        绝对值 resvar = |var_abs|
        :param resvar:
        :param var_abs:
        :return:
        """
        ...

    @abstractmethod
    def addGenConstrMultiply(self, z: IVar, l: Tuple[IVar, IVar]):
        """
        满足 z = x * y
        其中 x 为0,1变量
        :param l:
        :param z: 变量
        :return:
        """
        if len(list(l)) != 2:
            raise RuntimeError("Only need two variables")

    @abstractmethod
    def addRange(self, expr, min_value: Real, max_value: Real):
        """
        添加范围约束
        :param expr: 表达式
        :param min_value: 最小值
        :param max_value: 最大值
        :return:
        """
        if isinstance(min_value, (int, float)) and isinstance(max_value, (int, float)):
            if min_value > max_value:
                raise ValueError("min_value is bigger than max_value")
        self.addConstr(expr >= min_value)
        self.addConstr(expr <= max_value)

    @abstractmethod
    def addConstrOr(
        self,
        constrs: List,
        ok_num: int = 1,
        cmp_type: CmpType = CmpType.EQUAL,
        M=None,
    ):
        """
        约束的满足情况,满足的次数
        :param constr: 所有的约束
        :param ok_num:  需要满足的个数，具体则根据cmpType
        :param cmpType: CmpType.LESS_EQUAL CmpType.EQUAL,CmpType.GREATER_EQUAL
        :param M: M值，推荐指定M值。
        :return:
        """
        ...

    @abstractmethod
    def numVars(self, vtype: Optional[Vtype] = None) -> int:
        """
        变量个数
        :return:
        """
        ...

    @abstractmethod
    def numConstraints(self) -> int:
        """
        约束个数
        :return:
        """
        ...

    @abstractmethod
    def write(self, filename: str, obfuscated=False):
        """
        写入到文件
        :param filename:文件名，支持后缀 .lp .mps .proto(目前有问题)
        :param obfuscated: 是否混淆，默认不混淆
        :return:
        """
        ...

    @abstractmethod
    def read(self, path: str):
        """读取文件 lp,mps 文件。

        Args:
            path (str): _description_
        """
        ...

    @property
    @abstractmethod
    def ObjVal(self) -> Real:
        """目标值"""
        ...

    @abstractmethod
    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        """
        优化目标
        :param time_limit_milliseconds:最大运行时长
        :param obj_type:优化目标。ObjType.MINIMIZE（最小值），ObjType.MAXIMIZE(最大值)
        :param enable_output: 是否显示gap日志。
        :return:
        """
        ...

    @abstractmethod
    def clear(self):
        """清空所有的目标和约束"""
        self._multi_object_expr.clear()
        self._allkpis = {}
        self._flag_objective_n = None

    @abstractmethod
    def close(self):
        """关闭"""
        ...

    @abstractmethod
    def valueExpression(self, expression) -> Real:
        """
        计算表达式的值。
        :param expression:
        :return:计算后的值
        """
        ...

    def X(self, expression):
        """
        计算表达式的值。
        :param expression:
        :return:计算后的值
        """
        return self.valueExpression(expression)

    @abstractmethod
    def newIntervalVar(self, start, size, end) -> Any:
        """
        创建变量： start+size=end

        Args:
            start (_type_): 开始
            size (_type_): 大小
            end (_type_): 结束
        """
        ...

    @abstractmethod
    def addNoOverlap(self, interval_vars: List, M):
        """
        互相之间不重复

        Args:
            interval_vars (List): 间隔变量
        """
        pass

    @abstractmethod
    def setNumThreads(self, num_theads: int):
        """
        设置线程的个数

        Args:
            num_theads (int): 线程个数
        """
        ...


class ICpModel(IModel):
    def __init__(self, solver_id: Literal["CPLEX_CP", "CP"], name=""):
        super().__init__(
            solver_id,
            name,
        )

    @abstractmethod
    def addCpElement(self, index, variables, target): ...

    @abstractmethod
    def addCpCircuit(self, arcs): ...

    @abstractmethod
    def addCpAllowedAssignments(self, variables, tuples_list): ...

    @abstractmethod
    def addCpForbiddenAssignments(self, variables, tuples_list): ...

    @abstractmethod
    def addCpInverse(
        self,
        variables,
        inverse_variables,
    ): ...

    @abstractmethod
    def addCpMapDomain(self, var, bool_var_array, offset):
        """Adds `var == i + offset <=> bool_var_array[i] == true for all i`."""
        ...

    @abstractmethod
    def addCpImplication(self, a, b): ...

    @abstractmethod
    def addCpBoolTrueOr(self, literals): ...

    @abstractmethod
    def addCpBoolTrueAnd(self, literals): ...

    @abstractmethod
    def addCpAtLeastOneIsTrue(self, literals): ...

    @abstractmethod
    def addCpAtMostOneIsTrue(self, literals): ...

    @abstractmethod
    def addCpExactlyNumIsTrue(self, literals, num: int = 1): ...

    @abstractmethod
    def addCpGenConstrMax(self, target: IVar, varList: List[IVar]):
        """
        最大值约束
        """
        ...

    @abstractmethod
    def addCpGenConstrMin(self, target: IVar, varList: List[IVar]):
        """
        最小值约束
        """
        ...

    @abstractmethod
    def addCpGenConstrDivision(self, target, num, denom):
        """Adds `target == num // denom` (integer division rounded towards 0)."""
        ...

    @abstractmethod
    def addCpGenConstrModulo(self, target, num, denom):
        """Adds `target = expr % mod`."""
        ...

    @abstractmethod
    def addCpGenConstrMultiplication(
        self,
        target,
        *expressions,
    ): ...
