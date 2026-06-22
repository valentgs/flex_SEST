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

bus_33 = [0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
          0.000, 0.034, 0.079, 0.120, 0.152, 0.173,
          0.183, 0.181, 0.166, 0.140, 0.104, 0.061,
          0.014, 0.000, 0.000, 0.000, 0.000, 0.000]

solar_curve.append([1.0 * x for x in bus_18])
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
net = pp.create_empty_network()

# Create buses
bus1 = pp.create_bus(net, vn_kv=12.66, name="Bus 1")
bus2 = pp.create_bus(net, vn_kv=12.66, name="Bus 2")
bus3 = pp.create_bus(net, vn_kv=12.66, name="Bus 3")

pp.create_ext_grid(net, bus2, vn_kv=12.66, max_p_mw=0.0, min_p_mw=-0.0, max_q_mvar=0.2, min_q_mvar=-0.2, slack=True)

# Create static generators (sgens) for each solar power curve
pp.create_sgen(net, bus=bus1, p_mw=1.0, q_mvar=0.0, in_service=True, name=f"Solar_2", controllable=False)
pp.create_sgen(net, bus=bus3, p_mw=1.0, q_mvar=0.0, in_service=True, name=f"Solar_3", controllable=False)

# Create loads at bus 1, 2, 3
pp.create_load(net, bus1, p_mw=0.0, name="Load 1")
pp.create_load(net, bus2, p_mw=0.0, name="Load 2")
pp.create_load(net, bus3, p_mw=0.0, name="Load 3")

# Create lines connecting the buses
# Line 1-2: From Bus 1 to Bus 2 using `create_line_from_parameters`
pp.create_line_from_parameters(net, bus1, bus2, length_km=1, r_ohm_per_km=0.0922, x_ohm_per_km=0.0470, c_nf_per_km=0, max_i_ka=0.2, name="Line 1-2")
pp.create_line_from_parameters(net, bus2, bus3, length_km=1, r_ohm_per_km=0.0922, x_ohm_per_km=0.0470, c_nf_per_km=0, max_i_ka=0.2, name="Line 2-3")

n_ch = 0.98
n_disch = 0.98
buses_with_flexible_loads = [0, 2] 

# Create a battery at bus N
batteries = {}
for bt in buses_with_flexible_loads:
    batteries[f'Battery {bt}'] = {'bf_min': -1.5, 
                                  'bf_max': +1.5,
                                  'soc_min': 10.0, 
                                  'soc_max': 90.0,
                                  'soc_now': 90.0, 
                                  'e_nom': 0.4}

    neime = "Battery" + str(bt)
    pp.create_storage(net, bus=bt, p_mw=0.0, q_mvar=0.0, min_p_mw=-1.5, max_p_mw=1.5, 
                    min_q_mvar=-0.0, max_q_mvar=0.0, min_e_mwh=1, max_e_mwh=10,
                    soc_percent=10.0, controllable=True, name=neime)

print(net)
# ##########################################################################################################


# Initialize plot
fig, axs = plt.subplots(3, 1, figsize=(13, 10))

total_cost = 0.0
prices = create_empty_price_curves(net)
files = glob.glob("asset_*.csv")
sorted_files = sorted(files, key=lambda x: int(x.split('_')[1].split('.')[0]))
ld_day = load_data_to_variables()
selected_assets = ["asset_02.csv", "asset_02.csv", "asset_20.csv"]
slct_ld_day = {}
for ass in selected_assets:
    slct_ld_day[ass] = ld_day[ass]
print(slct_ld_day)

sorted_files = selected_assets

h, sc, lc, oc, tc, flexibility_results, p_bat, bat_socs, dump = [], [], [], [], [], [], [], [], []
total_load, total_flex, total_dumped, total_generated, total_ren = 0.0, 0.0, 0.0, 0.0, 0.0
for K in range(24):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! DEBUGGING SESSION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("Hour:", K)
    h.append(K)

    fl, nfl = [], []
    for index, bus in net.load.iterrows():
        if net.load['bus'][index] in buses_with_flexible_loads:
            fl.append(slct_ld_day[sorted_files[index]]["Active Power"][K])
        else:
            nfl.append(slct_ld_day[sorted_files[index]]["Active Power"][K])
        net.load.loc[net.load['bus'] == net.load['bus'][index], 'p_mw']  = slct_ld_day[sorted_files[index]]["Active Power"][K] 
        net.load.loc[net.load['bus'] == net.load['bus'][index], 'q_mvar'] = 0.0 
        
    
    for index, bus in net.sgen.iterrows():
        net.sgen.loc[net.sgen.bus == net.sgen['bus'][index], 'p_mw']   = solar_curve[index][K]

    # print(net.load)
    # print(net.sgen)
    

    pp.runopp(net, verbose=False)
    # print("GENERATORS", net.res_gen)
    # print("EXTERNAL GRID", net.res_ext_grid)
    # print("STORAGE", net.res_storage)
    
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
    l_flex, char_flex, disc_flex, soc_flex, dumped_flex = flexibility(L_max, np.array(prices_load), 
                                                                      gen_ren, batteries, n_ch, 
                                                                      n_disch, dt, 200.0, 50.0)
    
    # print("Bus prices (λ_p) in EUR/MWh:")
    # for i, price in enumerate(net.res_bus.lam_p):
    #     print(f"Bus {i}: {1000*price:.4f}")
    
    total_generated += sum(gen_ren) + sum(gen_n_ren)
    total_ren       += sum(gen_ren)
    total_load      += sum(L_max)
    total_flex      += sum(l_flex)
    total_dumped    += sum(dumped_flex)

    print(f"Hour: {K};")
    print("Solar Generators: \n", net.res_sgen)
    print("Solar Generators (sum): \n", net.res_sgen.p_mw.sum())
    print("Generators: \n", net.res_gen)
    print("External Grid: \n", net.res_ext_grid)
    print("Loads: \n", net.res_load)
    print("Loads (sum): \n", net.res_load.p_mw.sum())
    print("Storage: \n", net.res_storage)
    print(f"Load Max: ({', '.join(f'{x:.2f}' for x in L_max)});")
    print(f"Price LD: ({', '.join(f'{x:.4f}' for x in prices_load)});")
    print(f"Generation Renewable: {gen_ren};")
    print(f"Generation Non-Renewable: {gen_n_ren};")
    print(f"Flexible Load: {', '.join(f'{x:.2f}' for x in l_flex)}")
    print(f"Flexible Discharge: {', '.join(f'{x:.2f}' for x in disc_flex)};")
    print(f"Flexible Charging: {', '.join(f'{x:.2f}' for x in char_flex)};")
    print(f"Flexible SOC: {', '.join(f'{x:.2f}' for x in soc_flex)};")
    print(f"Dumped Energy: {', '.join(f'{x:.2f}' for x in dumped_flex)};")
    
    for i, bt in enumerate(net.storage.index):
        net.storage.at[bt, 'soc_percent'] = soc_flex[i]
    for bt in buses_with_flexible_loads:
        batteries[f'Battery {bt}']["soc_now"] = soc_flex[i]
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

