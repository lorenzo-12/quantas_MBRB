#!/bin/bash

#SBATCH --job-name=exemple
#SBATCH --nodes=1
#SBATCH --mem=256G
#SBATCH --gpus=a100_3g.40gb:1
#SBATCH --time=14400
#SBATCH --mail-type=ALL
#SBATCH --output=server_outputs/%x-%j.out
#SBATCH --error=server_outputs/%x-%j.err


python3 run_experiments_alg.py --alg "opodis_t+1" --ma 1

