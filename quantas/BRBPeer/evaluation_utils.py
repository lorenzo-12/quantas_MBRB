import pathlib 
import os
import numpy as np
import json
import math
import pandas as pd
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re
from matplotlib import animation
import time
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import distinctipy
import matplotlib.ticker as mticker
from PIL import Image

img_path = pathlib.Path(__file__).parent.parent.parent / "results_img" 

# base paths for the results
path_gw_n100_k6         = pathlib.Path(__file__).parent.parent.parent / "results" / "MA<x>" / "generalized_wheel" / "n100_k6" / "<alg>"
path_gwbc_n100_k6       = pathlib.Path(__file__).parent.parent.parent / "results" / "MA<x>" / "generalized_wheel_byz_center" / "n100_k6" / "<alg>"
path_mw_n99_k6          = pathlib.Path(__file__).parent.parent.parent / "results" / "MA<x>" / "multipartite_wheel" / "n99_k6" / "<alg>"
path_rg_n100_k6         = pathlib.Path(__file__).parent.parent.parent / "results" / "MA<x>" / "random_graph" / "n100_k6" / "<alg>"
path_rg_n100_k6_e500    = pathlib.Path(__file__).parent.parent.parent / "results" / "MA<x>" / "random_graph" / "n100_k6_e500" / "<alg>"
path_rg_n100_k6_e600    = pathlib.Path(__file__).parent.parent.parent / "results" / "MA<x>" / "random_graph" / "n100_k6_e600" / "<alg>"
path_rg_n100_k6_e700    = pathlib.Path(__file__).parent.parent.parent / "results" / "MA<x>" / "random_graph" / "n100_k6_e700" / "<alg>"
path_rgbhc_n100_k6      = pathlib.Path(__file__).parent.parent.parent / "results" / "MA<x>" / "random_graph_byz_high_conn" / "n100_k6" / "<alg>"
path_rgp_n100_k6        = pathlib.Path(__file__).parent.parent.parent / "results" / "MA<x>" / "random_graph_pruned" / "n100_k6" / "<alg>"

results_paths = {
    "generalized_wheel_n100_k6": path_gw_n100_k6,
    "generalized_wheel_byz_center_n100_k6": path_gwbc_n100_k6,
    "multi_wheel_n99_k6": path_mw_n99_k6,
    "random_graph_n100_k6": path_rg_n100_k6,
    "random_graph_pruned_n100_k6": path_rgp_n100_k6,
    "random_graph_n100_k6_e500": path_rg_n100_k6_e500,
    "random_graph_n100_k6_e600": path_rg_n100_k6_e600,
    "random_graph_n100_k6_e700": path_rg_n100_k6_e700,
    "random_graph_n100_k6_byz_high_conn": path_rgbhc_n100_k6
}



def get_name(s):
    return s.split("_n")[0]
    
def extract_info(s):
    n = -1
    k = -1
    t = -1
    d = -1
    if "_n" in s:
        match = re.search(r'_n(\d+)', s)
        if match:
            n = int(match.group(1))
    if "_k" in s:
        match = re.search(r'_k(\d+)', s)
        if match:
            k = int(match.group(1))
    if "_t" in s:
        match = re.search(r'_t(\d+)', s)
        if match:
            t = int(match.group(1))
    if "_d" in s:
        match = re.search(r'_d(\d+)', s)
        if match:
            d = int(match.group(1))
    return n, k, t, d

def compute_confidence_bounds(values):
    values = np.array(values)
    if np.isnan(values).any():
        print("Warning: NaN values detected in the input array.")
    count = np.sum(~np.isnan(values))  # no axis
    mean = np.nanmean(values)
    std = np.nanstd(values, ddof=1)
    error = 2 * (std / np.sqrt(count))
    lower = mean - error
    upper = mean + error
    return mean, lower, upper

    
# Extract the list of topology names (your dict values)
topology_labels = list(results_paths.keys())

def get_distinct_colors(n, pastel_factor=0.0, cmap_name='hsv'):
    cmap = plt.get_cmap(cmap_name)
    hues = np.linspace(0, 1, n, endpoint=False)
    base_colors = cmap(hues)[:, :3]
    
    if pastel_factor > 0:
        # blend each color with white
        white = np.ones_like(base_colors)
        base_colors = (1 - pastel_factor) * base_colors + pastel_factor * white

    print(base_colors)
    return [tuple(c) for c in base_colors]

