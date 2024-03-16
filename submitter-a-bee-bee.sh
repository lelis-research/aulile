#!/bin/bash

benchmark_name="38"
benchmark_filename="bustle_38.txt"

for ((aug = 1; aug <= 1; aug++))
	do
	for ((model = 1; model <= 5; model ++))
		do
		for ((taskId = 1; taskId <=38; taskId ++))
			do
				# if [[ $taskId -eq 17 || $taskId -eq 24 || $taskId -eq 71 || $taskId -eq 83 || $taskId -eq 84 || $taskId -eq 88 || $taskId -eq 89 ]]; then
				echo "Augment : ${aug}"
				echo "Model : ${model}"
				echo "TaskID : ${taskId}"
				echo "Benchmark Name : ${benchmark_name}"
				echo "Benchmark Filename : ${benchmark_filename}"
				sbatch --export=m="${model}",t="${taskId}",a="${aug}",bn="${benchmark_name}",b="${benchmark_filename}" batcher-a-bee-bee.sh
				# fi
			done
		done
	done
