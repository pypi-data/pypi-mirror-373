import mipx
import numpy as np


def test_max_flow():
    smf = mipx.maxflow.SimpleMaxFlow()
    start_nodes = np.array([0, 0, 0, 1, 1, 2, 2, 3, 3])
    end_nodes = np.array([1, 2, 3, 2, 4, 3, 4, 2, 4])
    capacities = np.array([20, 30, 10, 40, 30, 10, 20, 5, 20])
    smf.add_arcs_with_capacity(start_nodes, end_nodes, capacities)
    status = smf.optimize(0, 4)
    assert status == smf.OPTIMAL
    assert smf.optimal_flow() == 60


def test_min_cost_flow():
    smcf = mipx.mincost.SimpleMinCostFlow()
    start_nodes = np.array([0, 0, 1, 1, 1, 2, 2, 3, 4])
    end_nodes = np.array([1, 2, 2, 3, 4, 3, 4, 4, 2])
    capacities = np.array([15, 8, 20, 4, 10, 15, 4, 20, 5])
    unit_costs = np.array([4, 4, 2, 2, 6, 1, 3, 2, 3])
    supplies = [20, 0, 0, -5, -15]
    smcf.add_arcs_with_capacity_and_unit_cost(
        start_nodes, end_nodes, capacities, unit_costs
    )
    smcf.set_nodes_supplies(np.arange(0, len(supplies)), supplies)
    status = smcf.optimize()
    assert status == smcf.OPTIMAL
    assert smcf.optimal_cost() == 150
    print(smcf.maximun_flow())