colors_9_hex = ["#d03f72",
                "#ca5340",
                "#c98542",
                "#999a3e",
                "#57a95b",
                "#45b2c4",
                "#7278cb",
                "#b85abe",
                "#be6c90"
                ]

colors = [mcolors.to_rgb(c) for c in colors_9_hex]
#colors = get_distinct_colors(len(topology_labels),0.2)

# Create the color map
color_map = {label: colors[i] for i, label in enumerate(topology_labels)}

def getValues(file_path):
    DelNodes = []
    TimeTimes = []
    totalMsg = []
    with open(file_path, 'r') as file:
        data = json.load(file)
        ntest = len(data['tests'])
        for t in data['tests']:
            test = data['tests'][t]
            
            if test['avgDeliveryNodes'] is not None:
                DelNodes.append(int(test['avgDeliveryNodes']))
            else:
                DelNodes.append(0)
            if test['avgDeliveryTime'] is not None:
                TimeTimes.append(int(test['avgDeliveryTime']))
            else:
                TimeTimes.append(0)
            if test['totalMsgsSent'] is not None:
                totalMsg.append(int(test['totalMsgsSent']))
            else:
                totalMsg.append(0)
    return DelNodes, TimeTimes, totalMsg

data = {}
def get_data():
    for label, path in results_paths.items():
        data[label] = {}
        for ma in [1,2,3]:
            data[label][ma] = {}
            for alg in ["bracha", "opodis_1", "opodis_t+1", "opodis_2t+1"]:
                full_path = pathlib.Path(str(path).replace("<x>", str(ma)).replace("<alg>", alg))
                data[label][ma][alg] = {}
                files = list(full_path.glob("*.json"))
                for file in files:
                    tmp = str(file).replace(str(full_path)+"/","").replace(".json","").split("_")
                    t = int(tmp[0].replace("t",""))
                    d = int(tmp[1].replace("d",""))
                    x = data[label][ma][alg]
                    
                    if (t not in x):
                        x[t] = {}
                    if (d not in x[t]):
                        x[t][d] = { "del":[], "time": [], "msg": [] }
                        
                    DelNodes, DelTimes, totalMsg = getValues(file)
                    
                    x[t][d]["del"].append(compute_confidence_bounds(DelNodes))
                    x[t][d]["time"].append(compute_confidence_bounds(DelTimes))
                    x[t][d]["msg"].append(compute_confidence_bounds(totalMsg))
                         
get_data()
with open("results.json","w+") as f:
    json.dump(data,f,indent=4)



