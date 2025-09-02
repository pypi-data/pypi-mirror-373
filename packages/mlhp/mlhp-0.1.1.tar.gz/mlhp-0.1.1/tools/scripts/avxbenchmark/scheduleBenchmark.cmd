#!/bin/bash
#SBATCH -J bench
#SBATCH -o ./benchmark_new.out
#SBATCH -D ./
#SBATCH --get-user-env
#SBATCH --clusters=htce
#SBATCH --partition=htce_special
#SBATCH --reservation=htce_users
#SBATCH --exclusive
#SBATCH --cpus-per-task=40
#SBATCH --mail-type=end
#SBATCH --mail-user=philipp.kopp@tum.de

source ~/prepareModules.sh

cd ~/mlhp

./benchmark.py
