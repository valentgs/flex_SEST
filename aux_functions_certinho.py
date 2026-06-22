import os
import pandas as pd
import matplotlib.pyplot as plt
import pandapower as pp
import numpy as np  

def load_data_to_variables():
    # Get the directory where the current Python script is located
    script_path = os.path.abspath(__file__)
    directory = os.path.dirname(script_path)

    # List all CSV files in the directory
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    load_data = {}
    loco = [2.909, 2.741, 2.686, 2.63, 2.596, 2.518, 2.462, 2.63, 2.976, 2.976,3.133, 3.245, 3.301, 3.402, 3.301, 3.301, 3.267, 3.133, 3.211, 3.625,3.715, 3.625, 3.581, 3.301]

    # Manually defining load data for each asset
    load_data['asset_02.csv'] = {'Active Power': [0.05082, 0.08618, 0.03228, 0.0774, 0.04408, 0.06764, 
                                                  0.01276, 0.0774, 0.01648, 0.01648, 0.07034, 0.0801, 
                                                  0.03498, 0.03396, 0.03498, 0.03498, 0.00166, 0.07034, 
                                                  0.04678, 0.0525, 0.0407, 0.0525, 0.00938, 0.03498]}
    
    load_data['asset_03.csv'] = {'Active Power': [x * 0.0 for x in loco]} 
    
    load_data['asset_04.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_05.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_06.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    
    load_data['asset_07.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_08.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_09.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_10.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_11.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_12.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_13.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_14.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_15.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_16.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_17.csv'] = {'Active Power': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.1, 1.1, 1.0, 1.0, 1.0]}
    load_data['asset_18.csv'] = {'Active Power': [x * 0.005 for x in loco]}
    
    load_data['asset_19.csv'] = {'Active Power': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
    load_data['asset_20.csv'] = {'Active Power': [0.4, 0.2, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} 
    load_data['asset_21.csv'] = {'Active Power': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
    load_data['asset_22.csv'] = {'Active Power': [x * 0.005 for x in loco]} 
    
    load_data['asset_23.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_24.csv'] = {'Active Power': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.2, 2.3, 2.2, 2.2, 2.2, 2.0, 2.1, 2.4, 2.5, 2.5, 2.5, 2.4]}
    load_data['asset_25.csv'] = {'Active Power': [x * 0.005 for x in loco]}

    load_data['asset_26.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_27.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_28.csv'] = {'Active Power': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
    load_data['asset_29.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_30.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_31.csv'] = {'Active Power': [x * 0.0 for x in loco]}
    load_data['asset_32.csv'] = {'Active Power': [1.9, 1.9, 1.9, 1.9, 1.9, 1.9, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
    load_data['asset_33.csv'] = {'Active Power': [x * 0.005 for x in loco]}

        
    return load_data 


def create_empty_price_curves(nw):
    prices = []
    for _ in range(len(nw.bus)):
        prices.append([[], []])
    return prices


def print_curve(nld, prc, old):
    plt.figure()
    if nld is not None:
        plt.step(range(len(nld)), nld, marker='o', linestyle='-', where='post')
    if prc is not None:
        plt.step(range(len(prc)), prc, marker='o', linestyle='-', where='post')
    if old is not None:
        plt.step(range(len(old)), old, marker='o', linestyle='-', where='post')
    plt.title(f'')
    plt.xlabel('Time [h]')
    plt.ylabel('')
    plt.grid(True)


def calculate_cost_N(loads, sorted_files, nw, solars, new_loads):
    total_cost = 0.0
    prices = create_empty_price_curves(nw)
    # Run OPF for every hour to get prices and check the power flow    
    for hour in range(len(loads[sorted_files[0]]["Active Power"])):
        
        # Getting the load at hour h 
        for index, bus in nw.load.iterrows():
            nw.load.loc[nw.load['bus'] == nw.load['bus'][index], 'p_mw'] =   new_loads[sorted_files[index]]["Active Power"][hour]
            nw.load.loc[nw.load['bus'] == nw.load['bus'][index], 'q_mvar'] = new_loads[sorted_files[index]]["Reactive Power"][hour] 
        
        # Getting the pv curve at hour h
        if solars is not None:
            for index, s in enumerate(solars):
                nw.sgen.loc[nw.sgen['bus'] == nw.sgen['bus'][index], 'p_mw'] =   solars[index][hour]
                nw.sgen.loc[nw.sgen['bus'] == nw.sgen['bus'][index], 'q_mvar'] = 0.0

        pp.runopp(nw, verbose=False, tolerance_mva=1e-6)
        total_cost += nw.res_cost
        for i in range(len(nw.res_bus['lam_p'])):
            prices[i][0].append(nw.res_bus['lam_p'][i])
            prices[i][1].append(nw.res_bus['lam_q'][i])

    return total_cost, prices


def plot_prices_and_loads_over_time(iteration, prices, loads, network):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Plot loads on the top subplot
    ax1.set_ylabel('Load [MW]', color='tab:red')
    sorted_files = [file for file in loads.keys()]
    for index, bus in network.load.iterrows():
        ax1.step(range(len(loads[sorted_files[index]]['Active Power'])), 
                 loads[sorted_files[index]]['Active Power'], 
                 marker='o', linestyle='-', where='post', color='tab:red', alpha=0.5)
    ax1.tick_params(axis='y', labelcolor='tab:red')
    ax1.grid(True)
    ax1.set_ylim([0.0, 2.5])
    ax1.set_title('Load Over Time')

    # Plot prices on the bottom subplot
    ax2.set_xlabel('Time [h]')
    ax2.set_ylabel('Price [$]', color='tab:blue')
    if prices is not None:
        for i in range(len(prices)):
            ax2.step(range(len(prices[i][0])), prices[i][0], 
                     marker='o', linestyle='-', where='post', color='tab:blue', alpha=0.5)
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.grid(True)
    ax2.set_title('Prices Over Time')

    # Adjust layout and save the figure
    fig.tight_layout()
    plt.savefig(f'images/plot_asset_pov_{iteration}.png')
    plt.close()


def get_first_cost(nw, ld, sl, sf):
    total_cost = 0.0
    # Run OPF for every hour to get prices and check the power flow 
    new_loads = ld
    for hour in range(len(ld[sf[0]]["Active Power"])):
        
        # Sum up all active power of new loads for this specific hour
        total_active_power = sum(new_loads[sf[index]]["Active Power"][hour] for index in range(len(sf)))
        print(hour, total_active_power)

        # Getting the load at hour h 
        for index, bus in nw.load.iterrows():
            nw.load.loc[nw.load['bus'] == nw.load['bus'][index], 'p_mw'] =   new_loads[sf[index]]["Active Power"][hour]
            # nw.load.loc[nw.load['bus'] == nw.load['bus'][index], 'q_mvar'] = new_loads[sf[index]]["Reactive Power"][hour] 
        
        # Getting the pv curve at hour h
        if sl is not None:
            for index, s in enumerate(sl):
                nw.sgen.loc[nw.sgen['bus'] == nw.sgen['bus'][index], 'p_mw'] =   sl[index][hour]
                # nw.sgen.loc[nw.sgen['bus'] == nw.sgen['bus'][index], 'q_mvar'] = 0.0

        pp.runopp(nw, init="flat", verbose=False)
        total_cost += nw.res_cost
    return total_cost
    