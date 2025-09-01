# -*- coding: utf-8 -*-
# @Time    : 2023/4/29 10:13
# @Author  : luyi
import numbers

try:
    from ortools.linear_solver.linear_solver_natural_api import CastToLinExp, OFFSET_KEY  # type: ignore
except Exception as e:
    from ortools.linear_solver.python.linear_solver_natural_api import (
        CastToLinExp,
        OFFSET_KEY,
    )

from ortools.linear_solver.pywraplp import SumArray
from .utilx import is_list_or_tuple
from .interface_ import IVar


def SumExpr(*args):
    return LineExpr(args)


class LineExpr(SumArray):
    def __init__(self, array=None):
        if array is None:
            array = []
        else:
            if not is_list_or_tuple(array):
                array = [array]
        super().__init__(array)
        self._array: list = self._SumArray__array  # type: ignore

    def add(self, arg, mult=1.0):
        self._array.append(CastToLinExp(arg * mult))

    def addConstant(self, constant):
        """
        添加常量
        :param constant:
        :return:
        """
        self._array.append(CastToLinExp(constant))

    def addTerms(self, newcoeffs, newvars):
        """
        通过系数和变量来添加线性表达式
            addTerms(1.0, x)
            addTerms([1.0, 2.0], [x, y])
        :param newcoeffs: 系数集合或者系数
        :param newvars: 变量集合或者变量
        :return:
        """
        if is_list_or_tuple(newcoeffs) == is_list_or_tuple(newvars):
            if is_list_or_tuple(newcoeffs) and len(newcoeffs) != len(newvars):
                raise TypeError("传参异常")
            # 动态添加
            if is_list_or_tuple(newcoeffs):
                for i in range(len(newcoeffs)):
                    self.add(newvars[i], newcoeffs[i])
            else:
                self.add(newvars, newcoeffs)
        else:
            raise TypeError("传参异常")

    def clear(self):
        self._array.clear()

    def copy(self):
        return LineExpr(self._array)

    def getCoeff(self, x: IVar):
        """
        获取第i个系数
        :param x:
        :return:
        """
        coeffs = self.GetCoeffs()
        return coeffs.get(x)

    def getConstant(self):
        coeffs = self.GetCoeffs()
        KEY = OFFSET_KEY
        print(coeffs)
        if KEY in coeffs:
            return coeffs.get(KEY)
        else:
            return 0

    def getValue(self) -> numbers.Number:
        """
        表达式的值
        :return:
        """
        value = 0
        coeffs = self.GetCoeffs()
        for key, coeff in coeffs.items():
            if key is OFFSET_KEY:
                value += coeffs.get(key)  # type: ignore
            else:
                var: IVar = key
                x = var.X
                value += coeff * x
        return value  # type: ignore

    def size(self):
        return len(self.GetCoeffs())

    def __add__(self, expr):
        return SumExpr(self, expr)

    def __radd__(self, cst):
        return SumExpr(self, cst)

    def __sub__(self, expr):
        return SumExpr(self, -expr)

    def __rsub__(self, cst):
        return SumExpr(-self, cst)

    def __mul__(self, other):  # type: ignore
        pass
