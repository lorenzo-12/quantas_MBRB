import os 
import pathlib 
import subprocess
import time
import json



path_makefile = pathlib.Path(__file__).parent / "makefile"
path_makefile_dir = pathlib.Path(__file__).parent / "makefiles"
path_ma1 = pathlib.Path(__file__).parent / "quantas" / "BRBPeer" / "topologies_bracha" /"MA1_topologies"


files = [
    "generalized_wheel_byz_center_n100_k6.txt",
    "generalized_wheel_n100_k6.txt",
    "multipartite_wheel_n99_k6.txt",
    "random_graph_byz_high_conn_n100_k6.txt",
    "random_graph_n100_k6_e500.txt",
    "random_graph_n100_k6_e600.txt",
    "random_graph_n100_k6_e700.txt",
    "random_graph_n100_k6.txt",
    "random_graph_pruned_n100_k6.txt"
]


file = os.listdir(path_ma1)[0]
with open(path_ma1/file,"r") as f:
    data = json.load(f)
    #total_tests = int(data["experiments"][0]["tests"])*len(data["experiments"])*int(data["experiments"][0]["rounds"])
    total_tests = int(data["experiments"][0]["tests"])*len(data["experiments"])*3
        
# Monitor and display progress until all processes finish
while True:
    # clear terminal screen
    text = ""
    
    for algorithm in ["bracha", "opodis_1", "opodis_t+1", "opodis_2t+1"]:
        # build progress text
        text += f"{"-"*50} {algorithm:<18} {"-"*50}\n"
        for file in files:
            ma1 = 0
            ma2 = 0
            ma3 = 0
            try:
                with open(f"results_status/MA1_{algorithm}_{file}", "r") as f:
                    ma1 = f.readlines()
            except FileNotFoundError:
                ma1 = []
            try:
                with open(f"results_status/MA2_{algorithm}_{file}", "r") as f:
                    ma2 = f.readlines()
            except FileNotFoundError:
                ma2 = []
            try:
                with open(f"results_status/MA3_{algorithm}_{file}", "r") as f:
                    ma3 = f.readlines()
            except FileNotFoundError:
                ma3 = []
            x = len(ma1)+len(ma2)+len(ma3)   
            perc = min(int(x * 100 / total_tests),100)
            y = len(str(total_tests))
            text += f"[{'#' * perc:<100}]{perc:>3}%  {x:>{y}}/{total_tests}   {file}\n"
            
    text += f"{"-"*120}\n"
    os.system('cls' if os.name == 'nt' else 'clear')
    print(text, end="\n", flush=True)
    time.sleep(3)

        
        