#-----------------------------------------------------------------------------------------------------------------------------
def plot_2D(data, ma, alg, t_fix: int = -1, d_fix: int = -1):
    
    lw = 4
    fs = 18
    
    k = 6
    
    title_delivery = f"avgDelNodes fixed"
    title_time = f"avgDelTime fixed"
    title_msg = f"avgMsgsSent fixed"
    if (t_fix != -1):
        title_delivery += f" t={t_fix}"
        title_time += f" t={t_fix}"
        title_msg += f" t={t_fix}"
        xlabel1 = "Message Adversary Power (d)"
    else:
        title_delivery += f" d={d_fix}"
        title_time += f" d={d_fix}"
        title_msg += f" d={d_fix}"
        xlabel1 = "Byzantine nodes (t)"
        
    ylabel_avgdelnodes = "AvgCorrectNodesDelivered"
    ylabel_avgdeltime = "AvgDeliveryTime"
    ylabel_totmsgsent = "totalMsgsSent"
    
    import matplotlib.pyplot as plt
    fig1, axs1 = plt.subplots(1, 1, figsize=(12,12),constrained_layout=True)
    
    x_d = [f"d={d}" for d in range(k)]
    x_t = [f"t={t}" for t in range(k)]
    
    epsilon = 0.005
    idx = 0
    
    if (t_fix != -1):
        x = np.arange(k - t_fix)
    else:
        x = np.arange(k - d_fix)
    
    # Subplot 1: avg delivery nodes 
    for topology in data.keys():
        """ if topology == "generalized_wheel_byz_center_n100_k6" or topology == "generalized_wheel_n100_k6":
            continue """
        y = []
        ci = []
        if (t_fix != -1):
            for d in range(k-t_fix):
                val = data[topology][ma][alg][t_fix][d]["del"]
                y.append(val[0][0])
                ci.append((val[0][1], val[0][2]))
                
            lower_bounds = [ci[i][0] for i in range(k-t_fix)]
            upper_bounds = [ci[i][1] for i in range(k-t_fix)]
            x_shifted = [i + idx * epsilon for i in range(k-t_fix)]  # Shift each line slightly
        else:
            for t in range(k-d_fix):
                val = data[topology][ma][alg][t][d_fix]["del"]
                y.append(val[0][0])
                ci.append((val[0][1], val[0][2]))
                
            lower_bounds = [ci[i][0] for i in range(k-d_fix)]
            upper_bounds = [ci[i][1] for i in range(k-d_fix)]
            x_shifted = [i + idx * epsilon for i in range(k-d_fix)]  # Shift each line slightly
        short_name = topology
        short_name = short_name.replace("multi_wheel","ml")
        short_name = short_name.replace("generalized_wheel_center","gwc").replace("generalized_wheel","gw")
        short_name = short_name.replace("diamond","d").replace("pasted_tree","pt")
        short_name = short_name.replace("random_graph_pruned","rg_pruned")
        short_name = short_name.replace("random_graph_n100_k6_byz_high_conn","rg_high_n100_k6")
        short_name = short_name.replace("random_graph","rg")
        short_name = short_name.replace("_n24_k4","").replace("_n100_k6","").replace("_n99_k6","")
        axs1.plot(x_shifted, y, marker='o', label=f"{short_name}", color=color_map[topology], linewidth=lw)
        axs1.fill_between(x_shifted, lower_bounds, upper_bounds, color=color_map[topology], alpha=0.3)
        idx += 1
    
    axs1.set_title(title_delivery, fontsize=fs)
    axs1.set_xlabel(xlabel1, fontsize=fs)
    axs1.set_ylabel(ylabel_avgdeltime, fontsize=fs)
    axs1.set_ylim(0,105)
    axs1.grid(True)
    axs1.set_xticks(x)
    if (t_fix != -1):
        axs1.set_xticklabels([f"d={d}" for d in range(k - t_fix)], fontsize=fs)
    else:
         axs1.set_xticklabels([f"t={t}" for t in range(k - d_fix)], fontsize=fs)
    #axs1.legend()
    plt.xticks(fontsize=fs)  # x-axis tick numbers
    plt.yticks(fontsize=fs)  # y-axis tick numbers
    #plt.legend(fontsize=fs, ncol=2)
    #plt.show()
    if (t_fix != -1):
        plt.savefig(img_path/f"t{t_fix}_MA{ma}_{alg}_delivery.jpg", dpi=100)
        plt.close()
    else:
        plt.savefig(img_path/f"d{d_fix}_MA{ma}_{alg}_delivery.jpg", dpi=100)
        plt.close()
    
    
    # Subplot 2: avg delivery time 
    fig1, axs1 = plt.subplots(1, 1, figsize=(12,12),constrained_layout=True)
    epsilon = 0.01
    idx = 0
    for topology in data.keys():
        """ if topology == "generalized_wheel_byz_center_n100_k6" or topology == "generalized_wheel_n100_k6":
            continue """
        y = []
        ci = []
        if (t_fix != -1):
            for d in range(k-t_fix):
                val = data[topology][ma][alg][t_fix][d]["time"]
                y.append(val[0][0])
                ci.append((val[0][1], val[0][2]))
                
            lower_bounds = [ci[i][0] for i in range(k-t_fix)]
            upper_bounds = [ci[i][1] for i in range(k-t_fix)]
            x_shifted = [i + idx * epsilon for i in range(k-t_fix)]  # Shift each line slightly
        else:
            for t in range(k-d_fix):
                val = data[topology][ma][alg][t][d_fix]["time"]
                y.append(val[0][0])
                ci.append((val[0][1], val[0][2]))
                
            lower_bounds = [ci[i][0] for i in range(k-d_fix)]
            upper_bounds = [ci[i][1] for i in range(k-d_fix)]
            x_shifted = [i + idx * epsilon for i in range(k-d_fix)]  # Shift each line slightly
            
        short_name = topology
        short_name = short_name.replace("multi_wheel","ml")
        short_name = short_name.replace("generalized_wheel_center","gwc").replace("generalized_wheel","gw")
        short_name = short_name.replace("diamond","d").replace("pasted_tree","pt")
        short_name = short_name.replace("random_graph_pruned","rg_pruned")
        short_name = short_name.replace("random_graph_n100_k6_byz_high_conn","rg_high_n100_k6")
        short_name = short_name.replace("random_graph","rg")
        short_name = short_name.replace("_n24_k4","").replace("_n100_k6","").replace("_n99_k6","")
        axs1.plot(x_shifted, y, marker='o', label=f"{short_name}", color=color_map[topology], linewidth=lw)
        axs1.fill_between(x_shifted, lower_bounds, upper_bounds, color=color_map[topology], alpha=0.3)
        idx += 1
    
    axs1.set_title(title_time, fontsize=fs)
    axs1.set_xlabel(xlabel1, fontsize=fs)
    axs1.set_ylabel(ylabel_avgdeltime, fontsize=fs)
    axs1.set_ylim(0,25)
    axs1.grid(True)
    axs1.set_xticks(x)
    if (t_fix != -1):
        axs1.set_xticklabels([f"d={d}" for d in range(k - t_fix)], fontsize=fs)
    else:
         axs1.set_xticklabels([f"t={t}" for t in range(k - d_fix)], fontsize=fs)
    #axs1.legend()
    plt.xticks(fontsize=fs)  # x-axis tick numbers
    plt.yticks(fontsize=fs)  # y-axis tick numbers
    #plt.legend(fontsize=fs, ncol=2)
    #plt.show()
    if (t_fix != -1):
        plt.savefig(img_path/f"t{t_fix}_MA{ma}_{alg}_time.jpg", dpi=100)
        plt.close()
    else:
        plt.savefig(img_path/f"d{d_fix}_MA{ma}_{alg}_time.jpg", dpi=100)
        plt.close()
    
    
    # Subplot 3: avg msgs sent 
    fig1, axs1 = plt.subplots(1, 1, figsize=(12,12),constrained_layout=True)
    scale = 1_000_000  # to convert to millions
    epsilon = 0.01
    idx = 0
    max_val = 0
    for topology in data.keys():
        """ if topology == "generalized_wheel_byz_center_n100_k6" or topology == "generalized_wheel_n100_k6":
            continue """
        y = []
        ci = []
        if (t_fix != -1):
            for d in range(k-t_fix):
                val = data[topology][ma][alg][t_fix][d]["msg"] 
                y.append(val[0][0] / scale)
                max_val = max(max_val,val[0][0] / scale)
                ci.append((val[0][1], val[0][2]))
                
            lower_bounds = [ci[i][0] for i in range(k-t_fix)]
            upper_bounds = [ci[i][1] for i in range(k-t_fix)]
            x_shifted = [i + idx * epsilon for i in range(k-t_fix)]  # Shift each line slightly
        else:
            for t in range(k-d_fix):
                val = data[topology][ma][alg][t][d_fix]["msg"] 
                y.append(val[0][0] / scale)
                max_val = max(max_val,val[0][0] / scale)
                ci.append((val[0][1], val[0][2]))
                
            lower_bounds = [ci[i][0] for i in range(k-d_fix)]
            upper_bounds = [ci[i][1] for i in range(k-d_fix)]
            x_shifted = [i + idx * epsilon for i in range(k-d_fix)]  # Shift each line slightly
        short_name = topology
        short_name = short_name.replace("multi_wheel","ml")
        short_name = short_name.replace("generalized_wheel_center","gwc").replace("generalized_wheel","gw")
        short_name = short_name.replace("diamond","d").replace("pasted_tree","pt")
        short_name = short_name.replace("random_graph_pruned","rg_pruned")
        short_name = short_name.replace("random_graph_n100_k6_byz_high_conn","rg_high_n100_k6")
        short_name = short_name.replace("random_graph","rg")
        short_name = short_name.replace("_n24_k4","").replace("_n100_k6","").replace("_n99_k6","")
        axs1.plot(x_shifted, y, marker='o', label=f"{short_name}", color=color_map[topology], linewidth=lw)
        axs1.fill_between(x_shifted, lower_bounds, upper_bounds, color=color_map[topology], alpha=0.3)
        idx += 1
    
    axs1.set_title(title_msg, fontsize=fs)
    axs1.set_xlabel(xlabel1, fontsize=fs)
    axs1.set_ylabel(f"{ylabel_avgdeltime} (Millions)", fontsize=fs)
    axs1.set_ylim(0,max_val*1.05)
    axs1.yaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=False))
    axs1.ticklabel_format(style='plain', axis='y')
    axs1.grid(True)
    axs1.set_xticks(x)
    if (t_fix != -1):
        axs1.set_xticklabels([f"d={d}" for d in range(k - t_fix)], fontsize=fs)
    else:
        axs1.set_xticklabels([f"t={t}" for t in range(k - d_fix)], fontsize=fs)
    #axs1.legend()
    plt.xticks(fontsize=fs)  # x-axis tick numbers
    plt.yticks(fontsize=fs)  # y-axis tick numbers
    #plt.legend(fontsize=fs, ncol=2)
    #plt.show()
    if (t_fix != -1):
        plt.savefig(img_path/f"t{t_fix}_MA{ma}_{alg}_msgs.jpg", dpi=100)
        plt.close()
    else:
        plt.savefig(img_path/f"d{d_fix}_MA{ma}_{alg}_msgs.jpg", dpi=100)
        plt.close()
