#!/bin/bash

results_dir=augmented/bustle_results
mkdir -p ${results_dir}

# CrossBeam
maxni=3
maxsw=20
beam_size=10
data_root=crossbeam/data
models_dir=trained_models/bustle/
model=vw-bustle_sig-vsize

export CUDA_VISIBLE_DEVICES=0
task_timeout=600
total_max_values_explored=50000
for run in 1 2 3 4 5; do
  for attempts in 2 4 8; do
    let max_values_explored=${total_max_values_explored}/${attempts}
    for dataset in sygus new; do
        # Augmented (growing library) CrossBeam with UR for evaluation
      grow_library=True
      sbatch --export=grow_library=${grow_library},attempts=${attempts},run=${run},dataset=${dataset},max_values_explored=${max_values_explored},maxni=${maxni},maxsw=${maxsw},beam_size=${beam_size},data_root=${data_root},model=${model},results_dir=${results_dir},attempts=${attempts},models_dir=${models_dir},task_timeout=${task_timeout} sbatch_exp.sh
    done
  done
done
