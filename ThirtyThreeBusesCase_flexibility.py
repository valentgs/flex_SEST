import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
import glob

from flexibility import flexibility
from iterative_plot import plot_everything
from aux_functions import load_data_to_variables, create_empty_price_curves, print_curve, plot_everything_pap
import os

os.system('clear')

##########################################################################################################
solar_curve  = []

bus_18 = [0.000, 0.000, 0.000, 0.000, 0.000, 0.005, 
          0.025, 0.065, 0.105, 0.120, 0.145, 0.150, 
          0.160, 0.155, 0.130, 0.100, 0.075, 0.025, 
          0.008, 0.000, 0.000, 0.000, 0.000, 0.000]

bus_22 = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
          0.000, 0.052, 0.100, 0.141, 0.173, 0.193,
          0.200, 0.193, 0.173, 0.141, 0.100, 0.052,
          0.000, 0.000, 0.000, 0.000, 0.000, 0.000]

bus_25 = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
          0.000, 0.010, 0.059, 0.103, 0.141, 0.169,
          0.186, 0.190, 0.181, 0.159, 0.127, 0.086,
          0.040, 0.000, 0.000, 0.000, 0.000, 0.000]

bus_33 = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
          0.000, 0.034, 0.079, 0.120, 0.152, 0.173,
          0.183, 0.181, 0.166, 0.140, 0.104, 0.061,
          0.014, 0.000, 0.000, 0.000, 0.000, 0.000]

solar_curve.append([1.0 * x for x in bus_18])
solar_curve.append([1.0 * x for x in bus_22])
solar_curve.append([1.0 * x for x in bus_25])
solar_curve.append([1.0 * x for x in bus_33])

# plt.step(range(24), solar_curve[0], label='Solar Generation (Bus 18)', marker='o', linestyle='-', where='pre', linewidth=3, color='green')
# plt.step(range(24), solar_curve[1], label='Solar Generation (Bus 22)', marker='o', linestyle='-', where='pre', linewidth=3, color='mediumseagreen')
# plt.step(range(24), solar_curve[2], label='Solar Generation (Bus 25)', marker='o', linestyle='-', where='pre', linewidth=3, color='limegreen')
# plt.step(range(24), solar_curve[3], label='Solar Generation (Bus 33)', marker='o', linestyle='-', where='pre', linewidth=3, color='forestgreen')
# plt.ylabel('Power (MW)')
# plt.grid(True)
# plt.xlim(0,23)
# plt.xlabel('Hour [h]')
# plt.ylabel('Power [MW]')
# plt.title('Solar Generation')
# plt.xticks(np.arange(0, 24, 1))
# plt.tight_layout(pad=0.0)
# plt.gcf().set_size_inches(8, 5)
# plt.legend(loc='upper left')
# plt.show()

##########################################################################################################
## CREATING AND ADAPTING THE NETWORK
net = pp.networks.case33bw()


# Create static generators (sgens) for each solar power curve
pp.create_sgen(net, bus=17, p_mw=0.0, q_mvar=0.0, in_service=True, name=f"Solar_1", controllable=False)
pp.create_sgen(net, bus=21, p_mw=0.0, q_mvar=0.0, in_service=True, name=f"Solar_2", controllable=False)
pp.create_sgen(net, bus=24, p_mw=0.0, q_mvar=0.0, in_service=True, name=f"Solar_3", controllable=False)
pp.create_sgen(net, bus=32, p_mw=0.0, q_mvar=0.0, in_service=True, name=f"Solar_4", controllable=False)

net.poly_cost.at[0, "cp0_eur"] = 240            ## constant term
net.poly_cost.at[0, "cp1_eur_per_mw"] = 80      ## linear term
net.poly_cost.at[0, "cp2_eur_per_mw2"] = 0.003  ## quadratic term

net.ext_grid.at[0, "max_p_mw"] = 4.0
for i in net.sgen.index:
    pp.create_poly_cost(
        net, 
        element=i, 
        et='sgen', 
        cp0_eur=210,          # fixed cost term
        cp1_eur_per_mw=10.26,   # linear cost term
        cp2_eur_per_mw2=0.0026   # quadratic cost term
    )

n_ch = 0.98
n_disch = 0.98
buses_with_flexible_loads = [20, 23] 

# Create a battery at bus N
batteries = {}
for bt in buses_with_flexible_loads:
    batteries[f'Battery {bt}'] = {'bf_min': -0.2, 
                                  'bf_max': +0.2,
                                  'soc_min': 10.0, 
                                  'soc_max': 90.0,
                                  'soc_now': 50.0, 
                                  'e_nom': 0.4}

#     neime = "Battery" + str(N)
#     pp.create_storage(net, bus=N, p_mw=0.0, q_mvar=0.0, min_p_mw=-1.5, max_p_mw=1.5, 
#                     min_q_mvar=-1.5, max_q_mvar=1.5, min_e_mwh=0.5, max_e_mwh=5.0,
#                     soc_percent=50.0, controllable=True, name=neime)


# ##########################################################################################################


# Initialize plot
fig, axs = plt.subplots(3, 1, figsize=(13, 10))