#-----------------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------------
def plot_2D_together(data, ma, alg, t_fix:int = -1, d_fix: int = -1):
    
    lw = 4
    fs = 18
    
    k = 6
    
    title_delivery = f"avgDelNodes fixed"
    title_time = f"avgDelTime fixed"
    title_msg = f"avgMsgsSent fixed"
    if (t_fix != -1):
        title_delivery += f" t={t_fix}"
        title_time += f" t={t_fix}"
        title_msg += f" t={t_fix}"
        xlabel1 = "Message Adversary Power (d)"
    else:
        title_delivery += f" d={d_fix}"
        title_time += f" d={d_fix}"
        title_msg += f" d={d_fix}"
        xlabel1 = "Byzantine nodes (t)"
    ylabel_avgdelnodes = "AvgCorrectNodesDelivered"
    ylabel_avgdeltime = "AvgDeliveryTime"
    ylabel_totmsgsent = "totalMsgsSent"
    
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(36,12),constrained_layout=True)
    
    x_d = [f"d={d}" for d in range(k)]
    x_t = [f"t={t}" for t in range(k)]
    
    epsilon = 0.005
    idx = 0
    
    if (t_fix != -1):
        x = np.arange(k - t_fix)
    else:
        x = np.arange(k - d_fix)
    
    # Subplot 1: avg delivery nodes 
    idx = 0
    for topology in data.keys():
        y = []
        ci = []
        if (t_fix != -1):
            for d in range(k - t_fix):
                val = data[topology][ma][alg][t_fix][d]["del"]
                y.append(val[0][0])
                ci.append((val[0][1], val[0][2]))

            lower_bounds = [ci[i][0] for i in range(k - t_fix)]
            upper_bounds = [ci[i][1] for i in range(k - t_fix)]
            x_shifted = [i + idx * epsilon for i in range(k - t_fix)]
        else:
            for t in range(k - d_fix):
                val = data[topology][ma][alg][t][d_fix]["del"]
                y.append(val[0][0])
                ci.append((val[0][1], val[0][2]))

            lower_bounds = [ci[i][0] for i in range(k - d_fix)]
            upper_bounds = [ci[i][1] for i in range(k - d_fix)]
            x_shifted = [i + idx * epsilon for i in range(k - d_fix)]

        short_name = topology
        short_name = short_name.replace("multi_wheel", "ml") \
                               .replace("generalized_wheel_center", "gwc") \
                               .replace("generalized_wheel", "gw") \
                               .replace("diamond", "d") \
                               .replace("pasted_tree", "pt") \
                               .replace("random_graph_pruned", "rg_pruned") \
                               .replace("random_graph_n100_k6_byz_high_conn", "rg_high_n100_k6") \
                               .replace("random_graph", "rg") \
                               .replace("_n24_k4", "").replace("_n100_k6", "").replace("_n99_k6", "")

        axs[0].plot(x_shifted, y, marker='o', label=short_name, color=color_map[topology], linewidth=lw)
        axs[0].fill_between(x_shifted, lower_bounds, upper_bounds, color=color_map[topology], alpha=0.3)
        idx += 1

    axs[0].set_title(title_delivery, fontsize=fs)
    axs[0].set_xlabel(xlabel1, fontsize=fs)
    axs[0].set_ylabel(ylabel_avgdelnodes, fontsize=fs)
    axs[0].set_ylim(0, 105)
    axs[0].grid(True)
    axs[0].set_xticks(x)
    if (t_fix != -1):
        axs[0].set_xticklabels([f"d={d}" for d in range(k - t_fix)], fontsize=fs)
    else:
        axs[0].set_xticklabels([f"t={t}" for t in range(k - d_fix)], fontsize=fs)
    axs[0].tick_params(labelsize=fs)
    
    
    # Subplot 2: avg delivery time 
    epsilon = 0.005
    idx = 0
    for topology in data.keys():
        y = []
        ci = []
        if (t_fix != -1):
            for d in range(k - t_fix):
                val = data[topology][ma][alg][t_fix][d]["time"]
                y.append(val[0][0])
                ci.append((val[0][1], val[0][2]))

            lower_bounds = [ci[i][0] for i in range(k - t_fix)]
            upper_bounds = [ci[i][1] for i in range(k - t_fix)]
            x_shifted = [i + idx * epsilon for i in range(k - t_fix)]
        else:
            for t in range(k - d_fix):
                val = data[topology][ma][alg][t][d_fix]["time"]
                y.append(val[0][0])
                ci.append((val[0][1], val[0][2]))

            lower_bounds = [ci[i][0] for i in range(k - d_fix)]
            upper_bounds = [ci[i][1] for i in range(k - d_fix)]
            x_shifted = [i + idx * epsilon for i in range(k - d_fix)]

        short_name = topology.replace("multi_wheel", "ml") \
                             .replace("generalized_wheel_center", "gwc") \
                             .replace("generalized_wheel", "gw") \
                             .replace("diamond", "d") \
                             .replace("pasted_tree", "pt") \
                             .replace("random_graph_pruned", "rg_pruned") \
                             .replace("random_graph_n100_k6_byz_high_conn", "rg_high_n100_k6") \
                             .replace("random_graph", "rg") \
                             .replace("_n24_k4", "").replace("_n100_k6", "").replace("_n99_k6", "")

        axs[1].plot(x_shifted, y, marker='o', label=short_name, color=color_map[topology], linewidth=lw)
        axs[1].fill_between(x_shifted, lower_bounds, upper_bounds, color=color_map[topology], alpha=0.3)
        idx += 1

    axs[1].set_title(title_time, fontsize=fs)
    axs[1].set_xlabel(xlabel1, fontsize=fs)
    axs[1].set_ylabel(ylabel_avgdeltime, fontsize=fs)
    axs[1].set_ylim(0, 27)
    axs[1].grid(True)
    axs[1].set_xticks(x)
    if (t_fix != -1):
        axs[1].set_xticklabels([f"d={d}" for d in range(k - t_fix)], fontsize=fs)
    else:
        axs[1].set_xticklabels([f"t={t}" for t in range(k - d_fix)], fontsize=fs)
    axs[1].tick_params(labelsize=fs)
    
    
    # Subplot 3: avg msgs sent 
    epsilon = 0.005
    scale = 1_000_000  # millions
    idx = 0
    max_val = 0
    for topology in data.keys():
        y = []
        ci = []
        if (t_fix != -1):
            for d in range(k - t_fix):
                val = data[topology][ma][alg][t_fix][d]["msg"]
                y_val = val[0][0] / scale
                y.append(y_val)
                max_val = max(max_val, y_val)
                ci.append((val[0][1] / scale, val[0][2] / scale))

            lower_bounds = [ci[i][0] for i in range(k - t_fix)]
            upper_bounds = [ci[i][1] for i in range(k - t_fix)]
            x_shifted = [i + idx * epsilon for i in range(k - t_fix)]
        else:
            for t in range(k - d_fix):
                val = data[topology][ma][alg][t][d_fix]["msg"]
                y_val = val[0][0] / scale
                y.append(y_val)
                max_val = max(max_val, y_val)
                ci.append((val[0][1] / scale, val[0][2] / scale))

            lower_bounds = [ci[i][0] for i in range(k - d_fix)]
            upper_bounds = [ci[i][1] for i in range(k - d_fix)]
            x_shifted = [i + idx * epsilon for i in range(k - d_fix)]

        short_name = topology.replace("multi_wheel", "ml") \
                             .replace("generalized_wheel_center", "gwc") \
                             .replace("generalized_wheel", "gw") \
                             .replace("diamond", "d") \
                             .replace("pasted_tree", "pt") \
                             .replace("random_graph_pruned", "rg_pruned") \
                             .replace("random_graph_n100_k6_byz_high_conn", "rg_high_n100_k6") \
                             .replace("random_graph", "rg") \
                             .replace("_n24_k4", "").replace("_n100_k6", "").replace("_n99_k6", "")

        axs[2].plot(x_shifted, y, marker='o', label=short_name, color=color_map[topology], linewidth=lw)
        axs[2].fill_between(x_shifted, lower_bounds, upper_bounds, color=color_map[topology], alpha=0.3)
        idx += 1

    axs[2].set_title(title_msg, fontsize=fs)
    axs[2].set_xlabel(xlabel1, fontsize=fs)
    axs[2].set_ylabel(f"{ylabel_totmsgsent} (Millions)", fontsize=fs)
    axs[2].set_ylim(0, max_val * 1.05)
    axs[2].yaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=False))
    axs[2].ticklabel_format(style='plain', axis='y')
    axs[2].grid(True)
    axs[2].set_xticks(x)
    if (t_fix != -1):
        axs[2].set_xticklabels([f"d={d}" for d in range(k - t_fix)], fontsize=fs)
    else:
        axs[2].set_xticklabels([f"t={t}" for t in range(k - d_fix)], fontsize=fs)
    axs[2].tick_params(labelsize=fs)

    # Add legend once for the whole figure
    #handles, labels = axs[0].get_legend_handles_labels()
    #fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=fs)

    if (t_fix != -1):
        plt.savefig(img_path / f"t{t_fix}_MA{ma}_{alg}_combined.jpg", dpi=100)
        plt.close()
    else:
        plt.savefig(img_path / f"d{d_fix}_MA{ma}_{alg}_combined.jpg", dpi=100)
        plt.close()
