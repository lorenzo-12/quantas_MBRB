import json 
import os 
from utils import *
from collections import OrderedDict

path_base_topologies = pathlib.Path(__file__).parent / "base_topologies"
path_bracha_ma1 = pathlib.Path(__file__).parent / "topologies_bracha" / "MA1_topologies"
path_bracha_ma2 = pathlib.Path(__file__).parent / "topologies_bracha" / "MA2_topologies"
path_bracha_ma3 = pathlib.Path(__file__).parent / "topologies_bracha" / "MA3_topologies"

def getDeliveryThreshold(algorithm: str, t: int, d: int):
    epsilon = 0.05
    if algorithm == "bracha":
        return 2*t + 1
    elif algorithm == "opodis_1":
        return 1
    elif algorithm == "opodis_t+1":
        return t + 1
    elif algorithm == "opodis_2t+1":
        return 2*t + 1
    
    return 2*t+1

desired_order = ["outFile","logFile","tests","rounds","topology","distribution","threadCount"]

def generate_net(algorithm):

    #----------------- GENERATE NETWORK MA1 -------------------------
    for file in path_base_topologies.rglob("*.json"):
        file = str(file)
        if ("n24" in file or "n48" in file or "n48" in file):
            continue
        net_json = getNetwork(file)
        n,k = extractNK(file)
        td_list = gen_t_d_combination(0,k)
        
        net_json["experiments"] = []
        for t,d in td_list:
            delivery_threshold = getDeliveryThreshold(algorithm, t, d)
            x = generateRandomNetMA1(file,t,d, delivery_threshold, algorithm)
            net_json["experiments"].append(x)
        
        out = file.replace("base_topologies",f"topologies_{algorithm}/MA1_topologies")
        out_dict = str(path_base_topologies).replace("base_topologies",f"topologies_{algorithm}/MA1_topologies")
        os.makedirs(out_dict, exist_ok=True)
        with open(out, "w+") as f:
            json.dump(net_json, f, indent=4)

    #----------------------------------------------------------------



    #----------------- GENERATE NETWORK MA2 -------------------------
    for file in path_base_topologies.rglob("*.json"):
        file = str(file)
        if ("n24" in file or "n48" in file or "n48" in file):
            continue
        net_json = getNetwork(file)
        n,k = extractNK(file)
        td_list = gen_t_d_combination(0,k)
        
        net_json["experiments"] = []
        for t,d in td_list:
            delivery_threshold = getDeliveryThreshold(algorithm, t, d)
            x = generateRandomNetMA2(file,t,d,delivery_threshold,algorithm)
            net_json["experiments"].append(x)
        
        out = file.replace("base_topologies",f"topologies_{algorithm}/MA2_topologies")
        out_dict = str(path_base_topologies).replace("base_topologies",f"topologies_{algorithm}/MA2_topologies")
        os.makedirs(out_dict, exist_ok=True)
        with open(out, "w+") as f:
            json.dump(net_json, f, indent=4)
            
    #----------------------------------------------------------------



    #----------------- GENERATE NETWORK MA3 -------------------------
    for file in path_base_topologies.rglob("*.json"):
        file = str(file)
        if ("n24" in file or "n48" in file or "n48" in file):
            continue
        net_json = getNetwork(file)
        n,k = extractNK(file)
        td_list = gen_t_d_combination(0,k)
        
        net_json["experiments"] = []
        for t,d in td_list:
            delivery_threshold = getDeliveryThreshold(algorithm, t, d)
            x = generateRandomNetMA3(file,t,d,delivery_threshold,algorithm)
            net_json["experiments"].append(x)
        
        out = file.replace("base_topologies",f"topologies_{algorithm}/MA3_topologies")
        out_dict = str(path_base_topologies).replace("base_topologies",f"topologies_{algorithm}/MA3_topologies")
        os.makedirs(out_dict, exist_ok=True)
        with open(out, "w+") as f:
            json.dump(net_json, f, indent=4)

    #----------------------------------------------------------------

def copyNetwork(algorithm):
    for file in path_bracha_ma1.rglob("*.json"):
        net_json = getNetwork(file)
        
        for net in net_json["experiments"]:
            net["logFile"] = net["logFile"].replace("bracha",algorithm)
            os.makedirs(net["logFile"].split("/t")[0], exist_ok=True)
            net["outFile"] = net["outFile"].replace("bracha",algorithm)
            topology = net["topology"]
            topology["algorithm"] = algorithm
            t = topology["byzantine"]["total"]
            d = topology["messageAdversary"]["power"]
            topology["delivery_threshold"] = getDeliveryThreshold(algorithm, t, d)
        
        out = str(file).replace("topologies_bracha",f"topologies_{algorithm}")
        tmp = out.split("/")[-1]
        out_dict = out.replace(tmp,"").replace("topologies_bracha",f"topologies_{algorithm}")
        os.makedirs(out_dict, exist_ok=True)
        with open(out, "w+") as f:
            json.dump(net_json, f, indent=4)
    
    for file in path_bracha_ma2.rglob("*.json"):
        net_json = getNetwork(file)
        
        for net in net_json["experiments"]:
            net["logFile"] = net["logFile"].replace("bracha",algorithm)
            os.makedirs(net["logFile"].split("/t")[0], exist_ok=True)
            net["outFile"] = net["outFile"].replace("bracha",algorithm)
            topology = net["topology"]
            topology["algorithm"] = algorithm
            t = topology["byzantine"]["total"]
            d = topology["messageAdversary"]["power"]
            topology["delivery_threshold"] = getDeliveryThreshold(algorithm, t, d)
        
        out = str(file).replace("topologies_bracha",f"topologies_{algorithm}")
        tmp = out.split("/")[-1]
        out_dict = out.replace(tmp,"").replace("topologies_bracha",f"topologies_{algorithm}")
        os.makedirs(out_dict, exist_ok=True)
        with open(out, "w+") as f:
            json.dump(net_json, f, indent=4)
            
    for file in path_bracha_ma3.rglob("*.json"):
        net_json = getNetwork(file)
        
        for net in net_json["experiments"]:
            net["logFile"] = net["logFile"].replace("bracha",algorithm)
            os.makedirs(net["logFile"].split("/t")[0], exist_ok=True)
            net["outFile"] = net["outFile"].replace("bracha",algorithm)
            topology = net["topology"]
            topology["algorithm"] = algorithm
            t = topology["byzantine"]["total"]
            d = topology["messageAdversary"]["power"]
            topology["delivery_threshold"] = getDeliveryThreshold(algorithm, t, d)
        
        out = str(file).replace("topologies_bracha",f"topologies_{algorithm}")
        tmp = out.split("/")[-1]
        out_dict = out.replace(tmp,"").replace("topologies_bracha",f"topologies_{algorithm}")
        os.makedirs(out_dict, exist_ok=True)
        with open(out, "w+") as f:
            json.dump(net_json, f, indent=4)

def addGitKeep():
    code = "find . -type d -empty -exec touch {}/.gitkeep \;"

""" generate_net("bracha")
copyNetwork("opodis_1")
copyNetwork("opodis_2t+1")
copyNetwork("opodis_t+1") """


