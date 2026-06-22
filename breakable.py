import cvxpy as cp
import numpy as np
import matplotlib.pyplot as plt

# T = 24 
# p_i =   np.array([9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 9, 9, 7, 9, 9, 6, 9, 9, 5, 9, 9, 9, 9, 9])  # Price vector
# ell_i = np.array([0, 2, 4, 6, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # Original load curve

def breakload(T, p_i, ell_i, plot_initial=False, plot_final=False, print_initial=False, print_final=False):
    p_i, ell_i = np.array(p_i), np.array(ell_i)

    # Print inital costs
    if(print_initial):
        print("Original cost", p_i @ ell_i)

    # Plot initial curves
    if(plot_initial):
        fig, ax1 = plt.subplots()
        color = 'black'
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Load', color=color)
        ax1.step(range(T), ell_i, label="Original curve", marker='.', where='post', color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_xlim([0, 23])
        ax1.set_ylim([-.5, 20])
        ax1.set_xticks(range(0, 24))
        ax1.grid(True)
        ax1.set_yticks(range(0, 21, 2))
        
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:red'
        ax2.set_ylabel('Price', color=color)  # we already handled the x-label with ax1
        ax2.step(range(T), p_i, label="Price curve", marker='.', where='post', color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_xlim([0, 23])
        ax2.set_ylim([-0.25, 10])
        ax2.set_xticks(range(0, 24))
        
        
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.title('Load and Price curve before optimization')
        fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
        plt.show()

    # Find non-zero values in the original load curve
    non_zero_indices = np.where(ell_i != 0)[0]
    non_zero_values = ell_i[non_zero_indices]

    # Decision variables
    ell_i_prime = cp.Variable(T)  # Reshuffled load curve
    z = cp.Variable((T, len(non_zero_values)), boolean=True)  # Reshuffling indicators

    # Constraints
    constraints = []

    # 1. Reshuffling constraint: Link ell_i_prime with non-zero values of ell_i
    for t in range(T):
        constraints.append(ell_i_prime[t] == cp.sum(z[t, :] @ non_zero_values))

    # 2. Each non-zero value must be assigned exactly once
    for j in range(len(non_zero_values)):
        constraints.append(cp.sum(z[:, j]) == 1)

    # 3. Each time slot can have at most one assigned value
    for t in range(T):
        constraints.append(cp.sum(z[t, :]) <= 1)

    # Objective: Minimize cost
    objective = cp.Minimize(p_i @ ell_i_prime)

    # Problem definition
    problem = cp.Problem(objective, constraints)

    # Solve the problem
    problem.solve()

    if(print_final):
        if problem.status == "optimal":
            print("Optimal reshaped curve (ell_i_prime):", ell_i_prime.value)
            print("Optimal cost:", problem.value)
        else:
            print("Problem status: ", problem.status)
    
    # Plot resulting curves
    if(plot_final):
        fig, ax1 = plt.subplots()
        color = 'black'
        ax1.set_xlabel('Time [h]')
        ax1.set_ylabel('Load [W]', color=color)
        ax1.step(range(T), ell_i_prime.value, label="Curve after optimization", marker='.', where='post', color=color, )
        ax1.step(range(T), ell_i, label="Curve before optimization", marker='.', where='post', color='mediumblue', linestyle='--')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_xlim([0, 23])
        ax1.set_ylim([-.5, 20])
        ax1.set_xticks(range(0, 24))
        ax1.grid(True)
        ax1.set_yticks(range(0, 21, 2))
        
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:red'
        ax2.set_ylabel('Price [$]', color=color)  # we already handled the x-label with ax1
        ax2.step(range(T), p_i, label="Price curve", marker='.', where='post', color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_xlim([0, 23])
        ax2.set_ylim([-0.25, 10])
        ax2.set_xticks(range(0, 24))
        
        
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.title('Load and Price Curves Before/After Optimization')
        fig.legend(loc="center left", bbox_to_anchor=(0, 0.6), bbox_transform=ax2.transAxes)
        fig.tight_layout(pad=0.0)
        fig.set_size_inches(8, 5)
        plt.show()
    
    return ell_i_prime.value

# breakload(T, p_i, ell_i, plot_initial=False, plot_final=True, print_initial=True, print_final=True)