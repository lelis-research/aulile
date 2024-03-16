#!/bin/bash

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Run from the root crossbeam/ directory.

results_dir=augmented/bustle_results
#if [ -d "$results_dir" ]; then
#  echo "WARNING: The results directory ${results_dir} already exists. If you continue, results may be overwritten."
#  while true; do
#    read -p "Continue? [y/n] " yn
#    case $yn in
#      [Yy]* ) break;;
#      [Nn]* ) echo "Exiting."; exit;;
#      * ) echo "Please answer yes or no.";;
#    esac
#  done
#else
#  mkdir -p ${results_dir}
#fi
mkdir -p ${results_dir}

# CrossBeam
maxni=3
maxsw=20
beam_size=10
data_root=crossbeam/data
models_dir=trained_models/bustle/
model=vw-bustle_sig-vsize

export CUDA_VISIBLE_DEVICES=0

total_max_values_explored=50000
for run in 1 2 3 4 5; do
  for attempts in 2 4 8; do
    let max_values_explored=${total_max_values_explored}/${attempts}
    for dataset in sygus new; do
        # Augmented (growing library) CrossBeam with UR for evaluation
      grow_library=True
      python3 -m crossbeam.experiment.run_crossbeam \
          --grow_library=${grow_library} \
          --stop_if_no_grow=False \
          --attempts=${attempts} \
          --seed=${run} \
          --domain=bustle \
          --model_type=char \
          --max_num_inputs=$maxni \
          --max_search_weight=$maxsw \
          --data_folder=${data_root}/${dataset} \
          --save_dir=${models_dir} \
          --beam_size=$beam_size \
          --gpu_list=0 \
          --num_proc=1 \
          --eval_every=1 \
          --train_steps=0 \
          --do_test=True \
          --use_ur=True \
          --task_timeout=300 \
          --attempt_timeout=172800 \
          --max_values_explored=${max_values_explored} \
          --load_model=${model}/model-best-valid.ckpt \
          --io_encoder=bustle_sig --value_encoder=bustle_sig --encode_weight=True \
          --json_results_file=${results_dir}/run_${run}.${attempts}.grow-${grow_library}.${model}.${dataset}.json
    done
  done
done
