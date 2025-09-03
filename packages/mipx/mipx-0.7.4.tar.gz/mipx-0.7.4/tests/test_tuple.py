import mipx
from mipx.types import TupleDict


def test_key_pattern_set():
    model = mipx.Model(solver_id="GUROBI")
    x: TupleDict[int, int] = model.addVars(1, 2)
    s = x.keyset("-", "*")
    assert len(s) == 2
    y: TupleDict[int, int] = model.addVars(3, 2)
    z = model.addVars(10)
    res = y.key_pattern_set("-", "*")
    res1 = y.keyset("-", "*")
    # res = z.key_pattern_set("*")
    status = model.optimize()
    assert mipx.success(status)
    print(model.WallTime, "ms")


if __name__ == "__main__":
    test_key_pattern_set()
