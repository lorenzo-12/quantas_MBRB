# QUANTAS
A Quantitative User-friendly Adaptive Networked Things Abstract Simulator.

This project is a simulator that enables quantitative performance analysis of distributed algorithms. QUANTAS is an abstract simulator, therefore, the obtained results are not affected by the specifics of a particular network or operating system architecture. QUANTAS allows distributed algorithms researchers to quickly investigate a potential solution  and collect data about its performance. QUANTAS programming is relatively straightforward and is accessible to theoretical researchers. 


---


## FULL PAPER
This anonymous repository contains the full version of the paper submitted to **ICDCS 2026**, including:
- full proofs for all theorems
- complete experimental results
- all figures/plots from the evaluation

Paper file:
`ICDCS__Message_Adversary___FULL_PAPER___anonymous_4open_science_.pdf`


---


## Repository Structure

### `quantas/`
Core code used to run the experiments. It contains multiple algorithm implementations, including `BRBPeer/`. 

The directory contains:
- all the **topologies** used in experiments
- the `.cpp` implementation that replicates the corresponding algorithm


### `results/`
Experimental outputs in JSON format for **all test combinations**.

Results are organized:
1. by message adversary (MA1/MA2/MA3)
2. then by the topology
3. then by network size and metrics (number of nodes, connectivity)
4. finally by algorithm


### `results_img_3d/`
This directory contains the 3D plots, generated from the JSON files in `results/`, measuring the "delivery rate", "total messages sent" and "time to terminate" for each possible combination of (algorithm, message adversary). 



### `makefiles`
directory containing the Makefile files needed by quantas to run an experiment, one for each experiment that we runned.


### `HOWTO.md`
This file contains a step-by-step how-to to write and simulate a distributed algorithm with QUANTAS. 


### `run_experiments_alg.py`
Main Python entry point used to launch experiments (referenced by the .sh files).

It:
- takes as input the configuration of the desired tests (algorithm, message adversary type)
- runs them using Python threads to speed up execution


## How to Replicate the Experiments

To replicate the experiments in this repository (Linux):

1. **Download and extract** this repository on your machine.
2. Open a terminal and **cd into** the repository root directory.
3. Ensure all **dependencies** are installed and correctly configured.
4. Follow the instructions in **`HOWTO.md`** to verify that the simulator builds and runs correctly (i.e., the basic workflow works end-to-end).
5. Run:

```bash
make clean
python3 run_experiments_alg.py --alg "<algorithm_name>" --ma <message_adversary>
```

where `<algorithm_name>` can be one of `[bracha, opodis_1, opodis_t+1, opodis_2t+1]` and `<message_adversary>`  can be one of `[1,2,3]`.

Tip: the .sh files show the exact logic/configurations used to launch batches of experiments on the university servers.


## Notes
- This is an **anonymous** research repository for open science / review.
