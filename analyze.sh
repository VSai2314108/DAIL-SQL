#!/bin/bash
#SBATCH --job-name=test1
#SBATCH --output=./outputs/temp.out
#SBATCH --error=./outputs/temp.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=somasundaramv@ufl.edu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --ntasks-per-node=1
#SBATCH --distribution=cyclic:cyclic
#SBATCH --time=48:00:00
#SBATCH --account=dream_team
#SBATCH --qos=dream_team

cd /blue/daisyw/somasundaramv/DAIL-SQL
module purge
module load conda java cuda/11.4.3 nvhpc/23.7 openmpi/4.1.5 vasp/6.4.1

mamba activate DAIL-SQL 
python -u /blue/daisyw/somasundaramv/DAIL-SQL/dataset/mimic/to_test_output.py