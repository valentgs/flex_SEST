import cvxpy as cp
import numpy as np
import matplotlib.pyplot as plt

# T = 24 
# p_i =   np.array([9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 9, 9, 7, 9, 9, 6, 9, 9, 5, 9, 9, 9, 9, 9])  # Price vector
# ell_i = np.array([0, 2, 4, 6, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # Original load curve

def shiftload(T, p_i, ell_i, plot_initial=False, plot_final=False, print_initial=False, print_final=False):
    p_i, ell_i = np.array(p_i), np.array(ell_i)
    
    # Print inital costs
    if(print_initial):
        print("Original cost", p_i @ ell_i)

    # Plot initial curves
    if(plot_initial):
        plt.step(range(T), ell_i, label="Original curve", marker='o', where='post')  # Marker
        plt.step(range(T), p_i, label="Price curve", marker='o', where='post')
        plt.title('Load curve before optimization')
        plt.xlabel('Time')
        plt.ylabel('')
        plt.legend()
        plt.show()

    # Decision variables
    delta_ell_i = cp.Variable(T)  # Shifted curve
    b_i = cp.Variable(T, boolean=True)  # Binary activation for shift

    # Constraints
    constraints = []

    # 1. Define all possible shifts of the original curve
    shifted_curves = np.array([np.roll(ell_i, j) for j in range(T)])

    # 2. Enforce that delta_ell_i is one of the shifted versions, activated by b_i
    constraints.append(delta_ell_i == shifted_curves.T @ b_i)

    # 3. Only one shift is active
    constraints.append(cp.sum(b_i) == 1)

    # 4. Non-negativity
    constraints.append(delta_ell_i >= 0)

    # Objective function
    objective = cp.Minimize(p_i @ delta_ell_i)

    # Problem definition
    problem = cp.Problem(objective, constraints)

    # Solve the problem
    problem.solve()

    # Output results
    if(print_final):
        if problem.status == "optimal":
            print("Original curve:    ", ell_i)
            print("Shifted curve:     ", np.round(delta_ell_i.value, 2))
            print("Objective value:   ", problem.value)
        else:
            print("Problem status: ", problem.status)
    
    # Plot resulting curves
    if(plot_final):
        fig, ax1 = plt.subplots()
        color = 'black'
        ax1.set_xlabel('Time [h]')
        ax1.set_ylabel('Load [W]', color=color)
        ax1.step(range(T), delta_ell_i.value, label="Curve after optimization", marker='.', where='post', color=color, )
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

    return delta_ell_i.value

# shiftload(T, p_i, ell_i, plot_initial=False, plot_final=True, print_initial=True, print_final=True)