#-----------------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------------
def get_3D_matrix(data, ma, alg, topology):
    k = 6    
    short_name = topology.replace("multi_wheel", "ml") \
                            .replace("generalized_wheel_center", "gwc") \
                            .replace("generalized_wheel", "gw") \
                            .replace("diamond", "d") \
                            .replace("pasted_tree", "pt") \
                            .replace("random_graph_pruned", "rg_pruned") \
                            .replace("random_graph_n100_k6_byz_high_conn", "rg_high_n100_k6") \
                            .replace("random_graph", "rg") \
                            .replace("_n24_k4", "").replace("_n100_k6", "").replace("_n99_k6", "")
                            
    d_del = [[None for i in range(k)] for j in range(k)]
    d_time = [[None for i in range(k)] for j in range(k)]
    d_msg = [[None for i in range(k)] for j in range(k)]
    
    matrix = data[topology][ma][alg]
    for t in sorted(matrix.keys()):
        for d in sorted(matrix[t]):
            d_del[t][d] = matrix[t][d]["del"][0][0]
            d_time[t][d] = matrix[t][d]["time"][0][0]
            d_msg[t][d] = matrix[t][d]["msg"][0][0] / 1_000_000
            
    d_del = np.asarray(d_del, dtype=float)
    d_time = np.asarray(d_time, dtype=float)
    d_msg = np.asarray(d_msg, dtype=float)  
    
    return d_del, d_time, d_msg, short_name
        
