import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

from breakable import breakload
from shiftable import shiftload
from modulatable import modulateload
from aux_functions_certinho import load_data_to_variables, create_empty_price_curves, calculate_cost_N, plot_prices_and_loads_over_time, get_first_cost


import time

start_time = time.perf_counter()

os.system('clear')

pv_bus = [0.000, 0.000, 0.000, 0.000, 0.000, 0.005, 0.025, 0.065, 0.105, 0.120, 0.145, 0.150, 0.160, 0.155, 0.130, 0.100, 0.075, 0.025, 0.008, 0.000, 0.000, 0.000, 0.000, 0.000]
solar_data = [pv_bus]

plt.figure(figsize=(8,4))
plt.step(range(len(pv_bus)), pv_bus, where='pre', linewidth=3)
plt.xlabel("Time [h]", fontsize=32)
plt.ylabel("PV Output [MW]", fontsize=32)
plt.title("Daily PV Generation Profile", fontsize=32)
plt.xlim(0, 23)
plt.xticks(range(len(pv_bus)), fontsize=32)
plt.yticks(fontsize=32) 
plt.ylim(0, max(pv_bus)*1.1)
plt.grid(True)
plt.show()

net = pp.networks.case33bw()

net.poly_cost.at[0, "cp0_eur"] = 100           ## constant term
net.poly_cost.at[0, "cp1_eur_per_mw"] = 40     ## linear term
net.poly_cost.at[0, "cp2_eur_per_mw2"] = 0.01  ## quadratic term

# print(net.poly_cost)
# print(net.gen)
# print(net.ext_grid)

net.ext_grid.at[0, 'max_p_mw'] = 10.0          ##
net.ext_grid.at[0, 'max_q_mvar'] = 2.5
net.ext_grid.at[0, 'min_q_mvar'] = -2.5

for index, row in net.load.iterrows():
    net.load.at[index, 'q_mvar'] = 0.0

pp.create_sgen(net, bus=17, p_mw=0, q_mvar=0, name="Solar Generation 18")
# print(net.sgen)
net.poly_cost.at[17, "cp0_eur"] = 210           ## constant term
net.poly_cost.at[17, "cp1_eur_per_mw"] = 10.26     ## linear term
net.poly_cost.at[17, "cp2_eur_per_mw2"] = 0.0026  ## quadratic term

# pp.create_sgen(net, bus=21, p_mw=0, q_mvar=0, name="Solar Generation 22")
# pp.create_sgen(net, bus=24, p_mw=0, q_mvar=0, name="Solar Generation 25")
# pp.create_sgen(net, bus=32, p_mw=0, q_mvar=0, name="Solar Generation 33")
# print(net.sgen)
# net.poly_cost.at[21, "cp0_eur"] = 210           ## constant term
# net.poly_cost.at[21, "cp1_eur_per_mw"] = 10.26     ## linear term
# net.poly_cost.at[21, "cp2_eur_per_mw2"] = 0.0026  ## quadratic term


total_cost = 0.0
prices = create_empty_price_curves(net)
files = glob.glob("asset_*.csv")
sorted_files = sorted(files, key=lambda x: int(x.split('_')[1].split('.')[0]))
data = load_data_to_variables()

buses = list(range(1, 33))
# print(buses)

# print(sorted_files)

# Define the load curves
load_data = {}
for ind, key in enumerate(sorted(data.keys())):
    # load_data[key] = {'Bus': buses[ind], 'Active Power': data[key]['Active Power'], 'Reactive Power': data[key]['Reactive Power'], 'Type': 'Inflexible'}
    load_data[key] = {'Bus': buses[ind], 'Active Power': data[key]['Active Power'], 'Type': 'Inflexible'}
    
    if key in ['asset_02.csv', 
               'asset_17.csv', 
               'asset_21.csv', 
               'asset_24.csv', 
               'asset_32.csv'
               ]:
        load_data[key]['Type'] = 'Modulatable'
    elif key in ['asset_19.csv', 
                 'asset_28.csv'
                 ]:
        load_data[key]['Type'] = 'Breakable'
    elif key in [
                'asset_20.csv'
                ]:
        load_data[key]['Type'] = 'Shiftable'
    
