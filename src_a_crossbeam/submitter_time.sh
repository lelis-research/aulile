#!/bin/bash

results_dir=augmented/bustle_results_nodup
maxni=3
maxsw=20
beam_size=10
data_root=crossbeam/data
models_dir=trained_models/bustle/
model=vw-bustle_sig-vsize

task_timeout=3600
max_values_explored=50000
datasets=("sygus" "new")

export CUDA_VISIBLE_DEVICES=0

# Loop through each dataset
for dataset in "${datasets[@]}"; do
    argfile=/scratch/hab1b/crossbeam-grow/augmented/bustle_results_nodup/failed_${dataset}_${max_values_explored}.txt
    # argfile="augmented/bustle_results_nodup/failed_${dataset}_${max_values_explored}.txt"
    # Get the total number of lines (tasks) in the argfile
    total_tasks=$(wc -l < $argfile)

    # Loop through each line in the argfile
    for (( SLURM_ARRAY_TASK_ID=1; SLURM_ARRAY_TASK_ID<=total_tasks; SLURM_ARRAY_TASK_ID++ )); do
        # Extracting arguments for each task
        args=$(sed "${SLURM_ARRAY_TASK_ID}q;d" $argfile)
        run=$(echo $args | cut -d' ' -f1)
        task_name=$(echo $args | cut -d' ' -f2)

        grow_library=True
        for attempts in 86400; do
            echo $run $task_name $grow_library $attempts $dataset
            # Using the extracted run and task_name in the sbatch command
            sbatch --export=grow_library=${grow_library},attempts=${attempts},run=${run},dataset=${dataset},max_values_explored=${max_values_explored},maxni=${maxni},maxsw=${maxsw},beam_size=${beam_size},data_root=${data_root},model=${model},results_dir=${results_dir},models_dir=${models_dir},task_timeout=${task_timeout},task_name=${task_name} sbatch_time.sh
        done
    done
done