#-----------------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------------
def trim_manual(img_path, top=0, bottom=0, left=0, right=0):
    """
    Crop fixed pixels from each side of the image.
    Example: top=5 removes 5 rows from the top.
    """
    img = Image.open(img_path)
    w, h = img.size

    # compute crop box (left, upper, right, lower)
    crop_box = (
        left,                  # new left
        top,                   # new top
        w - right,             # new right
        h - bottom             # new bottom
    )

    cropped = img.crop(crop_box)
    cropped.save(img_path)
#-----------------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------------
def plot_3D(data, ma, alg, plot_type):
    # Create t and d axes (0 to 5)
    fs = 28
    k = 6
    t = np.arange(k)
    d = np.arange(k)
    T, D = np.meshgrid(t, d, indexing="ij")  # Align axes with M[t, d]

    # Build the plot
    fig = plt.figure(figsize=(8,8), constrained_layout=True)
    ax = fig.add_subplot(111, projection='3d')
    max_val = 0
    for topology in data.keys():
        M_del, M_time, M_msg, short_name = get_3D_matrix(data, ma, alg, topology)
        if (plot_type == "del"):
            M = M_del 
            zlable = "Avg Delivery Nodes \n(percentage)"
        if (plot_type == "time"):
            M = M_time
            zlable = "Avg Delivery Time \n(steps)"
        if (plot_type == "msg"):
            M = M_msg
            zlable = "Total Msgs Sent \n(millions)"
        
        tmp_val = []
        for row in M:
            tmp_val.append(max(row))
        local_max = np.nanmax(M)
        max_val = max(max_val, local_max)
        if (plot_type == "time"):
            max_val = 20

        # ensure M is a NumPy array with 2D shape
        M = np.asarray(M, dtype=float)
        #ax.plot_surface(T, D, M, shade=False, alpha=0.8, label=short_name, color=color_map[topology])
        Z = np.ma.masked_invalid(M)
        ax.plot_surface(T, D, Z, shade=False, alpha=0.8, label=short_name, color=color_map[topology])
        
    ax.set_xlabel('Byzantine (t)', labelpad=20, fontsize=fs)
    ax.set_ylabel('Message adversary (d)', labelpad=20, fontsize=fs)
    ax.set_zlabel(zlable, labelpad=25, fontsize=fs)
    ax.set_title(f"MA{ma} - {alg.replace("opodis","Albouy")}", y=0.9, fontsize=fs)
    ax.tick_params(axis='x', which='major', labelsize=20)
    ax.tick_params(axis='y', which='major', labelsize=20)
    ax.tick_params(axis='z', which='major', labelsize=20)
    
    # Set axes limits
    from matplotlib.ticker import MultipleLocator
    ax.set_xlim(0, k-1)
    ax.set_ylim(0, k-1)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_zlim(0, max_val*1.1)
    ax.view_init(elev=10., azim=45)
    ax.set_position([0.06, 0.02, 0.90, 0.94])
    
    out_name = f"{plot_type}_MA{ma}_{alg.replace("opodis","Albouy")}.png"
    img_path = os.path.join("results_img_3d", out_name)
    plt.savefig(img_path, dpi=120, bbox_inches='tight', pad_inches=1)
    plt.close()
    trim_manual(img_path, top=120, bottom=120, left=10, right=40)
    