# print(load_data)

def schedule_N(nw, loads, solars):
    global opf_counter
    new_loads = loads
    for ld in loads:
        # print(ld)
        
        if new_loads[ld]['Type'] == 'Inflexible': 
            continue

        total_cost = 0.0
        prices = create_empty_price_curves(nw)

        # Get the bus in the network to which the load is connected
        bus_ld = int(nw.load.loc[nw.load['bus'] == loads[ld]['Bus'], 'bus'].values[0])
        
        # Run OPF for every hour to get prices and check the power flow    
        for hour in range(len(loads[ld]["Active Power"])):
            
            # Getting the load at hour h 
            for index, bus in nw.load.iterrows():
                nw.load.loc[nw.load['bus'] == nw.load['bus'][index], 'p_mw'] =   new_loads[sorted_files[index]]["Active Power"][hour]

            if solars is not None:
                for index, s in enumerate(solars):
                    nw.sgen.loc[nw.sgen['bus'] == nw.sgen['bus'][index], 'p_mw'] =   solars[index][hour]
                    nw.sgen.loc[nw.sgen['bus'] == nw.sgen['bus'][index], 'q_mvar'] = 0.0
            
            pp.runopp(nw, verbose=False, init="results", tolerance_mva=1e-4)
            opf_counter += 1
            # print(net.res_line.loading_percent)
            total_cost += nw.res_cost
            # print(nw.res_bus['lam_p'])
            for i in range(len(nw.res_bus['lam_p'])):
                prices[i][0].append(nw.res_bus['lam_p'][i])
        
        # Load Scheduling Part
        T = len(new_loads[ld]["Active Power"])
        p_before = new_loads[ld]["Active Power"]
        price_p_at_bus = prices[bus_ld][0]
        
        print(ld)
        if new_loads[ld]['Type'] == 'Breakable':
            p = breakload(T, price_p_at_bus, p_before)
            new_loads[ld]["Active Power"] = p
        elif new_loads[ld]['Type'] == 'Shiftable':
            p = shiftload(T, price_p_at_bus, p_before)
            new_loads[ld]["Active Power"] = p
        elif new_loads[ld]['Type'] == 'Modulatable':
            p = modulateload(T, price_p_at_bus, p_before, min_power=0.01, max_power=4.01, max_change=0.1)
            new_loads[ld]["Active Power"] = p
            
    return new_loads, nw, total_cost, prices


opf_counter = 0
tc = []
fc = get_first_cost(net, load_data, solar_data, sorted_files)
tc.append(fc)
plot_prices_and_loads_over_time(0, None, load_data, net)
print("First cost: ", fc)
for iterator in range(1, 21):
    nlc, nnw, ntc, npr = schedule_N(net, load_data, solar_data)
    load_data = nlc
    net = nnw
    tc.append(ntc)
    print(iterator, ntc)
    
    if (iterator % 1 == 0):
        # print(iterator, npr, nlc, nnw)
        plot_prices_and_loads_over_time(iterator, npr, nlc, nnw)

end_time = time.perf_counter()

print(f"Total execution time: {end_time - start_time:.4f} seconds")
print("Total OPF runs: ", opf_counter)
print("total iterations: ", len(tc))
print("iterations with OPF runs: ", iterator)

print(tc)
plt.plot(tc)
plt.xlabel('Iteration')
plt.xticks(range(21))
plt.xlim([-0.1, 21.1])
plt.ylabel('Total Cost [\$]')
plt.title('Total Cost Over Iterations')
plt.tight_layout(pad=0.0)
plt.gcf().set_size_inches(10, 6)
plt.show()