total_cost = 0.0
prices = create_empty_price_curves(net)
files = glob.glob("asset_*.csv")
sorted_files = sorted(files, key=lambda x: int(x.split('_')[1].split('.')[0]))
ld_day = load_data_to_variables()


h, sc, lc, oc, tc, flexibility_results, p_bat, bat_socs, dump = [], [], [], [], [], [], [], [], []
total_load, total_flex, total_dumped, total_generated, total_ren = 0.0, 0.0, 0.0, 0.0, 0.0
for K in range(24):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! DEBUGGING SESSION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("Hour:", K)
    h.append(K)

    fl, nfl = [], []
    for index, bus in net.load.iterrows():
        if net.load['bus'][index] in buses_with_flexible_loads:
            fl.append(ld_day[sorted_files[index]]["Active Power"][K])
        else:
            nfl.append(ld_day[sorted_files[index]]["Active Power"][K])
        net.load.loc[net.load['bus'] == net.load['bus'][index], 'p_mw']  = ld_day[sorted_files[index]]["Active Power"][K] 
        net.load.loc[net.load['bus'] == net.load['bus'][index], 'q_mvar'] = 0.0 
        
    
    for index, bus in net.sgen.iterrows():
        net.sgen.loc[net.sgen.bus == net.sgen['bus'][index], 'p_mw']   = solar_curve[index][K]

    pp.runopp(net, verbose=False)
    prices_load = []

    for index, load in net.load.iterrows():
        if load['bus'] in buses_with_flexible_loads:
            prices_load.append(net.res_bus.at[load['bus'], 'lam_p'])
    prices_load = np.array([x + 0.0 for x in prices_load])
    print(prices_load)

    L_max = np.array(fl)
    L_non_flex = np.array(nfl)

    gen_ren = np.array([solar_curve[i][K] for i in range(len(solar_curve))])
    gen_n_ren = np.array(np.array([net.res_ext_grid.p_mw.sum()]))
    
    dt = 1
    
    print(batteries)
    l_flex, char_flex, disc_flex, soc_flex, dumped_flex = flexibility(L_max, np.array(prices_load), gen_ren, batteries, n_ch, n_disch, dt, 200, 50)
    
    # print("Bus prices (λ_p) in EUR/MWh:")
    # for i, price in enumerate(net.res_bus.lam_p):
    #     print(f"Bus {i}: {1000*price:.4f}")
    
    total_generated += sum(gen_ren) + sum(gen_n_ren)
    total_ren       += sum(gen_ren)
    total_load      += sum(L_max)
    total_flex      += sum(l_flex)
    total_dumped    += sum(dumped_flex)

    print(f"Hour: {K};")
    # print("Solar Generators: \n", net.res_sgen)
    print("Solar Generators (sum): \n", net.res_sgen.p_mw.sum())
    # print("Generators: \n", net.res_gen)
    print("External Grid: \n", net.res_ext_grid)
    # print("Loads: \n", net.res_load)
    print("Loads (sum): \n", net.res_load.p_mw.sum())
    # print("Storage: \n", net.res_storage)
    print(f"Load Max: ({', '.join(f'{x:.2f}' for x in L_max)});")
    print(f"Price LD: ({', '.join(f'{x:.4f}' for x in prices_load)});")
    print(f"Generation Renewable: {gen_ren};")
    print(f"Generation Non-Renewable: {gen_n_ren};")
    print(f"Flexible Load: {', '.join(f'{x:.2f}' for x in l_flex)}")
    print(f"Flexible Discharge: {', '.join(f'{x:.2f}' for x in disc_flex)};")
    print(f"Flexible Charging: {', '.join(f'{x:.2f}' for x in char_flex)};")
    print(f"Flexible SOC: {', '.join(f'{x:.2f}' for x in soc_flex)};")
    print(f"Dumped Energy: {', '.join(f'{x:.2f}' for x in dumped_flex)};")
    
    # for i, bt in enumerate(net.storage.index):
    #     net.storage.at[bt, 'soc_percent'] = soc_flex[i]
    bat_flex = char_flex - disc_flex
    p_bat.append(bat_flex)
    bat_socs.append(soc_flex)
    dump.append(dumped_flex)
    flexibility_results.append(l_flex)
    lc.append(fl)

    # update_plot(fig, axs, h, sc, hoc, oc, tc, flexibility_results, p_bat, bat_socs)

plot_everything_pap(fig, axs, h, None, lc, flexibility_results, p_bat, bat_socs, dump, buses_with_flexible_loads)


print("----------------------------------- Final Results -----------------------------------")
print("Total Load: ", total_load)
print("Total Flex: ", total_flex)
print("Percentage of energy delivery: ", total_flex * 100/ total_load)
print("Total Generated (R + NR): ", total_generated)
print("Total Generated (R): ", total_ren)
print("Total Generated (NR): ", total_generated - total_ren)
print("Total Dumped: ", total_dumped)
print("Percentage of energy dumped: ", total_dumped * 100/ total_generated)
print("Final SoCs: ", soc_flex)

print("-------------------------------------------------------------------------------------")
# plot_everything(fig, axs, hours, solar_curve, load_curve, flexibility_results, p_bat, bat_socs, dumped):

