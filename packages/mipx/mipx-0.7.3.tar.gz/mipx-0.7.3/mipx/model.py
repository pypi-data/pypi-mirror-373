from typing import Any, Generator, List, Literal, Optional, Tuple, Union
from typing_extensions import override

from .utilx import pre_condition, get_update_lub
from .interface_ import IModel, IVar
from .commonsolver import CommonModelSolver
from .constants import CmpType, ObjType, OptimizationStatus, Params, Vtype

Real = Union[float, int]


class Model(IModel):
    """模型接口"""

    def __init__(
        self,
        solver_id: Literal[
            "SCIP", "CBC", "SAT", "CLP", "CPLEX", "GLOP", "BOP", "GLPK", "GUROBI"
        ] = "SCIP",
        name="",
    ):
        super().__init__(solver_id, name)
        self.solver_id = solver_id
        if solver_id == "CPLEX":
            try:
                from .cplexmpsolver import CplexMpSolver

                self.__model = CplexMpSolver(name=name)
                if not self.__model.has_cplex_env:
                    raise Exception("No CPLEX environment found")
            except ImportError:
                raise Exception("未找到cplex 库，请安装")
            except:
                raise Exception("未知错误")
        elif solver_id == "GUROBI":
            try:
                from .gurobisolver import GurobiSolver

                self.__model = GurobiSolver(name=name)
            except ImportError:
                raise Exception("未找到gurobi 库，请安装")
            except:
                raise Exception("未知错误")
        else:
            self.__model = CommonModelSolver(solver_id=solver_id, name=name)

    @property
    def Params(self) -> Params:
        """
        获取模型参数
        :return:
        """
        return self.__model.Params

    @override
    def Sum(self, expr_array):
        return self.__model.Sum(expr_array)

    @override
    def setHint(self, start: List[Tuple[IVar, Real]]):
        self.__model.setHint(start)  # type: ignore

    @override
    def setTimeLimit(self, time_limit_seconds: int):
        """
        设置程序最大运行时间
        :param time_limit_seconds: 秒
        """
        self.__model.setTimeLimit(time_limit_seconds)

    @override
    def wall_time(self) -> float:
        """
        求解所花费的时间
        :return: 求解所花费的时间，单位毫秒
        """
        return self.__model.wall_time()

    @override
    def iterations(self):
        """

        :return: 算法迭代的次数
        """
        return self.__model.iterations()

    @override
    def nodes(self) -> Real:
        """

        :return: 节点数
        """
        return self.__model.nodes()

    @override
    def addVar(
        self, lb: Real = 0, ub=None, vtype: Vtype = Vtype.CONTINUOUS, name: str = ""
    ) -> IVar:
        """
        创建变量
        :param lb: 变量下界
        :param ub: 变量上界
        :param vtype: 变量类型： Vtype.CONTINUOUS（连续）,Vtype.BINARY(0-1变量), Vtype.BINARY（整数变量）
        :param name:变量名
        :return:变量实体
        """
        lb, ub = get_update_lub(lb, ub, vtype)
        return self.__model.addVar(lb=lb, ub=ub, vtype=vtype, name=name)

    @override
    def addVars(
        self,
        *indices,
        lb: Real = 0,
        ub=None,
        vtype: Vtype = Vtype.CONTINUOUS,
        name: str = "",
    ):
        """
        创建多维变量
        :param indices:多维的参数，如addVars(1,2),addVars(mList,nList),addVars([1,2,3],[3,4,5])等。
        :param lb:变量下界
        :param ub:变量上界
        :param vtype:变量类型： Vtype.CONTINUOUS（连续）,Vtype.BINARY(0-1变量), Vtype.BINARY（整数变量）
        :param name:变量名
        :return:tupledict类型
        """
        pre_condition(len(indices) > 0, "addVars中多维参数缺失")
        lb, ub = get_update_lub(lb, ub, vtype)
        return self.__model.addVars(*indices, lb=lb, ub=ub, vtype=vtype, name=name)

    @override
    def getVars(self) -> List[IVar]:
        """
        获取所有的变量对象
        :return:
        """
        return self.__model.getVars()

    @override
    def getVar(self, i) -> IVar:
        """
        获取第i个变量
        :param i:
        :return:
        """
        return self.__model.getVar(i)

    @override
    def addConstr(self, lin_expr):
        """
        向模型添加约束条件，
        :param lin_expr:线性约束表达式
        :return:
        """
        self.__model.addConstr(lin_expr)

    @override
    def addConstrs(self, lin_exprs: Union[List, Generator, Tuple]):
        """
        向模型添加多个约束条件，
        :param lin_exprs: 线性约束表达式集合 可以为列表或者元组。
        :return:
        """
        self.__model.addConstrs(lin_exprs)

    @override
    def setObjective(self, expr):
        """
        设置模型的单一目标
        :param expr: 目标表达式
        优化方向。ObjType.MINIMIZE（最小值），ObjType.MAXIMIZE(最大值)
        :return:
        """
        super().setObjective(expr)
        self.__model.setObjective(expr)

    @override
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
        super().setObjectiveN(expr, index, priority, weight, name)
        self.__model.setObjectiveN(
            expr, index, priority=priority, weight=weight, name=name
        )

    @override
    def addGenConstrAnd(self, resvar, varList: List[IVar]):
        """
        and 运算。
        addGenConstrAnd(y, [x1, x2]) 表示y = and(x1,x2)。 所有变量均为0-1变量
        即 x1 x2 都为1时,y = 1
        :param resvar:
        :param varList:
        :return:
        """
        self.__model.addGenConstrAnd(resvar, varList)

    @override
    def addGenConstrOr(self, resvar: IVar, varList: List[IVar]):
        """
        或运算
        addGenConstrOr(y, [x1, x2]) 表示y = or(x1,x2)。 所有变量均为0-1变量
        即 x1,x2 至少有一个为1时,y = 1
        :param resvar:
        :param varList:
        :return:
        """
        self.__model.addGenConstrOr(resvar, varList)

    @override
    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar]):
        """
        异或运算
        addGenConstrXOr(y, [x1, x2])。 所有变量均为0-1变量
        x1 x2 y
        1  1  0
        1  0  1
        0  1  1
        0  0  0
        :param resvar:
        :param varList:
        :return:
        """
        self.__model.addGenConstrXOr(resvar, varList)

    @override
    def addGenConstrPWL(
        self,
        var_x: IVar,
        var_y: IVar,
        x_range: List[float],
        y_range: List[float],
        cmp_type: Union[List[CmpType], CmpType] = CmpType.EQUAL,
        M=None,
    ):
        """
        设置分段约束
        model.addGenConstrPWL(var, [1, 3, 5], [1, 2, 4])
        :param var_y: f(x)
        :param var_x:指定变量的目标函数是分段线性
        :param x:  定义分段线性变量的点的范围边界(非减序列)，要求x的范围大于0
        :param y:定义分段线性变量的范围所对应的目标函数的值
        :return:
        """
        if M is None:
            M = self.__model.INFINITY
        self.__model.addGenConstrPWL(
            var_x, var_y, x_range, y_range, cmp_type=cmp_type, M=M
        )

    @override
    def addGenConstrIndicator(
        self, binvar: IVar, binval: bool, lhs: IVar, sense: CmpType, rhs, M=None
    ):
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
        if M is None:
            M = self.__model.INFINITY
            # 检查是否能够
        self.__model.addGenConstrIndicator(binvar, binval, lhs, sense, rhs, M=M)

    @override
    def addIndicator(self, binvar: IVar, binval: bool, constr):
        self.__model.addIndicator(binvar, binval, constr)

    @override
    def addGenConstrAbs(self, resvar, var_abs: IVar, M=None):
        """
        绝对值 resvar = |var_abs|
        :param resvar:
        :param var_abs:
        :return:
        """
        if M is None:
            M = self.__model.INFINITY
        self.__model.addGenConstrAbs(resvar, var_abs, M=M)

    @override
    def addGenConstrMultiply(self, z: IVar, l: Tuple[IVar, IVar]):
        """
        满足 z = x * y
        其中 x 为0,1变量
        :param l:
        :param z: 变量
        :return:
        """
        self.__model.addGenConstrMultiply(z, l)

    @override
    def addRange(
        self, expr, min_value: Union[float, int], max_value: Union[float, int]
    ):
        """
        添加范围约束
        :param expr: 表达式
        :param min_value: 最小值
        :param max_value: 最大值
        :return:
        """
        self.__model.addRange(expr, min_value, max_value)

    @override
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
        self.__model.addConstrOr(constrs, ok_num=ok_num, cmp_type=cmp_type, M=M)

    @override
    def numVars(self, vtype: Optional[Vtype] = None) -> int:
        """
        变量个数
        :return:
        """
        return self.__model.numVars(vtype)

    @override
    def numConstraints(self) -> int:
        """
        约束个数
        :return:
        """
        return self.__model.numConstraints()

    @override
    def write(self, filename: str, obfuscated=False):
        """
        写入到文件
        :param filename:文件名，支持后缀 .lp .mps .proto(目前有问题)
        :param obfuscated: 是否混淆，默认不混淆
        :return:
        """
        self.__model.write(filename, obfuscated=obfuscated)

    @override
    def read(self, path: str):
        self.__model.read(path)

    @property
    @override
    def ObjVal(self) -> Real:
        """目标值"""
        return self.__model.ObjVal

    @override
    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        """
        优化目标
        :param time_limit_milliseconds:最大运行时长
        :param obj_type:优化目标。ObjType.MINIMIZE（最小值），ObjType.MAXIMIZE(最大值)
        :param enable_output: 是否显示gap日志。
        :return:
        """
        return self.__model.optimize(obj_type=obj_type)

    @override
    def clear(self):
        super().clear()
        self.clearKpis()
        self.__model.clear()

    @override
    def close(self):
        self.__model.close()

    @override
    def valueExpression(self, expression):
        """
        计算表达式的值。
        :param expression:
        :return:
        """
        if isinstance(expression, (int, float)):
            return expression
        return self.__model.valueExpression(expression)

    @override
    def newIntervalVar(self, start, size, end):
        """
        创建变量： start+size=end

        Args:
            start (_type_): 开始
            size (_type_): 大小
            end (_type_): 结束
        """
        return self.__model.newIntervalVar(start, size, end)

    @override
    def addNoOverlap(self, interval_vars: List, M: int):
        """
        互相之间不重复

        Args:
            interval_vars (List): 间隔变量
        """
        self.__model.addNoOverlap(interval_vars, M)

    @override
    def setNumThreads(self, num_theads: int):
        """
        设置线程的个数

        Args:
            num_theads (int): 线程个数
        """
        self.__model.setNumThreads(num_theads)

    @override
    def calc_lbub_and_expr(self, constr) -> Tuple[Real, Real, Any]:
        return self.__model.calc_lbub_and_expr(constr)
