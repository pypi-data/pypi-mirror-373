## Python (Mixed-Integer Linear Programming Constraint Programming) Optimization Tools

Provide a same interface

`scip`,`sat`,`cplex`,`cbc`,`clp`,`glpk`,`cplex_cp`,...

### Simple Examples

```python
import mipx

model = mipx.Model(solver_id="SAT", name="test_model")
# model = mipx.CpModel()
model.Params.EnableOutput = False
model.Params.Precision = 1e-6
x = model.addVar(ub=10, vtype=mipx.INTEGER, name="x")
x1 = model.addVar(ub=10.1, vtype=mipx.INTEGER, name="x1")
y = model.addVar(ub=5, name="y")
z = model.addVar(ub=10, vtype=mipx.BINARY, name="z")
# ms = model.addVars([1, 2, 3], name='m')
# ms = model.addVars(4, name='m')
z = model.sum([x, y])
model.addConstr(z >= 15)
model.setObjective(y)
model.addKpi(z, "z")
model.addKpi(z + 40 + y, "z1")
# model.removeKpi("z")
print(model.name)
print(model.numOfKpis)
print("numvars:", model.numVars(mipx.INTEGER))
print("", model.numConstraints())
# print("numvars:", model.numVars())
model.statistics()
status = model.optimize()
if status == mipx.OptimizationStatus.OPTIMAL:
    print("objective is ", model.ObjVal)
    print(model.valueExpression(z + 4))
    print(y.X)
    mipx.debugVar(x)
    model.reportKpis()
    print(model.kpiByName("z"))
    print(model.kpiValueByName("z1"))
```
