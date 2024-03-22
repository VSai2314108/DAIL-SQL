#!/bin/bash
#SBATCH --job-name=test1
#SBATCH --output=./outputs/vasp.out
#SBATCH --error=./outputs/vasp.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=somasundaramv@ufl.edu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --ntasks-per-node=1
#SBATCH --distribution=cyclic:cyclic
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --mem-per-gpu=70000
#SBATCH --time=48:00:00


export HF_HOME=/blue/daisyw/somasundaramv/mis
export HF_DATASETS_CACHE=/blue/daisyw/somasundaramv/datasets
export TRANSFORMERS_CACHE=/blue/daisyw/somasundaramv/models
cd /blue/daisyw/somasundaramv/DAIL-SQL
module purge
module load conda java cuda/11.4.3 nvhpc/23.7 openmpi/4.1.5 vasp/6.4.1

mamba activate DAIL-SQL 
nvcc --version
# pip install --upgrade pip
# pip install wheel setuptools
# pip install torch torchvision torchaudio
# pip install accelerate
# pip install transformers
# pip install optimum
# pip install pandas
# pip3 install auto-gptq --extra-index-url https://huggingface.github.io/autogptq-index/whl/cu117/  # Use cu117 if on CUDA 11.7

# echo "data_preprocess"
# python data_preprocess.py

echo "generate question with EUCDISQUESTIONMASK"
python generate_question.py \
--data_type spider \
--split test \
--tokenizer gpt-3.5-turbo \
--max_seq_len 4096 \
--prompt_repr SQL \
--k_shot 9 \
--example_type QA \
--selector_type  EUCDISQUESTIONMASK

echo "generate SQL by LLAMA for EUCDISMASKPRESKLSIMTHR as the pre-generated SQL query"
python ask_llm.py \
--model code-llama-34B \
--question ./dataset/process/SPIDER-TEST_SQL_9-SHOT_EUCDISQUESTIONMASK_QA-EXAMPLE_CTX-200_ANS-4096/ \
--n 1 \
--end_index 2

echo "generate question with EUCDISMASKPRESKLSIMTHR"
python generate_question.py \
--data_type spider \
--split test \
--tokenizer gpt-3.5-turbo \
--max_seq_len 4096 \
--selector_type EUCDISMASKPRESKLSIMTHR \
--pre_test_result ./results/DAIL-SQL+GPT-4.txt \
--prompt_repr SQL \
--k_shot 9 \
--example_type QA

echo "generate SQL by LLAMA for EUCDISMASKPRESKLSIMTHR"
python ask_llm.py \
--model code-llama-34B \
--question ./dataset/process/SPIDER-TEST_SQL_9-SHOT_EUCDISMASKPRESKLSIMTHR_QA-EXAMPLE_CTX-200_ANS-4096/ \
--n 1 \
--end_index 2
