import mipx as gp
import numpy as np
import math


# 生成随机城市坐标
def generate_cities(n_cities, seed=42):
    np.random.seed(seed)
    return np.random.rand(n_cities, 2) * 100


# 计算欧几里得距离
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def solve_tsp(cities):
    n = len(cities)

    # 创建距离矩阵
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i, j] = euclidean_distance(cities[i], cities[j])

    # 创建模型
    model = gp.Model(solver_id="CPLEX")
    # model = gp.CpModel(solver_id="CP")
    model.Params.EnableOutput = True

    # 创建变量
    # x[i,j] = 1表示从城市i到城市j的边在路径中
    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                x[i, j] = model.addVar(vtype=gp.BINARY, name=f"x_{i}_{j}")

    # 创建辅助变量用于消除子回路
    u = model.addVars(n, vtype=gp.CONTINUOUS, lb=0, name="u")

    # 添加约束：每个城市恰好有一个出边
    for i in range(n):
        model.addConstr(model.sum(x[i, j] for j in range(n) if i != j) == 1)

    # 添加约束：每个城市恰好有一个入边
    for j in range(n):
        model.addConstr(model.sum(x[i, j] for i in range(n) if i != j) == 1)

    # 添加子回路消除约束（MTZ约束）
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1)

    # 设置参数

    # 设置目标函数：最小化总距离
    model.setObjective(
        model.sum(dist[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j),
    )
    # 求解模型
    status = model.optimize()

    # 提取解
    if status == gp.OPTIMAL:
        print(f"最优解找到，总距离: {model.ObjVal}")

        # 重建路径
        path = []
        current_city = 0
        visited = set([0])
        path.append(0)

        while len(visited) < n:
            for j in range(n):
                if j != current_city and x[current_city, j].X > 0.5:
                    current_city = j
                    path.append(j)
                    visited.add(j)
                    break

        print("最优路径:", path)

        # 进一步测试setHint
        # x 和 u
        var_list = []
        for var in x.values():
            var_list.append((var, var.X))
        for var in u.values():
            var_list.append((var, var.X))
        model.setHint(var_list)
        status = model.optimize()

        # 提取解
        if status == gp.OPTIMAL:
            print("第二次求解成功")
            print(f"最优解找到，总距离: {model.ObjVal}")

        return path, model.ObjVal
    else:
        print("未找到最优解")
        return None, None


# 示例使用
if __name__ == "__main__":
    # 生成10个城市的随机实例
    n_cities = 47
    cities = generate_cities(n_cities)

    # 求解TSP
    path, total_distance = solve_tsp(cities)

    # 打印结果
    # if path:
    #     print("\n最优路径顺序:")
    #     for i, city in enumerate(path):
    #         print(f"城市 {city}: ({cities[city, 0]:.2f}, {cities[city, 1]:.2f})")
    #
    #     print(f"\n总距离: {total_distance:.2f}")
