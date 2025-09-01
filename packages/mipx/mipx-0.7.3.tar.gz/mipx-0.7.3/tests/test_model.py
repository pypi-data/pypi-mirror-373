import pytest
import mipx

SOLVERS = ["CBC", "SCIP", "GUROBI", "CPLEX", "SAT", "CP", "CPLEX_CP"]
CP_SOLVERS = ["CP", "CPLEX_CP"]


@pytest.fixture(params=SOLVERS)
def model(request):
    if request.param in CP_SOLVERS:
        return mipx.CpModel(solver_id=request.param)
    return mipx.Model(solver_id=request.param)


@pytest.fixture(params=CP_SOLVERS)
def cpmodel(request):
    return mipx.CpModel(solver_id=request.param)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.usefixtures("model")
class TestModel:
    def test_tuple_dict(self, model: mipx.Model):
        x = model.addVars(2, 3, 4)
        model.addConstr(x[1, 2, 3] == 1)
        model.addConstr(x[1, 1, 3] == 2)
        model.addConstr(x.quicksum(1, 2, "*") >= 1)
        model.addConstr(x.quickprod({(1, 2, 3): 3}, 1, 2, "*") >= 0)
        status = model.optimize()
        assert mipx.success(status)

    def test_add_constr(self, model: mipx.Model):
        x = model.addVar(ub=1)
        y = model.addVars(10)
        model.addConstr(x == 1)
        model.addConstr(y.quicksum() == 10)
        y.quicksum([1, 2])
        status = model.optimize()
        assert mipx.success(status)
        assert x.X == 1
        assert model.valueExpression(y.quicksum()) == 10

    def test_gen_constr_and(self, model: mipx.Model):
        x = model.addVars(6, vtype=mipx.BINARY)
        y = model.addVar(vtype=mipx.BINARY)
        model.addConstr(x[0] == 0)
        model.addConstr(x.quicksum() == 5)
        model.addGenConstrAnd(y, x.quickselect())
        m = model.addVar(vtype=mipx.BINARY, ub=1)
        z = model.addVars(3, vtype=mipx.BINARY, ub=1)
        model.addConstr(z.quicksum() == 3)
        model.addGenConstrAnd(m, z.quickselect())
        status = model.optimize()
        assert mipx.success(status)
        assert y.X == 0
        assert m.X == 1

    def test_gen_constr_or(self, model: mipx.Model):
        x = model.addVars(6, vtype=mipx.BINARY)
        y = model.addVar(vtype=mipx.BINARY)
        model.addConstr(x[0] == 0)
        model.addConstr(x.quicksum() == 5)
        model.addGenConstrOr(y, x.quickselect())
        m = model.addVar(vtype=mipx.BINARY, ub=1)
        z = model.addVars(3, vtype=mipx.BINARY, ub=1)
        model.addConstr(z.quicksum() == 0)
        model.addGenConstrOr(m, z.quickselect())
        status = model.optimize()
        assert mipx.success(status)
        assert y.X == 1
        assert m.X == 0

    def test_gen_constr_xor(self, model: mipx.Model):
        x = model.addVars(2, vtype=mipx.BINARY)
        y = model.addVar(vtype=mipx.BINARY)
        # 不同时
        model.addConstrs([x[0] == 0, x[1] == 1])
        model.addGenConstrXOr(y, x.quickselect())
        a = model.addVars(2, vtype=mipx.BINARY)
        b = model.addVar(vtype=mipx.BINARY)
        # 同时
        model.addConstrs([a[0] == 1, a[1] == 1])
        model.addGenConstrXOr(b, a.quickselect())
        c = model.addVars(2, vtype=mipx.BINARY)
        d = model.addVar(vtype=mipx.BINARY)
        # 同时
        model.addConstrs([c[0] == 0, c[1] == 0])
        model.addGenConstrXOr(d, c.quickselect())
        e = model.addVars(2, vtype=mipx.BINARY)
        f = model.addVar(vtype=mipx.BINARY)
        # 同时
        model.addConstrs([e[0] == 1, e[1] == 0])
        model.addGenConstrXOr(f, e.quickselect())
        status = model.optimize()
        assert mipx.success(status)
        assert mipx.succ(status)
        assert y.X == 1
        assert b.X == 0
        assert d.X == 0
        assert f.X == 1

    def test_set_objeciven(self, model: mipx.Model):
        x = model.addVars(10)
        y = model.addVars(10)
        model.addConstr(x[1] <= 20)
        model.addConstr(x[2] <= 10)
        model.setObjectiveN(-x[1], 0)
        model.setObjectiveN(-x[2], 1)
        status = model.optimize()
        assert mipx.success(status)
        assert mipx.succ(status)
        assert x[1].X == 20
        assert x[2].X == 10

    def test_gen_constr_pwl(self, model: mipx.Model):
        x = model.addVar(ub=10, vtype=mipx.INTEGER)
        y = model.addVar(ub=100, vtype=mipx.INTEGER)
        z = model.addVar(lb=1, ub=10, vtype=mipx.INTEGER)
        model.addGenConstrPWL(x, y, [4, 10], [1, 5 + z, 10], M=1000)
        model.setObjective(y)
        status = model.optimize(mipx.MAXIMIZE)
        assert mipx.success(status)
        assert y.X == 15
        assert z.X == 10

    def test_gen_constr_abs(self, model: mipx.Model):
        x = model.addVar(lb=-10, ub=10, vtype=mipx.INTEGER)
        y = model.addVar(ub=10, vtype=mipx.INTEGER)
        model.addGenConstrAbs(y, x, M=1000)
        model.addConstr(x == -5)
        status = model.optimize(mipx.MAXIMIZE)
        assert mipx.success(status)
        assert y.X == 5

    def test_tuple_select(self, model: mipx.Model):
        data = [(1, 2, 4), (3, 4, 6), (5, 6, 8)]
        x = mipx.tupledict()
        for key in data:
            x[key] = model.addVar(lb=0, vtype=mipx.INTEGER)
        assert len(x.keyset("-", "*", "*")) == 3
        z = model.addVars([1, 2, 3], [2, 3, 4])
        assert len(z.keyset("-", "*")) == 3

        y = model.addVars(10)
        assert len(y.quickselect("*")) == 10
        assert len(y.quickselect([1, 2])) == 2

        data = [(1, 2), (2, 2), (2, 3)]
        z = mipx.tupledict()
        for key in data:
            z[key] = model.addVar(lb=0, vtype=mipx.INTEGER)
        assert len(z.quickselect(2, 2)) == 1
        assert len(z.quickselect(2, "*")) == 2
        assert len(z.quickselect("*", "*")) == 3
        assert len(z.quickselect([1, 2], 3)) == 1

    def test_var(self, model: mipx.Model):
        x = model.addVar(lb=-10.5, ub=10, vtype=mipx.INTEGER)
        y = model.addVar(lb=-10, ub=10, vtype=mipx.CONTINUOUS)
        model.setObjective(x + y)
        status = model.optimize()
        assert mipx.success(status)
        assert model.ObjVal == -20
        assert x.X == -10
        assert y.X == -10
        assert x.LB == -10
        assert y.LB == -10
        assert y.UB == 10
        assert x.UB == 10

    def test_kpi(self, model: mipx.Model):
        x = model.addVar(ub=10)
        y = model.addVar(ub=10)
        model.setObjective(x + y)
        model.addKpi(x, "x")
        model.addKpi(y, "y")
        model.addKpi(x + y, "z")
        status = model.optimize(mipx.MAXIMIZE)
        assert mipx.success(status)
        assert model.kpiValueByName("x") == 10
        assert model.kpiValueByName("y") == 10
        assert model.kpiValueByName("z") == 10 + 10
        assert model.numOfKpis == 3

    def test_sum(self, model: mipx.Model):
        x = model.addVar(ub=10)
        y = model.addVar(ub=10)
        z = model.sum([x, y])
        model.setObjective(z)
        status = model.optimize(mipx.MAXIMIZE)
        assert mipx.success(status)
        assert model.valueExpression(z) == x.X + y.X
        assert model.X(z) == x.X + y.X

    def test_addGenConstrIndicator(self, model: mipx.Model):
        x = model.addVar(ub=10, name="x")
        y = model.addVar(ub=10, name="y")
        b = model.addVar(vtype=mipx.BINARY, name="b")
        model.addConstr(b == 1)
        model.addGenConstrIndicator(b, True, x + y, mipx.GREATER_EQUAL, 10)
        model.setObjective(x + y)
        status = model.optimize()
        assert mipx.success(status)
        assert int(model.ObjVal) == 10
        assert int(model.X(x + y)) == 10

    def test_addGenConstrMultiply(self, model: mipx.Model):
        pass

    def test_addConstrOr(self, model: mipx.Model):
        pass

    def test_addNoOverlap(self, model: mipx.Model):
        pass
