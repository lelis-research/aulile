#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:v100:1
#SBATCH --time=0:05:00
#SBATCH --output=/scratch/hab1b/crossbeam-grow/slurm_outputs/nodup/grow50kt3600/%j.txt
#SBATCH --account=rrg-lelis


module load python/3.8 cuda cudnn
source $HOME/cb-env/bin/activate
cd /scratch/hab1b/crossbeam-grow

python3 -m crossbeam.experiment.run_crossbeam \
	  --task_name=${task_name} \
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
	  --task_timeout=${task_timeout} \
	  --attempt_timeout=${task_timeout} \
	  --max_values_explored=${max_values_explored} \
	  --load_model=${model}/model-best-valid.ckpt \
	  --io_encoder=bustle_sig --value_encoder=bustle_sig --encode_weight=True \
	  --json_results_file=${results_dir}/run_${run}.${max_values_explored}.attempt-${attempts}.${task_timeout}.grow-${grow_library}.${model}.${dataset}.${task_name}.json
