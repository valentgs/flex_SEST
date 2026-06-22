import cvxpy as cp
import numpy as np
import matplotlib.pyplot as plt
 
# ell_max = np.array([10.0, 50.0]) # np.array([11.85, 40.39]) 
# pl_i    = np.array([10.0,  2.0])  # Price vector for each load
# g_i     = np.array([20.0])  # Generation vector
# batt = {'Battery 1': {'bf_min': -15.0, 'bf_max': 20.0, 'soc_min': 10.0, 'soc_max': 90.0, 'soc_now': 45.0, 'e_nom': 100.0},
#         'Battery 2': {'bf_min': -35.0, 'bf_max': 40.0, 'soc_min': 10.0, 'soc_max': 90.0, 'soc_now': 45.0, 'e_nom': 100.0}}
# dt = 1.0 # hour

# ell_max = np.array([2.92, 3.37]) # np.array([11.85, 40.39]) 
# pl_i  = np.array([1.0015, 1.0017])  # Price vector for each load
# pb_i  = np.array([1.0015, 1.0017])
# g_i   = np.array([0.0])  # Generation vector
# batt = {'Battery 1': {'bf_min': -50.0, 'bf_max': 50.0, 'soc_min': 10.0, 'soc_max': 90.0, 'soc_now': 50.0, 'e_nom': 39.0},
#         'Battery 2': {'bf_min': -50.0, 'bf_max': 50.0, 'soc_min': 10.0, 'soc_max': 90.0, 'soc_now': 50.0, 'e_nom': 39.0}}
# dt = 1.0 # hour

def flexibility(ell_max, pl_i, gr, batts, nc, nd, delta_t, a1, a2): 
    # Define decision variable
    ell      = cp.Variable(len(pl_i))
    bf_dis   = cp.Variable(len(batts.values()))
    bf_cha   = cp.Variable(len(batts.values()))
    ebat_new = cp.Variable(len(batts.values()))
    dumped   = cp.Variable(len(batts.values()))

    # Define objective function
    print("pl_i", pl_i)
    c_deg = np.full(len(pl_i), 0.03)
    print("pl_i + c_deg", c_deg + pl_i)
    print("ell_max", ell_max)
    print("gr", gr)
    
    objective = cp.Minimize((c_deg + pl_i) @ (bf_cha + 10.0 * bf_dis) + a1 * pl_i @ (ell_max - ell) + a2 * pl_i @ dumped) 

    # Define constraints
    constraints = []
    constraints.append(cp.sum(gr) + cp.sum(bf_dis)*nd == cp.sum(ell) + cp.sum(bf_cha / nc) + cp.sum(dumped))
    constraints.append(ell >= 0)
    constraints.append(ell <= ell_max)
    for i, battery in enumerate(batts.values()):
        # print(i, battery)
        constraints.append(bf_cha[i] >= 0)
        constraints.append(bf_cha[i] <= battery['bf_max'])
        constraints.append(bf_dis[i] >= 0)
        constraints.append(bf_dis[i] <= -battery['bf_min'])
        constraints.append(ebat_new[i] == battery['e_nom'] * battery['soc_now'] / 100 + (bf_cha[i] - bf_dis[i]) * delta_t)
        constraints.append(ebat_new[i] >= battery['e_nom'] * battery['soc_min'] / 100)
        constraints.append(ebat_new[i] <= battery['e_nom'] * battery['soc_max'] / 100)
        
    constraints.append(dumped >= 0)
    # Solve problem
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.ECOS, verbose=False)

    # Print results
    if problem.status == cp.OPTIMAL:
        print("Problem solved successfully.")
        print(f"Optimal cost: {problem.value:.2f}")
        print(f"Optimal ell: {np.round(ell.value, 2)}")
        print(f"Optimal bf_dis: {np.round(bf_dis.value, 2)}")
        print(f"Optimal bf_cha:, {np.round(bf_cha.value, 2)}")
        print(f"Dumped Energy: {np.round(dumped.value, 2)}")
        print(f"New SOC: {np.round((ebat_new.value / battery['e_nom']) * 100, 2)}") 
        return ell.value, bf_cha.value, bf_dis.value, (ebat_new.value / battery['e_nom']) * 100, dumped.value
    else:
        print('Problem Failed:', problem.status)
        print('Solver error message:', problem.solver_stats)    
        return None

###########################################################################################################
# for g_i in range(0, 151, 10):
#     print("Generation:", g_i)
#     a, b, c, d, e = flexibility(ell_max, pl_i, g_i, 0, batt, 0.98, 0.98, dt, 50, 200)
#     print('---------------------------------')