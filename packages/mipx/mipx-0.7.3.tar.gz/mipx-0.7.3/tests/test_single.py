import mipx


def main():
    model = mipx.CpModel("CP")
    x = model.addVar(ub=10, name="x")
    y = model.addVar(ub=10, name="y")
    b = model.addVar(vtype=mipx.BINARY, name="b")
    model.addConstr(b == 1)
    s = model.sum([x, y, 10])
    # model.addGenConstrIndicator(b, True, s, mipx.GREATER_EQUAL, 10)
    # z = x + y + 10 >= b
    # print(z.GetCoeffs())
    model.addGenConstrIndicator(b, True, x + y + s + 4, mipx.GREATER_EQUAL, 10)
    model.setObjective(x + y)
    status = model.optimize()
    assert mipx.success(status)
    # assert int(model.ObjVal) == 10
    # assert int(model.X(x + y)) == 10


if __name__ == "__main__":
    main()