#-----------------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------------
# Legend built from color_map
f = lambda m, c: plt.plot([], [], marker=m, color=c, ls='none', markersize=12)[0]
handles = []
labels = []
for lbl, rgb in color_map.items():
    handles.append(f('s', rgb))
    labels.append(lbl)
legend = plt.legend(handles, labels, loc=3, framealpha=1, frameon=True, ncol=3, columnspacing=1.0, handletextpad=0.5, borderaxespad=0.5)

def export_legend(legend, filename="results_img/legend.png", expand=[-5, -5, 5, 5]):
    fig = legend.figure
    fig.canvas.draw()
    bbox = legend.get_window_extent()
    bbox = bbox.from_extents(*(bbox.extents + np.array(expand)))
    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi=300, bbox_inches=bbox)

export_legend(legend)
#-----------------------------------------------------------------------------------------------------------------------------

""" a,b,c,d = get_3D_matrix(data,1,"opodis_2t+1","multi_wheel_n99_k6")
print(a) """

for ma in [1,2,3]:
    for alg in ["bracha","opodis_1", "opodis_t+1","opodis_2t+1"]:
        for plot_type in ["del","time","msg"]:
            plot_3D(data,ma,alg,plot_type)

""" for d in range(6):
    plot_2D_together(data,1,"bracha",d_fix=d)
    plot_2D_together(data,1,"opodis_1",d_fix=d)
    plot_2D_together(data,1,"opodis_2t+1",d_fix=d)

    plot_2D_together(data,2,"bracha",d_fix=d)
    plot_2D_together(data,2,"opodis_1",d_fix=d)
    plot_2D_together(data,2,"opodis_2t+1",d_fix=d)

    plot_2D_together(data,3,"bracha",d_fix=d)
    plot_2D_together(data,3,"opodis_1",d_fix=d)
    plot_2D_together(data,3,"opodis_2t+1",d_fix=d) """

""" for d in range(6):
    plot_2D(data,1,"bracha",d_fix=d)
    plot_2D(data,1,"opodis_1",d_fix=d)
    plot_2D(data,1,"opodis_2t+1",d_fix=d)

    plot_2D(data,2,"bracha",d_fix=d)
    plot_2D(data,2,"opodis_1",d_fix=d)
    plot_2D(data,2,"opodis_2t+1",d_fix=d)

    plot_2D(data,3,"bracha",d_fix=d)
    plot_2D(data,3,"opodis_1",d_fix=d)
    plot_2D(data,3,"opodis_2t+1",d_fix=d) """